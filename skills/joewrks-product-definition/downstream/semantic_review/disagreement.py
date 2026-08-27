"""Hash-bound classification of frozen cross-review disagreements."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

from .hashing import canonical_json_bytes, sha256_bytes


CLOSED_CAUSE_CODES = {
    "REVIEWER_EXECUTION_ERROR",
    "PACKAGE_DEFECT",
    "CANDIDATE_IDENTITY_DRIFT",
    "NORMATIVE_RESPONSIBILITY",
    "NORMATIVE_COMPLETENESS",
    "UNRESOLVED_NORMATIVE",
}
NORMATIVE_CAUSES = {
    "NORMATIVE_RESPONSIBILITY",
    "NORMATIVE_COMPLETENESS",
    "UNRESOLVED_NORMATIVE",
}
STRUCTURAL_CAUSES = {"PACKAGE_DEFECT", "CANDIDATE_IDENTITY_DRIFT"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_CLASSIFICATION_FIELDS = {
    "review_identity",
    "responsibility_rule_id",
    "observed_verdict_rationale_pairs",
    "semantic_obligation_ids",
    "cited_rule_hash",
    "cited_evidence_hashes",
    "classifier_context_id",
    "cause_code",
    "interpretation",
    "semantic_field",
    "completeness_mode",
    "rationale_code",
    "canonical_obligation_type",
}


def responsibility_rule_hash(
    rule_id: str, profile: dict[str, Any] | None = None
) -> str:
    """Return the exact frozen normative rule hash cited by classifications."""

    if profile is None:
        profile_path = (
            Path(__file__).resolve().parent
            / "artifacts"
            / "responsibility-profile-v1.json"
        )
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    for kind in ("action", "lifecycle"):
        for rule in profile.get(kind, {}).values():
            if rule.get("responsibility_rule_id") == rule_id:
                exact_rule = {
                    key: value
                    for key, value in rule.items()
                    if key != "brief_owns_label"
                }
                return sha256_bytes(canonical_json_bytes(exact_rule))
    raise ValueError(f"unknown responsibility rule: {rule_id}")


def _records_by_identity(output: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["review_identity"]: record for record in output.get("records", [])}


def _pair(record: dict[str, Any]) -> str:
    return f"{record['verdict']}/{record['rationale_code']}"


def _classification_valid(
    classification: dict[str, Any],
    identity: str,
    records: list[dict[str, Any]],
    responsibility_profile: dict[str, Any],
) -> bool:
    if set(classification) != REQUIRED_CLASSIFICATION_FIELDS:
        return False
    first = records[0]
    if classification["review_identity"] != identity:
        return False
    if classification["responsibility_rule_id"] != first["responsibility_rule_id"]:
        return False
    if classification["semantic_field"] != first["semantic_field"]:
        return False
    if classification["completeness_mode"] != first["completeness_mode"]:
        return False
    observed_pairs = sorted({_pair(record) for record in records})
    if classification["observed_verdict_rationale_pairs"] != observed_pairs:
        return False
    obligation_ids = sorted(
        {item for record in records for item in record["semantic_obligation_ids"]}
    )
    if classification["semantic_obligation_ids"] != obligation_ids:
        return False
    evidence_hashes = sorted(
        {
            evidence["value_sha256"]
            for record in records
            for evidence in record["canonical_evidence_refs"]
        }
    )
    if classification["cited_evidence_hashes"] != evidence_hashes:
        return False
    if SHA256_RE.fullmatch(str(classification["cited_rule_hash"])) is None:
        return False
    try:
        expected_rule_hash = responsibility_rule_hash(
            first["responsibility_rule_id"], responsibility_profile
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False
    if classification["cited_rule_hash"] != expected_rule_hash:
        return False
    if classification["cause_code"] not in CLOSED_CAUSE_CODES:
        return False
    if not isinstance(classification["classifier_context_id"], str) or not classification[
        "classifier_context_id"
    ].strip():
        return False
    if not isinstance(classification["interpretation"], str) or not classification[
        "interpretation"
    ].strip():
        return False
    if classification["cause_code"] == "REVIEWER_EXECUTION_ERROR" and not (
        classification["cited_rule_hash"] and classification["cited_evidence_hashes"]
    ):
        return False
    return True


def validate_disagreement_classifications(
    outputs: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    responsibility_profile: dict[str, Any],
) -> dict[str, Any]:
    """Require one closed, evidence-bound classification per frozen disagreement."""

    record_maps = [_records_by_identity(output) for output in outputs]
    identity_sets = [set(mapping) for mapping in record_maps]
    identities = set.intersection(*identity_sets) if identity_sets else set()
    disagreements: dict[str, list[dict[str, Any]]] = {}
    for identity in sorted(identities):
        records = [mapping[identity] for mapping in record_maps]
        if len({_pair(record) for record in records}) > 1:
            disagreements[identity] = records

    classification_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for classification in classifications:
        classification_groups[classification.get("review_identity", "")].append(
            classification
        )
    resolved: dict[str, dict[str, Any]] = {}
    invalid_or_missing: list[str] = []
    for identity, records in disagreements.items():
        candidates = classification_groups.get(identity, [])
        if len(candidates) != 1 or not _classification_valid(
            candidates[0], identity, records, responsibility_profile
        ):
            invalid_or_missing.append(identity)
            resolved[identity] = {
                "review_identity": identity,
                "responsibility_rule_id": records[0]["responsibility_rule_id"],
                "cause_code": "UNRESOLVED_NORMATIVE",
                "interpretation": "missing or invalid hash-bound classification",
                "semantic_field": records[0]["semantic_field"],
                "completeness_mode": records[0]["completeness_mode"],
                "rationale_code": records[0]["rationale_code"],
                "canonical_obligation_type": "unresolved",
            }
        else:
            resolved[identity] = candidates[0]
    extras = sorted(set(classification_groups) - set(disagreements))
    invalid_or_missing.extend(extras)

    rule_counts = Counter(
        classification["responsibility_rule_id"] for classification in resolved.values()
    )
    cluster_fields = (
        "semantic_field",
        "responsibility_rule_id",
        "completeness_mode",
        "rationale_code",
        "canonical_obligation_type",
    )
    clusters = {
        field: dict(
            Counter(str(classification[field]) for classification in resolved.values())
        )
        for field in cluster_fields
    }
    return {
        "disagreement_count": len(disagreements),
        "classified_count": len(resolved) - len(set(invalid_or_missing) & set(resolved)),
        "invalid_or_missing_identities": sorted(set(invalid_or_missing)),
        "unresolved_normative_count": sum(
            classification["cause_code"] in NORMATIVE_CAUSES
            for classification in resolved.values()
        )
        + len(extras),
        "structural_cause_count": sum(
            classification["cause_code"] in STRUCTURAL_CAUSES
            for classification in resolved.values()
        ),
        "same_rule_disagreement_counts": dict(rule_counts),
        "repeated_rule_ids": sorted(
            rule for rule, count in rule_counts.items() if count >= 2
        ),
        "classifications": resolved,
        "clusters": clusters,
    }
