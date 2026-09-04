import json
import os
import subprocess
import sys
import tempfile
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
        ["git", "-C", str(ROOT), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


class ReviewerRunnerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.revision = _git("rev-parse", "HEAD")
        cls.tree = _git("rev-parse", "HEAD^{tree}")

    def require_audit_implementation(self):
        self.assertIsNotNone(
            build_capability_audit,
            "audit_reviewer_runner implementation is missing",
        )
        self.assertIsNotNone(canonical_audit_json)
        self.assertIsNotNone(frozen_blob_map)

    def test_no_registered_real_adapter_reports_unavailable_and_calibration_not_run(self):
        self.require_audit_implementation()

        result = build_capability_audit(ROOT, self.revision)

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
                "implementation_code_commit": self.revision,
                "implementation_code_tree": self.tree,
            },
        )

    def test_fake_backend_is_excluded_from_observed_pass(self):
        self.require_audit_implementation()
        from tests.reviewer_runner_support import DeterministicFakeBackend

        fake = DeterministicFakeBackend(b'{"result":"synthetic"}')
        result = build_capability_audit(
            ROOT,
            self.revision,
            registered_adapters=(fake,),
        )

        self.assertEqual(result["registered_real_adapter_count"], 0)
        self.assertEqual(result["real_backend_capability"], "UNAVAILABLE")
        self.assertEqual(result["runner_state"], "ISOLATION_CAPABILITY_UNAVAILABLE")
        self.assertFalse(result["fake_backend_authoritative"])

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
                build_capability_audit(ROOT, self.revision)
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

        completed = subprocess.CompletedProcess([], 0, stdout="")
        with patch.object(
            audit_module.subprocess,
            "run",
            return_value=completed,
        ) as run:
            audit_module._git(ROOT, "status")

        command = run.call_args.args[0]
        self.assertEqual(command[:3], ["git", "--no-optional-locks", "-C"])


if __name__ == "__main__":
    unittest.main()
