"""Exact raw-response freezing, validation, binding, and replay defense."""

from __future__ import annotations

from collections.abc import Set as AbstractSet
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Callable

from .backend import BackendEvent, BackendResponse
from .evidence import EvidenceLifecycleError, atomic_freeze_evidence
from .identity import (
    BackendIdentity,
    ResponseIdentity,
    RunIdentity,
    RunnerIdentityError,
    RunnerState,
    backend_identity_sha256,
    canonical_json_bytes,
    sha256_bytes,
)


_JSON_WHITESPACE = re.compile(r"[ \t\r\n]*")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SAFE_PATH_COMPONENT = re.compile(r"[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?")
_MAX_PATH_COMPONENT_LENGTH = 128
_WINDOWS_RESERVED_PATH_STEMS = frozenset(
    {
        "aux",
        "con",
        "nul",
        "prn",
        *(f"com{number}" for number in range(1, 10)),
        *(f"lpt{number}" for number in range(1, 10)),
    }
)


@dataclass(frozen=True)
class FrozenResponse:
    path: Path
    byte_count: int
    sha256: str


@dataclass(frozen=True)
class BoundResponse:
    frozen: FrozenResponse
    parsed: dict[str, object]
    identity: ResponseIdentity


OutputValidator = Callable[[dict[str, object]], None]


class ResponseValidationError(RunnerIdentityError):
    """Response failure with the exact controller outcome classification."""

    def __init__(self, runner_state: RunnerState, message: str):
        super().__init__(runner_state.value, message)
        self.runner_state = runner_state


class _DuplicateJsonKey(ValueError):
    pass


def atomic_freeze_raw_response(
    raw_bytes: bytes,
    *,
    evidence_root: Path,
    review_run_id: str,
    context_id: str,
) -> FrozenResponse:
    """Atomically persist exact response bytes and verify the final readback."""

    if type(raw_bytes) is not bytes:
        _fail("raw response must be exact bytes")
    root = _resolved_evidence_root(evidence_root)
    _require_path_component(review_run_id, "review_run_id")
    _require_path_component(context_id, "context_id")
    target = (
        root / "runs" / review_run_id / context_id / "raw-response.json"
    ).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        _fail("raw response path escapes the evidence root")

    expected_count = len(raw_bytes)
    expected_sha256 = sha256_bytes(raw_bytes)
    try:
        atomic_freeze_evidence(raw_bytes, target)
    except EvidenceLifecycleError as error:
        _fail(f"raw response freeze failed: {error}")

    observed = target.read_bytes()
    if len(observed) != expected_count or sha256_bytes(observed) != expected_sha256:
        _fail("frozen raw response readback does not match returned bytes")
    return FrozenResponse(
        path=target,
        byte_count=expected_count,
        sha256=expected_sha256,
    )


def parse_single_json_document(frozen: FrozenResponse) -> dict[str, object]:
    """Read and strictly parse one hash-bound JSON object from frozen evidence."""

    if type(frozen) is not FrozenResponse:
        _fail("parser requires an exact FrozenResponse")
    try:
        raw_bytes = frozen.path.read_bytes()
    except OSError as error:
        _fail(f"frozen raw response cannot be read: {error}")
    if (
        len(raw_bytes) != frozen.byte_count
        or sha256_bytes(raw_bytes) != frozen.sha256
    ):
        _fail("frozen raw response readback hash or byte count changed")
    try:
        text = raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        _fail(f"raw response is not valid UTF-8: {error}")

    decoder = json.JSONDecoder(
        object_pairs_hook=_object_without_duplicate_keys,
        parse_constant=_reject_non_json_number,
    )
    start = _JSON_WHITESPACE.match(text).end()
    try:
        parsed, end = decoder.raw_decode(text, idx=start)
    except (
        json.JSONDecodeError,
        _DuplicateJsonKey,
        RecursionError,
        ValueError,
    ) as error:
        _fail(f"raw response is not one valid JSON document: {error}")
    if _JSON_WHITESPACE.fullmatch(text, pos=end) is None:
        _fail("raw response contains trailing bytes or another JSON document")
    if not isinstance(parsed, dict):
        _fail("raw response JSON document must be an object")
    return parsed


def freeze_validate_bind_response(
    response: BackendResponse,
    *,
    expected_run: RunIdentity,
    expected_backend: BackendIdentity,
    expected_request_sha256: str,
    evidence_root: Path,
    output_validator: OutputValidator,
    used_provider_request_ids: AbstractSet[str],
) -> BoundResponse:
    """Freeze first, then validate and bind one isolated backend response."""

    try:
        raw_bytes = response.raw_bytes
    except AttributeError:
        _fail("response must contain raw_bytes")
    frozen = atomic_freeze_raw_response(
        raw_bytes,
        evidence_root=evidence_root,
        review_run_id=expected_run.review_run_id,
        context_id=expected_run.context_id,
    )

    _validate_invocation_binding(
        response,
        expected_run=expected_run,
        expected_backend=expected_backend,
        expected_request_sha256=expected_request_sha256,
        used_provider_request_ids=used_provider_request_ids,
    )
    parsed = parse_single_json_document(frozen)
    if not callable(output_validator):
        _fail("output_validator must be callable")

    parsed_sha256 = _canonical_parsed_sha256(parsed)
    try:
        output_validator(parsed)
    except Exception as error:
        _fail(f"review output schema validation failed: {error}")
    if _canonical_parsed_sha256(parsed) != parsed_sha256:
        _fail("output validator must not mutate parsed response data")

    identity = ResponseIdentity(
        provider_request_id=response.provider_request_id,
        request_sha256=response.request_sha256,
        reviewer_id=response.reviewer_id,
        review_run_id=response.review_run_id,
        context_id=response.context_id,
        backend_identity_sha256=response.backend_identity_sha256,
        response_count=response.response_count,
        raw_response_byte_count=frozen.byte_count,
        raw_response_sha256=frozen.sha256,
        parsed_output_sha256=parsed_sha256,
    )
    return BoundResponse(frozen=frozen, parsed=parsed, identity=identity)


