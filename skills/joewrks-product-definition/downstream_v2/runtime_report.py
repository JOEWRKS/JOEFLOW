"""Deterministic aggregate report for V2 implementation conformance."""

from __future__ import annotations

import json
import re
from pathlib import Path

from downstream.protocol import encode_typed_numbers
from downstream.schema_validation import SchemaValidationError, validate_instance

from .runtime import (
    RuntimeVerificationError,
    canonical_runtime_evidence,
    contained_runtime_error_result,
    required_lifecycle_cases,
    semantic_value,
    source_contract_identity,
    verify_action_execution,
    verify_lifecycle_execution,
)


RUNTIME_REPORT_VERSION = "joewrks.runtime-conformance-report/1.0"
_REPORT_SCHEMA = json.loads(
    (Path(__file__).resolve().parent / "schemas" / "runtime-conformance-report.schema.json").read_text(
        encoding="utf-8"
    )
)

_HASH = re.compile(r"^[0-9a-f]{64}$")
_SCOPES = {"FULL_CONTRACT", "PARTIAL_PROBE"}
_DEPENDENCY = {"CONFORMANT", "REENTRY_REQUIRED", "DEFINITION_NOT_READY"}
_REVIEW = {"NOT_REQUIRED", "PENDING", "REVIEW_OUTPUT_RECORDED", "REENTRY_REQUIRED"}
_RESULT_CLASSES = {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"}
_COMPONENTS = {
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
}
_COMPONENT_ORDER = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)
_ASSERTION_RESULT_KEYS = {"type", "pointer", "passed", "observed", "expected"}
_ASSERTION_TYPES = {
    "path_present",
    "path_absent",
    "path_equals",
    "collection_item_field_equals",
}
_INVARIANT_TYPES = {
    "required",
    "finite_number",
    "positive_number",
    "non_negative_number",
    "equals",
}
_LIFECYCLE_FAILURES = {
    "from_state does not match lifecycle case",
    "to_state does not match lifecycle case",
    "allowed verdict does not match lifecycle case",
    "lifecycle boundary conditions failed",
    "object outcome does not match lifecycle authority",
    "actor authority does not match lifecycle authority",
    "required lifecycle reason is absent",
    "required lifecycle confirmation is absent",
    "required lifecycle evidence is absent",
    "lifecycle history preservation is absent",
}


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical(value: object) -> str:
    return json.dumps(
        encode_typed_numbers(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _identity(owner_key: str, owner_id: str, item_key: str, item_id: str) -> dict[str, str]:
    return {owner_key: owner_id, item_key: item_id}


def _failure_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and all(_nonblank(item) for item in value)
        and len(value) == len(set(value))
    )


def _invariant_failure_list(value: object) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, dict)
        and set(item) == {"type", "pointer", "observed"}
        and item.get("type") in _INVARIANT_TYPES
        and isinstance(item.get("pointer"), str)
        for item in value
    )


def _action_result_semantically_consistent(result: dict[str, object]) -> bool:
    expected = result["expected_result"]
    observed = result["observed_result"]
    result_matches = expected == observed
    if result["result_matches"] is not result_matches:
        return False
    if result["input_invariant_failures"] and expected != "REJECTED":
        return False
    components = result["components"]
    for component in _COMPONENT_ORDER:
        item = components[component]
        should_pass = (
            item["expectation"] == "ANY"
            or (item["expectation"] == "CHANGED" and item["changed"] is True)
            or (item["expectation"] == "UNCHANGED" and item["changed"] is False)
        )
        if item["passed"] is not should_pass:
            return False
    assertions = result["assertions"]
    if any(
        not isinstance(assertion, dict)
        or set(assertion) != _ASSERTION_RESULT_KEYS
        or assertion.get("type") not in _ASSERTION_TYPES
        or not isinstance(assertion.get("pointer"), str)
        or type(assertion.get("passed")) is not bool
        for assertion in assertions
    ):
        return False
    expected_failures = []
    if not result_matches:
        expected_failures.append(f"expected {expected}, observed {observed}")
    expected_failures.extend(
        f"{component} expected {components[component]['expectation']}"
        for component in _COMPONENT_ORDER
        if not components[component]["passed"]
    )
    expected_failures.extend(
        f"evidence assertion failed: {assertion['type']} {assertion['pointer']}"
        for assertion in assertions
        if not assertion["passed"]
    )
    expected_conformant = (
        result_matches
        and all(components[component]["passed"] for component in _COMPONENT_ORDER)
        and all(assertion["passed"] for assertion in assertions)
    )
    return (
        result["failures"] == expected_failures
        and result["conformant"] is expected_conformant
    )


