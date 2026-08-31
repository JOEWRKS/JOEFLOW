import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream_v21.runtime_evidence import build_runtime_evidence_bundle  # noqa: E402
try:
    from integration_v2.dogfood_v21 import (  # noqa: E402
        implementation_drift_probe,
        materialize_dogfood,
    )
except ImportError:
    from integration_v2.dogfood_v21 import materialize_dogfood  # noqa: E402
    implementation_drift_probe = None
from integration_v2.runtime_v21 import verify_runtime_v21  # noqa: E402

try:  # Keep the RED import state visible as an assertion.
    from integration_v2.runtime_v21 import (  # noqa: E402
        validate_runtime_conformance_report_v21,
    )
except ImportError:
    validate_runtime_conformance_report_v21 = None


class RuntimeV21SemanticVerificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.materialized = materialize_dogfood(ROOT)
        except (KeyError, TypeError, ValueError) as error:
            raise AssertionError(
                f"dogfood does not execute its planned runtime cases: {error}"
            ) from error
        cls.contract = cls.materialized["contract"]
        cls.plan = cls.materialized["plan"]
        cls.records = cls.materialized["records"]
        cls.bundle = cls.materialized["bundle"]
        cls.report = cls.materialized["report"]
        cls.case_index = {
            case["test_id"]: {
                "action_id": action["action_id"],
                "result_class": case["result_expectation"]["result_class"],
            }
            for action in cls.plan["actions"]
            for case in action["cases"]
        }

    def record(self, action_id, result_class):
        return next(
            record
            for record in self.records
            if self.case_index[record["test_id"]]
            == {"action_id": action_id, "result_class": result_class}
        )

    def mutated_report(self, mutate, *, scope="FULL_CONTRACT"):
        records = copy.deepcopy(self.records)
        mutate(records)
        bundle = build_runtime_evidence_bundle(self.contract, self.plan, records)
        return verify_runtime_v21(
            self.contract,
            self.plan,
            bundle,
            verification_scope=scope,
        )

    def assert_nonconformant(self, report, code):
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
        self.assertEqual(report["runtime_status"], "NON_CONFORMANT")
        observed_codes = {
            error["code"]
            for error in report["evidence_errors"] + report["contract_execution_errors"]
        }
        self.assertIn(code, observed_codes)

    def test_real_records_cover_every_planned_case_and_bind_action_and_result(self):
        self.assertEqual(len(self.records), 21)
        self.assertEqual(len({record["test_id"] for record in self.records}), 21)
        self.assertEqual(set(self.case_index), {record["test_id"] for record in self.records})
        for record in self.records:
            expected = self.case_index[record["test_id"]]
            with self.subTest(test_id=record["test_id"]):
                self.assertEqual(record["command"]["action_id"], expected["action_id"])
                self.assertEqual(record["result"]["result_class"], expected["result_class"])
                self.assertNotIn("semantic", record["result"])
                self.assertEqual(
                    record["deltas"]["revision"],
                    record["after"]["revision"] - record["before"]["revision"],
                )
        self.assertFalse(
            any(
                assertion["pointer"].startswith("/result/semantic")
                for action in self.plan["actions"]
                for case in action["cases"]
                for assertion in case["evidence_assertions"]
            )
        )

    def test_full_report_has_exact_inventory_review_and_global_gates(self):
        report = self.report
        self.assertEqual(report["report_schema_version"], "joewrks.runtime-conformance-report/1.0")
        self.assertEqual(report["verification_scope"], "FULL_CONTRACT")
        self.assertEqual(report["contract_dependency_status"], "CONFORMANT")
        self.assertEqual(report["coverage_status"], "COMPLETE")
        self.assertEqual(report["action_coverage_status"], "COMPLETE")
        self.assertEqual(report["lifecycle_coverage_status"], "COMPLETE")
        self.assertEqual(report["lifecycle_applicability"], "NOT_APPLICABLE")
        self.assertEqual(report["review_completion"], "NOT_REQUIRED")
        self.assertEqual(report["semantic_review_reliability"], "NOT_MEASURED")
        self.assertEqual(report["runtime_status"], "CONFORMANT")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_CONFORMANT")
        self.assertEqual(len(report["required_action_test_ids"]), 21)
        self.assertEqual(report["required_action_test_ids"], report["observed_action_test_ids"])
        self.assertEqual(report["missing_action_test_ids"], [])
        self.assertEqual(report["unexpected_action_test_ids"], [])
        self.assertEqual(len(report["action_results"]), 21)
        self.assertEqual(report["lifecycle_results"], [])
        self.assertEqual(report["blocking_reentry_events"], [])
        self.assertEqual(report["contract_execution_errors"], [])
        self.assertEqual(report["evidence_errors"], [])

    def test_report_validates_against_exact_v21_branch_and_recomputes_aggregate(self):
        self.assertIsNotNone(validate_runtime_conformance_report_v21)
        validate_runtime_conformance_report_v21(
            self.report,
            self.contract,
            self.plan,
            self.bundle,
        )
        missing = copy.deepcopy(self.report)
        del missing["report_inputs"]
        with self.assertRaisesRegex(ValueError, "RUNTIME_REPORT_INVALID"):
            validate_runtime_conformance_report_v21(
                missing,
                self.contract,
                self.plan,
                self.bundle,
            )
        forged = copy.deepcopy(self.report)
        forged["implementation_status"] = "IMPLEMENTATION_NOT_CONFORMANT"
        with self.assertRaisesRegex(ValueError, "RUNTIME_REPORT_INVALID"):
            validate_runtime_conformance_report_v21(
                forged,
                self.contract,
                self.plan,
                self.bundle,
            )

    def test_unrelated_command_wrong_actor_and_wrong_input_are_rejected(self):
        def unrelated(records):
            target = next(record for record in records if self.case_index[record["test_id"]]["result_class"] == "SUCCESS")
            target["command"]["action_id"] = "UNRELATED_NOOP"

        self.assert_nonconformant(
            self.mutated_report(unrelated),
            "RUNTIME_ACTION_BINDING_MISMATCH",
        )

        def wrong_actor(records):
            target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "create_pin", "result_class": "SUCCESS"})
            target["command"]["actor"] = "Workspace Owner / Designer"

        self.assert_nonconformant(
            self.mutated_report(wrong_actor),
            "RUNTIME_FIXTURE_EXECUTION_MISMATCH",
        )

        def wrong_input(records):
            target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "create_pin", "result_class": "SUCCESS"})
            target["command"]["x"] = 1.5

        self.assert_nonconformant(
            self.mutated_report(wrong_input),
            "RUNTIME_FIXTURE_EXECUTION_MISMATCH",
        )

    def test_wrong_snapshots_revision_history_business_delivery_and_deltas_are_rejected(self):
        mutations = {
            "authoritative_state": lambda target: target["after"]["authoritative_state"].update({"active_review_link_id": "forged-link"}),
            "revision": lambda target: target["after"].update({"revision": target["after"]["revision"] + 10}),
            "history": lambda target: target["after"]["history"].append({"event": "FORGED"}),
            "business_side_effects": lambda target: target["after"]["business_side_effects"].append({"effect": "FORGED"}),
            "delivery_effects": lambda target: target["after"]["delivery_effects"].append({"effect": "FORGED"}),
            "deltas": lambda target: target["deltas"].update({"revision": 99}),
        }
        for component, change in mutations.items():
            with self.subTest(component=component):
                def mutate(records, change=change):
                    target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "send_review_request", "result_class": "SUCCESS"})
                    change(target)

                self.assert_nonconformant(
                    self.mutated_report(mutate),
                    "RUNTIME_FIXTURE_EXECUTION_MISMATCH",
                )

    def test_duplicate_effect_replay_stale_and_rejection_violations_are_rejected(self):
        def duplicate_delivery(records):
            target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "send_review_request", "result_class": "SUCCESS"})
            duplicate = copy.deepcopy(target["after"]["delivery_effects"][-1])
            target["after"]["delivery_effects"].append(duplicate)
            target["deltas"]["delivery_effects"].append(copy.deepcopy(duplicate))

        def replay_mutates(records):
            target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "send_review_request", "result_class": "IDEMPOTENT_REPLAY"})
            target["after"]["revision"] += 1
            target["deltas"]["revision"] = 1

        def stale_mutates(records):
            target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "resend_review_request", "result_class": "STALE"})
            target["after"]["authoritative_state"]["review_link_revision"] += 1

        def rejection_mutates(records):
            target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "resolve_thread", "result_class": "REJECTED"})
            target["after"]["history"].append({"event": "FORGED_REJECTION_EFFECT"})

        for name, mutate in {
            "duplicate_delivery": duplicate_delivery,
            "replay": replay_mutates,
            "stale": stale_mutates,
            "rejection": rejection_mutates,
        }.items():
            with self.subTest(name=name):
                self.assert_nonconformant(
                    self.mutated_report(mutate),
                    "RUNTIME_FIXTURE_EXECUTION_MISMATCH",
                )

    def test_partial_probe_is_nested_partial_and_never_globally_conformant(self):
        def drift(records):
            target = next(record for record in records if self.case_index[record["test_id"]] == {"action_id": "create_pin", "result_class": "SUCCESS"})
            target["command"]["actor"] = "Workspace Owner / Designer"

        report = self.mutated_report(drift, scope="PARTIAL_PROBE")
        self.assertEqual(report["verification_scope"], "PARTIAL_PROBE")
        self.assertEqual(report["coverage_status"], "COMPLETE")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
        self.assertEqual(report["runtime_status"], "NON_CONFORMANT")

        passing_partial = verify_runtime_v21(
            self.contract,
            self.plan,
            self.bundle,
            verification_scope="PARTIAL_PROBE",
        )
        self.assertEqual(passing_partial["verification_scope"], "PARTIAL_PROBE")
        self.assertEqual(passing_partial["runtime_status"], "CONFORMANT")
        self.assertEqual(passing_partial["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")

    def test_materialized_drift_probe_is_partial_at_outer_and_report_scope(self):
        self.assertIsNotNone(implementation_drift_probe)
        probe = implementation_drift_probe(self.materialized)
        self.assertEqual(probe["probe_status"], "PARTIAL_PROBE")
        self.assertEqual(probe["report"]["verification_scope"], "PARTIAL_PROBE")
        self.assertEqual(probe["report"]["coverage_status"], "COMPLETE")
        self.assertEqual(probe["report"]["runtime_status"], "NON_CONFORMANT")
        self.assertEqual(
            probe["report"]["implementation_status"],
            "IMPLEMENTATION_NOT_CONFORMANT",
        )

    def test_malformed_record_is_contained_in_schema_valid_error_report(self):
        malformed = copy.deepcopy(self.bundle)
        del malformed["records"][0]["after"]["history"]

        report = verify_runtime_v21(self.contract, self.plan, malformed)

        self.assert_nonconformant(report, "RUNTIME_RECORD_VERIFICATION_ERROR")
        self.assertTrue(
            any(
                error["code"] == "RUNTIME_EVIDENCE_BUNDLE_INVALID"
                for error in report["evidence_errors"]
            )
        )

    def test_unexpected_test_id_remains_visible_in_report_inventory(self):
        unexpected = copy.deepcopy(self.bundle)
        unexpected["records"][0]["test_id"] = "TEST-UNEXPECTED-FIXTURE"
        unexpected["records"][0]["command"]["action_id"] = "UNRELATED_NOOP"

        report = verify_runtime_v21(self.contract, self.plan, unexpected)

        self.assertEqual(report["coverage_status"], "INCOMPLETE")
        self.assertIn(
            {
                "action_id": "UNRELATED_NOOP",
                "test_id": "TEST-UNEXPECTED-FIXTURE",
            },
            report["unexpected_action_test_ids"],
        )
        self.assertEqual(
            report["implementation_status"],
            "IMPLEMENTATION_NOT_CONFORMANT",
        )


if __name__ == "__main__":
    unittest.main()
