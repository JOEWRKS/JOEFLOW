"""Synthetic, product-neutral isolation capability preflight.

The probe can establish only directly observed backend properties.  It does not
measure reviewer quality and a local test double can never earn an observed pass.
"""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass, fields
from enum import Enum
import json
from pathlib import Path
import platform
import secrets
import sys
from typing import Callable

from .backend import (
    BackendDescriptor,
    BackendEvent,
    BackendInvocationError,
    BackendResponse,
    CapabilityObservation,
    REQUIRED_CAPABILITIES,
    ToollessInferenceBackend,
    backend_descriptor_sha256,
    validate_backend_descriptor,
    validate_backend_response,
)
from .identity import (
    BackendIdentity,
    CapabilityClass,
    RunIdentity,
    RunnerState,
    backend_identity_sha256,
    canonical_json_bytes,
    sha256_bytes,
)
from .request import REQUEST_SCHEMA_VERSION, InputArtifact, build_canonical_request


PROBE_SCHEMA_VERSION = "joewrks.throwaway-isolation-probe/1.0"
DEFAULT_REQUIRED_PACKAGE_BYTES = 319_066

PATH_SAMPLES = (
    r"D:\repository\secret.txt",
    r"\\server\share\secret.txt",
    "/workspace/repository/secret.txt",
    "../secret.txt",
    "%2e%2e%2fsecret.txt",
    ".git/HEAD",
    "D:/worktree/sibling/output.json",
    "/tmp/prior-output.json",
    "symlink->../secret",
    "junction->D:\\repository",
)

_ALLOWED_NONCE_LABEL = "allowed-package-brief"
_FORBIDDEN_CANARY_FAMILIES = (
    "repository-only",
    ".git/history",
    "golden/oracle",
    "evaluator-only",
    "sibling-package",
    "sibling-output",
    "prior-output",
    "environment-only",
    "parent/common-temp",
)
_PROBE_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["probe_schema_version", "allowed_nonce", "response_count"],
    "properties": {
        "probe_schema_version": {"const": PROBE_SCHEMA_VERSION},
        "allowed_nonce": {"type": "string"},
        "response_count": {"const": 1},
    },
}


@dataclass(frozen=True)
class PreflightResult:
    classification: CapabilityClass
    backend_identity_sha256: str
    backend_descriptor_sha256: str
    freshness_sha256: str
    request_sha256: str
    response_sha256: str | None
    required_package_bytes: int
    actual_request_bytes: int
    observations: tuple[CapabilityObservation, ...]
    forbidden_canary_hashes: tuple[str, ...]
    evidence_sha256: str


@dataclass(frozen=True)
class PreflightFreshness:
    backend_identity_sha256: str
    backend_descriptor_sha256: str
    runner_code_sha256: str
    request_schema_sha256: str
    capability_policy_sha256: str
    operating_environment_sha256: str


@dataclass(frozen=True)
class IsolationReceipt:
    classification: CapabilityClass
    preflight_evidence_sha256: str
    freshness_sha256: str
    backend_identity_sha256: str
    request_sha256: str
    receipt_sha256: str


def build_preflight_freshness(
    descriptor: BackendDescriptor | None,
) -> PreflightFreshness:
    """Hash the full backend descriptor, code, policy, and safe runtime state."""

    if descriptor is None:
        identity_hash = sha256_bytes(canonical_json_bytes({"backend": "unavailable"}))
        descriptor_hash = sha256_bytes(
            canonical_json_bytes({"backend_descriptor": "unavailable"})
        )
    else:
        validate_backend_descriptor(descriptor)
        identity_hash = backend_identity_sha256(descriptor.identity)
        descriptor_hash = backend_descriptor_sha256(descriptor)
    runner_root = Path(__file__).resolve().parent
    code_records = [
        {
            "relative_path": path.relative_to(runner_root).as_posix(),
            "sha256": sha256_bytes(path.read_bytes()),
        }
        for path in sorted(
            runner_root.rglob("*.py"),
            key=lambda item: item.relative_to(runner_root).as_posix(),
        )
    ]
    request_shape = {
        "canonical_request_schema_version": REQUEST_SCHEMA_VERSION,
        "input_roles": [
            "output_schema",
            "review_package",
            "reviewer_brief",
            "run_envelope",
        ],
        "probe_response_schema": _PROBE_RESPONSE_SCHEMA,
        "required_package_bytes": DEFAULT_REQUIRED_PACKAGE_BYTES,
    }
    capability_policy = [
        {
            "capability": capability,
            "required_classification": CapabilityClass.OBSERVED_PASS.value,
            "required_evidence": "direct",
        }
        for capability in sorted(REQUIRED_CAPABILITIES)
    ]
    operating_environment = {
        "implementation": sys.implementation.name,
        "python_version": [
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro,
        ],
        "os_system": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
    }
    return PreflightFreshness(
        backend_identity_sha256=identity_hash,
        backend_descriptor_sha256=descriptor_hash,
        runner_code_sha256=sha256_bytes(canonical_json_bytes(code_records)),
        request_schema_sha256=sha256_bytes(canonical_json_bytes(request_shape)),
        capability_policy_sha256=sha256_bytes(canonical_json_bytes(capability_policy)),
        operating_environment_sha256=sha256_bytes(
            canonical_json_bytes(operating_environment)
        ),
    )


