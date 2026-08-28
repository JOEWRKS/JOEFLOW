#!/usr/bin/env python3
"""Validate whether a product definition satisfies the closure gate."""

import json
import sys

from state_contract_dispatch import evaluate_closure_for_version
from state_validation import load_state


def main(argv):
    if len(argv) != 2:
        print(json.dumps({"validator": "closure", "closed": False, "errors": [{"code": "usage_error", "message": "usage: validate_closure.py STATE_JSON", "path": ""}], "metrics": {}}))
        return 2
    try:
        state = load_state(argv[1])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"validator": "closure", "closed": False, "errors": [{"code": "read_error", "message": str(exc), "path": argv[1]}], "metrics": {}}, sort_keys=True))
        return 2
    result = evaluate_closure_for_version(state)
    print(json.dumps({"validator": "closure", **result}, indent=2, sort_keys=True))
    return 0 if result["closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
