"""Pure exact record-relative authority binding primitives for V2 state."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


CONTRACT_DIR = Path(__file__).resolve().parents[1] / "references" / "binding-contracts"
CONTRACT_FILES = {
    "product": "product-coverage-binding-v1.json",
    "ux": "ux-coverage-binding-v1.json",
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_OBJECT_TYPES = {
    "goals": "GOAL", "users": "USR", "requirements": "REQ", "unknowns": "UNK",
    "decisions": "DEC", "rules": "RULE", "flows": "FLOW", "screens": "SCR",
    "states": "STATE", "data": "DATA", "integrations": "INT",
    "acceptance_criteria": "AC", "tasks": "TASK",
}
_BASIS_EVIDENCE_SOURCE_KINDS = {
    "USER_CONFIRMED_INTENT", "DOCUMENTED_INTENT", "HISTORICAL_DECISION", "EXTERNAL_CONSTRAINT",
}
_BASIS_EVIDENCE_CLASSES = {"INTENT", "PREFERENCE", "CONSTRAINT"}

_SEMANTIC_ROOTS = {
    "GOAL": ["statement"], "USR": ["description", "actor_kind"],
    "REQ": ["statement", "scope", "ui_required"], "DEC": ["statement", "accepted_recommendation"],
    "RULE": ["statement"], "FLOW": ["entry", "preconditions", "paths", "outcomes"],
    "SCR": ["purpose", "interaction_mode", "major_actions"], "STATE": ["state_name", "conditions"],
    "DATA": ["name", "purpose", "ownership"], "INT": ["name", "purpose"], "AC": ["assertion"],
}
_BASIS_TYPES = ["GOAL", "USR", "REQ", "DEC", "RULE", "FLOW", "SCR", "STATE", "DATA", "INT", "AC", "SURF", "EVD"]
_BASIS_ROOTS = {
    **_SEMANTIC_ROOTS,
    "SURF": ["status", "kind", "rationale", "intent_classification"],
    "EVD": ["claim", "source_kind", "authority_classes"],
}
_PRODUCT_CORE_AXIS_TYPES = {
    "actor": ["USR", "DEC", "RULE"], "goal": ["GOAL", "REQ"], "entry_point": ["FLOW", "SCR", "RULE"], "precondition": ["RULE", "STATE", "FLOW"], "happy_path": ["FLOW", "REQ"], "alternative_path": ["FLOW", "RULE"], "error": ["FLOW", "STATE", "RULE"], "recovery": ["FLOW", "STATE", "RULE"], "permission": ["RULE", "DEC", "USR"], "state": ["STATE", "RULE"], "data": ["DATA", "RULE"], "side_effect": ["RULE", "DATA", "INT"], "notification": ["RULE", "FLOW", "INT"], "validation": ["RULE", "DATA", "AC"], "boundary": ["RULE", "DEC"], "persistence": ["DATA", "RULE"], "security": ["RULE", "DEC"], "privacy": ["RULE", "DEC", "DATA"], "analytics": ["RULE", "DATA", "INT"], "acceptance": ["AC"],
}
_SPECIALIST_PACK_TYPES = {
    "GRILL-AUTH-1": ["USR", "DEC", "RULE", "FLOW", "STATE", "DATA", "AC"], "GRILL-MONEY-1": ["DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"], "GRILL-FILE-UPLOAD-1": ["DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"], "GRILL-ASYNC-1": ["DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"], "GRILL-PERMISSION-1": ["USR", "DEC", "RULE", "FLOW", "STATE", "DATA", "AC"], "GRILL-DESTRUCTIVE-ACTION-1": ["DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"],
}
_UX_STATE_AXIS_TYPES = {
    "default": ["SCR", "STATE", "FLOW", "RULE"], "loading": ["STATE", "FLOW"], "empty": ["STATE", "FLOW", "RULE"], "partial": ["STATE", "FLOW", "RULE"], "success": ["STATE", "FLOW", "AC"], "error": ["STATE", "FLOW", "RULE", "AC"], "disabled": ["STATE", "RULE"], "permission_denied": ["STATE", "RULE", "DEC", "USR"], "unauthenticated": ["STATE", "RULE", "FLOW"], "offline": ["STATE", "FLOW", "RULE"], "timeout": ["STATE", "FLOW", "RULE"], "retrying": ["STATE", "FLOW", "RULE"], "submitting": ["STATE", "FLOW"], "completed": ["STATE", "FLOW", "AC"], "cancelled": ["STATE", "FLOW", "RULE"], "expired": ["STATE", "RULE", "FLOW"],
}
_UX_ACTION_AXIS_TYPES = {
    "entry": ["FLOW", "SCR", "RULE"], "precondition": ["RULE", "STATE", "FLOW"], "input": ["DATA", "SCR", "RULE"], "validation": ["RULE", "DATA", "AC"], "submit": ["FLOW", "SCR", "RULE"], "success": ["FLOW", "STATE", "AC"], "failure": ["FLOW", "STATE", "RULE", "AC"], "retry": ["FLOW", "STATE", "RULE"], "cancel": ["FLOW", "STATE", "RULE"], "back": ["FLOW", "SCR", "RULE"], "refresh": ["FLOW", "STATE", "RULE"], "duplicate_concurrent_action": ["RULE", "STATE", "FLOW"], "timeout": ["FLOW", "STATE", "RULE"], "offline": ["STATE", "FLOW", "RULE"], "permission": ["RULE", "DEC", "USR"], "session_expiration": ["STATE", "RULE", "FLOW"], "data_mutation": ["DATA", "RULE", "FLOW"], "side_effect": ["RULE", "DATA", "INT"], "notification": ["RULE", "FLOW", "INT"], "persistence": ["DATA", "RULE"], "undo": ["FLOW", "STATE", "RULE"], "destructive_confirmation": ["RULE", "DEC", "FLOW"],
}
_CONTRACT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["contract_id", "version", "semantic_roots", "basis_types", "basis_semantic_roots"],
    "properties": {
        "contract_id": {"type": "string"}, "version": {"const": "1.0"},
        "semantic_roots": {"type": "object"},
        "basis_types": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "basis_semantic_roots": {"type": "object"}, "core_axis_types": {"type": "object"},
        "specialist_pack_types": {"type": "object"}, "state_axis_types": {"type": "object"},
        "action_axis_types": {"type": "object"},
    },
}


class BindingError(ValueError):
    """A deterministic binding failure with a machine-readable code."""

    def __init__(self, code: str, detail: object):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _decode_token(token: str, pointer: str) -> str:
    decoded: list[str] = []
    position = 0
    while position < len(token):
        if token[position] != "~":
            decoded.append(token[position])
            position += 1
            continue
        if position + 1 == len(token) or token[position + 1] not in "01":
            raise BindingError("invalid_record_pointer", pointer)
        decoded.append("~" if token[position + 1] == "0" else "/")
        position += 2
    return "".join(decoded)


def resolve_record_pointer(record: object, pointer: str) -> object:
    """Resolve an RFC 6901 pointer rooted at one canonical record."""
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        raise BindingError("invalid_record_pointer", pointer)
    current = record
    if pointer == "":
        return current
    for raw_token in pointer[1:].split("/"):
        token = _decode_token(raw_token, pointer)
        if isinstance(current, dict):
            if token not in current:
                raise BindingError("invalid_record_pointer", pointer)
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit() or (len(token) > 1 and token.startswith("0")):
                raise BindingError("invalid_record_pointer", pointer)
            index = int(token)
            if index >= len(current):
                raise BindingError("invalid_record_pointer", pointer)
            current = current[index]
        else:
            raise BindingError("invalid_record_pointer", pointer)
    return current


def canonical_record_index(state: dict[str, object]) -> dict[str, tuple[str, dict[str, object]]]:
    """Return the one canonical index of stable V2 records."""
    if not isinstance(state, dict):
        raise BindingError("invalid_state", "state must be an object")
    index: dict[str, tuple[str, dict[str, object]]] = {}

    def add(record_type: str, record: object) -> None:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            return
        record_id = record["id"]
        if record_id in index:
            raise BindingError("duplicate_authority_record", record_id)
        if record_id.split("-", 1)[0] != record_type:
            return
        index[record_id] = (record_type, record)

    objects = state.get("objects")
    if isinstance(objects, dict):
        for group, record_type in _OBJECT_TYPES.items():
            records = objects.get(group)
            if isinstance(records, list):
                for record in records:
                    add(record_type, record)
    for key, record_type in (("evidence", "EVD"), ("contradictions", "CON")):
        records = state.get(key)
        if isinstance(records, list):
            for record in records:
                add(record_type, record)
    surface_manifest = state.get("surface_manifest")
    records = surface_manifest.get("records") if isinstance(surface_manifest, dict) else None
    if isinstance(records, list):
        for record in records:
            add("SURF", record)
    return index


def make_authority_binding(state: dict[str, object], record_id: str, pointer: str) -> dict[str, str]:
    index = canonical_record_index(state)
    if record_id not in index:
        raise BindingError("unknown_authority_record", record_id)
    _, record = index[record_id]
    return {"record_id": record_id, "pointer": pointer, "value_sha256": sha256_json(resolve_record_pointer(record, pointer))}


def _binding_shape(binding: object) -> tuple[str, str, str]:
    if not isinstance(binding, dict) or set(binding) != {"record_id", "pointer", "value_sha256"}:
        raise BindingError("invalid_authority_binding_shape", binding)
    record_id, pointer, value_hash = binding["record_id"], binding["pointer"], binding["value_sha256"]
    if not isinstance(record_id, str) or not isinstance(pointer, str) or not isinstance(value_hash, str) or not _HEX64.fullmatch(value_hash):
        raise BindingError("invalid_authority_binding_shape", binding)
    return record_id, pointer, value_hash


def _first_pointer_token(pointer: str) -> str:
    if pointer == "":
        raise BindingError("empty_authority_binding_pointer", pointer)
    if not pointer.startswith("/"):
        raise BindingError("invalid_record_pointer", pointer)
    return _decode_token(pointer[1:].split("/", 1)[0], pointer)


def _is_empty_semantic_value(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip()) or (isinstance(value, (list, dict)) and not value)


def _verify_basis_record(record_type: str, record: dict[str, object], root: str) -> None:
    if record_type == "SURF":
        if root != "status" or record.get("status") not in {"IN_SCOPE", "OUT_OF_SCOPE"}:
            raise BindingError("ineligible_basis_authority", record.get("id"))
        return
    if record.get("status") != "CURRENT":
        raise BindingError("stale_authority_binding", record.get("id"))
    if record_type == "EVD":
        authority_classes = record.get("authority_classes")
        if (
            record.get("source_kind") not in _BASIS_EVIDENCE_SOURCE_KINDS
            or not isinstance(authority_classes, list)
            or not _BASIS_EVIDENCE_CLASSES.intersection(authority_classes)
        ):
            raise BindingError("ineligible_basis_authority", record.get("id"))


def verify_authority_binding(
    state: dict[str, object], binding: dict[str, str], *, allowed_types: set[str],
    semantic_roots: dict[str, set[str]], basis: bool = False,
) -> tuple[str, dict[str, object]]:
    """Verify shape, exact value hash, type, status, and semantic pointer policy."""
    record_id, pointer, supplied_hash = _binding_shape(binding)
    index = canonical_record_index(state)
    if record_id not in index:
        raise BindingError("unknown_authority_record", record_id)
    record_type, record = index[record_id]
    if record_type not in allowed_types:
        raise BindingError("invalid_authority_binding_type", record_type)
    root = _first_pointer_token(pointer)
    if root not in semantic_roots.get(record_type, set()):
        raise BindingError("nonsemantic_authority_binding_pointer", pointer)
    value = resolve_record_pointer(record, pointer)
    if sha256_json(value) != supplied_hash:
        raise BindingError("authority_binding_hash_mismatch", record_id)
    if basis:
        _verify_basis_record(record_type, record, root)
    else:
        if record.get("status") != "CURRENT":
            raise BindingError("stale_authority_binding", record_id)
        if _is_empty_semantic_value(value):
            raise BindingError("empty_authority_binding_value", pointer)
    return record_type, record


def _expected_contracts() -> dict[str, dict[str, object]]:
    common = {"semantic_roots": _SEMANTIC_ROOTS, "basis_types": _BASIS_TYPES, "basis_semantic_roots": _BASIS_ROOTS}
    return {
        "product": {"contract_id": "joewrks.product-coverage-binding", "version": "1.0", "core_axis_types": _PRODUCT_CORE_AXIS_TYPES, "specialist_pack_types": _SPECIALIST_PACK_TYPES, **common},
        "ux": {"contract_id": "joewrks.ux-coverage-binding", "version": "1.0", "state_axis_types": _UX_STATE_AXIS_TYPES, "action_axis_types": _UX_ACTION_AXIS_TYPES, **common},
    }


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BindingError("binding_contract_load_error", str(exc)) from exc


def load_binding_contracts() -> dict[str, dict[str, object]]:
    """Load the two frozen contracts and reject all inventory/schema drift."""
    expected_files = {"binding-contract.schema.json", *CONTRACT_FILES.values()}
    actual_files = {path.name for path in CONTRACT_DIR.glob("*.json")}
    if actual_files != expected_files:
        raise BindingError("binding_contract_file_set_mismatch", sorted(actual_files))
    schema = _load_json(CONTRACT_DIR / "binding-contract.schema.json")
    if schema != _CONTRACT_SCHEMA:
        raise BindingError("binding_contract_schema_drift", schema)
    expected = _expected_contracts()
    contracts: dict[str, dict[str, object]] = {}
    identities: set[tuple[object, object]] = set()
    for name, filename in CONTRACT_FILES.items():
        contract = _load_json(CONTRACT_DIR / filename)
        if not isinstance(contract, dict) or "digest" in contract or contract != expected[name]:
            raise BindingError("binding_contract_drift", name)
        identity = (contract["contract_id"], contract["version"])
        if identity in identities:
            raise BindingError("duplicate_binding_contract_identity", identity)
        identities.add(identity)
        contracts[name] = contract
    return contracts


def binding_contract_identity() -> dict[str, dict[str, str]]:
    return {
        name: {"contract_id": contract["contract_id"], "version": contract["version"], "digest": sha256_json(contract)}
        for name, contract in load_binding_contracts().items()
    }
