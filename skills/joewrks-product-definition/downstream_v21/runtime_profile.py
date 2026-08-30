"""Frozen runtime-responsibility/1.0 classification and digest."""

import copy
import json
from pathlib import Path

from downstream_v2.authority import sha256_json

from .identity import RUNTIME_PROFILE_ID


_PROFILE_PATH = Path(__file__).with_name("references") / "runtime-responsibility-v1.json"
_ACTION_RUNTIME_CRITICAL = {
    "actor",
    "authentication",
    "relationship_predicate",
    "object_binding",
    "concurrency",
    "preconditions",
    "allowed_current_states",
    "forbidden_states",
    "input_invariants",
    "command",
    "expected_domain_mutation",
    "forbidden_mutations",
    "version_result",
    "history_result",
    "business_side_effects",
    "delivery_effects",
    "idempotency",
    "rejection",
    "recovery",
    "superseded_rules",
}
_ACTION_NON_RUNTIME_PRESENTATION = {"visible_success", "visible_error"}
_ACTION_ASSURANCE_ONLY = {"trace"}
_LIFECYCLE_RUNTIME_CRITICAL = {
    "current_states",
    "allowed_transitions",
    "forbidden_transitions",
    "boundary_conditions",
    "reversibility",
    "reversal_window",
    "object_outcome",
    "required_reason",
    "required_confirmation",
    "required_evidence",
    "authority",
    "history_preservation",
}


def _expected_profile() -> dict[str, object]:
    action_fields = {
        field_name: "RUNTIME_CRITICAL"
        for field_name in _ACTION_RUNTIME_CRITICAL
    }
    action_fields.update(
        {
            field_name: "NON_RUNTIME_PRESENTATION"
            for field_name in _ACTION_NON_RUNTIME_PRESENTATION
        }
    )
    action_fields.update(
        {field_name: "ASSURANCE_ONLY" for field_name in _ACTION_ASSURANCE_ONLY}
    )
    return {
        "profile_id": RUNTIME_PROFILE_ID,
        "action_fields": action_fields,
        "lifecycle_fields": {
            field_name: "RUNTIME_CRITICAL"
            for field_name in _LIFECYCLE_RUNTIME_CRITICAL
        },
    }


def _validate_profile(profile: object) -> dict[str, object]:
    if not isinstance(profile, dict) or profile != _expected_profile():
        raise ValueError("RUNTIME_RESPONSIBILITY_PROFILE_DRIFT")
    return profile


def load_runtime_responsibility_profile() -> dict[str, object]:
    """Load a fresh copy of the exact profile; callers cannot reclassify fields."""
    try:
        with _PROFILE_PATH.open("r", encoding="utf-8") as handle:
            profile = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("INVALID_RUNTIME_RESPONSIBILITY_PROFILE") from error
    return copy.deepcopy(_validate_profile(profile))


def runtime_responsibility_digest() -> str:
    return sha256_json(load_runtime_responsibility_profile())


__all__ = [
    "load_runtime_responsibility_profile",
    "runtime_responsibility_digest",
]