def _lifecycle_result_semantically_consistent(result: dict[str, object]) -> bool:
    failures = result["failures"]
    if not _failure_list(failures) or any(failure not in _LIFECYCLE_FAILURES for failure in failures):
        return False
    verdict_failure = "allowed verdict does not match lifecycle case"
    boundary_failure = "lifecycle boundary conditions failed"
    if (verdict_failure in failures) is not (
        result["expected_allowed"] is not result["observed_allowed"]
    ):
        return False
    if (boundary_failure in failures) is not bool(result["boundary_failures"]):
        return False
    return result["conformant"] is (not failures)


def _required_actions(
    contract: dict[str, object],
    errors: list[dict[str, object]],
) -> list[dict[str, str]]:
    actions = contract.get("actions") if isinstance(contract, dict) else None
    if not isinstance(actions, list):
        errors.append({"code": "RUNTIME_CONTRACT_NOT_EXECUTABLE", "detail": "actions must be an array"})
        return []
    seen_actions = set()
    inventory = []
    for index, action in enumerate(actions):
        action_id = action.get("action_id") if isinstance(action, dict) else None
        if not _nonblank(action_id):
            errors.append({
                "code": "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                "detail": f"actions/{index} requires a nonblank action_id",
            })
            continue
        if action_id in seen_actions:
            errors.append({"code": "RUNTIME_DUPLICATE_ACTION_ID", "detail": {"action_id": action_id}})
            continue
        seen_actions.add(action_id)
        fields = action.get("fields")
        try:
            obligations = semantic_value(fields["test_obligations"])
        except (KeyError, TypeError, RuntimeVerificationError) as error:
            errors.append({
                "code": "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                "detail": f"{action_id} test_obligations: {getattr(error, 'detail', str(error))}",
            })
            continue
        if (
            not isinstance(obligations, list)
            or not obligations
            or any(not _nonblank(value) for value in obligations)
            or len(obligations) != len(set(obligations))
        ):
            errors.append({
                "code": "RUNTIME_CONTRACT_NOT_EXECUTABLE",
                "detail": f"{action_id} test_obligations must be nonempty unique strings",
            })
            continue
        inventory.extend(
            _identity("action_id", action_id, "test_id", test_id)
            for test_id in obligations
        )
    return sorted(inventory, key=lambda item: (item["action_id"], item["test_id"]))


