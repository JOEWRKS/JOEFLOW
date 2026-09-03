import ast
import copy
import dataclasses
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL_ROOT / "scripts"
for path in (SKILL_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream_v21.compiler import compile_handoff_definition_v21  # noqa: E402
from downstream_v21.semantic_review import (  # noqa: E402
    build_semantic_review_package_v21,
)
from reviewer_runner.backend import (  # noqa: E402
    BackendEvent,
    BackendInvocationError,
    BackendResponse,
)
from reviewer_runner.identity import (  # noqa: E402
    CapabilityClass,
    RunIdentity,
    RunnerState,
    backend_identity_sha256,
    canonical_json_bytes,
    sha256_bytes,
)
from reviewer_runner.preflight import (  # noqa: E402
    build_preflight_freshness,
    run_isolation_preflight,
)
from tests.downstream_v21_support import closed_v2_state  # noqa: E402
from tests.reviewer_runner_support import DeterministicFakeBackend  # noqa: E402
from tests.semantic_review_support import make_run_set  # noqa: E402
from tests.test_downstream_v21_compiler import complete_definition_v21  # noqa: E402
from tests.test_downstream_v21_semantic_review import reviewed_output  # noqa: E402

try:
    from reviewer_runner.controller import RunOutcome, execute_review  # noqa: E402
    from reviewer_runner.semantic_review import (  # noqa: E402
        PreparedReview,
        prepare_semantic_review_v1,
        prepare_semantic_review_v21,
    )
except ImportError:
    RunOutcome = None
    PreparedReview = None
    execute_review = None
    prepare_semantic_review_v1 = None
    prepare_semantic_review_v21 = None


def _nonce_bytes(label: str) -> bytes:
    return bytes.fromhex(sha256_bytes(("task-7:" + label).encode("utf-8")))


def _response_event() -> BackendEvent:
    return BackendEvent(
        kind="RESPONSE",
        metadata_sha256=sha256_bytes(b"task-7-response-event"),
    )


def _init_clean_repository(parent: Path) -> Path:
    repository = parent / "source-repository"
    repository.mkdir()
    subprocess.run(
        ["git", "init", "-q", str(repository)],
        check=True,
        shell=False,
    )
    subprocess.run(
        ["git", "-C", str(repository), "config", "core.autocrlf", "false"],
        check=True,
        shell=False,
    )
    (repository / "tracked.txt").write_bytes(b"unchanged source\n")
    subprocess.run(
        ["git", "-C", str(repository), "add", "tracked.txt"],
        check=True,
        shell=False,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Reviewer Runner Tests",
            "-c",
            "user.email=runner-tests@example.invalid",
            "commit",
            "-q",
            "-m",
            "test fixture",
        ],
        check=True,
        shell=False,
    )
    return repository


def _v1_material(*, run_id: str = "run-001", context_id: str = "context-001"):
    packages, envelopes, outputs = make_run_set(["APPROVED"], run_count=1)
    package = packages[0]
    envelope = envelopes[0]
    output = outputs[0]
    package_archive_bytes = b"synthetic-v1-package-archive"
    reviewer_brief_bytes = b"Use the exact frozen semantic review contract.\n"
    package_digest = sha256_bytes(package_archive_bytes)
    brief_digest = sha256_bytes(reviewer_brief_bytes)
    package["reviewer_input_package_hash"] = package_digest
    package["reviewer_brief_hash"] = brief_digest
    package["role_hashes"]["reviewer_brief"] = brief_digest
    envelope["review_run_id"] = run_id
    envelope["reviewer_context_id"] = context_id
    envelope["reviewer_input_package_hash"] = package_digest
    envelope["reviewer_brief_hash"] = brief_digest
    output["review_run_id"] = run_id
    output["reviewer_context_id"] = context_id
    output["reviewer_input_package_hash"] = package_digest
    output["reviewer_brief_hash"] = brief_digest
    for record in output["records"]:
        record["reviewer_brief_hash"] = brief_digest
    run_identity = RunIdentity(
        semantic_review_contract_version="joewrks.semantic-review/1.0",
        package_schema_version="joewrks.semantic-review-input/1.0",
        package_digest=package_digest,
        source_action_contract_hash=package["contract_hash"],
        source_definition_digest=None,
        reviewer_id="reviewer-001",
        review_run_id=run_id,
        context_id=context_id,
        cohort_id=None,
        case_id=None,
    )
    return {
        "package": package,
        "package_bytes": package_archive_bytes,
        "brief_bytes": reviewer_brief_bytes,
        "envelope": envelope,
        "schema_bytes": canonical_json_bytes(package["review_output_schema"]),
        "run_identity": run_identity,
        "output": output,
    }


