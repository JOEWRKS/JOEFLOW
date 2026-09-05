import dataclasses
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.backend import BackendInvocationError
from reviewer_runner.identity import CapabilityClass, RunIdentity, canonical_json_bytes, sha256_bytes
from reviewer_runner.request import InputArtifact, build_canonical_request
from reviewer_runner.response import freeze_validate_bind_response
from reviewer_runner.providers import anthropic as module
from reviewer_runner.providers.anthropic_admission import (
    AnthropicAdmissionEvidence,
    AnthropicProvisioningEvidence,
    AnthropicProvisioningStatus,
    build_anthropic_backend_configuration,
    anthropic_credential_readiness_evidence_sha256,
    unprovisioned_anthropic_admission,
)


def _digest(label):
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _run_identity():
    return RunIdentity(
        semantic_review_contract_version="joewrks.semantic-review/1.0",
        package_schema_version="joewrks.semantic-review-input/1.0",
        package_digest=sha256_bytes(b"package"),
        source_action_contract_hash=sha256_bytes(b"action-contract"),
        source_definition_digest=sha256_bytes(b"definition"),
        reviewer_id="reviewer-001",
        review_run_id="run-001",
        context_id="context-001",
        cohort_id=None,
        case_id=None,
    )


def _request_bytes():
    return build_canonical_request(
        _run_identity(),
        (
            InputArtifact("reviewer_brief", "text/markdown", b"Review only declared inputs."),
            InputArtifact("review_package", "application/json", b'{"package":true}'),
            InputArtifact("run_envelope", "application/json", b'{"run":true}'),
            InputArtifact("output_schema", "application/schema+json", b'{"type":"object"}'),
        ),
        controller_only_hashes={},
    ).content


def _ready_configuration(*, workspace_id="workspace-001"):
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
        credential_readiness_evidence_sha256=anthropic_credential_readiness_evidence_sha256(provisioning),
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
        raise AssertionError("test fixture must compile READY_FOR_PREFLIGHT")
    return configuration


def _message(*, text='{\n "verdict":"ok"\n}\n', **changes):
    envelope = {
        "id": "msg-001",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "model": "claude-sonnet-5",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 4,
            "service_tier": "standard",
            "inference_geo": "us",
        },
    }
    envelope.update(changes)
    return canonical_json_bytes(envelope)


class _FakeTransport:
    is_test_double = True

    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, body, *, api_key, timeout_seconds):
        self.calls.append((body, api_key, timeout_seconds))
        return self.response


