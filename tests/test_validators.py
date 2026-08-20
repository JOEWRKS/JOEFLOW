import json
import copy
import hashlib
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
    coverage_dimensions = (
        "actor", "goal", "entry_point", "precondition", "happy_path",
        "alternative_path", "error", "recovery", "permission", "state",
        "data", "side_effect", "notification", "validation", "boundary",
        "persistence", "security", "privacy", "analytics", "acceptance",
    )
    screen_states = (
        "default", "loading", "empty", "partial", "success", "error",
        "disabled", "permission_denied", "unauthenticated", "offline",
        "timeout", "retrying", "submitting", "completed", "cancelled", "expired",
    )
    action_axes = (
        "entry", "precondition", "input", "validation", "submit", "success",
        "failure", "retry", "cancel", "back", "refresh", "duplicate_concurrent_action",
        "timeout", "offline", "permission",
        "session_expiration", "data_mutation", "side_effect", "notification",
        "persistence", "undo", "destructive_confirmation",
    )
    state = {
        "schema_version": "0.1.1",
        "project": {"slug": "sample", "status": "CLOSED", "definition_revision": 1, "user_approved": True, "approval": {"approved_revision": 1, "approved_digest": None, "approved_at": "2026-08-20T00:00:00Z"}},
        "objects": {
            "goals": [{"id": "GOAL-001", "status": "CURRENT"}],
            "users": [{"id": "USR-001", "status": "CURRENT"}],
            "requirements": [{"id": "REQ-001", "status": "CURRENT", "acceptance": ["AC-001"], "screens": ["SCR-001"]}],
            "unknowns": [],
            "decisions": [{"id": "DEC-001", "status": "ANSWERED", "decision": "Use the defined flow", "source": "user", "affects": ["REQ-001"]}],
            "rules": [],
            "flows": [{"id": "FLOW-001", "status": "CURRENT", "screens": ["SCR-001"]}],
            "screens": [{"id": "SCR-001", "status": "CURRENT", "requirements": ["REQ-001"]}],
            "states": [],
            "data": [],
            "integrations": [],
            "acceptance_criteria": [{"id": "AC-001", "status": "CURRENT", "requirements": ["REQ-001"]}],
            "tasks": [{"id": "TASK-001", "status": "CURRENT", "implements": ["REQ-001"], "acceptance": ["AC-001"]}],
        },
        "coverage": [{"feature_id": "REQ-001", "cells": {key: {"status": "COVERED"} for key in coverage_dimensions}}],
        "ux_coverage": [{
            "screen_id": "SCR-001",
            "states": {key: {"status": "COVERED"} for key in screen_states},
            "actions": [{"key": "submit", "cells": {key: {"status": "COVERED"} for key in action_axes}}],
        }],
        "contradictions": [],
    }
    canonical = copy.deepcopy(state)
    canonical["project"].pop("approval")
    canonical["project"].pop("user_approved")
    canonical["project"].pop("status")
    state["project"]["approval"]["approved_digest"] = hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return state


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
        state["project"] = {"slug": "sample", "status": "OPEN"}
        state["project"]["user_approved"] = False
        state["project"]["approval"] = {"approved_revision": None, "approved_digest": None, "approved_at": None}
        state["objects"]["unknowns"] = [{"id": "UNK-001", "status": "OPEN", "material": True}]
        state["objects"]["decisions"].append({"id": "DEC-002", "status": "OPEN", "material": True, "affects": []})
        state["objects"]["screens"][0]["status"] = "STALE"
        state["coverage"][0]["cells"]["privacy"] = {"status": "OPEN"}
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

    def test_closure_rejects_missing_required_coverage_dimensions(self):
        state = closed_state()
        for key in list(state["coverage"][0]["cells"])[3:]:
            del state["coverage"][0]["cells"][key]
        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertFalse(payload["closed"])
        self.assertEqual(payload["metrics"]["coverage_gaps"], 17)

    def test_closure_rejects_empty_product_definition(self):
        state = {
            "schema_version": "0.1.1",
            "project": {"slug": "empty", "status": "CLOSED", "definition_revision": 1, "user_approved": True, "approval": {"approved_revision": 1, "approved_digest": "invalid", "approved_at": "2026-08-20T00:00:00Z"}},
            "objects": {
                "goals": [], "users": [], "requirements": [], "unknowns": [],
                "decisions": [], "rules": [], "flows": [], "screens": [],
                "states": [], "data": [], "integrations": [],
                "acceptance_criteria": [], "tasks": [],
            },
            "coverage": [], "ux_coverage": [], "contradictions": [],
        }
        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertFalse(payload["closed"])
        self.assertIn("minimum_definition_gaps", payload["metrics"])
        self.assertGreater(payload["metrics"].get("minimum_definition_gaps", 0), 0)

    def test_closure_rejects_approval_for_prior_revision(self):
        state = closed_state()
        state["project"]["definition_revision"] = 2
        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertFalse(payload["closed"])
        self.assertEqual(payload["metrics"]["stale_approval"], 1)

    def test_closure_rejects_digest_changed_after_approval(self):
        state = closed_state()
        state["objects"]["requirements"][0]["statement"] = "changed after approval"
        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertFalse(payload["closed"])
        self.assertGreater(payload["metrics"].get("stale_user_approval", 0), 0)

    def test_state_validator_rejects_duplicate_coverage_row(self):
        state = closed_state()
        state["coverage"].append(state["coverage"][0].copy())
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("duplicate_coverage", {item["code"] for item in payload["errors"]})

    def test_non_ui_requirement_needs_reason_but_not_screen(self):
        state = closed_state()
        requirement = state["objects"]["requirements"][0]
        requirement["ui_required"] = False
        requirement["no_screen_reason"] = "Background synchronization requirement."
        requirement["screens"] = []
        canonical = copy.deepcopy(state)
        canonical["project"].pop("approval")
        canonical["project"].pop("user_approved")
        canonical["project"].pop("status")
        state["project"]["approval"]["approved_digest"] = hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 0, payload)

    def test_state_validator_requires_canonical_object_groups(self):
        state = closed_state()
        del state["objects"]["users"]
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("schema_error", {item["code"] for item in payload["errors"]})

    def test_state_validator_requires_current_schema_version(self):
        state = closed_state()
        state["schema_version"] = "0.1"
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("schema_error", {item["code"] for item in payload["errors"]})

    def test_closure_requires_coverage_row_for_every_requirement(self):
        state = closed_state()
        state["objects"]["requirements"].append({"id": "REQ-002", "status": "CURRENT", "acceptance": ["AC-001"], "screens": ["SCR-001"]})
        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertEqual(payload["metrics"]["coverage_gaps"], 20)

    def test_state_validator_rejects_group_prefix_mismatch(self):
        state = closed_state()
        state["objects"]["requirements"][0]["id"] = "DEC-009"
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("invalid_id_type", {item["code"] for item in payload["errors"]})

    def test_state_validator_rejects_semantically_wrong_reference_type(self):
        state = closed_state()
        state["objects"]["requirements"][0]["acceptance"] = ["DEC-001"]
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("invalid_reference_type", {item["code"] for item in payload["errors"]})

    def test_closure_requires_complete_screen_state_and_action_coverage(self):
        state = closed_state()
        del state["ux_coverage"][0]["states"]["offline"]
        del state["ux_coverage"][0]["actions"][0]["cells"]["retry"]
        code, payload = self.run_validator(CLOSURE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertEqual(payload["metrics"]["screen_state_gaps"], 1)
        self.assertEqual(payload["metrics"]["screen_action_gaps"], 1)

    def test_state_validator_requires_rationale_for_not_applicable(self):
        state = closed_state()
        state["coverage"][0]["cells"]["analytics"] = {"status": "N/A"}
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        self.assertIn("missing_rationale", {item["code"] for item in payload["errors"]})

    def test_state_validator_requires_evidence_for_escape_hatches(self):
        state = closed_state()
        state["objects"]["unknowns"] = [{"id": "UNK-001", "status": "DEFERRED_NON_BLOCKING", "material": True}]
        state["objects"]["decisions"][0] = {"id": "DEC-001", "status": "ASSUMED_ACCEPTED", "affects": ["REQ-001"]}
        code, payload = self.run_validator(STATE_VALIDATOR, state)
        self.assertEqual(code, 1)
        codes = {item["code"] for item in payload["errors"]}
        self.assertIn("invalid_deferred_unknown", codes)
        self.assertIn("invalid_assumed_decision", codes)


if __name__ == "__main__":
    unittest.main()
