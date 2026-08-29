"""Frozen responsibility policy and safe semantic field derivation for downstream V2."""

import copy
import hashlib
import json
import re
from pathlib import Path


RESPONSIBILITY_PROFILE_ID = "joewrks.downstream-responsibility/1.0"

_ACTION_POLICY = {
    "actor": ("DIRECT_REQUIRED", "INTENT", ["CORE:actor"]),
    "authentication": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:permission", "CORE:security", "GRILL:GRILL-AUTH-1:login", "GRILL:GRILL-AUTH-1:session_expiry", "GRILL:GRILL-AUTH-1:session_renewal"]),
    "relationship_predicate": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:permission", "CORE:boundary", "GRILL:GRILL-PERMISSION-1:role", "GRILL:GRILL-PERMISSION-1:resource_ownership"]),
    "object_binding": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:data", "CORE:state"]),
    "concurrency": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:alternative_path", "CORE:error", "CORE:recovery", "GRILL:GRILL-ASYNC-1:idempotency", "GRILL:GRILL-ASYNC-1:duplicate_execution", "UX_ACTION:duplicate_concurrent_action"]),
    "preconditions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:precondition", "UX_ACTION:precondition"]),
    "allowed_current_states": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state"]),
    "forbidden_states": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:boundary"]),
    "input_invariants": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:validation", "CORE:data", "UX_ACTION:input", "UX_ACTION:validation"]),
    "command": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:happy_path", "CORE:entry_point", "UX_ACTION:submit"]),
    "expected_domain_mutation": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:side_effect", "CORE:data", "CORE:persistence", "UX_ACTION:data_mutation"]),
    "forbidden_mutations": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary", "CORE:side_effect"]),
    "default_result": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:happy_path", "UX_ACTION:success", "UX_STATE:success"]),
    "result_expectations": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:happy_path", "CORE:alternative_path", "CORE:error", "CORE:recovery", "CORE:acceptance", "UX_ACTION:success", "UX_ACTION:failure", "UX_STATE:success", "UX_STATE:error"]),
    "version_result": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:persistence"]),
    "history_result": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:persistence", "CORE:data"]),
    "business_side_effects": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:side_effect"]),
    "delivery_effects": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:notification", "CORE:side_effect", "UX_ACTION:notification"]),
    "idempotency": ("DETERMINISTIC_REQUIRED", "INTENT", ["GRILL:GRILL-ASYNC-1:idempotency", "CORE:recovery", "CORE:side_effect"]),
    "rejection": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:error", "CORE:validation", "CORE:permission", "UX_ACTION:failure", "UX_ACTION:permission"]),
    "recovery": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:recovery", "GRILL:GRILL-ASYNC-1:retry", "GRILL:GRILL-ASYNC-1:reconciliation", "UX_ACTION:retry"]),
    "visible_success": ("REVIEW_PERMITTED", "PREFERENCE", ["UX_STATE:success", "UX_STATE:completed", "UX_ACTION:success", "CORE:acceptance"]),
    "visible_error": ("REVIEW_PERMITTED", "PREFERENCE", ["UX_STATE:error", "UX_ACTION:failure", "CORE:error"]),
    "superseded_rules": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary"]),
    "test_obligations": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:acceptance"]),
    "trace": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:goal", "CORE:acceptance"]),
}
_LIFECYCLE_POLICY = {
    "current_states": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state"]),
    "allowed_transitions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:happy_path", "CORE:alternative_path"]),
    "forbidden_transitions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:boundary"]),
    "boundary_conditions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary", "CORE:precondition"]),
    "reversibility": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:recovery", "CORE:boundary", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:undo", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:irreversible_boundary"]),
    "reversal_window": ("DETERMINISTIC_REQUIRED", "INTENT", ["GRILL:GRILL-DESTRUCTIVE-ACTION-1:grace_period", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:undo", "CORE:boundary"]),
    "object_outcome": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:side_effect"]),
    "required_reason": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:validation", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:reason"]),
    "required_confirmation": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary", "CORE:permission", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:confirmation"]),
    "required_evidence": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:validation", "CORE:data"]),
    "authority": ("DIRECT_REQUIRED", "INTENT", ["CORE:actor", "CORE:permission", "GRILL:GRILL-PERMISSION-1:role"]),
    "history_preservation": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:persistence", "CORE:data"]),
}
_VALID_AUTHORITY_CLASSES = {"FACTUAL", "INTENT", "CONSTRAINT", "BEHAVIORAL", "PREFERENCE"}
_SCOPE_REF = re.compile(r"^(?:REQ|SURF|SCR)-[^\s]+$")


class SemanticGap(ValueError):
    def __init__(self, code: str, detail: object):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(detail: object):
    raise ValueError(detail)


