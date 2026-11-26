#!/usr/bin/env python3
"""Record builders that read the current state, with the patch being written laid over it.

Each builder copies the existing records it changes, applies one author decision and
returns complete records, cell edits and profile cells for new_records.py to merge into
the patch. open_revision.py then validates and applies the patch as one revision.

  resolve            close existing OPEN questions from the user's answer (bundle A)
  requirement        draft a requirement from decisions and move the surface IN_SCOPE (D)
  topology-on/-off   turn a topology domain ON or OFF from its decision (B)
  edit               change one field of an existing record (FREEZE and re-entry text edits)
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any

import record_builders as build
from decision_policy import PolicyError, evidence_index, explain_authority, open_authority, user_resolution
from grill_v2 import (
    DOMAIN_PACK_IDS,
    FORCED_SURFACE_KIND_DOMAINS,
    GRILL_PROFILE_DOMAINS,
    PACK_AXIS_ORDER,
    canonical_pack_digest,
    load_grill_packs,
)


PACK_DOMAINS = {pack_id: domain for domain, pack_id in DOMAIN_PACK_IDS.items()}
DOMAIN_FORCED_KIND = {domain: kind for kind, domain in FORCED_SURFACE_KIND_DOMAINS.items()}
DOMAIN_RISK_FLAG = {"MONEY": ("money",), "AUTH": ("security",), "PERMISSION": ("security",),
                    "DESTRUCTIVE_ACTION": ("destructive",), "FILE_UPLOAD": (), "ASYNC": ()}
_ID = re.compile(r"^([A-Z]+)-(\d+)$")


def _upsert(records: list[dict[str, Any]], record: dict[str, Any]) -> None:
    for position, existing in enumerate(records):
        if existing.get("id") == record.get("id"):
            records[position] = record
            return
    records.append(record)


class View:
    """The state with the patch's records and profile cells laid over it (patch wins)."""

    def __init__(self, state: dict[str, Any], patch: dict[str, Any]) -> None:
        self.state = copy.deepcopy(state)
        self.patch = patch
        for record in patch.get("evidence", []):
            _upsert(self.state.setdefault("evidence", []), copy.deepcopy(record))
        for group, records in patch.get("objects", {}).items():
            for record in records:
                _upsert(self.state["objects"].setdefault(group, []), copy.deepcopy(record))
        for record in patch.get("surfaces", []):
            _upsert(self.state["surface_manifest"]["records"], copy.deepcopy(record))
        for domain, cell in patch.get("grill_profile", {}).items():
            self.state["surface_manifest"].setdefault("grill_profile", {})[domain] = copy.deepcopy(cell)
        self.reserved: set[str] = set()
        self._reindex()

    def _reindex(self) -> None:
        self.index: dict[str, tuple[str, dict[str, Any]]] = {}
        for record in self.state.get("evidence", []):
            self.index[record["id"]] = ("evidence", record)
        for group, records in self.state["objects"].items():
            for record in records:
                self.index[record["id"]] = (group, record)
        for record in self.state["surface_manifest"]["records"]:
            self.index[record["id"]] = ("surfaces", record)
        self.evidence = evidence_index(self.state)

    def apply(self, group: str, record: dict[str, Any]) -> None:
        target = (self.state["evidence"] if group == "evidence" else self.state["surface_manifest"]["records"]
                  if group == "surfaces" else self.state["objects"].setdefault(group, []))
        _upsert(target, copy.deepcopy(record))
        self._reindex()

    def get(self, record_id: str, group: str | None = None) -> dict[str, Any]:
        entry = self.index.get(record_id)
        if entry is None or (group is not None and entry[0] != group):
            kind = f" {group}" if group else ""
            raise PolicyError(f"{record_id} is not a{kind} record in the state or the patch")
        return copy.deepcopy(entry[1])

    def group_of(self, record_id: str) -> str:
        if record_id not in self.index:
            raise PolicyError(f"{record_id} is not in the state or the patch")
        return self.index[record_id][0]

    def unknowns(self) -> list[dict[str, Any]]:
        return self.state["objects"].get("unknowns", [])

    def surfaces(self) -> list[dict[str, Any]]:
        return self.state["surface_manifest"]["records"]

    def next_id(self, prefix: str) -> str:
        numbers, width = [], 3
        for record_id in list(self.index) + list(self.reserved):
            match = _ID.match(record_id)
            if match and match.group(1) == prefix:
                numbers.append(int(match.group(2)))
                width = max(width, len(match.group(2)))
        # IDs from the template's 900 range are placeholders, not the project's own sequence
        ordinary = [n for n in numbers if n < 900] or [0]
        record_id = f"{prefix}-{max(ordinary) + 1:0{width}d}"
        self.reserved.add(record_id)
        return record_id

    def new_id(self, record_id: str) -> str:
        if record_id in self.index or record_id in self.reserved:
            raise PolicyError(f"{record_id} already exists; stable IDs are never reused")
        self.reserved.add(record_id)
        return record_id


