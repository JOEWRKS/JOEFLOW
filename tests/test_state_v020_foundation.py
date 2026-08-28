import json
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.v020_support import foundation_state, materiality
except ModuleNotFoundError:
    from v020_support import foundation_state, materiality


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"

sys.path.insert(0, str(SCRIPTS))
import state_validation_v2
from state_validation_v2 import evaluate_closure_v2, validate_state_v2


VALID_RECORDS = {
    "goals": {"id": "GOAL-001", "status": "CURRENT", "statement": "Ship the product"},
    "users": {"id": "USR-001", "status": "CURRENT", "description": "Primary user", "actor_kind": "PERSON"},
    "requirements": {
        "id": "REQ-001", "status": "CURRENT", "statement": "Save work", "scope": "CORE",
        "ui_required": True, "materiality": materiality(),
    },
    "unknowns": {
        "id": "UNK-001", "status": "OPEN", "question": "Which format?",
        "materiality": materiality(), "decision_authority": "USER_CONFIRMATION",
    },
    "decisions": {
        "id": "DEC-001", "status": "CURRENT", "statement": "Use JSON", "decision_type": "FORMAT",
        "resolution_mode": "USER_DECISION", "decision_authority": "USER_DECISION_REQUIRED",
        "source_unknown_refs": ["UNK-001"], "evidence_refs": [], "materiality": materiality(),
        "affects": ["REQ-001"],
    },
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

        self.assertEqual(
            set(schema["required"]),
            {
                "schema_version", "project", "migration", "evidence", "surface_manifest",
                "contradictions", "objects", "coverage", "ux_coverage",
                "discovery_baseline", "approval", "approval_history",
            },
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["properties"]["project"]["additionalProperties"])

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

    def test_materiality_shape_is_exact_but_classification_is_not_recomputed_in_m1(self):
        state = foundation_state()
        requirement = copy.deepcopy(VALID_RECORDS["requirements"])
        requirement["materiality"] = materiality(classification="MATERIAL")
        state["objects"]["requirements"] = [requirement]
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