def _deduplicate_results(
    results: object,
    *,
    owner_key: str,
    item_key: str,
    result_kind: str,
    contract: dict[str, object],
    expected_source_contract: dict[str, object] | None,
) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    errors = []
    if not isinstance(results, list):
        return [], [{"code": "RUNTIME_EVIDENCE_INVALID", "detail": f"{result_kind} results must be an array"}], 0
    by_key: dict[tuple[str, str], dict[str, object]] = {}
    deduplicated = 0
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            errors.append({"code": "RUNTIME_EVIDENCE_INVALID", "detail": f"{result_kind}/{index} must be an object"})
            continue
        owner_id = result.get(owner_key)
        item_id = result.get(item_key)
        evidence_hash = result.get("evidence_sha256")
        if (
            not _nonblank(owner_id)
            or not _nonblank(item_id)
            or not isinstance(evidence_hash, str)
            or _HASH.fullmatch(evidence_hash) is None
            or type(result.get("conformant")) is not bool
        ):
            errors.append({"code": "RUNTIME_EVIDENCE_INVALID", "detail": f"{result_kind}/{index} identity is malformed"})
            continue
        observed_source_contract = result.get("source_contract")
        source_contract_matches = (
            expected_source_contract is not None
            and isinstance(observed_source_contract, dict)
            and set(observed_source_contract) == set(expected_source_contract)
            and all(
                type(observed_source_contract[key]) is type(expected_source_contract[key])
                and observed_source_contract[key] == expected_source_contract[key]
                for key in expected_source_contract
            )
        )
        if not source_contract_matches:
            errors.append({
                "code": "RUNTIME_EVIDENCE_INVALID",
                "detail": f"{result_kind}/{index} source_contract identity does not match contract",
            })
            continue
        runtime_evidence = result.get("runtime_evidence")
        try:
            if result_kind == "actions":
                canonical_result = verify_action_execution(contract, runtime_evidence)
            else:
                canonical_result = verify_lifecycle_execution(contract, runtime_evidence)
        except RuntimeVerificationError as error:
            try:
                canonical_result = contained_runtime_error_result(
                    contract,
                    runtime_evidence,
                    error,
                    lifecycle=result_kind == "lifecycles",
                )
            except RuntimeVerificationError:
                errors.append({
                    "code": "RUNTIME_EVIDENCE_INVALID",
                    "detail": f"{result_kind}/{index} runtime evidence is not canonical",
                })
                continue
        except (KeyError, TypeError, ValueError, AttributeError, RecursionError):
            errors.append({
                "code": "RUNTIME_EVIDENCE_INVALID",
                "detail": f"{result_kind}/{index} runtime evidence could not be verified",
            })
            continue
        try:
            exact_result = _canonical(canonical_result) == _canonical(result)
        except (TypeError, ValueError, RecursionError):
            exact_result = False
        if not exact_result:
            errors.append({
                "code": "RUNTIME_EVIDENCE_INVALID",
                "detail": f"{result_kind}/{index} verifier result does not match runtime evidence",
            })
            continue
        common_error_keys = {"source_contract", owner_key, item_key, "test_id", "evidence_sha256", "runtime_evidence", "failures", "error", "conformant"}
        if result_kind == "actions":
            valid_keys = {
                "source_contract", "action_id", "test_id", "evidence_sha256", "expected_result",
                "observed_result", "result_matches", "input_invariant_failures",
                "components", "assertions", "runtime_evidence", "failures", "conformant",
            }
            components = result.get("components")
            valid_detail = (
                set(result) == valid_keys
                and result.get("expected_result") in _RESULT_CLASSES
                and result.get("observed_result") in _RESULT_CLASSES
                and type(result.get("result_matches")) is bool
                and _invariant_failure_list(result.get("input_invariant_failures"))
                and isinstance(components, dict)
                and set(components) == _COMPONENTS
                and all(
                    isinstance(value, dict)
                    and set(value) == {"expectation", "changed", "passed"}
                    and value.get("expectation") in {"CHANGED", "UNCHANGED", "ANY"}
                    and type(value.get("changed")) is bool
                    and type(value.get("passed")) is bool
                    for value in components.values()
                )
                and isinstance(result.get("assertions"), list)
                and _failure_list(result.get("failures"))
            )
            semantic_consistent = valid_detail and _action_result_semantically_consistent(result)
        else:
            valid_keys = {
                "source_contract", "lifecycle_id", "case_id", "test_id", "evidence_sha256",
                "expected_allowed", "observed_allowed", "boundary_failures",
                "runtime_evidence", "failures", "conformant",
            }
            valid_detail = (
                set(result) == valid_keys
                and type(result.get("expected_allowed")) is bool
                and type(result.get("observed_allowed")) is bool
                and _invariant_failure_list(result.get("boundary_failures"))
                and _failure_list(result.get("failures"))
            )
            semantic_consistent = valid_detail and _lifecycle_result_semantically_consistent(result)
        if set(result) == common_error_keys:
            error = result.get("error")
            valid_detail = (
                result.get("conformant") is False
                and _failure_list(result.get("failures"))
                and isinstance(error, dict)
                and set(error) == {"code", "detail"}
                and _nonblank(error.get("code"))
            )
            semantic_consistent = valid_detail and result.get("failures") == [error.get("code")]
        if not valid_detail:
            errors.append({"code": "RUNTIME_EVIDENCE_INVALID", "detail": f"{result_kind}/{index} verifier result is malformed"})
            continue
        if not semantic_consistent:
            errors.append({
                "code": "RUNTIME_EVIDENCE_INVALID",
                "detail": f"{result_kind}/{index} verifier result is semantically inconsistent",
            })
            continue
        key = (owner_id, item_id)
        previous = by_key.get(key)
        if previous is None:
            by_key[key] = result
            continue
        if _canonical(previous) == _canonical(result):
            deduplicated += 1
        else:
            errors.append({
                "code": "RUNTIME_CONFLICTING_DUPLICATE_EVIDENCE",
                "detail": {owner_key: owner_id, item_key: item_id},
            })
    ordered = [by_key[key] for key in sorted(by_key)]
    return ordered, errors, deduplicated


