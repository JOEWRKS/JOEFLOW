"""V2 admission profile over the frozen downstream execution/1.0 transport."""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

from downstream.invariants import evaluate_input_invariants
from downstream.protocol import (
    PROTOCOL_VERSION,
    encode_typed_numbers,
    validate_execution_record,
)
from downstream.verifier import VerificationError, verify_execution

from .contracts import semantic_contract_hash as recompute_semantic_contract_hash


_RESULT_CLASSES = {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"}
_HASH = re.compile(r"^[0-9a-f]{64}$")
_COMPONENTS = {
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
}
_EXPECTATIONS = {"CHANGED", "UNCHANGED", "ANY"}
_INVARIANT_KEYS = {
    "required": {"type", "pointer"},
    "finite_number": {"type", "pointer"},
    "positive_number": {"type", "pointer"},
    "non_negative_number": {"type", "pointer"},
    "equals": {"type", "pointer", "value"},
}
_ASSERTION_KEYS = {
    "path_present": {"type", "pointer"},
    "path_absent": {"type", "pointer"},
    "path_equals": {"type", "pointer", "value"},
    "collection_item_field_equals": {
        "type",
        "pointer",
        "match_field",
        "match_value",
        "field",
        "value",
    },
}
_LIFECYCLE_FIELDS = {
    "current_states",
    "allowed_transitions",
    "forbidden_transitions",
    "boundary_conditions",
    "reversibility",
    "reversal_window",
    "object_outcome",
    "required_reason",
    "required_confirmation",
    "required_evidence",
    "authority",
    "history_preservation",
}
_MAX_RUNTIME_EVIDENCE_DEPTH = 100
_MAX_RUNTIME_EVIDENCE_NODES = 100_000


class RuntimeVerificationError(ValueError):
    """Runtime evidence or semantic values cannot be admitted deterministically."""

    def __init__(self, code: str, detail: object):
        self.code = code
        self.detail = detail
        super().__init__(code)


def _error(code: str, detail: object) -> RuntimeVerificationError:
    return RuntimeVerificationError(code, detail)


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _unique_nonblank(values: object, *, allow_empty: bool = True) -> bool:
    return (
        isinstance(values, list)
        and (allow_empty or bool(values))
        and all(_nonblank(value) for value in values)
        and len(values) == len(set(values))
    )


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            encode_typed_numbers(value),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as error:
        raise _error("RUNTIME_EVIDENCE_INVALID", "evidence is not canonical JSON") from error


def canonical_runtime_evidence(value: object) -> object:
    """Return an exact bounded JSON deep copy suitable for report re-verification."""
    nodes = 0
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        nodes += 1
        if depth > _MAX_RUNTIME_EVIDENCE_DEPTH or nodes > _MAX_RUNTIME_EVIDENCE_NODES:
            raise _error("RUNTIME_EVIDENCE_INVALID", "evidence exceeds canonical JSON limits")
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise _error("RUNTIME_EVIDENCE_INVALID", "evidence object keys must be strings")
            stack.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            stack.extend((child, depth + 1) for child in item)
        elif item is None or isinstance(item, (str, bool, int)):
            continue
        elif isinstance(item, float) and math.isfinite(item):
            continue
        else:
            raise _error("RUNTIME_EVIDENCE_INVALID", "evidence is not canonical JSON")
    try:
        return json.loads(_canonical_bytes(value))
    except (json.JSONDecodeError, TypeError, ValueError, RecursionError) as error:
        raise _error("RUNTIME_EVIDENCE_INVALID", "evidence is not canonical JSON") from error


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _equal(left: object, right: object) -> bool:
    return _canonical_bytes(left) == _canonical_bytes(right)


def semantic_value(field: dict[str, object]) -> object:
    """Read an already materialized V2 value; never derive or interpret it."""
    if not isinstance(field, dict) or "value" not in field:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "semantic field must be an object containing value",
        )
    value = field["value"]
    if isinstance(value, str) and not value.strip():
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "semantic field value must not be blank",
        )
    return value


