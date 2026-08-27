"""Conjunctive deterministic semantic-review reliability gate."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Any

from .disagreement import validate_disagreement_classifications
from .output import OutputError, validate_review_output
from .statistics import (
    fleiss_kappa,
    gwet_ac1,
    is_balanced,
    minority_class_agreement,
    pairwise_cohen_kappas,
)


THRESHOLDS = {
    "minimum_runs": 3,
    "golden_verdict_accuracy": Fraction(1, 1),
    "golden_rationale_code_accuracy": Fraction(1, 1),
    "unanimity": Fraction(99, 100),
    "balanced_kappa": Fraction(9, 10),
    "imbalanced_ac1": Fraction(19, 20),
    "minority_class_agreement": Fraction(19, 20),
}


def _append_unique(failures: list[str], failure: str) -> None:
    if failure not in failures:
        failures.append(failure)


def _previous_verdict_exposed(
    packages: list[dict[str, Any]], envelopes: list[dict[str, Any]]
) -> bool:
    for package in packages:
        declared = package.get(
            "previous_reviewer_verdicts_present",
            package.get("manifest", {}).get("previous_reviewer_verdicts_present", False),
        )
        if declared is not False:
            return True
    return any(
        envelope.get("isolation_attestation", {}).get("previous_verdict_access")
        is not False
        for envelope in envelopes
    )


def _unique_verified_contexts(
    envelopes: list[dict[str, Any]], outputs: list[dict[str, Any]]
) -> bool:
    if len(envelopes) != len(outputs):
        return False
    run_ids = [item.get("review_run_id") for item in envelopes]
    context_ids = [item.get("reviewer_context_id") for item in envelopes]
    if (
        any(not isinstance(item, str) or not item for item in [*run_ids, *context_ids])
        or len(run_ids) != len(set(run_ids))
        or len(context_ids) != len(set(context_ids))
    ):
        return False
    for envelope, output in zip(envelopes, outputs):
        attestation = envelope.get("isolation_attestation")
        if attestation != {
            "fresh_context": True,
            "previous_verdict_access": False,
            "manifest_only_evidence": True,
        }:
            return False
        if (
            output.get("review_run_id") != envelope["review_run_id"]
            or output.get("reviewer_context_id") != envelope["reviewer_context_id"]
            or output.get("isolation_attestation_hash")
            != envelope.get("isolation_attestation_hash")
        ):
            return False
    return True


def _cross_run_hash_failures(packages: list[dict[str, Any]]) -> list[str]:
    if not packages:
        return []
    if len({item.get("reviewer_brief_hash") for item in packages}) != 1:
        return ["FAIL/BRIEF_IDENTITY_MISMATCH"]
    if len({item.get("reviewer_input_package_hash") for item in packages}) != 1:
        return ["FAIL/PACKAGE_IDENTITY_MISMATCH"]
    immutable_hashes = (
        "contract_hash",
        "responsibility_profile_hash",
        "semantic_obligation_index_hash",
        "review_identity_inventory_hash",
    )
    if any(len({item.get(key) for item in packages}) != 1 for key in immutable_hashes):
        return ["FAIL/PACKAGE_IDENTITY_MISMATCH"]
    return []


def _validate_structural_outputs(
    packages: list[dict[str, Any]],
    envelopes: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    if not (len(packages) == len(envelopes) == len(outputs)):
        return ["FAIL/REVIEWER_ISOLATION"]
    expected_sets = [tuple(package.get("expected_identities", [])) for package in packages]
    if expected_sets and len(set(expected_sets)) != 1:
        _append_unique(failures, "FAIL/IDENTITY_COVERAGE")
    if expected_sets and not expected_sets[0]:
        _append_unique(failures, "FAIL/IDENTITY_COVERAGE")
    for package, envelope, output in zip(packages, envelopes, outputs):
        try:
            validate_review_output(package, envelope, output)
        except OutputError as error:
            if error.code == "IDENTITY_SET_MISMATCH":
                _append_unique(failures, "FAIL/IDENTITY_COVERAGE")
            elif error.code in {"INVALID_COMPLETION_STATE", "SUMMARY_MISMATCH"}:
                _append_unique(failures, "FAIL/INCOMPLETE_REVIEW")
            elif error.code == "PREVIOUS_VERDICT_EXPOSURE":
                _append_unique(failures, "FAIL/PREVIOUS_VERDICT_EXPOSURE")
            elif error.code == "BRIEF_HASH_MISMATCH":
                _append_unique(failures, "FAIL/BRIEF_IDENTITY_MISMATCH")
            elif error.code in {
                "PACKAGE_HASH_MISMATCH",
                "IMMUTABLE_HASH_MISMATCH",
                "IMMUTABLE_IDENTITY_MISMATCH",
            }:
                _append_unique(failures, "FAIL/PACKAGE_IDENTITY_MISMATCH")
            else:
                _append_unique(failures, "FAIL/OUTPUT_SCHEMA_VIOLATION")
        if output.get("preflight_errors"):
            _append_unique(failures, "FAIL/UNEXPECTED_ERROR_VERDICT")
        if any(
            record.get("verdict") in {"RUBRIC_ERROR", "INPUT_PACKAGE_ERROR"}
            for record in output.get("records", [])
        ):
            _append_unique(failures, "FAIL/UNEXPECTED_ERROR_VERDICT")
        summary = output.get("summary", {})
        if summary.get("pending_count") != 0 or summary.get("complete") is not True:
            _append_unique(failures, "FAIL/INCOMPLETE_REVIEW")
    return failures


def _golden_failures(golden_report: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if (
        golden_report.get("case_count") != 15
        or golden_report.get("verdict_accuracy")
        != THRESHOLDS["golden_verdict_accuracy"]
    ):
        failures.append("FAIL/GOLDEN_VERDICT")
    if (
        golden_report.get("case_count") != 15
        or golden_report.get("rationale_code_accuracy")
        != THRESHOLDS["golden_rationale_code_accuracy"]
    ):
        failures.append("FAIL/GOLDEN_RATIONALE")
    if (
        golden_report.get("unexpected_rubric_error_count") != 0
        or golden_report.get("unexpected_input_package_error_count") != 0
    ):
        failures.append("FAIL/UNEXPECTED_ERROR_VERDICT")
    return failures


def _review_runs(outputs: list[dict[str, Any]]) -> list[list[dict[str, str]]]:
    return [
        [
            {
                "review_identity": record["review_identity"],
                "verdict": record["verdict"],
            }
            for record in output["records"]
        ]
        for output in outputs
    ]


def _three_review_unanimity(outputs: list[dict[str, Any]]) -> Fraction:
    maps = [
        {record["review_identity"]: record for record in output["records"]}
        for output in outputs
    ]
    identities = sorted(maps[0])
    results = []
    for selected in combinations(maps, 3):
        unanimous = 0
        for identity in identities:
            pairs = {
                (mapping[identity]["verdict"], mapping[identity]["rationale_code"])
                for mapping in selected
            }
            unanimous += len(pairs) == 1
        results.append(Fraction(unanimous, len(identities)))
    return min(results)


def _reliability_metrics(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    runs = _review_runs(outputs)
    return {
        "population": "BALANCED" if is_balanced(runs) else "IMBALANCED",
        "three_review_unanimity": _three_review_unanimity(outputs),
        "pairwise_cohen": pairwise_cohen_kappas(runs),
        "fleiss_kappa": fleiss_kappa(runs),
        "gwet_ac1": gwet_ac1(runs),
        "minority_class_agreement": minority_class_agreement(runs),
    }


def _agreement_failures(metrics: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if metrics["three_review_unanimity"] < THRESHOLDS["unanimity"]:
        failures.append("FAIL/EXACT_AGREEMENT")
    if metrics["population"] == "BALANCED":
        pairwise = metrics["pairwise_cohen"]
        fleiss = metrics["fleiss_kappa"]
        if (
            any(
                item.value is None or item.value < THRESHOLDS["balanced_kappa"]
                for item in pairwise
            )
            or fleiss.value is None
            or fleiss.value < THRESHOLDS["balanced_kappa"]
        ):
            failures.append("FAIL/BALANCED_RELIABILITY")
    else:
        ac1 = metrics["gwet_ac1"]
        minority = metrics["minority_class_agreement"]
        if ac1.value is None or ac1.value < THRESHOLDS["imbalanced_ac1"]:
            failures.append("FAIL/IMBALANCED_RELIABILITY")
        if (
            minority.value is None
            or minority.value < THRESHOLDS["minority_class_agreement"]
        ):
            failures.append("FAIL/MINORITY_CLASS_RELIABILITY")
    return failures


def evaluate_reliability_gate(
    run_packages: list[dict[str, Any]],
    run_envelopes: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
    golden_report: dict[str, Any],
    classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Apply every frozen structural, golden, disagreement, and metric gate."""

    failures: list[str] = []
    if len(outputs) < THRESHOLDS["minimum_runs"]:
        _append_unique(failures, "FAIL/INSUFFICIENT_INDEPENDENT_RUNS")
    if _previous_verdict_exposed(run_packages, run_envelopes):
        _append_unique(failures, "FAIL/PREVIOUS_VERDICT_EXPOSURE")
    elif not _unique_verified_contexts(run_envelopes, outputs):
        _append_unique(failures, "FAIL/REVIEWER_ISOLATION")
    else:
        for failure in _cross_run_hash_failures(run_packages):
            _append_unique(failures, failure)
    for failure in _validate_structural_outputs(
        run_packages, run_envelopes, outputs
    ):
        _append_unique(failures, failure)
    if failures:
        return {
            "passed": False,
            "failures": failures,
            "metrics": {},
            "disagreements": {},
            "thresholds": THRESHOLDS,
        }

    for failure in _golden_failures(golden_report):
        _append_unique(failures, failure)
    metrics = _reliability_metrics(outputs)
    disagreement_report = validate_disagreement_classifications(
        outputs, classifications
    )
    metrics["unchanged_disagreement_count"] = disagreement_report[
        "disagreement_count"
    ]
    if disagreement_report["unresolved_normative_count"]:
        _append_unique(failures, "FAIL/RUBRIC_NORMATIVE_AMBIGUITY")
    if disagreement_report["repeated_rule_ids"]:
        _append_unique(failures, "FAIL/RESPONSIBILITY_RULE_INSTABILITY")
    if disagreement_report["structural_cause_count"]:
        _append_unique(failures, "FAIL/PACKAGE_IDENTITY_MISMATCH")
    for failure in _agreement_failures(metrics):
        _append_unique(failures, failure)
    return {
        "passed": not failures,
        "failures": failures,
        "metrics": metrics,
        "disagreements": disagreement_report,
        "thresholds": THRESHOLDS,
    }
