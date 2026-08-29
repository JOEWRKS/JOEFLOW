import json
import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from tests.downstream_v2_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v2_compiler import complete_definition  # noqa: E402
import verify_runtime_v2  # noqa: E402


def canonical_bytes(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class InstalledV2WrapperTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.consumer_cwd = self.directory / "external-consumer"
        self.consumer_cwd.mkdir()
        self.state = closed_v2_state()
        self.definition = complete_definition(self.state)
        self.contract = compile_handoff_definition(
            self.state,
            self.definition,
        )["contract"]
        self.review_contract = compile_handoff_definition(
            self.state,
            complete_definition(self.state, review=True),
        )["contract"]

    def write_json(self, name, value):
        path = self.directory / name
        path.write_bytes(canonical_bytes(value))
        return path

    def run_wrapper(self, wrapper_name, *arguments):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment["PYTHONNOUSERSITE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / wrapper_name),
                *(str(argument) for argument in arguments),
            ],
            cwd=self.consumer_cwd,
            env=environment,
            capture_output=True,
            check=False,
        )

    def assert_json_result(self, result, expected_code):
        self.assertEqual(result.returncode, expected_code, result)
        self.assertEqual(result.stderr, b"")
        self.assertNotIn(b"Traceback", result.stdout)
        try:
            payload = json.loads(result.stdout)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self.fail(f"stdout is not one JSON document: {error}; bytes={result.stdout!r}")
        self.assertEqual(result.stdout, canonical_bytes(payload) + b"\n")
        return payload

    def test_v2_compile_wrapper_works_outside_repo_cwd_without_pythonpath(self):
        state_path = self.write_json("state.json", self.state)
        definition_path = self.write_json("handoff.json", self.definition)
        before = {path: path.read_bytes() for path in (state_path, definition_path)}

        payload = self.assert_json_result(
            self.run_wrapper(
                "compile_downstream_v2.py",
                state_path,
                definition_path,
            ),
            0,
        )

        self.assertEqual(payload["status"], "AUTHORITY_READY_MACHINE_VERIFIED")
        self.assertEqual(
            payload["contract"]["contract_schema_version"],
            "joewrks.action-conformance/2.0",
        )
        self.assertEqual(
            {path: path.read_bytes() for path in (state_path, definition_path)},
            before,
        )

    def test_v2_audit_wrapper_works_outside_repo_cwd_without_pythonpath(self):
        contract_path = self.write_json("contract.json", self.contract)
        state_path = self.write_json("state.json", self.state)
        before = {path: path.read_bytes() for path in (contract_path, state_path)}

        payload = self.assert_json_result(
            self.run_wrapper(
                "audit_downstream_v2.py",
                contract_path,
                state_path,
            ),
            0,
        )

        self.assertEqual(payload["status"], "CONFORMANT")
        self.assertEqual(
            {path: path.read_bytes() for path in (contract_path, state_path)},
            before,
        )

    def test_v2_review_wrapper_works_outside_repo_cwd_without_pythonpath(self):
        contract_path = self.write_json("review-contract.json", self.review_contract)
        before = contract_path.read_bytes()

        payload = self.assert_json_result(
            self.run_wrapper("build_semantic_review_v2.py", contract_path),
            0,
        )

        self.assertTrue(payload["review_required"])
        self.assertEqual(
            payload["package"]["review_schema_version"],
            "joewrks.semantic-review/2.0",
        )
        self.assertEqual(payload["package"]["reliability_status"], "NOT_MEASURED")
        self.assertEqual(contract_path.read_bytes(), before)

    def test_v2_runtime_wrapper_works_outside_repo_cwd_without_pythonpath(self):
        contract_path = self.write_json("runtime-contract.json", self.contract)
        state_path = self.write_json("runtime-state.json", self.state)
        evidence_path = self.directory / "runtime-evidence.jsonl"
        evidence_path.write_bytes(b"")
        before = {
            path: path.read_bytes()
            for path in (contract_path, state_path, evidence_path)
        }

        payload = self.assert_json_result(
            self.run_wrapper(
                "verify_runtime_v2.py",
                contract_path,
                state_path,
                evidence_path,
            ),
            1,
        )

        self.assertEqual(
            payload["report_schema_version"],
            "joewrks.runtime-conformance-report/1.0",
        )
        self.assertEqual(payload["verification_scope"], "FULL_CONTRACT")
        self.assertEqual(payload["contract_dependency_status"], "CONFORMANT")
        self.assertEqual(payload["coverage_status"], "INCOMPLETE")
        self.assertEqual(
            {path: path.read_bytes() for path in before},
            before,
        )

    def test_v2_runtime_wrapper_contains_deep_json_in_every_input_stream(self):
        contract_path = self.write_json("deep-runtime-contract.json", self.contract)
        state_path = self.write_json("deep-runtime-state.json", self.state)
        evidence_path = self.directory / "deep-runtime-evidence.jsonl"
        evidence_path.write_bytes(b"")
        deep_json = b'{"x":' * 600 + b"null" + b"}" * 600
        original = {
            contract_path: contract_path.read_bytes(),
            state_path: state_path.read_bytes(),
            evidence_path: evidence_path.read_bytes(),
        }
        cases = (
            ("contract", contract_path),
            ("state", state_path),
            ("jsonl", evidence_path),
        )
        for stream_name, deep_path in cases:
            with self.subTest(stream=stream_name):
                for path, value in original.items():
                    path.write_bytes(value)
                deep_path.write_bytes(deep_json + (b"\n" if stream_name == "jsonl" else b""))

                payload = self.assert_json_result(
                    self.run_wrapper(
                        "verify_runtime_v2.py",
                        contract_path,
                        state_path,
                        evidence_path,
                    ),
                    2,
                )

                self.assertEqual(payload["status"], "ERROR")
                self.assertEqual(payload["error"]["code"], "JSON_PARSE_ERROR")

    def test_v2_runtime_cli_validates_its_final_report_before_exit(self):
        contract_path = self.write_json("validated-runtime-contract.json", self.contract)
        state_path = self.write_json("validated-runtime-state.json", self.state)
        evidence_path = self.directory / "validated-runtime-evidence.jsonl"
        evidence_path.write_bytes(b"")
        real_builder = verify_runtime_v2.build_runtime_conformance_report

        def corrupted_builder(*arguments):
            report = real_builder(*arguments)
            report["implementation_status"] = "IMPLEMENTATION_CONFORMANT"
            return report

        captured = io.BytesIO()
        stdout = io.TextIOWrapper(captured, encoding="utf-8")
        with mock.patch.object(
            verify_runtime_v2,
            "build_runtime_conformance_report",
            side_effect=corrupted_builder,
        ), mock.patch.object(verify_runtime_v2.sys, "stdout", stdout):
            exit_code = verify_runtime_v2.main([
                str(contract_path),
                str(state_path),
                str(evidence_path),
            ])
            stdout.flush()

        payload = json.loads(captured.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(captured.getvalue(), canonical_bytes(payload) + b"\n")
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload["error"]["code"], "RUNTIME_REPORT_INVALID")

    def test_v2_runtime_wrapper_binds_contained_failure_to_source_contract(self):
        contract_path = self.write_json("failure-runtime-contract.json", self.contract)
        state_path = self.write_json("failure-runtime-state.json", self.state)
        evidence_path = self.directory / "failure-runtime-evidence.jsonl"
        evidence_path.write_bytes(b"{}\n")

        payload = self.assert_json_result(
            self.run_wrapper(
                "verify_runtime_v2.py",
                contract_path,
                state_path,
                evidence_path,
            ),
            1,
        )

        self.assertEqual(len(payload["action_results"]), 1)
        failed = payload["action_results"][0]
        self.assertFalse(failed["conformant"])
        self.assertEqual(failed["error"]["code"], "RUNTIME_EVIDENCE_PROTOCOL_INVALID")
        self.assertEqual(failed["source_contract"], payload["source_contract"])
        self.assertEqual(failed["runtime_evidence"], {})

    def test_installed_wrappers_preserve_m5_usage_json_and_exit_contract(self):
        cases = (
            "compile_downstream_v2.py",
            "audit_downstream_v2.py",
            "build_semantic_review_v2.py",
            "verify_runtime_v2.py",
        )
        for wrapper_name in cases:
            with self.subTest(wrapper_name=wrapper_name):
                payload = self.assert_json_result(
                    self.run_wrapper(wrapper_name),
                    2,
                )
                self.assertEqual(payload["status"], "ERROR")
                self.assertEqual(payload["error"]["code"], "USAGE_ERROR")


