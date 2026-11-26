#!/usr/bin/env python3
"""Check, read-only, that the human projections still match the current state.

For MASTER_PLANNING_SPEC.md and planning-review-core.html this reports whether
the current revision, definition digest and Approval Manifest digest appear,
which records this revision added that the spec never names, and which changed
or retired records the author should re-read, and any revision number in the title or
header area (<title>, the HTML header before the first section, the Markdown lines
before the first `## `) that differs from definition_revision
(stale_spec_title_revision / stale_review_title_revision). --draft prints the identity lines
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
from authority_binding_v2 import canonical_record_index
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


# A revision named in the title or header area: "revision 0", "Rev. 2", "rev <code>2</code>", "개정 2", "리비전 2".
# A range "rev 1→2" counts as its last number. Body text (change history, earlier approvals) is not read.
HEAD_REVISION = re.compile(
    r"(?i)(?<![\w-])(?:revision|rev\.?|리비전|개정판?)\s*(?:[:#]\s*)?(?:<code>|`)?\s*(\d+)(?!\d)"
    r"(?:\s*(?:</code>|`))?(?:\s*(?:→|->|–|~)\s*(?:rev(?:ision)?\.?\s*)?(\d+)(?!\d))?")
EARLIER = re.compile(r"(?i)(?:이전|직전|previous|prior|since|from)(?:\s*승인|\s+approvals?|\s+approved)?\W{0,3}$")
# 1.7.2: a sentence stating which revision was last approved ("마지막 승인은 revision 1", "마지막으로 승인된 것은
# revision 1", "revision 1만 승인됨", "last approved: rev 1") is a fact, not the document's name. It is skipped only
# when it names the state's last approved revision. A bare "승인 revision 1" / "Approved: rev 1" / "revision 1
# (approved)" can be a stale title and is still read, unless (1.7.3) the same line (HTML: the same block element's
# text) also carries the first 8+ hex characters of that approval's manifest_digest from approval_history, as in
# "> 승인: revision 1 (`dd1e837b…`)". A digest of another revision, no digest, or the current revision named on the
# same line (then either number could be the document's name) keeps the finding. So does a digest inside the
# document's name itself (<title>, <h1>, a Markdown `# ` line): a name line is read as a name, never as a fact.
LAST_APPROVED_BEFORE = re.compile(
    r"(?i)(?:(?:마지막|최근|최종|현재)(?:으로|에)?\s*승인(?:된|됨|한|받은)?(?:\s*(?:것|판|버전))?(?:은|는|이|가)?"
    r"|승인(?:된|받은)\s*(?:것|판|버전)(?:은|는|이|가)?"
    r"|(?:last|latest|most\s+recent(?:ly)?|currently)\s+(?:approved|approval)(?:\s+(?:is|was|at|in))?)\W{0,3}$")
LAST_APPROVED_AFTER = re.compile(
    r"(?i)^\s*(?:</code>|`)?\s*(?:(?:만|까지)\s*승인|(?:이|가)\s*(?:마지막|최근|최종)(?:으로)?\s*승인"
    r"|\W{0,3}(?:is|was)\s+(?:the\s+)?(?:last|latest|most\s+recent(?:ly)?)\s+approv|\W{0,3}\(\s*(?:last|latest)\s+approv)")
HEX_RUN = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{%d,64}(?![0-9a-f])" % SHORT)
BLOCK_TAG = re.compile(r"(?i)</?(?:p|li|h[1-6]|div|td|th|dd|dt|blockquote|figcaption|caption|header|section|nav|ul|ol|main|body|tr|table)\b[^>]*>")
COMMENT_OR_BLOCK = re.compile(r"<!-- JOEFLOW:([A-Z-]+):BEGIN -->.*?<!-- JOEFLOW:\1:END -->|<!--.*?-->", re.S)


def _blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group(0))  # keep offsets and line numbers


def _head_spans(text: str, html: bool) -> list[tuple[str, int, int]]:
    """Where a reader sees the document's name: <title> and the body up to the first section, or the
    Markdown lines before the first `## ` heading."""
    if not html:
        second = re.search(r"^##\s", text, re.M)
        if second:
            return [("heading", 0, second.start())]
        first = re.search(r"^#\s.*$", text, re.M)
        return [("heading", first.start(), first.end())] if first else []
    spans = []
    title = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    if title:
        spans.append(("<title>", title.start(1), title.end(1)))
    body = re.search(r"<body\b[^>]*>", text, re.I)
    start = body.end() if body else (title.end() if title else 0)
    ends = [m.start() for m in (re.compile(p, re.I).search(text, start)
                                for p in (r"</header>", r"<nav\b", r"<section\b", r"<h2\b")) if m]
    if not ends:
        h1 = re.search(r"</h1>", text[start:], re.I)
        ends = [start + h1.end()] if h1 else [start]
    spans.append(("header", start, min(ends)))
    return spans


def _same_line(visible: str, match: re.Match, start: int, end: int, html: bool) -> tuple[int, int]:
    """The text a reader takes together with the match: its Markdown line, or in HTML the run between the nearest
    block-level tags around it (inline <code>, <span> stay inside), never beyond the head span."""
    if not html:
        left = visible.rfind("\n", start, match.start())
        right = visible.find("\n", match.end(), end)
        return (left + 1 if left != -1 else start), (right if right != -1 else end)
    left = start
    for tag in BLOCK_TAG.finditer(visible, start, match.start()):
        left = tag.end()
    after = BLOCK_TAG.search(visible, match.end(), end)
    return left, (after.start() if after else end)


def _is_name_line(visible: str, left: int, start: int, match: re.Match, html: bool) -> bool:
    """A Markdown `# ` heading, or in HTML a run whose nearest enclosing block tag is <h1>: the document's name."""
    if not html:
        return bool(re.match(r"\s*#\s", visible[left:match.start()]))
    tags = list(BLOCK_TAG.finditer(visible, start, match.start()))
    return bool(tags) and tags[-1].group(0).lower().startswith("<h1")


