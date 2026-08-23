"""Contract-authoritative semantic and deep no-op verification."""

from __future__ import annotations

import json
from typing import Any

from .invariants import evaluate_input_invariants
from .protocol import encode_typed_numbers
from .provenance import ProvenanceError, resolve_pointer


COMPONENTS = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)

DEFAULT_EXPECTATIONS = {
    "REJECTED": {component: "UNCHANGED" for component in COMPONENTS},
    "STALE": {component: "UNCHANGED" for component in COMPONENTS},
    "IDEMPOTENT_REPLAY": {component: "UNCHANGED" for component in COMPONENTS},
    "SUCCESS": {
        "authoritative_state": "CHANGED",
        "revision": "ANY",
        "history": "ANY",
        "business_side_effects": "ANY",
        "delivery_effects": "ANY",
    },
}


class VerificationError(ValueError):
    """Evidence or expectation cannot be evaluated."""


def _equal(left: Any, right: Any) -> bool:
    return json.dumps(
        encode_typed_numbers(left),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) == json.dumps(
        encode_typed_numbers(right),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def classify_result(result: dict[str, Any]) -> str:
    if result.get("replay") is True or result.get("code") == "IDEMPOTENT_REPLAY":
        return "IDEMPOTENT_REPLAY"
    code = str(result.get("code", "")).upper()
    if code in {"STALE", "STALE_VERSION", "VERSION_CONFLICT"}:
        return "STALE"
    status = str(result.get("status", "")).lower()
    if status in {"committed", "success", "ok"}:
        return "SUCCESS"
    if status in {"rejected", "denied", "error", "failed"}:
        return "REJECTED"
    raise VerificationError(f"unknown runtime result: {result!r}")


def _expected_result(
    action: dict[str, Any],
    record: dict[str, Any],
    declared: str | None,
) -> tuple[str, list[dict[str, Any]]]:
    command = record.get("command", {})
    command_input = command.get("input", {}) if isinstance(command, dict) else {}
    invariant_failures = evaluate_input_invariants(action.get("input_invariants", []), command_input)
    if invariant_failures:
        return "REJECTED", invariant_failures
    return declared or action.get("default_result", "SUCCESS"), []


def _evaluate_assertion(record: dict[str, Any], assertion: dict[str, Any]) -> dict[str, Any]:
    kind = assertion.get("type")
    pointer = assertion.get("pointer")
    present = True
    try:
        observed = resolve_pointer(record, pointer)
    except ProvenanceError:
        present = False
        observed = None
    passed = False
    if kind == "path_present":
        passed = present
    elif kind == "path_absent":
        passed = not present
    elif kind == "path_equals":
        passed = present and _equal(observed, assertion.get("value"))
    elif kind == "collection_item_field_equals":
        if present and isinstance(observed, list):
            matches = [
                item
                for item in observed
                if isinstance(item, dict)
                and item.get(assertion.get("match_field")) == assertion.get("match_value")
            ]
            passed = len(matches) == 1 and _equal(
                matches[0].get(assertion.get("field")), assertion.get("value")
            )
    else:
        raise VerificationError(f"unsupported evidence assertion: {kind}")
    return {
        "type": kind,
        "pointer": pointer,
        "passed": passed,
        "observed": observed,
        "expected": assertion.get("value"),
    }


def verify_execution(
    action: dict[str, Any],
    record: dict[str, Any],
    *,
    expected_result: str | None = None,
) -> dict[str, Any]:
    expected, invariant_failures = _expected_result(action, record, expected_result)
    if expected not in DEFAULT_EXPECTATIONS:
        raise VerificationError(f"unsupported expected result: {expected}")
    actual = classify_result(record.get("result", {}))
    before = record.get("before")
    after = record.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise VerificationError("before and after snapshots are required")
    configured = action.get("result_expectations", {}).get(expected, {})
    expectations = {**DEFAULT_EXPECTATIONS[expected], **configured}
    component_results: dict[str, dict[str, Any]] = {}
    for component in COMPONENTS:
        if component not in before or component not in after:
            raise VerificationError(f"snapshot component missing: {component}")
        expectation = expectations[component]
        if expectation not in {"UNCHANGED", "CHANGED", "ANY"}:
            raise VerificationError(f"invalid {component} expectation: {expectation}")
        changed = not _equal(before[component], after[component])
        passed = expectation == "ANY" or (expectation == "CHANGED" and changed) or (
            expectation == "UNCHANGED" and not changed
        )
        component_results[component] = {
            "expectation": expectation,
            "changed": changed,
            "passed": passed,
        }
    result_matches = actual == expected
    assertion_results = [
        _evaluate_assertion(record, assertion)
        for assertion in configured.get("assertions", [])
    ]
    failures = []
    if not result_matches:
        failures.append(f"expected {expected}, observed {actual}")
    failures.extend(
        f"{component} expected {item['expectation']}"
        for component, item in component_results.items()
        if not item["passed"]
    )
    failures.extend(
        f"evidence assertion failed: {item['type']} {item['pointer']}"
        for item in assertion_results
        if not item["passed"]
    )
    return {
        "action_id": action.get("action_id"),
        "expected_result": expected,
        "observed_result": actual,
        "result_matches": result_matches,
        "input_invariant_failures": invariant_failures,
        "components": component_results,
        "assertions": assertion_results,
        "failures": failures,
        "conformant": result_matches
        and all(item["passed"] for item in component_results.values())
        and all(item["passed"] for item in assertion_results),
    }


def verify_lifecycle_transition(
    lifecycle: dict[str, Any], observation: dict[str, Any]
) -> dict[str, Any]:
    observed_sources = set(observation.get("source_ids", []))
    sentinel_sources = {
        sentinel.get("object_id")
        for sentinel in lifecycle.get("superseded_sentinels", [])
        if sentinel.get("source_status") == "SUPERSEDED" and sentinel.get("active") is False
    }
    matched = sorted(observed_sources & sentinel_sources)
    return {
        "lifecycle_id": lifecycle.get("lifecycle_id"),
        "transition": observation.get("transition"),
        "matched_superseded_sources": matched,
        "conformant": not matched,
        "failures": [f"superseded source implemented as current: {source}" for source in matched],
    }
