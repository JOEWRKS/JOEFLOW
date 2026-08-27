import copy
import json
import re
import sys
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.gate import evaluate_reliability_gate
from downstream.semantic_review.hashing import canonical_json_bytes, sha256_bytes
from tests.semantic_review_support import (
    disagreement_classification,
    make_run_set,
    passing_golden_report,
    replace_verdict_and_recount,
)


A = "APPROVED"
R = "REJECTED_CANDIDATE"
SUMMARY_PATH = (
    ROOT
    / "tests"
    / "fixtures"
    / "semantic-review-v1"
    / "v042-instability-summary.json"
)


class SemanticReviewNegativeRegressionTest(unittest.TestCase):
    def _evaluate(self, run_set, *, golden=None, classifications=None):
        return evaluate_reliability_gate(
            *run_set,
            passing_golden_report() if golden is None else golden,
            [] if classifications is None else classifications,
        )

    def _known_good(self, count=20):
        verdicts = [A] * (count // 2) + [R] * (count - count // 2)
        run_set = make_run_set(verdicts)
        self.assertTrue(self._evaluate(run_set)["passed"])
        return run_set

    def _source_hash(self, run_set):
        return sha256_bytes(canonical_json_bytes(run_set))

    def _assert_isolated_failure(self, source, mutated, expected, **kwargs):
        frozen = self._source_hash(source)
        report = self._evaluate(mutated, **kwargs)
        self.assertFalse(report["passed"])
        self.assertEqual(set(report["failures"]), expected)
        self.assertEqual(self._source_hash(source), frozen)
        return report

    def test_gate_rejects_one_normative_brief_byte_difference(self):
        source = self._known_good()
        mutated = copy.deepcopy(source)
        package, envelope, output = mutated[0][2], mutated[1][2], mutated[2][2]
        package["reviewer_brief_text"] = package["reviewer_brief_text"].replace(
            "rules", "rulex"
        )
        package.update(
            {
                "reviewer_brief_hash": "8" * 64,
                "reviewer_input_manifest_hash": "9" * 64,
                "reviewer_input_package_hash": "a" * 64,
            }
        )
        package["role_hashes"]["reviewer_brief"] = "8" * 64
        envelope.update(
            {"reviewer_brief_hash": "8" * 64, "reviewer_input_package_hash": "a" * 64}
        )
        output.update(
            {
                "reviewer_brief_hash": "8" * 64,
                "reviewer_input_manifest_hash": "9" * 64,
                "reviewer_input_package_hash": "a" * 64,
            }
        )
        for record in output["records"]:
            record["reviewer_brief_hash"] = "8" * 64
            record["reviewer_input_manifest_hash"] = "9" * 64
        self._assert_isolated_failure(
            source, mutated, {"FAIL/BRIEF_IDENTITY_MISMATCH"}
        )

    def test_gate_rejects_completeness_mode_drift(self):
        source = self._known_good()
        mutated = copy.deepcopy(source)
        package, envelope, output = mutated[0][2], mutated[1][2], mutated[2][2]
        identity = package["expected_identities"][0]
        package.update(
            {
                "responsibility_profile_hash": "8" * 64,
                "reviewer_input_manifest_hash": "9" * 64,
                "reviewer_input_package_hash": "a" * 64,
            }
        )
        package["identity_inventory"][identity]["completeness_mode"] = "COMPOSITIONAL"
        package["responsibility_profile_excerpt"]["FR-A09"][
            "completeness_mode"
        ] = "COMPOSITIONAL"
        envelope["reviewer_input_package_hash"] = "a" * 64
        output.update(
            {
                "responsibility_profile_hash": "8" * 64,
                "reviewer_input_manifest_hash": "9" * 64,
                "reviewer_input_package_hash": "a" * 64,
            }
        )
        target = next(r for r in output["records"] if r["review_identity"] == identity)
        target["completeness_mode"] = "COMPOSITIONAL"
        for record in output["records"]:
            record["reviewer_input_manifest_hash"] = "9" * 64
        self._assert_isolated_failure(
            source, mutated, {"FAIL/PACKAGE_IDENTITY_MISMATCH"}
        )

    def test_gate_rejects_repeated_same_rule_sibling_duplication_execution_errors(self):
        cases = {
            case["case_id"]: case
            for case in json.loads(
                (SUMMARY_PATH.parent / "golden-cases.json").read_text(encoding="utf-8")
            )
        }
        answers = {
            item["case_id"]: item
            for item in json.loads(
                (SUMMARY_PATH.parent / "golden-answers.json").read_text(encoding="utf-8")
            )["answers"]
        }
        for case_id in ("G-003", "G-005", "G-008"):
            self.assertEqual(answers[case_id]["verdict"], "APPROVED")
            self.assertTrue(cases[case_id]["expected_identity_inventory"])
        source = self._known_good(200)
        mutated = copy.deepcopy(source)
        targets = [record["review_identity"] for record in mutated[2][2]["records"][:2]]
        for identity in targets:
            replace_verdict_and_recount(
                mutated[2][2], identity, R, "MISSING_OWNED_SEMANTIC"
            )
        interpretation = "incorrectly required sibling-owned semantics in this LOCAL field"
        classifications = [
            disagreement_classification(identity, interpretation=interpretation)
            for identity in targets
        ]
        report = self._assert_isolated_failure(
            source,
            mutated,
            {"FAIL/RESPONSIBILITY_RULE_INSTABILITY"},
            classifications=classifications,
        )
        self.assertEqual(len(set(targets)), 2)
        self.assertTrue(
            all(item["cause_code"] == "REVIEWER_EXECUTION_ERROR" for item in classifications)
        )
        self.assertEqual(
            {item["interpretation"] for item in classifications}, {interpretation}
        )
        self.assertGreaterEqual(
            report["metrics"]["three_review_unanimity"], Fraction(99, 100)
        )
        self.assertTrue(
            all(item.value >= Fraction(9, 10) for item in report["metrics"]["pairwise_cohen"])
        )
        self.assertGreaterEqual(
            report["metrics"]["fleiss_kappa"].value, Fraction(9, 10)
        )

    def test_gate_rejects_missing_review_identity(self):
        source = self._known_good()
        mutated = copy.deepcopy(source)
        output = mutated[2][2]
        output["records"].pop()
        counts = Counter(record["verdict"] for record in output["records"])
        output["summary"].update(
            {
                "record_count": len(output["records"]),
                "unique_identity_count": len(output["records"]),
                "verdict_counts": {
                    "APPROVED": counts[A],
                    "REJECTED_CANDIDATE": counts[R],
                    "RUBRIC_ERROR": 0,
                    "INPUT_PACKAGE_ERROR": 0,
                },
            }
        )
        self._assert_isolated_failure(source, mutated, {"FAIL/IDENTITY_COVERAGE"})

    def test_gate_rejects_previous_verdict_exposure(self):
        source = self._known_good()
        mutated = copy.deepcopy(source)
        mutated[0][2]["previous_reviewer_verdicts_present"] = True
        mutated[0][2]["prior_review_material"] = [
            {"review_identity": "action:prior:actor", "verdict": "APPROVED"}
        ]
        self._assert_isolated_failure(
            source, mutated, {"FAIL/PREVIOUS_VERDICT_EXPOSURE"}
        )

    def test_gate_rejects_unexpected_candidate_semantic_bytes(self):
        source = self._known_good()
        mutated = copy.deepcopy(source)
        package, envelope, output = mutated[0][2], mutated[1][2], mutated[2][2]
        identity = package["expected_identities"][0]
        package.update(
            {
                "contract_hash": "8" * 64,
                "reviewer_input_manifest_hash": "9" * 64,
                "reviewer_input_package_hash": "a" * 64,
            }
        )
        package["identity_inventory"][identity]["semantic_value_hash"] = "b" * 64
        package["identity_inventory"][identity]["semantic_value_text"] = (
            package["identity_inventory"][identity]["semantic_value_text"] + "!"
        )
        envelope["reviewer_input_package_hash"] = "a" * 64
        output.update(
            {
                "contract_hash": "8" * 64,
                "reviewer_input_manifest_hash": "9" * 64,
                "reviewer_input_package_hash": "a" * 64,
            }
        )
        for record in output["records"]:
            record["contract_hash"] = "8" * 64
            record["reviewer_input_manifest_hash"] = "9" * 64
        target = next(r for r in output["records"] if r["review_identity"] == identity)
        target["semantic_value_hash"] = "b" * 64
        self._assert_isolated_failure(
            source, mutated, {"FAIL/PACKAGE_IDENTITY_MISMATCH"}
        )

    def test_gate_rejects_manifest_drift(self):
        source = self._known_good()
        mutated = copy.deepcopy(source)
        package, envelope, output = mutated[0][2], mutated[1][2], mutated[2][2]
        package.update(
            {"reviewer_input_manifest_hash": "8" * 64, "reviewer_input_package_hash": "9" * 64}
        )
        package["manifest_declared_files"] = list(
            reversed(package["manifest_declared_files"])
        )
        envelope["reviewer_input_package_hash"] = "9" * 64
        output.update(
            {"reviewer_input_manifest_hash": "8" * 64, "reviewer_input_package_hash": "9" * 64}
        )
        for record in output["records"]:
            record["reviewer_input_manifest_hash"] = "8" * 64
        self._assert_isolated_failure(
            source, mutated, {"FAIL/PACKAGE_IDENTITY_MISMATCH"}
        )

    def test_gate_rejects_golden_answer_contradiction(self):
        source = self._known_good()
        mutated = copy.deepcopy(source)
        golden = passing_golden_report()
        golden.update(
            {
                "verdict_accuracy": Fraction(14, 15),
                "rationale_code_accuracy": Fraction(14, 15),
            }
        )
        self._assert_isolated_failure(
            source,
            mutated,
            {"FAIL/GOLDEN_VERDICT", "FAIL/GOLDEN_RATIONALE"},
            golden=golden,
        )

    def test_v042_shaped_176_flip_fixture_fails_reliability(self):
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(summary["review_identity_count"], 665)
        self.assertEqual(summary["semantic_change_count"], 4)
        self.assertEqual(summary["unchanged_flip_count"], 176)
        self.assertEqual(
            summary["unchanged_flip_distribution"],
            {"input_invariants": 60, "visible_error": 60, "test_obligations": 56},
        )
        self.assertEqual(
            summary["candidate_b_rejected_distribution"],
            {"input_invariants": 62, "visible_error": 60, "test_obligations": 58},
        )
        encoded = json.dumps(summary, sort_keys=True)
        self.assertIsNone(re.search(r"\bRMA\b", encoded))
        self.assertEqual(summary["historical_reviewer_truth_oracle"], "NONE")

        base = [A] * 333 + [R] * 332
        run_set = make_run_set(base)
        for record in run_set[2][2]["records"][:176]:
            replace_verdict_and_recount(
                run_set[2][2], record["review_identity"], R, "MISSING_OWNED_SEMANTIC"
            )
        classifications = [
            disagreement_classification(
                record["review_identity"], cause_code="NORMATIVE_RESPONSIBILITY"
            )
            for record in run_set[2][2]["records"][:176]
        ]
        report = self._evaluate(run_set, classifications=classifications)
        self.assertFalse(report["passed"])
        self.assertEqual(report["metrics"]["unchanged_disagreement_count"], 176)
        self.assertIn("FAIL/EXACT_AGREEMENT", report["failures"])
        self.assertIn("FAIL/RUBRIC_NORMATIVE_AMBIGUITY", report["failures"])
        self.assertIn("FAIL/RESPONSIBILITY_RULE_INSTABILITY", report["failures"])


if __name__ == "__main__":
    unittest.main()