class ReviewerRunnerAnthropicResponseTests(unittest.TestCase):
    def backend(self, transport=None, credential_reader=None, configuration=None):
        backend_type = getattr(module, "AnthropicBackend", None)
        self.assertIsNotNone(backend_type, "AnthropicBackend must bind validated provider responses")
        return backend_type(
            configuration or _ready_configuration(),
            transport=transport,
            credential_reader=credential_reader,
        )

    def response(self, *, body=None, headers=None, status=200):
        response_type = module.AnthropicHttpResponse
        return response_type(
            status=status,
            headers=headers or (("request-id", "request-001"), ("anthropic-workspace-id", "workspace-001")),
            body=_message() if body is None else body,
        )

    def test_unprovisioned_invoke_returns_backend_provisioning_required_before_credential_or_transport(self):
        calls = []
        transport = _FakeTransport(self.response())
        backend = self.backend(
            transport=transport,
            credential_reader=lambda name: calls.append(name) or "sk-ant-test-secret",
            configuration=build_anthropic_backend_configuration(unprovisioned_anthropic_admission()),
        )
        required_type = getattr(module, "AnthropicProvisioningRequired", None)
        self.assertIsNotNone(required_type, "unprovisioned invocation must have a controlled error")
        with self.assertRaises(required_type) as raised:
            backend.invoke(_request_bytes(), timeout_seconds=5)
        self.assertEqual(raised.exception.code, "BACKEND_PROVISIONING_REQUIRED")
        self.assertEqual(calls, [])
        self.assertEqual(transport.calls, [])

    def test_missing_or_empty_api_key_fails_before_transport_without_echo(self):
        for key in (None, ""):
            with self.subTest(key=key):
                transport = _FakeTransport(self.response())
                backend = self.backend(transport, credential_reader=lambda name, key=key: key)
                with self.assertRaises(BackendInvocationError) as raised:
                    backend.invoke(_request_bytes(), timeout_seconds=5)
                self.assertEqual(raised.exception.code, "NO_RESPONSE")
                self.assertNotIn("ANTHROPIC_API_KEY", str(raised.exception))
                self.assertEqual(transport.calls, [])

    def test_valid_message_returns_exact_text_utf8_bytes_without_strip_or_reserialization(self):
        text = '{\n  "verdict" : "ok"\n}\n'
        transport = _FakeTransport(self.response(body=_message(text=text)))
        backend = self.backend(transport, credential_reader=lambda name: "sk-ant-test-secret")
        result = backend.invoke(_request_bytes(), timeout_seconds=5)
        self.assertEqual(result.raw_bytes, text.encode("utf-8", errors="strict"))
        self.assertEqual(result.provider_request_id, "request-001")
        self.assertEqual(len(transport.calls), 1)

    def test_request_id_is_nonempty_server_header_and_workspace_hash_matches_commitment(self):
        backend = self.backend(
            _FakeTransport(self.response()), credential_reader=lambda name: "sk-ant-test-secret"
        )
        result = backend.invoke(_request_bytes(), timeout_seconds=5)
        self.assertEqual(result.provider_request_id, "request-001")
        self.assertEqual(result.response_count, 1)
        self.assertIsNone(result.continuation_id)
        self.assertIsNone(result.previous_response_id)

    def test_missing_duplicate_or_mismatched_request_and_workspace_headers_fail_closed(self):
        cases = (
            (("anthropic-workspace-id", "workspace-001"),),
            (("request-id", "request-001"),),
            (("request-id", "request-001"), ("request-id", "request-002"), ("anthropic-workspace-id", "workspace-001")),
            (("request-id", "request-001"), ("anthropic-workspace-id", "workspace-001"), ("anthropic-workspace-id", "workspace-001")),
            (("request-id", "request-001"), ("anthropic-workspace-id", "other-workspace")),
        )
        for headers in cases:
            with self.subTest(headers=headers):
                backend = self.backend(
                    _FakeTransport(self.response(headers=headers)),
                    credential_reader=lambda name: "sk-ant-test-secret",
                )
                with self.assertRaises(BackendInvocationError) as raised:
                    backend.invoke(_request_bytes(), timeout_seconds=5)
                self.assertEqual(raised.exception.code, "NO_RESPONSE")

    def test_wrong_model_role_type_message_id_or_stop_reason_fails_closed(self):
        cases = (
            {"model": "other-model"}, {"role": "user"}, {"type": "other"},
            {"id": ""}, {"stop_reason": "max_tokens"}, {"stop_sequence": "stop"},
        )
        for changes in cases:
            with self.subTest(changes=changes):
                backend = self.backend(
                    _FakeTransport(self.response(body=_message(**changes))),
                    credential_reader=lambda name: "sk-ant-test-secret",
                )
                with self.assertRaises(BackendInvocationError):
                    backend.invoke(_request_bytes(), timeout_seconds=5)

    def test_zero_multiple_or_nonfinal_text_blocks_fail_closed(self):
        cases = (
            [], [{"type": "text", "text": "{}"}, {"type": "text", "text": "{}"}],
            [{"type": "text", "text": "{}"}, {"type": "thinking", "thinking": "hidden"}],
        )
        for content in cases:
            with self.subTest(content=content):
                backend = self.backend(
                    _FakeTransport(self.response(body=_message(content=content))),
                    credential_reader=lambda name: "sk-ant-test-secret",
                )
                with self.assertRaises(BackendInvocationError):
                    backend.invoke(_request_bytes(), timeout_seconds=5)

    def test_tool_server_tool_refusal_truncation_and_unexpected_active_blocks_fail_closed(self):
        cases = (
            [{"type": "tool_use", "id": "tool-001", "name": "x", "input": {}}],
            [{"type": "server_tool_use", "id": "tool-001", "name": "x", "input": {}}],
            [{"type": "refusal", "refusal": "no"}],
            [{"type": "unexpected_active_block", "data": "x"}, {"type": "text", "text": "{}"}],
        )
        for content in cases:
            with self.subTest(content=content):
                backend = self.backend(
                    _FakeTransport(self.response(body=_message(content=content, stop_reason="end_turn"))),
                    credential_reader=lambda name: "sk-ant-test-secret",
                )
                with self.assertRaises(BackendInvocationError):
                    backend.invoke(_request_bytes(), timeout_seconds=5)
        backend = self.backend(
            _FakeTransport(self.response(body=_message(stop_reason="max_tokens"))),
            credential_reader=lambda name: "sk-ant-test-secret",
        )
        with self.assertRaises(BackendInvocationError):
            backend.invoke(_request_bytes(), timeout_seconds=5)

    def test_thinking_and_redacted_thinking_are_metadata_only_before_one_final_text(self):
        content = [
            {"type": "thinking", "thinking": "private chain"},
            {"type": "redacted_thinking", "data": "encrypted"},
            {"type": "text", "text": '{"ok":true}\n'},
        ]
        backend = self.backend(
            _FakeTransport(self.response(body=_message(content=content))),
            credential_reader=lambda name: "sk-ant-test-secret",
        )
        self.assertEqual(backend.invoke(_request_bytes(), timeout_seconds=5).raw_bytes, b'{"ok":true}\n')

    def test_response_event_hash_binds_only_sanitized_closed_metadata(self):
        body = _message()
        transport = _FakeTransport(self.response(body=body))
        backend = self.backend(transport, credential_reader=lambda name: "sk-ant-test-secret")
        result = backend.invoke(_request_bytes(), timeout_seconds=5)
        expected = {
            "schema_version": "joewrks.anthropic-response-event/1.0",
            "http_body_byte_count": len(body),
            "http_body_sha256": sha256_bytes(body),
            "message_id": "msg-001",
            "model": "claude-sonnet-5",
            "stop_reason": "end_turn",
            "content_block_types": ["text"],
            "usage": {"input_tokens": 10, "output_tokens": 4, "service_tier": "standard", "inference_geo": "us"},
            "inference_geo": "us",
            "provider_request_body_sha256": sha256_bytes(_request_bytes()),
            "provider_request_id_sha256": sha256_bytes(b"request-001"),
            "anthropic_workspace_id_sha256": sha256_bytes(b"workspace-001"),
        }
        # The provider-body commitment is checked below from the actual fake call;
        # it cannot be derived by serializing the semantic request.
        expected["provider_request_body_sha256"] = sha256_bytes(transport.calls[0][0])
        self.assertEqual(result.events[0].metadata_sha256, sha256_bytes(canonical_json_bytes(expected)))

    def test_secret_and_raw_workspace_id_are_absent_from_response_event_error_and_repr(self):
        secret = "sk-ant-task-4-secret"
        raw_workspace = "workspace-raw-sensitive"
        backend = self.backend(
            _FakeTransport(self.response(headers=(("request-id", "request-raw-sensitive"), ("anthropic-workspace-id", raw_workspace)))),
            credential_reader=lambda name: secret,
        )
        with self.assertRaises(BackendInvocationError) as raised:
            backend.invoke(_request_bytes(), timeout_seconds=5)
        rendered = repr(raised.exception) + str(raised.exception)
        self.assertNotIn(secret, rendered)
        self.assertNotIn(raw_workspace, rendered)
        self.assertNotIn("request-raw-sensitive", rendered)

    def test_custom_transport_or_credential_reader_forces_test_double_non_authority(self):
        custom_transport = self.backend(
            _FakeTransport(self.response()), credential_reader=lambda name: "sk-ant-test-secret"
        ).describe()
        custom_reader = self.backend(credential_reader=lambda name: "sk-ant-test-secret").describe()
        for descriptor in (custom_transport, custom_reader):
            with self.subTest(descriptor=descriptor):
                self.assertTrue(descriptor.identity.is_test_double)
                self.assertTrue(all(item.classification is CapabilityClass.UNTESTED for item in descriptor.observations))

    def test_existing_freeze_parser_replay_and_controller_binding_accept_valid_translation(self):
        transport = _FakeTransport(self.response())
        backend = self.backend(transport, credential_reader=lambda name: "sk-ant-test-secret")
        request_bytes = _request_bytes()
        result = backend.invoke(request_bytes, timeout_seconds=5)
        with tempfile.TemporaryDirectory() as directory:
            bound = freeze_validate_bind_response(
                result,
                expected_run=_run_identity(),
                expected_backend=backend.describe().identity,
                expected_request_sha256=sha256_bytes(request_bytes),
                evidence_root=Path(directory) / "evidence",
                output_validator=lambda parsed: self.assertEqual(parsed, {"verdict": "ok"}),
                used_provider_request_ids=frozenset(),
            )
        self.assertEqual(bound.identity.provider_request_id, "request-001")


if __name__ == "__main__":
    unittest.main()
