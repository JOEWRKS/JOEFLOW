import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from downstream_v2.semantic_debt import semantic_debt_report  # noqa: E402


def field(kind):
    return {
        "value": kind,
        "source_seed_refs": ["SEED-001"],
        "derivation": {"kind": kind},
    }


def gap(path="actions/submit/authentication"):
    return {
        "code": "SEMANTIC_AUTHORITY_GAP",
        "field_path": path,
        "reason": "The declared derivation is not permitted.",
        "gap_type": "CONTRACT_CONFLICT",
        "required_expectation": "DETERMINISTIC_REQUIRED",
        "required_authority_class": "INTENT",
        "authority_scope_refs": ["REQ-001"],
        "candidate_seed_refs": ["SEED-001"],
        "evidence_refs": [],
    }


class SemanticDebtTests(unittest.TestCase):
    def test_counts_equal_the_exact_sorted_field_inventories(self):
        report = semantic_debt_report(
            derived_fields=[
                ("lifecycles/request/current_states", field("MACHINE_DERIVED")),
                ("actions/submit/visible_success", field("REVIEW_REQUIRED")),
                ("actions/submit/actor", field("DIRECT_AUTHORITY")),
                ("actions/submit/command", field("MACHINE_DERIVED")),
            ],
            gaps=[gap()],
        )
        self.assertEqual(report, {
            "direct_authority_count": 1,
            "machine_derived_count": 2,
            "review_required_count": 1,
            "authority_gap_count": 1,
            "direct_authority_fields": ["actions/submit/actor"],
            "machine_derived_fields": [
                "actions/submit/command", "lifecycles/request/current_states"
            ],
            "review_required_fields": ["actions/submit/visible_success"],
            "authority_gaps": [gap()],
        })
        self.assertEqual(report["direct_authority_count"], len(report["direct_authority_fields"]))
        self.assertEqual(report["machine_derived_count"], len(report["machine_derived_fields"]))
        self.assertEqual(report["review_required_count"], len(report["review_required_fields"]))
        self.assertEqual(report["authority_gap_count"], len(report["authority_gaps"]))

    def test_one_field_cannot_be_counted_twice(self):
        with self.assertRaises(ValueError):
            semantic_debt_report(
                derived_fields=[
                    ("actions/submit/actor", field("DIRECT_AUTHORITY")),
                    ("actions/submit/actor", field("MACHINE_DERIVED")),
                ],
                gaps=[],
            )

    def test_gap_is_not_review_debt(self):
        report = semantic_debt_report(derived_fields=[], gaps=[gap()])
        self.assertEqual(report["review_required_count"], 0)
        self.assertEqual(report["review_required_fields"], [])
        self.assertEqual(report["authority_gap_count"], 1)

    def test_input_order_does_not_change_canonical_report_bytes(self):
        fields = [
            ("actions/submit/command", field("MACHINE_DERIVED")),
            ("actions/submit/actor", field("DIRECT_AUTHORITY")),
            ("actions/submit/visible_success", field("REVIEW_REQUIRED")),
        ]
        gaps = [gap("lifecycles/request/reversibility"), gap()]
        first = semantic_debt_report(derived_fields=fields, gaps=gaps)
        second = semantic_debt_report(
            derived_fields=list(reversed(fields)), gaps=list(reversed(copy.deepcopy(gaps)))
        )
        canonical = lambda value: json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(canonical(first), canonical(second))


if __name__ == "__main__":
    unittest.main()
