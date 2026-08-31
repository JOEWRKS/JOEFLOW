"""Transport-preserving runtime evidence binding for downstream 2.1."""

from __future__ import annotations

import copy
import re
from collections import Counter

from downstream import protocol as frozen_protocol
from downstream_v2.authority import sha256_json

from .contracts import validate_action_contract_v21
from .identity import RUNTIME_EVIDENCE_BUNDLE_VERSION
from .runtime_plan import validate_persisted_runtime_plan


_HASH = re.compile(r"^[0-9a-f]{64}$")
_BUNDLE_KEYS = {
    "bundle_schema_version",
    "source_semantic_contract_hash",
    "source_runtime_plan_hash",
    "source_approved_definition_digest",
    "records",
    "bundle_hash",
}


def _error(path: str, message: str) -> dict[str, str]:
    return {"path": path, "message": message}


def _sorted_errors(errors: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


def _validate_frozen_records(records: object) -> list[dict[str, str]]:
    """Apply the frozen execution/1.0 validator before any 2.1 admission."""
    if not isinstance(records, list):
        return [_error("/records", "records must be an array")]
    errors = []
    for index, record in enumerate(records):
        try:
            frozen_protocol.validate_execution_record(record)
        except frozen_protocol.ProtocolError as exc:
            errors.append(_error(f"/records/{index}", str(exc)))
    return _sorted_errors(errors)


def _require_frozen_records(records: object) -> None:
    if not isinstance(records, list):
        raise ValueError("INVALID_EXECUTION_RECORD")
    for record in records:
        frozen_protocol.validate_execution_record(record)


def _plan_test_ids(plan: object) -> list[str]:
    if not isinstance(plan, dict):
        raise ValueError("INVALID_RUNTIME_PLAN")
    test_ids = []
    try:
        for collection_name in ("actions", "lifecycles"):
            collection = plan[collection_name]
            if not isinstance(collection, list):
                raise ValueError
            for item in collection:
                cases = item["cases"]
                if not isinstance(cases, list):
                    raise ValueError
                for case in cases:
                    test_id = case["test_id"]
                    if not isinstance(test_id, str) or not test_id:
                        raise ValueError
                    test_ids.append(test_id)
    except (KeyError, TypeError, ValueError):
        raise ValueError("INVALID_RUNTIME_PLAN") from None
    if len(test_ids) != len(set(test_ids)):
        raise ValueError("DUPLICATE_RUNTIME_PLAN_TEST_ID")
    return sorted(test_ids)


def _source_input_errors(
    contract: object,
    plan: object,
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> list[dict[str, str]]:
    errors = []
    if not isinstance(contract, dict) or validate_action_contract_v21(contract):
        errors.append(_error("/contract", "INVALID_ACTION_CONTRACT_V21"))
        return errors
    if validate_persisted_runtime_plan(
        plan,
        contract,
        review_package=review_package,
        review_output=review_output,
    ):
        return [_error("/plan", "INVALID_RUNTIME_PLAN")]
    try:
        _plan_test_ids(plan)
    except ValueError as exc:
        errors.append(_error("/plan", str(exc)))
    return _sorted_errors(errors)


def _record_admission_errors(
    records: list[dict[str, object]],
    contract: dict[str, object],
    plan: dict[str, object],
) -> list[dict[str, str]]:
    authority = contract["source_authority"]
    required_ids = set(_plan_test_ids(plan))
    errors = []
    observed_ids = []
    for index, record in enumerate(records):
        path = f"/records/{index}"
        test_id = record["test_id"]
        observed_ids.append(test_id)
        if record["contract_hash"] != contract["semantic_contract_hash"]:
            errors.append(
                _error(f"{path}/contract_hash", "RECORD_CONTRACT_HASH_MISMATCH")
            )
        if (
            record["authority"]["approved_digest"]
            != authority["approved_definition_digest"]
        ):
            errors.append(
                _error(
                    f"{path}/authority/approved_digest",
                    "RECORD_APPROVED_DIGEST_MISMATCH",
                )
            )
        if record["authority"]["approved_revision"] != authority["approved_revision"]:
            errors.append(
                _error(
                    f"{path}/authority/approved_revision",
                    "RECORD_APPROVED_REVISION_MISMATCH",
                )
            )
        if record["product_slug"] != authority["product_slug"]:
            errors.append(
                _error(f"{path}/product_slug", "RECORD_PRODUCT_SLUG_MISMATCH")
            )
        if test_id not in required_ids:
            errors.append(_error(f"{path}/test_id", "UNEXPECTED_RUNTIME_TEST_ID"))

    counts = Counter(observed_ids)
    for test_id in sorted(test_id for test_id, count in counts.items() if count > 1):
        errors.append(_error("/records", f"DUPLICATE_RUNTIME_TEST_ID: {test_id}"))
    missing_ids = sorted(required_ids - set(observed_ids))
    for test_id in missing_ids:
        errors.append(_error("/records", f"MISSING_RUNTIME_TEST_ID: {test_id}"))
    return _sorted_errors(errors)


def _bundle_projection(bundle: dict[str, object]) -> dict[str, object]:
    projection = copy.deepcopy(bundle)
    projection.pop("bundle_hash", None)
    return projection


def build_runtime_evidence_bundle(
    contract: dict[str, object],
    plan: dict[str, object],
    records: list[dict[str, object]],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a complete deterministic bundle over exact execution/1.0 records."""
    _require_frozen_records(records)

    source_errors = _source_input_errors(
        contract,
        plan,
        review_package=review_package,
        review_output=review_output,
    )
    if source_errors:
        raise ValueError(source_errors[0]["message"])

    admission_errors = _record_admission_errors(records, contract, plan)
    if admission_errors:
        record_errors = [
            error
            for error in admission_errors
            if error["path"].startswith("/records/")
        ]
        duplicate_errors = [
            error
            for error in admission_errors
            if error["message"].startswith("DUPLICATE_RUNTIME_TEST_ID")
        ]
        selected = (record_errors or duplicate_errors or admission_errors)[0]
        raise ValueError(selected["message"])

    ordered_records = sorted(copy.deepcopy(records), key=lambda record: record["test_id"])
    bundle = {
        "bundle_schema_version": RUNTIME_EVIDENCE_BUNDLE_VERSION,
        "source_semantic_contract_hash": contract["semantic_contract_hash"],
        "source_runtime_plan_hash": plan["plan_hash"],
        "source_approved_definition_digest": contract["source_authority"][
            "approved_definition_digest"
        ],
        "records": ordered_records,
    }
    bundle["bundle_hash"] = sha256_json(bundle)
    return bundle


def validate_runtime_evidence_bundle(
    bundle: object,
    contract: dict[str, object],
    plan: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> list[dict[str, str]]:
    """Validate transport first, then deterministic 2.1 admission and binding."""
    if not isinstance(bundle, dict):
        return [_error("/", "bundle must be an object")]

    records = bundle.get("records")
    transport_errors = _validate_frozen_records(records)
    if transport_errors:
        return transport_errors

    source_errors = _source_input_errors(
        contract,
        plan,
        review_package=review_package,
        review_output=review_output,
    )
    if source_errors:
        return source_errors

    errors = []
    if set(bundle) != _BUNDLE_KEYS:
        errors.append(_error("/", "bundle has missing or extra fields"))
    if bundle.get("bundle_schema_version") != RUNTIME_EVIDENCE_BUNDLE_VERSION:
        errors.append(
            _error(
                "/bundle_schema_version",
                "UNSUPPORTED_RUNTIME_EVIDENCE_BUNDLE_VERSION",
            )
        )
    if bundle.get("source_semantic_contract_hash") != contract["semantic_contract_hash"]:
        errors.append(
            _error(
                "/source_semantic_contract_hash",
                "SOURCE_SEMANTIC_CONTRACT_HASH_MISMATCH",
            )
        )
    if bundle.get("source_runtime_plan_hash") != plan["plan_hash"]:
        errors.append(
            _error(
                "/source_runtime_plan_hash",
                "SOURCE_RUNTIME_PLAN_HASH_MISMATCH",
            )
        )
    approved_digest = contract["source_authority"]["approved_definition_digest"]
    if bundle.get("source_approved_definition_digest") != approved_digest:
        errors.append(
            _error(
                "/source_approved_definition_digest",
                "SOURCE_APPROVED_DEFINITION_DIGEST_MISMATCH",
            )
        )
    errors.extend(_record_admission_errors(records, contract, plan))

    bundle_hash = bundle.get("bundle_hash")
    if not isinstance(bundle_hash, str) or _HASH.fullmatch(bundle_hash) is None:
        errors.append(_error("/bundle_hash", "INVALID_RUNTIME_EVIDENCE_BUNDLE_HASH"))
    else:
        try:
            if sha256_json(_bundle_projection(bundle)) != bundle_hash:
                errors.append(
                    _error("/bundle_hash", "INVALID_RUNTIME_EVIDENCE_BUNDLE_HASH")
                )
        except (TypeError, ValueError, RecursionError):
            errors.append(_error("/bundle_hash", "INVALID_RUNTIME_EVIDENCE_BUNDLE_HASH"))
    return _sorted_errors(errors)


def runtime_evidence_inventory(
    bundle: dict[str, object],
    plan: dict[str, object],
) -> dict[str, object]:
    """Report exact planned/observed coverage without judging semantic outcomes."""
    records = bundle.get("records") if isinstance(bundle, dict) else None
    _require_frozen_records(records)
    required_ids = _plan_test_ids(plan)
    observed_ids = sorted(
        record["test_id"]
        for record in records
        if isinstance(record, dict)
        and isinstance(record.get("test_id"), str)
        and record["test_id"]
    )
    required_set = set(required_ids)
    observed_set = set(observed_ids)
    missing_ids = sorted(required_set - observed_set)
    unexpected_ids = sorted(observed_set - required_set)
    return {
        "required_test_ids": required_ids,
        "observed_test_ids": observed_ids,
        "missing_test_ids": missing_ids,
        "unexpected_test_ids": unexpected_ids,
        "coverage_status": (
            "COMPLETE" if observed_ids == required_ids else "INCOMPLETE"
        ),
    }


__all__ = [
    "RUNTIME_EVIDENCE_BUNDLE_VERSION",
    "build_runtime_evidence_bundle",
    "runtime_evidence_inventory",
    "validate_runtime_evidence_bundle",
]