class InstalledV2WorkflowContractTest(unittest.TestCase):
    def test_skill_default_template_is_v020(self):
        skill = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        template = json.loads(
            (PACKAGE_ROOT / "templates" / "state-v0.2.0.example.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertTrue(
            "PRODUCT_DEFINITION_STATE_V2_DEFAULT" in skill,
            "missing V2-default skill marker",
        )
        self.assertTrue(
            "templates/state-v0.2.0.example.json" in skill,
            "skill does not route new projects to the V2 template",
        )
        self.assertTrue(
            "schemas/state-v0.2.0.schema.json" in skill,
            "skill does not name the V2 schema",
        )
        self.assertEqual(template["schema_version"], "0.2.0")
        self.assertEqual(template["migration"], {"mode": "NATIVE"})
        self.assertEqual(template["project"]["definition_status"], "OPEN")
        self.assertEqual(template["approval"], {"status": "UNAPPROVED"})
        self.assertNotIn("approved_at", template["approval"])

    def test_skill_keeps_legacy_dispatch_explicit(self):
        skill = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")

        for required_text in (
            "LEGACY_0_1_2_1_COMPATIBILITY_PRESERVED",
            "templates/state.example.json",
            "schemas/state.schema.json",
            "0.1.2.1",
            "never silently migrate",
            "only when the user explicitly asks to adopt V2",
        ):
            with self.subTest(required_text=required_text):
                self.assertTrue(required_text in skill, required_text)

    def test_v2_workflow_document_starts_with_the_plain_language_lifecycle(self):
        workflow_path = PACKAGE_ROOT / "references" / "workflow-v0.2.0.md"
        self.assertTrue(workflow_path.is_file(), workflow_path)
        workflow = workflow_path.read_text(encoding="utf-8")

        korean = "찾기 → 애매한 것 정하기 → 기준 고정 → 사용자 승인 → 구현 전달 → 구현 검증"
        internal = "DISCOVER → CLOSE → FREEZE → APPROVE → HANDOFF → VERIFY"
        self.assertLess(workflow.index(korean), workflow.index(internal))
        self.assertIn("compile_downstream_v2.py", workflow)
        self.assertIn("audit_downstream_v2.py", workflow)
        self.assertIn("build_semantic_review_v2.py", workflow)
        self.assertIn("affected scope", workflow)

    def test_readme_and_architecture_publish_exact_v2_status_markers(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        architecture = (ROOT / "PROGRAM_ARCHITECTURE.md").read_text(
            encoding="utf-8"
        )
        combined = readme + "\n" + architecture

        for marker in (
            "PRODUCT_DEFINITION_STATE_V2_DEFAULT",
            "LEGACY_0_1_2_1_COMPATIBILITY_PRESERVED",
            "DOWNSTREAM_V2_INSTALLED_ROUTING",
            "SEMANTIC_REVIEW_V2_RELIABILITY_NOT_MEASURED",
        ):
            with self.subTest(marker=marker):
                self.assertTrue(marker in combined, marker)
        for current_contract in (
            "Current Product Definition state contract: `0.2.0`",
            "Current V2 downstream authority contract: `joewrks.action-conformance/2.0`",
            "Current V2 semantic review boundary: `joewrks.semantic-review/2.0` / reliability `NOT_MEASURED`",
        ):
            with self.subTest(current_contract=current_contract):
                self.assertTrue(current_contract in combined, current_contract)
        historical = (
            "Historical compatibility: state `0.1.2.1`, "
            "`joewrks.action-conformance/1.0`, `joewrks.semantic-review/1.0`, "
            "and v0.4.3 evidence"
        )
        self.assertTrue(historical in combined, historical)


if __name__ == "__main__":
    unittest.main()
