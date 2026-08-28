"""Official calibration-only binding from raw cohort outputs to the production gate."""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.gate import evaluate_reliability_gate
from downstream.semantic_review.goldens import evaluate_goldens, verify_golden_packages
from downstream.semantic_review.package import load_and_verify_package


PACKAGE_HASH = "ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603"
BRIEF_HASH = "3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c"
COHORT_IDS = ("C1", "C2", "C3")
GOLDEN_CASE_IDS = tuple(f"G-{index:03d}" for index in range(1, 16))

FIXTURE_ROOT = Path(__file__).resolve().parent / "semantic-review-calibration-v1"
FULL_PACKAGE_ROOT = FIXTURE_ROOT / "reviewer-package"
GOLDEN_FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "semantic-review-v1"
GOLDEN_CASES_PATH = GOLDEN_FIXTURE_ROOT / "golden-cases.json"
GOLDEN_ANSWERS_PATH = GOLDEN_FIXTURE_ROOT / "golden-answers.json"
FROZEN_GOLDEN_CASES_SHA256 = "812d99c153c736fdd6eacdb0937ba924a83c642bc78f74674b6ad708154c84f3"
FROZEN_GOLDEN_CASES_BYTES = 918685
FROZEN_ORACLE_STATUS = "PM_APPROVED_NORMATIVE_ORACLE"
FROZEN_ORACLE_SHA256 = "4126bb8d316291d8362f04fe1160f53ad86adc73ec358effad7a84d104d7a173"
FROZEN_ORACLE_BYTES = 1648
FROZEN_ORACLE_TUPLE_SET_SHA256 = "7ddc257c085f8e9de4722b01f09646c25891418fbc92d60e7a15425657acc4aa"

VISIBILITY_KEYS = {
    "manifest_only_isolation_attested",
    "visible_inputs",
    "other_context_outputs_visible",
    "prior_verdicts_visible",
    "golden_answers_visible",
    "seed_oracle_visible",
    "repository_history_visible",
    "sibling_packages_visible",
    "controller_disagreement_analysis_visible",
}
FORBIDDEN_VISIBILITY_KEYS = VISIBILITY_KEYS - {
    "manifest_only_isolation_attested",
    "visible_inputs",
}
FULL_ENVELOPE_KEYS = {
    "review_run_id",
    "reviewer_context_id",
    "reviewer_input_package_hash",
    "reviewer_brief_hash",
    "isolation_attestation",
}
GOLDEN_ENVELOPE_KEYS = FULL_ENVELOPE_KEYS | {"isolation_attestation_hash"}
FULL_PACKAGE_IDENTITY_KEYS = {
    "reviewer_input_package_hash",
    "reviewer_brief_hash",
}
FORBIDDEN_REVIEWER_CONTENT_KEYS = {
    "correction_hint",
    "correction_hints",
    "expected_rationale_code",
    "expected_verdict",
    "golden_answer",
    "golden_answers",
    "oracle_bytes",
    "prior_reviewer_results",
    "prior_verdicts",
    "reviewer_results",
}


class CalibrationControllerError(ValueError):
    """One stable official-controller rejection."""

    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


def canonical_sha256(value: Any) -> str:
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _reject(code: str, detail: str = "") -> None:
    raise CalibrationControllerError(code, detail)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_frozen_oracle() -> tuple[dict[str, Any], str]:
    """Load only the controller-bound PM-approved oracle after outputs freeze."""

    data = GOLDEN_ANSWERS_PATH.read_bytes()
    if hashlib.sha256(data).hexdigest() != FROZEN_ORACLE_SHA256:
        _reject("ORACLE_HASH_MISMATCH")
    oracle = _require_mapping(
        json.loads(data.decode("utf-8")), "ORACLE_TUPLE_SET_MISMATCH", "oracle"
    )
    if oracle.get("adjudication_status") != FROZEN_ORACLE_STATUS:
        _reject("ORACLE_STATUS_NOT_APPROVED")
    answers = oracle.get("answers")
    if not isinstance(answers, list):
        _reject("GOLDEN_ORACLE_SPEC_MISMATCH")
    tuples = [
        {key: answer.get(key) for key in ("case_id", "verdict", "rationale_code")}
        for answer in answers
        if isinstance(answer, Mapping)
    ]
    if len(tuples) != 15 or tuple(item["case_id"] for item in tuples) != GOLDEN_CASE_IDS:
        _reject("GOLDEN_ORACLE_SPEC_MISMATCH")
    if canonical_sha256(tuples) != FROZEN_ORACLE_TUPLE_SET_SHA256:
        _reject("GOLDEN_ORACLE_SPEC_MISMATCH")
    if len(data) != FROZEN_ORACLE_BYTES:
        _reject("ORACLE_BYTES_MISMATCH")
    return dict(oracle), data.decode("utf-8")


