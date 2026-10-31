"""Dependency-scoped Product Definition re-entry events and contract drift audit."""

import copy
import re

from approval_v2 import definition_digest, validate_approval
from authority_binding_v2 import BindingError, canonical_record_index
from state_validation_v2 import evaluate_closure_v2

from .authority import DownstreamV2Error, REENTRY_VERSION, sha256_json
from .contracts import validate_action_contract_v2
from .derivation import load_responsibility_profile
from .seeds import build_source_seed_inventory, source_seed_index, verify_source_seed


_HASH = re.compile(r"^[0-9a-f]{64}$")
_FIELD_PATH = re.compile(r"^(actions|lifecycles)/([^/\s]+)/([^/\s]+)$")
_EVENT_TYPES = {"AMBIGUITY_FOUND", "CONTRACT_CONFLICT", "OUT_OF_SCOPE_REQUEST"}
_AUTHORITY_CLASSES = {"FACTUAL", "INTENT", "CONSTRAINT", "BEHAVIORAL", "PREFERENCE"}
_BINDING_KEYS = {"record_id", "pointer", "value_sha256"}


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _strings(values: object) -> list[str]:
    if not isinstance(values, list) or any(
        not isinstance(value, str) or not value.strip() for value in values
    ):
        raise ValueError("INVALID_REENTRY_STRING_INVENTORY")
    if len(values) != len(set(values)):
        raise ValueError("INVALID_REENTRY_STRING_INVENTORY")
    return sorted(values)


def _event(
    *,
    event_type: str,
    source_definition_digest: str,
    source_contract_hash: str | None,
    affected_authority_ids: list[str],
    affected_action_ids: list[str],
    affected_lifecycle_ids: list[str],
    evidence_refs: list[str],
    suggested_question: str,
    why_it_matters: str,
    required_authority_class: str,
) -> dict[str, object]:
    if (
        event_type not in _EVENT_TYPES
        or not _is_hash(source_definition_digest)
        or (source_contract_hash is not None and not _is_hash(source_contract_hash))
        or required_authority_class not in _AUTHORITY_CLASSES
        or not isinstance(suggested_question, str)
        or not suggested_question.strip()
        or not isinstance(why_it_matters, str)
        or not why_it_matters.strip()
    ):
        raise ValueError("INVALID_REENTRY_EVENT_INPUT")
    authority_ids = _strings(affected_authority_ids)
    action_ids = _strings(affected_action_ids)
    lifecycle_ids = _strings(affected_lifecycle_ids)
    evidence = _strings(evidence_refs)
    affected_ids = sorted(set(authority_ids + action_ids + lifecycle_ids))
    if not affected_ids:
        raise ValueError("EMPTY_REENTRY_SCOPE")
    content = {
        "schema_version": REENTRY_VERSION,
        "event_type": event_type,
        "source_definition_digest": source_definition_digest,
        "source_contract_hash": source_contract_hash,
        "affected_authority_ids": authority_ids,
        "affected_action_ids": action_ids,
        "affected_lifecycle_ids": lifecycle_ids,
        "evidence_refs": evidence,
        "halt_scope": {
            "mode": "AFFECTED_ONLY",
            "action_ids": action_ids,
            "lifecycle_ids": lifecycle_ids,
        },
        "candidate_unknown": {
            "suggested_question": suggested_question.strip(),
            "why_it_matters": why_it_matters.strip(),
            "required_authority_class": required_authority_class,
            "affected_ids": affected_ids,
        },
        "recommended_action": "REENTER_PRODUCT_DEFINITION",
    }
    event_id = "REENTRY-" + sha256_json(content)[:24]
    return {"schema_version": content.pop("schema_version"), "event_id": event_id, **content}


