"""Typed gap records and compilation-result routing for downstream 2.1."""

import copy

from downstream_v2.reentry import build_reentry_events

from .derivation import ContractExpressivenessGap, SemanticAuthorityGap


SEMANTIC_AUTHORITY_GAP = "SEMANTIC_AUTHORITY_GAP"
CONTRACT_EXPRESSIVENESS_GAP = "CONTRACT_EXPRESSIVENESS_GAP"
RUNTIME_MAPPING_GAP = "RUNTIME_MAPPING_GAP"


def _candidate_refs(spec: object) -> list[str]:
    if not isinstance(spec, dict):
        return []
    values = spec.get("source_seed_refs")
    if not isinstance(values, list):
        value = spec.get("source_seed_ref")
        values = [value] if isinstance(value, str) else []
    return sorted({value for value in values if isinstance(value, str) and value})


def _record_input(
    *,
    field_path: object,
    policy: object,
    authority_scope_refs: object,
) -> tuple[str, dict[str, object], list[str]]:
    if (
        not isinstance(field_path, str)
        or field_path.count("/") != 2
        or not all(field_path.split("/"))
        or not isinstance(policy, dict)
        or not isinstance(authority_scope_refs, list)
        or not authority_scope_refs
        or any(not isinstance(ref, str) or not ref for ref in authority_scope_refs)
        or len(authority_scope_refs) != len(set(authority_scope_refs))
    ):
        raise ValueError("INVALID_GAP_RECORD_INPUT")
    return field_path, policy, sorted(authority_scope_refs)


def semantic_gap_record(
    *,
    field_path: str,
    spec: object,
    error: SemanticAuthorityGap,
    policy: dict[str, object],
    authority_scope_refs: list[str],
) -> dict[str, object]:
    """Build a Product Definition gap only from the typed semantic signal."""
    field_path, policy, scope_refs = _record_input(
        field_path=field_path,
        policy=policy,
        authority_scope_refs=authority_scope_refs,
    )
    if not isinstance(error, SemanticAuthorityGap) or not isinstance(error.detail, dict):
        raise ValueError("INVALID_SEMANTIC_GAP_SIGNAL")
    detail = error.detail
    evidence_refs = detail.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        raise ValueError("INVALID_SEMANTIC_GAP_SIGNAL")
    return {
        "code": SEMANTIC_AUTHORITY_GAP,
        "field_path": field_path,
        "reason": detail["description"],
        "gap_type": detail["gap_type"],
        "required_expectation": policy["expectation"],
        "required_authority_class": detail["required_authority_class"],
        "authority_scope_refs": scope_refs,
        "candidate_seed_refs": _candidate_refs(spec),
        "evidence_refs": sorted(evidence_refs),
    }


def expressiveness_gap_record(
    *,
    field_path: str,
    spec: object,
    error: ContractExpressivenessGap,
    policy: dict[str, object],
    authority_scope_refs: list[str],
) -> dict[str, object]:
    """Build a contract-evolution record only from proven eligible authority."""
    field_path, policy, scope_refs = _record_input(
        field_path=field_path,
        policy=policy,
        authority_scope_refs=authority_scope_refs,
    )
    if not isinstance(error, ContractExpressivenessGap) or not isinstance(
        error.detail, dict
    ):
        raise ValueError("INVALID_EXPRESSIVENESS_GAP_SIGNAL")
    detail = error.detail
    eligible_refs = detail.get("eligible_seed_refs")
    semantic_form = detail.get("collection_semantics")
    if (
        semantic_form not in {"MEMBERSHIP_SET", "CONJUNCTIVE_SET"}
        or not isinstance(eligible_refs, list)
        or len(eligible_refs) < 2
        or eligible_refs != sorted(set(eligible_refs))
        or _candidate_refs(spec) != eligible_refs
    ):
        raise ValueError("INVALID_EXPRESSIVENESS_GAP_SIGNAL")
    return {
        "code": CONTRACT_EXPRESSIVENESS_GAP,
        "field_path": field_path,
        "reason": (
            "Eligible exact authority cannot be represented by the closed "
            "action-conformance/2.1 derivation vocabulary."
        ),
        "required_semantic_form": semantic_form,
        "contract_limitation": "collect_exact is not permitted by the target field policy",
        "authority_scope_refs": scope_refs,
        "candidate_seed_refs": list(eligible_refs),
    }


def route_compilation_gaps(
    *,
    source_authority: dict[str, object],
    definition: dict[str, object],
    semantic_debt: dict[str, object],
    semantic_gaps: list[dict[str, object]],
    expressiveness_gaps: list[dict[str, object]],
) -> dict[str, object]:
    """Return the compilation failure union without crossing gap boundaries."""
    if (
        not isinstance(semantic_gaps, list)
        or not isinstance(expressiveness_gaps, list)
        or not semantic_gaps
        and not expressiveness_gaps
    ):
        raise ValueError("INVALID_COMPILATION_GAP_INVENTORY")
    if any(gap.get("code") != SEMANTIC_AUTHORITY_GAP for gap in semantic_gaps):
        raise ValueError("INVALID_SEMANTIC_GAP_INVENTORY")
    if any(
        gap.get("code") != CONTRACT_EXPRESSIVENESS_GAP
        for gap in expressiveness_gaps
    ):
        raise ValueError("INVALID_EXPRESSIVENESS_GAP_INVENTORY")
    semantic = copy.deepcopy(semantic_gaps)
    expressiveness = copy.deepcopy(expressiveness_gaps)
    events = (
        build_reentry_events(
            source_authority=source_authority,
            definition=definition,
            gaps=semantic,
            source_contract_hash=None,
        )
        if semantic
        else []
    )
    return {
        "status": "REENTRY_REQUIRED" if semantic else "CONTRACT_EVOLUTION_REQUIRED",
        "contract": None,
        "semantic_debt": copy.deepcopy(semantic_debt),
        "semantic_gaps": semantic,
        "expressiveness_gaps": expressiveness,
        "reentry_events": events,
    }


__all__ = [
    "CONTRACT_EXPRESSIVENESS_GAP",
    "RUNTIME_MAPPING_GAP",
    "SEMANTIC_AUTHORITY_GAP",
    "expressiveness_gap_record",
    "route_compilation_gaps",
    "semantic_gap_record",
]
