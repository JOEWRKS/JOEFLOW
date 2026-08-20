#!/usr/bin/env python3
"""Validate product-definition state structure and reference integrity."""

import json
import sys

from state_validation import load_state, validate_state


def main(argv):
    if len(argv) != 2:
        print(json.dumps({"validator": "state", "valid": False, "errors": [{"code": "usage_error", "message": "usage: validate_state.py STATE_JSON", "path": ""}]}))
        return 2
    try:
        state = load_state(argv[1])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"validator": "state", "valid": False, "errors": [{"code": "read_error", "message": str(exc), "path": argv[1]}]}, sort_keys=True))
        return 2
    errors = validate_state(state)
    print(json.dumps({"validator": "state", "valid": not errors, "errors": errors}, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

