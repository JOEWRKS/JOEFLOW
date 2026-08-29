from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from materiality_v2 import classify_materiality, is_high_risk


UNKNOWN_REQUIRED_FIELDS = {
    "id", "status", "question", "why_it_matters", "required_authority_class",
    "question_category", "materiality", "decision_authority", "affects",
    "blocks_unknown_refs", "origin", "response_mode", "options",
    "recommendation", "evidence_refs", "resolved_by", "resolution_mode",
    "resolution_summary", "deferral", "blocked_reason",
}
DECISION_REQUIRED_FIELDS = {
    "id", "status", "statement", "decision_type", "resolution_mode",
    "decision_authority", "source_unknown_refs", "evidence_refs", "materiality",
    "affects", "decided_by", "accepted_recommendation",
}
LIFECYCLE_FIELDS = {"superseded_by", "retired_by", "retired_at_revision", "retirement_reason"}

UNKNOWN_STATUSES = {"OPEN", "RESOLVED", "DEFERRED", "BLOCKED", "SUPERSEDED", "RETIRED"}
REQUIRED_AUTHORITY_CLASSES = {"FACTUAL", "INTENT", "CONSTRAINT", "BEHAVIORAL", "PREFERENCE"}
QUESTION_CATEGORIES = {
    "CORE_FLOW", "SCOPE_BOUNDARY", "STATE_RECOVERY", "SECONDARY_BEHAVIOR",
    "PREFERENCE", "COSMETIC",
}
DECISION_AUTHORITIES = {
    "EVIDENCE_RESOLVABLE", "AGENT_AUTONOMOUS", "USER_CONFIRMATION",
    "USER_DECISION_REQUIRED", "EXTERNAL_AUTHORITY_REQUIRED",
}
RESOLUTION_MODES = {
    "EVIDENCE", "USER_DECISION", "USER_ACCEPTED_RECOMMENDATION",
    "AGENT_NON_MATERIAL_DEFAULT", "EXTERNAL_CONSTRAINT", "MIGRATION_RECONCILIATION",
}
DECISION_RESOLUTION_MODES = {
    "USER_DECISION", "USER_ACCEPTED_RECOMMENDATION",
    "AGENT_NON_MATERIAL_DEFAULT", "EXTERNAL_CONSTRAINT",
}
MODE_AUTHORITIES = {
    "EVIDENCE": "EVIDENCE_RESOLVABLE",
    "USER_DECISION": "USER_DECISION_REQUIRED",
    "USER_ACCEPTED_RECOMMENDATION": "USER_CONFIRMATION",
    "AGENT_NON_MATERIAL_DEFAULT": "AGENT_AUTONOMOUS",
    "EXTERNAL_CONSTRAINT": "EXTERNAL_AUTHORITY_REQUIRED",
}
MODE_DECIDERS = {
    "USER_DECISION": "USER",
    "USER_ACCEPTED_RECOMMENDATION": "USER",
    "AGENT_NON_MATERIAL_DEFAULT": "AGENT",
    "EXTERNAL_CONSTRAINT": "EXTERNAL_AUTHORITY",
}
ORIGIN_KEYS = {"kind", "surface_ref", "pack_id", "axis_id", "source_path"}
ORIGIN_KINDS = {
    "PRODUCT_SURFACE", "GRILL_TOPOLOGY", "GRILL_PACK_AXIS",
    "MIGRATION_RECONCILIATION", "MANUAL",
}
SPECIALIST_PACK_IDS = {
    "GRILL-AUTH-1", "GRILL-MONEY-1", "GRILL-FILE-UPLOAD-1",
    "GRILL-ASYNC-1", "GRILL-PERMISSION-1", "GRILL-DESTRUCTIVE-ACTION-1",
}
SPECIALIST_PACK_AXES = {
    "GRILL-AUTH-1": {
        "registration", "verification", "login", "logout", "session_expiry",
        "session_renewal", "password_reset", "account_recovery", "revocation",
        "role_change", "provider_failure", "duplicate_identity", "account_linking",
    },
    "GRILL-MONEY-1": {
        "currency", "price_authority", "tax", "discount", "payment_failure",
        "duplicate_payment", "refund", "partial_refund", "cancellation",
        "chargeback", "settlement", "receipt",
    },
    "GRILL-FILE-UPLOAD-1": {
        "type", "size", "quota", "malware", "processing", "partial_failure",
        "resume", "retention", "deletion", "ownership", "download_permission",
    },
    "GRILL-ASYNC-1": {
        "pending", "polling", "timeout", "retry", "idempotency",
        "duplicate_execution", "late_completion", "partial_completion", "cancel",
        "reconciliation",
    },
    "GRILL-PERMISSION-1": {
        "role", "resource_ownership", "read", "write", "delete", "delegation",
        "revocation", "role_change_mid_flow", "stale_permission", "audit",
    },
    "GRILL-DESTRUCTIVE-ACTION-1": {
        "confirmation", "reason", "undo", "grace_period", "dependency_effects",
        "irreversible_boundary", "audit", "notification",
    },
}
PRODUCT_AUTHORITY_GROUPS = {"requirements", "rules", "flows", "data", "integrations"}
IMPACT_REVIEW_KEYS = {
    "scope", "rules", "flows", "states", "privacy", "money", "security", "acceptance",
}
CANDIDATE_ONLY_SOURCE_KINDS = {"INFERRED_INTENT", "DESIGN_ARTIFACT"}
SOURCE_KIND_CAPABILITIES = {
    "USER_CONFIRMED_INTENT": {"INTENT", "PREFERENCE"},
    "DOCUMENTED_INTENT": {"INTENT", "PREFERENCE"},
    "HISTORICAL_DECISION": {"INTENT", "PREFERENCE"},
    "EXTERNAL_CONSTRAINT": {"FACTUAL", "CONSTRAINT"},
    "OBSERVED_IMPLEMENTATION": {"FACTUAL", "BEHAVIORAL"},
    "OBSERVED_RUNTIME": {"FACTUAL", "BEHAVIORAL"},
    "TEST_ASSERTION": {"FACTUAL", "BEHAVIORAL"},
    "DESIGN_ARTIFACT": {"INTENT", "PREFERENCE"},
    "INFERRED_INTENT": {"INTENT", "PREFERENCE"},
}
MEANINGLESS = {"none", "false", "n/a", "na", "later", "tbd"}
_QUESTION_FAN_OUT_PRIORITY = {
    "SYSTEMIC": 0,
    "MULTI_FLOW": 1,
    "MULTI_OBJECT": 2,
    "LOCAL": 3,
}
_QUESTION_CATEGORY_PRIORITY = {
    "CORE_FLOW": 0,
    "SCOPE_BOUNDARY": 1,
    "STATE_RECOVERY": 2,
    "SECONDARY_BEHAVIOR": 3,
    "PREFERENCE": 4,
    "COSMETIC": 5,
}

