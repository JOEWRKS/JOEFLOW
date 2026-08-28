from __future__ import annotations

from typing import Any

from materiality_v2 import classify_materiality


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
    return entry is not None and entry[1].get("status") not in {"SUPERSEDED", "RETIRED"}


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
    expected_authority = MODE_AUTHORITIES.get(mode) if isinstance(mode, str) else None
    if expected_authority is not None and authority != expected_authority:
        errors.append(_error(
            "invalid_unknown_resolution_authority",
            "resolution mode and decision authority do not match",
            path,
        ))
    if mode == "MIGRATION_RECONCILIATION":
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

    if decision.get("status") != "CURRENT":
        return errors
    if not source_refs:
        errors.append(_error(
            "invalid_decision_provenance", "current decisions require a source unknown", path,
        ))

    authority = decision.get("decision_authority")
    if not isinstance(mode, str) or mode not in DECISION_RESOLUTION_MODES:
        errors.append(_error(
            "invalid_decision_provenance",
            "evidence and migration reconciliation are not current decision modes",
            path,
        ))
    expected_authority = MODE_AUTHORITIES.get(mode) if isinstance(mode, str) else None
    if expected_authority is not None and authority != expected_authority:
        errors.append(_error(
            "invalid_unknown_resolution_authority",
            "decision mode and authority do not match",
            path,
        ))
    decision_id = decision.get("id")
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

    if mode == "AGENT_NON_MATERIAL_DEFAULT":
        decision_materiality = decision.get("materiality")
        material_decision = (
            not isinstance(decision_materiality, dict)
            or classify_materiality(decision_materiality) != "NON_MATERIAL"
            or any(
                not isinstance(unknown.get("materiality"), dict)
                or classify_materiality(unknown["materiality"]) != "NON_MATERIAL"
                for unknown in source_unknowns
            )
        )
        if material_decision:
            errors.append(_error(
                "unauthorized_agent_decision",
                "material decisions may not use AGENT_NON_MATERIAL_DEFAULT",
                path,
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
        "invalid_resolution_authority": unique_error_records("invalid_unknown_resolution_authority"),
        "unauthorized_agent_decisions": unique_error_records(
            "unauthorized_agent_decision", group="decisions",
        ),
        "missing_required_user_decisions": sum(
            isinstance(unknown, dict)
            and unknown.get("status") == "OPEN"
            and isinstance(unknown.get("decision_authority"), str)
            and unknown.get("decision_authority") in {"USER_CONFIRMATION", "USER_DECISION_REQUIRED"}
            for unknown in unknowns
        ),
    }
