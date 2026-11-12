#!/usr/bin/env python3
"""Record the user's explicit approval of the exact current Approval Manifest.

Run it in the session that received the user's approval words directly. A session
that only received the approval second-hand writes the evidence (the user's words,
the relaying session, the digest) into the project notes and asks the session that
holds the user's words to record it. check_approval.py runs the same checks
read-only.
"""

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
from project_pin import append_approval, read_project, running_version, schema_message, version_report
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
        epilog="Without --write the command only checks and prints what it would record "
               "(check_approval.py does the same and never writes). With --write and --quote, the approval words "
               "and relay path (--relayed-from) are appended to joeflow-project.json next to state.json.",
    )
    parser.add_argument("state", help="canonical state.json (schema 0.2.0, READY_FOR_REVIEW, UNAPPROVED)")
    parser.add_argument("--revision", required=True, type=int, help="revision named in the user's approval message")
    parser.add_argument("--manifest-digest", required=True, help="Approval Manifest digest named in the user's approval message")
    parser.add_argument(
        "--at", required=True,
        help="UTC time of the user's approval message as YYYY-MM-DDTHH:MM:SSZ, "
             "or 'observed' to use the time this command records it",
    )
    add_provenance_arguments(parser)
    parser.add_argument("--write", action="store_true", help="replace the state file with the approved state")
    return parser


def add_provenance_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--quote", help="the user's approval words, verbatim (e.g. '이대로 승인')")
    parser.add_argument(
        "--relayed-from",
        help="who passed the approval on when this session did not receive the user's words directly "
             "(e.g. 'session local_aa95d599'); requires --quote. Prefer recording in the session that received them",
    )


def provenance_errors(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.relayed_from and not (args.quote and args.quote.strip()):
        return [_error(
            "relayed_approval_needs_quote",
            "--relayed-from needs --quote with the user's exact approval words; a relayer's summary is not an approval. "
            "Ask the session that received the user's words to record it, or obtain the exact words",
            "--quote",
        )]
    return []


def prepare_approval(
    state: dict[str, object], revision_arg: int, digest_arg: str, approved_at: str,
) -> tuple[dict[str, object] | None, dict[str, object] | None, list[dict[str, str]]]:
    """(candidate, commitment, errors): the approved state the user's message would produce."""
    errors = validate_state_v2(state)
    if errors:
        return None, None, errors
    try:
        manifest = build_approval_manifest_for_review(state)
    except ValueError as exc:
        project = state.get("project", {})
        return None, None, [_error(
            "not_ready_for_approval",
            f"{exc}; current definition_status={project.get('definition_status')!r}, approval={state.get('approval')!r}",
            "project.definition_status",
        )]

    revision = state["project"]["definition_revision"]
    digest = approval_manifest_digest(manifest)
    mismatches = []
    if revision_arg != revision:
        mismatches.append(_error("revision_mismatch", f"approved revision {revision_arg} is not the current definition_revision {revision}", "--revision"))
    if digest_arg != digest:
        mismatches.append(_error("manifest_digest_mismatch", f"approved digest {digest_arg} is not the current Approval Manifest digest {digest}", "--manifest-digest"))
    if mismatches:
        return None, None, mismatches

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
        return None, None, closure["errors"] or [_error(
            "closure_not_reached",
            "approved candidate does not satisfy Semantic Closure: "
            + json.dumps({k: v for k, v in closure["metrics"].items() if v}, sort_keys=True),
            "",
        )]
    return candidate, commitment, []


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
        return _reject([_error("unsupported_schema_version", schema_message("record_approval.py", state), "schema_version")])

    approved_at, at_source = _approval_time(args.at)
    if approved_at is None:
        return _reject([_error("invalid_approval_time", f"--at must be YYYY-MM-DDTHH:MM:SSZ (UTC) or '{OBSERVED}'; got {args.at!r}", "--at")])

    provenance = provenance_errors(args)
    if provenance:
        return _reject(provenance)
    candidate, commitment, errors = prepare_approval(state, args.revision, args.manifest_digest, approved_at)
    if errors:
        return _reject(errors)
    revision = candidate["project"]["definition_revision"]
    digest = candidate["approval"]["approved_manifest_digest"]
    project = read_project(path)
    if args.write and isinstance(project, dict) and "error" in project:
        return _reject([_error("project_file_unreadable", f"{project['error']}; fix or move it before recording", "")])

    written = False
    if args.write:
        if path.read_bytes() != original:
            return _reject([_error("state_changed", "state file changed while recording approval; rerun", str(path))], 2)
        temporary = path.with_name(f".{path.name}.record-approval.tmp")
        temporary.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temporary, path)
        written = True
        log_entry = {
            "revision": revision, "manifest_digest": digest, "definition_digest": commitment["definition_digest"],
            "approved_at": approved_at, "approved_at_source": at_source,
            "quote": args.quote, "relayed_from": args.relayed_from, "recorded_with": running_version(),
        }
        if args.quote or args.relayed_from:
            append_approval(path, log_entry)

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
        "quote": args.quote,
        "relayed_from": args.relayed_from,
        "provenance_file": str(version_report(path)["project_file"]) if written and args.quote else None,
        "version_notice": version_report(path, state)["notice"],
        "next": (
            "commit state.json" + (" and joeflow-project.json" if args.quote else "")
            + "; run update_projection.py --write, then projection_check.py"
            if written else
            "checks passed; rerun with --write in the session that received the user's approval words"
        ),
    })
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
