import copy
import json
import sys
import unittest
from pathlib import Path

try:
    from tests.v020_support import (
        decision_record,
        evidence_record,
        foundation_state,
        materiality,
        surface_record,
        unknown_record,
    )
except ModuleNotFoundError:
    from v020_support import (
        decision_record,
        evidence_record,
        foundation_state,
        materiality,
        surface_record,
        unknown_record,
    )


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
sys.path.insert(0, str(SCRIPTS))

from state_validation_v2 import evaluate_closure_v2, validate_state_v2


UNKNOWN_REQUIRED_FIELDS = {
    "id", "status", "question", "why_it_matters", "required_authority_class",
    "question_category", "materiality", "decision_authority", "affects",
    "blocks_unknown_refs", "origin", "response_mode", "options",
    "recommendation", "evidence_refs", "resolved_by", "resolution_mode",
    "resolution_summary", "deferral", "blocked_reason",
}

DECISION_REQUIRED_FIELDS = {
    "id", "status", "statement", "decision_type", "resolution_mode",
    "decision_authority", "source_unknown_refs", "evidence_refs", "materiality",
    "affects", "decided_by", "accepted_recommendation",
}


def accepted_recommendation():
    return {
        "recommended_option": "OPT-B",
        "alternatives_presented": ["OPT-A", "OPT-B"],
        "tradeoffs_presented": ["The alternative changes the product behavior."],
        "accepted_by": "user",
        "accepted_at": None,
    }


def recommendation(*, reasoning_refs=None):
    if reasoning_refs is None:
        reasoning_refs = ["EVD-001"]
    return {
        "recommended_option": "OPT-B",
        "reasoning_refs": list(reasoning_refs),
        "tradeoffs": ["The alternative changes the product behavior."],
        "confidence": "HIGH",
    }


