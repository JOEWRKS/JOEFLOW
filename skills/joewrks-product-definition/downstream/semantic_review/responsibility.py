"""Normative field responsibility and semantic-obligation validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


VALID_MODES = {"LOCAL", "COMPOSITIONAL", "REFERENCE_ONLY"}
EXPECTED_ACTION_FIELDS = (
    "actor", "authentication", "relationship_predicate", "object_binding",
    "concurrency", "preconditions", "allowed_current_states", "forbidden_states",
    "input_invariants", "command", "expected_domain_mutation", "forbidden_mutations",
    "default_result", "result_expectations", "version_result", "history_result",
    "business_side_effects", "delivery_effects", "idempotency", "rejection",
    "recovery", "visible_success", "visible_error", "superseded_rules",
    "test_obligations", "trace",
)
EXPECTED_LIFECYCLE_FIELDS = (
    "current_states", "allowed_transitions", "forbidden_transitions",
    "boundary_conditions", "reversibility", "reversal_window", "object_outcome",
    "required_reason", "required_confirmation", "required_evidence", "authority",
    "history_preservation",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTITY_RE = re.compile(r"^(action|lifecycle):[^:]+:[^:]+$")


class ResponsibilityError(ValueError):
    """A deterministic responsibility-profile or obligation-index failure."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _default_profile_path() -> Path:
    return Path(__file__).resolve().parent / "artifacts" / "responsibility-profile-v1.json"


def load_responsibility_profile(path: Path) -> dict[str, Any]:
    """Load and structurally verify the frozen 38-rule responsibility profile."""

    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", str(error)) from error
    if profile.get("schema_version") != "joewrks.semantic-responsibility-profile/1.0":
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", "profile schema version")
    revision = profile.get("rubric_calibration_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", "calibration revision")
    expected = {
        "action": EXPECTED_ACTION_FIELDS,
        "lifecycle": EXPECTED_LIFECYCLE_FIELDS,
    }
    brief_labels = profile.get("brief_ownership_labels")
    if not isinstance(brief_labels, dict) or len(brief_labels) != 38:
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", "brief ownership labels")
    all_ids: list[str] = []
    for kind, fields in expected.items():
        rules = profile.get(kind)
        if not isinstance(rules, dict) or set(rules) != set(fields):
            raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", f"{kind} field set")
        for offset, field in enumerate(fields, start=1):
            rule = rules[field]
            expected_id = f"FR-{'A' if kind == 'action' else 'L'}{offset:02d}"
            if rule.get("responsibility_rule_id") != expected_id:
                raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", f"{kind}:{field}")
            if rule.get("completeness_mode") not in VALID_MODES:
                raise ResponsibilityError("COMPLETENESS_UNDEFINED", field)
            if not isinstance(brief_labels.get(expected_id), str) or not brief_labels[
                expected_id
            ]:
                raise ResponsibilityError(
                    "RESPONSIBILITY_UNDEFINED", f"brief ownership {field}"
                )
            rule["brief_owns_label"] = brief_labels[expected_id]
            required_metadata = {
                "owns", "may_reference_fields", "allowed_sibling_rules",
                "must_not_duplicate", "omission", "overreach", "omission_code",
                "overreach_code",
            }
            if not required_metadata.issubset(rule):
                raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", f"metadata {field}")
            if rule["omission_code"] != "MISSING_OWNED_SEMANTIC":
                raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", f"omission {field}")
            if rule["overreach_code"] != "UNSUPPORTED_OVERREACH":
                raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", f"overreach {field}")
            all_ids.append(expected_id)
    if len(all_ids) != 38 or len(set(all_ids)) != 38:
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", "rule count")
    return profile


def expected_responsibility(*args: Any) -> tuple[str, str]:
    """Return the unique responsibility rule and mode.

    Accepts ``(owner_kind, semantic_field)`` for the frozen profile and
    ``(profile, owner_kind, semantic_field)`` for a verified package profile.
    """

    if len(args) == 2:
        profile = load_responsibility_profile(_default_profile_path())
        owner_kind, semantic_field = args
    elif len(args) == 3 and isinstance(args[0], dict):
        profile, owner_kind, semantic_field = args
    else:
        raise TypeError("expected_responsibility expects 2 or 3 arguments")
    try:
        rule = profile[owner_kind][semantic_field]
    except (KeyError, TypeError) as error:
        raise ResponsibilityError(
            "RESPONSIBILITY_UNDEFINED", f"{owner_kind}:{semantic_field}"
        ) from error
    mode = rule.get("completeness_mode")
    if mode not in VALID_MODES:
        raise ResponsibilityError("COMPLETENESS_UNDEFINED", str(semantic_field))
    return rule["responsibility_rule_id"], mode