PACK_DIR = Path(__file__).resolve().parents[1] / "references" / "grill-packs"
GRILL_PROFILE_DOMAINS = (
    "AUTH", "MONEY", "FILE_UPLOAD", "ASYNC", "PERMISSION",
    "DESTRUCTIVE_ACTION",
)
DOMAIN_PACK_IDS = {
    "AUTH": "GRILL-AUTH-1",
    "MONEY": "GRILL-MONEY-1",
    "FILE_UPLOAD": "GRILL-FILE-UPLOAD-1",
    "ASYNC": "GRILL-ASYNC-1",
    "PERMISSION": "GRILL-PERMISSION-1",
    "DESTRUCTIVE_ACTION": "GRILL-DESTRUCTIVE-ACTION-1",
}
FORCED_SURFACE_KIND_DOMAINS = {
    "MONEY_FLOW": "MONEY",
    "ASYNC_PROCESS": "ASYNC",
    "PERMISSION": "PERMISSION",
    "DESTRUCTIVE_OPERATION": "DESTRUCTIVE_ACTION",
}
CORE_GRILL_AXES = (
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state",
    "data", "side_effect", "notification", "validation", "boundary",
    "persistence", "security", "privacy", "analytics", "acceptance",
)
PACK_AXIS_ORDER = {
    "GRILL-CORE-1": CORE_GRILL_AXES,
    "GRILL-AUTH-1": (
        "registration", "verification", "login", "logout", "session_expiry",
        "session_renewal", "password_reset", "account_recovery", "revocation",
        "role_change", "provider_failure", "duplicate_identity", "account_linking",
    ),
    "GRILL-MONEY-1": (
        "currency", "price_authority", "tax", "discount", "payment_failure",
        "duplicate_payment", "refund", "partial_refund", "cancellation",
        "chargeback", "settlement", "receipt",
    ),
    "GRILL-FILE-UPLOAD-1": (
        "type", "size", "quota", "malware", "processing", "partial_failure",
        "resume", "retention", "deletion", "ownership", "download_permission",
    ),
    "GRILL-ASYNC-1": (
        "pending", "polling", "timeout", "retry", "idempotency",
        "duplicate_execution", "late_completion", "partial_completion", "cancel",
        "reconciliation",
    ),
    "GRILL-PERMISSION-1": (
        "role", "resource_ownership", "read", "write", "delete", "delegation",
        "revocation", "role_change_mid_flow", "stale_permission", "audit",
    ),
    "GRILL-DESTRUCTIVE-ACTION-1": (
        "confirmation", "reason", "undo", "grace_period", "dependency_effects",
        "irreversible_boundary", "audit", "notification",
    ),
}
PACK_MATERIAL_FLOORS = {
    "GRILL-CORE-1": frozenset(),
    "GRILL-AUTH-1": frozenset({
        "session_expiry", "password_reset", "account_recovery", "revocation",
        "role_change", "duplicate_identity", "account_linking",
    }),
    "GRILL-MONEY-1": frozenset(PACK_AXIS_ORDER["GRILL-MONEY-1"]),
    "GRILL-FILE-UPLOAD-1": frozenset({
        "malware", "retention", "deletion", "ownership", "download_permission",
    }),
    "GRILL-ASYNC-1": frozenset({
        "idempotency", "duplicate_execution", "partial_completion", "reconciliation",
    }),
    "GRILL-PERMISSION-1": frozenset(PACK_AXIS_ORDER["GRILL-PERMISSION-1"]),
    "GRILL-DESTRUCTIVE-ACTION-1": frozenset(
        PACK_AXIS_ORDER["GRILL-DESTRUCTIVE-ACTION-1"]
    ),
}
PACK_SURFACE_KIND_METADATA = {
    "GRILL-CORE-1": (),
    "GRILL-AUTH-1": (),
    "GRILL-MONEY-1": ("MONEY_FLOW",),
    "GRILL-FILE-UPLOAD-1": (),
    "GRILL-ASYNC-1": ("ASYNC_PROCESS",),
    "GRILL-PERMISSION-1": ("PERMISSION",),
    "GRILL-DESTRUCTIVE-ACTION-1": ("DESTRUCTIVE_OPERATION",),
}
GRILL_PROFILE_CELL_KEYS = {
    "status", "surface_refs", "unknown_refs", "basis_refs", "rationale",
}
GRILL_AXIS_CELL_KEYS = {
    "status", "authority_refs", "unknown_refs", "basis_refs", "rationale",
}


def _error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _meaningful_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in MEANINGLESS


def _unique_strings(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) for item in value)
        and len(value) == len(set(value))
    )


def _is_current_surface(
    reference: Any,
    id_index: dict[str, tuple[str, dict[str, object]]],
) -> bool:
    if not isinstance(reference, str) or not reference.startswith("SURF-"):
        return False
    entry = id_index.get(reference)
    status = entry[1].get("status") if entry is not None else None
    return (
        entry is not None
        and isinstance(status, str)
        and status not in {"SUPERSEDED", "RETIRED"}
    )


def _is_valid_origin(
    origin: Any,
    id_index: dict[str, tuple[str, dict[str, object]]],
) -> bool:
    if not isinstance(origin, dict) or set(origin) != ORIGIN_KEYS:
        return False
    kind = origin.get("kind")
    surface_ref = origin.get("surface_ref")
    pack_id = origin.get("pack_id")
    axis_id = origin.get("axis_id")
    source_path = origin.get("source_path")
    if not isinstance(kind, str) or kind not in ORIGIN_KINDS:
        return False
    if kind == "PRODUCT_SURFACE":
        return (
            _is_current_surface(surface_ref, id_index)
            and pack_id is None and axis_id is None and source_path is None
        )
    if kind == "GRILL_TOPOLOGY":
        return (
            surface_ref is None and isinstance(pack_id, str) and pack_id in SPECIALIST_PACK_IDS
            and axis_id is None and source_path is None
        )
    if kind == "GRILL_PACK_AXIS":
        return (
            _is_current_surface(surface_ref, id_index)
            and isinstance(pack_id, str) and pack_id in SPECIALIST_PACK_IDS
            and isinstance(axis_id, str) and axis_id in SPECIALIST_PACK_AXES[pack_id]
            and source_path is None
        )
    if kind == "MIGRATION_RECONCILIATION":
        return (
            surface_ref is None and pack_id is None and axis_id is None
            and _meaningful_text(source_path)
        )
    return surface_ref is None and pack_id is None and axis_id is None and source_path is None


def _is_valid_options(response_mode: Any, options: Any) -> bool:
    if (
        not isinstance(response_mode, str)
        or response_mode not in {"MUTUALLY_EXCLUSIVE", "OPEN_RESPONSE_REQUIRED"}
    ):
        return False
    if not isinstance(options, list):
        return False
    if response_mode == "OPEN_RESPONSE_REQUIRED":
        return options == []
    if len(options) < 2:
        return False
    option_ids: list[str] = []
    for option in options:
        if not isinstance(option, dict) or set(option) != {"id", "statement", "consequences"}:
            return False
        option_id = option.get("id")
        consequences = option.get("consequences")
        if (
            not _meaningful_text(option_id)
            or not _meaningful_text(option.get("statement"))
            or not isinstance(consequences, list)
            or not consequences
            or any(not _meaningful_text(item) for item in consequences)
        ):
            return False
        option_ids.append(option_id)
    return len(option_ids) == len(set(option_ids))


def _evidence_can_support(
    record: dict[str, object], authority_class: str, *, external_constraint: bool = False,
) -> bool:
    source_kind = record.get("source_kind")
    authority_classes = record.get("authority_classes")
    return (
        record.get("status") == "CURRENT"
        and isinstance(source_kind, str)
        and isinstance(authority_class, str)
        and source_kind in SOURCE_KIND_CAPABILITIES
        and source_kind not in CANDIDATE_ONLY_SOURCE_KINDS
        and (not external_constraint or source_kind == "EXTERNAL_CONSTRAINT")
        and isinstance(authority_classes, list)
        and authority_class in authority_classes
        and authority_class in SOURCE_KIND_CAPABILITIES[source_kind]
    )


def _has_qualifying_evidence(
    refs: Any,
    evidence_index: dict[str, dict[str, object]],
    authority_class: str,
    *,
    external_constraint: bool = False,
) -> bool:
    return isinstance(refs, list) and any(
        isinstance(reference, str)
        and (evidence := evidence_index.get(reference)) is not None
        and _evidence_can_support(
            evidence, authority_class, external_constraint=external_constraint,
        )
        for reference in refs
    )


