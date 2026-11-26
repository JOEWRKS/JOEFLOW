#!/usr/bin/env python3
"""Select one canonical product question for user authority, or list them grouped.

  next_product_question.py STATE_JSON              the one highest-leverage question
  next_product_question.py STATE_JSON --grouped    every askable OPEN question, grouped by
                                                   pack (and target surface) or surface, as
                                                   a recommendation table per group
  ... --grouped --markdown                         the same tables as Markdown to show the user

Independent pack axes (independent_decision true, nothing blocking them) may be
presented as one table and answered together ("all as recommended"); record that answer
with new_records.py resolve --accept-recommended --pack PACK (workflow CLOSE).
"""

from __future__ import annotations

import argparse
import json
import sys

from cli_output import use_utf8_stdio
from grill_v2 import load_grill_packs, project_user_question, question_priority_key, select_next_user_question
from state_validation import load_state
from state_validation_v2 import validate_state_v2


ASKABLE = {"USER_CONFIRMATION", "USER_DECISION_REQUIRED"}


def _error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _write(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def grouped_questions(state: dict[str, object]) -> list[dict[str, object]]:
    errors = validate_state_v2(state)
    if errors:
        raise ValueError(errors)
    unknowns = state["objects"]["unknowns"]
    open_ids = {u["id"] for u in unknowns if u["status"] == "OPEN"}
    blocked_by: dict[str, list[str]] = {}
    for unknown in unknowns:
        if unknown["status"] == "OPEN":
            for target in unknown["blocks_unknown_refs"]:
                blocked_by.setdefault(target, []).append(unknown["id"])
    independent = {(pack["pack_id"], axis["id"]) for pack in load_grill_packs().values()
                   for axis in pack["axes"] if axis.get("independent_decision") is True}
    groups: dict[tuple[str, ...], list[dict[str, object]]] = {}
    for unknown in unknowns:
        if unknown["status"] != "OPEN" or unknown["decision_authority"] not in ASKABLE:
            continue
        origin = unknown["origin"]
        if origin["kind"] == "GRILL_PACK_AXIS":
            key = ("pack", origin["pack_id"], origin["surface_ref"] or "")
        elif origin["kind"] == "GRILL_TOPOLOGY":
            key = ("topology", "", "")
        elif origin["surface_ref"]:
            key = ("surface", "", origin["surface_ref"])
        else:
            key = ("manual", "", "")
        groups.setdefault(key, []).append(unknown)
    result = []
    for key, members in groups.items():
        members.sort(key=question_priority_key)
        kind, pack_id, surface = key
        rows = []
        for unknown in members:
            recommendation = unknown["recommendation"] or {}
            rows.append({
                **project_user_question(unknown),
                "decision_authority": unknown["decision_authority"],
                "recommended_option": recommendation.get("recommended_option"),
                "confidence": recommendation.get("confidence"),
                "axis_id": unknown["origin"]["axis_id"],
                "blocked_by": [ref for ref in blocked_by.get(unknown["id"], []) if ref in open_ids],
                "blocks": [ref for ref in unknown["blocks_unknown_refs"] if ref in open_ids],
            })
        table_ready = (kind == "pack" and all(
            (pack_id, row["axis_id"]) in independent and not row["blocked_by"] and not row["blocks"] for row in rows))
        all_recommended = all(row["recommended_option"] for row in rows)
        group = {"group": kind, "pack_id": pack_id or None, "surface": surface or None, "count": len(rows),
                 "present_as_one_table": table_ready, "all_recommended": all_recommended, "questions": rows}
        if table_ready and all_recommended:
            group["record_all_as_recommended"] = (
                f"new_records.py --state STATE --patch PATCH resolve --accept-recommended --pack {pack_id}"
                + (f" --surface {surface}" if surface else "") + " --words \"<the user's words>\"")
        elif not table_ready:
            group["why_not_one_table"] = ("only independent pack axes with nothing blocking them are presented together; "
                                          "ask these one at a time, highest leverage first")
        result.append(group)
    result.sort(key=lambda g: question_priority_key(next(u for u in unknowns if u["id"] == g["questions"][0]["unknown_id"])))
    return result


def markdown(groups: list[dict[str, object]]) -> str:
    lines = []
    for group in groups:
        title = {"pack": f"{group['pack_id']} · {group['surface']}", "topology": "topology domains",
                 "surface": f"surface {group['surface']}", "manual": "other questions"}[group["group"]]
        lines += [f"### {title} ({group['count']})", "",
                  "| ID | question | options | recommended | why it matters |", "|---|---|---|---|---|"]
        for row in group["questions"]:
            options = "<br>".join(f"{o['id']}: {o['statement']}" for o in row["options"])
            rec = row["recommended_option"] or "—"
            if row["recommendation"]:
                rec += f" ({row['confidence']}; " + "; ".join(row["recommendation"]["tradeoffs"]) + ")"
            cell = lambda text: str(text).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {row['unknown_id']} | {cell(row['question'])} | {cell(options)} | {cell(rec)} | {cell(row['why_it_matters'])} |")
        lines.append("")
        if group.get("record_all_as_recommended"):
            lines += [f"All as recommended: `{group['record_all_as_recommended']}`", ""]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state")
    parser.add_argument("--grouped", action="store_true", help="every askable OPEN question, grouped")
    parser.add_argument("--markdown", action="store_true", help="with --grouped: Markdown tables instead of JSON")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit as exc:
        if exc.code == 0:
            return 0
        _write({"next_question": None, "errors": [_error(
            "usage_error", "usage: next_product_question.py STATE_JSON [--grouped [--markdown]]", "")]})
        return 2

    try:
        state = load_state(args.state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _write({"next_question": None, "errors": [_error("read_error", str(exc), args.state)]})
        return 2

    try:
        if args.grouped:
            groups = grouped_questions(state)
        else:
            question = select_next_user_question(state)
    except ValueError as exc:
        errors = exc.args[0]
        _write({"next_question": None, "errors": errors})
        return 1

    if args.grouped:
        if args.markdown:
            print(markdown(groups), end="")
        else:
            _write({"groups": groups, "open_questions": sum(g["count"] for g in groups)})
        return 0
    _write({"next_question": question})
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main(sys.argv))
