import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"


class SkillPackageTest(unittest.TestCase):
    def test_required_package_resources_exist(self):
        required = [
            "SKILL.md", "agents/openai.yaml",
            "schemas/state.schema.json", "templates/state.example.json", "references/state-contract.md",
            "references/interrogation-engine.md", "references/unknown-taxonomy.md",
            "references/requirement-taxonomy.md", "references/product-coverage-matrix.md",
            "references/ux-state-taxonomy.md", "references/failure-recovery-taxonomy.md",
            "references/artifact-dependency-graph.md", "references/closure-gate.md",
            "references/figma-make-handoff.md",
            "templates/product-definition.md", "templates/unknown-ledger.md",
            "templates/decision-ledger.md", "templates/user-flows.md",
            "templates/screen-spec.md", "templates/implementation-plan.md",
            "templates/figma-make-handoff.md",
        ]
        missing = [relative for relative in required if not (SKILL / relative).is_file()]
        self.assertEqual(missing, [])

    def test_validator_scripts_only_import_standard_library_or_sibling_module(self):
        allowed = {"__future__", "copy", "hashlib", "json", "pathlib", "sys", "typing", "state_validation"}
        imports = set()
        for script in (SKILL / "scripts").glob("*.py"):
            tree = ast.parse(script.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
        self.assertEqual(imports - allowed, set())

    def test_openai_metadata_is_discoverable_by_default(self):
        path = SKILL / "agents" / "openai.yaml"
        self.assertTrue(path.is_file(), f"missing metadata: {path}")
        metadata = path.read_text(encoding="utf-8")
        self.assertNotIn("allow_implicit_invocation: false", metadata)

    def test_canonical_schema_and_example_are_machine_readable(self):
        schema = json.loads((SKILL / "schemas/state.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "validate_state.py"), str(SKILL / "templates" / "state.example.json")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
