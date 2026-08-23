import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.runner import SEQUENCE_CLASSES, evaluate_sequence, validate_sequence
from downstream.invariants import evaluate_domain_invariants
from downstream.verifier import (
    COMPONENTS,
    VerificationError,
    classify_result,
    verify_execution,
    verify_lifecycle_transition,
)


def snapshot(domain=None, revision=1, history=None, business=None, delivery=None):
    return {
        "authoritative_state": {} if domain is None else domain,
        "revision": revision,
        "history": [] if history is None else history,
        "business_side_effects": [] if business is None else business,
        "delivery_effects": [] if delivery is None else delivery,
    }


def evidence(before, after, status="rejected", code="VALIDATION_FAILED", command=None, replay=False):
    return {
        "sequence_id": "SEQ-1",
        "test_id": "step-1",
        "command": command or {"type": "MUTATE", "input": {}},
        "before": before,
        "result": {"status": status, "code": code, "replay": replay},
        "after": after,
        "deltas": {"history": [], "business_side_effects": [], "delivery_effects": []},
    }


def review(value):
    return {
        "value": value,
        "source_refs": [0],
        "derivation": {
            "kind": "REVIEW_REQUIRED",
            "explanation": "Compiler-reviewed fixture semantics.",
        },
    }


def no_op_expectation():
    return {
        "authoritative_state": "UNCHANGED",
        "revision": "UNCHANGED",
        "history": "UNCHANGED",
        "business_side_effects": "UNCHANGED",
        "delivery_effects": "UNCHANGED",
    }


def compiled_action(default_result, expectations, invariants=None):
    return {
        "default_result": review(default_result),
        "input_invariants": review([] if invariants is None else invariants),
        "result_expectations": review(expectations),
    }


