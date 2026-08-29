"""Pure exact record-relative authority binding primitives for V2 state."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from materiality_v2 import classify_materiality


CONTRACT_DIR = Path(__file__).resolve().parents[1] / "references" / "binding-contracts"
CONTRACT_FILES = {
    "product": "product-coverage-binding-v1.json",
    "ux": "ux-coverage-binding-v1.json",
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ARRAY_INDEX = re.compile(r"^(?:0|[1-9][0-9]*)$")
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
            if not _ARRAY_INDEX.fullmatch(token):
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


_CORE_COVERAGE_CELL_KEYS = {
    "status", "authority_bindings", "unknown_refs", "basis_bindings", "rationale",
}
_SPECIALIST_COVERAGE_CELL_KEYS = _CORE_COVERAGE_CELL_KEYS
_UX_COVERAGE_CELL_KEYS = _CORE_COVERAGE_CELL_KEYS


def _coverage_error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _meaningful_rationale(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _unique_strings(value: object, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not nonempty)
        and all(isinstance(item, str) for item in value)
        and len(value) == len(set(value))
    )


def _material_core_targets(state: dict[str, object]) -> list[str]:
    objects = state.get("objects")
    requirements = objects.get("requirements") if isinstance(objects, dict) else None
    if not isinstance(requirements, list):
        return []
    targets: list[str] = []
    for record in requirements:
        if not isinstance(record, dict) or record.get("status") != "CURRENT":
            continue
        record_id = record.get("id")
        materiality = record.get("materiality")
        try:
            is_material = isinstance(materiality, dict) and classify_materiality(materiality) == "MATERIAL"
        except (KeyError, TypeError, ValueError):
            is_material = False
        if isinstance(record_id, str) and is_material:
            targets.append(record_id)
    return sorted(set(targets))


def _open_unknowns_are_current(state: dict[str, object], refs: object) -> bool:
    if not _unique_strings(refs, nonempty=True):
        return False
    index = canonical_record_index(state)
    return all(
        reference in index
        and index[reference][0] == "UNK"
        and index[reference][1].get("status") == "OPEN"
        for reference in refs
    )


def _verify_bindings(
    state: dict[str, object], bindings: object, *, allowed_types: set[str],
    semantic_roots: dict[str, set[str]], basis: bool,
) -> list[str]:
    if not isinstance(bindings, list) or not bindings:
        return ["missing_authority_binding"]
    codes: list[str] = []
    for binding in bindings:
        try:
            verify_authority_binding(
                state, binding, allowed_types=allowed_types,
                semantic_roots=semantic_roots, basis=basis,
            )
        except BindingError as exc:
            codes.append(exc.code)
    return codes


def _binding_metric_codes(codes: list[str], metrics: dict[str, set[str]], cell_path: str) -> None:
    if not codes:
        return
    metrics["invalid_authority_binding"].add(cell_path)
    if "stale_authority_binding" in codes:
        metrics["stale_authority_binding"].add(cell_path)
    if "invalid_authority_binding_type" in codes:
        metrics["invalid_coverage_authority_type"].add(cell_path)


def _product_binding_analysis(state: dict[str, object]) -> tuple[list[dict[str, str]], dict[str, int]]:
    """Validate exact M4 Core and specialist coverage proof without M3 topology logic."""
    contract = load_binding_contracts()["product"]
    roots = {record_type: set(values) for record_type, values in contract["semantic_roots"].items()}
    basis_roots = {record_type: set(values) for record_type, values in contract["basis_semantic_roots"].items()}
    basis_types = set(contract["basis_types"])
    core_types = {axis: set(values) for axis, values in contract["core_axis_types"].items()}
    specialist_types = {pack: set(values) for pack, values in contract["specialist_pack_types"].items()}
    errors: list[dict[str, str]] = []
    metric_cells = {
        "invalid_authority_binding": set(), "stale_authority_binding": set(),
        "coverage_without_authority": set(), "open_coverage_without_unknown": set(),
        "unjustified_na_without_basis": set(), "invalid_coverage_authority_type": set(),
        "core_coverage_gaps": set(), "specialist_binding_gaps": set(),
    }

    coverage = state.get("coverage")
    rows = coverage if isinstance(coverage, list) else []
    by_target: dict[str, list[tuple[int, dict[str, object]]]] = {}
    for position, row in enumerate(rows):
        if isinstance(row, dict) and isinstance(row.get("feature_id"), str):
            by_target.setdefault(row["feature_id"], []).append((position, row))

    def validate_core_row(position: int, row: object) -> None:
        row_path = f"coverage[{position}]"
        if not isinstance(row, dict):
            errors.append(_coverage_error("invalid_core_coverage_row", "Core coverage rows must be objects", row_path))
            metric_cells["core_coverage_gaps"].add(row_path)
            return
        cells = row.get("cells")
        if not isinstance(cells, dict) or set(cells) != set(core_types):
            errors.append(_coverage_error("core_coverage_axis_inventory_mismatch", "Core cells must equal the frozen 20-axis inventory", f"coverage[{position}].cells"))
            metric_cells["core_coverage_gaps"].add(row_path)
            return
        for axis, allowed_types in core_types.items():
            cell_path = f"coverage[{position}].cells.{axis}"
            cell = cells[axis]
            if not isinstance(cell, dict) or set(cell) != _CORE_COVERAGE_CELL_KEYS:
                errors.append(_coverage_error("invalid_core_coverage_cell", "Core coverage cell must use the exact M4 shape", cell_path))
                metric_cells["invalid_authority_binding"].add(cell_path)
                if isinstance(cell, dict) and cell.get("status") == "COVERED":
                    metric_cells["coverage_without_authority"].add(cell_path)
                elif isinstance(cell, dict) and cell.get("status") == "OPEN":
                    metric_cells["open_coverage_without_unknown"].add(cell_path)
                elif isinstance(cell, dict) and cell.get("status") == "N/A":
                    metric_cells["unjustified_na_without_basis"].add(cell_path)
                continue
            status = cell.get("status")
            bindings, unknowns, basis, rationale = (
                cell.get("authority_bindings"), cell.get("unknown_refs"),
                cell.get("basis_bindings"), cell.get("rationale"),
            )
            if status == "COVERED":
                codes = _verify_bindings(state, bindings, allowed_types=allowed_types, semantic_roots=roots, basis=False)
                invalid = bool(codes) or unknowns != [] or basis != [] or rationale is not None
                if invalid:
                    if codes == ["missing_authority_binding"]:
                        metric_cells["coverage_without_authority"].add(cell_path)
                    _binding_metric_codes(codes, metric_cells, cell_path)
                    errors.append(_coverage_error(codes[0] if codes else "invalid_core_coverage_cell", "COVERED requires only verified exact authority bindings", cell_path))
            elif status == "OPEN":
                if bindings != [] or basis != [] or rationale is not None or not _open_unknowns_are_current(state, unknowns):
                    metric_cells["open_coverage_without_unknown"].add(cell_path)
                    errors.append(_coverage_error("open_coverage_without_unknown", "OPEN requires current OPEN unknown refs only", cell_path))
            elif status == "N/A":
                codes = _verify_bindings(state, basis, allowed_types=basis_types, semantic_roots=basis_roots, basis=True)
                if bindings != [] or unknowns != [] or not _meaningful_rationale(rationale) or codes:
                    metric_cells["unjustified_na_without_basis"].add(cell_path)
                    _binding_metric_codes(codes, metric_cells, cell_path)
                    errors.append(_coverage_error(codes[0] if codes else "unjustified_na_without_basis", "N/A requires rationale and verified exact basis bindings", cell_path))
            else:
                errors.append(_coverage_error("invalid_core_coverage_cell", "Core status must be COVERED, OPEN, or N/A", cell_path))

    for position, row in enumerate(rows):
        validate_core_row(position, row)

    for target in _material_core_targets(state):
        target_rows = by_target.get(target, [])
        target_path = f"coverage.{target}"
        if not target_rows:
            errors.append(_coverage_error("missing_core_coverage", "current MATERIAL requirement requires one Core coverage row", target_path))
            metric_cells["core_coverage_gaps"].add(target_path)
        elif len(target_rows) != 1:
            errors.append(_coverage_error("duplicate_core_coverage", "current MATERIAL requirement requires exactly one Core coverage row", target_path))
            metric_cells["core_coverage_gaps"].add(target_path)

    grill_coverage = state.get("grill_coverage")
    specialist_rows = grill_coverage if isinstance(grill_coverage, list) else []
    for row_position, row in enumerate(specialist_rows):
        if not isinstance(row, dict) or row.get("pack_id") not in specialist_types or not isinstance(row.get("axes"), dict):
            continue
        pack_id = row["pack_id"]
        for axis, cell in row["axes"].items():
            cell_path = f"grill_coverage[{row_position}].axes.{axis}"
            invalid_cell = False
            if not isinstance(cell, dict) or set(cell) != _SPECIALIST_COVERAGE_CELL_KEYS:
                errors.append(_coverage_error("invalid_specialist_coverage_cell", "specialist coverage cell must use the exact M4 shape", cell_path))
                metric_cells["specialist_binding_gaps"].add(cell_path)
                continue
            status = cell.get("status")
            bindings, unknowns, basis, rationale = (
                cell.get("authority_bindings"), cell.get("unknown_refs"),
                cell.get("basis_bindings"), cell.get("rationale"),
            )
            if status == "ADDRESSED":
                codes = _verify_bindings(state, bindings, allowed_types=specialist_types[pack_id], semantic_roots=roots, basis=False)
                invalid_cell = bool(codes) or unknowns != [] or basis != [] or rationale is not None
                if codes == ["missing_authority_binding"]:
                    metric_cells["coverage_without_authority"].add(cell_path)
                _binding_metric_codes(codes, metric_cells, cell_path)
                error_code = codes[0] if codes else "invalid_specialist_coverage_cell"
                message = "ADDRESSED requires only verified exact authority bindings"
            elif status == "OPEN":
                invalid_cell = bindings != [] or basis != [] or rationale is not None or not _open_unknowns_are_current(state, unknowns)
                if invalid_cell:
                    metric_cells["open_coverage_without_unknown"].add(cell_path)
                error_code = "open_coverage_without_unknown"
                message = "OPEN requires current OPEN unknown refs only"
            elif status == "N/A":
                codes = _verify_bindings(state, basis, allowed_types=basis_types, semantic_roots=basis_roots, basis=True)
                invalid_cell = bindings != [] or unknowns != [] or not _meaningful_rationale(rationale) or bool(codes)
                if invalid_cell:
                    metric_cells["unjustified_na_without_basis"].add(cell_path)
                _binding_metric_codes(codes, metric_cells, cell_path)
                error_code = codes[0] if codes else "unjustified_na_without_basis"
                message = "N/A requires rationale and verified exact basis bindings"
            else:
                invalid_cell = True
                error_code = "invalid_specialist_coverage_cell"
                message = "specialist status must be ADDRESSED, OPEN, or N/A"
            if invalid_cell:
                metric_cells["specialist_binding_gaps"].add(cell_path)
                errors.append(_coverage_error(error_code, message, cell_path))
    return errors, {name: len(cells) for name, cells in metric_cells.items()}


def validate_product_coverage_bindings(state: dict[str, object]) -> list[dict[str, str]]:
    """Return exact M4 authority-binding errors for Core and specialist coverage."""
    return _product_binding_analysis(state)[0]


def product_binding_metrics(state: dict[str, object]) -> dict[str, int]:
    """Count affected semantic coverage cells once for each M4 metric."""
    return _product_binding_analysis(state)[1]


def _current_screen_targets(state: dict[str, object]) -> dict[str, dict[str, object]]:
    objects = state.get("objects")
    screens = objects.get("screens") if isinstance(objects, dict) else None
    if not isinstance(screens, list):
        return {}
    return {
        record_id: record
        for record in screens
        if isinstance(record, dict)
        and record.get("status") == "CURRENT"
        and isinstance((record_id := record.get("id")), str)
    }


def _ux_binding_analysis(state: dict[str, object]) -> tuple[list[dict[str, str]], dict[str, int]]:
    """Validate exact M4 UX state/action coverage with record-relative authority proof."""
    contract = load_binding_contracts()["ux"]
    roots = {record_type: set(values) for record_type, values in contract["semantic_roots"].items()}
    basis_roots = {record_type: set(values) for record_type, values in contract["basis_semantic_roots"].items()}
    basis_types = set(contract["basis_types"])
    state_types = {axis: set(values) for axis, values in contract["state_axis_types"].items()}
    action_types = {axis: set(values) for axis, values in contract["action_axis_types"].items()}
    errors: list[dict[str, str]] = []
    metric_cells = {
        "ux_coverage_gaps": set(), "screen_state_gaps": set(),
        "screen_action_inventory_gaps": set(), "ux_invalid_authority_binding": set(),
        "ux_stale_authority_binding": set(), "ux_open_without_unknown": set(),
        "ux_unjustified_na": set(),
    }
    coverage = state.get("ux_coverage")
    rows = coverage if isinstance(coverage, list) else []
    by_screen: dict[str, list[tuple[int, dict[str, object]]]] = {}
    for position, row in enumerate(rows):
        if isinstance(row, dict) and isinstance(row.get("screen_id"), str):
            by_screen.setdefault(row["screen_id"], []).append((position, row))

    def validate_cell(cell: object, allowed_types: set[str], cell_path: str) -> None:
        if not isinstance(cell, dict) or set(cell) != _UX_COVERAGE_CELL_KEYS:
            errors.append(_coverage_error("invalid_ux_coverage_cell", "UX coverage cell must use the exact M4 shape", cell_path))
            metric_cells["ux_invalid_authority_binding"].add(cell_path)
            if isinstance(cell, dict) and cell.get("status") == "OPEN":
                metric_cells["ux_open_without_unknown"].add(cell_path)
            elif isinstance(cell, dict) and cell.get("status") == "N/A":
                metric_cells["ux_unjustified_na"].add(cell_path)
            return
        status = cell.get("status")
        bindings, unknowns, basis, rationale = (
            cell.get("authority_bindings"), cell.get("unknown_refs"),
            cell.get("basis_bindings"), cell.get("rationale"),
        )
        if status == "COVERED":
            codes = _verify_bindings(state, bindings, allowed_types=allowed_types, semantic_roots=roots, basis=False)
            if codes or unknowns != [] or basis != [] or rationale is not None:
                _binding_metric_codes(codes, {"invalid_authority_binding": metric_cells["ux_invalid_authority_binding"], "stale_authority_binding": metric_cells["ux_stale_authority_binding"], "invalid_coverage_authority_type": set()}, cell_path)
                errors.append(_coverage_error(codes[0] if codes else "invalid_ux_coverage_cell", "COVERED requires only verified exact authority bindings", cell_path))
        elif status == "OPEN":
            if bindings != [] or basis != [] or rationale is not None or not _open_unknowns_are_current(state, unknowns):
                metric_cells["ux_open_without_unknown"].add(cell_path)
                errors.append(_coverage_error("ux_open_without_unknown", "OPEN requires current OPEN unknown refs only", cell_path))
        elif status == "N/A":
            codes = _verify_bindings(state, basis, allowed_types=basis_types, semantic_roots=basis_roots, basis=True)
            if bindings != [] or unknowns != [] or not _meaningful_rationale(rationale) or codes:
                metric_cells["ux_unjustified_na"].add(cell_path)
                _binding_metric_codes(codes, {"invalid_authority_binding": metric_cells["ux_invalid_authority_binding"], "stale_authority_binding": metric_cells["ux_stale_authority_binding"], "invalid_coverage_authority_type": set()}, cell_path)
                errors.append(_coverage_error(codes[0] if codes else "ux_unjustified_na", "N/A requires rationale and verified exact basis bindings", cell_path))
        else:
            errors.append(_coverage_error("invalid_ux_coverage_cell", "UX status must be COVERED, OPEN, or N/A", cell_path))
            metric_cells["ux_invalid_authority_binding"].add(cell_path)

    def validate_axes(cells: object, expected: dict[str, set[str]], path: str, mismatch_code: str, mismatch_message: str, gap_metric: str) -> None:
        if not isinstance(cells, dict) or set(cells) != set(expected):
            errors.append(_coverage_error(mismatch_code, mismatch_message, path))
            metric_cells[gap_metric].add(path.rsplit(".", 1)[0])
        if not isinstance(cells, dict):
            return
        for axis, cell in cells.items():
            cell_path = f"{path}.{axis}"
            allowed_types = expected.get(axis)
            if allowed_types is None:
                if not isinstance(cell, dict) or set(cell) != _UX_COVERAGE_CELL_KEYS:
                    errors.append(_coverage_error("invalid_ux_coverage_cell", "UX coverage cell must use the exact M4 shape", cell_path))
                    metric_cells["ux_invalid_authority_binding"].add(cell_path)
                continue
            validate_cell(cell, allowed_types, cell_path)

    def validate_row(position: int, row: object) -> None:
        row_path = f"ux_coverage[{position}]"
        if not isinstance(row, dict):
            errors.append(_coverage_error("invalid_ux_coverage_row", "UX coverage rows must be objects", row_path))
            metric_cells["ux_coverage_gaps"].add(row_path)
            return
        if set(row) != {"screen_id", "states", "actions"}:
            errors.append(_coverage_error("invalid_ux_coverage_row", "UX coverage rows require exactly screen_id, states, and actions", row_path))
            metric_cells["ux_coverage_gaps"].add(row_path)
        validate_axes(
            row.get("states"), state_types, f"{row_path}.states",
            "screen_state_axis_inventory_mismatch", "screen states must equal the frozen 16-axis inventory",
            "screen_state_gaps",
        )
        actions = row.get("actions")
        if not isinstance(actions, list):
            errors.append(_coverage_error("invalid_ux_action_row", "UX actions must be an array", f"{row_path}.actions"))
            metric_cells["screen_action_inventory_gaps"].add(row_path)
            return
        keys: list[str] = []
        for action_position, action in enumerate(actions):
            action_path = f"{row_path}.actions[{action_position}]"
            if not isinstance(action, dict):
                errors.append(_coverage_error("invalid_ux_action_row", "UX action rows must be objects", action_path))
                metric_cells["screen_action_inventory_gaps"].add(action_path)
                continue
            if set(action) != {"key", "cells"} or not isinstance(action.get("key"), str):
                errors.append(_coverage_error("invalid_ux_action_row", "UX action rows require exactly key and cells", action_path))
                metric_cells["screen_action_inventory_gaps"].add(action_path)
            else:
                keys.append(action["key"])
            validate_axes(
                action.get("cells"), action_types, f"{action_path}.cells",
                "action_axis_inventory_mismatch", "action cells must equal the frozen 22-axis inventory",
                "screen_action_inventory_gaps",
            )
        screen_id = row.get("screen_id")
        target = _current_screen_targets(state).get(screen_id) if isinstance(screen_id, str) else None
        if target is not None:
            expected_keys = target.get("major_actions")
            if not isinstance(expected_keys, list) or len(keys) != len(set(keys)) or set(keys) != set(expected_keys):
                errors.append(_coverage_error("screen_action_inventory_mismatch", "UX action keys must exactly equal screen major_actions", f"{row_path}.actions"))
                metric_cells["screen_action_inventory_gaps"].add(row_path)

    for position, row in enumerate(rows):
        validate_row(position, row)

    for screen_id in sorted(_current_screen_targets(state)):
        target_rows = by_screen.get(screen_id, [])
        target_path = f"ux_coverage.{screen_id}"
        if not target_rows:
            errors.append(_coverage_error("missing_ux_coverage", "current screen requires one UX coverage row", target_path))
            metric_cells["ux_coverage_gaps"].add(target_path)
        elif len(target_rows) != 1:
            errors.append(_coverage_error("duplicate_ux_coverage", "current screen requires exactly one UX coverage row", target_path))
            metric_cells["ux_coverage_gaps"].add(target_path)
    return errors, {name: len(cells) for name, cells in metric_cells.items()}


def validate_ux_coverage_bindings(state: dict[str, object]) -> list[dict[str, str]]:
    """Return exact M4 authority-binding errors for UX coverage."""
    return _ux_binding_analysis(state)[0]


def ux_binding_metrics(state: dict[str, object]) -> dict[str, int]:
    """Count affected UX coverage rows and cells once for each M4 metric."""
    return _ux_binding_analysis(state)[1]
