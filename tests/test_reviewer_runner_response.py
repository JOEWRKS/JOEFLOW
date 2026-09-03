import dataclasses
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.backend import BackendEvent, BackendResponse  # noqa: E402
from reviewer_runner.identity import (  # noqa: E402
    BackendIdentity,
    RunIdentity,
    RunnerIdentityError,
    RunnerState,
    backend_identity_sha256,
    canonical_json_bytes,
    sha256_bytes,
)


def _response_contract():
    if importlib.util.find_spec("reviewer_runner.response") is None:
        raise AssertionError(
            "reviewer_runner.response must implement raw response freezing and binding"
        ) from None
    from reviewer_runner import response as response_module
    from reviewer_runner.response import (
        BoundResponse,
        FrozenResponse,
        atomic_freeze_raw_response,
        freeze_validate_bind_response,
        parse_single_json_document,
    )
    return (
        response_module,
        BoundResponse,
        FrozenResponse,
        atomic_freeze_raw_response,
        freeze_validate_bind_response,
        parse_single_json_document,
    )


def _run_identity(**changes):
    identity = RunIdentity(
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
    return dataclasses.replace(identity, **changes)


def _backend_identity(**changes):
    identity = BackendIdentity(
        backend_kind="STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
        adapter_id="external-inference-adapter",
        adapter_version="1.0.0",
        endpoint_identity="https://inference.example.invalid/v1",
        deployment_identity="reviewer-production",
        model_revision_identity="example-model@2026-09-03",
        model_identity_stability="IMMUTABLE",
        inference_settings_sha256=sha256_bytes(b"settings"),
        retention_policy_identity="no-retention",
        privacy_policy_identity="privacy-v1",
        is_test_double=False,
    )
    return dataclasses.replace(identity, **changes)


def _backend_response(
    raw_bytes=b'{ "status" : "synthetic-ok" }',
    *,
    run=None,
    backend=None,
    request_sha256=None,
    provider_request_id="provider-request-001",
    **changes,
):
    run = run or _run_identity()
    backend = backend or _backend_identity()
    response = BackendResponse(
        raw_bytes=raw_bytes,
        provider_request_id=provider_request_id,
        request_sha256=request_sha256 or sha256_bytes(b"request"),
        reviewer_id=run.reviewer_id,
        review_run_id=run.review_run_id,
        context_id=run.context_id,
        backend_identity_sha256=backend_identity_sha256(backend),
        response_count=1,
        continuation_id=None,
        previous_response_id=None,
        events=(
            BackendEvent(
                kind="RESPONSE",
                metadata_sha256=sha256_bytes(b"response-event"),
            ),
        ),
    )
    return dataclasses.replace(response, **changes)


def _bind(response, root, *, run=None, backend=None, validator=None, used=frozenset()):
    _, _, _, _, freeze_validate_bind_response, _ = _response_contract()
    run = run or _run_identity()
    backend = backend or _backend_identity()
    return freeze_validate_bind_response(
        response,
        expected_run=run,
        expected_backend=backend,
        expected_request_sha256=sha256_bytes(b"request"),
        evidence_root=root,
        output_validator=validator or (lambda parsed: None),
        used_provider_request_ids=used,
    )


def _assert_invalid(
    test_case,
    callable_,
    expected_state=RunnerState.REVIEW_OUTPUT_INVALID,
):
    with test_case.assertRaises(RunnerIdentityError) as raised:
        callable_()
    test_case.assertEqual(raised.exception.code, expected_state.value)
    test_case.assertEqual(
        getattr(raised.exception, "runner_state", None),
        expected_state,
    )


class ReviewerRunnerResponseTests(unittest.TestCase):
    def test_raw_bytes_are_atomically_frozen_before_parser_or_validator_runs(self):
        response_module, BoundResponse, FrozenResponse, _, _, _ = _response_contract()
        self.assertTrue(hasattr(response_module, "ResponseValidationError"))
        raw_bytes = b'{\n  "status": "synthetic-ok", "detail": "exact bytes"\n}\n'
        run = _run_identity()
        backend = _backend_identity()
        response = _backend_response(raw_bytes, run=run, backend=backend)
        with tempfile.TemporaryDirectory() as directory:
            evidence_root = Path(directory) / "evidence"
            expected_raw_path = (
                evidence_root
                / "runs"
                / run.review_run_id
                / run.context_id
                / "raw-response.json"
            )

            def validator(parsed):
                self.assertTrue(expected_raw_path.is_file())
                self.assertEqual(expected_raw_path.read_bytes(), raw_bytes)
                self.assertEqual(parsed["status"], "synthetic-ok")

            bound = _bind(
                response,
                evidence_root,
                run=run,
                backend=backend,
                validator=validator,
            )

            self.assertIsInstance(bound, BoundResponse)
            self.assertIsInstance(bound.frozen, FrozenResponse)
            self.assertEqual(bound.frozen.path, expected_raw_path.resolve())
            self.assertEqual(bound.frozen.byte_count, len(raw_bytes))
            self.assertEqual(bound.frozen.sha256, sha256_bytes(raw_bytes))
            self.assertEqual(bound.identity.raw_response_sha256, sha256_bytes(raw_bytes))
            self.assertEqual(
                bound.identity.parsed_output_sha256,
                sha256_bytes(
                    canonical_json_bytes(
                        {"status": "synthetic-ok", "detail": "exact bytes"}
                    )
                ),
            )

    def test_malformed_and_truncated_json_are_review_output_invalid(self):
        invalid_documents = (
            b'{"status":',
            b'{"status":"synthetic-ok"',
            b'{"status": invalid}',
            b'\xff',
            b'["not-an-object"]',
        )
        for index, raw_bytes in enumerate(invalid_documents):
            with self.subTest(raw_bytes=raw_bytes), tempfile.TemporaryDirectory() as directory:
                run = _run_identity(review_run_id=f"run-malformed-{index}")
                response = _backend_response(raw_bytes, run=run)
                root = Path(directory) / "evidence"
                _assert_invalid(self, lambda: _bind(response, root, run=run))
                self.assertEqual(
                    (
                        root
                        / "runs"
                        / run.review_run_id
                        / run.context_id
                        / "raw-response.json"
                    ).read_bytes(),
                    raw_bytes,
                )

    def test_duplicate_or_extra_json_document_is_rejected(self):
        invalid_documents = (
            b'{"status":"synthetic-ok","status":"forged"}',
            b'{"status":"synthetic-ok","nested":{"key":1,"key":2}}',
            b'{"status":"synthetic-ok"} {"status":"second"}',
            b'{"status":"synthetic-ok"} trailing',
        )
        for index, raw_bytes in enumerate(invalid_documents):
            with self.subTest(raw_bytes=raw_bytes), tempfile.TemporaryDirectory() as directory:
                run = _run_identity(review_run_id=f"run-document-{index}")
                response = _backend_response(raw_bytes, run=run)
                _assert_invalid(
                    self,
                    lambda: _bind(response, Path(directory) / "evidence", run=run),
                )

    def test_schema_invalid_output_is_rejected_without_scoring(self):
        raw_bytes = b'{"status":"schema-invalid"}'
        validator_calls = []

        def validator(parsed):
            validator_calls.append(parsed)
            raise ValueError("required semantic-review fields are missing")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            response = _backend_response(raw_bytes)
            _assert_invalid(
                self,
                lambda: _bind(response, root, validator=validator),
            )
            self.assertEqual(validator_calls, [{"status": "schema-invalid"}])
            self.assertEqual(
                (root / "runs" / "run-001" / "context-001" / "raw-response.json").read_bytes(),
                raw_bytes,
            )

    def test_package_contract_reviewer_run_and_context_mismatch_are_rejected(self):
        validator_calls = []
        cases = (
            {"request_sha256": sha256_bytes(b"other-package-contract")},
            {"reviewer_id": "other-reviewer"},
            {"review_run_id": "other-run"},
            {"context_id": "other-context"},
        )
        for index, changes in enumerate(cases):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as directory:
                response = _backend_response(**changes)
                root = Path(directory) / "evidence"
                _assert_invalid(
                    self,
                    lambda: _bind(
                        response,
                        root,
                        validator=lambda parsed: validator_calls.append(parsed),
                    ),
                    RunnerState.PACKAGE_BINDING_MISMATCH,
                )
                self.assertTrue(
                    (root / "runs" / "run-001" / "context-001" / "raw-response.json").is_file()
                )
        self.assertEqual(validator_calls, [])

        for run in (
            _run_identity(review_run_id="../escape"),
            _run_identity(context_id="..\\escape"),
        ):
            with self.subTest(run=run), tempfile.TemporaryDirectory() as directory:
                response = _backend_response(run=run)
                _assert_invalid(
                    self,
                    lambda: _bind(response, Path(directory) / "evidence", run=run),
                )

    def test_model_deployment_settings_or_request_metadata_mismatch_is_rejected(self):
        original_backend = _backend_identity()
        response = _backend_response(backend=original_backend)
        changed_backends = (
            dataclasses.replace(
                original_backend,
                model_revision_identity="other-model@2026-09-03",
            ),
            dataclasses.replace(
                original_backend,
                deployment_identity="other-deployment",
            ),
            dataclasses.replace(
                original_backend,
                inference_settings_sha256=sha256_bytes(b"other-settings"),
            ),
        )
        validator_calls = []
        for backend in changed_backends:
            with self.subTest(backend=backend), tempfile.TemporaryDirectory() as directory:
                _assert_invalid(
                    self,
                    lambda: _bind(
                        response,
                        Path(directory) / "evidence",
                        backend=backend,
                        validator=lambda parsed: validator_calls.append(parsed),
                    ),
                    RunnerState.PACKAGE_BINDING_MISMATCH,
                )
        self.assertEqual(validator_calls, [])

    def test_modified_frozen_bytes_fail_readback_hash(self):
        response_module, _, _, atomic_freeze_raw_response, _, parse_document = (
            _response_contract()
        )
        raw_bytes = b'{"status":"synthetic-ok"}'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            original_replace = response_module.os.replace

            def replace_then_modify(source, target):
                original_replace(source, target)
                Path(target).write_bytes(b'{"status":"modified"}')

            with mock.patch.object(
                response_module.os,
                "replace",
                side_effect=replace_then_modify,
            ):
                _assert_invalid(
                    self,
                    lambda: atomic_freeze_raw_response(
                        raw_bytes,
                        evidence_root=root,
                        review_run_id="run-001",
                        context_id="context-001",
                    ),
                )

            frozen = atomic_freeze_raw_response(
                raw_bytes,
                evidence_root=root,
                review_run_id="run-001",
                context_id="context-001",
            )
            frozen.path.write_bytes(b'{"status":"modified-after-freeze"}')
            _assert_invalid(self, lambda: parse_document(frozen))

    def test_provider_request_id_replay_across_runs_is_rejected(self):
        run = _run_identity(review_run_id="run-replay-attempt")
        response = _backend_response(run=run, provider_request_id="already-used")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            _assert_invalid(
                self,
                lambda: _bind(
                    response,
                    root,
                    run=run,
                    used=frozenset({"already-used"}),
                ),
                RunnerState.PACKAGE_BINDING_MISMATCH,
            )
            self.assertTrue(
                (root / "runs" / run.review_run_id / run.context_id / "raw-response.json").is_file()
            )

    def test_missing_or_multiple_response_count_is_rejected(self):
        event = BackendEvent("RESPONSE", sha256_bytes(b"response-event-2"))
        forbidden_event = BackendEvent("TOOL", sha256_bytes(b"tool-event"))
        cases = (
            {"response_count": None},
            {"response_count": 0},
            {"response_count": 2},
            {"response_count": True},
            {"response_count": 1.0},
            {"continuation_id": "continuation"},
            {"previous_response_id": "previous"},
            {"events": ()},
            {"events": (event, event)},
            {"events": (event, forbidden_event)},
            {"events": (BackendEvent("OTHER", sha256_bytes(b"other")),)},
        )
        for index, changes in enumerate(cases):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as directory:
                run = _run_identity(review_run_id=f"run-cardinality-{index}")
                response = _backend_response(run=run, **changes)
                _assert_invalid(
                    self,
                    lambda: _bind(response, Path(directory) / "evidence", run=run),
                    RunnerState.PACKAGE_BINDING_MISMATCH,
                )

    def test_identical_semantic_bytes_from_distinct_provider_requests_are_not_false_replay(self):
        raw_bytes = b'{ "status" : "synthetic-ok" }'
        first_run = _run_identity(review_run_id="run-distinct-001", context_id="context-a")
        second_run = _run_identity(review_run_id="run-distinct-002", context_id="context-b")
        first = _backend_response(
            raw_bytes,
            run=first_run,
            provider_request_id="provider-distinct-001",
        )
        second = _backend_response(
            raw_bytes,
            run=second_run,
            provider_request_id="provider-distinct-002",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            first_bound = _bind(first, root, run=first_run)
            second_bound = _bind(
                second,
                root,
                run=second_run,
                used=frozenset({first.provider_request_id}),
            )

            self.assertEqual(first_bound.frozen.sha256, second_bound.frozen.sha256)
            self.assertEqual(
                first_bound.identity.parsed_output_sha256,
                second_bound.identity.parsed_output_sha256,
            )
            self.assertNotEqual(
                first_bound.identity.provider_request_id,
                second_bound.identity.provider_request_id,
            )


if __name__ == "__main__":
    unittest.main()
