"""Compile approved Product Definition authority into action-conformance/2.1."""

import copy
import re

from downstream_v2.authority import (
    DownstreamV2Error,
    require_closed_authority,
    sha256_json,
)
from downstream_v2.seeds import (
    build_closed_source_seed_inventory,
    source_seed_index,
    source_seed_inventory_digest,
)
from downstream_v2.semantic_debt import semantic_debt_report

from .contracts import (
    COMPILER_ID,
    COMPILER_VERSION,
    artifact_hash_v21,
    semantic_contract_hash_v21,
    validate_action_contract_v21,
    validate_verification_basis,
)
from .derivation import (
    ContractExpressivenessGap,
    SemanticAuthorityGap,
    derive_semantic_field_v21,
)
from .field_refs import canonical_field_ref
from .gaps import (
    expressiveness_gap_record,
    route_compilation_gaps,
    semantic_gap_record,
)
from .identity import ACTION_CONTRACT_VERSION, HANDOFF_DEFINITION_VERSION
from .responsibility import (
    load_responsibility_profile_v21,
    responsibility_profile_digest_v21,
)


_SCOPE_REF = re.compile(r"^(?:REQ|SURF|SCR)-[^\s]+$")
_DEFINITION_KEYS = {"definition_schema_version", "product_slug", "actions", "lifecycles"}


def _fail(code: str, detail: object):
    raise DownstreamV2Error(code, detail)


def _scope_record_index(
    state: dict[str, object],
) -> dict[str, tuple[str, dict[str, object]]]:
    try:
        groups = (
            ("REQ", state["objects"]["requirements"], "CURRENT"),
            ("SCR", state["objects"]["screens"], "CURRENT"),
            ("SURF", state["surface_manifest"]["records"], "IN_SCOPE"),
        )
        index = {}
        for record_type, records, required_status in groups:
            if not isinstance(records, list):
                _fail("INVALID_CURRENT_SCOPE_INVENTORY", record_type)
            for record in records:
                if not isinstance(record, dict) or record.get("status") != required_status:
                    continue
                record_id = record.get("id")
                if (
                    not isinstance(record_id, str)
                    or not record_id.startswith(record_type + "-")
                    or record_id in index
                ):
                    _fail("INVALID_CURRENT_SCOPE_INVENTORY", record_id)
                index[record_id] = (record_type, record)
        return index
    except (KeyError, TypeError) as error:
        _fail("INVALID_CURRENT_SCOPE_INVENTORY", str(error))


def _validate_refs(
    raw: object,
    scope_index: dict[str, tuple[str, dict[str, object]]],
) -> list[str]:
    if (
        not isinstance(raw, list)
        or not raw
        or any(
            not isinstance(ref, str) or _SCOPE_REF.fullmatch(ref) is None
            for ref in raw
        )
        or len(raw) != len(set(raw))
    ):
        _fail("INVALID_AUTHORITY_SCOPE_REFS", raw)
    for ref in raw:
        if ref not in scope_index or scope_index[ref][0] != ref.split("-", 1)[0]:
            _fail("INVALID_AUTHORITY_SCOPE_REF", ref)
    return sorted(raw)


def _valid_unresolved_evidence_refs(values: object) -> bool:
    return (
        isinstance(values, list)
        and all(isinstance(value, str) and bool(value.strip()) for value in values)
        and len(values) == len(set(values))
    )