class UnknownResolutionV020Test(unittest.TestCase):
    def errors(self, state):
        return validate_state_v2(state)

    def error_codes(self, state):
        return {error["code"] for error in self.errors(state)}

    def state_with_unknown(self, unknown):
        state = foundation_state()
        state["objects"]["unknowns"] = [copy.deepcopy(unknown)]
        return state

    def resolved_unknown(
        self,
        *,
        mode,
        authority,
        classification="MATERIAL",
        required_authority_class="INTENT",
    ):
        unknown = unknown_record(
            status="RESOLVED",
            classification=classification,
            decision_authority=authority,
            required_authority_class=required_authority_class,
        )
        unknown.update({
            "resolution_mode": mode,
            "resolution_summary": "Current authority resolves this product question.",
        })
        return unknown

    def state_with_linked_decision(
        self,
        *,
        mode="USER_DECISION",
        authority="USER_DECISION_REQUIRED",
        decided_by="USER",
        classification="MATERIAL",
        acceptance=None,
    ):
        unknown = self.resolved_unknown(
            mode=mode,
            authority=authority,
            classification=classification,
        )
        unknown["resolved_by"] = ["DEC-001"]
        state = self.state_with_unknown(unknown)
        state["objects"]["decisions"] = [decision_record(
            resolution_mode=mode,
            decision_authority=authority,
            decided_by=decided_by,
            classification=classification,
            accepted_recommendation=acceptance,
        )]
        return state

    def test_schema_and_runtime_require_every_canonical_unknown_and_decision_field(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["$defs"]["unknowns"]["required"]), UNKNOWN_REQUIRED_FIELDS)
        self.assertEqual(set(schema["$defs"]["decisions"]["required"]), DECISION_REQUIRED_FIELDS)

        for field in sorted(UNKNOWN_REQUIRED_FIELDS - {"id", "status"}):
            with self.subTest(record="unknown", field=field):
                unknown = unknown_record()
                del unknown[field]
                self.assertIn("invalid_unknown_contract", self.error_codes(self.state_with_unknown(unknown)))

        valid = self.state_with_linked_decision()
        for field in ("decided_by", "accepted_recommendation"):
            with self.subTest(record="decision", field=field):
                state = copy.deepcopy(valid)
                del state["objects"]["decisions"][0][field]
                self.assertIn("invalid_decision_provenance", self.error_codes(state))

    def test_origin_is_the_exact_five_key_shape_and_enforces_each_kind_locator(self):
        surface = surface_record(classification="NON_MATERIAL")
        valid_origins = [
            {
                "kind": "PRODUCT_SURFACE", "surface_ref": "SURF-001",
                "pack_id": None, "axis_id": None, "source_path": None,
            },
            {
                "kind": "GRILL_TOPOLOGY", "surface_ref": None,
                "pack_id": "GRILL-AUTH-1", "axis_id": None, "source_path": None,
            },
            {
                "kind": "GRILL_PACK_AXIS", "surface_ref": "SURF-001",
                "pack_id": "GRILL-AUTH-1", "axis_id": "login", "source_path": None,
            },
            {
                "kind": "MIGRATION_RECONCILIATION", "surface_ref": None,
                "pack_id": None, "axis_id": None,
                "source_path": "objects.unknowns[0]",
            },
            {
                "kind": "MANUAL", "surface_ref": None,
                "pack_id": None, "axis_id": None, "source_path": None,
            },
        ]
        for origin in valid_origins:
            with self.subTest(kind=origin["kind"]):
                state = self.state_with_unknown(unknown_record(origin=origin))
                if origin["surface_ref"]:
                    state["surface_manifest"]["records"] = [surface]
                self.assertNotIn("invalid_unknown_contract", self.error_codes(state))

        malformed = [
            {"kind": "MANUAL", "surface_ref": None, "pack_id": None, "axis_id": None},
            {
                "kind": "PRODUCT_SURFACE", "surface_ref": None,
                "pack_id": None, "axis_id": None, "source_path": None,
            },
            {
                "kind": "GRILL_TOPOLOGY", "surface_ref": None,
                "pack_id": None, "axis_id": None, "source_path": None,
            },
            {
                "kind": "GRILL_PACK_AXIS", "surface_ref": "SURF-999",
                "pack_id": "GRILL-AUTH-1", "axis_id": "login", "source_path": None,
            },
            {
                "kind": "GRILL_PACK_AXIS", "surface_ref": "SURF-001",
                "pack_id": "GRILL-AUTH-1", "axis_id": "currency", "source_path": None,
            },
            {
                "kind": "MIGRATION_RECONCILIATION", "surface_ref": None,
                "pack_id": None, "axis_id": None, "source_path": "TBD",
            },
            {
                "kind": "MANUAL", "surface_ref": None,
                "pack_id": None, "axis_id": None, "source_path": "objects.unknowns[0]",
            },
        ]
        for origin in malformed:
            with self.subTest(origin=origin):
                state = self.state_with_unknown(unknown_record(origin=origin))
                if origin.get("surface_ref") == "SURF-001":
                    state["surface_manifest"]["records"] = [surface]
                self.assertIn(
                    "invalid_unknown_contract",
                    self.error_codes(state),
                )

    def test_schema_and_runtime_use_the_same_specialist_pack_axis_inventory(self):
        expected_axes = {
            "GRILL-AUTH-1": {
                "registration", "verification", "login", "logout", "session_expiry",
                "session_renewal", "password_reset", "account_recovery", "revocation",
                "role_change", "provider_failure", "duplicate_identity", "account_linking",
            },
            "GRILL-MONEY-1": {
                "currency", "price_authority", "tax", "discount", "payment_failure",
                "duplicate_payment", "refund", "partial_refund", "cancellation",
                "chargeback", "settlement", "receipt",
            },
            "GRILL-FILE-UPLOAD-1": {
                "type", "size", "quota", "malware", "processing", "partial_failure",
                "resume", "retention", "deletion", "ownership", "download_permission",
            },
            "GRILL-ASYNC-1": {
                "pending", "polling", "timeout", "retry", "idempotency",
                "duplicate_execution", "late_completion", "partial_completion", "cancel",
                "reconciliation",
            },
            "GRILL-PERMISSION-1": {
                "role", "resource_ownership", "read", "write", "delete", "delegation",
                "revocation", "role_change_mid_flow", "stale_permission", "audit",
            },
            "GRILL-DESTRUCTIVE-ACTION-1": {
                "confirmation", "reason", "undo", "grace_period", "dependency_effects",
                "irreversible_boundary", "audit", "notification",
            },
        }
        surface = surface_record(classification="NON_MATERIAL")
        for pack_id, axes in expected_axes.items():
            with self.subTest(layer="runtime", pack_id=pack_id):
                origin = {
                    "kind": "GRILL_PACK_AXIS", "surface_ref": "SURF-001",
                    "pack_id": pack_id, "axis_id": sorted(axes)[0], "source_path": None,
                }
                state = self.state_with_unknown(unknown_record(origin=origin))
                state["surface_manifest"]["records"] = [surface]
                self.assertNotIn("invalid_unknown_contract", self.error_codes(state))

                invalid = copy.deepcopy(state)
                invalid_axis = "currency" if pack_id != "GRILL-MONEY-1" else "login"
                invalid["objects"]["unknowns"][0]["origin"]["axis_id"] = invalid_axis
                self.assertIn("invalid_unknown_contract", self.error_codes(invalid))

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        origin_cases = schema["$defs"]["unknown_origin"]["oneOf"]
        axis_case = next(
            (
                case for case in origin_cases
                if case.get("properties", {}).get("kind", {}).get("const") == "GRILL_PACK_AXIS"
            ),
            {},
        )
        schema_axes = {
            case["properties"]["pack_id"]["const"]: set(case["properties"]["axis_id"]["enum"])
            for case in axis_case.get("oneOf", [])
        }
        self.assertEqual(schema_axes, expected_axes)

    def test_schema_and_runtime_require_sources_for_current_decisions(self):
        state = self.state_with_linked_decision()
        state["objects"]["decisions"][0]["source_unknown_refs"] = []
        self.assertIn("invalid_decision_provenance", self.error_codes(state))

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        current_condition = next(
            (
                condition for condition in schema["$defs"]["decisions"]["allOf"]
                if condition.get("if", {}).get("properties", {}).get("status", {}).get("const") == "CURRENT"
            ),
            {},
        )
        min_items = (
            current_condition.get("then", {})
            .get("properties", {})
            .get("source_unknown_refs", {})
            .get("minItems")
        )
        self.assertEqual(min_items, 1)

    def test_schema_and_runtime_align_recommendation_and_acceptance_mode_conditions(self):
        stale_non_accepting = self.state_with_linked_decision()
        stale_non_accepting["objects"]["decisions"][0]["status"] = "STALE"
        stale_non_accepting["objects"]["decisions"][0]["accepted_recommendation"] = accepted_recommendation()
        self.assertIn("invalid_recommendation_acceptance", self.error_codes(stale_non_accepting))

        stale_accepting = self.state_with_linked_decision(
            mode="USER_ACCEPTED_RECOMMENDATION",
            authority="USER_CONFIRMATION",
            acceptance=None,
        )
        stale_accepting["objects"]["decisions"][0]["status"] = "STALE"
        stale_accepting["objects"]["unknowns"][0]["recommendation"] = recommendation()
        stale_accepting["evidence"] = [evidence_record(
            source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
        )]
        self.assertIn("invalid_recommendation_acceptance", self.error_codes(stale_accepting))

        stale_accepting["objects"]["decisions"][0]["accepted_recommendation"] = accepted_recommendation()
        self.assertNotIn("invalid_recommendation_acceptance", self.error_codes(stale_accepting))

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        recommendation_schema = schema["$defs"].get("unknown_recommendation")
        self.assertIsNotNone(recommendation_schema)
        self.assertEqual(
            set(recommendation_schema.get("required", [])),
            {"recommended_option", "reasoning_refs", "tradeoffs", "confidence"},
        )
        self.assertEqual(
            schema["$defs"]["unknowns"]["properties"]["recommendation"],
            {"oneOf": [{"$ref": "#/$defs/unknown_recommendation"}, {"type": "null"}]},
        )
        unknown_acceptance_condition = next(
            (
                condition for condition in schema["$defs"]["unknowns"]["allOf"]
                if condition.get("if", {}).get("properties", {}).get("resolution_mode", {}).get("const")
                == "USER_ACCEPTED_RECOMMENDATION"
            ),
            {},
        )
        self.assertEqual(
            unknown_acceptance_condition.get("then", {}).get("properties", {}).get("recommendation"),
            {"$ref": "#/$defs/unknown_recommendation"},
        )
        acceptance_condition = next(
            condition for condition in schema["$defs"]["decisions"]["allOf"]
            if condition.get("if", {}).get("properties", {}).get("resolution_mode", {}).get("const")
            == "USER_ACCEPTED_RECOMMENDATION"
        )
        self.assertEqual(
            acceptance_condition["then"]["properties"]["accepted_recommendation"],
            {"$ref": "#/$defs/accepted_recommendation"},
        )
        self.assertEqual(
            acceptance_condition["else"]["properties"]["accepted_recommendation"],
            {"type": "null"},
        )

    def test_historical_user_accepted_recommendation_requires_a_canonical_source_unknown(self):
        for source_refs in ([], None, ["UNK-999"]):
            with self.subTest(source_refs=source_refs):
                state = foundation_state()
                decision = decision_record(
                    status="STALE",
                    source_unknown_refs=[],
                    resolution_mode="USER_ACCEPTED_RECOMMENDATION",
                    decision_authority="USER_CONFIRMATION",
                    accepted_recommendation=accepted_recommendation(),
                )
                decision["source_unknown_refs"] = source_refs
                state["objects"]["decisions"] = [decision]

                try:
                    errors = self.errors(state)
                except Exception as exception:
                    self.fail(f"validation raised {type(exception).__name__}: {exception}")
                codes = {error["code"] for error in errors}
                self.assertIn("invalid_decision_provenance", codes)
                self.assertIn("invalid_recommendation_acceptance", codes)
                self.assertTrue(
                    all(set(error) == {"code", "message", "path"} for error in errors),
                    errors,
                )

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        acceptance_condition = next(
            condition for condition in schema["$defs"]["decisions"]["allOf"]
            if condition.get("if", {}).get("properties", {}).get("resolution_mode", {}).get("const")
            == "USER_ACCEPTED_RECOMMENDATION"
        )
        self.assertEqual(
            acceptance_condition.get("then", {}).get("properties", {}).get("source_unknown_refs"),
            {"minItems": 1},
        )

    def test_response_options_are_exact_unique_and_match_response_mode(self):
        invalid_unknowns = []
        one_option = unknown_record()
        one_option["options"] = one_option["options"][:1]
        invalid_unknowns.append(one_option)
        duplicate = unknown_record()
        duplicate["options"][1]["id"] = "OPT-A"
        invalid_unknowns.append(duplicate)
        malformed = unknown_record()
        malformed["options"][0]["consequences"] = []
        invalid_unknowns.append(malformed)
        open_response = unknown_record(response_mode="OPEN_RESPONSE_REQUIRED")
        open_response["options"] = [unknown_record()["options"][0]]
        invalid_unknowns.append(open_response)

        for unknown in invalid_unknowns:
            with self.subTest(unknown=unknown):
                self.assertIn("invalid_unknown_contract", self.error_codes(self.state_with_unknown(unknown)))

        self.assertEqual(
            self.error_codes(self.state_with_unknown(unknown_record(response_mode="OPEN_RESPONSE_REQUIRED"))),
            set(),
        )

    def test_recommendation_is_canonical_and_reasoning_refs_are_current_permitted_authority(self):
        evidence_backed = unknown_record(decision_authority="USER_CONFIRMATION")
        evidence_backed["recommendation"] = recommendation()
        state = self.state_with_unknown(evidence_backed)
        state["evidence"] = [evidence_record(
            source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
        )]
        self.assertEqual(self.error_codes(state), set())

        authority_backed = unknown_record(decision_authority="USER_CONFIRMATION")
        authority_backed["recommendation"] = recommendation(reasoning_refs=["REQ-001"])
        authority_state = self.state_with_unknown(authority_backed)
        authority_state["objects"]["requirements"] = [{
            "id": "REQ-001", "status": "CURRENT", "statement": "Use the alternative behavior.",
            "scope": "CORE", "ui_required": True, "materiality": materiality(classification="MATERIAL"),
        }]
        self.assertEqual(self.error_codes(authority_state), set())

        invalid_states = []
        missing = copy.deepcopy(state)
        missing["objects"]["unknowns"][0]["recommendation"]["reasoning_refs"] = ["EVD-999"]
        invalid_states.append(missing)
        stale = copy.deepcopy(state)
        stale["evidence"][0]["status"] = "STALE"
        invalid_states.append(stale)
        candidate_only = copy.deepcopy(state)
        candidate_only["evidence"][0]["source_kind"] = "DESIGN_ARTIFACT"
        invalid_states.append(candidate_only)
        stale_authority = copy.deepcopy(authority_state)
        stale_authority["objects"]["requirements"][0]["status"] = "STALE"
        invalid_states.append(stale_authority)

        for invalid in invalid_states:
            with self.subTest(invalid=invalid):
                self.assertIn("invalid_recommendation_reference", self.error_codes(invalid))

    def test_open_unknown_cannot_carry_resolution_fields(self):
        unknown = unknown_record()
        unknown.update({
            "resolution_mode": "USER_DECISION",
            "resolution_summary": "A decision was recorded.",
            "resolved_by": ["DEC-001"],
        })
        state = self.state_with_unknown(unknown)
        state["objects"]["decisions"] = [decision_record()]
        self.assertIn("invalid_unknown_contract", self.error_codes(state))

    def test_evidence_resolution_requires_current_closure_eligible_matching_evidence_and_no_decision(self):
        unknown = self.resolved_unknown(mode="EVIDENCE", authority="EVIDENCE_RESOLVABLE")
        unknown["evidence_refs"] = ["EVD-001"]
        state = self.state_with_unknown(unknown)
        state["evidence"] = [evidence_record(
            source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
        )]
        self.assertEqual(self.error_codes(state), set())

        for evidence in (
            evidence_record(source_kind="DESIGN_ARTIFACT", authority_classes=["INTENT"]),
            evidence_record(source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"], status="STALE"),
            evidence_record(source_kind="OBSERVED_IMPLEMENTATION", authority_classes=["FACTUAL"]),
        ):
            with self.subTest(evidence=evidence):
                candidate = copy.deepcopy(state)
                candidate["evidence"] = [evidence]
                self.assertIn("unresolved_unknown_provenance", self.error_codes(candidate))

        linked = copy.deepcopy(state)
        linked["objects"]["unknowns"][0]["resolved_by"] = ["DEC-001"]
        linked["objects"]["decisions"] = [decision_record(
            resolution_mode="USER_DECISION",
            decision_authority="USER_DECISION_REQUIRED",
        )]
        self.assertIn("unresolved_unknown_provenance", self.error_codes(linked))

    def test_external_constraint_resolution_requires_qualifying_constraint_evidence(self):
        unknown = self.resolved_unknown(
            mode="EXTERNAL_CONSTRAINT",
            authority="EXTERNAL_AUTHORITY_REQUIRED",
            required_authority_class="CONSTRAINT",
        )
        unknown["evidence_refs"] = ["EVD-001"]
        state = self.state_with_unknown(unknown)
        state["evidence"] = [evidence_record(
            source_kind="EXTERNAL_CONSTRAINT", authority_classes=["CONSTRAINT"],
        )]
        self.assertEqual(self.error_codes(state), set())

        state["evidence"][0] = evidence_record(
            source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"],
        )
        self.assertIn("unresolved_unknown_provenance", self.error_codes(state))

    def test_user_decision_resolution_requires_exactly_one_matching_current_decision(self):
        state = self.state_with_linked_decision()
        self.assertEqual(self.error_codes(state), set())

        for mutate in ("missing", "stale", "wrong_source", "extra"):
            with self.subTest(mutate=mutate):
                candidate = copy.deepcopy(state)
                if mutate == "missing":
                    candidate["objects"]["decisions"] = []
                elif mutate == "stale":
                    candidate["objects"]["decisions"][0]["status"] = "STALE"
                elif mutate == "wrong_source":
                    candidate["objects"]["decisions"][0]["source_unknown_refs"] = ["UNK-999"]
                else:
                    candidate["objects"]["unknowns"][0]["resolved_by"].append("DEC-002")
                    candidate["objects"]["decisions"].append(decision_record("DEC-002"))
                self.assertIn("unresolved_unknown_provenance", self.error_codes(candidate))

    def test_user_accepted_recommendation_requires_acceptance_provenance(self):
        state = self.state_with_linked_decision(
            mode="USER_ACCEPTED_RECOMMENDATION",
            authority="USER_CONFIRMATION",
            acceptance=accepted_recommendation(),
        )
        state["objects"]["unknowns"][0]["recommendation"] = recommendation()
        state["evidence"] = [evidence_record(
            source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
        )]
        self.assertEqual(self.error_codes(state), set())

        phantom = self.state_with_linked_decision(
            mode="USER_ACCEPTED_RECOMMENDATION",
            authority="USER_CONFIRMATION",
            acceptance=accepted_recommendation(),
        )
        self.assertIn("invalid_recommendation_acceptance", self.error_codes(phantom))

        for value in (
            None,
            {**accepted_recommendation(), "recommended_option": "OPT-Z"},
            {**accepted_recommendation(), "alternatives_presented": ["OPT-B"]},
            {**accepted_recommendation(), "tradeoffs_presented": []},
            {**accepted_recommendation(), "accepted_by": "agent"},
        ):
            with self.subTest(value=value):
                candidate = copy.deepcopy(state)
                candidate["objects"]["decisions"][0]["accepted_recommendation"] = value
                self.assertIn("invalid_recommendation_acceptance", self.error_codes(candidate))

        mismatched_recommendation = copy.deepcopy(state)
        mismatched_recommendation["objects"]["unknowns"][0]["recommendation"]["recommended_option"] = "OPT-A"
        self.assertIn(
            "invalid_recommendation_acceptance",
            self.error_codes(mismatched_recommendation),
        )

        mismatched_tradeoffs = copy.deepcopy(state)
        mismatched_tradeoffs["objects"]["unknowns"][0]["recommendation"]["tradeoffs"] = [
            "A different tradeoff was presented."
        ]
        self.assertIn(
            "invalid_recommendation_acceptance",
            self.error_codes(mismatched_tradeoffs),
        )

    def test_agent_non_material_resolution_requires_agent_and_non_material_source(self):
        valid = self.state_with_linked_decision(
            mode="AGENT_NON_MATERIAL_DEFAULT",
            authority="AGENT_AUTONOMOUS",
            decided_by="AGENT",
            classification="NON_MATERIAL",
        )
        self.assertEqual(self.error_codes(valid), set())

        wrong_actor = copy.deepcopy(valid)
        wrong_actor["objects"]["decisions"][0]["decided_by"] = "USER"
        self.assertIn("invalid_decision_provenance", self.error_codes(wrong_actor))

        material = self.state_with_linked_decision(
            mode="AGENT_NON_MATERIAL_DEFAULT",
            authority="AGENT_AUTONOMOUS",
            decided_by="AGENT",
            classification="MATERIAL",
        )
        self.assertIn("unauthorized_agent_decision", self.error_codes(material))
        self.assertEqual(
            evaluate_closure_v2(material)["metrics"]["unauthorized_agent_decisions"],
            1,
        )

    def test_migration_reconciliation_is_not_a_completed_resolution_mode(self):
        unknown = self.resolved_unknown(
            mode="MIGRATION_RECONCILIATION",
            authority="USER_DECISION_REQUIRED",
        )
        self.assertIn(
            "unresolved_unknown_provenance",
            self.error_codes(self.state_with_unknown(unknown)),
        )

    def test_deferred_unknown_requires_user_accepted_full_eight_axis_impact_review(self):
        unknown = unknown_record(status="DEFERRED")
        unknown["deferral"] = {
            "reason": "The user accepted deferral until the next product revision.",
            "accepted_by": "user",
            "impact_review": {
                "scope": "No current scope changes.",
                "rules": "No current rule changes.",
                "flows": "No current flow changes.",
                "states": "No current state changes.",
                "privacy": "No current privacy changes.",
                "money": "No current money changes.",
                "security": "No current security changes.",
                "acceptance": "Acceptance remains explicitly deferred.",
            },
        }
        self.assertEqual(self.error_codes(self.state_with_unknown(unknown)), set())

        invalids = [None, copy.deepcopy(unknown["deferral"]), copy.deepcopy(unknown["deferral"])]
        invalids[1]["accepted_by"] = "agent"
        del invalids[2]["impact_review"]["security"]
        for value in invalids:
            with self.subTest(value=value):
                candidate = copy.deepcopy(unknown)
                candidate["deferral"] = value
                self.assertIn("invalid_unknown_deferral", self.error_codes(self.state_with_unknown(candidate)))

    def test_blocked_unknown_requires_a_meaningful_reason(self):
        valid = unknown_record(status="BLOCKED")
        valid["blocked_reason"] = "The external policy authority is unavailable."
        self.assertEqual(self.error_codes(self.state_with_unknown(valid)), set())

        for value in (None, "", "TBD"):
            with self.subTest(value=value):
                invalid = copy.deepcopy(valid)
                invalid["blocked_reason"] = value
                self.assertIn("invalid_unknown_block", self.error_codes(self.state_with_unknown(invalid)))

    def test_reference_integrity_and_unknown_dependency_cycles_are_rejected(self):
        missing_affect = unknown_record()
        missing_affect["affects"] = ["REQ-999"]
        self.assertIn("invalid_unknown_contract", self.error_codes(self.state_with_unknown(missing_affect)))

        first = unknown_record("UNK-001")
        second = unknown_record("UNK-002")
        first["blocks_unknown_refs"] = ["UNK-002"]
        second["blocks_unknown_refs"] = ["UNK-001"]
        state = foundation_state()
        state["objects"]["unknowns"] = [first, second]
        self.assertIn("unknown_dependency_cycle", self.error_codes(state))

        first["blocks_unknown_refs"] = ["UNK-001"]
        state["objects"]["unknowns"] = [first, second]
        self.assertIn("invalid_unknown_contract", self.error_codes(state))

        second["status"] = "BLOCKED"
        second["blocked_reason"] = "An external authority is unavailable."
        first["blocks_unknown_refs"] = ["UNK-002"]
        state["objects"]["unknowns"] = [first, second]
        self.assertIn("invalid_unknown_contract", self.error_codes(state))

    def test_current_decision_requires_existing_matching_source_unknown_and_actor(self):
        valid = self.state_with_linked_decision()

        cases = []
        empty = copy.deepcopy(valid)
        empty["objects"]["decisions"][0]["source_unknown_refs"] = []
        cases.append((empty, "invalid_decision_provenance"))
        missing = copy.deepcopy(valid)
        missing["objects"]["decisions"][0]["source_unknown_refs"] = ["UNK-999"]
        cases.append((missing, "invalid_decision_provenance"))
        wrong_mode = copy.deepcopy(valid)
        wrong_mode["objects"]["decisions"][0]["resolution_mode"] = "USER_ACCEPTED_RECOMMENDATION"
        cases.append((wrong_mode, "invalid_unknown_resolution_authority"))
        wrong_authority = copy.deepcopy(valid)
        wrong_authority["objects"]["decisions"][0]["decision_authority"] = "USER_CONFIRMATION"
        cases.append((wrong_authority, "invalid_unknown_resolution_authority"))
        wrong_actor = copy.deepcopy(valid)
        wrong_actor["objects"]["decisions"][0]["decided_by"] = "AGENT"
        cases.append((wrong_actor, "invalid_decision_provenance"))

        for state, code in cases:
            with self.subTest(code=code, state=state):
                self.assertIn(code, self.error_codes(state))

    def test_malformed_cross_link_containers_return_findings_instead_of_crashing(self):
        valid = self.state_with_linked_decision()
        cases = []
        missing_sources = copy.deepcopy(valid)
        missing_sources["objects"]["decisions"][0]["source_unknown_refs"] = None
        cases.append(missing_sources)
        missing_resolution_links = copy.deepcopy(valid)
        missing_resolution_links["objects"]["unknowns"][0]["resolved_by"] = None
        cases.append(missing_resolution_links)
        malformed_response_mode = self.state_with_unknown(unknown_record())
        malformed_response_mode["objects"]["unknowns"][0]["response_mode"] = []
        cases.append(malformed_response_mode)
        malformed_resolution_mode = self.state_with_unknown(self.resolved_unknown(
            mode="USER_DECISION", authority="USER_DECISION_REQUIRED",
        ))
        malformed_resolution_mode["objects"]["unknowns"][0]["resolution_mode"] = {}
        cases.append(malformed_resolution_mode)
        malformed_recommendation = self.state_with_unknown(unknown_record())
        malformed_recommendation["objects"]["unknowns"][0]["recommendation"] = recommendation()
        malformed_recommendation["objects"]["unknowns"][0]["recommendation"]["confidence"] = []
        cases.append(malformed_recommendation)

        for state in cases:
            with self.subTest(state=state):
                try:
                    errors = self.errors(state)
                except Exception as exception:
                    self.fail(f"validation raised {type(exception).__name__}: {exception}")
                self.assertTrue(errors)
                self.assertTrue(
                    all(set(error) == {"code", "message", "path"} for error in errors),
                    errors,
                )

    def test_external_constraint_decision_requires_external_actor_and_constraint_evidence(self):
        unknown = self.resolved_unknown(
            mode="EXTERNAL_CONSTRAINT",
            authority="EXTERNAL_AUTHORITY_REQUIRED",
            required_authority_class="CONSTRAINT",
        )
        unknown["resolved_by"] = ["DEC-001"]
        unknown["evidence_refs"] = ["EVD-001"]
        state = self.state_with_unknown(unknown)
        decision = decision_record(
            resolution_mode="EXTERNAL_CONSTRAINT",
            decision_authority="EXTERNAL_AUTHORITY_REQUIRED",
            decided_by="EXTERNAL_AUTHORITY",
        )
        decision["evidence_refs"] = ["EVD-001"]
        state["objects"]["decisions"] = [decision]
        state["evidence"] = [evidence_record(
            source_kind="EXTERNAL_CONSTRAINT", authority_classes=["CONSTRAINT"],
        )]
        self.assertEqual(self.error_codes(state), set())

        for mutate in ("stale", "source", "mode", "authority", "actor", "evidence"):
            with self.subTest(mutate=mutate):
                candidate = copy.deepcopy(state)
                if mutate == "stale":
                    candidate["objects"]["decisions"][0]["status"] = "STALE"
                elif mutate == "source":
                    candidate["objects"]["decisions"][0]["source_unknown_refs"] = ["UNK-999"]
                elif mutate == "mode":
                    candidate["objects"]["decisions"][0]["resolution_mode"] = "USER_DECISION"
                elif mutate == "authority":
                    candidate["objects"]["decisions"][0]["decision_authority"] = "USER_DECISION_REQUIRED"
                elif mutate == "actor":
                    candidate["objects"]["decisions"][0]["decided_by"] = "USER"
                else:
                    candidate["objects"]["decisions"][0]["evidence_refs"] = []
                self.assertIn("unresolved_unknown_provenance", self.error_codes(candidate))

    def test_evidence_and_migration_modes_are_invalid_for_current_decisions(self):
        for mode in ("EVIDENCE", "MIGRATION_RECONCILIATION"):
            with self.subTest(mode=mode):
                state = self.state_with_linked_decision()
                state["objects"]["decisions"][0]["resolution_mode"] = mode
                self.assertIn("invalid_decision_provenance", self.error_codes(state))

    def test_unknown_metrics_distinguish_open_blocked_and_deferred_records(self):
        open_unknown = unknown_record("UNK-001")
        blocked = unknown_record("UNK-002", status="BLOCKED")
        blocked["blocked_reason"] = "The external authority is unavailable."
        deferred = unknown_record("UNK-003", status="DEFERRED")
        deferred["deferral"] = {
            "reason": "The user accepted deferral until the next revision.",
            "accepted_by": "user",
            "impact_review": {
                "scope": "No current scope changes.", "rules": "No current rule changes.",
                "flows": "No current flow changes.", "states": "No current state changes.",
                "privacy": "No current privacy changes.", "money": "No current money changes.",
                "security": "No current security changes.",
                "acceptance": "Acceptance remains explicitly deferred.",
            },
        }
        state = foundation_state()
        state["objects"]["unknowns"] = [open_unknown, blocked, deferred]

        metrics = evaluate_closure_v2(state)["metrics"]
        for field in (
            "open_material_unknowns", "blocked_material_unknowns", "deferred_unknowns",
            "missing_required_user_decisions", "unresolved_unknown_provenance",
            "invalid_resolution_authority", "unauthorized_agent_decisions",
        ):
            self.assertIn(field, metrics)
        self.assertEqual(metrics["semantic_closure_not_implemented"], 1)
        self.assertEqual(metrics["open_material_unknowns"], 1)
        self.assertEqual(metrics["blocked_material_unknowns"], 1)
        self.assertEqual(metrics["deferred_unknowns"], 1)
        self.assertEqual(metrics["missing_required_user_decisions"], 1)
        self.assertEqual(metrics["unresolved_unknown_provenance"], 0)
        self.assertEqual(metrics["invalid_resolution_authority"], 0)
        self.assertEqual(metrics["unauthorized_agent_decisions"], 0)


if __name__ == "__main__":
    unittest.main()
