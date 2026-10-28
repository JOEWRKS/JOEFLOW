#!/usr/bin/env python3
"""Open definition_revision N+1 from a record patch and write it only if the result validates."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from approval_status import approval_status
from cli_output import use_utf8_stdio
from explain_state_errors import explain
from revision_v2 import LIFECYCLE_STATUSES, RevisionError, open_revision


def _write(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Patch JSON keys: evidence, objects (group -> records), surfaces, cells "
               "(edits like {\"cell\": \"coverage[REQ-001].cells.acceptance\", \"add\": [{\"record_id\": \"AC-009\", \"pointer\": \"/assertion\"}]}). "
               "Every record the revision changes must be in the patch.",
    )
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--patch", required=True, help="JSON file with the records and cell edits of this revision")
    parser.add_argument("--status", default="READY_FOR_REVIEW", choices=sorted(LIFECYCLE_STATUSES))
    parser.add_argument("--write", action="store_true", help="replace the state file when the new revision validates")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    path = Path(args.state)
    try:
        original = path.read_bytes()
        state = json.loads(original.decode("utf-8"))
        patch = json.loads(Path(args.patch).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _write({"written": False, "errors": [{"code": "read_error", "message": str(exc), "path": ""}]})
        return 2
    if not isinstance(state, dict) or state.get("schema_version") != "0.2.0":
        _write({"written": False, "errors": [{"code": "unsupported_schema_version", "message": "open_revision.py supports schema_version 0.2.0 only", "path": "schema_version"}]})
        return 1

    before = approval_status(state)
    try:
        candidate, report = open_revision(state, patch, status=args.status)
    except RevisionError as exc:
        _write({"written": False, "errors": [exc.error]})
        return 1
    if not before["current_revision_approved"]:
        report["warning"] = (
            f"revision {before['definition_revision']} was never approved; its changes will reach the user "
            "only inside the next Approval Manifest"
        )
    validation = explain(candidate)
    report["validation_errors"] = validation["errors"]
    written = False
    if args.write and validation["valid"] and not report["unresolved"]:
        if path.read_bytes() != original:
            _write({"written": False, "errors": [{"code": "state_changed", "message": "state file changed during the run; rerun", "path": str(path)}]})
            return 2
        temporary = path.with_name(f".{path.name}.open-revision.tmp")
        temporary.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, path)
        written = True
    _write({"written": written, **report})
    return 0 if validation["valid"] and not report["unresolved"] else 1


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