def source_contract_identity(contract: dict[str, object]) -> dict[str, object]:
    """Return the validated exact source-contract identity bound to evidence."""
    if not isinstance(contract, dict):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "contract must be an object")
    authority = contract.get("source_authority")
    if not isinstance(authority, dict):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "source_authority must be an object")
    schema_version = contract.get("contract_schema_version")
    if schema_version != "joewrks.action-conformance/2.0":
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "contract_schema_version must equal joewrks.action-conformance/2.0",
        )
    semantic_hash = contract.get("semantic_contract_hash")
    if not isinstance(semantic_hash, str) or _HASH.fullmatch(semantic_hash) is None:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "semantic_contract_hash must be a lowercase SHA-256",
        )
    try:
        recomputed_semantic_hash = recompute_semantic_contract_hash(contract)
    except (TypeError, ValueError, AttributeError, RecursionError) as error:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "contract semantics are not canonical JSON",
        ) from error
    if semantic_hash != recomputed_semantic_hash:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "semantic_contract_hash does not match contract semantics",
        )
    product_slug = authority.get("product_slug")
    if not _nonblank(product_slug):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "source product_slug must be nonblank")
    revision = authority.get("approved_revision")
    if type(revision) is not int or revision < 1:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "approved_revision must be a positive integer",
        )
    approved_digest = authority.get("approved_definition_digest")
    if not isinstance(approved_digest, str) or _HASH.fullmatch(approved_digest) is None:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "approved_definition_digest must be a lowercase SHA-256",
        )
    return {
        "contract_schema_version": schema_version,
        "semantic_contract_hash": semantic_hash,
        "product_slug": product_slug,
        "approved_revision": revision,
        "approved_definition_digest": approved_digest,
    }


def _validated_contract_collection(
    contract: dict[str, object],
    collection_name: str,
    id_key: str,
) -> dict[str, dict[str, object]]:
    collection = contract.get(collection_name)
    if not isinstance(collection, list):
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            f"{collection_name} must be an array",
        )
    index: dict[str, dict[str, object]] = {}
    for item in collection:
        if not isinstance(item, dict) or not _nonblank(item.get(id_key)):
            raise _error(
                "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                f"every {collection_name} item requires a nonblank {id_key}",
            )
        item_id = item[id_key]
        if item_id in index:
            code = (
                "RUNTIME_DUPLICATE_ACTION_ID"
                if id_key == "action_id"
                else "RUNTIME_DUPLICATE_LIFECYCLE_ID"
            )
            raise _error(code, {id_key: item_id})
        index[item_id] = item
    return index


def _admit_identity(contract: dict[str, object], record: dict[str, object]) -> None:
    try:
        validate_execution_record(record)
    except (TypeError, ValueError, RecursionError, AttributeError) as error:
        raise _error("RUNTIME_EVIDENCE_PROTOCOL_INVALID", str(error)) from error
    if record.get("protocol_version") != PROTOCOL_VERSION:
        raise _error(
            "RUNTIME_EVIDENCE_PROTOCOL_INVALID",
            {"expected": PROTOCOL_VERSION, "observed": record.get("protocol_version")},
        )
    identity = source_contract_identity(contract)
    record_authority = record.get("authority")
    if not isinstance(record_authority, dict):
        raise _error("RUNTIME_EVIDENCE_PROTOCOL_INVALID", "authority must be an object")
    identities = (
        (
            "product_slug",
            identity["product_slug"],
            record.get("product_slug"),
            "RUNTIME_AUTHORITY_IDENTITY_MISMATCH",
        ),
        (
            "contract_hash",
            identity["semantic_contract_hash"],
            record.get("contract_hash"),
            "RUNTIME_CONTRACT_IDENTITY_MISMATCH",
        ),
        (
            "authority.approved_revision",
            identity["approved_revision"],
            record_authority.get("approved_revision"),
            "RUNTIME_AUTHORITY_IDENTITY_MISMATCH",
        ),
        (
            "authority.approved_digest",
            identity["approved_definition_digest"],
            record_authority.get("approved_digest"),
            "RUNTIME_AUTHORITY_IDENTITY_MISMATCH",
        ),
    )
    for field, expected, observed, code in identities:
        if type(expected) is not type(observed) or expected != observed:
            raise _error(code, {"field": field, "expected": expected, "observed": observed})


def _validate_invariants(value: object, *, path: str) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{path} must be an array")
    validated = []
    for index, invariant in enumerate(value):
        item_path = f"{path}/{index}"
        if not isinstance(invariant, dict):
            raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{item_path} must be an object")
        kind = invariant.get("type")
        expected_keys = _INVARIANT_KEYS.get(kind)
        if expected_keys is None or set(invariant) != expected_keys:
            raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{item_path} invariant shape is invalid")
        pointer = invariant.get("pointer")
        if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
            raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{item_path} pointer is invalid")
        validated.append(invariant)
    return validated


