#!/usr/bin/env python3
"""Select one canonical product question for user authority."""

import json
import sys

from grill_v2 import select_next_user_question
from state_validation import load_state


def _error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _write(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        _write({
            "next_question": None,
            "errors": [_error(
                "usage_error",
                "usage: next_product_question.py STATE_JSON",
                "",
            )],
        })
        return 2

    try:
        state = load_state(argv[1])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _write({
            "next_question": None,
            "errors": [_error("read_error", str(exc), argv[1])],
        })
        return 2

    try:
        question = select_next_user_question(state)
    except ValueError as exc:
        errors = exc.args[0]
        _write({"next_question": None, "errors": errors})
        return 1

    _write({"next_question": question})
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
