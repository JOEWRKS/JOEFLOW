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

from downstream_v21.runtime_plan import materialize_runtime_plan  # noqa: E402
from integration_v2.dogfood_v21 import runtime_draft  # noqa: E402

try:  # The first TDD run must fail as an assertion, not abort test discovery.
    from integration_v2.client_feedback_portal_fixture import (  # noqa: E402
        ClientFeedbackPortalFixture,
        execute_fixture_scenario,
    )
except (ImportError, ModuleNotFoundError):
    ClientFeedbackPortalFixture = None
    execute_fixture_scenario = None


DOGFOOD = ROOT / "evals" / "core-semantic-closure-v2-m6" / "dogfood"
CONTRACT = json.loads((DOGFOOD / "action-contract-v21.json").read_text(encoding="utf-8"))
DESIGNER = "Workspace Owner / Designer"
REVIEWER = "Client Reviewer"


def review_command(action_id, attempt_id, expected_revision):
    return {
        "action_id": action_id,
        "actor": DESIGNER,
        "project_id": "project-fixture-001",
        "version_id": "version-fixture-001",
        "recipient": "client-reviewer@example.test",
        "client_attempt_id": attempt_id,
        "expected_review_link_revision": expected_revision,
    }


def pin_command(attempt_id="message-pin-001", actor=REVIEWER):
    return {
        "action_id": "create_pin",
        "actor": actor,
        "project_id": "project-fixture-001",
        "version_id": "version-fixture-001",
        "message_attempt_id": attempt_id,
        "media_type": "IMAGE",
        "x": 0.25,
        "y": 0.75,
        "comment": "Move the callout left.",
    }


def reply_command(thread_id, attempt_id="message-reply-001", actor=DESIGNER):
    return {
        "action_id": "reply_thread",
        "actor": actor,
        "project_id": "project-fixture-001",
        "version_id": "version-fixture-001",
        "thread_id": thread_id,
        "message_attempt_id": attempt_id,
        "message": "Updated in the next export.",
    }


def resolve_command(thread_id, attempt_id="message-resolve-001", actor=DESIGNER):
    return {
        "action_id": "resolve_thread",
        "actor": actor,
        "project_id": "project-fixture-001",
        "version_id": "version-fixture-001",
        "thread_id": thread_id,
        "message_attempt_id": attempt_id,
    }


