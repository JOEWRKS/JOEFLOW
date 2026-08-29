import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from downstream_v2.derivation import (  # noqa: E402
    load_responsibility_profile,
    seed_matches_selector,
)
from downstream_v2.seeds import build_closed_source_seed_inventory  # noqa: E402
from tests.downstream_v2_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v2_compiler import complete_definition  # noqa: E402
from tests.test_downstream_v2_reentry import make_in_progress  # noqa: E402


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


class DownstreamV2CliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.state = closed_v2_state()
        self.definition = complete_definition(self.state)
        self.machine_contract = compile_handoff_definition(
            self.state, self.definition
        )["contract"]
        self.review_contract = compile_handoff_definition(
            self.state, complete_definition(self.state, review=True)
        )["contract"]

    def write_json(self, name, value):
        path = self.directory / name
        path.write_bytes(canonical_bytes(value))
        return path

    def write_recursive_value(self, name, value):
        placeholder = "__DEEP_SEMANTIC_VALUE__"
        encoded = canonical_bytes(value)
        needle = canonical_bytes(placeholder)
        self.assertEqual(encoded.count(needle), 1)
        recursive = None
        for depth in range(100, 5001, 100):
            candidate = b"[" * depth + b"0" + b"]" * depth
            try:
                parsed = json.loads(candidate)
            except RecursionError:
                break
            try:
                copy.deepcopy(parsed)
            except RecursionError:
                recursive = candidate
                break
        if recursive is None:
            self.fail("could not trigger bounded post-decode semantic recursion")
        path = self.directory / name
        path.write_bytes(encoded.replace(needle, recursive))
        json.loads(path.read_bytes())
        return path

    def run_cli(self, module, *arguments):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join((str(PACKAGE_ROOT), str(SCRIPTS)))
        return subprocess.run(
            [sys.executable, "-m", module, *(str(argument) for argument in arguments)],
            cwd=ROOT,
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

    def test_compile_cli_materializes_a_deterministic_contract_without_writes(self):
        state_path = self.write_json("state.json", self.state)
        definition_path = self.write_json("handoff.json", self.definition)
        before = {path: path.read_bytes() for path in (state_path, definition_path)}

        first = self.run_cli("downstream_v2.compile", state_path, definition_path)
        second = self.run_cli("downstream_v2.compile", state_path, definition_path)

        payload = self.assert_json_result(first, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(second.stderr, b"")
        self.assertEqual(payload["status"], "AUTHORITY_READY_MACHINE_VERIFIED")
        self.assertEqual(
            payload["contract"]["contract_schema_version"],
            "joewrks.action-conformance/2.0",
        )
        self.assertEqual(payload["semantic_debt"]["authority_gap_count"], 0)
        self.assertEqual(
            {path: path.read_bytes() for path in (state_path, definition_path)}, before
        )

    def test_compile_cli_returns_reentry_for_an_authority_gap_without_a_contract(self):
        changed = copy.deepcopy(self.definition)
        changed["actions"][0]["fields"]["authentication"] = {
            "kind": "UNRESOLVED",
            "gap_type": "AMBIGUITY_FOUND",
            "description": "Authentication behavior has no approved authority.",
            "required_authority_class": "CONSTRAINT",
            "evidence_refs": ["EVD-001"],
        }
        result = self.run_cli(
            "downstream_v2.compile",
            self.write_json("state.json", self.state),
            self.write_json("gap.json", changed),
        )
        payload = self.assert_json_result(result, 1)
        self.assertEqual(payload["status"], "REENTRY_REQUIRED")
        self.assertIsNone(payload["contract"])
        self.assertGreater(payload["semantic_debt"]["authority_gap_count"], 0)
        self.assertTrue(payload["reentry_events"])

    def test_compile_cli_requires_actual_m4_closure(self):
        open_state = copy.deepcopy(self.state)
        open_state["project"]["definition_status"] = "OPEN"
        result = self.run_cli(
            "downstream_v2.compile",
            self.write_json("open-state.json", open_state),
            self.write_json("handoff.json", self.definition),
        )
        payload = self.assert_json_result(result, 1)
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload["error"]["code"], "PRODUCT_DEFINITION_NOT_CLOSED")

    def test_audit_cli_is_conformant_for_closed_and_inspectable_open_state(self):
        contract_path = self.write_json("contract.json", self.machine_contract)
        closed_path = self.write_json("closed.json", self.state)
        first = self.run_cli("downstream_v2.audit", contract_path, closed_path)
        closed = self.assert_json_result(first, 0)
        self.assertEqual(closed["status"], "CONFORMANT")
        self.assertTrue(closed["global_definition_closed"])

        in_progress = copy.deepcopy(self.state)
        make_in_progress(in_progress, increment_revision=True)
        open_path = self.write_json("in-progress.json", in_progress)
        before = {path: path.read_bytes() for path in (contract_path, open_path)}
        second = self.run_cli("downstream_v2.audit", contract_path, open_path)
        current = self.assert_json_result(second, 0)
        self.assertEqual(current["status"], "CONFORMANT")
        self.assertFalse(current["global_definition_closed"])
        self.assertEqual(
            current["authority_revision_relation"], "OLDER_APPROVED_REVISION_UNAFFECTED"
        )
        self.assertEqual(
            {path: path.read_bytes() for path in (contract_path, open_path)}, before
        )

    def test_audit_cli_fails_closed_for_an_invalid_contract(self):
        invalid = copy.deepcopy(self.machine_contract)
        invalid["semantic_contract_hash"] = "0" * 64
        result = self.run_cli(
            "downstream_v2.audit",
            self.write_json("invalid-contract.json", invalid),
            self.write_json("state.json", self.state),
        )
        payload = self.assert_json_result(result, 1)
        self.assertEqual(payload["status"], "REENTRY_REQUIRED")
        self.assertTrue(payload["reentry_events"])

    def test_audit_cli_reports_affected_only_scope_drift_without_writes(self):
        definition = copy.deepcopy(self.definition)
        profile = load_responsibility_profile()
        seeds = build_closed_source_seed_inventory(self.state)
        current_scope_refs = ["REQ-001", "SCR-001", "SURF-001"]
        second_context = {
            "authority_scope_refs": ["REQ-001"],
            "current_scope_refs": current_scope_refs,
        }
        second = copy.deepcopy(definition["actions"][0])
        second["action_id"] = "unrelated-action"
        second["authority_scope_refs"] = ["REQ-001"]
        second["ux_action_locator"] = None
        second["fields"] = {}
        for field_name, policy in profile["action_fields"].items():
            matches = [
                seed
                for seed in seeds
                if any(
                    seed_matches_selector(seed, selector, second_context)
                    for selector in policy["allowed_seed_selectors"]
                )
            ]
            self.assertTrue(matches, field_name)
            second["fields"][field_name] = {
                "kind": "DIRECT_AUTHORITY",
                "source_seed_ref": matches[0]["seed_key"],
            }
        definition["actions"].append(second)
        definition["actions"].sort(key=lambda action: action["action_id"])
        contract = compile_handoff_definition(self.state, definition)["contract"]
        self.assertIsNotNone(contract)

        drifted = copy.deepcopy(self.state)
        drifted["surface_manifest"]["records"][0]["name"] += " revised"
        make_in_progress(drifted, increment_revision=True)
        contract_path = self.write_json("scoped-contract.json", contract)
        state_path = self.write_json("scope-drift.json", drifted)
        before = {path: path.read_bytes() for path in (contract_path, state_path)}

        payload = self.assert_json_result(
            self.run_cli("downstream_v2.audit", contract_path, state_path), 1
        )
        self.assertEqual(payload["status"], "REENTRY_REQUIRED")
        self.assertTrue(payload["reentry_events"])
        self.assertTrue(all(
            event["halt_scope"]["mode"] == "AFFECTED_ONLY"
            for event in payload["reentry_events"]
        ))
        halted = {
            action_id
            for event in payload["reentry_events"]
            for action_id in event["halt_scope"]["action_ids"]
        }
        self.assertIn("submit-request", halted)
        self.assertNotIn("unrelated-action", halted)
        self.assertEqual(
            {path: path.read_bytes() for path in (contract_path, state_path)}, before
        )

    def test_semantic_review_cli_builds_deterministic_package_or_explicit_no_package(self):
        review_path = self.write_json("review-contract.json", self.review_contract)
        first = self.run_cli("downstream_v2.semantic_review.build_package", review_path)
        second = self.run_cli("downstream_v2.semantic_review.build_package", review_path)
        review = self.assert_json_result(first, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertTrue(review["review_required"])
        self.assertEqual(
            review["package"]["review_schema_version"], "joewrks.semantic-review/2.0"
        )
        self.assertEqual(review["package"]["reliability_status"], "NOT_MEASURED")

        machine = self.assert_json_result(
            self.run_cli(
                "downstream_v2.semantic_review.build_package",
                self.write_json("machine-contract.json", self.machine_contract),
            ),
            0,
        )
        self.assertEqual(machine, {"package": None, "review_required": False})

    def test_expected_usage_read_and_json_errors_are_structured_and_traceback_free(self):
        bad_json = self.directory / "bad.json"
        bad_json.write_text("{not json", encoding="utf-8")
        missing = self.directory / "missing.json"
        cases = (
            ("downstream_v2.compile", (), "USAGE_ERROR"),
            ("downstream_v2.compile", (missing, bad_json), "READ_ERROR"),
            ("downstream_v2.compile", (bad_json, bad_json), "JSON_PARSE_ERROR"),
            ("downstream_v2.audit", (), "USAGE_ERROR"),
            ("downstream_v2.audit", (missing, bad_json), "READ_ERROR"),
            ("downstream_v2.audit", (bad_json, bad_json), "JSON_PARSE_ERROR"),
            ("downstream_v2.semantic_review.build_package", (), "USAGE_ERROR"),
            ("downstream_v2.semantic_review.build_package", (missing,), "READ_ERROR"),
            ("downstream_v2.semantic_review.build_package", (bad_json,), "JSON_PARSE_ERROR"),
        )
        for module, arguments, code in cases:
            with self.subTest(module=module, arguments=arguments):
                payload = self.assert_json_result(self.run_cli(module, *arguments), 2)
                self.assertEqual(payload["status"], "ERROR")
                self.assertEqual(payload["error"]["code"], code)

    def test_deep_json_decode_recursion_is_a_structured_parse_error(self):
        deep_json = self.directory / "deep-json.json"
        recursive = None
        for depth in range(4000, 40001, 4000):
            candidate = b"[" * depth + b"0" + b"]" * depth
            try:
                json.loads(candidate)
            except RecursionError:
                recursive = candidate
                break
        if recursive is None:
            self.fail("could not trigger bounded JSON decoder recursion")
        deep_json.write_bytes(recursive)
        state_path = self.write_json("state.json", self.state)
        definition_path = self.write_json("handoff.json", self.definition)
        cases = (
            ("downstream_v2.compile", (deep_json, definition_path)),
            ("downstream_v2.audit", (deep_json, state_path)),
            ("downstream_v2.semantic_review.build_package", (deep_json,)),
        )
        for module, arguments in cases:
            with self.subTest(module=module):
                payload = self.assert_json_result(self.run_cli(module, *arguments), 2)
                self.assertEqual(payload["status"], "ERROR")
                self.assertEqual(payload["error"]["code"], "JSON_PARSE_ERROR")

    def test_semantic_processing_recursion_is_a_structured_invalid_input(self):
        recursive_definition = complete_definition(self.state, review=True)
        recursive_definition["actions"][0]["fields"]["visible_success"][
            "proposed_value"
        ] = "__DEEP_SEMANTIC_VALUE__"
        recursive_contract = copy.deepcopy(self.machine_contract)
        recursive_contract["unexpected_recursive_value"] = "__DEEP_SEMANTIC_VALUE__"
        state_path = self.write_json("state.json", self.state)
        definition_path = self.write_recursive_value(
            "recursive-handoff.json", recursive_definition
        )
        contract_path = self.write_recursive_value(
            "recursive-contract.json", recursive_contract
        )
        cases = (
            ("downstream_v2.compile", (state_path, definition_path), "INVALID_SEMANTIC_INPUT"),
            ("downstream_v2.audit", (contract_path, state_path), "INVALID_AUDIT_INPUT"),
            (
                "downstream_v2.semantic_review.build_package",
                (contract_path,),
                "INVALID_ACTION_CONTRACT_V2",
            ),
        )
        for module, arguments, code in cases:
            with self.subTest(module=module):
                payload = self.assert_json_result(self.run_cli(module, *arguments), 1)
                self.assertEqual(payload["status"], "ERROR")
                self.assertEqual(payload["error"]["code"], code)

    def test_semantic_review_cli_rejects_invalid_contract_as_semantic_input(self):
        invalid = copy.deepcopy(self.review_contract)
        invalid["artifact_hash"] = "0" * 64
        payload = self.assert_json_result(
            self.run_cli(
                "downstream_v2.semantic_review.build_package",
                self.write_json("invalid-review-contract.json", invalid),
            ),
            1,
        )
        self.assertEqual(payload["status"], "ERROR")
        self.assertEqual(payload["error"]["code"], "INVALID_ACTION_CONTRACT_V2")


class DownstreamV2DocumentationTests(unittest.TestCase):
    def test_posix_pythonpath_example_exports_the_two_package_roots(self):
        text = (PACKAGE_ROOT / "downstream_v2" / "README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'export PYTHONPATH="<skill-root>:<skill-root>/scripts"', text
        )

    def test_downstream_contract_contains_every_normative_m5_marker(self):
        text = (
            PACKAGE_ROOT / "references" / "downstream-v2-contract.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "DOWNSTREAM_V2_AUTHORITY_IMPLEMENTED_M5",
            "ACTION_CONFORMANCE_2_0",
            "SOURCE_SEEDS_FROM_M4_BINDINGS",
            "SEMANTIC_AUTHORITY_GAP_REENTERS_PRODUCT_DEFINITION",
            "REVIEW_REQUIRED_IS_ASSURANCE_NOT_AUTHORITY",
            "AUTHORITY_GAP_COUNT_MUST_BE_ZERO",
            "SEMANTIC_REVIEW_2_0_RELIABILITY_NOT_MEASURED",
            "DOWNSTREAM_V1_REMAINS_FROZEN",
            "M6_INTEGRATION_NOT_IMPLEMENTED_IN_M5",
            "RUNTIME_CONFORMANCE_NOT_INTEGRATED_IN_M5",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_reentry_contract_contains_every_normative_marker(self):
        text = (
            PACKAGE_ROOT / "references" / "implementation-reentry-contract.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "AMBIGUITY_FOUND",
            "CONTRACT_CONFLICT",
            "OUT_OF_SCOPE_REQUEST",
            "AFFECTED_ONLY",
            "CANDIDATE_UNKNOWN_IS_NOT_CANONICAL_AUTHORITY",
            "REENTER_PRODUCT_DEFINITION",
            "NO_SILENT_IMPLEMENTATION_PRODUCT_DECISIONS",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
