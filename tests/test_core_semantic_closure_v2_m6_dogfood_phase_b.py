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

from approval_v2 import (  # noqa: E402
    approval_manifest_digest,
    build_approval_commitment,
    build_approval_manifest_for_review,
    definition_digest,
)
from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402


DOGFOOD_ROOT = ROOT / "evals" / "core-semantic-closure-v2-m6" / "dogfood"
STATE_PATH = (
    DOGFOOD_ROOT
    / "product-definition"
    / "client-feedback-portal-dogfood-v2"
    / "state.json"
)
MANIFEST_PATH = DOGFOOD_ROOT / "approval-manifest.json"
HANDOFF_PATH = DOGFOOD_ROOT / "handoff-definition.json"
REENTRY_PATH = DOGFOOD_ROOT / "reentry-probe.json"

DEFINITION_DIGEST = "e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c"
MANIFEST_DIGEST = "60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705"
APPROVED_AT = "2026-08-30T11:54:26Z"
RUNTIME_GAP_FIELDS = {
    "input_invariants",
    "default_result",
    "result_expectations",
    "test_obligations",
}
ACTION_IDS = {
    "create_pin",
    "reply_thread",
    "resend_review_request",
    "resolve_thread",
    "revoke_review_link",
    "send_review_request",
}
ADDITIONAL_GAP_PATHS = {"actions/reply_thread/actor"}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class CoreSemanticClosureV2M6DogfoodPhaseBStoppedPathTest(unittest.TestCase):
    def setUp(self):
        self.state = load_json(STATE_PATH)
        self.manifest = load_json(MANIFEST_PATH)

    def test_exact_user_approval_closes_the_unchanged_definition(self):
        self.assertEqual(validate_state_v2(self.state), [])
        self.assertTrue(evaluate_closure_v2(self.state)["closed"])
        self.assertEqual(self.state["project"]["definition_revision"], 1)
        self.assertEqual(self.state["project"]["definition_status"], "CLOSED")
        self.assertEqual(definition_digest(self.state), DEFINITION_DIGEST)
        self.assertEqual(approval_manifest_digest(self.manifest), MANIFEST_DIGEST)
        review_copy = copy.deepcopy(self.state)
        review_copy["project"]["definition_status"] = "READY_FOR_REVIEW"
        review_copy["approval"] = {"status": "UNAPPROVED"}
        review_copy["approval_history"] = []
        self.assertEqual(build_approval_manifest_for_review(review_copy), self.manifest)
        self.assertEqual(
            self.state["approval"],
            {
                "status": "APPROVED",
                "approved_revision": 1,
                "approved_definition_digest": DEFINITION_DIGEST,
                "approved_manifest_digest": MANIFEST_DIGEST,
                "approved_at": APPROVED_AT,
                "approved_by": "user",
            },
        )
        self.assertEqual(
            self.state["approval_history"],
            [build_approval_commitment(self.state, self.manifest)],
        )

    def test_actual_compiler_gap_is_null_contract_and_affected_only_reentry(self):
        definition = load_json(HANDOFF_PATH)
        actions = {action["action_id"]: action for action in definition["actions"]}
        shared_canvas_scope = {
            "REQ-005",
            "REQ-006",
            "SCR-007",
            "SURF-001",
            "SURF-002",
            "SURF-003",
            "SURF-004",
        }
        for action_id in ("create_pin", "reply_thread", "resolve_thread"):
            self.assertEqual(
                set(actions[action_id]["authority_scope_refs"]), shared_canvas_scope
            )
        self.assertEqual(
            actions["create_pin"]["fields"]["actor"],
            {
                "kind": "DIRECT_AUTHORITY",
                "source_seed_ref": "SEED-85cdd056577c5a7b55b59c5a",
            },
        )
        self.assertEqual(
            actions["resolve_thread"]["fields"]["actor"],
            {
                "kind": "DIRECT_AUTHORITY",
                "source_seed_ref": "SEED-65b2a6c9b4932974b3b60496",
            },
        )
        self.assertEqual(
            actions["reply_thread"]["fields"]["actor"]["kind"], "UNRESOLVED"
        )
        result = compile_handoff_definition(self.state, definition)

        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertIsNone(result["contract"])
        self.assertEqual(result["semantic_debt"]["authority_gap_count"], 25)
        observed_paths = {
            gap["field_path"] for gap in result["semantic_debt"]["authority_gaps"]
        }
        self.assertEqual(
            observed_paths,
            {
                f"actions/{action_id}/{field_name}"
                for action_id in ACTION_IDS
                for field_name in RUNTIME_GAP_FIELDS
            }
            | ADDITIONAL_GAP_PATHS,
        )
        self.assertEqual(len(result["reentry_events"]), 25)
        for event in result["reentry_events"]:
            self.assertEqual(event["schema_version"], "joewrks.product-definition-reentry/1.0")
            self.assertIsNone(event["source_contract_hash"])
            self.assertEqual(event["source_definition_digest"], DEFINITION_DIGEST)
            self.assertEqual(event["halt_scope"]["mode"], "AFFECTED_ONLY")
            self.assertEqual(len(event["affected_action_ids"]), 1)
            self.assertEqual(event["affected_lifecycle_ids"], [])
            self.assertNotIn("id", event["candidate_unknown"])

    def test_persisted_reentry_evidence_is_exact_compiler_output(self):
        definition = load_json(HANDOFF_PATH)
        self.assertEqual(
            load_json(REENTRY_PATH),
            compile_handoff_definition(self.state, definition),
        )

    def test_stopped_path_does_not_fabricate_runtime_success(self):
        for relative in (
            "action-contract-v2.json",
            "runtime-evidence.jsonl",
            "runtime-conformance-report.json",
            "final-state.json",
        ):
            self.assertFalse((DOGFOOD_ROOT / relative).exists(), relative)
        self.assertFalse((DOGFOOD_ROOT / "runtime-fixture").exists())


if __name__ == "__main__":
    unittest.main()
