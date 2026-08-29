import json
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.v020_support import (
        decision_record,
        foundation_state,
        materiality,
        unknown_record,
    )
except ModuleNotFoundError:
    from v020_support import decision_record, foundation_state, materiality, unknown_record


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
REFERENCE = ROOT / "skills" / "joewrks-product-definition" / "references" / "state-contract-v0.2.0.md"
DISCOVERY_CONTRACT = ROOT / "skills" / "joewrks-product-definition" / "references" / "discovery-contract-v0.2.0.md"
GRILL_CONTRACT = ROOT / "skills" / "joewrks-product-definition" / "references" / "grill-contract-v0.2.0.md"
TEMPLATE = ROOT / "skills" / "joewrks-product-definition" / "templates" / "state-v0.2.0.example.json"

sys.path.insert(0, str(SCRIPTS))
import state_validation_v2
from authority_binding_v2 import make_authority_binding
from grill_v2 import CORE_GRILL_AXES
from state_validation_v2 import evaluate_closure_v2, validate_state_v2


def resolved_decision_source():
    record = unknown_record(
        "UNK-002",
        status="RESOLVED",
        classification="NON_MATERIAL",
        decision_authority="USER_DECISION_REQUIRED",
    )
    record.update({
        "resolved_by": ["DEC-001"],
        "resolution_mode": "USER_DECISION",
        "resolution_summary": "The user selected the canonical format.",
    })
    return record


def not_applicable_cell(state):
    return {
        "status": "N/A", "authority_bindings": [], "unknown_refs": [],
        "basis_bindings": [make_authority_binding(state, "EVD-900", "/claim")],
        "rationale": "The fixture has no applicable behavior for this axis.",
    }


def screen_ux_coverage(state):
    return [{
        "screen_id": "SCR-001",
        "states": {axis: not_applicable_cell(state) for axis in (
            "default", "loading", "empty", "partial", "success", "error", "disabled",
            "permission_denied", "unauthenticated", "offline", "timeout", "retrying",
            "submitting", "completed", "cancelled", "expired",
        )},
        "actions": [],
    }]


VALID_RECORDS = {
    "goals": {"id": "GOAL-001", "status": "CURRENT", "statement": "Ship the product"},
    "users": {"id": "USR-001", "status": "CURRENT", "description": "Primary user", "actor_kind": "PERSON"},
    "requirements": {
        "id": "REQ-001", "status": "CURRENT", "statement": "Save work", "scope": "CORE",
        "ui_required": True, "materiality": materiality(),
    },
    "unknowns": unknown_record(
        classification="NON_MATERIAL", decision_authority="AGENT_AUTONOMOUS",
    ),
    "decisions": decision_record(
        source_unknown_refs=["UNK-002"], classification="NON_MATERIAL",
    ),
    "rules": {"id": "RULE-001", "status": "CURRENT", "statement": "Persist changes", "applies_to": ["REQ-001"]},
    "flows": {
        "id": "FLOW-001", "status": "CURRENT", "goal_refs": ["GOAL-001"], "entry": "Open editor",
        "preconditions": ["Signed in"], "paths": ["Save"], "outcomes": ["Work persisted"],
    },
    "screens": {
        "id": "SCR-001", "status": "CURRENT", "purpose": "Edit work", "requirement_refs": ["REQ-001"],
        "interaction_mode": "INTERACTIVE", "major_actions": [],
    },
    "states": {
        "id": "STATE-001", "status": "CURRENT", "owner_refs": ["REQ-001"], "state_name": "SAVED",
        "conditions": ["Persistence succeeded"],
    },
    "data": {"id": "DATA-001", "status": "CURRENT", "name": "Document", "purpose": "Store work", "ownership": "USER"},
    "integrations": {"id": "INT-001", "status": "CURRENT", "name": "Storage", "purpose": "Persist work"},
    "acceptance_criteria": {
        "id": "AC-001", "status": "CURRENT", "requirement_refs": ["REQ-001"], "assertion": "Saved work reloads",
    },
    "tasks": {
        "id": "TASK-001", "status": "CURRENT", "implements": ["REQ-001"], "acceptance_refs": ["AC-001"],
    },
}


