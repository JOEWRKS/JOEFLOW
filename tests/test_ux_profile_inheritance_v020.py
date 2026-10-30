import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT))

from authority_binding_v2 import validate_ux_coverage_bindings  # noqa: E402
from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402
from ux_profile_inheritance import INHERITANCE_PATH, inheritable_ux_axes, load_inheritance  # noqa: E402
from tests.test_semantic_closure_v020 import (  # noqa: E402
    _profile_cell, approve_current_state, literal_approved_state, literal_ready_state,
)


def drop_axes(state, state_axes, action_axes):
    for row in state["ux_coverage"]:
        for axis in state_axes:
            row["states"].pop(axis, None)
        for action in row["actions"]:
            for axis in action_axes:
                action["cells"].pop(axis, None)
    return state


def codes(errors):
    return {error["code"] for error in errors}


class UxProfileInheritanceTest(unittest.TestCase):
    def test_reference_file_matches_the_module_table(self):
        contract = load_inheritance()
        self.assertEqual(json.loads(INHERITANCE_PATH.read_text(encoding="utf-8")), contract)
        self.assertEqual(set(contract["domains"]), {"AUTH", "PERMISSION"})

    def test_only_na_profile_domains_are_inheritable(self):
        # Fixture: AUTH ACTIVE, PERMISSION N/A.
        state = literal_ready_state()
        self.assertEqual(inheritable_ux_axes(state), ({"permission_denied"}, {"permission"}))
        state["surface_manifest"]["grill_profile"]["PERMISSION"]["status"] = "OPEN"
        self.assertEqual(inheritable_ux_axes(state), (set(), set()))
        state = literal_ready_state()
        state["surface_manifest"]["grill_profile"]["PERMISSION"]["basis_refs"] = []
        self.assertEqual(inheritable_ux_axes(state), (set(), set()))
        state["surface_manifest"]["grill_profile"]["PERMISSION"] = _profile_cell("N/A")
        state["surface_manifest"]["grill_profile"]["PERMISSION"]["rationale"] = "n/a"
        self.assertEqual(inheritable_ux_axes(state), (set(), set()))

    def test_states_with_every_cell_written_are_unchanged(self):
        self.assertEqual(validate_state_v2(literal_ready_state()), [])
        self.assertTrue(evaluate_closure_v2(literal_approved_state())["closed"])

    def test_inherited_axes_may_be_omitted_and_the_definition_still_closes(self):
        state = drop_axes(literal_ready_state(), {"permission_denied"}, {"permission"})
        self.assertEqual(validate_ux_coverage_bindings(state), [])
        self.assertEqual(validate_state_v2(state), [])
        result = evaluate_closure_v2(approve_current_state(state))
        self.assertTrue(result["closed"], result["errors"])

    def test_axes_of_an_active_domain_are_still_required(self):
        state = drop_axes(literal_ready_state(), {"unauthenticated"}, {"session_expiration"})
        self.assertEqual(
            codes(validate_ux_coverage_bindings(state)),
            {"screen_state_axis_inventory_mismatch", "action_axis_inventory_mismatch"},
        )

    def test_omission_is_rejected_once_the_profile_domain_reopens(self):
        state = drop_axes(literal_ready_state(), {"permission_denied"}, {"permission"})
        state["surface_manifest"]["grill_profile"]["PERMISSION"]["status"] = "OPEN"
        self.assertTrue({"screen_state_axis_inventory_mismatch", "action_axis_inventory_mismatch"}
                        <= codes(validate_ux_coverage_bindings(state)))

    def test_a_written_inherited_cell_is_still_validated(self):
        state = literal_ready_state()
        state["ux_coverage"][0]["states"]["permission_denied"]["status"] = "SKIPPED"
        self.assertIn("invalid_ux_coverage_cell", codes(validate_ux_coverage_bindings(state)))

    def test_unknown_axes_are_still_rejected(self):
        state = literal_ready_state()
        state["ux_coverage"][0]["states"]["made_up"] = state["ux_coverage"][0]["states"]["default"]
        self.assertIn("screen_state_axis_inventory_mismatch", codes(validate_ux_coverage_bindings(state)))


if __name__ == "__main__":
    unittest.main()
