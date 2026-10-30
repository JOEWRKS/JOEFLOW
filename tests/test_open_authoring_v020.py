"""U2-5/U2-7: while a native definition is OPEN, requirements and screens may exist before their
coverage rows, so closing every question no longer needs a placeholder authoring question."""
import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))
sys.path.insert(0, str(ROOT))

import record_builders as build  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_examples_v020 import discover_one_question  # noqa: E402
from tests.test_semantic_closure_v020 import literal_ready_state  # noqa: E402

DEFERRED = {"missing_core_coverage", "missing_core_grill_coverage", "missing_ux_coverage"}


def questions_closed_before_freeze():
    """The DISCOVER example after the user answered its only question, with REQ and SCR drafted."""
    state = discover_one_question()
    question = state["objects"]["unknowns"][0]
    state["objects"]["decisions"] = [build.user_decision(
        question, "DEC-001", statement="Only signed-in customers can send feedback.",
        summary='User: "signed-in only"', decision_type="PRODUCT_BEHAVIOR", accepted=False)]
    ready = literal_ready_state()
    state["objects"]["requirements"] = [copy.deepcopy(ready["objects"]["requirements"][0])]
    state["objects"]["screens"] = [copy.deepcopy(ready["objects"]["screens"][0])]
    state["surface_manifest"]["records"][0].update(
        status="IN_SCOPE", unknown_refs=[], decision_refs=["DEC-001"], authority_refs=["REQ-001"])
    return state


def codes(state):
    return {error["code"] for error in validate_state_v2(state)}


class OpenAuthoringTest(unittest.TestCase):
    def test_open_definition_is_valid_between_questions_and_freeze(self):
        self.assertEqual(codes(questions_closed_before_freeze()), set())

    def test_missing_rows_are_errors_again_once_ready_for_review(self):
        state = questions_closed_before_freeze()
        state["project"]["definition_status"] = "READY_FOR_REVIEW"
        self.assertTrue(DEFERRED <= codes(state))

    def test_migrated_candidates_keep_their_coverage_errors(self):
        state = questions_closed_before_freeze()
        state["migration"] = {"mode": "MIGRATED"}
        self.assertTrue({"missing_core_coverage", "missing_ux_coverage"} & codes(state))

    def test_rows_that_exist_are_still_validated_while_open(self):
        ready = literal_ready_state()
        ready["project"]["definition_status"] = "OPEN"
        ready["coverage"][0]["cells"]["actor"]["status"] = "SKIPPED"
        self.assertIn("invalid_core_coverage_cell", codes(ready))


if __name__ == "__main__":
    unittest.main()
