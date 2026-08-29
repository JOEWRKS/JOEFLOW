import copy
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
MIGRATION_CLI = SCRIPTS / "migrate_state.py"
STATE_SCHEMA = (
    ROOT
    / "skills"
    / "joewrks-product-definition"
    / "schemas"
    / "state-v0.2.0.schema.json"
)
sys.path.insert(0, str(SCRIPTS))

import migration_v2
import migrate_state
from approval_v2 import compute_approval_manifest, definition_digest
from authority_binding_v2 import binding_contract_identity, canonical_record_index
from state_validation import validate_state as validate_legacy_state
from state_validation_v2 import evaluate_closure_v2, validate_state_v2
from tests.test_validators import closed_state
from tests.v020_support import (
    decision_record,
    foundation_state,
    materiality,
    unknown_record,
)


MIGRATION_FIELDS = {
    "mode",
    "from_schema",
    "to_schema",
    "migration_version",
    "source_digest",
    "source_revision",
    "source_legacy_status",
    "source_legacy_approval_digest",
    "plan_digest",
    "preserved_ids",
    "promoted_ids",
    "generated_ids",
    "legacy_records",
    "reconciliation_gaps",
    "reconciliation_gap_count",
}
GRILL_DOMAINS = {
    "AUTH",
    "MONEY",
    "FILE_UPLOAD",
    "ASYNC",
    "PERMISSION",
    "DESTRUCTIVE_ACTION",
}
CORE_AXES = (
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state", "data",
    "side_effect", "notification", "validation", "boundary", "persistence",
    "security", "privacy", "analytics", "acceptance",
)
UX_STATE_AXES = (
    "default", "loading", "empty", "partial", "success", "error", "disabled",
    "permission_denied", "unauthenticated", "offline", "timeout", "retrying",
    "submitting", "completed", "cancelled", "expired",
)
UX_ACTION_AXES = (
    "entry", "precondition", "input", "validation", "submit", "success",
    "failure", "retry", "cancel", "back", "refresh",
    "duplicate_concurrent_action", "timeout", "offline", "permission",
    "session_expiration", "data_mutation", "side_effect", "notification",
    "persistence", "undo", "destructive_confirmation",
)
ABSENT_CELL_FIELDS = [
    "authority_bindings", "basis_bindings", "rationale", "status", "unknown_refs",
]


