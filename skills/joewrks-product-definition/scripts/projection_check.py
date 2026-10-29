#!/usr/bin/env python3
"""Check, read-only, that the human projections still match the current state.

For MASTER_PLANNING_SPEC.md and planning-review-core.html this reports whether
the current revision, definition digest and Approval Manifest digest appear,
which records this revision added that the spec never names, and which changed
or retired records the author should re-read. --draft prints the identity lines
and the current text of every added or changed record for the author to condense.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from approval_status import approval_status
from approval_v2 import compute_approval_manifest, definition_digest
from cli_output import use_utf8_stdio


DEFAULT_REQUIRED_TYPES = "REQ,RULE,FLOW,SCR,STATE,DATA,INT,AC,TASK"
SHORT = 8


def _mentions(text: str, record_id: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(record_id)}(?![\w-])", text) is not None


def _identity(state: dict[str, object]) -> dict[str, object]:
    approval = state.get("approval") if isinstance(state.get("approval"), dict) else {}
    status = approval_status(state)
    return {
        "revision": state["project"]["definition_revision"],
        "definition_status": state["project"].get("definition_status"),
        "approval_status": approval.get("status"),
        "approved_at": approval.get("approved_at"),
        "definition_digest": definition_digest(state),
        "manifest_digest": approval.get("approved_manifest_digest"),
        "approved_revisions": status["approved_revisions"],
        "revisions_without_own_approval": status["revisions_without_own_approval"],
    }


def _identity_findings(text: str, identity: dict[str, object]) -> list[str]:
    findings = []
    # "rev 32", "Revision: `32`", "revision <code>32</code>" — not any bare 32 such as "32px".
    if not re.search(rf"(?i)\brev(?:ision)?[^\d\n]{{0,12}}(?<!\d){identity['revision']}(?!\d)", text):
        findings.append(f"revision {identity['revision']} is not mentioned")
    for key in ("definition_digest", "manifest_digest"):
        digest = identity[key]
        if isinstance(digest, str) and digest[:SHORT] not in text:
            findings.append(f"{key} {digest[:SHORT]}… is not mentioned")
    return findings


def check(state: dict[str, object], spec_text: str, review_text: str | None,
          required_types: set[str]) -> dict[str, object]:
    identity = _identity(state)
    manifest = compute_approval_manifest(state)
    added = [row for row in manifest["added"] if row["type"] in required_types]
    report: dict[str, object] = {
        "identity": identity,
        "compared_with_revision": manifest["from_revision"],
        "spec": {
            "stale_identity": _identity_findings(spec_text, identity),
            "missing_added_records": [row["id"] for row in added if not _mentions(spec_text, row["id"])],
            "changed_records_to_reread": [row["id"] for row in manifest["changed"] if _mentions(spec_text, row["id"])],
            "retired_or_superseded_still_named": [
                row["id"] for row in manifest["superseded"] + manifest["retired"] if _mentions(spec_text, row["id"])
            ],
        },
    }
    if review_text is not None:
        report["review"] = {"stale_identity": _identity_findings(review_text, identity)}
    report["ok"] = not (
        report["spec"]["stale_identity"] or report["spec"]["missing_added_records"]
        or (review_text is not None and report["review"]["stale_identity"])
    )
    return report


def draft(state: dict[str, object]) -> str:
    """Identity lines plus the current text of every added/changed record, as Markdown."""
    identity = _identity(state)
    manifest = compute_approval_manifest(state)
    lines = [
        "## Approved identity (draft)",
        "",
        f"- Revision: `{identity['revision']}` (previous approvals: {', '.join(map(str, identity['approved_revisions'][:-1])) or 'none'};"
        f" revisions without their own approval: {', '.join(map(str, identity['revisions_without_own_approval'])) or 'none'})",
        f"- Definition digest: `{identity['definition_digest']}`",
        f"- Approval Manifest digest: `{identity['manifest_digest']}`",
        f"- Status: `{identity['definition_status']}` / `{identity['approval_status']}` (approved_at {identity['approved_at']})",
        "",
        f"## Records changed since revision {manifest['from_revision']} (condense into the spec; do not paste blindly)",
        "",
    ]
    for category in ("added", "changed", "superseded", "retired"):
        for row in manifest[category]:
            text = str(row["summary"]).replace("\n", " ")
            lines.append(f"- {category} `{row['id']}`: {text}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--spec", required=True, help="MASTER_PLANNING_SPEC.md")
    parser.add_argument("--review", help="planning-review-core.html")
    parser.add_argument("--require-types", default=DEFAULT_REQUIRED_TYPES,
                        help=f"record types the spec must name when added (default {DEFAULT_REQUIRED_TYPES})")
    parser.add_argument("--draft", action="store_true", help="print a Markdown draft instead of the JSON check")
    args = parser.parse_args(argv)
    try:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        spec_text = Path(args.spec).read_text(encoding="utf-8")
        review_text = Path(args.review).read_text(encoding="utf-8") if args.review else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    if args.draft:
        print(draft(state), end="")
        return 0
    report = check(state, spec_text, review_text, {t.strip() for t in args.require_types.split(",") if t.strip()})
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
