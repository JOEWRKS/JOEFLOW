import dataclasses
import hashlib
import http.client
import importlib
import inspect
import json
import os
import socket
import subprocess
import sys
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


class _CountingEnvironment(dict):
    def __init__(self, key: str, value: str):
        super().__init__({key: value})
        self.key = key
        self.reads: list[str] = []

    def __getitem__(self, key):
        self.reads.append(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
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

    def tearDown(self):
        self._remove_provider_modules()

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

    def test_no_provider_call_exists_in_unit_test_or_audit_entry_points(self):
        guard = self.require_guard()
        with (
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS")) as dns,
            patch.object(socket, "create_connection", side_effect=AssertionError("socket")) as connection,
            patch.object(http.client, "HTTPSConnection", side_effect=AssertionError("HTTPS")) as https,
        ):
            report = guard(ROOT, self.revision)
        self.assertEqual(report["entry_points_provider_calls"], 0)
        dns.assert_not_called()
        connection.assert_not_called()
        https.assert_not_called()

    def test_required_capability_tuple_and_generic_runner_interfaces_are_unchanged(self):
        self.require_guard()
        from reviewer_runner.backend import REQUIRED_CAPABILITIES, ToollessInferenceBackend

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
        self.assertEqual(tuple(inspect.signature(ToollessInferenceBackend.describe).parameters), ("self",))
        self.assertEqual(tuple(inspect.signature(ToollessInferenceBackend.invoke).parameters), ("self", "request_bytes", "timeout_seconds"))


if __name__ == "__main__":
    unittest.main()
