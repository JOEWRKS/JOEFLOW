"""Closed, deterministic inline requests for isolated reviewer executions."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Mapping, Sequence

from .identity import (
    RUNNER_CONTRACT_VERSION,
    InputCommitment,
    RunIdentity,
    canonical_json_bytes,
    sha256_bytes,
)


REQUEST_SCHEMA_VERSION = "joewrks.reviewer-runner-request/1.0"
_REQUIRED_ROLES = frozenset(
    {"reviewer_brief", "review_package", "run_envelope", "output_schema"}
)


class RequestError(ValueError):
    """A stable, machine-readable canonical-request validation failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class InputArtifact:
    """One permitted input represented by exact in-memory bytes."""

    logical_role: str
    media_type: str
    content: bytes


@dataclass(frozen=True, slots=True)
class CanonicalRequest:
    """The exact bytes and digest supplied for a single reviewer request."""

    content: bytes
    sha256: str


def build_permitted_inventory(
    artifacts: Sequence[InputArtifact],
) -> tuple[InputCommitment, ...]:
    """Return the exact, role-sorted commitments for four in-memory artifacts."""

    normalized = _validate_artifacts(artifacts)
    return tuple(
        InputCommitment(
            logical_role=artifact.logical_role,
            media_type=artifact.media_type,
            byte_count=len(artifact.content),
            sha256=sha256_bytes(artifact.content),
        )
        for artifact in normalized
    )


def build_canonical_request(
    run_identity: RunIdentity,
    artifacts: Sequence[InputArtifact],
    controller_only_hashes: Mapping[str, str],
) -> CanonicalRequest:
    """Build one exact-four-role request whose inputs are inline base64 bytes."""

    _validate_run_identity(run_identity)
    normalized = _validate_artifacts(artifacts)
    _validate_controller_hashes(controller_only_hashes, normalized)
    inventory = build_permitted_inventory(normalized)
    inputs = []
    for artifact, commitment in zip(normalized, inventory):
        content_base64 = base64.b64encode(artifact.content).decode("ascii")
        try:
            decoded = base64.b64decode(content_base64, validate=True)
        except (ValueError, TypeError) as error:
            raise RequestError("BASE64_INVALID", "input content cannot be base64 encoded") from error
        if decoded != artifact.content:
            raise RequestError("BASE64_ROUND_TRIP_MISMATCH", "input bytes changed during encoding")
        if commitment.byte_count != len(decoded):
            raise RequestError("INPUT_BYTE_COUNT_MISMATCH", "input byte count does not match content")
        inputs.append(
            {
                "logical_role": commitment.logical_role,
                "media_type": commitment.media_type,
                "byte_count": commitment.byte_count,
                "sha256": commitment.sha256,
                "content_base64": content_base64,
            }
        )

    document = {
        "request_schema_version": REQUEST_SCHEMA_VERSION,
        "runner_contract_version": RUNNER_CONTRACT_VERSION,
        "run_identity": {
            "semantic_review_contract_version": run_identity.semantic_review_contract_version,
            "package_schema_version": run_identity.package_schema_version,
            "reviewer_id": run_identity.reviewer_id,
            "review_run_id": run_identity.review_run_id,
            "context_id": run_identity.context_id,
        },
        "inputs": inputs,
        "response_contract": {
            "logical_response_count": 1,
            "media_type": "application/json",
        },
    }
    content = canonical_json_bytes(document)
    if content != canonical_json_bytes(document):
        raise RequestError("REQUEST_CANONICALIZATION_MISMATCH", "request bytes are not canonical")
    return CanonicalRequest(content=content, sha256=sha256_bytes(content))


def _validate_artifacts(artifacts: Sequence[InputArtifact]) -> tuple[InputArtifact, ...]:
    if isinstance(artifacts, (str, bytes)):
        raise RequestError("INPUT_ARTIFACTS_INVALID", "artifacts must be a sequence of artifacts")
    try:
        normalized = tuple(artifacts)
    except TypeError as error:
        raise RequestError("INPUT_ARTIFACTS_INVALID", "artifacts must be iterable") from error
    if len(normalized) != len(_REQUIRED_ROLES):
        raise RequestError("INPUT_ROLE_SET_INVALID", "exactly four input artifacts are required")
    observed_roles: list[str] = []
    for artifact in normalized:
        if not isinstance(artifact, InputArtifact):
            raise RequestError("INPUT_ARTIFACT_INVALID", "every input must be an InputArtifact")
        if not isinstance(artifact.logical_role, str) or artifact.logical_role not in _REQUIRED_ROLES:
            raise RequestError("INPUT_ROLE_SET_INVALID", "input role is not permitted")
        if not isinstance(artifact.media_type, str) or not artifact.media_type:
            raise RequestError("INPUT_MEDIA_TYPE_INVALID", "input media type must be a non-empty string")
        if not isinstance(artifact.content, bytes):
            raise RequestError("INPUT_CONTENT_INVALID", "input content must be exact bytes")
        observed_roles.append(artifact.logical_role)
    if set(observed_roles) != _REQUIRED_ROLES or len(set(observed_roles)) != len(_REQUIRED_ROLES):
        raise RequestError("INPUT_ROLE_SET_INVALID", "input roles must be unique and exact")
    return tuple(sorted(normalized, key=lambda artifact: artifact.logical_role))


def _validate_run_identity(run_identity: RunIdentity) -> None:
    if not isinstance(run_identity, RunIdentity):
        raise RequestError("RUN_IDENTITY_INVALID", "run_identity must be a RunIdentity")
    for name in (
        "semantic_review_contract_version",
        "package_schema_version",
        "reviewer_id",
        "review_run_id",
        "context_id",
    ):
        value = getattr(run_identity, name)
        if not isinstance(value, str) or not value:
            raise RequestError("RUN_IDENTITY_INVALID", f"run identity {name} must be a non-empty string")


def _validate_controller_hashes(
    controller_only_hashes: Mapping[str, str], artifacts: Sequence[InputArtifact]
) -> None:
    if not isinstance(controller_only_hashes, Mapping):
        raise RequestError("CONTROLLER_HASHES_INVALID", "controller hashes must be a mapping")
    hashes = set()
    for label, value in controller_only_hashes.items():
        if not isinstance(label, str) or not label or not isinstance(value, str):
            raise RequestError("CONTROLLER_HASHES_INVALID", "controller hash labels and values must be strings")
        hashes.add(value)
    if hashes.intersection(sha256_bytes(artifact.content) for artifact in artifacts):
        raise RequestError("CONTROLLER_HASH_EXPOSED", "controller-only content hash matches an input")
