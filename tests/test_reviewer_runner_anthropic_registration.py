import http.client
import importlib
import os
import socket
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS_ROOT = SKILL_ROOT / "scripts"
for path in (SKILL_ROOT, SCRIPTS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(ROOT), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


class _EnvironmentReadForbidden(dict):
    def __getitem__(self, key):
        raise AssertionError(f"registration read environment key {key!r}")

    def get(self, key, default=None):
        raise AssertionError(f"registration read environment key {key!r}")


class _NoopTransport:
    def post(self, body, *, api_key, timeout_seconds):
        raise AssertionError("test transport must not be invoked")


class ReviewerRunnerAnthropicRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.revision = _git("rev-parse", "HEAD")

    def tearDown(self):
        self._remove_live_provider_modules()

    @staticmethod
    def _remove_live_provider_modules() -> None:
        for name in tuple(sys.modules):
            if name == "reviewer_runner.providers" or name.startswith(
                "reviewer_runner.providers."
            ):
                sys.modules.pop(name, None)

    def _load_live_registration_module(self):
        self._remove_live_provider_modules()
        importlib.invalidate_caches()
        return importlib.import_module("reviewer_runner.providers")

    def _require_registration(self, module):
        self.assertTrue(
            hasattr(module, "REGISTERED_PRODUCTION_ADAPTERS"),
            "Task 5 registration is missing",
        )
        return module.REGISTERED_PRODUCTION_ADAPTERS

    def test_registration_contains_exactly_one_anthropic_backend(self):
        module = self._load_live_registration_module()
        registered = self._require_registration(module)

        from reviewer_runner.providers.anthropic import AnthropicBackend

        self.assertIs(type(registered), tuple)
        self.assertEqual(len(registered), 1)
        self.assertIs(type(registered[0]), AnthropicBackend)

    def test_registered_adapter_is_non_test_but_preflight_ineligible_while_unprovisioned(self):
        module = self._load_live_registration_module()
        registered = self._require_registration(module)

        from reviewer_runner.identity import CapabilityClass
        from reviewer_runner.preflight import classify_backend_eligibility

        descriptor = registered[0].describe()
        self.assertFalse(descriptor.identity.is_test_double)
        self.assertEqual(
            classify_backend_eligibility(descriptor),
            CapabilityClass.UNAVAILABLE,
        )

    def test_registration_import_reads_no_environment_and_opens_no_network(self):
        with (
            patch.object(os, "environ", _EnvironmentReadForbidden()),
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS")) as dns,
            patch.object(socket, "create_connection", side_effect=AssertionError("socket")) as connection,
            patch.object(http.client, "HTTPSConnection", side_effect=AssertionError("HTTPS")) as https,
        ):
            module = self._load_live_registration_module()
            registered = self._require_registration(module)

        self.assertEqual(len(registered), 1)
        dns.assert_not_called()
        connection.assert_not_called()
        https.assert_not_called()

    def test_registration_has_no_discovery_router_fallback_or_second_provider(self):
        module = self._load_live_registration_module()
        registered = self._require_registration(module)

        self.assertEqual(module.__all__, ("REGISTERED_PRODUCTION_ADAPTERS",))
        self.assertIs(type(registered), tuple)
        self.assertEqual(len(registered), 1)
        self.assertFalse(hasattr(module, "register"))
        self.assertFalse(hasattr(module, "discover"))
        self.assertFalse(hasattr(module, "router"))
        self.assertFalse(hasattr(module, "fallback"))

    def test_audit_snapshot_loader_reads_exact_provider_modules_from_target_revision(self):
        import audit_reviewer_runner as audit

        self.assertTrue(
            hasattr(audit, "_load_verified_snapshot_registration"),
            "Task 5 verified registration loader is missing",
        )
        snapshot = audit._verify_runner_source_binding(ROOT, self.revision)
        registered = audit._load_verified_snapshot_registration(
            ROOT.resolve(),
            self.revision,
            snapshot,
        )

        self.assertIs(type(registered), tuple)
        self.assertEqual(len(registered), 1)
        self.assertEqual(type(registered[0]).__name__, "AnthropicBackend")
        self.assertEqual(
            type(registered[0]).__module__,
            f"_audit_verified_reviewer_runner_{self.revision}.providers.anthropic",
        )

    def test_revision_without_provider_package_retains_empty_registration(self):
        import audit_reviewer_runner as audit

        self.assertTrue(
            hasattr(audit, "_load_verified_snapshot_registration"),
            "Task 5 verified registration loader is missing",
        )
        baseline_revision = audit.IMPLEMENTATION_BASE_REVISION
        registered = audit._load_verified_snapshot_registration(
            ROOT.resolve(),
            baseline_revision,
            {},
        )

        self.assertEqual(registered, ())

    def test_injected_transport_registration_cannot_count_as_authoritative(self):
        import audit_reviewer_runner as audit
        registration = self._load_live_registration_module()
        self._require_registration(registration)
        from reviewer_runner.providers.anthropic import AnthropicBackend
        from reviewer_runner.providers.anthropic_admission import (
            build_anthropic_backend_configuration,
            unprovisioned_anthropic_admission,
        )

        test_adapter = AnthropicBackend(
            build_anthropic_backend_configuration(unprovisioned_anthropic_admission()),
            transport=_NoopTransport(),
        )
        snapshot = audit._verify_runner_source_binding(ROOT, self.revision)
        identity_module, backend_module = audit._load_verified_runner_api(
            ROOT.resolve(),
            self.revision,
            snapshot,
        )

        self.assertTrue(test_adapter.describe().identity.is_test_double)
        self.assertEqual(
            audit._real_adapter_count(
                (test_adapter,),
                identity_module,
                backend_module,
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
