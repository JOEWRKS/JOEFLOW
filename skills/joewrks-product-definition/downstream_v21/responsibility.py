"""Frozen responsibility profile 2.0 projection and digest."""

import copy
import json
from pathlib import Path

from downstream_v2.authority import sha256_json

from .identity import RESPONSIBILITY_PROFILE_ID


_REMOVED_ACTION_FIELDS = {
    "default_result",
    "result_expectations",
    "test_obligations",
}
_COLLECTION_SEMANTICS = {
    ("action_fields", "actor"): "MEMBERSHIP_SET",
    ("action_fields", "input_invariants"): "CONJUNCTIVE_SET",
    ("lifecycle_fields", "authority"): "MEMBERSHIP_SET",
}
_FROZEN_ENTRY_KEYS = {
    "expectation",
    "required_authority_class",
    "allowed_seed_selectors",
}
_PROFILE_KEYS = {"profile_id", "action_fields", "lifecycle_fields"}
_PROFILE_PATH = Path(__file__).with_name("references") / "downstream-responsibility-v2.json"
_FROZEN_PROFILE_PATH = (
    Path(__file__).parent.parent
    / "downstream_v2"
    / "references"
    / "field-responsibility-v1.json"
)


def _fail(detail: object):
    raise ValueError(detail)


def _allowed_derivations(expectation: object, collection_semantics: str) -> list[str]:
    if collection_semantics != "NONE":
        derivations = ["DIRECT_AUTHORITY"]
        if expectation == "DETERMINISTIC_REQUIRED":
            derivations.extend(["extract", "select"])
        elif expectation != "DIRECT_REQUIRED":
            _fail("INVALID_FROZEN_RESPONSIBILITY_PROFILE")
        derivations.append("collect_exact")
        return derivations
    if expectation == "DIRECT_REQUIRED":
        return ["DIRECT_AUTHORITY"]
    if expectation == "DETERMINISTIC_REQUIRED":
        return ["DIRECT_AUTHORITY", "extract", "select"]
    if expectation == "REVIEW_PERMITTED":
        return ["DIRECT_AUTHORITY", "extract", "select", "REVIEW_REQUIRED"]
    _fail("INVALID_FROZEN_RESPONSIBILITY_PROFILE")


def _load_frozen_profile() -> dict[str, object]:
    try:
        with _FROZEN_PROFILE_PATH.open("r", encoding="utf-8") as handle:
            profile = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("INVALID_FROZEN_RESPONSIBILITY_PROFILE") from error
    if (
        not isinstance(profile, dict)
        or set(profile) != _PROFILE_KEYS
        or profile.get("profile_id") != "joewrks.downstream-responsibility/1.0"
        or not isinstance(profile.get("action_fields"), dict)
        or not isinstance(profile.get("lifecycle_fields"), dict)
    ):
        _fail("INVALID_FROZEN_RESPONSIBILITY_PROFILE")
    return profile


def _expected_profile_v21() -> dict[str, object]:
    frozen = _load_frozen_profile()
    expected = {
        "profile_id": RESPONSIBILITY_PROFILE_ID,
        "action_fields": {},
        "lifecycle_fields": {},
    }
    for group_name in ("action_fields", "lifecycle_fields"):
        group = frozen[group_name]
        if not isinstance(group, dict):
            _fail("INVALID_FROZEN_RESPONSIBILITY_PROFILE")
        target = expected[group_name]
        for field_name, entry in group.items():
            if (
                not isinstance(field_name, str)
                or not isinstance(entry, dict)
                or set(entry) != _FROZEN_ENTRY_KEYS
            ):
                _fail("INVALID_FROZEN_RESPONSIBILITY_PROFILE")
            if group_name == "action_fields" and field_name in _REMOVED_ACTION_FIELDS:
                continue
            collection_semantics = _COLLECTION_SEMANTICS.get(
                (group_name, field_name),
                "NONE",
            )
            target[field_name] = {
                "expectation": copy.deepcopy(entry["expectation"]),
                "required_authority_class": copy.deepcopy(
                    entry["required_authority_class"],
                ),
                "allowed_seed_selectors": copy.deepcopy(
                    entry["allowed_seed_selectors"],
                ),
                "allowed_derivations": _allowed_derivations(
                    entry["expectation"],
                    collection_semantics,
                ),
                "collection_semantics": collection_semantics,
            }
    return expected


def _validate_responsibility_profile_v21(profile: object) -> dict[str, object]:
    if not isinstance(profile, dict) or profile != _expected_profile_v21():
        _fail("RESPONSIBILITY_PROFILE_DRIFT")
    return profile


def load_responsibility_profile_v21() -> dict[str, object]:
    """Load the fixed profile fixture and reject every projection change."""
    try:
        with _PROFILE_PATH.open("r", encoding="utf-8") as handle:
            profile = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("INVALID_RESPONSIBILITY_PROFILE") from error
    return _validate_responsibility_profile_v21(profile)


def responsibility_profile_digest_v21() -> str:
    """Return the canonical JSON SHA-256 digest of profile 2.0."""
    return sha256_json(load_responsibility_profile_v21())


__all__ = [
    "load_responsibility_profile_v21",
    "responsibility_profile_digest_v21",
]