class Change:
    """Complete records, cell specs, profile cells and notes one builder run produces."""

    def __init__(self, view: View) -> None:
        self.view = view
        self.records: dict[str, tuple[str, dict[str, Any]]] = {}
        self.new_ids: list[str] = []
        self.cells: dict[str, dict[str, Any]] = {}
        self.rows: list[dict[str, Any]] = copy.deepcopy(view.patch.get("rows", []))
        self.rows_changed = False
        self.new_rows: list[dict[str, Any]] = []
        self.profile: dict[str, dict[str, Any]] = {}
        self.notes: list[str] = []
        self.derived: list[dict[str, Any]] = []
        self.next_steps: list[str] = []

    def put(self, group: str, record: dict[str, Any], *, new: bool = False) -> None:
        self.records[record["id"]] = (group, copy.deepcopy(record))
        if new and record["id"] not in self.new_ids:
            self.new_ids.append(record["id"])
        self.view.apply(group, record)

    def as_patch_parts(self) -> dict[str, Any]:
        def final(spec: dict[str, Any]) -> dict[str, Any]:
            # an OPEN cell carries no bindings; they are written once its last question is answered
            return {"status": "OPEN", "unknown_refs": spec["unknown_refs"]} if spec.get("status") == "OPEN" else spec

        for spec in self.rows + self.new_rows:
            table, row = next(iter(spec.items()))
            for cells in [row.get("axes", {}), row.get("cells", {}), row.get("states", {})] + [a.get("cells", {}) for a in row.get("actions", [])]:
                for axis, cell in cells.items():
                    if isinstance(cell, dict) and "bind" in cell and cell.get("status") == "OPEN":
                        cells[axis] = final(cell)
        return {"records": self.records, "new_ids": self.new_ids,
                "cells": {address: final(spec) for address, spec in self.cells.items()},
                "rows": self.rows if self.rows_changed else None, "new_rows": self.new_rows, "profile": self.profile}


# ---------------------------------------------------------------- coverage cells holding an unknown

def _state_cells(state: dict[str, Any]):
    """(address, cell) for every coverage cell, in the address form open_revision.py accepts."""
    packs: dict[str, int] = {}
    for row in state.get("grill_coverage", []):
        packs[row.get("pack_id")] = packs.get(row.get("pack_id"), 0) + 1
    for row in state.get("coverage", []):
        for axis, cell in (row.get("cells") or {}).items():
            yield f"coverage[{row.get('feature_id')}].cells.{axis}", cell
    for row in state.get("grill_coverage", []):
        key = row.get("pack_id") if packs[row.get("pack_id")] == 1 else f"{row.get('pack_id')}/{row.get('target_ref')}"
        for axis, cell in (row.get("axes") or {}).items():
            yield f"grill_coverage[{key}].axes.{axis}", cell
    for row in state.get("ux_coverage", []):
        for axis, cell in (row.get("states") or {}).items():
            yield f"ux_coverage[{row.get('screen_id')}].states.{axis}", cell
        for action in row.get("actions") or []:
            for axis, cell in (action.get("cells") or {}).items():
                yield f"ux_coverage[{row.get('screen_id')}].actions[{action.get('key')}].cells.{axis}", cell