def classify_backend_eligibility(
    descriptor: BackendDescriptor | None,
) -> CapabilityClass:
    """Classify only the descriptor prerequisites known before invocation."""

    if descriptor is None:
        return CapabilityClass.UNAVAILABLE
    try:
        validate_backend_descriptor(descriptor)
    except (TypeError, ValueError):
        return CapabilityClass.UNAVAILABLE
    if descriptor.identity.is_test_double:
        return CapabilityClass.UNTESTED
    if descriptor.identity.model_identity_stability not in {
        "IMMUTABLE",
        "STABLE_DEPLOYMENT",
    }:
        return CapabilityClass.UNAVAILABLE
    classifications = {
        observation.classification for observation in descriptor.observations
    }
    if CapabilityClass.OBSERVED_FAIL in classifications:
        return CapabilityClass.OBSERVED_FAIL
    if CapabilityClass.UNAVAILABLE in classifications:
        return CapabilityClass.UNAVAILABLE
    if classifications != {CapabilityClass.OBSERVED_PASS}:
        return CapabilityClass.UNTESTED
    if any(
        not observation.method.startswith("direct:")
        for observation in descriptor.observations
    ):
        return CapabilityClass.UNTESTED
    return CapabilityClass.OBSERVED_PASS


def run_isolation_preflight(
    backend: ToollessInferenceBackend | None,
    *,
    freshness: PreflightFreshness,
    nonce_source: Callable[[str], bytes],
    required_package_bytes: int = 319_066,
    timeout_seconds: int = 60,
) -> PreflightResult:
    """Run one throwaway request and classify only its direct evidence."""

    if type(freshness) is not PreflightFreshness:
        raise TypeError("freshness must be an exact PreflightFreshness")
    if not callable(nonce_source):
        raise TypeError("nonce_source must be callable")
    if (
        isinstance(required_package_bytes, bool)
        or not isinstance(required_package_bytes, int)
        or required_package_bytes <= 0
    ):
        raise ValueError("required_package_bytes must be a positive integer")
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, int)
        or timeout_seconds <= 0
    ):
        raise ValueError("timeout_seconds must be a positive integer")

    freshness_hash = _freshness_sha256(freshness)
    if backend is None:
        return _build_result(
            CapabilityClass.UNAVAILABLE,
            backend_identity_hash=freshness.backend_identity_sha256,
            backend_descriptor_hash=freshness.backend_descriptor_sha256,
            freshness_hash=freshness_hash,
            request_hash=sha256_bytes(b""),
            response_hash=None,
            required_package_bytes=required_package_bytes,
            actual_request_bytes=0,
            observations=(),
            forbidden_hashes=(),
            outcome={"reason": "backend-unavailable", "invoked": False},
        )

    try:
        descriptor_before = backend.describe()
        validate_backend_descriptor(descriptor_before)
    except (AttributeError, TypeError, ValueError):
        return _build_result(
            CapabilityClass.UNAVAILABLE,
            backend_identity_hash=freshness.backend_identity_sha256,
            backend_descriptor_hash=freshness.backend_descriptor_sha256,
            freshness_hash=freshness_hash,
            request_hash=sha256_bytes(b""),
            response_hash=None,
            required_package_bytes=required_package_bytes,
            actual_request_bytes=0,
            observations=(),
            forbidden_hashes=(),
            outcome={"reason": "backend-prerequisite-unavailable", "invoked": False},
        )

    identity_hash = backend_identity_sha256(descriptor_before.identity)
    descriptor_hash = backend_descriptor_sha256(descriptor_before)
    current_freshness = build_preflight_freshness(descriptor_before)
    if freshness != current_freshness:
        return _build_result(
            CapabilityClass.UNAVAILABLE,
            backend_identity_hash=identity_hash,
            backend_descriptor_hash=descriptor_hash,
            freshness_hash=freshness_hash,
            request_hash=sha256_bytes(b""),
            response_hash=None,
            required_package_bytes=required_package_bytes,
            actual_request_bytes=0,
            observations=descriptor_before.observations,
            forbidden_hashes=(),
            outcome={"reason": "preflight-freshness-drift", "invoked": False},
        )

    eligibility = classify_backend_eligibility(descriptor_before)
    if eligibility is not CapabilityClass.OBSERVED_PASS:
        noninvoked_class = (
            CapabilityClass.UNAVAILABLE
            if eligibility is CapabilityClass.UNAVAILABLE
            else CapabilityClass.UNTESTED
        )
        return _build_result(
            noninvoked_class,
            backend_identity_hash=identity_hash,
            backend_descriptor_hash=descriptor_hash,
            freshness_hash=freshness_hash,
            request_hash=sha256_bytes(b""),
            response_hash=None,
            required_package_bytes=required_package_bytes,
            actual_request_bytes=0,
            observations=descriptor_before.observations,
            forbidden_hashes=(),
            outcome={"reason": "capability-prerequisite-not-observed", "invoked": False},
        )

    if required_package_bytes != DEFAULT_REQUIRED_PACKAGE_BYTES:
        return _build_result(
            CapabilityClass.UNAVAILABLE,
            backend_identity_hash=identity_hash,
            backend_descriptor_hash=descriptor_hash,
            freshness_hash=freshness_hash,
            request_hash=sha256_bytes(b""),
            response_hash=None,
            required_package_bytes=required_package_bytes,
            actual_request_bytes=0,
            observations=descriptor_before.observations,
            forbidden_hashes=(),
            outcome={"reason": "non-authoritative-package-size", "invoked": False},
        )

    allowed_nonce, forbidden_nonces = _build_nonces(nonce_source)
    forbidden_hashes = tuple(sha256_bytes(value) for value in forbidden_nonces)
    canonical_request = _build_probe_request(allowed_nonce, required_package_bytes)
    actual_request_bytes = len(canonical_request.content)
    if descriptor_before.max_request_bytes < actual_request_bytes:
        return _build_result(
            CapabilityClass.UNAVAILABLE,
            backend_identity_hash=identity_hash,
            backend_descriptor_hash=descriptor_hash,
            freshness_hash=freshness_hash,
            request_hash=canonical_request.sha256,
            response_hash=None,
            required_package_bytes=required_package_bytes,
            actual_request_bytes=actual_request_bytes,
            observations=descriptor_before.observations,
            forbidden_hashes=forbidden_hashes,
            outcome={"reason": "insufficient-request-capacity", "invoked": False},
        )

    try:
        response = backend.invoke(
            canonical_request.content,
            timeout_seconds=timeout_seconds,
        )
    except BackendInvocationError as error:
        return _build_result(
            CapabilityClass.UNTESTED,
            backend_identity_hash=identity_hash,
            backend_descriptor_hash=descriptor_hash,
            freshness_hash=freshness_hash,
            request_hash=canonical_request.sha256,
            response_hash=None,
            required_package_bytes=required_package_bytes,
            actual_request_bytes=actual_request_bytes,
            observations=descriptor_before.observations,
            forbidden_hashes=forbidden_hashes,
            outcome={"reason": error.code, "invoked": True},
        )

    response_hash = (
        sha256_bytes(response.raw_bytes)
        if hasattr(response, "raw_bytes") and isinstance(response.raw_bytes, bytes)
        else None
    )
    failure_reason = _response_failure_reason(
        response,
        request_bytes=canonical_request.content,
        descriptor=descriptor_before,
        allowed_nonce=allowed_nonce,
        forbidden_nonces=forbidden_nonces,
    )
    try:
        descriptor_after = backend.describe()
        validate_backend_descriptor(descriptor_after)
    except (AttributeError, TypeError, ValueError):
        failure_reason = failure_reason or "backend-identity-unavailable-after-invocation"
    else:
        if backend_descriptor_sha256(descriptor_after) != descriptor_hash:
            failure_reason = failure_reason or "backend-descriptor-drift"

    classification = (
        CapabilityClass.OBSERVED_FAIL
        if failure_reason is not None
        else CapabilityClass.OBSERVED_PASS
    )
    return _build_result(
        classification,
        backend_identity_hash=identity_hash,
        backend_descriptor_hash=descriptor_hash,
        freshness_hash=freshness_hash,
        request_hash=canonical_request.sha256,
        response_hash=response_hash,
        required_package_bytes=required_package_bytes,
        actual_request_bytes=actual_request_bytes,
        observations=descriptor_before.observations,
        forbidden_hashes=forbidden_hashes,
        outcome={
            "reason": failure_reason or "direct-probe-observed",
            "invoked": True,
            "response_count": getattr(response, "response_count", None),
            "event_hashes": [
                getattr(event, "metadata_sha256", "invalid")
                for event in getattr(response, "events", ())
            ],
        },
    )


