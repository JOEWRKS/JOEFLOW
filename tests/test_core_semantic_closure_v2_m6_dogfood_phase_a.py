import json
from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from migration_v2 import migrate_state_v020, verify_migration_result  # noqa: E402
from approval_v2 import (  # noqa: E402
    approval_manifest_digest,
    build_approval_commitment,
    build_approval_manifest_for_review,
    definition_digest,
    semantic_readiness_metrics,
)
from state_validation_v2 import validate_state_v2  # noqa: E402


LEGACY_ROOT = ROOT / "product-definition" / "client-feedback-portal-dogfood"
EVAL_ROOT = ROOT / "evals" / "core-semantic-closure-v2-m6"
DOGFOOD_ROOT = EVAL_ROOT / "dogfood"
MIGRATION_ROOT = DOGFOOD_ROOT / "migration"
STATE_PATH = (
    DOGFOOD_ROOT
    / "product-definition"
    / "client-feedback-portal-dogfood-v2"
    / "state.json"
)
MIGRATION_CANDIDATE_PATH = MIGRATION_ROOT / "legacy-candidate.json"
MIGRATION_RECEIPT_PATH = MIGRATION_ROOT / "migration-receipt.json"
MANIFEST_PATH = DOGFOOD_ROOT / "approval-manifest.json"
EVIDENCE_MAP_PATH = DOGFOOD_ROOT / "phase-a-evidence-map.json"
RUNBOOK_PATH = EVAL_ROOT / "DOGFOOD_RUNBOOK.md"

SELECTED_IDS = {
    "goals": {"GOAL-001"},
    "users": {"USR-001", "USR-002"},
    "requirements": {"REQ-005", "REQ-006"},
    "decisions": {
        "DEC-001", "DEC-008", "DEC-012", "DEC-013", "DEC-018",
        "DEC-019", "DEC-034", "DEC-041",
    },
    "rules": {
        "RULE-001", "RULE-002", "RULE-003", "RULE-017", "RULE-020",
        "RULE-021", "RULE-022", "RULE-023", "RULE-024", "RULE-026",
        "RULE-030", "RULE-031", "RULE-032", "RULE-033", "RULE-034",
        "RULE-040", "RULE-041", "RULE-042", "RULE-043", "RULE-044",
        "RULE-046",
        "RULE-084", "RULE-093", "RULE-094", "RULE-095", "RULE-096",
    },
    "flows": {"FLOW-005", "FLOW-006"},
    "screens": {"SCR-006", "SCR-007"},
    "states": {"STATE-001"},
    "data": {"DATA-002", "DATA-004", "DATA-005", "DATA-007", "DATA-008", "DATA-015"},
    "integrations": {"INT-001"},
    "acceptance_criteria": {"AC-005", "AC-006"},
    "tasks": {"TASK-004", "TASK-005"},
}

ANALYTICS_DECISION = (
    "For this bounded M6 existing-product V2 dogfood Product Definition only, "
    "product analytics/telemetry is NOT used. REQ-005/REQ-006 review-link access and "
    "thread actions emit no analytics events. Introduce no analytics event names, "
    "properties, tracking identifiers, analytics retention/access policy, funnels, "
    "or success metrics. Existing domain/business history remains ordinary product "
    "state/history where already required. Existing email delivery/send status remains "
    "ordinary product operational/domain state where already required. Neither is "
    "reclassified as analytics telemetry. This is an explicit current user product "
    "decision/boundary, not an inference from missing implementation. It is not a "
    "permanent system-wide prohibition for future products/revisions."
)

EXPECTED_DEFINITION_DIGEST = "37354762f3af6df00ea95d045447883ef0e2d024f9f27a9616eeb80d7fe23250"
EXPECTED_MANIFEST_DIGEST = "924cb2ef00bba7290cec9320af2a0adb0e283dcc225947998f50881a605253b4"

REQ_005_UX_AUTHORITIES = {
    "SCR-006", "FLOW-005", "AC-005", "STATE-001", "DATA-004", "DATA-005",
    "INT-001", "RULE-001", "RULE-002", "RULE-003", "RULE-026", "RULE-030",
    "RULE-031", "RULE-032", "RULE-033", "RULE-034", "RULE-046",
}
REQ_006_UX_AUTHORITIES = {
    "SCR-007", "FLOW-005", "FLOW-006", "AC-006", "STATE-001", "DATA-002",
    "DATA-007", "DATA-008", "DATA-015", "INT-001", "RULE-001", "RULE-017",
    "RULE-020", "RULE-021", "RULE-022", "RULE-023", "RULE-024", "RULE-026",
    "RULE-040", "RULE-041", "RULE-042", "RULE-043", "RULE-044", "RULE-084",
    "RULE-093", "RULE-094", "RULE-095", "RULE-096",
}