def _validate_assertions(value: object, *, path: str) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{path} must be an array")
    validated = []
    for index, assertion in enumerate(value):
        item_path = f"{path}/{index}"
        if not isinstance(assertion, dict):
            raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{item_path} must be an object")
        kind = assertion.get("type")
        expected_keys = _ASSERTION_KEYS.get(kind)
        if expected_keys is None or set(assertion) != expected_keys:
            raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{item_path} assertion shape is invalid")
        pointer = assertion.get("pointer")
        if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
            raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{item_path} pointer is invalid")
        for key in ("match_field", "field"):
            if key in assertion and not _nonblank(assertion[key]):
                raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{item_path}/{key} is invalid")
        validated.append(assertion)
    return validated


def _validate_action_fields(action: dict[str, object]) -> dict[str, object]:
    fields = action.get("fields")
    if not isinstance(fields, dict):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "action fields must be an object")
    try:
        invariants = semantic_value(fields["input_invariants"])
        default_result = semantic_value(fields["default_result"])
        expectations = semantic_value(fields["result_expectations"])
    except KeyError as error:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            f"action runtime field is missing: {error.args[0]}",
        ) from error
    _validate_invariants(invariants, path="input_invariants")
    if default_result not in _RESULT_CLASSES:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "default_result is not executable")
    if not isinstance(expectations, dict) or not expectations:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "result_expectations must be a nonempty object")
    for result_class, expectation in expectations.items():
        if result_class not in _RESULT_CLASSES or not isinstance(expectation, dict):
            raise _error(
                "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                f"invalid result expectation: {result_class}",
            )
        permitted_keys = _COMPONENTS | {"assertions"}
        if set(expectation) - permitted_keys or not _COMPONENTS.issubset(expectation):
            raise _error(
                "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                f"{result_class} must define all five snapshot components",
            )
        if any(expectation[component] not in _EXPECTATIONS for component in _COMPONENTS):
            raise _error(
                "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                f"{result_class} has an invalid snapshot expectation",
            )
        _validate_assertions(
            expectation.get("assertions", []),
            path=f"result_expectations/{result_class}/assertions",
        )
    return fields


