"""Immutable identities and receipts for isolated reviewer-runner executions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields, replace
from enum import Enum
import hashlib
import json


RUNNER_CONTRACT_VERSION = "joewrks.reviewer-runner/1.0"
RECEIPT_SCHEMA_VERSION = "joewrks.reviewer-runner-receipt/1.0"
SEMANTIC_REVIEW_CONTRACT_VERSION = "joewrks.semantic-review/1.0"

_INPUT_ROLES = (
    "reviewer_brief",
    "review_package",
    "run_envelope",
    "output_schema",
)
_MODEL_IDENTITY_STABILITIES = {
    "IMMUTABLE",
    "STABLE_DEPLOYMENT",
    "FLOATING",
    "UNKNOWN",
}


class RunnerState(str, Enum):
    CALIBRATION_NOT_RUN = "CALIBRATION_NOT_RUN"
    ISOLATION_CAPABILITY_UNAVAILABLE = "ISOLATION_CAPABILITY_UNAVAILABLE"
    ISOLATION_PREFLIGHT_FAILED = "ISOLATION_PREFLIGHT_FAILED"
    PACKAGE_BINDING_MISMATCH = "PACKAGE_BINDING_MISMATCH"
    REVIEWER_EXECUTION_FAILED = "REVIEWER_EXECUTION_FAILED"
    REVIEW_OUTPUT_INVALID = "REVIEW_OUTPUT_INVALID"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"


class CapabilityClass(str, Enum):
    OBSERVED_PASS = "OBSERVED_PASS"
    OBSERVED_FAIL = "OBSERVED_FAIL"
    UNAVAILABLE = "UNAVAILABLE"
    UNTESTED = "UNTESTED"


class RunnerIdentityError(ValueError):
    """A stable, machine-readable contract validation failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class RunIdentity:
    semantic_review_contract_version: str
    package_schema_version: str
    package_digest: str
    source_action_contract_hash: str
    source_definition_digest: str | None
    reviewer_id: str
    review_run_id: str
    context_id: str
    cohort_id: str | None
    case_id: str | None


@dataclass(frozen=True)
class BackendIdentity:
    backend_kind: str
    adapter_id: str
    adapter_version: str
    endpoint_identity: str
    deployment_identity: str
    model_revision_identity: str
    model_identity_stability: str
    inference_settings_sha256: str
    retention_policy_identity: str
    privacy_policy_identity: str
    is_test_double: bool


@dataclass(frozen=True)
class InputCommitment:
    logical_role: str
    media_type: str
    byte_count: int
    sha256: str


@dataclass(frozen=True)
class ResponseIdentity:
    provider_request_id: str
    request_sha256: str
    reviewer_id: str
    review_run_id: str
    context_id: str
    backend_identity_sha256: str
    response_count: int
    raw_response_byte_count: int
    raw_response_sha256: str
    parsed_output_sha256: str


@dataclass(frozen=True)
class RunnerReceipt:
    state: RunnerState
    run_identity: RunIdentity
    backend_identity: BackendIdentity
    permitted_input_inventory: tuple[InputCommitment, ...]
    request_sha256: str
    capability_preflight_sha256: str
    isolation_receipt_sha256: str
    response_identity: ResponseIdentity
    receipt_sha256: str


def canonical_json_bytes(value: object) -> bytes:
    """Return deterministic compact UTF-8 JSON bytes."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for exact bytes."""

    return hashlib.sha256(value).hexdigest()


def receipt_content(receipt: RunnerReceipt) -> dict[str, object]:
    """Return the exact self-hashed, JSON-compatible receipt content."""

    _require_instance(receipt, RunnerReceipt, "RECEIPT_SCHEMA_INVALID")
    return {
        "state": receipt.state.value,
        "run_identity": _json_value(receipt.run_identity),
        "backend_identity": _json_value(receipt.backend_identity),
        "permitted_input_inventory": [
            _json_value(item) for item in receipt.permitted_input_inventory
        ],
        "request_sha256": receipt.request_sha256,
        "capability_preflight_sha256": receipt.capability_preflight_sha256,
        "isolation_receipt_sha256": receipt.isolation_receipt_sha256,
        "response_identity": _json_value(receipt.response_identity),
    }


