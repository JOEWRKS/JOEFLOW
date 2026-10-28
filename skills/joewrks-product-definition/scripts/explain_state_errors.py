#!/usr/bin/env python3
"""Validate a state and attach read-only hints that name allowed values for each error."""

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
            hint = {
                "cell_status": status,
                "status_shape": CELL_STATUS_SHAPES.get(status, "status must be one of " + ", ".join(sorted(CELL_STATUS_SHAPES))),
                "allowed_record_types": sorted(spec["allowed_types"]),
                "allowed_basis_record_types": sorted(spec["basis_types"]),
                "binding_findings": diagnose_cell(state, spec),
            }
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
