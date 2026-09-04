"""Explicit adapters for the frozen semantic-review/1.0 and /2.1 contracts."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import json

from downstream.semantic_review.output import validate_review_output
from downstream.semantic_review.package import verify_run_envelope
from downstream_v21.semantic_review.output import validate_semantic_review_output_v21
from downstream_v21.semantic_review.package import validate_semantic_review_package_v21

from .identity import RunIdentity, canonical_json_bytes, sha256_bytes
from .request import InputArtifact
from .response import OutputValidator


_V1_CONTRACT = "joewrks.semantic-review/1.0"
_V1_PACKAGE_SCHEMA = "joewrks.semantic-review-input/1.0"
_V21_CONTRACT = "joewrks.semantic-review/2.1"


@dataclass(frozen=True)
class PreparedReview:
    run_identity: RunIdentity
    artifacts: tuple[InputArtifact, ...]
    controller_only_hashes: tuple[tuple[str, str], ...]
    output_validator: OutputValidator


def prepare_semantic_review_v1(
    *,
    verified_package: dict[str, object],
    package_archive_bytes: bytes,
    reviewer_brief_bytes: bytes,
    run_envelope: dict[str, object],
    output_schema_bytes: bytes,
    run_identity: RunIdentity,
) -> PreparedReview:
    """Bind exact v1 inputs to the existing envelope and output validators."""

    _require_run_identity(run_identity, _V1_CONTRACT)
    if run_identity.package_schema_version != _V1_PACKAGE_SCHEMA:
        raise ValueError(
            "v1 package schema version does not match the authoritative schema"
        )
    if run_identity.source_definition_digest is not None:
        raise ValueError("v1 source definition digest must be absent")
    if not isinstance(verified_package, dict) or not isinstance(run_envelope, dict):
        raise ValueError("v1 package and run envelope must be objects")
    _require_bytes(package_archive_bytes, "package_archive_bytes")
    _require_bytes(reviewer_brief_bytes, "reviewer_brief_bytes")
    _require_bytes(output_schema_bytes, "output_schema_bytes")

    package_copy = copy.deepcopy(verified_package)
    envelope_copy = copy.deepcopy(run_envelope)
    verify_run_envelope(envelope_copy, package_copy)
    if run_identity.package_digest != package_copy.get("reviewer_input_package_hash"):
        raise ValueError("v1 package digest does not bind the verified package")
    if run_identity.source_action_contract_hash != package_copy.get("contract_hash"):
        raise ValueError("v1 source action contract hash does not bind the package")
    if run_identity.review_run_id != envelope_copy.get("review_run_id"):
        raise ValueError("v1 review run identity does not bind the run envelope")
    if run_identity.context_id != envelope_copy.get("reviewer_context_id"):
        raise ValueError("v1 context identity does not bind the run envelope")
    expected_brief_hash = package_copy.get("role_hashes", {}).get("reviewer_brief")
    if sha256_bytes(reviewer_brief_bytes) != expected_brief_hash:
        raise ValueError("v1 reviewer brief bytes do not bind the verified package")
    if _parse_json_object(output_schema_bytes, "v1 output schema") != package_copy.get(
        "review_output_schema"
    ):
        raise ValueError("v1 output schema bytes do not bind the verified package")

    envelope_bytes = canonical_json_bytes(envelope_copy)
    artifacts = _artifacts(
        reviewer_brief_bytes=reviewer_brief_bytes,
        review_package_bytes=package_archive_bytes,
        review_package_media_type="application/octet-stream",
        run_envelope_bytes=envelope_bytes,
        output_schema_bytes=output_schema_bytes,
    )

    def output_validator(output: dict[str, object]) -> None:
        validate_review_output(package_copy, envelope_copy, output)

    return PreparedReview(
        run_identity=run_identity,
        artifacts=artifacts,
        controller_only_hashes=(),
        output_validator=output_validator,
    )


def prepare_semantic_review_v21(
    *,
    package: dict[str, object],
    package_bytes: bytes,
    reviewer_brief_bytes: bytes,
    run_envelope_bytes: bytes,
    output_schema_bytes: bytes,
    run_identity: RunIdentity,
) -> PreparedReview:
    """Bind exact v2.1 bytes without translating package or output semantics."""

    _require_run_identity(run_identity, _V21_CONTRACT)
    if not isinstance(package, dict):
        raise ValueError("v2.1 package must be an object")
    _require_bytes(package_bytes, "package_bytes")
    _require_bytes(reviewer_brief_bytes, "reviewer_brief_bytes")
    _require_bytes(run_envelope_bytes, "run_envelope_bytes")
    _require_bytes(output_schema_bytes, "output_schema_bytes")
    parsed_package = _parse_json_object(package_bytes, "v2.1 package")
    if parsed_package != package:
        raise ValueError("v2.1 package bytes do not equal the supplied package")
    package_copy = copy.deepcopy(package)
    package_errors = validate_semantic_review_package_v21(package_copy)
    if package_errors:
        raise ValueError(f"v2.1 package validation failed: {package_errors}")
    if run_identity.package_schema_version != package_copy.get("review_schema_version"):
        raise ValueError("v2.1 package schema version does not bind the package")
    if run_identity.package_digest != package_copy.get("package_hash"):
        raise ValueError("v2.1 package digest does not bind the package")
    if run_identity.source_action_contract_hash != package_copy.get(
        "source_semantic_contract_hash"
    ):
        raise ValueError("v2.1 source semantic contract hash does not bind the package")
    if run_identity.source_definition_digest != package_copy.get(
        "source_definition_digest"
    ):
        raise ValueError("v2.1 source definition digest does not bind the package")

    artifacts = _artifacts(
        reviewer_brief_bytes=reviewer_brief_bytes,
        review_package_bytes=package_bytes,
        review_package_media_type="application/json",
        run_envelope_bytes=run_envelope_bytes,
        output_schema_bytes=output_schema_bytes,
    )

    def output_validator(output: dict[str, object]) -> None:
        errors = validate_semantic_review_output_v21(package_copy, output)
        if errors:
            raise ValueError(f"v2.1 output validation failed: {errors}")

    return PreparedReview(
        run_identity=run_identity,
        artifacts=artifacts,
        controller_only_hashes=(),
        output_validator=output_validator,
    )


def _artifacts(
    *,
    reviewer_brief_bytes: bytes,
    review_package_bytes: bytes,
    review_package_media_type: str,
    run_envelope_bytes: bytes,
    output_schema_bytes: bytes,
) -> tuple[InputArtifact, ...]:
    return (
        InputArtifact("reviewer_brief", "text/markdown", reviewer_brief_bytes),
        InputArtifact("review_package", review_package_media_type, review_package_bytes),
        InputArtifact("run_envelope", "application/json", run_envelope_bytes),
        InputArtifact("output_schema", "application/schema+json", output_schema_bytes),
    )


def _require_run_identity(run_identity: RunIdentity, contract_version: str) -> None:
    if type(run_identity) is not RunIdentity:
        raise ValueError("run_identity must be an exact RunIdentity")
    if run_identity.semantic_review_contract_version != contract_version:
        raise ValueError("semantic review contract version does not match adapter")


def _require_bytes(value: object, label: str) -> None:
    if type(value) is not bytes:
        raise ValueError(f"{label} must be exact bytes")


def _parse_json_object(raw_bytes: bytes, label: str) -> dict[str, object]:
    try:
        text = raw_bytes.decode("utf-8", errors="strict")
        decoder = json.JSONDecoder(
            object_pairs_hook=_without_duplicate_keys,
            parse_constant=_reject_non_json_number,
        )
        parsed, end = decoder.raw_decode(text, idx=len(text) - len(text.lstrip()))
    except (UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise ValueError(f"{label} must be one UTF-8 JSON object: {error}") from error
    if text[end:].strip():
        raise ValueError(f"{label} must contain exactly one JSON document")
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} must be a JSON object")
    return parsed


def _without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_non_json_number(value: str) -> object:
    raise ValueError(f"non-JSON numeric constant: {value}")