def receipt_document(receipt: RunnerReceipt) -> dict[str, object]:
    """Return the complete persisted JSON-compatible receipt."""

    return {**receipt_content(receipt), "receipt_sha256": receipt.receipt_sha256}


def backend_identity_sha256(identity: BackendIdentity) -> str:
    """Return the canonical hash binding a response to one backend identity."""

    _require_instance(identity, BackendIdentity, "BACKEND_IDENTITY_INVALID")
    return sha256_bytes(canonical_json_bytes(_json_value(identity)))


def build_runner_receipt(
    *,
    state: RunnerState,
    run_identity: RunIdentity,
    backend_identity: BackendIdentity,
    permitted_input_inventory: tuple[InputCommitment, ...] | list[InputCommitment],
    request_sha256: str,
    capability_preflight_sha256: str,
    isolation_receipt_sha256: str,
    response_identity: ResponseIdentity | dict[str, object],
) -> RunnerReceipt:
    """Build, freeze, self-hash, and validate an immutable runner receipt."""

    if isinstance(response_identity, dict):
        try:
            response_identity = ResponseIdentity(**dict(response_identity))
        except TypeError as error:
            raise RunnerIdentityError("RESPONSE_IDENTITY_INVALID", str(error)) from error
    _require_instance(response_identity, ResponseIdentity, "RESPONSE_IDENTITY_INVALID")
    receipt = RunnerReceipt(
        state=state,
        run_identity=run_identity,
        backend_identity=backend_identity,
        permitted_input_inventory=tuple(permitted_input_inventory),
        request_sha256=request_sha256,
        capability_preflight_sha256=capability_preflight_sha256,
        isolation_receipt_sha256=isolation_receipt_sha256,
        response_identity=response_identity,
        receipt_sha256="0" * 64,
    )
    receipt = replace(
        receipt,
        receipt_sha256=sha256_bytes(canonical_json_bytes(receipt_content(receipt))),
    )
    validate_runner_receipt(receipt)
    return receipt


def validate_runner_receipt(
    receipt: RunnerReceipt,
    *,
    expected_run_identity: RunIdentity | None = None,
    expected_backend_identity: BackendIdentity | None = None,
    expected_input_inventory: tuple[InputCommitment, ...] | list[InputCommitment] | None = None,
) -> None:
    """Validate receipt structure, internal bindings, self-hash, and optional inputs.

    Optional expected identities make an external comparison explicit; they are not
    persisted in the receipt and therefore do not weaken its self-hash contract.
    """

    _require_instance(receipt, RunnerReceipt, "RECEIPT_SCHEMA_INVALID")
    _validate_state(receipt.state)
    _validate_run_identity(receipt.run_identity)
    _validate_backend_identity(receipt.backend_identity)
    _validate_inventory(receipt.permitted_input_inventory)
    _validate_response_identity(receipt.response_identity)
    for name in (
        "request_sha256",
        "capability_preflight_sha256",
        "isolation_receipt_sha256",
        "receipt_sha256",
    ):
        _require_digest(getattr(receipt, name), name.upper())

    if receipt.run_identity.package_digest != _inventory_by_role(
        receipt.permitted_input_inventory
    )["review_package"].sha256:
        _fail("PACKAGE_DIGEST_MISMATCH", "package_digest must match review_package")
    if receipt.request_sha256 != receipt.response_identity.request_sha256:
        _fail("REQUEST_DIGEST_MISMATCH", "response request_sha256 does not match receipt")
    if receipt.run_identity.reviewer_id != receipt.response_identity.reviewer_id:
        _fail("REVIEWER_ID_MISMATCH", "response reviewer_id does not match run identity")
    if receipt.run_identity.review_run_id != receipt.response_identity.review_run_id:
        _fail("REVIEW_RUN_ID_MISMATCH", "response review_run_id does not match run identity")
    if receipt.run_identity.context_id != receipt.response_identity.context_id:
        _fail("CONTEXT_ID_MISMATCH", "response context_id does not match run identity")
    if receipt.response_identity.backend_identity_sha256 != backend_identity_sha256(
        receipt.backend_identity
    ):
        _fail("BACKEND_IDENTITY_MISMATCH", "response backend hash does not match backend identity")

    _validate_expected_run_identity(receipt.run_identity, expected_run_identity)
    _validate_expected_backend_identity(receipt.backend_identity, expected_backend_identity)
    _validate_expected_inventory(receipt.permitted_input_inventory, expected_input_inventory)

    observed_receipt_hash = sha256_bytes(canonical_json_bytes(receipt_content(receipt)))
    if receipt.receipt_sha256 != observed_receipt_hash:
        _fail("RECEIPT_SHA256_MISMATCH", "receipt_sha256 does not match receipt content")


