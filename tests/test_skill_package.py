import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"


class SkillPackageTest(unittest.TestCase):
    def test_program_release_docs_and_package_metadata_are_consistent(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        architecture = (ROOT / "PROGRAM_ARCHITECTURE.md").read_text(encoding="utf-8")
        regression_environment = (ROOT / "docs" / "regression-environment.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        metadata = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertEqual(version, "1.1.0")
        self.assertIn(f"v{version}", readme)
        self.assertIn(f"| 프로그램 릴리스 | `v{version}` |", architecture)
        self.assertIn(
            f"이 기준선의 전체 프로그램 릴리스: `v{version}`",
            architecture,
        )
        self.assertIn(f"## {version}", changelog)
        report_headings = (
            "## 1. 핵심 요약", "## 2. 설계 목적", "## 3. 주요 기능",
            "## 4. 사용 방법", "## 5. 도구 간 연결", "## 6. 한계",
        )
        for document in (readme, architecture, regression_environment):
            for heading in report_headings:
                self.assertIn(heading, document)
        for heading in (
            "## 1. Summary", "## 2. Design Purpose", "## 3. Key Features",
            "## 4. Usage", "## 5. Tool Integration", "## 6. Limitations",
        ):
            self.assertIn(heading, readme)
        for language_marker in (
            "[English](#english) | [한국어](#korean)",
            '<a name="english"></a>', '<a name="korean"></a>',
            "Program version: **`v1.1.0`**",
            "Runtime skill/package ID: **`joewrks-product-definition`**",
            "Authoritative source: **`product-definition/<project-slug>/state.json`**",
            "[Current V2 workflow](skills/joewrks-product-definition/references/workflow-v0.2.0.md)",
            "[Implementation mismatch re-entry procedure](skills/joewrks-product-definition/references/reentry-workflow-v0.2.0.md)",
        ):
            self.assertIn(language_marker, readme)
        self.assertEqual(readme.splitlines().count("# JOEFLOW"), 1)
        for role in (
            "요구사항·규칙·예외·완료 기준 확정",
            "화면 제작·시각 기준 수립·디자인 검수",
            "작업 순서·진행 상태·완료 근거 관리",
            "Requirements, rules, exceptions, and acceptance criteria",
            "UI creation, visual standards, and design review",
            "Task sequence, progress, and completion evidence",
        ):
            self.assertIn(role, readme)
        self.assertIn("skills/joewrks-product-definition", readme)
        self.assertIn("joewrks-product-definition", metadata)

    def test_required_package_resources_exist(self):
        required = [
            "SKILL.md", "agents/openai.yaml",
            "schemas/state.schema.json", "templates/state.example.json", "references/state-contract.md",
            "references/interrogation-engine.md", "references/unknown-taxonomy.md",
            "references/requirement-taxonomy.md", "references/product-coverage-matrix.md",
            "references/ux-state-taxonomy.md", "references/failure-recovery-taxonomy.md",
            "references/artifact-dependency-graph.md", "references/closure-gate.md",
            "references/figma-make-handoff.md", "references/discovery-contract-v0.2.0.md",
            "references/grill-contract-v0.2.0.md", "references/semantic-freeze-contract-v0.2.0.md",
            "references/grill-packs/grill-pack.schema.json",
            "references/grill-packs/core.json", "references/grill-packs/auth.json",
            "references/grill-packs/money.json", "references/grill-packs/file-upload.json",
            "references/grill-packs/async.json", "references/grill-packs/permission.json",
            "references/grill-packs/destructive-action.json",
            "scripts/discovery_v2.py", "scripts/build_discovery_baseline.py", "scripts/cli_output.py",
            "scripts/materiality_v2.py", "scripts/grill_v2.py", "scripts/next_product_question.py",
            "scripts/authority_binding_v2.py", "scripts/authority_binding_value.py",
            "scripts/approval_v2.py", "scripts/build_approval_manifest.py",
            "scripts/candidate_preflight_v2.py", "scripts/preflight_state_candidate.py",
            "scripts/projection_audit_v2.py", "scripts/audit_planning_projections.py",
            "references/binding-contracts/binding-contract.schema.json",
            "references/binding-contracts/product-coverage-binding-v1.json",
            "references/binding-contracts/ux-coverage-binding-v1.json",
            "templates/product-definition.md", "templates/unknown-ledger.md",
            "templates/decision-ledger.md", "templates/user-flows.md",
            "templates/screen-spec.md", "templates/implementation-plan.md",
            "templates/figma-make-handoff.md", "templates/master-planning-spec.md",
            "templates/planning-review-core.html",
        ]
        missing = [relative for relative in required if not (SKILL / relative).is_file()]
        self.assertEqual(missing, [])

    def test_v1_human_delivery_contract_is_declared(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        workflow_text = (SKILL / "references" / "workflow-v0.2.0.md").read_text(encoding="utf-8")
        for required in ("MASTER_PLANNING_SPEC.md", "planning-review-core.html"):
            self.assertIn(required, skill_text)
            self.assertIn(required, workflow_text)
        self.assertIn("Preserve conditional outcomes as conditional", workflow_text)

    def test_validator_scripts_only_import_standard_library_or_sibling_module(self):
        allowed = {"__future__", "argparse", "copy", "datetime", "hashlib", "importlib", "json", "os", "pathlib", "re", "stat", "subprocess", "sys", "typing", "uuid", "migration_v2", "state_contract_dispatch", "state_validation", "state_validation_v2", "discovery_v2", "materiality_v2", "grill_v2", "authority_binding_v2", "approval_v2", "downstream_v2", "integration_v2", "candidate_preflight_v2", "projection_audit_v2", "build_approval_manifest", "cli_output"}
        imports = set()
        for script in (SKILL / "scripts").glob("*.py"):
            tree = ast.parse(script.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
        self.assertEqual(imports, allowed)

    def test_validator_scripts_do_not_hide_dependencies_from_ast_policy(self):
        hidden_imports = []
        for script in (SKILL / "scripts").glob("*.py"):
            tree = ast.parse(script.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "__import__"
                ):
                    hidden_imports.append(f"{script.name}:{node.lineno}")
        self.assertEqual(hidden_imports, [])

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