def _inventory(
    results: list[dict[str, object]],
    *,
    owner_key: str,
    item_key: str,
) -> list[dict[str, str]]:
    return [
        _identity(owner_key, result[owner_key], item_key, result[item_key])
        for result in results
        if "error" not in result
    ]


def _difference(
    left: list[dict[str, str]],
    right: list[dict[str, str]],
    *,
    owner_key: str,
    item_key: str,
) -> list[dict[str, str]]:
    right_keys = {(item[owner_key], item[item_key]) for item in right}
    return [
        item
        for item in left
        if (item[owner_key], item[item_key]) not in right_keys
    ]


def build_runtime_conformance_report(
    contract: dict[str, object],
    audit_result: dict[str, object],
    action_results: list[dict[str, object]],
    lifecycle_results: list[dict[str, object]],
    semantic_assurance: dict[str, object],
) -> dict[str, object]:
    """Build a full-contract or partial-probe report without broadening its claim."""
    report_inputs = canonical_runtime_evidence({
        "audit_result": audit_result,
        "action_results": action_results,
        "lifecycle_results": lifecycle_results,
        "semantic_assurance": semantic_assurance,
    })
    assert isinstance(report_inputs, dict)
    audit_result = report_inputs["audit_result"]
    action_results = report_inputs["action_results"]
    lifecycle_results = report_inputs["lifecycle_results"]
    semantic_assurance = report_inputs["semantic_assurance"]
    action_execution_errors: list[dict[str, object]] = []
    try:
        expected_source_contract = source_contract_identity(contract)
    except RuntimeVerificationError as error:
        action_execution_errors.append({"code": error.code, "detail": error.detail})
        expected_source_contract = None
    required_actions = _required_actions(contract, action_execution_errors)
    actions, action_errors, action_deduplicated = _deduplicate_results(
        action_results,
        owner_key="action_id",
        item_key="test_id",
        result_kind="actions",
        contract=contract,
        expected_source_contract=expected_source_contract,
    )
    observed_actions = _inventory(actions, owner_key="action_id", item_key="test_id")
    missing_actions = _difference(
        required_actions,
        observed_actions,
        owner_key="action_id",
        item_key="test_id",
    )
    unexpected_actions = _difference(
        observed_actions,
        required_actions,
        owner_key="action_id",
        item_key="test_id",
    )
    action_coverage = (
        "COMPLETE"
        if not action_execution_errors and not action_errors and not missing_actions and not unexpected_actions
        else "INCOMPLETE"
    )

    lifecycles = contract.get("lifecycles") if isinstance(contract, dict) else None
    lifecycle_applicability = "NOT_APPLICABLE" if lifecycles == [] else "APPLICABLE"
    lifecycle_execution_errors: list[dict[str, object]] = []
    try:
        required_lifecycles = required_lifecycle_cases(contract)
    except RuntimeVerificationError as error:
        lifecycle_execution_errors.append({"code": error.code, "detail": error.detail})
        required_lifecycles = []
    lifecycle_items, lifecycle_errors, lifecycle_deduplicated = _deduplicate_results(
        lifecycle_results,
        owner_key="lifecycle_id",
        item_key="case_id",
        result_kind="lifecycles",
        contract=contract,
        expected_source_contract=expected_source_contract,
    )
    observed_lifecycles = _inventory(
        lifecycle_items,
        owner_key="lifecycle_id",
        item_key="case_id",
    )
    missing_lifecycles = _difference(
        required_lifecycles,
        observed_lifecycles,
        owner_key="lifecycle_id",
        item_key="case_id",
    )
    unexpected_lifecycles = _difference(
        observed_lifecycles,
        required_lifecycles,
        owner_key="lifecycle_id",
        item_key="case_id",
    )
    lifecycle_coverage = (
        "COMPLETE"
        if not lifecycle_execution_errors and not lifecycle_errors and not missing_lifecycles and not unexpected_lifecycles
        else "INCOMPLETE"
    )
    coverage = (
        "COMPLETE"
        if action_coverage == "COMPLETE" and lifecycle_coverage == "COMPLETE"
        else "INCOMPLETE"
    )

    evidence_errors = sorted(
        action_errors + lifecycle_errors,
        key=lambda error: (error["code"], _canonical(error["detail"])),
    )
    execution_errors = sorted(
        action_execution_errors + lifecycle_execution_errors,
        key=lambda error: (error["code"], _canonical(error["detail"])),
    )
    supplied_count = len(actions) + len(lifecycle_items)
    any_failure = any(not item["conformant"] for item in actions + lifecycle_items)
    if evidence_errors or unexpected_actions or unexpected_lifecycles or any_failure:
        runtime_status = "NON_CONFORMANT"
    elif supplied_count == 0:
        runtime_status = "NOT_RUN"
    else:
        runtime_status = "CONFORMANT"

    audit_status = audit_result.get("status") if isinstance(audit_result, dict) else None
    dependency_status = audit_status if audit_status in _DEPENDENCY else "DEFINITION_NOT_READY"
    blocking_events = (
        audit_result.get("reentry_events", [])
        if isinstance(audit_result, dict) and isinstance(audit_result.get("reentry_events"), list)
        else []
    )
    if dependency_status != "REENTRY_REQUIRED":
        blocking_events = []

    assurance = semantic_assurance if isinstance(semantic_assurance, dict) else {}
    verification_scope = assurance.get("verification_scope")
    if verification_scope not in _SCOPES:
        verification_scope = "PARTIAL_PROBE"
        execution_errors.append({
            "code": "INVALID_VERIFICATION_SCOPE",
            "detail": "verification_scope must be explicitly FULL_CONTRACT or PARTIAL_PROBE",
        })
    review_completion = assurance.get("review_completion")
    if review_completion not in _REVIEW:
        review_completion = "PENDING"
        execution_errors.append({
            "code": "INVALID_SEMANTIC_ASSURANCE",
            "detail": "review_completion is invalid",
        })
    if review_completion == "NOT_REQUIRED":
        review_reliability = "NOT_REQUIRED"
    else:
        review_reliability = "NOT_MEASURED"
        if assurance.get("reliability_status") != "NOT_MEASURED":
            execution_errors.append({
                "code": "INVALID_SEMANTIC_ASSURANCE",
                "detail": "semantic-review/2.0 reliability must remain NOT_MEASURED",
            })
    review_complete = review_completion in {"NOT_REQUIRED", "REVIEW_OUTPUT_RECORDED"}

    implementation_conformant = (
        verification_scope == "FULL_CONTRACT"
        and coverage == "COMPLETE"
        and action_coverage == "COMPLETE"
        and lifecycle_coverage == "COMPLETE"
        and dependency_status == "CONFORMANT"
        and runtime_status == "CONFORMANT"
        and not blocking_events
        and review_complete
        and not execution_errors
        and not evidence_errors
    )
    authority = contract.get("source_authority") if isinstance(contract, dict) else {}
    source_contract = expected_source_contract or {
        "contract_schema_version": contract.get("contract_schema_version") if isinstance(contract, dict) else None,
        "semantic_contract_hash": contract.get("semantic_contract_hash") if isinstance(contract, dict) else None,
        "product_slug": authority.get("product_slug") if isinstance(authority, dict) else None,
        "approved_revision": authority.get("approved_revision") if isinstance(authority, dict) else None,
        "approved_definition_digest": authority.get("approved_definition_digest") if isinstance(authority, dict) else None,
    }
    return {
        "report_schema_version": RUNTIME_REPORT_VERSION,
        "report_inputs": report_inputs,
        "source_contract": source_contract,
        "verification_scope": verification_scope,
        "contract_dependency_status": dependency_status,
        "runtime_status": runtime_status,
        "review_completion": review_completion,
        "semantic_review_reliability": review_reliability,
        "implementation_status": (
            "IMPLEMENTATION_CONFORMANT"
            if implementation_conformant
            else "IMPLEMENTATION_NOT_CONFORMANT"
        ),
        "coverage_status": coverage,
        "action_coverage_status": action_coverage,
        "lifecycle_coverage_status": lifecycle_coverage,
        "lifecycle_applicability": lifecycle_applicability,
        "required_action_test_ids": required_actions,
        "observed_action_test_ids": observed_actions,
        "missing_action_test_ids": missing_actions,
        "unexpected_action_test_ids": unexpected_actions,
        "required_lifecycle_case_ids": required_lifecycles,
        "observed_lifecycle_case_ids": observed_lifecycles,
        "missing_lifecycle_case_ids": missing_lifecycles,
        "unexpected_lifecycle_case_ids": unexpected_lifecycles,
        "action_results": actions,
        "lifecycle_results": lifecycle_items,
        "blocking_reentry_events": blocking_events,
        "contract_execution_errors": execution_errors,
        "evidence_errors": evidence_errors,
        "deduplicated_evidence_count": action_deduplicated + lifecycle_deduplicated,
    }


