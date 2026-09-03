import inspect
import sys
import unittest
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.identity import (  # noqa: E402
    CapabilityClass,
    RunIdentity,
    sha256_bytes,
)
from reviewer_runner.request import InputArtifact, build_canonical_request  # noqa: E402


def _backend_contract():
    try:
        from reviewer_runner.backend import (  # noqa: E402
            BackendEvent,
            BackendInvocationError,
            BackendResponse,
            ToollessInferenceBackend,
            is_backend_eligible,
            validate_backend_descriptor,
        )
    except ModuleNotFoundError as error:
        raise AssertionError(
            "reviewer_runner.backend must define the tool-free inference boundary"
        ) from error
    return (
        BackendEvent,
        BackendInvocationError,
        BackendResponse,
        ToollessInferenceBackend,
        is_backend_eligible,
        validate_backend_descriptor,
    )


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
    artifacts = (
        InputArtifact("reviewer_brief", "text/markdown", b"brief"),
        InputArtifact("review_package", "application/json", b'{"package":true}'),
        InputArtifact("run_envelope", "application/json", b'{"run":true}'),
        InputArtifact("output_schema", "application/schema+json", b'{"type":"object"}'),
    )
    return build_canonical_request(_run_identity(), artifacts, {}).content


class ReviewerRunnerBackendTests(unittest.TestCase):
    def test_protocol_exposes_only_describe_and_bytes_invoke(self):
        _, _, _, protocol, _, _ = _backend_contract()
        self.assertEqual(
            {name for name in protocol.__dict__ if not name.startswith("_")},
            {"describe", "invoke"},
        )
        parameters = tuple(inspect.signature(protocol.invoke).parameters.values())
        self.assertEqual(tuple(parameter.name for parameter in parameters), (
            "self", "request_bytes", "timeout_seconds",
        ))
        self.assertEqual(parameters[1].annotation, bytes)
        self.assertEqual(parameters[2].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertEqual(parameters[2].annotation, int)

    def test_fake_receives_one_exact_request_and_returns_one_raw_response(self):
        _, _, _, _, _, _ = _backend_contract()
        from tests.reviewer_runner_support import DeterministicFakeBackend

        request_bytes = _request_bytes()
        fake = DeterministicFakeBackend(b'{"verdict":"recorded"}')
        response = fake.invoke(request_bytes, timeout_seconds=5)

        self.assertEqual(fake.received_request_bytes, [request_bytes])
        self.assertEqual(response.raw_bytes, b'{"verdict":"recorded"}')
        self.assertEqual(response.response_count, 1)

    def test_response_binds_request_run_context_reviewer_and_backend_identity(self):
        _, _, _, _, _, _ = _backend_contract()
        from reviewer_runner.identity import backend_identity_sha256
        from tests.reviewer_runner_support import DeterministicFakeBackend

        request_bytes = _request_bytes()
        fake = DeterministicFakeBackend(b'{"verdict":"recorded"}')
        response = fake.invoke(request_bytes, timeout_seconds=5)

        self.assertEqual(response.request_sha256, sha256_bytes(request_bytes))
        self.assertEqual(response.reviewer_id, "reviewer-001")
        self.assertEqual(response.review_run_id, "run-001")
        self.assertEqual(response.context_id, "context-001")
        self.assertEqual(
            response.backend_identity_sha256,
            backend_identity_sha256(fake.describe().identity),
        )
        self.assertEqual(response.continuation_id, None)
        self.assertEqual(response.previous_response_id, None)

    def test_no_tool_path_environment_retrieval_or_file_reference_parameter_exists(self):
        _, _, _, protocol, _, _ = _backend_contract()
        parameter_names = set(inspect.signature(protocol.invoke).parameters)
        forbidden = {
            "tools", "tool", "path", "paths", "environment", "env", "retrieval",
            "file", "file_id", "file_ref", "uri", "network", "browser", "connector",
        }
        self.assertFalse(parameter_names.intersection(forbidden))

    def test_no_continuation_or_previous_response_identifier_is_accepted(self):
        _, _, _, _, _, _ = _backend_contract()
        from tests.reviewer_runner_support import DeterministicFakeBackend

        fake = DeterministicFakeBackend(b'{"verdict":"recorded"}')
        with self.assertRaises(TypeError):
            fake.invoke(_request_bytes(), timeout_seconds=5, continuation_id="prior")
        with self.assertRaises(TypeError):
            fake.invoke(_request_bytes(), timeout_seconds=5, previous_response_id="prior")

    def test_transport_timeout_and_cancellation_use_backend_invocation_error(self):
        _, invocation_error, _, _, _, _ = _backend_contract()
        from tests.reviewer_runner_support import DeterministicFakeBackend

        for code in ("TRANSPORT_ERROR", "TIMEOUT", "CANCELLED", "NO_RESPONSE"):
            with self.subTest(code=code):
                scripted = invocation_error(code, "controlled test failure")
                fake = DeterministicFakeBackend(
                    b'{"verdict":"recorded"}', scripted_error=scripted
                )
                with self.assertRaises(invocation_error) as raised:
                    fake.invoke(_request_bytes(), timeout_seconds=5)
                self.assertEqual(raised.exception.code, code)
        with self.assertRaises(ValueError):
            invocation_error("UNCLASSIFIED", "not permitted")

    def test_deterministic_fake_is_always_non_authoritative(self):
        _, _, _, _, is_backend_eligible, validate_backend_descriptor = _backend_contract()
        from reviewer_runner.backend import BackendDescriptor, CapabilityObservation
        from tests.reviewer_runner_support import DeterministicFakeBackend

        fake = DeterministicFakeBackend(b'{"verdict":"recorded"}')
        descriptor = fake.describe()
        validate_backend_descriptor(descriptor)
        self.assertTrue(descriptor.identity.is_test_double)
        self.assertFalse(is_backend_eligible(descriptor))
        self.assertTrue(all(
            observation.classification is not CapabilityClass.OBSERVED_PASS
            for observation in descriptor.observations
        ))
        self.assertEqual(
            tuple(observation.capability for observation in descriptor.observations),
            (
                "stateless_fresh_request", "no_continuation_id", "no_reviewer_memory",
                "no_tools", "no_retrieval", "no_web_or_browser", "no_connectors_or_mcp",
                "no_host_filesystem", "no_code_execution", "no_file_by_reference",
                "immutable_model_or_deployment_identity", "immutable_inference_settings",
                "sufficient_payload_capacity", "exact_structured_output",
                "controller_only_authentication", "accepted_retention_and_privacy",
                "request_response_commitments",
            ),
        )
        self.assertTrue(all(observation.method for observation in descriptor.observations))
        self.assertTrue(all(len(observation.evidence_sha256) == 64 for observation in descriptor.observations))

        observed_pass_descriptor = BackendDescriptor(
            identity=replace(
                descriptor.identity,
                is_test_double=False,
                model_identity_stability="IMMUTABLE",
            ),
            max_request_bytes=descriptor.max_request_bytes,
            observations=tuple(
                CapabilityObservation(
                    capability=observation.capability,
                    classification=CapabilityClass.OBSERVED_PASS,
                    method=observation.method,
                    evidence_sha256=observation.evidence_sha256,
                )
                for observation in descriptor.observations
            ),
        )
        self.assertTrue(is_backend_eligible(observed_pass_descriptor))
        for stability in ("FLOATING", "UNKNOWN"):
            with self.subTest(stability=stability):
                self.assertFalse(
                    is_backend_eligible(
                        replace(
                            observed_pass_descriptor,
                            identity=replace(
                                observed_pass_descriptor.identity,
                                model_identity_stability=stability,
                            ),
                        )
                    )
                )
        for field, malformed_value in (
            ("backend_kind", "TOOLS_ENABLED"),
            ("adapter_id", ""),
            ("adapter_id", " "),
            ("adapter_version", ""),
            ("endpoint_identity", ""),
            ("deployment_identity", ""),
            ("model_revision_identity", ""),
            ("retention_policy_identity", ""),
            ("privacy_policy_identity", ""),
            ("model_identity_stability", "UNRECOGNIZED"),
            ("inference_settings_sha256", "0" * 63),
            ("is_test_double", 1),
        ):
            with self.subTest(field=field):
                malformed = replace(
                    observed_pass_descriptor,
                    identity=replace(
                        observed_pass_descriptor.identity,
                        **{field: malformed_value},
                    ),
                )
                with self.assertRaises(ValueError):
                    is_backend_eligible(malformed)


if __name__ == "__main__":
    unittest.main()
