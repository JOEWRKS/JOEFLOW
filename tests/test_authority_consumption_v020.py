import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))

import authority_binding_v2 as binding  # noqa: E402
import grill_v2 as grill  # noqa: E402
import state_validation_v2 as validation  # noqa: E402
from tests.test_grill_binding_v020 import specialist_state  # noqa: E402
from tests.test_ux_binding_v020 import exact_ux_row, state_with_authorities  # noqa: E402
from tests.v020_support import foundation_state, materiality  # noqa: E402


CORE_AXES = (
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state",
    "data", "side_effect", "notification", "validation", "boundary",
    "persistence", "security", "privacy", "analytics", "acceptance",
)


def build_authority_consumption_graph(state):
    return getattr(binding, "build_authority_consumption_graph", lambda _: {})(state)


def authority_consumption_metrics(state):
    return getattr(
        binding,
        "authority_consumption_metrics",
        lambda _: {
            "orphan_material_authority": -1,
            "unconsumed_material_decision": -1,
            "requirement_acceptance_gaps": -1,
            "task_mapping_gaps": -1,
        },
    )(state)


def semantic_readiness_metrics(state):
    return getattr(validation, "semantic_readiness_metrics", lambda _: {})(state)


def requirement(requirement_id="REQ-001", *, status="CURRENT", classification="MATERIAL"):
    return {
        "id": requirement_id,
        "status": status,
        "statement": "Users can save their work.",
        "scope": "The primary workflow.",
        "ui_required": True,
        "materiality": materiality(classification=classification),
    }


def decision(decision_id="DEC-001", *, status="CURRENT", affects=None):
    return {
        "id": decision_id,
        "status": status,
        "statement": "Use the selected workflow.",
        "decision_type": "PRODUCT_POLICY",
        "resolution_mode": "USER_DECISION",
        "decision_authority": "USER_DECISION_REQUIRED",
        "source_unknown_refs": [],
        "evidence_refs": [],
        "materiality": materiality(classification="MATERIAL"),
        "affects": list(affects or []),
        "decided_by": "USER",
        "accepted_recommendation": None,
    }


def acceptance(acceptance_id="AC-001", *, status="CURRENT", requirement_refs=None):
    return {
        "id": acceptance_id,
        "status": status,
        "requirement_refs": list(requirement_refs or ["REQ-001"]),
        "assertion": "Saved work reloads.",
    }


def task(task_id="TASK-001", *, status="CURRENT", implements=None, acceptance_refs=None):
    return {
        "id": task_id,
        "status": status,
        "implements": list(implements or ["REQ-001"]),
        "acceptance_refs": list(acceptance_refs or ["AC-001"]),
    }


def current_rule(*, applies_to=None):
    return {
        "id": "RULE-001",
        "status": "CURRENT",
        "statement": "Saved changes persist.",
        "applies_to": list(applies_to or []),
    }


def covered_cell(state, record_id, pointer):
    return {
        "status": "COVERED",
        "authority_bindings": [binding.make_authority_binding(state, record_id, pointer)],
        "unknown_refs": [],
        "basis_bindings": [],
        "rationale": None,
    }


def add_exact_core_coverage(state):
    cells = {}
    for axis in CORE_AXES:
        if axis == "acceptance":
            source = ("AC-001", "/assertion")
        elif axis in {"goal", "happy_path"}:
            source = ("REQ-001", "/statement")
        else:
            source = ("RULE-001", "/statement")
        cells[axis] = covered_cell(state, *source)
    state["coverage"] = [{"feature_id": "REQ-001", "cells": cells}]


def core_state(*, with_mapping=True):
    state = foundation_state()
    state["objects"]["requirements"] = [requirement()]
    state["objects"]["rules"] = [current_rule()]
    state["objects"]["acceptance_criteria"] = [acceptance()]
    if with_mapping:
        state["objects"]["tasks"] = [task()]
    add_exact_core_coverage(state)
    return state


