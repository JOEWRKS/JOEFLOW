import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
MIGRATION_CLI = SCRIPTS / "migrate_state.py"
sys.path.insert(0, str(SCRIPTS))

from migration_v2 import (  # noqa: E402
    MigrationError,
    allocate_generated_ids,
    build_migration_plan,
    canonical_json_bytes,
)
from tests.test_validators import closed_state  # noqa: E402


class MigrationFoundationTest(unittest.TestCase):
    def test_valid_legacy_state_builds_foundation_only_plan(self):
        state = closed_state()

        plan = build_migration_plan(state)

        self.assertEqual(plan["schema_version"], "joewrks.state-migration-plan/1.0")
        self.assertEqual(plan["status"], "FOUNDATION_PLAN_ONLY")
        self.assertEqual(plan["from_schema"], "0.1.2.1")
        self.assertEqual(plan["to_schema"], "0.2.0")
        self.assertEqual(plan["migration_version"], "0.2.0-foundation.1")
        self.assertEqual(len(plan["source_digest"]), 64)
        self.assertNotIn("migrated_state", plan)

        temporal_keys = {"created_at", "generated_at", "migrated_at", "timestamp"}
        self.assertTrue(temporal_keys.isdisjoint(plan))

    def test_invalid_legacy_state_raises_source_invalid_with_validator_errors(self):
        state = closed_state()
        state["objects"]["requirements"][0]["screens"] = ["SCR-999"]

        with self.assertRaises(MigrationError) as caught:
            build_migration_plan(state)

        self.assertEqual(caught.exception.code, "MIGRATION_SOURCE_INVALID")
        self.assertIsInstance(caught.exception.detail, list)
        self.assertIn("broken_reference", {item["code"] for item in caught.exception.detail})

    def test_v020_source_is_rejected_as_invalid_migration_source(self):
        state = closed_state()
        state["schema_version"] = "0.2.0"

        with self.assertRaises(MigrationError) as caught:
            build_migration_plan(state)

        self.assertEqual(caught.exception.code, "MIGRATION_SOURCE_INVALID")

    def test_canonical_json_bytes_are_stable_and_compact(self):
        value = {"z": "한글", "a": {"y": 2, "x": 1}}

        self.assertEqual(
            canonical_json_bytes(value),
            '{"a":{"x":1,"y":2},"z":"한글"}'.encode("utf-8"),
        )

    def test_generated_unknown_ids_follow_sorted_paths_after_greatest_suffix(self):
        existing = {"UNK-001", "UNK-007", "UNK-103"}
        paths = [
            "/coverage/REQ-002/security",
            "/coverage/REQ-001/actor",
            "/coverage/REQ-001/security",
        ]

        self.assertEqual(
            allocate_generated_ids("UNK", existing, paths),
            {
                "/coverage/REQ-001/actor": "UNK-104",
                "/coverage/REQ-001/security": "UNK-105",
                "/coverage/REQ-002/security": "UNK-106",
            },
        )

    def test_generated_ids_keep_four_digit_suffixes(self):
        self.assertEqual(
            allocate_generated_ids("REQ", {"REQ-999"}, ["/generated/requirement"]),
            {"/generated/requirement": "REQ-1000"},
        )

    def test_reconciliation_sites_have_canonical_paths_reasons_and_unresolved_ids(self):
        state = closed_state()
        state["coverage"][0]["cells"] = {
            "security": {"status": "COVERED"},
        }
        state["ux_coverage"][0]["states"] = {
            "offline": {"status": "N/A", "rationale": "This screen is local only."},
        }
        state["objects"]["screens"][0]["major_actions"] = ["save~/now"]
        state["ux_coverage"][0]["actions"] = [
            {
                "key": "save~/now",
                "cells": {"retry": {"status": "OPEN"}},
            }
        ]

        plan = build_migration_plan(state)

        self.assertEqual(
            plan["reconciliation_sites"],
            [
                {
                    "path": "/coverage/REQ-001/cells/security",
                    "reason": "COVERED_BINDING_REQUIRED",
                    "generated_unknown_id": "UNK-001",
                },
                {
                    "path": "/ux_coverage/SCR-001/actions/save~0~1now/cells/retry",
                    "reason": "OPEN_UNKNOWN_BINDING_REQUIRED",
                    "generated_unknown_id": "UNK-002",
                },
                {
                    "path": "/ux_coverage/SCR-001/states/offline",
                    "reason": "NA_BASIS_BINDING_REQUIRED",
                    "generated_unknown_id": "UNK-003",
                },
            ],
        )
        for item in plan["reconciliation_sites"]:
            self.assertEqual(
                set(item), {"path", "reason", "generated_unknown_id"}
            )

    def test_preserved_ids_include_object_and_contradiction_record_ids(self):
        state = closed_state()
        state["contradictions"] = [{"id": "CON-777", "status": "RESOLVED"}]

        plan = build_migration_plan(state)

        expected = sorted(
            item["id"]
            for items in state["objects"].values()
            for item in items
            if isinstance(item.get("id"), str)
        ) + ["CON-777"]
        self.assertEqual(plan["preserved_ids"], sorted(expected))

    def test_cli_repeated_runs_emit_identical_canonical_stdout_without_mutating_source(self):
        state = closed_state()
        source_text = json.dumps(state, ensure_ascii=False, indent=2)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "legacy-state.json"
            source.write_text(source_text, encoding="utf-8")
            command = [sys.executable, str(MIGRATION_CLI), "--plan", str(source)]

            first = subprocess.run(command, capture_output=True, text=True, check=False)
            second = subprocess.run(command, capture_output=True, text=True, check=False)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            payload = json.loads(first.stdout)
            self.assertEqual(
                first.stdout,
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
            )
            self.assertEqual(source.read_text(encoding="utf-8"), source_text)
            self.assertEqual(payload["status"], "FOUNDATION_PLAN_ONLY")

    def test_cli_reports_migration_failure_as_canonical_json(self):
        state = closed_state()
        state["schema_version"] = "0.2.0"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "v2-state.json"
            source.write_text(json.dumps(state), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(MIGRATION_CLI), "--plan", str(source)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["error"]["code"], "MIGRATION_SOURCE_INVALID")
        self.assertEqual(
            result.stdout,
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
        )

    def test_cli_usage_and_read_errors_return_two(self):
        missing_argument = subprocess.run(
            [sys.executable, str(MIGRATION_CLI)],
            capture_output=True,
            text=True,
            check=False,
        )
        missing_file = subprocess.run(
            [sys.executable, str(MIGRATION_CLI), "--plan", str(ROOT / "missing.json")],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(missing_argument.returncode, 2)
        self.assertEqual(missing_file.returncode, 2)


if __name__ == "__main__":
    unittest.main()
