import importlib.util
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.goldens import (
    GoldenError,
    evaluate_goldens,
    verify_golden_packages,
)
from downstream.semantic_review.hashing import canonical_json_bytes
from downstream.semantic_review.output import OutputError
from downstream.semantic_review.package import (
    load_and_verify_package,
    verify_run_envelope,
)


CALIBRATION_ROOT = ROOT / "evals" / "semantic-review-v0.4.3" / "calibration"
CONTROL_PLANE_PATH = CALIBRATION_ROOT / "control_plane.py"
CONTROLLER_PATH = CALIBRATION_ROOT / "official_calibration_controller.py"
FULL_PACKAGE_ROOT = (
    CALIBRATION_ROOT / "semantic-review-calibration-v1" / "reviewer-package"
)
GOLDEN_CASES_PATH = (
    ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-cases.json"
)
GOLDEN_ANSWERS_PATH = (
    ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-answers.json"
)
GOLDEN_OUTPUTS_PATH = (
    ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-review-outputs.json"
)
EXPECTED_ENVELOPE_KEYS = {
    "review_run_id",
    "reviewer_context_id",
    "reviewer_input_package_hash",
    "reviewer_brief_hash",
    "isolation_attestation",
    "isolation_attestation_hash",
}


def load_control_plane():
    spec = importlib.util.spec_from_file_location(
        "semantic_review_calibration_control_plane", CONTROL_PLANE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_controller():
    spec = importlib.util.spec_from_file_location(
        "semantic_review_official_calibration_controller_actual_path",
        CONTROLLER_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SemanticReviewCalibrationControlPlaneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control_plane = load_control_plane()
        cls.cases = json.loads(GOLDEN_CASES_PATH.read_text(encoding="utf-8"))
        cls.cases_by_id = {case["case_id"]: case for case in cls.cases}
        cls.packages = verify_golden_packages(cls.cases)
        cls.answers = json.loads(GOLDEN_ANSWERS_PATH.read_text(encoding="utf-8"))
        cls.outputs = json.loads(GOLDEN_OUTPUTS_PATH.read_text(encoding="utf-8"))

    @staticmethod
    def _approved_full_output(package, envelope):
        records = []
        obligations = package["semantic_obligation_index"]["obligations"]
        for identity in package["expected_identities"]:
            item = package["identity_inventory"][identity]
            owned = sorted(
                (
                    obligation
                    for obligation in obligations
                    if (
                        obligation["owner_kind"],
                        obligation["owner_id"],
                        obligation["owning_field"],
                    )
                    == (
                        item["owner_kind"],
                        item["owner_id"],
                        item["semantic_field"],
                    )
                ),
                key=lambda obligation: obligation["obligation_id"],
            )
            evidence_by_bytes = {
                canonical_json_bytes(reference): reference
                for obligation in owned
                for reference in obligation["canonical_refs"]
            }
            records.append(
                {
                    "review_schema_version": "joewrks.semantic-review/1.0",
                    "reviewer_brief_hash": package["reviewer_brief_hash"],
                    "reviewer_input_manifest_hash": package[
                        "reviewer_input_manifest_hash"
                    ],
                    "contract_hash": package["contract_hash"],
                    "review_identity": identity,
                    "owner_kind": item["owner_kind"],
                    "owner_id": item["owner_id"],
                    "semantic_field": item["semantic_field"],
                    "semantic_value_hash": item["semantic_value_hash"],
                    "provenance_hashes": item["provenance_hashes"],
                    "provenance_set_hash": item["provenance_set_hash"],
                    "responsibility_rule_id": item["responsibility_rule_id"],
                    "completeness_mode": item["completeness_mode"],
                    "sibling_review_identity_refs": [],
                    "semantic_obligation_ids": [
                        obligation["obligation_id"] for obligation in owned
                    ],
                    "test_obligation_refs": sorted(
                        {
                            reference
                            for obligation in owned
                            for reference in obligation["required_test_refs"]
                        }
                    ),
                    "verdict": "APPROVED",
                    "rationale_code": "SUPPORTED_EXACTLY",
                    "canonical_evidence_refs": [
                        evidence_by_bytes[key] for key in sorted(evidence_by_bytes)
                    ],
                    "reviewer_explanation": (
                        "Synthetic integration output exercises the frozen validator path."
                    ),
                }
            )
        return {
            "review_schema_version": "joewrks.semantic-review/1.0",
            "review_run_id": envelope["review_run_id"],
            "reviewer_context_id": envelope["reviewer_context_id"],
            "isolation_attestation_hash": envelope["isolation_attestation_hash"],
            "reviewer_brief_hash": package["reviewer_brief_hash"],
            "reviewer_input_manifest_hash": package["reviewer_input_manifest_hash"],
            "reviewer_input_package_hash": package["reviewer_input_package_hash"],
            "contract_hash": package["contract_hash"],
            "responsibility_profile_hash": package["responsibility_profile_hash"],
            "semantic_obligation_index_hash": package[
                "semantic_obligation_index_hash"
            ],
            "review_identity_inventory_hash": package[
                "review_identity_inventory_hash"
            ],
            "preflight_errors": [],
            "records": records,
            "summary": {
                "expected_identity_count": len(records),
                "record_count": len(records),
                "unique_identity_count": len(records),
                "pending_count": 0,
                "verdict_counts": {
                    "APPROVED": len(records),
                    "REJECTED_CANDIDATE": 0,
                    "RUBRIC_ERROR": 0,
                    "INPUT_PACKAGE_ERROR": 0,
                },
                "complete": True,
            },
        }

    def _assemble_fixture_cohort(self, root):
        assembled = []
        for frozen in self.outputs:
            case_id = frozen["case_id"]
            context_id = f"ACTUAL-PATH-{case_id}"
            run_id = f"ACTUAL-PATH-RUN-{case_id}"
            envelope = self.control_plane.materialize_run_envelope(
                self.packages[case_id],
                review_run_id=run_id,
                reviewer_context_id=context_id,
            )
            output = copy.deepcopy(frozen["review_output"])
            output["review_run_id"] = run_id
            output["reviewer_context_id"] = context_id
            output["isolation_attestation_hash"] = envelope[
                "isolation_attestation_hash"
            ]
            raw_path = root / case_id / "raw-output.txt"
            raw_path.parent.mkdir(parents=True)
            raw_path.write_text(json.dumps(output), encoding="utf-8")
            assembled.append(
                self.control_plane.assemble_golden_review(
                    case=self.cases_by_id[case_id],
                    package=self.packages[case_id],
                    run_envelope=envelope,
                    raw_output_path=raw_path,
                )["raw_output"]
            )
        return assembled

    def test_materializer_builds_production_valid_identical_envelopes(self):
        self.assertTrue(
            CONTROL_PLANE_PATH.is_file(),
            "calibration control-plane materializer is required",
        )
        control_plane = self.control_plane
        full_package = load_and_verify_package(FULL_PACKAGE_ROOT)
        cases = json.loads(GOLDEN_CASES_PATH.read_text(encoding="utf-8"))
        golden_package = verify_golden_packages(cases)["G-001"]

        full = control_plane.materialize_run_envelope(
            full_package,
            review_run_id="RUN-02-C1-FULL",
            reviewer_context_id="C1-FULL-001",
        )
        golden = control_plane.materialize_run_envelope(
            golden_package,
            review_run_id="RUN-02-C1-G-001",
            reviewer_context_id="C1-G-001-001",
        )

        self.assertEqual(set(full), EXPECTED_ENVELOPE_KEYS)
        self.assertEqual(set(golden), EXPECTED_ENVELOPE_KEYS)
        self.assertEqual(set(full), set(golden))
        self.assertIs(verify_run_envelope(full, full_package), full)
        self.assertIs(verify_run_envelope(golden, golden_package), golden)

    def test_raw_output_assembly_adds_exact_frozen_case_manifest_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            assembled = self._assemble_fixture_cohort(Path(temporary))

        self.assertEqual(
            set(assembled[0]),
            {"case_id", "case_manifest_hash", "run_envelope", "review_output"},
        )
        self.assertEqual(
            assembled[0]["case_manifest_hash"],
            self.cases_by_id["G-001"]["case_manifest_hash"],
        )
        report = evaluate_goldens(assembled, self.answers, self.cases)
        self.assertEqual(report["verdict_hits"], 15)
        self.assertEqual(report["rationale_code_hits"], 15)

    def test_missing_or_wrong_case_manifest_hash_is_rejected_by_production(self):
        with tempfile.TemporaryDirectory() as temporary:
            assembled = self._assemble_fixture_cohort(Path(temporary))
        for mutation in ("missing", "wrong"):
            with self.subTest(mutation=mutation):
                invalid = copy.deepcopy(assembled)
                if mutation == "missing":
                    invalid[0].pop("case_manifest_hash")
                else:
                    invalid[0]["case_manifest_hash"] = "0" * 64
                with self.assertRaises(GoldenError) as caught:
                    evaluate_goldens(invalid, self.answers, self.cases)
                self.assertEqual(caught.exception.code, "GOLDEN_OUTPUT_INVALID")
                self.assertEqual(str(caught.exception), "GOLDEN_OUTPUT_INVALID: binding: G-001")

    def test_actual_raw_file_path_reaches_official_controller_with_48_contexts(self):
        controller = load_controller()
        full_package = load_and_verify_package(FULL_PACKAGE_ROOT)
        cohorts = []
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for cohort_id in ("C1", "C2", "C3"):
                full_context = f"ACTUAL-PATH-{cohort_id}-FULL"
                full_envelope = self.control_plane.materialize_run_envelope(
                    full_package,
                    review_run_id=f"ACTUAL-PATH-RUN-{cohort_id}-FULL",
                    reviewer_context_id=full_context,
                )
                full_path = root / full_context / "raw-output.txt"
                full_path.parent.mkdir(parents=True)
                full_path.write_text(
                    json.dumps(
                        self._approved_full_output(full_package, full_envelope)
                    ),
                    encoding="utf-8",
                )
                full_review = self.control_plane.assemble_full_review(
                    package=full_package,
                    run_envelope=full_envelope,
                    raw_output_path=full_path,
                )

                golden_reviews = []
                for frozen in self.outputs:
                    case_id = frozen["case_id"]
                    context_id = f"ACTUAL-PATH-{cohort_id}-{case_id}"
                    envelope = self.control_plane.materialize_run_envelope(
                        self.packages[case_id],
                        review_run_id=f"ACTUAL-PATH-RUN-{cohort_id}-{case_id}",
                        reviewer_context_id=context_id,
                    )
                    output = copy.deepcopy(frozen["review_output"])
                    output["review_run_id"] = envelope["review_run_id"]
                    output["reviewer_context_id"] = context_id
                    output["isolation_attestation_hash"] = envelope[
                        "isolation_attestation_hash"
                    ]
                    raw_path = root / context_id / "raw-output.txt"
                    raw_path.parent.mkdir(parents=True)
                    raw_path.write_text(json.dumps(output), encoding="utf-8")
                    golden_reviews.append(
                        self.control_plane.assemble_golden_review(
                            case=self.cases_by_id[case_id],
                            package=self.packages[case_id],
                            run_envelope=envelope,
                            raw_output_path=raw_path,
                        )
                    )
                cohorts.append(
                    self.control_plane.assemble_cohort(
                        cohort_id=cohort_id,
                        full_review=full_review,
                        golden_reviews=golden_reviews,
                    )
                )

        evidence = self.control_plane.assemble_official_evidence(
            full_package=full_package,
            cohorts=cohorts,
            disagreement_classifications=[],
        )
        result = controller.evaluate_official_calibration(evidence, real_mode=True)
        self.assertEqual(result["context_count"], 48)
        self.assertEqual(result["aggregate_golden_conjunction"], "PASS")

    def test_prebuilt_wrapper_cannot_bypass_actual_raw_output_assembly(self):
        frozen = copy.deepcopy(self.outputs[0])
        package = self.packages["G-001"]
        envelope = frozen["run_envelope"]
        with tempfile.TemporaryDirectory() as temporary:
            raw_path = Path(temporary) / "raw-output.txt"
            raw_path.write_text(json.dumps(frozen), encoding="utf-8")
            with self.assertRaises(OutputError) as caught:
                self.control_plane.assemble_golden_review(
                    case=self.cases_by_id["G-001"],
                    package=package,
                    run_envelope=envelope,
                    raw_output_path=raw_path,
                )
        self.assertEqual(caught.exception.code, "OUTPUT_SCHEMA_VIOLATION")

    def test_assembler_rejects_case_manifest_hash_drift_before_wrapping(self):
        frozen = copy.deepcopy(self.outputs[0])
        bad_case = copy.deepcopy(self.cases_by_id["G-001"])
        bad_case["case_manifest_hash"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            raw_path = Path(temporary) / "raw-output.txt"
            raw_path.write_text(
                json.dumps(frozen["review_output"]), encoding="utf-8"
            )
            with self.assertRaises(ValueError) as caught:
                self.control_plane.assemble_golden_review(
                    case=bad_case,
                    package=self.packages["G-001"],
                    run_envelope=frozen["run_envelope"],
                    raw_output_path=raw_path,
                )
        self.assertEqual(str(caught.exception), "CALIBRATION_GOLDEN_CASE_HASH_DRIFT")


if __name__ == "__main__":
    unittest.main()