def validate_receipt_document(document: dict[str, object]) -> RunnerReceipt:
    """Validate an exact JSON receipt document and return its frozen form."""

    if not isinstance(document, dict):
        _fail("RECEIPT_SCHEMA_INVALID", "receipt document must be an object")
    _require_exact_keys(document, _field_names(RunnerReceipt), "receipt document")
    try:
        receipt = RunnerReceipt(
            state=RunnerState(document["state"]),
            run_identity=_run_identity_from_document(document["run_identity"]),
            backend_identity=_backend_identity_from_document(document["backend_identity"]),
            permitted_input_inventory=tuple(
                _input_commitment_from_document(item)
                for item in _require_list(
                    document["permitted_input_inventory"], "permitted_input_inventory"
                )
            ),
            request_sha256=_require_string(document["request_sha256"], "request_sha256"),
            capability_preflight_sha256=_require_string(
                document["capability_preflight_sha256"], "capability_preflight_sha256"
            ),
            isolation_receipt_sha256=_require_string(
                document["isolation_receipt_sha256"], "isolation_receipt_sha256"
            ),
            response_identity=_response_identity_from_document(document["response_identity"]),
            receipt_sha256=_require_string(document["receipt_sha256"], "receipt_sha256"),
        )
    except (KeyError, TypeError, ValueError) as error:
        _fail("RECEIPT_SCHEMA_INVALID", str(error))
    validate_runner_receipt(receipt)
    return receipt


def _validate_run_identity(identity: RunIdentity) -> None:
    _require_instance(identity, RunIdentity, "RUN_IDENTITY_INVALID")
    if identity.semantic_review_contract_version != SEMANTIC_REVIEW_CONTRACT_VERSION:
        _fail(
            "SEMANTIC_REVIEW_CONTRACT_VERSION_MISMATCH",
            "semantic_review_contract_version is not the semantic-review/1.0 contract",
        )
    for name in (
        "package_schema_version",
        "reviewer_id",
        "review_run_id",
        "context_id",
    ):
        _require_identifier(getattr(identity, name), name)
    for name in ("package_digest", "source_action_contract_hash"):
        _require_digest(getattr(identity, name), name.upper())
    if identity.source_definition_digest is not None:
        _require_digest(identity.source_definition_digest, "SOURCE_DEFINITION_DIGEST")
    for name in ("cohort_id", "case_id"):
        value = getattr(identity, name)
        if value is not None:
            _require_identifier(value, name)