class StateV020FoundationTest(unittest.TestCase):
    def invoke(self, kind, state):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / f"validate_{kind}.py"), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        return result.returncode, json.loads(result.stdout)

    def test_schema_defines_the_v020_foundation_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(schema["properties"]["schema_version"]["const"], "0.2.0")
        self.assertEqual(
            set(schema["required"]),
            {
                "schema_version", "project", "migration", "evidence", "surface_manifest",
                "contradictions", "objects", "coverage", "ux_coverage", "grill_coverage",
                "discovery_baseline", "approval", "approval_history",
            },
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["properties"]["project"]["additionalProperties"])

    def test_v020_reference_and_native_example_define_the_m1_boundary(self):
        reference = REFERENCE.read_text(encoding="utf-8")
        template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

        self.assertEqual(template["schema_version"], "0.2.0")
        self.assertEqual(template["project"]["definition_status"], "OPEN")
        self.assertEqual(template["project"]["bootstrap_mode"], "NEW_PRODUCT")
        self.assertEqual(template["approval"]["status"], "UNAPPROVED")
        self.assertEqual(template["migration"]["mode"], "NATIVE")
        self.assertEqual(template["discovery_baseline"]["status"], "NOT_ESTABLISHED")
        self.assertEqual(validate_state_v2(template), [])

        closure = evaluate_closure_v2(template)
        self.assertFalse(closure["closed"])
        self.assertIsNone(closure["definition_digest"])
        self.assertEqual(closure["metrics"]["semantic_closure_not_implemented"], 1)

        for token in (
            "LEGACY_CLOSURE",
            "SEMANTIC_CLOSURE",
            "FOUNDATION_PLAN_ONLY",
            "SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_discovery_contract_defines_the_m2_authority_boundary(self):
        self.assertTrue(DISCOVERY_CONTRACT.is_file())

        state_contract = REFERENCE.read_text(encoding="utf-8")
        discovery_contract = DISCOVERY_CONTRACT.read_text(encoding="utf-8")

        self.assertIn("[M2 discovery authority contract](discovery-contract-v0.2.0.md)", state_contract)
        for marker in (
            "DISCOVER_AUTHORITY_IMPLEMENTED_M2",
            "OBSERVED_IMPLEMENTATION_IS_NOT_INTENT",
            "UNKNOWN_UNKNOWN_EXHAUSTIVENESS_NOT_CLAIMED",
            "ACTIVE_GRILL_PACKS_NOT_IMPLEMENTED_IN_M2",
            "SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M2",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, discovery_contract)

        self.assertIn("historical for M2", discovery_contract)
        self.assertIn("grill-contract-v0.2.0.md", discovery_contract)

    def test_grill_contract_defines_the_exact_m3_boundary_and_policy(self):
        self.assertTrue(GRILL_CONTRACT.is_file())
        state_contract = REFERENCE.read_text(encoding="utf-8")
        grill_contract = GRILL_CONTRACT.read_text(encoding="utf-8")

        self.assertIn("[M3 Grill Engine contract](grill-contract-v0.2.0.md)", state_contract)
        for marker in (
            "GRILL_ENGINE_IMPLEMENTED_M3",
            "INTERNALLY_EXHAUSTIVE_EXTERNALLY_SELECTIVE",
            "MATERIALITY_CLASSIFICATION_ENFORCED",
            "NO_SILENT_MATERIAL_AGENT_DECISIONS",
            "ACTIVE_GRILL_PACKS_IMPLEMENTED_M3",
            "UNKNOWN_UNKNOWN_EXHAUSTIVENESS_NOT_CLAIMED",
            "SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M3",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, grill_contract)

        self.assertIn("regardless of `user_visible`", grill_contract)
        self.assertIn("`user_visible` is auditable metadata only", grill_contract)
        self.assertIn("one highest-leverage user question", grill_contract)
        self.assertIn("Pack identity, version, and digest", grill_contract)

        metric_definitions = (
            "`open_material_unknowns` counts each `OPEN` unknown once when its Materiality recomputes to `MATERIAL`.",
            "`missing_required_user_decisions` counts each `OPEN` unknown once when deterministic `derive_decision_authority` produces `USER_CONFIRMATION` or `USER_DECISION_REQUIRED`; the stored declared authority is not trusted.",
            "`unresolved_unknown_provenance` counts each `RESOLVED` unknown once when it lacks a supported resolution mode and meaningful summary, uses `MIGRATION_RECONCILIATION` (which remains a gap), or lacks the qualifying evidence, current matching decision, or external constraint authority required by its declared mode.",
            "`invalid_resolution_authority` counts each affected unknown or decision once when its resolution mode or declared decision authority conflicts with deterministic policy, even when multiple policy findings overlap.",
            "`unassessed_materiality` counts each Materiality-bearing canonical requirement, unknown, decision, surface, or contradiction record once when its Materiality shape or stored classification is invalid.",
            "`unauthorized_agent_decisions` counts each agent decision once when it does not use `AGENT_NON_MATERIAL_DEFAULT` over source unknowns that recompute to `NON_MATERIAL` and declare the matching `AGENT_AUTONOMOUS` resolution authority. It does not rerun live deterministic authority derivation for `RESOLVED` sources; Task 3 live derivation applies only to `OPEN` and `BLOCKED` unknowns.",
            "`active_grill_pack_gaps` counts each invalid or `OPEN` topology-profile cell and each missing, duplicate, identity-mismatched, or axis-inventory-mismatched required Core or specialist coverage row.",
            "`unresolved_pack_axes` counts each `OPEN` Core or activated specialist axis independently of activation-inventory completeness and other violations.",
            "`umbrella_unknown_compression` counts each independent `OPEN` specialist axis that lacks exactly one unique `OPEN` unknown with the exact matching target, pack, and axis origin.",
            "`pack_materiality_floor_violations` counts each `MATERIAL`-floor independent `OPEN` specialist axis whose same exact unique origin unknown does not recompute to `MATERIAL`.",
        )
        for definition in metric_definitions:
            with self.subTest(definition=definition):
                self.assertIn(definition, grill_contract)

        self.assertIn(
            "These counts are independent and may intentionally overlap for the same record or coverage row.",
            grill_contract,
        )

    def test_foundation_state_passes_v2_validation(self):
        self.assertEqual(validate_state_v2(foundation_state()), [])

    def test_every_root_field_is_required(self):
        for field in foundation_state():
            with self.subTest(field=field):
                state = foundation_state()
                del state[field]
                self.assertIn("schema_error", {error["code"] for error in validate_state_v2(state)})

    def test_unknown_root_and_project_properties_are_rejected(self):
        state = foundation_state()
        state["unexpected"] = True
        self.assertIn("schema_error", {error["code"] for error in validate_state_v2(state)})

        state = foundation_state()
        state["project"]["unexpected"] = True
        self.assertIn("schema_error", {error["code"] for error in validate_state_v2(state)})

    def test_definition_status_is_required_and_legacy_project_fields_are_rejected(self):
        state = foundation_state()
        del state["project"]["definition_status"]
        self.assertIn("schema_error", {error["code"] for error in validate_state_v2(state)})

        for legacy_field in ("status", "user_approved"):
            with self.subTest(legacy_field=legacy_field):
                state = foundation_state()
                state["project"][legacy_field] = "CLOSED"
                self.assertIn("schema_error", {error["code"] for error in validate_state_v2(state)})

    def test_definition_status_rejects_non_string_json_values(self):
        for value in ([], {}):
            with self.subTest(value=value):
                state = foundation_state()
                state["project"]["definition_status"] = value

                self.assertIn("invalid_status", {error["code"] for error in validate_state_v2(state)})

    def test_bootstrap_mode_is_required_and_uses_the_v020_enum(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        project = schema["properties"]["project"]

        self.assertIn("bootstrap_mode", project["required"])
        self.assertEqual(
            project["properties"]["bootstrap_mode"]["enum"],
            ["NEW_PRODUCT", "EXISTING_PRODUCT_RECONCILIATION"],
        )

        missing = foundation_state()
        del missing["project"]["bootstrap_mode"]
        self.assertIn("schema_error", {error["code"] for error in validate_state_v2(missing)})

        invalid = foundation_state()
        invalid["project"]["bootstrap_mode"] = "MIGRATED_PRODUCT"
        self.assertIn("schema_error", {error["code"] for error in validate_state_v2(invalid)})

    def test_v2_is_dispatched_by_the_cli(self):
        code, payload = self.invoke("state", foundation_state())

        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["errors"], [])

    def test_v2_closure_is_explicitly_not_implemented(self):
        result = evaluate_closure_v2(foundation_state())
        code, payload = self.invoke("closure", foundation_state())

        self.assertEqual(result["errors"], [])
        self.assertFalse(result["closed"])
        self.assertIsNone(result["definition_digest"])
        self.assertEqual(result["metrics"]["semantic_closure_not_implemented"], 1)
        self.assertEqual(code, 1, payload)
        self.assertFalse(payload["closed"])
        self.assertIsNone(payload["definition_digest"])
        self.assertEqual(payload["metrics"]["semantic_closure_not_implemented"], 1)

    def test_unassessed_materiality_counts_each_invalid_canonical_record_once(self):
        state = foundation_state()
        requirement = copy.deepcopy(VALID_RECORDS["requirements"])
        requirement["materiality"] = None
        unknown = unknown_record(
            "UNK-010",
            classification="NON_MATERIAL",
            decision_authority="AGENT_AUTONOMOUS",
        )
        unknown["materiality"]["classification"] = "MATERIAL"
        decision = decision_record(
            "DEC-010",
            status="STALE",
            source_unknown_refs=[],
            classification="NON_MATERIAL",
        )
        decision["materiality"] = {"classification": "NON_MATERIAL"}
        surface = {
            "id": "SURF-010",
            "kind": "FEATURE_AREA",
            "name": "Malformed materiality surface",
            "status": "OPEN",
            "materiality": "MATERIAL",
            "evidence_refs": [],
            "authority_refs": [],
            "unknown_refs": [],
            "decision_refs": [],
            "contradiction_refs": [],
            "rationale": None,
            "intent_classification": None,
        }
        contradiction = {
            "id": "CON-010",
            "status": "OPEN",
            "claim_a_refs": [],
            "claim_b_refs": [],
            "scope_refs": [],
            "materiality": [],
            "resolution": None,
            "resolved_by": [],
            "selected_authority_refs": [],
        }
        state["objects"]["requirements"] = [requirement]
        state["objects"]["unknowns"] = [unknown]
        state["objects"]["decisions"] = [decision]
        state["surface_manifest"]["records"] = [surface]
        state["contradictions"] = [contradiction]

        result = evaluate_closure_v2(state)

        self.assertIn("unassessed_materiality", result["metrics"])
        self.assertEqual(result["metrics"]["unassessed_materiality"], 5)
        materiality_errors = {
            error["code"] for error in result["errors"]
            if error["code"] in {"invalid_materiality", "materiality_classification_mismatch"}
        }
        self.assertEqual(
            materiality_errors,
            {"invalid_materiality", "materiality_classification_mismatch"},
        )

    def test_every_typed_group_rejects_id_and_status_without_semantic_minimum(self):
        for group, record in VALID_RECORDS.items():
            with self.subTest(group=group):
                state = foundation_state()
                state["objects"][group] = [{"id": record["id"], "status": record["status"]}]

                self.assertIn("missing_semantic_fields", {error["code"] for error in validate_state_v2(state)})

    def test_every_typed_group_accepts_its_semantic_minimum(self):
        for group, record in VALID_RECORDS.items():
            with self.subTest(group=group):
                state = foundation_state()
                state["objects"][group] = [copy.deepcopy(record)]
                if group == "decisions":
                    state["objects"]["unknowns"] = [resolved_decision_source()]
                if group == "screens":
                    state["ux_coverage"] = screen_ux_coverage(state)

                self.assertEqual(validate_state_v2(state), [])

    def test_typed_records_reject_unknown_fields_empty_text_and_invalid_mapping_arrays(self):
        invalid_records = (
            ("goals", {**VALID_RECORDS["goals"], "unexpected": True}),
            ("goals", {**VALID_RECORDS["goals"], "statement": ""}),
            ("rules", {**VALID_RECORDS["rules"], "applies_to": ["REQ-001", "REQ-001"]}),
            ("tasks", {**VALID_RECORDS["tasks"], "implements": []}),
            ("tasks", {**VALID_RECORDS["tasks"], "acceptance_refs": []}),
        )
        for group, record in invalid_records:
            with self.subTest(group=group, record=record):
                state = foundation_state()
                state["objects"][group] = [copy.deepcopy(record)]
                self.assertIn("schema_error", {error["code"] for error in validate_state_v2(state)})

    def test_typed_authority_statuses_are_group_specific(self):
        for group, record in VALID_RECORDS.items():
            with self.subTest(group=group):
                state = foundation_state()
                invalid = copy.deepcopy(record)
                invalid["status"] = "OPEN" if group != "unknowns" else "CURRENT"
                state["objects"][group] = [invalid]
                self.assertIn("invalid_status", {error["code"] for error in validate_state_v2(state)})

    def test_materiality_shape_is_exact_and_valid_classification_is_accepted(self):
        state = foundation_state()
        requirement = copy.deepcopy(VALID_RECORDS["requirements"])
        requirement["materiality"] = materiality(classification="MATERIAL")
        state["objects"]["requirements"] = [requirement]
        state["coverage"] = [{
            "feature_id": requirement["id"],
            "cells": {axis: not_applicable_cell(state) for axis in CORE_GRILL_AXES},
        }]
        self.assertEqual(validate_state_v2(state), [])

        invalid_materiality = (
            {**materiality(), "unexpected": True},
            {key: value for key, value in materiality().items() if key != "risk_flags"},
            {**materiality(), "classification": "UNKNOWN"},
            {**materiality(), "outcome_divergence": []},
            {**materiality(), "user_visible": "false"},
            {**materiality(), "risk_flags": {**materiality()["risk_flags"], "money": 0}},
        )
        for value in invalid_materiality:
            with self.subTest(value=value):
                invalid = foundation_state()
                record = copy.deepcopy(VALID_RECORDS["requirements"])
                record["materiality"] = value
                invalid["objects"]["requirements"] = [record]
                self.assertIn("invalid_materiality", {error["code"] for error in validate_state_v2(invalid)})

    def test_enum_and_optional_lifecycle_fields_reject_wrong_json_types(self):
        invalid_records = (
            ("unknowns", {**VALID_RECORDS["unknowns"], "decision_authority": []}),
            ("decisions", {**VALID_RECORDS["decisions"], "resolution_mode": {}}),
            ("goals", {**VALID_RECORDS["goals"], "superseded_by": []}),
            ("goals", {**VALID_RECORDS["goals"], "retired_by": "REQ-001"}),
            ("goals", {**VALID_RECORDS["goals"], "retired_at_revision": "1"}),
            ("goals", {**VALID_RECORDS["goals"], "retirement_reason": ""}),
        )
        for group, record in invalid_records:
            with self.subTest(group=group, record=record):
                state = foundation_state()
                state["objects"][group] = [copy.deepcopy(record)]
                self.assertIn("schema_error", {error["code"] for error in validate_state_v2(state)})

    def test_schema_and_runtime_semantic_minima_are_identical(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertTrue(hasattr(state_validation_v2, "TYPE_MINIMA"))

        for group, runtime_minimum in state_validation_v2.TYPE_MINIMA.items():
            with self.subTest(group=group):
                schema_minimum = set(schema["$defs"][group]["required"]) - {"id", "status"}
                self.assertEqual(schema_minimum, runtime_minimum)

    def test_stable_ids_require_uppercase_prefix_and_at_least_three_digits(self):
        for object_id in ("REQ-001", "REQ-999", "REQ-1000"):
            with self.subTest(object_id=object_id):
                state = foundation_state()
                record = copy.deepcopy(VALID_RECORDS["requirements"])
                record["id"] = object_id
                state["objects"]["requirements"] = [record]
                self.assertNotIn("invalid_id", {error["code"] for error in validate_state_v2(state)})

        for object_id in ("REQ-01", "REQ-A01"):
            with self.subTest(object_id=object_id):
                state = foundation_state()
                record = copy.deepcopy(VALID_RECORDS["requirements"])
                record["id"] = object_id
                state["objects"]["requirements"] = [record]
                self.assertIn("invalid_id", {error["code"] for error in validate_state_v2(state)})

    def test_ids_are_unique_across_all_object_groups(self):
        state = foundation_state()
        requirement = copy.deepcopy(VALID_RECORDS["requirements"])
        goal = copy.deepcopy(VALID_RECORDS["goals"])
        goal["id"] = requirement["id"]
        state["objects"]["requirements"] = [requirement]
        state["objects"]["goals"] = [goal]

        self.assertIn("duplicate_id", {error["code"] for error in validate_state_v2(state)})

    def test_reserved_evidence_and_surface_ids_participate_in_global_collisions(self):
        for reserved_location in ("evidence", "surface_manifest"):
            with self.subTest(reserved_location=reserved_location):
                state = foundation_state()
                state["objects"]["requirements"] = [copy.deepcopy(VALID_RECORDS["requirements"])]
                if reserved_location == "evidence":
                    state["evidence"] = [{"id": "REQ-001"}]
                else:
                    state["surface_manifest"]["records"] = [{"id": "REQ-001"}]

                self.assertIn("duplicate_id", {error["code"] for error in validate_state_v2(state)})

    def test_object_and_contradiction_ids_participate_in_global_collisions(self):
        state = foundation_state()
        state["objects"]["requirements"] = [copy.deepcopy(VALID_RECORDS["requirements"])]
        state["contradictions"] = [{"id": "REQ-001"}]

        self.assertIn("duplicate_id", {error["code"] for error in validate_state_v2(state)})

    def test_contradiction_ids_are_unique_within_contradictions(self):
        state = foundation_state()
        state["contradictions"] = [{"id": "CON-001"}, {"id": "CON-001"}]

        self.assertIn("duplicate_id", {error["code"] for error in validate_state_v2(state)})

    def test_superseded_requires_a_different_existing_same_prefix_target(self):
        valid = foundation_state()
        old = copy.deepcopy(VALID_RECORDS["requirements"])
        old.update({"id": "REQ-001", "status": "SUPERSEDED", "superseded_by": "REQ-002"})
        replacement = copy.deepcopy(VALID_RECORDS["requirements"])
        replacement["id"] = "REQ-002"
        valid["objects"]["requirements"] = [old, replacement]
        self.assertNotIn("invalid_supersession", {error["code"] for error in validate_state_v2(valid)})

        invalid_targets = ("REQ-001", "REQ-999", "GOAL-001")
        for target in invalid_targets:
            with self.subTest(target=target):
                state = foundation_state()
                record = copy.deepcopy(old)
                record["superseded_by"] = target
                state["objects"]["requirements"] = [record]
                if target == "GOAL-001":
                    state["objects"]["goals"] = [copy.deepcopy(VALID_RECORDS["goals"])]
                self.assertIn("invalid_supersession", {error["code"] for error in validate_state_v2(state)})

        reserved = foundation_state()
        reserved_old = copy.deepcopy(old)
        reserved_old["superseded_by"] = "REQ-002"
        reserved["objects"]["requirements"] = [reserved_old]
        reserved["evidence"] = [{"id": "REQ-002"}]
        self.assertIn("invalid_supersession", {error["code"] for error in validate_state_v2(reserved)})

    def test_supersession_cycles_fail(self):
        state = foundation_state()
        first = copy.deepcopy(VALID_RECORDS["requirements"])
        first.update({"id": "REQ-001", "status": "SUPERSEDED", "superseded_by": "REQ-002"})
        second = copy.deepcopy(VALID_RECORDS["requirements"])
        second.update({"id": "REQ-002", "status": "SUPERSEDED", "superseded_by": "REQ-001"})
        state["objects"]["requirements"] = [first, second]

        self.assertIn("supersession_cycle", {error["code"] for error in validate_state_v2(state)})

    def test_retired_requires_decision_provenance_revision_and_meaningful_reason(self):
        state = foundation_state()
        state["project"]["definition_revision"] = 3
        decision = copy.deepcopy(VALID_RECORDS["decisions"])
        retired = copy.deepcopy(VALID_RECORDS["requirements"])
        retired.update({
            "status": "RETIRED", "retired_by": "DEC-001", "retired_at_revision": 3,
            "retirement_reason": "Requirement removed from scope",
        })
        state["objects"]["decisions"] = [decision]
        state["objects"]["unknowns"] = [resolved_decision_source()]
        state["objects"]["requirements"] = [retired]
        self.assertNotIn("invalid_retirement", {error["code"] for error in validate_state_v2(state)})

        invalid_overrides = (
            {"retired_by": ""},
            {"retired_by": "REQ-002"},
            {"retired_by": "DEC-999"},
            {"retired_at_revision": 0},
            {"retired_at_revision": 4},
            {"retirement_reason": "TBD"},
        )
        for override in invalid_overrides:
            with self.subTest(override=override):
                invalid = copy.deepcopy(state)
                invalid["objects"]["requirements"][0].update(override)
                if override.get("retired_by") == "REQ-002":
                    other = copy.deepcopy(VALID_RECORDS["requirements"])
                    other["id"] = "REQ-002"
                    invalid["objects"]["requirements"].append(other)
                self.assertIn("invalid_retirement", {error["code"] for error in validate_state_v2(invalid)})

    def test_validation_does_not_auto_retire_dependents(self):
        state = foundation_state()
        state["objects"]["decisions"] = [copy.deepcopy(VALID_RECORDS["decisions"])]
        state["objects"]["unknowns"] = [resolved_decision_source()]
        retired = copy.deepcopy(VALID_RECORDS["requirements"])
        retired.update({
            "status": "RETIRED", "retired_by": "DEC-001", "retired_at_revision": 1,
            "retirement_reason": "Requirement removed from scope",
        })
        dependent = copy.deepcopy(VALID_RECORDS["tasks"])
        state["objects"]["requirements"] = [retired]
        state["objects"]["tasks"] = [dependent]
        before = copy.deepcopy(state)

        self.assertEqual(validate_state_v2(state), [])
        self.assertEqual(state, before)
        self.assertEqual(state["objects"]["tasks"][0]["status"], "CURRENT")


if __name__ == "__main__":
    unittest.main()