def _existing_patch_cell(patch: dict[str, Any], address: str) -> dict[str, Any] | None:
    for edit in reversed(patch.get("cells", [])):
        if edit.get("cell") == address and "replace" in edit:
            return copy.deepcopy(edit["replace"])
    return None


def _close_cells(change: Change, unknown_id: str, decision_id: str) -> list[str]:
    """Close (or narrow) every OPEN cell that held `unknown_id`: the decision answers it."""
    touched = []

    def narrowed(spec: dict[str, Any], positive: str) -> dict[str, Any]:
        remaining = [ref for ref in spec.get("unknown_refs", []) if ref != unknown_id]
        bound = [b for b in spec.get("bind", [])] + [{"record_id": decision_id, "pointer": "/statement"}]
        still_open = [ref for ref in remaining
                      if change.view.index.get(ref, ("", {}))[1].get("status") == "OPEN"]
        if still_open:
            return {"status": "OPEN", "unknown_refs": still_open, "bind": bound}  # bind kept until the last answer
        return {"status": positive, "bind": bound}

    for address, cell in _state_cells(change.view.state):
        current = change.cells.get(address) or _existing_patch_cell(change.view.patch, address)
        if current is None:
            if not isinstance(cell, dict) or cell.get("status") != "OPEN" or unknown_id not in (cell.get("unknown_refs") or []):
                continue
            current = {"status": "OPEN", "unknown_refs": list(cell["unknown_refs"])}
        elif current.get("status") != "OPEN" or unknown_id not in current.get("unknown_refs", []):
            continue
        spec = narrowed(current, "ADDRESSED" if address.startswith("grill_coverage[") else "COVERED")
        if spec["status"] == "OPEN":
            change.notes.append(f"{address} stays OPEN: {spec['unknown_refs']} still open")
        change.cells[address] = spec
        touched.append(address)
    for spec in change.rows:
        table, row = next(iter(spec.items()))
        groups = ([("axes", row.get("axes", {}))] if table == "grill_coverage" else [("cells", row.get("cells", {}))]
                  if table == "coverage" else [("states", row.get("states", {}))]
                  + [(f"actions[{a.get('key')}].cells", a.get("cells", {})) for a in row.get("actions", [])])
        owner = row.get("target_ref") or row.get("feature_id") or row.get("screen_id")
        for field, cells in groups:
            for axis, cell in cells.items():
                if isinstance(cell, dict) and cell.get("status") == "OPEN" and unknown_id in cell.get("unknown_refs", []):
                    new = narrowed(cell, "ADDRESSED" if table == "grill_coverage" else "COVERED")
                    cell.clear()
                    cell.update(new)
                    change.rows_changed = True
                    touched.append(f"rows:{table}[{owner}].{field}.{axis}")
    return touched


# ---------------------------------------------------------------- A: resolve

def _summary(words: str, option_id: str, recommended: str | None, derived_from: str | None) -> str:
    if derived_from:
        return f"사용자 답: \"{words}\" ({derived_from}) — 이 답으로 {option_id}가 정해진다."
    if recommended == option_id:
        return f"사용자 답: \"{words}\" — {option_id} 추천안 수락."
    return f"사용자 답: \"{words}\" — {option_id} 선택."


