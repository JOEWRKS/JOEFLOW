"""Normative field responsibility and semantic-obligation validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from downstream.provenance import ProvenanceError, resolve_pointer

from .hashing import canonical_json_bytes, sha256_bytes


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
OBLIGATION_TAXONOMY = {
    "actor eligibility": "FR-A01",
    "authentication prerequisite": "FR-A02",
    "relationship authority": "FR-A03",
    "object/scope binding": "FR-A04",
    "concurrency/version conflict": "FR-A05",
    "non-input domain precondition": "FR-A06",
    "allowed state": "FR-A07",
    "forbidden state": "FR-A08",
    "input validity": "FR-A09",
    "command shape": "FR-A10",
    "authoritative mutation": "FR-A11",
    "protected no-op": "FR-A12",
    "result class": "FR-A13",
    "component result behavior": "FR-A14",
    "version effect": "FR-A15",
    "history effect": "FR-A16",
    "business side effect": "FR-A17",
    "delivery effect": "FR-A18",
    "idempotency/replay": "FR-A19",
    "rejection semantics": "FR-A20",
    "recovery semantics": "FR-A21",
    "visible success": "FR-A22",
    "visible error": "FR-A23",
    "superseded sentinel": "FR-A24",
    "verification coverage": "FR-A25",
    "end-to-end trace": "FR-A26",
    "lifecycle state vocabulary": "FR-L01",
    "allowed lifecycle transition": "FR-L02",
    "forbidden lifecycle transition": "FR-L03",
    "lifecycle boundary": "FR-L04",
    "lifecycle reversibility": "FR-L05",
    "lifecycle reversal window": "FR-L06",
    "lifecycle object outcome": "FR-L07",
    "lifecycle reason requirement": "FR-L08",
    "lifecycle confirmation requirement": "FR-L09",
    "lifecycle evidence requirement": "FR-L10",
    "lifecycle transition authority": "FR-L11",
    "lifecycle history preservation": "FR-L12",
}


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
    return validate_responsibility_profile(profile)


def validate_responsibility_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate one parsed responsibility profile and return that exact mapping."""

    if not isinstance(profile, dict):
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", "profile object")
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
    if profile.get("obligation_taxonomy") != OBLIGATION_TAXONOMY:
        raise ResponsibilityError("RESPONSIBILITY_UNDEFINED", "obligation taxonomy")
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


