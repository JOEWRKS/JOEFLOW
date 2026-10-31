#!/usr/bin/env python3
"""Read-only per-binding diagnosis for Core, specialist, and UX coverage cells.

The frozen validator reports one code per cell; this module names the binding,
the record, and the allowed values so an author can fix the cell directly.
"""

from __future__ import annotations

from typing import Any, Iterator

from authority_binding_v2 import (
    BindingError,
    canonical_record_index,
    load_binding_contracts,
    resolve_record_pointer,
    sha256_json,
    verify_authority_binding,
)


CELL_STATUS_SHAPES = {
    "COVERED": "authority_bindings verified and non-empty; unknown_refs [], basis_bindings [], rationale null",
    "ADDRESSED": "authority_bindings verified and non-empty; unknown_refs [], basis_bindings [], rationale null",
    "OPEN": "unknown_refs naming current OPEN unknowns; authority_bindings [], basis_bindings [], rationale null",
    "N/A": "basis_bindings verified and non-empty plus a meaningful rationale; authority_bindings [], unknown_refs []",
}


def _sets(values: dict[str, list[str]]) -> dict[str, set[str]]:
    return {key: set(items) for key, items in values.items()}


def iter_coverage_cells(state: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield every coverage cell with the binding policy that applies to it."""
    contracts = load_binding_contracts()
    product, ux = contracts["product"], contracts["ux"]
    product_policy = {
        "roots": _sets(product["semantic_roots"]),
        "basis_types": set(product["basis_types"]),
        "basis_roots": _sets(product["basis_semantic_roots"]),
    }
    ux_policy = {
        "roots": _sets(ux["semantic_roots"]),
        "basis_types": set(ux["basis_types"]),
        "basis_roots": _sets(ux["basis_semantic_roots"]),
    }

    def rows(name: str) -> list[tuple[int, dict[str, Any]]]:
        value = state.get(name)
        return [(i, row) for i, row in enumerate(value) if isinstance(row, dict)] if isinstance(value, list) else []

    def declared(row: dict[str, Any]) -> dict[str, Any] | None:
        # A default_authority re-hashes like a COVERED cell; the binding list is shared on purpose.
        bindings = row.get("default_authority")
        return ({"status": "COVERED", "authority_bindings": bindings, "unknown_refs": [], "basis_bindings": [], "rationale": None}
                if isinstance(bindings, list) else None)

    for i, row in rows("coverage"):
        cells = row.get("cells") if isinstance(row.get("cells"), dict) else {}
        for axis, cell in cells.items():
            yield {"path": f"coverage[{i}].cells.{axis}", "cell": cell,
                   "allowed_types": set(product["core_axis_types"].get(axis, [])), **product_policy}
        if declared(row):
            yield {"path": f"coverage[{i}].default_authority", "cell": declared(row),
                   "allowed_types": {t for v in product["core_axis_types"].values() for t in v}, **product_policy}
    for i, row in rows("grill_coverage"):
        axes = row.get("axes") if isinstance(row.get("axes"), dict) else {}
        allowed = set(product["specialist_pack_types"].get(row.get("pack_id"), []))
        for axis, cell in axes.items():
            yield {"path": f"grill_coverage[{i}].axes.{axis}", "cell": cell,
                   "allowed_types": allowed, **product_policy}
    for i, row in rows("ux_coverage"):
        states = row.get("states") if isinstance(row.get("states"), dict) else {}
        for axis, cell in states.items():
            yield {"path": f"ux_coverage[{i}].states.{axis}", "cell": cell,
                   "allowed_types": set(ux["state_axis_types"].get(axis, [])), **ux_policy}
        if declared(row):
            yield {"path": f"ux_coverage[{i}].default_authority", "cell": declared(row),
                   "allowed_types": {t for v in ux["state_axis_types"].values() for t in v}, **ux_policy}
        actions = row.get("actions") if isinstance(row.get("actions"), list) else []
        for j, action in enumerate(actions):
            cells = action.get("cells") if isinstance(action, dict) and isinstance(action.get("cells"), dict) else {}
            for axis, cell in cells.items():
                yield {"path": f"ux_coverage[{i}].actions[{j}].cells.{axis}", "cell": cell,
                       "allowed_types": set(ux["action_axis_types"].get(axis, [])), **ux_policy}
            if isinstance(action, dict) and declared(action):
                yield {"path": f"ux_coverage[{i}].actions[{j}].default_authority", "cell": declared(action),
                       "allowed_types": {t for v in ux["action_axis_types"].values() for t in v}, **ux_policy}


def diagnose_binding(
    state: dict[str, Any], binding: Any, *, allowed_types: set[str],
    roots: dict[str, set[str]], basis: bool, index: dict[str, tuple[str, dict[str, Any]]] | None = None,
) -> dict[str, Any] | None:
    """Return None for a valid binding, else what is wrong and what would be accepted."""
    try:
        verify_authority_binding(state, binding, allowed_types=allowed_types, semantic_roots=roots, basis=basis)
        return None
    except BindingError as exc:
        code = exc.code
    index = index if index is not None else canonical_record_index(state)
    record_id = binding.get("record_id") if isinstance(binding, dict) else None
    pointer = binding.get("pointer") if isinstance(binding, dict) else None
    finding: dict[str, Any] = {"code": code, "record_id": record_id, "pointer": pointer, "basis": basis}
    entry = index.get(record_id) if isinstance(record_id, str) else None
    if entry is not None:
        record_type, record = entry
        finding["record_type"] = record_type
        finding["record_status"] = record.get("status")
        finding["allowed_record_types"] = sorted(allowed_types)
        finding["allowed_pointer_roots"] = sorted(roots.get(record_type, set()))
        if code == "authority_binding_hash_mismatch":
            try:
                finding["current_value_sha256"] = sha256_json(resolve_record_pointer(record, pointer))
                finding["bound_value_sha256"] = binding.get("value_sha256")
            except (BindingError, TypeError, ValueError):
                pass
    return finding


def diagnose_cell(
    state: dict[str, Any], spec: dict[str, Any], index: dict[str, tuple[str, dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    cell = spec["cell"]
    if not isinstance(cell, dict):
        return []
    index = index if index is not None else canonical_record_index(state)
    findings = []
    for field, basis in (("authority_bindings", False), ("basis_bindings", True)):
        bindings = cell.get(field)
        for position, binding in enumerate(bindings if isinstance(bindings, list) else []):
            finding = diagnose_binding(
                state, binding,
                allowed_types=spec["basis_types"] if basis else spec["allowed_types"],
                roots=spec["basis_roots"] if basis else spec["roots"],
                basis=basis, index=index,
            )
            if finding is not None:
                findings.append({"field": f"{field}[{position}]", **finding})
    return findings