def resolve_one(change: Change, unknown_id: str, option_id: str, *, words: str | None, summary: str | None = None,
                statement: str | None = None, decision_id: str | None = None, accepted: bool | None = None,
                decision_affects: list[str] | None = None, decision_type: str = "PRODUCT_BEHAVIOR",
                derived_from: str | None = None) -> str:
    view = change.view
    unknown = view.get(unknown_id, "unknowns")
    if unknown.get("status") != "OPEN":
        raise PolicyError(f"{unknown_id} is {unknown.get('status')}, not OPEN; only an OPEN question can be resolved "
                          "(a changed answer supersedes the decision: supersede_records.py)")
    if not (words or summary):
        raise PolicyError(f"{unknown_id}: pass --words (the user's own words) or --summary; a user decision keeps the answer")
    mode, authority = user_resolution(unknown, option_id, view.evidence, accepted=False if derived_from else accepted)
    explained = explain_authority(unknown, view.evidence)
    option = next(item for item in unknown["options"] if item["id"] == option_id)
    recommendation = unknown.get("recommendation") or {}
    decision_id = view.new_id(decision_id) if decision_id else view.next_id("DEC")
    text = summary or _summary(words, option_id, recommendation.get("recommended_option"), derived_from)
    unknown.update({"status": "RESOLVED", "decision_authority": authority, "resolved_by": [decision_id],
                    "resolution_mode": mode, "resolution_summary": text})
    acceptance = None
    if mode == "USER_ACCEPTED_RECOMMENDATION":
        acceptance = {"recommended_option": recommendation["recommended_option"],
                      "alternatives_presented": [item["id"] for item in unknown["options"]],
                      "tradeoffs_presented": list(recommendation["tradeoffs"]), "accepted_by": "user", "accepted_at": None}
    decision = {"id": decision_id, "status": "CURRENT", "statement": statement or option["statement"],
                "decision_type": decision_type, "resolution_mode": mode, "decision_authority": authority,
                "source_unknown_refs": [unknown_id], "evidence_refs": list(unknown["evidence_refs"]),
                "materiality": copy.deepcopy(unknown["materiality"]),
                "affects": sorted(set(decision_affects)) if decision_affects else list(unknown["affects"]),
                "decided_by": "USER", "accepted_recommendation": acceptance}
    for reference in decision["affects"]:
        view.get(reference)
    change.put("unknowns", unknown)
    change.put("decisions", decision, new=True)
    change.derived.append({"unknown": unknown_id, "option": option_id, "decision": decision_id, "resolution_mode": mode,
                           "decision_authority": authority, "open_authority_was": explained["derived_authority"],
                           "why": explained["reason"]})
    # blocks_unknown_refs may name only OPEN unknowns: drop the answered one everywhere
    for other in list(view.unknowns()):
        if unknown_id in (other.get("blocks_unknown_refs") or []):
            cleaned = copy.deepcopy(other)
            cleaned["blocks_unknown_refs"] = [ref for ref in cleaned["blocks_unknown_refs"] if ref != unknown_id]
            change.put("unknowns", cleaned)
            change.notes.append(f"{other['id']}.blocks_unknown_refs: dropped {unknown_id} (no longer OPEN)")
    # the surfaces the answer belongs to now carry the decision
    origin_surface = (unknown.get("origin") or {}).get("surface_ref")
    for surface in list(view.surfaces()):
        if surface.get("status") in {"SUPERSEDED", "RETIRED"}:
            continue
        if surface["id"] in decision["affects"] or surface["id"] == origin_surface or unknown_id in (surface.get("unknown_refs") or []):
            if decision_id not in surface.get("decision_refs", []):
                extended = copy.deepcopy(surface)
                extended["decision_refs"] = list(extended.get("decision_refs", [])) + [decision_id]
                change.put("surfaces", extended)
    for address in _close_cells(change, unknown_id, decision_id):
        change.notes.append(f"{address}: answered by {decision_id}")
    return decision_id


def surfaces_left_without_question(change: Change) -> list[dict[str, Any]]:
    """OPEN material surfaces the run touched that no longer hold an OPEN question (bundle D)."""
    view, found = change.view, []
    for surface_id, (group, _) in change.records.items():
        if group != "surfaces":
            continue
        surface = view.get(surface_id, "surfaces")
        material = (surface.get("materiality") or {}).get("classification") == "MATERIAL"
        open_refs = [ref for ref in surface.get("unknown_refs", [])
                     if view.index.get(ref, ("", {}))[1].get("status") == "OPEN"]
        if surface.get("status") == "OPEN" and material and not open_refs:
            decisions = ",".join(surface.get("decision_refs", [])) or "DEC-..."
            found.append({"surface": surface_id, "decision_refs": surface.get("decision_refs", []),
                          "next": f"new_records.py --state STATE --patch PATCH requirement --from-decisions {decisions} "
                                  f"--surface {surface_id} --requirement {view.next_id('REQ')}",
                          "why": "an OPEN material surface needs an OPEN question (OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN); "
                                 "with every question answered, a requirement drafted from its decisions is its authority "
                                 "and the surface becomes IN_SCOPE"})
            view.reserved.discard(found[-1]["next"].rsplit(" ", 1)[-1])
    return found


