"""Closed semantic derivation primitives for action conformance 2.1."""

import copy
import re

from .responsibility import _validate_responsibility_profile_v21


_VALID_AUTHORITY_CLASSES = {
    "FACTUAL",
    "INTENT",
    "CONSTRAINT",
    "BEHAVIORAL",
    "PREFERENCE",
}
_COLLECTION_SEMANTICS = {"MEMBERSHIP_SET", "CONJUNCTIVE_SET"}
_SCOPE_REF = re.compile(r"^(?:REQ|SURF|SCR)-[^\s]+$")


class SemanticAuthorityGap(ValueError):
    """Approved product meaning is explicitly unresolved."""

    def __init__(self, detail: object):
        self.code = "SEMANTIC_AUTHORITY_GAP"
        self.detail = copy.deepcopy(detail)
        super().__init__(f"{self.code}: {self.detail}")


class ContractExpressivenessGap(ValueError):
    """Eligible exact authority cannot be represented by the declared vocabulary."""

    def __init__(self, detail: object):
        self.code = "CONTRACT_EXPRESSIVENESS_GAP"
        self.detail = copy.deepcopy(detail)
        super().__init__(f"{self.code}: {self.detail}")


def _fail(detail: object):
    raise ValueError(detail)


def _scope_refs(context: object) -> list[str]:
    if not isinstance(context, dict) or not isinstance(
        context.get("authority_scope_refs"),
        list,
    ):
        _fail("INVALID_AUTHORITY_SCOPE_REFS")
    refs = context["authority_scope_refs"]
    if (
        not refs
        or any(
            not isinstance(ref, str) or not _SCOPE_REF.fullmatch(ref)
            for ref in refs
        )
        or len(set(refs)) != len(refs)
    ):
        _fail("INVALID_AUTHORITY_SCOPE_REFS")
    current = context.get("current_scope_refs")
    if (
        not isinstance(current, list)
        or any(
            not isinstance(ref, str) or not _SCOPE_REF.fullmatch(ref)
            for ref in current
        )
        or len(set(current)) != len(current)
    ):
        _fail("INVALID_CURRENT_SCOPE_REFS")
    if any(ref not in current for ref in refs):
        _fail("UNRESOLVED_AUTHORITY_SCOPE_REF")
    return refs


def seed_matches_selector_v21(
    seed: dict[str, object],
    selector: dict[str, object],
    context: dict[str, object],
) -> bool:
    """Return whether a source seed is scope-current and selector-exact."""
    try:
        refs = _scope_refs(context)
        location = seed["location"]
        if not isinstance(location, dict) or not isinstance(selector, dict):
            return False
        if (
            location.get("owner_ref") not in refs
            or location.get("scope") != selector.get("scope")
            or location.get("axis") != selector.get("axis")
        ):
            return False
        if selector.get("scope") == "GRILL":
            return location.get("pack_id") == selector.get("pack_id")
        if "pack_id" in selector:
            return False
        if location.get("scope") == "UX_ACTION":
            locator = context.get("ux_action_locator")
            return (
                isinstance(locator, dict)
                and set(locator) == {"screen_ref", "action_key"}
                and location.get("owner_ref") == locator.get("screen_ref")
                and location.get("action_key") == locator.get("action_key")
            )
        return True
    except (KeyError, TypeError, ValueError):
        return False


def _seed(
    ref: object,
    seeds: object,
    selectors: list[object],
    context: dict[str, object],
) -> dict[str, object]:
    if (
        not isinstance(ref, str)
        or not isinstance(seeds, dict)
        or ref not in seeds
        or not isinstance(seeds[ref], dict)
    ):
        _fail("UNKNOWN_SOURCE_SEED")
    seed = seeds[ref]
    if (
        seed.get("seed_key") != ref
        or seed.get("source_status") not in {None, "CURRENT"}
        or not any(
            seed_matches_selector_v21(seed, selector, context)
            for selector in selectors
        )
    ):
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
        elif (
            isinstance(current, list)
            and token.isdigit()
            and (token == "0" or not token.startswith("0"))
            and int(token) < len(current)
        ):
            current = current[int(token)]
        else:
            _fail("JSON_POINTER_NOT_FOUND")
    return current


