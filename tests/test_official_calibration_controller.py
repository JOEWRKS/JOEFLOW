import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_ROOT = (
    ROOT / "evals" / "semantic-review-v0.4.3" / "calibration"
)
CONTROLLER_PATH = CALIBRATION_ROOT / "official_calibration_controller.py"
GOLDEN_OUTPUTS_PATH = (
    ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-review-outputs.json"
)
GOLDEN_ANSWERS_PATH = (
    ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-answers.json"
)

PACKAGE_HASH = "ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603"
BRIEF_HASH = "3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c"
DRIFT_HASH = "0" * 64


def canonical_sha256(value):
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_controller():
    spec = importlib.util.spec_from_file_location(
        "official_calibration_controller", CONTROLLER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def visibility(kind):
    visible_package = (
        "exact_full_reviewer_package"
        if kind == "full"
        else "exact_single_golden_package"
    )
    return {
        "manifest_only_isolation_attested": True,
        "visible_inputs": [visible_package, "run_envelope"],
        "other_context_outputs_visible": False,
        "prior_verdicts_visible": False,
        "golden_answers_visible": False,
        "seed_oracle_visible": False,
        "repository_history_visible": False,
        "sibling_packages_visible": False,
        "controller_disagreement_analysis_visible": False,
    }


def rehash_golden_wrapper(wrapper):
    wrapper["run_envelope_sha256"] = canonical_sha256(
        wrapper["raw_output"]["run_envelope"]
    )
    wrapper["review_output_sha256"] = canonical_sha256(
        wrapper["raw_output"]["review_output"]
    )
    wrapper["raw_output_sha256"] = canonical_sha256(wrapper["raw_output"])


def rehash_golden_set(cohort):
    cohort["golden_output_set_sha256"] = canonical_sha256(
        [item["raw_output_sha256"] for item in cohort["golden_reviews"]]
    )


def rebind_golden_context(wrapper, context_id):
    raw = wrapper["raw_output"]
    run_id = f"TEST-ONLY-RUN-{context_id}"
    raw["run_envelope"]["reviewer_context_id"] = context_id
    raw["run_envelope"]["review_run_id"] = run_id
    raw["review_output"]["reviewer_context_id"] = context_id
    raw["review_output"]["review_run_id"] = run_id
    rehash_golden_wrapper(wrapper)


def rehash_full_wrapper(wrapper):
    wrapper["run_envelope_sha256"] = canonical_sha256(wrapper["run_envelope"])
    wrapper["review_output_sha256"] = canonical_sha256(wrapper["review_output"])


def rebind_full_context(wrapper, context_id):
    run_id = f"TEST-ONLY-RUN-{context_id}"
    wrapper["run_envelope"]["reviewer_context_id"] = context_id
    wrapper["run_envelope"]["review_run_id"] = run_id
    wrapper["review_output"]["reviewer_context_id"] = context_id
    wrapper["review_output"]["review_run_id"] = run_id
    rehash_full_wrapper(wrapper)


def build_evidence():
    frozen_outputs = json.loads(GOLDEN_OUTPUTS_PATH.read_text(encoding="utf-8"))
    cohorts = []
    for cohort_id in ("C1", "C2", "C3"):
        full_context = f"TEST-ONLY-{cohort_id}-FULL"
        full_run_id = f"TEST-ONLY-RUN-{cohort_id}-FULL"
        full_review = {
            "run_envelope": {
                "review_run_id": full_run_id,
                "reviewer_context_id": full_context,
                "reviewer_input_package_hash": PACKAGE_HASH,
                "reviewer_brief_hash": BRIEF_HASH,
                "isolation_attestation": {
                    "fresh_context": True,
                    "previous_verdict_access": False,
                    "manifest_only_evidence": True,
                },
            },
            "review_output": {
                "review_run_id": full_run_id,
                "reviewer_context_id": full_context,
                "reviewer_input_package_hash": PACKAGE_HASH,
                "reviewer_brief_hash": BRIEF_HASH,
                "records": [],
                "preflight_errors": [],
            },
            "visibility": visibility("full"),
        }
        rehash_full_wrapper(full_review)

        golden_reviews = []
        for frozen in frozen_outputs:
            raw = copy.deepcopy(frozen)
            context_id = f"TEST-ONLY-{cohort_id}-{frozen['case_id']}"
            run_id = f"TEST-ONLY-RUN-{cohort_id}-{frozen['case_id']}"
            raw["run_envelope"]["reviewer_context_id"] = context_id
            raw["run_envelope"]["review_run_id"] = run_id
            raw["review_output"]["reviewer_context_id"] = context_id
            raw["review_output"]["review_run_id"] = run_id
            wrapper = {
                "raw_output": raw,
                "visibility": visibility("golden"),
            }
            rehash_golden_wrapper(wrapper)
            golden_reviews.append(wrapper)
        cohort = {
            "cohort_id": cohort_id,
            "full_review": full_review,
            "golden_reviews": golden_reviews,
        }
        rehash_golden_set(cohort)
        cohorts.append(cohort)
    return {
        "schema_version": "joewrks.semantic-review-official-calibration-input/1.0",
        "full_reviewer_package": {
            "reviewer_input_package_hash": PACKAGE_HASH,
            "reviewer_brief_hash": BRIEF_HASH,
        },
        "cohorts": cohorts,
        "disagreement_classifications": [],
    }


class OfficialCalibrationControllerNegativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = load_controller()

    def assert_rejected(self, evidence, code, *, real_mode=False):
        with self.assertRaises(self.controller.CalibrationControllerError) as caught:
            self.controller.evaluate_official_calibration(
                evidence, real_mode=real_mode
            )
        self.assertEqual(caught.exception.code, code)

    def test_rejects_scalar_fabricated_golden_report_without_raw_outputs(self):
        evidence = {
            "golden_report": {
                "case_count": 15,
                "verdict_accuracy": 1,
                "rationale_code_accuracy": 1,
            }
        }
        self.assert_rejected(evidence, "RAW_GOLDEN_OUTPUTS_REQUIRED")

    def test_rejects_only_two_golden_cohorts(self):
        evidence = build_evidence()
        evidence["cohorts"].pop()
        self.assert_rejected(evidence, "COHORT_SET_MISMATCH")

    def test_rejects_one_missing_golden_case(self):
        evidence = build_evidence()
        evidence["cohorts"][0]["golden_reviews"].pop()
        rehash_golden_set(evidence["cohorts"][0])
        self.assert_rejected(evidence, "GOLDEN_CASE_SET_MISMATCH")

    def test_rejects_reused_golden_context_id(self):
        evidence = build_evidence()
        cohort = evidence["cohorts"][0]
        reused = cohort["golden_reviews"][0]["raw_output"]["run_envelope"][
            "reviewer_context_id"
        ]
        rebind_golden_context(cohort["golden_reviews"][1], reused)
        rehash_golden_set(cohort)
        self.assert_rejected(evidence, "CONTEXT_ID_REUSE")

    def test_rejects_reused_full_review_context_id(self):
        evidence = build_evidence()
        reused = evidence["cohorts"][0]["full_review"]["run_envelope"][
            "reviewer_context_id"
        ]
        rebind_full_context(evidence["cohorts"][1]["full_review"], reused)
        self.assert_rejected(evidence, "CONTEXT_ID_REUSE")

    def test_rejects_golden_answer_exposure(self):
        evidence = build_evidence()
        evidence["cohorts"][0]["golden_reviews"][0]["visibility"][
            "golden_answers_visible"
        ] = True
        self.assert_rejected(evidence, "FORBIDDEN_CONTEXT_EXPOSURE")

    def test_rejects_seed_oracle_exposure(self):
        evidence = build_evidence()
        evidence["cohorts"][0]["full_review"]["visibility"][
            "seed_oracle_visible"
        ] = True
        self.assert_rejected(evidence, "FORBIDDEN_CONTEXT_EXPOSURE")

    def test_rejects_every_other_forbidden_visibility_channel(self):
        fields = (
            "other_context_outputs_visible",
            "prior_verdicts_visible",
            "repository_history_visible",
            "sibling_packages_visible",
            "controller_disagreement_analysis_visible",
        )
        for field in fields:
            with self.subTest(field=field):
                evidence = build_evidence()
                evidence["cohorts"][0]["full_review"]["visibility"][field] = True
                self.assert_rejected(evidence, "FORBIDDEN_CONTEXT_EXPOSURE")

    def test_rejects_package_hash_drift(self):
        evidence = build_evidence()
        evidence["full_reviewer_package"]["reviewer_input_package_hash"] = DRIFT_HASH
        self.assert_rejected(evidence, "PACKAGE_HASH_MISMATCH")

    def test_rejects_reviewer_brief_hash_drift(self):
        evidence = build_evidence()
        evidence["full_reviewer_package"]["reviewer_brief_hash"] = DRIFT_HASH
        self.assert_rejected(evidence, "BRIEF_HASH_MISMATCH")

    def test_rejects_full_review_output_bound_to_different_package(self):
        evidence = build_evidence()
        full_review = evidence["cohorts"][0]["full_review"]
        full_review["review_output"]["reviewer_input_package_hash"] = DRIFT_HASH
        rehash_full_wrapper(full_review)
        self.assert_rejected(evidence, "FULL_REVIEW_PACKAGE_MISMATCH")

    def _assert_oracle_rejected(self, oracle, code, *, expected_sha256=None):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "golden-answers.json"
            path.write_text(
                json.dumps(oracle, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            previous_path = self.controller.GOLDEN_ANSWERS_PATH
            missing = object()
            previous_hash = getattr(
                self.controller, "FROZEN_ORACLE_SHA256", missing
            )
            self.controller.GOLDEN_ANSWERS_PATH = path
            if expected_sha256 is not None:
                self.controller.FROZEN_ORACLE_SHA256 = expected_sha256
            try:
                self.assert_rejected(build_evidence(), code, real_mode=True)
            finally:
                self.controller.GOLDEN_ANSWERS_PATH = previous_path
                if previous_hash is missing:
                    if hasattr(self.controller, "FROZEN_ORACLE_SHA256"):
                        del self.controller.FROZEN_ORACLE_SHA256
                else:
                    self.controller.FROZEN_ORACLE_SHA256 = previous_hash

    def test_rejects_non_approved_oracle_status_before_reviewer_evaluation(self):
        oracle = json.loads(GOLDEN_ANSWERS_PATH.read_text(encoding="utf-8"))
        oracle["adjudication_status"] = "PM_SPEC_ORACLE_NOT_HUMAN_ADJUDICATED"
        sha256 = hashlib.sha256(
            (json.dumps(oracle, indent=2) + "\n").encode("utf-8")
        ).hexdigest()
        self._assert_oracle_rejected(oracle, "ORACLE_STATUS_NOT_APPROVED", expected_sha256=sha256)

    def test_rejects_oracle_file_hash_drift_before_reviewer_evaluation(self):
        oracle = json.loads(GOLDEN_ANSWERS_PATH.read_text(encoding="utf-8"))
        self._assert_oracle_rejected(oracle, "ORACLE_HASH_MISMATCH")

    def test_rejects_one_changed_oracle_answer_pair_before_reviewer_evaluation(self):
        oracle = json.loads(GOLDEN_ANSWERS_PATH.read_text(encoding="utf-8"))
        oracle["answers"][0]["rationale_code"] = "UNSUPPORTED_OVERREACH"
        sha256 = hashlib.sha256(
            (json.dumps(oracle, indent=2) + "\n").encode("utf-8")
        ).hexdigest()
        self._assert_oracle_rejected(
            oracle, "GOLDEN_ORACLE_SPEC_MISMATCH", expected_sha256=sha256
        )

    def test_rejects_oracle_bytes_in_reviewer_visible_context_content(self):
        evidence = build_evidence()
        full_review = evidence["cohorts"][0]["full_review"]
        full_review["run_envelope"]["reviewer_visible_context_content"] = (
            GOLDEN_ANSWERS_PATH.read_text(encoding="utf-8")
        )
        rehash_full_wrapper(full_review)
        self.assert_rejected(evidence, "FORBIDDEN_CONTEXT_EXPOSURE", real_mode=True)

    def test_rejects_oracle_bytes_in_reviewer_visible_package_content(self):
        evidence = build_evidence()
        evidence["full_reviewer_package"]["reviewer_visible_package_content"] = (
            GOLDEN_ANSWERS_PATH.read_text(encoding="utf-8")
        )
        self.assert_rejected(evidence, "FORBIDDEN_CONTEXT_EXPOSURE", real_mode=True)

    def test_rejects_oracle_bytes_visible_to_a_reviewer_context(self):
        evidence = build_evidence()
        evidence["cohorts"][0]["golden_reviews"][0]["visibility"][
            "golden_answers_visible"
        ] = True
        self.assert_rejected(evidence, "FORBIDDEN_CONTEXT_EXPOSURE", real_mode=True)

    def test_accepts_the_pm_approved_oracle_without_completed_human_forms(self):
        oracle_before = GOLDEN_ANSWERS_PATH.read_bytes()
        result = self.controller.evaluate_official_calibration(
            build_evidence(), real_mode=True
        )
        self.assertEqual(result["aggregate_golden_conjunction"], "PASS")
        self.assertEqual(result["context_count"], 48)
        self.assertEqual(len(result["per_cohort_golden_reports"]), 3)
        self.assertEqual(GOLDEN_ANSWERS_PATH.read_bytes(), oracle_before)


if __name__ == "__main__":
    unittest.main()
