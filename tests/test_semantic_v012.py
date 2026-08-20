import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_validators import closed_state

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"


def stamp(state):
    canonical = copy.deepcopy(state)
    canonical["project"].pop("approval", None)
    canonical["project"].pop("user_approved", None)
    canonical["project"].pop("status", None)
    state["project"]["approval"]["approved_revision"] = state["project"]["definition_revision"]
    state["project"]["approval"]["approved_digest"] = hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    state["project"]["approval"]["approved_at"] = "2026-08-20T00:00:00Z"
    state["project"]["user_approved"] = True
    state["project"]["status"] = "CLOSED"
    return state


class SemanticV012Test(unittest.TestCase):
    def invoke(self, kind, state):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "state.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPTS / f"validate_{kind}.py"), str(path)], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def codes(self, payload):
        return {e["code"] for e in payload["errors"]}

    def test_unknown_closed_statuses_require_evidence(self):
        cases = [
            ({"id":"UNK-001","status":"ANSWERED","material":True}, "invalid_answered_unknown"),
            ({"id":"UNK-001","status":"ASSUMED_ACCEPTED","material":True,"accepted_by":"agent"}, "invalid_assumed_unknown"),
            ({"id":"UNK-001","status":"DEFERRED_NON_BLOCKING","material":True,"source":"user","deferral_reason":"later","non_blocking_impact_review":{"scope":False}}, "invalid_deferred_unknown"),
        ]
        for unknown, expected in cases:
            state=closed_state(); state["objects"]["unknowns"]=[unknown]
            code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertIn(expected,self.codes(p))

    def test_decision_closed_statuses_require_evidence(self):
        state=closed_state(); state["objects"]["decisions"][0]={"id":"DEC-001","status":"DEFERRED_NON_BLOCKING","source":"user"}
        code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertIn("invalid_deferred_decision",self.codes(p))

    def test_superseded_requires_same_type_replacement(self):
        for target in (None,"DEC-001"):
            state=closed_state(); item={"id":"REQ-002","status":"SUPERSEDED","acceptance":[],"screens":[]}
            if target:item["superseded_by"]=target
            state["objects"]["requirements"].append(item)
            code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertIn("invalid_supersession",self.codes(p))

    def test_only_superseded_requirements_do_not_satisfy_minimum(self):
        state=closed_state(); state["objects"]["requirements"][0]["status"]="SUPERSEDED"; state["objects"]["requirements"][0]["superseded_by"]="REQ-002"; state["objects"]["requirements"].append({"id":"REQ-002","status":"SUPERSEDED","superseded_by":"REQ-001"})
        code,p=self.invoke("closure",state); self.assertEqual(code,1); self.assertGreater(p["metrics"].get("missing_material_requirement",0),0)

    def test_historical_objects_need_no_current_coverage(self):
        state=closed_state(); state["objects"]["requirements"].append({"id":"REQ-002","status":"SUPERSEDED","superseded_by":"REQ-001"}); state["objects"]["screens"].append({"id":"SCR-002","status":"SUPERSEDED","superseded_by":"SCR-001"})
        stamp(state); code,p=self.invoke("closure",state); self.assertEqual(code,0,p)

    def test_genuine_screenless_api_product_closes(self):
        state=closed_state(); req=state["objects"]["requirements"][0]; req.update({"ui_required":False,"no_screen_reason":"API-only background synchronization.","screens":[]}); state["objects"]["screens"]=[]; state["objects"]["flows"]=[]; state["ux_coverage"]=[]; stamp(state)
        code,p=self.invoke("closure",state); self.assertEqual(code,0,p)

    def test_noninteractive_screen_requires_reason_but_no_ux(self):
        state=closed_state(); screen=state["objects"]["screens"][0]; screen["interactive"]=False; state["ux_coverage"]=[]; stamp(state)
        code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertIn("missing_non_interactive_reason",self.codes(p))
        screen["non_interactive_reason"]="Read-only legal notice."; stamp(state); code,p=self.invoke("closure",state); self.assertEqual(code,0,p)

    def test_action_inventory_must_equal_coverage(self):
        for declared,covered in [(["submit","forgot"],["submit"]),(["submit"],["submit","extra"]),(["submit"],["submit","submit"])]:
            state=closed_state(); state["objects"]["screens"][0]["major_actions"]=declared; action=state["ux_coverage"][0]["actions"][0]; state["ux_coverage"][0]["actions"]=[dict(action,key=k) for k in covered]
            code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertTrue(self.codes(p)&{"action_inventory_mismatch","duplicate_action_coverage"})

    def test_zero_actions_requires_screen_reason(self):
        state=closed_state(); state["objects"]["screens"][0]["major_actions"]=[]; state["ux_coverage"][0]["actions"]=[]
        code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertIn("missing_no_major_actions_reason",self.codes(p))
        state["objects"]["screens"][0]["no_major_actions_reason"]="Passive result screen."; stamp(state); code,p=self.invoke("closure",state); self.assertEqual(code,0,p)

    def test_duplicate_ux_coverage_rejected(self):
        state=closed_state(); state["ux_coverage"].append(copy.deepcopy(state["ux_coverage"][0])); code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertIn("duplicate_ux_coverage",self.codes(p))

    def test_remaining_typed_edges_and_supersession(self):
        for group,field,target in [("requirements","rules","SCR-001"),("screens","flows","AC-001")]:
            state=closed_state(); state["objects"][group][0][field]=[target]; code,p=self.invoke("state",state); self.assertEqual(code,1); self.assertIn("invalid_reference_type",self.codes(p))

    def test_schema_runtime_critical_shape(self):
        schema=json.loads((ROOT/"skills/joewrks-product-definition/schemas/state.schema.json").read_text())
        self.assertNotIn("$ref",schema)
        action=schema["$defs"]["screenCoverage"]["properties"]["actions"]
        self.assertEqual(action["type"],"array"); self.assertEqual(set(action["items"]["required"]),{"key","cells"})
        for path in (ROOT/"README.md",ROOT/"skills/joewrks-product-definition/SKILL.md",ROOT/"skills/joewrks-product-definition/references/state-contract.md"):
            self.assertIn("schemas/state.schema.json",path.read_text(encoding="utf-8"))


if __name__ == "__main__": unittest.main()