def _load_frozen_golden_cases() -> list[dict[str, Any]]:
    data = GOLDEN_CASES_PATH.read_bytes()
    if (
        hashlib.sha256(data).hexdigest() != FROZEN_GOLDEN_CASES_SHA256
        or len(data) != FROZEN_GOLDEN_CASES_BYTES
    ):
        _reject("GOLDEN_CASES_COMMITMENT_MISMATCH")
    cases = _load_json(GOLDEN_CASES_PATH)
    if not isinstance(cases, list):
        _reject("GOLDEN_CASES_COMMITMENT_MISMATCH")
    try:
        verify_golden_packages(cases)
    except ValueError as error:
        _reject("GOLDEN_CASES_COMMITMENT_MISMATCH", str(error))
    return cases


def _scan_reviewer_visible_content(
    value: Any, oracle_text: str, oracle_pairs: set[tuple[str, str, str]], detail: str
) -> None:
    """Reject answer-bearing or correction-bearing material visible to a reviewer."""

    def scan(item: Any) -> None:
        if isinstance(item, bytes):
            try:
                item = item.decode("utf-8")
            except UnicodeDecodeError:
                _reject("FORBIDDEN_CONTEXT_EXPOSURE", detail)
        if isinstance(item, str):
            if oracle_text in item:
                _reject("FORBIDDEN_CONTEXT_EXPOSURE", detail)
            try:
                parsed = json.loads(item)
            except json.JSONDecodeError:
                return
            if isinstance(parsed, (Mapping, list)):
                scan(parsed)
            return
        if isinstance(item, Mapping):
            keys = {str(key).lower() for key in item}
            if keys & FORBIDDEN_REVIEWER_CONTENT_KEYS:
                _reject("FORBIDDEN_CONTEXT_EXPOSURE", detail)
            pair = tuple(item.get(key) for key in ("case_id", "verdict", "rationale_code"))
            if all(isinstance(part, str) for part in pair) and pair in oracle_pairs:
                _reject("FORBIDDEN_CONTEXT_EXPOSURE", detail)
            for child in item.values():
                scan(child)
            return
        if isinstance(item, list):
            for child in item:
                scan(child)

    scan(value)


def _trusted_full_reviewer_package(
    oracle_text: str, oracle_pairs: set[tuple[str, str, str]]
) -> dict[str, Any]:
    verified = load_and_verify_package(FULL_PACKAGE_ROOT)
    if verified.get("reviewer_input_package_hash") != PACKAGE_HASH:
        _reject("PACKAGE_HASH_MISMATCH", "controller full package")
    declared_paths = {"manifest.json"}
    for item in verified["manifest"]["files"]:
        declared_paths.add(item["path"])
    actual_paths = {
        path.relative_to(FULL_PACKAGE_ROOT).as_posix()
        for path in FULL_PACKAGE_ROOT.rglob("*")
        if path.is_file()
    }
    if actual_paths != declared_paths:
        _reject("PACKAGE_HASH_MISMATCH", "controller full package files")
    for relative in sorted(actual_paths):
        _scan_reviewer_visible_content(
            (FULL_PACKAGE_ROOT / relative).read_bytes(),
            oracle_text,
            oracle_pairs,
            f"controller full package:{relative}",
        )
    return verified