class FailingBinaryWriter:
    def __init__(self, raw, failure):
        self.raw = raw
        self.failure = failure

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.raw.close()

    def write(self, payload):
        if self.failure == "write":
            self.raw.write(payload[: max(1, len(payload) // 2)])
            raise OSError("simulated mid-write failure")
        return self.raw.write(payload)

    def flush(self):
        if self.failure == "flush":
            raise OSError("simulated flush failure")
        return self.raw.flush()

    def fileno(self):
        return self.raw.fileno()


class MigrationApplyTest(unittest.TestCase):
    def write_source(self, directory: Path, state=None) -> tuple[Path, bytes]:
        source = directory / "legacy-state.json"
        source_bytes = (
            json.dumps(
                closed_state() if state is None else state,
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        ).encode("utf-8")
        source.write_bytes(source_bytes)
        return source, source_bytes

    def apply(self, source: Path, destination: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(MIGRATION_CLI),
                "--apply",
                str(source),
                "--output",
                str(destination),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def apply_main_with_file_failure(self, source, destination, failure):
        real_open = Path.open

        def controlled_open(path, *args, **kwargs):
            handle = real_open(path, *args, **kwargs)
            mode = args[0] if args else kwargs.get("mode", "r")
            if "x" in mode and "b" in mode and path.parent == destination.parent:
                return FailingBinaryWriter(handle, failure)
            return handle

        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(Path, "open", new=controlled_open),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            exit_code = migrate_state.main(
                ["--apply", str(source), "--output", str(destination)]
            )
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def candidate_for(self, state=None):
        candidate, receipt = migration_v2.migrate_state_v020(
            closed_state() if state is None else state
        )
        return candidate, receipt

    def gap_at(self, candidate, source_path):
        gaps = candidate["migration"]["reconciliation_gaps"]
        self.assertIsInstance(gaps, dict)
        matches = [gap for gap in gaps.values() if gap["source_path"] == source_path]
        self.assertEqual(len(matches), 1, (source_path, gaps))
        return matches[0]

    def explicit_semantics_state(self):
        state = closed_state()
        complete_unknown = unknown_record("UNK-001", status="RESOLVED")
        complete_unknown["status"] = "ANSWERED"
        complete_unknown["resolved_by"] = ["DEC-001"]
        complete_unknown["resolution_mode"] = "USER_DECISION"
        complete_unknown["resolution_summary"] = "The user selected the explicit option."
        complete_unknown["resolution"] = "The user selected the explicit option."
        complete_unknown["source"] = "user"
        complete_decision = decision_record("DEC-001")
        complete_decision["status"] = "ANSWERED"
        complete_decision["decision"] = complete_decision.pop("statement")
        complete_decision["reason"] = "It satisfies the explicit requirement."
        complete_decision["source"] = "user"
        state["objects"] = {
            "goals": [
                {"id": "GOAL-001", "status": "CURRENT", "text": "Ship the workflow."}
            ],
            "users": [
                {
                    "id": "USR-001",
                    "status": "CURRENT",
                    "role": "Operator",
                    "cardinality": "one per workspace",
                    "identity": "workspace account",
                }
            ],
            "requirements": [
                {
                    "id": "REQ-001",
                    "status": "CURRENT",
                    "text": "Persist submitted work.",
                    "scope": "Submission workflow",
                    "ui_required": True,
                    "materiality": materiality(classification="MATERIAL"),
                }
            ],
            "unknowns": [complete_unknown],
            "decisions": [complete_decision],
            "rules": [
                {
                    "id": "RULE-001",
                    "status": "CURRENT",
                    "text": "Reject duplicate submissions.",
                    "applies_to": ["REQ-001"],
                }
            ],
            "flows": [
                {
                    "id": "FLOW-001",
                    "status": "CURRENT",
                    "goal_refs": ["GOAL-001"],
                    "entry": "The operator opens the form.",
                    "preconditions": ["The operator is signed in."],
                    "paths": ["Submit the completed form."],
                    "outcomes": ["The work is persisted."],
                }
            ],
            "screens": [
                {
                    "id": "SCR-001",
                    "status": "CURRENT",
                    "purpose": "Collect a submission.",
                    "requirements": ["REQ-001"],
                    "interaction_mode": "Interactive form",
                    "major_actions": ["submit"],
                }
            ],
            "states": [
                {
                    "id": "STATE-001",
                    "status": "CURRENT",
                    "owner_refs": ["REQ-001"],
                    "name": "Submitted",
                    "conditions": ["Persistence completed."],
                }
            ],
            "data": [
                {
                    "id": "DATA-001",
                    "status": "CURRENT",
                    "name": "Submission",
                    "purpose": "Store submitted work.",
                    "ownership": "Workspace",
                }
            ],
            "integrations": [
                {
                    "id": "INT-001",
                    "status": "CURRENT",
                    "name": "Persistence service",
                    "purpose": "Write submission records.",
                }
            ],
            "acceptance_criteria": [
                {
                    "id": "AC-001",
                    "status": "CURRENT",
                    "requirements": ["REQ-001"],
                    "assertion": "A valid submission is stored exactly once.",
                }
            ],
            "tasks": [
                {
                    "id": "TASK-001",
                    "status": "CURRENT",
                    "implements": ["REQ-001"],
                    "acceptance": ["AC-001"],
                }
            ],
        }
        state["coverage"] = []
        state["ux_coverage"] = []
        return state

    def lossy_promotion_cases(self):
        return (
            (
                "decision_answer_conflict",
                "decisions",
                {"answer": "Use a conflicting product behavior."},
                ["source_field:reason", "source_field:source", "statement"],
            ),
            (
                "rule_statement_text_conflict",
                "rules",
                {"statement": "Allow duplicate submissions."},
                ["statement"],
            ),
            (
                "screen_requirement_alias_conflict",
                "screens",
                {"requirement_refs": ["REQ-999"]},
                ["requirement_refs"],
            ),
            (
                "acceptance_alias_conflicts",
                "acceptance_criteria",
                {
                    "requirement_refs": ["REQ-999"],
                    "text": "A conflicting acceptance assertion.",
                },
                ["assertion", "requirement_refs"],
            ),
            (
                "task_acceptance_alias_conflict",
                "tasks",
                {"acceptance_refs": ["AC-999"]},
                ["acceptance_refs"],
            ),
            (
                "unconsumed_custom_semantics",
                "goals",
                {"custom_semantics": "This meaning has no V2 destination."},
                ["source_field:custom_semantics"],
            ),
            (
                "unconsumed_optional_user_semantics",
                "users",
                {"cardinality": ""},
                ["source_field:cardinality"],
            ),
            (
                "unconsumed_lifecycle_semantics",
                "goals",
                {"superseded_by": "GOAL-001"},
                ["source_field:superseded_by"],
            ),
        )

    def partial_coverage_state(self, *, empty):
        state = closed_state()
        core_cells = state["coverage"][0]["cells"]
        state_cells = state["ux_coverage"][0]["states"]
        action_cells = state["ux_coverage"][0]["actions"][0]["cells"]
        state["coverage"][0]["cells"] = (
            {} if empty else {"actor": copy.deepcopy(core_cells["actor"])}
        )
        state["ux_coverage"][0]["states"] = (
            {} if empty else {"default": copy.deepcopy(state_cells["default"])}
        )
        state["ux_coverage"][0]["actions"][0]["cells"] = (
            {} if empty else {"entry": copy.deepcopy(action_cells["entry"])}
        )
        return state

    def extra_axis_coverage_state(self):
        state = closed_state()
        state["coverage"][0]["cells"]["legacy_core_axis"] = {
            "status": "COVERED"
        }
        state["ux_coverage"][0]["states"]["legacy_state_axis"] = {
            "status": "N/A",
            "rationale": "The legacy state axis was explicitly not applicable.",
        }
        state["ux_coverage"][0]["actions"][0]["cells"][
            "legacy_action_axis"
        ] = {"status": "OPEN"}
        return state

    def assert_exact_archive_and_gap(
        self, candidate, *, group, source_record, missing_fields
    ):
        source_id = source_record["id"]
        archives = [
            entry
            for entry in candidate["migration"]["legacy_records"]
            if entry["source_id"] == source_id
        ]
        self.assertEqual(len(archives), 1, candidate["migration"]["legacy_records"])
        self.assertEqual(
            archives[0],
            {
                "source_id": source_id,
                "source_group": group,
                "source_record": source_record,
                "source_record_sha256": hashlib.sha256(
                    json.dumps(
                        source_record,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
            },
        )
        source_path = f"/objects/{group}/0"
        gap = self.gap_at(candidate, source_path)
        self.assertEqual(
            gap,
            {
                "source_id": source_id,
                "source_path": source_path,
                "missing_v2_fields": missing_fields,
                "reason_code": "MISSING_V2_SEMANTIC_AUTHORITY",
            },
        )
        expected_key = "gap:" + hashlib.sha256(
            json.dumps(
                gap,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:24]
        self.assertEqual(candidate["migration"]["reconciliation_gaps"][expected_key], gap)

    def assert_exact_absence_gap(self, candidate, *, source_id, source_path):
        gap = self.gap_at(candidate, source_path)
        self.assertEqual(
            gap,
            {
                "source_id": source_id,
                "source_path": source_path,
                "missing_v2_fields": ABSENT_CELL_FIELDS,
                "reason_code": "MISSING_V2_SEMANTIC_AUTHORITY",
            },
        )
        expected_key = "gap:" + hashlib.sha256(
            json.dumps(
                gap,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:24]
        self.assertEqual(candidate["migration"]["reconciliation_gaps"][expected_key], gap)

    def assert_exact_extra_axis_gap(
        self, candidate, *, source_id, source_path, missing_fields
    ):
        gap = self.gap_at(candidate, source_path)
        self.assertEqual(
            gap,
            {
                "source_id": source_id,
                "source_path": source_path,
                "missing_v2_fields": missing_fields,
                "reason_code": "MISSING_V2_SEMANTIC_AUTHORITY",
            },
        )
        expected_key = "gap:" + hashlib.sha256(
            json.dumps(
                gap,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:24]
        self.assertEqual(candidate["migration"]["reconciliation_gaps"][expected_key], gap)

    def assert_extra_axis_candidate(self, candidate):
        expected_open = {
            "status": "OPEN",
            "authority_bindings": [],
            "unknown_refs": [],
            "basis_bindings": [],
            "rationale": None,
        }
        self.assertEqual(
            candidate["coverage"][0]["cells"]["legacy_core_axis"], expected_open
        )
        self.assertEqual(
            candidate["ux_coverage"][0]["states"]["legacy_state_axis"],
            expected_open,
        )
        self.assertEqual(
            candidate["ux_coverage"][0]["actions"][0]["cells"][
                "legacy_action_axis"
            ],
            expected_open,
        )
        self.assertEqual(candidate["objects"]["unknowns"], [])
        self.assertEqual(candidate["migration"]["generated_ids"], [])
        self.assert_exact_extra_axis_gap(
            candidate,
            source_id="REQ-001",
            source_path="/coverage/0/cells/legacy_core_axis",
            missing_fields=["authority_bindings", "axis_inventory"],
        )
        self.assert_exact_extra_axis_gap(
            candidate,
            source_id="SCR-001",
            source_path="/ux_coverage/0/states/legacy_state_axis",
            missing_fields=["axis_inventory", "basis_bindings"],
        )
        self.assert_exact_extra_axis_gap(
            candidate,
            source_id="SCR-001",
            source_path=(
                "/ux_coverage/0/actions/0/cells/legacy_action_axis"
            ),
            missing_fields=["axis_inventory", "unknown_refs"],
        )

    def assert_partial_coverage_candidate(self, candidate, *, empty):
        present_core = set() if empty else {"actor"}
        present_states = set() if empty else {"default"}
        present_actions = set() if empty else {"entry"}
        self.assertEqual(set(candidate["coverage"][0]["cells"]), present_core)
        self.assertEqual(set(candidate["ux_coverage"][0]["states"]), present_states)
        self.assertEqual(
            set(candidate["ux_coverage"][0]["actions"][0]["cells"]),
            present_actions,
        )
        self.assertEqual(candidate["objects"]["unknowns"], [])
        self.assertEqual(candidate["migration"]["generated_ids"], [])
        for axis in sorted(set(CORE_AXES) - present_core):
            self.assert_exact_absence_gap(
                candidate,
                source_id="REQ-001",
                source_path=f"/coverage/0/cells/{axis}",
            )
        for axis in sorted(set(UX_STATE_AXES) - present_states):
            self.assert_exact_absence_gap(
                candidate,
                source_id="SCR-001",
                source_path=f"/ux_coverage/0/states/{axis}",
            )
        for axis in sorted(set(UX_ACTION_AXES) - present_actions):
            self.assert_exact_absence_gap(
                candidate,
                source_id="SCR-001",
                source_path=f"/ux_coverage/0/actions/0/cells/{axis}",
            )

    def test_apply_produces_open_unapproved_v2_candidate(self):
        state = closed_state()
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, _ = self.write_source(directory, state)
            destination = directory / "candidate.json"

            result = self.apply(source, destination)

            self.assertEqual(result.returncode, 0, result.stderr)
            candidate = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(candidate["schema_version"], "0.2.0")
            self.assertEqual(candidate["project"]["definition_status"], "OPEN")
            self.assertEqual(
                candidate["project"]["definition_revision"],
                state["project"]["definition_revision"] + 1,
            )
            self.assertEqual(
                candidate["project"]["bootstrap_mode"],
                "EXISTING_PRODUCT_RECONCILIATION",
            )
            self.assertEqual(candidate["approval"], {"status": "UNAPPROVED"})
            self.assertEqual(candidate["approval_history"], [])
            self.assertEqual(
                candidate["discovery_baseline"], {"status": "NOT_ESTABLISHED"}
            )

    def test_apply_never_modifies_source_bytes(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, source_bytes = self.write_source(directory)

            result = self.apply(source, directory / "candidate.json")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_bytes(), source_bytes)

    def test_apply_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, source_bytes = self.write_source(directory)
            destination = directory / "candidate.json"
            original_destination = b'{"owner":"preexisting"}\n'
            destination.write_bytes(original_destination)

            result = self.apply(source, destination)

            self.assertEqual(result.returncode, 2)
            self.assertIn("destination already exists", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(destination.read_bytes(), original_destination)

    def test_apply_cleans_owned_artifact_after_mid_write_failure(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, source_bytes = self.write_source(directory)
            destination = directory / "candidate.json"

            exit_code, stdout, stderr = self.apply_main_with_file_failure(
                source, destination, "write"
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("simulated mid-write failure", stderr)
            self.assertNotIn("Traceback", stderr)
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertFalse(destination.exists())
            self.assertEqual(list(directory.glob(".candidate.json.*.tmp")), [])

    def test_apply_cleans_owned_artifact_after_flush_failure(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, source_bytes = self.write_source(directory)
            destination = directory / "candidate.json"

            exit_code, stdout, stderr = self.apply_main_with_file_failure(
                source, destination, "flush"
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("simulated flush failure", stderr)
            self.assertNotIn("Traceback", stderr)
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertFalse(destination.exists())
            self.assertEqual(list(directory.glob(".candidate.json.*.tmp")), [])

    def test_publish_race_preserves_external_destination_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, source_bytes = self.write_source(directory)
            destination = directory / "candidate.json"
            external_bytes = b'{"owner":"external-race-winner"}\n'

            def external_winner(_source, target):
                Path(target).write_bytes(external_bytes)
                raise FileExistsError("simulated publish race")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                mock.patch.object(os, "link", side_effect=external_winner),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = migrate_state.main(
                    ["--apply", str(source), "--output", str(destination)]
                )

            self.assertEqual(exit_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("destination already exists", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(destination.read_bytes(), external_bytes)
            self.assertEqual(list(directory.glob(".candidate.json.*.tmp")), [])

    def test_apply_is_byte_deterministic_for_same_source(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, _ = self.write_source(directory)
            first_destination = directory / "candidate-one.json"
            second_destination = directory / "candidate-two.json"

            first = self.apply(source, first_destination)
            second = self.apply(source, second_destination)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first_destination.read_bytes(), second_destination.read_bytes())
            self.assertEqual(first.stdout, second.stdout)

    def test_apply_preserves_every_legacy_stable_id(self):
        state = closed_state()
        expected_ids = {
            record["id"]
            for records in state["objects"].values()
            for record in records
        }
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, _ = self.write_source(directory, state)
            destination = directory / "candidate.json"

            result = self.apply(source, destination)

            self.assertEqual(result.returncode, 0, result.stderr)
            candidate = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(set(candidate["migration"]["preserved_ids"]), expected_ids)
            promoted_ids = {
                record["id"]
                for records in candidate["objects"].values()
                for record in records
            }
            archived_ids = {
                record["source_id"]
                for record in candidate["migration"]["legacy_records"]
            }
            self.assertEqual(promoted_ids | archived_ids, expected_ids)
            self.assertEqual(promoted_ids & archived_ids, set())

    def test_apply_does_not_copy_legacy_approval_as_v2_approval(self):
        state = closed_state()
        legacy_approval = copy.deepcopy(state["project"]["approval"])
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, _ = self.write_source(directory, state)
            destination = directory / "candidate.json"

            result = self.apply(source, destination)

            self.assertEqual(result.returncode, 0, result.stderr)
            candidate = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(candidate["approval"], {"status": "UNAPPROVED"})
            self.assertEqual(candidate["approval_history"], [])
            self.assertNotEqual(candidate["approval"], legacy_approval)
            self.assertNotIn("approved_at", candidate["approval"])
            self.assertNotIn("migrated_at", candidate)
            self.assertNotIn("migrated_at", candidate["migration"])

    def test_api_receipt_hashes_the_completed_candidate_canonically(self):
        self.assertTrue(hasattr(migration_v2, "migrate_state_v020"))

        candidate, receipt = migration_v2.migrate_state_v020(closed_state())

        expected_digest = hashlib.sha256(
            json.dumps(
                candidate,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(receipt["candidate_state_sha256"], expected_digest)
        self.assertEqual(receipt["migration_version"], "0.2.0-m6.1")
        self.assertNotIn("candidate_state_sha256", candidate["migration"])
        self.assertTrue(
            {"created_at", "generated_at", "migrated_at", "timestamp"}.isdisjoint(
                receipt
            )
        )

    def test_verify_migration_result_rejects_candidate_tampering(self):
        self.assertTrue(hasattr(migration_v2, "migrate_state_v020"))
        self.assertTrue(hasattr(migration_v2, "verify_migration_result"))
        state = closed_state()
        candidate, receipt = migration_v2.migrate_state_v020(state)
        candidate["project"]["definition_status"] = "CLOSED"

        errors = migration_v2.verify_migration_result(state, candidate, receipt)

        self.assertIn("candidate_invariant_mismatch", {error["code"] for error in errors})
        self.assertIn("candidate_digest_mismatch", {error["code"] for error in errors})

    def test_legacy_covered_cell_becomes_open_binding_reconciliation(self):
        state = closed_state()
        state["coverage"][0]["cells"] = {"security": {"status": "COVERED"}}

        candidate, _ = self.candidate_for(state)

        self.assertEqual(
            candidate["coverage"],
            [
                {
                    "feature_id": "REQ-001",
                    "cells": {
                        "security": {
                            "status": "OPEN",
                            "authority_bindings": [],
                            "unknown_refs": [],
                            "basis_bindings": [],
                            "rationale": None,
                        }
                    },
                }
            ],
        )
        gap = self.gap_at(candidate, "/coverage/0/cells/security")
        self.assertEqual(gap["source_id"], "REQ-001")
        self.assertEqual(gap["missing_v2_fields"], ["authority_bindings"])
        self.assertEqual(gap["reason_code"], "MISSING_V2_SEMANTIC_AUTHORITY")

    def test_legacy_na_cell_becomes_open_basis_reconciliation(self):
        state = closed_state()
        state["ux_coverage"][0]["states"] = {
            "offline": {"status": "N/A", "rationale": "Legacy local-only basis."}
        }
        state["ux_coverage"][0]["actions"] = [
            {"key": "submit", "cells": {"failure": {"status": "OPEN"}}}
        ]

        candidate, _ = self.candidate_for(state)

        self.assertEqual(len(candidate["ux_coverage"]), 1)
        offline = candidate["ux_coverage"][0]["states"]["offline"]
        self.assertEqual(offline["status"], "OPEN")
        self.assertEqual(offline["authority_bindings"], [])
        self.assertEqual(offline["basis_bindings"], [])
        self.assertEqual(offline["unknown_refs"], [])
        self.assertIsNone(offline["rationale"])
        gap = self.gap_at(candidate, "/ux_coverage/0/states/offline")
        self.assertEqual(gap["source_id"], "SCR-001")
        self.assertEqual(gap["missing_v2_fields"], ["basis_bindings"])

    def test_legacy_material_boolean_never_manufactures_full_materiality(self):
        state = closed_state()
        state["objects"]["requirements"][0]["material"] = True

        candidate, _ = self.candidate_for(state)

        self.assertEqual(candidate["objects"]["requirements"], [])
        archived = {
            entry["source_id"]: entry
            for entry in candidate["migration"]["legacy_records"]
        }
        self.assertIs(archived["REQ-001"]["source_record"]["material"], True)
        self.assertNotIn("materiality", archived["REQ-001"]["source_record"])
        gap = self.gap_at(candidate, "/objects/requirements/0")
        self.assertIn("materiality", gap["missing_v2_fields"])

    def test_six_grill_topology_domains_begin_open_without_v2_evidence(self):
        candidate, _ = self.candidate_for()

        self.assertEqual(candidate["surface_manifest"]["grill_profile"], {})
        self.assertEqual(candidate["objects"]["unknowns"], [])
        self.assertIsInstance(candidate["migration"]["reconciliation_gaps"], dict)
        topology_gaps = {
            gap["source_path"].rsplit("/", 1)[-1]: gap
            for gap in candidate["migration"]["reconciliation_gaps"].values()
            if gap["source_path"].startswith("/surface_manifest/grill_profile/")
        }
        self.assertEqual(set(topology_gaps), GRILL_DOMAINS)
        for domain, gap in topology_gaps.items():
            with self.subTest(domain=domain):
                self.assertIsNone(gap["source_id"])
                self.assertEqual(
                    gap["missing_v2_fields"],
                    ["basis_refs", "rationale", "status", "surface_refs", "unknown_refs"],
                )

    def test_generated_unknown_ids_are_deterministic_and_after_existing_max(self):
        state = closed_state()
        state["objects"]["unknowns"] = [
            {"id": "UNK-099", "status": "OPEN", "material": True}
        ]

        first_candidate, first_receipt = self.candidate_for(state)
        second_candidate, second_receipt = self.candidate_for(state)

        self.assertEqual(first_candidate, second_candidate)
        self.assertEqual(first_receipt, second_receipt)
        self.assertIn("UNK-099", first_candidate["migration"]["preserved_ids"])
        self.assertEqual(first_candidate["migration"]["generated_ids"], [])
        self.assertEqual(first_candidate["objects"]["unknowns"], [])

    def test_migration_unknown_origin_preserves_exact_source_path(self):
        state = closed_state()
        state["coverage"][0]["cells"] = {
            "security~/role": {"status": "COVERED"}
        }

        candidate, _ = self.candidate_for(state)

        gap = self.gap_at(candidate, "/coverage/0/cells/security~0~1role")
        self.assertEqual(gap["source_id"], "REQ-001")
        self.assertEqual(candidate["objects"]["unknowns"], [])
        self.assertEqual(candidate["migration"]["generated_ids"], [])

    def test_api_records_every_missing_core_and_ux_axis_without_fabrication(self):
        for empty in (False, True):
            with self.subTest(empty=empty):
                state = self.partial_coverage_state(empty=empty)
                self.assertEqual(validate_legacy_state(state), [])

                candidate, receipt = self.candidate_for(state)

                self.assert_partial_coverage_candidate(candidate, empty=empty)
                self.assertEqual(
                    migration_v2.verify_migration_result(state, candidate, receipt), []
                )

    def test_cli_applies_partial_and_empty_coverage_deterministically(self):
        for empty in (False, True):
            with self.subTest(empty=empty):
                state = self.partial_coverage_state(empty=empty)
                self.assertEqual(validate_legacy_state(state), [])
                with tempfile.TemporaryDirectory() as raw_directory:
                    directory = Path(raw_directory)
                    source, source_bytes = self.write_source(directory, state)
                    first_destination = directory / "first-candidate.json"
                    second_destination = directory / "second-candidate.json"

                    first = self.apply(source, first_destination)
                    second = self.apply(source, second_destination)

                    self.assertEqual(first.returncode, 0, first.stderr)
                    self.assertEqual(second.returncode, 0, second.stderr)
                    self.assertEqual(first.stdout, second.stdout)
                    self.assertEqual(
                        first_destination.read_bytes(), second_destination.read_bytes()
                    )
                    self.assertEqual(source.read_bytes(), source_bytes)
                    candidate = json.loads(first_destination.read_text(encoding="utf-8"))
                    self.assert_partial_coverage_candidate(candidate, empty=empty)

    def test_api_retains_and_accounts_for_every_extra_legacy_axis(self):
        state = self.extra_axis_coverage_state()
        self.assertEqual(validate_legacy_state(state), [])

        candidate, receipt = self.candidate_for(state)

        self.assert_extra_axis_candidate(candidate)
        self.assertEqual(
            migration_v2.verify_migration_result(state, candidate, receipt), []
        )

    def test_cli_applies_extra_legacy_axes_deterministically(self):
        state = self.extra_axis_coverage_state()
        self.assertEqual(validate_legacy_state(state), [])
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, source_bytes = self.write_source(directory, state)
            first_destination = directory / "first-candidate.json"
            second_destination = directory / "second-candidate.json"

            first = self.apply(source, first_destination)
            second = self.apply(source, second_destination)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(first_destination.read_bytes(), second_destination.read_bytes())
            self.assertEqual(source.read_bytes(), source_bytes)
            candidate = json.loads(first_destination.read_text(encoding="utf-8"))
            self.assert_extra_axis_candidate(candidate)

    def test_api_archives_conflicting_aliases_and_unconsumed_source_fields(self):
        for label, group, updates, missing_fields in self.lossy_promotion_cases():
            with self.subTest(label=label):
                state = self.explicit_semantics_state()
                source_record = state["objects"][group][0]
                source_record.update(copy.deepcopy(updates))
                source_record = copy.deepcopy(source_record)
                self.assertEqual(validate_legacy_state(state), [])

                candidate, receipt = self.candidate_for(state)

                self.assertNotIn(
                    source_record["id"],
                    {
                        record["id"]
                        for record in candidate["objects"][group]
                    },
                )
                self.assert_exact_archive_and_gap(
                    candidate,
                    group=group,
                    source_record=source_record,
                    missing_fields=missing_fields,
                )
                self.assertEqual(
                    migration_v2.verify_migration_result(state, candidate, receipt), []
                )

    def test_cli_archives_lossy_records_deterministically_without_source_mutation(self):
        for label, group, updates, missing_fields in self.lossy_promotion_cases():
            with self.subTest(label=label):
                state = self.explicit_semantics_state()
                source_record = state["objects"][group][0]
                source_record.update(copy.deepcopy(updates))
                source_record = copy.deepcopy(source_record)
                self.assertEqual(validate_legacy_state(state), [])
                with tempfile.TemporaryDirectory() as raw_directory:
                    directory = Path(raw_directory)
                    source, source_bytes = self.write_source(directory, state)
                    first_destination = directory / "first-candidate.json"
                    second_destination = directory / "second-candidate.json"

                    first = self.apply(source, first_destination)
                    second = self.apply(source, second_destination)

                    self.assertEqual(first.returncode, 0, first.stderr)
                    self.assertEqual(second.returncode, 0, second.stderr)
                    self.assertEqual(first.stdout, second.stdout)
                    self.assertEqual(
                        first_destination.read_bytes(), second_destination.read_bytes()
                    )
                    self.assertEqual(source.read_bytes(), source_bytes)
                    candidate = json.loads(first_destination.read_text(encoding="utf-8"))
                    self.assert_exact_archive_and_gap(
                        candidate,
                        group=group,
                        source_record=source_record,
                        missing_fields=missing_fields,
                    )

    def test_identical_source_aliases_remain_losslessly_promotable(self):
        cases = (
            ("rules", {"statement": "Reject duplicate submissions."}),
            ("screens", {"requirement_refs": ["REQ-001"]}),
            (
                "acceptance_criteria",
                {
                    "requirement_refs": ["REQ-001"],
                    "text": "A valid submission is stored exactly once.",
                },
            ),
            ("tasks", {"acceptance_refs": ["AC-001"]}),
        )
        for group, updates in cases:
            with self.subTest(group=group):
                state = self.explicit_semantics_state()
                state["objects"][group][0].update(copy.deepcopy(updates))
                self.assertEqual(validate_legacy_state(state), [])

                candidate, receipt = self.candidate_for(state)

                source_id = state["objects"][group][0]["id"]
                self.assertIn(
                    source_id,
                    {record["id"] for record in candidate["objects"][group]},
                )
                self.assertEqual(
                    migration_v2.verify_migration_result(state, candidate, receipt), []
                )

    def test_explicit_legacy_semantics_promote_only_when_lossless(self):
        state = self.explicit_semantics_state()
        expected_ids = {
            record["id"]
            for records in state["objects"].values()
            for record in records
        }
        archived_ids = {"UNK-001", "DEC-001"}
        promoted_ids = expected_ids - archived_ids

        candidate, receipt = self.candidate_for(state)

        promoted = {
            record["id"]: record
            for records in candidate["objects"].values()
            for record in records
        }
        self.assertEqual(set(promoted), promoted_ids)
        self.assertEqual(candidate["migration"]["preserved_ids"], sorted(expected_ids))
        self.assertEqual(candidate["migration"]["promoted_ids"], sorted(promoted_ids))
        self.assertEqual(candidate["migration"]["generated_ids"], [])
        self.assertEqual(receipt["archived_ids"], sorted(archived_ids))
        self.assert_exact_archive_and_gap(
            candidate,
            group="unknowns",
            source_record=state["objects"]["unknowns"][0],
            missing_fields=["source_field:resolution", "source_field:source"],
        )
        self.assert_exact_archive_and_gap(
            candidate,
            group="decisions",
            source_record=state["objects"]["decisions"][0],
            missing_fields=["source_field:reason", "source_field:source"],
        )
        self.assertEqual(promoted["GOAL-001"]["statement"], "Ship the workflow.")
        self.assertEqual(promoted["USR-001"]["actor_kind"], "Operator")
        self.assertEqual(
            promoted["USR-001"]["description"],
            "role: Operator; cardinality: one per workspace; identity: workspace account",
        )
        self.assertEqual(promoted["REQ-001"]["statement"], "Persist submitted work.")
        self.assertEqual(promoted["RULE-001"]["statement"], "Reject duplicate submissions.")
        self.assertEqual(promoted["STATE-001"]["state_name"], "Submitted")
        self.assertEqual(promoted["AC-001"]["requirement_refs"], ["REQ-001"])
        self.assertEqual(promoted["TASK-001"]["acceptance_refs"], ["AC-001"])
        self.assertEqual(
            migration_v2.verify_migration_result(state, candidate, receipt), []
        )

    def test_migration_metadata_and_receipt_have_exact_deterministic_schema(self):
        state = self.explicit_semantics_state()
        candidate, receipt = self.candidate_for(state)
        source_digest = hashlib.sha256(
            json.dumps(
                state, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        expected_plan = {
            "schema_version": "joewrks.state-migration-plan/1.0",
            "status": "FOUNDATION_PLAN_ONLY",
            "from_schema": "0.1.2.1",
            "to_schema": "0.2.0",
            "migration_version": "0.2.0-foundation.1",
            "source_digest": source_digest,
            "preserved_ids": sorted(
                record["id"]
                for records in state["objects"].values()
                for record in records
            ),
            "reconciliation_sites": [],
        }
        plan_digest = hashlib.sha256(
            json.dumps(
                expected_plan,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        approval_digest = hashlib.sha256(
            json.dumps(
                state["project"]["approval"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        self.assertEqual(set(candidate["migration"]), MIGRATION_FIELDS)
        self.assertEqual(candidate["migration"]["source_digest"], source_digest)
        self.assertEqual(candidate["migration"]["plan_digest"], plan_digest)
        self.assertEqual(
            candidate["migration"]["source_legacy_approval_digest"], approval_digest
        )
        self.assertEqual(candidate["migration"]["source_legacy_status"], "CLOSED")
        self.assertEqual(
            set(receipt),
            {
                "schema_version",
                "migration_version",
                "source_digest",
                "plan_digest",
                "candidate_state_sha256",
                "preserved_ids",
                "promoted_ids",
                "generated_ids",
                "archived_ids",
                "reconciliation_gap_count",
            },
        )

    def test_structural_errors_are_absent_and_semantic_errors_are_gap_attributed(self):
        candidate, receipt = self.candidate_for()

        semantic_errors = validate_state_v2(candidate)
        integrity_errors = migration_v2.verify_migration_result(
            closed_state(), candidate, receipt
        )

        self.assertTrue(semantic_errors)
        self.assertNotIn("schema_error", {error["code"] for error in semantic_errors})
        self.assertEqual(integrity_errors, [])
        self.assertEqual(
            {error["code"] for error in semantic_errors},
            {
                "invalid_grill_profile",
                "core_coverage_target_mismatch",
                "open_coverage_without_unknown",
                "ux_open_without_unknown",
                "invalid_ux_coverage_row",
                "screen_action_inventory_mismatch",
                "missing_authority_graph_reference",
            },
        )
        gap_values = list(candidate["migration"]["reconciliation_gaps"].values())
        gap_paths = {gap["source_path"] for gap in gap_values}
        for error in semantic_errors:
            path = error["path"]
            if error["code"] == "invalid_grill_profile":
                attributed = sum(
                    gap_path.startswith("/surface_manifest/grill_profile/")
                    for gap_path in gap_paths
                ) == 6
            elif error["code"] == "open_coverage_without_unknown":
                match = re.fullmatch(r"coverage\[(\d+)\]\.cells\.(.+)", path)
                self.assertIsNotNone(match)
                attributed = f"/coverage/{match[1]}/cells/{match[2]}" in gap_paths
            elif error["code"] == "ux_open_without_unknown":
                state_match = re.fullmatch(
                    r"ux_coverage\[(\d+)\]\.states\.(.+)", path
                )
                action_match = re.fullmatch(
                    r"ux_coverage\[(\d+)\]\.actions\[(\d+)\]\.cells\.(.+)",
                    path,
                )
                attributed = bool(
                    state_match
                    and f"/ux_coverage/{state_match[1]}/states/{state_match[2]}"
                    in gap_paths
                ) or bool(
                    action_match
                    and (
                        f"/ux_coverage/{action_match[1]}/actions/{action_match[2]}"
                        f"/cells/{action_match[3]}"
                    )
                    in gap_paths
                )
            elif error["code"] in {
                "core_coverage_target_mismatch",
                "missing_authority_graph_reference",
            }:
                relevant_ids = {"REQ-001", "AC-001"}
                attributed = any(
                    gap["source_id"] in relevant_ids
                    and gap["source_path"].startswith("/objects/")
                    for gap in gap_values
                )
            else:
                attributed = any(
                    gap["source_id"] == "SCR-001"
                    and gap["source_path"].startswith("/objects/screens/")
                    for gap in gap_values
                )
            self.assertTrue(attributed, error)
        self.assertEqual(
            candidate["migration"]["reconciliation_gap_count"],
            len(candidate["migration"]["reconciliation_gaps"]),
        )

    def test_migration_candidate_cannot_claim_closure_approval_or_downstream_contract(self):
        candidate, _ = self.candidate_for()

        closure = evaluate_closure_v2(candidate)

        self.assertFalse(closure["closed"])
        self.assertEqual(candidate["approval"], {"status": "UNAPPROVED"})
        self.assertEqual(candidate["approval_history"], [])
        self.assertNotIn("approved_at", candidate["approval"])
        self.assertNotIn("migrated_at", candidate["migration"])
        self.assertEqual(
            set(candidate["project"]["closure_contract"]),
            {"level", "product_binding_contract", "ux_binding_contract"},
        )
        self.assertNotIn("downstream_contract", candidate)

    def test_v2_validator_rejects_malformed_migrated_metadata_but_accepts_native(self):
        candidate, _ = self.candidate_for()
        del candidate["migration"]["source_digest"]

        migrated_codes = {error["code"] for error in validate_state_v2(candidate)}

        self.assertIn("schema_error", migrated_codes)
        self.assertNotIn("schema_error", {error["code"] for error in validate_state_v2(foundation_state())})

    def test_verify_rejects_a_missing_reconciliation_gap_after_receipt_rehash(self):
        state = closed_state()
        candidate, receipt = self.candidate_for(state)
        gaps = candidate["migration"]["reconciliation_gaps"]
        self.assertIsInstance(gaps, dict)
        self.assertTrue(gaps)
        del gaps[next(iter(gaps))]
        candidate["migration"]["reconciliation_gap_count"] = len(gaps)
        receipt["reconciliation_gap_count"] = len(gaps)
        receipt["candidate_state_sha256"] = hashlib.sha256(
            json.dumps(
                candidate,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        errors = migration_v2.verify_migration_result(state, candidate, receipt)

        self.assertIn("reconciliation_gap_mismatch", {error["code"] for error in errors})

    def test_migrated_candidate_satisfies_the_json_structural_schema(self):
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if powershell is None:
            self.skipTest("PowerShell Test-Json is unavailable")
        fixtures = (closed_state(), self.explicit_semantics_state())
        for position, state in enumerate(fixtures):
            with self.subTest(position=position):
                candidate, _ = self.candidate_for(state)
                with tempfile.TemporaryDirectory() as raw_directory:
                    candidate_path = Path(raw_directory) / "candidate.json"
                    candidate_path.write_text(
                        json.dumps(candidate, ensure_ascii=False), encoding="utf-8"
                    )
                    quoted_candidate = str(candidate_path).replace("'", "''")
                    quoted_schema = str(STATE_SCHEMA).replace("'", "''")
                    result = subprocess.run(
                        [
                            powershell,
                            "-NoProfile",
                            "-NonInteractive",
                            "-Command",
                            (
                                "$payload = Get-Content -Raw -LiteralPath "
                                f"'{quoted_candidate}'; if (Test-Json -Json $payload "
                                f"-SchemaFile '{quoted_schema}' -ErrorAction Stop) "
                                "{ exit 0 }; exit 1"
                            ),
                        ],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        check=False,
                    )

                self.assertEqual(result.returncode, 0, result.stderr)

    def test_verify_rejects_structural_defect_after_receipt_rehash(self):
        state = self.explicit_semantics_state()
        candidate, receipt = self.candidate_for(state)
        candidate["objects"]["goals"][0]["unexpected"] = True
        receipt["candidate_state_sha256"] = hashlib.sha256(
            json.dumps(
                candidate,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        errors = migration_v2.verify_migration_result(state, candidate, receipt)

        self.assertIn("structural_schema_error", {error["code"] for error in errors})

    def test_verify_rejects_promoted_reference_without_reconciliation_gap(self):
        state = self.explicit_semantics_state()
        state["objects"]["rules"][0]["applies_to"] = ["REQ-999"]
        candidate, receipt = self.candidate_for(state)

        errors = migration_v2.verify_migration_result(state, candidate, receipt)

        self.assertIn("unattributed_semantic_error", {error["code"] for error in errors})

    def test_migration_metadata_is_excluded_from_semantic_authority(self):
        candidate, _ = self.candidate_for()
        mutated = copy.deepcopy(candidate)
        mutated["migration"]["source_legacy_status"] = "OPEN"
        mutated["migration"]["legacy_records"][0]["source_record"]["status"] = "STALE"

        self.assertEqual(definition_digest(candidate), definition_digest(mutated))
        self.assertEqual(
            compute_approval_manifest(candidate), compute_approval_manifest(mutated)
        )
        authority_index = canonical_record_index(candidate)
        archived_ids = {
            entry["source_id"]
            for entry in candidate["migration"]["legacy_records"]
            if entry["source_id"] is not None
        }
        self.assertTrue(archived_ids.isdisjoint(authority_index))
        self.assertTrue(
            set(candidate["migration"]["reconciliation_gaps"]).isdisjoint(
                authority_index
            )
        )
        identities = binding_contract_identity()
        self.assertEqual(
            candidate["project"]["closure_contract"],
            {
                "level": "SEMANTIC_CLOSURE",
                "product_binding_contract": identities["product"],
                "ux_binding_contract": identities["ux"],
            },
        )

    def test_apply_writes_nothing_when_integrity_verification_fails(self):
        state = self.explicit_semantics_state()
        state["objects"]["rules"][0]["applies_to"] = ["REQ-999"]
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source, source_bytes = self.write_source(directory, state)
            destination = directory / "candidate.json"

            result = self.apply(source, destination)

            self.assertEqual(result.returncode, 1, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["error"]["code"], "MIGRATION_RESULT_INVALID")
            self.assertFalse(destination.exists())
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertNotIn("Traceback", result.stderr)

    def test_malformed_explicit_unknown_shape_is_archived_not_promoted(self):
        state = self.explicit_semantics_state()
        state["objects"]["unknowns"][0]["options"] = [{}]

        candidate, receipt = self.candidate_for(state)

        self.assertEqual(candidate["objects"]["unknowns"], [])
        archived_ids = {
            entry["source_id"] for entry in candidate["migration"]["legacy_records"]
        }
        self.assertIn("UNK-001", archived_ids)
        gap = self.gap_at(candidate, "/objects/unknowns/0")
        self.assertIn("options", gap["missing_v2_fields"])
        self.assertEqual(migration_v2.verify_migration_result(state, candidate, receipt), [])

    def test_malformed_explicit_decision_shape_is_archived_not_promoted(self):
        state = self.explicit_semantics_state()
        state["objects"]["decisions"][0]["accepted_recommendation"] = {}

        candidate, receipt = self.candidate_for(state)

        self.assertEqual(candidate["objects"]["decisions"], [])
        archived_ids = {
            entry["source_id"] for entry in candidate["migration"]["legacy_records"]
        }
        self.assertIn("DEC-001", archived_ids)
        gap = self.gap_at(candidate, "/objects/decisions/0")
        self.assertIn("accepted_recommendation", gap["missing_v2_fields"])
        self.assertEqual(migration_v2.verify_migration_result(state, candidate, receipt), [])

    def test_verify_rejects_semantic_tampering_after_receipt_rehash(self):
        state = self.explicit_semantics_state()
        candidate, receipt = self.candidate_for(state)
        candidate["objects"]["goals"][0]["statement"] = "Tampered meaning."
        receipt["candidate_state_sha256"] = hashlib.sha256(
            json.dumps(
                candidate,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        errors = migration_v2.verify_migration_result(state, candidate, receipt)

        self.assertIn("candidate_derivation_mismatch", {error["code"] for error in errors})

    def test_verify_rejects_receipt_field_tampering(self):
        state = self.explicit_semantics_state()
        candidate, receipt = self.candidate_for(state)
        receipt["promoted_ids"] = []

        errors = migration_v2.verify_migration_result(state, candidate, receipt)

        self.assertIn("receipt_mismatch", {error["code"] for error in errors})


if __name__ == "__main__":
    unittest.main()
