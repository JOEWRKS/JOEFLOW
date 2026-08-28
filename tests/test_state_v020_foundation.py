import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.v020_support import foundation_state
except ModuleNotFoundError:
    from v020_support import foundation_state


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"

sys.path.insert(0, str(SCRIPTS))
from state_validation_v2 import evaluate_closure_v2, validate_state_v2


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


if __name__ == "__main__":
    unittest.main()
