import copy
import json
import sys
import unittest
from pathlib import Path

try:
    from tests.v020_support import evidence_record, foundation_state
except ModuleNotFoundError:
    from v020_support import evidence_record, foundation_state


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
sys.path.insert(0, str(SCRIPTS))

import state_validation_v2
from state_validation_v2 import validate_state_v2


class EvidenceV020Test(unittest.TestCase):
    def error_codes(self, state):
        return {error["code"] for error in validate_state_v2(state)}

    def state_with(self, *records):
        state = foundation_state()
        state["evidence"] = [copy.deepcopy(record) for record in records]
        return state

    def test_schema_defines_the_exact_evidence_record_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        record = schema["$defs"]["evidence_record"]

        self.assertFalse(record["additionalProperties"])
        self.assertEqual(
            set(record["required"]),
            {
                "id", "status", "source_kind", "locator", "claim", "confidence",
                "authority_classes", "observed_version", "content_hash",
            },
        )
        self.assertEqual(
            schema["properties"]["evidence"]["items"],
            {"$ref": "#/$defs/evidence_record"},
        )

    def test_evidence_ids_must_use_the_evd_prefix_and_participate_in_global_uniqueness(self):
        invalid = self.state_with(evidence_record("REQ-001"))
        self.assertIn("invalid_evidence_id", self.error_codes(invalid))

        duplicate = self.state_with(evidence_record("EVD-001"), evidence_record("EVD-001"))
        self.assertIn("duplicate_id", self.error_codes(duplicate))

        cross_scope = self.state_with(evidence_record("EVD-001"))
        cross_scope["contradictions"] = [{"id": "EVD-001"}]
        self.assertIn("duplicate_id", self.error_codes(cross_scope))

        object_collision = self.state_with(evidence_record("EVD-001"))
        object_collision["objects"]["goals"] = [{
            "id": "EVD-001", "status": "CURRENT", "statement": "Duplicated ID",
        }]
        self.assertIn("duplicate_id", self.error_codes(object_collision))

        surface_collision = self.state_with(evidence_record("EVD-002"))
        surface_collision["surface_manifest"]["records"] = [{"id": "EVD-002"}]
        self.assertIn("duplicate_id", self.error_codes(surface_collision))

    def test_required_text_enums_and_authority_classes_are_validated(self):
        for field, value in (
            ("locator", ""),
            ("claim", ""),
            ("source_kind", "UNKNOWN"),
            ("confidence", "UNKNOWN"),
            ("status", "UNKNOWN"),
            ("authority_classes", ["UNKNOWN"]),
            ("authority_classes", []),
            ("authority_classes", [[]]),
        ):
            with self.subTest(field=field, value=value):
                record = evidence_record()
                record[field] = value
                self.assertIn("invalid_evidence_shape", self.error_codes(self.state_with(record)))

    def test_source_kind_capability_matrix_rejects_unsupported_declared_authority(self):
        state = self.state_with(evidence_record(authority_classes=["INTENT"]))

        self.assertIn("invalid_evidence_authority_class", self.error_codes(state))

    def test_candidate_evidence_is_structurally_valid_but_cannot_close_intent_authority(self):
        for source_kind in ("INFERRED_INTENT", "DESIGN_ARTIFACT"):
            with self.subTest(source_kind=source_kind):
                record = evidence_record(
                    source_kind=source_kind,
                    authority_classes=["INTENT"],
                )
                self.assertEqual(self.error_codes(self.state_with(record)), set())
                self.assertFalse(
                    state_validation_v2._evidence_can_support(
                        record, "INTENT", for_closure=True,
                    )
                )

    def test_observed_implementation_cannot_support_intent_or_preference(self):
        record = evidence_record()

        self.assertFalse(state_validation_v2._evidence_can_support(record, "INTENT", for_closure=False))
        self.assertFalse(state_validation_v2._evidence_can_support(record, "PREFERENCE", for_closure=False))

    def test_current_user_confirmed_intent_can_support_intent_for_closure(self):
        record = evidence_record(
            source_kind="USER_CONFIRMED_INTENT",
            authority_classes=["INTENT"],
        )

        self.assertTrue(state_validation_v2._evidence_can_support(record, "INTENT", for_closure=True))
        self.assertTrue(state_validation_v2._evidence_is_current_closure_eligible(record))

    def test_non_current_evidence_cannot_support_closure_authority(self):
        for status in ("STALE", "SUPERSEDED", "UNAVAILABLE"):
            with self.subTest(status=status):
                record = evidence_record(status=status)
                self.assertFalse(
                    state_validation_v2._evidence_can_support(
                        record, "FACTUAL", for_closure=True,
                    )
                )

    def test_superseded_evidence_requires_a_different_current_evidence_target(self):
        old = evidence_record("EVD-001", status="SUPERSEDED")
        old["superseded_by"] = "EVD-002"
        current = evidence_record("EVD-002")
        self.assertEqual(self.error_codes(self.state_with(old, current)), set())

        for target, target_status in (
            ("EVD-001", "CURRENT"),
            ("EVD-999", "CURRENT"),
            ("REQ-001", "CURRENT"),
            ("EVD-002", "STALE"),
        ):
            with self.subTest(target=target, target_status=target_status):
                invalid = evidence_record("EVD-001", status="SUPERSEDED")
                invalid["superseded_by"] = target
                state = self.state_with(invalid)
                if target == "EVD-002":
                    state["evidence"].append(evidence_record("EVD-002", status=target_status))
                self.assertIn("invalid_evidence_supersession", self.error_codes(state))

    def test_unavailable_evidence_requires_a_meaningful_reason_and_evidence_supersession_cycles_fail(self):
        unavailable = evidence_record(status="UNAVAILABLE")
        self.assertIn("invalid_evidence_unavailable", self.error_codes(self.state_with(unavailable)))

        unavailable["unavailable_reason"] = "Source access was revoked."
        self.assertEqual(self.error_codes(self.state_with(unavailable)), set())

        first = evidence_record("EVD-001", status="SUPERSEDED")
        second = evidence_record("EVD-002", status="SUPERSEDED")
        first["superseded_by"] = "EVD-002"
        second["superseded_by"] = "EVD-001"
        self.assertIn("evidence_supersession_cycle", self.error_codes(self.state_with(first, second)))


if __name__ == "__main__":
    unittest.main()
