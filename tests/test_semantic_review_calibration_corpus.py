import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
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
CALIBRATION_AUDIT_PATH = (
    ROOT
    / "evals"
    / "semantic-review-v0.4.3"
    / "calibration"
    / "semantic_review_calibration_audit.py"
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


def load_calibration_audit():
    spec = importlib.util.spec_from_file_location(
        "semantic_review_calibration_audit", CALIBRATION_AUDIT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tracked_calibration_paths():
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "-z",
            "--",
            "evals/semantic-review-v0.4.3/calibration",
            "tests/test_semantic_review_calibration_corpus.py",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = [ROOT / item for item in result.stdout.decode("utf-8").split("\0") if item]
    if CALIBRATION_AUDIT_PATH not in paths:
        paths.append(CALIBRATION_AUDIT_PATH)
    return paths


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

    def test_structured_calibration_semantics_are_product_neutral(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        record = read_json(RECORD_PATH)
        self.assertEqual(record["fixture_name"], "semantic-review-calibration-v1")
        self.assertEqual(record["fixture_kind"], "synthetic_calibration_fixture")
        self.assertFalse(record["product_definition_authority"])
        self.assertEqual(
            record["semantic_scope"],
            "neutral generic request and document approval semantics",
        )
        findings = audit.audit_product_neutrality(
            read_json(PACKAGE_ROOT / "canonical-authority.json"),
            read_json(PACKAGE_ROOT / "action-contract.json"),
            read_json(PACKAGE_ROOT / "semantic-obligation-index.json"),
            read_json(PACKAGE_ROOT / "review-identity-inventory.json"),
        )
        self.assertEqual(findings, [])

    def test_structured_neutrality_rejects_product_specific_semantics(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        authority = read_json(PACKAGE_ROOT / "canonical-authority.json")
        authority = copy.deepcopy(authority)
        authority["objects"]["rules"][0]["text"] = (
            "The actor for REQUEST-01 must authorize a purchase order; "
            "it must also settle a vendor invoice."
        )
        findings = audit.audit_product_neutrality(
            authority,
            read_json(PACKAGE_ROOT / "action-contract.json"),
            read_json(PACKAGE_ROOT / "semantic-obligation-index.json"),
            read_json(PACKAGE_ROOT / "review-identity-inventory.json"),
        )
        self.assertIn("NON_NEUTRAL_TERM", {item["code"] for item in findings})

    def test_corrected_owner_purity_families_do_not_borrow_adjacent_rules(self):
        authority = read_json(PACKAGE_ROOT / "canonical-authority.json")
        contract = read_json(PACKAGE_ROOT / "action-contract.json")
        expectations = {
            ("action", "expected_domain_mutation"): {
                "canonical": (
                    "authoritative decision state change",
                    "submitted approval outcome",
                ),
                "candidate": "authoritative decision state change",
                "foreign": ("unchanged", "preserve"),
            },
            ("action", "default_result"): {
                "canonical": (
                    "default result class after all owned guards pass",
                    "successful decision outcome",
                ),
                "candidate": "default result class after all owned guards pass",
                "foreign": ("no-op", "rejection"),
            },
            ("action", "business_side_effects"): {
                "canonical": (
                    "non-authoritative business record",
                    "only after the authoritative decision commit",
                ),
                "candidate": "non-authoritative business record",
                "foreign": ("notification", "delivery", "duplicate"),
            },
            ("lifecycle", "required_reason"): {
                "canonical": (
                    "non-empty reason when declining a transition",
                    "non-empty reason when requesting a reversal",
                ),
                "candidate": "non-empty reason when declining a transition",
                "foreign": ("history", "preserve"),
            },
        }
        canonical_by_field = {
            (rule["owner_kind"], rule["owner_id"], rule["responsibility_rule_id"]): rule[
                "text"
            ].lower()
            for rule in authority["objects"]["rules"]
        }

        for (owner_kind, field), expected in expectations.items():
            profile = read_json(PROFILE_SOURCE)[owner_kind][field]
            rule_id = profile["responsibility_rule_id"]
            collection = contract["actions" if owner_kind == "action" else "lifecycles"]
            id_key = "action_id" if owner_kind == "action" else "lifecycle_id"
            for owner in collection:
                identity = (owner_kind, owner[id_key], rule_id)
                canonical = canonical_by_field[identity]
                candidate = " ".join(owner[field]["value"]).lower()
                with self.subTest(owner_kind=owner_kind, field=field, owner=owner[id_key]):
                    for phrase in expected["canonical"]:
                        self.assertIn(phrase, canonical)
                    self.assertIn(expected["candidate"], candidate)
                    for phrase in expected["foreign"]:
                        self.assertNotIn(phrase, canonical)
                        self.assertNotIn(phrase, candidate)

    def test_implication_prone_local_candidates_keep_an_explicit_owned_constraint(self):
        contract = read_json(PACKAGE_ROOT / "action-contract.json")
        alternatives = {
            ("action", "actor"): (
                "exclude unassigned participants",
                "allow an unassigned participant to perform the operation",
            ),
            ("action", "relationship_predicate"): (
                "reject an unrelated actor",
                "allow an actor with no assignment to the request",
            ),
            ("action", "object_binding"): (
                "reject a target outside that binding",
                "allow a target outside the stated request and document binding",
            ),
            ("action", "allowed_current_states"): (
                "exclude every other state",
                "allow the operation from draft as well as pending",
            ),
            ("action", "history_result"): (
                "preserve every earlier event",
                "replace every earlier event with the new decision event",
            ),
            ("lifecycle", "required_confirmation"): (
                "reject an absent confirmation",
                "allow finalization without confirmation",
            ),
            ("lifecycle", "required_evidence"): (
                "reject evidence bound to another request",
                "accept evidence bound to another request",
            ),
            ("lifecycle", "authority"): (
                "reject transition attempts by other actors",
                "allow transitions by an unassigned actor",
            ),
        }
        for (owner_kind, field), (required, explicit_alternative) in alternatives.items():
            collection = contract["actions" if owner_kind == "action" else "lifecycles"]
            id_key = "action_id" if owner_kind == "action" else "lifecycle_id"
            for owner in collection:
                candidate = " ".join(owner[field]["value"]).lower()
                with self.subTest(owner_kind=owner_kind, field=field, owner=owner[id_key]):
                    self.assertEqual(candidate.count(";"), 1)
                    self.assertNotEqual(
                        required in candidate,
                        explicit_alternative in candidate,
                    )

    def test_candidate_surfaces_do_not_expose_a_unique_prose_slot(self):
        authority = read_json(PACKAGE_ROOT / "canonical-authority.json")
        contract = read_json(PACKAGE_ROOT / "action-contract.json")
        profile = read_json(PROFILE_SOURCE)
        canonical = {
            (rule["owner_kind"], rule["owner_id"], rule["responsibility_rule_id"]): rule[
                "text"
            ]
            for rule in authority["objects"]["rules"]
        }
        for owner_kind, collection_name, id_key in (
            ("action", "actions", "action_id"),
            ("lifecycle", "lifecycles", "lifecycle_id"),
        ):
            for field, rule in profile[owner_kind].items():
                if rule["completeness_mode"] == "REFERENCE_ONLY":
                    continue
                signatures = []
                for owner in contract[collection_name]:
                    text = " ".join(owner[field]["value"])
                    signatures.append(
                        (
                            text == canonical[
                                (owner_kind, owner[id_key], rule["responsibility_rule_id"])
                            ],
                            text.count(";"),
                        )
                    )
                with self.subTest(owner_kind=owner_kind, field=field):
                    self.assertEqual(len(set(signatures)), 1)
                    self.assertEqual(signatures[0], (False, 1))

    def test_leak_detector_rejects_synthetic_per_identity_outcome(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        identity = ":".join(("action", "ACT-SYNTHETIC", "actor"))
        outcome_key = "_".join(("intended", "verdict"))
        outcome_value = "".join(("APP", "ROVED"))
        with tempfile.TemporaryDirectory() as temporary:
            leaked = Path(temporary) / "synthetic.json"
            leaked.write_text(
                json.dumps({"review_identity": identity, outcome_key: outcome_value}),
                encoding="utf-8",
            )
            findings = audit.find_answer_leaks([leaked], allowed_exact_sha256=set())
        self.assertIn("PER_IDENTITY_OUTCOME", {item["code"] for item in findings})

    def test_leak_detector_rejects_synthetic_owner_field_outcome(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        support_key = "_".join(("expected", "support"))
        support_value = "".join(("defect", "ive"))
        payload = {
            "owner_kind": "action",
            "owner_id": "ACT-SYNTHETIC",
            "semantic_field": "actor",
            support_key: support_value,
        }
        with tempfile.TemporaryDirectory() as temporary:
            leaked = Path(temporary) / "synthetic.json"
            leaked.write_text(json.dumps(payload), encoding="utf-8")
            findings = audit.find_answer_leaks([leaked], allowed_exact_sha256=set())
        self.assertIn("PER_IDENTITY_OUTCOME", {item["code"] for item in findings})

    def test_leak_detector_rejects_synthetic_plaintext_outcome_hint(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        owner = "-".join(("ACT", "SYNTHETIC"))
        outcome = "".join(("defect", "ive"))
        with tempfile.TemporaryDirectory() as temporary:
            leaked = Path(temporary) / "synthetic.txt"
            leaked.write_text(f"{owner} actor is {outcome}", encoding="utf-8")
            findings = audit.find_answer_leaks([leaked], allowed_exact_sha256=set())
        self.assertIn("PER_IDENTITY_OUTCOME", {item["code"] for item in findings})

    def test_leak_detector_rejects_frozen_underscore_rationale_form(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        identity = ":".join(("action", "ACT-SYNTHETIC", "actor"))
        rationale = "_".join(("SUPPORTED", "EXACTLY"))
        with tempfile.TemporaryDirectory() as temporary:
            leaked = Path(temporary) / "synthetic.txt"
            leaked.write_text(f"{identity} => {rationale}", encoding="utf-8")
            findings = audit.find_answer_leaks([leaked], allowed_exact_sha256=set())
        self.assertIn("PER_IDENTITY_OUTCOME", {item["code"] for item in findings})

    def test_leak_detector_rejects_structured_defect_labels_in_plaintext(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        owner = "-".join(("ACT", "SYNTHETIC"))
        defect_labels = (
            "_".join(("owned", "secondary", "clause", "omitted")),
            "_".join(("unowned", "secondary", "clause", "overreach")),
            "_".join(("owner", "predicate", "contradiction")),
            "_".join(("owned", "secondary", "clause", "duplication")),
        )
        for defect_label in defect_labels:
            with self.subTest(defect_label=defect_label):
                with tempfile.TemporaryDirectory() as temporary:
                    leaked = Path(temporary) / "synthetic.txt"
                    leaked.write_text(f"{owner} actor => {defect_label}", encoding="utf-8")
                    findings = audit.find_answer_leaks(
                        [leaked], allowed_exact_sha256=set()
                    )
                self.assertIn(
                    "PER_IDENTITY_OUTCOME", {item["code"] for item in findings}
                )

    def test_leak_detector_rejects_synthetic_external_evidence_path(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        absolute_path = "".join(
            ("D:", "/controlled/", "calibration-controller-", "evidence/", "hidden.json")
        )
        with tempfile.TemporaryDirectory() as temporary:
            leaked = Path(temporary) / "synthetic.txt"
            leaked.write_text(absolute_path, encoding="utf-8")
            findings = audit.find_answer_leaks([leaked], allowed_exact_sha256=set())
        self.assertIn("EXTERNAL_ORACLE_PATH", {item["code"] for item in findings})

    def test_all_tracked_calibration_surfaces_are_answer_blind(self):
        self.assertTrue(CALIBRATION_AUDIT_PATH.is_file(), "calibration audit missing")
        audit = load_calibration_audit()
        allowed_public_hashes = {
            sha256(BRIEF_SOURCE)[0],
            sha256(PROFILE_SOURCE)[0],
            sha256(OUTPUT_SCHEMA_SOURCE)[0],
        }
        findings = audit.find_answer_leaks(
            tracked_calibration_paths(),
            allowed_exact_sha256=allowed_public_hashes,
        )
        self.assertEqual(findings, [])

    def test_oracle_commitment_is_aggregate_only_and_portable(self):
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
        self.assertRegex(commitment["sha256"], r"^[0-9a-f]{64}$")
        self.assertGreater(commitment["bytes"], 0)
        self.assertEqual(
            commitment["intended_approved_count"]
            + commitment["intended_rejected_candidate_count"],
            commitment["expected_identity_count"],
        )

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
