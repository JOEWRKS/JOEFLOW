import copy
import json
import sys
import unittest
from pathlib import Path

try:
    from tests.v020_support import (
        decision_record,
        evidence_record,
        evidence_with_grill_basis,
        foundation_state,
        materiality,
        unknown_record,
    )
except ModuleNotFoundError:
    from v020_support import (
        decision_record,
        evidence_record,
        evidence_with_grill_basis,
        foundation_state,
        materiality,
        unknown_record,
    )


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
sys.path.insert(0, str(SCRIPTS))

import grill_v2
from state_validation_v2 import evaluate_closure_v2, validate_state_v2


def recommendation(*, confidence="HIGH", reasoning_refs=None):
    return {
        "recommended_option": "OPT-B",
        "reasoning_refs": list(reasoning_refs or ["EVD-001"]),
        "tradeoffs": [
            "The alternative has a simpler recovery path.",
            "It requires slightly more state handling.",
        ],
        "confidence": confidence,
    }


def accepted_recommendation(*, alternatives=None, accepted_by="user"):
    return {
        "recommended_option": "OPT-B",
        "alternatives_presented": list(alternatives or ["OPT-A", "OPT-B"]),
        "tradeoffs_presented": [
            "The alternative has a simpler recovery path.",
            "It requires slightly more state handling.",
        ],
        "accepted_by": accepted_by,
        "accepted_at": None,
    }


def intent_evidence(*, status="CURRENT", source_kind="USER_CONFIRMED_INTENT"):
    return evidence_record(
        source_kind=source_kind,
        authority_classes=["INTENT"],
        status=status,
        claim="The recorded product intent supports the recommendation.",
    )


def high_risk_materiality():
    value = materiality(classification="MATERIAL")
    value["risk_flags"]["security"] = True
    return value


