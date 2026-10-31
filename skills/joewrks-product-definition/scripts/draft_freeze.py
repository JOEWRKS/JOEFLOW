#!/usr/bin/env python3
"""Draft the coverage rows FREEZE still needs, as a patch the author edits.

For every current material requirement, current screen and active specialist target
that has no coverage row yet, this writes the exact axis inventory and:
  * fills a cell only when the record graph decides it: a requirement's acceptance
    criteria, its users, goal plus itself, flows plus itself, a screen's default state;
  * marks every other cell DECIDE with up to five candidates (records bound on the same
    axis in sibling rows first, then records linked to the target) and a hint when
    siblings answered the axis with N/A. DECIDE is not a valid status, so the draft
    cannot be applied until the author settles those cells.
Sibling answers are not prefilled: on AI-Gomoku they were right only about half the
time, and a wrong binding still passes validation. UX axes inherited from an N/A grill
profile domain are left out. open_revision.py checks the edited patch like any other.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from authority_binding_v2 import canonical_record_index, load_binding_contracts
from cli_output import use_utf8_stdio
from grill_v2 import compile_active_grill_packs, load_grill_packs
from ux_profile_inheritance import inheritable_ux_axes


POINTERS = {
    "GOAL": "/statement", "USR": "/description", "REQ": "/statement", "DEC": "/statement",
    "RULE": "/statement", "FLOW": "/paths", "SCR": "/purpose", "STATE": "/conditions",
    "DATA": "/purpose", "INT": "/purpose", "AC": "/assertion", "SURF": "/rationale", "EVD": "/claim",
}
POSITIVE = {"coverage": "COVERED", "ux_coverage": "COVERED", "grill_coverage": "ADDRESSED"}


def _prefix(record_id: str) -> str:
    return record_id.split("-", 1)[0]


def _links(state: dict[str, Any]) -> dict[str, set[str]]:
    """Undirected reference graph between CURRENT records (any field naming another ID)."""
    index = canonical_record_index(state)
    current = {rid for rid, (_, record) in index.items() if record.get("status") == "CURRENT"}
    graph: dict[str, set[str]] = {rid: set() for rid in current}
    for rid in current:
        record = index[rid][1]
        for key, value in record.items():
            if key == "id":
                continue
            values = value if isinstance(value, list) else [value]
            for item in values:
                if isinstance(item, str) and item in current and item != rid:
                    graph[rid].add(item)
                    graph[item].add(rid)
    return graph


class Drafter:
    def __init__(self, state: dict[str, Any]) -> None:
        self.state = state
        self.contracts = load_binding_contracts()
        self.graph = _links(state)
        self.index = canonical_record_index(state)
        self.global_use = Counter(
            binding["record_id"] for _, _, cell in self._all_cells() for binding in cell.get("authority_bindings", []))

    def _all_cells(self):
        """(table, row key, cell) for every existing cell; row key groups siblings."""
        for row in self.state.get("coverage", []):
            for axis, cell in row.get("cells", {}).items():
                yield ("coverage", axis), row.get("feature_id"), cell
        for row in self.state.get("ux_coverage", []):
            for axis, cell in row.get("states", {}).items():
                yield ("ux_state", axis), row.get("screen_id"), cell
            for action in row.get("actions", []):
                for axis, cell in action.get("cells", {}).items():
                    yield ("ux_action", axis), row.get("screen_id"), cell
        for row in self.state.get("grill_coverage", []):
            for axis, cell in row.get("axes", {}).items():
                yield (f"grill:{row.get('pack_id')}", axis), row.get("target_ref"), cell

    def _siblings(self, kind: tuple[str, str], owner: str) -> tuple[list[dict], list[dict]]:
        same, other = [], []
        for cell_kind, cell_owner, cell in self._all_cells():
            if cell_kind == kind:
                (same if cell_owner == owner else other).append(cell)
        return same, other

    def _structural(self, kind: tuple[str, str], owner: str, allowed: set[str]) -> list[str]:
        """Axes whose answer follows from the record graph alone."""
        linked = self.graph.get(owner, set())
        of = lambda prefix: sorted(r for r in linked if _prefix(r) == prefix)  # noqa: E731
        table, axis = kind
        if table == "coverage":
            if axis == "acceptance":
                return sorted(rid for rid, (group, record) in self.index.items()
                              if group == "AC" and record.get("status") == "CURRENT"
                              and owner in (record.get("requirement_refs") or []))
            if axis == "actor":
                return of("USR")
            if axis in {"goal", "happy_path"}:
                return of("GOAL" if axis == "goal" else "FLOW") + [owner]
            if axis == "entry_point":
                return of("FLOW")
        if table == "ux_state" and axis == "default":
            return [owner] + of("FLOW")
        return []

    def _bind(self, records: list[str]) -> list[dict[str, str]]:
        return [{"record_id": rid, "pointer": POINTERS[_prefix(rid)]} for rid in records]

    def propose(self, table: str, kind: tuple[str, str], owner: str, allowed: set[str]) -> dict[str, Any]:
        structural = [r for r in self._structural(kind, owner, allowed) if _prefix(r) in allowed]
        if structural:
            return {"status": POSITIVE[table], "bind": self._bind(structural), "why": "follows from linked records"}
        # Anything else is the author's call. Sibling answers were right only about half the time
        # on AI-Gomoku and a wrong binding still validates, so they are shown, never prefilled.
        same, other = self._siblings(kind, owner)
        linked = self.graph.get(owner, set())
        hints: list[str] = []
        suggested: list[str] = []
        for scope, cells in (("this screen", same), ("other rows", other)):
            if not cells:
                continue
            statuses = Counter(cell.get("status") for cell in cells)
            if statuses["N/A"]:
                hints.append(f"{statuses['N/A']} of {len(cells)} cells on this axis in {scope} are N/A")
            used = Counter(b["record_id"] for cell in cells for b in cell.get("authority_bindings", []))
            suggested += [rid for rid, _ in used.most_common()
                          if _prefix(rid) in allowed and (scope == "this screen" or rid in linked) and rid not in suggested]
        shortlist = suggested + sorted((r for r in linked if _prefix(r) in allowed and _prefix(r) in POINTERS and r not in suggested),
                                       key=lambda rid: (-self.global_use[rid], rid))
        return {"status": "DECIDE", "candidates": shortlist[:5],
                "why": "; ".join(hints) or ("choose from linked records" if shortlist else "no linked record of an allowed type")}

    def missing_rows(self) -> list[dict[str, Any]]:
        objects = self.state["objects"]
        product, ux = self.contracts["product"], self.contracts["ux"]
        rows: list[dict[str, Any]] = []
        have_core = {row.get("feature_id") for row in self.state.get("coverage", [])}
        for req in objects.get("requirements", []):
            if req.get("status") == "CURRENT" and req.get("materiality", {}).get("classification") == "MATERIAL" and req["id"] not in have_core:
                cells = {axis: self.propose("coverage", ("coverage", axis), req["id"], set(types))
                         for axis, types in product["core_axis_types"].items()}
                rows.append({"coverage": {"feature_id": req["id"], "cells": cells}})
        have_ux = {row.get("screen_id") for row in self.state.get("ux_coverage", [])}
        skip_states, skip_actions = inheritable_ux_axes(self.state)
        for screen in objects.get("screens", []):
            if screen.get("status") != "CURRENT" or screen["id"] in have_ux:
                continue
            states = {axis: self.propose("ux_coverage", ("ux_state", axis), screen["id"], set(types))
                      for axis, types in ux["state_axis_types"].items() if axis not in skip_states}
            actions = [{"key": key, "cells": {axis: self.propose("ux_coverage", ("ux_action", axis), screen["id"], set(types))
                                              for axis, types in ux["action_axis_types"].items() if axis not in skip_actions}}
                       for key in screen.get("major_actions", [])]
            rows.append({"ux_coverage": {"screen_id": screen["id"], "states": states, "actions": actions}})
        packs = load_grill_packs()
        have_grill = {(row.get("pack_id"), row.get("target_ref")) for row in self.state.get("grill_coverage", [])}
        for instance in compile_active_grill_packs(self.state):
            if instance["pack_id"] == "GRILL-CORE-1":
                continue
            allowed = set(product["specialist_pack_types"][instance["pack_id"]])
            for target in instance["target_refs"]:
                if (instance["pack_id"], target) in have_grill:
                    continue
                axes = {axis["id"]: self.propose("grill_coverage", (f"grill:{instance['pack_id']}", axis["id"]), target, allowed)
                        for axis in packs[instance["pack_id"]]["axes"]}
                rows.append({"grill_coverage": {"target_ref": target, "pack_id": instance["pack_id"],
                                                "pack_version": instance["version"], "pack_digest": instance["digest"], "axes": axes}})
        return rows


def _cells_of(row_spec: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    table, row = next(iter(row_spec.items()))
    if table == "ux_coverage":
        cells = [(f"ux_coverage[{row['screen_id']}].states.{a}", c) for a, c in row["states"].items()]
        for action in row["actions"]:
            cells += [(f"ux_coverage[{row['screen_id']}].actions[{action['key']}].cells.{a}", c) for a, c in action["cells"].items()]
        return cells
    if table == "coverage":
        return [(f"coverage[{row['feature_id']}].cells.{a}", c) for a, c in row["cells"].items()]
    return [(f"grill_coverage[{row['pack_id']}/{row['target_ref']}].axes.{a}", c) for a, c in row["axes"].items()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--patch", help="write the draft rows into this patch file (created or extended)")
    args = parser.parse_args(argv)
    try:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        rows = Drafter(state).missing_rows()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    cells = [(address, cell) for row in rows for address, cell in _cells_of(row)]
    report = {
        "ok": True,
        "rows": [f"{table}[{row.get('feature_id') or row.get('screen_id') or row.get('pack_id') + '/' + row['target_ref']}]"
                 for spec in rows for table, row in spec.items()],
        "proposed": dict(Counter(cell["status"] for _, cell in cells)),
        "decide": [address for address, cell in cells if cell["status"] == "DECIDE"],
    }
    if args.patch:
        path = Path(args.patch)
        patch = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        patch.setdefault("rows", []).extend(rows)
        path.write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        report["patch"] = str(path)
    else:
        report["draft"] = rows
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
