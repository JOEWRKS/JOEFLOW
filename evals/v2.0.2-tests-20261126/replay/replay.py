#!/usr/bin/env python3
"""Replay one ATELIER revision with the JOEFLOW 2.0.2 builders only.

Input: the committed state.json of revision N-1 (BASE), the committed state.json of
revision N (TARGET) and the patch the user's session applied (ORIGINAL_PATCH, used only to
know which records revision N touched). The driver writes the builder commands an author
would type — question/resolve/requirement for the product records, edit for record text —
taking the words from TARGET, runs them through new_records.py, applies the patch with
open_revision.py and compares definition_digest with TARGET. No patch JSON is written by
hand: every record in the patch comes out of new_records.py.

Fields a builder refuses to reproduce (the derivation does not allow them) are listed, then
copied from TARGET into a scratch copy of the replay to show that the digest matches once
exactly those fields are restored.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path


PROTECTED = {"status", "resolution_mode", "decision_authority", "resolved_by", "accepted_recommendation",
             "source_unknown_refs", "decided_by", "resolution_summary"}
INTENT_KINDS = {"USER_CONFIRMED_INTENT", "RELAYED_USER_INTENT", "USER_STATED_PREFERENCE"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def index(state):
    found = {}
    for record in state.get("evidence", []):
        found[record["id"]] = ("evidence", record)
    for group, records in state["objects"].items():
        for record in records:
            found[record["id"]] = (group, record)
    for record in state["surface_manifest"]["records"]:
        found[record["id"]] = ("surfaces", record)
    return found


class Runner:
    def __init__(self, skill, workdir, log):
        self.scripts = Path(skill) / "scripts"
        self.workdir = Path(workdir)
        self.log = log
        self.count = 0

    def run(self, script, *args, expect=None):
        self.count += 1
        argv = [sys.executable, "-B", str(self.scripts / script), *map(str, args)]
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        result = subprocess.run(argv, capture_output=True, stdin=subprocess.DEVNULL, env=env, cwd=self.workdir)
        out = result.stdout.decode("utf-8")
        shown = f"python {script} " + " ".join(shlex.quote(str(a)) for a in args)
        self.log.write(f"\n### {self.count}. exit {result.returncode}\n\n```\n{shown}\n```\n\n```json\n{out.strip()}\n```\n")
        if result.stderr:
            self.log.write(f"\nstderr:\n```\n{result.stderr.decode('utf-8').strip()}\n```\n")
        return result.returncode, out


def materiality_arg(m):
    flags = [flag for flag, value in m["risk_flags"].items() if value]
    return ",".join([m["outcome_divergence"], m["fan_out"], "true" if m["user_visible"] else "false", m["reversibility"], *flags])


def chosen_option(unknown, decision):
    if decision.get("accepted_recommendation"):
        return decision["accepted_recommendation"]["recommended_option"]
    ids = [o["id"] for o in unknown["options"]]
    for token in re.findall(r"OPT-[A-Z0-9-]+", unknown.get("resolution_summary") or ""):
        token = token.rstrip("-")
        if token in ids:
            return token
    for option in unknown["options"]:
        if option["statement"] and option["statement"] in decision["statement"]:
            return option["id"]
    return (unknown.get("recommendation") or {}).get("recommended_option") or ids[0]


def question_args(unknown, base_index):
    args = ["question", "--unknown", unknown["id"], "--question", unknown["question"], "--why", unknown["why_it_matters"],
            "--category", unknown["question_category"], "--materiality", materiality_arg(unknown["materiality"])]
    for option in unknown["options"]:
        args += ["--option", f"{option['id']}=" + "|".join([option["statement"], *option["consequences"]])]
    for ref in unknown["affects"]:
        args += ["--affects", ref]
    origin = unknown["origin"]
    if origin["kind"] == "PRODUCT_SURFACE":
        args += ["--surface", origin["surface_ref"]]
    elif origin["kind"] == "GRILL_PACK_AXIS":
        args += ["--pack", origin["pack_id"], "--axis", origin["axis_id"], "--surface", origin["surface_ref"]]
    elif origin["kind"] == "GRILL_TOPOLOGY":
        args += ["--pack", origin["pack_id"]]
    moved = []
    for ref in unknown["evidence_refs"]:
        kind = base_index.get(ref, ("", {}))[1].get("source_kind")
        if kind in INTENT_KINDS:
            moved.append(ref)  # first-plan-guide: the user's intent is a reason, not evidence that answers the question
        else:
            args += ["--evidence", ref]
    rec = unknown.get("recommendation")
    if rec:
        args += ["--recommend", rec["recommended_option"], "--confidence", rec["confidence"]]
        for ref in rec["reasoning_refs"]:
            args += ["--reason", ref]
        for item in rec["tradeoffs"]:
            args += ["--tradeoff", item]
    return args, moved


def string_edits(old, new, path=""):
    """(pointer, old_text, new_text) for every string leaf that differs; ('json', pointer, value) otherwise."""
    if isinstance(old, dict) and isinstance(new, dict) and set(old) == set(new):
        for key in old:
            if key != "id":
                yield from string_edits(old[key], new[key], f"{path}/{key}")
    elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for position, (a, b) in enumerate(zip(old, new)):
            yield from string_edits(a, b, f"{path}/{position}")
    elif isinstance(old, str) and isinstance(new, str):
        if old != new:
            yield ("text", path, old, new)
    elif old != new:
        yield ("json", path, old, new)


def minimal_replace(record, old, new):
    """The shortest OLD span (around the change) that occurs once in the record, and its replacement."""
    prefix = 0
    while prefix < min(len(old), len(new)) and old[prefix] == new[prefix]:
        prefix += 1
    suffix = 0
    while suffix < min(len(old), len(new)) - prefix and old[-1 - suffix] == new[-1 - suffix]:
        suffix += 1
    texts = [text for _, text in _strings(record)]
    left, right = prefix, len(old) - suffix
    while True:
        span = old[left:right]
        if span and sum(text.count(span) for text in texts) == 1:
            return span, new[left:len(new) - (len(old) - right)]
        if left == 0 and right == len(old):
            return None
        left, right = max(0, left - 8), min(len(old), right + 8)


def _strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            if key != "id":
                yield from _strings(item, f"{path}/{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _strings(item, f"{path}/{i}")


def field_diffs(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            yield from field_diffs(a.get(key), b.get(key), f"{path}/{key}")
    elif a != b:
        yield path, a, b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--original-patch", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base, target, original = load(args.base), load(args.target), load(args.original_patch)
    sys.path.insert(0, str(Path(args.skill) / "scripts"))
    from approval_v2 import definition_digest  # noqa: E402

    state_path, patch_path = out / "state.json", out / "patch.json"
    state_path.write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if patch_path.exists():
        patch_path.unlink()
    base_index, target_index = index(base), index(target)
    touched = [r["id"] for g in original.get("objects", {}).values() for r in g] + [r["id"] for r in original.get("surfaces", [])]
    with (out / "commands.md").open("w", encoding="utf-8", newline="\n") as log:
        log.write(f"# Replay {args.label}: builder commands and their output\n\nBase: revision {base['project']['definition_revision']}"
                  f" (committed). Target: revision {target['project']['definition_revision']} (committed).\n")
        run = Runner(args.skill, out, log)
        common = ["--state", state_path.name, "--patch", patch_path.name]
        moved_evidence = {}
        # 1. new questions (asked and answered in this revision) and answers to existing ones
        unknown_ids = [r["id"] for r in original.get("objects", {}).get("unknowns", [])]
        for unknown_id in unknown_ids:
            unknown = target_index[unknown_id][1]
            existed = unknown_id in base_index
            if not existed:
                qargs, moved = question_args(unknown, base_index)
                if moved:
                    moved_evidence[unknown_id] = moved
                run.run("new_records.py", *common, *qargs)
            if unknown["status"] == "RESOLVED" and (not existed or base_index[unknown_id][1]["status"] == "OPEN"):
                decision = target_index[unknown["resolved_by"][0]][1]
                rargs = ["resolve", unknown_id, "--option", chosen_option(unknown, decision),
                         "--summary", unknown["resolution_summary"], "--statement", decision["statement"],
                         "--decision", decision["id"], "--decision-type", decision["decision_type"]]
                if sorted(decision["affects"]) != sorted(unknown["affects"]):
                    for ref in decision["affects"]:
                        rargs += ["--decision-affects", ref]
                code, _ = run.run("new_records.py", *common, *rargs)
                if code != 0 and decision["resolution_mode"] == "USER_ACCEPTED_RECOMMENDATION":
                    log.write("\nThe derivation refused the recorded mode; the author drops --accepted-style recording "
                              "and the builder derives the mode:\n")
        # 2. requirements drafted from decisions for surfaces that became IN_SCOPE
        for requirement in original.get("objects", {}).get("requirements", []):
            if requirement["id"] in base_index:
                continue
            final = target_index[requirement["id"]][1]
            owners = [s for s in target["surface_manifest"]["records"] if requirement["id"] in s.get("authority_refs", [])]
            decisions = [d for d in dict.fromkeys(re.findall(r"DEC-\d+", final["statement"])) if d in target_index]
            for surface in owners:
                run.run("new_records.py", *common, "requirement", "--from-decisions", ",".join(decisions),
                        "--surface", surface["id"], "--requirement", requirement["id"], "--statement", final["statement"],
                        "--scope", final["scope"], "--ui-required", "true" if final["ui_required"] else "false")
        # 3. text edits for every other touched record, then anything left on the touched records
        def overlay():
            patch = load(patch_path) if patch_path.exists() else {}
            found = index(base)
            for g, records in patch.get("objects", {}).items():
                for r in records:
                    found[r["id"]] = (g, r)
            for r in patch.get("surfaces", []):
                found[r["id"]] = ("surfaces", r)
            return found
        refused = []
        for record_id in touched:
            now = overlay().get(record_id)
            final = target_index[record_id][1]
            if now is None:
                refused.append({"record": record_id, "reason": "no builder produced this record"})
                continue
            edits, protected = [], []
            for kind, pointer, old, new in string_edits(now[1], final):
                if pointer.lstrip("/").split("/")[0] in PROTECTED or pointer.startswith("/evidence_refs") \
                        or pointer.startswith("/accepted_recommendation"):
                    protected.append((pointer, old, new))
                    continue
                if kind == "text":
                    span = minimal_replace(now[1], old, new)
                    edits += ["--replace-text", *span] if span else ["--set", pointer, new]
                else:
                    edits += ["--set-json", pointer, json.dumps(new, ensure_ascii=False)]
            if set(now[1]) != set(final):
                protected.append(("(field set)", sorted(now[1]), sorted(final)))
            if edits:
                run.run("new_records.py", *common, "edit", record_id, *edits)
            for pointer, old, new in protected:
                refused.append({"record": record_id, "field": pointer, "builder": old, "committed": new})
        # 4. apply
        status = target["project"]["definition_status"]
        status = "READY_FOR_REVIEW" if status in {"CLOSED", "READY_FOR_REVIEW"} else status
        code, report = run.run("open_revision.py", state_path.name, "--patch", patch_path.name, "--status", status, "--write")
    replay = load(state_path)
    result = {"label": args.label, "base_revision": base["project"]["definition_revision"],
              "target_revision": target["project"]["definition_revision"], "open_revision_exit": code,
              "written": json.loads(report).get("written"), "commands": run.count,
              "target_definition_digest": definition_digest(target),
              "replay_definition_digest": definition_digest(replay) if replay["project"]["definition_revision"] != base["project"]["definition_revision"] else None,
              "intent_evidence_moved_to_reason": moved_evidence}
    result["digest_equal"] = result["target_definition_digest"] == result["replay_definition_digest"]
    # per-record differences between the replay and the committed revision
    diffs = []
    replay_index = index(replay)
    for record_id in sorted(set(replay_index) | set(target_index)):
        a = replay_index.get(record_id, (None, None))[1]
        b = target_index.get(record_id, (None, None))[1]
        if a != b:
            diffs.append({"record": record_id, "fields": [{"field": f, "replay": x, "committed": y} for f, x, y in field_diffs(a or {}, b or {})]})
    for table in ("coverage", "grill_coverage", "ux_coverage"):
        if replay.get(table) != target.get(table):
            diffs.append({"record": table, "fields": [{"field": "(table)", "replay": "differs", "committed": "differs"}]})
    if replay["surface_manifest"].get("grill_profile") != target["surface_manifest"].get("grill_profile"):
        diffs.append({"record": "grill_profile", "fields": [{"field": "(profile)", "replay": "differs", "committed": "differs"}]})
    result["differences"] = diffs
    result["fields_the_builders_refused"] = refused
    if diffs and result["replay_definition_digest"]:
        restored = copy.deepcopy(replay)
        restored_index = index(restored)
        for item in diffs:
            if item["record"] in restored_index and item["record"] in target_index:
                group, record = restored_index[item["record"]]
                record.clear()
                record.update(copy.deepcopy(target_index[item["record"]][1]))
        from revision_v2 import refresh_bindings  # noqa: E402
        refresh_bindings(restored, {d["record"] for d in diffs})
        result["digest_after_restoring_listed_records"] = definition_digest(restored)
        result["digest_equal_after_restoring"] = result["digest_after_restoring_listed_records"] == result["target_definition_digest"]
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {"differences"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
