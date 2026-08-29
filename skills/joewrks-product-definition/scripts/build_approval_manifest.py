from __future__ import annotations

import json
import sys
from pathlib import Path

from approval_v2 import (
    approval_manifest_digest,
    build_approval_commitment,
    build_approval_manifest_for_review,
)
from state_validation_v2 import semantic_readiness_metrics, validate_state_v2


def _reject_constant(value: str) -> object:
    raise ValueError(f"non-canonical JSON constant: {value}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"error": "usage: build_approval_manifest.py STATE_JSON"}), file=sys.stderr)
        return 2
    try:
        state = json.loads(
            Path(argv[1]).read_text(encoding="utf-8"), parse_constant=_reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    errors = validate_state_v2(state) if isinstance(state, dict) else [{
        "code": "schema_error", "message": "state must be an object", "path": "",
    }]
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 1
    blockers = {name: count for name, count in semantic_readiness_metrics(state).items() if count}
    if blockers:
        print(json.dumps({"valid": False, "semantic_readiness_metrics": blockers}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 1
    try:
        manifest = build_approval_manifest_for_review(state)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 1
    packet = {
        "manifest": manifest,
        "manifest_digest": approval_manifest_digest(manifest),
        "approval_commitment": build_approval_commitment(state, manifest),
    }
    print(json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