def _carries_approval_digest(visible: str, match: re.Match, start: int, end: int, html: bool,
                             revision: int, digest: str | None, where: str = "") -> bool:
    """1.7.3: the line names the last approved revision together with that approval's manifest digest
    (8+ leading hex characters, any case, `…` or <code> around it), does not also name the current revision, and is
    not the document's name line (<title>, <h1>, Markdown `# `)."""
    if not digest or where == "<title>":
        return False
    left, right = _same_line(visible, match, start, end, html)
    segment = visible[left:right]
    if _is_name_line(visible, left, start, match, html):
        return False
    if any(int(other.group(2) or other.group(1)) == revision for other in HEAD_REVISION.finditer(segment)):
        return False
    plain = re.sub(r"<[^>]+>", " ", segment) if html else segment
    return any(digest.lower().startswith(run.group(0).lower()) for run in HEX_RUN.finditer(plain))


def _title_findings(text: str, revision: int, html: bool, code: str,
                    last_approved: int | None = None,
                    last_approved_digest: str | None = None) -> list[dict[str, object]]:
    """Revision numbers in the title/header area that differ from the state's definition_revision."""
    visible = COMMENT_OR_BLOCK.sub(_blank, text)
    findings = []
    for where, start, end in _head_spans(visible, html):
        for match in HEAD_REVISION.finditer(visible, start, end):
            if EARLIER.search(visible[max(0, match.start() - 20):match.start()]):
                continue
            found = int(match.group(2) or match.group(1))
            if found == revision:
                continue
            if found == last_approved and (
                    LAST_APPROVED_BEFORE.search(visible[max(0, match.start() - 30):match.start()])
                    or LAST_APPROVED_AFTER.search(visible[match.end():match.end() + 30])
                    or _carries_approval_digest(visible, match, start, end, html, revision, last_approved_digest, where)):
                continue
            line_no = visible.count("\n", 0, match.start()) + 1
            line = text.split("\n")[line_no - 1]
            shown = re.sub(r"<[^>]+>", "", line).strip()
            findings.append({
                "code": code,
                "line": line_no,
                "where": where,
                "text": shown[:160],
                "expected": revision,
                "actual": found,
                "next_action": (f"line {line_no}: if this line names the document's own revision (title, header), "
                                f"change revision {found} to {revision} by hand; update_projection.py rewrites only the "
                                "identity block and the 'REVIEW VIEW … revision N' form. If it truthfully states another "
                                "revision (an earlier or the last approval), leave it and report a checker false positive"),
            })
    return findings