def _validate_spec(spec: object) -> str:
    if not isinstance(spec, dict) or not isinstance(spec.get("kind"), str):
        _fail("INVALID_FIELD_SPEC")
    return spec["kind"]


def _valid_unresolved_evidence_refs(values: object) -> bool:
    return (
        isinstance(values, list)
        and all(
            isinstance(value, str) and bool(value.strip())
            for value in values
        )
        and len(values) == len(set(values))
    )


def classify_exact_collection_request(
    *,
    field_policy: dict[str, object],
    eligible_seed_refs: list[str],
    requested_collection_semantics: str,
) -> None:
    """Classify only a proven eligible exact-set request against field vocabulary."""
    if (
        not isinstance(field_policy, dict)
        or not isinstance(eligible_seed_refs, list)
        or len(eligible_seed_refs) < 2
        or any(
            not isinstance(ref, str) or not ref.strip()
            for ref in eligible_seed_refs
        )
        or len(eligible_seed_refs) != len(set(eligible_seed_refs))
        or requested_collection_semantics not in _COLLECTION_SEMANTICS
        or field_policy.get("collection_semantics")
        != requested_collection_semantics
        or not isinstance(field_policy.get("allowed_derivations"), list)
    ):
        _fail("INVALID_EXACT_COLLECTION_REQUEST")
    if "collect_exact" in field_policy["allowed_derivations"]:
        return
    raise ContractExpressivenessGap(
        {
            "collection_semantics": requested_collection_semantics,
            "eligible_seed_refs": copy.deepcopy(eligible_seed_refs),
        },
    )


