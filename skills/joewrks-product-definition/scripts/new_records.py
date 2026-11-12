#!/usr/bin/env python3
"""Append complete evidence, unknown, and decision records to a revision patch file.

Each subcommand takes only the fields an author decides and fills the rest of
the V2 record shape. Apply the patch with open_revision.py, which validates it.

Rules checked here, before the patch is written:
  * option IDs, statements and consequences may not be a reserved non-answer
    word (none, false, n/a, na, later, tbd; any case), e.g. use NO_HINT, not NONE;
  * --recommend needs at least one --reason (EVD/REQ/RULE/FLOW/DATA/INT ID) and
    one --tradeoff, and must name one of the --option IDs;
  * user-decision --accepted needs --recommend (with its --reason and --tradeoff).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import record_builders as build
from cli_output import use_utf8_stdio
from grill_v2 import MEANINGLESS


def _reserved(label: str, value: str) -> None:
    if value.strip().lower() in MEANINGLESS:
        raise argparse.ArgumentTypeError(
            f"{label} {value!r} is a reserved non-answer word ({', '.join(sorted(MEANINGLESS))}); "
            "the validator rejects it, so rename it (e.g. NO_HINT, OFF, SKIP)"
        )


def _option(text: str) -> dict[str, object]:
    option_id, sep, rest = text.partition("=")
    if not sep or not option_id.strip():
        raise argparse.ArgumentTypeError(f"option must be ID=statement|consequence...; got {text!r}")
    statement, *consequences = rest.split("|")
    consequences = [item.strip() for item in consequences if item.strip()]
    if not statement.strip() or not consequences:
        raise argparse.ArgumentTypeError(f"option needs a statement and at least one consequence (ID=statement|consequence); got {text!r}")
    _reserved("option ID", option_id.strip())
    _reserved(f"option {option_id.strip()} statement", statement.strip())
    for item in consequences:
        _reserved(f"option {option_id.strip()} consequence", item)
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
    parser.add_argument("--recommend", help="recommended option ID; needs --reason and --tradeoff")
    parser.add_argument("--reason", action="append", default=[],
                        help="reasoning_refs for the recommendation; required (at least one) with --recommend (repeat)")
    parser.add_argument("--tradeoff", action="append", default=[],
                        help="tradeoff shown with the recommendation; required (at least one) with --recommend (repeat)")


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
    decided.add_argument("--accepted", action="store_true",
                         help="the user accepted the recommendation; requires --recommend, --reason and --tradeoff")
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

    relayed = sub.add_parser("relayed", help="a user instruction passed on by another session or person (RELAYED_USER_INTENT)")
    relayed.add_argument("--id", required=True)
    relayed.add_argument("--relayer", required=True, help="who passed it on, e.g. 'parent session (JOEFLOW 보강)'")
    relayed.add_argument("--when", help="when the user said it, if known")
    words = relayed.add_mutually_exclusive_group(required=True)
    words.add_argument("--quote", help="the user's exact words (confidence DIRECT: may close a material question)")
    words.add_argument("--summary", help="the relayer's own words (confidence INFERRED: prepares the question, cannot close it)")
    asked = relayed.add_mutually_exclusive_group()
    asked.add_argument("--asked", help="the exact question or message the user was answering, as it was shown to the user")
    asked.add_argument("--asked-summary",
                       help="the relayer's description of what the user was answering, when its exact words are not available")
    relayed.add_argument("--class", dest="classes", action="append", default=None, help="INTENT (default) or PREFERENCE (repeat)")

    baseline = sub.add_parser("baseline", help="existing behaviour a feature extension must keep (references/feature-extension.md)")
    baseline.add_argument("--requirement", required=True, help="new REQ ID for the preserved behaviour")
    baseline.add_argument("--rule", required=True, help="new RULE ID that lists the behaviours")
    baseline.add_argument("--acceptance", required=True, help="new AC ID")
    baseline.add_argument("--surface", required=True, help="new SURF ID (FEATURE_AREA, IN_SCOPE) that owns the requirement")
    baseline.add_argument("--goal", required=True, help="existing GOAL ID the preserved behaviour serves")
    baseline.add_argument("--evidence", action="append", required=True,
                          help="observed evidence of the behaviour: OBSERVED_IMPLEMENTATION, OBSERVED_RUNTIME or TEST_ASSERTION (repeat)")
    baseline.add_argument("--behavior", action="append", required=True, help="one behaviour that must not change (repeat)")
    baseline.add_argument("--check", required=True, help="the acceptance assertion, e.g. the existing checks that must still pass")
    baseline.add_argument("--name", default="기존 동작 유지", help="surface name and requirement scope")
    baseline.add_argument("--task", help="new TASK ID that implements the requirement (the Approval Manifest needs one)")
    return parser


def baseline_records(args: argparse.Namespace) -> dict[str, object]:
    """A preserved-behaviour requirement: records, its surface and a Core row answered by the rule."""
    behaviours = [item.strip() for item in args.behavior if item.strip()]
    if not behaviours:
        raise ValueError("at least one --behavior is required")
    listed = " ".join(f"({i}) {text}" for i, text in enumerate(behaviours, 1))
    rule = {"status": "CURRENT", "id": args.rule, "applies_to": [args.requirement],
            "statement": f"{args.name}: 이번 변경은 다음 기존 동작을 바꾸지 않는다. {listed}"}
    requirement = {"status": "CURRENT", "id": args.requirement,
                   "statement": f"{args.name}. 다음 기존 동작은 이번 변경 뒤에도 그대로다: {listed} 근거는 {', '.join(args.evidence)}.",
                   "scope": args.name, "ui_required": False,
                   "materiality": build.materiality("HIGH", "MULTI_FLOW", True, "REVERSIBLE")}
    acceptance = {"status": "CURRENT", "id": args.acceptance, "requirement_refs": [args.requirement], "assertion": args.check}
    surface = {"id": args.surface, "kind": "FEATURE_AREA", "name": args.name, "status": "IN_SCOPE",
               "materiality": build.materiality("HIGH", "MULTI_FLOW", True, "REVERSIBLE"),
               "evidence_refs": list(args.evidence), "authority_refs": [args.requirement], "unknown_refs": [],
               "decision_refs": [], "contradiction_refs": [],
               "rationale": "기존 제품의 관찰된 동작을 이번 변경의 회귀 금지 목록으로 둔다.", "intent_classification": None}
    bind = lambda record_id, pointer: {"record_id": record_id, "pointer": pointer}
    row = {"coverage": {"feature_id": args.requirement, "default_authority": [bind(args.rule, "/statement")], "cells": {
        "goal": {"status": "COVERED", "bind": [bind(args.goal, "/statement"), bind(args.requirement, "/statement")]},
        "happy_path": {"status": "COVERED", "bind": [bind(args.requirement, "/statement")]},
        "acceptance": {"status": "COVERED", "bind": [bind(args.acceptance, "/assertion")]},
    }}}
    built: dict[str, object] = {"requirements": [requirement], "rules": [rule], "acceptance_criteria": [acceptance],
                                "surfaces": [surface], "rows": [row]}
    if args.task:
        built["tasks"] = [{"status": "CURRENT", "id": args.task, "implements": [args.requirement], "acceptance_refs": [args.acceptance]}]
    return built


def address_cells(decision_id: str, cells: list[str]) -> list[dict[str, object]]:
    """Cell edits that close the OPEN cells a resolved unknown was holding open."""
    return [{
        "cell": cell,
        "replace": {"status": "ADDRESSED" if cell.startswith("grill_coverage[") else "COVERED",
                    "bind": [{"record_id": decision_id, "pointer": "/statement"}]},
    } for cell in cells]


def build_records(args: argparse.Namespace) -> dict[str, object]:
    if args.kind == "baseline":
        return baseline_records(args)
    if args.kind == "relayed":
        locator = f"relayed by {args.relayer}" + (f", said {args.when}" if args.when else "")
        asked, asked_summary = getattr(args, "asked", None), getattr(args, "asked_summary", None)
        if asked:
            context = f" — 답한 질문 원문: \"{asked}\""
        elif asked_summary:
            context = f" — 답한 질문(전달자 요약, 원문 없음): {asked_summary}"
        else:
            context = ""
        if args.quote:
            return {"evidence": [build.evidence(args.id, source_kind="RELAYED_USER_INTENT", authority_classes=args.classes or ["INTENT"],
                                                locator=locator, claim=f"사용자 원문: \"{args.quote}\"{context}", confidence="DIRECT")]}
        return {"evidence": [build.evidence(args.id, source_kind="RELAYED_USER_INTENT", authority_classes=args.classes or ["INTENT"],
                                            locator=locator, claim=f"전달자 요약: {args.summary}{context}", confidence="INFERRED")]}
    if args.kind == "evidence":
        return {"evidence": [build.evidence(args.id, source_kind=args.source_kind, authority_classes=args.classes,
                                            locator=args.locator, claim=args.claim, confidence=args.confidence)]}
    if args.kind == "authoring":
        record, decision = build.authoring_pair(
            args.unknown, args.decision, task=args.task, why=args.why, summary=args.summary,
            statement=args.statement, affects=args.affects, evidence_refs=args.evidence,
            surface=args.surface, options=args.option)
        return {"unknowns": [record], "decisions": [decision], "cells": address_cells(args.decision, args.address)}
    option_ids = [item["id"] for item in args.option]
    if args.recommend:
        missing = [flag for flag, values in (("--reason", args.reason), ("--tradeoff", args.tradeoff)) if not values]
        if missing:
            raise ValueError(f"--recommend {args.recommend} needs {' and '.join(missing)}: a recommendation must cite at least one "
                             "reasoning ref and show at least one tradeoff, or open_revision.py rejects it "
                             "('recommendation must match the canonical M3 structure')")
        if args.recommend not in option_ids:
            raise ValueError(f"--recommend {args.recommend!r} is not one of the --option IDs {option_ids}")
        for item in args.tradeoff:
            if item.strip().lower() in MEANINGLESS or not item.strip():
                raise ValueError(f"--tradeoff {item!r} is empty or a reserved non-answer word")
    if getattr(args, "accepted", False) and not args.recommend:
        raise ValueError("--accepted records that the user accepted a presented recommendation; "
                         "pass --recommend OPTION_ID with --reason and --tradeoff (what was shown), or drop --accepted")
    if len(set(option_ids)) != len(option_ids):
        raise ValueError(f"option IDs repeat: {option_ids}")
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
    rows = built.pop("rows", [])
    surfaces = built.pop("surfaces", [])
    existing = {record.get("id") for record in patch.get("evidence", []) + patch.get("surfaces", [])}
    existing |= {record.get("id") for group in patch.get("objects", {}).values() for record in group}
    new_ids = [record["id"] for records in built.values() for record in records] + [record["id"] for record in surfaces]
    duplicates = sorted(set(new_ids) & existing)
    if duplicates:
        print(json.dumps({"written": False, "error": f"IDs already in the patch: {duplicates}"}, ensure_ascii=False))
        return 1
    for group, records in built.items():
        target = patch.setdefault("evidence", []) if group == "evidence" else patch.setdefault("objects", {}).setdefault(group, [])
        target.extend(records)
    if cells:
        patch.setdefault("cells", []).extend(cells)
    if surfaces:
        patch.setdefault("surfaces", []).extend(surfaces)
    if rows:
        patch.setdefault("rows", []).extend(rows)
    path.write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"written": True, "patch": str(path), "added": new_ids,
                      "cells": [edit["cell"] for edit in cells],
                      "rows": [f"{table}[{row.get('feature_id') or row.get('screen_id')}]" for spec in rows for table, row in spec.items()]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
