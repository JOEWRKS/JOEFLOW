import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.gate import evaluate_reliability_gate
from tests.semantic_review_support import (
    disagreement_classification,
    make_run_set,
    passing_golden_report,
    replace_verdict_and_recount,
)


A = "APPROVED"
R = "REJECTED_CANDIDATE"


class SemanticReviewGateTest(unittest.TestCase):
    def _evaluate(self, run_set, classifications=None, golden_report=None):
        packages, envelopes, outputs = run_set
        return evaluate_reliability_gate(
            packages,
            envelopes,
            outputs,
            passing_golden_report() if golden_report is None else golden_report,
            [] if classifications is None else classifications,
        )

    def test_balanced_known_good_run_set_passes_every_gate(self):
        report = self._evaluate(make_run_set([A] * 10 + [R] * 10))
        self.assertTrue(report["passed"])
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["metrics"]["population"], "BALANCED")
        self.assertEqual(
            report["metrics"]["three_review_unanimity"]["value"],
            {"numerator": 1, "denominator": 1},
        )

    def test_imbalanced_known_good_run_set_passes_ac1_and_minority(self):
        report = self._evaluate(make_run_set([A] * 20 + [R]))
        self.assertTrue(report["passed"])
        self.assertEqual(report["metrics"]["population"], "IMBALANCED")
        self.assertEqual(
            report["metrics"]["gwet_ac1"]["value"],
            {"numerator": 1, "denominator": 1},
        )
        self.assertEqual(
            report["metrics"]["minority_class_agreement"]["value"],
            {"numerator": 1, "denominator": 1},
        )

    def test_all_one_class_cannot_pass_on_ac1_alone(self):
        report = self._evaluate(make_run_set([A] * 20))
        self.assertFalse(report["passed"])
        self.assertIn("FAIL/MINORITY_CLASS_RELIABILITY", report["failures"])
        self.assertNotIn("FAIL/IMBALANCED_RELIABILITY", report["failures"])

    def test_majority_agreement_cannot_override_same_rule_disagreement(self):
        run_set = make_run_set([A] * 100 + [R] * 100)
        targets = [record["review_identity"] for record in run_set[2][2]["records"][:2]]
        for identity in targets:
            replace_verdict_and_recount(
                run_set[2][2],
                identity,
                R,
                "MISSING_OWNED_SEMANTIC",
            )
        classifications = [disagreement_classification(identity) for identity in targets]
        report = self._evaluate(run_set, classifications)
        self.assertFalse(report["passed"])
        self.assertIn("FAIL/RESPONSIBILITY_RULE_INSTABILITY", report["failures"])
        self.assertNotIn("FAIL/RUBRIC_NORMATIVE_AMBIGUITY", report["failures"])
        self.assertNotIn("FAIL/EXACT_AGREEMENT", report["failures"])
        self.assertNotIn("FAIL/BALANCED_RELIABILITY", report["failures"])

    def test_normative_classification_fails_without_rewriting_metrics(self):
        run_set = make_run_set([A] * 100 + [R] * 100)
        identity = run_set[2][2]["records"][0]["review_identity"]
        replace_verdict_and_recount(
            run_set[2][2], identity, R, "MISSING_OWNED_SEMANTIC"
        )
        classification = disagreement_classification(
            identity, cause_code="NORMATIVE_COMPLETENESS"
        )
        report = self._evaluate(run_set, [classification])
        self.assertIn("FAIL/RUBRIC_NORMATIVE_AMBIGUITY", report["failures"])
        self.assertEqual(
            report["metrics"]["three_review_unanimity"]["value"],
            {"numerator": 199, "denominator": 200},
        )

    def test_insufficient_runs_and_golden_misses_fail_conjunctively(self):
        run_set = make_run_set([A, R], run_count=2)
        golden = passing_golden_report()
        golden["verdict_accuracy"] = Fraction(14, 15)
        report = self._evaluate(run_set, golden_report=golden)
        self.assertFalse(report["passed"])
        self.assertIn("FAIL/INSUFFICIENT_INDEPENDENT_RUNS", report["failures"])

    def test_extra_disagreement_classification_is_not_silently_accepted(self):
        run_set = make_run_set([A] * 10 + [R] * 10)
        identity = run_set[2][0]["records"][0]["review_identity"]
        report = self._evaluate(run_set, [disagreement_classification(identity)])
        self.assertFalse(report["passed"])
        self.assertIn("FAIL/RUBRIC_NORMATIVE_AMBIGUITY", report["failures"])

    def test_zero_identity_population_fails_structurally_before_metrics(self):
        report = self._evaluate(make_run_set([]))
        self.assertFalse(report["passed"])
        self.assertIn("FAIL/IDENTITY_COVERAGE", report["failures"])
        self.assertIsNone(report["metrics"]["fleiss_kappa"]["value"])
        self.assertEqual(
            report["metrics"]["fleiss_kappa"]["null_reason"],
            "ZERO_ALIGNED_IDENTITIES",
        )

    def test_rationale_only_difference_does_not_reduce_verdict_unanimity(self):
        run_set = make_run_set([R] * 200)
        run_set[2][2]["records"][0]["rationale_code"] = "UNSUPPORTED_OVERREACH"
        report = self._evaluate(run_set)
        self.assertEqual(
            report["metrics"]["three_review_unanimity"]["value"],
            {"numerator": 1, "denominator": 1},
        )

    def test_gate_report_is_json_serializable(self):
        passing = self._evaluate(make_run_set([A] * 10 + [R] * 10))
        failing = self._evaluate(make_run_set([]))
        json.dumps(passing, sort_keys=True)
        json.dumps(failing, sort_keys=True)

    def test_forged_disagreement_rule_hash_is_unresolved(self):
        run_set = make_run_set([A] * 100 + [R] * 100)
        identity = run_set[2][2]["records"][0]["review_identity"]
        replace_verdict_and_recount(
            run_set[2][2], identity, R, "MISSING_OWNED_SEMANTIC"
        )
        classification = disagreement_classification(identity)
        classification["cited_rule_hash"] = "f" * 64
        report = self._evaluate(run_set, [classification])
        self.assertIn("FAIL/RUBRIC_NORMATIVE_AMBIGUITY", report["failures"])


if __name__ == "__main__":
    unittest.main()
