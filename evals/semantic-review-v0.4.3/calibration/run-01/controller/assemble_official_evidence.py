from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parents[1]
INPUT_MANIFEST_PATH = RUN_ROOT / "INPUT_FREEZE_MANIFEST.json"
RAW_MANIFEST_PATH = RUN_ROOT / "RAW_OUTPUT_MANIFEST.json"
DISAGREEMENT_PATH = RUN_ROOT / "FULL_REVIEW_DISAGREEMENT_ANALYSIS.json"
EVIDENCE_PATH = RUN_ROOT / "OFFICIAL_CALIBRATION_EVIDENCE.json"
PACKAGE_HASH = "ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603"
BRIEF_HASH = "3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c"
COHORT_IDS = ("C1", "C2", "C3")


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def visibility(kind: str) -> dict[str, Any]:
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


def load_frozen_output(context_id: str, expected_raw_hash: str) -> dict[str, Any]:
    path = RUN_ROOT / "raw-outputs" / context_id / "raw-output.txt"
    require(path.is_file(), f"missing raw output: {context_id}")
    require(file_sha256(path) == expected_raw_hash, f"raw output drift: {context_id}")
    output = load_json(path)
    require(isinstance(output, dict), f"raw output is not an object: {context_id}")
    return output


def main() -> int:
    require(not DISAGREEMENT_PATH.exists(), "disagreement analysis already exists")
    require(not EVIDENCE_PATH.exists(), "official evidence already exists")

    input_manifest = load_json(INPUT_MANIFEST_PATH)
    raw_manifest = load_json(RAW_MANIFEST_PATH)
    require(raw_manifest["raw_outputs_frozen_before_oracle_scoring"] is True, "raw freeze ordering not established")
    require(raw_manifest["verdicts_interpreted"] is False, "raw freeze manifest was not pre-score")
    require(raw_manifest["actual_attempt_count"] == 48, "raw attempt count mismatch")
    require(raw_manifest["retry_count"] == 0, "reviewer retry found")

    input_by_id = {
        item["planned_context_id"]: item for item in input_manifest["contexts"]
    }
    raw_by_id = {
        item["planned_context_id"]: item for item in raw_manifest["contexts"]
    }
    require(set(input_by_id) == set(raw_by_id), "input/raw context set mismatch")

    cohorts: list[dict[str, Any]] = []
    full_outputs: dict[str, dict[str, Any]] = {}
    for cohort_id in COHORT_IDS:
        full_id = f"{cohort_id}-FULL-001"
        full_entry = raw_by_id[full_id]
        full_output = load_frozen_output(
            full_id, full_entry["files"]["raw-output.txt"]["sha256"]
        )
        full_envelope = load_json(RUN_ROOT / "inputs" / full_id / "run-envelope.json")
        require(full_output.get("review_run_id") == full_envelope["review_run_id"], f"full run binding mismatch: {cohort_id}")
        require(full_output.get("reviewer_context_id") == full_envelope["reviewer_context_id"], f"full context binding mismatch: {cohort_id}")
        full_outputs[cohort_id] = full_output

        golden_wrappers: list[dict[str, Any]] = []
        raw_output_hashes: list[str] = []
        for case_number in range(1, 16):
            case_id = f"G-{case_number:03d}"
            context_id = f"{cohort_id}-{case_id}-001"
            entry = raw_by_id[context_id]
            output = load_frozen_output(
                context_id, entry["files"]["raw-output.txt"]["sha256"]
            )
            envelope = load_json(
                RUN_ROOT / "inputs" / context_id / "run-envelope.json"
            )
            require(output.get("review_run_id") == envelope["review_run_id"], f"golden run binding mismatch: {context_id}")
            require(output.get("reviewer_context_id") == envelope["reviewer_context_id"], f"golden context binding mismatch: {context_id}")
            raw_output = {
                "case_id": case_id,
                "review_output": output,
                "run_envelope": envelope,
            }
            raw_output_sha256 = canonical_sha256(raw_output)
            raw_output_hashes.append(raw_output_sha256)
            golden_wrappers.append(
                {
                    "raw_output": raw_output,
                    "raw_output_sha256": raw_output_sha256,
                    "review_output_sha256": canonical_sha256(output),
                    "run_envelope_sha256": canonical_sha256(envelope),
                    "visibility": visibility("golden"),
                }
            )

        cohorts.append(
            {
                "cohort_id": cohort_id,
                "full_review": {
                    "review_output": full_output,
                    "review_output_sha256": canonical_sha256(full_output),
                    "run_envelope": full_envelope,
                    "run_envelope_sha256": canonical_sha256(full_envelope),
                    "visibility": visibility("full"),
                },
                "golden_output_set_sha256": canonical_sha256(raw_output_hashes),
                "golden_reviews": golden_wrappers,
            }
        )

    records_by_cohort = {
        cohort_id: {
            record["review_identity"]: record
            for record in full_outputs[cohort_id].get("records", [])
        }
        for cohort_id in COHORT_IDS
    }
    identity_union = set().union(*(set(items) for items in records_by_cohort.values()))
    identity_intersection = set.intersection(
        *(set(items) for items in records_by_cohort.values())
    )
    disagreements: list[dict[str, Any]] = []
    for identity in sorted(identity_intersection):
        decisions = {
            cohort_id: {
                "rationale_code": records_by_cohort[cohort_id][identity]["rationale_code"],
                "verdict": records_by_cohort[cohort_id][identity]["verdict"],
            }
            for cohort_id in COHORT_IDS
        }
        if len({(item["verdict"], item["rationale_code"]) for item in decisions.values()}) > 1:
            disagreements.append(
                {"decisions": decisions, "review_identity": identity}
            )

    coverage_gaps = [
        {
            "present_in": [
                cohort_id
                for cohort_id in COHORT_IDS
                if identity in records_by_cohort[cohort_id]
            ],
            "review_identity": identity,
        }
        for identity in sorted(identity_union - identity_intersection)
    ]
    classifications: list[dict[str, Any]] = []
    require(not disagreements, "verdict/rationale disagreements require classifier contexts")
    disagreement_analysis = {
        "classifier_context_count": 0,
        "coverage_gap_count": len(coverage_gaps),
        "coverage_gaps": coverage_gaps,
        "disagreement_classifications": classifications,
        "full_identity_counts": {
            cohort_id: len(records_by_cohort[cohort_id]) for cohort_id in COHORT_IDS
        },
        "identity_intersection_count": len(identity_intersection),
        "identity_union_count": len(identity_union),
        "rationale_verdict_disagreement_count": len(disagreements),
        "rationale_verdict_disagreements": disagreements,
        "schema_version": "joewrks.semantic-review-full-disagreement-analysis/1.0",
    }
    evidence = {
        "cohorts": cohorts,
        "disagreement_classifications": classifications,
        "full_reviewer_package": {
            "reviewer_brief_hash": BRIEF_HASH,
            "reviewer_input_package_hash": PACKAGE_HASH,
        },
        "schema_version": "joewrks.semantic-review-official-calibration-input/1.0",
    }

    DISAGREEMENT_PATH.write_bytes(canonical_bytes(disagreement_analysis))
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    print("OFFICIAL_EVIDENCE_ASSEMBLY=PASS")
    print(f"FULL_IDENTITY_COUNTS={json.dumps(disagreement_analysis['full_identity_counts'], sort_keys=True)}")
    print(f"COVERAGE_GAPS={len(coverage_gaps)}")
    print(f"VERDICT_RATIONALE_DISAGREEMENTS={len(disagreements)}")
    print("DISAGREEMENT_CLASSIFICATIONS=0")
    print(f"OFFICIAL_EVIDENCE_SHA256={file_sha256(EVIDENCE_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