class ClientFeedbackPortalFixtureTest(unittest.TestCase):
    def fixture(self, **options):
        self.assertIsNotNone(
            ClientFeedbackPortalFixture,
            "stateful Client Feedback Portal fixture is missing",
        )
        return ClientFeedbackPortalFixture(CONTRACT, **options)

    def assert_no_effect(self, execution):
        self.assertEqual(execution["before"], execution["after"])
        self.assertEqual(
            execution["deltas"],
            {
                "authoritative_state": {},
                "revision": 0,
                "history": [],
                "business_side_effects": [],
                "delivery_effects": [],
            },
        )

    def test_review_link_attempts_commit_replay_stale_refresh_and_revoke_without_email(self):
        fixture = self.fixture()

        sent = fixture.execute(review_command("send_review_request", "review-send-001", 0))
        self.assertEqual(sent["result"]["result_class"], "SUCCESS")
        self.assertEqual(sent["after"]["revision"], 2)
        self.assertEqual(sent["after"]["authoritative_state"]["version"]["status"], "IN_REVIEW")
        self.assertEqual(sent["after"]["authoritative_state"]["review_link_revision"], 1)
        self.assertEqual(len(sent["deltas"]["history"]), 1)
        self.assertEqual(len(sent["deltas"]["business_side_effects"]), 1)
        self.assertEqual(len(sent["deltas"]["delivery_effects"]), 1)
        first_link = sent["result"]["review_link"]["link_id"]

        replayed = fixture.execute(review_command("send_review_request", "review-send-001", 0))
        self.assertEqual(replayed["result"]["result_class"], "IDEMPOTENT_REPLAY")
        self.assertEqual(replayed["result"]["committed_result"]["review_link"]["link_id"], first_link)
        self.assert_no_effect(replayed)

        stale = fixture.execute(review_command("resend_review_request", "review-resend-stale", 0))
        self.assertEqual(stale["result"]["result_class"], "STALE")
        self.assertEqual(stale["result"]["latest_review_link_revision"], 1)
        self.assertEqual(stale["result"]["latest_review_link"]["link_id"], first_link)
        self.assert_no_effect(stale)

        resent = fixture.execute(review_command("resend_review_request", "review-resend-002", 1))
        self.assertEqual(resent["result"]["result_class"], "SUCCESS")
        self.assertEqual(resent["after"]["authoritative_state"]["review_link_revision"], 2)
        second_link = resent["result"]["review_link"]["link_id"]
        self.assertNotEqual(second_link, first_link)
        links = resent["after"]["authoritative_state"]["review_links"]
        self.assertEqual([link["link_id"] for link in links if link["status"] == "ACTIVE"], [second_link])
        self.assertEqual(len(resent["deltas"]["delivery_effects"]), 1)

        stale_revoke = fixture.execute(review_command("revoke_review_link", "review-revoke-stale", 1))
        self.assertEqual(stale_revoke["result"]["result_class"], "STALE")
        self.assertEqual(stale_revoke["result"]["latest_review_link_revision"], 2)
        self.assert_no_effect(stale_revoke)

        revoked = fixture.execute(review_command("revoke_review_link", "review-revoke-003", 2))
        self.assertEqual(revoked["result"]["result_class"], "SUCCESS")
        self.assertEqual(revoked["after"]["authoritative_state"]["review_link_revision"], 3)
        self.assertIsNone(revoked["after"]["authoritative_state"]["active_review_link_id"])
        self.assertEqual(len(revoked["deltas"]["history"]), 1)
        self.assertEqual(len(revoked["deltas"]["business_side_effects"]), 1)
        self.assertEqual(revoked["deltas"]["delivery_effects"], [])

        revoke_replay = fixture.execute(review_command("revoke_review_link", "review-revoke-003", 2))
        self.assertEqual(revoke_replay["result"]["result_class"], "IDEMPOTENT_REPLAY")
        self.assert_no_effect(revoke_replay)

    def test_review_link_rejects_missing_or_conflicting_attempt_inputs_without_effects(self):
        fixture = self.fixture()
        missing = review_command("send_review_request", "review-missing", 0)
        del missing["expected_review_link_revision"]
        rejected = fixture.execute(missing)
        self.assertEqual(rejected["result"], {"result_class": "REJECTED", "error": {"code": "REVIEW_ATTEMPT_INPUT_REQUIRED"}})
        self.assert_no_effect(rejected)

        fixture.execute(review_command("send_review_request", "review-conflict", 0))
        conflict = review_command("send_review_request", "review-conflict", 0)
        conflict["recipient"] = "different-reviewer@example.test"
        rejected_conflict = fixture.execute(conflict)
        self.assertEqual(rejected_conflict["result"]["result_class"], "REJECTED")
        self.assertEqual(rejected_conflict["result"]["error"]["code"], "ATTEMPT_ID_CONFLICT")
        self.assert_no_effect(rejected_conflict)

    def test_pin_reply_and_resolve_enforce_actor_input_state_and_idempotency(self):
        fixture = self.fixture()

        wrong_actor = fixture.execute(pin_command(actor=DESIGNER))
        self.assertEqual(wrong_actor["result"]["error"]["code"], "ACTOR_NOT_ALLOWED")
        self.assert_no_effect(wrong_actor)

        bad_coordinate = pin_command("message-pin-bad")
        bad_coordinate["x"] = 1.25
        invalid = fixture.execute(bad_coordinate)
        self.assertEqual(invalid["result"]["error"]["code"], "PIN_INPUT_INVALID")
        self.assert_no_effect(invalid)

        created = fixture.execute(pin_command())
        self.assertEqual(created["result"]["result_class"], "SUCCESS")
        thread_id = created["result"]["thread_id"]
        self.assertEqual(created["after"]["authoritative_state"]["threads"][0]["status"], "OPEN")

        pin_replay = fixture.execute(pin_command())
        self.assertEqual(pin_replay["result"]["result_class"], "IDEMPOTENT_REPLAY")
        self.assertEqual(pin_replay["result"]["committed_result"]["thread_id"], thread_id)
        self.assert_no_effect(pin_replay)

        replied = fixture.execute(reply_command(thread_id, actor=DESIGNER))
        self.assertEqual(replied["result"]["result_class"], "SUCCESS")
        self.assertEqual(len(replied["after"]["authoritative_state"]["threads"][0]["replies"]), 1)
        self.assertEqual(replied["deltas"]["delivery_effects"], [])

        reply_replay = fixture.execute(reply_command(thread_id, actor=DESIGNER))
        self.assertEqual(reply_replay["result"]["result_class"], "IDEMPOTENT_REPLAY")
        self.assert_no_effect(reply_replay)

        reviewer_resolve = fixture.execute(resolve_command(thread_id, "message-resolve-wrong", REVIEWER))
        self.assertEqual(reviewer_resolve["result"]["error"]["code"], "ACTOR_NOT_ALLOWED")
        self.assert_no_effect(reviewer_resolve)

        resolved = fixture.execute(resolve_command(thread_id))
        self.assertEqual(resolved["result"]["result_class"], "SUCCESS")
        self.assertEqual(resolved["after"]["authoritative_state"]["threads"][0]["status"], "RESOLVED")
        self.assertEqual(resolved["deltas"]["delivery_effects"], [])

        already_resolved = fixture.execute(resolve_command(thread_id, "message-resolve-again"))
        self.assertEqual(already_resolved["result"]["error"]["code"], "THREAD_NOT_OPEN")
        self.assert_no_effect(already_resolved)

        reopened = fixture.execute(reply_command(thread_id, "message-reopen", REVIEWER))
        self.assertEqual(reopened["result"]["result_class"], "SUCCESS")
        self.assertEqual(reopened["after"]["authoritative_state"]["threads"][0]["status"], "OPEN")

        approved = self.fixture(initial_version_status="APPROVED")
        approved_reply = approved.execute(reply_command("thread-fixture-missing"))
        self.assertEqual(approved_reply["result"]["error"]["code"], "VERSION_READ_ONLY")
        self.assert_no_effect(approved_reply)

    def test_runtime_plan_has_real_distinct_cases_and_complete_concrete_coverage(self):
        plan = materialize_runtime_plan(CONTRACT, runtime_draft(CONTRACT))
        self.assertEqual(plan["coverage_summary"]["status"], "COMPLETE")
        self.assertEqual(plan["coverage_summary"]["missing_field_refs"], [])
        self.assertEqual(plan["mapping_gaps"], [])
        by_action = {item["action_id"]: item["cases"] for item in plan["actions"]}
        self.assertEqual(set(by_action), {
            "create_pin", "reply_thread", "resend_review_request",
            "resolve_thread", "revoke_review_link", "send_review_request",
        })
        for action_id, cases in by_action.items():
            with self.subTest(action_id=action_id):
                self.assertGreaterEqual(len(cases), 3)
                self.assertTrue(all(case["component_expectations"] for case in cases))
                self.assertTrue(all(case["evidence_assertions"] for case in cases))
                self.assertTrue(all(case["contract_field_refs"] for case in cases))
        for action_id in ("send_review_request", "resend_review_request", "revoke_review_link"):
            self.assertEqual(
                {case["result_expectation"]["result_class"] for case in by_action[action_id]},
                {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
            )

    def test_named_runtime_scenarios_execute_the_real_handlers(self):
        self.assertIsNotNone(execute_fixture_scenario)
        expected = {
            "create_pin": {"SUCCESS", "REJECTED", "IDEMPOTENT_REPLAY"},
            "reply_thread": {"SUCCESS", "REJECTED", "IDEMPOTENT_REPLAY"},
            "resolve_thread": {"SUCCESS", "REJECTED", "IDEMPOTENT_REPLAY"},
            "send_review_request": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
            "resend_review_request": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
            "revoke_review_link": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
        }
        for action_id, result_classes in expected.items():
            for result_class in result_classes:
                with self.subTest(action_id=action_id, result_class=result_class):
                    execution = execute_fixture_scenario(CONTRACT, action_id, result_class)
                    self.assertEqual(execution["command"]["action_id"], action_id)
                    self.assertEqual(execution["result"]["result_class"], result_class)
                    if result_class in {"REJECTED", "STALE", "IDEMPOTENT_REPLAY"}:
                        self.assert_no_effect(execution)
                    else:
                        self.assertEqual(execution["deltas"]["revision"], 1)
                        self.assertEqual(len(execution["deltas"]["history"]), 1)
                        self.assertEqual(len(execution["deltas"]["business_side_effects"]), 1)

    def test_same_fixture_command_with_changed_payload_is_not_replayed(self):
        fixture = self.fixture()
        first = fixture.execute(pin_command("message-conflict"))
        self.assertEqual(first["result"]["result_class"], "SUCCESS")
        changed = copy.deepcopy(pin_command("message-conflict"))
        changed["comment"] = "Different logical message."
        conflict = fixture.execute(changed)
        self.assertEqual(conflict["result"]["error"]["code"], "ATTEMPT_ID_CONFLICT")
        self.assert_no_effect(conflict)


if __name__ == "__main__":
    unittest.main()
