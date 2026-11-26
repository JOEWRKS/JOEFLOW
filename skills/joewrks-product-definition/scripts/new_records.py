#!/usr/bin/env python3
"""Append complete evidence, unknown, decision and surface records to a revision patch file.

Each subcommand takes only the fields an author decides and fills the rest of
the V2 record shape. Apply the patch with open_revision.py, which validates it.

Subcommands that create records: evidence, question, user-decision, authoring,
relayed, baseline. Subcommands that read the current state (--state STATE_JSON; the
patch already written is laid over it, so several commands build one revision):

  resolve UNK --option OPT --words "..." [--also UNK=OPT ...]
                           close an existing OPEN question; the resolution mode is
                           derived (decision_policy.py), answered IDs leave every
                           blocks_unknown_refs list, the surfaces get the decision
                           and the OPEN coverage cells it held are answered
  resolve --accept-recommended --pack GRILL-…-1 [--surface SURF] --words "..."
                           the same for every OPEN question of a pack, each with its
                           recommended option (one decision per question)
  requirement --from-decisions DEC-a,DEC-b --surface SURF --requirement REQ
                           a requirement drafted from the decisions; the surface
                           becomes IN_SCOPE with it as authority
  topology-on DEC [--new-surface SURF --name ... | --target SURF]
                           a domain ON: profile ACTIVE, forced-kind surface, the pack's
                           coverage row (version and digest) and one OPEN question
                           skeleton per axis
  topology-off DEC --rationale "..."
                           a domain N/A with the decision as basis
  edit ID --set POINTER TEXT | --set-json POINTER JSON | --replace-text OLD NEW
                           change fields of an existing record

Rules checked here, before the patch is written:
  * option IDs, statements and consequences may not be a reserved non-answer
    word (none, false, n/a, na, later, tbd; any case), e.g. use NO_HINT, not NONE;
  * --recommend needs at least one --reason (EVD/REQ/RULE/FLOW/DATA/INT ID) and
    one --tradeoff, and must name one of the --option IDs;
  * a question's decision_authority is the validator's own derivation, and a
    resolution the derivation does not allow is refused with the reason (for
    example --accepted on a question that derives USER_DECISION_REQUIRED);
  * a materiality claim (5th value MATERIAL or NON_MATERIAL) must match the
    derived classification, and risk flags must be known names.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import record_builders as build
import state_builders
from cli_output import use_utf8_stdio
from decision_policy import CLASSIFICATIONS, PolicyError, evidence_index
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
            "materiality must be DIVERGENCE,FAN_OUT,true|false,REVERSIBILITY[,RISK_FLAG...][,MATERIAL|NON_MATERIAL]; "
            f"risk flags: {', '.join(build.RISK_FLAGS)}"
        )
    extra = parts[4:]
    claimed = [item for item in extra if item in CLASSIFICATIONS]
    flags = tuple(item for item in extra if item not in CLASSIFICATIONS)
    try:
        return build.materiality(parts[0], parts[1], parts[2] == "true", parts[3], flags,
                                 claimed=claimed[-1] if claimed else None)
    except PolicyError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


def _common_question(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--unknown", required=True, help="new UNK ID")
    parser.add_argument("--question", required=True)
    parser.add_argument("--why", required=True, help="why_it_matters")
    parser.add_argument("--category", default="CORE_FLOW",
                        choices=["CORE_FLOW", "SCOPE_BOUNDARY", "STATE_RECOVERY", "SECONDARY_BEHAVIOR", "PREFERENCE", "COSMETIC"])
    parser.add_argument("--option", action="append", type=_option, required=True, help="ID=statement|consequence (repeat)")
    parser.add_argument("--affects", action="append", required=True, help="affected ID (repeat)")
    parser.add_argument("--evidence", action="append", default=[],
                        help="EVD ID of a fact that frames the question (repeat; optional). The user's intent goes "
                             "in --reason: intent here answers an INTENT question and it is never asked")
    parser.add_argument("--surface", help="SURF ID the question came from (origin PRODUCT_SURFACE), or the pack target with --pack --axis")
    parser.add_argument("--pack", help="GRILL-…-1: with --axis, origin GRILL_PACK_AXIS (needs --surface, the pack target); "
                                       "without --axis, origin GRILL_TOPOLOGY (the domain's classification question)")
    parser.add_argument("--axis", help="pack axis ID, e.g. currency (needs --pack)")
    parser.add_argument("--materiality", type=_materiality,
                        help="DIVERGENCE,FAN_OUT,true|false,REVERSIBILITY[,RISK_FLAG...][,MATERIAL|NON_MATERIAL]; "
                             "default HIGH,MULTI_FLOW,true,REVERSIBLE; the classification is derived")
    parser.add_argument("--recommend", help="recommended option ID; needs --reason and --tradeoff")
    parser.add_argument("--confidence", default="HIGH", choices=["LOW", "MEDIUM", "HIGH"], help="recommendation confidence")
    parser.add_argument("--reason", action="append", default=[],
                        help="reasoning_refs for the recommendation; required (at least one) with --recommend (repeat)")
    parser.add_argument("--tradeoff", action="append", default=[],
                        help="tradeoff shown with the recommendation; required (at least one) with --recommend (repeat)")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--patch", required=True, help="patch JSON file to create or append to")
    parser.add_argument("--state", help="canonical state.json: needed by resolve, requirement, topology-on/-off and edit; "
                                        "with question/user-decision it lets the builder check evidence and IDs")
    parser.add_argument("--replace", action="store_true",
                        help="replace records with the same ID already in this patch, and with question an OPEN unknown of the "
                             "state (rewrite a topology-on skeleton question before it is asked)")
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

    decided = sub.add_parser("user-decision", help="a new question answered in the same revision: RESOLVED unknown plus CURRENT decision")
    _common_question(decided)
    decided.add_argument("--decision", required=True, help="new DEC ID")
    decided.add_argument("--statement", required=True, help="decision statement")
    decided.add_argument("--summary", required=True, help="resolution_summary, quoting the user")
    decided.add_argument("--decision-type", default="PRODUCT_BEHAVIOR")
    decided.add_argument("--accepted", action="store_true",
                         help="the user accepted the recommendation; requires --recommend, --reason and --tradeoff, and is "
                              "refused when the question derives USER_DECISION_REQUIRED (high risk or not HIGH confidence)")
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

    resolve = sub.add_parser("resolve", help="close existing OPEN questions from the user's answer (needs --state)")
    resolve.add_argument("unknown", nargs="?", help="the OPEN UNK the user answered")
    resolve.add_argument("--option", help="the option the user chose")
    resolve.add_argument("--words", help="the user's own words; the summary quotes them")
    resolve.add_argument("--summary", help="the resolution_summary verbatim instead of the one composed from --words")
    resolve.add_argument("--statement", help="decision statement (default: the chosen option's statement)")
    resolve.add_argument("--decision", help="new DEC ID (default: the next free DEC number)")
    resolve.add_argument("--decision-type", default="PRODUCT_BEHAVIOR")
    resolve.add_argument("--decision-affects", action="append", help="decision affects when wider than the question's (repeat)")
    mode = resolve.add_mutually_exclusive_group()
    mode.add_argument("--accepted", action="store_true",
                      help="insist on USER_ACCEPTED_RECOMMENDATION (refused when the derivation does not allow it)")
    mode.add_argument("--user-decision", action="store_true",
                      help="record USER_DECISION even when the chosen option is the recommended one")
    resolve.add_argument("--also", action="append", default=[], metavar="UNK=OPT",
                         help="another OPEN question the same answer decides (its own USER_DECISION, repeat)")
    resolve.add_argument("--accept-recommended", action="store_true",
                         help="resolve every OPEN question of --pack/--surface with its recommended option")
    resolve.add_argument("--pack", help="with --accept-recommended: the pack whose OPEN questions are answered")
    resolve.add_argument("--surface", help="with --accept-recommended: only questions of this surface")
    resolve.add_argument("--first-decision", help="with --accept-recommended: first DEC ID, numbered upward")

    requirement = sub.add_parser("requirement", help="a requirement drafted from decisions; the surface becomes IN_SCOPE (needs --state)")
    requirement.add_argument("--from-decisions", required=True, help="DEC-a,DEC-b,...")
    requirement.add_argument("--surface", required=True, help="the surface whose questions are all answered")
    requirement.add_argument("--requirement", required=True, help="new REQ ID")
    requirement.add_argument("--statement", help="statement instead of the draft joined from the decisions")
    requirement.add_argument("--scope", help="scope (default: the surface name)")
    requirement.add_argument("--ui-required", choices=["true", "false"], default="true")

    for name, helptext in (("topology-on", "turn a topology domain ON from its decision (needs --state)"),
                           ("topology-off", "mark a topology domain N/A from its decision (needs --state)")):
        topo = sub.add_parser(name, help=helptext)
        topo.add_argument("basis", help="the CURRENT decision that answered the domain's topology question (or evidence with --domain)")
        topo.add_argument("--domain", help="AUTH, MONEY, FILE_UPLOAD, ASYNC, PERMISSION or DESTRUCTIVE_ACTION (default: from the decision)")
        if name == "topology-on":
            topo.add_argument("--target", action="append", default=[], help="existing surface the pack covers (repeat)")
            topo.add_argument("--new-surface", help="new SURF ID for the domain's surface (forced kind for MONEY, ASYNC, PERMISSION, DESTRUCTIVE_ACTION)")
            topo.add_argument("--name", help="name of the new surface")
            topo.add_argument("--kind", dest="surface_kind", help="kind of the new surface when the domain forces none (default FEATURE_AREA)")
            topo.add_argument("--intent-classification", default=None, help="for EXISTING_PRODUCT_RECONCILIATION projects")
            topo.add_argument("--first-unknown", help="first UNK ID of the axis questions, numbered upward (default: next free)")
        else:
            topo.add_argument("--rationale", required=True, help="why the domain does not apply")

    edit = sub.add_parser("edit", help="change fields of an existing record (needs --state)")
    edit.add_argument("record", help="the record ID")
    edit.add_argument("--set", nargs=2, action="append", default=[], metavar=("POINTER", "TEXT"), help="e.g. --set /statement \"...\"")
    edit.add_argument("--set-json", nargs=2, action="append", default=[], metavar=("POINTER", "JSON"), help="e.g. --set-json /paths '[...]'")
    edit.add_argument("--replace-text", nargs=2, action="append", default=[], metavar=("OLD", "NEW"),
                      help="replace text that occurs exactly once in the record's strings (repeat)")
    return parser


STATE_KINDS = {"resolve", "requirement", "topology-on", "topology-off", "edit"}


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


def _origin(args: argparse.Namespace) -> dict[str, object]:
    if args.axis and not args.pack:
        raise ValueError("--axis needs --pack")
    if args.pack and args.axis and not args.surface:
        raise ValueError("--pack --axis needs --surface: the pack target surface (origin GRILL_PACK_AXIS)")
    if args.pack and not args.axis and args.surface:
        raise ValueError("a topology question (--pack without --axis) has no surface: drop --surface")
    return {"pack": args.pack, "axis": args.axis}


def build_records(args: argparse.Namespace, index: dict[str, dict[str, object]] | None = None) -> dict[str, object]:
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
    origin = _origin(args)
    rec = build.recommendation(args.recommend, args.reason, args.tradeoff, args.confidence) if args.recommend else None
    record = build.unknown(args.unknown, question=args.question, why=args.why, category=args.category,
                           options=args.option, affects=args.affects, evidence_refs=args.evidence,
                           surface=args.surface, rec=rec, mat=args.materiality, index=index, **origin)
    if args.kind == "question":
        return {"unknowns": [record]}
    decision = build.user_decision(record, args.decision, statement=args.statement, summary=args.summary,
                                   decision_type=args.decision_type, accepted=args.accepted, index=index)
    if args.decision_affects:
        decision["affects"] = sorted(set(args.decision_affects))
    return {"unknowns": [record], "decisions": [decision], "cells": address_cells(args.decision, args.address)}


def _state_records(args: argparse.Namespace, state: dict[str, object], patch: dict[str, object]) -> dict[str, object]:
    view = state_builders.View(state, patch)
    change = state_builders.Change(view)
    handler = {"resolve": state_builders.resolve, "requirement": state_builders.requirement_from_decisions,
               "topology-on": state_builders.topology_on, "topology-off": state_builders.topology_off,
               "edit": state_builders.edit}[args.kind]
    try:
        handler(change, args)
    except (KeyError, IndexError, TypeError) as exc:
        raise PolicyError(f"{args.kind}: {type(exc).__name__} {exc}") from None
    parts = change.as_patch_parts()
    if args.kind == "resolve":
        parts["left_without_question"] = state_builders.surfaces_left_without_question(change)
    parts["notes"], parts["derived"], parts["next_steps"] = change.notes, change.derived, change.next_steps
    return parts


def _merge(patch: dict[str, object], group: str, record: dict[str, object], *, new: bool, replace: bool) -> str:
    target = (patch.setdefault("evidence", []) if group == "evidence" else patch.setdefault("surfaces", [])
              if group == "surfaces" else patch.setdefault("objects", {}).setdefault(group, []))
    for position, existing in enumerate(target):
        if existing.get("id") == record["id"]:
            if new and not replace:
                raise PolicyError(f"IDs already in the patch: ['{record['id']}'] (pass --replace to rewrite it)")
            target[position] = record
            return "replaced"
    target.append(record)
    return "added" if new else "changed"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    path = Path(args.patch)
    try:
        patch = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        state = json.loads(Path(args.state).read_text(encoding="utf-8")) if args.state else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"written": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    if args.kind in STATE_KINDS and state is None:
        print(json.dumps({"written": False, "error": f"{args.kind} reads the existing records: pass --state STATE_JSON"}, ensure_ascii=False))
        return 2
    report: dict[str, object] = {}
    try:
        if args.kind in STATE_KINDS:
            parts = _state_records(args, state, patch)
            outcome: dict[str, list[str]] = {"added": [], "changed": [], "replaced": []}
            for record_id, (group, record) in parts["records"].items():
                outcome[_merge(patch, group, record, new=record_id in parts["new_ids"], replace=args.replace)].append(record_id)
            cells = []
            for address, spec in parts["cells"].items():
                patch["cells"] = [edit for edit in patch.get("cells", []) if edit.get("cell") != address]
                patch["cells"].append({"cell": address, "replace": spec})
                cells.append(address)
            if parts["rows"] is not None:
                patch["rows"] = parts["rows"]
            if parts["new_rows"]:
                patch.setdefault("rows", []).extend(parts["new_rows"])
            if parts["profile"]:
                patch.setdefault("grill_profile", {}).update(parts["profile"])
            report = {**outcome, "cells": cells,
                      "rows": [f"{t}[{r.get('target_ref') or r.get('feature_id') or r.get('screen_id')}]"
                               for spec in parts["new_rows"] for t, r in spec.items()],
                      "grill_profile": sorted(parts["profile"]), "derived": parts["derived"], "notes": parts["notes"]}
            if parts.get("left_without_question"):
                report["surfaces_left_without_open_question"] = parts["left_without_question"]
            if parts["next_steps"]:
                report["next_steps"] = parts["next_steps"]
        else:
            index = evidence_index(state) if state is not None else None
            built = build_records(args, index)
            cells = built.pop("cells", [])
            rows = built.pop("rows", [])
            surfaces = built.pop("surfaces", [])
            existing = {record.get("id") for record in patch.get("evidence", []) + patch.get("surfaces", [])}
            existing |= {record.get("id") for group in patch.get("objects", {}).values() for record in group}
            new_ids = [record["id"] for records in built.values() for record in records] + [record["id"] for record in surfaces]
            duplicates = sorted(set(new_ids) & existing)
            if duplicates and not args.replace:
                raise PolicyError(f"IDs already in the patch: {duplicates} (pass --replace to rewrite them)")
            if state is not None:
                state_index = state_builders.View(state, {}).index
                rewritable = {rid for rid in new_ids if args.replace and args.kind == "question" and rid in state_index
                              and state_index[rid][0] == "unknowns" and state_index[rid][1].get("status") == "OPEN"}
                in_state = sorted((set(new_ids) & set(state_index)) - rewritable)
                if in_state:
                    raise PolicyError(f"IDs already in the state: {in_state}; stable IDs are never reused "
                                      "(to close an existing question use resolve, to change a record use edit)")
            for group, records in built.items():
                for record in records:
                    _merge(patch, group, record, new=True, replace=args.replace)
            for record in surfaces:
                _merge(patch, "surfaces", record, new=True, replace=args.replace)
            if cells:
                patch.setdefault("cells", []).extend(cells)
            if rows:
                patch.setdefault("rows", []).extend(rows)
            report = {"added": new_ids, "cells": [edit["cell"] for edit in cells],
                      "rows": [f"{table}[{row.get('feature_id') or row.get('screen_id')}]" for spec in rows for table, row in spec.items()]}
            for records in built.values():
                for record in records:
                    if record["id"].startswith("UNK-"):
                        report.setdefault("decision_authority", {})[record["id"]] = record["decision_authority"]
                        if record["status"] == "OPEN" and record["decision_authority"] in {"EVIDENCE_RESOLVABLE", "AGENT_AUTONOMOUS",
                                                                                         "EXTERNAL_AUTHORITY_REQUIRED"}:
                            report.setdefault("notices", []).append(
                                f"{record['id']} derives {record['decision_authority']}: next_product_question.py will not ask it "
                                "(evidence answers it, it is non-material, or it needs external authority)")
            if state is None and args.kind in {"question", "user-decision"} and args.evidence:
                report["notice"] = ("no --state: the builder could not check whether --evidence answers the question "
                                    "(EVIDENCE_RESOLVABLE); open_revision.py will")
    except (ValueError, argparse.ArgumentTypeError) as exc:
        print(json.dumps({"written": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    path.write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"written": True, "patch": str(path), **report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
