#!/usr/bin/env python3
"""Show every error message and output 2.0.2 changed, before (2.0.1) and after (2.0.2).

Usage: python run_messages.py SKILL_DIR LABEL OUT_JSON [BIG_STATE_JSON]
Each scenario builds a small broken state from the skill's own examples, runs the CLI the
author would run, and keeps only the error or line in question.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL, LABEL, OUT = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
BIG = Path(sys.argv[4]).resolve() if len(sys.argv) > 4 else None
SCRIPTS = SKILL / "scripts"
EXAMPLES = SKILL / "templates" / "examples"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
TMP = Path(tempfile.mkdtemp())


def load(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def run(script, *args, state=None):
    path = TMP / "state.json"
    if state is not None:
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *[str(path) if a == "STATE" else str(a) for a in args]],
                            capture_output=True, stdin=subprocess.DEVNULL, env=ENV)
    return result.returncode, result.stdout.decode("utf-8"), result.stderr.decode("utf-8")


def errors_of(state, code=None, path_prefix=None):
    _, out, _ = run("explain_state_errors.py", "STATE", state=state)
    errors = json.loads(out)["errors"]
    return [{"code": e["code"], "path": e["path"], "message": e["message"]} for e in errors
            if (code is None or e["code"] == code) and (path_prefix is None or e["path"].startswith(path_prefix))]


def rehash(state):
    sys.path.insert(0, str(SCRIPTS))
    from revision_v2 import refresh_bindings  # noqa: E402
    from authority_binding_v2 import canonical_record_index  # noqa: E402
    refresh_bindings(state, set(canonical_record_index(state)))
    sys.path.pop(0)
    return state


results = {}

# G/D: an OPEN material surface whose last question was answered
state = load("discover-one-question.state.json")
question = state["objects"]["unknowns"][0]
question.update({"status": "RESOLVED", "decision_authority": "USER_DECISION_REQUIRED", "resolved_by": ["DEC-001"],
                 "resolution_mode": "USER_DECISION", "resolution_summary": 'User: "signed-in only"'})
state["objects"]["decisions"] = [{"id": "DEC-001", "status": "CURRENT", "statement": "Only signed-in customers can send feedback.",
                                  "decision_type": "PRODUCT_BEHAVIOR", "resolution_mode": "USER_DECISION",
                                  "decision_authority": "USER_DECISION_REQUIRED", "source_unknown_refs": [question["id"]],
                                  "evidence_refs": list(question["evidence_refs"]), "materiality": question["materiality"],
                                  "affects": list(question["affects"]), "decided_by": "USER", "accepted_recommendation": None}]
state["surface_manifest"]["records"][0]["decision_refs"] = ["DEC-001"]
results["open_surface_without_unknown"] = errors_of(state, "OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN")

# G: a Core cell bound to a record type the axis does not allow
closed = load("closed-minimal.state.json")
state = copy.deepcopy(closed)
state["coverage"][0]["cells"]["state"]["authority_bindings"] = [{"record_id": "FLOW-001", "pointer": "/paths", "value_sha256": "0" * 64}]
state = rehash(state)
results["core_cell_wrong_type"] = errors_of(state, path_prefix="coverage[0].cells.state")

# G: a UX action cell (back) bound to STATE, as in ATELIER rev17
state = copy.deepcopy(closed)
action = state["ux_coverage"][0]["actions"][0]
action["cells"]["back"] = {"status": "COVERED", "authority_bindings": [{"record_id": "STATE-001", "pointer": "/state_name", "value_sha256": "0" * 64}],
                           "unknown_refs": [], "basis_bindings": [], "rationale": None}
state = rehash(state)
results["ux_action_back_bound_to_state"] = errors_of(state, path_prefix="ux_coverage[0].actions[0].cells.back")

# G: an OPEN topology cell pointing at a question of the wrong origin, with a rationale
state = copy.deepcopy(closed)
state["surface_manifest"]["grill_profile"]["MONEY"] = {"status": "OPEN", "surface_refs": [], "unknown_refs": ["UNK-001"],
                                                        "basis_refs": [], "rationale": "not decided yet"}
results["open_topology_cell"] = errors_of(state, "invalid_grill_profile")

# G: blocks_unknown_refs naming an answered question
state = copy.deepcopy(closed)
blocked = copy.deepcopy(state["objects"]["unknowns"][0])
blocked.update({"id": "UNK-002", "status": "OPEN", "resolved_by": [], "resolution_mode": None, "resolution_summary": None,
                "blocks_unknown_refs": ["UNK-001"]})
state["objects"]["unknowns"].append(blocked)
results["blocks_answered_question"] = [e for e in errors_of(state, "invalid_unknown_contract") if "blocks" in e["path"]]

# C: an OPEN question whose decision_authority is not the derivation (COSTLY_TO_REVERSE with USER_CONFIRMATION)
state = load("discover-one-question.state.json")
question = state["objects"]["unknowns"][0]
question["materiality"]["reversibility"] = "COSTLY_TO_REVERSE"
question["decision_authority"] = "USER_CONFIRMATION"  # what 2.0.1 new_records.py question wrote for a HIGH recommendation
results["authority_derivation"] = errors_of(state, "invalid_decision_authority_derivation")

# G: first approval in the projection identity block and draft heading
sys.path.insert(0, str(SCRIPTS))
for module in ("update_projection", "projection_check"):
    sys.modules.pop(module, None)
import update_projection  # noqa: E402
import projection_check  # noqa: E402
first = copy.deepcopy(closed)
first["project"]["definition_revision"] = 1
results["identity_block_first_approval"] = [line for line in update_projection.identity_block(update_projection.facts(first), korean=True, html=False).splitlines() if "Manifest" in line] + \
    [line for line in update_projection.identity_block(update_projection.facts(first), korean=False, html=False).splitlines() if "Manifest" in line]
draft = projection_check.draft(first)
results["draft_heading_first_approval"] = [line for line in draft.splitlines() if line.startswith("## Records")]
results["draft_flow_line"] = [line for line in draft.splitlines() if "FLOW-001" in line]
try:
    full = projection_check.draft(first, full=True)
    lines = full.splitlines()
    start = next(i for i, line in enumerate(lines) if "FLOW-001" in line)
    results["draft_full_flow"] = lines[start:start + 14]
except TypeError as exc:
    results["draft_full_flow"] = f"not available: {exc}"

# G: a pipe the reader closes early (Select-Object -First / head): ATELIER rev17, its first approval (203 records)
if BIG is not None:
    (TMP / "spec.md").write_text("# spec\n", encoding="utf-8")
    proc = subprocess.Popen([sys.executable, "-B", str(SCRIPTS / "projection_check.py"), str(BIG), "--spec", str(TMP / "spec.md"), "--draft"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, env=ENV)
    proc.stdout.close()  # the reader is gone before the command writes (head / Select-Object -First stopped reading)
    stderr = proc.stderr.read().decode("utf-8")
    proc.wait()
    results["pipe_closed_early"] = {"exit": proc.returncode, "stderr_last_line": stderr.strip().splitlines()[-1] if stderr.strip() else ""}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"version": LABEL, **results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"version": LABEL, "scenarios": len(results)}))
