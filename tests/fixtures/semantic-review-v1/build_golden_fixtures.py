"""Materialize the 15 frozen, self-contained semantic-review golden packages."""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.hashing import (  # noqa: E402
    canonical_json_bytes,
    manifest_hash,
    package_hash,
    sha256_bytes,
)
from downstream.semantic_review.responsibility import (  # noqa: E402
    EXPECTED_ACTION_FIELDS,
    EXPECTED_LIFECYCLE_FIELDS,
)


HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "golden-cases.json"
OUTPUTS_PATH = HERE / "golden-review-outputs.json"
PROFILE_PATH = (
    SKILL_ROOT
    / "downstream"
    / "semantic_review"
    / "artifacts"
    / "responsibility-profile-v1.json"
)
BRIEF_PATH = PROFILE_PATH.with_name("reviewer-brief-v1.md")
OUTPUT_SCHEMA_PATH = (
    SKILL_ROOT / "downstream" / "schemas" / "semantic-review-output.schema.json"
)

FROZEN_RESULTS = {
    "G-001": ("REJECTED_CANDIDATE", "MISSING_OWNED_SEMANTIC"),
    "G-002": ("APPROVED", "SUPPORTED_EXACTLY"),
    "G-003": ("APPROVED", "SUPPORTED_EXACTLY"),
    "G-004": ("REJECTED_CANDIDATE", "MISSING_OWNED_SEMANTIC"),
    "G-005": ("APPROVED", "SUPPORTED_EXACTLY"),
    "G-006": ("REJECTED_CANDIDATE", "UNSUPPORTED_OVERREACH"),
    "G-007": ("REJECTED_CANDIDATE", "MISSING_OWNED_SEMANTIC"),
    "G-008": ("APPROVED", "SUPPORTED_EXACTLY"),
    "G-009": ("REJECTED_CANDIDATE", "CONTRADICTS_OWNER"),
    "G-010": ("REJECTED_CANDIDATE", "UNSUPPORTED_OVERREACH"),
    "G-011": ("APPROVED", "SUPPORTED_EXACTLY"),
    "G-012": ("INPUT_PACKAGE_ERROR", "ACTIVE_SUPERSEDED_SOURCE"),
    "G-013": ("INPUT_PACKAGE_ERROR", "INVALID_PROVENANCE"),
    "G-014": ("REJECTED_CANDIDATE", "UNSUPPORTED_OVERREACH"),
    "G-015": ("RUBRIC_ERROR", "RESPONSIBILITY_UNDEFINED"),
}