def _runtime_report_invalid(detail: object) -> RuntimeVerificationError:
    return RuntimeVerificationError("RUNTIME_REPORT_INVALID", detail)


def _ordered_unique_inventory(
    inventory: list[dict[str, str]],
    *,
    owner_key: str,
    item_key: str,
) -> bool:
    keys = [(item[owner_key], item[item_key]) for item in inventory]
    return keys == sorted(keys) and len(keys) == len(set(keys))


def validate_runtime_conformance_report(
    report: dict[str, object],
    contract: dict[str, object],
) -> None:
    """Totally validate schema, result semantics, inventories, and aggregate gates."""
    try:
        _canonical(report)
        validate_instance(report, _REPORT_SCHEMA)
    except (SchemaValidationError, TypeError, ValueError, RecursionError) as error:
        raise _runtime_report_invalid(str(error)) from error

    inputs = report["report_inputs"]
    try:
        expected_report = build_runtime_conformance_report(
            contract,
            inputs["audit_result"],
            inputs["action_results"],
            inputs["lifecycle_results"],
            inputs["semantic_assurance"],
        )
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
        raise _runtime_report_invalid("preserved report inputs are invalid") from error
    if _canonical(report) != _canonical(expected_report):
        raise _runtime_report_invalid(
            "report does not exactly match its preserved bounded inputs"
        )

    try:
        expected_source_contract = source_contract_identity(contract)
    except RuntimeVerificationError as error:
        raise _runtime_report_invalid(error.detail) from error
    source_contract = report["source_contract"]
    if (
        not isinstance(source_contract, dict)
        or set(source_contract) != set(expected_source_contract)
        or any(
            type(source_contract[key]) is not type(expected_source_contract[key])
            or source_contract[key] != expected_source_contract[key]
            for key in expected_source_contract
        )
    ):
        raise _runtime_report_invalid("source contract does not match supplied contract")
    inventory_errors: list[dict[str, object]] = []
    expected_required_actions = _required_actions(contract, inventory_errors)
    try:
        expected_required_lifecycles = required_lifecycle_cases(contract)
    except RuntimeVerificationError as error:
        inventory_errors.append({"code": error.code, "detail": error.detail})
        expected_required_lifecycles = []
    if report["required_action_test_ids"] != expected_required_actions:
        raise _runtime_report_invalid("required action inventory does not match supplied contract")
    if report["required_lifecycle_case_ids"] != expected_required_lifecycles:
        raise _runtime_report_invalid("required lifecycle inventory does not match supplied contract")
    action_results, action_errors, action_duplicates = _deduplicate_results(
        report["action_results"],
        owner_key="action_id",
        item_key="test_id",
        result_kind="actions",
        contract=contract,
        expected_source_contract=expected_source_contract,
    )
    lifecycle_results, lifecycle_errors, lifecycle_duplicates = _deduplicate_results(
        report["lifecycle_results"],
        owner_key="lifecycle_id",
        item_key="case_id",
        result_kind="lifecycles",
        contract=contract,
        expected_source_contract=expected_source_contract,
    )
    if action_errors or lifecycle_errors or action_duplicates or lifecycle_duplicates:
        raise _runtime_report_invalid("runtime result objects are invalid or duplicated")

    inventories = (
        ("required_action_test_ids", "action_id", "test_id"),
        ("observed_action_test_ids", "action_id", "test_id"),
        ("missing_action_test_ids", "action_id", "test_id"),
        ("unexpected_action_test_ids", "action_id", "test_id"),
        ("required_lifecycle_case_ids", "lifecycle_id", "case_id"),
        ("observed_lifecycle_case_ids", "lifecycle_id", "case_id"),
        ("missing_lifecycle_case_ids", "lifecycle_id", "case_id"),
        ("unexpected_lifecycle_case_ids", "lifecycle_id", "case_id"),
    )
    for field_name, owner_key, item_key in inventories:
        if not _ordered_unique_inventory(
            report[field_name],
            owner_key=owner_key,
            item_key=item_key,
        ):
            raise _runtime_report_invalid(f"{field_name} must be sorted and unique")

    observed_actions = _inventory(action_results, owner_key="action_id", item_key="test_id")
    observed_lifecycles = _inventory(
        lifecycle_results,
        owner_key="lifecycle_id",
        item_key="case_id",
    )
    if report["observed_action_test_ids"] != observed_actions:
        raise _runtime_report_invalid("observed action inventory does not match action results")
    if report["observed_lifecycle_case_ids"] != observed_lifecycles:
        raise _runtime_report_invalid("observed lifecycle inventory does not match lifecycle results")

    expected_missing_actions = _difference(
        report["required_action_test_ids"],
        observed_actions,
        owner_key="action_id",
        item_key="test_id",
    )
    expected_unexpected_actions = _difference(
        observed_actions,
        report["required_action_test_ids"],
        owner_key="action_id",
        item_key="test_id",
    )
    expected_missing_lifecycles = _difference(
        report["required_lifecycle_case_ids"],
        observed_lifecycles,
        owner_key="lifecycle_id",
        item_key="case_id",
    )
    expected_unexpected_lifecycles = _difference(
        observed_lifecycles,
        report["required_lifecycle_case_ids"],
        owner_key="lifecycle_id",
        item_key="case_id",
    )
    difference_fields = (
        ("missing_action_test_ids", expected_missing_actions),
        ("unexpected_action_test_ids", expected_unexpected_actions),
        ("missing_lifecycle_case_ids", expected_missing_lifecycles),
        ("unexpected_lifecycle_case_ids", expected_unexpected_lifecycles),
    )
    if any(report[field_name] != expected for field_name, expected in difference_fields):
        raise _runtime_report_invalid("reported coverage inventories are inconsistent")

    action_gaps = bool(expected_missing_actions or expected_unexpected_actions)
    lifecycle_gaps = bool(expected_missing_lifecycles or expected_unexpected_lifecycles)
    if report["action_coverage_status"] == "COMPLETE" and action_gaps:
        raise _runtime_report_invalid("complete action coverage has inventory gaps")
    if report["lifecycle_coverage_status"] == "COMPLETE" and lifecycle_gaps:
        raise _runtime_report_invalid("complete lifecycle coverage has inventory gaps")
    if (
        report["action_coverage_status"] == "INCOMPLETE"
        and not action_gaps
        and not report["contract_execution_errors"]
        and not report["evidence_errors"]
    ):
        raise _runtime_report_invalid("incomplete action coverage has no blocking gap or error")
    if (
        report["lifecycle_coverage_status"] == "INCOMPLETE"
        and not lifecycle_gaps
        and not report["contract_execution_errors"]
        and not report["evidence_errors"]
    ):
        raise _runtime_report_invalid("incomplete lifecycle coverage has no blocking gap or error")
    expected_coverage = (
        "COMPLETE"
        if report["action_coverage_status"] == "COMPLETE"
        and report["lifecycle_coverage_status"] == "COMPLETE"
        else "INCOMPLETE"
    )
    if report["coverage_status"] != expected_coverage:
        raise _runtime_report_invalid("coverage status contradicts coverage dimensions")
    if report["required_lifecycle_case_ids"]:
        if report["lifecycle_applicability"] != "APPLICABLE":
            raise _runtime_report_invalid("lifecycle cases require APPLICABLE")
    elif (
        not report["contract_execution_errors"]
        and report["lifecycle_coverage_status"] == "COMPLETE"
        and report["lifecycle_applicability"] != "NOT_APPLICABLE"
    ):
        raise _runtime_report_invalid("an exact empty lifecycle inventory is NOT_APPLICABLE")

    any_failure = any(
        not result["conformant"] for result in action_results + lifecycle_results
    )
    if (
        report["evidence_errors"]
        or expected_unexpected_actions
        or expected_unexpected_lifecycles
        or any_failure
    ):
        expected_runtime_status = "NON_CONFORMANT"
    elif not action_results and not lifecycle_results:
        expected_runtime_status = "NOT_RUN"
    else:
        expected_runtime_status = "CONFORMANT"
    if report["runtime_status"] != expected_runtime_status:
        raise _runtime_report_invalid("runtime status contradicts supplied evidence")

    expected_reliability = (
        "NOT_REQUIRED"
        if report["review_completion"] == "NOT_REQUIRED"
        else "NOT_MEASURED"
    )
    if report["semantic_review_reliability"] != expected_reliability:
        raise _runtime_report_invalid("semantic review reliability contradicts review completion")
    if (
        report["contract_dependency_status"] != "REENTRY_REQUIRED"
        and report["blocking_reentry_events"]
    ):
        raise _runtime_report_invalid("blocking re-entry events require REENTRY_REQUIRED")

    review_complete = report["review_completion"] in {
        "NOT_REQUIRED",
        "REVIEW_OUTPUT_RECORDED",
    }
    implementation_conformant = (
        report["verification_scope"] == "FULL_CONTRACT"
        and report["coverage_status"] == "COMPLETE"
        and report["action_coverage_status"] == "COMPLETE"
        and report["lifecycle_coverage_status"] == "COMPLETE"
        and report["contract_dependency_status"] == "CONFORMANT"
        and report["runtime_status"] == "CONFORMANT"
        and not report["blocking_reentry_events"]
        and review_complete
        and not report["contract_execution_errors"]
        and not report["evidence_errors"]
    )
    expected_implementation = (
        "IMPLEMENTATION_CONFORMANT"
        if implementation_conformant
        else "IMPLEMENTATION_NOT_CONFORMANT"
    )
    if report["implementation_status"] != expected_implementation:
        raise _runtime_report_invalid("implementation status contradicts global conformance gates")
