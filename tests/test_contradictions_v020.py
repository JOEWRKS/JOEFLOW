import copy
import json
import sys
import unittest
from pathlib import Path

try:
    from tests.v020_support import (
        decision_record as canonical_decision_record,
        evidence_record,
        foundation_state,
        materiality,
        unknown_record as canonical_unknown_record,
    )
except ModuleNotFoundError:
    from v020_support import (
        decision_record as canonical_decision_record,
        evidence_record,
        foundation_state,
        materiality,
        unknown_record as canonical_unknown_record,
    )


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
sys.path.insert(0, str(SCRIPTS))

from state_validation_v2 import evaluate_closure_v2, validate_state_v2


def decision_record(decision_id="DEC-001", *, status="CURRENT"):
    record = canonical_decision_record(
        decision_id,
        status=status,
        source_unknown_refs=["UNK-001"],
        classification="NON_MATERIAL",
    )
    record["statement"] = "Choose the documented product behavior."
    return record


def decision_source_unknown():
    record = canonical_unknown_record(
        status="RESOLVED",
        classification="NON_MATERIAL",
        decision_authority="USER_DECISION_REQUIRED",
    )
    record.update({
        "resolved_by": ["DEC-001"],
        "resolution_mode": "USER_DECISION",
        "resolution_summary": "The user selected the documented behavior.",
    })
    return record


def contradiction_record(contradiction_id="CON-001", *, status="OPEN", classification="MATERIAL"):
    return {
        "id": contradiction_id,
        "status": status,
        "claim_a_refs": ["EVD-001"],
        "claim_b_refs": ["EVD-002"],
        "scope_refs": ["DEC-001"],
        "materiality": materiality(classification=classification),
        "resolution": None,
        "resolved_by": [],
        "selected_authority_refs": [],
    }