def _validate_invocation_binding(
    response: BackendResponse,
    *,
    expected_run: RunIdentity,
    expected_backend: BackendIdentity,
    expected_request_sha256: str,
    used_provider_request_ids: AbstractSet[str],
) -> None:
    if type(response) is not BackendResponse:
        _binding_fail("response must be an exact BackendResponse")
    if type(expected_run) is not RunIdentity:
        _binding_fail("expected_run must be an exact RunIdentity")
    if type(expected_backend) is not BackendIdentity:
        _binding_fail("expected_backend must be an exact BackendIdentity")
    if not isinstance(expected_request_sha256, str) or _SHA256.fullmatch(
        expected_request_sha256
    ) is None:
        _binding_fail("expected_request_sha256 must be a lowercase SHA-256 digest")
    if response.request_sha256 != expected_request_sha256:
        _binding_fail("response request hash does not bind the canonical request")
    for actual, expected, label in (
        (response.reviewer_id, expected_run.reviewer_id, "reviewer_id"),
        (response.review_run_id, expected_run.review_run_id, "review_run_id"),
        (response.context_id, expected_run.context_id, "context_id"),
    ):
        if actual != expected:
            _binding_fail(f"response {label} does not bind the invocation")
    try:
        expected_backend_sha256 = backend_identity_sha256(expected_backend)
    except (RunnerIdentityError, TypeError, ValueError) as error:
        _binding_fail(f"expected backend identity is invalid: {error}")
    if response.backend_identity_sha256 != expected_backend_sha256:
        _binding_fail(
            "response backend hash does not bind model, deployment, and settings"
        )
    if (
        isinstance(response.response_count, bool)
        or type(response.response_count) is not int
        or response.response_count != 1
    ):
        _binding_fail("response_count must be exactly one")
    if response.continuation_id is not None or response.previous_response_id is not None:
        _binding_fail("continuation and previous-response identifiers are forbidden")
    _validate_response_events(response.events)
    if (
        not isinstance(response.provider_request_id, str)
        or not response.provider_request_id
        or response.provider_request_id != response.provider_request_id.strip()
    ):
        _binding_fail("provider_request_id must be a non-empty identifier")
    if not isinstance(used_provider_request_ids, AbstractSet) or isinstance(
        used_provider_request_ids, (str, bytes)
    ):
        _binding_fail("used_provider_request_ids must be a set-like frozen receipt index")
    if response.provider_request_id in used_provider_request_ids:
        _binding_fail("provider_request_id has already been used by a frozen receipt")


def _validate_response_events(events: object) -> None:
    if not isinstance(events, tuple) or len(events) != 1:
        _binding_fail("response must contain exactly one RESPONSE event")
    event = events[0]
    if type(event) is not BackendEvent:
        _binding_fail("response event must be an exact BackendEvent")
    if event.kind != "RESPONSE":
        _binding_fail("response contains a forbidden or extra event kind")
    if not isinstance(event.metadata_sha256, str) or _SHA256.fullmatch(
        event.metadata_sha256
    ) is None:
        _binding_fail("response event metadata must be hash-bound")


def _resolved_evidence_root(evidence_root: Path) -> Path:
    if not isinstance(evidence_root, Path):
        _fail("evidence_root must be a Path")
    return evidence_root.resolve()


def _require_path_component(value: object, label: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) > _MAX_PATH_COMPONENT_LENGTH
        or _SAFE_PATH_COMPONENT.fullmatch(value) is None
        or value.split(".", 1)[0] in _WINDOWS_RESERVED_PATH_STEMS
    ):
        _fail(f"{label} is not a safe evidence-path component")


def _object_without_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey(f"duplicate object key: {key}")
        result[key] = value
    return result


def _reject_non_json_number(value: str) -> object:
    raise ValueError(f"non-JSON numeric constant: {value}")


def _canonical_parsed_sha256(parsed: dict[str, object]) -> str:
    try:
        return sha256_bytes(canonical_json_bytes(parsed))
    except (RecursionError, TypeError, ValueError, UnicodeError) as error:
        _fail(f"parsed response cannot be canonically hashed: {error}")


def _fail(message: str):
    raise ResponseValidationError(RunnerState.REVIEW_OUTPUT_INVALID, message)


def _binding_fail(message: str):
    raise ResponseValidationError(RunnerState.PACKAGE_BINDING_MISMATCH, message)
