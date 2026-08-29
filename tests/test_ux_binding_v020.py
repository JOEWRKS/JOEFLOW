import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))

import authority_binding_v2 as binding  # noqa: E402
from tests.v020_support import foundation_state  # noqa: E402


make_authority_binding = binding.make_authority_binding


def validate_ux_coverage_bindings(state):
    return getattr(
        binding, "validate_ux_coverage_bindings",
        lambda _: [{"code": "missing_ux_binding_api"}],
    )(state)


def ux_binding_metrics(state):
    return getattr(
        binding, "ux_binding_metrics",
        lambda _: {key: 0 for key in (
            "ux_coverage_gaps", "screen_state_gaps", "screen_action_inventory_gaps",
            "ux_invalid_authority_binding", "ux_stale_authority_binding",
            "ux_open_without_unknown", "ux_unjustified_na",
        )},
    )(state)


STATE_AXES = (
    "default", "loading", "empty", "partial", "success", "error", "disabled",
    "permission_denied", "unauthenticated", "offline", "timeout", "retrying",
    "submitting", "completed", "cancelled", "expired",
)
ACTION_AXES = (
    "entry", "precondition", "input", "validation", "submit", "success", "failure",
    "retry", "cancel", "back", "refresh", "duplicate_concurrent_action", "timeout",
    "offline", "permission", "session_expiration", "data_mutation", "side_effect",
    "notification", "persistence", "undo", "destructive_confirmation",
)


def state_with_authorities(*, actions=("submit",)):
    state = foundation_state()
    state["objects"]["screens"] = [{
        "id": "SCR-001", "status": "CURRENT", "purpose": "Edit work.",
        "interaction_mode": "INTERACTIVE", "major_actions": list(actions),
    }]
    state["objects"]["states"] = [{
        "id": "STATE-001", "status": "CURRENT", "state_name": "WORKING", "conditions": ["While editing."],
    }]
    state["objects"]["flows"] = [{
        "id": "FLOW-001", "status": "CURRENT", "entry": "Open the editor.",
        "preconditions": ["Signed in."], "paths": ["Submit."], "outcomes": ["Saved."],
    }]
    state["objects"]["rules"] = [{
        "id": "RULE-001", "status": "CURRENT", "statement": "Validate each edit.", "applies_to": [],
    }]
    state["objects"]["data"] = [{
        "id": "DATA-001", "status": "CURRENT", "name": "Draft", "purpose": "Hold edits.", "ownership": "USER",
    }]
    state["objects"]["acceptance_criteria"] = [{
        "id": "AC-001", "status": "CURRENT", "assertion": "An edit saves.",
    }]
    state["objects"]["unknowns"] = [{"id": "UNK-001", "status": "OPEN"}]
    return state


def cell(state, record_id, pointer):
    return {
        "status": "COVERED", "authority_bindings": [make_authority_binding(state, record_id, pointer)],
        "unknown_refs": [], "basis_bindings": [], "rationale": None,
    }


def exact_states(state):
    records = {
        "default": ("SCR-001", "/purpose"), "loading": ("FLOW-001", "/entry"),
        "empty": ("RULE-001", "/statement"), "partial": ("RULE-001", "/statement"),
        "success": ("FLOW-001", "/entry"), "error": ("RULE-001", "/statement"),
        "disabled": ("STATE-001", "/state_name"), "permission_denied": ("RULE-001", "/statement"),
        "unauthenticated": ("RULE-001", "/statement"), "offline": ("RULE-001", "/statement"),
        "timeout": ("RULE-001", "/statement"), "retrying": ("RULE-001", "/statement"),
        "submitting": ("FLOW-001", "/entry"), "completed": ("FLOW-001", "/entry"),
        "cancelled": ("RULE-001", "/statement"), "expired": ("RULE-001", "/statement"),
    }
    return {axis: cell(state, *records[axis]) for axis in STATE_AXES}


def exact_action_cells(state):
    records = {
        "entry": ("SCR-001", "/purpose"), "precondition": ("RULE-001", "/statement"),
        "input": ("DATA-001", "/name"), "validation": ("RULE-001", "/statement"),
        "submit": ("SCR-001", "/purpose"), "success": ("FLOW-001", "/entry"),
        "failure": ("RULE-001", "/statement"), "retry": ("RULE-001", "/statement"),
        "cancel": ("RULE-001", "/statement"), "back": ("SCR-001", "/purpose"),
        "refresh": ("RULE-001", "/statement"), "duplicate_concurrent_action": ("RULE-001", "/statement"),
        "timeout": ("RULE-001", "/statement"), "offline": ("RULE-001", "/statement"),
        "permission": ("RULE-001", "/statement"), "session_expiration": ("RULE-001", "/statement"),
        "data_mutation": ("DATA-001", "/name"), "side_effect": ("RULE-001", "/statement"),
        "notification": ("RULE-001", "/statement"), "persistence": ("DATA-001", "/name"),
        "undo": ("RULE-001", "/statement"), "destructive_confirmation": ("RULE-001", "/statement"),
    }
    return {axis: cell(state, *records[axis]) for axis in ACTION_AXES}