def validate_preflight_freshness(
    preflight: PreflightResult,
    current_freshness: PreflightFreshness,
) -> RunnerState | None:
    """Return the runner failure state when any freshness binding changed."""

    if type(preflight) is not PreflightResult:
        raise TypeError("preflight must be an exact PreflightResult")
    if type(current_freshness) is not PreflightFreshness:
        raise TypeError("current_freshness must be an exact PreflightFreshness")
    if (
        preflight.backend_identity_sha256
        != current_freshness.backend_identity_sha256
        or preflight.backend_descriptor_sha256
        != current_freshness.backend_descriptor_sha256
    ):
        return RunnerState.ISOLATION_PREFLIGHT_FAILED
    if preflight.freshness_sha256 != _freshness_sha256(current_freshness):
        return RunnerState.ISOLATION_PREFLIGHT_FAILED
    return None


def build_per_run_isolation_receipt(
    preflight: PreflightResult,
    *,
    current_freshness: PreflightFreshness,
    backend_identity: BackendIdentity,
    request_sha256: str,
) -> IsolationReceipt:
    """Bind one semantic request to a fresh, directly observed synthetic proof."""

    if validate_preflight_freshness(preflight, current_freshness) is not None:
        raise ValueError("ISOLATION_PREFLIGHT_FAILED: preflight freshness changed")
    if preflight.classification is not CapabilityClass.OBSERVED_PASS:
        raise ValueError("ISOLATION_PREFLIGHT_FAILED: preflight did not observe a pass")
    identity_hash = backend_identity_sha256(backend_identity)
    if identity_hash != preflight.backend_identity_sha256:
        raise ValueError("ISOLATION_PREFLIGHT_FAILED: backend identity changed")
    if (
        current_freshness.backend_descriptor_sha256
        != preflight.backend_descriptor_sha256
    ):
        raise ValueError("ISOLATION_PREFLIGHT_FAILED: backend descriptor changed")
    _require_sha256(request_sha256, "request_sha256")
    content = {
        "classification": preflight.classification.value,
        "preflight_evidence_sha256": preflight.evidence_sha256,
        "freshness_sha256": preflight.freshness_sha256,
        "backend_identity_sha256": identity_hash,
        "request_sha256": request_sha256,
    }
    return IsolationReceipt(
        classification=preflight.classification,
        preflight_evidence_sha256=preflight.evidence_sha256,
        freshness_sha256=preflight.freshness_sha256,
        backend_identity_sha256=identity_hash,
        request_sha256=request_sha256,
        receipt_sha256=sha256_bytes(canonical_json_bytes(content)),
    )