def _definition_items(definition: object) -> dict[tuple[str, str], dict[str, object]]:
    if not isinstance(definition, dict):
        raise ValueError("INVALID_HANDOFF_DEFINITION")
    index: dict[tuple[str, str], dict[str, object]] = {}
    for collection, id_key in (("actions", "action_id"), ("lifecycles", "lifecycle_id")):
        items = definition.get(collection)
        if not isinstance(items, list):
            raise ValueError("INVALID_HANDOFF_DEFINITION")
        for item in items:
            item_id = item.get(id_key) if isinstance(item, dict) else None
            refs = item.get("authority_scope_refs") if isinstance(item, dict) else None
            if (
                not isinstance(item_id, str)
                or not item_id
                or not isinstance(refs, list)
                or (collection, item_id) in index
            ):
                raise ValueError("INVALID_HANDOFF_DEFINITION")
            index[(collection, item_id)] = item
    return index


def build_reentry_events(
    *,
    source_authority: dict[str, object],
    definition: dict[str, object],
    gaps: list[dict[str, object]],
    source_contract_hash: str | None,
) -> list[dict[str, object]]:
    """Convert compiler semantic gaps into deterministic affected-only proposals."""
    digest = source_authority.get("approved_definition_digest") if isinstance(source_authority, dict) else None
    if not _is_hash(digest) or not isinstance(gaps, list):
        raise ValueError("INVALID_REENTRY_SOURCE")
    items = _definition_items(definition)
    events = []
    for raw_gap in gaps:
        if not isinstance(raw_gap, dict):
            raise ValueError("INVALID_REENTRY_GAP")
        match = _FIELD_PATH.fullmatch(str(raw_gap.get("field_path", "")))
        if match is None:
            raise ValueError("INVALID_REENTRY_GAP")
        collection, item_id, field_name = match.groups()
        item = items.get((collection, item_id))
        event_type = raw_gap.get("gap_type")
        reason = raw_gap.get("reason")
        authority_class = raw_gap.get("required_authority_class")
        if (
            item is None
            or event_type not in _EVENT_TYPES
            or not isinstance(reason, str)
            or not reason.strip()
            or authority_class not in _AUTHORITY_CLASSES
        ):
            raise ValueError("INVALID_REENTRY_GAP")
        gap_refs = _strings(raw_gap.get("authority_scope_refs"))
        item_refs = _strings(item.get("authority_scope_refs"))
        if gap_refs != item_refs:
            raise ValueError("INVALID_REENTRY_GAP_SCOPE")
        evidence_refs = _strings(raw_gap.get("evidence_refs"))
        owner_kind = "action" if collection == "actions" else "lifecycle"
        if event_type == "OUT_OF_SCOPE_REQUEST":
            question = f"Should {collection}/{item_id}/{field_name} be added to approved Product Definition scope?"
        elif event_type == "CONTRACT_CONFLICT":
            question = f"Which approved authority resolves the conflict for {collection}/{item_id}/{field_name}?"
        else:
            question = f"What approved product meaning should {collection}/{item_id}/{field_name} use?"
        events.append(_event(
            event_type=event_type,
            source_definition_digest=digest,
            source_contract_hash=source_contract_hash,
            affected_authority_ids=gap_refs,
            affected_action_ids=[item_id] if collection == "actions" else [],
            affected_lifecycle_ids=[item_id] if collection == "lifecycles" else [],
            evidence_refs=evidence_refs,
            suggested_question=question,
            why_it_matters=(
                f"The {owner_kind} cannot continue at this field because Product Definition authority says: "
                f"{reason.strip()}"
            ),
            required_authority_class=authority_class,
        ))
    return sorted(events, key=lambda event: event["event_id"])


def _raw_record_ids(state: dict[str, object]) -> list[str]:
    containers = []
    objects = state.get("objects")
    if isinstance(objects, dict):
        containers.extend(objects.values())
    containers.extend((state.get("evidence"), state.get("contradictions")))
    manifest = state.get("surface_manifest")
    containers.append(manifest.get("records") if isinstance(manifest, dict) else None)
    return [
        record["id"]
        for records in containers
        if isinstance(records, list)
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    ]


