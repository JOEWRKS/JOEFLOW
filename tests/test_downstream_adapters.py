import json
import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.adapter_runtime import AdapterError, build_request, run_file_jsonl_adapter
from downstream.run_frozen_regressions import execute_frozen_regressions


class AdapterRuntimeTest(unittest.TestCase):
    def request(self):
        return build_request(
            sequence_id="SEQ-1",
            test_id="STEP-1",
            product_slug="sample",
            authority={"approved_revision": 1, "approved_digest": "digest"},
            contract_hash="a" * 64,
            adapter={"name": "fake", "version": "1.0.0"},
            frozen_source={"commit": "b" * 40, "tree": "c" * 40},
            command={"type": "NOOP", "input": {}},
        )

    def test_file_adapter_accepts_complete_matching_execution_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "adapter.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import json, os
                    requests = [json.loads(line) for line in open(os.environ['JOEWRKS_REQUEST_JSONL'], encoding='utf-8') if line.strip()]
                    snapshot = {'authoritative_state': {}, 'revision': 1, 'history': [], 'business_side_effects': [], 'delivery_effects': []}
                    with open(os.environ['JOEWRKS_RESPONSE_JSONL'], 'w', encoding='utf-8', newline='\\n') as output:
                        for request in requests:
                            evidence = {**request, 'record_kind': 'execution_evidence', 'before': snapshot, 'result': {'status': 'rejected', 'code': 'NOOP'}, 'after': snapshot, 'deltas': {'history': [], 'business_side_effects': [], 'delivery_effects': []}}
                            output.write(json.dumps(evidence, separators=(',', ':')) + '\\n')
                    """
                ),
                encoding="utf-8",
            )
            records = run_file_jsonl_adapter([sys.executable, str(script)], [self.request()])
        self.assertEqual(1, len(records))
        self.assertEqual("STEP-1", records[0]["test_id"])
        self.assertNotIn("conformant", records[0]["result"])

    def test_adapter_identity_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "adapter.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import json, os
                    request = json.loads(open(os.environ['JOEWRKS_REQUEST_JSONL'], encoding='utf-8').readline())
                    request['contract_hash'] = '0' * 64
                    snapshot = {'authoritative_state': {}, 'revision': 1, 'history': [], 'business_side_effects': [], 'delivery_effects': []}
                    evidence = {**request, 'record_kind': 'execution_evidence', 'before': snapshot, 'result': {'status': 'rejected', 'code': 'NOOP'}, 'after': snapshot, 'deltas': {'history': [], 'business_side_effects': [], 'delivery_effects': []}}
                    open(os.environ['JOEWRKS_RESPONSE_JSONL'], 'w', encoding='utf-8').write(json.dumps(evidence) + '\\n')
                    """
                ),
                encoding="utf-8",
            )
            with self.assertRaises(AdapterError):
                run_file_jsonl_adapter([sys.executable, str(script)], [self.request()])


@unittest.skipUnless(
    os.environ.get("JOEWRKS_FROZEN_A_ROOT") and os.environ.get("JOEWRKS_FROZEN_B_WORKTREE"),
    "set JOEWRKS_FROZEN_A_ROOT and JOEWRKS_FROZEN_B_WORKTREE for pinned runtime regression",
)
class FrozenRuntimeRegressionTest(unittest.TestCase):
    def test_pinned_a_and_b_defects_are_executed_and_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            report = execute_frozen_regressions(
                a_root=Path(os.environ["JOEWRKS_FROZEN_A_ROOT"]),
                b_worktree=Path(os.environ["JOEWRKS_FROZEN_B_WORKTREE"]),
                output_dir=Path(directory),
            )
            self.assertEqual("0.4.1.1", report["harness_version"])
            self.assertEqual(
                {
                    "replication_a": "joewrks.downstream.regression-slice/1.0",
                    "replication_b": "joewrks.downstream.regression-slice/1.0",
                    "client_feedback_rev44": "joewrks.action-conformance/1.0",
                },
                report["contract_versions"],
            )
            self.assertEqual(
                {
                    "replication_a": False,
                    "replication_b": False,
                    "client_feedback_rev44": True,
                },
                report["production_handoff_eligible"],
            )
            self.assertEqual(0, report["authority_assessments"]["replication_a"]["machine_derived_field_count"])
            self.assertEqual(4, report["authority_assessments"]["replication_a"]["review_required_field_count"])
            self.assertEqual(0, report["authority_assessments"]["replication_b"]["machine_derived_field_count"])
            self.assertEqual(64, report["authority_assessments"]["replication_b"]["review_required_field_count"])
            self.assertEqual(1, report["authority_assessments"]["client_feedback_rev44"]["machine_derived_field_count"])
            self.assertEqual(37, report["authority_assessments"]["client_feedback_rev44"]["review_required_field_count"])
            expected = {
                "A_UI_DOMAIN_DISCONNECT",
                "B030_REJECTED_PARTIAL_MUTATION",
                "B031_NAN_SUBMISSION",
                "B031_POSITIVE_INFINITY_SUBMISSION",
                "B_STALE_LATEST_VALUE",
                "B_HISTORICAL_STATUS_PROJECTION",
                "B_TERMINAL_RETRY_STOP",
            }
            self.assertTrue(expected <= set(report["regressions"]))
            self.assertTrue(all(report["regressions"][key]["detected"] for key in expected))
            classes = {
                item["classification"]
                for item in report["regressions"]["B031_NAN_SUBMISSION"]["runtime_non_finite_inputs"]
            }
            self.assertIn("NaN", classes)
            classes = {
                item["classification"]
                for item in report["regressions"]["B031_POSITIVE_INFINITY_SUBMISSION"]["runtime_non_finite_inputs"]
            }
            self.assertIn("+Infinity", classes)
            for coverage in (
                "authority_loss",
                "stale_no_op",
                "idempotent_replay",
                "delivery_business_separation",
                "manual_delivery_retry",
            ):
                with self.subTest(coverage=coverage):
                    self.assertTrue(report["coverage"][coverage]["conformant"])
            self.assertFalse(report["coverage"]["superseded_transition_sentinel"]["conformant"])
            self.assertEqual(
                ["DEC-011"],
                report["coverage"]["superseded_transition_sentinel"]["matched_superseded_sources"],
            )
            self.assertTrue((Path(directory) / "frozen-a-evidence.jsonl").is_file())
            self.assertTrue((Path(directory) / "frozen-b-evidence.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