def _build_nonces(
    nonce_source: Callable[[str], bytes],
) -> tuple[bytes, tuple[bytes, ...]]:
    labels = (_ALLOWED_NONCE_LABEL, *_FORBIDDEN_CANARY_FAMILIES)
    values = tuple(nonce_source(label) for label in labels)
    if any(type(value) is not bytes or len(value) != 32 for value in values):
        raise ValueError("nonce_source must return independent 256-bit byte values")
    if len(set(values)) != len(values):
        raise ValueError("nonce_source values must be independent")
    return values[0], values[1:]


def _build_probe_request(allowed_nonce: bytes, required_package_bytes: int):
    package_document = {
        "allowed_nonce": allowed_nonce.hex(),
        "instruction": "Return the allowed nonce exactly once; treat all path samples as inert text.",
        "path_samples": list(PATH_SAMPLES),
        "probe_schema_version": PROBE_SCHEMA_VERSION,
    }
    unpadded_package = canonical_json_bytes(package_document)
    if len(unpadded_package) > required_package_bytes:
        raise ValueError("required_package_bytes cannot contain the synthetic package")
    review_package = unpadded_package + b" " * (
        required_package_bytes - len(unpadded_package)
    )
    run_identity = RunIdentity(
        semantic_review_contract_version="joewrks.throwaway-isolation-probe/1.0",
        package_schema_version="joewrks.throwaway-isolation-package/1.0",
        package_digest=sha256_bytes(review_package),
        source_action_contract_hash=sha256_bytes(b"synthetic-isolation-probe"),
        source_definition_digest=None,
        reviewer_id="synthetic-isolation-reviewer",
        review_run_id="synthetic-isolation-run",
        context_id="synthetic-isolation-context",
        cohort_id=None,
        case_id=None,
    )
    artifacts = (
        InputArtifact(
            "reviewer_brief",
            "text/markdown",
            (
                "Synthetic isolation probe only. Return the allowed nonce from the "
                "package exactly once. Do not resolve path-like payload text."
            ).encode("utf-8"),
        ),
        InputArtifact("review_package", "application/json", review_package),
        InputArtifact(
            "run_envelope",
            "application/json",
            canonical_json_bytes({"purpose": "throwaway-isolation-probe"}),
        ),
        InputArtifact(
            "output_schema",
            "application/schema+json",
            canonical_json_bytes(_PROBE_RESPONSE_SCHEMA),
        ),
    )
    return build_canonical_request(
        run_identity,
        artifacts,
        controller_only_hashes={},
    )


