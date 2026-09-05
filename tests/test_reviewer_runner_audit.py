import http.client
import json
import importlib.util
import os
import py_compile
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS_ROOT = SKILL_ROOT / "scripts"
for path in (SKILL_ROOT, SCRIPTS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:  # A missing Task 8 implementation is a controlled RED assertion.
    from audit_reviewer_runner import (  # noqa: E402
        IMPLEMENTATION_BASE_REVISION,
        build_capability_audit,
        canonical_audit_json,
        frozen_blob_map,
    )
except ImportError:
    IMPLEMENTATION_BASE_REVISION = None
    build_capability_audit = None
    canonical_audit_json = None
    frozen_blob_map = None


def _git(*arguments):
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(ROOT), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


class _EnvironmentAccessForbidden(dict):
    """Raise if the audit touches any process-environment mapping surface."""

    @staticmethod
    def _forbid(*_arguments, **_keywords):
        raise AssertionError("audit accessed the process environment")

    __contains__ = _forbid
    __getitem__ = _forbid
    __iter__ = _forbid
    copy = _forbid
    get = _forbid
    items = _forbid
    keys = _forbid
    values = _forbid


class ReviewerRunnerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.revision = _git("rev-parse", "HEAD")
        cls.tree = _git("rev-parse", "HEAD^{tree}")
        cls.historical_revision = "0b754bdc2502be35a7f657275f17fe117e8c49bd"
        cls.historical_tree = _git("rev-parse", f"{cls.historical_revision}^{{tree}}")

    def require_audit_implementation(self):
        self.assertIsNotNone(
            build_capability_audit,
            "audit_reviewer_runner implementation is missing",
        )
        self.assertIsNotNone(canonical_audit_json)
        self.assertIsNotNone(frozen_blob_map)

    def assert_private_namespace_collision_fails_closed(self, suffix, seeded_module):
        namespace = f"_audit_verified_reviewer_runner_{self.revision}"
        seeded_name = f"{namespace}{suffix}"
        self.assertFalse(
            any(
                name == namespace or name.startswith(f"{namespace}.")
                for name in sys.modules
            )
        )
        sys.modules[seeded_name] = seeded_module
        try:
            with self.assertRaisesRegex(RuntimeError, "module namespace collision"):
                build_capability_audit(ROOT, self.revision)
            self.assertFalse(
                any(
                    name == namespace or name.startswith(f"{namespace}.")
                    for name in sys.modules
                ),
                "private verified-runner modules survived a failed load",
            )
        finally:
            for name in tuple(sys.modules):
                if name == namespace or name.startswith(f"{namespace}."):
                    sys.modules.pop(name, None)

    def test_no_registered_real_adapter_reports_unavailable_and_calibration_not_run(self):
        self.require_audit_implementation()

        result = build_capability_audit(ROOT, self.historical_revision)

        self.assertEqual(
            result,
            {
                "schema_version": "joewrks.reviewer-runner-capability-audit/1.0",
                "runner_contract_version": "joewrks.reviewer-runner/1.0",
                "implementation_status": "RUNNER_IMPLEMENTED",
                "backend_kind": "STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
                "registered_real_adapter_count": 0,
                "real_backend_capability": "UNAVAILABLE",
                "runner_state": "ISOLATION_CAPABILITY_UNAVAILABLE",
                "calibration_status": "CALIBRATION_NOT_RUN",
                "semantic_review_21_reliability": "NOT_MEASURED",
                "v044_status": "BLOCKED",
                "real_calibration_attempts": 1,
                "valid_real_calibration_runs": 0,
                "fake_backend_authoritative": False,
                "provider_selected": None,
                "implementation_code_commit": self.historical_revision,
                "implementation_code_tree": self.historical_tree,
            },
        )

    def test_registered_unprovisioned_anthropic_revision_reports_v11_bounded_truth(self):
        self.require_audit_implementation()

        self.assertEqual(
            build_capability_audit(ROOT, self.revision),
            {
                "adapter_implementation": "IMPLEMENTED",
                "backend_kind": "STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
                "backend_provisioning": "REQUIRED",
                "calibration_status": "CALIBRATION_NOT_RUN",
                "fake_backend_authoritative": False,
                "implementation_code_commit": self.revision,
                "implementation_code_tree": self.tree,
                "implementation_status": "RUNNER_IMPLEMENTED",
                "provider_candidate": "anthropic",
                "provider_selected": "anthropic",
                "real_backend_capability": "UNAVAILABLE",
                "real_calibration_attempts": 1,
                "real_provider_request_count": 0,
                "real_synthetic_preflight": "NOT_RUN",
                "registered_real_adapter_count": 1,
                "runner_contract_version": "joewrks.reviewer-runner/1.0",
                "runner_state": "ISOLATION_CAPABILITY_UNAVAILABLE",
                "schema_version": "joewrks.reviewer-runner-capability-audit/1.1",
                "semantic_review_21_reliability": "NOT_MEASURED",
                "v044_status": "BLOCKED",
                "valid_real_calibration_runs": 0,
            },
        )

    def test_v11_reports_adapter_implemented_count_one_and_provider_anthropic(self):
        self.require_audit_implementation()

        result = build_capability_audit(ROOT, self.revision)

        self.assertEqual(
            result["schema_version"],
            "joewrks.reviewer-runner-capability-audit/1.1",
        )
        self.assertEqual(result["adapter_implementation"], "IMPLEMENTED")
        self.assertEqual(result["registered_real_adapter_count"], 1)
        self.assertEqual(result["provider_candidate"], "anthropic")
        self.assertEqual(result["provider_selected"], "anthropic")

    def test_v11_keeps_capability_unavailable_preflight_not_run_and_request_count_zero(self):
        self.require_audit_implementation()

        result = build_capability_audit(ROOT, self.revision)

        self.assertEqual(
            result["schema_version"],
            "joewrks.reviewer-runner-capability-audit/1.1",
        )
        self.assertEqual(result["real_backend_capability"], "UNAVAILABLE")
        self.assertEqual(result["runner_state"], "ISOLATION_CAPABILITY_UNAVAILABLE")
        self.assertEqual(result["backend_provisioning"], "REQUIRED")
        self.assertEqual(result["real_synthetic_preflight"], "NOT_RUN")
        self.assertEqual(result["real_provider_request_count"], 0)

    def test_v11_keeps_calibration_not_run_reliability_not_measured_and_v044_blocked(self):
        self.require_audit_implementation()

        result = build_capability_audit(ROOT, self.revision)

        self.assertEqual(
            result["schema_version"],
            "joewrks.reviewer-runner-capability-audit/1.1",
        )
        self.assertEqual(result["calibration_status"], "CALIBRATION_NOT_RUN")
        self.assertEqual(result["semantic_review_21_reliability"], "NOT_MEASURED")
        self.assertEqual(result["v044_status"], "BLOCKED")
        self.assertEqual(result["real_calibration_attempts"], 1)
        self.assertEqual(result["valid_real_calibration_runs"], 0)

    def test_v11_contains_no_environment_value_raw_workspace_or_credential_material(self):
        self.require_audit_implementation()
        secret = "do-not-serialize-this-anthropic-secret"
        workspace = "do-not-serialize-this-raw-workspace"
        environment = _EnvironmentAccessForbidden()
        with (
            patch.object(os, "environ", environment),
            patch.object(
                socket,
                "getaddrinfo",
                side_effect=AssertionError("audit performed DNS resolution"),
            ) as getaddrinfo,
            patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("audit opened a socket"),
            ) as create_connection,
            patch.object(
                http.client,
                "HTTPSConnection",
                side_effect=AssertionError("audit opened HTTPS"),
            ) as https_connection,
        ):
            document = canonical_audit_json(build_capability_audit(ROOT, self.revision))

        getaddrinfo.assert_not_called()
        create_connection.assert_not_called()
        https_connection.assert_not_called()
        decoded = json.loads(document)
        self.assertEqual(
            decoded["schema_version"],
            "joewrks.reviewer-runner-capability-audit/1.1",
        )
        self.assertEqual(decoded["provider_selected"], "anthropic")
        self.assertNotIn(secret, document)
        self.assertNotIn(workspace, document)
        self.assertFalse(
            {"environment", "credentials", "credential_values", "api_key"}
            .intersection(decoded)
        )

    def test_historical_v10_revision_and_frozen_evidence_remain_byte_exact(self):
        self.require_audit_implementation()
        evidence_path = (
            ROOT
            / "evals"
            / "post-m6-semantic-review-reliability-enablement"
            / "RUNNER_CAPABILITY_EVIDENCE.json"
        )

        document = canonical_audit_json(
            build_capability_audit(ROOT, self.historical_revision)
        ).encode("utf-8")

        self.assertEqual(document, evidence_path.read_bytes())

    def test_fake_or_injected_adapter_cannot_promote_capability(self):
        self.require_audit_implementation()
        from tests.reviewer_runner_support import DeterministicFakeBackend

        fake = DeterministicFakeBackend(b'{"result":"synthetic"}')
        result = build_capability_audit(
            ROOT,
            self.revision,
            registered_adapters=(fake,),
        )

        self.assertEqual(result, build_capability_audit(ROOT, self.revision))
        self.assertEqual(result["adapter_implementation"], "IMPLEMENTED")
        self.assertEqual(result["registered_real_adapter_count"], 1)
        self.assertEqual(result["provider_candidate"], "anthropic")
        self.assertEqual(result["provider_selected"], "anthropic")
        self.assertEqual(result["real_backend_capability"], "UNAVAILABLE")

    def test_invalid_injected_adapter_is_rejected_after_verified_registration_load(self):
        self.require_audit_implementation()

        with self.assertRaisesRegex(ValueError, "registered adapter must expose describe"):
            build_capability_audit(
                ROOT,
                self.revision,
                registered_adapters=(object(),),
            )

    def test_preseeded_private_package_fails_closed_and_is_removed(self):
        namespace = f"_audit_verified_reviewer_runner_{self.revision}"
        poisoned_package = types.ModuleType(namespace)
        poisoned_package.__package__ = namespace
        poisoned_package.__path__ = [str(SKILL_ROOT / "reviewer_runner")]
        poisoned_package.__spec__ = importlib.util.spec_from_loader(
            namespace,
            loader=None,
            is_package=True,
        )

        self.assert_private_namespace_collision_fails_closed("", poisoned_package)

    def test_preseeded_private_identity_fails_closed_and_is_removed(self):
        poisoned_identity = importlib.import_module("reviewer_runner.identity")

        self.assert_private_namespace_collision_fails_closed(
            ".identity",
            poisoned_identity,
        )

    def test_preseeded_private_backend_fails_closed_and_is_removed(self):
        poisoned_backend = importlib.import_module("reviewer_runner.backend")

        self.assert_private_namespace_collision_fails_closed(
            ".backend",
            poisoned_backend,
        )

    def test_preseeded_private_transitive_module_fails_closed_and_is_removed(self):
        namespace = f"_audit_verified_reviewer_runner_{self.revision}"
        poisoned_controller = types.ModuleType(f"{namespace}.controller")

        self.assert_private_namespace_collision_fails_closed(
            ".controller",
            poisoned_controller,
        )

    def test_private_verified_namespace_is_removed_after_successful_audit(self):
        namespace = f"_audit_verified_reviewer_runner_{self.revision}"

        result = build_capability_audit(ROOT, self.revision)

        self.assertEqual(result["runner_contract_version"], "joewrks.reviewer-runner/1.0")
        self.assertFalse(
            any(
                name == namespace or name.startswith(f"{namespace}.")
                for name in sys.modules
            ),
            "private verified-runner modules survived a successful load",
        )

    def test_injected_real_adapter_cannot_change_historical_v10_evidence(self):
        self.require_audit_implementation()
        from reviewer_runner.providers import REGISTERED_PRODUCTION_ADAPTERS

        expected = build_capability_audit(ROOT, self.historical_revision)
        result = build_capability_audit(
            ROOT,
            self.historical_revision,
            registered_adapters=REGISTERED_PRODUCTION_ADAPTERS,
        )

        self.assertEqual(result, expected)
        self.assertEqual(result["schema_version"], "joewrks.reviewer-runner-capability-audit/1.0")
        self.assertEqual(result["registered_real_adapter_count"], 0)

    def test_audit_contains_no_environment_values_or_credentials(self):
        self.require_audit_implementation()
        sentinel = "do-not-serialize-this-secret-value"
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": sentinel,
                "MOORCHEH_API_KEY": sentinel,
                "REVIEWER_ENDPOINT_TOKEN": sentinel,
            },
            clear=False,
        ):
            document = canonical_audit_json(
                build_capability_audit(ROOT, self.historical_revision)
            )

        decoded = json.loads(document)
        self.assertNotIn(sentinel, document)
        self.assertFalse(
            {"environment", "credentials", "credential_values", "api_key"}
            .intersection(decoded)
        )
        self.assertIsNone(decoded["provider_selected"])

    def test_audit_preserves_not_measured_v044_block_and_attempt_counters(self):
        self.require_audit_implementation()

        result = build_capability_audit(ROOT, self.revision)

        self.assertEqual(result["calibration_status"], "CALIBRATION_NOT_RUN")
        self.assertEqual(result["semantic_review_21_reliability"], "NOT_MEASURED")
        self.assertEqual(result["v044_status"], "BLOCKED")
        self.assertEqual(result["real_calibration_attempts"], 1)
        self.assertEqual(result["valid_real_calibration_runs"], 0)

    def test_frozen_product_semantic_review_and_m6_paths_are_unchanged(self):
        self.require_audit_implementation()
        self.assertEqual(
            IMPLEMENTATION_BASE_REVISION,
            "71ffc0a66618c11e2fe08a442df5fd2d67718f7b",
        )

        baseline = frozen_blob_map(ROOT, IMPLEMENTATION_BASE_REVISION)
        observed = frozen_blob_map(ROOT, self.revision)

        self.assertTrue(baseline)
        self.assertEqual(observed, baseline)

    def test_revision_without_complete_runner_inventory_cannot_claim_implemented(self):
        self.require_audit_implementation()

        with self.assertRaisesRegex(RuntimeError, "runner source inventory"):
            build_capability_audit(ROOT, IMPLEMENTATION_BASE_REVISION)

    def test_live_runner_source_must_be_clean_tracked_and_revision_exact(self):
        self.require_audit_implementation()
        import audit_reviewer_runner as audit_module

        real_git = audit_module._git
        runner_path = "skills/joewrks-product-definition/reviewer_runner"

        for status in (
            f" M {runner_path}/identity.py\0".encode("utf-8"),
            f"?? {runner_path}/extra.py\0".encode("utf-8"),
        ):
            with self.subTest(status=status):
                def dirty_git(repository, *arguments, binary=False):
                    if arguments[:3] == ("status", "--porcelain=v1", "-z"):
                        return status
                    return real_git(repository, *arguments, binary=binary)

                with patch.object(audit_module, "_git", side_effect=dirty_git):
                    with self.assertRaisesRegex(RuntimeError, "runner source"):
                        build_capability_audit(ROOT, self.revision)

        def incomplete_index_git(repository, *arguments, binary=False):
            result = real_git(repository, *arguments, binary=binary)
            if arguments[:3] == ("ls-files", "--stage", "-z"):
                records = result.rstrip(b"\0").split(b"\0")
                return b"\0".join(records[:-1]) + b"\0"
            return result

        with patch.object(audit_module, "_git", side_effect=incomplete_index_git):
            with self.assertRaisesRegex(RuntimeError, "runner source inventory"):
                build_capability_audit(ROOT, self.revision)

    def test_stat_stale_same_size_live_runner_edit_is_rejected_from_raw_bytes(self):
        self.require_audit_implementation()
        import audit_reviewer_runner as audit_module

        source_path = SKILL_ROOT / "reviewer_runner" / "identity.py"
        original_bytes = source_path.read_bytes()
        original_stat = source_path.stat()
        mutated_bytes = original_bytes.replace(
            b"joewrks.reviewer-runner/1.0",
            b"badwrks.reviewer-runner/1.0",
            1,
        )
        self.assertNotEqual(mutated_bytes, original_bytes)
        self.assertEqual(len(mutated_bytes), len(original_bytes))

        real_git = audit_module._git

        def stat_stale_git(repository, *arguments, binary=False):
            if arguments[:3] == ("status", "--porcelain=v1", "-z"):
                return b""
            return real_git(repository, *arguments, binary=binary)

        try:
            source_path.write_bytes(mutated_bytes)
            os.utime(
                source_path,
                ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
            )
            self.assertEqual(source_path.stat().st_size, original_stat.st_size)
            self.assertEqual(source_path.stat().st_mtime_ns, original_stat.st_mtime_ns)

            with patch.object(audit_module, "_git", side_effect=stat_stale_git):
                with self.assertRaisesRegex(RuntimeError, "live runner source"):
                    build_capability_audit(ROOT, self.revision)
        finally:
            source_path.write_bytes(original_bytes)
            os.utime(
                source_path,
                ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
            )

        self.assertEqual(source_path.read_bytes(), original_bytes)
        self.assertEqual(source_path.stat().st_mtime_ns, original_stat.st_mtime_ns)

    def test_stale_runner_bytecode_cannot_override_verified_source(self):
        self.require_audit_implementation()
        evidence_path = (
            ROOT
            / "evals"
            / "post-m6-semantic-review-reliability-enablement"
            / "RUNNER_CAPABILITY_EVIDENCE.json"
        )
        evidence = json.loads(evidence_path.read_bytes())
        identity_path = SKILL_ROOT / "reviewer_runner" / "identity.py"
        source_bytes = identity_path.read_bytes()
        source_stat = identity_path.stat()
        poisoned_bytes = source_bytes.replace(
            b"joewrks.reviewer-runner/1.0",
            b"badwrks.reviewer-runner/1.0",
            1,
        )
        self.assertNotEqual(poisoned_bytes, source_bytes)
        self.assertEqual(len(poisoned_bytes), len(source_bytes))

        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            cache_root = temporary_root / "external-bytecode-cache"
            poison_source = temporary_root / "identity.py"
            poison_source.write_bytes(poisoned_bytes)
            os.utime(
                poison_source,
                ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns),
            )

            previous_cache_prefix = sys.pycache_prefix
            try:
                sys.pycache_prefix = str(cache_root)
                cache_path = Path(importlib.util.cache_from_source(str(identity_path)))
            finally:
                sys.pycache_prefix = previous_cache_prefix
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            py_compile.compile(
                str(poison_source),
                cfile=str(cache_path),
                dfile=str(identity_path),
                doraise=True,
                invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP,
            )

            environment = os.environ.copy()
            environment.pop("PYTHONDONTWRITEBYTECODE", None)
            environment.pop("PYTHONPYCACHEPREFIX", None)
            launcher = (
                "import runpy,sys;"
                "sys.pycache_prefix=sys.argv[1];"
                "script=sys.argv[2];"
                "sys.argv=[script,*sys.argv[3:]];"
                "runpy.run_path(script,run_name='__main__')"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    launcher,
                    str(cache_root),
                    str(SCRIPTS_ROOT / "audit_reviewer_runner.py"),
                    "--repository",
                    str(ROOT),
                    "--revision",
                    evidence["implementation_code_commit"],
                    "--json",
                ],
                check=True,
                capture_output=True,
                env=environment,
            )

            self.assertEqual(completed.stdout, evidence_path.read_bytes())

    def test_cli_stdout_bytes_exactly_match_frozen_canonical_evidence(self):
        self.require_audit_implementation()
        evidence_path = (
            ROOT
            / "evals"
            / "post-m6-semantic-review-reliability-enablement"
            / "RUNNER_CAPABILITY_EVIDENCE.json"
        )
        evidence = json.loads(evidence_path.read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            cache_root = Path(directory) / "audit-bytecode-cache"
            environment = os.environ.copy()
            environment.pop("PYTHONDONTWRITEBYTECODE", None)
            environment.pop("PYTHONPYCACHEPREFIX", None)
            launcher = (
                "import runpy,sys,pkgutil,__future__;"
                "sys.pycache_prefix=sys.argv[1];"
                "script=sys.argv[2];"
                "sys.argv=[script,*sys.argv[3:]];"
                "runpy.run_path(script,run_name='__main__')"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    launcher,
                    str(cache_root),
                    str(SCRIPTS_ROOT / "audit_reviewer_runner.py"),
                    "--repository",
                    str(ROOT),
                    "--revision",
                    evidence["implementation_code_commit"],
                    "--json",
                ],
                check=True,
                capture_output=True,
                env=environment,
            )

            self.assertEqual(completed.stdout, evidence_path.read_bytes())
            self.assertEqual(
                list(Path(directory).rglob("*")),
                [],
                "read-only audit command created Python bytecode files",
            )

    def test_git_inspection_disables_optional_index_writes(self):
        self.require_audit_implementation()
        import audit_reviewer_runner as audit_module

        text_completed = subprocess.CompletedProcess([], 0, stdout="")
        with patch.object(
            audit_module.subprocess,
            "run",
            return_value=text_completed,
        ) as run:
            audit_module._git(ROOT, "status")

        command = run.call_args.args[0]
        self.assertEqual(command[:3], ["git", "--no-optional-locks", "-C"])

        binary_completed = subprocess.CompletedProcess([], 0, stdout=b"0" * 40 + b"\n")
        with patch.object(
            audit_module.subprocess,
            "run",
            return_value=binary_completed,
        ) as run:
            audit_module._git_blob_id(ROOT, b"source bytes")

        command = run.call_args.args[0]
        self.assertEqual(command[:3], ["git", "--no-optional-locks", "-C"])
        self.assertEqual(command[-2:], ["hash-object", "--stdin"])


if __name__ == "__main__":
    unittest.main()