class AuthorityConsumptionGraphV020Test(unittest.TestCase):
    def test_decision_rule_and_exact_core_binding_form_a_transitive_sink_path(self):
        # Break caught: reverse RULE.applies_to edges or exact Core bindings failing to consume a material decision transitively.
        state = core_state()
        state["objects"]["decisions"] = [decision(affects=["REQ-001"])]
        state["objects"]["rules"][0]["applies_to"] = ["REQ-001"]

        graph = build_authority_consumption_graph(state)

        self.assertEqual(graph["DEC-001"], {"REQ-001"})
        self.assertIn("RULE-001", graph["REQ-001"])
        self.assertEqual(graph["RULE-001"], {"SINK:CORE"})
        self.assertEqual(authority_consumption_metrics(state)["unconsumed_material_decision"], 0)

    def test_requirement_acceptance_task_path_reaches_the_terminal_delivery_sink(self):
        # Break caught: AC/TASK relationship directions preventing a material requirement from reaching terminal delivery.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]
        state["objects"]["acceptance_criteria"] = [acceptance()]
        state["objects"]["tasks"] = [task()]

        graph = build_authority_consumption_graph(state)

        self.assertEqual(graph["REQ-001"], {"AC-001", "TASK-001"})
        self.assertEqual(graph["AC-001"], {"TASK-001"})
        self.assertEqual(graph["TASK-001"], {"SINK:TASK"})
        self.assertEqual(authority_consumption_metrics(state), {
            "orphan_material_authority": 0,
            "unconsumed_material_decision": 0,
            "requirement_acceptance_gaps": 0,
            "task_mapping_gaps": 0,
        })

    def test_unbound_reachable_rule_and_its_material_decision_are_orphans(self):
        # Break caught: only seed records being audited, leaving a material-reachable unbound Rule invisible.
        state = foundation_state()
        state["objects"]["decisions"] = [decision(affects=["RULE-001"])]
        state["objects"]["rules"] = [current_rule()]

        self.assertEqual(authority_consumption_metrics(state), {
            "orphan_material_authority": 2,
            "unconsumed_material_decision": 1,
            "requirement_acceptance_gaps": 0,
            "task_mapping_gaps": 0,
        })

    def test_historical_and_wrong_type_references_do_not_create_consumption_edges(self):
        # Break caught: historical targets or a REQ-* in FLOW.goal_refs satisfying current typed consumption.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]
        state["objects"]["acceptance_criteria"] = [acceptance(status="SUPERSEDED")]
        state["objects"]["tasks"] = [task(status="RETIRED")]
        state["objects"]["flows"] = [{
            "id": "FLOW-001", "status": "CURRENT", "goal_refs": ["REQ-001"],
            "entry": "Open editor.", "preconditions": [], "paths": [], "outcomes": [],
        }]

        graph = build_authority_consumption_graph(state)

        self.assertEqual(graph["REQ-001"], set())
        self.assertNotIn("AC-001", graph)
        self.assertNotIn("TASK-001", graph)
        self.assertEqual(authority_consumption_metrics(state), {
            "orphan_material_authority": 1,
            "unconsumed_material_decision": 0,
            "requirement_acceptance_gaps": 1,
            "task_mapping_gaps": 1,
        })

    def test_goal_user_and_task_terminal_exceptions_do_not_false_positive_as_orphans(self):
        # Break caught: explicit root/terminal exception types being counted as orphan material authority.
        state = foundation_state()
        state["objects"]["decisions"] = [decision(affects=["GOAL-001", "USR-001", "TASK-001"])]
        state["objects"]["goals"] = [{"id": "GOAL-001", "status": "CURRENT", "statement": "Ship."}]
        state["objects"]["users"] = [{
            "id": "USR-001", "status": "CURRENT", "description": "Primary user.", "actor_kind": "PERSON",
        }]
        state["objects"]["tasks"] = [task(implements=["REQ-999"], acceptance_refs=["AC-999"])]

        self.assertEqual(authority_consumption_metrics(state)["orphan_material_authority"], 0)
        self.assertEqual(authority_consumption_metrics(state)["unconsumed_material_decision"], 0)

    def test_validated_core_grill_and_ux_bindings_create_distinct_semantic_sinks(self):
        # Break caught: one exact coverage family being omitted or broad refs being treated as a semantic sink.
        core = core_state()
        core_graph = build_authority_consumption_graph(core)
        self.assertIn("SINK:CORE", core_graph["RULE-001"])

        grill = specialist_state()
        grill["grill_coverage"][0]["axes"]["registration"].update({
            "status": "ADDRESSED",
            "authority_bindings": [binding.make_authority_binding(grill, "RULE-900", "/statement")],
            "unknown_refs": [], "basis_bindings": [], "rationale": None,
        })
        self.assertIn("SINK:GRILL", build_authority_consumption_graph(grill)["RULE-900"])

        ux = state_with_authorities()
        ux["ux_coverage"] = [exact_ux_row(ux)]
        self.assertIn("SINK:UX", build_authority_consumption_graph(ux)["SCR-001"])

    def test_valid_known_ux_cell_remains_a_sink_when_row_inventory_is_incomplete(self):
        # Break caught: the sink collector skipping exact cells that the UX validator still checks in an inventory-gapped row.
        state = state_with_authorities(actions=())
        state["ux_coverage"] = [exact_ux_row(state, action_keys=())]
        del state["ux_coverage"][0]["states"]["expired"]

        graph = build_authority_consumption_graph(state)

        self.assertIn("SINK:UX", graph["SCR-001"])

    def test_valid_known_core_cell_remains_a_sink_when_row_inventory_is_incomplete(self):
        # Break caught: one Core inventory gap discarding exact sinks from every supplied known axis.
        state = core_state()
        del state["coverage"][0]["cells"]["analytics"]

        graph = build_authority_consumption_graph(state)

        self.assertIn("SINK:CORE", graph["RULE-001"])
        self.assertEqual(binding.product_binding_metrics(state)["core_coverage_gaps"], 1)

    def test_undefined_specialist_axis_cannot_create_a_grill_sink(self):
        # Break caught: a positive exact cell under an undefined pack axis becoming semantic delivery proof.
        state = specialist_state()
        state["grill_coverage"][0]["axes"]["undefined_axis"] = {
            "status": "ADDRESSED",
            "authority_bindings": [
                binding.make_authority_binding(state, "RULE-900", "/statement")
            ],
            "unknown_refs": [], "basis_bindings": [], "rationale": None,
        }

        graph = build_authority_consumption_graph(state)

        self.assertNotIn("SINK:GRILL", graph["RULE-900"])
        self.assertEqual(grill.grill_pack_metrics(state)["active_grill_pack_gaps"], 1)

    def test_surface_authority_refs_are_scope_trace_not_terminal_consumption(self):
        # Break caught: a SURF.authority_refs trace being mistaken for delivery proof.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]
        state["surface_manifest"]["records"] = [{
            "id": "SURF-001", "kind": "FEATURE_AREA", "name": "Save", "status": "IN_SCOPE",
            "materiality": materiality(classification="MATERIAL"), "evidence_refs": [],
            "authority_refs": ["REQ-001"], "unknown_refs": [], "decision_refs": [],
            "contradiction_refs": [], "rationale": None, "intent_classification": None,
        }]

        graph = build_authority_consumption_graph(state)

        self.assertEqual(graph["SURF-001"], {"REQ-001"})
        self.assertEqual(graph["REQ-001"], set())
        self.assertEqual(authority_consumption_metrics(state)["orphan_material_authority"], 1)


