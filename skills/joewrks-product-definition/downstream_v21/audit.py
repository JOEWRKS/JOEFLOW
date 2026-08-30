"""Read-only dependency-scoped audit for action-conformance/2.1."""

from authority_binding_v2 import BindingError, canonical_record_index
from downstream_v2.authority import DownstreamV2Error, sha256_json
from downstream_v2.reentry import _builder_failure_is_consumed, _state_controls
from downstream_v2.seeds import (
    build_source_seed_inventory,
    source_seed_index,
    verify_source_seed,
)

from .contracts import validate_action_contract_v21


def _relation(contract: object, project: object) -> str:
    if not isinstance(contract, dict) or not isinstance(project, dict):
        return "NOT_APPLICABLE"
    authority = contract.get("source_authority")
    source_revision = authority.get("approved_revision") if isinstance(authority, dict) else None
    current_revision = project.get("definition_revision")
    if not isinstance(source_revision, int) or not isinstance(current_revision, int):
        return "NOT_APPLICABLE"
    return (
        "OLDER_APPROVED_REVISION_UNAFFECTED"
        if current_revision > source_revision
        else "SAME_APPROVED_REVISION"
    )


def _result(
    status: str,
    *,
    relation: str,
    affected: dict[tuple[str, str], set[str]] | None = None,
    semantic_gaps: list[dict[str, object]] | None = None,
    errors: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    affected = {} if affected is None else affected
    return {
        "status": status,
        "authority_revision_relation": relation,
        "affected_consumers": [
            {
                "consumer_kind": kind,
                "consumer_id": consumer_id,
                "dependency_paths": sorted(paths),
            }
            for (kind, consumer_id), paths in sorted(affected.items())
        ],
        "semantic_gaps": sorted(
            [] if semantic_gaps is None else semantic_gaps,
            key=lambda gap: (
                str(gap.get("dependency_kind")),
                str(gap.get("dependency_ref")),
                str(gap.get("reason")),
            ),
        ),
        "errors": sorted(
            [] if errors is None else errors,
            key=lambda error: (str(error.get("code")), str(error.get("detail"))),
        ),
    }


def _consumption(contract: dict[str, object]):
    seed_consumers: dict[str, list[tuple[str, str, str]]] = {}
    scope_consumers: dict[str, list[tuple[str, str, str]]] = {}
    for collection, id_key, consumer_kind in (
        ("actions", "action_id", "ACTION"),
        ("lifecycles", "lifecycle_id", "LIFECYCLE"),
    ):
        for item in contract[collection]:
            item_id = item[id_key]
            for ref in item["authority_scope_refs"]:
                scope_consumers.setdefault(ref, []).append(
                    (consumer_kind, item_id, "authority_scope_refs")
                )
            for field_name, field in item["fields"].items():
                path = f"{collection}/{item_id}/{field_name}"
                for ref in field["source_seed_refs"]:
                    seed_consumers.setdefault(ref, []).append(
                        (consumer_kind, item_id, path)
                    )
            if collection == "actions":
                for basis_name, refs in item["verification_basis"].items():
                    path = f"actions/{item_id}/verification_basis/{basis_name}"
                    for ref in refs:
                        seed_consumers.setdefault(ref, []).append(
                            (consumer_kind, item_id, path)
                        )
    return seed_consumers, scope_consumers


def _record_dependency_gap(
    *,
    dependency_kind: str,
    dependency_ref: str,
    reason: str,
    consumers: list[tuple[str, str, str]],
    affected: dict[tuple[str, str], set[str]],
    gaps: dict[tuple[str, str, str], dict[str, object]],
) -> None:
    normalized_consumers = sorted(set(consumers))
    for kind, consumer_id, path in normalized_consumers:
        affected.setdefault((kind, consumer_id), set()).add(path)
    key = (dependency_kind, dependency_ref, reason)
    gaps[key] = {
        "code": "SEMANTIC_AUTHORITY_GAP",
        "gap_type": "CONTRACT_CONFLICT",
        "dependency_kind": dependency_kind,
        "dependency_ref": dependency_ref,
        "reason": reason,
        "affected_consumers": [
            {"consumer_kind": kind, "consumer_id": consumer_id}
            for kind, consumer_id in sorted(
                {(kind, consumer_id) for kind, consumer_id, _ in normalized_consumers}
            )
        ],
    }


def audit_action_contract_v21_against_state(
    contract: dict[str, object],
    current_state: dict[str, object],
) -> dict[str, object]:
    """Audit only consumed seeds and scope commitments against current state."""
    contract_errors = validate_action_contract_v21(contract)
    if contract_errors:
        relation = _relation(contract, None)
        return _result(
            "REENTRY_REQUIRED",
            relation=relation,
            errors=[{"code": "INVALID_ACTION_CONTRACT_V21", "detail": contract_errors}],
        )

    try:
        project, current_bindings = _state_controls(current_state)
        state_index = canonical_record_index(current_state)
    except (
        BindingError,
        DownstreamV2Error,
        KeyError,
        TypeError,
        ValueError,
        AttributeError,
        RecursionError,
    ) as error:
        return _result(
            "DEFINITION_NOT_READY",
            relation="NOT_APPLICABLE",
            errors=[{"code": "INVALID_CURRENT_STATE", "detail": str(error)}],
        )

    relation = _relation(contract, project)
    seed_consumers, scope_consumers = _consumption(contract)
    affected: dict[tuple[str, str], set[str]] = {}
    gaps: dict[tuple[str, str, str], dict[str, object]] = {}
    seeds = contract["source_seed_inventory"]
    source_authority = contract["source_authority"]

    history_matches = [
        entry
        for entry in current_state["approval_history"]
        if entry.get("revision") == source_authority["approved_revision"]
        and entry.get("definition_digest")
        == source_authority["approved_definition_digest"]
        and entry.get("manifest_digest") == source_authority["approved_manifest_digest"]
    ]
    if (
        len(history_matches) != 1
        or project["slug"] != source_authority["product_slug"]
        or project["definition_revision"] < source_authority["approved_revision"]
    ):
        all_consumers = [
            ("ACTION", item["action_id"], "source_authority")
            for item in contract["actions"]
        ] + [
            ("LIFECYCLE", item["lifecycle_id"], "source_authority")
            for item in contract["lifecycles"]
        ]
        _record_dependency_gap(
            dependency_kind="SOURCE_AUTHORITY",
            dependency_ref=source_authority["approved_definition_digest"],
            reason="Source approval provenance is not uniquely present in current history.",
            consumers=all_consumers,
            affected=affected,
            gaps=gaps,
        )

    for state_key, scopes in (
        ("product_binding_contract", {"CORE", "GRILL"}),
        ("ux_binding_contract", {"UX_STATE", "UX_ACTION"}),
    ):
        if current_bindings[state_key] != source_authority[state_key]:
            for seed in seeds:
                location = seed.get("location")
                if isinstance(location, dict) and location.get("scope") in scopes:
                    _record_dependency_gap(
                        dependency_kind="SOURCE_SEED",
                        dependency_ref=seed["seed_key"],
                        reason=f"{state_key} identity changed for this consumed dependency.",
                        consumers=seed_consumers[seed["seed_key"]],
                        affected=affected,
                        gaps=gaps,
                    )

    drifted = []
    for seed in seeds:
        try:
            verify_source_seed(current_state, seed)
        except DownstreamV2Error as error:
            drifted.append(seed)
            _record_dependency_gap(
                dependency_kind="SOURCE_SEED",
                dependency_ref=seed["seed_key"],
                reason=error.code,
                consumers=seed_consumers[seed["seed_key"]],
                affected=affected,
                gaps=gaps,
            )

    available = None
    inventory_error = None
    try:
        available = source_seed_index(build_source_seed_inventory(current_state))
    except DownstreamV2Error as error:
        inventory_error = error
    if inventory_error is not None and (
        not drifted or not _builder_failure_is_consumed(inventory_error, drifted)
    ):
        return _result(
            "DEFINITION_NOT_READY",
            relation="NOT_APPLICABLE",
            errors=[{"code": inventory_error.code, "detail": inventory_error.detail}],
        )
    if available is not None:
        drifted_refs = {seed["seed_key"] for seed in drifted}
        for seed in seeds:
            if seed["seed_key"] not in drifted_refs and available.get(seed["seed_key"]) != seed:
                _record_dependency_gap(
                    dependency_kind="SOURCE_SEED",
                    dependency_ref=seed["seed_key"],
                    reason="Consumed exact seed is absent from the current positive inventory.",
                    consumers=seed_consumers[seed["seed_key"]],
                    affected=affected,
                    gaps=gaps,
                )

    required_status = {"REQ": "CURRENT", "SCR": "CURRENT", "SURF": "IN_SCOPE"}
    for commitment in contract["scope_commitments"]:
        record_id = commitment["record_id"]
        current = state_index.get(record_id)
        if (
            current is None
            or current[0] != commitment["record_type"]
            or current[1].get("status") != required_status[commitment["record_type"]]
            or sha256_json(current[1]) != commitment["record_sha256"]
        ):
            _record_dependency_gap(
                dependency_kind="SCOPE_COMMITMENT",
                dependency_ref=record_id,
                reason="Scope commitment changed, disappeared, or became non-current.",
                consumers=scope_consumers[record_id],
                affected=affected,
                gaps=gaps,
            )

    if gaps:
        return _result(
            "REENTRY_REQUIRED",
            relation=relation,
            affected=affected,
            semantic_gaps=list(gaps.values()),
        )
    return _result("CONFORMANT", relation=relation)


__all__ = ["audit_action_contract_v21_against_state"]
