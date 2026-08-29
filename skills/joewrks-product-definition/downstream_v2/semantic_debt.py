"""Deterministic executable accounting for downstream V2 semantic debt."""

import copy
import json
import re


_FIELD_PATH = re.compile(r"^(?:actions|lifecycles)/[^/\s]+/[^/\s]+$")
_DERIVATION_BUCKETS = {
    "DIRECT_AUTHORITY": "direct_authority_fields",
    "MACHINE_DERIVED": "machine_derived_fields",
    "REVIEW_REQUIRED": "review_required_fields",
}
_GAP_KEYS = {
    "code", "field_path", "reason", "gap_type", "required_expectation",
    "required_authority_class", "authority_scope_refs", "candidate_seed_refs",
    "evidence_refs",
}


def _canonical(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    )


def _field_path(value: object) -> str:
    if not isinstance(value, str) or _FIELD_PATH.fullmatch(value) is None:
        raise ValueError("INVALID_SEMANTIC_FIELD_PATH")
    return value


def _validated_gap(gap: object) -> dict[str, object]:
    if not isinstance(gap, dict) or set(gap) != _GAP_KEYS:
        raise ValueError("INVALID_SEMANTIC_AUTHORITY_GAP")
    if gap.get("code") != "SEMANTIC_AUTHORITY_GAP":
        raise ValueError("INVALID_SEMANTIC_AUTHORITY_GAP")
    _field_path(gap.get("field_path"))
    if (
        not isinstance(gap.get("reason"), str)
        or not gap["reason"].strip()
        or gap.get("gap_type") not in {
            "AMBIGUITY_FOUND", "CONTRACT_CONFLICT", "OUT_OF_SCOPE_REQUEST"
        }
        or gap.get("required_expectation") not in {
            "DIRECT_REQUIRED", "DETERMINISTIC_REQUIRED", "REVIEW_PERMITTED"
        }
        or gap.get("required_authority_class") not in {
            "FACTUAL", "INTENT", "CONSTRAINT", "BEHAVIORAL", "PREFERENCE"
        }
    ):
        raise ValueError("INVALID_SEMANTIC_AUTHORITY_GAP")
    for key in ("authority_scope_refs", "candidate_seed_refs", "evidence_refs"):
        values = gap.get(key)
        if (
            not isinstance(values, list)
            or any(not isinstance(value, str) or not value for value in values)
            or len(values) != len(set(values))
        ):
            raise ValueError("INVALID_SEMANTIC_AUTHORITY_GAP")
    return copy.deepcopy(gap)


def semantic_debt_report(
    *,
    derived_fields: list[tuple[str, dict[str, object]]],
    gaps: list[dict[str, object]],
) -> dict[str, object]:
    """Return stable, mutually exclusive field and authority-gap inventories."""
    if not isinstance(derived_fields, list) or not isinstance(gaps, list):
        raise ValueError("INVALID_SEMANTIC_DEBT_INPUT")
    inventories = {name: [] for name in _DERIVATION_BUCKETS.values()}
    seen_paths = set()
    for item in derived_fields:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("INVALID_DERIVED_FIELD")
        path, field = item
        path = _field_path(path)
        if path in seen_paths:
            raise ValueError("DUPLICATE_SEMANTIC_FIELD_PATH")
        seen_paths.add(path)
        if not isinstance(field, dict) or not isinstance(field.get("derivation"), dict):
            raise ValueError("INVALID_DERIVED_FIELD")
        kind = field["derivation"].get("kind")
        if kind not in _DERIVATION_BUCKETS:
            raise ValueError("INVALID_DERIVATION_KIND")
        inventories[_DERIVATION_BUCKETS[kind]].append(path)

    authority_gaps = []
    for raw_gap in gaps:
        validated = _validated_gap(raw_gap)
        if validated["field_path"] in seen_paths:
            raise ValueError("FIELD_PATH_IS_DERIVED_AND_GAPPED")
        if validated["field_path"] in {gap["field_path"] for gap in authority_gaps}:
            raise ValueError("DUPLICATE_SEMANTIC_GAP_PATH")
        authority_gaps.append(validated)
    for inventory in inventories.values():
        inventory.sort()
    authority_gaps.sort(key=lambda gap: (gap["field_path"], _canonical(gap)))
    return {
        "direct_authority_count": len(inventories["direct_authority_fields"]),
        "machine_derived_count": len(inventories["machine_derived_fields"]),
        "review_required_count": len(inventories["review_required_fields"]),
        "authority_gap_count": len(authority_gaps),
        "direct_authority_fields": inventories["direct_authority_fields"],
        "machine_derived_fields": inventories["machine_derived_fields"],
        "review_required_fields": inventories["review_required_fields"],
        "authority_gaps": authority_gaps,
    }