def resolve(change: Change, args: Any) -> None:
    if args.accept_recommended:
        if args.unknown or args.option or args.also or args.decision or args.statement or args.summary:
            raise PolicyError("--accept-recommended resolves every OPEN question of --pack (and --surface) with its "
                              "recommended option; it takes --words and optionally --first-decision only")
        if not (args.pack or args.surface):
            raise PolicyError("--accept-recommended needs --pack GRILL-…-1 and/or --surface SURF-…")
        selected = [u for u in change.view.unknowns() if u.get("status") == "OPEN"
                    and (not args.pack or (u.get("origin") or {}).get("pack_id") == args.pack)
                    and (not args.surface or (u.get("origin") or {}).get("surface_ref") == args.surface
                         or u["id"] in (_surface_or_none(change.view, args.surface) or {}).get("unknown_refs", []))]
        if not selected:
            raise PolicyError(f"no OPEN question matches --pack {args.pack} --surface {args.surface}")
        order = {axis: i for i, axis in enumerate(PACK_AXIS_ORDER.get(args.pack, ()))} if args.pack else {}
        selected.sort(key=lambda u: (order.get((u.get("origin") or {}).get("axis_id"), -1), u["id"]))
        missing = [u["id"] for u in selected if not u.get("recommendation")]
        if missing:
            raise PolicyError(f"no recommendation to accept on {missing}; resolve those one by one with --option")
        next_number = args.first_decision
        for unknown in selected:
            decision_id = None
            if next_number:
                decision_id, next_number = next_number, _bump(next_number)
            resolve_one(change, unknown["id"], unknown["recommendation"]["recommended_option"], words=args.words,
                        decision_id=decision_id, decision_type=args.decision_type)
        return
    if not args.unknown or not args.option:
        raise PolicyError("resolve needs UNKNOWN and --option OPTION_ID (or --accept-recommended --pack …)")
    accepted = True if args.accepted else False if args.user_decision else None
    main = resolve_one(change, args.unknown, args.option, words=args.words, summary=args.summary, statement=args.statement,
                       decision_id=args.decision, accepted=accepted, decision_affects=args.decision_affects,
                       decision_type=args.decision_type)
    for pair in args.also:
        unknown_id, sep, option_id = pair.partition("=")
        if not sep:
            raise PolicyError(f"--also takes UNK-…=OPTION_ID; got {pair!r}")
        resolve_one(change, unknown_id.strip(), option_id.strip(), words=args.words or args.summary,
                    derived_from=f"{args.unknown}={args.option}, {main}", decision_type=args.decision_type)


def _surface_or_none(view: View, surface_id: str) -> dict[str, Any] | None:
    try:
        return view.get(surface_id, "surfaces")
    except PolicyError:
        return None


def _bump(record_id: str) -> str:
    match = _ID.match(record_id)
    if not match:
        raise PolicyError(f"{record_id!r} is not an ID like DEC-042")
    return f"{match.group(1)}-{int(match.group(2)) + 1:0{len(match.group(2))}d}"


# ---------------------------------------------------------------- D: requirement --from-decisions