def _contract_owners(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    owners: dict[str, dict[str, Any]] = {}
    for owner_kind, collection_name, id_key in (
        ("action", "actions", "action_id"),
        ("lifecycle", "lifecycles", "lifecycle_id"),
    ):
        for owner in contract.get(collection_name, []):
            if isinstance(owner, dict) and isinstance(owner.get(id_key), str):
                owners[f"{owner_kind}:{owner[id_key]}"] = owner
    return owners


def _review_identity_rules(
    contract: dict[str, Any], profile: dict[str, Any]
) -> dict[str, str]:
    result: dict[str, str] = {}
    for owner_prefix, owner in _contract_owners(contract).items():
        owner_kind = owner_prefix.split(":", 1)[0]
        for field, rule in profile[owner_kind].items():
            semantic = owner.get(field)
            if (
                isinstance(semantic, dict)
                and isinstance(semantic.get("derivation"), dict)
                and semantic["derivation"].get("kind") == "REVIEW_REQUIRED"
            ):
                result[f"{owner_prefix}:{field}"] = rule["responsibility_rule_id"]
    return result


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
    contract_owners = _contract_owners(contract)
    review_identity_rules = _review_identity_rules(contract, profile)
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
        if profile["obligation_taxonomy"].get(obligation["obligation_type"]) != (
            expected_rule
        ):
            raise ResponsibilityError(
                "INVALID_OBLIGATION_INDEX", f"obligation taxonomy: {obligation_id}"
            )
        if obligation["owner_id"] not in _contract_owner_ids(
            contract, obligation["owner_kind"]
        ):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "owner ID")
        owner_prefix = f"{obligation['owner_kind']}:{obligation['owner_id']}"
        owner_record = contract_owners.get(owner_prefix)
        semantic = owner_record.get(obligation["owning_field"]) if owner_record else None
        if (
            not isinstance(semantic, dict)
            or not isinstance(semantic.get("derivation"), dict)
            or semantic["derivation"].get("kind") != "REVIEW_REQUIRED"
        ):
            raise ResponsibilityError(
                "INVALID_OBLIGATION_INDEX", f"owner is not REVIEW_REQUIRED: {obligation_id}"
            )
        if not isinstance(obligation_id, str) or not obligation_id.startswith("OBL-"):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "obligation ID")
        if not isinstance(obligation["semantic_value_pointer"], str) or not obligation[
            "semantic_value_pointer"
        ].startswith("/"):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "semantic pointer")
        if SHA256_RE.fullmatch(str(obligation["semantic_value_hash"])) is None:
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "semantic hash")
        collection_name = (
            "actions" if obligation["owner_kind"] == "action" else "lifecycles"
        )
        owner_index = contract[collection_name].index(owner_record)
        expected_pointer = (
            f"/{collection_name}/{owner_index}/{obligation['owning_field']}/value"
        )
        if obligation["semantic_value_pointer"] != expected_pointer:
            raise ResponsibilityError(
                "INVALID_OBLIGATION_INDEX", f"semantic pointer: {obligation_id}"
            )
        try:
            semantic_value = resolve_pointer(contract, expected_pointer)
        except ProvenanceError as error:
            raise ResponsibilityError(
                "INVALID_OBLIGATION_INDEX", f"semantic pointer: {obligation_id}"
            ) from error
        if obligation["semantic_value_hash"] != sha256_bytes(
            canonical_json_bytes(semantic_value)
        ):
            raise ResponsibilityError(
                "INVALID_OBLIGATION_INDEX", f"semantic hash: {obligation_id}"
            )
        _require_sorted_strings(obligation["allowed_sibling_refs"], "sibling refs")
        if not all(IDENTITY_RE.fullmatch(ref) for ref in obligation["allowed_sibling_refs"]):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "sibling identity")
        allowed_rules = set(
            profile[obligation["owner_kind"]][obligation["owning_field"]][
                "allowed_sibling_rules"
            ]
        )
        for sibling in obligation["allowed_sibling_refs"]:
            sibling_rule = review_identity_rules.get(sibling)
            if sibling_rule is None or sibling_rule not in allowed_rules:
                raise ResponsibilityError(
                    "INVALID_OBLIGATION_INDEX", f"disallowed sibling: {sibling}"
                )
        _require_sorted_strings(obligation["required_test_refs"], "test refs")
        if not obligation["required_test_refs"]:
            raise ResponsibilityError(
                "INVALID_OBLIGATION_INDEX", f"test coverage: {obligation_id}"
            )
        canonical_refs = obligation["canonical_refs"]
        if not isinstance(canonical_refs, list) or not canonical_refs:
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "canonical refs")
        canonical_keys = []
        try:
            declared_source_keys = {
                canonical_json_bytes(owner_record["sources"][source_index])
                for source_index in semantic["source_refs"]
            }
        except (IndexError, KeyError, TypeError) as error:
            raise ResponsibilityError(
                "INVALID_OBLIGATION_INDEX", f"owner sources: {obligation_id}"
            ) from error
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
            if canonical_json_bytes(reference) not in declared_source_keys:
                raise ResponsibilityError(
                    "INVALID_OBLIGATION_INDEX",
                    f"canonical ref outside owning field: {obligation_id}",
                )
            canonical_keys.append((reference["object_id"], reference["pointer"]))
        if canonical_keys != sorted(canonical_keys) or len(canonical_keys) != len(
            set(canonical_keys)
        ):
            raise ResponsibilityError("INVALID_OBLIGATION_INDEX", "canonical ref order")
