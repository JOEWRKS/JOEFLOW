#!/usr/bin/env python3
"""List coverage bindings that no longer verify, and re-hash only those whose records you name."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from cli_output import use_utf8_stdio
from revision_v2 import refresh_bindings


def _write(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--accept", default="", help="comma-separated record IDs whose changed content you intend to re-bind")
    parser.add_argument("--write", action="store_true", help="replace the state file with the refreshed bindings")
    args = parser.parse_args(argv)
    path = Path(args.state)
    try:
        original = path.read_bytes()
        state = json.loads(original.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _write({"written": False, "errors": [{"code": "read_error", "message": str(exc), "path": str(path)}]})
        return 2
    accepted = {item.strip() for item in args.accept.split(",") if item.strip()}
    report = refresh_bindings(state, accepted)
    written = False
    if args.write and report["refreshed"]:
        if path.read_bytes() != original:
            _write({"written": False, "errors": [{"code": "state_changed", "message": "state file changed during the run; rerun", "path": str(path)}]})
            return 2
        temporary = path.with_name(f".{path.name}.refresh-bindings.tmp")
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, path)
        written = True
    _write({"written": written, "dry_run": not args.write, **report})
    return 0 if not report["unresolved"] else 1


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