def _validate_definition(
    definition: object,
    scope_index: dict[str, tuple[str, dict[str, object]]],
    profile: dict[str, object],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if (
        not isinstance(definition, dict)
        or set(definition) != _DEFINITION_KEYS
        or definition.get("definition_schema_version") != HANDOFF_DEFINITION_VERSION
        or not isinstance(definition.get("product_slug"), str)
        or not definition["product_slug"].strip()
        or not isinstance(definition.get("actions"), list)
        or not isinstance(definition.get("lifecycles"), list)
    ):
        _fail("INVALID_HANDOFF_DEFINITION", definition)

    validated = []
    for collection_name, id_key, profile_key, expected_keys in (
        (
            "actions",
            "action_id",
            "action_fields",
            {
                "action_id",
                "authority_scope_refs",
                "ux_action_locator",
                "fields",
                "verification_basis",
            },
        ),
        (
            "lifecycles",
            "lifecycle_id",
            "lifecycle_fields",
            {"lifecycle_id", "authority_scope_refs", "fields"},
        ),
    ):
        items = []
        seen = set()
        for raw in definition[collection_name]:
            if not isinstance(raw, dict) or set(raw) != expected_keys:
                _fail("INVALID_HANDOFF_DEFINITION", raw)
            item_id = raw.get(id_key)
            if not isinstance(item_id, str) or not item_id.strip():
                _fail("INVALID_HANDOFF_DEFINITION", raw)
            if item_id in seen:
                _fail(f"DUPLICATE_{id_key.removesuffix('_id').upper()}_ID", item_id)
            seen.add(item_id)
            fields = raw.get("fields")
            if not isinstance(fields, dict) or set(fields) != set(profile[profile_key]):
                _fail("INVALID_SEMANTIC_FIELD_INVENTORY", item_id)
            for spec in fields.values():
                if (
                    isinstance(spec, dict)
                    and spec.get("kind") == "UNRESOLVED"
                    and not _valid_unresolved_evidence_refs(spec.get("evidence_refs"))
                ):
                    _fail("INVALID_HANDOFF_DEFINITION", spec)
            item = copy.deepcopy(raw)
            item["authority_scope_refs"] = _validate_refs(
                item["authority_scope_refs"], scope_index
            )
            if collection_name == "actions":
                locator = item["ux_action_locator"]
                if (
                    not isinstance(locator, dict)
                    or set(locator) != {"screen_ref", "action_key"}
                    or locator.get("screen_ref") not in item["authority_scope_refs"]
                    or not isinstance(locator.get("action_key"), str)
                    or not locator["action_key"].strip()
                    or locator["screen_ref"] not in scope_index
                    or scope_index[locator["screen_ref"]][0] != "SCR"
                ):
                    _fail("INVALID_UX_ACTION_LOCATOR", locator)
                if not isinstance(item.get("verification_basis"), dict):
                    _fail("INVALID_VERIFICATION_BASIS", item.get("verification_basis"))
            items.append(item)
        items.sort(key=lambda item: item[id_key])
        validated.append(items)
    return validated[0], validated[1]


def _normalized_field(derived: dict[str, object]) -> dict[str, object]:
    spec = derived["derivation"]
    kind = spec["kind"]
    if kind == "DIRECT_AUTHORITY":
        derivation = {"kind": kind}
    elif kind == "MACHINE_DERIVED":
        derivation = {
            key: copy.deepcopy(value)
            for key, value in spec.items()
            if key != "source_seed_ref"
        }
    else:
        derivation = {
            "kind": kind,
            "why_structuring_is_insufficient": spec[
                "why_structuring_is_insufficient"
            ],
            "interpretation_scope": spec["interpretation_scope"],
        }
    return {
        "value": copy.deepcopy(derived["value"]),
        "source_seed_refs": list(derived["source_seed_refs"]),
        "derivation": derivation,
    }


def _compile_items(
    items: list[dict[str, object]],
    *,
    collection_name: str,
    id_key: str,
    field_kind: str,
    profile_key: str,
    current_scope_refs: list[str],
    available_seeds: dict[str, dict[str, object]],
    profile: dict[str, object],
    derived_fields: list[tuple[str, dict[str, object]]],
    semantic_gaps: list[dict[str, object]],
    expressiveness_gaps: list[dict[str, object]],
) -> list[dict[str, object]]:
    compiled = []
    for item in items:
        item_id = item[id_key]
        context = {
            "authority_scope_refs": item["authority_scope_refs"],
            "current_scope_refs": current_scope_refs,
        }
        output = {id_key: item_id, "authority_scope_refs": item["authority_scope_refs"]}
        if collection_name == "actions":
            output["ux_action_locator"] = copy.deepcopy(item["ux_action_locator"])
            context["ux_action_locator"] = item["ux_action_locator"]
            try:
                output["verification_basis"] = validate_verification_basis(
                    item["verification_basis"],
                    context=context,
                    seeds=available_seeds,
                    profile=profile,
                )
            except (KeyError, TypeError, ValueError, AttributeError) as error:
                _fail(
                    "INVALID_VERIFICATION_BASIS",
                    {"action_id": item_id, "error": str(error)},
                )
        fields = {}
        for field_name in sorted(profile[profile_key]):
            path = canonical_field_ref(collection_name, item_id, field_name)
            spec = item["fields"][field_name]
            policy = profile[profile_key][field_name]
            try:
                derived = derive_semantic_field_v21(
                    spec,
                    field_name=field_name,
                    field_kind=field_kind,
                    context=context,
                    seeds=available_seeds,
                    profile=profile,
                )
                field = _normalized_field(derived)
                fields[field_name] = field
                derived_fields.append((path, field))
            except SemanticAuthorityGap as error:
                semantic_gaps.append(
                    semantic_gap_record(
                        field_path=path,
                        spec=spec,
                        error=error,
                        policy=policy,
                        authority_scope_refs=item["authority_scope_refs"],
                    )
                )
            except ContractExpressivenessGap as error:
                expressiveness_gaps.append(
                    expressiveness_gap_record(
                        field_path=path,
                        spec=spec,
                        error=error,
                        policy=policy,
                        authority_scope_refs=item["authority_scope_refs"],
                    )
                )
            except (KeyError, TypeError, ValueError, AttributeError) as error:
                _fail(
                    "INVALID_HANDOFF_DEFINITION",
                    {"field_path": path, "error": str(error)},
                )
        output["fields"] = fields
        compiled.append(output)
    return compiled


def compile_handoff_definition_v21(
    state: dict[str, object],
    definition: dict[str, object],
) -> dict[str, object]:
    """Compile closed authority or return typed semantic/expressiveness gaps."""
    authority = require_closed_authority(state)
    available_inventory = build_closed_source_seed_inventory(state)
    available_seeds = source_seed_index(available_inventory)
    profile = load_responsibility_profile_v21()
    scope_index = _scope_record_index(state)
    actions, lifecycles = _validate_definition(definition, scope_index, profile)
    if definition["product_slug"] != authority["product_slug"]:
        _fail("PRODUCT_SLUG_MISMATCH", definition["product_slug"])

    derived_fields = []
    semantic_gaps = []
    expressiveness_gaps = []
    current_scope_refs = sorted(scope_index)
    compiled_actions = _compile_items(
        actions,
        collection_name="actions",
        id_key="action_id",
        field_kind="ACTION",
        profile_key="action_fields",
        current_scope_refs=current_scope_refs,
        available_seeds=available_seeds,
        profile=profile,
        derived_fields=derived_fields,
        semantic_gaps=semantic_gaps,
        expressiveness_gaps=expressiveness_gaps,
    )
    compiled_lifecycles = _compile_items(
        lifecycles,
        collection_name="lifecycles",
        id_key="lifecycle_id",
        field_kind="LIFECYCLE",
        profile_key="lifecycle_fields",
        current_scope_refs=current_scope_refs,
        available_seeds=available_seeds,
        profile=profile,
        derived_fields=derived_fields,
        semantic_gaps=semantic_gaps,
        expressiveness_gaps=expressiveness_gaps,
    )
    debt = semantic_debt_report(derived_fields=derived_fields, gaps=semantic_gaps)
    if semantic_gaps or expressiveness_gaps:
        return route_compilation_gaps(
            source_authority=authority,
            definition=definition,
            semantic_debt=debt,
            semantic_gaps=semantic_gaps,
            expressiveness_gaps=expressiveness_gaps,
        )

    consumed_refs = {
        ref for _, field in derived_fields for ref in field["source_seed_refs"]
    }
    consumed_refs.update(
        ref
        for action in compiled_actions
        for values in action["verification_basis"].values()
        for ref in values
    )
    consumed_inventory = [
        copy.deepcopy(available_seeds[ref]) for ref in sorted(consumed_refs)
    ]
    source_authority = copy.deepcopy(authority)
    source_authority["consumed_seed_inventory_digest"] = source_seed_inventory_digest(
        consumed_inventory
    )
    referenced_scope_refs = sorted(
        {
            ref
            for item in actions + lifecycles
            for ref in item["authority_scope_refs"]
        }
    )
    scope_commitments = [
        {
            "record_id": ref,
            "record_type": scope_index[ref][0],
            "record_sha256": sha256_json(scope_index[ref][1]),
        }
        for ref in referenced_scope_refs
    ]
    review_count = debt["review_required_count"]
    handoff_status = (
        "AUTHORITY_READY_REVIEW_PENDING"
        if review_count
        else "AUTHORITY_READY_MACHINE_VERIFIED"
    )
    contract = {
        "contract_schema_version": ACTION_CONTRACT_VERSION,
        "compiler": {"id": COMPILER_ID, "version": COMPILER_VERSION},
        "source_authority": source_authority,
        "responsibility_profile": {
            "profile_id": profile["profile_id"],
            "digest": responsibility_profile_digest_v21(),
        },
        "scope_commitments": scope_commitments,
        "source_seed_inventory": consumed_inventory,
        "actions": compiled_actions,
        "lifecycles": compiled_lifecycles,
        "semantic_debt": debt,
        "handoff_status": handoff_status,
        "semantic_assurance": {
            "status": "NOT_MEASURED" if review_count else "NOT_REQUIRED"
        },
    }
    contract["semantic_contract_hash"] = semantic_contract_hash_v21(contract)
    contract["artifact_hash"] = artifact_hash_v21(contract)
    errors = validate_action_contract_v21(contract)
    if errors:
        _fail("INVALID_ACTION_CONTRACT_V21", errors)
    return {
        "status": handoff_status,
        "contract": contract,
        "semantic_debt": debt,
        "semantic_gaps": [],
        "expressiveness_gaps": [],
        "reentry_events": [],
    }


__all__ = [
    "COMPILER_ID",
    "COMPILER_VERSION",
    "compile_handoff_definition_v21",
    "validate_verification_basis",
]
