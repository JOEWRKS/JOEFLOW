"""Materialize the answer-blind human packet from the frozen reviewer packages."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CALIBRATION_ROOT = Path(__file__).resolve().parent
PACKET_ROOT = CALIBRATION_ROOT / "semantic-review-calibration-v1"
GOLDEN_CASES_PATH = (
    ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-cases.json"
)
PAYLOAD_PATH = PACKET_ROOT / "human-adjudication-common-evidence.json"
MANIFEST_PATH = PACKET_ROOT / "human-adjudication-manifest.json"
FORM_PATHS = (
    PACKET_ROOT / "human-adjudicator-a-response-form.json",
    PACKET_ROOT / "human-adjudicator-b-response-form.json",
)
PROTOCOL_DOC_PATH = CALIBRATION_ROOT / "CALIBRATION_CONTROLLER_PROTOCOL.md"
EXTERNAL_VALIDATION_STATUS = "OPTIONAL_EXTERNAL_VALIDATION_NOT_REQUIRED_FOR_V043_CALIBRATION"

ALLOWED_VERDICTS = [
    "APPROVED",
    "REJECTED_CANDIDATE",
    "RUBRIC_ERROR",
    "INPUT_PACKAGE_ERROR",
]
ALLOWED_RATIONALE_CODES = [
    "SUPPORTED_EXACTLY",
    "MISSING_OWNED_SEMANTIC",
    "MISSING_REQUIRED_REFERENCE",
    "UNSUPPORTED_OVERREACH",
    "CONTRADICTS_OWNER",
    "INVALID_DUPLICATION",
    "INVALID_PROVENANCE",
    "ACTIVE_SUPERSEDED_SOURCE",
    "RESPONSIBILITY_UNDEFINED",
    "COMPLETENESS_UNDEFINED",
    "PACKAGE_HASH_MISMATCH",
    "BRIEF_HASH_MISMATCH",
    "CONTRACT_HASH_MISMATCH",
    "RESPONSIBILITY_PROFILE_HASH_MISMATCH",
    "OBLIGATION_INDEX_HASH_MISMATCH",
    "IDENTITY_SET_MISMATCH",
    "PREVIOUS_VERDICT_EXPOSURE",
    "OUTPUT_SCHEMA_VIOLATION",
]

CANDIDATE_COMPARISON_FACTS = {
    "G-001": [
        "The candidate input_invariants array contains 0 entries.",
        "The canonical clause states a non-empty reason-input requirement.",
    ],
    "G-002": [
        "The candidate input_invariants array contains 1 entry.",
        "That entry is `reason is non-empty`.",
    ],
    "G-003": [
        "The candidate input_invariants array contains 0 entries.",
        "The same candidate action has a relationship_predicate field with 1 entry.",
    ],
    "G-004": [
        "The candidate visible_error array contains 1 entry.",
        "That entry is `show validation category`.",
    ],
    "G-005": [
        "The candidate visible_error array contains 2 entries.",
        "Those entries are `present error` and `preserve input`.",
    ],
    "G-006": [
        "The candidate visible_error array contains 2 entries.",
        "Those entries are `show error` and `offer retry`.",
    ],
    "G-007": [
        "The candidate test_obligations array contains 0 entries.",
        "The semantic obligation records the stable reference `TEST-G-007-FOCUS`.",
    ],
    "G-008": [
        "The candidate test_obligations array contains the reference `TEST-G008`.",
        "The frozen candidate fixture records its copied-business-prose flag as false.",
    ],
    "G-009": [
        "The candidate test_obligations array contains the reference `TEST-G009`.",
        "The frozen candidate fixture also carries prose requiring a result distinct from the canonical permitted result.",
    ],
    "G-010": [
        "The materialized candidate preconditions array contains 1 opaque fixture entry.",
        "The frozen candidate fixture lists one `declared constraint` and one additional constraint.",
    ],
    "G-011": [
        "The frozen candidate fixture describes visible_success as visible readback.",
        "The same candidate action has an authoritative-mutation sibling field with 1 entry.",
    ],
    "G-012": [
        "The candidate lifecycle superseded_sentinels array contains 1 source reference.",
        "That reference has source_status SUPERSEDED and active true.",
    ],
    "G-013": [
        "The candidate input_invariants array contains 1 opaque fixture entry.",
        "The identity inventory contains 0 provenance hashes and the provenance inventory contains 0 records.",
    ],
    "G-014": [
        "The materialized candidate input_invariants array contains 1 opaque fixture entry.",
        "The frozen candidate fixture states `The bounded input is forbidden.`.",
    ],
    "G-015": [
        "The candidate preconditions array contains 1 opaque fixture entry.",
        "The frozen candidate fixture states `A candidate projection exists.`.",
    ],
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def embedded_text(golden_case: dict[str, Any], logical_name: str) -> str:
    return golden_case["reviewer_package"]["embedded_files"][logical_name]["text"]


def embedded_json(golden_case: dict[str, Any], logical_name: str) -> Any:
    return json.loads(embedded_text(golden_case, logical_name))


def resolve_pointer(document: Any, pointer: str) -> Any:
    value = document
    for token in pointer.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def normalized_sibling_refs(golden_case: dict[str, Any]) -> list[str]:
    fixture = golden_case["candidate_fixture"]
    values = fixture.get("sibling_references", [])
    if "sibling_reference" in fixture:
        values = [fixture["sibling_reference"], *values]
    return [
        re.sub(r"\b(ACT|LC)-G(\d{3})\b", r"\1-G-\2", value)
        for value in values
    ]


def build_case(golden_case: dict[str, Any]) -> dict[str, Any]:
    case_id = golden_case["case_id"]
    authority = embedded_json(golden_case, "authority.json")
    contract = embedded_json(golden_case, "contract.json")
    provenance = embedded_json(golden_case, "provenance.json")["records"]
    obligations = embedded_json(golden_case, "obligations.json")["obligations"]
    identities = embedded_json(golden_case, "identities.json")["identities"]
    responsibility_text = embedded_text(golden_case, "responsibility.json")
    responsibility = json.loads(responsibility_text)
    authority_rule = authority["objects"]["rules"][0]

    canonical_refs = obligations[0]["canonical_refs"] if obligations else provenance[:1]
    if canonical_refs:
        canonical_evidence = canonical_refs[0]
    else:
        canonical_evidence = {
            "source_lookup_status": "ABSENT",
            "authority_object": {
                "object_id": authority_rule["id"],
                "pointer": "/objects/rules/0/text",
                "status": authority_rule["status"],
                "value_sha256": sha256(canonical_bytes(authority_rule["text"])),
            },
        }

    profile_hash = sha256(responsibility_text.encode("utf-8"))
    if identities:
        identity = identities[0]
        obligation = obligations[0]
        pointer = obligation["semantic_value_pointer"]
        candidate_value = resolve_pointer(contract, pointer)
        owner_kind = identity["owner_kind"]
        semantic_field = identity["semantic_field"]
        rule_semantics = responsibility[owner_kind][semantic_field]
        taxonomy_key = obligation["obligation_type"]
        taxonomy = responsibility["obligation_taxonomy"]
        taxonomy_status = "PRESENT" if taxonomy_key in taxonomy else "ABSENT"
        profile_evidence = {
            "responsibility_profile_sha256": profile_hash,
            "field_lookup_path": f"/{owner_kind}/{semantic_field}",
            "field_lookup_status": "PRESENT",
            "rule_semantics": rule_semantics,
            "obligation_taxonomy_lookup": {
                "lookup_path": f"/obligation_taxonomy/{taxonomy_key}",
                "lookup_status": taxonomy_status,
                "declared_responsibility_rule_id": identity[
                    "responsibility_rule_id"
                ],
            },
        }
        obligation_evidence = {
            key: obligation[key]
            for key in (
                "obligation_id",
                "obligation_type",
                "owner_kind",
                "owner_id",
                "owning_field",
                "responsibility_rule_id",
                "completeness_mode",
                "semantic_value_pointer",
                "semantic_value_hash",
                "canonical_refs",
                "allowed_sibling_refs",
                "required_test_refs",
            )
        }
        candidate_evidence = {
            "review_identity": identity["review_identity"],
            "semantic_value_pointer": pointer,
            "semantic_value_sha256": identity["semantic_value_hash"],
        }
        responsibility_rule_id = identity["responsibility_rule_id"]
        completeness_mode = identity["completeness_mode"]
    else:
        pointer = "/lifecycles/0/superseded_sentinels"
        candidate_value = resolve_pointer(contract, pointer)
        candidate_evidence = {
            "review_identity_lookup_status": "ABSENT",
            "semantic_value_pointer": pointer,
            "semantic_value_sha256": sha256(canonical_bytes(candidate_value)),
        }
        obligation_evidence = {
            "identity_lookup_status": "ABSENT",
            "obligation_lookup_status": "ABSENT",
        }
        profile_evidence = {
            "responsibility_profile_sha256": profile_hash,
            "field_lookup_path": None,
            "field_lookup_status": "NOT_APPLICABLE",
            "rule_semantics": None,
            "obligation_taxonomy_lookup": {
                "lookup_path": None,
                "lookup_status": "NOT_APPLICABLE",
                "declared_responsibility_rule_id": None,
            },
        }
        responsibility_rule_id = None
        completeness_mode = None

    return {
        "case_id": case_id,
        "canonical_clause": authority_rule["text"],
        "canonical_evidence": canonical_evidence,
        "candidate_semantic_value": candidate_value,
        "candidate_evidence": candidate_evidence,
        "candidate_comparison_facts": CANDIDATE_COMPARISON_FACTS[case_id],
        "semantic_obligation_evidence": obligation_evidence,
        "responsibility_rule_id": responsibility_rule_id,
        "completeness_mode": completeness_mode,
        "responsibility_profile_evidence": profile_evidence,
        "relevant_sibling_refs": normalized_sibling_refs(golden_case),
        "allowed_verdicts": ALLOWED_VERDICTS,
        "allowed_rationale_codes": ALLOWED_RATIONALE_CODES,
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def materialize() -> tuple[str, int]:
    golden_cases = json.loads(GOLDEN_CASES_PATH.read_text(encoding="utf-8"))
    payload = {
        "schema_version": "joewrks.semantic-review-human-adjudication-evidence/1.0",
        "source": "frozen G-001 through G-015 reviewer packages and case evidence",
        "cases": [build_case(golden_case) for golden_case in golden_cases],
    }
    write_json(PAYLOAD_PATH, payload)
    payload_bytes = PAYLOAD_PATH.read_bytes()
    payload_reference = {
        "path": PAYLOAD_PATH.name,
        "sha256": sha256(payload_bytes),
        "bytes": len(payload_bytes),
    }

    manifest = {
        "schema_version": "joewrks.semantic-review-human-adjudication-manifest/1.0",
        "common_evidence_payload": payload_reference,
        "response_forms": [
            {
                "path": FORM_PATHS[0].name,
                "non_normative_form_identity": "HUMAN-ADJUDICATOR-A",
            },
            {
                "path": FORM_PATHS[1].name,
                "non_normative_form_identity": "HUMAN-ADJUDICATOR-B",
            },
        ],
        "required_independent_human_responses": 2,
        "completed_independent_human_responses": 0,
        "HUMAN_ADJUDICATION_COMPLETE": "NO",
        "external_validation_status": EXTERNAL_VALIDATION_STATUS,
        "HUMAN_ADJUDICATION_REQUIRED": "NO",
    }
    write_json(MANIFEST_PATH, manifest)

    responses = [
        {"case_id": f"G-{index:03d}", "verdict": None, "rationale_code": None}
        for index in range(1, 16)
    ]
    for identity, path in zip(
        ("HUMAN-ADJUDICATOR-A", "HUMAN-ADJUDICATOR-B"), FORM_PATHS
    ):
        write_json(
            path,
            {
                "schema_version": "joewrks.semantic-review-human-adjudication-response-form/1.0",
                "non_normative_form_identity": identity,
                "common_evidence_payload": payload_reference,
                "HUMAN_ADJUDICATION_COMPLETE": "NO",
                "external_validation_status": EXTERNAL_VALIDATION_STATUS,
                "HUMAN_ADJUDICATION_REQUIRED": "NO",
                "responses": responses,
            },
        )

    protocol_doc = PROTOCOL_DOC_PATH.read_text(encoding="utf-8")
    protocol_doc = re.sub(
        r"(?m)^- Common human evidence payload SHA-256: `[0-9a-f]{64}`$",
        f"- Common human evidence payload SHA-256: `{payload_reference['sha256']}`",
        protocol_doc,
    )
    PROTOCOL_DOC_PATH.write_text(protocol_doc, encoding="utf-8", newline="\n")
    return payload_reference["sha256"], payload_reference["bytes"]


if __name__ == "__main__":
    digest, byte_count = materialize()
    print(f"common_payload_sha256={digest}")
    print(f"common_payload_bytes={byte_count}")
