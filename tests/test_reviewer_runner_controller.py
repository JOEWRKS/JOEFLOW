import ast
import copy
import dataclasses
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
from reviewer_runner.request import build_canonical_request  # noqa: E402
import reviewer_runner.controller as controller_module  # noqa: E402
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


def _tree_bytes_sha256(path: Path) -> str:
    resolved = path.resolve(strict=True)
    manifest = [{"path": "", "type": "directory"}]
    for current, directories, files in os.walk(
        resolved,
        topdown=True,
        followlinks=False,
    ):
        directories.sort()
        files.sort()
        current_path = Path(current)
        for name in directories:
            candidate = current_path / name
            relative = candidate.relative_to(resolved).as_posix()
            if candidate.is_symlink():
                manifest.append(
                    {
                        "path": relative,
                        "target": os.readlink(candidate),
                        "type": "symlink",
                    }
                )
            else:
                manifest.append({"path": relative, "type": "directory"})
        for name in files:
            candidate = current_path / name
            relative = candidate.relative_to(resolved).as_posix()
            if candidate.is_symlink():
                manifest.append(
                    {
                        "path": relative,
                        "target": os.readlink(candidate),
                        "type": "symlink",
                    }
                )
                continue
            content = candidate.read_bytes()
            manifest.append(
                {
                    "byte_count": len(content),
                    "content_sha256": hashlib.sha256(content).hexdigest(),
                    "path": relative,
                    "type": "file",
                }
            )
    return hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


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
    freshness = build_preflight_freshness(backend.describe())
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

    def test_unsafe_path_topology_matrix_fails_before_state_or_invocation(self):
        cases = (
            ("evidence-equals-repository", "repository_root overlaps evidence_root"),
            ("evidence-inside-repository", "repository_root overlaps evidence_root"),
            ("repository-inside-evidence", "repository_root overlaps evidence_root"),
            ("transient-equals-repository", "repository_root overlaps transient_parent"),
            ("transient-inside-repository", "repository_root overlaps transient_parent"),
            ("repository-inside-transient", "repository_root overlaps transient_parent"),
            ("writable-roots-equal", "evidence_root overlaps transient_parent"),
            ("evidence-inside-transient", "evidence_root overlaps transient_parent"),
            ("transient-inside-evidence", "evidence_root overlaps transient_parent"),
            ("nonexistent-lexical-alias", "repository_root overlaps evidence_root"),
        )
        for index, (label, expected_error) in enumerate(cases):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                base = Path(directory).resolve()
                if label == "repository-inside-evidence":
                    evidence_root = base / "writable-parent"
                    evidence_root.mkdir()
                    repository = _init_clean_repository(evidence_root)
                    transient_parent = base / "transient"
                    transient_parent.mkdir()
                elif label == "repository-inside-transient":
                    transient_parent = base / "writable-parent"
                    transient_parent.mkdir()
                    repository = _init_clean_repository(transient_parent)
                    evidence_root = base / "evidence"
                else:
                    repository = _init_clean_repository(base)
                    if label == "evidence-equals-repository":
                        evidence_root = repository
                        transient_parent = base / "transient"
                        transient_parent.mkdir()
                    elif label == "evidence-inside-repository":
                        evidence_root = repository / "future-evidence"
                        transient_parent = base / "transient"
                        transient_parent.mkdir()
                    elif label == "transient-equals-repository":
                        evidence_root = base / "evidence"
                        transient_parent = repository
                    elif label == "transient-inside-repository":
                        evidence_root = base / "evidence"
                        transient_parent = repository / "future-transient"
                    elif label == "writable-roots-equal":
                        evidence_root = base / "writable"
                        evidence_root.mkdir()
                        transient_parent = evidence_root
                    elif label == "evidence-inside-transient":
                        transient_parent = base / "writable"
                        transient_parent.mkdir()
                        evidence_root = transient_parent / "future-evidence"
                    elif label == "transient-inside-evidence":
                        evidence_root = base / "writable"
                        evidence_root.mkdir()
                        transient_parent = evidence_root / "future-transient"
                    elif label == "nonexistent-lexical-alias":
                        evidence_root = repository / "missing" / ".."
                        transient_parent = base / "transient"
                        transient_parent.mkdir()
                    else:
                        self.fail(f"unhandled path-topology fixture: {label}")

                prepared, material = _prepared_v1(
                    run_id=f"run-topology-{index}",
                    context_id=f"context-topology-{index}",
                )
                backend = _fake_backend(canonical_json_bytes(material["output"]))
                preflight, freshness = _fake_preflight(backend)
                before = _tree_bytes_sha256(base)

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
                self.assertEqual(
                    outcome.errors,
                    (f"unsafe runner path topology: {expected_error}",),
                )
                self.assertEqual(backend.received_request_bytes, [])
                self.assertIsNone(outcome.receipt_path)
                self.assertIsNone(outcome.raw_response_path)
                self.assertEqual(_tree_bytes_sha256(base), before)
                self.assertFalse(any(base.rglob("run-claims")))
                self.assertFalse(any(base.rglob(".joewrks-run-reservations")))
                self.assertFalse(any(base.rglob(".joewrks-runner-owner.json")))

    def test_symlink_alias_with_nonexistent_leaf_fails_topology_without_escape(self):
        prepared, material = _prepared_v1(
            run_id="run-topology-symlink",
            context_id="context-topology-symlink",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            alias = base / "repository-alias"
            try:
                alias.symlink_to(repository, target_is_directory=True)
            except (NotImplementedError, OSError):
                return
            evidence_root = alias / "future-evidence"
            before = _tree_bytes_sha256(base)

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
            self.assertEqual(
                outcome.errors,
                (
                    "unsafe runner path topology: evidence_root contains a symlink or junction",
                ),
            )
            self.assertEqual(backend.received_request_bytes, [])
            self.assertEqual(_tree_bytes_sha256(base), before)
            self.assertFalse((repository / "future-evidence").exists())

    def test_disjoint_absolute_roots_execute_from_unrelated_cwd(self):
        prepared, material = _prepared_v1(
            run_id="run-topology-disjoint",
            context_id="context-topology-disjoint",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            evidence_root = base / "future-evidence"
            unrelated_cwd = base / "unrelated-cwd"
            unrelated_cwd.mkdir()
            prior_cwd = Path.cwd()
            try:
                os.chdir(unrelated_cwd)
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
            finally:
                os.chdir(prior_cwd)

            self.assertEqual(outcome.state, RunnerState.REVIEW_COMPLETED)
            self.assertEqual(len(backend.received_request_bytes), 1)
            self.assertTrue(outcome.receipt_path.is_file())
            self.assertTrue(outcome.raw_response_path.is_file())
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(repository), "status", "--porcelain=v1"],
                    check=True,
                    shell=False,
                    stdout=subprocess.PIPE,
                ).stdout,
                b"",
            )

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

    def test_live_os_runtime_freshness_is_rebuilt_before_semantic_invocation(self):
        prepared, material = _prepared_v1(
            run_id="run-live-runtime-drift",
            context_id="context-live-runtime-drift",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, caller_freshness = _fake_preflight(backend)
        live_freshness = dataclasses.replace(
            caller_freshness,
            operating_environment_sha256=sha256_bytes(b"live-runtime-drift"),
        )

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            controller_module,
            "build_preflight_freshness",
            return_value=live_freshness,
        ):
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                caller_freshness,
                Path(directory),
            )

        self.assertEqual(outcome.state, RunnerState.ISOLATION_PREFLIGHT_FAILED)
        self.assertEqual(
            backend.received_request_bytes,
            [],
            "live runtime drift must stop before semantic request transmission",
        )

    def test_stale_caller_freshness_cannot_authorize_live_descriptor_drift(self):
        prepared, material = _prepared_v1(
            run_id="run-live-descriptor-drift",
            context_id="context-live-descriptor-drift",
        )
        drifts = {}
        seed_backend = _fake_backend(canonical_json_bytes(material["output"]))
        baseline_descriptor = seed_backend.describe()
        drifts["capacity"] = dataclasses.replace(
            baseline_descriptor,
            max_request_bytes=baseline_descriptor.max_request_bytes - 1,
        )
        drifts["observation-method"] = dataclasses.replace(
            baseline_descriptor,
            observations=(
                dataclasses.replace(
                    baseline_descriptor.observations[0],
                    method="changed-test-observation-method",
                ),
                *baseline_descriptor.observations[1:],
            ),
        )
        drifts["observation-evidence"] = dataclasses.replace(
            baseline_descriptor,
            observations=(
                dataclasses.replace(
                    baseline_descriptor.observations[0],
                    evidence_sha256=sha256_bytes(b"changed-test-observation-evidence"),
                ),
                *baseline_descriptor.observations[1:],
            ),
        )
        drifts["observation-classification"] = dataclasses.replace(
            baseline_descriptor,
            observations=(
                dataclasses.replace(
                    baseline_descriptor.observations[0],
                    classification=CapabilityClass.UNTESTED,
                ),
                *baseline_descriptor.observations[1:],
            ),
        )

        wrong_states = []
        transmitted = []
        for index, (label, changed_descriptor) in enumerate(drifts.items()):
            case_prepared, case_material = _prepared_v1(
                run_id=f"run-live-descriptor-drift-{index}",
                context_id=f"context-live-descriptor-drift-{index}",
            )
            backend = _fake_backend(canonical_json_bytes(case_material["output"]))
            preflight, stale_caller_freshness = _fake_preflight(backend)
            backend._descriptor = changed_descriptor
            with tempfile.TemporaryDirectory() as directory:
                outcome, _, _, _ = self._execute(
                    case_prepared,
                    backend,
                    preflight,
                    stale_caller_freshness,
                    Path(directory),
                )
            if outcome.state is not RunnerState.ISOLATION_PREFLIGHT_FAILED:
                wrong_states.append((label, outcome.state))
            if backend.received_request_bytes:
                transmitted.append(label)

        self.assertEqual(wrong_states, [])
        self.assertEqual(
            transmitted,
            [],
            "capacity and complete capability-observation drift must stop semantic bytes",
        )

    def test_descriptor_drift_during_guarded_setup_stops_at_invoke_boundary(self):
        prepared, material = _prepared_v1(
            run_id="run-invoke-boundary-drift",
            context_id="context-invoke-boundary-drift",
        )
        seed_backend = _fake_backend(canonical_json_bytes(material["output"]))
        baseline = seed_backend.describe()
        drifts = {
            "claim-observation-method": dataclasses.replace(
                baseline,
                observations=(
                    dataclasses.replace(
                        baseline.observations[0],
                        method="workspace-stage-observation-method-drift",
                    ),
                    *baseline.observations[1:],
                ),
            ),
            "claim-capacity": dataclasses.replace(
                baseline,
                max_request_bytes=baseline.max_request_bytes - 1,
            ),
            "workspace-identity": dataclasses.replace(
                baseline,
                identity=dataclasses.replace(
                    baseline.identity,
                    model_revision_identity="workspace-stage-identity-drift",
                ),
            ),
        }

        wrong_states = []
        transmitted = []
        for index, (label, changed_descriptor) in enumerate(drifts.items()):
            case_prepared, case_material = _prepared_v1(
                run_id=f"run-invoke-boundary-drift-{index}",
                context_id=f"context-invoke-boundary-drift-{index}",
            )
            backend = _fake_backend(canonical_json_bytes(case_material["output"]))
            preflight, freshness = _fake_preflight(backend)

            if label.startswith("claim-"):
                original_boundary = controller_module._acquire_durable_run_claim

                def drift_at_boundary(*args, changed=changed_descriptor, **kwargs):
                    result = original_boundary(*args, **kwargs)
                    backend._descriptor = changed
                    return result

                patcher = mock.patch.object(
                    controller_module,
                    "_acquire_durable_run_claim",
                    side_effect=drift_at_boundary,
                )
            else:
                original_boundary = controller_module.TaskWorkspace.create

                def drift_at_boundary(*args, changed=changed_descriptor, **kwargs):
                    result = original_boundary(*args, **kwargs)
                    backend._descriptor = changed
                    return result

                patcher = mock.patch.object(
                    controller_module.TaskWorkspace,
                    "create",
                    side_effect=drift_at_boundary,
                )

            with tempfile.TemporaryDirectory() as directory, patcher:
                outcome, _, _, _ = self._execute(
                    case_prepared,
                    backend,
                    preflight,
                    freshness,
                    Path(directory),
                )
            if outcome.state is not RunnerState.ISOLATION_PREFLIGHT_FAILED:
                wrong_states.append((label, outcome.state))
            if backend.received_request_bytes:
                transmitted.append(label)

        self.assertEqual(wrong_states, [])
        self.assertEqual(
            transmitted,
            [],
            "guarded setup descriptor drift must stop before semantic invocation",
        )

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

    def test_v1_adapter_rejects_unbound_package_schema_versions_before_request_artifacts(self):
        material = _v1_material()
        for package_schema_version in (
            "joewrks.semantic-review-input/999.0",
            "joewrks.semantic-review/2.1",
        ):
            with self.subTest(package_schema_version=package_schema_version):
                run_identity = dataclasses.replace(
                    material["run_identity"],
                    package_schema_version=package_schema_version,
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "v1 package schema version does not match the authoritative schema",
                ):
                    prepare_semantic_review_v1(
                        verified_package=material["package"],
                        package_archive_bytes=material["package_bytes"],
                        reviewer_brief_bytes=material["brief_bytes"],
                        run_envelope=material["envelope"],
                        output_schema_bytes=material["schema_bytes"],
                        run_identity=run_identity,
                    )

    def test_v1_adapter_rejects_unbound_source_definition_digest_before_request_artifacts(self):
        material = _v1_material()
        run_identity = dataclasses.replace(
            material["run_identity"],
            source_definition_digest="a" * 64,
        )
        with self.assertRaisesRegex(
            ValueError,
            "v1 source definition digest must be absent",
        ):
            prepare_semantic_review_v1(
                verified_package=material["package"],
                package_archive_bytes=material["package_bytes"],
                reviewer_brief_bytes=material["brief_bytes"],
                run_envelope=material["envelope"],
                output_schema_bytes=material["schema_bytes"],
                run_identity=run_identity,
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

    def test_non_finite_json_constants_map_to_review_output_invalid(self):
        for index, constant in enumerate((b"NaN", b"Infinity", b"-Infinity")):
            with self.subTest(constant=constant), tempfile.TemporaryDirectory() as directory:
                prepared, _ = _prepared_v1(
                    run_id=f"run-non-finite-{index}",
                    context_id=f"context-non-finite-{index}",
                )
                raw_response = b'{"value":' + constant + b"}"
                backend = _fake_backend(raw_response)
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
                self.assertEqual(outcome.raw_response_path.read_bytes(), raw_response)
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
                    / "cleanup-failure.json"
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

    def test_success_receipt_consumes_inventory_from_the_canonical_request(self):
        prepared, material = _prepared_v1(
            run_id="run-request-inventory",
            context_id="context-request-inventory",
        )
        request = build_canonical_request(
            prepared.run_identity,
            prepared.artifacts,
            controller_only_hashes=dict(prepared.controller_only_hashes),
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            controller_module,
            "build_permitted_inventory",
            side_effect=AssertionError(
                "controller must consume the inventory already bound to the request"
            ),
            create=True,
        ):
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                Path(directory),
            )
            self.assertEqual(outcome.state, RunnerState.REVIEW_COMPLETED)
            receipt = json.loads(outcome.receipt_path.read_bytes())
            self.assertEqual(
                receipt["permitted_input_inventory"],
                [dataclasses.asdict(item) for item in request.inventory],
            )

    def test_completed_run_identity_is_permanently_reserved_before_second_invoke(self):
        prepared, material = _prepared_v1(
            run_id="run-permanent-reservation",
            context_id="context-permanent-reservation",
        )
        first_raw = canonical_json_bytes(material["output"])
        first_backend = _fake_backend(first_raw)
        first_preflight, first_freshness = _fake_preflight(first_backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            evidence_root = base / "evidence"
            first = execute_review(
                prepared,
                backend=first_backend,
                preflight=first_preflight,
                current_freshness=first_freshness,
                evidence_root=evidence_root,
                transient_parent=transient_parent,
                repository_root=repository,
                execution_mode="SYNTHETIC_TEST",
            )
            self.assertEqual(first.state, RunnerState.REVIEW_COMPLETED)
            first_raw_readback = first.raw_response_path.read_bytes()
            first_receipt_readback = first.receipt_path.read_bytes()
            claims = list((evidence_root / "run-claims").glob("*.json"))
            self.assertEqual(len(claims), 1)
            expected_claim_key = sha256_bytes(
                canonical_json_bytes(
                    {
                        "context_id": prepared.run_identity.context_id,
                        "review_run_id": prepared.run_identity.review_run_id,
                    }
                )
            )
            self.assertEqual(claims[0].name, f"{expected_claim_key}.json")
            self.assertEqual(
                json.loads(claims[0].read_bytes()),
                {
                    "claim_schema_version": "joewrks.reviewer-runner-run-claim/1.0",
                    "request_sha256": sha256_bytes(
                        first_backend.received_request_bytes[0]
                    ),
                    "run_identity": dataclasses.asdict(prepared.run_identity),
                },
            )
            first_receipt = json.loads(first_receipt_readback)
            self.assertEqual(
                first_receipt["response_identity"]["raw_response_sha256"],
                sha256_bytes(first_raw_readback),
            )

            second_backend = _fake_backend(
                b" " + first_raw,
                metadata_drift={
                    "provider_request_id": "deterministic-fake-request-second"
                },
            )
            second_preflight, second_freshness = _fake_preflight(second_backend)
            second = execute_review(
                prepared,
                backend=second_backend,
                preflight=second_preflight,
                current_freshness=second_freshness,
                evidence_root=evidence_root,
                transient_parent=transient_parent,
                repository_root=repository,
                execution_mode="SYNTHETIC_TEST",
            )

            self.assertEqual(second.state, RunnerState.PACKAGE_BINDING_MISMATCH)
            self.assertEqual(
                len(first_backend.received_request_bytes)
                + len(second_backend.received_request_bytes),
                1,
                "a completed run identity must block reuse before transmission",
            )
            self.assertEqual(first.raw_response_path.read_bytes(), first_raw_readback)
            self.assertEqual(first.receipt_path.read_bytes(), first_receipt_readback)
            self.assertEqual(
                json.loads(first.receipt_path.read_bytes())["response_identity"][
                    "raw_response_sha256"
                ],
                sha256_bytes(first.raw_response_path.read_bytes()),
            )

    def test_durable_claim_store_failure_blocks_invoke_and_checks_source(self):
        prepared, material = _prepared_v1(
            run_id="run-claim-store-failure",
            context_id="context-claim-store-failure",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        original_verify = controller_module.verify_source_unchanged
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            controller_module,
            "atomic_claim_evidence",
            side_effect=OSError("forced durable claim store failure"),
        ), mock.patch.object(
            controller_module,
            "verify_source_unchanged",
            wraps=original_verify,
        ) as verify:
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                Path(directory),
            )
        self.assertEqual(outcome.state, RunnerState.REVIEWER_EXECUTION_FAILED)
        self.assertEqual(backend.received_request_bytes, [])
        self.assertEqual(verify.call_count, 1)
        self.assertTrue(any("durable run claim failed" in e for e in outcome.errors))

    def test_post_claim_source_failure_still_records_diagnostic(self):
        prepared, material = _prepared_v1(
            run_id="run-guarded-source-diagnostic",
            context_id="context-guarded-source-diagnostic",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            evidence_root = base / "evidence"
            with mock.patch.object(
                controller_module,
                "load_used_provider_request_ids",
                side_effect=ValueError("forced replay index failure"),
            ), mock.patch.object(
                controller_module,
                "verify_source_unchanged",
                side_effect=ValueError("forced guarded source drift"),
            ) as verify:
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
            self.assertEqual(verify.call_count, 1)
            self.assertEqual(len(backend.received_request_bytes), 0)
            diagnostic = (
                evidence_root
                / "runs"
                / prepared.run_identity.review_run_id
                / prepared.run_identity.context_id
                / "source-readback-failure.json"
            )
            self.assertTrue(diagnostic.is_file())

    def test_controller_topology_rejects_reparse_evidence_root_without_escape(self):
        prepared, material = _prepared_v1(
            run_id="run-claim-reparse-root",
            context_id="context-claim-reparse-root",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            outside = base / "outside-evidence"
            outside.mkdir()
            outside_receipt = outside / "runs" / "prior" / "context"
            outside_receipt.mkdir(parents=True)
            (outside_receipt / "runner-receipt.json").write_bytes(
                b'{"outside":"must-not-be-indexed"}'
            )
            outside_before = {
                path.relative_to(outside).as_posix(): path.read_bytes()
                for path in outside.rglob("*")
                if path.is_file()
            }
            evidence_alias = base / "evidence-alias"
            evidence_alias.symlink_to(outside, target_is_directory=True)
            outcome = execute_review(
                prepared,
                backend=backend,
                preflight=preflight,
                current_freshness=freshness,
                evidence_root=evidence_alias,
                transient_parent=transient_parent,
                repository_root=repository,
                execution_mode="SYNTHETIC_TEST",
            )
            self.assertEqual(outcome.state, RunnerState.REVIEWER_EXECUTION_FAILED)
            self.assertEqual(len(backend.received_request_bytes), 0)
            self.assertEqual(
                outcome.errors,
                (
                    "unsafe runner path topology: evidence_root contains a symlink or junction",
                ),
            )
            self.assertEqual(
                {
                    path.relative_to(outside).as_posix(): path.read_bytes()
                    for path in outside.rglob("*")
                    if path.is_file()
                },
                outside_before,
            )

    def test_durable_claim_survives_post_claim_preinvoke_workspace_failure(self):
        prepared, material = _prepared_v1(
            run_id="run-claim-workspace-failure",
            context_id="context-claim-workspace-failure",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            evidence_root = base / "evidence"
            missing_transient_parent = base / "missing-transient"
            first = execute_review(
                prepared,
                backend=backend,
                preflight=preflight,
                current_freshness=freshness,
                evidence_root=evidence_root,
                transient_parent=missing_transient_parent,
                repository_root=repository,
                execution_mode="SYNTHETIC_TEST",
            )
            self.assertEqual(first.state, RunnerState.REVIEWER_EXECUTION_FAILED)
            self.assertEqual(len(backend.received_request_bytes), 0)
            claims = list((evidence_root / "run-claims").glob("*.json"))
            self.assertEqual(len(claims), 1)
            claim_bytes = claims[0].read_bytes()

            valid_transient_parent = base / "valid-transient"
            valid_transient_parent.mkdir()
            second = execute_review(
                prepared,
                backend=backend,
                preflight=preflight,
                current_freshness=freshness,
                evidence_root=evidence_root,
                transient_parent=valid_transient_parent,
                repository_root=repository,
                execution_mode="SYNTHETIC_TEST",
            )
            self.assertEqual(second.state, RunnerState.PACKAGE_BINDING_MISMATCH)
            self.assertEqual(len(backend.received_request_bytes), 0)
            self.assertEqual(claims[0].read_bytes(), claim_bytes)

    def test_durable_evidence_claim_blocks_same_identity_across_transient_parents(self):
        prepared, material = _prepared_v1(
            run_id="run-durable-claim",
            context_id="context-durable-claim",
        )
        first_raw = canonical_json_bytes(material["output"])
        first_backend = _fake_backend(first_raw)
        first_preflight, first_freshness = _fake_preflight(first_backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            evidence_root = base / "evidence"
            transient_first = base / "transient-first"
            transient_second = base / "transient-second"
            transient_first.mkdir()
            transient_second.mkdir()
            first = execute_review(
                prepared,
                backend=first_backend,
                preflight=first_preflight,
                current_freshness=first_freshness,
                evidence_root=evidence_root,
                transient_parent=transient_first,
                repository_root=repository,
                execution_mode="SYNTHETIC_TEST",
            )
            self.assertEqual(first.state, RunnerState.REVIEW_COMPLETED)
            first_raw_readback = first.raw_response_path.read_bytes()
            first_receipt_readback = first.receipt_path.read_bytes()

            second_backend = _fake_backend(
                b" " + first_raw,
                metadata_drift={"provider_request_id": "cross-parent-second-request"},
            )
            second_preflight, second_freshness = _fake_preflight(second_backend)
            original_verify = controller_module.verify_source_unchanged
            with mock.patch.object(
                controller_module,
                "verify_source_unchanged",
                wraps=original_verify,
            ) as verify:
                second = execute_review(
                    prepared,
                    backend=second_backend,
                    preflight=second_preflight,
                    current_freshness=second_freshness,
                    evidence_root=evidence_root,
                    transient_parent=transient_second,
                    repository_root=repository,
                    execution_mode="SYNTHETIC_TEST",
                )

            self.assertNotEqual(second.state, RunnerState.REVIEW_COMPLETED)
            self.assertEqual(verify.call_count, 1)
            self.assertEqual(
                len(second_backend.received_request_bytes),
                0,
                "durable same-run/context claim must block before transmission",
            )
            self.assertEqual(first.raw_response_path.read_bytes(), first_raw_readback)
            self.assertEqual(first.receipt_path.read_bytes(), first_receipt_readback)
            receipt = json.loads(first.receipt_path.read_bytes())
            self.assertEqual(
                receipt["response_identity"]["raw_response_sha256"],
                sha256_bytes(first.raw_response_path.read_bytes()),
            )

    def test_invalid_output_and_cleanup_failure_have_distinct_immutable_diagnostics(self):
        prepared, _ = _prepared_v1(
            run_id="run-compound-failure",
            context_id="context-compound-failure",
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
            delegate = _fake_backend(b'{"unexpected":true}')
            backend = _PostInvokeSideEffectBackend(delegate, marker.unlink)
            preflight, freshness = _fake_preflight(backend)
            outcome, _, _, evidence_root = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                base,
            )
            run_evidence = (
                evidence_root
                / "runs"
                / prepared.run_identity.review_run_id
                / prepared.run_identity.context_id
            )
            initial = json.loads((run_evidence / "failure.json").read_bytes())
            self.assertTrue(
                (run_evidence / "cleanup-failure.json").is_file(),
                "cleanup failure must use a distinct immutable diagnostic",
            )
            cleanup = json.loads(
                (run_evidence / "cleanup-failure.json").read_bytes()
            )
            self.assertEqual(
                initial["runner_state"], RunnerState.REVIEW_OUTPUT_INVALID.value
            )
            self.assertTrue(
                any("cleanup failed" in error for error in cleanup["errors"])
            )
            self.assertEqual(outcome.state, RunnerState.REVIEWER_EXECUTION_FAILED)
            self.assertTrue(any("cleanup failed" in error for error in outcome.errors))

    def test_failure_evidence_publication_error_is_never_silently_swallowed(self):
        prepared, _ = _prepared_v1(
            run_id="run-failure-evidence",
            context_id="context-failure-evidence",
        )
        backend = _fake_backend(b'{"unexpected":true}')
        preflight, freshness = _fake_preflight(backend)
        original_freeze = controller_module.atomic_freeze_evidence

        def fail_initial_failure_evidence(content, target_path):
            if Path(target_path).name == "failure.json":
                raise OSError("forced initial failure evidence error")
            return original_freeze(content, target_path)

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            controller_module,
            "atomic_freeze_evidence",
            side_effect=fail_initial_failure_evidence,
        ):
            outcome, _, _, _ = self._execute(
                prepared,
                backend,
                preflight,
                freshness,
                Path(directory),
            )
        self.assertEqual(outcome.state, RunnerState.REVIEWER_EXECUTION_FAILED)
        self.assertTrue(
            any(
                "failure.json evidence publication failed" in error
                for error in outcome.errors
            )
        )

    def test_cleanup_evidence_failure_does_not_suppress_repository_drift(self):
        prepared, material = _prepared_v1(
            run_id="run-cleanup-evidence-drift",
            context_id="context-cleanup-evidence-drift",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            evidence_root = base / "evidence"
            backend = _fake_backend(canonical_json_bytes(material["output"]))
            preflight, freshness = _fake_preflight(backend)
            original_freeze = controller_module.atomic_freeze_evidence

            def fail_cleanup_evidence(content, target_path):
                if Path(target_path).name == "cleanup.json":
                    (repository / "unexpected.txt").write_bytes(b"drift")
                    raise OSError("forced cleanup evidence error")
                return original_freeze(content, target_path)

            with mock.patch.object(
                controller_module,
                "atomic_freeze_evidence",
                side_effect=fail_cleanup_evidence,
            ):
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
            self.assertTrue(
                any("cleanup evidence publication failed" in e for e in outcome.errors)
            )
            self.assertTrue(any("source readback failed" in e for e in outcome.errors))

    def test_cleanup_failure_does_not_suppress_repository_drift(self):
        prepared, material = _prepared_v1(
            run_id="run-cleanup-drift",
            context_id="context-cleanup-drift",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            evidence_root = base / "evidence"
            marker = (
                transient_parent
                / "joewrks-reviewer-runner"
                / prepared.run_identity.review_run_id
                / ".joewrks-runner-owner.json"
            )
            delegate = _fake_backend(canonical_json_bytes(material["output"]))

            def break_cleanup_and_mutate_source():
                marker.unlink()
                (repository / "unexpected.txt").write_bytes(b"drift")

            backend = _PostInvokeSideEffectBackend(
                delegate,
                break_cleanup_and_mutate_source,
            )
            preflight, freshness = _fake_preflight(backend)
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
            self.assertTrue(any("cleanup failed" in e for e in outcome.errors))
            self.assertTrue(any("source readback failed" in e for e in outcome.errors))
            source_diagnostic = (
                evidence_root
                / "runs"
                / prepared.run_identity.review_run_id
                / prepared.run_identity.context_id
                / "source-readback-failure.json"
            )
            self.assertTrue(source_diagnostic.is_file())

    def test_early_gate_exit_still_requires_repository_readback(self):
        prepared, _ = _prepared_v1(
            run_id="run-early-source-readback",
            context_id="context-early-source-readback",
        )
        freshness = build_preflight_freshness(None)
        preflight = run_isolation_preflight(
            None,
            freshness=freshness,
            nonce_source=_nonce_bytes,
        )
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            controller_module,
            "verify_source_unchanged",
            side_effect=ValueError("injected repository drift"),
        ) as verify:
            outcome, _, _, _ = self._execute(
                prepared,
                None,
                preflight,
                freshness,
                Path(directory),
                execution_mode="REAL_REVIEW",
            )
        self.assertEqual(verify.call_count, 1)
        self.assertEqual(outcome.state, RunnerState.REVIEWER_EXECUTION_FAILED)
        self.assertTrue(any("source readback failed" in e for e in outcome.errors))

    def test_malformed_replay_index_blocks_transmission_before_invoke(self):
        prepared, material = _prepared_v1(
            run_id="run-malformed-index",
            context_id="context-malformed-index",
        )
        backend = _fake_backend(canonical_json_bytes(material["output"]))
        preflight, freshness = _fake_preflight(backend)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = _init_clean_repository(base)
            transient_parent = base / "transient"
            transient_parent.mkdir()
            evidence_root = base / "evidence"
            malformed = evidence_root / "runs" / "prior" / "context"
            malformed.mkdir(parents=True)
            (malformed / "runner-receipt.json").write_bytes(b'{"invalid":true}')
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
            self.assertEqual(outcome.state, RunnerState.PACKAGE_BINDING_MISMATCH)
            self.assertEqual(backend.received_request_bytes, [])
            self.assertIsNone(outcome.raw_response_path)

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