def _prepared_v1(*, run_id: str = "run-001", context_id: str = "context-001"):
    material = _v1_material(run_id=run_id, context_id=context_id)
    prepared = prepare_semantic_review_v1(
        verified_package=material["package"],
        package_archive_bytes=material["package_bytes"],
        reviewer_brief_bytes=material["brief_bytes"],
        run_envelope=material["envelope"],
        output_schema_bytes=material["schema_bytes"],
        run_identity=material["run_identity"],
    )
    return prepared, material


def _fake_backend(raw_response: bytes, **kwargs) -> DeterministicFakeBackend:
    return DeterministicFakeBackend(
        raw_response,
        events=(_response_event(),),
        **kwargs,
    )


def _fake_preflight(backend):
    freshness = build_preflight_freshness(backend.describe().identity)
    preflight = run_isolation_preflight(
        backend,
        freshness=freshness,
        nonce_source=_nonce_bytes,
    )
    if preflight.classification is not CapabilityClass.UNTESTED:
        raise AssertionError("deterministic fake preflight must remain UNTESTED")
    if backend.received_request_bytes:
        raise AssertionError("deterministic fake preflight must not invoke the backend")
    return preflight, freshness


class _ArbitraryRawFake:
    def __init__(self, raw_bytes: bytes):
        self._delegate = _fake_backend(b"{}")
        self._raw_bytes = raw_bytes
        self.received_request_bytes = []

    def describe(self):
        return self._delegate.describe()

    def invoke(self, request_bytes: bytes, *, timeout_seconds: int):
        del timeout_seconds
        self.received_request_bytes.append(request_bytes)
        request = json.loads(request_bytes)
        run = request["run_identity"]
        identity = self.describe().identity
        return BackendResponse(
            raw_bytes=self._raw_bytes,
            provider_request_id="arbitrary-raw-fake-request",
            request_sha256=sha256_bytes(request_bytes),
            reviewer_id=run["reviewer_id"],
            review_run_id=run["review_run_id"],
            context_id=run["context_id"],
            backend_identity_sha256=backend_identity_sha256(identity),
            response_count=1,
            continuation_id=None,
            previous_response_id=None,
            events=(_response_event(),),
        )


class _PostInvokeSideEffectBackend:
    def __init__(self, delegate, side_effect):
        self._delegate = delegate
        self._side_effect = side_effect
        self.received_request_bytes = delegate.received_request_bytes

    def describe(self):
        return self._delegate.describe()

    def invoke(self, request_bytes: bytes, *, timeout_seconds: int):
        response = self._delegate.invoke(
            request_bytes,
            timeout_seconds=timeout_seconds,
        )
        self._side_effect()
        return response


class ReviewerRunnerControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v21_package = None
        cls.v21_output = None
        if prepare_semantic_review_v21 is not None:
            state = closed_v2_state()
            contract = compile_handoff_definition_v21(
                state,
                complete_definition_v21(state, review=True),
            )["contract"]
            cls.v21_package = build_semantic_review_package_v21(contract)
            cls.v21_output = reviewed_output(cls.v21_package)

    def setUp(self):
        self.assertIsNotNone(
            execute_review,
            "reviewer_runner.controller implementation is missing",
        )
        self.assertIsNotNone(
            prepare_semantic_review_v1,
            "reviewer_runner.semantic_review implementation is missing",
        )
        self.assertIsNotNone(
            prepare_semantic_review_v21,
            "reviewer_runner.semantic_review implementation is missing",
        )

    def _execute(self, prepared, backend, preflight, freshness, base: Path, **changes):
        repository = _init_clean_repository(base)
        transient_parent = base / "transient"
        transient_parent.mkdir()
        evidence_root = base / "evidence"
        outcome = execute_review(
            prepared,
            backend=backend,
            preflight=preflight,
            current_freshness=freshness,
            evidence_root=evidence_root,
            transient_parent=transient_parent,
            repository_root=repository,
            execution_mode=changes.pop("execution_mode", "SYNTHETIC_TEST"),
            **changes,
        )
        return outcome, repository, transient_parent, evidence_root

    def test_real_review_without_backend_returns_isolation_capability_unavailable_before_invoke(self):
        prepared, _ = _prepared_v1()
        freshness = build_preflight_freshness(None)
        preflight = run_isolation_preflight(
            None,
            freshness=freshness,
            nonce_source=_nonce_bytes,
        )
        with tempfile.TemporaryDirectory() as directory:
            outcome, _, _, _ = self._execute(
                prepared,
                None,
                preflight,
                freshness,
                Path(directory),
                execution_mode="REAL_REVIEW",
            )
        self.assertIsInstance(outcome, RunOutcome)
        self.assertEqual(outcome.state, RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE)
        self.assertEqual(outcome.capability_classification, CapabilityClass.UNAVAILABLE)
        self.assertIsNone(outcome.receipt_path)
        self.assertIsNone(outcome.raw_response_path)

        class BrokenDescriptorBackend:
            received_request_bytes = []

            def describe(self):
                raise RuntimeError("descriptor unavailable")

            def invoke(self, request_bytes: bytes, *, timeout_seconds: int):
                self.received_request_bytes.append(request_bytes)
                raise AssertionError("ineligible backend must not be invoked")

        backend = BrokenDescriptorBackend()
        with tempfile.TemporaryDirectory() as directory:
            try:
                outcome, _, _, _ = self._execute(
                    prepared,
                    backend,
                    preflight,
                    freshness,
                    Path(directory),
                    execution_mode="REAL_REVIEW",
                )
            except RuntimeError as error:
                self.fail(f"descriptor failure must be contained: {error}")
        self.assertEqual(outcome.state, RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE)
        self.assertEqual(backend.received_request_bytes, [])

    def test_failed_or_stale_preflight_returns_isolation_preflight_failed_before_semantic_bytes(self):
        prepared, material = _prepared_v1()
        for label, mutation in (
            (
                "failed",
                lambda preflight, freshness: (
                    dataclasses.replace(
                        preflight,
                        classification=CapabilityClass.OBSERVED_FAIL,
                    ),
                    freshness,
                ),
            ),
            (
                "stale",
                lambda preflight, freshness: (
                    preflight,
                    dataclasses.replace(
                        freshness,
                        runner_code_sha256=sha256_bytes(b"stale-runner-code"),
                    ),
                ),
            ),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                backend = _fake_backend(canonical_json_bytes(material["output"]))
                preflight, freshness = _fake_preflight(backend)
                preflight, freshness = mutation(preflight, freshness)
                outcome, _, _, _ = self._execute(
                    prepared,
                    backend,
                    preflight,
                    freshness,
                    Path(directory),
                )
                self.assertEqual(
                    outcome.state,
                    RunnerState.ISOLATION_PREFLIGHT_FAILED,
                )
                self.assertEqual(backend.received_request_bytes, [])

    def test_v1_adapter_delegates_to_existing_envelope_and_output_validators(self):
        prepared, material = _prepared_v1()
        self.assertIsInstance(prepared, PreparedReview)
        self.assertEqual(
            {artifact.logical_role for artifact in prepared.artifacts},
            {"reviewer_brief", "review_package", "run_envelope", "output_schema"},
        )
        prepared.output_validator(copy.deepcopy(material["output"]))

        invalid_output = copy.deepcopy(material["output"])
        invalid_output["reviewer_input_package_hash"] = "0" * 64
        with self.assertRaises(ValueError):
            prepared.output_validator(invalid_output)

        invalid_envelope = copy.deepcopy(material["envelope"])
        invalid_envelope["reviewer_brief_hash"] = "0" * 64
        with self.assertRaises(ValueError):
            prepare_semantic_review_v1(
                verified_package=material["package"],
                package_archive_bytes=material["package_bytes"],
                reviewer_brief_bytes=material["brief_bytes"],
                run_envelope=invalid_envelope,
                output_schema_bytes=material["schema_bytes"],
                run_identity=material["run_identity"],
            )

    def test_v21_adapter_delegates_to_existing_package_and_output_validators_without_changing_output_fields(self):
        package = copy.deepcopy(self.v21_package)
        output = copy.deepcopy(self.v21_output)
        package_bytes = canonical_json_bytes(package)
        run_identity = RunIdentity(
            semantic_review_contract_version="joewrks.semantic-review/2.1",
            package_schema_version=package["review_schema_version"],
            package_digest=package["package_hash"],
            source_action_contract_hash=package["source_semantic_contract_hash"],
            source_definition_digest=package["source_definition_digest"],
            reviewer_id="reviewer-v21",
            review_run_id="run-v21",
            context_id="context-v21",
            cohort_id=None,
            case_id=None,
        )
        prepared = prepare_semantic_review_v21(
            package=package,
            package_bytes=package_bytes,
            reviewer_brief_bytes=b"Review only the exact 2.1 obligations.\n",
            run_envelope_bytes=canonical_json_bytes(
                {"review_run_id": "run-v21", "context_id": "context-v21"}
            ),
            output_schema_bytes=(
                SKILL_ROOT
                / "downstream_v21"
                / "schemas"
                / "semantic-review-output-v21.schema.json"
            ).read_bytes(),
            run_identity=run_identity,
        )
        original_output = copy.deepcopy(output)
        prepared.output_validator(output)
        self.assertEqual(output, original_output)
        self.assertEqual(
            set(output),
            {
                "review_schema_version",
                "input_package_hash",
                "reliability_status",
                "results",
                "output_hash",
            },
        )
        self.assertNotEqual(package["package_hash"], sha256_bytes(package_bytes))

        backend = _fake_backend(canonical_json_bytes(output))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                Path(directory),
            )
        self.assertEqual(outcome.state, RunnerState.REVIEW_COMPLETED)
        self.assertEqual(outcome.capability_classification, CapabilityClass.UNTESTED)

        changed_package_bytes = canonical_json_bytes(
            {**package, "reliability_status": "CALIBRATED"}
        )
        with self.assertRaises(ValueError):
            prepare_semantic_review_v21(
                package=package,
                package_bytes=changed_package_bytes,
                reviewer_brief_bytes=b"Review only the exact 2.1 obligations.\n",
                run_envelope_bytes=b"{}",
                output_schema_bytes=b"{}",
                run_identity=run_identity,
            )

    def test_package_binding_error_never_becomes_semantic_verdict(self):
        prepared, material = _prepared_v1()
        backend = _fake_backend(
            canonical_json_bytes(material["output"]),
            metadata_drift={"request_sha256": "0" * 64},
        )
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                Path(directory),
            )
        self.assertEqual(outcome.state, RunnerState.PACKAGE_BINDING_MISMATCH)
        self.assertIsNone(outcome.receipt_path)
        self.assertFalse(any("APPROVED" in error for error in outcome.errors))
        self.assertFalse(any("REJECTED" in error for error in outcome.errors))

    def test_transport_timeout_and_cancellation_return_reviewer_execution_failed_without_retry(self):
        for code, scripted_error in (
            ("TIMEOUT", BackendInvocationError("TIMEOUT", "timeout")),
            ("CANCELLED", BackendInvocationError("CANCELLED", "cancelled")),
            ("UNEXPECTED", RuntimeError("unexpected transport failure")),
        ):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                prepared, material = _prepared_v1(
                    run_id=f"run-{code.lower()}",
                    context_id=f"context-{code.lower()}",
                )
                backend = _fake_backend(
                    canonical_json_bytes(material["output"]),
                    scripted_error=scripted_error,
                )
                preflight, freshness = _fake_preflight(backend)
                try:
                    outcome, _, _, evidence_root = self._execute(
                        prepared,
                        backend,
                        preflight,
                        freshness,
                        Path(directory),
                    )
                except RuntimeError as error:
                    self.fail(f"backend failure must be contained: {error}")
                self.assertEqual(
                    outcome.state,
                    RunnerState.REVIEWER_EXECUTION_FAILED,
                )
                self.assertEqual(len(backend.received_request_bytes), 1)
                self.assertIsNone(outcome.receipt_path)
                self.assertTrue(
                    (
                        evidence_root
                        / "runs"
                        / prepared.run_identity.review_run_id
                        / prepared.run_identity.context_id
                        / "failure.json"
                    ).is_file()
                )

    def test_malformed_schema_invalid_or_duplicate_output_returns_review_output_invalid_without_scoring(self):
        cases = []
        material = _v1_material()
        cases.append(("malformed", b'{"broken":', _ArbitraryRawFake))
        cases.append(("duplicate-json-key", b'{"a":1,"a":2}', _fake_backend))
        cases.append(("schema-invalid", b'{"unexpected":true}', _fake_backend))
        duplicate_output = copy.deepcopy(material["output"])
        duplicate_output["records"].append(copy.deepcopy(duplicate_output["records"][0]))
        cases.append(
            ("duplicate-review-identity", canonical_json_bytes(duplicate_output), _fake_backend)
        )
        for index, (label, raw_bytes, factory) in enumerate(cases):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                prepared, _ = _prepared_v1(
                    run_id=f"run-invalid-{index}",
                    context_id=f"context-invalid-{index}",
                )
                backend = factory(raw_bytes)
                preflight, freshness = _fake_preflight(backend)
                outcome, _, _, _ = self._execute(
                    prepared,
                    backend,
                    preflight,
                    freshness,
                    Path(directory),
                )
                self.assertEqual(outcome.state, RunnerState.REVIEW_OUTPUT_INVALID)
                self.assertEqual(len(backend.received_request_bytes), 1)
                self.assertIsNotNone(outcome.raw_response_path)
                self.assertIsNone(outcome.receipt_path)

    def test_valid_synthetic_test_flow_freezes_raw_response_receipt_and_cleanup_evidence(self):
        prepared, material = _prepared_v1()
        raw_response = canonical_json_bytes(material["output"])
        backend = _fake_backend(raw_response)
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            outcome, _, transient_parent, evidence_root = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                Path(directory),
            )
            self.assertEqual(outcome.state, RunnerState.REVIEW_COMPLETED)
            self.assertEqual(outcome.capability_classification, CapabilityClass.UNTESTED)
            self.assertEqual(outcome.execution_mode, "SYNTHETIC_TEST")
            self.assertEqual(outcome.raw_response_path.read_bytes(), raw_response)
            self.assertTrue(outcome.receipt_path.is_file())
            receipt = json.loads(outcome.receipt_path.read_bytes())
            self.assertEqual(receipt["state"], RunnerState.REVIEW_COMPLETED.value)
            cleanup_path = (
                evidence_root
                / "runs"
                / prepared.run_identity.review_run_id
                / prepared.run_identity.context_id
                / "cleanup.json"
            )
            self.assertTrue(cleanup_path.is_file())
            workspace = (
                transient_parent
                / "joewrks-reviewer-runner"
                / prepared.run_identity.review_run_id
            )
            self.assertFalse(workspace.exists())
            self.assertEqual(len(backend.received_request_bytes), 1)

        prepared, material = _prepared_v1(
            run_id="run-cleanup-failure",
            context_id="context-cleanup-failure",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            transient_parent = base / "transient"
            marker = (
                transient_parent
                / "joewrks-reviewer-runner"
                / prepared.run_identity.review_run_id
                / ".joewrks-runner-owner.json"
            )
            delegate = _fake_backend(canonical_json_bytes(material["output"]))
            backend = _PostInvokeSideEffectBackend(delegate, marker.unlink)
            preflight, freshness = _fake_preflight(backend)
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                base,
            )
            self.assertEqual(outcome.state, RunnerState.REVIEWER_EXECUTION_FAILED)
            self.assertIsNone(outcome.receipt_path)
            self.assertEqual(len(backend.received_request_bytes), 1)
            self.assertTrue(
                (
                    base
                    / "evidence"
                    / "runs"
                    / prepared.run_identity.review_run_id
                    / prepared.run_identity.context_id
                    / "failure.json"
                ).is_file()
            )

        prepared, material = _prepared_v1(
            run_id="run-source-drift",
            context_id="context-source-drift",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_holder = {}
            delegate = _fake_backend(canonical_json_bytes(material["output"]))

            def mutate_source():
                (repository_holder["repository"] / "unexpected.txt").write_bytes(b"drift")

            backend = _PostInvokeSideEffectBackend(delegate, mutate_source)
            preflight, freshness = _fake_preflight(backend)
            repository = _init_clean_repository(base)
            repository_holder["repository"] = repository
            transient_parent = base / "transient"
            transient_parent.mkdir()
            evidence_root = base / "evidence"
            outcome = execute_review(
                prepared,
                backend=backend,
                preflight=preflight,
                current_freshness=freshness,
                evidence_root=evidence_root,
                transient_parent=transient_parent,
                repository_root=repository,
                execution_mode="SYNTHETIC_TEST",
            )
            self.assertEqual(outcome.state, RunnerState.REVIEWER_EXECUTION_FAILED)
            self.assertIsNone(outcome.receipt_path)
            self.assertEqual(len(backend.received_request_bytes), 1)

    def test_oracle_goldens_gate_and_reliability_modules_are_never_imported_or_called(self):
        forbidden = {"goldens", "gate", "statistics", "disagreement", "oracle"}
        for relative_path in (
            "reviewer_runner/controller.py",
            "reviewer_runner/semantic_review.py",
        ):
            source = (SKILL_ROOT / relative_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module)
            imported_segments = {
                segment
                for module_name in imported
                for segment in module_name.split(".")
            }
            self.assertTrue(forbidden.isdisjoint(imported_segments))
            identifiers = {
                node.id.lower()
                for node in ast.walk(tree)
                if isinstance(node, ast.Name)
            }
            self.assertTrue(forbidden.isdisjoint(identifiers))

    def test_fake_backend_cannot_execute_real_review_or_change_not_measured_status(self):
        prepared, material = _prepared_v1()
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                Path(directory),
                execution_mode="REAL_REVIEW",
            )
        self.assertEqual(outcome.state, RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE)
        self.assertEqual(outcome.capability_classification, CapabilityClass.UNTESTED)
        self.assertEqual(backend.received_request_bytes, [])
        self.assertFalse(hasattr(outcome, "reliability_status"))
        self.assertEqual(self.v21_package["reliability_status"], "NOT_MEASURED")


if __name__ == "__main__":
    unittest.main()
