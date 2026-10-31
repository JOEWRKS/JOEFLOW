#!/usr/bin/env python3
"""Open a new definition revision from an explicit record patch, as one canonical mutation.

A patch names every record the author changes. Bindings that point at a
patched record are re-hashed; a binding whose record changed without being in
the patch, or that points at a record that is no longer CURRENT, is reported
and blocks the write.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from authority_binding_v2 import (
    BindingError,
    canonical_record_index,
    make_authority_binding,
    resolve_record_pointer,
    sha256_json,
)
from binding_diagnostics import diagnose_cell, iter_coverage_cells
from discovery_v2 import build_discovery_baseline
from state_validation_v2 import GROUP_PREFIXES


PATCH_KEYS = {"evidence", "objects", "surfaces", "cells", "rows"}
LIFECYCLE_STATUSES = {"OPEN", "BLOCKED", "READY_FOR_REVIEW"}
_CELL_ADDRESS = re.compile(
    r"^(?:coverage\[(?P<feature>[^\]]+)\]\.cells\.(?P<core_axis>\w+)"
    r"|grill_coverage\[(?P<pack>[^\]]+)\]\.axes\.(?P<pack_axis>\w+)"
    r"|ux_coverage\[(?P<screen>[^\]]+)\]\.(?:states\.(?P<state_axis>\w+)"
    r"|actions\[(?P<action>[^\]]+)\]\.cells\.(?P<action_axis>\w+)))$"
)


class RevisionError(ValueError):
    def __init__(self, code: str, message: str, path: str = "") -> None:
        super().__init__(message)
        self.error = {"code": code, "message": message, "path": path}


def _upsert(records: list[dict[str, Any]], record: dict[str, Any]) -> str:
    for position, existing in enumerate(records):
        if existing.get("id") == record.get("id"):
            records[position] = record
            return "changed"
    records.append(record)
    return "added"


def _cell(state: dict[str, Any], address: str) -> dict[str, Any]:
    match = _CELL_ADDRESS.match(address)
    if match is None:
        raise RevisionError("invalid_cell_address", f"cell address {address!r} must look like coverage[REQ-001].cells.AXIS, grill_coverage[PACK].axes.AXIS, ux_coverage[SCR-001].states.AXIS or ux_coverage[SCR-001].actions[KEY].cells.AXIS", "cells")
    groups = match.groupdict()
    try:
        if groups["feature"]:
            row = next(r for r in state["coverage"] if r.get("feature_id") == groups["feature"])
            return row["cells"][groups["core_axis"]]
        if groups["pack"]:
            row = next(r for r in state["grill_coverage"] if r.get("pack_id") == groups["pack"])
            return row["axes"][groups["pack_axis"]]
        row = next(r for r in state["ux_coverage"] if r.get("screen_id") == groups["screen"])
        if groups["state_axis"]:
            return row["states"][groups["state_axis"]]
        action = next(a for a in row["actions"] if a.get("key") == groups["action"])
        return action["cells"][groups["action_axis"]]
    except (StopIteration, KeyError, TypeError):
        raise RevisionError("unknown_cell", f"no coverage cell at {address!r}", "cells") from None


def _binding_field(cell: dict[str, Any]) -> str:
    return "basis_bindings" if cell.get("status") == "N/A" else "authority_bindings"


def _built_cell(state: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    """An exact coverage cell from {status, bind: [{record_id, pointer}], unknown_refs, rationale}."""
    cell = {"status": spec.get("status"), "authority_bindings": [], "unknown_refs": list(spec.get("unknown_refs", [])),
            "basis_bindings": [], "rationale": spec.get("rationale")}
    cell[_binding_field(cell)] = [make_authority_binding(state, b["record_id"], b["pointer"]) for b in spec.get("bind", [])]
    return cell


_ROW_TABLES = {"coverage": ("feature_id", "cells"), "ux_coverage": ("screen_id", None), "grill_coverage": ("target_ref", "axes")}


def _declared(state: dict[str, Any], spec: dict[str, Any], built: dict[str, Any]) -> None:
    """Carry a row's `shape` and `default_authority` (coverage-inheritance.md); the default is hashed like a binding."""
    if "shape" in spec:
        built["shape"] = spec["shape"]
    if "default_authority" in spec:
        built["default_authority"] = [make_authority_binding(state, b["record_id"], b["pointer"]) for b in spec["default_authority"]]


def _add_row(state: dict[str, Any], spec: dict[str, Any]) -> str:
    """Append one new coverage row whose cells are given as cell specs."""
    if not isinstance(spec, dict) or len(spec) != 1 or next(iter(spec)) not in _ROW_TABLES:
        raise RevisionError("invalid_row", f"a row entry is one of {sorted(_ROW_TABLES)} mapped to the row", "rows")
    table, row = next(iter(spec.items()))
    key, cells_field = _ROW_TABLES[table]
    target = row.get(key)
    same = [r for r in state[table] if r.get(key) == target and (table != "grill_coverage" or r.get("pack_id") == row.get("pack_id"))]
    if same:
        raise RevisionError("row_exists", f"{table} already has a row for {target!r}; edit its cells instead", "rows")
    built = copy.deepcopy(row)
    if table == "ux_coverage":
        built["states"] = {axis: _built_cell(state, cell) for axis, cell in row.get("states", {}).items()}
        built["actions"] = []
        for action in row.get("actions", []):
            built_action = {"key": action["key"], "cells": {axis: _built_cell(state, cell) for axis, cell in action["cells"].items()}}
            _declared(state, action, built_action)
            built["actions"].append(built_action)
    else:
        built[cells_field] = {axis: _built_cell(state, cell) for axis, cell in row.get(cells_field, {}).items()}
    if table != "grill_coverage":
        _declared(state, row, built)
    state[table].append(built)
    return f"{table}[{target}]"