def requirement_from_decisions(change: Change, args: Any) -> None:
    view = change.view
    decision_ids = [item.strip() for item in args.from_decisions.split(",") if item.strip()]
    decisions = [view.get(item, "decisions") for item in decision_ids]
    stale = [d["id"] for d in decisions if d.get("status") != "CURRENT"]
    if stale:
        raise PolicyError(f"decisions {stale} are not CURRENT; a requirement may only restate current decisions")
    surface = view.get(args.surface, "surfaces")
    open_refs = [ref for ref in surface.get("unknown_refs", []) if view.index.get(ref, ("", {}))[1].get("status") == "OPEN"]
    if open_refs:
        raise PolicyError(f"{args.surface} still holds OPEN questions {open_refs}; answer them first (or keep it OPEN)")
    requirement_id = view.new_id(args.requirement)
    if args.statement:
        statement = args.statement
    else:
        statement = " ".join(f"{d['statement'].rstrip().rstrip('.')}({d['id']})." for d in decisions)
    requirement = {"status": "CURRENT", "id": requirement_id, "statement": statement,
                   "scope": args.scope or surface["name"], "ui_required": args.ui_required == "true",
                   "materiality": copy.deepcopy(surface["materiality"])}
    change.put("requirements", requirement, new=True)
    surface["status"] = "IN_SCOPE"
    surface["authority_refs"] = list(surface.get("authority_refs", [])) + [requirement_id]
    surface["decision_refs"] = list(surface.get("decision_refs", [])) + [d for d in decision_ids if d not in surface.get("decision_refs", [])]
    change.put("surfaces", surface)
    change.notes.append(f"{args.surface}: IN_SCOPE with {requirement_id} as authority; the statement is a draft joined from "
                        f"{decision_ids} — edit it to read as one requirement (new_records.py edit {requirement_id} --set /statement ...)")
    change.next_steps.append(f"{requirement_id} is MATERIAL: FREEZE needs its Core coverage row (draft_freeze.py)")


# ---------------------------------------------------------------- B: topology on / off

def _topology_basis(view: View, reference: str, domain: str | None) -> tuple[str, dict[str, Any]]:
    record = view.get(reference)
    group = view.group_of(reference)
    if group == "decisions":
        if record.get("status") != "CURRENT":
            raise PolicyError(f"{reference} is not CURRENT")
        packs = {(view.get(ref, "unknowns").get("origin") or {}).get("pack_id") for ref in record.get("source_unknown_refs", [])
                 if view.group_of(ref) == "unknowns"}
        domains = {PACK_DOMAINS[p] for p in packs if p in PACK_DOMAINS}
        if domain is None:
            if len(domains) != 1:
                raise PolicyError(f"{reference} does not answer one topology question (origin GRILL_TOPOLOGY); pass --domain")
            domain = domains.pop()
    elif group == "evidence":
        if domain is None:
            raise PolicyError(f"{reference} is evidence: pass --domain {'|'.join(GRILL_PROFILE_DOMAINS)}")
    else:
        raise PolicyError(f"{reference} must be a CURRENT decision or evidence (the basis of the topology answer)")
    if domain not in GRILL_PROFILE_DOMAINS:
        raise PolicyError(f"--domain {domain!r} is not one of {list(GRILL_PROFILE_DOMAINS)}")
    return domain, record


def _resolve_topology_question(change: Change, domain: str, basis_id: str) -> None:
    """The domain's OPEN topology question must already be answered by the basis decision."""
    cell = change.view.state["surface_manifest"].get("grill_profile", {}).get(domain, {})
    still_open = [ref for ref in cell.get("unknown_refs", [])
                  if change.view.index.get(ref, ("", {}))[1].get("status") == "OPEN"]
    if still_open:
        raise PolicyError(f"{domain} topology question(s) {still_open} are still OPEN: resolve them first "
                          f"(new_records.py resolve {still_open[0]} --option … --words …), then pass that decision")


