import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.hashing import manifest_hash, package_hash, sha256_bytes
from downstream.semantic_review.package import (
    PackageError,
    load_and_verify_package,
    verify_run_envelope,
)
from downstream.semantic_review.responsibility import (
    EXPECTED_ACTION_FIELDS,
    EXPECTED_LIFECYCLE_FIELDS,
)


REQUIRED_ROLE_FILES = {
    "canonical_authority": "authority.json",
    "action_contract": "contract.json",
    "provenance_inventory": "provenance.json",
    "responsibility_profile": "responsibility.json",
    "semantic_obligation_index": "obligations.json",
    "reviewer_brief": "reviewer-brief.md",
    "review_output_schema": "review-output.schema.json",
    "review_identity_inventory": "identities.json",
    "exclusion_manifest": "exclusions.json",
}


def _json_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _write_package(root: Path, *, active_superseded=False):
    canonical_value = "A non-empty reason is required."
    evidence_ref = {
        "object_id": "RULE-001",
        "pointer": "/objects/rules/0/text",
        "value_sha256": sha256_bytes(_json_bytes(canonical_value)),
        "source_status": "CURRENT",
        "active": True,
    }
    superseded_value = "An obsolete lifecycle transition."
    sentinel_ref = {
        "object_id": "RULE-OLD",
        "pointer": "/objects/rules/1/text",
        "value_sha256": sha256_bytes(_json_bytes(superseded_value)),
        "source_status": "SUPERSEDED",
        "active": active_superseded,
    }
    semantic_value = ["reason is non-empty"]
    provenance_hashes = [sha256_bytes(_json_bytes(evidence_ref))]
    def semantic_field(field, *, review=False):
        return {
            "value": semantic_value if field == "input_invariants" else [field],
            "source_refs": [0],
            "derivation": (
                {
                    "kind": "REVIEW_REQUIRED",
                    "explanation": "The input predicate requires semantic review.",
                }
                if review
                else {"kind": "MACHINE_DERIVED", "operator": "exact"}
            ),
        }

    action = {
        "action_id": "ACT-001",
        "sources": [evidence_ref],
        **{
            field: semantic_field(field, review=field == "input_invariants")
            for field in EXPECTED_ACTION_FIELDS
        },
    }
    lifecycle = {
        "lifecycle_id": "LC-001",
        "sources": [evidence_ref],
        **{field: semantic_field(field) for field in EXPECTED_LIFECYCLE_FIELDS},
        "superseded_sentinels": [sentinel_ref],
    }
    contract = {
        "contract_schema_version": "joewrks.action-conformance/1.0",
        "compiler": {"id": "semantic-review-test", "version": "1.0"},
        "source_authority": {
            "product_slug": "semantic-review-fixture",
            "approved_revision": 1,
            "approved_digest": "fixture",
            "canonical_state_sha256": "d" * 64,
        },
        "actions": [action],
        "lifecycles": [lifecycle],
        "authority_assessment": {
            "structurally_valid": True,
            "provenance_valid": True,
            "machine_derived_obligations_verified": True,
            "machine_derived_field_count": 37,
            "review_required_field_count": 1,
            "review_required_obligations_present": True,
            "machine_verifiable_coverage": 1,
        },
    }
    contract["contract_hash"] = sha256_bytes(_json_bytes(contract))
    profile_path = (
        SKILL_ROOT
        / "downstream"
        / "semantic_review"
        / "artifacts"
        / "responsibility-profile-v1.json"
    )
    output_schema_path = (
        SKILL_ROOT / "downstream" / "schemas" / "semantic-review-output.schema.json"
    )
    brief_path = profile_path.with_name("reviewer-brief-v1.md")
    obligation = {
        "obligation_id": "OBL-INPUT-001",
        "canonical_refs": [evidence_ref],
        "obligation_type": "input validity",
        "owner_kind": "action",
        "owner_id": "ACT-001",
        "owning_field": "input_invariants",
        "responsibility_rule_id": "FR-A09",
        "completeness_mode": "LOCAL",
        "semantic_value_pointer": "/actions/0/input_invariants/value",
        "semantic_value_hash": sha256_bytes(_json_bytes(semantic_value)),
        "allowed_sibling_refs": [],
        "required_test_refs": ["TEST-INPUT-001"],
        "projection_notes": "Synthetic package integration fixture.",
    }
    values = {
        "canonical_authority": {
            "objects": {
                "rules": [
                    {"id": "RULE-001", "status": "CURRENT", "text": canonical_value},
                    {"id": "RULE-OLD", "status": "SUPERSEDED", "text": superseded_value},
                ]
            }
        },
        "action_contract": contract,
        "provenance_inventory": {
            "schema_version": "joewrks.semantic-review-provenance-inventory/1.0",
            "records": [evidence_ref],
        },
        "responsibility_profile": profile_path.read_bytes(),
        "semantic_obligation_index": {
            "schema_version": "joewrks.semantic-obligation-index/1.0",
            "contract_hash": contract["contract_hash"],
            "obligations": [obligation],
        },
        "reviewer_brief": brief_path.read_bytes(),
        "review_output_schema": output_schema_path.read_bytes(),
        "review_identity_inventory": {
            "schema_version": "joewrks.semantic-review-identity-inventory/1.0",
            "contract_hash": contract["contract_hash"],
            "identities": [
                {
                    "review_identity": "action:ACT-001:input_invariants",
                    "owner_kind": "action",
                    "owner_id": "ACT-001",
                    "semantic_field": "input_invariants",
                    "semantic_value_hash": obligation["semantic_value_hash"],
                    "provenance_hashes": provenance_hashes,
                    "provenance_set_hash": sha256_bytes(_json_bytes(provenance_hashes)),
                    "responsibility_rule_id": "FR-A09",
                    "completeness_mode": "LOCAL",
                    "semantic_obligation_ids": ["OBL-INPUT-001"],
                }
            ],
        },
        "exclusion_manifest": {
            "previous_reviewer_verdicts_present": False,
            "hidden_answers_present": False,
            "implementation_outcomes_present": False,
            "unrelated_product_evidence_present": False,
        },
    }
    files = []
    for role, relative in REQUIRED_ROLE_FILES.items():
        payload = values[role]
        data = payload if isinstance(payload, bytes) else _json_bytes(payload)
        (root / relative).write_bytes(data)
        files.append(
            {
                "logical_role": role,
                "path": relative,
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "schema_identity": f"joewrks.semantic-review-role/{role}",
            }
        )
    manifest = {
        "schema_version": "joewrks.semantic-review-input/1.0",
        "previous_reviewer_verdicts_present": False,
        "files": files,
    }
    manifest["reviewer_input_manifest_hash"] = manifest_hash(manifest)
    (root / "manifest.json").write_bytes(_json_bytes(manifest))
    return manifest


class SemanticReviewPackageTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.manifest = _write_package(self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def _rewrite_manifest(self, manifest):
        manifest["reviewer_input_manifest_hash"] = manifest_hash(manifest)
        (self.root / "manifest.json").write_bytes(_json_bytes(manifest))

    def _replace_role(self, logical_role, value):
        manifest = json.loads((self.root / "manifest.json").read_text("utf-8"))
        item = next(
            entry for entry in manifest["files"] if entry["logical_role"] == logical_role
        )
        data = value if isinstance(value, bytes) else _json_bytes(value)
        (self.root / item["path"]).write_bytes(data)
        item["sha256"] = sha256_bytes(data)
        item["bytes"] = len(data)
        self._rewrite_manifest(manifest)

    def _mutate_contract(self, mutation, *, rebind_sidecars=False):
        contract = json.loads((self.root / "contract.json").read_text("utf-8"))
        mutation(contract)
        contract.pop("contract_hash", None)
        contract["contract_hash"] = sha256_bytes(_json_bytes(contract))
        self._replace_role("action_contract", contract)
        if rebind_sidecars:
            obligations = json.loads((self.root / "obligations.json").read_text("utf-8"))
            obligations["contract_hash"] = contract["contract_hash"]
            self._replace_role("semantic_obligation_index", obligations)
            identities = json.loads((self.root / "identities.json").read_text("utf-8"))
            identities["contract_hash"] = contract["contract_hash"]
            self._replace_role("review_identity_inventory", identities)

    def test_package_verifies_exact_hashes_roles_and_package_identity(self):
        verified = load_and_verify_package(self.root)
        expected = package_hash(
            self.manifest["reviewer_input_manifest_hash"], self.manifest["files"]
        )
        self.assertEqual(verified["reviewer_input_package_hash"], expected)
        self.assertEqual(verified["manifest"], self.manifest)
        self.assertEqual(verified["contract_hash"], verified["contract"]["contract_hash"])
        self.assertEqual(
            verified["expected_identities"], ["action:ACT-001:input_invariants"]
        )
        self.assertIn("FR-A09", verified["responsibility_profile"]["brief_ownership_labels"])
        self.assertEqual(
            verified["semantic_obligation_index"]["obligations"][0]["obligation_id"],
            "OBL-INPUT-001",
        )
        self.assertEqual(
            verified["review_output_schema"]["$defs"]["verdict"]["enum"],
            ["APPROVED", "REJECTED_CANDIDATE", "RUBRIC_ERROR", "INPUT_PACKAGE_ERROR"],
        )

    def test_package_rejects_prior_verdict_exposure(self):
        (self.root / "prior-review.json").write_text(
            '{"verdict":"APPROVED"}', encoding="utf-8", newline="\n"
        )
        with self.assertRaisesRegex(PackageError, "PREVIOUS_VERDICT_EXPOSURE"):
            load_and_verify_package(self.root)

    def test_package_rejects_declared_prior_verdict_payload(self):
        data = _json_bytes({"previous_reviewer_verdict": "APPROVED"})
        (self.root / "notes.json").write_bytes(data)
        manifest = json.loads((self.root / "manifest.json").read_text("utf-8"))
        manifest["files"].append(
            {
                "logical_role": "supporting_projection",
                "path": "notes.json",
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "schema_identity": "joewrks.semantic-review-supporting/1.0",
            }
        )
        self._rewrite_manifest(manifest)
        with self.assertRaisesRegex(PackageError, "PREVIOUS_VERDICT_EXPOSURE"):
            load_and_verify_package(self.root)

    def test_package_rejects_disguised_declared_review_output_payload(self):
        data = _json_bytes(
            {
                "review_identity": "action:ACT-001:input_invariants",
                "verdict": "APPROVED",
                "rationale_code": "SUPPORTED_EXACTLY",
            }
        )
        (self.root / "supporting.json").write_bytes(data)
        manifest = json.loads((self.root / "manifest.json").read_text("utf-8"))
        manifest["files"].append(
            {
                "logical_role": "supporting_projection",
                "path": "supporting.json",
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "schema_identity": "joewrks.semantic-review-supporting/1.0",
            }
        )
        self._rewrite_manifest(manifest)
        with self.assertRaisesRegex(PackageError, "PREVIOUS_VERDICT_EXPOSURE"):
            load_and_verify_package(self.root)

    def test_package_rejects_disguised_prior_review_inside_required_role(self):
        authority = json.loads((self.root / "authority.json").read_text("utf-8"))
        authority["prior_assessment"] = {
            "review_identity": "action:ACT-001:input_invariants",
            "verdict": "APPROVED",
            "rationale_code": "SUPPORTED_EXACTLY",
        }
        self._replace_role("canonical_authority", authority)
        with self.assertRaisesRegex(PackageError, "PREVIOUS_VERDICT_EXPOSURE"):
            load_and_verify_package(self.root)

    def test_package_rejects_action_and_lifecycle_schema_drift(self):
        self._mutate_contract(lambda contract: contract.pop("compiler"))
        with self.assertRaisesRegex(PackageError, "CONTRACT_HASH_MISMATCH"):
            load_and_verify_package(self.root)
        self.temporary.cleanup()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        _write_package(self.root)
        self._mutate_contract(
            lambda contract: contract["lifecycles"][0].pop("current_states")
        )
        with self.assertRaisesRegex(PackageError, "CONTRACT_HASH_MISMATCH"):
            load_and_verify_package(self.root)

    def test_package_rejects_forged_output_schema_with_same_id(self):
        self._replace_role(
            "review_output_schema",
            {
                "$id": (
                    "https://joewrks.example/schemas/"
                    "semantic-review-output-1.0.schema.json"
                ),
                "type": "object",
            },
        )
        with self.assertRaisesRegex(PackageError, "OUTPUT_SCHEMA_VIOLATION"):
            load_and_verify_package(self.root)

    def test_package_rejects_declared_schema_identity_drift(self):
        manifest = json.loads((self.root / "manifest.json").read_text("utf-8"))
        item = next(
            entry
            for entry in manifest["files"]
            if entry["logical_role"] == "action_contract"
        )
        item["schema_identity"] = "forged/action-contract"
        self._rewrite_manifest(manifest)
        with self.assertRaisesRegex(PackageError, "PACKAGE_HASH_MISMATCH"):
            load_and_verify_package(self.root)

    def test_package_rejects_path_escape(self):
        manifest = json.loads((self.root / "manifest.json").read_text("utf-8"))
        manifest["files"][0]["path"] = "../outside.json"
        self._rewrite_manifest(manifest)
        with self.assertRaisesRegex(PackageError, "INVALID_PACKAGE_PATH"):
            load_and_verify_package(self.root)

    def test_package_rejects_active_superseded_lifecycle_sentinel(self):
        self.temporary.cleanup()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        _write_package(self.root, active_superseded=True)
        with self.assertRaisesRegex(PackageError, "ACTIVE_SUPERSEDED_SOURCE"):
            load_and_verify_package(self.root)

    def test_package_rejects_invalid_inactive_sentinel_provenance(self):
        self._mutate_contract(
            lambda contract: contract["lifecycles"][0]["superseded_sentinels"][0].update(
                {"value_sha256": "f" * 64}
            )
        )
        with self.assertRaisesRegex(PackageError, "INVALID_PROVENANCE"):
            load_and_verify_package(self.root)

    def test_package_rejects_invalid_contract_source_and_source_ref_index(self):
        self._mutate_contract(
            lambda contract: contract["actions"][0]["sources"][0].update(
                {"value_sha256": "f" * 64}
            ),
            rebind_sidecars=True,
        )
        with self.assertRaisesRegex(PackageError, "INVALID_PROVENANCE"):
            load_and_verify_package(self.root)

    def test_package_rejects_duplicate_contract_owner_identity(self):
        self._mutate_contract(
            lambda contract: contract["actions"].append(
                copy.deepcopy(contract["actions"][0])
            ),
            rebind_sidecars=True,
        )
        with self.assertRaisesRegex(PackageError, "CONTRACT_HASH_MISMATCH"):
            load_and_verify_package(self.root)
        self.temporary.cleanup()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        _write_package(self.root)
        self._mutate_contract(
            lambda contract: contract["actions"][0]["actor"].update(
                {"source_refs": [99]}
            ),
            rebind_sidecars=True,
        )
        with self.assertRaisesRegex(PackageError, "INVALID_PROVENANCE"):
            load_and_verify_package(self.root)

    def test_package_rejects_declared_byte_drift(self):
        (self.root / "authority.json").write_bytes(b"{}")
        with self.assertRaisesRegex(PackageError, "PACKAGE_HASH_MISMATCH"):
            load_and_verify_package(self.root)

    def test_run_envelope_binds_hashes_and_isolation_attestation(self):
        package = load_and_verify_package(self.root)
        attestation = {
            "fresh_context": True,
            "previous_verdict_access": False,
            "manifest_only_evidence": True,
        }
        envelope = {
            "review_run_id": "run-001",
            "reviewer_context_id": "context-001",
            "reviewer_input_package_hash": package["reviewer_input_package_hash"],
            "reviewer_brief_hash": package["role_hashes"]["reviewer_brief"],
            "isolation_attestation": attestation,
            "isolation_attestation_hash": sha256_bytes(_json_bytes(attestation)),
        }
        self.assertEqual(verify_run_envelope(envelope, package), envelope)
        envelope["isolation_attestation"]["previous_verdict_access"] = True
        with self.assertRaisesRegex(PackageError, "PREVIOUS_VERDICT_EXPOSURE"):
            verify_run_envelope(envelope, package)


if __name__ == "__main__":
    unittest.main()
