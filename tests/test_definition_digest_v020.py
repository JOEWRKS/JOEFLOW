import copy
import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))

try:
    import approval_v2 as approval
except ModuleNotFoundError:
    approval = None

from tests.v020_support import (  # noqa: E402
    establish_current_baseline,
    evidence_record,
    evidence_with_grill_basis,
    foundation_state,
    materiality,
    surface_record,
    unknown_record,
)


def api(name):
    if approval is None or not hasattr(approval, name):
        raise AssertionError(f"missing Task 5 API: {name}")
    return getattr(approval, name)


def current_decision(decision_id="DEC-001", *, evidence_refs=None, status="CURRENT"):
    return {
        "id": decision_id,
        "status": status,
        "statement": "Use the selected submission policy.",
        "decision_type": "PRODUCT_POLICY",
        "resolution_mode": "EVIDENCE",
        "decision_authority": "EVIDENCE_RESOLVABLE",
        "source_unknown_refs": [],
        "evidence_refs": list(evidence_refs or []),
        "materiality": materiality(),
        "affects": [],
        "decided_by": "AGENT",
        "accepted_recommendation": None,
    }


class DefinitionDigestV020Test(unittest.TestCase):
    def test_consumed_evidence_boundary_uses_every_frozen_current_authority_source(self):
        # Break caught: one M4 authority family silently failing to commit the EVD record it consumes.
        state = foundation_state()
        records = [
            evidence_record(f"EVD-{number:03d}", source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"])
            for number in range(1, 10)
        ]
        state["evidence"] = evidence_with_grill_basis(*records)
        state["objects"]["decisions"] = [current_decision(evidence_refs=["EVD-001"])]
        resolved = unknown_record("UNK-001", status="RESOLVED", classification="NON_MATERIAL", decision_authority="EVIDENCE_RESOLVABLE")
        resolved.update({
            "evidence_refs": ["EVD-002"],
            "resolution_mode": "EVIDENCE",
            "resolution_summary": "The current source resolves the question.",
        })
        ignored = unknown_record("UNK-002", status="RESOLVED", classification="NON_MATERIAL")
        ignored.update({
            "evidence_refs": ["EVD-009"],
            "resolution_mode": "USER_DECISION",
            "resolution_summary": "The user resolved the question.",
        })
        state["objects"]["unknowns"] = [resolved, ignored]
        surface = surface_record(classification="NON_MATERIAL")
        surface["evidence_refs"] = ["EVD-003"]
        historical_surface = surface_record("SURF-002", status="RETIRED", classification="NON_MATERIAL")
        historical_surface["evidence_refs"] = ["EVD-009"]
        state["surface_manifest"]["records"] = [surface, historical_surface]
        state["contradictions"] = [{
            "id": "CON-001", "status": "RESOLVED",
            "claim_a_refs": ["EVD-004"], "claim_b_refs": ["EVD-005"],
            "scope_refs": ["SURF-001"], "materiality": materiality(),
            "resolution": "The selected source controls.", "resolved_by": [],
            "selected_authority_refs": ["EVD-006"],
        }]
        state["coverage"] = [{
            "feature_id": "REQ-999",
            "cells": {"actor": {
                "status": "N/A", "authority_bindings": [], "unknown_refs": [],
                "basis_bindings": [{"record_id": "EVD-007", "pointer": "/claim", "value_sha256": "0" * 64}],
                "rationale": "The evidence establishes non-applicability.",
            }},
        }]
        state["ux_coverage"] = [{
            "screen_id": "SCR-999", "states": {"default": {
                "status": "N/A", "authority_bindings": [], "unknown_refs": [],
                "basis_bindings": [{"record_id": "EVD-008", "pointer": "/claim", "value_sha256": "1" * 64}],
                "rationale": "The evidence establishes non-applicability.",
            }}, "actions": [],
        }]

        self.assertEqual(api("consumed_evidence_ids")(state), [
            "EVD-001", "EVD-002", "EVD-003", "EVD-004", "EVD-005",
            "EVD-006", "EVD-007", "EVD-008", "EVD-900",
        ])

    def test_digest_is_stable_for_same_state_top_level_reordering_and_control_state_changes(self):
        # Break caught: storage order or the READY/approval lifecycle changing approved product meaning.
        state = foundation_state()
        state["objects"]["goals"] = [
            {"id": "GOAL-002", "status": "CURRENT", "statement": "Second goal."},
            {"id": "GOAL-001", "status": "CURRENT", "statement": "First goal."},
        ]
        state["evidence"] = evidence_with_grill_basis(
            evidence_record("EVD-901", source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"]),
        )
        state["surface_manifest"]["grill_profile"]["AUTH"]["basis_refs"].append("EVD-901")
        establish_current_baseline(state)
        first = api("definition_digest")(state)
        self.assertEqual(first, api("definition_digest")(copy.deepcopy(state)))

        reordered = copy.deepcopy(state)
        reordered["objects"]["goals"].reverse()
        reordered["evidence"].reverse()
        self.assertEqual(api("definition_digest")(reordered), first)

        control_only = copy.deepcopy(state)
        control_only["project"]["definition_status"] = "CLOSED"
        control_only["approval"] = {
            "status": "APPROVED", "approved_revision": 1,
            "approved_definition_digest": "a" * 64,
            "approved_manifest_digest": "b" * 64,
            "approved_at": "2026-08-29T00:00:00Z", "approved_by": "user",
        }
        control_only["approval_history"] = [{"revision": 999, "opaque": True}]
        self.assertEqual(api("definition_digest")(control_only), first)

    def test_unconsumed_evidence_and_all_evidence_baseline_refresh_do_not_change_semantic_digest(self):
        # Break caught: M3's all-evidence freshness commitment leaking into M4 approved product meaning.
        state = establish_current_baseline(foundation_state())
        before = api("definition_digest")(state)
        state["evidence"].append(evidence_record("EVD-001"))
        establish_current_baseline(state)

        self.assertEqual(api("definition_digest")(state), before)
        self.assertNotIn("EVD-001", api("semantic_record_hashes")(state))

    def test_consuming_evidence_and_changing_its_semantic_source_fields_changes_digest(self):
        # Break caught: current authority or its exact EVD claim/version/hash changing behind a stable digest.
        state = foundation_state()
        source = evidence_record("EVD-001", source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"])
        source.update({"observed_version": "v1", "content_hash": "sha256:one"})
        state["evidence"] = evidence_with_grill_basis(source)
        state["objects"]["decisions"] = [current_decision()]
        establish_current_baseline(state)
        unconsumed = api("definition_digest")(state)

        state["objects"]["decisions"][0]["evidence_refs"] = ["EVD-001"]
        consumed = api("definition_digest")(state)
        self.assertNotEqual(consumed, unconsumed)
        for field, value in (("claim", "Changed claim."), ("observed_version", "v2"), ("content_hash", "sha256:two")):
            candidate = copy.deepcopy(state)
            candidate["evidence"][0][field] = value
            self.assertNotEqual(api("definition_digest")(candidate), consumed, field)

    def test_exact_coverage_pack_and_binding_contract_commitments_change_digest(self):
        # Break caught: exact proof, active-pack identity, or frozen contract identity drifting without semantic staleness.
        state = establish_current_baseline(foundation_state())
        state["coverage"] = [{
            "feature_id": "REQ-001", "cells": {"actor": {
                "status": "COVERED",
                "authority_bindings": [{"record_id": "RULE-001", "pointer": "/statement", "value_sha256": "1" * 64}],
                "unknown_refs": [], "basis_bindings": [], "rationale": None,
            }},
        }]
        baseline = api("definition_digest")(state)

        binding = copy.deepcopy(state)
        binding["coverage"][0]["cells"]["actor"]["authority_bindings"][0]["value_sha256"] = "2" * 64
        self.assertNotEqual(api("definition_digest")(binding), baseline)

        contract = copy.deepcopy(state)
        contract["project"]["closure_contract"]["product_binding_contract"]["digest"] = "3" * 64
        self.assertNotEqual(api("definition_digest")(contract), baseline)

        for field, value in (
            ("pack_id", "GRILL-CORE-2"),
            ("digest", "4" * 64),
            ("target_refs", ["REQ-001"]),
        ):
            pack = copy.deepcopy(state)
            pack["discovery_baseline"]["active_grill_packs"][0][field] = value
            self.assertNotEqual(api("definition_digest")(pack), baseline, field)

    def test_projection_is_active_only_but_record_hashes_preserve_historical_product_records(self):
        # Break caught: historical stable records either altering current meaning or disappearing from approval history proof.
        state = foundation_state()
        state["objects"]["goals"] = [
            {"id": "GOAL-001", "status": "CURRENT", "statement": "Current goal."},
            {"id": "GOAL-002", "status": "SUPERSEDED", "statement": "Old goal.", "superseded_by": "GOAL-001"},
        ]
        establish_current_baseline(state)

        projection = api("semantic_projection")(state)
        self.assertEqual([record["id"] for record in projection["objects"]["goals"]], ["GOAL-001"])
        self.assertEqual(set(api("semantic_record_hashes")(state)), {"EVD-900", "GOAL-001", "GOAL-002"})
        self.assertNotIn("evidence_commitment_digest", projection["discovery_baseline"])
        self.assertNotIn("definition_status", projection["project"])
        self.assertNotIn("approval", projection)
        self.assertNotIn("approval_history", projection)
        self.assertNotIn("migration", projection)

    def test_nan_is_rejected_instead_of_receiving_an_implementation_defined_digest(self):
        # Break caught: Python's non-standard NaN JSON token producing a cross-runtime-incompatible approval digest.
        state = foundation_state()
        state["project"]["slug"] = math.nan
        with self.assertRaises((TypeError, ValueError)):
            api("definition_digest")(state)

    def test_operational_acceptance_timestamp_is_not_product_meaning(self):
        # Break caught: an authoring-time timestamp churning the approved semantic definition.
        state = foundation_state()
        decision = current_decision()
        decision.update({
            "resolution_mode": "USER_ACCEPTED_RECOMMENDATION",
            "decision_authority": "USER_CONFIRMATION",
            "decided_by": "USER",
            "accepted_recommendation": {
                "recommended_option": "OPT-A",
                "alternatives_presented": ["OPT-A", "OPT-B"],
                "tradeoffs_presented": ["The current behavior remains stable."],
                "accepted_by": "user",
                "accepted_at": "2026-08-29T00:00:00Z",
            },
        })
        state["objects"]["decisions"] = [decision]
        establish_current_baseline(state)
        before = api("definition_digest")(state)
        state["objects"]["decisions"][0]["accepted_recommendation"]["accepted_at"] = "2026-08-29T00:01:00Z"

        self.assertEqual(api("definition_digest")(state), before)


if __name__ == "__main__":
    unittest.main()
