"""Emit a deterministic migration plan without writing V2 authority state."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from migration_v2 import MigrationError, build_migration_plan


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2 or args[0] != "--plan":
        print("usage: migrate_state.py --plan SOURCE_JSON", file=sys.stderr)
        return 2

    try:
        with Path(args[1]).open(encoding="utf-8") as handle:
            state = json.load(handle)
        if not isinstance(state, dict):
            raise ValueError("state root must be a JSON object")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"migrate_state.py: error: {exc}", file=sys.stderr)
        return 2

    try:
        plan = build_migration_plan(state)
    except MigrationError as exc:
        print(
            json.dumps(
                {"error": {"code": exc.code, "detail": exc.detail}},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 1

    print(json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