class RequirementDeliveryGateV020Test(unittest.TestCase):
    def test_missing_acceptance_and_task_each_count_the_requirement_once(self):
        # Break caught: raw missing-reference counts inflating one affected requirement into multiple gaps.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]

        self.assertEqual(authority_consumption_metrics(state), {
            "orphan_material_authority": 1,
            "unconsumed_material_decision": 0,
            "requirement_acceptance_gaps": 1,
            "task_mapping_gaps": 1,
        })

    def test_current_acceptance_without_task_only_leaves_the_task_mapping_gap(self):
        # Break caught: the presence of a valid AC incorrectly satisfying the separate task mapping gate.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]
        state["objects"]["acceptance_criteria"] = [acceptance()]

        metrics = authority_consumption_metrics(state)

        self.assertEqual(metrics["requirement_acceptance_gaps"], 0)
        self.assertEqual(metrics["task_mapping_gaps"], 1)

    def test_task_with_acceptance_for_another_requirement_is_not_a_valid_mapping(self):
        # Break caught: any current AC reference being accepted without belonging to the implemented requirement.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]
        state["objects"]["acceptance_criteria"] = [
            acceptance("AC-001"),
            acceptance("AC-002", requirement_refs=["REQ-002"]),
        ]
        state["objects"]["tasks"] = [task(acceptance_refs=["AC-002"])]

        metrics = authority_consumption_metrics(state)

        self.assertEqual(metrics["requirement_acceptance_gaps"], 0)
        self.assertEqual(metrics["task_mapping_gaps"], 1)

    def test_historical_acceptance_and_task_do_not_satisfy_delivery_gate(self):
        # Break caught: SUPERSEDED/RETIRED delivery records satisfying a CURRENT material requirement.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]
        state["objects"]["acceptance_criteria"] = [acceptance(status="SUPERSEDED")]
        state["objects"]["tasks"] = [task(status="RETIRED")]

        metrics = authority_consumption_metrics(state)

        self.assertEqual(metrics["requirement_acceptance_gaps"], 1)
        self.assertEqual(metrics["task_mapping_gaps"], 1)

    def test_valid_current_acceptance_and_task_mapping_clear_both_gates(self):
        # Break caught: a valid same-requirement CURRENT AC/TASK delivery chain being rejected.
        state = foundation_state()
        state["objects"]["requirements"] = [requirement()]
        state["objects"]["acceptance_criteria"] = [acceptance()]
        state["objects"]["tasks"] = [task()]

        metrics = authority_consumption_metrics(state)

        self.assertEqual(metrics["requirement_acceptance_gaps"], 0)
        self.assertEqual(metrics["task_mapping_gaps"], 0)