def _selector(text: str) -> dict[str, object]:
    parts = text.split(":")
    if len(parts) == 2:
        scope, axis = parts
        return {"scope": scope, "axis": axis}
    scope, pack_id, axis = parts
    return {"scope": scope, "pack_id": pack_id, "axis": axis}


def _expected_group(policy: dict[str, tuple[str, str, list[str]]]) -> dict[str, object]:
    return {
        field: {"expectation": expectation, "required_authority_class": authority, "allowed_seed_selectors": [_selector(item) for item in selectors]}
        for field, (expectation, authority, selectors) in policy.items()
    }


def _expected_profile() -> dict[str, object]:
    return {"profile_id": RESPONSIBILITY_PROFILE_ID, "action_fields": _expected_group(_ACTION_POLICY), "lifecycle_fields": _expected_group(_LIFECYCLE_POLICY)}


def _validate_profile(profile: object) -> dict[str, object]:
    if not isinstance(profile, dict) or profile != _expected_profile():
        _fail("RESPONSIBILITY_PROFILE_DRIFT")
    return profile


def load_responsibility_profile() -> dict[str, object]:
    """Load the frozen JSON profile and reject all inventory or mapping drift."""
    path = Path(__file__).with_name("references") / "field-responsibility-v1.json"
    try:
        with path.open("r", encoding="utf-8") as handle:
            return _validate_profile(json.load(handle))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("INVALID_RESPONSIBILITY_PROFILE") from error


