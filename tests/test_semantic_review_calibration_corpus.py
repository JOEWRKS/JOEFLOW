import hashlib
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.hashing import package_hash
from downstream.semantic_review.package import REQUIRED_ROLES, load_and_verify_package


FIXTURE_ROOT = (
    ROOT
    / "evals"
    / "semantic-review-v0.4.3"
    / "calibration"
    / "semantic-review-calibration-v1"
)
PACKAGE_ROOT = FIXTURE_ROOT / "reviewer-package"
RECORD_PATH = FIXTURE_ROOT / "calibration-record.json"
HUMAN_PACKET_PATH = FIXTURE_ROOT / "human-adjudication-packet.md"
AUDIT_EVIDENCE_PATH = FIXTURE_ROOT / "implementation-audit-evidence.md"
EXTERNAL_ORACLE_PATH = Path(
    "D:/JOEWRKS/JOEWRKS-Product-v043-calibration-controller-evidence/"
    "semantic-review-calibration-v1-seed-oracle.json"
)

PROFILE_SOURCE = (
    SKILL_ROOT
    / "downstream"
    / "semantic_review"
    / "artifacts"
    / "responsibility-profile-v1.json"
)
BRIEF_SOURCE = PROFILE_SOURCE.with_name("reviewer-brief-v1.md")
OUTPUT_SCHEMA_SOURCE = (
    SKILL_ROOT / "downstream" / "schemas" / "semantic-review-output.schema.json"
)

PACKAGE_ROLE_PATHS = {
    "canonical_authority": "canonical-authority.json",
    "action_contract": "action-contract.json",
    "provenance_inventory": "provenance-inventory.json",
    "responsibility_profile": "responsibility-profile-v1.json",
    "semantic_obligation_index": "semantic-obligation-index.json",
    "reviewer_brief": "reviewer-brief-v1.md",
    "review_output_schema": "semantic-review-output.schema.json",
    "review_identity_inventory": "review-identity-inventory.json",
    "exclusion_manifest": "exclusion-manifest.json",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path):
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


