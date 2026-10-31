"""Compact coverage rows: cells a row may omit because something declared once implies them.

Three sources, all optional, all inside State 0.2.0 (a state without them is unchanged):
  * `surface_manifest.grill_profile.AUTH|PERMISSION` = N/A  -> UX account, permission and
    session axes are N/A (ux_profile_inheritance);
  * an action row's `shape` (ux-action-shapes-v1.json) -> that shape's axes are N/A;
  * a row's `default_authority` (authority bindings)  -> every other omitted axis is COVERED
    by those bindings.
`expand_coverage` returns the canonical explicit state: omitted cells are written out and
tagged `inherited_from`, so validators, digests and downstream read one shape. With
`strip=True` the tags and the declarations are removed, so a compact state and its
explicit twin hash the same. `compact_coverage` is the inverse for cells whose expansion
reproduces them exactly.
"""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ux_profile_inheritance import inheritable_ux_axes

SHAPES_PATH = Path(__file__).resolve().parents[1] / "references" / "ux-action-shapes-v1.json"
ROW_FIELDS = {"shape", "default_authority"}
TAG = "inherited_from"
_UX_STATE_AXES = (
    "default", "loading", "empty", "partial", "success", "error", "disabled", "permission_denied",
    "unauthenticated", "offline", "timeout", "retrying", "submitting", "completed", "cancelled", "expired",
)
_UX_ACTION_AXES = (
    "entry", "precondition", "input", "validation", "submit", "success", "failure", "retry", "cancel",
    "back", "refresh", "duplicate_concurrent_action", "timeout", "offline", "permission",
    "session_expiration", "data_mutation", "side_effect", "notification", "persistence", "undo",
    "destructive_confirmation",
)
_CORE_AXES = (
    "actor", "goal", "entry_point", "precondition", "happy_path", "alternative_path", "error", "recovery",
    "permission", "state", "data", "side_effect", "notification", "validation", "boundary", "persistence",
    "security", "privacy", "analytics", "acceptance",
)


def load_shapes() -> dict[str, dict[str, Any]]:
    contract = json.loads(SHAPES_PATH.read_text(encoding="utf-8"))
    if contract.get("contract_id") != "joewrks.ux-action-shapes" or contract.get("version") != "1.0":
        raise ValueError("ux_action_shapes_drift")
    return contract["shapes"]


def _na_cell(source: str) -> dict[str, Any]:
    return {"status": "N/A", "authority_bindings": [], "unknown_refs": [], "basis_bindings": [],
            "rationale": None, TAG: source}


def _covered_cell(bindings: list[dict[str, Any]], source: str) -> dict[str, Any]:
    return {"status": "COVERED", "authority_bindings": copy.deepcopy(bindings), "unknown_refs": [],
            "basis_bindings": [], "rationale": None, TAG: source}


def _fill(cells: dict[str, Any], axes: tuple[str, ...], na_axes: dict[str, str],
          default: list[dict[str, Any]] | None, default_source: str) -> None:
    for axis in axes:
        if axis in cells:
            continue
        if axis in na_axes:
            cells[axis] = _na_cell(na_axes[axis])
        elif isinstance(default, list):
            cells[axis] = _covered_cell(default, default_source)
        # otherwise the axis stays missing and the inventory check reports it


def expand_coverage(state: dict[str, Any], *, strip: bool = False) -> dict[str, Any]:
    """A deep copy with every inheritable cell written out (see module docstring)."""
    expanded = copy.deepcopy(state)
    if not isinstance(expanded, dict):
        return expanded
    try:
        shapes = load_shapes()
    except (OSError, ValueError, KeyError):
        shapes = {}
    profile_states, profile_actions = inheritable_ux_axes(expanded)
    profile_na = {axis: "profile" for axis in profile_states}
    profile_na_actions = {axis: "profile" for axis in profile_actions}

    for row in expanded.get("coverage") or []:
        if isinstance(row, dict) and isinstance(row.get("cells"), dict):
            _fill(row["cells"], _CORE_AXES, {}, row.get("default_authority"), "row")
    for row in expanded.get("ux_coverage") or []:
        if not isinstance(row, dict):
            continue
        if isinstance(row.get("states"), dict):
            _fill(row["states"], _UX_STATE_AXES, profile_na, row.get("default_authority"), "row")
        for action in row.get("actions") or []:
            if not isinstance(action, dict) or not isinstance(action.get("cells"), dict):
                continue
            na = dict(profile_na_actions)
            shape = action.get("shape")
            if isinstance(shape, str) and shape in shapes:
                na.update({axis: f"shape:{shape}" for axis in shapes[shape]["not_applicable"]})
            _fill(action["cells"], _UX_ACTION_AXES, na, action.get("default_authority"), "row")
    if strip:
        _strip(expanded)
    return expanded


