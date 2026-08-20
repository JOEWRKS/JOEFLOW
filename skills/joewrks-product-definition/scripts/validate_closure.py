#!/usr/bin/env python3
"""Validate whether a product definition satisfies the closure gate."""

import json
import sys

from state_validation import closure_metrics, load_state, validate_state


def main(argv):
    if len(argv) != 2:
        print(json.dumps({"validator": "closure", "closed": False, "errors": [{"code": "usage_error", "message": "usage: validate_closure.py STATE_JSON", "path": ""}], "metrics": {}}))
        return 2
    try:
        state = load_state(argv[1])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"validator": "closure", "closed": False, "errors": [{"code": "read_error", "message": str(exc), "path": argv[1]}], "metrics": {}}, sort_keys=True))
        return 2
    errors = validate_state(state)
    metrics = closure_metrics(state)
    closed = not errors and all(value == 0 for value in metrics.values())
    print(json.dumps({"validator": "closure", "closed": closed, "errors": errors, "metrics": metrics}, indent=2, sort_keys=True))
    return 0 if closed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