def exact_ux_row(state, *, action_keys=("submit",)):
    return {
        "screen_id": "SCR-001", "states": exact_states(state),
        "actions": [{"key": key, "cells": exact_action_cells(state)} for key in action_keys],
    }


class UxBindingV020Test(unittest.TestCase):
    def codes(self, state):
        return {error["code"] for error in validate_ux_coverage_bindings(state)}

    def test_current_screen_requires_exactly_one_ux_row(self):
        # Break caught: a current product surface silently losing UX coverage or accepting a duplicate row.
        state = state_with_authorities()
        self.assertIn("missing_ux_coverage", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["ux_coverage_gaps"], 1)
        state["ux_coverage"] = [exact_ux_row(state), exact_ux_row(state)]
        self.assertIn("duplicate_ux_coverage", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["ux_coverage_gaps"], 1)

    def test_state_inventory_is_the_exact_frozen_sixteen_axes(self):
        # Break caught: a UX row omitting or inventing a screen-state case.
        state = state_with_authorities()
        state["ux_coverage"] = [exact_ux_row(state)]
        del state["ux_coverage"][0]["states"]["expired"]
        self.assertIn("screen_state_axis_inventory_mismatch", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["screen_state_gaps"], 1)
        state["ux_coverage"][0]["states"]["unexpected"] = {"status": "COVERED"}
        self.assertIn("screen_state_axis_inventory_mismatch", self.codes(state))
        self.assertIn("invalid_ux_coverage_cell", self.codes(state))

    def test_extra_state_axis_still_enforces_open_unknown_proof(self):
        # Break caught: a well-shaped extra state cell bypassing OPEN's required current unknown.
        state = state_with_authorities()
        state["ux_coverage"] = [exact_ux_row(state)]
        state["ux_coverage"][0]["states"]["unexpected"] = {
            "status": "OPEN", "authority_bindings": [], "unknown_refs": [],
            "basis_bindings": [], "rationale": None,
        }
        self.assertIn("screen_state_axis_inventory_mismatch", self.codes(state))
        self.assertIn("ux_open_without_unknown", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["ux_open_without_unknown"], 1)

    def test_action_keys_equal_major_actions_without_missing_extra_or_duplicates(self):
        # Break caught: action rows diverging from the screen's declared major actions.
        state = state_with_authorities(actions=("submit", "cancel"))
        state["ux_coverage"] = [exact_ux_row(state, action_keys=("submit",))]
        self.assertIn("screen_action_inventory_mismatch", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["screen_action_inventory_gaps"], 1)
        state["ux_coverage"] = [exact_ux_row(state, action_keys=("submit", "cancel", "extra"))]
        self.assertIn("screen_action_inventory_mismatch", self.codes(state))
        state["ux_coverage"] = [exact_ux_row(state, action_keys=("submit", "submit"))]
        self.assertIn("screen_action_inventory_mismatch", self.codes(state))

    def test_orphan_row_with_duplicate_actions_fails_row_and_action_inventory(self):
        # Break caught: orphan or non-current UX rows bypassing duplicate-action validation.
        state = state_with_authorities()
        orphan = exact_ux_row(state, action_keys=("submit", "submit"))
        orphan["screen_id"] = "SCR-999"
        state["ux_coverage"] = [exact_ux_row(state), orphan]
        self.assertIn("invalid_ux_coverage_row", self.codes(state))
        self.assertIn("screen_action_inventory_mismatch", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["screen_action_inventory_gaps"], 1)
        stale = copy.deepcopy(state_with_authorities())
        stale["objects"]["screens"].append({
            "id": "SCR-002", "status": "STALE", "major_actions": ["cancel"],
        })
        non_current = exact_ux_row(stale, action_keys=("submit", "submit"))
        non_current["screen_id"] = "SCR-002"
        stale["ux_coverage"] = [exact_ux_row(stale), non_current]
        self.assertIn("screen_action_inventory_mismatch", self.codes(stale))
        self.assertEqual(ux_binding_metrics(stale)["screen_action_inventory_gaps"], 1)

    def test_every_action_row_has_the_exact_frozen_twenty_two_axes(self):
        # Break caught: a declared action dropping or inventing a required action-axis cell.
        state = state_with_authorities()
        state["ux_coverage"] = [exact_ux_row(state)]
        del state["ux_coverage"][0]["actions"][0]["cells"]["destructive_confirmation"]
        self.assertIn("action_axis_inventory_mismatch", self.codes(state))
        state["ux_coverage"][0]["actions"][0]["cells"]["unexpected"] = {"status": "COVERED"}
        self.assertIn("action_axis_inventory_mismatch", self.codes(state))
        self.assertIn("invalid_ux_coverage_cell", self.codes(state))

    def test_valid_exact_state_and_action_bindings_have_no_ux_errors(self):
        # Break caught: valid record-relative UX proofs being rejected despite matching every frozen axis.
        state = state_with_authorities()
        state["ux_coverage"] = [exact_ux_row(state)]
        self.assertEqual(validate_ux_coverage_bindings(state), [])
        self.assertEqual(ux_binding_metrics(state), {
            "ux_coverage_gaps": 0, "screen_state_gaps": 0, "screen_action_inventory_gaps": 0,
            "ux_invalid_authority_binding": 0, "ux_stale_authority_binding": 0,
            "ux_open_without_unknown": 0, "ux_unjustified_na": 0,
        })

    def test_axis_type_rules_reject_wrong_permission_error_and_persistence_authority(self):
        # Break caught: a type-ineligible authority proving permission, error, or persistence UX behavior.
        state = state_with_authorities()
        state["ux_coverage"] = [exact_ux_row(state)]
        wrong = make_authority_binding(state, "SCR-001", "/purpose")
        state["ux_coverage"][0]["states"]["permission_denied"]["authority_bindings"] = [wrong]
        state["ux_coverage"][0]["states"]["error"]["authority_bindings"] = [wrong]
        state["ux_coverage"][0]["actions"][0]["cells"]["persistence"]["authority_bindings"] = [wrong]
        self.assertIn("invalid_authority_binding_type", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["ux_invalid_authority_binding"], 3)

    def test_hash_drift_and_stale_status_reject_covered_ux_cells(self):
        # Break caught: stale or hash-drifted authority still proving a COVERED UX cell.
        state = state_with_authorities()
        state["ux_coverage"] = [exact_ux_row(state)]
        state["ux_coverage"][0]["states"]["default"]["authority_bindings"][0]["value_sha256"] = "0" * 64
        self.assertIn("authority_binding_hash_mismatch", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["ux_invalid_authority_binding"], 1)
        stale = copy.deepcopy(state_with_authorities())
        stale["ux_coverage"] = [exact_ux_row(stale)]
        stale["objects"]["states"][0]["status"] = "STALE"
        self.assertIn("stale_authority_binding", self.codes(stale))
        self.assertEqual(ux_binding_metrics(stale)["ux_stale_authority_binding"], 1)

    def test_open_and_na_require_exact_unknown_and_basis_proof(self):
        # Break caught: OPEN without a live unknown or N/A without a strict, meaningful basis proof.
        state = state_with_authorities()
        state["ux_coverage"] = [exact_ux_row(state)]
        target = state["ux_coverage"][0]["states"]["default"]
        target.update({"status": "OPEN", "authority_bindings": [], "unknown_refs": [], "basis_bindings": [], "rationale": None})
        self.assertIn("ux_open_without_unknown", self.codes(state))
        self.assertEqual(ux_binding_metrics(state)["ux_open_without_unknown"], 1)
        target.update({"status": "N/A", "unknown_refs": [], "basis_bindings": [], "rationale": None})
        self.assertEqual(ux_binding_metrics(state)["ux_unjustified_na"], 1)
        target.update({
            "basis_bindings": [make_authority_binding(state, "EVD-900", "/claim")],
            "rationale": "No applicable state exists for this screen.",
        })
        self.assertNotIn("ux_unjustified_na", self.codes(state))

    def test_zero_major_actions_still_requires_states_and_no_action_rows(self):
        # Break caught: an action-free screen bypassing state coverage or accepting an invented action row.
        state = state_with_authorities(actions=())
        state["ux_coverage"] = [exact_ux_row(state, action_keys=())]
        self.assertEqual(validate_ux_coverage_bindings(state), [])
        state["ux_coverage"][0]["actions"] = [{"key": "submit", "cells": exact_action_cells(state)}]
        self.assertIn("screen_action_inventory_mismatch", self.codes(state))


if __name__ == "__main__":
    unittest.main()