def _validate_backend_identity(identity: BackendIdentity) -> None:
    _require_instance(identity, BackendIdentity, "BACKEND_IDENTITY_INVALID")
    if identity.backend_kind != "STATELESS_TOOLLESS_EXTERNAL_INFERENCE":
        _fail("BACKEND_KIND_INVALID", "backend_kind must be STATELESS_TOOLLESS_EXTERNAL_INFERENCE")
    for name in (
        "adapter_id",
        "adapter_version",
        "endpoint_identity",
        "deployment_identity",
        "model_revision_identity",
        "retention_policy_identity",
        "privacy_policy_identity",
    ):
        _require_identifier(getattr(identity, name), name)
    if identity.model_identity_stability not in _MODEL_IDENTITY_STABILITIES:
        _fail("MODEL_IDENTITY_STABILITY_INVALID", "model_identity_stability is invalid")
    if not identity.is_test_double and identity.model_identity_stability in {"FLOATING", "UNKNOWN"}:
        _fail(
            "MODEL_IDENTITY_NOT_IMMUTABLE",
            "a non-test backend requires an immutable or stable deployment model identity",
        )
    if not isinstance(identity.is_test_double, bool):
        _fail("BACKEND_IDENTITY_INVALID", "is_test_double must be a boolean")
    _require_digest(identity.inference_settings_sha256, "INFERENCE_SETTINGS_SHA256")


def _validate_inventory(inventory: tuple[InputCommitment, ...]) -> None:
    if not isinstance(inventory, tuple) or len(inventory) != len(_INPUT_ROLES):
        _fail("INPUT_INVENTORY_INVALID", "input inventory must contain exactly four records")
    observed_roles: list[str] = []
    for item in inventory:
        _require_instance(item, InputCommitment, "INPUT_INVENTORY_INVALID")
        _require_identifier(item.logical_role, "logical_role")
        _require_identifier(item.media_type, "media_type")
        if isinstance(item.byte_count, bool) or not isinstance(item.byte_count, int) or item.byte_count < 0:
            _fail("INPUT_INVENTORY_INVALID", "input byte_count must be a non-negative integer")
        _require_digest(item.sha256, "INPUT_SHA256")
        observed_roles.append(item.logical_role)
    if set(observed_roles) != set(_INPUT_ROLES) or len(set(observed_roles)) != len(_INPUT_ROLES):
        _fail("INPUT_INVENTORY_INVALID", "input inventory roles must be unique and exact")


def _validate_response_identity(identity: ResponseIdentity) -> None:
    _require_instance(identity, ResponseIdentity, "RESPONSE_IDENTITY_INVALID")
    for name in ("provider_request_id", "reviewer_id", "review_run_id", "context_id"):
        _require_identifier(getattr(identity, name), name)
    for name in (
        "request_sha256",
        "backend_identity_sha256",
        "raw_response_sha256",
        "parsed_output_sha256",
    ):
        _require_digest(getattr(identity, name), name.upper())
    if identity.response_count != 1:
        _fail("RESPONSE_COUNT_INVALID", "response_count must be exactly one")
    if (
        isinstance(identity.raw_response_byte_count, bool)
        or not isinstance(identity.raw_response_byte_count, int)
        or identity.raw_response_byte_count < 0
    ):
        _fail("RESPONSE_IDENTITY_INVALID", "raw_response_byte_count must be non-negative")


def _validate_expected_run_identity(actual: RunIdentity, expected: RunIdentity | None) -> None:
    if expected is None:
        return
    _validate_run_identity(expected)
    codes = {
        "package_digest": "PACKAGE_DIGEST_MISMATCH",
        "source_action_contract_hash": "SOURCE_ACTION_CONTRACT_HASH_MISMATCH",
        "source_definition_digest": "SOURCE_DEFINITION_DIGEST_MISMATCH",
        "reviewer_id": "REVIEWER_ID_MISMATCH",
        "review_run_id": "REVIEW_RUN_ID_MISMATCH",
        "context_id": "CONTEXT_ID_MISMATCH",
        "cohort_id": "COHORT_ID_MISMATCH",
        "case_id": "CASE_ID_MISMATCH",
    }
    for name, code in codes.items():
        if getattr(actual, name) != getattr(expected, name):
            _fail(code, f"run identity {name} does not match expected identity")


