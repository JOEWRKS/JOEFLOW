import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from migration_v2 import migrate_state_v020, verify_migration_result  # noqa: E402


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
README_PATH = EVAL_ROOT / "README.md"
AUDIT_PATH = EVAL_ROOT / "MIGRATION_AUDIT.md"

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


class CoreSemanticClosureV2M6DogfoodNeedsContextTest(unittest.TestCase):
    def test_invalid_track_b_checkpoint_is_absent_until_field_level_authority_exists(self):
        invalid_checkpoint_artifacts = (
            STATE_PATH,
            MANIFEST_PATH,
            EVIDENCE_MAP_PATH,
            RUNBOOK_PATH,
        )
        self.assertEqual(
            [path for path in invalid_checkpoint_artifacts if path.exists()], []
        )

    def test_stop_documents_preserve_user_authority_and_exact_gap_without_readiness(self):
        readme = README_PATH.read_text(encoding="utf-8")
        audit = AUDIT_PATH.read_text(encoding="utf-8")
        stop_record = readme + "\n" + audit

        self.assertIn("NEEDS_CONTEXT", stop_record)
        self.assertIn("FIELD_LEVEL_UX_AUTHORITY_GAP", stop_record)
        self.assertIn(ANALYTICS_DECISION, stop_record)
        self.assertNotIn("READY_FOR_REVIEW", stop_record)
        self.assertNotIn("DOGFOOD_V2_MANIFEST_READY", stop_record)
        self.assertNotIn("Approval Manifest digest", stop_record)
        self.assertTrue((LEGACY_ROOT / "state.json").is_file())


if __name__ == "__main__":
    unittest.main()