def _valid_deferral(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {"reason", "accepted_by", "impact_review"}:
        return False
    impact_review = value.get("impact_review")
    return (
        _meaningful_text(value.get("reason"))
        and value.get("accepted_by") == "user"
        and isinstance(impact_review, dict)
        and set(impact_review) == IMPACT_REVIEW_KEYS
        and all(_meaningful_text(impact_review[field]) for field in IMPACT_REVIEW_KEYS)
    )


def _recommendation_shape_is_valid(value: Any, options: Any) -> bool:
    if (
        not isinstance(value, dict)
        or set(value) != {"recommended_option", "reasoning_refs", "tradeoffs", "confidence"}
        or not isinstance(options, list)
    ):
        return False
    option_ids = [option.get("id") for option in options if isinstance(option, dict)]
    reasoning_refs = value.get("reasoning_refs")
    tradeoffs = value.get("tradeoffs")
    return (
        _meaningful_text(value.get("recommended_option"))
        and value.get("recommended_option") in option_ids
        and _unique_strings(reasoning_refs, nonempty=True)
        and isinstance(tradeoffs, list)
        and bool(tradeoffs)
        and all(_meaningful_text(item) for item in tradeoffs)
        and isinstance(value.get("confidence"), str)
        and value.get("confidence") in {"LOW", "MEDIUM", "HIGH"}
    )


def recommendation_is_confirmation_ready(unknown: dict[str, object]) -> bool:
    recommendation = unknown.get("recommendation")
    options = unknown.get("options")
    return (
        unknown.get("response_mode") == "MUTUALLY_EXCLUSIVE"
        and _is_valid_options(unknown.get("response_mode"), options)
        and _recommendation_shape_is_valid(recommendation, options)
        and recommendation.get("confidence") == "HIGH"
    )


def derive_decision_authority(
    unknown: dict[str, object],
    *,
    evidence_index: dict[str, dict[str, object]],
) -> str:
    required_authority_class = unknown.get("required_authority_class")
    if (
        isinstance(required_authority_class, str)
        and _has_qualifying_evidence(
            unknown.get("evidence_refs"),
            evidence_index,
            required_authority_class,
        )
    ):
        return "EVIDENCE_RESOLVABLE"
    if (
        isinstance(required_authority_class, str)
        and required_authority_class in {"FACTUAL", "CONSTRAINT", "BEHAVIORAL"}
    ):
        return "EXTERNAL_AUTHORITY_REQUIRED"

    materiality = unknown.get("materiality")
    if isinstance(materiality, dict) and classify_materiality(materiality) == "NON_MATERIAL":
        return "AGENT_AUTONOMOUS"
    if isinstance(materiality, dict) and is_high_risk(materiality):
        return "USER_DECISION_REQUIRED"
    if recommendation_is_confirmation_ready(unknown):
        return "USER_CONFIRMATION"
    return "USER_DECISION_REQUIRED"


def question_priority_key(unknown: dict[str, object]) -> tuple[object, ...]:
    materiality = unknown["materiality"]
    return (
        -len(unknown["blocks_unknown_refs"]),
        not is_high_risk(materiality),
        _QUESTION_FAN_OUT_PRIORITY[materiality["fan_out"]],
        _QUESTION_CATEGORY_PRIORITY[unknown["question_category"]],
        unknown["id"],
    )


def project_user_question(unknown: dict[str, object]) -> dict[str, object]:
    return deepcopy({
        "unknown_id": unknown["id"],
        "question": unknown["question"],
        "why_it_matters": unknown["why_it_matters"],
        "evidence_refs": unknown["evidence_refs"],
        "affected_ids": unknown["affects"],
        "response_mode": unknown["response_mode"],
        "options": unknown["options"],
        "recommendation": unknown["recommendation"],
    })


def select_next_user_question(state: dict[str, object]) -> dict[str, object] | None:
    from state_validation_v2 import validate_state_v2

    errors = validate_state_v2(state)
    if errors:
        raise ValueError(errors)

    eligible = (
        unknown
        for unknown in state["objects"]["unknowns"]
        if unknown["status"] == "OPEN"
        and unknown["decision_authority"] in {"USER_CONFIRMATION", "USER_DECISION_REQUIRED"}
    )
    selected = min(eligible, key=question_priority_key, default=None)
    return None if selected is None else project_user_question(selected)


def validate_decision_authority_policy(
    state: dict[str, object],
    *,
    evidence_index: dict[str, dict[str, object]],
) -> list[dict[str, str]]:
    objects = state.get("objects")
    unknowns = objects.get("unknowns") if isinstance(objects, dict) else None
    if not isinstance(unknowns, list):
        return []

    errors: list[dict[str, str]] = []
    for position, unknown in enumerate(unknowns):
        if not isinstance(unknown, dict):
            continue
        status = unknown.get("status")
        if not isinstance(status, str) or status not in {"OPEN", "BLOCKED"}:
            continue
        derived = derive_decision_authority(unknown, evidence_index=evidence_index)
        if unknown.get("decision_authority") != derived:
            errors.append(_error(
                "invalid_decision_authority_derivation",
                f"decision_authority must equal deterministic derivation {derived}",
                f"objects.unknowns[{position}].decision_authority",
            ))
    return errors


def _recommendation_ref_is_current_and_permitted(
    reference: Any,
    *,
    required_authority_class: Any,
    id_index: dict[str, tuple[str, dict[str, object]]],
    evidence_index: dict[str, dict[str, object]],
) -> bool:
    if not isinstance(reference, str):
        return False
    evidence = evidence_index.get(reference)
    if evidence is not None:
        return (
            isinstance(required_authority_class, str)
            and _evidence_can_support(evidence, required_authority_class)
        )
    entry = id_index.get(reference)
    return (
        entry is not None
        and entry[0] in PRODUCT_AUTHORITY_GROUPS
        and entry[1].get("status") == "CURRENT"
    )


def _accepted_recommendation_is_valid(value: Any, unknowns: list[dict[str, object]]) -> bool:
    required = {
        "recommended_option", "alternatives_presented", "tradeoffs_presented",
        "accepted_by", "accepted_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        return False
    alternatives = value.get("alternatives_presented")
    tradeoffs = value.get("tradeoffs_presented")
    if (
        value.get("accepted_by") != "user"
        or not _meaningful_text(value.get("recommended_option"))
        or not _unique_strings(alternatives, nonempty=True)
        or not isinstance(tradeoffs, list)
        or not tradeoffs
        or any(not _meaningful_text(item) for item in tradeoffs)
        or not (value.get("accepted_at") is None or _meaningful_text(value.get("accepted_at")))
    ):
        return False
    if not unknowns:
        return False
    for unknown in unknowns:
        options = unknown.get("options")
        recommendation = unknown.get("recommendation")
        if not _recommendation_shape_is_valid(recommendation, options):
            return False
        option_ids = [option.get("id") for option in options if isinstance(option, dict)]
        if (
            value["recommended_option"] != recommendation["recommended_option"]
            or alternatives != option_ids
            or tradeoffs != recommendation["tradeoffs"]
        ):
            return False
    return True


def _validate_unknown_shape(
    unknown: dict[str, object],
    *,
    path: str,
    id_index: dict[str, tuple[str, dict[str, object]]],
    evidence_index: dict[str, dict[str, object]],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if (
        UNKNOWN_REQUIRED_FIELDS - set(unknown)
        or set(unknown) - UNKNOWN_REQUIRED_FIELDS - LIFECYCLE_FIELDS
    ):
        errors.append(_error(
            "invalid_unknown_contract",
            "unknown fields do not match the canonical M3 contract",
            path,
        ))

    status = unknown.get("status")
    if (
        not isinstance(status, str)
        or status not in UNKNOWN_STATUSES
        or not _meaningful_text(unknown.get("question"))
        or not _meaningful_text(unknown.get("why_it_matters"))
        or not isinstance(unknown.get("required_authority_class"), str)
        or unknown.get("required_authority_class") not in REQUIRED_AUTHORITY_CLASSES
        or not isinstance(unknown.get("question_category"), str)
        or unknown.get("question_category") not in QUESTION_CATEGORIES
        or not isinstance(unknown.get("decision_authority"), str)
        or unknown.get("decision_authority") not in DECISION_AUTHORITIES
        or not _is_valid_origin(unknown.get("origin"), id_index)
        or not _is_valid_options(unknown.get("response_mode"), unknown.get("options"))
        or not _unique_strings(unknown.get("affects"))
        or not _unique_strings(unknown.get("blocks_unknown_refs"))
        or not _unique_strings(unknown.get("evidence_refs"))
        or not _unique_strings(unknown.get("resolved_by"))
        or not (unknown.get("recommendation") is None or isinstance(unknown.get("recommendation"), dict))
    ):
        errors.append(_error("invalid_unknown_contract", "invalid unknown semantic shape", path))

    recommendation = unknown.get("recommendation")
    if recommendation is not None:
        if not _recommendation_shape_is_valid(recommendation, unknown.get("options")):
            errors.append(_error(
                "invalid_unknown_contract",
                "recommendation must match the canonical M3 structure",
                f"{path}.recommendation",
            ))
        else:
            reasoning_refs = recommendation["reasoning_refs"]
            if any(
                not _recommendation_ref_is_current_and_permitted(
                    reference,
                    required_authority_class=unknown.get("required_authority_class"),
                    id_index=id_index,
                    evidence_index=evidence_index,
                )
                for reference in reasoning_refs
            ):
                errors.append(_error(
                    "invalid_recommendation_reference",
                    "reasoning_refs must resolve to permitted current evidence or product authority",
                    f"{path}.recommendation.reasoning_refs",
                ))

    unknown_id = unknown.get("id")
    for field, expected_group in (("blocks_unknown_refs", "unknowns"), ("resolved_by", "decisions")):
        refs = unknown.get(field)
        if not isinstance(refs, list):
            continue
        for reference in refs:
            entry = id_index.get(reference) if isinstance(reference, str) else None
            target_status = entry[1].get("status") if entry is not None else None
            valid = entry is not None and entry[0] == expected_group
            if field == "blocks_unknown_refs":
                valid = valid and reference != unknown_id and target_status == "OPEN"
            if not valid:
                errors.append(_error(
                    "invalid_unknown_contract",
                    f"{field} must resolve to the required current record type",
                    f"{path}.{field}",
                ))

    affects = unknown.get("affects")
    if isinstance(affects, list) and any(
        not isinstance(reference, str) or reference not in id_index
        for reference in affects
    ):
        errors.append(_error(
            "invalid_unknown_contract", "affects refs must resolve to canonical IDs", f"{path}.affects",
        ))
    evidence_refs = unknown.get("evidence_refs")
    if isinstance(evidence_refs, list) and any(
        not isinstance(reference, str) or reference not in evidence_index
        for reference in evidence_refs
    ):
        errors.append(_error(
            "invalid_unknown_contract", "evidence_refs must resolve to EVD records", f"{path}.evidence_refs",
        ))

    mode = unknown.get("resolution_mode")
    summary = unknown.get("resolution_summary")
    resolved_by = unknown.get("resolved_by")
    if status == "RESOLVED":
        if (
            not isinstance(mode, str)
            or mode not in RESOLUTION_MODES
            or not _meaningful_text(summary)
        ):
            errors.append(_error(
                "unresolved_unknown_provenance",
                "RESOLVED requires a supported mode and meaningful summary",
                path,
            ))
        if unknown.get("deferral") is not None or unknown.get("blocked_reason") is not None:
            errors.append(_error("invalid_unknown_contract", "RESOLVED cannot carry deferral or block fields", path))
    elif mode is not None or summary is not None or resolved_by != []:
        errors.append(_error(
            "invalid_unknown_contract",
            "unresolved lifecycle states cannot carry resolution provenance",
            path,
        ))

    if status == "DEFERRED":
        if not _valid_deferral(unknown.get("deferral")):
            errors.append(_error(
                "invalid_unknown_deferral", "DEFERRED requires a full user-accepted impact review", path,
            ))
    elif unknown.get("deferral") is not None:
        errors.append(_error("invalid_unknown_contract", "deferral is only valid for DEFERRED", path))

    if status == "BLOCKED":
        if not _meaningful_text(unknown.get("blocked_reason")):
            errors.append(_error("invalid_unknown_block", "BLOCKED requires a meaningful reason", path))
    elif unknown.get("blocked_reason") is not None:
        errors.append(_error("invalid_unknown_contract", "blocked_reason is only valid for BLOCKED", path))
    return errors


def _validate_unknown_resolution(
    unknown: dict[str, object],
    *,
    path: str,
    id_index: dict[str, tuple[str, dict[str, object]]],
    evidence_index: dict[str, dict[str, object]],
) -> list[dict[str, str]]:
    if unknown.get("status") != "RESOLVED":
        return []
    errors: list[dict[str, str]] = []
    mode = unknown.get("resolution_mode")
    authority = unknown.get("decision_authority")
    if not isinstance(mode, str) or mode not in RESOLUTION_MODES:
        errors.append(_error(
            "invalid_unknown_resolution_authority",
            "resolution mode is not supported by deterministic authority policy",
            path,
        ))
        return errors
    expected_authority = MODE_AUTHORITIES.get(mode)
    if expected_authority is not None and authority != expected_authority:
        errors.append(_error(
            "invalid_unknown_resolution_authority",
            "resolution mode and decision authority do not match",
            path,
        ))
    if mode == "MIGRATION_RECONCILIATION":
        errors.append(_error(
            "invalid_unknown_resolution_authority",
            "migration reconciliation is not a completed authority mode",
            path,
        ))
        errors.append(_error(
            "unresolved_unknown_provenance",
            "migration reconciliation is a gap, not a completed resolution",
            path,
        ))
        return errors

    evidence_refs = unknown.get("evidence_refs")
    resolved_by = unknown.get("resolved_by")
    if mode == "EVIDENCE":
        if resolved_by != [] or not _has_qualifying_evidence(
            evidence_refs,
            evidence_index,
            unknown.get("required_authority_class") if isinstance(unknown.get("required_authority_class"), str) else "",
        ):
            errors.append(_error(
                "unresolved_unknown_provenance",
                "EVIDENCE resolution requires matching closure-eligible evidence and no decision",
                path,
            ))
    elif mode == "EXTERNAL_CONSTRAINT":
        if not _has_qualifying_evidence(
            evidence_refs, evidence_index, "CONSTRAINT", external_constraint=True,
        ):
            errors.append(_error(
                "unresolved_unknown_provenance",
                "EXTERNAL_CONSTRAINT requires current qualifying constraint evidence",
                path,
            ))
        if isinstance(resolved_by, list) and resolved_by:
            linked_decision = None
            if len(resolved_by) == 1 and isinstance(resolved_by[0], str):
                entry = id_index.get(resolved_by[0])
                if (
                    entry is not None
                    and entry[0] == "decisions"
                    and entry[1].get("status") == "CURRENT"
                ):
                    linked_decision = entry[1]
            source_refs = linked_decision.get("source_unknown_refs") if linked_decision else None
            if (
                linked_decision is None
                or not isinstance(source_refs, list)
                or unknown.get("id") not in source_refs
                or linked_decision.get("resolution_mode") != "EXTERNAL_CONSTRAINT"
                or linked_decision.get("decision_authority") != "EXTERNAL_AUTHORITY_REQUIRED"
                or linked_decision.get("decided_by") != "EXTERNAL_AUTHORITY"
                or not _has_qualifying_evidence(
                    linked_decision.get("evidence_refs"),
                    evidence_index,
                    "CONSTRAINT",
                    external_constraint=True,
                )
            ):
                errors.append(_error(
                    "unresolved_unknown_provenance",
                    "EXTERNAL_CONSTRAINT decision link must be one matching current externally-authorized decision",
                    path,
                ))
    elif isinstance(mode, str) and mode in {
        "USER_DECISION", "USER_ACCEPTED_RECOMMENDATION", "AGENT_NON_MATERIAL_DEFAULT",
    }:
        decisions = []
        if isinstance(resolved_by, list):
            for reference in resolved_by:
                entry = id_index.get(reference) if isinstance(reference, str) else None
                if entry is not None and entry[0] == "decisions" and entry[1].get("status") == "CURRENT":
                    decisions.append(entry[1])
        if (
            len(decisions) != 1
            or not isinstance(decisions[0].get("source_unknown_refs"), list)
            or unknown.get("id") not in decisions[0]["source_unknown_refs"]
            or decisions[0].get("resolution_mode") != mode
            or decisions[0].get("decision_authority") != authority
        ):
            errors.append(_error(
                "unresolved_unknown_provenance",
                "decision resolution requires exactly one matching current decision",
                path,
            ))

    if mode == "AGENT_NON_MATERIAL_DEFAULT" and isinstance(unknown.get("materiality"), dict):
        if classify_materiality(unknown["materiality"]) != "NON_MATERIAL":
            errors.append(_error(
                "unauthorized_agent_decision",
                "agent defaults may resolve only non-material unknowns",
                path,
            ))
    return errors


def _validate_decision(
    decision: dict[str, object],
    *,
    path: str,
    id_index: dict[str, tuple[str, dict[str, object]]],
    evidence_index: dict[str, dict[str, object]],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if (
        DECISION_REQUIRED_FIELDS - set(decision)
        or set(decision) - DECISION_REQUIRED_FIELDS - LIFECYCLE_FIELDS
    ):
        errors.append(_error(
            "invalid_decision_provenance",
            "decision fields do not match the canonical M3 contract",
            path,
        ))

    source_refs = decision.get("source_unknown_refs")
    evidence_refs = decision.get("evidence_refs")
    affects = decision.get("affects")
    if (
        not isinstance(decision.get("decided_by"), str)
        or decision.get("decided_by") not in {"USER", "AGENT", "EXTERNAL_AUTHORITY"}
        or not _unique_strings(source_refs)
        or not _unique_strings(evidence_refs)
        or not _unique_strings(affects)
    ):
        errors.append(_error("invalid_decision_provenance", "invalid decision provenance shape", path))

    source_unknowns: list[dict[str, object]] = []
    if isinstance(source_refs, list):
        for reference in source_refs:
            entry = id_index.get(reference) if isinstance(reference, str) else None
            if entry is None or entry[0] != "unknowns":
                errors.append(_error(
                    "invalid_decision_provenance",
                    "source_unknown_refs must resolve to unknowns",
                    f"{path}.source_unknown_refs",
                ))
            else:
                source_unknowns.append(entry[1])
    if isinstance(evidence_refs, list) and any(
        not isinstance(reference, str) or reference not in evidence_index
        for reference in evidence_refs
    ):
        errors.append(_error(
            "invalid_decision_provenance", "evidence_refs must resolve to evidence", f"{path}.evidence_refs",
        ))
    if isinstance(affects, list) and any(
        not isinstance(reference, str) or reference not in id_index
        for reference in affects
    ):
        errors.append(_error(
            "invalid_decision_provenance", "affects refs must resolve to canonical IDs", f"{path}.affects",
        ))

    mode = decision.get("resolution_mode")
    acceptance = decision.get("accepted_recommendation")
    if (
        (decision.get("status") == "CURRENT" or mode == "USER_ACCEPTED_RECOMMENDATION")
        and not _unique_strings(source_refs, nonempty=True)
    ):
        errors.append(_error(
            "invalid_decision_provenance",
            "current and recommendation-acceptance decisions require a source unknown",
            f"{path}.source_unknown_refs",
        ))
    if mode == "USER_ACCEPTED_RECOMMENDATION":
        if not _accepted_recommendation_is_valid(acceptance, source_unknowns):
            errors.append(_error(
                "invalid_recommendation_acceptance",
                "accepted recommendation must reproduce the presented option provenance",
                path,
            ))
    elif acceptance is not None:
        errors.append(_error(
            "invalid_recommendation_acceptance",
            "accepted_recommendation is only valid for USER_ACCEPTED_RECOMMENDATION",
            path,
        ))

    authority = decision.get("decision_authority")
    decision_id = decision.get("id")
    reciprocal_provenance_valid = (
        bool(source_unknowns)
        and _unique_strings(source_refs, nonempty=True)
        and len(source_unknowns) == len(source_refs)
        and all(
            unknown.get("status") == "RESOLVED"
            and unknown.get("resolution_mode") == mode
            and unknown.get("decision_authority") == authority
            and unknown.get("resolved_by") == [decision_id]
            for unknown in source_unknowns
        )
    )
    decision_materiality = decision.get("materiality")
    authorized_agent_decision = (
        decision.get("decided_by") == "AGENT"
        and decision.get("status") == "CURRENT"
        and mode == "AGENT_NON_MATERIAL_DEFAULT"
        and authority == "AGENT_AUTONOMOUS"
        and reciprocal_provenance_valid
        and isinstance(decision_materiality, dict)
        and classify_materiality(decision_materiality) == "NON_MATERIAL"
        and all(
            unknown.get("decision_authority") == "AGENT_AUTONOMOUS"
            and isinstance(unknown.get("materiality"), dict)
            and classify_materiality(unknown["materiality"]) == "NON_MATERIAL"
            for unknown in source_unknowns
        )
    )
    if decision.get("decided_by") == "AGENT" and not authorized_agent_decision:
        errors.append(_error(
            "unauthorized_agent_decision",
            "agent decisions require exact non-material authority and reciprocal provenance",
            path,
        ))

    if decision.get("status") != "CURRENT":
        return errors

    if not isinstance(mode, str) or mode not in DECISION_RESOLUTION_MODES:
        errors.append(_error(
            "invalid_decision_provenance",
            "evidence and migration reconciliation are not current decision modes",
            path,
        ))
        if isinstance(mode, str) and mode in {
            "EVIDENCE", "MIGRATION_RECONCILIATION",
        }:
            errors.append(_error(
                "invalid_unknown_resolution_authority",
                "evidence and migration reconciliation cannot authorize a current decision",
                path,
            ))
    expected_authority = MODE_AUTHORITIES.get(mode) if isinstance(mode, str) else None
    if expected_authority is not None and authority != expected_authority:
        errors.append(_error(
            "invalid_unknown_resolution_authority",
            "decision mode and authority do not match",
            path,
        ))
    for unknown in source_unknowns:
        if (
            unknown.get("status") != "RESOLVED"
            or unknown.get("resolution_mode") != mode
            or unknown.get("decision_authority") != authority
            or not isinstance(unknown.get("resolved_by"), list)
            or decision_id not in unknown["resolved_by"]
        ):
            errors.append(_error(
                "invalid_unknown_resolution_authority",
                "decision provenance must match every source unknown",
                path,
            ))

    if isinstance(mode, str) and mode in MODE_DECIDERS and decision.get("decided_by") != MODE_DECIDERS[mode]:
        errors.append(_error(
            "invalid_decision_provenance", "decided_by does not match resolution mode", path,
        ))

    if mode == "EXTERNAL_CONSTRAINT" and not _has_qualifying_evidence(
        evidence_refs, evidence_index, "CONSTRAINT", external_constraint=True,
    ):
        errors.append(_error(
            "invalid_decision_provenance",
            "external constraint decisions require qualifying constraint evidence",
            path,
        ))
    return errors


def _unknown_dependency_cycle_errors(state: dict[str, object]) -> list[dict[str, str]]:
    objects = state.get("objects")
    unknowns = objects.get("unknowns") if isinstance(objects, dict) else None
    if not isinstance(unknowns, list):
        return []
    graph = {
        unknown["id"]: list(unknown.get("blocks_unknown_refs", []))
        for unknown in unknowns
        if isinstance(unknown, dict)
        and isinstance(unknown.get("id"), str)
        and isinstance(unknown.get("blocks_unknown_refs"), list)
    }
    errors: list[dict[str, str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            cycle = trail[trail.index(node):] + [node]
            errors.append(_error("unknown_dependency_cycle", " -> ".join(cycle), "objects.unknowns"))
            return
        if node in visited:
            return
        visiting.add(node)
        trail.append(node)
        for target in graph.get(node, []):
            if isinstance(target, str) and target in graph:
                visit(target, trail)
        trail.pop()
        visiting.remove(node)
        visited.add(node)

    for unknown_id in graph:
        visit(unknown_id, [])
    return errors


def validate_unknown_decision_integrity(
    state: dict[str, object],
    *,
    id_index: dict[str, tuple[str, dict[str, object]]],
    evidence_index: dict[str, dict[str, object]],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    objects = state.get("objects")
    if not isinstance(objects, dict):
        return errors
    unknowns = objects.get("unknowns")
    if isinstance(unknowns, list):
        for position, unknown in enumerate(unknowns):
            path = f"objects.unknowns[{position}]"
            if not isinstance(unknown, dict):
                errors.append(_error("invalid_unknown_contract", "unknown must be an object", path))
                continue
            errors.extend(_validate_unknown_shape(
                unknown, path=path, id_index=id_index, evidence_index=evidence_index,
            ))
            errors.extend(_validate_unknown_resolution(
                unknown, path=path, id_index=id_index, evidence_index=evidence_index,
            ))
    decisions = objects.get("decisions")
    if isinstance(decisions, list):
        for position, decision in enumerate(decisions):
            path = f"objects.decisions[{position}]"
            if not isinstance(decision, dict):
                errors.append(_error("invalid_decision_provenance", "decision must be an object", path))
                continue
            errors.extend(_validate_decision(
                decision, path=path, id_index=id_index, evidence_index=evidence_index,
            ))
    errors.extend(_unknown_dependency_cycle_errors(state))
    return errors


def canonical_pack_digest(pack: dict[str, object]) -> str:
    canonical = json.dumps(
        pack,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_pack_contract(pack: object, *, source: Path) -> dict[str, object]:
    if not isinstance(pack, dict) or set(pack) != {"pack_id", "version", "activation", "axes"}:
        raise ValueError(f"invalid Grill Pack object: {source}")
    pack_id = pack.get("pack_id")
    if not isinstance(pack_id, str) or pack_id not in PACK_AXIS_ORDER:
        raise ValueError(f"invalid Grill Pack identity: {source}")
    if pack.get("version") != "1.0" or "digest" in pack:
        raise ValueError(f"invalid Grill Pack version or stored digest: {source}")

    activation = pack.get("activation")
    if not isinstance(activation, dict) or set(activation) != {
        "always", "surface_kinds", "topology_tags",
    }:
        raise ValueError(f"invalid Grill Pack activation metadata: {source}")
    expected_domain = next(
        (domain for domain, identity in DOMAIN_PACK_IDS.items() if identity == pack_id),
        None,
    )
    expected_tags = [] if expected_domain is None else [expected_domain]
    if (
        activation.get("always") is not (pack_id == "GRILL-CORE-1")
        or activation.get("surface_kinds") != list(PACK_SURFACE_KIND_METADATA[pack_id])
        or activation.get("topology_tags") != expected_tags
    ):
        raise ValueError(f"Grill Pack activation metadata drift: {source}")

    axes = pack.get("axes")
    if not isinstance(axes, list):
        raise ValueError(f"invalid Grill Pack axes: {source}")
    axis_ids: list[str] = []
    for axis in axes:
        if (
            not isinstance(axis, dict)
            or set(axis) != {
                "id", "description", "independent_decision", "materiality_floor",
            }
            or not isinstance(axis.get("id"), str)
            or not _meaningful_text(axis.get("description"))
            or axis.get("independent_decision") is not True
            or axis.get("materiality_floor") not in {"INHERIT", "MATERIAL"}
        ):
            raise ValueError(f"invalid Grill Pack axis: {source}")
        axis_ids.append(axis["id"])
    if tuple(axis_ids) != PACK_AXIS_ORDER[pack_id] or len(axis_ids) != len(set(axis_ids)):
        raise ValueError(f"Grill Pack axis inventory drift: {source}")
    material_axes = {
        axis["id"] for axis in axes if axis["materiality_floor"] == "MATERIAL"
    }
    if material_axes != PACK_MATERIAL_FLOORS[pack_id]:
        raise ValueError(f"Grill Pack materiality floor drift: {source}")
    return pack


def load_grill_packs(pack_dir: Path = PACK_DIR) -> dict[str, dict[str, object]]:
    directory = Path(pack_dir)
    loaded: dict[str, dict[str, object]] = {}
    for source in sorted(directory.glob("*.json"), key=lambda path: path.name):
        if source.name == "grill-pack.schema.json":
            continue
        try:
            parsed = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"cannot load Grill Pack: {source}") from error
        pack = _validate_pack_contract(parsed, source=source)
        pack_id = pack["pack_id"]
        if pack_id in loaded:
            raise ValueError(f"duplicate Grill Pack identity: {pack_id}")
        loaded[pack_id] = pack
    if set(loaded) != set(PACK_AXIS_ORDER):
        raise ValueError("the checked-in Grill Pack authority set must contain exactly seven packs")
    return {pack_id: loaded[pack_id] for pack_id in sorted(loaded)}


def _grill_indexes(
    state: dict[str, object],
) -> tuple[
    dict[str, tuple[str, dict[str, object]]],
    dict[str, dict[str, object]],
    dict[str, dict[str, object]],
]:
    index: dict[str, tuple[str, dict[str, object]]] = {}
    objects = state.get("objects")
    if isinstance(objects, dict):
        for group, records in objects.items():
            if not isinstance(records, list):
                continue
            for record in records:
                if isinstance(record, dict) and isinstance(record.get("id"), str):
                    index[record["id"]] = (group, record)
    evidence_index: dict[str, dict[str, object]] = {}
    evidence = state.get("evidence")
    if isinstance(evidence, list):
        for record in evidence:
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                evidence_index[record["id"]] = record
                index[record["id"]] = ("evidence", record)
    surfaces: dict[str, dict[str, object]] = {}
    manifest = state.get("surface_manifest")
    records = manifest.get("records") if isinstance(manifest, dict) else None
    if isinstance(records, list):
        for record in records:
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                surfaces[record["id"]] = record
                index[record["id"]] = ("surfaces", record)
    return index, evidence_index, surfaces


def _surface_is_current(record: object) -> bool:
    if not isinstance(record, dict):
        return False
    status = record.get("status")
    return isinstance(status, str) and status not in {"SUPERSEDED", "RETIRED"}


def _basis_ref_is_current(
    reference: object,
    *,
    index: dict[str, tuple[str, dict[str, object]]],
    topology_profile: bool,
) -> bool:
    if not isinstance(reference, str) or reference not in index:
        return False
    group, record = index[reference]
    if group == "evidence":
        source_kind = record.get("source_kind")
        return (
            record.get("status") == "CURRENT"
            and isinstance(source_kind, str)
            and source_kind not in CANDIDATE_ONLY_SOURCE_KINDS
        )
    if group == "surfaces":
        return _surface_is_current(record)
    if group == "decisions":
        return record.get("status") == "CURRENT"
    return not topology_profile and record.get("status") == "CURRENT" and group != "unknowns"


def _profile_analysis(
    state: dict[str, object],
) -> tuple[list[dict[str, str]], int, dict[str, tuple[str, ...]]]:
    errors: list[dict[str, str]] = []
    gaps = 0
    valid_active: dict[str, tuple[str, ...]] = {}
    index, _, surfaces = _grill_indexes(state)
    manifest = state.get("surface_manifest")
    profile = manifest.get("grill_profile") if isinstance(manifest, dict) else None
    forced_refs: dict[str, set[str]] = {domain: set() for domain in GRILL_PROFILE_DOMAINS}
    for surface_id, surface in surfaces.items():
        if not _surface_is_current(surface):
            continue
        surface_kind = surface.get("kind")
        domain = (
            FORCED_SURFACE_KIND_DOMAINS.get(surface_kind)
            if isinstance(surface_kind, str)
            else None
        )
        if domain is not None:
            forced_refs[domain].add(surface_id)
    if not isinstance(profile, dict):
        errors = [_error(
            "invalid_grill_profile",
            "surface_manifest.grill_profile must contain all six topology domains",
            "surface_manifest.grill_profile",
        )]
        for domain, references in forced_refs.items():
            if references:
                errors.append(_error(
                    "grill_topology_contradiction",
                    "forced current surface kinds require an ACTIVE topology profile cell",
                    f"surface_manifest.grill_profile.{domain}",
                ))
        return errors, len(GRILL_PROFILE_DOMAINS), {}

    expected_domains = set(GRILL_PROFILE_DOMAINS)
    missing = expected_domains - set(profile)
    extra = set(profile) - expected_domains
    if missing or extra:
        errors.append(_error(
            "invalid_grill_profile",
            "grill_profile keys must exactly equal the six topology domains",
            "surface_manifest.grill_profile",
        ))
        gaps += len(missing) + len(extra)

    for domain in GRILL_PROFILE_DOMAINS:
        if domain not in profile:
            if forced_refs[domain]:
                errors.append(_error(
                    "grill_topology_contradiction",
                    "forced current surface kinds require an ACTIVE topology profile cell",
                    f"surface_manifest.grill_profile.{domain}",
                ))
            continue
        path = f"surface_manifest.grill_profile.{domain}"
        cell = profile[domain]
        cell_valid = True
        if not isinstance(cell, dict) or set(cell) != GRILL_PROFILE_CELL_KEYS:
            errors.append(_error(
                "invalid_grill_profile",
                "topology profile cells must use the exact M3 shape",
                path,
            ))
            if forced_refs[domain]:
                errors.append(_error(
                    "grill_topology_contradiction",
                    "forced current surface kinds require an ACTIVE topology profile cell",
                    path,
                ))
            gaps += 1
            continue

        status = cell.get("status")
        surface_refs = cell.get("surface_refs")
        unknown_refs = cell.get("unknown_refs")
        basis_refs = cell.get("basis_refs")
        if (
            not isinstance(status, str)
            or status not in {"ACTIVE", "N/A", "OPEN"}
            or not _unique_strings(surface_refs)
            or not _unique_strings(unknown_refs)
            or not _unique_strings(basis_refs)
        ):
            cell_valid = False

        current_surface_refs = (
            isinstance(surface_refs, list)
            and all(
                isinstance(reference, str)
                and reference in surfaces
                and _surface_is_current(surfaces[reference])
                for reference in surface_refs
            )
        )
        current_basis_refs = (
            isinstance(basis_refs, list)
            and all(
                _basis_ref_is_current(reference, index=index, topology_profile=True)
                for reference in basis_refs
            )
        )
        if not current_surface_refs or not current_basis_refs:
            cell_valid = False

        if status == "ACTIVE":
            if not surface_refs or unknown_refs != [] or cell.get("rationale") is not None:
                cell_valid = False
        elif status == "N/A":
            if (
                surface_refs != []
                or unknown_refs != []
                or not basis_refs
                or not _meaningful_text(cell.get("rationale"))
            ):
                cell_valid = False
        elif status == "OPEN":
            pack_id = DOMAIN_PACK_IDS[domain]
            if not unknown_refs or cell.get("rationale") is not None:
                cell_valid = False
            elif any(
                not isinstance(reference, str)
                or reference not in index
                or index[reference][0] != "unknowns"
                or index[reference][1].get("status") != "OPEN"
                or index[reference][1].get("origin") != {
                    "kind": "GRILL_TOPOLOGY",
                    "surface_ref": None,
                    "pack_id": pack_id,
                    "axis_id": None,
                    "source_path": None,
                }
                for reference in unknown_refs
            ):
                cell_valid = False

        forced = forced_refs[domain]
        forced_contradiction = bool(forced) and (
            status != "ACTIVE"
            or not _unique_strings(surface_refs)
            or not forced.issubset(set(surface_refs))
        )
        if forced_contradiction:
            errors.append(_error(
                "grill_topology_contradiction",
                "forced current surface kinds require ACTIVE and every forced surface ref",
                path,
            ))
            cell_valid = False

        if not cell_valid:
            errors.append(_error(
                "invalid_grill_profile",
                "topology profile cell does not satisfy its declared status",
                path,
            ))
            gaps += 1
        elif status == "OPEN":
            gaps += 1
        elif status == "ACTIVE":
            valid_active[domain] = tuple(sorted(set(surface_refs)))
    return errors, gaps, valid_active


def _core_target_refs(state: dict[str, object]) -> list[str]:
    objects = state.get("objects")
    requirements = objects.get("requirements") if isinstance(objects, dict) else None
    if not isinstance(requirements, list):
        return []
    targets = []
    for requirement in requirements:
        if (
            isinstance(requirement, dict)
            and isinstance(requirement.get("id"), str)
            and requirement.get("status") == "CURRENT"
            and isinstance(requirement.get("materiality"), dict)
        ):
            try:
                is_material = classify_materiality(requirement["materiality"]) == "MATERIAL"
            except (KeyError, TypeError, ValueError):
                is_material = False
            if is_material:
                targets.append(requirement["id"])
    return sorted(set(targets))


def _compile_active_grill_packs(
    state: dict[str, object],
    packs: dict[str, dict[str, object]],
    valid_active: dict[str, tuple[str, ...]],
) -> list[dict[str, object]]:
    instances = [{
        "pack_id": "GRILL-CORE-1",
        "version": packs["GRILL-CORE-1"]["version"],
        "digest": canonical_pack_digest(packs["GRILL-CORE-1"]),
        "target_refs": _core_target_refs(state),
    }]
    for domain, target_refs in valid_active.items():
        pack_id = DOMAIN_PACK_IDS[domain]
        pack = packs[pack_id]
        instances.append({
            "pack_id": pack_id,
            "version": pack["version"],
            "digest": canonical_pack_digest(pack),
            "target_refs": list(target_refs),
        })
    return sorted(instances, key=lambda instance: instance["pack_id"])


def compile_active_grill_packs(state: dict[str, object]) -> list[dict[str, object]]:
    packs = load_grill_packs()
    _, _, valid_active = _profile_analysis(state)
    return _compile_active_grill_packs(state, packs, valid_active)


def _current_product_authority(
    reference: object,
    index: dict[str, tuple[str, dict[str, object]]],
) -> bool:
    if not isinstance(reference, str) or reference not in index:
        return False
    group, record = index[reference]
    return group in PRODUCT_AUTHORITY_GROUPS and record.get("status") == "CURRENT"


def _coverage_analysis(
    state: dict[str, object],
    packs: dict[str, dict[str, object]],
    profile_gaps: int,
    valid_active: dict[str, tuple[str, ...]],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    errors: list[dict[str, str]] = []
    active_gaps = profile_gaps
    unresolved_axes = 0
    umbrella_violations = 0
    materiality_floor_violations = 0
    index, _, surfaces = _grill_indexes(state)
    instances = _compile_active_grill_packs(state, packs, valid_active)

    coverage = state.get("coverage")
    coverage = coverage if isinstance(coverage, list) else []
    core_rows: dict[str, list[tuple[int, dict[str, object]]]] = {}
    for position, row in enumerate(coverage):
        if isinstance(row, dict) and isinstance(row.get("feature_id"), str):
            core_rows.setdefault(row["feature_id"], []).append((position, row))
    core_targets = next(
        instance["target_refs"] for instance in instances if instance["pack_id"] == "GRILL-CORE-1"
    )
    for target_ref in core_targets:
        rows = core_rows.get(target_ref, [])
        if not rows:
            errors.append(_error(
                "missing_core_grill_coverage",
                "current material requirement requires one Core Grill coverage row",
                f"coverage.{target_ref}",
            ))
            active_gaps += 1
            continue
        if len(rows) != 1:
            errors.append(_error(
                "duplicate_core_grill_coverage",
                "current material requirement requires exactly one Core Grill coverage row",
                f"coverage.{target_ref}",
            ))
            active_gaps += 1
        position, row = rows[0]
        cells = row.get("cells")
        if not isinstance(cells, dict) or set(cells) != set(CORE_GRILL_AXES):
            errors.append(_error(
                "core_grill_axis_inventory_mismatch",
                "Core Grill coverage cells must exactly equal the frozen 20 axes",
                f"coverage[{position}].cells",
            ))
            active_gaps += 1
            continue
        unresolved_axes += sum(
            isinstance(cell, dict) and cell.get("status") == "OPEN"
            for cell in cells.values()
        )

    grill_coverage = state.get("grill_coverage")
    grill_coverage = grill_coverage if isinstance(grill_coverage, list) else []
    required_pairs = {
        (target_ref, instance["pack_id"]): instance
        for instance in instances
        if instance["pack_id"] != "GRILL-CORE-1"
        for target_ref in instance["target_refs"]
    }
    row_groups: dict[tuple[str, str], list[tuple[int, dict[str, object]]]] = {}
    row_keys = {"target_ref", "pack_id", "pack_version", "pack_digest", "axes"}
    for position, row in enumerate(grill_coverage):
        path = f"grill_coverage[{position}]"
        if not isinstance(row, dict) or set(row) != row_keys:
            errors.append(_error(
                "invalid_grill_coverage",
                "specialist coverage rows must use the exact M3 shape",
                path,
            ))
            continue
        target_ref = row.get("target_ref")
        pack_id = row.get("pack_id")
        if not isinstance(target_ref, str) or not isinstance(pack_id, str):
            errors.append(_error("invalid_grill_coverage", "invalid specialist row identity", path))
            continue
        pair = (target_ref, pack_id)
        row_groups.setdefault(pair, []).append((position, row))
        if (
            pack_id not in SPECIALIST_PACK_IDS
            or target_ref not in surfaces
            or not _surface_is_current(surfaces[target_ref])
            or pair not in required_pairs
        ):
            errors.append(_error(
                "invalid_grill_coverage",
                "specialist coverage must target a current ACTIVE pack instance",
                path,
            ))

    independent_open_axes: list[
        tuple[int, str, str, str, list[object], dict[str, object]]
    ] = []
    for pair, instance in sorted(required_pairs.items()):
        target_ref, pack_id = pair
        rows = row_groups.get(pair, [])
        if not rows:
            errors.append(_error(
                "missing_grill_coverage",
                "ACTIVE specialist pack target requires one coverage row",
                f"grill_coverage.{pack_id}.{target_ref}",
            ))
            active_gaps += 1
            continue
        if len(rows) != 1:
            errors.append(_error(
                "duplicate_grill_coverage",
                "specialist coverage permits one row per target and pack",
                f"grill_coverage.{pack_id}.{target_ref}",
            ))
            active_gaps += 1
        position, row = rows[0]
        path = f"grill_coverage[{position}]"
        identity_valid = (
            row.get("pack_version") == instance["version"]
            and row.get("pack_digest") == instance["digest"]
        )
        if not identity_valid:
            errors.append(_error(
                "grill_pack_identity_mismatch",
                "coverage pack version and digest must match checked-in authority",
                path,
            ))
            active_gaps += 1
        axes = row.get("axes")
        expected_axes = set(PACK_AXIS_ORDER[pack_id])
        if not isinstance(axes, dict):
            errors.append(_error(
                "grill_pack_axis_inventory_mismatch",
                "specialist row axes must exactly equal the activated pack definition",
                f"{path}.axes",
            ))
            active_gaps += 1
            continue
        if set(axes) != expected_axes:
            errors.append(_error(
                "grill_pack_axis_inventory_mismatch",
                "specialist row axes must exactly equal the activated pack definition",
                f"{path}.axes",
            ))
            active_gaps += 1

        pack_axis_defs = {
            axis["id"]: axis for axis in packs[pack_id]["axes"]
        }
        for axis_id in PACK_AXIS_ORDER[pack_id]:
            if axis_id not in axes:
                continue
            cell_path = f"{path}.axes.{axis_id}"
            cell = axes[axis_id]
            if not isinstance(cell, dict) or set(cell) != GRILL_AXIS_CELL_KEYS:
                errors.append(_error(
                    "invalid_grill_axis_coverage",
                    "specialist axis coverage must use the exact M3 shape",
                    cell_path,
                ))
                continue
            status = cell.get("status")
            authority_refs = cell.get("authority_refs")
            unknown_refs = cell.get("unknown_refs")
            basis_refs = cell.get("basis_refs")
            lists_valid = all(
                _unique_strings(value)
                for value in (authority_refs, unknown_refs, basis_refs)
            )
            if (
                not isinstance(status, str)
                or status not in {"ADDRESSED", "OPEN", "N/A"}
                or not lists_valid
            ):
                errors.append(_error(
                    "invalid_grill_axis_coverage",
                    "invalid specialist axis status or reference arrays",
                    cell_path,
                ))
                continue

            if status == "ADDRESSED":
                if (
                    not authority_refs
                    or unknown_refs != []
                    or basis_refs != []
                    or cell.get("rationale") is not None
                    or any(not _current_product_authority(ref, index) for ref in authority_refs)
                ):
                    errors.append(_error(
                        "invalid_grill_axis_authority",
                        "ADDRESSED requires broad current canonical product authority",
                        cell_path,
                    ))
            elif status == "N/A":
                if (
                    authority_refs != []
                    or unknown_refs != []
                    or not basis_refs
                    or not _meaningful_text(cell.get("rationale"))
                    or any(
                        not _basis_ref_is_current(ref, index=index, topology_profile=False)
                        for ref in basis_refs
                    )
                ):
                    errors.append(_error(
                        "invalid_grill_axis_basis",
                        "N/A requires meaningful rationale and current basis authority",
                        cell_path,
                    ))
            else:
                unresolved_axes += 1
                unknowns_valid = (
                    bool(unknown_refs)
                    and all(
                        isinstance(ref, str)
                        and ref in index
                        and index[ref][0] == "unknowns"
                        and index[ref][1].get("status") == "OPEN"
                        for ref in unknown_refs
                    )
                )
                if (
                    authority_refs != []
                    or basis_refs != []
                    or cell.get("rationale") is not None
                    or not unknowns_valid
                ):
                    errors.append(_error(
                        "invalid_grill_axis_unknown",
                        "OPEN requires one or more current OPEN unknown refs",
                        cell_path,
                    ))
                if pack_axis_defs[axis_id].get("independent_decision") is True:
                    independent_open_axes.append((
                        position,
                        target_ref,
                        pack_id,
                        axis_id,
                        list(unknown_refs) if isinstance(unknown_refs, list) else [],
                        pack_axis_defs[axis_id],
                    ))

    origin_usage: dict[str, int] = {}
    for _, _, _, _, refs, _ in independent_open_axes:
        for reference in refs:
            if isinstance(reference, str):
                origin_usage[reference] = origin_usage.get(reference, 0) + 1
    for position, target_ref, pack_id, axis_id, refs, axis_definition in independent_open_axes:
        cell_path = f"grill_coverage[{position}].axes.{axis_id}"
        origin_unknown = None
        if len(refs) == 1 and isinstance(refs[0], str):
            entry = index.get(refs[0])
            if entry is not None and entry[0] == "unknowns" and entry[1].get("status") == "OPEN":
                origin_unknown = entry[1]
        exact_origin = {
            "kind": "GRILL_PACK_AXIS",
            "surface_ref": target_ref,
            "pack_id": pack_id,
            "axis_id": axis_id,
            "source_path": None,
        }
        origin_valid = (
            origin_unknown is not None
            and origin_unknown.get("origin") == exact_origin
            and origin_usage.get(refs[0], 0) == 1
        )
        if not origin_valid:
            umbrella_violations += 1
            errors.append(_error(
                "umbrella_unknown_compression",
                "independent OPEN axes require one unique exact-origin unknown",
                cell_path,
            ))
        if axis_definition.get("materiality_floor") == "MATERIAL":
            material = False
            if origin_valid and origin_unknown is not None:
                materiality_value = origin_unknown.get("materiality")
                try:
                    material = (
                        isinstance(materiality_value, dict)
                        and classify_materiality(materiality_value) == "MATERIAL"
                    )
                except (KeyError, TypeError, ValueError):
                    material = False
            if not material:
                materiality_floor_violations += 1
                errors.append(_error(
                    "pack_materiality_floor_violation",
                    "MATERIAL-floor OPEN axis requires a MATERIAL origin unknown",
                    cell_path,
                ))

    return errors, {
        "active_grill_pack_gaps": active_gaps,
        "unresolved_pack_axes": unresolved_axes,
        "umbrella_unknown_compression": umbrella_violations,
        "pack_materiality_floor_violations": materiality_floor_violations,
    }


def validate_grill_coverage(state: dict[str, object]) -> list[dict[str, str]]:
    packs = load_grill_packs()
    profile_errors, profile_gaps, valid_active = _profile_analysis(state)
    coverage_errors, _ = _coverage_analysis(
        state,
        packs,
        profile_gaps,
        valid_active,
    )
    return profile_errors + coverage_errors


def grill_pack_metrics(state: dict[str, object]) -> dict[str, int]:
    packs = load_grill_packs()
    _, profile_gaps, valid_active = _profile_analysis(state)
    _, metrics = _coverage_analysis(
        state,
        packs,
        profile_gaps,
        valid_active,
    )
    return metrics


def grill_unknown_metrics(state: dict[str, object]) -> dict[str, int]:
    objects = state.get("objects")
    unknowns = objects.get("unknowns") if isinstance(objects, dict) else None
    decisions = objects.get("decisions") if isinstance(objects, dict) else None
    unknowns = unknowns if isinstance(unknowns, list) else []
    decisions = decisions if isinstance(decisions, list) else []

    id_index: dict[str, tuple[str, dict[str, object]]] = {}
    for group, records in (("unknowns", unknowns), ("decisions", decisions)):
        for record in records:
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                id_index[record["id"]] = (group, record)
    evidence = state.get("evidence")
    evidence_index = {
        record["id"]: record
        for record in evidence if isinstance(record, dict) and isinstance(record.get("id"), str)
    } if isinstance(evidence, list) else {}
    integrity_errors = validate_unknown_decision_integrity(
        state, id_index=id_index, evidence_index=evidence_index,
    )
    integrity_errors.extend(validate_decision_authority_policy(
        state, evidence_index=evidence_index,
    ))

    def recomputed_material(record: object) -> bool:
        return (
            isinstance(record, dict)
            and isinstance(record.get("materiality"), dict)
            and classify_materiality(record["materiality"]) == "MATERIAL"
        )

    def unique_error_records(code: str, *, group: str | None = None) -> int:
        return len({
            error["path"].split(".", 2)[1]
            for error in integrity_errors
            if error["code"] == code
            and error["path"].startswith(f"objects.{group}" if group else "objects.")
        })

    return {
        "open_material_unknowns": sum(
            isinstance(unknown, dict) and unknown.get("status") == "OPEN" and recomputed_material(unknown)
            for unknown in unknowns
        ),
        "blocked_material_unknowns": sum(
            isinstance(unknown, dict) and unknown.get("status") == "BLOCKED" and recomputed_material(unknown)
            for unknown in unknowns
        ),
        "deferred_unknowns": sum(
            isinstance(unknown, dict) and unknown.get("status") == "DEFERRED"
            for unknown in unknowns
        ),
        "unresolved_unknown_provenance": unique_error_records("unresolved_unknown_provenance"),
        "invalid_resolution_authority": len({
            error["path"].split(".", 2)[1]
            for error in integrity_errors
            if error["code"] in {
                "invalid_unknown_resolution_authority",
                "invalid_decision_authority_derivation",
                "unauthorized_agent_decision",
            }
            and error["path"].startswith("objects.")
        }),
        "unauthorized_agent_decisions": unique_error_records(
            "unauthorized_agent_decision", group="decisions",
        ),
        "missing_required_user_decisions": sum(
            isinstance(unknown, dict)
            and unknown.get("status") == "OPEN"
            and derive_decision_authority(
                unknown, evidence_index=evidence_index,
            ) in {"USER_CONFIRMATION", "USER_DECISION_REQUIRED"}
            for unknown in unknowns
        ),
    }
