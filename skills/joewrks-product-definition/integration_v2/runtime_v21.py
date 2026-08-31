"""Plan-and-bundle-bound semantic verification for action-conformance/2.1.

This is intentionally separate from the frozen 2.0 runtime verifier.  A valid
bundle admits transport records; this module independently evaluates the plan's
claimed runtime semantics against those records.
"""

from __future__ import annotations

from downstream_v21.contracts import validate_action_contract_v21
from downstream_v21.runtime_evidence import (
    runtime_evidence_inventory,
    validate_runtime_evidence_bundle,
)
from downstream_v21.runtime_plan import validate_persisted_runtime_plan


REPORT_VERSION = "joewrks.runtime-conformance-report/1.0"
_COMPONENTS = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)


def _pointer(value: object, pointer: str) -> object:
    if pointer == "":
        return value
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("INVALID_RUNTIME_ASSERTION_POINTER")
    current = value
    for part in pointer[1:].split("/"):
        token = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdecimal() and int(token) < len(current):
            current = current[int(token)]
        else:
            raise ValueError("RUNTIME_ASSERTION_POINTER_MISSING")
    return current


def _assertions(record: dict[str, object], assertions: list[dict[str, object]]) -> list[dict[str, str]]:
    failures = []
    for assertion in assertions:
        pointer = assertion["pointer"]
        try:
            value = _pointer(record, pointer)
        except ValueError:
            value = None
            found = False
        else:
            found = True
        kind = assertion["type"]
        passed = (kind == "path_present" and found) or (kind == "path_absent" and not found)
        if kind == "path_equals":
            passed = found and value == assertion["value"]
        if not passed:
            failures.append({"code": "RUNTIME_ASSERTION_FAILED", "pointer": pointer})
    return failures


def _case_failures(record: dict[str, object], case: dict[str, object]) -> list[dict[str, str]]:
    failures = []
    expected = case.get("result_expectation")
    if isinstance(expected, dict):
        observed = record.get("result", {}).get("result_class") if isinstance(record.get("result"), dict) else None
        if observed != expected["result_class"]:
            failures.append({"code": "RUNTIME_RESULT_CLASS_MISMATCH", "test_id": record["test_id"]})
    for expectation in case.get("component_expectations", []):
        component = expectation["component"]
        changed = record["before"][component] != record["after"][component]
        wants = expectation["expectation"]
        if (wants == "CHANGED" and not changed) or (wants == "UNCHANGED" and changed):
            failures.append({"code": "RUNTIME_COMPONENT_EXPECTATION_MISMATCH", "test_id": record["test_id"]})
    failures.extend(_assertions(record, case.get("evidence_assertions", [])))
    return failures


def verify_runtime_v21(
    contract: dict[str, object], plan: dict[str, object], bundle: dict[str, object], *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> dict[str, object]:
    """Re-evaluate every planned case; no bundle-completeness shortcut exists."""
    failures: list[dict[str, str]] = []
    contract_errors = validate_action_contract_v21(contract)
    dependency_status = "CONFORMANT" if not contract_errors else "DEFINITION_NOT_READY"
    if contract_errors:
        failures.append({"code": "INVALID_ACTION_CONTRACT_V21"})
    if validate_persisted_runtime_plan(
        plan, contract, review_package=review_package, review_output=review_output,
    ):
        failures.append({"code": "INVALID_RUNTIME_PLAN"})
    bundle_errors = validate_runtime_evidence_bundle(
        bundle, contract, plan, review_package=review_package, review_output=review_output,
    )
    failures.extend({"code": error["message"]} for error in bundle_errors)
    inventory = runtime_evidence_inventory(bundle, plan) if not bundle_errors else {
        "coverage_status": "INCOMPLETE", "required_test_ids": [], "observed_test_ids": [],
        "missing_test_ids": [], "unexpected_test_ids": []
    }
    cases = {
        case["test_id"]: case
        for collection in (plan.get("actions", []), plan.get("lifecycles", []))
        for item in collection for case in item.get("cases", [])
    }
    for record in bundle.get("records", []):
        case = cases.get(record.get("test_id"))
        if case is not None:
            failures.extend(_case_failures(record, case))
    lifecycle_status = "NOT_APPLICABLE" if not contract.get("lifecycles") else "APPLICABLE"
    full_contract = inventory["coverage_status"] == "COMPLETE" and not bundle_errors
    runtime_status = "CONFORMANT" if not failures and full_contract else "NON_CONFORMANT"
    status = "IMPLEMENTATION_CONFORMANT" if (
        dependency_status == "CONFORMANT" and full_contract and runtime_status == "CONFORMANT"
        and plan.get("review_commitments", {}).get("completion") != "REENTRY_REQUIRED"
    ) else "NON_CONFORMANT"
    return {
        "report_schema_version": REPORT_VERSION,
        "source_semantic_contract_hash": contract.get("semantic_contract_hash"),
        "source_runtime_plan_hash": plan.get("plan_hash"),
        "source_runtime_evidence_bundle_hash": bundle.get("bundle_hash"),
        "contract_dependency_status": dependency_status,
        "contract_coverage": "FULL_CONTRACT" if full_contract else "PARTIAL_PROBE",
        "coverage_status": inventory["coverage_status"],
        "lifecycle_status": lifecycle_status,
        "semantic_failures": failures,
        "runtime_status": runtime_status,
        "implementation_status": status,
    }


__all__ = ["REPORT_VERSION", "verify_runtime_v21"]
