import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
STATE_VALIDATOR = SCRIPTS / "validate_state.py"
CLOSURE_VALIDATOR = SCRIPTS / "validate_closure.py"


def closed_state():
    return {
        "schema_version": "0.1",
        "project": {"slug": "sample", "status": "CLOSED", "user_approved": True},
        "objects": {
            "goals": [{"id": "GOAL-001", "status": "CURRENT"}],
            "requirements": [{"id": "REQ-001", "status": "CURRENT", "acceptance": ["AC-001"], "screens": ["SCR-001"]}],
            "unknowns": [],
            "decisions": [{"id": "DEC-001", "status": "ANSWERED", "affects": ["REQ-001"]}],
            "rules": [],
            "flows": [{"id": "FLOW-001", "status": "CURRENT", "screens": ["SCR-001"]}],
            "screens": [{"id": "SCR-001", "status": "CURRENT", "requirements": ["REQ-001"]}],
            "states": [],
            "data": [],
            "integrations": [],
            "acceptance_criteria": [{"id": "AC-001", "status": "CURRENT", "requirements": ["REQ-001"]}],
            "tasks": [{"id": "TASK-001", "status": "CURRENT", "implements": ["REQ-001"], "acceptance": ["AC-001"]}],
        },
        "coverage": [{"feature_id": "REQ-001", "cells": {"actor": "COVERED", "goal": "COVERED", "acceptance": "COVERED"}}],
        "contradictions": [],
    }


class ValidatorCLITest(unittest.TestCase):
    def run_validator(self, script, state):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertTrue(result.stdout.strip(), f"validator did not emit JSON: {result.stderr.strip()}")
        payload = json.loads(result.stdout)
        return result.returncode, payload

    def test_state_validator_accepts_well_formed_graph(self):
        code, payload = self.run_validator(STATE_VALIDATOR, closed_state())
        self.assertEqual(code, 0)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["errors"], [])

    def test_state_validator_rejects_duplicate_ids(self):
        state = closed_state()
        state["objects"]["rules"] = [{"id": "REQ-001", "status": "CURRENT"}]
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("duplicate_id", {error["code"] for error in payload["errors"]})

    def test_state_validator_rejects_broken_references(self):
        state = closed_state()
        state["objects"]["decisions"][0]["affects"] = ["REQ-999"]
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("broken_reference", {error["code"] for error in payload["errors"]})

    def test_state_validator_rejects_invalid_status(self):
        state = closed_state()
        state["objects"]["decisions"][0]["status"] = "MAYBE"
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("invalid_status", {error["code"] for error in payload["errors"]})

    def test_state_validator_rejects_dependency_cycle(self):
        state = closed_state()
        state["objects"]["requirements"][0]["depends_on"] = ["DEC-001"]
        state["objects"]["decisions"][0]["depends_on"] = ["REQ-001"]
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("dependency_cycle", {error["code"] for error in payload["errors"]})

    def test_closure_validator_accepts_closed_state(self):
        code, payload = self.run_validator(CLOSURE_VALIDATOR, closed_state())
        self.assertEqual(code, 0)
        self.assertTrue(payload["closed"])
        self.assertTrue(all(value == 0 for value in payload["metrics"].values()))

    def test_closure_validator_reports_all_blocker_classes(self):
        state = closed_state()
        state["project"] = {"slug": "sample", "status": "OPEN", "user_approved": False}
        state["objects"]["unknowns"] = [{"id": "UNK-001", "status": "OPEN", "material": True}]
        state["objects"]["decisions"].append({"id": "DEC-002", "status": "OPEN", "material": True, "affects": []})
        state["objects"]["screens"][0]["status"] = "STALE"
        state["coverage"][0]["cells"]["privacy"] = "OPEN"
        state["contradictions"] = [{"id": "CON-001", "status": "OPEN"}]
        state["objects"]["requirements"][0]["acceptance"] = []
        state["objects"]["screens"].append({"id": "SCR-002", "status": "CURRENT", "requirements": []})
        state["objects"]["acceptance_criteria"].append({"id": "AC-002", "status": "CURRENT", "requirements": []})
        state["objects"]["tasks"].append({"id": "TASK-002", "status": "CURRENT", "implements": [], "acceptance": []})

        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertFalse(payload["closed"])
        for metric in (
            "blocking_unknowns", "open_material_decisions", "contradictions",
            "stale_artifacts", "coverage_gaps", "orphan_requirements",
            "orphan_screens", "orphan_acceptance_criteria",
            "unmapped_implementation_tasks", "missing_user_approval",
        ):
            self.assertGreater(payload["metrics"][metric], 0, metric)


if __name__ == "__main__":
    unittest.main()
