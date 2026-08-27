import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.responsibility import (
    ResponsibilityError,
    expected_responsibility,
    load_responsibility_profile,
    validate_obligation_index,
)
from downstream.semantic_review.hashing import canonical_json_bytes, sha256_bytes


PROFILE_PATH = (
    SKILL_ROOT
    / "downstream"
    / "semantic_review"
    / "artifacts"
    / "responsibility-profile-v1.json"
)
EXPECTED_ACTION_FIELDS = {
    "actor",
    "authentication",
    "relationship_predicate",
    "object_binding",
    "concurrency",
    "preconditions",
    "allowed_current_states",
    "forbidden_states",
    "input_invariants",
    "command",
    "expected_domain_mutation",
    "forbidden_mutations",
    "default_result",
    "result_expectations",
    "version_result",
    "history_result",
    "business_side_effects",
    "delivery_effects",
    "idempotency",
    "rejection",
    "recovery",
    "visible_success",
    "visible_error",
    "superseded_rules",
    "test_obligations",
    "trace",
}
EXPECTED_LIFECYCLE_FIELDS = {
    "current_states",
    "allowed_transitions",
    "forbidden_transitions",
    "boundary_conditions",
    "reversibility",
    "reversal_window",
    "object_outcome",
    "required_reason",
    "required_confirmation",
    "required_evidence",
    "authority",
    "history_preservation",
}


def valid_index():
    return {
        "schema_version": "joewrks.semantic-obligation-index/1.0",
        "contract_hash": "a" * 64,
        "obligations": [
            {
                "obligation_id": "OBL-INPUT-001",
                "canonical_refs": [
                    {
                        "object_id": "RULE-001",
                        "pointer": "/objects/rules/0/text",
                        "value_sha256": "b" * 64,
                        "source_status": "CURRENT",
                        "active": True,
                    }
                ],
                "obligation_type": "input validity",
                "owner_kind": "action",
                "owner_id": "ACT-001",
                "owning_field": "input_invariants",
                "responsibility_rule_id": "FR-A09",
                "completeness_mode": "LOCAL",
                "semantic_value_pointer": "/actions/0/input_invariants/value",
                "semantic_value_hash": sha256_bytes(
                    canonical_json_bytes(["reason is non-empty"])
                ),
                "allowed_sibling_refs": [],
                "required_test_refs": ["TEST-ACT-001-INPUT"],
                "projection_notes": "Reason input predicate.",
            }
        ],
    }


