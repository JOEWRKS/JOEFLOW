"""Ordered, fail-closed orchestration for one isolated reviewer request."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .backend import (
    BackendDescriptor,
    BackendInvocationError,
    ToollessInferenceBackend,
    validate_backend_descriptor,
)
from .evidence import (
    CleanupResult,
    EvidenceClaimConflict,
    EvidenceRootLease,
    TaskWorkspace,
    acquire_evidence_root_lease,
    atomic_claim_evidence,
    atomic_freeze_evidence,
    capture_source_snapshot,
    load_used_provider_request_ids,
    verify_source_unchanged,
)
from .identity import (
    CapabilityClass,
    RunnerIdentityError,
    RunnerState,
    backend_identity_sha256,
    build_runner_receipt,
    canonical_json_bytes,
    receipt_document,
    sha256_bytes,
)
from .preflight import (
    IsolationReceipt,
    PreflightFreshness,
    PreflightResult,
    build_per_run_isolation_receipt,
    classify_backend_eligibility,
    validate_preflight_freshness,
)
from .request import (
    RequestError,
    build_canonical_request,
)
from .response import BoundResponse, ResponseValidationError, freeze_validate_bind_response
from .semantic_review import PreparedReview


_EXECUTION_MODES = frozenset({"REAL_REVIEW", "SYNTHETIC_TEST"})


@dataclass(frozen=True)
class RunOutcome:
    state: RunnerState
    capability_classification: CapabilityClass
    execution_mode: str
    receipt_path: Path | None
    raw_response_path: Path | None
    errors: tuple[str, ...]


def execute_review(
    prepared: PreparedReview,
    *,
    backend: ToollessInferenceBackend | None,
    preflight: PreflightResult,
    current_freshness: PreflightFreshness,
    evidence_root: Path,
    transient_parent: Path,
    repository_root: Path,
    timeout_seconds: int = 60,
    execution_mode: str = "REAL_REVIEW",
) -> RunOutcome:
    """Execute at most one request and expose success only after cleanup."""

    classification = _preflight_classification(preflight)
    try:
        before = capture_source_snapshot(repository_root)
    except (OSError, TypeError, ValueError) as error:
        return _outcome(
            RunnerState.REVIEWER_EXECUTION_FAILED,
            classification,
            execution_mode,
            errors=(str(error),),
        )

    try:
        _validate_prepared_review(prepared)
        request = build_canonical_request(
            prepared.run_identity,
            prepared.artifacts,
            controller_only_hashes=dict(prepared.controller_only_hashes),
        )
    except (RequestError, RunnerIdentityError, TypeError, ValueError) as error:
        return _finish_early(
            RunnerState.PACKAGE_BINDING_MISMATCH,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            prepared=prepared,
            errors=(str(error),),
        )

    descriptor = _describe_backend(backend)
    authorization = _authorize_execution(
        execution_mode,
        descriptor,
        preflight,
        current_freshness,
        request_byte_count=len(request.content),
    )
    if authorization is not None:
        state, classification, message = authorization
        return _finish_early(
            state,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            prepared=prepared,
            errors=(message,),
        )
    if backend is None or descriptor is None:
        return _finish_early(
            RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            prepared=prepared,
            errors=("backend is unavailable",),
        )

    try:
        isolation = _build_isolation_receipt(
            execution_mode,
            descriptor,
            preflight,
            current_freshness,
            request.sha256,
        )
    except (RunnerIdentityError, TypeError, ValueError) as error:
        return _finish_early(
            RunnerState.ISOLATION_PREFLIGHT_FAILED,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            prepared=prepared,
            errors=(str(error),),
        )

    try:
        evidence_lease = acquire_evidence_root_lease(evidence_root)
    except Exception as error:
        return _finish_early(
            RunnerState.REVIEWER_EXECUTION_FAILED,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            prepared=prepared,
            errors=(f"evidence-root lease failed: {error}",),
        )

    release_error: Exception | None = None
    try:
        try:
            outcome = _execute_with_evidence_root_lease(
                evidence_lease,
                prepared=prepared,
                backend=backend,
                descriptor=descriptor,
                preflight=preflight,
                isolation=isolation,
                request=request,
                transient_parent=transient_parent,
                repository_root=repository_root,
                before=before,
                classification=classification,
                execution_mode=execution_mode,
                timeout_seconds=timeout_seconds,
            )
        except Exception as error:
            outcome = _finish_early(
                RunnerState.REVIEWER_EXECUTION_FAILED,
                classification,
                execution_mode,
                before=before,
                repository_root=repository_root,
                active_evidence_lease=evidence_lease,
                prepared=prepared,
                errors=(f"evidence-root guarded execution failed: {error}",),
            )
    finally:
        try:
            evidence_lease.close()
        except Exception as error:
            release_error = error

    if release_error is not None:
        return _outcome(
            RunnerState.REVIEWER_EXECUTION_FAILED,
            classification,
            execution_mode,
            raw_response_path=outcome.raw_response_path,
            errors=(*outcome.errors, f"evidence-root lease release failed: {release_error}"),
        )
    return outcome


def _execute_with_evidence_root_lease(
    evidence_lease: EvidenceRootLease,
    *,
    prepared: PreparedReview,
    backend: ToollessInferenceBackend,
    descriptor: BackendDescriptor,
    preflight: PreflightResult,
    isolation: IsolationReceipt,
    request,
    transient_parent: Path,
    repository_root: Path,
    before,
    classification: CapabilityClass,
    execution_mode: str,
    timeout_seconds: int,
) -> RunOutcome:
    evidence_root = evidence_lease.root
    try:
        evidence_lease.verify()
        _acquire_durable_run_claim(evidence_root, prepared, request.sha256)
        evidence_lease.verify()
    except EvidenceClaimConflict as error:
        return _finish_early(
            RunnerState.PACKAGE_BINDING_MISMATCH,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            active_evidence_lease=evidence_lease,
            prepared=prepared,
            errors=(f"durable run claim conflict: {error}",),
        )
    except Exception as error:
        return _finish_early(
            RunnerState.REVIEWER_EXECUTION_FAILED,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            active_evidence_lease=evidence_lease,
            prepared=prepared,
            errors=(f"durable run claim failed: {error}",),
        )

    try:
        evidence_lease.verify()
        used_provider_request_ids = load_used_provider_request_ids(evidence_root)
        evidence_lease.verify()
    except Exception as error:
        return _finish_early(
            RunnerState.PACKAGE_BINDING_MISMATCH,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            active_evidence_lease=evidence_lease,
            prepared=prepared,
            errors=(f"replay index validation failed: {error}",),
        )

    try:
        workspace = TaskWorkspace.create(
            transient_parent,
            prepared.run_identity.review_run_id,
        )
    except (OSError, TypeError, ValueError) as error:
        return _finish_early(
            RunnerState.REVIEWER_EXECUTION_FAILED,
            classification,
            execution_mode,
            before=before,
            repository_root=repository_root,
            active_evidence_lease=evidence_lease,
            prepared=prepared,
            errors=(str(error),),
        )

    state = RunnerState.REVIEW_COMPLETED
    errors: list[str] = []
    bound: BoundResponse | None = None
    receipt = None
    raw_response_path: Path | None = None
    preserved_paths: list[Path] = []
    try:
        evidence_lease.verify()
        response = backend.invoke(
            request.content,
            timeout_seconds=timeout_seconds,
        )
        evidence_lease.verify()
        bound = freeze_validate_bind_response(
            response,
            expected_run=prepared.run_identity,
            expected_backend=descriptor.identity,
            expected_request_sha256=request.sha256,
            evidence_root=evidence_root,
            output_validator=prepared.output_validator,
            used_provider_request_ids=used_provider_request_ids,
        )
        evidence_lease.verify()
        raw_response_path = bound.frozen.path
        preserved_paths.append(bound.frozen.path)
        receipt = build_runner_receipt(
            state=RunnerState.REVIEW_COMPLETED,
            run_identity=prepared.run_identity,
            backend_identity=descriptor.identity,
            permitted_input_inventory=request.inventory,
            request_sha256=request.sha256,
            capability_preflight_sha256=preflight.evidence_sha256,
            isolation_receipt_sha256=isolation.receipt_sha256,
            response_identity=bound.identity,
        )
    except BackendInvocationError as error:
        state = RunnerState.REVIEWER_EXECUTION_FAILED
        errors.append(f"{error.code}: {error}")
    except ResponseValidationError as error:
        state = error.runner_state
        errors.append(f"{error.code}: {error}")
        raw_response_path = _existing_raw_response_path(evidence_root, prepared)
        if raw_response_path is not None:
            preserved_paths.append(raw_response_path)
    except RunnerIdentityError as error:
        state = RunnerState.PACKAGE_BINDING_MISMATCH
        errors.append(f"{error.code}: {error}")
        if bound is not None:
            raw_response_path = bound.frozen.path
            preserved_paths.append(bound.frozen.path)
    except Exception as error:
        state = RunnerState.REVIEWER_EXECUTION_FAILED
        errors.append(str(error))

    if state is not RunnerState.REVIEW_COMPLETED:
        try:
            evidence_lease.verify()
        except Exception as error:
            state = RunnerState.REVIEWER_EXECUTION_FAILED
            errors.append(f"evidence-root verification failed: {error}")
        else:
            if not _record_failure_evidence(
                "failure.json",
                state,
                errors,
                evidence_root,
                prepared,
                preserved_paths=preserved_paths,
            ):
                state = RunnerState.REVIEWER_EXECUTION_FAILED

    cleanup: CleanupResult | None = None
    try:
        evidence_lease.verify()
        cleanup = workspace.cleanup(
            preserved_evidence_paths=tuple(preserved_paths),
            sibling_paths=_sibling_run_paths(transient_parent, prepared),
        )
    except Exception as error:
        state = RunnerState.REVIEWER_EXECUTION_FAILED
        errors.append(f"cleanup failed: {error}")
        try:
            evidence_lease.verify()
        except Exception as verification_error:
            errors.append(f"evidence-root verification failed: {verification_error}")
        else:
            _record_failure_evidence(
                "cleanup-failure.json",
                state,
                errors,
                evidence_root,
                prepared,
            )

    if cleanup is not None:
        try:
            evidence_lease.verify()
            _freeze_cleanup_evidence(
                cleanup,
                evidence_root,
                prepared,
            )
        except Exception as error:
            state = RunnerState.REVIEWER_EXECUTION_FAILED
            errors.append(f"cleanup evidence publication failed: {error}")
            try:
                evidence_lease.verify()
            except Exception as verification_error:
                errors.append(
                    f"evidence-root verification failed: {verification_error}"
                )
            else:
                _record_failure_evidence(
                    "cleanup-evidence-failure.json",
                    state,
                    errors,
                    evidence_root,
                    prepared,
                )

    try:
        verify_source_unchanged(before, repository_root)
    except Exception as error:
        state = RunnerState.REVIEWER_EXECUTION_FAILED
        errors.append(f"source readback failed: {error}")
        try:
            evidence_lease.verify()
        except Exception as verification_error:
            errors.append(f"evidence-root verification failed: {verification_error}")
        else:
            _record_failure_evidence(
                "source-readback-failure.json",
                state,
                errors,
                evidence_root,
                prepared,
            )

    receipt_path: Path | None = None
    if state is RunnerState.REVIEW_COMPLETED and receipt is not None and cleanup is not None:
        try:
            evidence_lease.verify()
            receipt_path = _freeze_receipt(receipt, evidence_root, prepared)
            evidence_lease.verify()
        except Exception as error:
            state = RunnerState.REVIEWER_EXECUTION_FAILED
            errors.append(f"receipt evidence publication failed: {error}")
            try:
                evidence_lease.verify()
            except Exception as verification_error:
                errors.append(
                    f"evidence-root verification failed: {verification_error}"
                )
            else:
                _record_failure_evidence(
                    "receipt-publication-failure.json",
                    state,
                    errors,
                    evidence_root,
                    prepared,
                )
            receipt_path = None

    evidence_lease.verify()
    return _outcome(
        state,
        classification,
        execution_mode,
        receipt_path=receipt_path,
        raw_response_path=raw_response_path,
        errors=tuple(errors),
    )


def _validate_prepared_review(prepared: PreparedReview) -> None:
    if type(prepared) is not PreparedReview:
        raise ValueError("prepared must be an exact PreparedReview")
    if not isinstance(prepared.artifacts, tuple):
        raise ValueError("prepared artifacts must be an immutable tuple")
    if not isinstance(prepared.controller_only_hashes, tuple):
        raise ValueError("controller-only hashes must be an immutable tuple")
    if len(dict(prepared.controller_only_hashes)) != len(prepared.controller_only_hashes):
        raise ValueError("controller-only hash labels must be unique")
    if not callable(prepared.output_validator):
        raise ValueError("prepared output validator must be callable")


def _acquire_durable_run_claim(
    evidence_root: Path,
    prepared: PreparedReview,
    request_sha256: str,
) -> Path:
    identity_key = sha256_bytes(
        canonical_json_bytes(
            {
                "context_id": prepared.run_identity.context_id,
                "review_run_id": prepared.run_identity.review_run_id,
            }
        )
    )
    claim = {
        "claim_schema_version": "joewrks.reviewer-runner-run-claim/1.0",
        "request_sha256": request_sha256,
        "run_identity": asdict(prepared.run_identity),
    }
    return atomic_claim_evidence(
        canonical_json_bytes(claim),
        evidence_root / "run-claims" / f"{identity_key}.json",
    )


def _describe_backend(
    backend: ToollessInferenceBackend | None,
) -> BackendDescriptor | None:
    if backend is None:
        return None
    try:
        descriptor = backend.describe()
        validate_backend_descriptor(descriptor)
    except Exception:
        return None
    return descriptor


def _authorize_execution(
    execution_mode: str,
    descriptor: BackendDescriptor | None,
    preflight: PreflightResult,
    current_freshness: PreflightFreshness,
    *,
    request_byte_count: int,
) -> tuple[RunnerState, CapabilityClass, str] | None:
    classification = _preflight_classification(preflight)
    if execution_mode not in _EXECUTION_MODES:
        return (
            RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE,
            classification,
            "execution mode is not permitted",
        )
    if descriptor is None:
        return (
            RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE,
            classification,
            "backend descriptor is unavailable",
        )
    eligibility = classify_backend_eligibility(descriptor)
    if request_byte_count > descriptor.max_request_bytes:
        return (
            RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE,
            eligibility,
            "backend request capacity is insufficient",
        )
    if execution_mode == "REAL_REVIEW":
        if eligibility is not CapabilityClass.OBSERVED_PASS:
            return (
                RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE,
                eligibility,
                "real review requires an eligible observed backend",
            )
        required_classification = CapabilityClass.OBSERVED_PASS
    else:
        if not descriptor.identity.is_test_double:
            return (
                RunnerState.ISOLATION_CAPABILITY_UNAVAILABLE,
                eligibility,
                "synthetic execution requires the deterministic test boundary",
            )
        required_classification = CapabilityClass.UNTESTED
    if type(preflight) is not PreflightResult:
        return (
            RunnerState.ISOLATION_PREFLIGHT_FAILED,
            classification,
            "preflight result is invalid",
        )
    if preflight.classification is not required_classification:
        return (
            RunnerState.ISOLATION_PREFLIGHT_FAILED,
            classification,
            "preflight classification does not authorize this execution mode",
        )
    if preflight.backend_identity_sha256 != backend_identity_sha256(descriptor.identity):
        return (
            RunnerState.ISOLATION_PREFLIGHT_FAILED,
            classification,
            "preflight backend identity changed",
        )
    try:
        stale = validate_preflight_freshness(preflight, current_freshness)
    except (TypeError, ValueError):
        stale = RunnerState.ISOLATION_PREFLIGHT_FAILED
    if stale is not None:
        return (
            RunnerState.ISOLATION_PREFLIGHT_FAILED,
            classification,
            "preflight freshness changed",
        )
    return None


def _build_isolation_receipt(
    execution_mode: str,
    descriptor: BackendDescriptor,
    preflight: PreflightResult,
    current_freshness: PreflightFreshness,
    request_sha256: str,
) -> IsolationReceipt:
    if execution_mode == "REAL_REVIEW":
        return build_per_run_isolation_receipt(
            preflight,
            current_freshness=current_freshness,
            backend_identity=descriptor.identity,
            request_sha256=request_sha256,
        )
    content = {
        "classification": CapabilityClass.UNTESTED.value,
        "preflight_evidence_sha256": preflight.evidence_sha256,
        "freshness_sha256": preflight.freshness_sha256,
        "backend_identity_sha256": backend_identity_sha256(descriptor.identity),
        "request_sha256": request_sha256,
    }
    return IsolationReceipt(
        classification=CapabilityClass.UNTESTED,
        preflight_evidence_sha256=preflight.evidence_sha256,
        freshness_sha256=preflight.freshness_sha256,
        backend_identity_sha256=content["backend_identity_sha256"],
        request_sha256=request_sha256,
        receipt_sha256=sha256_bytes(canonical_json_bytes(content)),
    )


def _freeze_diagnostic_evidence(
    filename: str,
    state: RunnerState,
    errors: list[str],
    evidence_root: Path,
    prepared: PreparedReview,
) -> Path:
    if filename not in {
        "failure.json",
        "cleanup-failure.json",
        "cleanup-evidence-failure.json",
        "source-readback-failure.json",
        "receipt-publication-failure.json",
    }:
        raise ValueError("diagnostic evidence filename is not permitted")
    return atomic_freeze_evidence(
        canonical_json_bytes(
            {"errors": list(errors), "runner_state": state.value}
        ),
        _run_evidence_directory(evidence_root, prepared) / filename,
    )


def _record_failure_evidence(
    filename: str,
    state: RunnerState,
    errors: list[str],
    evidence_root: Path,
    prepared: PreparedReview,
    *,
    preserved_paths: list[Path] | None = None,
) -> bool:
    try:
        path = _freeze_diagnostic_evidence(
            filename,
            state,
            errors,
            evidence_root,
            prepared,
        )
    except Exception as error:
        errors.append(f"{filename} evidence publication failed: {error}")
        return False
    if preserved_paths is not None:
        preserved_paths.append(path)
    return True


def _freeze_cleanup_evidence(
    cleanup: CleanupResult,
    evidence_root: Path,
    prepared: PreparedReview,
) -> Path:
    return atomic_freeze_evidence(
        canonical_json_bytes(asdict(cleanup)),
        _run_evidence_directory(evidence_root, prepared) / "cleanup.json",
    )


def _freeze_receipt(receipt, evidence_root: Path, prepared: PreparedReview) -> Path:
    return atomic_freeze_evidence(
        canonical_json_bytes(receipt_document(receipt)),
        _run_evidence_directory(evidence_root, prepared) / "runner-receipt.json",
    )


def _existing_raw_response_path(
    evidence_root: Path,
    prepared: PreparedReview,
) -> Path | None:
    path = _run_evidence_directory(evidence_root, prepared) / "raw-response.json"
    return path.resolve() if path.is_file() else None


def _run_evidence_directory(evidence_root: Path, prepared: PreparedReview) -> Path:
    return (
        evidence_root
        / "runs"
        / prepared.run_identity.review_run_id
        / prepared.run_identity.context_id
    )


def _sibling_run_paths(
    transient_parent: Path,
    prepared: PreparedReview,
) -> tuple[Path, ...]:
    runner_parent = transient_parent.resolve() / "joewrks-reviewer-runner"
    if not runner_parent.is_dir():
        return ()
    return tuple(
        sorted(
            (
                path
                for path in runner_parent.iterdir()
                if path.name not in {
                    prepared.run_identity.review_run_id,
                    ".joewrks-run-reservations",
                }
            ),
            key=lambda path: path.name,
        )
    )


def _preflight_classification(preflight: object) -> CapabilityClass:
    classification = getattr(preflight, "classification", CapabilityClass.UNAVAILABLE)
    return (
        classification
        if isinstance(classification, CapabilityClass)
        else CapabilityClass.UNAVAILABLE
    )


def _finish_early(
    state: RunnerState,
    classification: CapabilityClass,
    execution_mode: str,
    *,
    before,
    repository_root: Path,
    active_evidence_lease: EvidenceRootLease | None = None,
    prepared: object,
    errors: tuple[str, ...],
) -> RunOutcome:
    final_errors = list(errors)
    try:
        verify_source_unchanged(before, repository_root)
    except Exception as error:
        state = RunnerState.REVIEWER_EXECUTION_FAILED
        final_errors.append(f"source readback failed: {error}")
        if type(prepared) is PreparedReview and active_evidence_lease is not None:
            try:
                active_evidence_lease.verify()
            except Exception as verification_error:
                final_errors.append(
                    "source readback diagnostic suppressed because evidence-root "
                    f"lease verification failed: {verification_error}"
                )
            else:
                _record_failure_evidence(
                    "source-readback-failure.json",
                    state,
                    final_errors,
                    active_evidence_lease.root,
                    prepared,
                )
    return _outcome(
        state,
        classification,
        execution_mode,
        errors=tuple(final_errors),
    )


def _outcome(
    state: RunnerState,
    classification: CapabilityClass,
    execution_mode: str,
    *,
    receipt_path: Path | None = None,
    raw_response_path: Path | None = None,
    errors: tuple[str, ...] = (),
) -> RunOutcome:
    return RunOutcome(
        state=state,
        capability_classification=classification,
        execution_mode=execution_mode,
        receipt_path=receipt_path,
        raw_response_path=raw_response_path,
        errors=errors,
    )