def topology_on(change: Change, args: Any) -> None:
    view = change.view
    domain, basis = _topology_basis(view, args.basis, args.domain)
    _resolve_topology_question(change, domain, args.basis)
    pack_id = DOMAIN_PACK_IDS[domain]
    forced_kind = DOMAIN_FORCED_KIND.get(domain)
    targets = list(args.target)
    current = [s for s in view.surfaces() if s.get("status") not in {"SUPERSEDED", "RETIRED"}]
    if forced_kind:
        for surface in current:
            if surface.get("kind") == forced_kind and surface["id"] not in targets:
                targets.append(surface["id"])
    for surface_id in targets:
        view.get(surface_id, "surfaces")
    if args.new_surface:
        if not args.name:
            raise PolicyError("--new-surface needs --name")
        kind = forced_kind or args.surface_kind
        if forced_kind and args.surface_kind not in (None, forced_kind):
            raise PolicyError(f"{domain} surfaces are kind {forced_kind}")
        surface_id = view.new_id(args.new_surface)
        surface = {"id": surface_id, "kind": kind or "FEATURE_AREA", "name": args.name, "status": "OPEN",
                   "materiality": build.materiality("HIGH", "MULTI_FLOW", True, "COSTLY_TO_REVERSE", DOMAIN_RISK_FLAG[domain]),
                   "evidence_refs": list(basis.get("evidence_refs", [])) if view.group_of(args.basis) == "decisions" else [args.basis],
                   "authority_refs": [], "unknown_refs": [], "decision_refs": [args.basis] if view.group_of(args.basis) == "decisions" else [],
                   "contradiction_refs": [], "rationale": None, "intent_classification": args.intent_classification}
        change.put("surfaces", surface, new=True)
        targets.append(surface_id)
    if not targets:
        need = (f"a {forced_kind} surface: pass --new-surface SURF-… --name …" if forced_kind
                else "the surface the pack covers: pass --target SURF-… (e.g. the account area) or --new-surface")
        raise PolicyError(f"{domain} ON needs {need}")
    pack = load_grill_packs()[pack_id]
    axes_by_id = {axis["id"]: axis for axis in pack["axes"]}
    flags = DOMAIN_RISK_FLAG[domain]
    next_unknown = args.first_unknown
    created: list[str] = []
    for target in sorted(targets):
        cells = {}
        axis_unknowns = []
        for axis_id in PACK_AXIS_ORDER[pack_id]:
            axis = axes_by_id[axis_id]
            if next_unknown:
                unknown_id, next_unknown = view.new_id(next_unknown), _bump(next_unknown)
            else:
                unknown_id = view.next_id("UNK")
            description = axis.get("description", axis_id).rstrip(".")
            record = build.unknown(
                unknown_id, question=f"{domain} · {axis_id}: {description} — 이 제품은 어떻게 하는가?",
                why=f"{pack_id} 축 {axis_id}는 독립 결정이다. 답이 FREEZE에서 이 축의 권위가 된다.",
                category="SECONDARY_BEHAVIOR",
                options=[build.option("OPT-SPECIFY", f"이 제품은 {axis_id} 동작을 정한다: {description}.",
                                      "후속 결정 문장이 동작을 정하고 축은 그 결정에 묶인다."),
                         build.option("OPT-NOT-APPLICABLE", f"이 제품에는 {axis_id} 동작이 없다.",
                                      "축은 이 답을 근거로 N/A가 된다.")],
                affects=[target], evidence_refs=[], surface=target, pack=pack_id, axis=axis_id,
                mat=build.materiality("MEDIUM", "MULTI_OBJECT", True, "REVERSIBLE", flags), index=view.evidence)
            change.put("unknowns", record, new=True)
            axis_unknowns.append(unknown_id)
            cells[axis_id] = {"status": "OPEN", "unknown_refs": [unknown_id]}
            created.append(unknown_id)
        row = {"grill_coverage": {"target_ref": target, "pack_id": pack_id, "pack_version": pack["version"],
                                  "pack_digest": canonical_pack_digest(pack), "axes": cells}}
        change.new_rows.append(row)
        surface = view.get(target, "surfaces")
        surface["unknown_refs"] = list(surface.get("unknown_refs", [])) + [u for u in axis_unknowns if u not in surface.get("unknown_refs", [])]
        if view.group_of(args.basis) == "decisions" and args.basis not in surface.get("decision_refs", []):
            surface["decision_refs"] = list(surface.get("decision_refs", [])) + [args.basis]
        if surface.get("status") == "IN_SCOPE":
            change.notes.append(f"{target} is IN_SCOPE; its new axis questions keep it answerable, but it stays IN_SCOPE")
        change.put("surfaces", surface)
    change.profile[domain] = {"status": "ACTIVE", "surface_refs": sorted(targets), "unknown_refs": [],
                              "basis_refs": [args.basis], "rationale": None}
    change.next_steps.append(f"{args.basis} is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core "
                             "boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority")
    change.notes.append(f"{len(created)} axis questions are skeletons (two generic options, no recommendation): rewrite each "
                        f"with new_records.py --replace question --unknown ID --pack {pack_id} --axis AXIS --surface TARGET "
                        "… before asking; next_product_question.py --grouped lists them as one table")