def _apply_cell_edit(state: dict[str, Any], edit: dict[str, Any]) -> str:
    address = edit.get("cell")
    if not isinstance(address, str) or set(edit) - {"cell", "add", "remove", "replace"}:
        raise RevisionError("invalid_cell_edit", "a cell edit has 'cell' plus 'add', 'remove' and/or 'replace'", "cells")
    cell = _cell(state, address)
    if "replace" in edit:
        built = _built_cell(state, edit["replace"])
        cell.clear()
        cell.update(built)
    field = _binding_field(cell)
    removed = set(edit.get("remove", []))
    if removed:
        cell[field] = [b for b in cell[field] if b.get("record_id") not in removed]
    for binding in edit.get("add", []):
        cell[field].append(make_authority_binding(state, binding["record_id"], binding["pointer"]))
    return address


def apply_patch(state: dict[str, Any], patch: dict[str, Any]) -> dict[str, list[str]]:
    """Upsert patch records and apply cell edits in place; return what changed."""
    if not isinstance(patch, dict) or set(patch) - PATCH_KEYS:
        raise RevisionError("invalid_patch", f"patch keys must be a subset of {sorted(PATCH_KEYS)}")
    report: dict[str, list[str]] = {"added": [], "changed": [], "cells": []}
    for record in patch.get("evidence", []):
        report[_upsert(state["evidence"], record)].append(record["id"])
    for group, records in patch.get("objects", {}).items():
        if group not in GROUP_PREFIXES:
            raise RevisionError("invalid_patch", f"unknown object group {group!r}; allowed {sorted(GROUP_PREFIXES)}", f"objects.{group}")
        for record in records:
            report[_upsert(state["objects"].setdefault(group, []), record)].append(record["id"])
    for record in patch.get("surfaces", []):
        report[_upsert(state["surface_manifest"]["records"], record)].append(record["id"])
    if "rows" in patch:
        report["rows"] = [_add_row(state, spec) for spec in patch["rows"]]
    for edit in patch.get("cells", []):
        report["cells"].append(_apply_cell_edit(state, edit))
    return report


def refresh_bindings(state: dict[str, Any], accepted: set[str]) -> dict[str, list[dict[str, Any]]]:
    """Re-hash bindings whose record is in `accepted`; report every other broken binding."""
    index = canonical_record_index(state)
    refreshed, unresolved = [], []
    for spec in iter_coverage_cells(state):
        cell = spec["cell"]
        if not isinstance(cell, dict):
            continue
        for finding in diagnose_cell(state, spec, index):
            field, position = finding["field"].split("[")
            binding = cell[field][int(position.rstrip("]"))]
            fixable = (
                finding["code"] == "authority_binding_hash_mismatch"
                and finding["record_id"] in accepted
            )
            if fixable:
                record = index[finding["record_id"]][1]
                binding["value_sha256"] = sha256_json(resolve_record_pointer(record, binding["pointer"]))
                refreshed.append({"cell": spec["path"], "record_id": finding["record_id"], "pointer": binding["pointer"]})
            else:
                unresolved.append({"cell": spec["path"], **finding})
    return {"refreshed": refreshed, "unresolved": unresolved}


def open_revision(
    state: dict[str, Any], patch: dict[str, Any], *, status: str = "READY_FOR_REVIEW",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (candidate, report): revision+1, UNAPPROVED, patch applied, bindings refreshed, baseline recomputed."""
    if status not in LIFECYCLE_STATUSES:
        raise RevisionError("invalid_status", f"status must be one of {sorted(LIFECYCLE_STATUSES)}", "--status")
    candidate = copy.deepcopy(state)
    project = candidate["project"]
    previous = project.get("definition_revision")
    project["definition_revision"] = previous + 1
    project["definition_status"] = status
    candidate["approval"] = {"status": "UNAPPROVED"}
    report: dict[str, Any] = {"from_revision": previous, "to_revision": previous + 1, "status": status}
    try:
        report.update(apply_patch(candidate, patch))
    except (BindingError, KeyError, TypeError) as exc:
        raise RevisionError("invalid_patch", f"patch could not be applied: {exc}") from exc
    bindings = refresh_bindings(candidate, set(report["added"]) | set(report["changed"]))
    report.update(bindings)
    baseline = candidate.get("discovery_baseline")
    if isinstance(baseline, dict) and baseline.get("status") == "CURRENT":
        candidate["discovery_baseline"] = build_discovery_baseline(
            candidate,
            procedure_complete=baseline.get("procedure_complete") is True,
            applicable_surface_classes_complete=baseline.get("applicable_surface_classes_complete") is True,
        )
    return candidate, report
