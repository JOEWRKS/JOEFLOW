#!/usr/bin/env python3
"""Validate a state and attach read-only hints that name allowed values for each error.

The frozen validator's messages for coverage cells and empty OPEN surfaces stay as they are
(state_validation_v2.py and authority_binding_v2.py are protected blobs); this layer, which
open_revision.py prints, appends the actual condition: the axis, its allowed record types and
the bound record's type, or the way out of an OPEN surface whose questions are all answered.
"""

from __future__ import annotations

import json
import re
import sys

from binding_diagnostics import CELL_STATUS_SHAPES, diagnose_cell, iter_coverage_cells
from cli_output import use_utf8_stdio
from state_contract_dispatch import validate_state_for_version
from state_validation import load_state
from state_validation_v2 import SOURCE_KIND_CAPABILITIES


_EVIDENCE_PATH = re.compile(r"^evidence\[(\d+)\]")
_SURFACE_PATH = re.compile(r"^surface_manifest\.records\[(\d+)\]$")


def _write(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _evidence_hint(state: dict[str, object], path: str) -> dict[str, object] | None:
    match = _EVIDENCE_PATH.match(path)
    evidence = state.get("evidence")
    if match is None or not isinstance(evidence, list) or int(match.group(1)) >= len(evidence):
        return None
    record = evidence[int(match.group(1))]
    source_kind = record.get("source_kind") if isinstance(record, dict) else None
    return {
        "evidence_id": record.get("id") if isinstance(record, dict) else None,
        "source_kind": source_kind,
        "supported_authority_classes": sorted(SOURCE_KIND_CAPABILITIES.get(source_kind, set())),
        "source_kind_capabilities": {kind: sorted(classes) for kind, classes in sorted(SOURCE_KIND_CAPABILITIES.items())},
    }


def _axis_condition(spec: dict[str, object], findings: list[dict[str, object]]) -> str:
    """'axis back: allowed [FLOW, RULE, SCR], actual STATE (STATE-007)' and the other binding facts."""
    axis = spec["path"].rsplit(".", 1)[-1]
    parts = []
    for finding in findings:
        record = f"{finding.get('record_id')} {finding.get('pointer')}"
        if finding.get("record_type") is None:
            parts.append(f"{finding.get('field')}: {finding.get('record_id')!r} is not a record in this state")
        elif finding["basis"] is False and finding["record_type"] not in spec["allowed_types"]:
            parts.append(f"axis {axis}: allowed [{', '.join(sorted(spec['allowed_types']))}], actual {finding['record_type']} ({record})")
        elif finding["basis"] is True and finding["record_type"] not in spec["basis_types"]:
            parts.append(f"axis {axis} basis: allowed [{', '.join(sorted(spec['basis_types']))}], actual {finding['record_type']} ({record})")
        elif finding.get("record_status") not in (None, "CURRENT") and finding["record_type"] not in {"SURF"}:
            parts.append(f"{record} is {finding.get('record_status')}, not CURRENT")
        elif finding.get("code") == "authority_binding_hash_mismatch":
            parts.append(f"{record} changed after it was bound (value hash differs): put the record in the revision patch "
                         "so open_revision.py re-hashes it, or run refresh_bindings.py")
        elif finding.get("allowed_pointer_roots") is not None and finding.get("pointer") is not None and not any(
                str(finding["pointer"]) == root or str(finding["pointer"]).startswith(root + "/") for root in finding["allowed_pointer_roots"]):
            parts.append(f"{record}: pointer must start with one of {finding['allowed_pointer_roots']}")
        else:
            parts.append(f"{record}: {finding.get('code')}")
    return "; ".join(parts)


def _surface_way_out(state: dict[str, object], path: str) -> str | None:
    match = _SURFACE_PATH.match(path)
    records = (state.get("surface_manifest") or {}).get("records") if isinstance(state.get("surface_manifest"), dict) else None
    if match is None or not isinstance(records, list) or int(match.group(1)) >= len(records):
        return None
    surface = records[int(match.group(1))]
    surface_id = surface.get("id")
    decisions = ",".join(surface.get("decision_refs") or []) or "DEC-a,DEC-b"
    return (f"{surface_id} is OPEN and material but holds no OPEN question (unknown_refs {surface.get('unknown_refs')}). "
            "When every question of the surface is answered, the way out is a requirement as its authority and status "
            f"IN_SCOPE: new_records.py --state STATE --patch PATCH requirement --from-decisions {decisions} "
            f"--surface {surface_id} --requirement REQ-NNN (workflow CLOSE). If something is still undecided, open that "
            "question on the surface instead")


def explain(state: dict[str, object]) -> dict[str, object]:
    errors = validate_state_for_version(state)
    cells = {spec["path"]: spec for spec in iter_coverage_cells(state)} if state.get("schema_version") == "0.2.0" else {}
    explained = []
    for error in errors:
        path = error.get("path", "")
        hint = None
        if error.get("code") == "invalid_evidence_authority_class":
            hint = _evidence_hint(state, path)
        elif path in cells:
            spec = cells[path]
            status = spec["cell"].get("status") if isinstance(spec["cell"], dict) else None
            findings = diagnose_cell(state, spec)
            condition = _axis_condition(spec, findings)
            if condition:
                error = {**error, "message": f"{error.get('message')} — {condition}"}
            hint = {
                "cell_status": status,
                "status_shape": CELL_STATUS_SHAPES.get(status, "status must be one of " + ", ".join(sorted(CELL_STATUS_SHAPES))),
                "allowed_record_types": sorted(spec["allowed_types"]),
                "allowed_basis_record_types": sorted(spec["basis_types"]),
                "binding_findings": findings,
            }
        if error.get("code") == "OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN":
            way_out = _surface_way_out(state, path)
            if way_out:
                error = {**error, "message": f"{error.get('message')} — {way_out}"}
        explained.append({**error, "hint": hint} if hint is not None else dict(error))
    return {"valid": not errors, "errors": explained}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        _write({"valid": False, "errors": [{"code": "usage_error", "message": "usage: explain_state_errors.py STATE_JSON", "path": ""}]})
        return 2
    try:
        state = load_state(argv[1])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _write({"valid": False, "errors": [{"code": "read_error", "message": str(exc), "path": argv[1]}]})
        return 2
    result = explain(state)
    _write(result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main(sys.argv))
