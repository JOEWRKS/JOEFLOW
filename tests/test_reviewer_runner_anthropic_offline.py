import ast
from contextlib import contextmanager
import dataclasses
import hashlib
import http.client
import importlib
import inspect
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
for path in (SKILL_ROOT, SKILL_ROOT / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:  # Task 7 RED must be a controlled missing-audit assertion, not an import error.
    from audit_reviewer_runner import build_anthropic_offline_guard_report
except ImportError:
    build_anthropic_offline_guard_report = None


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(ROOT), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_at(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@contextmanager
def _temporary_runner_repository():
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory)
        runner_target = (
            repository / "skills" / "joewrks-product-definition" / "reviewer_runner"
        )
        shutil.copytree(
            SKILL_ROOT / "reviewer_runner",
            runner_target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        for arguments in (
            ("init", "-q"),
            ("config", "user.email", "offline-test@example.invalid"),
            ("config", "user.name", "offline-test"),
            ("add", "."),
            ("commit", "-qm", "runner fixture"),
        ):
            _git_at(repository, *arguments)
        yield repository


def _commit_provider_registration(
    repository: Path,
    source: str,
    message: str,
) -> str:
    registration_path = (
        repository
        / "skills"
        / "joewrks-product-definition"
        / "reviewer_runner"
        / "providers"
        / "__init__.py"
    )
    registration_path.write_text(source, encoding="utf-8", newline="\n")
    _git_at(repository, "add", "--", registration_path.relative_to(repository).as_posix())
    _git_at(repository, "commit", "-qm", message)
    return _git_at(repository, "rev-parse", "HEAD")


def _commit_anthropic_source(
    repository: Path,
    source: str,
    message: str,
) -> str:
    source_path = (
        repository
        / "skills"
        / "joewrks-product-definition"
        / "reviewer_runner"
        / "providers"
        / "anthropic.py"
    )
    source_path.write_text(source, encoding="utf-8", newline="\n")
    _git_at(repository, "add", "--", source_path.relative_to(repository).as_posix())
    _git_at(repository, "commit", "-qm", message)
    return _git_at(repository, "rev-parse", "HEAD")


def _offline_globals() -> tuple[object, ...]:
    return (
        os.environ,
        socket.getaddrinfo,
        socket.socket,
        socket.create_connection,
        http.client.HTTPSConnection,
    )


def _restore_offline_globals(originals: tuple[object, ...]) -> None:
    (
        os.environ,
        socket.getaddrinfo,
        socket.socket,
        socket.create_connection,
        http.client.HTTPSConnection,
    ) = originals


class _CapturedStdout:
    def __init__(self):
        self.buffer = io.BytesIO()

    def write(self, value):
        return len(value)

    def flush(self):
        pass


class _CountingEnvironment(dict):
    def __init__(self, key: str, value: str):
        super().__init__({key: value})
        self.key = key
        self.reads: list[str] = []

    def __getitem__(self, key):
        if key == self.key:
            self.reads.append(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == self.key:
            self.reads.append(key)
        return super().get(key, default)


class _NeverCalledTransport:
    is_test_double = True

    def __init__(self):
        self.calls = []

    def post(self, body, *, api_key, timeout_seconds):
        self.calls.append((body, api_key, timeout_seconds))
        raise AssertionError("test transport must not be invoked")


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _request_bytes() -> bytes:
    from reviewer_runner.identity import RunIdentity, sha256_bytes
    from reviewer_runner.request import InputArtifact, build_canonical_request

    identity = RunIdentity(
        semantic_review_contract_version="joewrks.semantic-review/1.0",
        package_schema_version="joewrks.semantic-review-input/1.0",
        package_digest=sha256_bytes(b"package"),
        source_action_contract_hash=sha256_bytes(b"action-contract"),
        source_definition_digest=sha256_bytes(b"definition"),
        reviewer_id="reviewer-offline",
        review_run_id="run-offline",
        context_id="context-offline",
        cohort_id=None,
        case_id=None,
    )
    return build_canonical_request(
        identity,
        (
            InputArtifact("reviewer_brief", "text/markdown", b"Review only declared inputs."),
            InputArtifact("review_package", "application/json", b'{"package":true}'),
            InputArtifact("run_envelope", "application/json", b'{"run":true}'),
            InputArtifact("output_schema", "application/schema+json", b'{"type":"object"}'),
        ),
        controller_only_hashes={},
    ).content


def _ready_configuration(*, workspace_id: str = "offline-workspace"):
    from reviewer_runner.identity import sha256_bytes
    from reviewer_runner.providers.anthropic_admission import (
        AnthropicAdmissionEvidence,
        AnthropicProvisioningEvidence,
        AnthropicProvisioningStatus,
        anthropic_credential_readiness_evidence_sha256,
        build_anthropic_backend_configuration,
    )

    provisioning = AnthropicProvisioningEvidence(
        schema_version="joewrks.anthropic-provisioning-evidence/1.0",
        expected_anthropic_workspace_id_sha256=sha256_bytes(workspace_id.encode("utf-8")),
        workspace_key_scope="WORKSPACE_SCOPED",
        workspace_evidence_channel="MACHINE_READABLE",
        workspace_evidence_sha256=_digest("workspace-evidence"),
        retention_privacy_evidence_channel="CONTRACT_CONSOLE_OR_ADMINISTRATOR",
        retention_privacy_evidence_sha256=_digest("privacy-evidence"),
        retention_privacy_approval="ZDR_VERIFIED",
        inference_geo_evidence_sha256=_digest("geo-evidence"),
        model_entitlement_evidence_sha256=_digest("model-entitlement"),
        capacity_and_quota_evidence_sha256=_digest("quota-evidence"),
        spend_approval_evidence_sha256=_digest("spend-approval"),
        provider_policy_approval_evidence_sha256=_digest("provider-policy"),
        credential_readiness_evidence_sha256=None,
    )
    provisioning = dataclasses.replace(
        provisioning,
        credential_readiness_evidence_sha256=(
            anthropic_credential_readiness_evidence_sha256(provisioning)
        ),
    )
    configuration = build_anthropic_backend_configuration(
        AnthropicAdmissionEvidence(
            schema_version="joewrks.anthropic-admission-evidence/1.0",
            adapter_source_manifest_sha256=_digest("adapter-source"),
            local_conformance_evidence_sha256=_digest("local-conformance"),
            canonical_provider_body_sha256=_digest("canonical-provider-body"),
            provider_official_contract_sha256=_digest("official-contract"),
            local_capacity_measurement_sha256=_digest("local-capacity"),
            provisioning=provisioning,
        )
    )
    if configuration.provisioning_status is not AnthropicProvisioningStatus.READY_FOR_PREFLIGHT:
        raise AssertionError("offline fixture must be ready for preflight")
    return configuration


def _response(*, workspace_id: str = "offline-workspace"):
    from reviewer_runner.identity import canonical_json_bytes
    from reviewer_runner.providers.anthropic import AnthropicHttpResponse

    return AnthropicHttpResponse(
        status=200,
        headers=(
            ("request-id", "offline-request-001"),
            ("anthropic-workspace-id", workspace_id),
        ),
        body=canonical_json_bytes(
            {
                "id": "offline-message-001",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": '{"verdict":"ok"}'}],
                "model": "claude-sonnet-5",
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {
                    "input_tokens": 1,
                    "output_tokens": 1,
                    "service_tier": "standard",
                    "inference_geo": "us",
                },
            }
        ),
    )


class _RecordingTransport:
    is_test_double = True

    def __init__(self, response=None, error: Exception | None = None):
        self.response = response if response is not None else _response()
        self.error = error
        self.calls = []

    def post(self, body, *, api_key, timeout_seconds):
        self.calls.append((body, api_key, timeout_seconds))
        if self.error is not None:
            raise self.error
        return self.response


class _TransportResponse:
    def __init__(self, *, status=200, body=b"{}", read_error=None):
        self.status = status
        self.body = body
        self.read_error = read_error

    def getheaders(self):
        return ()

    def read(self, amount=-1):
        if self.read_error is not None:
            raise self.read_error
        return self.body


class _TransportConnection:
    def __init__(self, response=None, *, request_error=None, response_error=None):
        self.response = response if response is not None else _TransportResponse()
        self.request_error = request_error
        self.response_error = response_error
        self.requests = []
        self.response_reads = 0
        self.close_count = 0

    def request(self, method, path, body=None, headers=None):
        self.requests.append((method, path, body, headers))
        if self.request_error is not None:
            raise self.request_error

    def getresponse(self):
        self.response_reads += 1
        if self.response_error is not None:
            raise self.response_error
        return self.response

    def close(self):
        self.close_count += 1


class ReviewerRunnerAnthropicOfflineTests(unittest.TestCase):
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
        self._remove_provider_modules()
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
    def require_guard():
        assert build_anthropic_offline_guard_report is not None, (
            "build_anthropic_offline_guard_report is missing"
        )
        return build_anthropic_offline_guard_report

    @staticmethod
    def _remove_provider_modules():
        for name in tuple(sys.modules):
            if name == "reviewer_runner.providers" or name.startswith("reviewer_runner.providers."):
                sys.modules.pop(name, None)

    def _report(self):
        return self.require_guard()(ROOT, self.revision)

    def test_import_describe_registration_and_audit_never_resolve_dns_or_open_socket(self):
        guard = self.require_guard()
        environment = _CountingEnvironment("ANTHROPIC_API_KEY", "offline-fake-key")
        with (
            patch.object(os, "environ", environment),
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS")) as dns,
            patch.object(socket, "create_connection", side_effect=AssertionError("socket")) as connection,
            patch.object(http.client, "HTTPSConnection", side_effect=AssertionError("HTTPS")) as https,
        ):
            self._remove_provider_modules()
            providers = importlib.import_module("reviewer_runner.providers")
            descriptor = providers.REGISTERED_PRODUCTION_ADAPTERS[0].describe()
            report = guard(ROOT, self.revision)
        self.assertFalse(descriptor.identity.is_test_double)
        self.assertEqual(report["overall"], "PASS")
        self.assertEqual(environment.reads, [])
        dns.assert_not_called()
        connection.assert_not_called()
        https.assert_not_called()

        import audit_reviewer_runner as audit

        system_originals = (
            os.environ,
            socket.getaddrinfo,
            socket.socket,
            socket.create_connection,
            http.client.HTTPSConnection,
        )
        with _temporary_runner_repository() as repository:
            registration_path = (
                repository
                / "skills"
                / "joewrks-product-definition"
                / "reviewer_runner"
                / "providers"
                / "__init__.py"
            )
            original_registration = registration_path.read_text(encoding="utf-8")
            side_effects = {
                "environment": 'import os\nos.environ.get("TASK7_OFFLINE_CANARY")\n',
                "dns": 'import socket\nsocket.getaddrinfo("offline.invalid", 443)\n',
                "raw-socket": "import socket\nsocket.socket()\n",
                "create-connection": (
                    'import socket\nsocket.create_connection(("offline.invalid", 443))\n'
                ),
                "https": (
                    'import http.client\nhttp.client.HTTPSConnection("offline.invalid")\n'
                ),
            }
            external_environment = _CountingEnvironment(
                "TASK7_OFFLINE_CANARY", "present-but-inert"
            )
            external_dns = lambda *args, **kwargs: []
            external_socket = lambda *args, **kwargs: object()
            external_connection = lambda *args, **kwargs: object()
            external_https = lambda *args, **kwargs: object()
            with (
                patch.object(os, "environ", external_environment),
                patch.object(socket, "getaddrinfo", external_dns),
                patch.object(socket, "socket", external_socket),
                patch.object(socket, "create_connection", external_connection),
                patch.object(http.client, "HTTPSConnection", external_https),
            ):
                external_originals = (
                    os.environ,
                    socket.getaddrinfo,
                    socket.socket,
                    socket.create_connection,
                    http.client.HTTPSConnection,
                )
                for label, side_effect in side_effects.items():
                    revision = _commit_provider_registration(
                        repository,
                        side_effect + original_registration,
                        f"adversarial {label}",
                    )
                    with self.subTest(side_effect=label):
                        with patch.object(
                            audit,
                            "_SKILL_ROOT",
                            repository / "skills" / "joewrks-product-definition",
                        ):
                            with self.assertRaisesRegex(
                                RuntimeError, "offline guard prohibited"
                            ):
                                guard(repository, revision)
                        for observed, expected in zip(
                            (
                                os.environ,
                                socket.getaddrinfo,
                                socket.socket,
                                socket.create_connection,
                                http.client.HTTPSConnection,
                            ),
                            external_originals,
                            strict=True,
                        ):
                            self.assertIs(observed, expected)
        for observed, expected in zip(
            (
                os.environ,
                socket.getaddrinfo,
                socket.socket,
                socket.create_connection,
                http.client.HTTPSConnection,
            ),
            system_originals,
            strict=True,
        ):
            self.assertIs(observed, expected)

        concurrent_originals = _offline_globals()
        a_entered = threading.Event()
        release_a = threading.Event()
        a_exited = threading.Event()
        b_attempting = threading.Event()
        b_entered = threading.Event()
        observations: dict[str, object] = {}
        thread_errors: list[BaseException] = []

        def caller_a():
            try:
                barrier = audit._AnthropicOfflineBarrier()
                with barrier:
                    observations["a_blockers"] = _offline_globals()
                    a_entered.set()
                    if not release_a.wait(5):
                        raise AssertionError("caller A release was not signaled")
                a_exited.set()
            except BaseException as error:
                thread_errors.append(error)
                a_exited.set()

        def caller_b():
            try:
                if not a_entered.wait(5):
                    raise AssertionError("caller A never entered the barrier")
                b_attempting.set()
                barrier = audit._AnthropicOfflineBarrier()
                with barrier:
                    observations["b_originals"] = barrier._originals
                    observations["b_blockers"] = _offline_globals()
                    b_entered.set()
                    if not a_exited.wait(5):
                        raise AssertionError("caller A never exited the barrier")
                    observations["b_owned_after_a_exit"] = all(
                        observed is expected
                        for observed, expected in zip(
                            _offline_globals(),
                            observations["b_blockers"],
                            strict=True,
                        )
                    )
            except BaseException as error:
                thread_errors.append(error)
                b_entered.set()

        thread_a = threading.Thread(target=caller_a, name="task7-offline-a")
        thread_b = threading.Thread(target=caller_b, name="task7-offline-b")
        final_before_cleanup = None
        try:
            thread_a.start()
            self.assertTrue(a_entered.wait(5))
            thread_b.start()
            self.assertTrue(b_attempting.wait(5))
            observations["b_entered_while_a_owned"] = b_entered.wait(0.25)
            release_a.set()
            self.assertTrue(a_exited.wait(5))
            self.assertTrue(b_entered.wait(5))
            thread_a.join(5)
            thread_b.join(5)
            final_before_cleanup = _offline_globals()
        finally:
            release_a.set()
            thread_a.join(5)
            thread_b.join(5)
            _restore_offline_globals(concurrent_originals)

        self.assertFalse(thread_a.is_alive())
        self.assertFalse(thread_b.is_alive())
        self.assertEqual(thread_errors, [])
        self.assertFalse(observations["b_entered_while_a_owned"])
        for blockers in (observations["a_blockers"], observations["b_blockers"]):
            for observed, original in zip(blockers, concurrent_originals, strict=True):
                self.assertIsNot(observed, original)
        for observed, original in zip(
            observations["b_originals"], concurrent_originals, strict=True
        ):
            self.assertIs(observed, original)
        self.assertTrue(observations["b_owned_after_a_exit"])
        for observed, original in zip(
            final_before_cleanup, concurrent_originals, strict=True
        ):
            self.assertIs(observed, original)
        for observed, original in zip(
            _offline_globals(), concurrent_originals, strict=True
        ):
            self.assertIs(observed, original)

        nested_error = None
        try:
            with audit._AnthropicOfflineBarrier():
                try:
                    with audit._AnthropicOfflineBarrier():
                        pass
                except BaseException as error:
                    nested_error = error
        finally:
            _restore_offline_globals(concurrent_originals)
        self.assertIsInstance(nested_error, RuntimeError)
        self.assertRegex(str(nested_error), "reentrant")

        sentinel = ValueError("controlled barrier body failure")
        propagated = None
        try:
            with audit._AnthropicOfflineBarrier():
                raise sentinel
        except BaseException as error:
            propagated = error
        self.assertIs(propagated, sentinel)
        for observed, original in zip(
            _offline_globals(), concurrent_originals, strict=True
        ):
            self.assertIs(observed, original)

        tamper_error = None
        try:
            with audit._AnthropicOfflineBarrier():
                socket.socket = object()
        except BaseException as error:
            tamper_error = error
        finally:
            tamper_restored = _offline_globals()
            _restore_offline_globals(concurrent_originals)
        self.assertIsInstance(tamper_error, RuntimeError)
        self.assertRegex(str(tamper_error), "ownership")
        for observed, original in zip(
            tamper_restored, concurrent_originals, strict=True
        ):
            self.assertIs(observed, original)

        owner_barrier = audit._AnthropicOfflineBarrier()
        owner_barrier.__enter__()
        owner_thread_id = threading.get_ident()
        waiter_attempting = threading.Event()
        waiter_entered = threading.Event()
        release_waiter = threading.Event()
        waiter_errors: list[BaseException] = []

        def waiter():
            try:
                waiter_attempting.set()
                with audit._AnthropicOfflineBarrier():
                    waiter_entered.set()
                    if not release_waiter.wait(5):
                        raise AssertionError("tamper waiter release was not signaled")
            except BaseException as error:
                waiter_errors.append(error)
                waiter_entered.set()

        waiter_thread = threading.Thread(
            target=waiter,
            name="task7-offline-tamper-waiter",
            daemon=True,
        )
        counterfeit_owner = object()
        owner_tamper_error = None
        waiter_woke_without_test_cleanup = False
        globals_after_tampered_exit = None
        try:
            waiter_thread.start()
            self.assertTrue(waiter_attempting.wait(5))
            self.assertFalse(waiter_entered.wait(0.25))
            with audit._ANTHROPIC_OFFLINE_CONDITION:
                audit._ANTHROPIC_OFFLINE_ACTIVE_OWNER = counterfeit_owner
                audit._ANTHROPIC_OFFLINE_ACTIVE_THREAD_ID = owner_thread_id + 1
            try:
                owner_barrier.__exit__(None, None, None)
            except BaseException as error:
                owner_tamper_error = error
            globals_after_tampered_exit = _offline_globals()
            waiter_woke_without_test_cleanup = waiter_entered.wait(0.5)
        finally:
            if not waiter_woke_without_test_cleanup:
                with audit._ANTHROPIC_OFFLINE_CONDITION:
                    if audit._ANTHROPIC_OFFLINE_ACTIVE_OWNER is counterfeit_owner:
                        audit._ANTHROPIC_OFFLINE_ACTIVE_OWNER = None
                    if audit._ANTHROPIC_OFFLINE_ACTIVE_THREAD_ID == owner_thread_id + 1:
                        audit._ANTHROPIC_OFFLINE_ACTIVE_THREAD_ID = None
                    if (
                        getattr(audit, "_ANTHROPIC_OFFLINE_ACTIVE_CONTEXT", None)
                        is owner_barrier
                    ):
                        audit._ANTHROPIC_OFFLINE_ACTIVE_CONTEXT = None
                    audit._ANTHROPIC_OFFLINE_CONDITION.notify_all()
            self.assertTrue(waiter_entered.wait(5))
            release_waiter.set()
            waiter_thread.join(5)
            _restore_offline_globals(concurrent_originals)

        self.assertFalse(waiter_thread.is_alive())
        self.assertEqual(waiter_errors, [])
        self.assertIsInstance(owner_tamper_error, RuntimeError)
        self.assertRegex(str(owner_tamper_error), "ownership")
        self.assertTrue(waiter_woke_without_test_cleanup)
        for observed, original in zip(
            globals_after_tampered_exit, concurrent_originals, strict=True
        ):
            self.assertIs(observed, original)
        with audit._ANTHROPIC_OFFLINE_CONDITION:
            self.assertIsNone(audit._ANTHROPIC_OFFLINE_ACTIVE_OWNER)
            self.assertIsNone(audit._ANTHROPIC_OFFLINE_ACTIVE_THREAD_ID)

        legitimate_owner = audit._AnthropicOfflineBarrier()
        intruder = audit._AnthropicOfflineBarrier()
        with legitimate_owner:
            with audit._ANTHROPIC_OFFLINE_CONDITION:
                legitimate_token = audit._ANTHROPIC_OFFLINE_ACTIVE_OWNER
                legitimate_thread = audit._ANTHROPIC_OFFLINE_ACTIVE_THREAD_ID
            self.assertFalse(intruder._release_ownership())
            with audit._ANTHROPIC_OFFLINE_CONDITION:
                self.assertIs(audit._ANTHROPIC_OFFLINE_ACTIVE_OWNER, legitimate_token)
                self.assertEqual(
                    audit._ANTHROPIC_OFFLINE_ACTIVE_THREAD_ID,
                    legitimate_thread,
                )
        self.assertEqual(guard(ROOT, self.revision)["overall"], "PASS")

    def test_unexpected_real_named_credential_never_triggers_integration_execution(self):
        guard = self.require_guard()
        environment = _CountingEnvironment("ANTHROPIC_API_KEY", "offline-fake-key")
        with (
            patch.object(os, "environ", environment),
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS")) as dns,
            patch.object(socket, "create_connection", side_effect=AssertionError("socket")) as connection,
            patch.object(http.client, "HTTPSConnection", side_effect=AssertionError("HTTPS")) as https,
        ):
            self._remove_provider_modules()
            importlib.import_module("reviewer_runner.providers")
            report = guard(ROOT, self.revision)
        self.assertEqual(report["provider_mode"], "stdlib-direct-https")
        self.assertEqual(report["entry_points_provider_calls"], 0)
        self.assertEqual(environment.reads, [])
        dns.assert_not_called()
        connection.assert_not_called()
        https.assert_not_called()

    def test_only_invoke_can_read_anthropic_api_key_and_reads_it_once(self):
        self.require_guard()
        from reviewer_runner.providers.anthropic import AnthropicBackend

        reads = []
        transport = _RecordingTransport()
        backend = AnthropicBackend(
            _ready_configuration(),
            transport=transport,
            credential_reader=lambda name: reads.append(name) or "offline-fake-key",
        )
        backend.describe()
        self._report()
        self.assertEqual(reads, [])
        backend.invoke(_request_bytes(), timeout_seconds=1)
        self.assertEqual(reads, ["ANTHROPIC_API_KEY"])
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(self._report()["overall"], "PASS")

    def test_fake_key_is_absent_from_descriptor_response_event_audit_error_and_repr(self):
        self.require_guard()
        secret = "offline-fake-key-must-never-persist"
        from reviewer_runner.providers.anthropic import AnthropicBackend

        transport = _RecordingTransport()
        backend = AnthropicBackend(
            _ready_configuration(),
            transport=transport,
            credential_reader=lambda name: secret,
        )
        descriptor = backend.describe()
        response = backend.invoke(_request_bytes(), timeout_seconds=1)
        failing_backend = AnthropicBackend(
            _ready_configuration(),
            transport=_RecordingTransport(error=RuntimeError(secret)),
            credential_reader=lambda name: secret,
        )
        with self.assertRaises(Exception) as raised:
            failing_backend.invoke(_request_bytes(), timeout_seconds=1)
        observed = (
            json.dumps(self._report(), sort_keys=True),
            repr(descriptor),
            str(descriptor),
            repr(response),
            str(response),
            repr(response.events),
            str(response.events),
            repr(raised.exception),
            str(raised.exception),
        )
        self.assertTrue(all(secret not in value for value in observed))

    def test_raw_workspace_value_is_absent_from_persistable_objects(self):
        self.require_guard()
        workspace = "offline-raw-workspace-must-never-persist"
        from reviewer_runner.providers.anthropic import AnthropicBackend

        backend = AnthropicBackend(
            _ready_configuration(workspace_id=workspace),
            transport=_RecordingTransport(_response(workspace_id=workspace)),
            credential_reader=lambda name: "offline-fake-key",
        )
        descriptor = backend.describe()
        response = backend.invoke(_request_bytes(), timeout_seconds=1)
        persistable = (
            json.dumps(self._report(), sort_keys=True),
            repr(descriptor),
            str(descriptor),
            repr(response),
            str(response),
            repr(response.events),
            str(response.events),
        )
        self.assertTrue(all(workspace not in value for value in persistable))

    def test_source_import_graph_contains_no_sdk_requests_httpx_proxy_or_admin_client(self):
        self.require_guard()
        report = self._report()
        self.assertEqual(report["forbidden_imports"], [])
        self.assertEqual(report["provider_source_imports"], ["base64", "dataclasses", "hashlib", "http.client", "json", "os", "socket", "ssl", "typing"])

    def test_all_failure_classes_make_zero_or_one_request_and_zero_retries(self):
        self.require_guard()
        from reviewer_runner.backend import BackendInvocationError
        from reviewer_runner.providers.anthropic import StdlibAnthropicTransport

        cases = (
            ("request", _TransportConnection(request_error=OSError("request"))),
            ("response", _TransportConnection(response_error=EOFError("response"))),
            (
                "read",
                _TransportConnection(
                    _TransportResponse(read_error=TimeoutError("read"))
                ),
            ),
            ("http-408", _TransportConnection(_TransportResponse(status=408))),
            ("http-409", _TransportConnection(_TransportResponse(status=409))),
            ("http-429", _TransportConnection(_TransportResponse(status=429))),
            ("http-500", _TransportConnection(_TransportResponse(status=500))),
        )
        for label, connection in cases:
            factory_calls = []

            def factory(host, port, timeout, context, *, connection=connection):
                factory_calls.append((host, port, timeout, context))
                return connection

            with self.subTest(label=label):
                transport = StdlibAnthropicTransport(
                    test_only_connection_factory=factory
                )
                with self.assertRaises(BackendInvocationError):
                    transport.post(
                        b'{"request":true}',
                        api_key="offline-fake-key",
                        timeout_seconds=1,
                    )
                self.assertEqual(len(factory_calls), 1)
                self.assertEqual(len(connection.requests), 1)
                self.assertEqual(connection.close_count, 1)
        self.assertEqual(self._report()["request_retry_policy"], "ONE_REQUEST_ZERO_RETRIES")

        import audit_reviewer_runner as audit

        direct_request = """\
            connection.request(
                "POST",
                ANTHROPIC_PATH,
                body=body,
                headers={
                    "anthropic-version": ANTHROPIC_API_VERSION,
                    "connection": "close",
                    "content-type": "application/json",
                    "x-api-key": api_key,
                },
            )
"""
        request_in_comprehension = """\
            [
                connection.request(
                    "POST",
                    ANTHROPIC_PATH,
                    body=body,
                    headers={
                        "anthropic-version": ANTHROPIC_API_VERSION,
                        "connection": "close",
                        "content-type": "application/json",
                        "x-api-key": api_key,
                    },
                )
                for _ in range(2)
            ]
"""
        repeated_aliased_helper = """\
            def issue_request():
                connection.request(
                    "POST",
                    ANTHROPIC_PATH,
                    body=body,
                    headers={
                        "anthropic-version": ANTHROPIC_API_VERSION,
                        "connection": "close",
                        "content-type": "application/json",
                        "x-api-key": api_key,
                    },
                )

            request_alias = issue_request
            request_alias()
            request_alias()
"""
        direct_plus_method_alias = direct_request + """\
            send_again = connection.request
            send_again(
                "POST",
                ANTHROPIC_PATH,
                body=body,
                headers={
                    "anthropic-version": ANTHROPIC_API_VERSION,
                    "connection": "close",
                    "content-type": "application/json",
                    "x-api-key": api_key,
                },
            )
"""
        direct_plus_computed_getattr = direct_request + """\
            send_again = getattr(connection, "re" + "quest")
            send_again(
                "POST",
                ANTHROPIC_PATH,
                body=body,
                headers={
                    "anthropic-version": ANTHROPIC_API_VERSION,
                    "connection": "close",
                    "content-type": "application/json",
                    "x-api-key": api_key,
                },
            )
"""
        direct_plus_vars_type_lookup = direct_request + """\
            send_again = vars(type(connection))["request"]
            send_again(
                "POST",
                ANTHROPIC_PATH,
                body=body,
                headers={
                    "anthropic-version": ANTHROPIC_API_VERSION,
                    "connection": "close",
                    "content-type": "application/json",
                    "x-api-key": api_key,
                },
            )
"""
        with _temporary_runner_repository() as repository:
            source_path = (
                repository
                / "skills"
                / "joewrks-product-definition"
                / "reviewer_runner"
                / "providers"
                / "anthropic.py"
            )
            original_source = source_path.read_text(encoding="utf-8")
            self.assertEqual(original_source.count(direct_request), 1)
            adversarial_sources = {
                "request-in-comprehension": original_source.replace(
                    direct_request, request_in_comprehension
                ),
                "repeated-aliased-local-helper": original_source.replace(
                    direct_request, repeated_aliased_helper
                ),
                "direct-plus-method-alias": original_source.replace(
                    direct_request, direct_plus_method_alias
                ),
                "direct-plus-computed-getattr": original_source.replace(
                    direct_request, direct_plus_computed_getattr
                ),
                "direct-plus-vars-type-lookup": original_source.replace(
                    direct_request, direct_plus_vars_type_lookup
                ),
            }
            for label, source in adversarial_sources.items():
                revision = _commit_anthropic_source(
                    repository,
                    source,
                    label,
                )
                with self.subTest(request_policy=label):
                    with patch.object(
                        audit,
                        "_SKILL_ROOT",
                        repository / "skills" / "joewrks-product-definition",
                    ):
                        with self.assertRaisesRegex(
                            RuntimeError,
                            "one request with zero retries",
                        ):
                            self.require_guard()(repository, revision)

            _commit_anthropic_source(
                repository,
                original_source,
                "restore approved transport before runtime interception",
            )
            registration_prelude = """\
from .anthropic import AnthropicBackend, StdlibAnthropicTransport
from .anthropic_admission import (
    build_anthropic_backend_configuration,
    unprovisioned_anthropic_admission,
)
"""
            registration_suffix = """\

REGISTERED_PRODUCTION_ADAPTERS = (
    AnthropicBackend(
        build_anthropic_backend_configuration(unprovisioned_anthropic_admission())
    ),
)
__all__ = ("REGISTERED_PRODUCTION_ADAPTERS",)
"""
            module_post_replacement = registration_prelude + """\

_approved_post = StdlibAnthropicTransport.post


def _post_twice(self, body, *, api_key, timeout_seconds):
    _approved_post(
        self,
        body,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )
    return _approved_post(
        self,
        body,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )


StdlibAnthropicTransport.post = _post_twice
""" + registration_suffix
            class_getattribute_interception = registration_prelude + """\

_approved_getattribute = StdlibAnthropicTransport.__getattribute__


def _intercept_post(self, name):
    value = _approved_getattribute(self, name)
    if name != "post":
        return value

    def post_twice(body, *, api_key, timeout_seconds):
        value(
            body,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        return value(
            body,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )

    return post_twice


StdlibAnthropicTransport.__getattribute__ = _intercept_post
""" + registration_suffix
            runtime_interception_registrations = {
                "module-post-replacement": module_post_replacement,
                "class-getattribute-interception": class_getattribute_interception,
            }
            invoke_wrapper = """\

_approved_invoke = AnthropicBackend.invoke


def _invoke_twice(self, request_bytes, *, timeout_seconds):
    _approved_invoke(self, request_bytes, timeout_seconds=timeout_seconds)
    return _approved_invoke(self, request_bytes, timeout_seconds=timeout_seconds)


AnthropicBackend.invoke = _invoke_twice
"""
            invoke_interception = """\

_approved_getattribute = AnthropicBackend.__getattribute__


def _intercept_invoke(self, name):
    value = _approved_getattribute(self, name)
    if name != "invoke":
        return value

    def invoke_twice(request_bytes, *, timeout_seconds):
        value(request_bytes, timeout_seconds=timeout_seconds)
        return value(request_bytes, timeout_seconds=timeout_seconds)

    return invoke_twice


AnthropicBackend.__getattribute__ = _intercept_invoke
"""
            runtime_interception_registrations.update({
                "module-invoke-replacement": (
                    registration_prelude + invoke_wrapper + registration_suffix
                ),
                "backend-getattribute-interception": (
                    registration_prelude + invoke_interception + registration_suffix
                ),
            })
            for label, registration in runtime_interception_registrations.items():
                revision = _commit_provider_registration(
                    repository,
                    registration,
                    label,
                )
                with self.subTest(runtime_request_policy=label):
                    with patch.object(
                        audit,
                        "_SKILL_ROOT",
                        repository / "skills" / "joewrks-product-definition",
                    ):
                        try:
                            report = self.require_guard()(repository, revision)
                        except RuntimeError as error:
                            self.assertRegex(
                                str(error),
                                "one request with zero retries",
                            )
                        else:
                            self.assertNotEqual(
                                report["overall"],
                                "PASS",
                                f"{label} complete offline report falsely passed: {report!r}",
                            )

            # An unchanged callable identity also needs its approved source body.
            original_registration = registration_prelude + registration_suffix
            _commit_provider_registration(repository, original_registration, "restore registration")
            invoke_post = "            transport_response = self._transport.post(\n"
            self.assertEqual(original_source.count(invoke_post), 1)
            repeated_invoke_post = """\
            self._transport.post(
                projection.provider_body,
                api_key=api_key,
                timeout_seconds=timeout_seconds,
            )
""" + invoke_post
            revision = _commit_anthropic_source(
                repository,
                original_source.replace(invoke_post, repeated_invoke_post),
                "invoke issues two transport requests",
            )
            with self.subTest(runtime_request_policy="invoke-body-two-posts"):
                with patch.object(audit, "_SKILL_ROOT", repository / "skills" / "joewrks-product-definition"):
                    with self.assertRaisesRegex(RuntimeError, "one request with zero retries"):
                        self.require_guard()(repository, revision)

        # A helper-only change leaves invoke/post untouched but can add a request.
        with _temporary_runner_repository() as repository:
            provider_path = repository / "skills" / "joewrks-product-definition" / "reviewer_runner" / "providers" / "anthropic.py"
            source = provider_path.read_text(encoding="utf-8")
            helper_header = "def _validate_timeout(timeout_seconds: object) -> None:\n"
            self.assertEqual(source.count(helper_header), 1)
            revision = _commit_anthropic_source(
                repository,
                source.replace(helper_header, helper_header + (
                    "    StdlibAnthropicTransport().post(b'{}', api_key='offline-fixture', timeout_seconds=1)\n"
                )),
                "helper-only extra transport request",
            )
            with self.subTest(transitive_helper="committed-timeout-extra-request"):
                with patch.object(audit, "_SKILL_ROOT", repository / "skills" / "joewrks-product-definition"):
                    with self.assertRaisesRegex(RuntimeError, "one request with zero retries"):
                        self.require_guard()(repository, revision)

        original_capture = audit._SnapshotSourceFinder._capture_verified_export
        for mutation in ("replacement", "code", "defaults", "keyword-defaults"):
            def capture_then_mutate(finder, fullname, module, code):
                original_capture(finder, fullname, module, code)
                if not fullname.endswith(".providers.anthropic"):
                    return
                helper = module._validate_timeout

                def unexpected_helper(value):
                    raise AssertionError("audit must not execute a provider helper")

                if mutation == "replacement":
                    module._validate_timeout = unexpected_helper
                elif mutation == "code":
                    helper.__code__ = unexpected_helper.__code__
                elif mutation == "defaults":
                    helper.__defaults__ = (1,)
                else:
                    helper.__kwdefaults__ = {"unexpected": 1}

            with self.subTest(transitive_helper="post-load-" + mutation):
                with patch.object(audit._SnapshotSourceFinder, "_capture_verified_export", capture_then_mutate):
                    with self.assertRaisesRegex(RuntimeError, "one request with zero retries"):
                        self.require_guard()(ROOT, self.revision)

    def test_capability_audit_rejects_inherited_http_callables_mutated_after_capture(self):
        import audit_reviewer_runner as audit

        original_capture = audit._SnapshotSourceFinder._capture_verified_export
        for method_name in ("request", "getresponse", "close"):
            original_method = getattr(http.client.HTTPConnection, method_name)
            defining_class = next(
                candidate
                for candidate in http.client.HTTPSConnection.__mro__
                if method_name in candidate.__dict__
            )
            self.assertIs(defining_class, http.client.HTTPConnection)
            self.assertIs(
                getattr(http.client.HTTPSConnection, method_name),
                original_method,
            )
            mutation_calls = []

            def capture_then_mutate(
                finder,
                fullname,
                module,
                code,
                *,
                method_name=method_name,
            ):
                original_capture(finder, fullname, module, code)
                if not fullname.endswith(".providers.anthropic"):
                    return

                def mutated_http_callable(connection, *args, **kwargs):
                    mutation_calls.append((connection, args, kwargs))
                    raise AssertionError("audit must not execute an inherited HTTP callable")

                setattr(http.client.HTTPConnection, method_name, mutated_http_callable)
                self.assertIs(
                    getattr(http.client.HTTPSConnection, method_name),
                    mutated_http_callable,
                )

            try:
                with self.subTest(inherited_http_callable=method_name):
                    with patch.object(
                        audit._SnapshotSourceFinder,
                        "_capture_verified_export",
                        capture_then_mutate,
                    ):
                        with self.assertRaisesRegex(
                            RuntimeError,
                            "HTTP transport dependency does not prove one request with zero retries",
                        ):
                            audit.build_capability_audit(ROOT, self.revision)
                    self.assertEqual(mutation_calls, [])
            finally:
                setattr(http.client.HTTPConnection, method_name, original_method)
            self.assertIs(
                getattr(http.client.HTTPSConnection, method_name),
                original_method,
            )

    def test_capability_audit_rechecks_inherited_http_callables_after_descriptor_callbacks(self):
        import audit_reviewer_runner as audit

        original_verify = audit._SnapshotSourceFinder.verify_anthropic_transport_binding
        for method_name in ("request", "getresponse", "close"):
            original_method = getattr(http.client.HTTPConnection, method_name)
            mutation_calls = []
            mutation_installed = []

            def verify_then_mutate(
                finder,
                module,
                registered,
                *,
                method_name=method_name,
            ):
                result = original_verify(finder, module, registered)
                if mutation_installed:
                    return result

                def mutated_http_callable(connection, *args, **kwargs):
                    mutation_calls.append((connection, args, kwargs))
                    raise AssertionError("audit must not execute an inherited HTTP callable")

                setattr(http.client.HTTPConnection, method_name, mutated_http_callable)
                mutation_installed.append(mutated_http_callable)
                self.assertIs(
                    getattr(http.client.HTTPSConnection, method_name),
                    mutated_http_callable,
                )
                return result

            try:
                with self.subTest(inherited_http_callable=method_name):
                    with patch.object(
                        audit._SnapshotSourceFinder,
                        "verify_anthropic_transport_binding",
                        verify_then_mutate,
                    ):
                        with self.assertRaisesRegex(
                            RuntimeError,
                            "HTTP transport dependency does not prove one request with zero retries",
                        ):
                            audit.build_capability_audit(ROOT, self.revision)
                    self.assertEqual(len(mutation_installed), 1)
                    self.assertEqual(mutation_calls, [])
            finally:
                setattr(http.client.HTTPConnection, method_name, original_method)
            self.assertIs(
                getattr(http.client.HTTPSConnection, method_name),
                original_method,
            )

    def test_offline_guard_rechecks_original_https_class_hidden_by_barrier(self):
        import audit_reviewer_runner as audit

        saved_https_connection = http.client.HTTPSConnection
        original_capture = audit._SnapshotSourceFinder._capture_verified_export
        original_verify = audit._SnapshotSourceFinder.verify_anthropic_transport_binding
        missing = object()

        for timing in ("after-capture", "after-initial-binding"):
            original_descriptor = saved_https_connection.__dict__.get("request", missing)
            mutation_calls = []
            mutation_installed = []

            def install_mutation():
                if mutation_installed:
                    return

                def replacement_request(connection, *args, **kwargs):
                    mutation_calls.append((connection, args, kwargs))
                    raise AssertionError("audit must not execute an HTTPS callable")

                self.assertIsNot(http.client.HTTPSConnection, saved_https_connection)
                saved_https_connection.request = replacement_request
                mutation_installed.append(replacement_request)
                probe = object.__new__(saved_https_connection)
                self.assertIs(probe.request.__func__, replacement_request)

            def capture_then_mutate(finder, fullname, module, code):
                original_capture(finder, fullname, module, code)
                if fullname.endswith(".providers.anthropic"):
                    install_mutation()

            def verify_then_mutate(finder, module, registered):
                result = original_verify(finder, module, registered)
                install_mutation()
                return result

            patch_target = (
                "_capture_verified_export"
                if timing == "after-capture"
                else "verify_anthropic_transport_binding"
            )
            replacement = (
                capture_then_mutate
                if timing == "after-capture"
                else verify_then_mutate
            )
            try:
                with self.subTest(timing=timing):
                    with patch.object(
                        audit._SnapshotSourceFinder,
                        patch_target,
                        replacement,
                    ):
                        with self.assertRaisesRegex(
                            RuntimeError,
                            "HTTP transport dependency does not prove one request with zero retries",
                        ):
                            self.require_guard()(ROOT, self.revision)
                    self.assertEqual(len(mutation_installed), 1)
                    self.assertEqual(mutation_calls, [])
            finally:
                if original_descriptor is missing:
                    delattr(saved_https_connection, "request")
                else:
                    setattr(saved_https_connection, "request", original_descriptor)

    def test_capability_audit_rejects_http_descriptor_binding_mutation(self):
        import audit_reviewer_runner as audit

        http_connection = http.client.HTTPConnection
        https_connection = http.client.HTTPSConnection
        original_capture = audit._SnapshotSourceFinder._capture_verified_export
        original_verify = audit._SnapshotSourceFinder.verify_anthropic_transport_binding

        for timing in ("after-capture", "after-initial-binding"):
            original_descriptor = http_connection.__dict__["request"]
            mutation_installed = []

            def install_mutation():
                if mutation_installed:
                    return
                http_connection.request = staticmethod(original_descriptor)
                mutation_installed.append(original_descriptor)
                probe = https_connection(
                    "offline.invalid",
                    port=443,
                    context=object(),
                )
                self.assertIs(https_connection.request, original_descriptor)
                self.assertIs(probe.request, original_descriptor)

            def capture_then_mutate(finder, fullname, module, code):
                original_capture(finder, fullname, module, code)
                if fullname.endswith(".providers.anthropic"):
                    install_mutation()

            def verify_then_mutate(finder, module, registered):
                result = original_verify(finder, module, registered)
                install_mutation()
                return result

            patch_target = (
                "_capture_verified_export"
                if timing == "after-capture"
                else "verify_anthropic_transport_binding"
            )
            replacement = (
                capture_then_mutate
                if timing == "after-capture"
                else verify_then_mutate
            )
            try:
                with self.subTest(timing=timing):
                    with patch.object(
                        audit._SnapshotSourceFinder,
                        patch_target,
                        replacement,
                    ):
                        with self.assertRaisesRegex(
                            RuntimeError,
                            "HTTP transport dependency does not prove one request with zero retries",
                        ):
                            audit.build_capability_audit(ROOT, self.revision)
                    self.assertEqual(len(mutation_installed), 1)
            finally:
                http_connection.request = original_descriptor
            self.assertIs(https_connection.request, original_descriptor)

    def test_capability_audit_rejects_http_instance_dispatch_mutations(self):
        import audit_reviewer_runner as audit

        http_connection = http.client.HTTPConnection
        https_connection = http.client.HTTPSConnection
        original_capture = audit._SnapshotSourceFinder._capture_verified_export
        original_verify = audit._SnapshotSourceFinder.verify_anthropic_transport_binding
        original_class_request = https_connection.request
        missing = object()

        for timing in ("after-capture", "after-initial-binding"):
            for mechanism in ("getattribute", "init", "setattr"):
                mutation_calls = []
                mutation_installed = []
                attribute_name = "__" + mechanism + "__"
                original_attribute = http_connection.__dict__.get(attribute_name, missing)

                def install_mutation(*, mechanism=mechanism, attribute_name=attribute_name):
                    if mutation_installed:
                        return

                    def replacement_request(connection, *args, **kwargs):
                        mutation_calls.append((connection, args, kwargs))
                        raise AssertionError("audit must not execute an inherited HTTP callable")

                    if mechanism == "getattribute":
                        inherited_getattribute = http_connection.__getattribute__

                        def mutated_getattribute(connection, name):
                            if name == "request":
                                return replacement_request.__get__(connection, type(connection))
                            return inherited_getattribute(connection, name)

                        setattr(http_connection, attribute_name, mutated_getattribute)
                    elif mechanism == "init":
                        inherited_init = http_connection.__init__

                        def mutated_init(connection, *args, **kwargs):
                            inherited_init(connection, *args, **kwargs)
                            object.__setattr__(
                                connection,
                                "request",
                                replacement_request.__get__(connection, type(connection)),
                            )

                        setattr(http_connection, attribute_name, mutated_init)
                    elif mechanism == "setattr":
                        inherited_setattr = http_connection.__setattr__

                        def mutated_setattr(connection, name, value):
                            inherited_setattr(connection, name, value)
                            if name == "host":
                                inherited_setattr(
                                    connection,
                                    "request",
                                    replacement_request.__get__(connection, type(connection)),
                                )

                        setattr(http_connection, attribute_name, mutated_setattr)
                    mutation_installed.append(replacement_request)
                    probe = https_connection(
                        "offline.invalid",
                        port=443,
                        context=object(),
                    )
                    self.assertIs(https_connection.request, original_class_request)
                    self.assertIs(probe.request.__func__, replacement_request)

                def capture_then_mutate(finder, fullname, module, code):
                    original_capture(finder, fullname, module, code)
                    if fullname.endswith(".providers.anthropic"):
                        install_mutation()

                def verify_then_mutate(finder, module, registered):
                    result = original_verify(finder, module, registered)
                    install_mutation()
                    return result

                patch_target = (
                    "_capture_verified_export"
                    if timing == "after-capture"
                    else "verify_anthropic_transport_binding"
                )
                replacement = (
                    capture_then_mutate
                    if timing == "after-capture"
                    else verify_then_mutate
                )
                try:
                    with self.subTest(timing=timing, mechanism=mechanism):
                        with patch.object(
                            audit._SnapshotSourceFinder,
                            patch_target,
                            replacement,
                        ):
                            with self.assertRaisesRegex(
                                RuntimeError,
                                "HTTP transport dependency does not prove one request with zero retries",
                            ):
                                audit.build_capability_audit(ROOT, self.revision)
                        self.assertEqual(len(mutation_installed), 1)
                        self.assertEqual(mutation_calls, [])
                finally:
                    if original_attribute is missing:
                        delattr(http_connection, attribute_name)
                    else:
                        setattr(http_connection, attribute_name, original_attribute)
                self.assertIs(https_connection.request, original_class_request)

    def test_capability_audit_rejects_http_instance_new_mutation_in_isolated_process(self):
        script = r"""
import http.client
from pathlib import Path
import socket
import sys

repository = Path(sys.argv[1])
revision = sys.argv[2]
skill_root = Path(sys.argv[3])
sys.path.insert(0, str(skill_root / "scripts"))
sys.path.insert(0, str(skill_root))
import audit_reviewer_runner as audit

network_calls = []


def forbidden_network(*args, **kwargs):
    network_calls.append((args, kwargs))
    raise AssertionError("network access is prohibited")


socket.getaddrinfo = forbidden_network
socket.socket = forbidden_network
socket.create_connection = forbidden_network
http_connection = http.client.HTTPConnection
https_connection = http.client.HTTPSConnection
original_class_request = https_connection.request
original_capture = audit._SnapshotSourceFinder._capture_verified_export
original_verify = audit._SnapshotSourceFinder.verify_anthropic_transport_binding
installed = []
replacement_calls = []


def install_mutation():
    if installed:
        return

    def replacement_request(connection, *args, **kwargs):
        replacement_calls.append((connection, args, kwargs))
        raise AssertionError("audit must not execute an inherited HTTP callable")

    def mutated_new(connection_type, *args, **kwargs):
        connection = object.__new__(connection_type)
        object.__setattr__(
            connection,
            "request",
            replacement_request.__get__(connection, connection_type),
        )
        return connection

    http_connection.__new__ = staticmethod(mutated_new)
    installed.append(replacement_request)
    probe = https_connection("offline.invalid", port=443, context=object())
    assert https_connection.request is original_class_request
    assert probe.request.__func__ is replacement_request


def capture_then_mutate(finder, fullname, module, code):
    original_capture(finder, fullname, module, code)
    if fullname.endswith(".providers.anthropic"):
        install_mutation()


def verify_then_mutate(finder, module, registered):
    result = original_verify(finder, module, registered)
    install_mutation()
    return result


timing = sys.argv[4]
if timing == "after-capture":
    audit._SnapshotSourceFinder._capture_verified_export = capture_then_mutate
else:
    audit._SnapshotSourceFinder.verify_anthropic_transport_binding = verify_then_mutate

try:
    audit.build_capability_audit(repository, revision)
except RuntimeError as error:
    if "HTTP transport dependency does not prove one request with zero retries" not in str(error):
        raise
    assert len(installed) == 1
    assert replacement_calls == []
    assert network_calls == []
    print("NETWORK_CALLS=0")
else:
    print("NOT_CAUGHT")
    raise SystemExit(3)
"""
        for timing in ("after-capture", "after-initial-binding"):
            with self.subTest(timing=timing):
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        script,
                        str(ROOT),
                        self.revision,
                        str(SKILL_ROOT),
                        timing,
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    completed.stdout + completed.stderr,
                )
                self.assertEqual(completed.stdout, "NETWORK_CALLS=0\n")

    def test_test_transport_descriptor_is_ineligible_and_preflight_does_not_invoke(self):
        self.require_guard()
        from reviewer_runner.identity import CapabilityClass
        from reviewer_runner.providers.anthropic import AnthropicBackend
        from reviewer_runner.preflight import (
            build_preflight_freshness,
            classify_backend_eligibility,
            run_isolation_preflight,
        )

        transport = _NeverCalledTransport()
        backend = AnthropicBackend(
            _ready_configuration(),
            transport=transport,
        )
        descriptor = backend.describe()
        self.assertEqual(classify_backend_eligibility(descriptor), CapabilityClass.UNTESTED)
        result = run_isolation_preflight(
            backend,
            freshness=build_preflight_freshness(descriptor),
            nonce_source=lambda label: label.encode("ascii"),
        )
        self.assertEqual(result.classification, CapabilityClass.UNTESTED)
        self.assertIsNone(result.response_sha256)
        self.assertEqual(transport.calls, [])

        import audit_reviewer_runner as audit

        counterfeit_registration = """\
from .anthropic import AnthropicBackend as _VerifiedAnthropicBackend
from .anthropic_admission import (
    build_anthropic_backend_configuration,
    unprovisioned_anthropic_admission,
)


class AnthropicBackend:
    def __init__(self):
        self._delegate = _VerifiedAnthropicBackend(
            build_anthropic_backend_configuration(unprovisioned_anthropic_admission())
        )

    def describe(self):
        return self._delegate.describe()


REGISTERED_PRODUCTION_ADAPTERS = (AnthropicBackend(),)
__all__ = ("REGISTERED_PRODUCTION_ADAPTERS",)
"""
        mutated_export_registration = """\
from . import anthropic as _anthropic_module
from .anthropic import AnthropicBackend as _VerifiedAnthropicBackend
from .anthropic_admission import (
    build_anthropic_backend_configuration,
    unprovisioned_anthropic_admission,
)


class AnthropicBackend:
    def __init__(self):
        self._delegate = _VerifiedAnthropicBackend(
            build_anthropic_backend_configuration(unprovisioned_anthropic_admission())
        )

    def describe(self):
        return self._delegate.describe()


_anthropic_module.AnthropicBackend = AnthropicBackend
REGISTERED_PRODUCTION_ADAPTERS = (AnthropicBackend(),)
__all__ = ("REGISTERED_PRODUCTION_ADAPTERS",)
"""
        with _temporary_runner_repository() as repository:
            registrations = {
                "counterfeit-class": counterfeit_registration,
                "mutated-sibling-export": mutated_export_registration,
            }
            for label, registration in registrations.items():
                revision = _commit_provider_registration(
                    repository,
                    registration,
                    label,
                )
                with self.subTest(registration=label):
                    with patch.object(
                        audit,
                        "_SKILL_ROOT",
                        repository / "skills" / "joewrks-product-definition",
                    ):
                        with self.assertRaisesRegex(
                            RuntimeError, "exact verified AnthropicBackend"
                        ):
                            self.require_guard()(repository, revision)

            dependency_prelude = """\
from . import anthropic as _anthropic_module
from .anthropic import AnthropicBackend
from .anthropic_admission import (
    build_anthropic_backend_configuration,
    unprovisioned_anthropic_admission,
)

_backend = AnthropicBackend(
    build_anthropic_backend_configuration(unprovisioned_anthropic_admission())
)
_original_descriptor = _backend.describe()
"""
            dependency_mutations = {
                "post-construction-connection-factory": (
                    "_backend._transport._test_only_connection_factory = lambda *args: None\n"
                ),
                "post-construction-credential-reader": (
                    "_backend._credential_reader = lambda name: 'offline-fake-key'\n"
                ),
                "module-http-replacement": """\
class _FakeHTTP:
    class client:
        HTTPSConnection = staticmethod(lambda *args, **kwargs: None)

_anthropic_module.http = _FakeHTTP
""",
            }
            for label, mutation in dependency_mutations.items():
                revision = _commit_provider_registration(
                    repository,
                    dependency_prelude + mutation + """\
assert _backend.describe() is _original_descriptor
assert not _backend.describe().identity.is_test_double
REGISTERED_PRODUCTION_ADAPTERS = (_backend,)
__all__ = ("REGISTERED_PRODUCTION_ADAPTERS",)
""",
                    label,
                )
                with self.subTest(mutable_dependency=label):
                    with patch.object(audit, "_SKILL_ROOT", repository / "skills" / "joewrks-product-definition"):
                        with self.assertRaisesRegex(RuntimeError, "verified Anthropic|one request with zero retries"):
                            self.require_guard()(repository, revision)

            describe_mutations = dict(dependency_mutations)
            describe_mutations["invoke-replacement"] = """\
AnthropicBackend.invoke = lambda self, request_bytes, *, timeout_seconds: (
    _approved_invoke(self, request_bytes, timeout_seconds=timeout_seconds),
    _approved_invoke(self, request_bytes, timeout_seconds=timeout_seconds),
)[1]
"""
            for label, mutation in describe_mutations.items():
                registration = dependency_prelude + """\
_approved_invoke = AnthropicBackend.invoke
_original_describe = AnthropicBackend.describe


def _mutating_describe(self):
    descriptor = _original_describe(self)
""" + "\n".join("    " + line for line in mutation.splitlines()) + """\

    return descriptor


AnthropicBackend.describe = _mutating_describe
REGISTERED_PRODUCTION_ADAPTERS = (_backend,)
__all__ = ("REGISTERED_PRODUCTION_ADAPTERS",)
"""
                revision = _commit_provider_registration(
                    repository, registration, "describe mutates " + label
                )
                with self.subTest(describe_mutation=label):
                    with patch.object(audit, "_SKILL_ROOT", repository / "skills" / "joewrks-product-definition"):
                        with self.assertRaisesRegex(RuntimeError, "one request with zero retries"):
                            self.require_guard()(repository, revision)

    def test_no_provider_call_exists_in_unit_test_or_audit_entry_points(self):
        guard = self.require_guard()
        import audit_reviewer_runner as audit

        environment = _CountingEnvironment("ANTHROPIC_API_KEY", "offline-fake-key")
        captured_stdout = _CapturedStdout()
        with (
            patch.object(os, "environ", environment),
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS")) as dns,
            patch.object(socket, "socket", side_effect=AssertionError("raw socket")) as raw_socket,
            patch.object(socket, "create_connection", side_effect=AssertionError("socket")) as connection,
            patch.object(http.client, "HTTPSConnection", side_effect=AssertionError("HTTPS")) as https,
        ):
            report = guard(ROOT, self.revision)
            capability_audit = audit.build_capability_audit(ROOT, self.revision)
            with patch.object(sys, "stdout", captured_stdout):
                exit_code = audit.main(
                    [
                        "--repository",
                        str(ROOT),
                        "--revision",
                        self.revision,
                        "--json",
                    ]
                )
        self.assertEqual(report["entry_points_provider_calls"], 0)
        self.assertEqual(capability_audit["real_provider_request_count"], 0)
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            json.loads(captured_stdout.buffer.getvalue()),
            capability_audit,
        )
        self.assertEqual(environment.reads, [])
        dns.assert_not_called()
        raw_socket.assert_not_called()
        connection.assert_not_called()
        https.assert_not_called()

        audit_tree = ast.parse(
            (SKILL_ROOT / "scripts" / "audit_reviewer_runner.py").read_bytes()
        )
        audit_entry_points = {
            node.name: node
            for node in audit_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name
            in {"build_anthropic_offline_guard_report", "build_capability_audit", "main"}
        }
        self.assertEqual(
            set(audit_entry_points),
            {"build_anthropic_offline_guard_report", "build_capability_audit", "main"},
        )
        for name, entry_point in audit_entry_points.items():
            with self.subTest(audit_entry_point=name):
                calls = tuple(
                    node for node in ast.walk(entry_point) if isinstance(node, ast.Call)
                )
                self.assertFalse(
                    any(
                        isinstance(call.func, ast.Attribute)
                        and call.func.attr == "invoke"
                        for call in calls
                    )
                )
                self.assertFalse(
                    any(
                        isinstance(call.func, ast.Name)
                        and call.func.id == "StdlibAnthropicTransport"
                        for call in calls
                    )
                )

        test_tree = ast.parse(Path(__file__).read_bytes())
        for call in (
            node for node in ast.walk(test_tree) if isinstance(node, ast.Call)
        ):
            called_name = (
                call.func.id
                if isinstance(call.func, ast.Name)
                else call.func.attr
                if isinstance(call.func, ast.Attribute)
                else None
            )
            if called_name == "AnthropicBackend":
                self.assertIn("transport", {keyword.arg for keyword in call.keywords})
            if called_name == "StdlibAnthropicTransport":
                self.assertIn(
                    "test_only_connection_factory",
                    {keyword.arg for keyword in call.keywords},
                )

        module_entry_points = tuple(
            node for node in test_tree.body if isinstance(node, ast.If)
        )
        self.assertEqual(len(module_entry_points), 1)
        self.assertFalse(
            any(
                isinstance(node, ast.Attribute) and node.attr == "invoke"
                for node in ast.walk(module_entry_points[0])
            )
        )

    def test_required_capability_tuple_and_generic_runner_interfaces_are_unchanged(self):
        self.require_guard()
        from reviewer_runner.backend import (
            REQUIRED_CAPABILITIES,
            BackendDescriptor,
            BackendEvent,
            BackendResponse,
            CapabilityObservation,
            ToollessInferenceBackend,
        )
        from reviewer_runner.identity import (
            BackendIdentity,
            InputCommitment,
            ResponseIdentity,
            RunIdentity,
            RunnerReceipt,
        )
        from reviewer_runner.request import CanonicalRequest, InputArtifact

        expected_capabilities = (
            "stateless_fresh_request",
            "no_continuation_id",
            "no_reviewer_memory",
            "no_tools",
            "no_retrieval",
            "no_web_or_browser",
            "no_connectors_or_mcp",
            "no_host_filesystem",
            "no_code_execution",
            "no_file_by_reference",
            "immutable_model_or_deployment_identity",
            "immutable_inference_settings",
            "sufficient_payload_capacity",
            "exact_structured_output",
            "controller_only_authentication",
            "accepted_retention_and_privacy",
            "request_response_commitments",
        )
        report = self._report()
        self.assertEqual(report["required_capabilities_sha256"], report["expected_required_capabilities_sha256"])
        self.assertEqual(REQUIRED_CAPABILITIES, expected_capabilities)

        authority_revision = "ab95074704af0e93248d56344d6a220dfec88a93"
        expected_blobs = {
            "skills/joewrks-product-definition/reviewer_runner/backend.py": (
                "100644:5c6c6883b0f27077762f9a240684ffcb6bfa369e"
            ),
            "skills/joewrks-product-definition/reviewer_runner/identity.py": (
                "100644:f476b1da1d075d1495880483d40fdad2b49f1424"
            ),
            "skills/joewrks-product-definition/reviewer_runner/request.py": (
                "100644:8b64bff1f2c6315b8b16d585b10886fe8585739f"
            ),
        }
        source_paths = tuple(expected_blobs)
        _git("merge-base", "--is-ancestor", authority_revision, self.revision)
        for revision in (authority_revision, self.revision):
            records = {}
            for line in _git("ls-tree", "-r", revision, "--", *source_paths).splitlines():
                metadata, path = line.split("\t", 1)
                mode, object_type, object_id = metadata.split(" ")
                self.assertEqual(object_type, "blob")
                records[path] = f"{mode}:{object_id}"
            self.assertEqual(records, expected_blobs)

        describe_signature = inspect.signature(ToollessInferenceBackend.describe)
        self.assertEqual(tuple(describe_signature.parameters), ("self",))
        self.assertIs(
            describe_signature.parameters["self"].kind,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        self.assertIs(
            describe_signature.parameters["self"].default,
            inspect.Parameter.empty,
        )
        self.assertIs(describe_signature.return_annotation, BackendDescriptor)

        invoke_signature = inspect.signature(ToollessInferenceBackend.invoke)
        self.assertEqual(
            tuple(invoke_signature.parameters),
            ("self", "request_bytes", "timeout_seconds"),
        )
        self.assertEqual(
            tuple(
                parameter.kind
                for parameter in invoke_signature.parameters.values()
            ),
            (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ),
        )
        self.assertTrue(
            all(
                parameter.default is inspect.Parameter.empty
                for parameter in invoke_signature.parameters.values()
            )
        )
        self.assertIs(invoke_signature.parameters["request_bytes"].annotation, bytes)
        self.assertIs(invoke_signature.parameters["timeout_seconds"].annotation, int)
        self.assertIs(invoke_signature.return_annotation, BackendResponse)

        expected_dataclass_fields = {
            RunIdentity: (
                "semantic_review_contract_version",
                "package_schema_version",
                "package_digest",
                "source_action_contract_hash",
                "source_definition_digest",
                "reviewer_id",
                "review_run_id",
                "context_id",
                "cohort_id",
                "case_id",
            ),
            BackendIdentity: (
                "backend_kind",
                "adapter_id",
                "adapter_version",
                "endpoint_identity",
                "deployment_identity",
                "model_revision_identity",
                "model_identity_stability",
                "inference_settings_sha256",
                "retention_policy_identity",
                "privacy_policy_identity",
                "is_test_double",
            ),
            InputCommitment: ("logical_role", "media_type", "byte_count", "sha256"),
            ResponseIdentity: (
                "provider_request_id",
                "request_sha256",
                "reviewer_id",
                "review_run_id",
                "context_id",
                "backend_identity_sha256",
                "response_count",
                "raw_response_byte_count",
                "raw_response_sha256",
                "parsed_output_sha256",
            ),
            RunnerReceipt: (
                "state",
                "run_identity",
                "backend_identity",
                "permitted_input_inventory",
                "request_sha256",
                "capability_preflight_sha256",
                "isolation_receipt_sha256",
                "response_identity",
                "receipt_sha256",
            ),
            CapabilityObservation: (
                "capability",
                "classification",
                "method",
                "evidence_sha256",
            ),
            BackendDescriptor: ("identity", "max_request_bytes", "observations"),
            BackendEvent: ("kind", "metadata_sha256"),
            BackendResponse: (
                "raw_bytes",
                "provider_request_id",
                "request_sha256",
                "reviewer_id",
                "review_run_id",
                "context_id",
                "backend_identity_sha256",
                "response_count",
                "continuation_id",
                "previous_response_id",
                "events",
            ),
            InputArtifact: ("logical_role", "media_type", "content"),
            CanonicalRequest: ("content", "sha256", "inventory"),
        }
        for dataclass_type, expected_fields in expected_dataclass_fields.items():
            with self.subTest(dataclass_type=dataclass_type.__name__):
                fields = dataclasses.fields(dataclass_type)
                self.assertEqual(tuple(field.name for field in fields), expected_fields)
                self.assertTrue(dataclass_type.__dataclass_params__.frozen)
                self.assertTrue(
                    all(
                        field.default is dataclasses.MISSING
                        and field.default_factory is dataclasses.MISSING
                        for field in fields
                    )
                )
        self.assertEqual(InputArtifact.__slots__, ("logical_role", "media_type", "content"))
        self.assertEqual(CanonicalRequest.__slots__, ("content", "sha256", "inventory"))


if __name__ == "__main__":
    unittest.main()
