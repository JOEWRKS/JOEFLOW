#!/usr/bin/env python3
"""Record the user's explicit approval of the exact current Approval Manifest."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from approval_v2 import (
    _valid_timestamp,
    approval_manifest_digest,
    build_approval_commitment,
    build_approval_manifest_for_review,
)
from cli_output import use_utf8_stdio
from state_contract_dispatch import evaluate_closure_for_version
from state_validation_v2 import validate_state_v2


OBSERVED = "observed"


def _error(code: str, message: str, path: str = "") -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _write(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _reject(errors: list[dict[str, str]], return_code: int = 1) -> int:
    _write({"recorded": False, "errors": errors})
    return return_code


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Without --write the command only checks and prints what it would record.",
    )
    parser.add_argument("state", help="canonical state.json (schema 0.2.0, READY_FOR_REVIEW, UNAPPROVED)")
    parser.add_argument("--revision", required=True, type=int, help="revision named in the user's approval message")
    parser.add_argument("--manifest-digest", required=True, help="Approval Manifest digest named in the user's approval message")
    parser.add_argument(
        "--at", required=True,
        help="UTC time of the user's approval message as YYYY-MM-DDTHH:MM:SSZ, "
             "or 'observed' to use the time this command records it",
    )
    parser.add_argument("--write", action="store_true", help="replace the state file with the approved state")
    return parser


def _approval_time(value: str) -> tuple[str | None, str | None]:
    if value == OBSERVED:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "observed_at_recording"
    if _valid_timestamp(value):
        return value, "user_message"
    return None, None


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    path = Path(args.state)
    try:
        original = path.read_bytes()
        state = json.loads(original.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _reject([_error("read_error", str(exc), str(path))], 2)
    if not isinstance(state, dict) or state.get("schema_version") != "0.2.0":
        return _reject([_error("unsupported_schema_version", "record_approval.py supports schema_version 0.2.0 only", "schema_version")])

    approved_at, at_source = _approval_time(args.at)
    if approved_at is None:
        return _reject([_error("invalid_approval_time", f"--at must be YYYY-MM-DDTHH:MM:SSZ (UTC) or '{OBSERVED}'; got {args.at!r}", "--at")])

    errors = validate_state_v2(state)
    if errors:
        return _reject(errors)
    try:
        manifest = build_approval_manifest_for_review(state)
    except ValueError as exc:
        project = state.get("project", {})
        return _reject([_error(
            "not_ready_for_approval",
            f"{exc}; current definition_status={project.get('definition_status')!r}, approval={state.get('approval')!r}",
            "project.definition_status",
        )])

    revision = state["project"]["definition_revision"]
    digest = approval_manifest_digest(manifest)
    mismatches = []
    if args.revision != revision:
        mismatches.append(_error("revision_mismatch", f"approved revision {args.revision} is not the current definition_revision {revision}", "--revision"))
    if args.manifest_digest != digest:
        mismatches.append(_error("manifest_digest_mismatch", f"approved digest {args.manifest_digest} is not the current Approval Manifest digest {digest}", "--manifest-digest"))
    if mismatches:
        return _reject(mismatches)

    # Same key order as the approval_commitment printed by build_approval_manifest.py.
    commitment = dict(sorted(build_approval_commitment(state, manifest).items()))
    candidate = copy.deepcopy(state)
    candidate["project"]["definition_status"] = "CLOSED"
    candidate["approval"] = {
        "status": "APPROVED",
        "approved_revision": revision,
        "approved_definition_digest": commitment["definition_digest"],
        "approved_manifest_digest": digest,
        "approved_at": approved_at,
        "approved_by": "user",
    }
    candidate["approval_history"] = list(candidate.get("approval_history", [])) + [commitment]

    closure = evaluate_closure_for_version(candidate)
    if closure["errors"] or not closure["closed"]:
        return _reject(closure["errors"] or [_error(
            "closure_not_reached",
            "approved candidate does not satisfy Semantic Closure: "
            + json.dumps({k: v for k, v in closure["metrics"].items() if v}, sort_keys=True),
            "",
        )])

    written = False
    if args.write:
        if path.read_bytes() != original:
            return _reject([_error("state_changed", "state file changed while recording approval; rerun", str(path))], 2)
        temporary = path.with_name(f".{path.name}.record-approval.tmp")
        temporary.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, path)
        written = True

    _write({
        "recorded": written,
        "dry_run": not written,
        "revision": revision,
        "manifest_digest": digest,
        "definition_digest": commitment["definition_digest"],
        "approved_at": approved_at,
        "approved_at_source": at_source,
        "approval_history_revisions": [entry["revision"] for entry in candidate["approval_history"]],
        "closed": True,
    })
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
