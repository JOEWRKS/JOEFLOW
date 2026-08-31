"""Independent plan-bound verification for action-conformance/2.1 dogfood.

Admission by the frozen execution/1.0 bundle is necessary but not sufficient.
This verifier binds each test ID to one action case, reruns the deterministic
local action scenario, evaluates every planned relationship, and builds the
versioned aggregate report used by the installed wrapper.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from urllib.parse import unquote

from downstream.schema_validation import SchemaValidationError, validate_instance
from downstream_v2.authority import sha256_json
from downstream_v21.contracts import validate_action_contract_v21
from downstream_v21.runtime_evidence import (
    runtime_evidence_inventory,
    validate_runtime_evidence_bundle,
)
from downstream_v21.runtime_plan import validate_persisted_runtime_plan

from .client_feedback_portal_fixture import execute_fixture_scenario


REPORT_VERSION = "joewrks.runtime-conformance-report/1.0"
_REPORT_SCHEMA = json.loads(
    (
        Path(__file__).resolve().parent
        / "schemas"
        / "runtime-conformance-report.schema.json"
    ).read_text(encoding="utf-8")
)
_COMPONENTS = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)
_RESULT_CLASSES = {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"}
_SCOPES = {"FULL_CONTRACT", "PARTIAL_PROBE"}


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _pointer(value: object, pointer: str) -> object:
    if pointer == "":
        return value
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("INVALID_RUNTIME_ASSERTION_POINTER")
    current = value
    for raw_part in pointer[1:].split("/"):
        token = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif (
            isinstance(current, list)
            and token.isdecimal()
            and int(token) < len(current)
        ):
            current = current[int(token)]
        else:
            raise ValueError("RUNTIME_ASSERTION_POINTER_MISSING")
    return current


def _source_contract(contract: dict[str, object]) -> dict[str, object]:
    authority = contract.get("source_authority", {})
    return {
        "contract_schema_version": contract.get("contract_schema_version"),
        "semantic_contract_hash": contract.get("semantic_contract_hash"),
        "product_slug": authority.get("product_slug"),
        "approved_revision": authority.get("approved_revision"),
        "approved_definition_digest": authority.get("approved_definition_digest"),
    }


def _contract_expected_value(
    contract: dict[str, object],
    source: dict[str, object],
) -> object:
    source_kind = source.get("source")
    if source_kind == "CONTRACT_DERIVED":
        field_path = source.get("contract_field_path")
        if not isinstance(field_path, str):
            raise ValueError("INVALID_EXPECTED_VALUE_SOURCE")
        parts = field_path.split("/", 2)
        if len(parts) != 3 or parts[0] not in {"actions", "lifecycles"}:
            raise ValueError("INVALID_EXPECTED_VALUE_SOURCE")
        collection, encoded_item_id, field_name = parts
        id_key = "action_id" if collection == "actions" else "lifecycle_id"
        item_id = unquote(encoded_item_id)
        item = next(
            (
                candidate
                for candidate in contract[collection]
                if candidate[id_key] == item_id
            ),
            None,
        )
        if item is None or field_name not in item["fields"]:
            raise ValueError("INVALID_EXPECTED_VALUE_SOURCE")
        return copy.deepcopy(_pointer(item["fields"][field_name], source["pointer"]))
    if source_kind == "VERIFICATION_BASIS":
        seed_ref = source.get("seed_ref")
        seed = next(
            (
                candidate
                for candidate in contract.get("source_seed_inventory", [])
                if candidate.get("seed_key") == seed_ref
            ),
            None,
        )
        if seed is None:
            raise ValueError("INVALID_EXPECTED_VALUE_SOURCE")
        return copy.deepcopy(_pointer(seed, source["pointer"]))
    raise ValueError("INVALID_EXPECTED_VALUE_SOURCE")


def _assertion_results(
    contract: dict[str, object],
    record: dict[str, object],
    assertions: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[str]]:
    results = []
    failures = []
    for assertion in assertions:
        pointer = assertion["pointer"]
        try:
            observed = _pointer(record, pointer)
        except ValueError:
            observed = None
            present = False
        else:
            present = True
        kind = assertion["type"]
        if kind == "path_present":
            expected = True
            passed = present
        elif kind == "path_absent":
            expected = False
            passed = not present
        else:
            try:
                expected = _contract_expected_value(
                    contract,
                    assertion["expected_value_source"],
                )
            except (KeyError, TypeError, ValueError):
                expected = None
                passed = False
            else:
                if kind == "path_equals":
                    passed = present and observed == expected
                elif kind == "collection_item_field_equals":
                    passed = present and isinstance(observed, list) and expected in observed
                else:
                    passed = False
        results.append({
            "type": kind,
            "pointer": pointer,
            "passed": passed,
            "observed": copy.deepcopy(observed),
            "expected": copy.deepcopy(expected),
        })
        if not passed:
            failures.append(f"evidence assertion failed: {kind} {pointer}")
    return results, failures


def _component_results(
    record: dict[str, object],
    case: dict[str, object],
) -> tuple[dict[str, dict[str, object]], list[str]]:
    planned = {
        expectation["component"]: expectation["expectation"]
        for expectation in case.get("component_expectations", [])
    }
    results = {}
    failures = []
    for component in _COMPONENTS:
        expectation = planned.get(component, "ANY")
        changed = record["before"][component] != record["after"][component]
        passed = (
            expectation == "ANY"
            or (expectation == "CHANGED" and changed)
            or (expectation == "UNCHANGED" and not changed)
        )
        results[component] = {
            "expectation": expectation,
            "changed": changed,
            "passed": passed,
        }
        if not passed:
            failures.append(f"{component} expected {expectation}")
    return results, failures


def _error_result(
    source_contract: dict[str, object],
    action_id: str,
    record: dict[str, object],
    code: str,
    detail: object,
) -> dict[str, object]:
    return {
        "source_contract": copy.deepcopy(source_contract),
        "action_id": action_id,
        "test_id": str(record.get("test_id", "UNKNOWN_TEST_ID")),
        "evidence_sha256": sha256_json(record),
        "runtime_evidence": copy.deepcopy(record),
        "failures": [code],
        "error": {"code": code, "detail": copy.deepcopy(detail)},
        "conformant": False,
    }


def _verify_action_record(
    contract: dict[str, object],
    source_contract: dict[str, object],
    action_id: str,
    case: dict[str, object],
    record: dict[str, object],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    errors: list[dict[str, object]] = []
    expected_result = case["result_expectation"]["result_class"]
    result = record.get("result")
    observed_result = result.get("result_class") if isinstance(result, dict) else None
    if observed_result not in _RESULT_CLASSES:
        code = "RUNTIME_RESULT_CLASS_INVALID"
        errors.append({"code": code, "detail": {"action_id": action_id, "test_id": record.get("test_id")}})
        return _error_result(source_contract, action_id, record, code, observed_result), errors

    failures = []
    command_action = record.get("command", {}).get("action_id") if isinstance(record.get("command"), dict) else None
    if command_action != action_id:
        failures.append("runtime action binding mismatch")
        errors.append({
            "code": "RUNTIME_ACTION_BINDING_MISMATCH",
            "detail": {
                "test_id": record.get("test_id"),
                "expected_action_id": action_id,
                "observed_action_id": command_action,
            },
        })
    result_matches = observed_result == expected_result
    if not result_matches:
        failures.append(f"expected {expected_result}, observed {observed_result}")

    components, component_failures = _component_results(record, case)
    failures.extend(component_failures)
    assertions, assertion_failures = _assertion_results(
        contract,
        record,
        case.get("evidence_assertions", []),
    )
    failures.extend(assertion_failures)

    expected_execution = execute_fixture_scenario(
        contract,
        action_id,
        expected_result,
    )
    observed_execution = {
        key: copy.deepcopy(record.get(key))
        for key in ("command", "before", "result", "after", "deltas")
    }
    if _canonical(observed_execution) != _canonical(expected_execution):
        failures.append("runtime fixture execution mismatch")
        errors.append({
            "code": "RUNTIME_FIXTURE_EXECUTION_MISMATCH",
            "detail": {"action_id": action_id, "test_id": record.get("test_id")},
        })

    failures = list(dict.fromkeys(failures))
    verified = {
        "source_contract": copy.deepcopy(source_contract),
        "action_id": action_id,
        "test_id": record["test_id"],
        "evidence_sha256": sha256_json(record),
        "runtime_evidence": copy.deepcopy(record),
        "expected_result": expected_result,
        "observed_result": observed_result,
        "result_matches": result_matches,
        "input_invariant_failures": [],
        "components": components,
        "assertions": assertions,
        "failures": failures,
        "conformant": not failures,
    }
    return verified, errors


def _case_indexes(plan: dict[str, object]):
    actions: dict[str, tuple[str, dict[str, object]]] = {}
    lifecycles: dict[str, tuple[str, dict[str, object]]] = {}
    duplicates = []
    for item in plan.get("actions", []):
        for case in item.get("cases", []):
            test_id = case.get("test_id")
            if test_id in actions or test_id in lifecycles:
                duplicates.append(test_id)
            actions[test_id] = (item.get("action_id"), case)
    for item in plan.get("lifecycles", []):
        for case in item.get("cases", []):
            test_id = case.get("test_id")
            if test_id in actions or test_id in lifecycles:
                duplicates.append(test_id)
            lifecycles[test_id] = (item.get("lifecycle_id"), case)
    return actions, lifecycles, sorted(set(duplicates))


def _action_inventory(
    test_ids: list[str],
    action_cases: dict[str, tuple[str, dict[str, object]]],
    record_actions: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    record_actions = {} if record_actions is None else record_actions
    return sorted(
        [
            {
                "action_id": (
                    action_cases[test_id][0]
                    if test_id in action_cases
                    else record_actions.get(test_id, "UNKNOWN_ACTION")
                ),
                "test_id": test_id,
            }
            for test_id in test_ids
        ],
        key=lambda item: (item["action_id"], item["test_id"]),
    )


def verify_runtime_v21(
    contract: dict[str, object],
    plan: dict[str, object],
    bundle: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
    verification_scope: str = "FULL_CONTRACT",
) -> dict[str, object]:
    """Re-evaluate every admitted record and aggregate the exact 2.1 gates."""
    if verification_scope not in _SCOPES:
        raise ValueError("INVALID_VERIFICATION_SCOPE")
    contract_errors = validate_action_contract_v21(contract)
    plan_errors = validate_persisted_runtime_plan(
        plan,
        contract,
        review_package=review_package,
        review_output=review_output,
    )
    contract_execution_errors: list[dict[str, object]] = []
    if contract_errors:
        contract_execution_errors.append({
            "code": "INVALID_ACTION_CONTRACT_V21",
            "detail": copy.deepcopy(contract_errors),
        })
    if plan_errors:
        contract_execution_errors.append({
            "code": "INVALID_RUNTIME_PLAN",
            "detail": copy.deepcopy(plan_errors),
        })

    action_cases, lifecycle_cases, duplicate_case_ids = _case_indexes(plan)
    if duplicate_case_ids:
        contract_execution_errors.append({
            "code": "DUPLICATE_RUNTIME_CASE",
            "detail": duplicate_case_ids,
        })
    if lifecycle_cases or contract.get("lifecycles"):
        contract_execution_errors.append({
            "code": "RUNTIME_LIFECYCLE_VERIFICATION_INCOMPLETE",
            "detail": "2.1 lifecycle cases require an implemented exact transition verifier",
        })

    bundle_errors = validate_runtime_evidence_bundle(
        bundle,
        contract,
        plan,
        review_package=review_package,
        review_output=review_output,
    )
    evidence_errors = [
        {"code": "RUNTIME_EVIDENCE_BUNDLE_INVALID", "detail": copy.deepcopy(error)}
        for error in bundle_errors
    ]
    if bundle_errors:
        raw_inventory = {
            "coverage_status": "INCOMPLETE",
            "required_test_ids": sorted(action_cases) + sorted(lifecycle_cases),
            "observed_test_ids": sorted(
                record.get("test_id")
                for record in bundle.get("records", [])
                if isinstance(record, dict) and isinstance(record.get("test_id"), str)
            ),
            "missing_test_ids": [],
            "unexpected_test_ids": [],
        }
        required_set = set(raw_inventory["required_test_ids"])
        observed_set = set(raw_inventory["observed_test_ids"])
        raw_inventory["missing_test_ids"] = sorted(required_set - observed_set)
        raw_inventory["unexpected_test_ids"] = sorted(observed_set - required_set)
    else:
        raw_inventory = runtime_evidence_inventory(bundle, plan)

    source_contract = _source_contract(contract)
    action_results = []
    record_actions: dict[str, str] = {}
    for record in bundle.get("records", []):
        if not isinstance(record, dict):
            continue
        record_test_id = record.get("test_id")
        command = record.get("command")
        command_action = command.get("action_id") if isinstance(command, dict) else None
        if isinstance(record_test_id, str):
            record_actions[record_test_id] = (
                command_action
                if isinstance(command_action, str) and command_action.strip()
                else "UNKNOWN_ACTION"
            )
        planned = action_cases.get(record.get("test_id"))
        if planned is None:
            continue
        action_id, case = planned
        try:
            verified, record_errors = _verify_action_record(
                contract,
                source_contract,
                action_id,
                case,
                record,
            )
        except (IndexError, KeyError, TypeError, ValueError) as error:
            code = "RUNTIME_RECORD_VERIFICATION_ERROR"
            detail = {
                "action_id": action_id,
                "test_id": record.get("test_id"),
                "error_type": type(error).__name__,
                "message": str(error),
            }
            verified = _error_result(
                source_contract,
                action_id,
                record,
                code,
                detail,
            )
            record_errors = [{"code": code, "detail": detail}]
        action_results.append(verified)
        evidence_errors.extend(record_errors)
    action_results.sort(key=lambda item: (item["action_id"], item["test_id"]))

    required_action_ids = _action_inventory(
        raw_inventory["required_test_ids"],
        action_cases,
    )
    observed_action_ids = _action_inventory(
        raw_inventory["observed_test_ids"],
        action_cases,
        record_actions,
    )
    missing_action_ids = _action_inventory(
        raw_inventory["missing_test_ids"],
        action_cases,
    )
    unexpected_action_ids = _action_inventory(
        raw_inventory["unexpected_test_ids"],
        action_cases,
        record_actions,
    )
    plan_complete = plan.get("coverage_summary", {}).get("status") == "COMPLETE"
    action_coverage = (
        "COMPLETE"
        if plan_complete
        and raw_inventory["coverage_status"] == "COMPLETE"
        and not bundle_errors
        and not missing_action_ids
        and not unexpected_action_ids
        else "INCOMPLETE"
    )
    lifecycle_applicability = "NOT_APPLICABLE" if not contract.get("lifecycles") else "APPLICABLE"
    lifecycle_coverage = "COMPLETE" if lifecycle_applicability == "NOT_APPLICABLE" else "INCOMPLETE"
    coverage_status = (
        "COMPLETE"
        if action_coverage == "COMPLETE" and lifecycle_coverage == "COMPLETE"
        else "INCOMPLETE"
    )

    review = plan.get("review_commitments", {})
    review_completion = review.get("completion", "PENDING")
    if review_completion == "REENTRY_REQUIRED":
        dependency_status = "REENTRY_REQUIRED"
    elif contract_execution_errors:
        dependency_status = "DEFINITION_NOT_READY"
    else:
        dependency_status = "CONFORMANT"
    any_runtime_failure = (
        any(not result["conformant"] for result in action_results)
        or bool(evidence_errors)
        or bool(missing_action_ids)
        or bool(unexpected_action_ids)
    )
    if any_runtime_failure:
        runtime_status = "NON_CONFORMANT"
    elif not action_results:
        runtime_status = "NOT_RUN"
    else:
        runtime_status = "CONFORMANT"
    review_complete = review_completion in {"NOT_REQUIRED", "REVIEW_OUTPUT_RECORDED"}
    implementation_conformant = (
        verification_scope == "FULL_CONTRACT"
        and coverage_status == "COMPLETE"
        and dependency_status == "CONFORMANT"
        and runtime_status == "CONFORMANT"
        and review_complete
        and not contract_execution_errors
        and not evidence_errors
    )

    audit_input = {
        "status": dependency_status,
        "source_semantic_contract_hash": contract.get("semantic_contract_hash"),
        "source_runtime_plan_hash": plan.get("plan_hash"),
        "source_runtime_evidence_bundle_hash": bundle.get("bundle_hash"),
    }
    assurance_input = {
        "verification_scope": verification_scope,
        "review_completion": review_completion,
        "reliability_status": "NOT_MEASURED",
    }
    report_inputs = {
        "audit_result": copy.deepcopy(audit_input),
        "action_results": copy.deepcopy(action_results),
        "lifecycle_results": [],
        "semantic_assurance": copy.deepcopy(assurance_input),
    }
    report = {
        "report_schema_version": REPORT_VERSION,
        "report_inputs": report_inputs,
        "source_contract": source_contract,
        "verification_scope": verification_scope,
        "contract_dependency_status": dependency_status,
        "runtime_status": runtime_status,
        "review_completion": review_completion,
        "semantic_review_reliability": "NOT_MEASURED",
        "implementation_status": (
            "IMPLEMENTATION_CONFORMANT"
            if implementation_conformant
            else "IMPLEMENTATION_NOT_CONFORMANT"
        ),
        "coverage_status": coverage_status,
        "action_coverage_status": action_coverage,
        "lifecycle_coverage_status": lifecycle_coverage,
        "lifecycle_applicability": lifecycle_applicability,
        "required_action_test_ids": required_action_ids,
        "observed_action_test_ids": observed_action_ids,
        "missing_action_test_ids": missing_action_ids,
        "unexpected_action_test_ids": unexpected_action_ids,
        "required_lifecycle_case_ids": [],
        "observed_lifecycle_case_ids": [],
        "missing_lifecycle_case_ids": [],
        "unexpected_lifecycle_case_ids": [],
        "action_results": action_results,
        "lifecycle_results": [],
        "blocking_reentry_events": [],
        "contract_execution_errors": contract_execution_errors,
        "evidence_errors": evidence_errors,
        "deduplicated_evidence_count": 0,
    }
    try:
        validate_instance(report, _REPORT_SCHEMA)
    except SchemaValidationError as error:
        raise ValueError(f"RUNTIME_REPORT_INVALID: {error}") from error
    return report


def validate_runtime_conformance_report_v21(
    report: dict[str, object],
    contract: dict[str, object],
    plan: dict[str, object],
    bundle: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> None:
    """Validate schema and rederive the full report from its bounded inputs."""
    try:
        validate_instance(report, _REPORT_SCHEMA)
        scope = report["verification_scope"]
        expected = verify_runtime_v21(
            contract,
            plan,
            bundle,
            review_package=review_package,
            review_output=review_output,
            verification_scope=scope,
        )
        if _canonical(report) != _canonical(expected):
            raise ValueError("report does not match independently recomputed result")
    except (KeyError, SchemaValidationError, TypeError, ValueError, RecursionError) as error:
        if isinstance(error, ValueError) and str(error).startswith("RUNTIME_REPORT_INVALID"):
            raise
        raise ValueError(f"RUNTIME_REPORT_INVALID: {error}") from error


__all__ = [
    "REPORT_VERSION",
    "validate_runtime_conformance_report_v21",
    "verify_runtime_v21",
]
