"""Validation for deterministic ``joewrks.semantic-review/1.0`` outputs."""

from __future__ import annotations

from collections import Counter
from typing import Any

from downstream.schema_validation import SchemaValidationError, validate_instance

from .package import PackageError, verify_run_envelope


VERDICTS = {
    "APPROVED",
    "REJECTED_CANDIDATE",
    "RUBRIC_ERROR",
    "INPUT_PACKAGE_ERROR",
}
RATIONALES_BY_VERDICT = {
    "APPROVED": {"SUPPORTED_EXACTLY"},
    "REJECTED_CANDIDATE": {
        "MISSING_OWNED_SEMANTIC",
        "MISSING_REQUIRED_REFERENCE",
        "UNSUPPORTED_OVERREACH",
        "CONTRADICTS_OWNER",
        "INVALID_DUPLICATION",
    },
    "RUBRIC_ERROR": {"RESPONSIBILITY_UNDEFINED", "COMPLETENESS_UNDEFINED"},
    "INPUT_PACKAGE_ERROR": {
        "INVALID_PROVENANCE",
        "ACTIVE_SUPERSEDED_SOURCE",
        "PACKAGE_HASH_MISMATCH",
        "BRIEF_HASH_MISMATCH",
        "CONTRACT_HASH_MISMATCH",
        "RESPONSIBILITY_PROFILE_HASH_MISMATCH",
        "OBLIGATION_INDEX_HASH_MISMATCH",
        "IDENTITY_SET_MISMATCH",
        "PREVIOUS_VERDICT_EXPOSURE",
        "OUTPUT_SCHEMA_VIOLATION",
    },
}
TOP_LEVEL_HASHES = (
    "reviewer_brief_hash",
    "reviewer_input_manifest_hash",
    "reviewer_input_package_hash",
    "contract_hash",
    "responsibility_profile_hash",
    "semantic_obligation_index_hash",
    "review_identity_inventory_hash",
)
RECORD_HASHES = (
    "reviewer_brief_hash",
    "reviewer_input_manifest_hash",
    "contract_hash",
)


class OutputError(ValueError):
    """A deterministic semantic-review output failure."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _identity(record: dict[str, Any]) -> str:
    return f"{record['owner_kind']}:{record['owner_id']}:{record['semantic_field']}"


def _validate_rationale(item: dict[str, Any], scope: str) -> None:
    verdict = item["verdict"]
    rationale = item["rationale_code"]
    if verdict not in VERDICTS or rationale not in RATIONALES_BY_VERDICT[verdict]:
        raise OutputError("VERDICT_RATIONALE_MISMATCH", scope)


def _validate_ordered_unique(value: Any, scope: str) -> None:
    if not isinstance(value, list) or value != sorted(set(value)):
        raise OutputError("INVALID_REFERENCE_SET", scope)


def _validate_summary(
    summary: dict[str, Any],
    expected_count: int,
    records: list[dict[str, Any]],
    preflight: list[dict[str, Any]],
) -> Counter[str]:
    identities = [_identity(record) for record in records]
    observed = Counter(item["verdict"] for item in [*preflight, *records])
    expected_verdict_counts = {verdict: observed.get(verdict, 0) for verdict in VERDICTS}
    expected = {
        "expected_identity_count": expected_count,
        "record_count": len(records),
        "unique_identity_count": len(set(identities)),
        "pending_count": 0,
        "verdict_counts": expected_verdict_counts,
        "complete": summary.get("complete"),
    }
    if summary != expected:
        raise OutputError("SUMMARY_MISMATCH", "summary arithmetic")
    return observed


def validate_review_output(
    package: dict[str, Any],
    run_envelope: dict[str, Any],
    output: dict[str, Any],
) -> dict[str, int]:
    """Validate schema, run identity, hashes, identities, and summary arithmetic."""

    try:
        validate_instance(output, package["review_output_schema"])
    except (KeyError, SchemaValidationError) as error:
        raise OutputError("OUTPUT_SCHEMA_VIOLATION", str(error)) from error
    try:
        verify_run_envelope(run_envelope, package)
    except PackageError as error:
        raise OutputError(error.code, str(error)) from error
    for key in ("review_run_id", "reviewer_context_id", "isolation_attestation_hash"):
        if output[key] != run_envelope[key]:
            raise OutputError("RUN_ENVELOPE_MISMATCH", key)
    for key in TOP_LEVEL_HASHES:
        if output[key] != package[key]:
            raise OutputError("IMMUTABLE_HASH_MISMATCH", key)

    expected_identities = package["expected_identities"]
    if (
        not isinstance(expected_identities, list)
        or expected_identities != sorted(set(expected_identities))
    ):
        raise OutputError("IDENTITY_SET_MISMATCH", "invalid expected inventory")
    preflight = output["preflight_errors"]
    records = output["records"]
    if preflight:
        for error in preflight:
            _validate_rationale(error, error["scope"])
        if output["summary"]["complete"]:
            raise OutputError(
                "INVALID_COMPLETION_STATE", "preflight failure cannot be complete"
            )
        observed = _validate_summary(
            output["summary"], len(expected_identities), records, preflight
        )
        return dict(observed)

    observed_identities = [_identity(record) for record in records]
    if any(record["review_identity"] != _identity(record) for record in records):
        raise OutputError("IDENTITY_SET_MISMATCH", "record identity tuple mismatch")
    if (
        len(observed_identities) != len(set(observed_identities))
        or set(observed_identities) != set(expected_identities)
    ):
        raise OutputError(
            "IDENTITY_SET_MISMATCH", "completed output must equal expected identities"
        )
    if not output["summary"]["complete"] or output["summary"]["pending_count"] != 0:
        raise OutputError(
            "INVALID_COMPLETION_STATE",
            "valid completed review must be complete with zero pending",
        )
    for record in records:
        identity = _identity(record)
        expected = package["identity_inventory"].get(identity)
        if expected is None:
            raise OutputError("IDENTITY_SET_MISMATCH", identity)
        for key in RECORD_HASHES:
            if record[key] != package[key]:
                raise OutputError("IMMUTABLE_HASH_MISMATCH", f"{identity}:{key}")
        for key in (
            "semantic_value_hash",
            "provenance_set_hash",
            "responsibility_rule_id",
            "completeness_mode",
        ):
            if record[key] != expected[key]:
                raise OutputError("IMMUTABLE_IDENTITY_MISMATCH", f"{identity}:{key}")
        provenance = record["provenance_hashes"]
        if len(provenance) != len(set(provenance)):
            raise OutputError("DUPLICATE_PROVENANCE", identity)
        _validate_ordered_unique(
            record["sibling_review_identity_refs"], f"{identity}:siblings"
        )
        _validate_ordered_unique(
            record["semantic_obligation_ids"], f"{identity}:obligations"
        )
        _validate_ordered_unique(
            record["test_obligation_refs"], f"{identity}:tests"
        )
        _validate_rationale(record, identity)
    observed = _validate_summary(
        output["summary"], len(expected_identities), records, preflight
    )
    return dict(observed)
