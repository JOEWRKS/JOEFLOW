import http.client
import importlib
import os
import socket
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

    def setUp(self):
        self._prior_provider_modules = {
            name: module for name, module in sys.modules.items()
            if name == "reviewer_runner.providers" or name.startswith("reviewer_runner.providers.")
        }
        self._provider_parent = sys.modules.get("reviewer_runner")
        self._missing_provider_attribute = object()
        self._prior_provider_attribute = (
            vars(self._provider_parent).get("providers", self._missing_provider_attribute)
            if self._provider_parent is not None else self._missing_provider_attribute
        )

    def tearDown(self):
        self._remove_live_provider_modules()
        sys.modules.update(self._prior_provider_modules)
        if self._provider_parent is not None:
            if self._prior_provider_attribute is self._missing_provider_attribute:
                vars(self._provider_parent).pop("providers", None)
            else:
                self._provider_parent.providers = self._prior_provider_attribute
            self.assertIs(
                vars(self._provider_parent).get("providers", self._missing_provider_attribute),
                self._prior_provider_attribute,
            )
        restored = {
            name: module for name, module in sys.modules.items()
            if name == "reviewer_runner.providers" or name.startswith("reviewer_runner.providers.")
        }
        self.assertEqual(set(restored), set(self._prior_provider_modules))
        for name, module in self._prior_provider_modules.items():
            self.assertIs(restored[name], module)

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
        historical_revision = "0b754bdc2502be35a7f657275f17fe117e8c49bd"
        snapshot = audit._verify_runner_source_binding(ROOT, historical_revision)
        self.assertNotIn(
            "skills/joewrks-product-definition/reviewer_runner/providers/__init__.py",
            snapshot,
        )
        registered = audit._load_verified_snapshot_registration(
            ROOT.resolve(),
            historical_revision,
            snapshot,
        )

        self.assertEqual(registered, ())

    def test_current_provider_revision_rejects_empty_or_partial_snapshot(self):
        import audit_reviewer_runner as audit

        snapshot = audit._verify_runner_source_binding(ROOT, self.revision)
        registration_source = (
            "skills/joewrks-product-definition/reviewer_runner/providers/__init__.py"
        )
        for incomplete_snapshot in (
            {},
            {registration_source: snapshot[registration_source]},
        ):
            with self.subTest(snapshot=tuple(incomplete_snapshot)):
                with self.assertRaisesRegex(RuntimeError, "provider source snapshot"):
                    audit._load_verified_snapshot_registration(
                        ROOT.resolve(),
                        self.revision,
                        incomplete_snapshot,
                    )

    def test_absolute_public_runner_import_from_verified_provider_fails_and_restores_modules(self):
        import audit_reviewer_runner as audit

        importlib.import_module("reviewer_runner.controller")
        original_public_modules = {
            name: module
            for name, module in sys.modules.items()
            if name == "reviewer_runner" or name.startswith("reviewer_runner.")
        }
        source_root = "skills/joewrks-product-definition/reviewer_runner"
        fixture_sources = {
            f"{source_root}/__init__.py": b"",
            f"{source_root}/identity.py": b"",
            f"{source_root}/backend.py": b"",
            f"{source_root}/request.py": b"",
            f"{source_root}/providers/__init__.py": (
                b"from .. import backend, identity, request\n"
                b"from . import anthropic, anthropic_admission\n"
                b"import reviewer_runner.controller\n"
                b"REGISTERED_PRODUCTION_ADAPTERS = ()\n"
            ),
            f"{source_root}/providers/anthropic.py": b"",
            f"{source_root}/providers/anthropic_admission.py": b"",
        }
        try:
            with tempfile.TemporaryDirectory() as directory:
                repository = Path(directory)
                for relative_source, source in fixture_sources.items():
                    target = repository.joinpath(*relative_source.split("/"))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source)
                for arguments in (
                    ("init", "-q"),
                    ("config", "user.email", "snapshot-test@example.invalid"),
                    ("config", "user.name", "snapshot-test"),
                    ("add", "."),
                    ("commit", "-qm", "absolute public import fixture"),
                ):
                    subprocess.run(
                        ["git", "-C", str(repository), *arguments],
                        check=True,
                        capture_output=True,
                    )
                revision = subprocess.run(
                    ["git", "-C", str(repository), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                snapshot = {
                    relative_source: subprocess.run(
                        ["git", "-C", str(repository), "show", f"{revision}:{relative_source}"],
                        check=True,
                        capture_output=True,
                    ).stdout
                    for relative_source in fixture_sources
                }

                with self.assertRaisesRegex(RuntimeError, "absolute public import"):
                    audit._load_verified_snapshot_registration(
                        repository,
                        revision,
                        snapshot,
                    )

            restored_public_modules = {
                name: module
                for name, module in sys.modules.items()
                if name == "reviewer_runner" or name.startswith("reviewer_runner.")
            }
            self.assertEqual(set(restored_public_modules), set(original_public_modules))
            for name, module in original_public_modules.items():
                self.assertIs(restored_public_modules[name], module)
        finally:
            for name in tuple(sys.modules):
                if name == "reviewer_runner" or name.startswith("reviewer_runner."):
                    sys.modules.pop(name, None)
            sys.modules.update(original_public_modules)

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
