import copy
import json
from pathlib import Path

from test_validators import closed_state

OUT = Path(__file__).parent / "fixtures"

def write(name, state):
    (OUT / name).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

base = closed_state()
write("closed.json", base)

state = copy.deepcopy(base); state["project"]["status"] = "OPEN"; state["project"]["user_approved"] = False
write("open.json", state)
state = copy.deepcopy(base); state["objects"]["requirements"][0]["status"] = "STALE"
write("stale.json", state)
state = copy.deepcopy(base); state["objects"]["decisions"][0]["affects"] = ["REQ-999"]
write("broken-reference.json", state)
state = copy.deepcopy(base); del state["coverage"][0]["cells"]["privacy"]
write("missing-coverage-dimension.json", state)
state = copy.deepcopy(base)
for group in state["objects"]: state["objects"][group] = []
state["coverage"] = []; state["ux_coverage"] = []
write("empty-definition.json", state)
state = copy.deepcopy(base); state["objects"]["acceptance_criteria"][0]["requirements"] = ["DEC-001"]
write("wrong-reference-type.json", state)
state = copy.deepcopy(base); state["project"]["definition_revision"] = 2
write("stale-approval.json", state)
state = copy.deepcopy(base); state["coverage"][0]["cells"]["privacy"] = {"status": "N/A"}
write("invalid-na-rationale.json", state)
state = copy.deepcopy(base); state["objects"]["unknowns"] = [{"id":"UNK-001","status":"DEFERRED_NON_BLOCKING","material":True,"deferral_reason":"later"}]
write("invalid-deferred-unknown.json", state)
state = copy.deepcopy(base); state["ux_coverage"] = []
write("missing-ux-coverage.json", state)
