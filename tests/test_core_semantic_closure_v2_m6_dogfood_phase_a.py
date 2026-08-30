import json
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
        self.assertEqual(
            {pack["pack_id"] for pack in manifest["active_grill_packs"]},
            {"GRILL-CORE-1", "GRILL-AUTH-1", "GRILL-ASYNC-1", "GRILL-PERMISSION-1"},
        )
        self.assertNotIn("approved_by", json.dumps(packet))
        self.assertNotIn("approved_at", json.dumps(packet))


if __name__ == "__main__":
    unittest.main()