def verify_action_execution(
    contract: dict[str, object],
    record: dict[str, object],
) -> dict[str, object]:
    """Admit and verify one frozen-protocol action execution record."""
    evidence = canonical_runtime_evidence(record)
    _admit_identity(contract, evidence)
    actions = _validated_contract_collection(contract, "actions", "action_id")
    command = evidence.get("command")
    action_id = command.get("action_id") if isinstance(command, dict) else None
    if not _nonblank(action_id) or action_id not in actions:
        raise _error("RUNTIME_ACTION_NOT_FOUND", {"action_id": action_id})
    action = actions[action_id]
    fields = _validate_action_fields(action)
    expected_result = command.get("expected_result")
    if expected_result is not None and expected_result not in _RESULT_CLASSES:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            {"expected_result": expected_result},
        )
    compiled_action = {"action_id": action_id, **fields}
    try:
        result = verify_execution(
            compiled_action,
            evidence,
            expected_result=expected_result,
        )
    except (VerificationError, KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", str(error)) from error
    return {
        **result,
        "source_contract": source_contract_identity(contract),
        "test_id": evidence["test_id"],
        "evidence_sha256": _sha256(evidence),
        "runtime_evidence": evidence,
    }


def _transition_inventory(value: object, *, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{field_name} must be an array")
    inventory = []
    for index, transition in enumerate(value):
        if (
            not isinstance(transition, dict)
            or set(transition) != {"case_id", "from_state", "to_state"}
            or not all(_nonblank(transition.get(key)) for key in transition)
        ):
            raise _error(
                "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                f"{field_name}/{index} transition shape is invalid",
            )
        inventory.append(transition)
    case_ids = [item["case_id"] for item in inventory]
    if len(case_ids) != len(set(case_ids)):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", f"{field_name} case IDs must be unique")
    return inventory


def _lifecycle_profile(lifecycle: dict[str, object]) -> dict[str, object]:
    fields = lifecycle.get("fields")
    if not isinstance(fields, dict) or set(fields) != _LIFECYCLE_FIELDS:
        raise _error(
            "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "lifecycle runtime field inventory is incomplete or malformed",
        )
    values = {name: semantic_value(fields[name]) for name in sorted(_LIFECYCLE_FIELDS)}
    states = values["current_states"]
    if not _unique_nonblank(states, allow_empty=False):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "current_states must be unique nonblank strings")
    allowed = _transition_inventory(values["allowed_transitions"], field_name="allowed_transitions")
    forbidden = _transition_inventory(values["forbidden_transitions"], field_name="forbidden_transitions")
    transitions = allowed + forbidden
    case_ids = [item["case_id"] for item in transitions]
    if not case_ids or len(case_ids) != len(set(case_ids)):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "lifecycle case IDs must be nonempty and globally unique")
    if any(item["from_state"] not in states or item["to_state"] not in states for item in transitions):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "lifecycle transition references an unknown state")
    case_set = set(case_ids)
    boundaries = values["boundary_conditions"]
    if not isinstance(boundaries, dict) or set(boundaries) != case_set:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "boundary_conditions must cover every lifecycle case")
    for case_id in case_ids:
        _validate_invariants(boundaries[case_id], path=f"boundary_conditions/{case_id}")
    reversibility = values["reversibility"]
    if not isinstance(reversibility, dict) or set(reversibility) != {"reversible"} or type(reversibility["reversible"]) is not bool:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "reversibility must declare one boolean")
    reversal_window = values["reversal_window"]
    if reversibility["reversible"]:
        if not _nonblank(reversal_window):
            raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "reversible lifecycle requires a reversal window")
    elif reversal_window is not None:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "non-reversible lifecycle requires a null reversal window")
    outcomes = values["object_outcome"]
    authorities = values["authority"]
    evidence = values["required_evidence"]
    if not isinstance(outcomes, dict) or set(outcomes) != case_set:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "object_outcome must cover every lifecycle case")
    if (
        not isinstance(authorities, dict)
        or set(authorities) != case_set
        or any(not _nonblank(value) for value in authorities.values())
    ):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "authority must cover every lifecycle case")
    if not isinstance(evidence, dict) or set(evidence) != case_set:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "required_evidence must cover every lifecycle case")
    if any(not _unique_nonblank(value) for value in evidence.values()):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "required_evidence entries must be unique strings")
    required_reason = values["required_reason"]
    required_confirmation = values["required_confirmation"]
    if not _unique_nonblank(required_reason) or not set(required_reason).issubset(case_set):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "required_reason must reference lifecycle cases")
    if not _unique_nonblank(required_confirmation) or not set(required_confirmation).issubset(case_set):
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "required_confirmation must reference lifecycle cases")
    preservation = values["history_preservation"]
    if not isinstance(preservation, dict) or set(preservation) != {"required"} or type(preservation["required"]) is not bool:
        raise _error("RUNTIME_CONTRACT_NOT_EXECUTABLE", "history_preservation must declare one boolean")
    return {
        "states": states,
        "allowed": {item["case_id"]: item for item in allowed},
        "forbidden": {item["case_id"]: item for item in forbidden},
        "boundaries": boundaries,
        "outcomes": outcomes,
        "authorities": authorities,
        "evidence": evidence,
        "required_reason": set(required_reason),
        "required_confirmation": set(required_confirmation),
        "history_required": preservation["required"],
    }


def required_lifecycle_cases(contract: dict[str, object]) -> list[dict[str, str]]:
    """Return the deterministic complete structured lifecycle case inventory."""
    lifecycles = _validated_contract_collection(contract, "lifecycles", "lifecycle_id")
    inventory = []
    for lifecycle_id in sorted(lifecycles):
        profile = _lifecycle_profile(lifecycles[lifecycle_id])
        for case_id in sorted(set(profile["allowed"]) | set(profile["forbidden"])):
            inventory.append({"lifecycle_id": lifecycle_id, "case_id": case_id})
    return inventory


