#!/usr/bin/env python3
"""Refresh the mechanical parts of MASTER_PLANNING_SPEC.md and planning-review-core.html.

The condensed product text stays hand-written. This rewrites only what the state
decides on its own:
  * blocks between <!-- JOEFLOW:IDENTITY:BEGIN --> / END and
    <!-- JOEFLOW:SOURCE-MAP:BEGIN --> / END, regenerated whole;
  * outside those blocks, the first `code` value after the labels "Revision:",
    "Definition digest:" and "Approval Manifest digest:"/"Approval Manifest:",
    "revision N" in the review header, and approval-manifest-rN.json links.
It then lists, per added/changed/superseded/retired record, the document lines that
name it, so the author edits exactly those rows. Without --write nothing is written.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path

from approval_status import approval_status
from approval_v2 import approval_manifest_digest, compute_approval_manifest, definition_digest
from cli_output import use_utf8_stdio


TYPE_LABELS = {  # objects key -> (prefix, Korean label, English label)
    "goals": ("GOAL", "목표", "Goals"), "users": ("USR", "사용자", "Users"),
    "requirements": ("REQ", "요구사항", "Requirements"), "decisions": ("DEC", "결정", "Decisions"),
    "rules": ("RULE", "규칙", "Rules"), "flows": ("FLOW", "흐름", "Flows"),
    "screens": ("SCR", "화면", "Screens"), "states": ("STATE", "상태", "States"),
    "data": ("DATA", "데이터", "Data"), "integrations": ("INT", "연동", "Integrations"),
    "acceptance_criteria": ("AC", "완료 기준", "Acceptance criteria"), "tasks": ("TASK", "작업", "Tasks"),
    "unknowns": ("UNK", "질문", "Unknowns"),
}
BLOCK = "<!-- JOEFLOW:{name}:BEGIN -->\n{body}\n<!-- JOEFLOW:{name}:END -->"
BLOCK_RE = r"<!-- JOEFLOW:{name}:BEGIN -->\n.*?\n<!-- JOEFLOW:{name}:END -->"


def _mentions(text: str, record_id: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(record_id)}(?![\w-])", text) is not None


def facts(state: dict[str, object]) -> dict[str, object]:
    project = state["project"]
    approval = state.get("approval") if isinstance(state.get("approval"), dict) else {}
    manifest = compute_approval_manifest(state)
    approved = approval.get("status") == "APPROVED" and approval.get("approved_revision") == project["definition_revision"]
    history = [entry for entry in state.get("approval_history") or [] if isinstance(entry, dict)]
    status = approval_status(state)
    return {
        "revision": project["definition_revision"],
        "definition_status": project.get("definition_status"),
        "approval_status": approval.get("status"),
        "approved": approved,
        "approved_at": approval.get("approved_at") if approved else None,
        "definition_digest": definition_digest(state),
        "manifest_digest": approval.get("approved_manifest_digest") if approved else approval_manifest_digest(manifest),
        "previous": [(entry["revision"], entry.get("manifest_digest"))
                     for entry in history if entry.get("revision") != project["definition_revision"]],
        "bundled": status["revisions_without_own_approval"],
        "manifest": manifest,
    }


def identity_block(f: dict[str, object], korean: bool, html: bool, manifest_file: str | None = None) -> str:
    m = f["manifest"]
    counts = {key: len(m[key]) for key in ("added", "changed", "superseded", "retired")}
    previous = ", ".join(f"rev {rev} `{(digest or '')[:8]}…`" for rev, digest in f["previous"]) or ("없음" if korean else "none")
    bundled = ", ".join(map(str, f["bundled"]))
    if korean:
        state_text = "승인됨" if f["approved"] else "승인 대기"
        rows = [
            f"Revision: `{f['revision']}` · {f['definition_status']} · {state_text}"
            + (f" ({f['approved_at']})" if f["approved_at"] else ""),
            f"Definition digest: `{f['definition_digest']}`",
            f"Approval Manifest digest: `{f['manifest_digest']}`"
            + f" (rev {m['from_revision']}→{f['revision']}: 추가 {counts['added']} · 변경 {counts['changed']} · 대체 {counts['superseded']} · 폐기 {counts['retired']})",
            f"이전 승인: {previous}" + (f" (rev {bundled}은 다음 승인에 포함)" if bundled else ""),
        ]
    else:
        state_text = "approved" if f["approved"] else "pending approval"
        rows = [
            f"Revision: `{f['revision']}` · {f['definition_status']} · {state_text}"
            + (f" ({f['approved_at']})" if f["approved_at"] else ""),
            f"Definition digest: `{f['definition_digest']}`",
            f"Approval Manifest digest: `{f['manifest_digest']}`"
            + f" (rev {m['from_revision']}→{f['revision']}: added {counts['added']} · changed {counts['changed']} · superseded {counts['superseded']} · retired {counts['retired']})",
            f"Previous approvals: {previous}" + (f" (rev {bundled} were approved inside a later Manifest)" if bundled else ""),
        ]
    if manifest_file:
        rows[2] += f" ({manifest_file})" if html else f" ([{manifest_file}]({manifest_file}))"
    if html:
        if manifest_file:
            rows[2] = rows[2].replace(f"({manifest_file})", f'(<a href="{manifest_file}">{manifest_file}</a>)')
        return "\n".join("<li>" + re.sub(r"`([^`]*)`", r"<code>\1</code>", row) + "</li>" for row in rows)
    return "\n".join(f"- {row}" for row in rows)


def source_map_block(state: dict[str, object], korean: bool) -> str:
    objects = state.get("objects") if isinstance(state.get("objects"), dict) else {}
    head = "| 종류 | 현재 | 대체·폐기 |\n|---|---|---|" if korean else "| Type | Current | Superseded or retired |\n|---|---|---|"
    lines = [head]
    for key, (prefix, ko, en) in TYPE_LABELS.items():
        records = [r for r in objects.get(key) or [] if isinstance(r, dict) and isinstance(r.get("id"), str)]
        if not records:
            continue
        current = [r["id"] for r in records if r.get("status") not in {"SUPERSEDED", "RETIRED"}]
        old = [r["id"] for r in records if r.get("status") in {"SUPERSEDED", "RETIRED"}]
        lines.append(f"| {ko if korean else en} (`/objects/{key}`) | {', '.join(current) or '-'} | {', '.join(old) or '-'} |")
    return "\n".join(lines)


def _replace_block(text: str, name: str, body: str) -> tuple[str, bool]:
    pattern = re.compile(BLOCK_RE.format(name=name), re.S)
    if not pattern.search(text):
        return text, False
    return pattern.sub(lambda _: BLOCK.format(name=name, body=body), text, count=1), True


def _outside_blocks(text: str, edit) -> str:
    parts = re.split(r"(<!-- JOEFLOW:[A-Z-]+:BEGIN -->.*?<!-- JOEFLOW:[A-Z-]+:END -->)", text, flags=re.S)
    return "".join(part if part.startswith("<!-- JOEFLOW:") else edit(part) for part in parts)


LABEL_LINE = re.compile(
    r"^(?:- |\s*<li>)(?:Revision|Definition digest|Approval Manifest(?: digest)?|Status|이전 승인|Previous approvals)\b.*$", re.M)


def adopt(text: str) -> tuple[str, bool]:
    """Wrap the first run of consecutive identity label lines in an IDENTITY block."""
    if "<!-- JOEFLOW:IDENTITY:BEGIN -->" in text:
        return text, False
    lines = text.split("\n")
    start = next((i for i, line in enumerate(lines) if LABEL_LINE.match(line)), None)
    if start is None:
        return text, False
    end = start
    while end + 1 < len(lines) and LABEL_LINE.match(lines[end + 1]):
        end += 1
    block = BLOCK.format(name="IDENTITY", body="\n".join(lines[start:end + 1])).split("\n")
    return "\n".join(lines[:start] + block + lines[end + 1:]), True


def refresh(text: str, f: dict[str, object], state: dict[str, object], html: bool,
            adopt_identity: bool = False, manifest_file: str | None = None) -> tuple[str, list[str]]:
    korean = re.search(r"[가-힣]", text) is not None
    notes = []
    if adopt_identity:
        text, adopted = adopt(text)
        if adopted:
            notes.append("identity label lines wrapped in a generated block")
    text, found = _replace_block(text, "IDENTITY", identity_block(f, korean, html, manifest_file))
    notes.append("identity block regenerated" if found else "no identity block; label lines updated only")
    if not html:
        text, found = _replace_block(text, "SOURCE-MAP", source_map_block(state, korean))
        if found:
            notes.append("source map block regenerated")
    value = {"Revision": str(f["revision"]), "Definition digest": f["definition_digest"],
             "Approval Manifest digest": f["manifest_digest"], "Approval Manifest": f["manifest_digest"]}

    def labels(part: str) -> str:
        for label, new in value.items():
            if new is None:
                continue
            part = re.sub(rf"({re.escape(label)}:\s*)`[^`\n]*`", lambda m: f"{m.group(1)}`{new}`", part)
            part = re.sub(rf"({re.escape(label)}:\s*)<code>[^<\n]*</code>", lambda m: f"{m.group(1)}<code>{new}</code>", part)
        part = re.sub(r"(?i)(REVIEW VIEW[^\n<]*?\brevision )\d+", lambda m: f"{m.group(1)}{f['revision']}", part)
        return re.sub(r"approval-manifest-r\d+\.json", f"approval-manifest-r{f['revision']}.json", part)

    text = _outside_blocks(text, labels)
    # A label line with more text after its value (time, counts, earlier approvals) is only partly updated.
    for number, line in _hand_written_lines(text):
        bare = re.sub(r"</li>\s*$", "", line)
        if LABEL_LINE.match(line) and re.search(r"(?:`|</code>)(?=[^`]*$)(?![^`]*</code>)\s*\S", bare):
            notes.append(f"line {number}: text after the updated value is not maintained; check it or use --adopt")
    return text, notes


def _hand_written_lines(text: str) -> list[tuple[int, str]]:
    lines, depth = [], 0
    for number, line in enumerate(text.split("\n"), 1):
        if re.match(r"<!-- JOEFLOW:[A-Z-]+:BEGIN -->", line):
            depth += 1
        elif re.match(r"<!-- JOEFLOW:[A-Z-]+:END -->", line):
            depth -= 1
        elif depth == 0:
            lines.append((number, line))
    return lines


def worklist(f: dict[str, object], docs: dict[str, str]) -> list[dict[str, object]]:
    rows = []
    hand = {name: _hand_written_lines(text) for name, text in docs.items()}
    for category in ("added", "changed", "superseded", "retired"):
        for row in f["manifest"][category]:
            where = {
                name: [n for n, line in lines if _mentions(line, row["id"])]
                for name, lines in hand.items()
            }
            rows.append({"id": row["id"], "category": category, "lines": where,
                         "current_text": str(row["summary"]).replace("\n", " ")})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--spec", required=True, help="MASTER_PLANNING_SPEC.md")
    parser.add_argument("--review", help="planning-review-core.html")
    parser.add_argument("--write", action="store_true", help="write the refreshed files (default: show the diff only)")
    parser.add_argument("--adopt", action="store_true",
                        help="wrap existing identity label lines in a generated IDENTITY block (once per document)")
    args = parser.parse_args(argv)
    try:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        paths = {"spec": Path(args.spec)} | ({"review": Path(args.review)} if args.review else {})
        before = {name: path.read_bytes().decode("utf-8") for name, path in paths.items()}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    f = facts(state)
    saved = paths["spec"].parent / f"approval-manifest-r{f['revision']}.json"
    manifest_file = saved.name if saved.is_file() else None
    after, notes, diffs = {}, {}, {}
    for name, raw in before.items():
        newline = "\r\n" if "\r\n" in raw else "\n"  # work on LF, keep the file's own line endings
        text = raw.replace("\r\n", "\n")
        after[name], notes[name] = refresh(text, f, state, html=name == "review", adopt_identity=args.adopt,
                                           manifest_file=manifest_file)
        diffs[name] = "".join(difflib.unified_diff(
            text.splitlines(True), after[name].splitlines(True), str(paths[name]), str(paths[name]), n=0))
        if args.write and after[name] != text:
            paths[name].write_bytes(after[name].replace("\n", newline).encode("utf-8"))
    report = {
        "ok": True, "written": args.write, "revision": f["revision"],
        "compared_with_revision": f["manifest"]["from_revision"], "notes": notes,
        "changed_lines": {name: sum(1 for line in d.splitlines() if line[:1] in "+-" and not line.startswith(("+++", "---")))
                          for name, d in diffs.items()},
        "records_to_edit_by_hand": worklist(f, after),
        "diff": diffs,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