def _positive_cells(state: dict[str, object]):
    coverage = state.get("coverage")
    if not isinstance(coverage, list):
        raise ValueError("INVALID_COVERAGE_STRUCTURE")
    for row in coverage:
        if not isinstance(row, dict) or not isinstance(row.get("cells"), dict):
            raise ValueError("INVALID_COVERAGE_STRUCTURE")
        for axis, cell in row["cells"].items():
            if isinstance(cell, dict) and cell.get("status") == "COVERED":
                yield {
                    "scope": "CORE", "owner_ref": row.get("feature_id"), "axis": axis,
                    "pack_id": None, "action_key": None,
                }, cell
    coverage = state.get("grill_coverage")
    if not isinstance(coverage, list):
        raise ValueError("INVALID_GRILL_STRUCTURE")
    for row in coverage:
        if not isinstance(row, dict) or not isinstance(row.get("axes"), dict):
            raise ValueError("INVALID_GRILL_STRUCTURE")
        for axis, cell in row["axes"].items():
            if isinstance(cell, dict) and cell.get("status") == "ADDRESSED":
                yield {
                    "scope": "GRILL", "owner_ref": row.get("target_ref"), "axis": axis,
                    "pack_id": row.get("pack_id"), "action_key": None,
                }, cell
    coverage = state.get("ux_coverage")
    if not isinstance(coverage, list):
        raise ValueError("INVALID_UX_STRUCTURE")
    for row in coverage:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("states"), dict)
            or not isinstance(row.get("actions"), list)
        ):
            raise ValueError("INVALID_UX_STRUCTURE")
        for axis, cell in row["states"].items():
            if isinstance(cell, dict) and cell.get("status") == "COVERED":
                yield {
                    "scope": "UX_STATE", "owner_ref": row.get("screen_id"), "axis": axis,
                    "pack_id": None, "action_key": None,
                }, cell
        for action in row["actions"]:
            if not isinstance(action, dict) or not isinstance(action.get("cells"), dict):
                raise ValueError("INVALID_UX_STRUCTURE")
            for axis, cell in action["cells"].items():
                if isinstance(cell, dict) and cell.get("status") == "COVERED":
                    yield {
                        "scope": "UX_ACTION", "owner_ref": row.get("screen_id"), "axis": axis,
                        "pack_id": None, "action_key": action.get("key"),
                    }, cell


def _validate_positive_binding_structures(state: dict[str, object]) -> None:
    seen_locations = set()
    for location, cell in _positive_cells(state):
        location_key = sha256_json(location)
        bindings = cell.get("authority_bindings")
        if location_key in seen_locations or not isinstance(bindings, list):
            raise ValueError("INVALID_POSITIVE_BINDING_STRUCTURE")
        seen_locations.add(location_key)
        for binding in bindings:
            if (
                not isinstance(binding, dict)
                or set(binding) != _BINDING_KEYS
                or not isinstance(binding.get("record_id"), str)
                or not isinstance(binding.get("pointer"), str)
                or not _is_hash(binding.get("value_sha256"))
            ):
                raise ValueError("INVALID_POSITIVE_BINDING_STRUCTURE")


def _binding_identity(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"contract_id", "version", "digest"}
        and isinstance(value.get("contract_id"), str)
        and bool(value["contract_id"])
        and isinstance(value.get("version"), str)
        and bool(value["version"])
        and _is_hash(value.get("digest"))
    )


