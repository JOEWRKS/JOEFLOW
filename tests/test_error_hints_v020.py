import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from authority_binding_v2 import make_authority_binding  # noqa: E402
from explain_state_errors import explain  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_approval_manifest_v020 import approved_recommendation_state  # noqa: E402
from tests.test_semantic_closure_v020 import literal_ready_state  # noqa: E402
from tests.v020_support import foundation_state  # noqa: E402


def _errors(state, code):
    return [error for error in validate_state_v2(state) if error["code"] == code]


def _first_covered_cell(state):
    for row in state["coverage"]:
        for axis, cell in row["cells"].items():
            if cell["status"] == "COVERED":
                return axis, cell
    raise AssertionError("fixture has no COVERED Core cell")


class GrillErrorMessageTest(unittest.TestCase):
    def test_unknown_contract_names_missing_and_unexpected_fields(self):
        state = literal_ready_state()
        unknown = state["objects"]["unknowns"][0]
        del unknown["why_it_matters"]
        unknown["note"] = "extra"

        messages = [error["message"] for error in _errors(state, "invalid_unknown_contract")]

        self.assertTrue(any("missing ['why_it_matters']" in m and "unexpected ['note']" in m for m in messages), messages)

    def test_reasoning_refs_names_rejected_refs_and_permitted_kinds(self):
        state = approved_recommendation_state()
        decision_id = state["objects"]["decisions"][0]["id"]
        state["objects"]["unknowns"][0]["recommendation"]["reasoning_refs"].append(decision_id)

        messages = [error["message"] for error in _errors(state, "invalid_recommendation_reference")]

        self.assertEqual(len(messages), 1, messages)
        self.assertIn(f"rejected ['{decision_id}']", messages[0])
        self.assertIn("decisions (DEC) are not permitted", messages[0])

    def test_accepted_recommendation_names_the_exact_expected_values(self):
        state = approved_recommendation_state()
        state["objects"]["decisions"][0]["accepted_recommendation"]["alternatives_presented"] = ["OPT-B"]

        messages = [error["message"] for error in _errors(state, "invalid_recommendation_acceptance")]

        self.assertEqual(len(messages), 1, messages)
        self.assertIn("alternatives_presented ['OPT-A', 'OPT-B']", messages[0])
        self.assertIn("recommended_option 'OPT-A'", messages[0])

    def test_grill_profile_names_the_shape_for_each_status(self):
        state = foundation_state()
        profile = state["surface_manifest"]["grill_profile"]["AUTH"]
        profile["status"] = "ACTIVE"

        messages = [error["message"] for error in _errors(state, "invalid_grill_profile")]

        self.assertTrue(messages)
        self.assertIn("declared status 'ACTIVE'", messages[0])
        self.assertIn("ACTIVE needs current surface_refs, unknown_refs [] and rationale null", messages[0])


class ExplainStateErrorsTest(unittest.TestCase):
    def test_valid_state_has_no_errors(self):
        self.assertEqual(explain(literal_ready_state()), {"valid": True, "errors": []})

    def test_evidence_authority_class_hint_lists_supported_classes(self):
        state = literal_ready_state()
        state["evidence"][0]["authority_classes"] = ["FACTUAL"]

        hints = [e["hint"] for e in explain(state)["errors"] if e["code"] == "invalid_evidence_authority_class"]

        self.assertEqual(hints[0]["source_kind"], "USER_CONFIRMED_INTENT")
        self.assertEqual(hints[0]["supported_authority_classes"], ["INTENT", "PREFERENCE"])

    def test_coverage_hint_names_each_bad_binding_with_allowed_types_and_hashes(self):
        state = literal_ready_state()
        axis, cell = _first_covered_cell(state)
        bound = cell["authority_bindings"][0]
        record = next(
            r for group in state["objects"].values() if isinstance(group, list)
            for r in group if isinstance(r, dict) and r.get("id") == bound["record_id"]
        )
        stale = copy.deepcopy(bound)
        stale["value_sha256"] = "0" * 64
        cell["authority_bindings"] = [stale, make_authority_binding(state, "GOAL-001", "/statement")]

        errors = [e for e in explain(state)["errors"] if e["path"].endswith(f".cells.{axis}")]

        self.assertEqual(len(errors), 1, errors)
        hint = errors[0]["hint"]
        self.assertEqual(hint["cell_status"], "COVERED")
        findings = {finding["code"]: finding for finding in hint["binding_findings"]}
        self.assertEqual(findings["authority_binding_hash_mismatch"]["record_id"], record["id"])
        self.assertEqual(findings["authority_binding_hash_mismatch"]["bound_value_sha256"], "0" * 64)
        self.assertIn("current_value_sha256", findings["authority_binding_hash_mismatch"])
        if "GOAL" not in hint["allowed_record_types"]:
            self.assertEqual(findings["invalid_authority_binding_type"]["record_type"], "GOAL")

    def test_cli_exit_codes_and_utf8(self):
        state = literal_ready_state()
        state["evidence"][0]["authority_classes"] = ["FACTUAL"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "상태.json"
            path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPTS / "explain_state_errors.py"), str(path)],
                                    cwd=ROOT, capture_output=True, check=False)
        self.assertEqual(result.returncode, 1, result.stderr.decode("utf-8", "replace"))
        payload = json.loads(result.stdout.decode("utf-8"))
        self.assertFalse(payload["valid"])


if __name__ == "__main__":
    unittest.main()