def _approval_digest(state: dict[str, object], revision: int | None) -> str | None:
    """manifest_digest of the approval_history entry for that revision (the last one if repeated), else None."""
    history = state.get("approval_history") if isinstance(state.get("approval_history"), list) else []
    digests = [entry.get("manifest_digest") for entry in history
               if isinstance(entry, dict) and revision is not None and entry.get("revision") == revision]
    digest = digests[-1] if digests else None
    return digest if isinstance(digest, str) and len(digest) >= SHORT else None


def check(state: dict[str, object], spec_text: str, review_text: str | None,
          required_types: set[str]) -> dict[str, object]:
    identity = _identity(state)
    last_approved = approval_status(state)["last_approved_revision"]
    last_approved_digest = _approval_digest(state, last_approved)
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
            "stale_title_revision": _title_findings(spec_text, identity["revision"], False, "stale_spec_title_revision",
                                                    last_approved, last_approved_digest),
        },
    }
    if review_text is not None:
        report["review"] = {
            "stale_identity": _identity_findings(review_text, identity),
            "stale_title_revision": _title_findings(review_text, identity["revision"], True,
                                                    "stale_review_title_revision", last_approved,
                                                    last_approved_digest),
        }
    report["ok"] = not (
        report["spec"]["stale_identity"] or report["spec"]["missing_added_records"]
        or report["spec"]["stale_title_revision"]
        or (review_text is not None and (report["review"]["stale_identity"] or report["review"]["stale_title_revision"]))
    )
    return report


def _full_record(record: dict[str, object]) -> list[str]:
    """Every field of a record, one Markdown sub-bullet each (string lists one line per item)."""
    lines = []
    for key, value in record.items():
        if key == "id":
            continue
        if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
            lines.append(f"  - {key}:")
            lines.extend(f"    - {item}" for item in value)
        elif isinstance(value, (dict, list)):
            lines.append(f"  - {key}: `{json.dumps(value, ensure_ascii=False)}`")
        else:
            lines.append(f"  - {key}: {value}")
    return lines


def draft(state: dict[str, object], full: bool = False) -> str:
    """Identity lines plus the current text of every added/changed record, as Markdown.

    full=True adds every field of each added/changed record (FLOW paths and outcomes, STATE
    conditions, DATA purpose, SCR major_actions, ...) under its one-line summary."""
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
        (f"## Records changed since revision {manifest['from_revision']} (condense into the spec; do not paste blindly)"
         if manifest["from_revision"] is not None
         else "## Records of the first approval (condense into the spec; do not paste blindly)"),
        "",
    ]
    index = canonical_record_index(state) if full else {}
    for category in ("added", "changed", "superseded", "retired"):
        for row in manifest[category]:
            text = str(row["summary"]).replace("\n", " ")
            lines.append(f"- {category} `{row['id']}`: {text}")
            if full and row["id"] in index:
                lines.extend(_full_record(index[row["id"]][1]))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--spec", required=True, help="MASTER_PLANNING_SPEC.md")
    parser.add_argument("--review", help="planning-review-core.html")
    parser.add_argument("--require-types", default=DEFAULT_REQUIRED_TYPES,
                        help=f"record types the spec must name when added (default {DEFAULT_REQUIRED_TYPES})")
    parser.add_argument("--draft", action="store_true", help="print a Markdown draft instead of the JSON check")
    parser.add_argument("--full", action="store_true", help="with --draft: every field of each added/changed record")
    args = parser.parse_args(argv)
    try:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        spec_text = Path(args.spec).read_text(encoding="utf-8")
        review_text = Path(args.review).read_text(encoding="utf-8") if args.review else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    if args.draft:
        print(draft(state, full=args.full), end="")
        return 0
    report = check(state, spec_text, review_text, {t.strip() for t in args.require_types.split(",") if t.strip()})
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
