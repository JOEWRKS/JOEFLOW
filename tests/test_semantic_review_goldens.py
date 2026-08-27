import copy
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.goldens import GoldenError, evaluate_goldens
from downstream.semantic_review.hashing import canonical_json_bytes, sha256_bytes
from downstream.semantic_review.responsibility import load_responsibility_profile


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "semantic-review-v1"
GOLDEN_CASES = FIXTURE_ROOT / "golden-cases.json"
GOLDEN_ANSWERS = FIXTURE_ROOT / "golden-answers.json"
BRIEF = (
    SKILL_ROOT
    / "downstream"
    / "semantic_review"
    / "artifacts"
    / "reviewer-brief-v1.md"
)


class SemanticReviewGoldenTest(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(GOLDEN_CASES.read_text(encoding="utf-8"))
        self.answers = json.loads(GOLDEN_ANSWERS.read_text(encoding="utf-8"))

    def _correct_outputs(self):
        return [
            {
                "case_id": item["case_id"],
                "verdict": item["verdict"],
                "rationale_code": item["rationale_code"],
            }
            for item in self.answers["answers"]
        ]

    def test_golden_suite_has_exactly_fifteen_unique_hash_bound_cases(self):
        self.assertEqual(len(self.cases), 15)
        self.assertEqual(
            {case["case_id"] for case in self.cases},
            {f"G-{index:03d}" for index in range(1, 16)},
        )
        hashes = set()
        for case in self.cases:
            frozen_hash = case["case_manifest_hash"]
            unhashed = {key: value for key, value in case.items() if key != "case_manifest_hash"}
            self.assertEqual(frozen_hash, sha256_bytes(canonical_json_bytes(unhashed)))
            hashes.add(frozen_hash)
            self.assertNotIn("verdict", case)
            self.assertNotIn("rationale_code", case)
        self.assertEqual(len(hashes), 15)

    def test_answer_bank_is_separate_and_uses_exact_frozen_pairs(self):
        answers = {item["case_id"]: item for item in self.answers["answers"]}
        self.assertEqual(len(answers), 15)
        self.assertEqual(
            (answers["G-012"]["verdict"], answers["G-012"]["rationale_code"]),
            ("INPUT_PACKAGE_ERROR", "ACTIVE_SUPERSEDED_SOURCE"),
        )
        self.assertEqual(
            (answers["G-015"]["verdict"], answers["G-015"]["rationale_code"]),
            ("RUBRIC_ERROR", "RESPONSIBILITY_UNDEFINED"),
        )
        self.assertEqual(
            self.answers["adjudication_status"], "PM_SPEC_ORACLE_NOT_HUMAN_ADJUDICATED"
        )

    def test_golden_accuracy_requires_verdict_and_rationale_code(self):
        outputs = self._correct_outputs()
        outputs[0]["rationale_code"] = "UNSUPPORTED_OVERREACH"
        report = evaluate_goldens(outputs, self.answers)
        self.assertEqual(report["verdict_accuracy"], Fraction(1, 1))
        self.assertLess(report["rationale_code_accuracy"], Fraction(1, 1))

    def test_golden_evaluator_reports_expected_errors_as_expected(self):
        report = evaluate_goldens(self._correct_outputs(), self.answers)
        self.assertEqual(report["verdict_accuracy"], Fraction(1, 1))
        self.assertEqual(report["rationale_code_accuracy"], Fraction(1, 1))
        self.assertEqual(report["unexpected_rubric_error_count"], 0)
        self.assertEqual(report["unexpected_input_package_error_count"], 0)

    def test_golden_evaluator_rejects_missing_or_duplicate_identity(self):
        outputs = self._correct_outputs()
        with self.assertRaisesRegex(GoldenError, "GOLDEN_IDENTITY_SET_MISMATCH"):
            evaluate_goldens(outputs[:-1], self.answers)
        outputs[-1]["case_id"] = outputs[0]["case_id"]
        with self.assertRaisesRegex(GoldenError, "GOLDEN_IDENTITY_SET_MISMATCH"):
            evaluate_goldens(outputs, self.answers)

    def test_canonical_brief_is_lf_utf8_and_contains_all_frozen_rules(self):
        data = BRIEF.read_bytes()
        self.assertFalse(data.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r", data)
        text = data.decode("utf-8")
        self.assertIn("joewrks.semantic-review-brief/1.0", text)
        for number in range(1, 27):
            self.assertEqual(text.count(f"`FR-A{number:02d}`"), 1)
        for number in range(1, 13):
            self.assertEqual(text.count(f"`FR-L{number:02d}`"), 1)
        self.assertNotIn("FR-L13", text)
        self.assertIn("`PR-P01`", text)

    def test_brief_table_matches_profile_rule_field_mode_and_ownership_labels(self):
        profile_path = BRIEF.parent / "responsibility-profile-v1.json"
        profile = load_responsibility_profile(profile_path)
        rows = {}
        for line in BRIEF.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| `FR-"):
                continue
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            rule_id, field, mode, owns_label = cells
            rows[rule_id] = (field, mode, owns_label)
        expected = {}
        for kind in ("action", "lifecycle"):
            for field, rule in profile[kind].items():
                expected[rule["responsibility_rule_id"]] = (
                    field,
                    rule["completeness_mode"],
                    rule["brief_owns_label"],
                )
        self.assertEqual(rows, expected)


if __name__ == "__main__":
    unittest.main()
