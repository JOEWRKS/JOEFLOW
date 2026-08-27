import copy
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.hashing import canonical_json_bytes, sha256_bytes


SCHEMA_PATH = (
    SKILL_ROOT / "downstream" / "schemas" / "semantic-review-output.schema.json"
)
BASE_HASHES = {
    "reviewer_brief_hash": "1" * 64,
    "reviewer_input_manifest_hash": "2" * 64,
    "reviewer_input_package_hash": "3" * 64,
    "contract_hash": "4" * 64,
    "responsibility_profile_hash": "5" * 64,
    "semantic_obligation_index_hash": "6" * 64,
    "review_identity_inventory_hash": "7" * 64,
}


def _identity(index):
    return f"action:ACT-{index:04d}:input_invariants"


def _stable_hash(prefix, index):
    return sha256_bytes(f"{prefix}:{index}".encode("ascii"))


def make_run_set(verdicts, *, run_count=3, rule_id="FR-A09"):
    expected = sorted(_identity(index) for index in range(len(verdicts)))
    inventory = {
        identity: {
            "semantic_value_hash": _stable_hash("semantic", index),
            "semantic_value_text": f"synthetic semantic value {index}",
            "provenance_set_hash": _stable_hash("provenance-set", index),
            "responsibility_rule_id": rule_id,
            "completeness_mode": "LOCAL",
        }
        for index, identity in enumerate(expected)
    }
    base_package = {
        **BASE_HASHES,
        "previous_reviewer_verdicts_present": False,
        "reviewer_brief_text": "Use frozen composition rules.\n",
        "responsibility_profile_excerpt": {
            rule_id: {"completeness_mode": "LOCAL"}
        },
        "manifest_declared_files": [
            "canonical_authority",
            "action_contract",
            "responsibility_profile",
            "reviewer_brief",
        ],
        "role_hashes": {"reviewer_brief": BASE_HASHES["reviewer_brief_hash"]},
        "review_output_schema": json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
        "expected_identities": expected,
        "identity_inventory": inventory,
    }
    packages = [copy.deepcopy(base_package) for _ in range(run_count)]
    envelopes = []
    outputs = []
    for run_index in range(run_count):
        attestation = {
            "fresh_context": True,
            "previous_verdict_access": False,
            "manifest_only_evidence": True,
        }
        envelope = {
            "review_run_id": f"run-{run_index + 1:03d}",
            "reviewer_context_id": f"context-{run_index + 1:03d}",
            "reviewer_input_package_hash": BASE_HASHES[
                "reviewer_input_package_hash"
            ],
            "reviewer_brief_hash": BASE_HASHES["reviewer_brief_hash"],
            "isolation_attestation": attestation,
            "isolation_attestation_hash": sha256_bytes(
                canonical_json_bytes(attestation)
            ),
        }
        records = []
        for index, verdict in enumerate(verdicts):
            identity = expected[index]
            rationale = (
                "SUPPORTED_EXACTLY"
                if verdict == "APPROVED"
                else "MISSING_OWNED_SEMANTIC"
            )
            records.append(
                {
                    "review_schema_version": "joewrks.semantic-review/1.0",
                    "reviewer_brief_hash": BASE_HASHES["reviewer_brief_hash"],
                    "reviewer_input_manifest_hash": BASE_HASHES[
                        "reviewer_input_manifest_hash"
                    ],
                    "contract_hash": BASE_HASHES["contract_hash"],
                    "review_identity": identity,
                    "owner_kind": "action",
                    "owner_id": f"ACT-{index:04d}",
                    "semantic_field": "input_invariants",
                    "semantic_value_hash": inventory[identity]["semantic_value_hash"],
                    "provenance_hashes": [_stable_hash("provenance", index)],
                    "provenance_set_hash": inventory[identity]["provenance_set_hash"],
                    "responsibility_rule_id": rule_id,
                    "completeness_mode": "LOCAL",
                    "sibling_review_identity_refs": [],
                    "semantic_obligation_ids": [f"OBL-INPUT-{index:04d}"],
                    "test_obligation_refs": [f"TEST-INPUT-{index:04d}"],
                    "verdict": verdict,
                    "rationale_code": rationale,
                    "canonical_evidence_refs": [
                        {
                            "object_id": f"RULE-{index:04d}",
                            "pointer": f"/objects/rules/{index}/text",
                            "value_sha256": _stable_hash("canonical", index),
                            "source_status": "CURRENT",
                            "active": True,
                        }
                    ],
                    "reviewer_explanation": "The frozen owner rule determines this result.",
                }
            )
        counts = Counter(record["verdict"] for record in records)
        output = {
            "review_schema_version": "joewrks.semantic-review/1.0",
            "review_run_id": envelope["review_run_id"],
            "reviewer_context_id": envelope["reviewer_context_id"],
            "isolation_attestation_hash": envelope["isolation_attestation_hash"],
            **BASE_HASHES,
            "preflight_errors": [],
            "records": records,
            "summary": {
                "expected_identity_count": len(expected),
                "record_count": len(expected),
                "unique_identity_count": len(expected),
                "pending_count": 0,
                "verdict_counts": {
                    "APPROVED": counts["APPROVED"],
                    "REJECTED_CANDIDATE": counts["REJECTED_CANDIDATE"],
                    "RUBRIC_ERROR": 0,
                    "INPUT_PACKAGE_ERROR": 0,
                },
                "complete": True,
            },
        }
        envelopes.append(envelope)
        outputs.append(output)
    return packages, envelopes, outputs


def replace_verdict_and_recount(output, identity, verdict, rationale):
    target = next(
        record for record in output["records"] if record["review_identity"] == identity
    )
    target["verdict"] = verdict
    target["rationale_code"] = rationale
    counts = Counter(record["verdict"] for record in output["records"])
    output["summary"]["verdict_counts"] = {
        "APPROVED": counts["APPROVED"],
        "REJECTED_CANDIDATE": counts["REJECTED_CANDIDATE"],
        "RUBRIC_ERROR": counts["RUBRIC_ERROR"],
        "INPUT_PACKAGE_ERROR": counts["INPUT_PACKAGE_ERROR"],
    }


def passing_golden_report():
    from fractions import Fraction

    return {
        "case_count": 15,
        "verdict_accuracy": Fraction(1, 1),
        "rationale_code_accuracy": Fraction(1, 1),
        "unexpected_rubric_error_count": 0,
        "unexpected_input_package_error_count": 0,
    }


def disagreement_classification(
    identity,
    rule_id="FR-A09",
    *,
    cause_code="REVIEWER_EXECUTION_ERROR",
    interpretation="incorrectly required sibling-owned semantics in this LOCAL field",
):
    owner_id = identity.split(":")[1]
    index = owner_id.removeprefix("ACT-")
    return {
        "review_identity": identity,
        "responsibility_rule_id": rule_id,
        "observed_verdict_rationale_pairs": [
            "APPROVED/SUPPORTED_EXACTLY",
            "REJECTED_CANDIDATE/MISSING_OWNED_SEMANTIC",
        ],
        "semantic_obligation_ids": [f"OBL-INPUT-{index}"],
        "cited_rule_hash": "a" * 64,
        "cited_evidence_hashes": [_stable_hash("canonical", int(index))],
        "classifier_context_id": f"classifier-{identity}",
        "cause_code": cause_code,
        "interpretation": interpretation,
        "semantic_field": "input_invariants",
        "completeness_mode": "LOCAL",
        "rationale_code": "MISSING_OWNED_SEMANTIC",
        "canonical_obligation_type": "input validity",
    }