class ContradictionsV020Test(unittest.TestCase):
    def error_codes(self, state):
        return {error["code"] for error in validate_state_v2(state)}

    def state_with(self, contradiction, *evidence):
        state = foundation_state()
        state["evidence"] = [copy.deepcopy(record) for record in evidence]
        state["objects"]["unknowns"] = [decision_source_unknown()]
        state["objects"]["decisions"] = [decision_record()]
        state["contradictions"] = [copy.deepcopy(contradiction)]
        return state

    def canonical_state(self, contradiction=None):
        return self.state_with(
            contradiction or contradiction_record(),
            evidence_record("EVD-001"),
            evidence_record("EVD-002"),
        )

    def test_schema_defines_the_exact_typed_contradiction_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        record = schema["$defs"].get("contradiction_record")

        self.assertEqual(schema["properties"]["contradictions"]["items"], {"$ref": "#/$defs/contradiction_record"})
        self.assertFalse(record["additionalProperties"])
        self.assertEqual(
            set(record["required"]),
            {
                "id", "status", "claim_a_refs", "claim_b_refs", "scope_refs",
                "materiality", "resolution", "resolved_by", "selected_authority_refs",
            },
        )

    def test_contradiction_ids_are_con_stable_and_global(self):
        invalid = contradiction_record("EVD-001")
        self.assertIn("invalid_contradiction_id", self.error_codes(self.canonical_state(invalid)))

        duplicate = self.canonical_state()
        duplicate["contradictions"].append(contradiction_record())
        self.assertIn("duplicate_id", self.error_codes(duplicate))

    def test_claim_arrays_and_scope_refs_must_be_non_empty_unique_and_resolve(self):
        for field, value in (
            ("claim_a_refs", []),
            ("claim_b_refs", ["EVD-002", "EVD-002"]),
            ("scope_refs", []),
            ("scope_refs", ["DEC-001", "DEC-001"]),
        ):
            with self.subTest(field=field, value=value):
                contradiction = contradiction_record()
                contradiction[field] = value
                self.assertIn(
                    "invalid_contradiction_shape",
                    self.error_codes(self.canonical_state(contradiction)),
                )

        for field, value in (
            ("claim_b_refs", ["DEC-001"]),
            ("claim_a_refs", ["EVD-999"]),
            ("scope_refs", ["REQ-999"]),
        ):
            with self.subTest(field=field, value=value):
                contradiction = contradiction_record()
                contradiction[field] = value
                self.assertIn(
                    "invalid_contradiction_reference",
                    self.error_codes(self.canonical_state(contradiction)),
                )

    def test_resolved_requires_meaningful_resolution_and_current_decision_or_selected_authority(self):
        resolved_by_decision = contradiction_record(status="RESOLVED")
        resolved_by_decision.update({
            "resolution": "The decision explicitly selects the documented behavior.",
            "resolved_by": ["DEC-001"],
        })
        self.assertEqual(self.error_codes(self.canonical_state(resolved_by_decision)), set())

        resolved_by_evidence = contradiction_record(status="RESOLVED")
        resolved_by_evidence.update({
            "resolution": "The current implementation evidence is selected.",
            "selected_authority_refs": ["EVD-001"],
        })
        self.assertEqual(self.error_codes(self.canonical_state(resolved_by_evidence)), set())

        missing_resolution = copy.deepcopy(resolved_by_decision)
        missing_resolution["resolution"] = None
        self.assertIn("invalid_contradiction_resolution", self.error_codes(self.canonical_state(missing_resolution)))

        stale_decision = copy.deepcopy(resolved_by_decision)
        stale_decision["resolved_by"] = ["DEC-001"]
        stale_state = self.canonical_state(stale_decision)
        stale_state["objects"]["decisions"][0]["status"] = "STALE"
        self.assertIn("unresolved_contradiction_authority", self.error_codes(stale_state))

    def test_selected_authority_must_be_current_and_not_candidate_only(self):
        resolved = contradiction_record(status="RESOLVED")
        resolved.update({
            "resolution": "Select a current authoritative source.",
            "selected_authority_refs": ["EVD-001"],
        })

        for status in ("STALE", "SUPERSEDED", "UNAVAILABLE"):
            with self.subTest(status=status):
                state = self.canonical_state(resolved)
                state["evidence"][0]["status"] = status
                self.assertIn("invalid_selected_authority", self.error_codes(state))

        for source_kind in ("INFERRED_INTENT", "DESIGN_ARTIFACT"):
            with self.subTest(source_kind=source_kind):
                state = self.canonical_state(resolved)
                state["evidence"][0] = evidence_record(
                    "EVD-001", source_kind=source_kind, authority_classes=["INTENT"],
                )
                self.assertIn("unresolved_contradiction_authority", self.error_codes(state))

    def test_selected_authority_allows_current_candidate_evidence_when_current_authority_is_also_selected(self):
        resolved = contradiction_record(status="RESOLVED")
        resolved.update({
            "resolution": "The current implementation authority resolves the conflict.",
            "selected_authority_refs": ["EVD-001", "EVD-003"],
        })
        state = self.canonical_state(resolved)
        state["evidence"].append(evidence_record(
            "EVD-003", source_kind="INFERRED_INTENT", authority_classes=["INTENT"],
        ))

        self.assertEqual(self.error_codes(state), set())

    def test_bare_resolution_acknowledgement_fails_without_authority(self):
        acknowledged = contradiction_record(status="RESOLVED")
        acknowledged["resolution"] = "The conflict was reviewed and acknowledged."

        self.assertIn(
            "unresolved_contradiction_authority",
            self.error_codes(self.canonical_state(acknowledged)),
        )

    def test_material_open_contradictions_increment_only_the_material_metric(self):
        material_metrics = evaluate_closure_v2(self.canonical_state())["metrics"]
        self.assertEqual(material_metrics["unresolved_material_contradictions"], 1)

        non_material = contradiction_record(classification="NON_MATERIAL")
        non_material_metrics = evaluate_closure_v2(self.canonical_state(non_material))["metrics"]
        self.assertEqual(non_material_metrics["unresolved_material_contradictions"], 0)

    def test_stale_selected_authority_metric_counts_selected_non_current_evidence(self):
        resolved = contradiction_record(status="RESOLVED")
        resolved.update({
            "resolution": "The authority was selected before the source became stale.",
            "selected_authority_refs": ["EVD-001"],
        })
        state = self.canonical_state(resolved)
        state["evidence"][0]["status"] = "STALE"

        self.assertEqual(evaluate_closure_v2(state)["metrics"]["stale_selected_authority"], 1)

    def test_open_contradictions_preserve_nullable_resolution_shape_without_implying_resolution(self):
        open_record = contradiction_record()
        open_record["resolution"] = "TBD"

        self.assertEqual(self.error_codes(self.canonical_state(open_record)), set())

    def test_malformed_selected_authority_array_does_not_break_closure_metrics(self):
        malformed = contradiction_record()
        malformed["selected_authority_refs"] = None

        self.assertEqual(evaluate_closure_v2(self.canonical_state(malformed))["metrics"]["stale_selected_authority"], 0)

    def test_superseded_and_retired_contradictions_follow_explicit_lifecycle_rules(self):
        superseded = contradiction_record(status="SUPERSEDED")
        superseded["superseded_by"] = "CON-002"
        state = self.canonical_state(superseded)
        state["contradictions"].append(contradiction_record("CON-002"))
        self.assertEqual(self.error_codes(state), set())

        same_type_failure = self.canonical_state(superseded)
        self.assertIn("invalid_contradiction_supersession", self.error_codes(same_type_failure))

        retired = contradiction_record(status="RETIRED")
        retired.update({
            "retired_by": "DEC-001",
            "retired_at_revision": 1,
            "retirement_reason": "A current decision retired this obsolete conflict.",
        })
        self.assertEqual(self.error_codes(self.canonical_state(retired)), set())

        invalid_retired = copy.deepcopy(retired)
        invalid_retired["retired_by"] = "DEC-999"
        self.assertIn("invalid_contradiction_retirement", self.error_codes(self.canonical_state(invalid_retired)))


if __name__ == "__main__":
    unittest.main()
