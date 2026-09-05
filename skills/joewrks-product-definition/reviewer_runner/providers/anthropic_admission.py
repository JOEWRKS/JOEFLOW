"""Closed, local Anthropic admission evidence; this module performs no I/O."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum

from ..backend import (
    BackendDescriptor,
    CapabilityObservation,
    REQUIRED_CAPABILITIES,
    hash_evidence_record,
)
from ..identity import BackendIdentity, CapabilityClass, canonical_json_bytes, sha256_bytes
from .anthropic import (
    ANTHROPIC_ADAPTER_ID,
    ANTHROPIC_ADAPTER_VERSION,
    ANTHROPIC_API_VERSION,
    ANTHROPIC_ENDPOINT,
    ANTHROPIC_MAX_PROVIDER_BODY_BYTES,
    ANTHROPIC_MODEL,
    anthropic_settings_sha256,
)


ANTHROPIC_PROVISIONING_SCHEMA_VERSION = "joewrks.anthropic-provisioning-evidence/1.0"
ANTHROPIC_ADMISSION_SCHEMA_VERSION = "joewrks.anthropic-admission-evidence/1.0"
ANTHROPIC_CAPABILITY_EVIDENCE_SCHEMA_VERSION = "joewrks.anthropic-capability-evidence/1.0"
ANTHROPIC_CAPACITY_SCHEMA_VERSION = "joewrks.anthropic-local-capacity-measurement/1.0"
_CREDENTIAL_READINESS_EVIDENCE_KIND = "anthropic-credential-readiness"
_CREDENTIAL_READINESS_EVIDENCE_SOURCE = "controller-boundary"


class AnthropicProvisioningStatus(str, Enum):
    READY_FOR_PREFLIGHT = "READY_FOR_PREFLIGHT"
    BACKEND_PROVISIONING_REQUIRED = "BACKEND_PROVISIONING_REQUIRED"


@dataclass(frozen=True, slots=True)
class AnthropicProvisioningEvidence:
    schema_version: str
    expected_anthropic_workspace_id_sha256: str | None
    workspace_key_scope: str | None
    workspace_evidence_channel: str | None
    workspace_evidence_sha256: str | None
    retention_privacy_evidence_channel: str | None
    retention_privacy_evidence_sha256: str | None
    retention_privacy_approval: str | None
    inference_geo_evidence_sha256: str | None
    model_entitlement_evidence_sha256: str | None
    capacity_and_quota_evidence_sha256: str | None
    spend_approval_evidence_sha256: str | None
    provider_policy_approval_evidence_sha256: str | None
    credential_readiness_evidence_sha256: str | None


@dataclass(frozen=True, slots=True)
class AnthropicAdmissionEvidence:
    schema_version: str
    adapter_source_manifest_sha256: str | None
    local_conformance_evidence_sha256: str | None
    canonical_provider_body_sha256: str | None
    provider_official_contract_sha256: str | None
    local_capacity_measurement_sha256: str | None
    provisioning: AnthropicProvisioningEvidence


@dataclass(frozen=True, slots=True)
class AnthropicBackendConfiguration:
    provisioning_status: AnthropicProvisioningStatus
    descriptor: BackendDescriptor
    expected_anthropic_workspace_id_sha256: str | None
    admission_evidence_sha256: str


_METHODS = (
    "direct:anthropic-single-message-body",
    "direct:anthropic-no-continuation-fields",
    "direct:anthropic-direct-messages-stateless-contract",
    "direct:anthropic-tool-fields-absent",
    "direct:anthropic-retrieval-fields-absent",
    "direct:anthropic-web-fields-absent",
    "direct:anthropic-connector-mcp-fields-absent",
    "direct:anthropic-inline-text-only",
    "direct:anthropic-code-execution-fields-absent",
    "direct:anthropic-no-file-reference",
    "direct:anthropic-pinned-model-workspace-commitment",
    "direct:anthropic-canonical-settings",
    "direct:anthropic-capacity-and-quota-record",
    "direct:anthropic-one-text-existing-json-validator",
    "direct:anthropic-workspace-key-controller-boundary",
    "direct:anthropic-approved-account-policy",
    "direct:anthropic-request-response-hash-binding",
)

_BASE_PROOF = frozenset(
    {
        "adapter_source_manifest_sha256",
        "canonical_provider_body_sha256",
        "provider_official_contract_sha256",
        "local_conformance_evidence_sha256",
    }
)
_DEPENDENCIES = {
    "stateless_fresh_request": _BASE_PROOF,
    "no_continuation_id": _BASE_PROOF,
    "no_reviewer_memory": _BASE_PROOF,
    "no_tools": _BASE_PROOF,
    "no_retrieval": _BASE_PROOF,
    "no_web_or_browser": _BASE_PROOF,
    "no_connectors_or_mcp": _BASE_PROOF,
    "no_host_filesystem": frozenset({"adapter_source_manifest_sha256", "canonical_provider_body_sha256", "local_conformance_evidence_sha256"}),
    "no_code_execution": _BASE_PROOF,
    "no_file_by_reference": frozenset({"adapter_source_manifest_sha256", "canonical_provider_body_sha256", "local_conformance_evidence_sha256"}),
    "immutable_model_or_deployment_identity": frozenset({"adapter_source_manifest_sha256", "provider_official_contract_sha256", "expected_anthropic_workspace_id_sha256", "workspace_evidence_channel", "workspace_evidence_sha256", "inference_geo_evidence_sha256", "model_entitlement_evidence_sha256"}),
    "immutable_inference_settings": frozenset({"adapter_source_manifest_sha256", "canonical_provider_body_sha256", "local_conformance_evidence_sha256"}),
    "sufficient_payload_capacity": frozenset({"canonical_provider_body_sha256", "provider_official_contract_sha256", "local_capacity_measurement_sha256", "capacity_and_quota_evidence_sha256", "spend_approval_evidence_sha256"}),
    "exact_structured_output": _BASE_PROOF,
    "controller_only_authentication": frozenset({"adapter_source_manifest_sha256", "provider_official_contract_sha256", "local_conformance_evidence_sha256", "expected_anthropic_workspace_id_sha256", "workspace_evidence_channel", "workspace_evidence_sha256", "workspace_key_scope", "credential_readiness_evidence_sha256"}),
    "accepted_retention_and_privacy": frozenset({"provider_official_contract_sha256", "expected_anthropic_workspace_id_sha256", "workspace_evidence_channel", "workspace_evidence_sha256", "retention_privacy_evidence_channel", "retention_privacy_evidence_sha256", "retention_privacy_approval", "provider_policy_approval_evidence_sha256"}),
    "request_response_commitments": frozenset({"adapter_source_manifest_sha256", "canonical_provider_body_sha256", "local_conformance_evidence_sha256", "expected_anthropic_workspace_id_sha256", "workspace_evidence_channel", "workspace_evidence_sha256"}),
}


def provisioning_record(evidence: AnthropicProvisioningEvidence) -> dict[str, object]:
    """Return the exact fourteen-field JSON-compatible provisioning record."""

    _validate_provisioning_shape(evidence)
    return {field.name: getattr(evidence, field.name) for field in fields(AnthropicProvisioningEvidence)}


def admission_record(evidence: AnthropicAdmissionEvidence) -> dict[str, object]:
    """Return the exact seven-field JSON-compatible admission record."""

    _validate_admission_shape(evidence)
    return {
        "schema_version": evidence.schema_version,
        "adapter_source_manifest_sha256": evidence.adapter_source_manifest_sha256,
        "local_conformance_evidence_sha256": evidence.local_conformance_evidence_sha256,
        "canonical_provider_body_sha256": evidence.canonical_provider_body_sha256,
        "provider_official_contract_sha256": evidence.provider_official_contract_sha256,
        "local_capacity_measurement_sha256": evidence.local_capacity_measurement_sha256,
        "provisioning": provisioning_record(evidence.provisioning),
    }


def anthropic_credential_readiness_evidence_sha256(
    provisioning: AnthropicProvisioningEvidence,
) -> str:
    """Commit fixed non-secret controller-readiness evidence for one workspace."""

    _validate_provisioning_shape(provisioning)
    bindings = {
        field.name: getattr(provisioning, field.name)
        for field in fields(AnthropicProvisioningEvidence)
        if field.name != "credential_readiness_evidence_sha256"
    }
    return sha256_bytes(canonical_json_bytes({
        "evidence_kind": _CREDENTIAL_READINESS_EVIDENCE_KIND,
        "evidence_source": _CREDENTIAL_READINESS_EVIDENCE_SOURCE,
        "provisioning_bindings": bindings,
    }))


def unprovisioned_anthropic_admission() -> AnthropicAdmissionEvidence:
    """Return the registered-production placeholder without account authority."""

    return AnthropicAdmissionEvidence(
        schema_version=ANTHROPIC_ADMISSION_SCHEMA_VERSION,
        adapter_source_manifest_sha256=None,
        local_conformance_evidence_sha256=None,
        canonical_provider_body_sha256=None,
        provider_official_contract_sha256=None,
        local_capacity_measurement_sha256=None,
        provisioning=AnthropicProvisioningEvidence(
            schema_version=ANTHROPIC_PROVISIONING_SCHEMA_VERSION,
            expected_anthropic_workspace_id_sha256=None,
            workspace_key_scope=None,
            workspace_evidence_channel=None,
            workspace_evidence_sha256=None,
            retention_privacy_evidence_channel=None,
            retention_privacy_evidence_sha256=None,
            retention_privacy_approval=None,
            inference_geo_evidence_sha256=None,
            model_entitlement_evidence_sha256=None,
            capacity_and_quota_evidence_sha256=None,
            spend_approval_evidence_sha256=None,
            provider_policy_approval_evidence_sha256=None,
            credential_readiness_evidence_sha256=None,
        ),
    )


def build_anthropic_backend_configuration(
    evidence: AnthropicAdmissionEvidence,
) -> AnthropicBackendConfiguration:
    """Compile immutable local evidence into a non-I/O backend descriptor."""

    _validate_admission_shape(evidence)
    provisioning_hash = sha256_bytes(canonical_json_bytes(provisioning_record(evidence.provisioning)))
    admission_hash = sha256_bytes(canonical_json_bytes(admission_record(evidence)))
    invalid_fields = _invalid_evidence_fields(evidence)
    observations = tuple(
        _observation(capability, method, evidence, provisioning_hash, invalid_fields)
        for capability, method in zip(REQUIRED_CAPABILITIES, _METHODS, strict=True)
    )
    status = (
        AnthropicProvisioningStatus.READY_FOR_PREFLIGHT
        if all(item.classification is CapabilityClass.OBSERVED_PASS for item in observations)
        else AnthropicProvisioningStatus.BACKEND_PROVISIONING_REQUIRED
    )
    descriptor = BackendDescriptor(
        identity=BackendIdentity(
            backend_kind="STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
            adapter_id=ANTHROPIC_ADAPTER_ID,
            adapter_version=ANTHROPIC_ADAPTER_VERSION,
            endpoint_identity=ANTHROPIC_ENDPOINT,
            deployment_identity=_deployment_identity(evidence.provisioning),
            model_revision_identity=ANTHROPIC_MODEL,
            model_identity_stability="IMMUTABLE",
            inference_settings_sha256=anthropic_settings_sha256(),
            retention_policy_identity="anthropic-retention:" + provisioning_hash,
            privacy_policy_identity="anthropic-privacy:" + provisioning_hash,
            is_test_double=False,
        ),
        max_request_bytes=ANTHROPIC_MAX_PROVIDER_BODY_BYTES,
        observations=observations,
    )
    return AnthropicBackendConfiguration(
        provisioning_status=status,
        descriptor=descriptor,
        expected_anthropic_workspace_id_sha256=evidence.provisioning.expected_anthropic_workspace_id_sha256,
        admission_evidence_sha256=admission_hash,
    )


def _deployment_identity(provisioning: AnthropicProvisioningEvidence) -> str:
    return sha256_bytes(canonical_json_bytes({
        "adapter_id": ANTHROPIC_ADAPTER_ID,
        "adapter_version": ANTHROPIC_ADAPTER_VERSION,
        "api_version": ANTHROPIC_API_VERSION,
        "endpoint": ANTHROPIC_ENDPOINT,
        "expected_anthropic_workspace_id_sha256": provisioning.expected_anthropic_workspace_id_sha256,
        "inference_geo_policy": "us",
        "platform": "direct_claude_api",
        "provider": "anthropic",
    }))


def _observation(
    capability: str,
    method: str,
    evidence: AnthropicAdmissionEvidence,
    provisioning_hash: str,
    invalid_fields: frozenset[str],
) -> CapabilityObservation:
    dependencies = _DEPENDENCIES[capability]
    if dependencies.intersection(invalid_fields):
        classification = CapabilityClass.OBSERVED_FAIL
    elif any(_evidence_value(evidence, dependency) is None for dependency in dependencies):
        classification = CapabilityClass.UNAVAILABLE
    else:
        classification = CapabilityClass.OBSERVED_PASS
    record = {
        "schema_version": ANTHROPIC_CAPABILITY_EVIDENCE_SCHEMA_VERSION,
        "capability": capability,
        "method": method,
        "classification": classification.value,
        "adapter_source_sha256": evidence.adapter_source_manifest_sha256,
        "canonical_provider_body_sha256": evidence.canonical_provider_body_sha256,
        "provisioning_evidence_sha256": provisioning_hash,
        "provider_official_contract_sha256": evidence.provider_official_contract_sha256,
        "workspace_commitment_sha256": evidence.provisioning.workspace_evidence_sha256,
        "local_capacity_measurement_sha256": evidence.local_capacity_measurement_sha256,
        "local_conformance_evidence_sha256": evidence.local_conformance_evidence_sha256,
        "settings_sha256": anthropic_settings_sha256(),
    }
    return CapabilityObservation(capability, classification, method, hash_evidence_record(record))


def _evidence_value(evidence: AnthropicAdmissionEvidence, name: str) -> object:
    if hasattr(evidence, name):
        return getattr(evidence, name)
    return getattr(evidence.provisioning, name)


def _validate_admission_shape(evidence: AnthropicAdmissionEvidence) -> None:
    _require_exact_instance(evidence, AnthropicAdmissionEvidence, "admission")
    if evidence.schema_version != ANTHROPIC_ADMISSION_SCHEMA_VERSION:
        raise ValueError("admission schema_version does not match")
    for name in (
        "adapter_source_manifest_sha256", "local_conformance_evidence_sha256",
        "canonical_provider_body_sha256", "provider_official_contract_sha256",
        "local_capacity_measurement_sha256",
    ):
        _require_optional_string(getattr(evidence, name), name)
    _validate_provisioning_shape(evidence.provisioning)


def _validate_provisioning_shape(evidence: AnthropicProvisioningEvidence) -> None:
    _require_exact_instance(evidence, AnthropicProvisioningEvidence, "provisioning")
    if evidence.schema_version != ANTHROPIC_PROVISIONING_SCHEMA_VERSION:
        raise ValueError("provisioning schema_version does not match")
    for field in fields(AnthropicProvisioningEvidence):
        if field.name != "schema_version":
            _require_optional_string(
                getattr(evidence, field.name),
                field.name,
            )


def _invalid_evidence_fields(evidence: AnthropicAdmissionEvidence) -> frozenset[str]:
    provisioning = evidence.provisioning
    invalid: set[str] = set()
    if provisioning.workspace_key_scope not in (None, "WORKSPACE_SCOPED"):
        invalid.add("workspace_key_scope")
    if provisioning.workspace_evidence_channel not in (None, "MACHINE_READABLE", "CONSOLE_OR_ADMINISTRATOR"):
        invalid.add("workspace_evidence_channel")
    if provisioning.retention_privacy_evidence_channel not in (None, "CONTRACT_CONSOLE_OR_ADMINISTRATOR"):
        invalid.add("retention_privacy_evidence_channel")
    if provisioning.retention_privacy_approval not in (None, "STANDARD_RETENTION_ACCEPTED", "ZDR_VERIFIED"):
        invalid.add("retention_privacy_approval")
    evidence_digest_names = (
            "adapter_source_manifest_sha256", "local_conformance_evidence_sha256",
            "canonical_provider_body_sha256", "provider_official_contract_sha256",
            "local_capacity_measurement_sha256",
        )
    provisioning_digest_names = tuple(
        field.name for field in fields(AnthropicProvisioningEvidence)
        if field.name.endswith("_sha256")
    )
    named_digests = {
        **{name: getattr(evidence, name) for name in evidence_digest_names},
        **{name: getattr(provisioning, name) for name in provisioning_digest_names},
    }
    for name, digest in named_digests.items():
        if digest is not None and not _is_sha256(digest):
            invalid.add(name)
    for name, digest in named_digests.items():
        if digest is None:
            continue
        for other_name, other_digest in named_digests.items():
            if name != other_name and digest == other_digest:
                invalid.update({name, other_name})
    credential_digest = provisioning.credential_readiness_evidence_sha256
    if (
        credential_digest is not None
        and credential_digest != anthropic_credential_readiness_evidence_sha256(provisioning)
    ):
        invalid.add("credential_readiness_evidence_sha256")
    return frozenset(invalid)


def _require_exact_instance(value: object, expected: type[object], label: str) -> None:
    if type(value) is not expected:
        raise ValueError(f"{label} must be an exact {expected.__name__}")


def _require_optional_string(
    value: object,
    name: str,
    *,
    reject_sensitive: bool = True,
) -> None:
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{name} must be a string or null")
    if reject_sensitive and isinstance(value, str) and _looks_like_secret_or_path(value):
        raise ValueError(f"{name} cannot contain a credential, key label, or path")


def _looks_like_secret_or_path(value: str) -> bool:
    lowered = value.lower()
    return (
        "api_key" in lowered or "api-key" in lowered or "apikey" in lowered
        or "sk-" in lowered or "secret" in lowered or "key" in lowered
        or "/" in value or "\\" in value
    )


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)