class SemanticReadinessV020Test(unittest.TestCase):
    def test_readiness_is_the_literal_present_non_approval_metric_contract(self):
        # Break caught: an implemented M1-M4 blocker or deferred count entering/leaving readiness silently.
        self.assertEqual(semantic_readiness_metrics(foundation_state()), {
            "open_material_surfaces": 0,
            "unbound_material_surfaces": 0,
            "unresolved_material_contradictions": 0,
            "stale_selected_authority": 0,
            "stale_consumed_evidence": 0,
            "discovery_baseline_gaps": 1,
            "unassessed_materiality": 0,
            "open_material_unknowns": 0,
            "blocked_material_unknowns": 0,
            "unresolved_unknown_provenance": 0,
            "invalid_resolution_authority": 0,
            "unauthorized_agent_decisions": 0,
            "missing_required_user_decisions": 0,
            "active_grill_pack_gaps": 0,
            "unresolved_pack_axes": 0,
            "umbrella_unknown_compression": 0,
            "pack_materiality_floor_violations": 0,
            "invalid_authority_binding": 0,
            "stale_authority_binding": 0,
            "coverage_without_authority": 0,
            "open_coverage_without_unknown": 0,
            "unjustified_na_without_basis": 0,
            "invalid_coverage_authority_type": 0,
            "core_coverage_gaps": 0,
            "specialist_binding_gaps": 0,
            "ux_coverage_gaps": 0,
            "screen_state_gaps": 0,
            "screen_action_inventory_gaps": 0,
            "ux_invalid_authority_binding": 0,
            "ux_stale_authority_binding": 0,
            "ux_open_without_unknown": 0,
            "ux_unjustified_na": 0,
            "orphan_material_authority": 0,
            "unconsumed_material_decision": 0,
            "requirement_acceptance_gaps": 0,
            "task_mapping_gaps": 0,
            "semantic_change_without_revision_increment": 0,
            "approved_record_missing_from_state": 0,
        })

    def test_evaluator_preserves_deferred_information_and_m3_closure_guard(self):
        # Break caught: readiness aggregation either blocking on valid deferral or implementing Closure before Task 6.
        state = foundation_state()
        deferred = {
            "id": "UNK-001", "status": "DEFERRED", "question": "Later?",
            "why_it_matters": "It affects later scope.", "required_authority_class": "INTENT",
            "question_category": "CORE_FLOW", "materiality": materiality(classification="MATERIAL"),
            "decision_authority": "USER_DECISION_REQUIRED", "affects": [], "blocks_unknown_refs": [],
            "origin": {"kind": "MANUAL", "surface_ref": None, "pack_id": None, "axis_id": None, "source_path": None},
            "response_mode": "OPEN_RESPONSE_REQUIRED", "options": [], "recommendation": None,
            "evidence_refs": [], "resolved_by": [], "resolution_mode": None, "resolution_summary": None,
            "deferral": {
                "reason": "The user accepted deferral.", "accepted_by": "user",
                "impact_review": {
                    "scope": "No current scope impact.", "rules": "No current rule impact.",
                    "flows": "No current flow impact.", "states": "No current state impact.",
                    "privacy": "No current privacy impact.", "money": "No current money impact.",
                    "security": "No current security impact.", "acceptance": "No current acceptance impact.",
                },
            },
            "blocked_reason": None,
        }
        state["objects"]["unknowns"] = [deferred]

        readiness = semantic_readiness_metrics(state)
        result = validation.evaluate_closure_v2(state)

        self.assertNotIn("deferred_unknowns", readiness)
        self.assertEqual(readiness["semantic_change_without_revision_increment"], 0)
        self.assertEqual(readiness["approved_record_missing_from_state"], 0)
        self.assertEqual(result["metrics"]["deferred_unknowns"], 1)
        self.assertEqual(result["metrics"]["semantic_closure_not_implemented"], 1)
        self.assertFalse(result["closed"])


if __name__ == "__main__":
    unittest.main()
