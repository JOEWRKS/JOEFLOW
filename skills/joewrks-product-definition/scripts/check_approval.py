#!/usr/bin/env python3
"""Check, read-only, whether an approval of revision N / Manifest digest D would record cleanly.

Runs exactly the checks of record_approval.py (state validation, Manifest
recomputation, revision and digest match, Semantic Closure of the approved
candidate) and never writes. Use it before asking the user to approve, and in a
session that only received the approval second-hand.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cli_output import use_utf8_stdio
from project_pin import schema_message, version_report
from record_approval import OBSERVED, _approval_time, add_provenance_arguments, prepare_approval, provenance_errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0, READY_FOR_REVIEW, UNAPPROVED)")
    parser.add_argument("--revision", required=True, type=int)
    parser.add_argument("--manifest-digest", required=True)
    parser.add_argument("--at", default=OBSERVED, help="as for record_approval.py (default observed)")
    add_provenance_arguments(parser)
    args = parser.parse_args(argv)
    path = Path(args.state)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ready": False, "errors": [{"code": "read_error", "message": str(exc), "path": str(path)}]}, ensure_ascii=False))
        return 2
    errors = []
    if not isinstance(state, dict) or state.get("schema_version") != "0.2.0":
        errors = [{"code": "unsupported_schema_version", "message": schema_message("check_approval.py", state), "path": "schema_version"}]
    approved_at, _ = _approval_time(args.at)
    if not errors and approved_at is None:
        errors = [{"code": "invalid_approval_time", "message": f"--at must be YYYY-MM-DDTHH:MM:SSZ (UTC) or '{OBSERVED}'; got {args.at!r}", "path": "--at"}]
    errors = errors or provenance_errors(args)
    candidate = None
    if not errors:
        candidate, commitment, errors = prepare_approval(state, args.revision, args.manifest_digest, approved_at)
    payload = {"ready": not errors, "written": False, "errors": errors,
               "version_notice": version_report(path, state if isinstance(state, dict) else None)["notice"]}
    if candidate is not None:
        payload.update({"revision": args.revision, "manifest_digest": args.manifest_digest,
                        "definition_digest": commitment["definition_digest"],
                        "next": "after the user approves, run record_approval.py with the same arguments and --write "
                                "in the session that received the user's words"})
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