EXACT_ACTION_AUTHORITIES = {
    ("SCR-006", "send_review_request"): {
        "entry": "SCR-006", "precondition": "FLOW-005", "input": "DATA-004",
        "validation": "AC-005", "submit": "FLOW-005", "success": "AC-005",
        "failure": "RULE-032", "retry": "RULE-034", "cancel": "FLOW-005",
        "back": "SCR-006", "refresh": "RULE-034",
        "duplicate_concurrent_action": "RULE-030", "timeout": "RULE-034",
        "offline": "RULE-034",
        "permission": "RULE-031", "data_mutation": "DATA-004",
        "session_expiration": "RULE-026", "side_effect": "RULE-046",
        "notification": "INT-001", "persistence": "DATA-004", "undo": "FLOW-005",
        "destructive_confirmation": "N/A:EVD-007",
    },
    ("SCR-006", "revoke_review_link"): {
        "entry": "SCR-006", "precondition": "FLOW-005", "input": "DATA-004",
        "validation": "AC-005", "submit": "FLOW-005", "success": "AC-005",
        "failure": "RULE-032", "retry": "RULE-034", "cancel": "FLOW-005",
        "back": "SCR-006", "refresh": "RULE-034",
        "duplicate_concurrent_action": "RULE-030", "timeout": "RULE-034",
        "offline": "RULE-034",
        "permission": "RULE-033", "data_mutation": "DATA-004",
        "session_expiration": "RULE-026", "side_effect": "DATA-004",
        "notification": "N/A:EVD-014", "persistence": "DATA-004",
        "undo": "FLOW-005", "destructive_confirmation": "N/A:EVD-007",
    },
    ("SCR-006", "resend_review_request"): {
        "entry": "SCR-006", "precondition": "FLOW-005", "input": "DATA-004",
        "validation": "AC-005", "submit": "FLOW-005", "success": "AC-005",
        "failure": "RULE-032", "retry": "RULE-034", "cancel": "FLOW-005",
        "back": "SCR-006", "refresh": "RULE-034",
        "duplicate_concurrent_action": "RULE-030", "timeout": "RULE-034",
        "offline": "RULE-034",
        "permission": "RULE-031", "data_mutation": "DATA-004",
        "session_expiration": "RULE-026", "side_effect": "RULE-046",
        "notification": "INT-001", "persistence": "DATA-004", "undo": "FLOW-005",
        "destructive_confirmation": "N/A:EVD-007",
    },
    ("SCR-007", "create_pin"): {
        "entry": "SCR-007", "precondition": "FLOW-006", "input": "DATA-002",
        "validation": "AC-006", "submit": "FLOW-006", "success": "AC-006",
        "failure": "RULE-084", "retry": "RULE-095", "cancel": "RULE-024",
        "back": "SCR-007", "refresh": "RULE-095",
        "duplicate_concurrent_action": "RULE-084", "timeout": "RULE-093",
        "offline": "RULE-093",
        "permission": "RULE-020", "data_mutation": "DATA-002",
        "session_expiration": "RULE-026",
        "side_effect": "DATA-007", "notification": "INT-001",
        "persistence": "DATA-002", "undo": "RULE-024",
        "destructive_confirmation": "N/A:EVD-007",
    },
    ("SCR-007", "reply_thread"): {
        "entry": "SCR-007", "precondition": "FLOW-006", "input": "DATA-002",
        "validation": "AC-006", "submit": "FLOW-006", "success": "AC-006",
        "failure": "RULE-084", "retry": "RULE-095", "cancel": "RULE-024",
        "back": "SCR-007", "refresh": "RULE-095",
        "duplicate_concurrent_action": "RULE-084", "timeout": "RULE-093",
        "offline": "RULE-093",
        "permission": "RULE-020", "data_mutation": "DATA-002",
        "session_expiration": "RULE-026",
        "side_effect": "DATA-008", "notification": "INT-001",
        "persistence": "DATA-002", "undo": "RULE-024",
        "destructive_confirmation": "N/A:EVD-007",
    },
    ("SCR-007", "resolve_thread"): {
        "entry": "SCR-007", "precondition": "FLOW-006", "input": "DATA-002",
        "validation": "AC-006", "submit": "FLOW-006", "success": "AC-006",
        "failure": "RULE-084", "retry": "RULE-095", "cancel": "RULE-024",
        "back": "SCR-007", "refresh": "RULE-095",
        "duplicate_concurrent_action": "RULE-084", "timeout": "RULE-093",
        "offline": "RULE-093",
        "permission": "RULE-021", "data_mutation": "DATA-002",
        "session_expiration": "RULE-026",
        "side_effect": "DATA-002", "notification": "N/A:EVD-014",
        "persistence": "DATA-002", "undo": "RULE-024",
        "destructive_confirmation": "N/A:EVD-007",
    },
}