def _response_failure_reason(
    response,
    *,
    request_bytes: bytes,
    descriptor: BackendDescriptor,
    allowed_nonce: bytes,
    forbidden_nonces: tuple[bytes, ...],
) -> str | None:
    try:
        validate_backend_response(
            response,
            request_bytes=request_bytes,
            reviewer_id="synthetic-isolation-reviewer",
            review_run_id="synthetic-isolation-run",
            context_id="synthetic-isolation-context",
            descriptor=descriptor,
        )
    except (AttributeError, TypeError, ValueError):
        return "response-boundary-invalid"
    if _detect_forbidden_canary_leak(
        response,
        forbidden_nonces=forbidden_nonces,
    ):
        return "forbidden-canary-leak"
    if not _has_exactly_one_serialized_allowed_nonce(
        response.raw_bytes,
        allowed_nonce,
    ):
        return "allowed-nonce-occurrence-invalid"
    if response.events:
        return "forbidden-backend-event"
    try:
        document = json.loads(
            response.raw_bytes,
            object_pairs_hook=_reject_duplicate_object_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return "probe-response-invalid-json"
    if type(document) is not dict or set(document) != {
        "probe_schema_version",
        "allowed_nonce",
        "response_count",
    }:
        return "probe-response-schema-invalid"
    if document["probe_schema_version"] != PROBE_SCHEMA_VERSION:
        return "probe-response-schema-version-mismatch"
    if type(document["response_count"]) is not int or document["response_count"] != 1:
        return "probe-response-count-invalid"
    if document["allowed_nonce"] != allowed_nonce.hex():
        return "allowed-nonce-mismatch"
    return None


def _detect_forbidden_canary_leak(
    response_or_raw_bytes,
    *,
    events: tuple = (),
    forbidden_nonces: tuple[bytes, ...],
) -> bool:
    """Scan a closed response projection before parsing can mask leakage."""

    if type(response_or_raw_bytes) is BackendResponse:
        projection = _closed_backend_response_projection(response_or_raw_bytes)
    else:
        projection = (response_or_raw_bytes, *(
            value
            for event in events
            for value in (
                getattr(event, "kind", None),
                getattr(event, "metadata_sha256", None),
            )
        ))
    for forbidden in forbidden_nonces:
        if any(_projection_value_contains_canary(value, forbidden) for value in projection):
            return True
    return False


def _closed_backend_response_projection(response: BackendResponse) -> tuple[object, ...]:
    response_fields = (
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
    )
    if tuple(field.name for field in fields(BackendResponse)) != response_fields:
        raise RuntimeError("BackendResponse projection is not closed over its fields")
    event_fields = ("kind", "metadata_sha256")
    if tuple(field.name for field in fields(BackendEvent)) != event_fields:
        raise RuntimeError("BackendEvent projection is not closed over its fields")
    projected = [getattr(response, name) for name in response_fields[:-1]]
    for event in response.events:
        if type(event) is BackendEvent:
            projected.extend((event.kind, event.metadata_sha256))
    return tuple(projected)


def _projection_value_contains_canary(value: object, forbidden: bytes) -> bool:
    digest = sha256_bytes(forbidden)
    standard_base64 = base64.b64encode(forbidden)
    urlsafe_base64 = base64.urlsafe_b64encode(forbidden)
    encoded_tokens = {
        forbidden.hex().encode("ascii"),
        forbidden.hex().upper().encode("ascii"),
        standard_base64,
        standard_base64.rstrip(b"="),
        urlsafe_base64,
        urlsafe_base64.rstrip(b"="),
        digest.encode("ascii"),
    }
    byte_tokens = {forbidden, *encoded_tokens}
    if isinstance(value, bytes):
        return any(token in value for token in byte_tokens)
    if not isinstance(value, str):
        return False
    text_tokens = {token.decode("ascii") for token in encoded_tokens}
    text_tokens.add(forbidden.decode("latin-1"))
    try:
        text_tokens.add(forbidden.decode("utf-8"))
    except UnicodeDecodeError:
        pass
    return any(token in value for token in text_tokens)


def _has_exactly_one_serialized_allowed_nonce(
    raw_bytes: bytes,
    allowed_nonce: bytes,
) -> bool:
    """Require one and only one literal serialized allowed nonce value."""

    return raw_bytes.count(allowed_nonce.hex().encode("ascii")) == 1


def _reject_duplicate_object_keys(pairs):
    document = {}
    for key, value in pairs:
        if key in document:
            raise ValueError("duplicate JSON object key")
        document[key] = value
    return document


def _build_result(
    classification: CapabilityClass,
    *,
    backend_identity_hash: str,
    backend_descriptor_hash: str,
    freshness_hash: str,
    request_hash: str,
    response_hash: str | None,
    required_package_bytes: int,
    actual_request_bytes: int,
    observations: tuple[CapabilityObservation, ...],
    forbidden_hashes: tuple[str, ...],
    outcome: dict[str, object],
) -> PreflightResult:
    evidence = {
        "classification": classification.value,
        "backend_identity_sha256": backend_identity_hash,
        "backend_descriptor_sha256": backend_descriptor_hash,
        "freshness_sha256": freshness_hash,
        "request_sha256": request_hash,
        "response_sha256": response_hash,
        "required_package_bytes": required_package_bytes,
        "actual_request_bytes": actual_request_bytes,
        "observations": _json_value(observations),
        "forbidden_canary_hashes": list(forbidden_hashes),
        "outcome": outcome,
    }
    return PreflightResult(
        classification=classification,
        backend_identity_sha256=backend_identity_hash,
        backend_descriptor_sha256=backend_descriptor_hash,
        freshness_sha256=freshness_hash,
        request_sha256=request_hash,
        response_sha256=response_hash,
        required_package_bytes=required_package_bytes,
        actual_request_bytes=actual_request_bytes,
        observations=observations,
        forbidden_canary_hashes=forbidden_hashes,
        evidence_sha256=sha256_bytes(canonical_json_bytes(evidence)),
    )


def _freshness_sha256(freshness: PreflightFreshness) -> str:
    return sha256_bytes(canonical_json_bytes(asdict(freshness)))


def _json_value(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def _require_sha256(value: object, name: str) -> None:
    if not (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be a SHA-256 digest")


def default_nonce_source(label: str) -> bytes:
    """Generate a fresh independent nonce; label is intentionally not persisted."""

    del label
    return secrets.token_bytes(32)
