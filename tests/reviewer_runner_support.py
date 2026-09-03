"""Test-only deterministic support for reviewer-runner backend tests."""

from __future__ import annotations

from dataclasses import fields, replace
import json
from typing import Mapping


class DeterministicFakeBackend:
    """A deliberately local, deterministic bytes-in/bytes-out test double."""

    def __init__(
        self,
        raw_response: bytes,
        *,
        descriptor=None,
        scripted_error=None,
        events=(),
        metadata_drift: Mapping[str, object] | None = None,
    ):
        # Imports are deferred so RED can load and execute before backend.py exists.
        from reviewer_runner.backend import (
            BackendDescriptor,
            BackendResponse,
            CapabilityObservation,
            REQUIRED_CAPABILITIES,
            hash_evidence_record,
        )
        from reviewer_runner.identity import BackendIdentity, CapabilityClass, canonical_json_bytes, sha256_bytes

        if not isinstance(raw_response, bytes):
            raise TypeError("raw_response must be exact bytes")
        try:
            decoded_response = json.loads(raw_response)
        except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("raw_response must be precomputed JSON bytes") from error
        if not isinstance(decoded_response, (dict, list)):
            raise ValueError("raw_response must be a JSON object or array")
        if metadata_drift is not None and not isinstance(metadata_drift, Mapping):
            raise TypeError("metadata_drift must be a mapping")

        if descriptor is None:
            identity = BackendIdentity(
                backend_kind="STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
                adapter_id="deterministic-fake",
                adapter_version="test-only",
                endpoint_identity="test-only",
                deployment_identity="test-only",
                model_revision_identity="test-only",
                model_identity_stability="UNKNOWN",
                inference_settings_sha256=sha256_bytes(canonical_json_bytes({"test": "fake"})),
                retention_policy_identity="test-only",
                privacy_policy_identity="test-only",
                is_test_double=True,
            )
            descriptor = BackendDescriptor(
                identity=identity,
                max_request_bytes=1_000_000,
                observations=tuple(
                    CapabilityObservation(
                        capability=capability,
                        classification=CapabilityClass.UNAVAILABLE,
                        method="test-double",
                        evidence_sha256=hash_evidence_record(
                            {"capability": capability, "method": "test-double"}
                        ),
                    )
                    for capability in REQUIRED_CAPABILITIES
                ),
            )
        else:
            identity = replace(descriptor.identity, is_test_double=True)
            descriptor = replace(
                descriptor,
                identity=identity,
                observations=tuple(
                    replace(observation, classification=CapabilityClass.UNAVAILABLE)
                    for observation in descriptor.observations
                ),
            )

        self._raw_response = raw_response
        self._descriptor = descriptor
        self._scripted_error = scripted_error
        self._events = tuple(events)
        self._metadata_drift = dict(metadata_drift or {})
        allowed_drift = {field.name for field in fields(BackendResponse)}
        unsupported_drift = set(self._metadata_drift).difference(allowed_drift)
        if unsupported_drift:
            raise ValueError("metadata_drift contains unsupported BackendResponse fields")
        self.received_request_bytes: list[bytes] = []

    def describe(self):
        return self._descriptor

    def invoke(self, request_bytes: bytes, *, timeout_seconds: int):
        from reviewer_runner.backend import BackendResponse
        from reviewer_runner.identity import backend_identity_sha256, sha256_bytes

        if not isinstance(request_bytes, bytes):
            raise TypeError("request_bytes must be exact bytes")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive integer")
        self.received_request_bytes.append(request_bytes)
        if self._scripted_error is not None:
            raise self._scripted_error
        request_document = json.loads(request_bytes)
        run_identity = request_document["run_identity"]
        response = BackendResponse(
            raw_bytes=self._raw_response,
            provider_request_id="deterministic-fake-request",
            request_sha256=sha256_bytes(request_bytes),
            reviewer_id=run_identity["reviewer_id"],
            review_run_id=run_identity["review_run_id"],
            context_id=run_identity["context_id"],
            backend_identity_sha256=backend_identity_sha256(self._descriptor.identity),
            response_count=1,
            continuation_id=None,
            previous_response_id=None,
            events=self._events,
        )
        return replace(response, **self._metadata_drift)