EXACT_STATE_AUTHORITIES = {
    "SCR-006": {
        "default": "SCR-006", "loading": "FLOW-005", "empty": "RULE-030",
        "partial": "RULE-034", "success": "AC-005", "error": "RULE-032",
        "disabled": "RULE-032", "permission_denied": "RULE-033",
        "unauthenticated": "FLOW-005", "offline": "RULE-034",
        "timeout": "RULE-034", "retrying": "RULE-034",
        "submitting": "FLOW-005", "completed": "AC-005",
        "cancelled": "FLOW-005", "expired": "RULE-026",
    },
    "SCR-007": {
        "default": "SCR-007", "loading": "FLOW-006", "empty": "RULE-017",
        "partial": "STATE-001", "success": "AC-006", "error": "RULE-084",
        "disabled": "RULE-017", "permission_denied": "RULE-020",
        "unauthenticated": "FLOW-005", "offline": "RULE-093",
        "timeout": "RULE-093", "retrying": "RULE-095",
        "submitting": "FLOW-006", "completed": "AC-006",
        "cancelled": "RULE-024", "expired": "RULE-026",
    },
}

EXPECTED_RECORD_EVIDENCE = {
    "GOAL-001": ["EVD-001"], "USR-001": ["EVD-001"],
    "USR-002": ["EVD-001"], "REQ-005": ["EVD-001"],
    "REQ-006": ["EVD-001"], "DEC-001": ["EVD-002"],
    "DEC-008": ["EVD-003"], "DEC-012": ["EVD-002"],
    "DEC-013": ["EVD-002"], "DEC-018": ["EVD-004"],
    "DEC-019": ["EVD-004"], "DEC-034": ["EVD-005"],
    "DEC-041": ["EVD-008"], "RULE-001": ["EVD-002"],
    "RULE-002": ["EVD-002"], "RULE-003": ["EVD-013"],
    "RULE-017": ["EVD-009"], "RULE-020": ["EVD-003"],
    "RULE-021": ["EVD-003"], "RULE-022": ["EVD-003"],
    "RULE-023": ["EVD-003"], "RULE-024": ["EVD-003", "EVD-012"],
    "RULE-026": ["EVD-002"], "RULE-030": ["EVD-002"],
    "RULE-031": ["EVD-002"], "RULE-032": ["EVD-002"],
    "RULE-033": ["EVD-002"], "RULE-034": ["EVD-002"],
    "RULE-040": ["EVD-004"], "RULE-041": ["EVD-004"],
    "RULE-042": ["EVD-004"], "RULE-043": ["EVD-004"],
    "RULE-044": ["EVD-004"], "RULE-046": ["EVD-011"],
    "RULE-084": ["EVD-010"], "RULE-093": ["EVD-005"],
    "RULE-094": ["EVD-005"], "RULE-095": ["EVD-005"],
    "RULE-096": ["EVD-005"], "FLOW-005": ["EVD-006"],
    "FLOW-006": ["EVD-006"], "SCR-006": ["EVD-006"],
    "SCR-007": ["EVD-006"], "STATE-001": ["EVD-010", "EVD-012"],
    "DATA-002": ["EVD-003", "EVD-012"], "DATA-004": ["EVD-002"],
    "DATA-005": ["EVD-002"], "DATA-007": ["EVD-004"],
    "DATA-008": ["EVD-004"], "DATA-015": ["EVD-005"],
    "INT-001": ["EVD-004", "EVD-011"], "AC-005": ["EVD-006"],
    "AC-006": ["EVD-006"], "TASK-004": ["EVD-006"],
    "TASK-005": ["EVD-006"], "UNK-001": ["EVD-002"],
    "UNK-005": ["EVD-003"], "UNK-018": ["EVD-005"],
    "UNK-021": ["EVD-002"], "UNK-031": ["EVD-002"],
    "UNK-034": ["EVD-004"], "UNK-036": ["EVD-004"],
    "UNK-049": ["EVD-008"],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def legacy_ids(state):
    return sorted(
        record["id"]
        for records in state["objects"].values()
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    )


def statuses(value):
    if isinstance(value, dict):
        if isinstance(value.get("status"), str):
            yield value["status"]
        for child in value.values():
            yield from statuses(child)
    elif isinstance(value, list):
        for child in value:
            yield from statuses(child)


def covered_authority_ids(cell):
    return [binding["record_id"] for binding in cell["authority_bindings"]]


def semantic_correspondence_errors(state):
    errors = []
    allowed_by_screen = {
        "SCR-006": REQ_005_UX_AUTHORITIES,
        "SCR-007": REQ_006_UX_AUTHORITIES,
    }
    for screen in state["ux_coverage"]:
        screen_id = screen["screen_id"]
        allowed = allowed_by_screen[screen_id]
        for state_key, cell in screen["states"].items():
            foreign = set(covered_authority_ids(cell)) - allowed
            if foreign:
                errors.append((screen_id, "state", state_key, tuple(sorted(foreign))))
            expected_id = EXACT_STATE_AUTHORITIES[screen_id][state_key]
            if cell["status"] != "COVERED" or covered_authority_ids(cell) != [expected_id]:
                errors.append((screen_id, "state", state_key, expected_id))
        for action in screen["actions"]:
            action_key = action["key"]
            for axis, cell in action["cells"].items():
                foreign = set(covered_authority_ids(cell)) - allowed
                if foreign:
                    errors.append((screen_id, action_key, axis, tuple(sorted(foreign))))
            for axis, expected_id in EXACT_ACTION_AUTHORITIES[(screen_id, action_key)].items():
                cell = action["cells"][axis]
                actual_ids = covered_authority_ids(cell)
                if expected_id.startswith("N/A:"):
                    expected_evidence = expected_id.split(":", 1)[1]
                    basis_ids = [binding["record_id"] for binding in cell["basis_bindings"]]
                    if cell["status"] != "N/A" or actual_ids or basis_ids != [expected_evidence]:
                        errors.append((screen_id, action_key, axis, expected_id))
                elif cell["status"] != "COVERED" or actual_ids != [expected_id]:
                    errors.append((screen_id, action_key, axis, expected_id, tuple(actual_ids)))
    return errors


class CoreSemanticClosureV2M6DogfoodPhaseATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legacy = load_json(LEGACY_ROOT / "state.json")
        cls.migrated = load_json(MIGRATION_CANDIDATE_PATH)
        cls.receipt = load_json(MIGRATION_RECEIPT_PATH)

    def test_track_a_artifacts_exist(self):
        required = (
            EVAL_ROOT / "README.md",
            EVAL_ROOT / "MIGRATION_AUDIT.md",
            MIGRATION_CANDIDATE_PATH,
            MIGRATION_RECEIPT_PATH,
        )
        self.assertEqual([path for path in required if not path.is_file()], [])

    def test_track_a_is_the_complete_open_unapproved_migration_audit(self):
        fresh_candidate, fresh_receipt = migrate_state_v020(self.legacy)

        self.assertEqual(self.migrated, fresh_candidate)
        self.assertEqual(self.receipt, fresh_receipt)
        self.assertEqual(
            verify_migration_result(self.legacy, self.migrated, self.receipt), []
        )
        self.assertEqual(self.migrated["project"]["definition_status"], "OPEN")
        self.assertEqual(self.migrated["approval"], {"status": "UNAPPROVED"})
        self.assertEqual(self.migrated["approval_history"], [])
        self.assertEqual(
            self.migrated["migration"]["preserved_ids"], legacy_ids(self.legacy)
        )
        self.assertNotIn(
            "COVERED",
            set(
                statuses(
                    {
                        "coverage": self.migrated["coverage"],
                        "ux_coverage": self.migrated["ux_coverage"],
                        "grill_coverage": self.migrated["grill_coverage"],
                    }
                )
            ),
        )
        self.assertIsNotNone(
            self.migrated["migration"]["source_legacy_approval_digest"]
        )
        self.assertTrue(self.migrated["migration"]["reconciliation_gaps"])
        self.assertTrue(
            all(
                isinstance(gap["source_path"], str) and gap["source_path"]
                for gap in self.migrated["migration"]["reconciliation_gaps"].values()
            )
        )
        for unknown in self.migrated["objects"]["unknowns"]:
            if unknown.get("origin", {}).get("kind") == "MIGRATION_RECONCILIATION":
                self.assertTrue(unknown["origin"]["source_path"])

class CoreSemanticClosureV2M6DogfoodContinuationTest(unittest.TestCase):
    def test_selected_ux_cells_bind_exact_surface_and_action_authority(self):
        state = load_json(STATE_PATH)

        self.assertEqual(semantic_correspondence_errors(state), [])

        mutation = deepcopy(state)
        review_screen = next(
            row for row in mutation["ux_coverage"] if row["screen_id"] == "SCR-006"
        )
        send_action = next(
            action for action in review_screen["actions"]
            if action["key"] == "send_review_request"
        )
        canvas_screen = next(
            row for row in state["ux_coverage"] if row["screen_id"] == "SCR-007"
        )
        canvas_action = next(
            action for action in canvas_screen["actions"] if action["key"] == "reply_thread"
        )
        send_action["cells"]["precondition"] = deepcopy(
            canvas_action["cells"]["precondition"]
        )
        self.assertIn(
            ("SCR-006", "send_review_request", "precondition", ("FLOW-006",)),
            semantic_correspondence_errors(mutation),
        )

    def test_current_records_have_exact_first_class_evidence_correspondence(self):
        state = load_json(STATE_PATH)
        evidence_map = load_json(EVIDENCE_MAP_PATH)
        evidence = {record["id"]: record for record in state["evidence"]}

        self.assertEqual(evidence_map["record_evidence"], EXPECTED_RECORD_EVIDENCE)
        self.assertEqual(
            evidence["EVD-003"]["locator"],
            "product-definition/client-feedback-portal-dogfood/state.json#/objects/decisions/DEC-008,DEC-009",
        )
        self.assertNotIn("append-only", evidence["EVD-003"]["claim"])
        self.assertNotIn("exact Version", evidence["EVD-003"]["claim"])
        self.assertIn("SCREEN_SPEC.md#SCR-006-SCR-007", evidence["EVD-006"]["locator"])
        self.assertEqual(
            evidence["EVD-009"]["locator"],
            "product-definition/client-feedback-portal-dogfood/state.json#/objects/decisions/DEC-006",
        )
        self.assertEqual(
            evidence["EVD-010"]["locator"],
            "product-definition/client-feedback-portal-dogfood/state.json#/objects/decisions/DEC-031",
        )
        self.assertIn("review request", evidence["EVD-011"]["claim"])
        self.assertIn("append-only", evidence["EVD-012"]["claim"])
        self.assertIn("public anonymous", evidence["EVD-013"]["claim"])
        self.assertIn("no revocation or thread-resolution", evidence["EVD-014"]["claim"])

        mutation = deepcopy(evidence_map["record_evidence"])
        mutation["INT-001"] = ["EVD-004"]
        self.assertNotEqual(mutation, EXPECTED_RECORD_EVIDENCE)
        mutation = deepcopy(evidence_map["record_evidence"])
        mutation["RULE-084"] = ["EVD-003"]
        self.assertNotEqual(mutation, EXPECTED_RECORD_EVIDENCE)

    def test_user_decision_closes_analytics_only_for_the_bounded_slice(self):
        self.assertTrue(STATE_PATH.is_file())
        state = load_json(STATE_PATH)

        evidence = {record["id"]: record for record in state["evidence"]}
        decisions = {record["id"]: record for record in state["objects"]["decisions"]}
        self.assertEqual(evidence["EVD-008"]["source_kind"], "USER_CONFIRMED_INTENT")
        self.assertEqual(evidence["EVD-008"]["authority_classes"], ["INTENT"])
        self.assertEqual(evidence["EVD-008"]["claim"], ANALYTICS_DECISION)
        self.assertEqual(decisions["DEC-041"]["statement"], ANALYTICS_DECISION)
        self.assertEqual(decisions["DEC-041"]["evidence_refs"], ["EVD-008"])

        for row in state["coverage"]:
            analytics = row["cells"]["analytics"]
            self.assertEqual(analytics["status"], "N/A")
            self.assertEqual(analytics["authority_bindings"], [])
            self.assertEqual(
                [binding["record_id"] for binding in analytics["basis_bindings"]],
                ["EVD-008"],
            )
        serialized = json.dumps(state, ensure_ascii=False)
        self.assertNotIn('"analytics_events"', serialized.lower())
        self.assertNotIn('"analytics_properties"', serialized.lower())
        self.assertNotIn('"tracking_identifiers"', serialized.lower())

    def test_track_b_is_exact_ready_unapproved_native_v2_and_manifest_is_deterministic(self):
        for path in (STATE_PATH, MANIFEST_PATH, EVIDENCE_MAP_PATH, RUNBOOK_PATH):
            self.assertTrue(path.is_file(), path)
        state = load_json(STATE_PATH)
        packet = load_json(MANIFEST_PATH)
        evidence_map = load_json(EVIDENCE_MAP_PATH)

        self.assertEqual(state["project"]["slug"], "client-feedback-portal-dogfood-v2")
        self.assertEqual(state["project"]["definition_status"], "READY_FOR_REVIEW")
        self.assertEqual(state["project"]["definition_revision"], 1)
        self.assertEqual(state["project"]["bootstrap_mode"], "EXISTING_PRODUCT_RECONCILIATION")
        self.assertEqual(state["migration"], {"mode": "NATIVE"})
        self.assertEqual(state["approval"], {"status": "UNAPPROVED"})
        self.assertEqual(state["approval_history"], [])
        self.assertEqual(validate_state_v2(state), [])
        self.assertTrue(all(value == 0 for value in semantic_readiness_metrics(state).values()))

        for group, expected in SELECTED_IDS.items():
            self.assertSetEqual({record["id"] for record in state["objects"][group]}, expected, group)
        evidence = {record["id"]: record for record in state["evidence"]}
        evidence_mapped_ids = {
            record["id"]
            for group, records in state["objects"].items()
            for record in records
            if record["status"] == "CURRENT"
            or (group == "unknowns" and record["status"] == "RESOLVED")
        }
        self.assertEqual(evidence_map["scope"], ["REQ-005", "REQ-006"])
        self.assertSetEqual(set(evidence_map["record_evidence"]), evidence_mapped_ids)
        for record_id, refs in evidence_map["record_evidence"].items():
            self.assertTrue(refs, record_id)
            self.assertTrue(all("INTENT" in evidence[ref]["authority_classes"] for ref in refs), record_id)

        manifest = build_approval_manifest_for_review(state)
        self.assertEqual(packet, {
            "manifest": manifest,
            "manifest_digest": approval_manifest_digest(manifest),
            "approval_commitment": build_approval_commitment(state, manifest),
        })
        self.assertEqual(definition_digest(state), EXPECTED_DEFINITION_DIGEST)
        self.assertEqual(packet["manifest"]["definition_digest"], EXPECTED_DEFINITION_DIGEST)
        self.assertEqual(packet["manifest_digest"], EXPECTED_MANIFEST_DIGEST)
        self.assertEqual(len(packet["manifest"]["added"]), 81)

        drifted_state = deepcopy(state)
        drifted_state["objects"]["integrations"][0]["purpose"] += " drift"
        self.assertNotEqual(definition_digest(drifted_state), EXPECTED_DEFINITION_DIGEST)
        drifted_packet = deepcopy(packet)
        drifted_packet["manifest"]["definition_digest"] = "0" * 64
        drifted_packet["manifest_digest"] = approval_manifest_digest(
            drifted_packet["manifest"]
        )
        self.assertNotEqual(drifted_packet["manifest_digest"], EXPECTED_MANIFEST_DIGEST)
        self.assertEqual(
            {pack["pack_id"] for pack in manifest["active_grill_packs"]},
            {"GRILL-CORE-1", "GRILL-AUTH-1", "GRILL-ASYNC-1", "GRILL-PERMISSION-1"},
        )
        self.assertNotIn("approved_by", json.dumps(packet))
        self.assertNotIn("approved_at", json.dumps(packet))


if __name__ == "__main__":
    unittest.main()