def _require_mapping(value: Any, code: str, detail: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _reject(code, detail)
    return value


def _validate_visibility(value: Any, kind: str) -> None:
    visibility = _require_mapping(
        value, "MANIFEST_ONLY_ISOLATION_REQUIRED", f"{kind} visibility"
    )
    visible_package = (
        "exact_full_reviewer_package"
        if kind == "full"
        else "exact_single_golden_package"
    )
    if set(visibility) != VISIBILITY_KEYS:
        _reject("MANIFEST_ONLY_ISOLATION_REQUIRED", f"{kind} visibility fields")
    if visibility["manifest_only_isolation_attested"] is not True:
        _reject("MANIFEST_ONLY_ISOLATION_REQUIRED", f"{kind} attestation")
    if visibility["visible_inputs"] != [visible_package, "run_envelope"]:
        _reject("FORBIDDEN_CONTEXT_EXPOSURE", f"{kind} visible inputs")
    exposed = sorted(
        key for key in FORBIDDEN_VISIBILITY_KEYS if visibility[key] is not False
    )
    if exposed:
        _reject("FORBIDDEN_CONTEXT_EXPOSURE", ",".join(exposed))


def _validate_isolation_attestation(envelope: Mapping[str, Any], detail: str) -> None:
    if envelope.get("isolation_attestation") != {
        "fresh_context": True,
        "previous_verdict_access": False,
        "manifest_only_evidence": True,
    }:
        _reject("MANIFEST_ONLY_ISOLATION_REQUIRED", detail)


def _validate_hash(value: Any, observed: Any, code: str, detail: str) -> None:
    if not isinstance(value, str) or value != canonical_sha256(observed):
        _reject(code, detail)


def _validate_full_review(
    wrapper: Any, cohort_id: str, context_ids: set[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    full = _require_mapping(wrapper, "FULL_REVIEW_OUTPUT_INVALID", cohort_id)
    if set(full) != {
        "run_envelope",
        "review_output",
        "visibility",
        "run_envelope_sha256",
        "review_output_sha256",
    }:
        _reject("FULL_REVIEW_OUTPUT_INVALID", f"{cohort_id} fields")
    envelope = _require_mapping(
        full["run_envelope"], "FULL_REVIEW_OUTPUT_INVALID", f"{cohort_id} envelope"
    )
    output = _require_mapping(
        full["review_output"], "FULL_REVIEW_OUTPUT_INVALID", f"{cohort_id} output"
    )
    _validate_hash(
        full["run_envelope_sha256"],
        envelope,
        "RUN_ENVELOPE_HASH_MISMATCH",
        cohort_id,
    )
    _validate_hash(
        full["review_output_sha256"],
        output,
        "RAW_OUTPUT_HASH_MISMATCH",
        cohort_id,
    )
    _validate_visibility(full["visibility"], "full")
    _validate_isolation_attestation(envelope, f"{cohort_id} full")
    context_id = envelope.get("reviewer_context_id")
    if (
        not isinstance(context_id, str)
        or not context_id
        or output.get("reviewer_context_id") != context_id
        or output.get("review_run_id") != envelope.get("review_run_id")
    ):
        _reject("FULL_REVIEW_OUTPUT_INVALID", f"{cohort_id} run/context binding")
    if context_id in context_ids:
        _reject("CONTEXT_ID_REUSE", context_id)
    context_ids.add(context_id)
    if envelope.get("reviewer_input_package_hash") != PACKAGE_HASH:
        _reject("PACKAGE_HASH_MISMATCH", f"{cohort_id} full envelope")
    if envelope.get("reviewer_brief_hash") != BRIEF_HASH:
        _reject("BRIEF_HASH_MISMATCH", f"{cohort_id} full envelope")
    if output.get("reviewer_input_package_hash") != PACKAGE_HASH:
        _reject("FULL_REVIEW_PACKAGE_MISMATCH", cohort_id)
    if output.get("reviewer_brief_hash") != BRIEF_HASH:
        _reject("FULL_REVIEW_BRIEF_MISMATCH", cohort_id)
    return dict(envelope), dict(output)


def _validate_golden_reviews(
    wrappers: Any,
    cohort_id: str,
    output_set_sha256: Any,
    context_ids: set[str],
    trusted_package_hashes: Mapping[str, str],
) -> list[dict[str, Any]]:
    if not isinstance(wrappers, list):
        _reject("RAW_GOLDEN_OUTPUTS_REQUIRED", cohort_id)
    raw_outputs: list[dict[str, Any]] = []
    case_ids: list[str] = []
    raw_hashes: list[str] = []
    for wrapper in wrappers:
        item = _require_mapping(wrapper, "RAW_GOLDEN_OUTPUT_INVALID", cohort_id)
        if set(item) != {
            "raw_output",
            "visibility",
            "run_envelope_sha256",
            "review_output_sha256",
            "raw_output_sha256",
        }:
            _reject("RAW_GOLDEN_OUTPUT_INVALID", f"{cohort_id} fields")
        raw = _require_mapping(
            item["raw_output"], "RAW_GOLDEN_OUTPUT_INVALID", cohort_id
        )
        envelope = _require_mapping(
            raw.get("run_envelope"), "RAW_GOLDEN_OUTPUT_INVALID", cohort_id
        )
        output = _require_mapping(
            raw.get("review_output"), "RAW_GOLDEN_OUTPUT_INVALID", cohort_id
        )
        _validate_hash(
            item["run_envelope_sha256"],
            envelope,
            "RUN_ENVELOPE_HASH_MISMATCH",
            cohort_id,
        )
        _validate_hash(
            item["review_output_sha256"],
            output,
            "RAW_OUTPUT_HASH_MISMATCH",
            cohort_id,
        )
        _validate_hash(
            item["raw_output_sha256"],
            raw,
            "RAW_OUTPUT_HASH_MISMATCH",
            cohort_id,
        )
        _validate_visibility(item["visibility"], "golden")
        _validate_isolation_attestation(envelope, f"{cohort_id} golden")
        context_id = envelope.get("reviewer_context_id")
        if (
            not isinstance(context_id, str)
            or not context_id
            or output.get("reviewer_context_id") != context_id
            or output.get("review_run_id") != envelope.get("review_run_id")
        ):
            _reject("RAW_GOLDEN_OUTPUT_INVALID", f"{cohort_id} run/context binding")
        if context_id in context_ids:
            _reject("CONTEXT_ID_REUSE", context_id)
        context_ids.add(context_id)
        if envelope.get("reviewer_brief_hash") != BRIEF_HASH:
            _reject("BRIEF_HASH_MISMATCH", f"{cohort_id} golden envelope")
        if output.get("reviewer_brief_hash") != BRIEF_HASH:
            _reject("BRIEF_HASH_MISMATCH", f"{cohort_id} golden output")
        if output.get("reviewer_input_package_hash") != envelope.get(
            "reviewer_input_package_hash"
        ):
            _reject("RAW_GOLDEN_OUTPUT_INVALID", f"{cohort_id} package binding")
        case_id = raw.get("case_id")
        if envelope.get("reviewer_input_package_hash") != trusted_package_hashes.get(
            case_id
        ):
            _reject("GOLDEN_REVIEW_PACKAGE_MISMATCH", f"{cohort_id}:{case_id}")
        case_ids.append(case_id)
        raw_hashes.append(item["raw_output_sha256"])
        raw_outputs.append(dict(raw))
    if tuple(sorted(case_ids)) != GOLDEN_CASE_IDS or len(set(case_ids)) != 15:
        _reject("GOLDEN_CASE_SET_MISMATCH", cohort_id)
    if output_set_sha256 != canonical_sha256(raw_hashes):
        _reject("GOLDEN_OUTPUT_SET_HASH_MISMATCH", cohort_id)
    return raw_outputs


def _golden_report_passes(report: Mapping[str, Any]) -> bool:
    return (
        report.get("case_count") == 15
        and report.get("verdict_hits") == 15
        and report.get("rationale_code_hits") == 15
        and report.get("verdict_accuracy") == Fraction(1, 1)
        and report.get("rationale_code_accuracy") == Fraction(1, 1)
        and report.get("unexpected_rubric_error_count") == 0
        and report.get("unexpected_input_package_error_count") == 0
    )


def _serializable_golden_report(report: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(report)
    for key in ("verdict_accuracy", "rationale_code_accuracy"):
        value = result[key]
        result[key] = {
            "numerator": value.numerator,
            "denominator": value.denominator,
        }
    return result


def evaluate_official_calibration(
    evidence: Mapping[str, Any], *, real_mode: bool
) -> dict[str, Any]:
    """Validate three raw cohorts, derive goldens internally, then call the gate."""

    evidence = _require_mapping(
        evidence, "RAW_GOLDEN_OUTPUTS_REQUIRED", "official evidence"
    )
    if {"golden_report", "golden_summary"} & set(evidence):
        _reject("RAW_GOLDEN_OUTPUTS_REQUIRED", "scalar golden input is forbidden")
    if set(evidence) != {
        "schema_version",
        "full_reviewer_package",
        "cohorts",
        "disagreement_classifications",
    }:
        _reject("RAW_GOLDEN_OUTPUTS_REQUIRED", "official evidence fields")

    package_identity = _require_mapping(
        evidence["full_reviewer_package"], "PACKAGE_HASH_MISMATCH", "package"
    )
    if package_identity.get("reviewer_input_package_hash") != PACKAGE_HASH:
        _reject("PACKAGE_HASH_MISMATCH", "official package")
    if package_identity.get("reviewer_brief_hash") != BRIEF_HASH:
        _reject("BRIEF_HASH_MISMATCH", "official package")

    cases = _load_frozen_golden_cases()
    trusted_golden_package_hashes = {
        case["case_id"]: case["reviewer_package"]["reviewer_input_package_hash"]
        for case in cases
    }

    cohorts = evidence["cohorts"]
    if not isinstance(cohorts, list):
        _reject("COHORT_SET_MISMATCH")
    cohort_ids = [item.get("cohort_id") for item in cohorts if isinstance(item, Mapping)]
    if tuple(cohort_ids) != COHORT_IDS or len(set(cohort_ids)) != 3:
        _reject("COHORT_SET_MISMATCH")

    context_ids: set[str] = set()
    full_envelopes: list[dict[str, Any]] = []
    full_outputs: list[dict[str, Any]] = []
    raw_golden_sets: list[list[dict[str, Any]]] = []
    golden_output_set_hashes: list[str] = []
    for cohort in cohorts:
        if set(cohort) != {
            "cohort_id",
            "full_review",
            "golden_reviews",
            "golden_output_set_sha256",
        }:
            _reject("RAW_GOLDEN_OUTPUTS_REQUIRED", f"{cohort['cohort_id']} fields")
        envelope, output = _validate_full_review(
            cohort["full_review"], cohort["cohort_id"], context_ids
        )
        full_envelopes.append(envelope)
        full_outputs.append(output)
        raw_golden_sets.append(
            _validate_golden_reviews(
                cohort["golden_reviews"],
                cohort["cohort_id"],
                cohort["golden_output_set_sha256"],
                context_ids,
                trusted_golden_package_hashes,
            )
        )
        golden_output_set_hashes.append(cohort["golden_output_set_sha256"])
    if len(context_ids) != 48:
        _reject("CONTEXT_POPULATION_MISMATCH", str(len(context_ids)))

    answers, oracle_text = _load_frozen_oracle()
    oracle_pairs = {
        (item["case_id"], item["verdict"], item["rationale_code"])
        for item in answers["answers"]
    }
    _scan_reviewer_visible_content(
        package_identity, oracle_text, oracle_pairs, "official package identity"
    )
    if set(package_identity) != FULL_PACKAGE_IDENTITY_KEYS:
        _reject("PACKAGE_HASH_MISMATCH", "official package fields")
    for envelope in full_envelopes:
        _scan_reviewer_visible_content(
            envelope, oracle_text, oracle_pairs, "full reviewer context"
        )
        if set(envelope) != FULL_ENVELOPE_KEYS:
            _reject("FULL_REVIEW_OUTPUT_INVALID", "full envelope fields")
    for raw_set in raw_golden_sets:
        for raw in raw_set:
            envelope = raw["run_envelope"]
            _scan_reviewer_visible_content(
                envelope, oracle_text, oracle_pairs, "golden reviewer context"
            )
            if set(envelope) != GOLDEN_ENVELOPE_KEYS:
                _reject("RAW_GOLDEN_OUTPUT_INVALID", "golden envelope fields")
    for case in cases:
        _scan_reviewer_visible_content(
            case["reviewer_package"],
            oracle_text,
            oracle_pairs,
            f"golden reviewer package:{case['case_id']}",
        )
    verified_package = _trusted_full_reviewer_package(oracle_text, oracle_pairs)
    cohort_reports = [
        evaluate_goldens(raw_outputs, answers, cases)
        for raw_outputs in raw_golden_sets
    ]
    if not all(_golden_report_passes(report) for report in cohort_reports):
        _reject("GOLDEN_COHORT_CONJUNCTION_FAILED")

    derived_golden_summary = {
        "case_count": 15,
        "verdict_hits": 15,
        "rationale_code_hits": 15,
        "verdict_accuracy": Fraction(1, 1),
        "rationale_code_accuracy": Fraction(1, 1),
        "unexpected_rubric_error_count": 0,
        "unexpected_input_package_error_count": 0,
    }
    gate_report = evaluate_reliability_gate(
        [verified_package, verified_package, verified_package],
        full_envelopes,
        full_outputs,
        derived_golden_summary,
        evidence["disagreement_classifications"],
    )
    serializable_reports = [
        _serializable_golden_report(report) for report in cohort_reports
    ]
    return {
        "schema_version": "joewrks.semantic-review-official-calibration-evidence/1.0",
        "reviewer_input_package_hash": PACKAGE_HASH,
        "reviewer_brief_hash": BRIEF_HASH,
        "cohort_ids": list(COHORT_IDS),
        "context_count": 48,
        "golden_output_set_hashes": golden_output_set_hashes,
        "per_cohort_golden_reports": serializable_reports,
        "aggregate_golden_conjunction": "PASS",
        "aggregate_golden_evidence_sha256": canonical_sha256(serializable_reports),
        "gate_report": gate_report,
    }
