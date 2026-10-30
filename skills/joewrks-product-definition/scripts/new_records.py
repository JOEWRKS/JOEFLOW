#!/usr/bin/env python3
"""Append complete evidence, unknown, and decision records to a revision patch file.

Each subcommand takes only the fields an author decides and fills the rest of
the V2 record shape. Apply the patch with open_revision.py, which validates it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import record_builders as build
from cli_output import use_utf8_stdio


def _option(text: str) -> dict[str, object]:
    option_id, sep, rest = text.partition("=")
    if not sep or not option_id.strip():
        raise argparse.ArgumentTypeError(f"option must be ID=statement|consequence...; got {text!r}")
    statement, *consequences = rest.split("|")
    consequences = [item.strip() for item in consequences if item.strip()]
    if not statement.strip() or not consequences:
        raise argparse.ArgumentTypeError(f"option needs a statement and at least one consequence (ID=statement|consequence); got {text!r}")
    return build.option(option_id.strip(), statement.strip(), *consequences)


def _materiality(text: str) -> dict[str, object]:
    parts = [item.strip() for item in text.split(",")]
    if len(parts) < 4 or parts[2] not in {"true", "false"}:
        raise argparse.ArgumentTypeError(
            "materiality must be DIVERGENCE,FAN_OUT,true|false,REVERSIBILITY[,RISK_FLAG...]; "
            f"risk flags: {', '.join(build.RISK_FLAGS)}"
        )
    return build.materiality(parts[0], parts[1], parts[2] == "true", parts[3], tuple(parts[4:]))


def _common_question(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--unknown", required=True, help="new UNK ID")
    parser.add_argument("--question", required=True)
    parser.add_argument("--why", required=True, help="why_it_matters")
    parser.add_argument("--category", default="CORE_FLOW",
                        choices=["CORE_FLOW", "SCOPE_BOUNDARY", "STATE_RECOVERY", "SECONDARY_BEHAVIOR", "PREFERENCE", "COSMETIC"])
    parser.add_argument("--option", action="append", type=_option, required=True, help="ID=statement|consequence (repeat)")
    parser.add_argument("--affects", action="append", required=True, help="affected ID (repeat)")
    parser.add_argument("--evidence", action="append", required=True, help="EVD ID behind the question (repeat)")
    parser.add_argument("--surface", help="SURF ID the question came from (origin PRODUCT_SURFACE)")
    parser.add_argument("--materiality", type=_materiality, help="default HIGH,MULTI_FLOW,true,REVERSIBLE")
    parser.add_argument("--recommend", help="recommended option ID")
    parser.add_argument("--reason", action="append", default=[], help="reasoning_refs for the recommendation (repeat)")
    parser.add_argument("--tradeoff", action="append", default=[], help="tradeoff shown with the recommendation (repeat)")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--patch", required=True, help="patch JSON file to create or append to")
    sub = parser.add_subparsers(dest="kind", required=True)

    ev = sub.add_parser("evidence", help="one evidence record")
    ev.add_argument("--id", required=True)
    ev.add_argument("--source-kind", required=True)
    ev.add_argument("--class", dest="classes", action="append", required=True, help="authority class (repeat)")
    ev.add_argument("--locator", required=True)
    ev.add_argument("--claim", required=True)
    ev.add_argument("--confidence", default="DIRECT")

    question = sub.add_parser("question", help="an OPEN unknown to ask the user")
    _common_question(question)

    decided = sub.add_parser("user-decision", help="a RESOLVED unknown plus the CURRENT decision the user stated")
    _common_question(decided)
    decided.add_argument("--decision", required=True, help="new DEC ID")
    decided.add_argument("--statement", required=True, help="decision statement")
    decided.add_argument("--summary", required=True, help="resolution_summary, quoting the user")
    decided.add_argument("--decision-type", default="PRODUCT_BEHAVIOR")
    decided.add_argument("--accepted", action="store_true", help="the user accepted the recommendation")
    decided.add_argument("--decision-affects", action="append",
                         help="decision affects when wider than the question's, e.g. the REQ it changes (repeat)")
    decided.add_argument("--address", action="append", default=[], metavar="CELL",
                         help="coverage cell this decision now answers, e.g. grill_coverage[GRILL-ASYNC-1].axes.retry;"
                              " the patch replaces it with ADDRESSED/COVERED bound to the decision statement (repeat)")

    authoring = sub.add_parser("authoring", help="a non-material agent authoring unknown plus its decision")
    authoring.add_argument("--unknown", required=True)
    authoring.add_argument("--decision", required=True)
    authoring.add_argument("--task", required=True, help="what is being written, e.g. 'rev 31 decisions into RULE/AC records'")
    authoring.add_argument("--why", required=True)
    authoring.add_argument("--summary", required=True)
    authoring.add_argument("--statement", required=True)
    authoring.add_argument("--affects", action="append", required=True)
    authoring.add_argument("--evidence", action="append", required=True)
    authoring.add_argument("--surface")
    authoring.add_argument("--option", action="append", type=_option, help="override the two default authoring options")
    authoring.add_argument("--address", action="append", default=[], metavar="CELL", help="as for user-decision (repeat)")
    return parser


def address_cells(decision_id: str, cells: list[str]) -> list[dict[str, object]]:
    """Cell edits that close the OPEN cells a resolved unknown was holding open."""
    return [{
        "cell": cell,
        "replace": {"status": "ADDRESSED" if cell.startswith("grill_coverage[") else "COVERED",
                    "bind": [{"record_id": decision_id, "pointer": "/statement"}]},
    } for cell in cells]


def build_records(args: argparse.Namespace) -> dict[str, list[dict[str, object]]]:
    if args.kind == "evidence":
        return {"evidence": [build.evidence(args.id, source_kind=args.source_kind, authority_classes=args.classes,
                                            locator=args.locator, claim=args.claim, confidence=args.confidence)]}
    if args.kind == "authoring":
        record, decision = build.authoring_pair(
            args.unknown, args.decision, task=args.task, why=args.why, summary=args.summary,
            statement=args.statement, affects=args.affects, evidence_refs=args.evidence,
            surface=args.surface, options=args.option)
        return {"unknowns": [record], "decisions": [decision], "cells": address_cells(args.decision, args.address)}
    rec = build.recommendation(args.recommend, args.reason, args.tradeoff) if args.recommend else None
    record = build.unknown(args.unknown, question=args.question, why=args.why, category=args.category,
                           options=args.option, affects=args.affects, evidence_refs=args.evidence,
                           surface=args.surface, rec=rec, mat=args.materiality)
    if args.kind == "question":
        return {"unknowns": [record]}
    decision = build.user_decision(record, args.decision, statement=args.statement, summary=args.summary,
                                   decision_type=args.decision_type, accepted=args.accepted)
    if args.decision_affects:
        decision["affects"] = sorted(set(args.decision_affects))
    return {"unknowns": [record], "decisions": [decision], "cells": address_cells(args.decision, args.address)}


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    path = Path(args.patch)
    try:
        patch = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"written": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    try:
        built = build_records(args)
    except ValueError as exc:
        print(json.dumps({"written": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    cells = built.pop("cells", [])
    existing = {record.get("id") for record in patch.get("evidence", [])}
    existing |= {record.get("id") for group in patch.get("objects", {}).values() for record in group}
    new_ids = [record["id"] for records in built.values() for record in records]
    duplicates = sorted(set(new_ids) & existing)
    if duplicates:
        print(json.dumps({"written": False, "error": f"IDs already in the patch: {duplicates}"}, ensure_ascii=False))
        return 1
    for group, records in built.items():
        target = patch.setdefault("evidence", []) if group == "evidence" else patch.setdefault("objects", {}).setdefault(group, [])
        target.extend(records)
    if cells:
        patch.setdefault("cells", []).extend(cells)
    path.write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"written": True, "patch": str(path), "added": new_ids,
                      "cells": [edit["cell"] for edit in cells]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
