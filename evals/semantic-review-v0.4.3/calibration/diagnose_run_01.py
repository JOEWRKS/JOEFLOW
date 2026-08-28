"""Read-only diagnostic salvage for the invalid v0.4.3 run-01 evidence.

The script reads immutable Git objects, adds only the controller-owned golden
case binding in memory, and never writes into the historical run-01 tree.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.goldens import (
    GoldenError,
    evaluate_goldens,
    verify_golden_packages,
)
from downstream.semantic_review.output import OutputError, validate_review_output
from downstream.semantic_review.package import (
    PackageError,
    load_and_verify_package,
    verify_run_envelope,
)


RUN_01_FINAL = "6f78bb610aeb52e6c475601b4327ce96f0fc509d"
RUN_01_RAW_FREEZE = "a4b641929f071e34eae922096ee7b21f3294b7ef"
RUN_01_LOCK = "f08eb78428b6f43ef76c2eed94f10be56f46cf9a"
FROZEN_INPUT = "96b2b6e7c5435ccdbab5f7371073ec34c2d04078"
RUN_ROOT = "evals/semantic-review-v0.4.3/calibration/run-01"
CALIBRATION_ROOT = ROOT / "evals" / "semantic-review-v0.4.3" / "calibration"
FULL_PACKAGE_ROOT = CALIBRATION_ROOT / "semantic-review-calibration-v1" / "reviewer-package"
GOLDEN_CASES_PATH = ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-cases.json"
GOLDEN_ANSWERS_PATH = ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-answers.json"


def _run_git(repository: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def _git_file(repository: Path, revision: str, path: str) -> bytes:
    return _run_git(repository, "show", f"{revision}:{path}")


def _git_text(repository: Path, *args: str) -> str:
    return _run_git(repository, *args).decode("utf-8").strip()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _serializable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, dict):
        return {key: _serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serializable(item) for item in value]
    return value


def diagnose(repository: Path) -> dict[str, Any]:
    cases_bytes = GOLDEN_CASES_PATH.read_bytes()
    answers_bytes = GOLDEN_ANSWERS_PATH.read_bytes()
    cases = json.loads(cases_bytes)
    answers = json.loads(answers_bytes)
    cases_by_id = {case["case_id"]: case for case in cases}
    answers_by_id = {item["case_id"]: item for item in answers["answers"]}
    golden_packages = verify_golden_packages(cases)
    raw_manifest_items: list[dict[str, str]] = []
    golden_reports: dict[str, Any] = {}

    for cohort_id in ("C1", "C2", "C3"):
        diagnostic_outputs = []
        for number in range(1, 16):
            case_id = f"G-{number:03d}"
            context_id = f"{cohort_id}-{case_id}-001"
            output_path = f"{RUN_ROOT}/raw-outputs/{context_id}/raw-output.txt"
            envelope_path = f"{RUN_ROOT}/inputs/{context_id}/run-envelope.json"
            output_bytes = _git_file(repository, RUN_01_RAW_FREEZE, output_path)
            envelope_bytes = _git_file(repository, RUN_01_RAW_FREEZE, envelope_path)
            raw_manifest_items.append(
                {
                    "context_id": context_id,
                    "raw_output_sha256": _sha256(output_bytes),
                    "run_envelope_sha256": _sha256(envelope_bytes),
                }
            )
            diagnostic_outputs.append(
                {
                    "case_id": case_id,
                    "case_manifest_hash": cases_by_id[case_id]["case_manifest_hash"],
                    "run_envelope": json.loads(envelope_bytes),
                    "review_output": json.loads(output_bytes),
                }
            )
        invalid_raw_outputs = []
        for item in diagnostic_outputs:
            case_id = item["case_id"]
            try:
                validate_review_output(
                    golden_packages[case_id],
                    item["run_envelope"],
                    item["review_output"],
                )
            except OutputError as error:
                invalid_raw_outputs.append(
                    {
                        "case_id": case_id,
                        "error_code": error.code,
                        "error": str(error),
                    }
                )
        try:
            production_report = {
                "status": "PASS",
                "report": _serializable(
                    evaluate_goldens(diagnostic_outputs, answers, cases)
                ),
            }
        except GoldenError as error:
            production_report = {
                "status": "INVALID_RAW_OUTPUT",
                "error_code": error.code,
                "error": str(error),
            }

        observed_pairs = {}
        for item in diagnostic_outputs:
            case_id = item["case_id"]
            output = item["review_output"]
            case = cases_by_id[case_id]
            if case["review_phase"] == "preflight":
                terminal = output["preflight_errors"][0]
            else:
                terminal = next(
                    record
                    for record in output["records"]
                    if record["review_identity"] == case["focus_review_identity"]
                )
            observed_pairs[case_id] = {
                "verdict": terminal["verdict"],
                "rationale_code": terminal["rationale_code"],
            }
        verdict_hits = sum(
            observed_pairs[case_id]["verdict"]
            == answers_by_id[case_id]["verdict"]
            for case_id in observed_pairs
        )
        rationale_hits = sum(
            observed_pairs[case_id]["rationale_code"]
            == answers_by_id[case_id]["rationale_code"]
            for case_id in observed_pairs
        )
        golden_reports[cohort_id] = {
            "production_evaluate_goldens": production_report,
            "invalid_raw_outputs": invalid_raw_outputs,
            "decision_pair_diagnostic_only": {
                "case_count": 15,
                "verdict_hits": verdict_hits,
                "rationale_code_hits": rationale_hits,
                "verdict_accuracy": {
                    "numerator": verdict_hits,
                    "denominator": 15,
                },
                "rationale_code_accuracy": {
                    "numerator": rationale_hits,
                    "denominator": 15,
                },
            },
        }

    full_package = load_and_verify_package(FULL_PACKAGE_ROOT)
    full_diagnostics: dict[str, Any] = {}
    for cohort_id in ("C1", "C2", "C3"):
        context_id = f"{cohort_id}-FULL-001"
        output_path = f"{RUN_ROOT}/raw-outputs/{context_id}/raw-output.txt"
        envelope_path = f"{RUN_ROOT}/inputs/{context_id}/run-envelope.json"
        output_bytes = _git_file(repository, RUN_01_RAW_FREEZE, output_path)
        envelope_bytes = _git_file(repository, RUN_01_RAW_FREEZE, envelope_path)
        output = json.loads(output_bytes)
        envelope = json.loads(envelope_bytes)
        try:
            verify_run_envelope(envelope, full_package)
        except PackageError as error:
            validation = {
                "status": "INVALID",
                "error_code": error.code,
                "error": str(error),
            }
        else:
            validation = {"status": "UNEXPECTED_VALID"}
        full_diagnostics[cohort_id] = {
            "classification": "invalid full input",
            "run_envelope_fields": sorted(envelope),
            "record_count": len(output.get("records", [])),
            "raw_output_sha256": _sha256(output_bytes),
            "run_envelope_sha256": _sha256(envelope_bytes),
            "production_verify_run_envelope": validation,
        }

    tree_entries = _git_text(
        repository, "ls-tree", "-r", "--name-only", RUN_01_FINAL
    ).splitlines()
    seed_paths = [path for path in tree_entries if "seed" in path.lower()]

    return {
        "schema_version": "joewrks.semantic-review-run-01-diagnostic/1.0",
        "classification": {
            "real_calibration_attempts": 1,
            "valid_real_calibration_runs": 0,
            "official_semantic_reliability_result": "NOT MEASURED",
            "root_cause_family": "CALIBRATION_CONTROL_PLANE_DEFECT",
        },
        "authority_commits": {
            "frozen_calibration_input": FROZEN_INPUT,
            "run_01_pre_run_lock": RUN_01_LOCK,
            "run_01_raw_output_freeze": RUN_01_RAW_FREEZE,
            "run_01_final_evidence": RUN_01_FINAL,
            "run_01_raw_output_freeze_tree": _git_text(
                repository, "rev-parse", f"{RUN_01_RAW_FREEZE}^{{tree}}"
            ),
            "run_01_final_evidence_tree": _git_text(
                repository, "rev-parse", f"{RUN_01_FINAL}^{{tree}}"
            ),
        },
        "golden_diagnostic": {
            "label": "RUN_01_GOLDEN_DIAGNOSTIC_ONLY",
            "official_gate_evidence": False,
            "frozen_raw_output_count": len(raw_manifest_items),
            "raw_outputs_modified": False,
            "controller_owned_metadata_added_in_memory": ["case_manifest_hash"],
            "raw_binding_manifest_sha256": _sha256(
                _canonical_bytes(raw_manifest_items)
            ),
            "per_cohort": golden_reports,
        },
        "full_review_diagnostic": {
            "label": "NON_OFFICIAL_DIAGNOSTIC",
            "official_gate_evidence": False,
            "historical_envelopes_modified": False,
            "per_cohort": full_diagnostics,
        },
        "optional_c3_seed_diagnostic": {
            "status": "NOT_AVAILABLE",
            "reason": "No hidden 114-identity seed-oracle plaintext artifact exists in the frozen run-01 final tree.",
            "matching_seed_paths": seed_paths,
        },
        "frozen_inputs": {
            "golden_cases_file_sha256": _sha256(cases_bytes),
            "golden_answers_file_sha256": _sha256(answers_bytes),
            "golden_answer_pairs_sha256": _sha256(
                _canonical_bytes(answers["answers"])
            ),
            "full_reviewer_package_hash": full_package[
                "reviewer_input_package_hash"
            ],
            "reviewer_brief_hash": full_package["role_hashes"]["reviewer_brief"],
            "responsibility_profile_hash": full_package["role_hashes"][
                "responsibility_profile"
            ],
        },
        "new_reviewer_contexts": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = diagnose(args.repository.resolve())
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
