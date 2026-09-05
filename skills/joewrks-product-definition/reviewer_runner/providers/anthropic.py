"""Pure Anthropic Messages settings and canonical four-role request projection."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import json

from ..identity import (
    RUNNER_CONTRACT_VERSION,
    SEMANTIC_REVIEW_CONTRACT_VERSIONS,
    canonical_json_bytes,
    sha256_bytes,
)
from ..request import REQUEST_SCHEMA_VERSION


ANTHROPIC_ADAPTER_ID = "anthropic-direct-messages"
ANTHROPIC_ADAPTER_VERSION = "1.0.0"
ANTHROPIC_API_VERSION = "2023-06-01"
ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
ANTHROPIC_HOST = "api.anthropic.com"
ANTHROPIC_PATH = "/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-5"
ANTHROPIC_PROJECTION_VERSION = "joewrks.anthropic-message-projection/1.0"
ANTHROPIC_MAX_TOKENS = 65536
ANTHROPIC_MAX_PROVIDER_BODY_BYTES = 32_000_000
ANTHROPIC_MAX_RESPONSE_BYTES = 16_777_216
ANTHROPIC_CREDENTIAL_SOURCE = "ANTHROPIC_API_KEY"

_REQUEST_KEYS = frozenset(
    {
        "inputs",
        "request_schema_version",
        "response_contract",
        "run_identity",
        "runner_contract_version",
    }
)
_RUN_IDENTITY_KEYS = frozenset(
    {
        "semantic_review_contract_version",
        "package_schema_version",
        "reviewer_id",
        "review_run_id",
        "context_id",
    }
)
_INPUT_KEYS = frozenset(
    {"logical_role", "media_type", "byte_count", "sha256", "content_base64"}
)
_REQUIRED_INPUTS = {
    "reviewer_brief": "text/markdown",
    "review_package": "application/json",
    "run_envelope": "application/json",
    "output_schema": "application/schema+json",
}
_CANONICAL_INPUT_ORDER = tuple(sorted(_REQUIRED_INPUTS))
_USER_BLOCK_ORDER = ("review_package", "run_envelope", "output_schema")


@dataclass(frozen=True, slots=True)
class AnthropicProjection:
    """A validated canonical request and its deterministic provider body."""

    canonical_request_sha256: str
    reviewer_id: str
    review_run_id: str
    context_id: str
    provider_body: bytes
    provider_body_sha256: str


def anthropic_settings_record() -> dict[str, object]:
    """Return the immutable-design identity of this fixed Messages projection."""

    return {
        "api_version": ANTHROPIC_API_VERSION,
        "containers": "ABSENT",
        "effort": "high",
        "endpoint": ANTHROPIC_ENDPOINT,
        "files": "ABSENT",
        "inference_geo": "us",
        "max_tokens": ANTHROPIC_MAX_TOKENS,
        "mcp": "ABSENT",
        "model": ANTHROPIC_MODEL,
        "output_mode": "plain_text_expected_to_be_exact_json",
        "projection": ANTHROPIC_PROJECTION_VERSION,
        "retrieval": "ABSENT",
        "seed": "ABSENT_NO_API_FIELD_DOCUMENTED",
        "service_tier": "standard_only",
        "skills": "ABSENT",
        "stream": False,
        "temperature": "ABSENT",
        "thinking": {"type": "adaptive"},
        "tools": "ABSENT",
        "top_k": "ABSENT",
        "top_p": "ABSENT",
    }


def anthropic_settings_bytes() -> bytes:
    """Return canonical bytes for the fixed settings identity record."""

    return canonical_json_bytes(anthropic_settings_record())


def anthropic_settings_sha256() -> str:
    """Return the digest derived from the canonical settings identity record."""

    return sha256_bytes(anthropic_settings_bytes())


def project_anthropic_request(request_bytes: bytes) -> AnthropicProjection:
    """Validate one canonical runner request and project it without I/O."""

    document = _parse_canonical_request(request_bytes)
    identity = _validate_request_document(document)
    inputs = _validate_inputs(document["inputs"])
    reviewer_brief = _decode_strict_utf8(inputs["reviewer_brief"]["content"])
    ordered_user_blocks = [
        {
            "type": "text",
            "text": canonical_json_bytes(
                {
                    "byte_count": inputs[role]["byte_count"],
                    "logical_role": role,
                    "media_type": inputs[role]["media_type"],
                    "sha256": inputs[role]["sha256"],
                }
            ).decode("utf-8")
            + "\n"
            + _decode_strict_utf8(inputs[role]["content"]),
        }
        for role in _USER_BLOCK_ORDER
    ]
    body = {
        "inference_geo": "us",
        "max_tokens": ANTHROPIC_MAX_TOKENS,
        "messages": [{"role": "user", "content": ordered_user_blocks}],
        "model": ANTHROPIC_MODEL,
        "output_config": {"effort": "high"},
        "service_tier": "standard_only",
        "stream": False,
        "system": [{"type": "text", "text": reviewer_brief}],
        "thinking": {"type": "adaptive"},
    }
    provider_body = canonical_json_bytes(body)
    if len(provider_body) > ANTHROPIC_MAX_PROVIDER_BODY_BYTES:
        raise ValueError("Anthropic provider body exceeds the configured size limit")
    return AnthropicProjection(
        canonical_request_sha256=sha256_bytes(request_bytes),
        reviewer_id=identity["reviewer_id"],
        review_run_id=identity["review_run_id"],
        context_id=identity["context_id"],
        provider_body=provider_body,
        provider_body_sha256=sha256_bytes(provider_body),
    )


def _parse_canonical_request(request_bytes: bytes) -> dict[str, object]:
    if not isinstance(request_bytes, bytes):
        raise ValueError("canonical request must be exact bytes")
    try:
        decoded = request_bytes.decode("utf-8")
        document = json.loads(
            decoded,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_number,
            parse_float=_reject_non_json_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("canonical request must be strict UTF-8 JSON") from error
    if type(document) is not dict:
        raise ValueError("canonical request must be a JSON object")
    try:
        canonical = canonical_json_bytes(document)
    except (TypeError, ValueError) as error:
        raise ValueError("canonical request JSON is invalid") from error
    if request_bytes != canonical:
        raise ValueError("canonical request bytes do not match the parsed document")
    return document


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_non_json_number(value: str) -> None:
    raise ValueError("non-integer JSON numbers are not permitted")


def _validate_request_document(document: dict[str, object]) -> dict[str, str]:
    if set(document) != _REQUEST_KEYS:
        raise ValueError("canonical request has an invalid top-level key set")
    if document["request_schema_version"] != REQUEST_SCHEMA_VERSION:
        raise ValueError("canonical request schema version does not match")
    if document["runner_contract_version"] != RUNNER_CONTRACT_VERSION:
        raise ValueError("runner contract version does not match")
    if document["response_contract"] != {
        "logical_response_count": 1,
        "media_type": "application/json",
    }:
        raise ValueError("response contract does not match the single JSON response")
    identity = document["run_identity"]
    if type(identity) is not dict or set(identity) != _RUN_IDENTITY_KEYS:
        raise ValueError("run identity key set does not match")
    for key in _RUN_IDENTITY_KEYS:
        if not _is_identifier(identity[key]):
            raise ValueError("run identity contains an invalid identifier")
    if identity["semantic_review_contract_version"] not in SEMANTIC_REVIEW_CONTRACT_VERSIONS:
        raise ValueError("semantic review contract version does not match")
    return identity  # type: ignore[return-value]


def _validate_inputs(raw_inputs: object) -> dict[str, dict[str, object]]:
    if type(raw_inputs) is not list or len(raw_inputs) != len(_REQUIRED_INPUTS):
        raise ValueError("canonical request must contain exactly four inputs")
    if [item.get("logical_role") if type(item) is dict else None for item in raw_inputs] != list(
        _CANONICAL_INPUT_ORDER
    ):
        raise ValueError("canonical request inputs are not in logical-role sort order")
    validated: dict[str, dict[str, object]] = {}
    for item in raw_inputs:
        if type(item) is not dict or set(item) != _INPUT_KEYS:
            raise ValueError("input record key set does not match")
        role = item["logical_role"]
        media_type = item["media_type"]
        if not isinstance(role, str) or _REQUIRED_INPUTS.get(role) != media_type:
            raise ValueError("input role or media type is not permitted")
        if type(item["byte_count"]) is not int or item["byte_count"] < 0:
            raise ValueError("input byte count is invalid")
        if not _is_sha256(item["sha256"]):
            raise ValueError("input SHA-256 is invalid")
        encoded = item["content_base64"]
        if not isinstance(encoded, str):
            raise ValueError("input base64 content is invalid")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError) as error:
            raise ValueError("input base64 content is invalid") from error
        if base64.b64encode(content).decode("ascii") != encoded:
            raise ValueError("input base64 content is not canonical")
        if len(content) != item["byte_count"] or sha256_bytes(content) != item["sha256"]:
            raise ValueError("input content commitment does not match")
        if role in validated:
            raise ValueError("input logical roles must be unique")
        validated[role] = {**item, "content": content}
    if set(validated) != set(_REQUIRED_INPUTS):
        raise ValueError("input logical roles must be exact")
    return validated


def _decode_strict_utf8(content: object) -> str:
    if not isinstance(content, bytes):
        raise ValueError("input content must be exact bytes")
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("input content must be strict UTF-8") from error


def _is_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