def verify_lifecycle_execution(
    contract: dict[str, object],
    observation: dict[str, object],
) -> dict[str, object]:
    """Admit and verify one structured lifecycle observation."""
    evidence = canonical_runtime_evidence(observation)
    _admit_identity(contract, evidence)
    lifecycles = _validated_contract_collection(contract, "lifecycles", "lifecycle_id")
    command = evidence.get("command")
    lifecycle_id = command.get("lifecycle_id") if isinstance(command, dict) else None
    if not _nonblank(lifecycle_id) or lifecycle_id not in lifecycles:
        raise _error("RUNTIME_LIFECYCLE_NOT_FOUND", {"lifecycle_id": lifecycle_id})
    profile = _lifecycle_profile(lifecycles[lifecycle_id])
    case_id = command.get("case_id")
    allowed_case = profile["allowed"].get(case_id)
    forbidden_case = profile["forbidden"].get(case_id)
    transition = allowed_case or forbidden_case
    if transition is None:
        raise _error("RUNTIME_LIFECYCLE_CASE_NOT_FOUND", {"case_id": case_id})
    failures = []
    for key in ("from_state", "to_state"):
        if command.get(key) != transition[key]:
            failures.append(f"{key} does not match lifecycle case")
    result = evidence.get("result")
    if not isinstance(result, dict):
        raise _error("RUNTIME_EVIDENCE_INVALID", "lifecycle result must be an object")
    expected_allowed = allowed_case is not None
    observed_allowed = result.get("allowed")
    if type(observed_allowed) is not bool:
        raise _error("RUNTIME_EVIDENCE_INVALID", "lifecycle result.allowed must be boolean")
    if observed_allowed != expected_allowed:
        failures.append("allowed verdict does not match lifecycle case")
    command_input = command.get("input")
    if not isinstance(command_input, dict):
        raise _error("RUNTIME_EVIDENCE_INVALID", "lifecycle command.input must be an object")
    boundary_failures = evaluate_input_invariants(profile["boundaries"][case_id], command_input)
    if boundary_failures:
        failures.append("lifecycle boundary conditions failed")
    if not _equal(result.get("object_outcome"), profile["outcomes"][case_id]):
        failures.append("object outcome does not match lifecycle authority")
    if result.get("authority") != profile["authorities"][case_id]:
        failures.append("actor authority does not match lifecycle authority")
    if case_id in profile["required_reason"] and not _nonblank(result.get("reason")):
        failures.append("required lifecycle reason is absent")
    if case_id in profile["required_confirmation"] and result.get("confirmed") is not True:
        failures.append("required lifecycle confirmation is absent")
    observed_evidence = result.get("evidence_refs")
    if not _unique_nonblank(observed_evidence):
        raise _error("RUNTIME_EVIDENCE_INVALID", "lifecycle evidence_refs must be unique strings")
    if not set(profile["evidence"][case_id]).issubset(observed_evidence):
        failures.append("required lifecycle evidence is absent")
    if profile["history_required"] and result.get("history_preserved") is not True:
        failures.append("lifecycle history preservation is absent")
    return {
        "source_contract": source_contract_identity(contract),
        "lifecycle_id": lifecycle_id,
        "case_id": case_id,
        "test_id": evidence["test_id"],
        "evidence_sha256": _sha256(evidence),
        "runtime_evidence": evidence,
        "expected_allowed": expected_allowed,
        "observed_allowed": observed_allowed,
        "boundary_failures": boundary_failures,
        "failures": failures,
        "conformant": not failures,
    }


def _source_contract_snapshot(contract: object) -> dict[str, object]:
    mapping = contract if isinstance(contract, dict) else {}
    authority = mapping.get("source_authority")
    authority = authority if isinstance(authority, dict) else {}
    return {
        "contract_schema_version": mapping.get("contract_schema_version"),
        "semantic_contract_hash": mapping.get("semantic_contract_hash"),
        "product_slug": authority.get("product_slug"),
        "approved_revision": authority.get("approved_revision"),
        "approved_definition_digest": authority.get("approved_definition_digest"),
    }


def contained_runtime_error_result(
    contract: dict[str, object],
    runtime_evidence: object,
    error: RuntimeVerificationError,
    *,
    lifecycle: bool,
) -> dict[str, object]:
    """Return the canonical fail-closed result for one rejected evidence object."""
    evidence = canonical_runtime_evidence(runtime_evidence)
    mapping = evidence if isinstance(evidence, dict) else {}
    command = mapping.get("command") if isinstance(mapping.get("command"), dict) else {}
    try:
        source_contract = source_contract_identity(contract)
    except RuntimeVerificationError:
        source_contract = _source_contract_snapshot(contract)
    common = {
        "source_contract": source_contract,
        "test_id": (
            mapping.get("test_id")
            if isinstance(mapping.get("test_id"), str) and mapping["test_id"].strip()
            else "__invalid_test__"
        ),
        "evidence_sha256": _sha256(evidence),
        "runtime_evidence": evidence,
        "failures": [error.code],
        "error": {
            "code": error.code,
            "detail": canonical_runtime_evidence(error.detail),
        },
        "conformant": False,
    }
    if lifecycle:
        return {
            "lifecycle_id": (
                command.get("lifecycle_id")
                if isinstance(command.get("lifecycle_id"), str) and command["lifecycle_id"].strip()
                else "__invalid_lifecycle__"
            ),
            "case_id": (
                command.get("case_id")
                if isinstance(command.get("case_id"), str) and command["case_id"].strip()
                else "__invalid_case__"
            ),
            **common,
        }
    return {
        "action_id": (
            command.get("action_id")
            if isinstance(command.get("action_id"), str) and command["action_id"].strip()
            else "__invalid_action__"
        ),
        **common,
    }
