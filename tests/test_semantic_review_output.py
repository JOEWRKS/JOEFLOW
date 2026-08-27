import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.hashing import canonical_json_bytes, sha256_bytes
from downstream.semantic_review.output import OutputError, validate_review_output


SCHEMA_PATH = (
    SKILL_ROOT
    / "downstream"
    / "schemas"
    / "semantic-review-output.schema.json"
)
HASHES = {
    "reviewer_brief_hash": "1" * 64,
    "reviewer_input_manifest_hash": "2" * 64,
    "reviewer_input_package_hash": "3" * 64,
    "contract_hash": "4" * 64,
    "responsibility_profile_hash": "5" * 64,
    "semantic_obligation_index_hash": "6" * 64,
    "review_identity_inventory_hash": "7" * 64,
}


def package_fixture():
    identity = "action:ACT-001:input_invariants"
    evidence_ref = {
        "object_id": "RULE-001",
        "pointer": "/objects/rules/0/text",
        "value_sha256": "b" * 64,
        "source_status": "CURRENT",
        "active": True,
    }
    provenance_hashes = [sha256_bytes(canonical_json_bytes(evidence_ref))]
    inventory = {
        identity: {
            "semantic_value_hash": "8" * 64,
            "provenance_hashes": provenance_hashes,
            "provenance_set_hash": sha256_bytes(
                canonical_json_bytes(provenance_hashes)
            ),
            "responsibility_rule_id": "FR-A09",
            "completeness_mode": "LOCAL",
            "semantic_obligation_ids": ["OBL-INPUT-001"],
        }
    }
    return {
        **HASHES,
        "expected_preflight_errors": [],
        "role_hashes": {"reviewer_brief": HASHES["reviewer_brief_hash"]},
        "review_output_schema": json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
        "expected_identities": [identity],
        "identity_inventory": inventory,
        "semantic_obligation_index": {
            "obligations": [
                {
                    "obligation_id": "OBL-INPUT-001",
                    "canonical_refs": [evidence_ref],
                    "owner_kind": "action",
                    "owner_id": "ACT-001",
                    "owning_field": "input_invariants",
                    "allowed_sibling_refs": [],
                    "required_test_refs": ["TEST-ACT-001-INPUT"],
                }
            ]
        },
    }


def run_envelope_fixture():
    attestation = {
        "fresh_context": True,
        "previous_verdict_access": False,
        "manifest_only_evidence": True,
    }
    return {
        "review_run_id": "run-001",
        "reviewer_context_id": "context-001",
        "reviewer_input_package_hash": HASHES["reviewer_input_package_hash"],
        "reviewer_brief_hash": HASHES["reviewer_brief_hash"],
        "isolation_attestation": attestation,
        "isolation_attestation_hash": sha256_bytes(canonical_json_bytes(attestation)),
    }


def output_fixture():
    envelope = run_envelope_fixture()
    package = package_fixture()
    expected = package["identity_inventory"]["action:ACT-001:input_invariants"]
    record = {
        "review_schema_version": "joewrks.semantic-review/1.0",
        "reviewer_brief_hash": HASHES["reviewer_brief_hash"],
        "reviewer_input_manifest_hash": HASHES["reviewer_input_manifest_hash"],
        "contract_hash": HASHES["contract_hash"],
        "review_identity": "action:ACT-001:input_invariants",
        "owner_kind": "action",
        "owner_id": "ACT-001",
        "semantic_field": "input_invariants",
        "semantic_value_hash": "8" * 64,
        "provenance_hashes": expected["provenance_hashes"],
        "provenance_set_hash": expected["provenance_set_hash"],
        "responsibility_rule_id": "FR-A09",
        "completeness_mode": "LOCAL",
        "sibling_review_identity_refs": [],
        "semantic_obligation_ids": ["OBL-INPUT-001"],
        "test_obligation_refs": ["TEST-ACT-001-INPUT"],
        "verdict": "APPROVED",
        "rationale_code": "SUPPORTED_EXACTLY",
        "canonical_evidence_refs": [
            {
                "object_id": "RULE-001",
                "pointer": "/objects/rules/0/text",
                "value_sha256": "b" * 64,
                "source_status": "CURRENT",
                "active": True,
            }
        ],
        "reviewer_explanation": "The owned input predicate is exactly supported.",
    }
    return {
        "review_schema_version": "joewrks.semantic-review/1.0",
        "review_run_id": envelope["review_run_id"],
        "reviewer_context_id": envelope["reviewer_context_id"],
        "isolation_attestation_hash": envelope["isolation_attestation_hash"],
        **HASHES,
        "preflight_errors": [],
        "records": [record],
        "summary": {
            "expected_identity_count": 1,
            "record_count": 1,
            "unique_identity_count": 1,
            "pending_count": 0,
            "verdict_counts": {
                "APPROVED": 1,
                "REJECTED_CANDIDATE": 0,
                "RUBRIC_ERROR": 0,
                "INPUT_PACKAGE_ERROR": 0,
            },
            "complete": True,
        },
    }


