"""Verify a 2.1 runtime plan and admitted evidence bundle without state input."""

from __future__ import annotations

import json
import sys
from pathlib import Path


_SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(_SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILL_ROOT))

from downstream_v2.authority import canonical_json
from integration_v2.runtime_v21 import verify_runtime_v21


USAGE = "python verify_runtime_v21.py CONTRACT_JSON RUNTIME_PLAN_JSON RUNTIME_EVIDENCE_BUNDLE_JSON [REVIEW_PACKAGE_JSON REVIEW_OUTPUT_JSON]"


def _read(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) not in {3, 5}:
        sys.stdout.write(canonical_json({"status": "ERROR", "error": {"code": "USAGE_ERROR", "detail": {"usage": USAGE}}}) + "\n")
        return 2
    try:
        contract, plan, bundle = (_read(argument) for argument in arguments[:3])
        review = {} if len(arguments) == 3 else {
            "review_package": _read(arguments[3]), "review_output": _read(arguments[4])
        }
        report = verify_runtime_v21(contract, plan, bundle, **review)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        sys.stdout.write(canonical_json({"status": "ERROR", "error": {"code": "INVALID_RUNTIME_INPUT", "detail": str(error)}}) + "\n")
        return 1
    sys.stdout.write(canonical_json(report) + "\n")
    return 0 if report["implementation_status"] == "IMPLEMENTATION_CONFORMANT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
