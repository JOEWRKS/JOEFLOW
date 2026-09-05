"""Pure Anthropic Messages settings and canonical four-role request projection."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import http.client
import json
import socket
import ssl
from typing import Callable

from ..backend import BackendInvocationError
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


@dataclass(frozen=True, slots=True)
class AnthropicHttpResponse:
    """One bounded HTTP response returned by the fixed Anthropic transport."""

    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes


class StdlibAnthropicTransport:
    """Make one direct, non-streaming HTTPS request to the fixed endpoint."""

    def __init__(
        self,
        *,
        test_only_connection_factory: Callable[[str, int, int, ssl.SSLContext], object]
        | None = None,
    ):
        self._test_only_connection_factory = test_only_connection_factory

    @property
    def is_test_double(self) -> bool:
        """Return whether the explicit test-only connection seam is active."""

        return self._test_only_connection_factory is not None

    def post(
        self,
        body: bytes,
        *,
        api_key: str,
        timeout_seconds: int,
    ) -> AnthropicHttpResponse:
        """Send exactly one fixed Messages POST and return one bounded response."""

        if type(body) is not bytes:
            raise ValueError("Anthropic request body must be exact bytes")
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("Anthropic API key must be a non-empty string")
        if any(ord(character) < 32 or ord(character) == 127 or ord(character) > 255 for character in api_key):
            raise BackendInvocationError(
                "TRANSPORT_ERROR", "Anthropic API credential is not valid for an HTTP header"
            )
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, int)
            or timeout_seconds <= 0
        ):
            raise ValueError("Anthropic timeout_seconds must be a positive integer")

        connection: object | None = None
        response_exists = False
        try:
            context = ssl.create_default_context()
            if self._test_only_connection_factory is None:
                connection = http.client.HTTPSConnection(
                    ANTHROPIC_HOST,
                    port=443,
                    timeout=timeout_seconds,
                    context=context,
                )
            else:
                connection = self._test_only_connection_factory(
                    ANTHROPIC_HOST,
                    443,
                    timeout_seconds,
                    context,
                )
            connection.request(
                "POST",
                ANTHROPIC_PATH,
                body=body,
                headers={
                    "anthropic-version": ANTHROPIC_API_VERSION,
                    "connection": "close",
                    "content-type": "application/json",
                    "x-api-key": api_key,
                },
            )
            response = connection.getresponse()
            response_exists = True
            if response.status != 200:
                raise BackendInvocationError(
                    "NO_RESPONSE", "Anthropic API returned a non-success response"
                )
            response_headers = tuple(response.getheaders())
            declared_content_length = _declared_content_length(response_headers)
            if (
                declared_content_length is not None
                and declared_content_length > ANTHROPIC_MAX_RESPONSE_BYTES
            ):
                raise BackendInvocationError(
                    "NO_RESPONSE", "Anthropic API response could not be read"
                )
            response_body = response.read(ANTHROPIC_MAX_RESPONSE_BYTES + 1)
            if len(response_body) > ANTHROPIC_MAX_RESPONSE_BYTES:
                raise BackendInvocationError(
                    "NO_RESPONSE", "Anthropic API response exceeded the configured size limit"
                )
            if (
                declared_content_length is not None
                and len(response_body) != declared_content_length
            ):
                raise BackendInvocationError(
                    "NO_RESPONSE", "Anthropic API response could not be read"
                )
            return AnthropicHttpResponse(
                status=response.status,
                headers=response_headers,
                body=response_body,
            )
        except BackendInvocationError:
            raise
        except (socket.timeout, TimeoutError):
            raise BackendInvocationError("TIMEOUT", "Anthropic API request timed out") from None
        except (OSError, EOFError, ssl.SSLError, http.client.HTTPException, ValueError, UnicodeError):
            if response_exists:
                raise BackendInvocationError(
                    "NO_RESPONSE", "Anthropic API response could not be read"
                ) from None
            raise BackendInvocationError(
                "TRANSPORT_ERROR", "Anthropic API transport failed"
            ) from None
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass


def _declared_content_length(headers: tuple[tuple[str, str], ...]) -> int | None:
    """Return one valid Content-Length, rejecting ambiguous response framing."""

    content_lengths: list[str] = []
    transfer_encoding_present = False
    for name, value in headers:
        if not isinstance(name, str) or not isinstance(value, str):
            raise BackendInvocationError("NO_RESPONSE", "Anthropic API response could not be read")
        normalized_name = name.lower()
        if normalized_name == "content-length":
            content_lengths.append(value)
        elif normalized_name == "transfer-encoding":
            transfer_encoding_present = True
    if not content_lengths:
        return None
    if len(content_lengths) != 1 or transfer_encoding_present:
        raise BackendInvocationError("NO_RESPONSE", "Anthropic API response could not be read")
    declared = content_lengths[0]
    if not declared or any(character < "0" or character > "9" for character in declared):
        raise BackendInvocationError("NO_RESPONSE", "Anthropic API response could not be read")
    return int(declared)


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
    response_contract = document["response_contract"]
    if (
        type(response_contract) is not dict
        or set(response_contract) != {"logical_response_count", "media_type"}
        or type(response_contract["logical_response_count"]) is not int
        or response_contract["logical_response_count"] != 1
        or response_contract["media_type"] != "application/json"
    ):
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