def _validate_expected_backend_identity(
    actual: BackendIdentity, expected: BackendIdentity | None
) -> None:
    if expected is None:
        return
    _validate_backend_identity(expected)
    for name in ("model_revision_identity", "model_identity_stability"):
        if getattr(actual, name) != getattr(expected, name):
            _fail("MODEL_IDENTITY_MISMATCH", "backend model identity does not match expected")
    if actual.inference_settings_sha256 != expected.inference_settings_sha256:
        _fail("INFERENCE_SETTINGS_MISMATCH", "inference settings do not match expected")
    if actual != expected:
        _fail("BACKEND_IDENTITY_MISMATCH", "backend identity does not match expected")


def _validate_expected_inventory(
    actual: tuple[InputCommitment, ...],
    expected: tuple[InputCommitment, ...] | list[InputCommitment] | None,
) -> None:
    if expected is None:
        return
    expected_inventory = tuple(expected)
    _validate_inventory(expected_inventory)
    actual_by_role = _inventory_by_role(actual)
    expected_by_role = _inventory_by_role(expected_inventory)
    for role, code in (
        ("review_package", "PACKAGE_DIGEST_MISMATCH"),
        ("reviewer_brief", "BRIEF_DIGEST_MISMATCH"),
        ("output_schema", "OUTPUT_SCHEMA_DIGEST_MISMATCH"),
        ("run_envelope", "RUN_ENVELOPE_DIGEST_MISMATCH"),
    ):
        if actual_by_role[role] != expected_by_role[role]:
            _fail(code, f"{role} commitment does not match expected inventory")


def _validate_state(state: RunnerState) -> None:
    if not isinstance(state, RunnerState):
        _fail("RUNNER_STATE_INVALID", "state must be a RunnerState")


def _inventory_by_role(inventory: tuple[InputCommitment, ...]) -> dict[str, InputCommitment]:
    return {item.logical_role: item for item in inventory}


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


def _field_names(cls: type[object]) -> set[str]:
    return {field.name for field in fields(cls)}


def _require_exact_keys(value: dict[str, object], expected: set[str], label: str) -> None:
    if set(value) != expected:
        _fail("RECEIPT_SCHEMA_INVALID", f"{label} has missing or extra fields")


def _require_mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail("RECEIPT_SCHEMA_INVALID", f"{label} must be an object")
    return value


def _require_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        _fail("RECEIPT_SCHEMA_INVALID", f"{label} must be an array")
    return value


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str):
        _fail("RECEIPT_SCHEMA_INVALID", f"{label} must be a string")
    return value


def _run_identity_from_document(value: object) -> RunIdentity:
    value = _require_mapping(value, "run_identity")
    _require_exact_keys(value, _field_names(RunIdentity), "run_identity")
    return RunIdentity(**dict(value))


def _backend_identity_from_document(value: object) -> BackendIdentity:
    value = _require_mapping(value, "backend_identity")
    _require_exact_keys(value, _field_names(BackendIdentity), "backend_identity")
    return BackendIdentity(**dict(value))


def _input_commitment_from_document(value: object) -> InputCommitment:
    value = _require_mapping(value, "input commitment")
    _require_exact_keys(value, _field_names(InputCommitment), "input commitment")
    return InputCommitment(**dict(value))


def _response_identity_from_document(value: object) -> ResponseIdentity:
    value = _require_mapping(value, "response_identity")
    _require_exact_keys(value, _field_names(ResponseIdentity), "response_identity")
    return ResponseIdentity(**dict(value))


def _require_instance(value: object, expected_type: type[object], code: str) -> None:
    if not isinstance(value, expected_type):
        _fail(code, f"expected {expected_type.__name__}")


def _require_identifier(value: object, label: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail("IDENTIFIER_INVALID", f"{label} must be a non-empty trimmed string")


def _require_digest(value: object, label: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _fail("DIGEST_INVALID", f"{label} must be lowercase 64-hex SHA-256")


def _fail(code: str, message: str) -> None:
    raise RunnerIdentityError(code, message)