class SemanticReviewOutputTest(unittest.TestCase):
    def setUp(self):
        self.package = package_fixture()
        self.envelope = run_envelope_fixture()
        self.output = output_fixture()

    def test_completed_output_accepts_exact_identity_and_summary(self):
        self.assertEqual(
            validate_review_output(self.package, self.envelope, self.output),
            {"APPROVED": 1},
        )

    def test_completed_output_requires_exact_identity_set(self):
        self.output["records"].pop()
        self.output["summary"].update(
            {"record_count": 0, "unique_identity_count": 0}
        )
        self.output["summary"]["verdict_counts"]["APPROVED"] = 0
        with self.assertRaisesRegex(OutputError, "IDENTITY_SET_MISMATCH"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_output_rejects_synthetic_lifecycle_sentinel_identity(self):
        synthetic = copy.deepcopy(self.output["records"][0])
        synthetic.update(
            {
                "owner_kind": "lifecycle",
                "semantic_field": "superseded_sentinels",
                "review_identity": "lifecycle:LC-001:superseded_sentinels",
            }
        )
        self.output["records"] = [synthetic]
        with self.assertRaisesRegex(OutputError, "OUTPUT_SCHEMA_VIOLATION"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_rubric_error_is_not_candidate_rejection(self):
        self.output["records"] = []
        expected_error = {
            "verdict": "RUBRIC_ERROR",
            "rationale_code": "RESPONSIBILITY_UNDEFINED",
            "scope": "responsibility-profile",
            "canonical_evidence_refs": [],
            "reviewer_explanation": (
                "The frozen taxonomy has no unique owner for the fixture obligation."
            ),
        }
        self.package["expected_preflight_errors"] = [
            {
                key: expected_error[key]
                for key in (
                    "verdict",
                    "rationale_code",
                    "scope",
                    "canonical_evidence_refs",
                )
            }
        ]
        self.output["preflight_errors"] = [expected_error]
        self.output["summary"].update(
            {
                "record_count": 0,
                "unique_identity_count": 0,
                "pending_count": 0,
                "verdict_counts": {
                    "APPROVED": 0,
                    "REJECTED_CANDIDATE": 0,
                    "RUBRIC_ERROR": 1,
                    "INPUT_PACKAGE_ERROR": 0,
                },
                "complete": False,
            }
        )
        summary = validate_review_output(self.package, self.envelope, self.output)
        self.assertEqual(summary, {"RUBRIC_ERROR": 1})

    def test_preflight_scope_and_evidence_must_match_package_diagnostic(self):
        self.package["expected_preflight_errors"] = [
            {
                "verdict": "INPUT_PACKAGE_ERROR",
                "rationale_code": "INVALID_PROVENANCE",
                "scope": "package",
                "canonical_evidence_refs": [],
            }
        ]
        self.output["records"] = []
        self.output["preflight_errors"] = [
            {
                "verdict": "INPUT_PACKAGE_ERROR",
                "rationale_code": "INVALID_PROVENANCE",
                "scope": "forged-scope",
                "canonical_evidence_refs": [
                    {
                        "object_id": "FORGED",
                        "pointer": "/not/in/package",
                        "value_sha256": "f" * 64,
                        "source_status": "CURRENT",
                        "active": True,
                    }
                ],
                "reviewer_explanation": "Forged package evidence must not be accepted.",
            }
        ]
        self.output["summary"] = {
            "expected_identity_count": 1,
            "record_count": 0,
            "unique_identity_count": 0,
            "pending_count": 0,
            "verdict_counts": {
                "APPROVED": 0,
                "REJECTED_CANDIDATE": 0,
                "RUBRIC_ERROR": 0,
                "INPUT_PACKAGE_ERROR": 1,
            },
            "complete": False,
        }
        with self.assertRaisesRegex(OutputError, "PREFLIGHT_BINDING_MISMATCH"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_output_rejects_immutable_identity_and_verdict_rationale_drift(self):
        self.output["records"][0]["semantic_value_hash"] = "f" * 64
        with self.assertRaisesRegex(OutputError, "IMMUTABLE_IDENTITY_MISMATCH"):
            validate_review_output(self.package, self.envelope, self.output)
        self.output = output_fixture()
        self.output["records"][0]["rationale_code"] = "UNSUPPORTED_OVERREACH"
        with self.assertRaisesRegex(OutputError, "VERDICT_RATIONALE_MISMATCH"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_output_rejects_summary_arithmetic_and_unsorted_reference_sets(self):
        self.output["summary"]["record_count"] = 2
        with self.assertRaisesRegex(OutputError, "SUMMARY_MISMATCH"):
            validate_review_output(self.package, self.envelope, self.output)
        self.output = output_fixture()
        self.output["records"][0]["semantic_obligation_ids"] = [
            "OBL-Z",
            "OBL-A",
        ]
        with self.assertRaisesRegex(OutputError, "INVALID_REFERENCE_SET"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_output_rejects_forged_provenance_hashes_with_retained_set_hash(self):
        self.output["records"][0]["provenance_hashes"] = ["f" * 64]
        with self.assertRaisesRegex(OutputError, "IMMUTABLE_IDENTITY_MISMATCH"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_output_rejects_forged_obligation_sibling_and_test_refs(self):
        self.output["records"][0]["semantic_obligation_ids"] = ["OBL-FORGED"]
        with self.assertRaisesRegex(OutputError, "INVALID_REFERENCE_SET"):
            validate_review_output(self.package, self.envelope, self.output)
        self.output = output_fixture()
        self.output["records"][0]["sibling_review_identity_refs"] = [
            "action:ACT-001:visible_error"
        ]
        with self.assertRaisesRegex(OutputError, "INVALID_REFERENCE_SET"):
            validate_review_output(self.package, self.envelope, self.output)
        self.output = output_fixture()
        self.output["records"][0]["test_obligation_refs"] = ["TEST-FORGED"]
        with self.assertRaisesRegex(OutputError, "INVALID_REFERENCE_SET"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_output_rejects_forged_or_duplicate_canonical_evidence(self):
        self.output["records"][0]["canonical_evidence_refs"][0][
            "value_sha256"
        ] = "d" * 64
        with self.assertRaisesRegex(OutputError, "INVALID_REFERENCE_SET"):
            validate_review_output(self.package, self.envelope, self.output)
        self.output = output_fixture()
        self.output["records"][0]["canonical_evidence_refs"].append(
            copy.deepcopy(self.output["records"][0]["canonical_evidence_refs"][0])
        )
        with self.assertRaisesRegex(OutputError, "INVALID_REFERENCE_SET"):
            validate_review_output(self.package, self.envelope, self.output)

    def test_preflight_output_still_validates_any_emitted_records(self):
        self.output["preflight_errors"] = [
            {
                "verdict": "RUBRIC_ERROR",
                "rationale_code": "RESPONSIBILITY_UNDEFINED",
                "scope": "responsibility-profile",
                "canonical_evidence_refs": [],
                "reviewer_explanation": "The owner taxonomy is incomplete.",
            }
        ]
        record = self.output["records"][0]
        record["semantic_value_hash"] = "f" * 64
        record["rationale_code"] = "UNSUPPORTED_OVERREACH"
        self.output["summary"]["verdict_counts"]["RUBRIC_ERROR"] = 1
        self.output["summary"]["complete"] = False
        with self.assertRaisesRegex(
            OutputError, "IMMUTABLE_IDENTITY_MISMATCH|VERDICT_RATIONALE_MISMATCH"
        ):
            validate_review_output(self.package, self.envelope, self.output)

    def test_preflight_evidence_rejects_duplicate_references(self):
        self.output["records"] = []
        evidence = copy.deepcopy(
            output_fixture()["records"][0]["canonical_evidence_refs"][0]
        )
        self.output["preflight_errors"] = [
            {
                "verdict": "INPUT_PACKAGE_ERROR",
                "rationale_code": "INVALID_PROVENANCE",
                "scope": "provenance",
                "canonical_evidence_refs": [evidence, copy.deepcopy(evidence)],
                "reviewer_explanation": "The same source was cited twice.",
            }
        ]
        self.output["summary"].update(
            {
                "record_count": 0,
                "unique_identity_count": 0,
                "verdict_counts": {
                    "APPROVED": 0,
                    "REJECTED_CANDIDATE": 0,
                    "RUBRIC_ERROR": 0,
                    "INPUT_PACKAGE_ERROR": 1,
                },
                "complete": False,
            }
        )
        with self.assertRaisesRegex(OutputError, "INVALID_REFERENCE_SET"):
            validate_review_output(self.package, self.envelope, self.output)


if __name__ == "__main__":
    unittest.main()
