from __future__ import annotations

import json
import sys
from pathlib import Path

from discovery_v2 import build_discovery_baseline
from state_validation_v2 import SCHEMA_VERSION, _validate_state_v2


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"error": "usage: build_discovery_baseline.py STATE_JSON"}), file=sys.stderr)
        return 2
    try:
        state = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
        print(json.dumps({"valid": False, "errors": [{
            "code": "schema_error", "message": "schema_version must equal 0.2.0", "path": "schema_version",
        }]}))
        return 1
    errors = _validate_state_v2(state, check_discovery_baseline=False)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(build_discovery_baseline(
        state, procedure_complete=True, applicable_surface_classes_complete=True,
    ), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
