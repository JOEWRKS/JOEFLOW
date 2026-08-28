"""Calibration input materialization and raw-output assembly.

This module deliberately delegates every semantic package and output check to
the frozen production validators.  It owns only run-time binding fields and
the wrapper evidence consumed by the official calibration controller.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import json

from downstream.semantic_review.hashing import canonical_json_bytes, sha256_bytes
from downstream.semantic_review.package import verify_run_envelope
from downstream.semantic_review.output import validate_review_output


RUN_ENVELOPE_KEYS = {
    "review_run_id",
    "reviewer_context_id",
    "reviewer_input_package_hash",
    "reviewer_brief_hash",
    "isolation_attestation",
    "isolation_attestation_hash",
}

ISOLATION_ATTESTATION = {
    "fresh_context": True,
    "previous_verdict_access": False,
    "manifest_only_evidence": True,
}


def _canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _visibility(kind: str) -> dict[str, Any]:
    if kind not in {"full", "golden"}:
        raise ValueError("CALIBRATION_VISIBILITY_KIND_INVALID")
    return {
        "controller_disagreement_analysis_visible": False,
        "golden_answers_visible": False,
        "manifest_only_isolation_attested": True,
        "other_context_outputs_visible": False,
        "prior_verdicts_visible": False,
        "repository_history_visible": False,
        "seed_oracle_visible": False,
        "sibling_packages_visible": False,
        "visible_inputs": [
            "exact_full_reviewer_package"
            if kind == "full"
            else "exact_single_golden_package",
            "run_envelope",
        ],
    }


def materialize_run_envelope(
    package: dict[str, Any],
    *,
    review_run_id: str,
    reviewer_context_id: str,
) -> dict[str, Any]:
    """Build and production-verify the exact six-field run envelope."""

    attestation = deepcopy(ISOLATION_ATTESTATION)
    envelope = {
        "review_run_id": review_run_id,
        "reviewer_context_id": reviewer_context_id,
        "reviewer_input_package_hash": package["reviewer_input_package_hash"],
        "reviewer_brief_hash": package["role_hashes"]["reviewer_brief"],
        "isolation_attestation": attestation,
        "isolation_attestation_hash": sha256_bytes(canonical_json_bytes(attestation)),
    }
    if set(envelope) != RUN_ENVELOPE_KEYS:
        raise ValueError("CALIBRATION_RUN_ENVELOPE_FIELDS_INVALID")
    verify_run_envelope(envelope, package)
    return envelope


def read_raw_output(path: str | Path) -> dict[str, Any]:
    """Read a reviewer-authored raw output without manufacturing review data."""

    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("CALIBRATION_RAW_OUTPUT_INVALID")
    return value


def assemble_golden_review(
    *,
    case: dict[str, Any],
    package: dict[str, Any],
    run_envelope: dict[str, Any],
    raw_output_path: str | Path,
) -> dict[str, Any]:
    """Bind one raw reviewer output to its frozen golden case and envelope."""

    case_id = case.get("case_id")
    case_manifest_hash = case.get("case_manifest_hash")
    if not isinstance(case_id, str) or not isinstance(case_manifest_hash, str):
        raise ValueError("CALIBRATION_GOLDEN_CASE_BINDING_INVALID")
    unhashed_case = dict(case)
    unhashed_case.pop("case_manifest_hash", None)
    if case_manifest_hash != _canonical_sha256(unhashed_case):
        raise ValueError("CALIBRATION_GOLDEN_CASE_HASH_DRIFT")
    declared_package = case.get("reviewer_package")
    if (
        not isinstance(declared_package, dict)
        or declared_package.get("reviewer_input_package_hash")
        != package.get("reviewer_input_package_hash")
    ):
        raise ValueError("CALIBRATION_GOLDEN_CASE_PACKAGE_DRIFT")
    verify_run_envelope(run_envelope, package)
    output = read_raw_output(raw_output_path)
    validate_review_output(package, run_envelope, output)
    raw_output = {
        "case_id": case_id,
        "case_manifest_hash": case_manifest_hash,
        "run_envelope": deepcopy(run_envelope),
        "review_output": output,
    }
    return {
        "raw_output": raw_output,
        "raw_output_sha256": _canonical_sha256(raw_output),
        "review_output_sha256": _canonical_sha256(output),
        "run_envelope_sha256": _canonical_sha256(run_envelope),
        "visibility": _visibility("golden"),
    }


def assemble_full_review(
    *,
    package: dict[str, Any],
    run_envelope: dict[str, Any],
    raw_output_path: str | Path,
) -> dict[str, Any]:
    """Validate and wrap one full-review raw output for the controller."""

    verify_run_envelope(run_envelope, package)
    output = read_raw_output(raw_output_path)
    validate_review_output(package, run_envelope, output)
    return {
        "run_envelope": deepcopy(run_envelope),
        "review_output": output,
        "run_envelope_sha256": _canonical_sha256(run_envelope),
        "review_output_sha256": _canonical_sha256(output),
        "visibility": _visibility("full"),
    }


def assemble_cohort(
    *,
    cohort_id: str,
    full_review: dict[str, Any],
    golden_reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble the exact one-full plus fifteen-golden cohort shape."""

    case_ids = [item.get("raw_output", {}).get("case_id") for item in golden_reviews]
    expected_ids = [f"G-{index:03d}" for index in range(1, 16)]
    if sorted(case_ids) != expected_ids or len(set(case_ids)) != 15:
        raise ValueError("CALIBRATION_GOLDEN_CASE_SET_INVALID")
    raw_hashes = [item["raw_output_sha256"] for item in golden_reviews]
    return {
        "cohort_id": cohort_id,
        "full_review": deepcopy(full_review),
        "golden_reviews": deepcopy(golden_reviews),
        "golden_output_set_sha256": _canonical_sha256(raw_hashes),
    }


def assemble_official_evidence(
    *,
    full_package: dict[str, Any],
    cohorts: list[dict[str, Any]],
    disagreement_classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble official input without accepting caller-supplied golden summaries."""

    if [cohort.get("cohort_id") for cohort in cohorts] != ["C1", "C2", "C3"]:
        raise ValueError("CALIBRATION_COHORT_SET_INVALID")
    return {
        "schema_version": "joewrks.semantic-review-official-calibration-input/1.0",
        "full_reviewer_package": {
            "reviewer_input_package_hash": full_package[
                "reviewer_input_package_hash"
            ],
            "reviewer_brief_hash": full_package["role_hashes"]["reviewer_brief"],
        },
        "cohorts": deepcopy(cohorts),
        "disagreement_classifications": deepcopy(disagreement_classifications),
    }
