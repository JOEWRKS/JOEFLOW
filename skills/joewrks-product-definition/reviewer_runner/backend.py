"""Closed bytes-in/bytes-out boundary for isolated inference backends.

This module declares only the controller-facing protocol.  It intentionally
contains no provider implementation, registry, filesystem access, tools, or
retrieval capability.
"""

from dataclasses import dataclass
from typing import Protocol

from .identity import (
    BackendIdentity,
    CapabilityClass,
    backend_identity_sha256,
    canonical_json_bytes,
    sha256_bytes,
)


REQUIRED_CAPABILITIES = (
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

_INVOCATION_ERROR_CODES = frozenset(
    {"TRANSPORT_ERROR", "TIMEOUT", "CANCELLED", "NO_RESPONSE"}
)
_ELIGIBLE_MODEL_STABILITIES = frozenset({"IMMUTABLE", "STABLE_DEPLOYMENT"})


@dataclass(frozen=True)
class CapabilityObservation:
    capability: str
    classification: CapabilityClass
    method: str
    evidence_sha256: str


@dataclass(frozen=True)
class BackendDescriptor:
    identity: BackendIdentity
    max_request_bytes: int
    observations: tuple[CapabilityObservation, ...]


@dataclass(frozen=True)
class BackendEvent:
    kind: str
    metadata_sha256: str


@dataclass(frozen=True)
class BackendResponse:
    raw_bytes: bytes
    provider_request_id: str
    request_sha256: str
    reviewer_id: str
    review_run_id: str
    context_id: str
    backend_identity_sha256: str
    response_count: int
    continuation_id: None
    previous_response_id: None
    events: tuple[BackendEvent, ...]


class ToollessInferenceBackend(Protocol):
    def describe(self) -> BackendDescriptor:
        ...

    def invoke(
        self,
        request_bytes: bytes,
        *,
        timeout_seconds: int,
    ) -> BackendResponse:
        ...


class BackendInvocationError(RuntimeError):
    """One of the closed transport outcomes permitted by this boundary."""

    def __init__(self, code: str, message: str):
        if code not in _INVOCATION_ERROR_CODES:
            raise ValueError("backend invocation code is not permitted")
        super().__init__(message)
        self.code = code


def hash_evidence_record(evidence_record: object) -> str:
    """Return the canonical digest used to bind capability and event evidence."""

    return sha256_bytes(canonical_json_bytes(evidence_record))


def validate_backend_descriptor(descriptor: BackendDescriptor) -> None:
    """Validate the immutable, exact capability metadata for one backend."""

    if type(descriptor) is not BackendDescriptor:
        raise ValueError("backend descriptor must be an exact BackendDescriptor")
    if type(descriptor.identity) is not BackendIdentity:
        raise ValueError("backend descriptor must contain an exact BackendIdentity")
    if (
        isinstance(descriptor.max_request_bytes, bool)
        or not isinstance(descriptor.max_request_bytes, int)
        or descriptor.max_request_bytes <= 0
    ):
        raise ValueError("max_request_bytes must be a positive integer")
    if not isinstance(descriptor.observations, tuple):
        raise ValueError("observations must be an immutable tuple")
    if tuple(observation.capability for observation in descriptor.observations) != REQUIRED_CAPABILITIES:
        raise ValueError("observations must contain the required capabilities in order")
    for observation in descriptor.observations:
        if type(observation) is not CapabilityObservation:
            raise ValueError("observations must be exact CapabilityObservation values")
        if not isinstance(observation.classification, CapabilityClass):
            raise ValueError("observation classification must be a CapabilityClass")
        if not isinstance(observation.method, str) or not observation.method.strip():
            raise ValueError("observation method must be non-empty")
        if not _is_sha256(observation.evidence_sha256):
            raise ValueError("observation evidence_sha256 must be a SHA-256 digest")


def is_backend_eligible(descriptor: BackendDescriptor) -> bool:
    """Return whether a real backend has all required observed capabilities."""

    validate_backend_descriptor(descriptor)
    return (
        not descriptor.identity.is_test_double
        and descriptor.identity.model_identity_stability in _ELIGIBLE_MODEL_STABILITIES
        and all(
            observation.classification is CapabilityClass.OBSERVED_PASS
            for observation in descriptor.observations
        )
    )


def validate_backend_response(
    response: BackendResponse,
    *,
    request_bytes: bytes,
    reviewer_id: str,
    review_run_id: str,
    context_id: str,
    descriptor: BackendDescriptor,
) -> None:
    """Validate a single stateless response against controller-known bindings."""

    validate_backend_descriptor(descriptor)
    if type(response) is not BackendResponse:
        raise ValueError("response must be an exact BackendResponse")
    if not isinstance(request_bytes, bytes):
        raise ValueError("request_bytes must be exact bytes")
    if not isinstance(response.raw_bytes, bytes):
        raise ValueError("raw_bytes must be exact bytes")
    if not _is_identifier(response.provider_request_id):
        raise ValueError("provider_request_id must be non-empty")
    if response.request_sha256 != sha256_bytes(request_bytes):
        raise ValueError("response request_sha256 does not bind the supplied request")
    for actual, expected, name in (
        (response.reviewer_id, reviewer_id, "reviewer_id"),
        (response.review_run_id, review_run_id, "review_run_id"),
        (response.context_id, context_id, "context_id"),
    ):
        if not _is_identifier(actual) or actual != expected:
            raise ValueError(f"response {name} does not bind controller context")
    if response.backend_identity_sha256 != backend_identity_sha256(descriptor.identity):
        raise ValueError("response backend identity does not bind descriptor identity")
    if (
        isinstance(response.response_count, bool)
        or not isinstance(response.response_count, int)
        or response.response_count != 1
    ):
        raise ValueError("response_count must be exactly one")
    if response.continuation_id is not None or response.previous_response_id is not None:
        raise ValueError("continuation identifiers are not permitted")
    if not isinstance(response.events, tuple):
        raise ValueError("events must be an immutable tuple")
    for event in response.events:
        if type(event) is not BackendEvent:
            raise ValueError("events must be exact BackendEvent values")
        if not _is_identifier(event.kind) or not _is_sha256(event.metadata_sha256):
            raise ValueError("event metadata must be hash-bound")


def _is_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
