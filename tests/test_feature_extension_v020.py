"""Feature extension (U2-10): a baseline of preserved behaviour as ordinary 0.2.0 authority."""
import argparse
import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))
sys.path.insert(0, str(ROOT))

from coverage_inheritance import TAG, expand_coverage  # noqa: E402
from new_records import baseline_records  # noqa: E402
from record_builders import evidence  # noqa: E402
from revision_v2 import open_revision  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_semantic_closure_v020 import literal_approved_state  # noqa: E402


def baseline_args(**overrides):
    args = dict(requirement="REQ-002", rule="RULE-002", acceptance="AC-002", surface="SURF-002", goal="GOAL-001",
                evidence=["EVD-050"], behavior=["undo restores the previous position", "new game asks before discarding"],
                check="the existing e2e suite passes unchanged", name="기존 동작 유지", task="TASK-002")
    args.update(overrides)
    return argparse.Namespace(**args)


class BaselineTest(unittest.TestCase):
    def test_baseline_patch_applies_as_a_valid_revision_with_three_hand_written_cells(self):
        state = literal_approved_state()
        built = baseline_records(baseline_args())
        patch = {"evidence": [evidence("EVD-050", source_kind="OBSERVED_RUNTIME", authority_classes=["BEHAVIORAL"],
                                       locator="app v1 (2026-10-31), tests/e2e", claim="Undo and new game behave as the suite asserts")],
                 "objects": {k: v for k, v in built.items() if k not in ("surfaces", "rows")},
                 "surfaces": built["surfaces"], "rows": built["rows"]}
        candidate, report = open_revision(copy.deepcopy(state), patch, status="READY_FOR_REVIEW")
        self.assertEqual(validate_state_v2(candidate), [])
        self.assertEqual(report["rows"], ["coverage[REQ-002]"])
        row = next(r for r in candidate["coverage"] if r["feature_id"] == "REQ-002")
        self.assertEqual(set(row["cells"]), {"goal", "happy_path", "acceptance"})
        expanded = next(r for r in expand_coverage(candidate)["coverage"] if r["feature_id"] == "REQ-002")
        inherited = [axis for axis, cell in expanded["cells"].items() if cell.get(TAG) == "row"]
        self.assertEqual(len(expanded["cells"]), 20)
        self.assertEqual(len(inherited), 17)
        self.assertEqual(expanded["cells"]["boundary"]["authority_bindings"][0]["record_id"], "RULE-002")
        self.assertEqual(candidate["objects"]["tasks"][-1], {"status": "CURRENT", "id": "TASK-002", "implements": ["REQ-002"], "acceptance_refs": ["AC-002"]})

    def test_baseline_needs_a_behaviour(self):
        with self.assertRaises(ValueError):
            baseline_records(baseline_args(behavior=["  "]))


if __name__ == "__main__":
    unittest.main()