def responsibility_profile_digest() -> str:
    profile = load_responsibility_profile()
    canonical = json.dumps(profile, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _scope_refs(context: object) -> list[str]:
    if not isinstance(context, dict) or not isinstance(context.get("authority_scope_refs"), list):
        _fail("INVALID_AUTHORITY_SCOPE_REFS")
    refs = context["authority_scope_refs"]
    if not refs or any(not isinstance(ref, str) or not _SCOPE_REF.fullmatch(ref) for ref in refs) or len(set(refs)) != len(refs):
        _fail("INVALID_AUTHORITY_SCOPE_REFS")
    current = context.get("current_scope_refs")
    if not isinstance(current, list) or any(not isinstance(ref, str) or not _SCOPE_REF.fullmatch(ref) for ref in current) or len(set(current)) != len(current):
        _fail("INVALID_CURRENT_SCOPE_REFS")
    if any(ref not in current for ref in refs):
        _fail("UNRESOLVED_AUTHORITY_SCOPE_REF")
    return refs


def seed_matches_selector(seed: dict[str, object], selector: dict[str, object], context: dict[str, object]) -> bool:
    """Return whether a source seed is both scope-eligible and selector-exact."""
    try:
        refs = _scope_refs(context)
        location = seed["location"]
        if not isinstance(location, dict) or not isinstance(selector, dict):
            return False
        if location.get("owner_ref") not in refs or location.get("scope") != selector.get("scope") or location.get("axis") != selector.get("axis"):
            return False
        if selector.get("scope") == "GRILL":
            return location.get("pack_id") == selector.get("pack_id")
        if "pack_id" in selector:
            return False
        if location.get("scope") == "UX_ACTION":
            locator = context.get("ux_action_locator")
            return isinstance(locator, dict) and set(locator) == {"screen_ref", "action_key"} and location.get("owner_ref") == locator.get("screen_ref") and location.get("action_key") == locator.get("action_key")
        return True
    except (KeyError, TypeError, ValueError):
        return False


def _seed(ref: object, seeds: object, selectors: list[object], context: dict[str, object]) -> dict[str, object]:
    if not isinstance(ref, str) or not isinstance(seeds, dict) or ref not in seeds or not isinstance(seeds[ref], dict):
        _fail("UNKNOWN_SOURCE_SEED")
    seed = seeds[ref]
    if seed.get("seed_key") != ref or not any(seed_matches_selector(seed, selector, context) for selector in selectors):
        _fail("SOURCE_SEED_NOT_PERMITTED")
    return seed


def _resolve_pointer(value: object, pointer: object) -> object:
    if not isinstance(pointer, str) or not pointer or not pointer.startswith("/"):
        _fail("INVALID_JSON_POINTER")
    current = value
    for token in pointer[1:].split("/"):
        if "~" in token and re.search(r"~(?:[^01]|$)", token):
            _fail("INVALID_JSON_POINTER")
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and (token == "0" or not token.startswith("0")) and int(token) < len(current):
            current = current[int(token)]
        else:
            _fail("JSON_POINTER_NOT_FOUND")
    return current


def _validate_spec(spec: object) -> str:
    if not isinstance(spec, dict) or not isinstance(spec.get("kind"), str):
        _fail("INVALID_FIELD_SPEC")
    return spec["kind"]


def valid_unresolved_evidence_refs(values: object) -> bool:
    """Return whether unresolved evidence references are unique nonblank strings."""
    return (
        isinstance(values, list)
        and all(isinstance(value, str) and bool(value.strip()) for value in values)
        and len(values) == len(set(values))
    )


def derive_semantic_field(spec: dict[str, object], *, field_name: str, field_kind: str, context: dict[str, object], seeds: dict[str, dict[str, object]], profile: dict[str, object]) -> dict[str, object]:
    """Safely materialize one field from direct, deterministic, or reviewed authority."""
    if field_kind not in {"ACTION", "LIFECYCLE"}:
        _fail("INVALID_FIELD_KIND")
    frozen = _validate_profile(profile)
    group = frozen["action_fields" if field_kind == "ACTION" else "lifecycle_fields"]
    if not isinstance(field_name, str) or field_name not in group:
        _fail("UNKNOWN_SEMANTIC_FIELD")
    _scope_refs(context)
    entry = group[field_name]
    expectation = entry["expectation"]
    selectors = entry["allowed_seed_selectors"]
    kind = _validate_spec(spec)
    if kind == "UNRESOLVED":
        if set(spec) != {"kind", "gap_type", "description", "required_authority_class", "evidence_refs"} or spec.get("gap_type") not in {"AMBIGUITY_FOUND", "CONTRACT_CONFLICT", "OUT_OF_SCOPE_REQUEST"} or not isinstance(spec.get("description"), str) or not spec["description"].strip() or spec.get("required_authority_class") not in _VALID_AUTHORITY_CLASSES or not valid_unresolved_evidence_refs(spec.get("evidence_refs")):
            _fail("INVALID_UNRESOLVED_SPEC")
        raise SemanticGap("SEMANTIC_GAP", spec)
    allowed = {"DIRECT_REQUIRED": {"DIRECT_AUTHORITY"}, "DETERMINISTIC_REQUIRED": {"DIRECT_AUTHORITY", "MACHINE_DERIVED"}, "REVIEW_PERMITTED": {"DIRECT_AUTHORITY", "MACHINE_DERIVED", "REVIEW_REQUIRED"}}
    if kind not in allowed[expectation]:
        _fail("DERIVATION_NOT_PERMITTED")
    if kind == "DIRECT_AUTHORITY":
        if set(spec) != {"kind", "source_seed_ref"}:
            _fail("INVALID_DIRECT_SPEC")
        seed = _seed(spec["source_seed_ref"], seeds, selectors, context)
        value, refs = seed["value"], [spec["source_seed_ref"]]
    elif kind == "MACHINE_DERIVED":
        operator = spec.get("operator")
        if operator == "extract" and set(spec) == {"kind", "operator", "source_seed_ref", "pointer"}:
            seed = _seed(spec["source_seed_ref"], seeds, selectors, context)
            value, refs = _resolve_pointer(seed["value"], spec["pointer"]), [spec["source_seed_ref"]]
        elif operator == "select" and set(spec) == {"kind", "operator", "source_seed_ref", "keys"}:
            seed = _seed(spec["source_seed_ref"], seeds, selectors, context)
            keys = spec.get("keys")
            if not isinstance(seed.get("value"), dict) or not isinstance(keys, list) or not keys or any(not isinstance(key, str) or not key for key in keys) or keys != sorted(keys) or len(keys) != len(set(keys)) or any(key not in seed["value"] for key in keys):
                _fail("INVALID_SELECT_SPEC")
            value, refs = {key: seed["value"][key] for key in keys}, [spec["source_seed_ref"]]
        else:
            _fail("INVALID_MACHINE_SPEC")
    elif kind == "REVIEW_REQUIRED":
        if set(spec) != {"kind", "source_seed_refs", "proposed_value", "why_structuring_is_insufficient", "interpretation_scope"} or not isinstance(spec.get("source_seed_refs"), list) or not spec["source_seed_refs"] or any(not isinstance(value, str) for value in spec["source_seed_refs"]) or len(set(spec["source_seed_refs"])) != len(spec["source_seed_refs"]) or not isinstance(spec.get("why_structuring_is_insufficient"), str) or not spec["why_structuring_is_insufficient"].strip() or not isinstance(spec.get("interpretation_scope"), str) or not spec["interpretation_scope"].strip():
            _fail("INVALID_REVIEW_SPEC")
        for ref in spec["source_seed_refs"]:
            _seed(ref, seeds, selectors, context)
        value, refs = spec["proposed_value"], list(spec["source_seed_refs"])
    else:
        _fail("INVALID_FIELD_SPEC")
    return {"value": copy.deepcopy(value), "source_seed_refs": refs, "derivation": copy.deepcopy(spec)}