class SemanticReviewResponsibilityTest(unittest.TestCase):
    def setUp(self):
        self.profile = load_responsibility_profile(PROFILE_PATH)
        def reviewed(value):
            return {
                "value": value,
                "source_refs": [0],
                "derivation": {"kind": "REVIEW_REQUIRED", "explanation": "review"},
            }
        self.contract = {
            "contract_hash": "a" * 64,
            "actions": [
                {
                    "action_id": "ACT-001",
                    "sources": copy.deepcopy(valid_index()["obligations"][0]["canonical_refs"]),
                    "input_invariants": reviewed(["reason is non-empty"]),
                    "visible_error": reviewed(["show validation error"]),
                    "actor": reviewed(["requester"]),
                    "command": reviewed(["submit reason"]),
                }
            ],
            "lifecycles": [{"lifecycle_id": "LC-001"}],
        }

    def test_profile_assigns_all_current_action_and_lifecycle_fields_once(self):
        self.assertEqual(set(self.profile["action"]), EXPECTED_ACTION_FIELDS)
        self.assertEqual(set(self.profile["lifecycle"]), EXPECTED_LIFECYCLE_FIELDS)
        self.assertEqual(len(self.profile["action"]), 26)
        self.assertEqual(len(self.profile["lifecycle"]), 12)
        self.assertNotIn("superseded_sentinels", self.profile["lifecycle"])
        self.assertEqual(self.profile["rubric_calibration_revision"], 1)
        all_ids = {
            rule["responsibility_rule_id"]
            for kind in ("action", "lifecycle")
            for rule in self.profile[kind].values()
        }
        self.assertNotIn("FR-L13", all_ids)
        self.assertNotIn("PR-P01", all_ids)
        self.assertEqual(len(self.profile["obligation_taxonomy"]), 38)
        self.assertEqual(
            self.profile["obligation_taxonomy"]["input validity"], "FR-A09"
        )

    def test_profile_carries_normative_modes_siblings_and_failure_codes(self):
        visible_error = self.profile["action"]["visible_error"]
        self.assertEqual(visible_error["responsibility_rule_id"], "FR-A23")
        self.assertEqual(visible_error["completeness_mode"], "COMPOSITIONAL")
        self.assertIn("FR-A09", visible_error["allowed_sibling_rules"])
        self.assertEqual(visible_error["omission_code"], "MISSING_OWNED_SEMANTIC")
        self.assertEqual(visible_error["overreach_code"], "UNSUPPORTED_OVERREACH")
        self.assertEqual(
            expected_responsibility("action", "input_invariants"),
            ("FR-A09", "LOCAL"),
        )

    def test_obligation_index_accepts_unique_exact_owner(self):
        validate_obligation_index(self.contract, self.profile, valid_index())

    def test_obligation_cannot_have_two_owners(self):
        index = valid_index()
        duplicate = copy.deepcopy(index["obligations"][0])
        duplicate["owning_field"] = "visible_error"
        duplicate["responsibility_rule_id"] = "FR-A23"
        duplicate["completeness_mode"] = "COMPOSITIONAL"
        index["obligations"].append(duplicate)
        with self.assertRaisesRegex(ResponsibilityError, "MULTIPLE_OWNERS"):
            validate_obligation_index(self.contract, self.profile, index)

    def test_obligation_rejects_raw_lifecycle_sentinel_identity(self):
        index = valid_index()
        obligation = index["obligations"][0]
        obligation.update(
            {
                "owner_kind": "lifecycle",
                "owner_id": "LC-001",
                "owning_field": "superseded_sentinels",
                "responsibility_rule_id": "PR-P01",
            }
        )
        with self.assertRaisesRegex(ResponsibilityError, "RESPONSIBILITY_UNDEFINED"):
            validate_obligation_index(self.contract, self.profile, index)

    def test_obligation_rejects_wrong_rule_and_unsorted_references(self):
        index = valid_index()
        index["obligations"][0]["responsibility_rule_id"] = "FR-A23"
        with self.assertRaisesRegex(ResponsibilityError, "RESPONSIBILITY_UNDEFINED"):
            validate_obligation_index(self.contract, self.profile, index)
        index = valid_index()
        index["obligations"][0]["allowed_sibling_refs"] = [
            "action:ACT-001:visible_error",
            "action:ACT-001:rejection",
        ]
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)

    def test_obligation_type_must_match_closed_taxonomy(self):
        index = valid_index()
        index["obligations"][0]["obligation_type"] = "invented semantic category"
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)

    def test_sibling_must_exist_and_be_allowed_by_owner_rule(self):
        index = valid_index()
        index["obligations"][0]["allowed_sibling_refs"] = [
            "action:ACT-999:visible_error"
        ]
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)
        index = valid_index()
        index["obligations"][0]["allowed_sibling_refs"] = ["action:ACT-001:actor"]
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)

    def test_allowed_review_sibling_is_accepted(self):
        index = valid_index()
        index["obligations"][0]["allowed_sibling_refs"] = [
            "action:ACT-001:command"
        ]
        validate_obligation_index(self.contract, self.profile, index)

    def test_material_obligation_requires_test_reference(self):
        index = valid_index()
        index["obligations"][0]["required_test_refs"] = []
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)

    def test_semantic_pointer_and_hash_must_resolve_exact_contract_value(self):
        index = valid_index()
        index["obligations"][0]["semantic_value_pointer"] = (
            "/actions/0/visible_error/value"
        )
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)
        index = valid_index()
        index["obligations"][0]["semantic_value_hash"] = "f" * 64
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)

    def test_canonical_refs_must_be_declared_by_owning_semantic_field(self):
        index = valid_index()
        index["obligations"][0]["canonical_refs"][0].update(
            {
                "object_id": "RULE-OTHER",
                "pointer": "/objects/rules/1/text",
                "value_sha256": "d" * 64,
            }
        )
        with self.assertRaisesRegex(ResponsibilityError, "INVALID_OBLIGATION_INDEX"):
            validate_obligation_index(self.contract, self.profile, index)


if __name__ == "__main__":
    unittest.main()