class AutonomyPolicyV020Test(unittest.TestCase):
    def setUp(self):
        self.derive = getattr(
            grill_v2,
            "derive_decision_authority",
            lambda unknown, *, evidence_index: "NOT_IMPLEMENTED",
        )
        self.confirmation_ready = getattr(
            grill_v2,
            "recommendation_is_confirmation_ready",
            lambda unknown: False,
        )

    @staticmethod
    def error_codes(state):
        return {error["code"] for error in validate_state_v2(state)}

    @staticmethod
    def state_with_unknown(unknown, *, evidence=None, decision=None):
        state = foundation_state()
        state["objects"]["unknowns"] = [copy.deepcopy(unknown)]
        state["evidence"] = evidence_with_grill_basis(*copy.deepcopy(evidence or []))
        if decision is not None:
            state["objects"]["decisions"] = [copy.deepcopy(decision)]
        return state

    def test_derives_each_authority_branch_in_frozen_order(self):
        evidence_backed = unknown_record(
            classification="NON_MATERIAL",
            decision_authority="EVIDENCE_RESOLVABLE",
            required_authority_class="BEHAVIORAL",
        )
        evidence_backed["materiality"]["risk_flags"]["security"] = True
        evidence_backed["materiality"]["classification"] = "MATERIAL"
        evidence_backed["evidence_refs"] = ["EVD-001"]
        evidence_backed["recommendation"] = recommendation()
        evidence_index = {"EVD-001": evidence_record(
            source_kind="OBSERVED_RUNTIME",
            authority_classes=["BEHAVIORAL"],
        )}
        self.assertEqual(
            self.derive(evidence_backed, evidence_index=evidence_index),
            "EVIDENCE_RESOLVABLE",
        )

        for authority_class in ("FACTUAL", "CONSTRAINT", "BEHAVIORAL"):
            with self.subTest(branch="external", authority_class=authority_class):
                unknown = unknown_record(required_authority_class=authority_class)
                self.assertEqual(
                    self.derive(unknown, evidence_index={}),
                    "EXTERNAL_AUTHORITY_REQUIRED",
                )

        non_material_invisible = unknown_record(
            classification="NON_MATERIAL",
            decision_authority="AGENT_AUTONOMOUS",
        )
        self.assertEqual(
            self.derive(non_material_invisible, evidence_index={}),
            "AGENT_AUTONOMOUS",
        )

        non_material_visible_ready = unknown_record(
            classification="NON_MATERIAL",
            decision_authority="AGENT_AUTONOMOUS",
        )
        non_material_visible_ready["materiality"]["user_visible"] = True
        non_material_visible_ready["recommendation"] = recommendation()
        self.assertEqual(
            self.derive(non_material_visible_ready, evidence_index={}),
            "AGENT_AUTONOMOUS",
        )

        non_material_visible_no_recommendation = copy.deepcopy(non_material_visible_ready)
        non_material_visible_no_recommendation["recommendation"] = None
        self.assertEqual(
            self.derive(non_material_visible_no_recommendation, evidence_index={}),
            "AGENT_AUTONOMOUS",
        )

        high_risk = unknown_record()
        high_risk["materiality"] = high_risk_materiality()
        high_risk["recommendation"] = recommendation()
        self.assertEqual(
            self.derive(high_risk, evidence_index={}),
            "USER_DECISION_REQUIRED",
        )

        material_ready = unknown_record(decision_authority="USER_CONFIRMATION")
        material_ready["recommendation"] = recommendation()
        self.assertEqual(
            self.derive(material_ready, evidence_index={}),
            "USER_CONFIRMATION",
        )

        material_no_recommendation = unknown_record()
        self.assertEqual(
            self.derive(material_no_recommendation, evidence_index={}),
            "USER_DECISION_REQUIRED",
        )

    def test_confirmation_ready_requires_mutually_exclusive_high_confidence_recommendation(self):
        ready = unknown_record(decision_authority="USER_CONFIRMATION")
        ready["recommendation"] = recommendation()
        self.assertTrue(self.confirmation_ready(ready))

        low_confidence = copy.deepcopy(ready)
        low_confidence["recommendation"]["confidence"] = "MEDIUM"
        self.assertFalse(self.confirmation_ready(low_confidence))

        open_response = copy.deepcopy(ready)
        open_response["response_mode"] = "OPEN_RESPONSE_REQUIRED"
        open_response["options"] = []
        self.assertFalse(self.confirmation_ready(open_response))

        one_option = copy.deepcopy(ready)
        one_option["options"] = one_option["options"][:1]
        self.assertFalse(self.confirmation_ready(one_option))

    def test_schema_requires_confirmation_ready_recommendation_for_user_confirmation(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        ready_schema = schema["$defs"].get("confirmation_ready_recommendation")
        self.assertEqual(
            ready_schema,
            {
                "allOf": [
                    {"$ref": "#/$defs/unknown_recommendation"},
                    {"properties": {"confidence": {"const": "HIGH"}}},
                ]
            },
        )
        authority_condition = next(
            (
                condition
                for condition in schema["$defs"]["unknowns"]["allOf"]
                if condition.get("then", {}).get("properties", {}).get("recommendation")
                == {"$ref": "#/$defs/confirmation_ready_recommendation"}
            ),
            None,
        )
        self.assertIsNotNone(authority_condition)
        self.assertEqual(
            authority_condition["if"],
            {
                "properties": {
                    "status": {"enum": ["OPEN", "BLOCKED"]},
                    "decision_authority": {"const": "USER_CONFIRMATION"},
                },
                "required": ["status", "decision_authority"],
            },
        )
        self.assertEqual(
            authority_condition["then"]["properties"],
            {
                "response_mode": {"const": "MUTUALLY_EXCLUSIVE"},
                "options": {"minItems": 2},
                "recommendation": {"$ref": "#/$defs/confirmation_ready_recommendation"},
            },
        )

    def test_resolved_and_deferred_recommendations_follow_historical_runtime_contracts(self):
        resolved = unknown_record(
            status="RESOLVED",
            decision_authority="USER_CONFIRMATION",
        )
        low_confidence_recommendation = recommendation(confidence="LOW")
        resolved.update({
            "recommendation": low_confidence_recommendation,
            "resolved_by": ["DEC-001"],
            "resolution_mode": "USER_ACCEPTED_RECOMMENDATION",
            "resolution_summary": "The user accepted the historical recommendation.",
        })
        decision = decision_record(
            resolution_mode="USER_ACCEPTED_RECOMMENDATION",
            decision_authority="USER_CONFIRMATION",
            accepted_recommendation=accepted_recommendation(),
        )
        resolved_state = self.state_with_unknown(
            resolved,
            evidence=[intent_evidence()],
            decision=decision,
        )
        self.assertEqual(self.error_codes(resolved_state), set())

        deferred = unknown_record(
            status="DEFERRED",
            decision_authority="USER_CONFIRMATION",
        )
        deferred["deferral"] = {
            "reason": "The user accepted deferral to a later product revision.",
            "accepted_by": "user",
            "impact_review": {
                "scope": "No current scope impact.",
                "rules": "No current rule impact.",
                "flows": "No current flow impact.",
                "states": "No current state impact.",
                "privacy": "No current privacy impact.",
                "money": "No current money impact.",
                "security": "No current security impact.",
                "acceptance": "No current acceptance impact.",
            },
        }
        self.assertEqual(self.error_codes(self.state_with_unknown(deferred)), set())

    def test_rejects_malformed_or_unproven_recommendations(self):
        base = unknown_record(decision_authority="USER_CONFIRMATION")
        base["recommendation"] = recommendation()
        state = self.state_with_unknown(base, evidence=[intent_evidence()])
        self.assertNotIn("invalid_recommendation_reference", self.error_codes(state))

        malformed_cases = []
        nonexistent_option = copy.deepcopy(state)
        nonexistent_option["objects"]["unknowns"][0]["recommendation"]["recommended_option"] = "OPT-Z"
        malformed_cases.append(nonexistent_option)
        empty_reasoning = copy.deepcopy(state)
        empty_reasoning["objects"]["unknowns"][0]["recommendation"]["reasoning_refs"] = []
        malformed_cases.append(empty_reasoning)
        empty_tradeoffs = copy.deepcopy(state)
        empty_tradeoffs["objects"]["unknowns"][0]["recommendation"]["tradeoffs"] = []
        malformed_cases.append(empty_tradeoffs)
        invalid_confidence = copy.deepcopy(state)
        invalid_confidence["objects"]["unknowns"][0]["recommendation"]["confidence"] = "CERTAIN"
        malformed_cases.append(invalid_confidence)
        for candidate in malformed_cases:
            with self.subTest(candidate=candidate["objects"]["unknowns"][0]["recommendation"]):
                self.assertIn("invalid_unknown_contract", self.error_codes(candidate))

        stale = copy.deepcopy(state)
        stale["evidence"][0]["status"] = "STALE"
        self.assertIn("invalid_recommendation_reference", self.error_codes(stale))

        candidate_only = copy.deepcopy(state)
        candidate_only["evidence"] = [intent_evidence(source_kind="DESIGN_ARTIFACT")]
        self.assertIn("invalid_recommendation_reference", self.error_codes(candidate_only))

    def test_user_acceptance_must_reproduce_options_and_cannot_be_self_marked_by_agent(self):
        unknown = unknown_record(
            status="RESOLVED",
            decision_authority="USER_CONFIRMATION",
        )
        unknown.update({
            "recommendation": recommendation(),
            "resolved_by": ["DEC-001"],
            "resolution_mode": "USER_ACCEPTED_RECOMMENDATION",
            "resolution_summary": "The user accepted the recommendation.",
        })
        decision = decision_record(
            resolution_mode="USER_ACCEPTED_RECOMMENDATION",
            decision_authority="USER_CONFIRMATION",
            accepted_recommendation=accepted_recommendation(),
        )
        valid = self.state_with_unknown(
            unknown,
            evidence=[intent_evidence()],
            decision=decision,
        )
        self.assertEqual(self.error_codes(valid), set())

        incomplete_options = copy.deepcopy(valid)
        incomplete_options["objects"]["decisions"][0]["accepted_recommendation"][
            "alternatives_presented"
        ] = ["OPT-B"]
        self.assertIn(
            "invalid_recommendation_acceptance",
            self.error_codes(incomplete_options),
        )

        agent_decider = copy.deepcopy(valid)
        agent_decider["objects"]["decisions"][0]["decided_by"] = "AGENT"
        self.assertIn("invalid_decision_provenance", self.error_codes(agent_decider))

        agent_acceptance = copy.deepcopy(valid)
        agent_acceptance["objects"]["decisions"][0]["accepted_recommendation"][
            "accepted_by"
        ] = "agent"
        self.assertIn(
            "invalid_recommendation_acceptance",
            self.error_codes(agent_acceptance),
        )

    def test_declared_authority_must_equal_strict_recomputation_after_each_input_change(self):
        material = unknown_record()
        baseline = self.state_with_unknown(material)
        self.assertNotIn("invalid_decision_authority_derivation", self.error_codes(baseline))

        changed_materiality = copy.deepcopy(baseline)
        changed_materiality["objects"]["unknowns"][0]["materiality"] = materiality(
            classification="NON_MATERIAL"
        )
        self.assertIn(
            "invalid_decision_authority_derivation",
            self.error_codes(changed_materiality),
        )
        changed_materiality["objects"]["unknowns"][0]["decision_authority"] = "AGENT_AUTONOMOUS"
        self.assertNotIn(
            "invalid_decision_authority_derivation",
            self.error_codes(changed_materiality),
        )

        changed_evidence = copy.deepcopy(baseline)
        changed_evidence["evidence"] = [intent_evidence()]
        changed_evidence["objects"]["unknowns"][0]["evidence_refs"] = ["EVD-001"]
        self.assertIn(
            "invalid_decision_authority_derivation",
            self.error_codes(changed_evidence),
        )
        changed_evidence["objects"]["unknowns"][0]["decision_authority"] = "EVIDENCE_RESOLVABLE"
        self.assertNotIn(
            "invalid_decision_authority_derivation",
            self.error_codes(changed_evidence),
        )

        changed_recommendation = copy.deepcopy(baseline)
        changed_recommendation["evidence"] = [intent_evidence()]
        changed_recommendation["objects"]["unknowns"][0]["recommendation"] = recommendation()
        self.assertIn(
            "invalid_decision_authority_derivation",
            self.error_codes(changed_recommendation),
        )
        changed_recommendation["objects"]["unknowns"][0]["decision_authority"] = "USER_CONFIRMATION"
        self.assertNotIn(
            "invalid_decision_authority_derivation",
            self.error_codes(changed_recommendation),
        )

    def test_live_derivation_applies_to_open_and_blocked_but_not_resolved_or_deferred(self):
        open_unknown = unknown_record(
            classification="NON_MATERIAL",
            decision_authority="USER_DECISION_REQUIRED",
        )
        self.assertIn(
            "invalid_decision_authority_derivation",
            self.error_codes(self.state_with_unknown(open_unknown)),
        )

        blocked_unknown = copy.deepcopy(open_unknown)
        blocked_unknown["status"] = "BLOCKED"
        blocked_unknown["blocked_reason"] = "The required product authority is unavailable."
        self.assertIn(
            "invalid_decision_authority_derivation",
            self.error_codes(self.state_with_unknown(blocked_unknown)),
        )

        resolved_unknown = unknown_record(
            status="RESOLVED",
            classification="NON_MATERIAL",
            decision_authority="USER_DECISION_REQUIRED",
        )
        resolved_unknown.update({
            "resolved_by": ["DEC-001"],
            "resolution_mode": "USER_DECISION",
            "resolution_summary": "The user made the historical product decision.",
        })
        historical_decision = decision_record(classification="NON_MATERIAL")
        resolved_state = self.state_with_unknown(
            resolved_unknown,
            decision=historical_decision,
        )
        self.assertNotIn(
            "invalid_decision_authority_derivation",
            self.error_codes(resolved_state),
        )

        deferred_unknown = unknown_record(
            status="DEFERRED",
            classification="NON_MATERIAL",
            decision_authority="USER_DECISION_REQUIRED",
        )
        deferred_unknown["deferral"] = {
            "reason": "The user accepted deferral to a later product revision.",
            "accepted_by": "user",
            "impact_review": {
                "scope": "No current scope impact.",
                "rules": "No current rule impact.",
                "flows": "No current flow impact.",
                "states": "No current state impact.",
                "privacy": "No current privacy impact.",
                "money": "No current money impact.",
                "security": "No current security impact.",
                "acceptance": "No current acceptance impact.",
            },
        }
        self.assertNotIn(
            "invalid_decision_authority_derivation",
            self.error_codes(self.state_with_unknown(deferred_unknown)),
        )

    def test_high_risk_and_material_agent_defaults_are_rejected(self):
        high_risk = unknown_record(decision_authority="AGENT_AUTONOMOUS")
        high_risk["materiality"] = high_risk_materiality()
        high_risk_state = self.state_with_unknown(high_risk)
        self.assertIn(
            "invalid_decision_authority_derivation",
            self.error_codes(high_risk_state),
        )
        self.assertEqual(
            evaluate_closure_v2(high_risk_state)["metrics"]["invalid_resolution_authority"],
            1,
        )

        material_unknown = unknown_record(
            status="RESOLVED",
            decision_authority="AGENT_AUTONOMOUS",
        )
        material_unknown.update({
            "resolved_by": ["DEC-001"],
            "resolution_mode": "AGENT_NON_MATERIAL_DEFAULT",
            "resolution_summary": "The agent selected a product default.",
        })
        material_decision = decision_record(
            resolution_mode="AGENT_NON_MATERIAL_DEFAULT",
            decision_authority="AGENT_AUTONOMOUS",
            decided_by="AGENT",
        )
        material_state = self.state_with_unknown(material_unknown, decision=material_decision)
        codes = self.error_codes(material_state)
        self.assertIn("unauthorized_agent_decision", codes)

    def test_missing_required_user_decisions_uses_derived_authority_not_stored_label(self):
        state = self.state_with_unknown(unknown_record(
            status="OPEN",
            classification="MATERIAL",
            decision_authority="AGENT_AUTONOMOUS",
        ))

        result = evaluate_closure_v2(state)

        self.assertIn(
            "invalid_decision_authority_derivation",
            {error["code"] for error in result["errors"]},
        )
        self.assertEqual(result["metrics"]["missing_required_user_decisions"], 1)

    def test_resolution_authority_metric_counts_unauthorized_agent_conflicts_once_per_record(self):
        unknown = unknown_record(
            status="RESOLVED",
            decision_authority="AGENT_AUTONOMOUS",
        )
        unknown.update({
            "resolved_by": ["DEC-001"],
            "resolution_mode": "AGENT_NON_MATERIAL_DEFAULT",
            "resolution_summary": "The agent selected a product default.",
        })
        decision = decision_record(
            resolution_mode="AGENT_NON_MATERIAL_DEFAULT",
            decision_authority="AGENT_AUTONOMOUS",
            decided_by="AGENT",
        )
        unauthorized_only = self.state_with_unknown(unknown, decision=decision)
        metrics = evaluate_closure_v2(unauthorized_only)["metrics"]
        self.assertEqual(metrics["invalid_resolution_authority"], 2)
        self.assertEqual(metrics["unauthorized_agent_decisions"], 1)

        overlapping_findings = copy.deepcopy(unauthorized_only)
        overlapping_findings["objects"]["unknowns"][0]["decision_authority"] = (
            "USER_DECISION_REQUIRED"
        )
        overlapping_findings["objects"]["decisions"][0]["decision_authority"] = (
            "USER_DECISION_REQUIRED"
        )
        overlapping_metrics = evaluate_closure_v2(overlapping_findings)["metrics"]
        self.assertEqual(overlapping_metrics["invalid_resolution_authority"], 2)
        self.assertEqual(overlapping_metrics["unauthorized_agent_decisions"], 1)


if __name__ == "__main__":
    unittest.main()
