"""Reusable input invariant hooks; product rules remain in product contracts."""

from __future__ import annotations

import math
from typing import Any

from .provenance import ProvenanceError, resolve_pointer


def _value_at(value: Any, pointer: str) -> tuple[bool, Any]:
    try:
        return True, resolve_pointer(value, pointer)
    except ProvenanceError:
        return False, None


def evaluate_input_invariants(invariants: Any, command_input: dict[str, Any]) -> list[dict[str, Any]]:
    if not invariants:
        return []
    failures: list[dict[str, Any]] = []
    for invariant in invariants:
        kind = invariant.get("type")
        pointer = invariant.get("pointer")
        present, value = _value_at(command_input, pointer) if isinstance(pointer, str) else (False, None)
        passed = True
        if kind == "required":
            passed = present and value not in (None, "")
        elif kind == "finite_number":
            passed = present and isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
        elif kind == "positive_number":
            passed = present and isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0
        elif kind == "non_negative_number":
            passed = present and isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0
        elif kind == "equals":
            passed = present and value == invariant.get("value")
        else:
            passed = False
        if not passed:
            failures.append({"type": kind, "pointer": pointer, "observed": value})
    return failures


def _resolve_or_missing(value: Any, pointer: Any) -> tuple[bool, Any]:
    if not isinstance(pointer, str):
        return False, None
    try:
        return True, resolve_pointer(value, pointer)
    except ProvenanceError:
        return False, None


def evaluate_domain_invariants(
    invariants: Any, context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Evaluate generic cross-product invariants against before/after/command context."""
    before = context.get("before", {})
    after = context.get("after", {})
    command = context.get("command", {})
    results: list[dict[str, Any]] = []
    for invariant in invariants or []:
        kind = invariant.get("type")
        passed = False
        observed: Any = None
        if kind in {"exact_object_ownership", "current_relationship_authority"}:
            owner_present, owner = _resolve_or_missing(before, invariant.get("owner_pointer") or invariant.get("authority_pointer"))
            actor_present, actor = _resolve_or_missing(command, invariant.get("actor_pointer"))
            observed = {"owner": owner, "actor": actor}
            passed = owner_present and actor_present and owner == actor
        elif kind == "single_active_object":
            present, collection = _resolve_or_missing(after, invariant.get("collection_pointer"))
            active_values = set(invariant.get("active_values", []))
            status_field = invariant.get("status_field")
            active_count = sum(
                1
                for item in collection or []
                if isinstance(item, dict) and item.get(status_field) in active_values
            ) if present and isinstance(collection, list) else -1
            maximum = invariant.get("maximum", 1)
            observed = active_count
            passed = active_count >= 0 and active_count <= maximum
        elif kind == "immutable_snapshot":
            before_present, before_value = _resolve_or_missing(before, invariant.get("pointer"))
            after_present, after_value = _resolve_or_missing(after, invariant.get("pointer"))
            observed = {"before": before_value, "after": after_value}
            passed = before_present and after_present and before_value == after_value
        elif kind == "event_time_provenance":
            before_present, before_events = _resolve_or_missing(before, invariant.get("collection_pointer"))
            after_present, after_events = _resolve_or_missing(after, invariant.get("collection_pointer"))
            required = invariant.get("required_fields", [])
            new_events = (
                after_events[len(before_events) :]
                if before_present and after_present and isinstance(before_events, list) and isinstance(after_events, list)
                else []
            )
            observed = new_events
            passed = bool(new_events) and all(
                isinstance(event, dict) and all(field in event and event[field] not in (None, "") for field in required)
                for event in new_events
            )
        elif kind == "terminal_state_worker_stop":
            state_present, state_value = _resolve_or_missing(before, invariant.get("state_pointer"))
            before_effect_present, before_effect = _resolve_or_missing(before, invariant.get("effect_pointer"))
            after_effect_present, after_effect = _resolve_or_missing(after, invariant.get("effect_pointer"))
            terminal = state_value in set(invariant.get("terminal_values", []))
            observed = {"state": state_value, "before_effect": before_effect, "after_effect": after_effect}
            passed = state_present and before_effect_present and after_effect_present and (
                not terminal or before_effect == after_effect
            )
        else:
            observed = "unsupported invariant"
        results.append({"type": kind, "passed": passed, "observed": observed})
    return results
