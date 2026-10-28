#!/usr/bin/env python3
"""Add a supersession and everything that must follow it to a revision patch.

For each OLD=NEW pair the OLD record becomes SUPERSEDED by NEW, every current
record that still names OLD is re-pointed to NEW, and coverage bindings on OLD
are moved to NEW at the same pointer. Historical (SUPERSEDED or RETIRED)
records keep their references. Apply and validate the patch with open_revision.py.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from approval_v2 import _SET_FIELDS
from binding_diagnostics import iter_coverage_cells
from cli_output import use_utf8_stdio


HISTORICAL = {"SUPERSEDED", "RETIRED"}
UNRESOLVED_ON_SUPERSEDE = {"resolved_by": [], "resolution_mode": None, "resolution_summary": None}
# Provenance links say which decision resolved which question; re-pointing them would rewrite history.
_PROVENANCE_KEYS = {"resolved_by", "source_unknown_refs"}
# Only reference fields are re-pointed; free text that happens to equal an ID is left alone.
_REFERENCE_KEYS = (set(_SET_FIELDS) | {"surface_ref"}) - _PROVENANCE_KEYS - {"authority_classes"}


def _records(state: dict[str, Any], patch: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    """Current view: state records overlaid by patch records, keyed by ID -> (patch group key, record)."""
    view: dict[str, tuple[str, dict[str, Any]]] = {}
    for source in (state, patch):
        for record in source.get("evidence", []):
            view[record["id"]] = ("evidence", record)
        for group, records in source.get("objects", {}).items():
            for record in records:
                view[record["id"]] = (f"objects.{group}", record)
        surfaces = source.get("surface_manifest", {}).get("records", []) if source is state else source.get("surfaces", [])
        for record in surfaces:
            view[record["id"]] = ("surfaces", record)
    return view


def _replace(value: Any, mapping: dict[str, str], path: str, changes: list[str], in_reference: bool = False) -> Any:
    if in_reference and isinstance(value, str) and value in mapping:
        changes.append(path)
        return mapping[value]
    if isinstance(value, list):
        out: list[Any] = []
        for position, item in enumerate(value):
            new = _replace(item, mapping, f"{path}[{position}]", changes, in_reference)
            if not (isinstance(new, str) and new in out):
                out.append(new)
        return out
    if isinstance(value, dict):
        return {key: _replace(item, mapping, f"{path}.{key}", changes, key in _REFERENCE_KEYS)
                for key, item in value.items()}
    return value


def _put(patch: dict[str, Any], location: str, record: dict[str, Any]) -> None:
    if location == "evidence":
        target = patch.setdefault("evidence", [])
    elif location == "surfaces":
        target = patch.setdefault("surfaces", [])
    else:
        target = patch.setdefault("objects", {}).setdefault(location.split(".", 1)[1], [])
    for position, existing in enumerate(target):
        if existing.get("id") == record["id"]:
            target[position] = record
            return
    target.append(record)


def _stable_cell_address(path: str, state: dict[str, Any]) -> str:
    """Turn coverage[0].cells.x into coverage[REQ-001].cells.x (and likewise for grill/UX rows)."""
    head, _, rest = path.partition("]")
    group, _, position = head.partition("[")
    row = state[group][int(position)]
    key = {"coverage": "feature_id", "grill_coverage": "pack_id", "ux_coverage": "screen_id"}[group]
    if group == "ux_coverage" and rest.startswith(".actions["):
        action_position, _, tail = rest[len(".actions["):].partition("]")
        return f"ux_coverage[{row[key]}].actions[{row['actions'][int(action_position)]['key']}]{tail}"
    return f"{group}[{row[key]}]{rest}"


def supersede(state: dict[str, Any], patch: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    """Extend `patch` in place; return a report of what was added."""
    view = _records(state, patch)
    missing = sorted({old for old in mapping if old not in view} | {new for new in mapping.values() if new not in view})
    if missing:
        raise ValueError(f"IDs not found in state or patch: {missing}; add NEW records to the patch first")
    report: dict[str, Any] = {"superseded": [], "repointed": {}, "cells": [], "provenance_to_review": []}

    for old, new in mapping.items():
        location, record = view[old]
        updated = copy.deepcopy(record)
        updated.update({"status": "SUPERSEDED", "superseded_by": new})
        if location == "objects.unknowns":
            updated.update(UNRESOLVED_ON_SUPERSEDE)
        _put(patch, location, updated)
        report["superseded"].append({"id": old, "superseded_by": new})

    for record_id, (location, record) in view.items():
        if record_id in mapping or record.get("status") in HISTORICAL:
            continue
        for key in _PROVENANCE_KEYS:
            linked = [ref for ref in record.get(key) or [] if ref in mapping]
            if linked:
                report["provenance_to_review"].append({"id": record_id, "field": key, "refs": linked})
        changes: list[str] = []
        rewritten = _replace(record, mapping, record_id, changes)
        if changes:
            _put(patch, location, rewritten)
            report["repointed"][record_id] = changes

    for spec in iter_coverage_cells(state):
        cell = spec["cell"]
        if not isinstance(cell, dict):
            continue
        field = "basis_bindings" if cell.get("status") == "N/A" else "authority_bindings"
        moved = [b for b in cell.get(field, []) if b.get("record_id") in mapping]
        if not moved:
            continue
        address = _stable_cell_address(spec["path"], state)
        existing = {b.get("record_id") for b in cell.get(field, [])}
        additions = [{"record_id": mapping[b["record_id"]], "pointer": b["pointer"]}
                     for b in moved if mapping[b["record_id"]] not in existing]
        patch.setdefault("cells", []).append({
            "cell": address, "remove": sorted({b["record_id"] for b in moved}), "add": additions,
        })
        report["cells"].append(address)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--patch", required=True, help="patch JSON that already holds the NEW records; extended in place")
    parser.add_argument("--replace", action="append", required=True, help="OLD=NEW (repeat), e.g. DEC-019=DEC-026 UNK-019=UNK-026")
    args = parser.parse_args(argv)
    try:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        patch_path = Path(args.patch)
        patch = json.loads(patch_path.read_text(encoding="utf-8")) if patch_path.exists() else {}
        mapping = dict(item.split("=", 1) for item in args.replace)
        report = supersede(state, patch, mapping)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"written": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    except ValueError as exc:
        print(json.dumps({"written": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    patch_path.write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"written": True, "patch": str(patch_path), **report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
