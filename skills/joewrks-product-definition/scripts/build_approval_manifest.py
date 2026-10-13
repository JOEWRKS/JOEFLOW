from __future__ import annotations

import json
import os
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


def _emit_json(payload: object, stream: object) -> bool:
    """Write one compact ASCII-safe JSON line without leaking stream failures."""
    try:
        rendered = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ) + "\n"
        written = stream.write(rendered)
        if isinstance(written, int) and written != len(rendered):
            return False
        stream.flush()
    except (BrokenPipeError, OSError, UnicodeError, TypeError, ValueError):
        return False
    return True


def _neutralize_failed_standard_stream(stream: object) -> None:
    """Prevent interpreter shutdown from flushing a standard stream that already failed."""
    if stream is not sys.stdout and stream is not sys.stderr:
        return
    try:
        descriptor = stream.fileno()
        devnull = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(devnull, descriptor)
        finally:
            os.close(devnull)
    except (AttributeError, BrokenPipeError, OSError, ValueError):
        return


def _finish(payload: object, *, stream: object, return_code: int) -> int:
    if _emit_json(payload, stream):
        return return_code
    _neutralize_failed_standard_stream(stream)
    if stream is not sys.stderr:
        _emit_json({"error": "output_write_failed"}, sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return _finish(
            {"error": "usage: build_approval_manifest.py STATE_JSON"},
            stream=sys.stderr,
            return_code=2,
        )
    try:
        state = json.loads(
            Path(argv[1]).read_text(encoding="utf-8"), parse_constant=_reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return _finish({"error": str(exc)}, stream=sys.stderr, return_code=2)
    errors = validate_state_v2(state) if isinstance(state, dict) else [{
        "code": "schema_error", "message": "state must be an object", "path": "",
    }]
    if errors:
        return _finish(
            {"valid": False, "errors": errors}, stream=sys.stdout, return_code=1,
        )
    blockers = {name: count for name, count in semantic_readiness_metrics(state).items() if count}
    if blockers:
        return _finish(
            {"valid": False, "semantic_readiness_metrics": blockers},
            stream=sys.stdout,
            return_code=1,
        )
    try:
        manifest = build_approval_manifest_for_review(state)
    except ValueError as exc:
        return _finish(
            {"valid": False, "error": str(exc)}, stream=sys.stdout, return_code=1,
        )
    packet = {
        "manifest": manifest,
        "manifest_digest": approval_manifest_digest(manifest),
        "approval_commitment": build_approval_commitment(state, manifest),
    }
    return _finish(packet, stream=sys.stdout, return_code=0)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