def _strip(state: dict[str, Any]) -> None:
    def cells_of(mapping: Any) -> None:
        if isinstance(mapping, dict):
            for cell in mapping.values():
                if isinstance(cell, dict):
                    cell.pop(TAG, None)

    for row in state.get("coverage") or []:
        if isinstance(row, dict):
            for field in ROW_FIELDS:
                row.pop(field, None)
            cells_of(row.get("cells"))
    for row in state.get("ux_coverage") or []:
        if not isinstance(row, dict):
            continue
        for field in ROW_FIELDS:
            row.pop(field, None)
        cells_of(row.get("states"))
        for action in row.get("actions") or []:
            if isinstance(action, dict):
                for field in ROW_FIELDS:
                    action.pop(field, None)
                cells_of(action.get("cells"))


def declared_rows(state: dict[str, Any]):
    """(path, row) for every row that declares a shape or default_authority."""
    for i, row in enumerate(state.get("coverage") or []):
        if isinstance(row, dict) and ROW_FIELDS & set(row):
            yield f"coverage[{i}]", row
    for i, row in enumerate(state.get("ux_coverage") or []):
        if not isinstance(row, dict):
            continue
        if ROW_FIELDS & set(row):
            yield f"ux_coverage[{i}]", row
        for j, action in enumerate(row.get("actions") or []):
            if isinstance(action, dict) and ROW_FIELDS & set(action):
                yield f"ux_coverage[{i}].actions[{j}]", action


def _compact_cells(cells: dict[str, Any], axes: tuple[str, ...]) -> tuple[list[dict[str, Any]] | None, int]:
    """Declare the most reused COVERED binding set as default and drop the cells it reproduces."""
    plain = {axis: cell for axis, cell in cells.items()
             if isinstance(cell, dict) and cell.get("status") == "COVERED"
             and cell.get("unknown_refs") == [] and cell.get("basis_bindings") == [] and cell.get("rationale") is None}
    counts = Counter(json.dumps(cell["authority_bindings"], sort_keys=True) for cell in plain.values())
    if not counts:
        return None, 0
    best, uses = counts.most_common(1)[0]
    if uses < 2:
        return None, 0
    default = json.loads(best)
    removed = 0
    for axis in axes:
        cell = plain.get(axis)
        if cell is not None and json.dumps(cell["authority_bindings"], sort_keys=True) == best:
            del cells[axis]
            removed += 1
    return default, removed


def compact_coverage(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    """Inverse of expand_coverage for rows where it is lossless; returns (compact state, removed counts)."""
    compact = copy.deepcopy(state)
    removed = Counter()
    for row in compact.get("coverage") or []:
        if isinstance(row, dict) and isinstance(row.get("cells"), dict) and "default_authority" not in row:
            default, n = _compact_cells(row["cells"], _CORE_AXES)
            if default is not None:
                row["default_authority"] = default
                removed["core"] += n
    for row in compact.get("ux_coverage") or []:
        if not isinstance(row, dict):
            continue
        if isinstance(row.get("states"), dict) and "default_authority" not in row:
            default, n = _compact_cells(row["states"], _UX_STATE_AXES)
            if default is not None:
                row["default_authority"] = default
                removed["ux_state"] += n
        for action in row.get("actions") or []:
            if isinstance(action, dict) and isinstance(action.get("cells"), dict) and "default_authority" not in action:
                default, n = _compact_cells(action["cells"], _UX_ACTION_AXES)
                if default is not None:
                    action["default_authority"] = default
                    removed["ux_action"] += n
    return compact, dict(removed)
