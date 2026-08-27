import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.statistics import (
    MetricResult,
    cohen_kappa,
    fleiss_kappa,
    format_metric,
    gwet_ac1,
    is_balanced,
    minority_class_agreement,
    pairwise_cohen_kappas,
    serialize_metric,
)


A = "APPROVED"
R = "REJECTED_CANDIDATE"


class SemanticReviewStatisticsTest(unittest.TestCase):
    def test_balanced_disagreement_vector_exact_readback(self):
        runs = [[A, A, R, R], [A, R, R, R], [A, A, R, R]]
        self.assertTrue(is_balanced(runs))
        self.assertEqual(
            [item.value for item in pairwise_cohen_kappas(runs)],
            [Fraction(1, 2), Fraction(1, 1), Fraction(1, 2)],
        )
        self.assertEqual(fleiss_kappa(runs).value, Fraction(23, 35))
        self.assertEqual(gwet_ac1(runs).value, Fraction(25, 37))
        self.assertEqual(minority_class_agreement(runs).value, Fraction(1, 2))
        self.assertEqual(format_metric(Fraction(23, 35)), "0.657143")
        self.assertEqual(format_metric(Fraction(25, 37)), "0.675676")

    def test_imbalanced_prevalence_vector_exact_readback(self):
        runs = [[A] * 20 + [R], [A] * 20 + [R], [A] * 21]
        self.assertFalse(is_balanced(runs))
        self.assertEqual(
            [item.value for item in pairwise_cohen_kappas(runs)],
            [Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)],
        )
        self.assertEqual(fleiss_kappa(runs).value, Fraction(59, 122))
        self.assertEqual(gwet_ac1(runs).value, Fraction(3599, 3725))
        self.assertEqual(minority_class_agreement(runs).value, Fraction(0, 1))
        self.assertEqual(format_metric(Fraction(59, 122)), "0.483607")
        self.assertEqual(format_metric(Fraction(3599, 3725)), "0.966174")

    def test_nr03_balanced_n200_vector_exact_readback(self):
        base = [A] * 100 + [R] * 100
        mutated = [R, R] + base[2:]
        runs = [base, base, mutated]
        self.assertTrue(is_balanced(runs))
        self.assertEqual(
            [item.value for item in pairwise_cohen_kappas(runs)],
            [Fraction(1, 1), Fraction(49, 50), Fraction(49, 50)],
        )
        self.assertEqual(fleiss_kappa(runs).value, Fraction(22199, 22499))
        self.assertEqual(gwet_ac1(runs).value, Fraction(22201, 22501))
        self.assertEqual(minority_class_agreement(runs).value, Fraction(49, 50))

    def test_all_one_class_has_frozen_null_semantics(self):
        runs = [[A] * 4, [A] * 4, [A] * 4]
        self.assertFalse(is_balanced(runs))
        pairs = pairwise_cohen_kappas(runs)
        self.assertEqual([item.value for item in pairs], [None, None, None])
        self.assertEqual(
            {item.null_reason for item in pairs},
            {"ALL_ONE_CLASS_CHANCE_DENOMINATOR"},
        )
        self.assertEqual(
            fleiss_kappa(runs),
            MetricResult(None, "ALL_ONE_CLASS_CHANCE_DENOMINATOR"),
        )
        self.assertEqual(gwet_ac1(runs).value, Fraction(1, 1))
        self.assertEqual(
            minority_class_agreement(runs),
            MetricResult(None, "MINORITY_CLASS_UNOBSERVED"),
        )

    def test_perfect_balanced_vector_exposes_minority_tie_diagnostic(self):
        runs = [[A, A, R, R]] * 3
        self.assertTrue(is_balanced(runs))
        self.assertEqual(
            [item.value for item in pairwise_cohen_kappas(runs)],
            [Fraction(1, 1)] * 3,
        )
        self.assertEqual(fleiss_kappa(runs).value, Fraction(1, 1))
        self.assertEqual(gwet_ac1(runs).value, Fraction(1, 1))
        self.assertEqual(
            minority_class_agreement(runs),
            MetricResult(None, "NO_UNIQUE_MINORITY"),
        )

    def test_identity_records_align_by_sorted_identity_not_source_order(self):
        left = [
            {"review_identity": "action:B:actor", "verdict": R},
            {"review_identity": "action:A:actor", "verdict": A},
        ]
        right = list(reversed(left))
        self.assertEqual(cohen_kappa(left, right).value, Fraction(1, 1))
        mismatched = [
            {"review_identity": "action:C:actor", "verdict": R},
            {"review_identity": "action:A:actor", "verdict": A},
        ]
        self.assertEqual(
            cohen_kappa(left, mismatched),
            MetricResult(None, "IDENTITY_SET_MISMATCH"),
        )

    def test_set_level_invalid_populations_have_stable_null_reasons(self):
        self.assertEqual(
            fleiss_kappa([[A], [A]]),
            MetricResult(None, "INSUFFICIENT_INDEPENDENT_RUNS"),
        )
        self.assertEqual(
            gwet_ac1([[], [], []]),
            MetricResult(None, "ZERO_ALIGNED_IDENTITIES"),
        )
        self.assertEqual(
            minority_class_agreement([[A], [A], ["RUBRIC_ERROR"]]),
            MetricResult(None, "UNEXPECTED_ERROR_VERDICT"),
        )

    def test_balance_boundary_is_exactly_one_twentieth(self):
        equality = [[R] + [A] * 19] * 3
        below = [[R] + [A] * 20] * 3
        self.assertTrue(is_balanced(equality))
        self.assertFalse(is_balanced(below))

    def test_half_even_display_and_serialization_are_exact(self):
        self.assertEqual(format_metric(Fraction(1, 2), 0), "0")
        self.assertEqual(format_metric(Fraction(3, 2), 0), "2")
        self.assertEqual(format_metric(Fraction(-3, 2), 0), "-2")
        self.assertEqual(
            serialize_metric(MetricResult(Fraction(23, 35))),
            {
                "value": {"numerator": 23, "denominator": 35},
                "display": "0.657143",
                "null_reason": None,
            },
        )
        self.assertEqual(
            serialize_metric(MetricResult(None, "NO_UNIQUE_MINORITY")),
            {"value": None, "display": None, "null_reason": "NO_UNIQUE_MINORITY"},
        )

    def test_negative_coefficients_are_preserved_without_clamping(self):
        result = cohen_kappa([A, R], [R, A])
        self.assertEqual(result.value, Fraction(-1, 1))
        self.assertEqual(format_metric(result.value), "-1.000000")


if __name__ == "__main__":
    unittest.main()