def _require_sorted_strings(value: Any, field: str) -> None:
    if (
        not isinstance(value, list)
        or not all(isinstance(item, str) and item for item in value)
        or value != sorted(value)
        or len(value) != len(set(value))
    ):
        raise ResponsibilityError("INVALID_OBLIGATION_INDEX", field)


def _contract_owner_ids(contract: dict[str, Any], owner_kind: str) -> set[str]:
    collection = contract.get("actions" if owner_kind == "action" else "lifecycles", [])
    key = "action_id" if owner_kind == "action" else "lifecycle_id"
    return {
        item[key]
        for item in collection
        if isinstance(item, dict) and isinstance(item.get(key), str)
    }


def validate_obligation_index(
    contract: dict[str, Any], profile: dict[str, Any], index: dict[str, Any]
) -> None:
    """Verify contract binding, unique ownership, and deterministic references."""

    if index.get("schema_version") != "joewrks.semantic-obligation-index/1.0":
        raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "schema version")
    if index.get("contract_hash") != contract.get("contract_hash"):
        raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "contract hash")
    obligations = index.get("obligations")
    if not isinstance(obligations, list):
        raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "obligations")
    owners_by_obligation: dict[str, tuple[str, str, str]] = {}
    scope_owners: dict[tuple[str, str, str], str] = {}
    for obligation in obligations:
        if not isinstance(obligation, dict):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "obligation record")
        required = {
            "obligation_id", "canonical_refs", "obligation_type", "owner_kind",
            "owner_id", "owning_field", "responsibility_rule_id", "completeness_mode",
            "semantic_value_pointer", "semantic_value_hash", "allowed_sibling_refs",
            "required_test_refs", "projection_notes",
        }
        if set(obligation) != required:
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "record fields")
        obligation_id = obligation["obligation_id"]
        owner = (
            obligation["owner_kind"], obligation["owner_id"], obligation["owning_field"]
        )
        if obligation_id in owners_by_obligation:
            raise ResponsibilityError("MULTIPLE_OWNERS", obligation_id)
        owners_by_obligation[obligation_id] = owner
        scope = (
            obligation["obligation_type"], obligation["owner_kind"], obligation["owner_id"]
        )
        prior_field = scope_owners.get(scope)
        if prior_field is not None and prior_field != obligation["owning_field"]:
            raise ResponsibilityError("MULTIPLE_OWNERS", ":".join(scope))
        scope_owners[scope] = obligation["owning_field"]
        expected_rule, expected_mode = expected_responsibility(
            profile, obligation["owner_kind"], obligation["owning_field"]
        )
        if (
            obligation["responsibility_rule_id"], obligation["completeness_mode"]
        ) != (expected_rule, expected_mode):
            raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", obligation_id)
        if obligation["owner_id"] not in _contract_owner_ids(
            contract, obligation["owner_kind"]
        ):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "owner ID")
        if not isinstance(obligation_id, str) or not obligation_id.startswith("OBL-"):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "obligation ID")
        if not isinstance(obligation["semantic_value_pointer"], str) or not obligation[
            "semantic_value_pointer"
        ].startswith("/"):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "semantic pointer")
        if SHA256_RE.fullmatch(str(obligation["semantic_value_hash"])) is None:
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "semantic hash")
        _require_sorted_strings(obligation["allowed_sibling_refs"], "sibling refs")
        if not all(IDENTITY_RE.fullmatch(ref) for ref in obligation["allowed_sibling_refs"]):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "sibling identity")
        _require_sorted_strings(obligation["required_test_refs"], "test refs")
        canonical_refs = obligation["canonical_refs"]
        if not isinstance(canonical_refs, list) or not canonical_refs:
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "canonical refs")
        canonical_keys = []
        for reference in canonical_refs:
            required_ref = {
                "object_id", "pointer", "value_sha256", "source_status", "active"
            }
            if not isinstance(reference, dict) or set(reference) != required_ref:
                raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "canonical ref")
            if reference["source_status"] != "CURRENT" or reference["active"] is not True:
                raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "inactive authority")
            if SHA256_RE.fullmatch(str(reference["value_sha256"])) is None:
                raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "canonical hash")
            canonical_keys.append((reference["object_id"], reference["pointer"]))
        if canonical_keys != sorted(canonical_keys) or len(canonical_keys) != len(
            set(canonical_keys)
        ):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "canonical ref order")