class SemanticReviewCalibrationCorpusTest(unittest.TestCase):
    def test_corpus_has_three_complete_owners_and_exact_rule_coverage(self):
        contract = read_json(PACKAGE_ROOT / "action-contract.json")
        profile = read_json(PACKAGE_ROOT / "responsibility-profile-v1.json")
        inventory = read_json(PACKAGE_ROOT / "review-identity-inventory.json")

        self.assertEqual(len(contract["actions"]), 3)
        self.assertEqual(len(contract["lifecycles"]), 3)
        for owner in contract["actions"]:
            for field in profile["action"]:
                self.assertEqual(owner[field]["derivation"]["kind"], "REVIEW_REQUIRED")
        for owner in contract["lifecycles"]:
            self.assertEqual(owner["superseded_sentinels"], [])
            for field in profile["lifecycle"]:
                self.assertEqual(owner[field]["derivation"]["kind"], "REVIEW_REQUIRED")

        identities = inventory["identities"]
        self.assertEqual(len(identities), 114)
        self.assertEqual(
            Counter(item["owner_kind"] for item in identities),
            Counter({"action": 78, "lifecycle": 36}),
        )
        expected_rules = [f"FR-A{index:02d}" for index in range(1, 27)] + [
            f"FR-L{index:02d}" for index in range(1, 13)
        ]
        self.assertEqual(
            Counter(item["responsibility_rule_id"] for item in identities),
            Counter({rule_id: 3 for rule_id in expected_rules}),
        )
        self.assertNotIn("FR-L13", {item["responsibility_rule_id"] for item in identities})
        self.assertFalse(
            any(item["semantic_field"] == "superseded_sentinels" for item in identities)
        )

    def test_calibration_specific_material_is_synthetic_and_product_neutral(self):
        record = read_json(RECORD_PATH)
        self.assertEqual(record["fixture_name"], "semantic-review-calibration-v1")
        self.assertEqual(record["fixture_kind"], "synthetic_calibration_fixture")
        self.assertFalse(record["product_definition_authority"])
        self.assertEqual(
            record["semantic_scope"],
            "neutral generic request and document approval semantics",
        )

        calibration_specific_paths = [
            RECORD_PATH,
            HUMAN_PACKET_PATH,
            AUDIT_EVIDENCE_PATH,
            PACKAGE_ROOT / "canonical-authority.json",
            PACKAGE_ROOT / "action-contract.json",
            PACKAGE_ROOT / "provenance-inventory.json",
            PACKAGE_ROOT / "semantic-obligation-index.json",
            PACKAGE_ROOT / "review-identity-inventory.json",
            PACKAGE_ROOT / "exclusion-manifest.json",
            PACKAGE_ROOT / "manifest.json",
        ]
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in calibration_specific_paths
        )
        for prohibited in (
            "client-feedback-portal",
            "expense reimbursement",
            "expense-reimbursement",
            "studio booking",
            "studio-booking",
        ):
            self.assertNotIn(prohibited, combined)
        self.assertIsNone(re.search(r"\brma\b", combined))

    def test_oracle_is_external_and_matches_only_the_tracked_commitment(self):
        record = read_json(RECORD_PATH)
        commitment = record["oracle_commitment"]
        self.assertEqual(
            set(commitment),
            {
                "schema_version",
                "sha256",
                "bytes",
                "expected_identity_count",
                "intended_approved_count",
                "intended_rejected_candidate_count",
            },
        )
        self.assertEqual(
            commitment["schema_version"],
            "joewrks.semantic-review-calibration-seed-oracle/1.0",
        )
        self.assertEqual(commitment["expected_identity_count"], 114)
        self.assertEqual(commitment["intended_approved_count"], 76)
        self.assertEqual(commitment["intended_rejected_candidate_count"], 38)
        self.assertTrue(EXTERNAL_ORACLE_PATH.is_file())
        self.assertEqual(sha256(EXTERNAL_ORACLE_PATH), (commitment["sha256"], commitment["bytes"]))

        package_files = {path.name for path in PACKAGE_ROOT.iterdir() if path.is_file()}
        self.assertFalse(any("oracle" in name.lower() for name in package_files))
        self.assertFalse(
            any(
                "golden" in name.lower()
                or "review-results" in name.lower()
                or "review-verdicts" in name.lower()
                for name in package_files
            )
        )
        packet_text = HUMAN_PACKET_PATH.read_text(encoding="utf-8")
        self.assertNotIn("REJECTED_CANDIDATE", packet_text)
        self.assertNotIn("SUPPORTED_EXACTLY", packet_text)

    def test_package_uses_exact_frozen_copies_and_no_undeclared_files(self):
        self.assertEqual(
            (PACKAGE_ROOT / "reviewer-brief-v1.md").read_bytes(),
            BRIEF_SOURCE.read_bytes(),
        )
        self.assertEqual(
            (PACKAGE_ROOT / "responsibility-profile-v1.json").read_bytes(),
            PROFILE_SOURCE.read_bytes(),
        )
        self.assertEqual(
            (PACKAGE_ROOT / "semantic-review-output.schema.json").read_bytes(),
            OUTPUT_SCHEMA_SOURCE.read_bytes(),
        )

        manifest = read_json(PACKAGE_ROOT / "manifest.json")
        self.assertEqual(len(manifest["files"]), 9)
        self.assertEqual(
            Counter(item["logical_role"] for item in manifest["files"]),
            Counter({role: 1 for role in REQUIRED_ROLES}),
        )
        self.assertEqual(
            {item["logical_role"]: item["path"] for item in manifest["files"]},
            PACKAGE_ROLE_PATHS,
        )
        self.assertEqual(
            {path.name for path in PACKAGE_ROOT.iterdir() if path.is_file()},
            {"manifest.json", *PACKAGE_ROLE_PATHS.values()},
        )

    def test_package_text_bytes_remain_lf_on_checkout(self):
        for path in sorted(PACKAGE_ROOT.iterdir()):
            if path.is_file() and path.suffix in {".json", ".md"}:
                relative = path.relative_to(ROOT).as_posix()
                result = subprocess.run(
                    ["git", "check-attr", "eol", "--", relative],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.stdout.strip(), f"{relative}: eol: lf")

    def test_production_loader_accepts_package_and_recorded_hashes_are_exact(self):
        verified = load_and_verify_package(PACKAGE_ROOT)
        record = read_json(RECORD_PATH)
        manifest = verified["manifest"]

        self.assertEqual(verified["expected_preflight_errors"], [])
        self.assertEqual(len(verified["expected_identities"]), 114)
        self.assertEqual(
            verified["reviewer_input_package_hash"],
            package_hash(manifest["reviewer_input_manifest_hash"], manifest["files"]),
        )
        expected_hashes = {
            "reviewer_input_manifest_hash": verified["reviewer_input_manifest_hash"],
            "reviewer_input_package_hash": verified["reviewer_input_package_hash"],
            "contract_hash": verified["contract_hash"],
            "canonical_authority_hash": verified["role_hashes"]["canonical_authority"],
            "reviewer_brief_hash": verified["reviewer_brief_hash"],
            "responsibility_profile_hash": verified["responsibility_profile_hash"],
            "semantic_obligation_index_hash": verified["semantic_obligation_index_hash"],
            "review_identity_inventory_hash": verified["review_identity_inventory_hash"],
            "review_output_schema_hash": verified["role_hashes"]["review_output_schema"],
        }
        self.assertEqual(record["hashes"], expected_hashes)
        manifest_file_hash, manifest_file_bytes = sha256(PACKAGE_ROOT / "manifest.json")
        self.assertIn("manifest_file", record)
        self.assertEqual(
            record["manifest_file"],
            {
                "path": "manifest.json",
                "sha256": manifest_file_hash,
                "bytes": manifest_file_bytes,
            },
        )
        self.assertEqual(
            record["package_files"],
            [
                {
                    "logical_role": item["logical_role"],
                    "path": item["path"],
                    "sha256": sha256(PACKAGE_ROOT / item["path"])[0],
                    "bytes": sha256(PACKAGE_ROOT / item["path"])[1],
                }
                for item in manifest["files"]
            ],
        )
        self.assertIn(
            "IMPLEMENTATION_AUDIT_RAW_EVIDENCE_NOT_PRESERVED",
            AUDIT_EVIDENCE_PATH.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