class DeepVerifierTest(unittest.TestCase):
    def test_verifier_consumes_compiled_semantic_envelopes(self):
        action = {
            "default_result": review("REJECTED"),
            "input_invariants": review([]),
            "result_expectations": review(
                {
                    "REJECTED": {
                        "authoritative_state": "UNCHANGED",
                        "revision": "UNCHANGED",
                        "history": "UNCHANGED",
                        "business_side_effects": "UNCHANGED",
                        "delivery_effects": "UNCHANGED",
                    }
                }
            ),
        }
        unchanged = snapshot({"value": 1})
        report = verify_execution(action, evidence(unchanged, unchanged))
        self.assertTrue(report["conformant"])

    def test_verifier_rejects_missing_explicit_component_expectation(self):
        action = {
            "default_result": review("REJECTED"),
            "input_invariants": review([]),
            "result_expectations": review(
                {
                    "REJECTED": {
                        "authoritative_state": "UNCHANGED",
                        "revision": "UNCHANGED",
                        "history": "UNCHANGED",
                        "business_side_effects": "UNCHANGED",
                    }
                }
            ),
        }
        unchanged = snapshot({"value": 1})
        with self.assertRaisesRegex(VerificationError, "missing component: delivery_effects"):
            verify_execution(action, evidence(unchanged, unchanged))

    def test_sequence_override_must_be_declared_by_compiled_contract(self):
        action = {
            "default_result": review("SUCCESS"),
            "input_invariants": review([]),
            "result_expectations": review(
                {
                    "SUCCESS": {
                        "authoritative_state": "CHANGED",
                        "revision": "CHANGED",
                        "history": "CHANGED",
                        "business_side_effects": "UNCHANGED",
                        "delivery_effects": "UNCHANGED",
                    }
                }
            ),
        }
        unchanged = snapshot({"value": 1})
        with self.assertRaisesRegex(VerificationError, "result expectation is not declared: STALE"):
            verify_execution(action, evidence(unchanged, unchanged, code="STALE_VERSION"), expected_result="STALE")

    def test_required_sequence_classes_are_executable_catalog_values(self):
        expected = {
            "valid_happy_transition",
            "wrong_role",
            "wrong_object_revision",
            "authority_lost_after_initial_access",
            "stale_expected_version",
            "validation_rejection",
            "repeated_same_idempotency_key",
            "same_key_replay_after_later_state_changes",
            "reversal_before_boundary",
            "reversal_at_boundary",
            "reversal_after_boundary",
            "superseded_transition_sentinel",
            "delivery_failure_after_successful_business_commit",
            "manual_delivery_retry",
            "stop_after_terminal_state",
            "destructive_action_without_confirmation_reason",
            "rejected_command_followed_by_related_second_command",
            "historical_projection_after_later_state_change",
        }
        self.assertEqual(expected, SEQUENCE_CLASSES)
        validate_sequence({"sequence_id": "SEQ", "sequence_class": "stale_expected_version", "steps": []})
        with self.assertRaises(ValueError):
            validate_sequence({"sequence_id": "SEQ", "sequence_class": "render_only", "steps": []})

    def test_generic_domain_invariant_hooks_cover_authority_single_active_snapshot_event_and_terminal_stop(self):
        before = {
            "claim": {"ownerId": "finance-1", "status": "Payment completed", "snapshot": {"amount": 100}},
            "adjustments": [{"status": "Failed"}],
            "history": [],
            "deliveries": [{"attempts": 1}],
        }
        after = {
            "claim": {"ownerId": "finance-1", "status": "Payment completed", "snapshot": {"amount": 100}},
            "adjustments": [{"status": "Failed"}, {"status": "In progress"}],
            "history": [{"actor": "finance-1", "at": "2026-08-23T00:00:00Z", "target": "claim-1"}],
            "deliveries": [{"attempts": 1}],
        }
        invariants = [
            {"type": "exact_object_ownership", "owner_pointer": "/claim/ownerId", "actor_pointer": "/actorId"},
            {"type": "current_relationship_authority", "authority_pointer": "/claim/ownerId", "actor_pointer": "/actorId"},
            {"type": "single_active_object", "collection_pointer": "/adjustments", "status_field": "status", "active_values": ["In progress"], "maximum": 1},
            {"type": "immutable_snapshot", "pointer": "/claim/snapshot"},
            {"type": "event_time_provenance", "collection_pointer": "/history", "required_fields": ["actor", "at", "target"]},
            {"type": "terminal_state_worker_stop", "state_pointer": "/claim/status", "terminal_values": ["Payment completed"], "effect_pointer": "/deliveries"},
        ]
        results = evaluate_domain_invariants(
            invariants,
            {"before": before, "after": after, "command": {"actorId": "finance-1"}},
        )
        self.assertTrue(all(item["passed"] for item in results))
    def test_rejected_no_op_reports_five_independent_components(self):
        before = snapshot({"value": 1})
        action = compiled_action("REJECTED", {"REJECTED": no_op_expectation()})
        report = verify_execution(action, evidence(before, snapshot({"value": 1})), expected_result="REJECTED")
        self.assertTrue(report["conformant"])
        self.assertEqual(set(COMPONENTS), set(report["components"]))
        self.assertTrue(all(item["passed"] for item in report["components"].values()))

    def test_rejected_partial_mutation_is_visible_even_when_version_and_history_are_unchanged(self):
        before = snapshot({"adjustment": {"status": "Failed"}})
        after = snapshot({"adjustment": {"status": "Failed", "verification": {"result": "Executed"}}})
        action = compiled_action("REJECTED", {"REJECTED": no_op_expectation()})
        report = verify_execution(action, evidence(before, after), expected_result="REJECTED")
        self.assertFalse(report["conformant"])
        self.assertFalse(report["components"]["authoritative_state"]["passed"])
        self.assertTrue(report["components"]["revision"]["passed"])
        self.assertTrue(report["components"]["history"]["passed"])

    def test_declared_success_can_separate_business_commit_from_delivery_failure(self):
        action = compiled_action(
            "SUCCESS",
            {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "CHANGED",
                }
            },
        )
        before = snapshot({"status": "Submitted"})
        after = snapshot(
            {"status": "Approved"},
            revision=2,
            history=[{"action": "approve"}],
            delivery=[{"status": "Permanent failure"}],
        )
        report = verify_execution(action, evidence(before, after, status="committed", code="APPROVED"), expected_result="SUCCESS")
        self.assertTrue(report["conformant"])
        self.assertTrue(report["components"]["delivery_effects"]["changed"])
        self.assertFalse(report["components"]["business_side_effects"]["changed"])

    def test_result_classification_handles_stale_and_replay_in_core(self):
        self.assertEqual("STALE", classify_result({"status": "rejected", "code": "STALE_VERSION"}))
        self.assertEqual("IDEMPOTENT_REPLAY", classify_result({"status": "committed", "code": "OK", "replay": True}))

    def test_input_invariant_derives_rejection_for_real_non_finite_values(self):
        action = compiled_action(
            "SUCCESS",
            {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "ANY",
                    "business_side_effects": "ANY",
                    "delivery_effects": "ANY",
                },
                "REJECTED": no_op_expectation(),
            },
            invariants=[{"type": "finite_number", "pointer": "/amountKrw"}],
        )
        before = snapshot({"draft": {"amountKrw": 100}})
        for number in (math.nan, math.inf, -math.inf):
            record = evidence(
                before,
                snapshot({"draft": {"amountKrw": number}}, revision=2),
                status="committed",
                code="UPDATED",
                command={"type": "UPDATE_DRAFT", "input": {"amountKrw": number}},
            )
            report = verify_execution(action, record)
            self.assertEqual("REJECTED", report["expected_result"])
            self.assertFalse(report["result_matches"])
            self.assertFalse(report["conformant"])

    def test_sequence_aggregates_authority_loss_stale_replay_and_delivery(self):
        no_change = snapshot({"status": "OPEN"})
        records = [
            evidence(no_change, no_change, code="AUTHORITY_LOST"),
            evidence(no_change, no_change, code="STALE_VERSION"),
            evidence(no_change, no_change, status="committed", code="ORIGINAL", replay=True),
            evidence(
                no_change,
                snapshot({"status": "DONE"}, revision=2, delivery=[{"status": "Permanent failure"}]),
                status="committed",
                code="DONE",
            ),
        ]
        sequence = {
            "sequence_id": "SEQ-MIXED",
            "steps": [
                {"action_id": "mutate", "expected_result": "REJECTED"},
                {"action_id": "mutate", "expected_result": "STALE"},
                {"action_id": "mutate", "expected_result": "IDEMPOTENT_REPLAY"},
                {"action_id": "deliver", "expected_result": "SUCCESS"},
            ],
        }
        bundle = {
            "actions": [
                {
                    "action_id": "mutate",
                    **compiled_action(
                        "REJECTED",
                        {
                            "REJECTED": no_op_expectation(),
                            "STALE": no_op_expectation(),
                            "IDEMPOTENT_REPLAY": no_op_expectation(),
                        },
                    ),
                },
                {
                    "action_id": "deliver",
                    **compiled_action(
                        "SUCCESS",
                        {
                        "SUCCESS": {
                            "authoritative_state": "CHANGED",
                            "revision": "CHANGED",
                            "history": "UNCHANGED",
                            "business_side_effects": "UNCHANGED",
                            "delivery_effects": "CHANGED",
                        }
                        },
                    ),
                },
            ]
        }
        report = evaluate_sequence(bundle, sequence, records)
        self.assertTrue(report["conformant"])
        self.assertEqual(4, len(report["steps"]))

    def test_result_assertions_detect_missing_latest_value_and_false_history_projection(self):
        action = compiled_action(
            "STALE",
            {
                "STALE": {
                    **no_op_expectation(),
                    "assertions": [
                        {"type": "path_present", "pointer": "/result/latestValues/user.active"}
                    ]
                },
                "SUCCESS": {
                    "authoritative_state": "UNCHANGED",
                    "revision": "UNCHANGED",
                    "history": "UNCHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                    "assertions": [
                        {
                            "type": "collection_item_field_equals",
                            "pointer": "/result/query",
                            "match_field": "action",
                            "match_value": "APPROVE_CLAIM",
                            "field": "businessStatus",
                            "value": "Payment pending",
                        }
                    ],
                },
            },
        )
        unchanged = snapshot({"status": "Submitted"})
        stale_record = evidence(unchanged, unchanged, code="STALE_VERSION")
        stale_record["result"]["latestValues"] = {}
        stale_report = verify_execution(action, stale_record, expected_result="STALE")
        self.assertFalse(stale_report["conformant"])
        self.assertFalse(stale_report["assertions"][0]["passed"])

        query_record = evidence(unchanged, unchanged, status="committed", code="QUERY")
        query_record["result"]["query"] = [
            {"action": "APPROVE_CLAIM", "businessStatus": "Submitted"},
            {"action": "REVOKE_APPROVAL", "businessStatus": "Submitted"},
        ]
        query_report = verify_execution(action, query_record, expected_result="SUCCESS")
        self.assertFalse(query_report["conformant"])
        self.assertFalse(query_report["assertions"][0]["passed"])

    def test_superseded_transition_sentinel_fails_an_observed_active_transition(self):
        lifecycle = {
            "lifecycle_id": "approval",
            "superseded_sentinels": [
                {"object_id": "DEC-OLD", "source_status": "SUPERSEDED", "active": False}
            ],
        }
        report = verify_lifecycle_transition(
            lifecycle,
            {"transition": "APPROVED -> IN_REVIEW", "source_ids": ["DEC-OLD"]},
        )
        self.assertFalse(report["conformant"])
        self.assertEqual(["DEC-OLD"], report["matched_superseded_sources"])


if __name__ == "__main__":
    unittest.main()