ROLE_PATHS = {
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


def _json_text(value: object) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def _semantic_field(value: object, *, review: bool) -> dict[str, object]:
    derivation = (
        {
            "kind": "REVIEW_REQUIRED",
            "explanation": "This golden focus identity requires semantic review.",
        }
        if review
        else {"kind": "MACHINE_DERIVED", "operator": "exact"}
    )
    return {"value": value, "source_refs": [0], "derivation": derivation}


def _candidate_value(case: dict[str, object], field: str) -> object:
    candidate = case.get("candidate_fixture", {})
    if isinstance(candidate, dict) and field in candidate:
        return candidate[field]
    return [f"{case['case_id']} candidate {field}"]


def _package_components(case: dict[str, object]) -> tuple[dict[str, str], str]:
    case_id = str(case["case_id"])
    current_text = str(case["canonical_fixture"].get("meaning", case["scenario"]))
    current_object = {
        "id": f"RULE-{case_id}",
        "status": "CURRENT",
        "text": current_text,
    }
    authority = {"objects": {"rules": [current_object]}}
    current_ref = {
        "object_id": current_object["id"],
        "pointer": "/objects/rules/0/text",
        "value_sha256": sha256_bytes(canonical_json_bytes(current_text)),
        "source_status": "CURRENT",
        "active": True,
    }

    focus_field = str(case.get("responsibility_fixture", {}).get("field", ""))
    focus_rule = str(case.get("responsibility_fixture", {}).get("rule_id", ""))
    if case_id == "G-015":
        focus_field, focus_rule = "preconditions", "FR-A06"
    has_identity = case_id != "G-012"
    focus_identity = (
        f"action:ACT-{case_id}:{focus_field}" if has_identity else ""
    )

    action = {
        "action_id": f"ACT-{case_id}",
        "sources": [current_ref],
        **{
            field: _semantic_field(
                _candidate_value(case, field),
                review=has_identity and field == focus_field,
            )
            for field in EXPECTED_ACTION_FIELDS
        },
    }
    lifecycle = {
        "lifecycle_id": f"LC-{case_id}",
        "sources": [current_ref],
        **{
            field: _semantic_field([f"{case_id} {field}"], review=False)
            for field in EXPECTED_LIFECYCLE_FIELDS
        },
        "superseded_sentinels": [],
    }
    if case_id == "G-012":
        superseded_text = "A superseded lifecycle transition."
        authority["objects"]["rules"].append(
            {"id": "RULE-G-012-OLD", "status": "SUPERSEDED", "text": superseded_text}
        )
        lifecycle["superseded_sentinels"] = [
            {
                "object_id": "RULE-G-012-OLD",
                "pointer": "/objects/rules/1/text",
                "value_sha256": sha256_bytes(canonical_json_bytes(superseded_text)),
                "source_status": "SUPERSEDED",
                "active": True,
            }
        ]

    contract = {
        "contract_schema_version": "joewrks.action-conformance/1.0",
        "compiler": {"id": "semantic-review-golden", "version": "1.0"},
        "source_authority": {
            "product_slug": f"golden-{case_id.lower()}",
            "approved_revision": 1,
            "approved_digest": f"pm-oracle-{case_id}",
            "canonical_state_sha256": sha256_bytes(canonical_json_bytes(authority)),
        },
        "actions": [action],
        "lifecycles": [lifecycle],
        "authority_assessment": {
            "structurally_valid": True,
            "provenance_valid": case_id not in {"G-012", "G-013"},
            "machine_derived_obligations_verified": True,
            "machine_derived_field_count": 38 - int(has_identity),
            "review_required_field_count": int(has_identity),
            "review_required_obligations_present": has_identity,
            "machine_verifiable_coverage": 1,
        },
    }
    contract["contract_hash"] = sha256_bytes(canonical_json_bytes(contract))

    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if case_id == "G-015":
        profile["obligation_taxonomy"].pop("non-input domain precondition")
    taxonomy = {
        rule_id: obligation_type
        for obligation_type, rule_id in profile.get("obligation_taxonomy", {}).items()
    }
    obligation_type = taxonomy.get(focus_rule, "deliberately unclassified")
    semantic_value = action[focus_field]["value"] if has_identity else None
    canonical_refs = [] if case_id == "G-013" else [current_ref]
    obligation_id = f"OBL-{case_id}-FOCUS"
    obligations = []
    identities = []
    if has_identity:
        obligations.append(
            {
                "obligation_id": obligation_id,
                "canonical_refs": canonical_refs,
                "obligation_type": obligation_type,
                "owner_kind": "action",
                "owner_id": f"ACT-{case_id}",
                "owning_field": focus_field,
                "responsibility_rule_id": focus_rule,
                "completeness_mode": (
                    profile["action"].get(focus_field, {}).get(
                        "completeness_mode", "LOCAL"
                    )
                ),
                "semantic_value_pointer": f"/actions/0/{focus_field}/value",
                "semantic_value_hash": sha256_bytes(canonical_json_bytes(semantic_value)),
                "allowed_sibling_refs": [],
                "required_test_refs": [f"TEST-{case_id}-FOCUS"],
                "projection_notes": str(case["scenario"]),
            }
        )
        provenance_hashes = sorted(
            sha256_bytes(canonical_json_bytes(reference)) for reference in canonical_refs
        )
        identities.append(
            {
                "review_identity": focus_identity,
                "owner_kind": "action",
                "owner_id": f"ACT-{case_id}",
                "semantic_field": focus_field,
                "semantic_value_hash": sha256_bytes(canonical_json_bytes(semantic_value)),
                "provenance_hashes": provenance_hashes,
                "provenance_set_hash": sha256_bytes(
                    canonical_json_bytes(provenance_hashes)
                ),
                "responsibility_rule_id": focus_rule,
                "completeness_mode": obligations[0]["completeness_mode"],
                "semantic_obligation_ids": [obligation_id],
            }
        )

    components = {
        "canonical_authority": _json_text(authority),
        "action_contract": _json_text(contract),
        "provenance_inventory": _json_text(
            {
                "schema_version": "joewrks.semantic-review-provenance-inventory/1.0",
                "records": [] if case_id == "G-013" else [current_ref],
            }
        ),
        "responsibility_profile": (
            _json_text(profile)
            if case_id == "G-015"
            else PROFILE_PATH.read_text(encoding="utf-8")
        ),
        "semantic_obligation_index": _json_text(
            {
                "schema_version": "joewrks.semantic-obligation-index/1.0",
                "contract_hash": contract["contract_hash"],
                "obligations": obligations,
            }
        ),
        "reviewer_brief": BRIEF_PATH.read_text(encoding="utf-8"),
        "review_output_schema": OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"),
        "review_identity_inventory": _json_text(
            {
                "schema_version": "joewrks.semantic-review-identity-inventory/1.0",
                "contract_hash": contract["contract_hash"],
                "identities": identities,
            }
        ),
        "exclusion_manifest": _json_text(
            {
                "previous_reviewer_verdicts_present": False,
                "hidden_answers_present": False,
                "implementation_outcomes_present": False,
                "unrelated_product_evidence_present": False,
            }
        ),
    }
    return components, focus_identity


def _build_package(case: dict[str, object]) -> tuple[dict[str, object], str]:
    components, focus_identity = _package_components(case)
    files = []
    embedded_files = {}
    for role, path in ROLE_PATHS.items():
        text = components[role]
        data = text.encode("utf-8")
        files.append(
            {
                "logical_role": role,
                "path": path,
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "schema_identity": f"joewrks.semantic-review-role/{role}",
            }
        )
        embedded_files[path] = {"encoding": "utf-8", "text": text}
    manifest = {
        "schema_version": "joewrks.semantic-review-input/1.0",
        "previous_reviewer_verdicts_present": False,
        "files": files,
    }
    manifest["reviewer_input_manifest_hash"] = manifest_hash(manifest)
    return (
        {
            "schema_version": "joewrks.semantic-review-golden-package/1.0",
            "manifest": manifest,
            "reviewer_input_package_hash": package_hash(
                manifest["reviewer_input_manifest_hash"], files
            ),
            "embedded_files": embedded_files,
        },
        focus_identity,
    )


def _parse_role(package: dict[str, object], role: str) -> object:
    item = next(
        entry for entry in package["manifest"]["files"] if entry["logical_role"] == role
    )
    text = package["embedded_files"][item["path"]]["text"]
    return text if role == "reviewer_brief" else json.loads(text)


def _role_hash(package: dict[str, object], role: str) -> str:
    return next(
        entry["sha256"]
        for entry in package["manifest"]["files"]
        if entry["logical_role"] == role
    )


def _build_output(case: dict[str, object]) -> dict[str, object]:
    case_id = case["case_id"]
    package = case["reviewer_package"]
    manifest = package["manifest"]
    contract = _parse_role(package, "action_contract")
    obligation_index = _parse_role(package, "semantic_obligation_index")
    identity_inventory = _parse_role(package, "review_identity_inventory")
    identities = identity_inventory["identities"]
    verdict, rationale = FROZEN_RESULTS[case_id]
    attestation = {
        "fresh_context": True,
        "previous_verdict_access": False,
        "manifest_only_evidence": True,
    }
    envelope = {
        "review_run_id": f"golden-run-{case_id}",
        "reviewer_context_id": f"golden-context-{case_id}",
        "reviewer_input_package_hash": package["reviewer_input_package_hash"],
        "reviewer_brief_hash": _role_hash(package, "reviewer_brief"),
        "isolation_attestation": attestation,
        "isolation_attestation_hash": sha256_bytes(canonical_json_bytes(attestation)),
    }
    preflight = []
    records = []
    if case["review_phase"] == "preflight":
        preflight.append(
            {
                "verdict": verdict,
                "rationale_code": rationale,
                "scope": f"golden:{case_id}",
                "canonical_evidence_refs": [],
                "reviewer_explanation": str(case["scenario"]),
            }
        )
    else:
        obligations = {
            item["obligation_id"]: item for item in obligation_index["obligations"]
        }
        for identity in identities:
            owned = [
                obligations[obligation_id]
                for obligation_id in identity["semantic_obligation_ids"]
            ]
            record_verdict, record_rationale = (
                (verdict, rationale)
                if identity["review_identity"] == case["focus_review_identity"]
                else ("APPROVED", "SUPPORTED_EXACTLY")
            )
            records.append(
                {
                    "review_schema_version": "joewrks.semantic-review/1.0",
                    "reviewer_brief_hash": envelope["reviewer_brief_hash"],
                    "reviewer_input_manifest_hash": manifest[
                        "reviewer_input_manifest_hash"
                    ],
                    "contract_hash": contract["contract_hash"],
                    "review_identity": identity["review_identity"],
                    "owner_kind": identity["owner_kind"],
                    "owner_id": identity["owner_id"],
                    "semantic_field": identity["semantic_field"],
                    "semantic_value_hash": identity["semantic_value_hash"],
                    "provenance_hashes": identity["provenance_hashes"],
                    "provenance_set_hash": identity["provenance_set_hash"],
                    "responsibility_rule_id": identity["responsibility_rule_id"],
                    "completeness_mode": identity["completeness_mode"],
                    "sibling_review_identity_refs": [],
                    "semantic_obligation_ids": identity["semantic_obligation_ids"],
                    "test_obligation_refs": sorted(
                        {
                            test_ref
                            for obligation in owned
                            for test_ref in obligation["required_test_refs"]
                        }
                    ),
                    "verdict": record_verdict,
                    "rationale_code": record_rationale,
                    "canonical_evidence_refs": sorted(
                        [
                            reference
                            for obligation in owned
                            for reference in obligation["canonical_refs"]
                        ],
                        key=canonical_json_bytes,
                    ),
                    "reviewer_explanation": str(case["scenario"]),
                }
            )
    counts = Counter(
        item["verdict"] for item in [*preflight, *records]
    )
    output = {
        "review_schema_version": "joewrks.semantic-review/1.0",
        "review_run_id": envelope["review_run_id"],
        "reviewer_context_id": envelope["reviewer_context_id"],
        "isolation_attestation_hash": envelope["isolation_attestation_hash"],
        "reviewer_brief_hash": envelope["reviewer_brief_hash"],
        "reviewer_input_manifest_hash": manifest["reviewer_input_manifest_hash"],
        "reviewer_input_package_hash": package["reviewer_input_package_hash"],
        "contract_hash": contract["contract_hash"],
        "responsibility_profile_hash": _role_hash(package, "responsibility_profile"),
        "semantic_obligation_index_hash": _role_hash(
            package, "semantic_obligation_index"
        ),
        "review_identity_inventory_hash": _role_hash(
            package, "review_identity_inventory"
        ),
        "preflight_errors": preflight,
        "records": records,
        "summary": {
            "expected_identity_count": len(identities),
            "record_count": len(records),
            "unique_identity_count": len(
                {record["review_identity"] for record in records}
            ),
            "pending_count": 0,
            "verdict_counts": {
                "APPROVED": counts["APPROVED"],
                "REJECTED_CANDIDATE": counts["REJECTED_CANDIDATE"],
                "RUBRIC_ERROR": counts["RUBRIC_ERROR"],
                "INPUT_PACKAGE_ERROR": counts["INPUT_PACKAGE_ERROR"],
            },
            "complete": not preflight,
        },
    }
    return {
        "case_id": case_id,
        "case_manifest_hash": case["case_manifest_hash"],
        "run_envelope": envelope,
        "review_output": output,
    }


def main() -> None:
    source_cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = []
    for source in source_cases:
        case = copy.deepcopy(source)
        case.pop("case_manifest_hash", None)
        case.pop("reviewer_package", None)
        case.pop("focus_review_identity", None)
        package, focus_identity = _build_package(case)
        case["focus_review_identity"] = focus_identity
        case["reviewer_package"] = package
        case["case_manifest_hash"] = sha256_bytes(canonical_json_bytes(case))
        cases.append(case)
    outputs = [_build_output(case) for case in cases]
    CASES_PATH.write_text(
        json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUTPUTS_PATH.write_text(
        json.dumps(outputs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