def topology_off(change: Change, args: Any) -> None:
    view = change.view
    domain, _ = _topology_basis(view, args.basis, args.domain)
    _resolve_topology_question(change, domain, args.basis)
    forced_kind = DOMAIN_FORCED_KIND.get(domain)
    forced = [s["id"] for s in view.surfaces() if forced_kind and s.get("kind") == forced_kind
              and s.get("status") not in {"SUPERSEDED", "RETIRED"}]
    if forced:
        raise PolicyError(f"{domain} cannot be N/A while {forced_kind} surfaces {forced} are current")
    if not args.rationale or not args.rationale.strip():
        raise PolicyError("topology-off needs --rationale: why the domain does not apply")
    change.profile[domain] = {"status": "N/A", "surface_refs": [], "unknown_refs": [], "basis_refs": [args.basis],
                              "rationale": args.rationale.strip()}
    change.next_steps.append(f"{args.basis} is a material decision with no coverage yet: at FREEZE bind it in a requirement's Core "
                             "boundary cell (DEC is allowed there), or READY_FOR_REVIEW reports orphan_material_authority")



# ---------------------------------------------------------------- edit

def _pointer(record: dict[str, Any], pointer: str) -> tuple[Any, str | int]:
    if not pointer.startswith("/") or pointer == "/":
        raise PolicyError(f"pointer {pointer!r} must look like /statement or /paths/3")
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]
    target: Any = record
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    last = parts[-1]
    if isinstance(target, list):
        last = int(last)
        if last >= len(target):
            raise PolicyError(f"{pointer}: index past the end of the list ({len(target)} items)")
    elif last not in target:
        raise PolicyError(f"{pointer}: field {last!r} does not exist (fields {sorted(target)})")
    return target, last


def _strings(value: Any, path: str = ""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            if key != "id":
                yield from _strings(item, f"{path}/{key}")
    elif isinstance(value, list):
        for position, item in enumerate(value):
            yield from _strings(item, f"{path}/{position}")


def edit(change: Change, args: Any) -> None:
    view = change.view
    group = view.group_of(args.record)
    record = view.get(args.record)
    changed = []
    for pointer, value in args.set:
        target, key = _pointer(record, pointer)
        target[key] = value
        changed.append(pointer)
    for pointer, raw in args.set_json:
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise PolicyError(f"--set-json {pointer}: {exc}") from None
        target, key = _pointer(record, pointer)
        target[key] = value
        changed.append(pointer)
    for old, new in args.replace_text:
        hits = [(path, text) for path, text in _strings(record) if old in text]
        count = sum(text.count(old) for _, text in hits)
        if count != 1:
            where = [path for path, _ in hits]
            raise PolicyError(f"--replace-text: {old!r} occurs {count} times in {args.record} {where}; "
                              "it must occur exactly once (quote more context, or use --set POINTER)")
        path = hits[0][0]
        target, key = _pointer(record, path)
        target[key] = target[key].replace(old, new)
        changed.append(path)
    if not changed:
        raise PolicyError("edit needs --set, --set-json or --replace-text")
    if isinstance(record.get("materiality"), dict):
        before = record["materiality"].get("classification")
        recomputed = build.classify_materiality(record["materiality"])
        if any(p.startswith("/materiality/classification") for p in changed) and before != recomputed:
            raise PolicyError(f"classification {before} contradicts the derivation ({recomputed}); "
                              "change the dimensions instead, the builder derives the classification")
        record["materiality"]["classification"] = recomputed
    if group == "unknowns" and record.get("status") == "OPEN":
        derived = open_authority(record, view.evidence)
        if derived != record.get("decision_authority"):
            change.notes.append(f"{args.record}.decision_authority: {record.get('decision_authority')} -> {derived} (derived)")
            record["decision_authority"] = derived
    change.put(group, record)
    change.notes.append(f"{args.record}: changed {changed}")
