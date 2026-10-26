#!/usr/bin/env python3
"""Report, read-only, which definition revisions the user approved and which are still pending."""

from __future__ import annotations

import json
import sys

from approval_v2 import compute_approval_manifest
from cli_output import use_utf8_stdio
from state_validation import load_state


def _write(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def approval_status(state: dict[str, object]) -> dict[str, object]:
    project = state.get("project") if isinstance(state.get("project"), dict) else {}
    approval = state.get("approval") if isinstance(state.get("approval"), dict) else {}
    history = state.get("approval_history") if isinstance(state.get("approval_history"), list) else []
    revision = _int(project.get("definition_revision"))
    approved = sorted({
        rev for rev in (_int(entry.get("revision")) for entry in history if isinstance(entry, dict))
        if rev is not None
    })
    current_approved = (
        approval.get("status") == "APPROVED"
        and approval.get("approved_revision") == revision
        and revision in approved
    )
    last_approved = approved[-1] if approved else None

    # Revisions between the first and the last approval that never got their own approval;
    # their changes reached the user only inside a later Manifest.
    skipped = [
        rev for rev in range(approved[0] + 1, last_approved) if rev not in approved
    ] if approved else []
    pending = []
    if revision is not None and not current_approved:
        pending = list(range((last_approved or 0) + 1, revision + 1))

    pending_changes = None
    if pending:
        try:
            manifest = compute_approval_manifest(state)
            pending_changes = {
                "from_revision": manifest["from_revision"],
                "to_revision": manifest["to_revision"],
                **{name: len(manifest[name]) for name in ("added", "changed", "superseded", "retired")},
            }
        except (KeyError, TypeError, ValueError):
            pending_changes = None

    if revision is None:
        summary = "No definition_revision; nothing to report."
    elif current_approved:
        summary = f"Revision {revision} is approved by the user."
    else:
        base = f"approved revision {last_approved}" if last_approved is not None else "no approved revision"
        summary = (
            f"Revision {revision} is NOT approved ({project.get('definition_status')}); "
            f"{len(pending)} revision(s) pending since {base}. "
            "Work built on these revisions is unapproved until the user approves the current Approval Manifest."
        )
    return {
        "definition_revision": revision,
        "definition_status": project.get("definition_status"),
        "approval_status": approval.get("status"),
        "approved_revision": approval.get("approved_revision"),
        "current_revision_approved": current_approved,
        "approved_revisions": approved,
        "last_approved_revision": last_approved,
        "pending_revisions": pending,
        "pending_changes": pending_changes,
        "revisions_without_own_approval": skipped,
        "summary": summary,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        _write({"error": "usage: approval_status.py STATE_JSON"})
        return 2
    try:
        state = load_state(argv[1])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _write({"error": str(exc)})
        return 2
    _write(approval_status(state))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main(sys.argv))
