#!/usr/bin/env python3
"""Print one read-only exact authority binding for a V2 state record."""

from __future__ import annotations

import json
import sys

from authority_binding_v2 import BindingError, make_authority_binding
from state_validation import load_state


def _error(code: str, detail: object) -> None:
    print(json.dumps({"code": code, "detail": detail}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        _error("usage_error", "usage: authority_binding_value.py STATE_JSON RECORD_ID RECORD_RELATIVE_POINTER")
        return 2
    try:
        state = load_state(argv[1])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _error("read_error", str(exc))
        return 2
    if state.get("schema_version") != "0.2.0":
        _error("invalid_state", "state must use schema_version 0.2.0")
        return 1
    try:
        binding = make_authority_binding(state, argv[2], argv[3])
    except BindingError as exc:
        _error(exc.code, exc.detail)
        return 1
    print(json.dumps(binding, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
