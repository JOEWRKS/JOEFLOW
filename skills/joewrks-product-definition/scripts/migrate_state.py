"""Plan or apply deterministic legacy-to-V2 state migration."""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

from migration_v2 import (
    MigrationError,
    build_migration_plan,
    canonical_json_bytes,
    migrate_state_v020,
    verify_migration_result,
)


def _load_source(path: str) -> dict[str, object]:
    with Path(path).open(encoding="utf-8") as handle:
        state = json.load(handle)
    if not isinstance(state, dict):
        raise ValueError("state root must be a JSON object")
    return state


def _migration_failure(exc: MigrationError) -> int:
    print(
        json.dumps(
            {"error": {"code": exc.code, "detail": exc.detail}},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 1


def _publish_candidate(destination: Path, payload: bytes) -> None:
    temporary: Path | None = None
    handle = None
    try:
        for _ in range(16):
            candidate = destination.with_name(
                f".{destination.name}.{uuid.uuid4().hex}.tmp"
            )
            try:
                handle = candidate.open("xb")
            except FileExistsError:
                continue
            temporary = candidate
            break
        if temporary is None or handle is None:
            raise OSError("unable to allocate a unique migration output artifact")

        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, destination)
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    plan_mode = len(args) == 2 and args[0] == "--plan"
    apply_mode = len(args) == 4 and args[0] == "--apply" and args[2] == "--output"
    if not plan_mode and not apply_mode:
        print("usage: migrate_state.py --plan SOURCE_JSON", file=sys.stderr)
        return 2

    destination = Path(args[3]) if apply_mode else None
    if destination is not None and destination.exists():
        print(
            f"migrate_state.py: error: destination already exists: {destination}",
            file=sys.stderr,
        )
        return 2

    try:
        state = _load_source(args[1])
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"migrate_state.py: error: {exc}", file=sys.stderr)
        return 2

    try:
        if plan_mode:
            plan = build_migration_plan(state)
        else:
            candidate, receipt = migrate_state_v020(state)
            integrity_errors = verify_migration_result(state, candidate, receipt)
            if integrity_errors:
                raise MigrationError("MIGRATION_RESULT_INVALID", integrity_errors)
    except MigrationError as exc:
        return _migration_failure(exc)

    if plan_mode:
        print(json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0

    assert destination is not None
    try:
        _publish_candidate(destination, canonical_json_bytes(candidate) + b"\n")
    except FileExistsError:
        print(
            f"migrate_state.py: error: destination already exists: {destination}",
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(f"migrate_state.py: error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