def derive_semantic_field_v21(
    spec: dict[str, object],
    *,
    field_name: str,
    field_kind: str,
    context: dict[str, object],
    seeds: dict[str, dict[str, object]],
    profile: dict[str, object],
) -> dict[str, object]:
    """Materialize one exact, deterministic, collected, or reviewed field."""
    if field_kind not in {"ACTION", "LIFECYCLE"}:
        _fail("INVALID_FIELD_KIND")
    frozen = _validate_responsibility_profile_v21(profile)
    group = frozen[
        "action_fields" if field_kind == "ACTION" else "lifecycle_fields"
    ]
    if not isinstance(field_name, str) or field_name not in group:
        _fail("UNKNOWN_SEMANTIC_FIELD")
    _scope_refs(context)
    field_policy = group[field_name]
    selectors = field_policy["allowed_seed_selectors"]
    allowed_derivations = field_policy["allowed_derivations"]
    kind = _validate_spec(spec)

    if kind == "UNRESOLVED":
        if (
            set(spec)
            != {
                "kind",
                "gap_type",
                "description",
                "required_authority_class",
                "evidence_refs",
            }
            or spec.get("gap_type")
            not in {
                "AMBIGUITY_FOUND",
                "CONTRACT_CONFLICT",
                "OUT_OF_SCOPE_REQUEST",
            }
            or not isinstance(spec.get("description"), str)
            or not spec["description"].strip()
            or spec.get("required_authority_class")
            not in _VALID_AUTHORITY_CLASSES
            or not _valid_unresolved_evidence_refs(spec.get("evidence_refs"))
        ):
            _fail("INVALID_UNRESOLVED_SPEC")
        raise SemanticAuthorityGap(spec)

    if kind == "DIRECT_AUTHORITY":
        if "DIRECT_AUTHORITY" not in allowed_derivations:
            _fail("DERIVATION_NOT_PERMITTED")
        if set(spec) != {"kind", "source_seed_ref"}:
            _fail("INVALID_DIRECT_SPEC")
        seed = _seed(spec["source_seed_ref"], seeds, selectors, context)
        return {
            "value": copy.deepcopy(seed["value"]),
            "source_seed_refs": [spec["source_seed_ref"]],
            "derivation": copy.deepcopy(spec),
        }

    if kind == "MACHINE_DERIVED":
        operator = spec.get("operator")
        if operator not in {"extract", "select", "collect_exact"}:
            _fail("INVALID_MACHINE_SPEC")
        if operator == "extract":
            if set(spec) != {"kind", "operator", "source_seed_ref", "pointer"}:
                _fail("INVALID_MACHINE_SPEC")
            if operator not in allowed_derivations:
                _fail("DERIVATION_NOT_PERMITTED")
            seed = _seed(spec["source_seed_ref"], seeds, selectors, context)
            value = _resolve_pointer(seed["value"], spec["pointer"])
            refs = [spec["source_seed_ref"]]
            normalized_spec = spec
        elif operator == "select":
            if set(spec) != {"kind", "operator", "source_seed_ref", "keys"}:
                _fail("INVALID_MACHINE_SPEC")
            if operator not in allowed_derivations:
                _fail("DERIVATION_NOT_PERMITTED")
            seed = _seed(spec["source_seed_ref"], seeds, selectors, context)
            keys = spec.get("keys")
            if (
                not isinstance(seed.get("value"), dict)
                or not isinstance(keys, list)
                or not keys
                or any(not isinstance(key, str) or not key for key in keys)
                or keys != sorted(keys)
                or len(keys) != len(set(keys))
                or any(key not in seed["value"] for key in keys)
            ):
                _fail("INVALID_SELECT_SPEC")
            value = {key: seed["value"][key] for key in keys}
            refs = [spec["source_seed_ref"]]
            normalized_spec = spec
        elif operator == "collect_exact":
            if set(spec) != {"kind", "operator", "source_seed_refs"}:
                _fail("INVALID_COLLECT_EXACT_SPEC")
            requested_refs = spec.get("source_seed_refs")
            if (
                not isinstance(requested_refs, list)
                or len(requested_refs) < 2
                or any(
                    not isinstance(ref, str) or not ref.strip()
                    for ref in requested_refs
                )
                or len(requested_refs) != len(set(requested_refs))
            ):
                _fail("INVALID_COLLECT_EXACT_SPEC")
            if operator not in allowed_derivations:
                _fail("DERIVATION_NOT_PERMITTED")
            refs = sorted(requested_refs)
            eligible_seeds = [
                _seed(ref, seeds, selectors, context)
                for ref in refs
            ]
            classify_exact_collection_request(
                field_policy=field_policy,
                eligible_seed_refs=refs,
                requested_collection_semantics=field_policy[
                    "collection_semantics"
                ],
            )
            value = [copy.deepcopy(seed["value"]) for seed in eligible_seeds]
            normalized_spec = {
                "kind": "MACHINE_DERIVED",
                "operator": "collect_exact",
                "source_seed_refs": refs,
            }
        return {
            "value": copy.deepcopy(value),
            "source_seed_refs": list(refs),
            "derivation": copy.deepcopy(normalized_spec),
        }

    if kind == "REVIEW_REQUIRED":
        if (
            set(spec)
            != {
                "kind",
                "source_seed_refs",
                "proposed_value",
                "why_structuring_is_insufficient",
                "interpretation_scope",
            }
            or not isinstance(spec.get("source_seed_refs"), list)
            or not spec["source_seed_refs"]
            or any(
                not isinstance(value, str)
                for value in spec["source_seed_refs"]
            )
            or len(set(spec["source_seed_refs"]))
            != len(spec["source_seed_refs"])
            or not isinstance(
                spec.get("why_structuring_is_insufficient"),
                str,
            )
            or not spec["why_structuring_is_insufficient"].strip()
            or not isinstance(spec.get("interpretation_scope"), str)
            or not spec["interpretation_scope"].strip()
        ):
            _fail("INVALID_REVIEW_SPEC")
        if "REVIEW_REQUIRED" not in allowed_derivations:
            _fail("DERIVATION_NOT_PERMITTED")
        for ref in spec["source_seed_refs"]:
            _seed(ref, seeds, selectors, context)
        return {
            "value": copy.deepcopy(spec["proposed_value"]),
            "source_seed_refs": list(spec["source_seed_refs"]),
            "derivation": copy.deepcopy(spec),
        }

    _fail("INVALID_FIELD_SPEC")


__all__ = [
    "ContractExpressivenessGap",
    "SemanticAuthorityGap",
    "classify_exact_collection_request",
    "derive_semantic_field_v21",
    "seed_matches_selector_v21",
]