def _state_controls(state: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    if not isinstance(state, dict) or state.get("schema_version") != "0.2.0":
        raise ValueError("INVALID_STATE_STRUCTURE")
    project = state.get("project")
    if not isinstance(project, dict):
        raise ValueError("INVALID_STATE_STRUCTURE")
    if (
        not isinstance(project.get("slug"), str)
        or not isinstance(project.get("definition_revision"), int)
        or isinstance(project.get("definition_revision"), bool)
        or project["definition_revision"] < 1
    ):
        raise ValueError("INVALID_STATE_STRUCTURE")
    closure_contract = project.get("closure_contract")
    if (
        not isinstance(closure_contract, dict)
        or set(closure_contract) != {
            "level", "product_binding_contract", "ux_binding_contract"
        }
        or closure_contract.get("level") != "SEMANTIC_CLOSURE"
        or not _binding_identity(closure_contract.get("product_binding_contract"))
        or not _binding_identity(closure_contract.get("ux_binding_contract"))
    ):
        raise ValueError("INVALID_STATE_BINDING_STRUCTURE")
    history = state.get("approval_history")
    if not isinstance(history, list) or any(not isinstance(entry, dict) for entry in history):
        raise ValueError("INVALID_APPROVAL_HISTORY_STRUCTURE")
    record_ids = _raw_record_ids(state)
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("DUPLICATE_STATE_RECORD")
    canonical_record_index(state)
    _validate_positive_binding_structures(state)
    definition_digest(state)
    closure = evaluate_closure_v2(state)
    if not isinstance(closure, dict) or closure.get("definition_digest") is None:
        raise ValueError("UNSAFE_SEMANTIC_PROJECTION")
    return project, closure_contract


def _contract_ids(contract: dict[str, object]) -> tuple[list[str], list[str], list[str]]:
    actions = sorted({
        item.get("action_id")
        for item in contract.get("actions", [])
        if isinstance(item, dict) and isinstance(item.get("action_id"), str)
    })
    lifecycles = sorted({
        item.get("lifecycle_id")
        for item in contract.get("lifecycles", [])
        if isinstance(item, dict) and isinstance(item.get("lifecycle_id"), str)
    })
    authorities = sorted({
        item.get("record_id")
        for item in contract.get("scope_commitments", [])
        if isinstance(item, dict) and isinstance(item.get("record_id"), str)
    })
    return actions, lifecycles, authorities


def _source_digest(contract: dict[str, object]) -> str:
    authority = contract.get("source_authority")
    digest = authority.get("approved_definition_digest") if isinstance(authority, dict) else None
    return digest if _is_hash(digest) else "0" * 64


def _source_contract_hash(contract: dict[str, object]) -> str | None:
    value = contract.get("semantic_contract_hash")
    return value if _is_hash(value) else None


def _global_event(contract: dict[str, object], reason: str) -> dict[str, object]:
    actions, lifecycles, authorities = _contract_ids(contract)
    if not actions and not lifecycles and not authorities:
        authorities = ["INVALID-CONTRACT"]
    return _event(
        event_type="CONTRACT_CONFLICT",
        source_definition_digest=_source_digest(contract),
        source_contract_hash=_source_contract_hash(contract),
        affected_authority_ids=authorities,
        affected_action_ids=actions,
        affected_lifecycle_ids=lifecycles,
        evidence_refs=[],
        suggested_question="Which approved Product Definition contract should replace this invalid provenance?",
        why_it_matters=reason,
        required_authority_class="CONSTRAINT",
    )


def _revision_relation(contract: dict[str, object], project: dict[str, object] | None) -> str:
    authority = contract.get("source_authority")
    source_revision = authority.get("approved_revision") if isinstance(authority, dict) else None
    current_revision = project.get("definition_revision") if isinstance(project, dict) else None
    return (
        "OLDER_APPROVED_REVISION_UNAFFECTED"
        if isinstance(source_revision, int)
        and isinstance(current_revision, int)
        and current_revision > source_revision
        else "SAME_APPROVED_REVISION"
    )


def _result(
    status: str,
    *,
    global_definition_closed: bool,
    authority_revision_relation: str,
    events: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "status": status,
        "global_definition_closed": global_definition_closed,
        "authority_revision_relation": authority_revision_relation,
        "reentry_events": sorted(events, key=lambda event: event["event_id"]),
    }


def _global_closed_truth(state: object) -> bool:
    try:
        closure = evaluate_closure_v2(state)
        return isinstance(closure, dict) and closure.get("closed") is True
    except (BindingError, KeyError, TypeError, ValueError, AttributeError):
        return False


def _consumption(contract: dict[str, object]):
    profile = load_responsibility_profile()
    seed_consumers: dict[str, list[dict[str, str]]] = {}
    scope_consumers: dict[str, dict[str, set[str]]] = {}
    for collection, id_key, profile_key in (
        ("actions", "action_id", "action_fields"),
        ("lifecycles", "lifecycle_id", "lifecycle_fields"),
    ):
        for item in contract[collection]:
            item_id = item[id_key]
            for ref in item["authority_scope_refs"]:
                scope = scope_consumers.setdefault(ref, {"actions": set(), "lifecycles": set()})
                scope[collection].add(item_id)
            for field_name, field in item["fields"].items():
                consumer = {
                    "collection": collection,
                    "item_id": item_id,
                    "field_name": field_name,
                    "authority_class": profile[profile_key][field_name]["required_authority_class"],
                }
                for seed_ref in field["source_seed_refs"]:
                    seed_consumers.setdefault(seed_ref, []).append(consumer)
    return seed_consumers, scope_consumers


def _seed_authority_ids(seed: dict[str, object]) -> tuple[list[str], list[str]]:
    ids = []
    evidence = []
    record_id = seed.get("record_id")
    if isinstance(record_id, str):
        if seed.get("record_type") == "EVD":
            evidence.append(record_id)
        else:
            ids.append(record_id)
    location = seed.get("location")
    owner_ref = location.get("owner_ref") if isinstance(location, dict) else None
    if isinstance(owner_ref, str):
        ids.append(owner_ref)
    return sorted(set(ids)), sorted(set(evidence))


def _seed_events(
    contract: dict[str, object],
    seed: dict[str, object],
    consumers: list[dict[str, str]],
    cause: str,
) -> list[dict[str, object]]:
    authority_ids, evidence = _seed_authority_ids(seed)
    events = []
    for consumer in sorted(
        consumers,
        key=lambda item: (item["collection"], item["item_id"], item["field_name"]),
    ):
        path = f"{consumer['collection']}/{consumer['item_id']}/{consumer['field_name']}"
        events.append(_event(
            event_type="CONTRACT_CONFLICT",
            source_definition_digest=_source_digest(contract),
            source_contract_hash=_source_contract_hash(contract),
            affected_authority_ids=authority_ids,
            affected_action_ids=[consumer["item_id"]] if consumer["collection"] == "actions" else [],
            affected_lifecycle_ids=[consumer["item_id"]] if consumer["collection"] == "lifecycles" else [],
            evidence_refs=evidence,
            suggested_question=f"Which approved authority should replace the changed dependency for {path}?",
            why_it_matters=f"Consumed seed {seed.get('seed_key')} no longer verifies: {cause}",
            required_authority_class=consumer["authority_class"],
        ))
    return events


def _scope_event(
    contract: dict[str, object],
    record_id: str,
    consumers: dict[str, set[str]],
    cause: str,
) -> dict[str, object]:
    return _event(
        event_type="CONTRACT_CONFLICT",
        source_definition_digest=_source_digest(contract),
        source_contract_hash=_source_contract_hash(contract),
        affected_authority_ids=[record_id],
        affected_action_ids=sorted(consumers["actions"]),
        affected_lifecycle_ids=sorted(consumers["lifecycles"]),
        evidence_refs=[],
        suggested_question=f"Which approved scope record should replace the changed commitment for {record_id}?",
        why_it_matters=cause,
        required_authority_class="CONSTRAINT",
    )


def _builder_failure_is_consumed(error: DownstreamV2Error, seeds: list[dict[str, object]]) -> bool:
    detail = error.detail
    if isinstance(detail, dict):
        for seed in seeds:
            if (
                detail.get("record_id") == seed.get("record_id")
                and detail.get("pointer") == seed.get("pointer")
            ):
                return True
            if detail == seed.get("location"):
                return True
    return False


def audit_contract_against_state(
    contract: object,
    state: dict[str, object],
) -> dict[str, object]:
    """Audit immutable contract provenance and only its current local dependencies."""
    contract_errors = validate_action_contract_v2(contract)
    if contract_errors:
        contract_object = contract if isinstance(contract, dict) else {}
        reason = "Contract semantic/artifact provenance is invalid at: " + ", ".join(
            sorted({error["path"] for error in contract_errors})
        )
        return _result(
            "REENTRY_REQUIRED",
            global_definition_closed=_global_closed_truth(state),
            authority_revision_relation=_revision_relation(contract_object, None),
            events=[_global_event(contract_object, reason)],
        )

    project = None
    try:
        project, current_bindings = _state_controls(state)
        closure = evaluate_closure_v2(state)
    except (BindingError, DownstreamV2Error, KeyError, TypeError, ValueError, AttributeError):
        return _result(
            "DEFINITION_NOT_READY",
            global_definition_closed=False,
            authority_revision_relation=_revision_relation(contract, project),
            events=[],
        )

    relation = _revision_relation(contract, project)
    globally_closed = closure.get("closed") is True
    authority = contract["source_authority"]
    seed_consumers, scope_consumers = _consumption(contract)
    seeds = contract["source_seed_inventory"]
    events = []

    history_matches = [
        entry
        for entry in state["approval_history"]
        if entry.get("revision") == authority["approved_revision"]
        and entry.get("definition_digest") == authority["approved_definition_digest"]
        and entry.get("manifest_digest") == authority["approved_manifest_digest"]
    ]
    approval_history_invalid = any(
        error.get("code") == "approval_history_gaps"
        for error in validate_approval(state)
    )
    if (
        len(history_matches) != 1
        or approval_history_invalid
        or project["slug"] != authority["product_slug"]
        or project["definition_revision"] < authority["approved_revision"]
    ):
        events.append(_global_event(
            contract,
            "The contract source revision/digest/manifest provenance is not uniquely approved in current history.",
        ))

    binding_mismatches = []
    for state_key, authority_key, scopes in (
        ("product_binding_contract", "product_binding_contract", {"CORE", "GRILL"}),
        ("ux_binding_contract", "ux_binding_contract", {"UX_STATE", "UX_ACTION"}),
    ):
        if current_bindings[state_key] != authority[authority_key]:
            binding_mismatches.append((state_key, scopes))
    for binding_name, scopes in binding_mismatches:
        for seed in seeds:
            location = seed.get("location")
            if isinstance(location, dict) and location.get("scope") in scopes:
                events.extend(_seed_events(
                    contract,
                    seed,
                    seed_consumers[seed["seed_key"]],
                    f"{binding_name} identity is incompatible with the contract source authority.",
                ))

    available = None
    inventory_error = None
    try:
        available = source_seed_index(build_source_seed_inventory(state))
    except DownstreamV2Error as error:
        inventory_error = error

    drifted_seeds = []
    for seed in seeds:
        try:
            verify_source_seed(state, seed)
        except DownstreamV2Error as error:
            drifted_seeds.append((seed, error))
            events.extend(_seed_events(
                contract,
                seed,
                seed_consumers[seed["seed_key"]],
                error.code,
            ))

    if inventory_error is not None:
        if not drifted_seeds or not _builder_failure_is_consumed(
            inventory_error, [seed for seed, _ in drifted_seeds]
        ):
            return _result(
                "DEFINITION_NOT_READY",
                global_definition_closed=globally_closed,
                authority_revision_relation=relation,
                events=[],
            )
    if available is not None:
        already_drifted = {seed["seed_key"] for seed, _ in drifted_seeds}
        for seed in seeds:
            if seed["seed_key"] not in already_drifted and available.get(seed["seed_key"]) != seed:
                events.extend(_seed_events(
                    contract,
                    seed,
                    seed_consumers[seed["seed_key"]],
                    "the exact seed is absent from the current positive inventory",
                ))

    index = canonical_record_index(state)
    required_status = {"REQ": "CURRENT", "SCR": "CURRENT", "SURF": "IN_SCOPE"}
    for commitment in contract["scope_commitments"]:
        record_id = commitment["record_id"]
        current = index.get(record_id)
        if (
            current is None
            or current[0] != commitment["record_type"]
            or current[1].get("status") != required_status[commitment["record_type"]]
            or sha256_json(current[1]) != commitment["record_sha256"]
        ):
            events.append(_scope_event(
                contract,
                record_id,
                scope_consumers[record_id],
                f"Declared scope commitment {record_id} changed, disappeared, or became non-current.",
            ))

    unique_events = {event["event_id"]: event for event in events}
    if unique_events:
        return _result(
            "REENTRY_REQUIRED",
            global_definition_closed=globally_closed,
            authority_revision_relation=relation,
            events=list(unique_events.values()),
        )
    return _result(
        "CONFORMANT",
        global_definition_closed=globally_closed,
        authority_revision_relation=relation,
        events=[],
    )
