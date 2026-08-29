from __future__ import annotations

from typing import Any

from authority_binding_v2 import (
    BindingError,
    binding_contract_identity,
    validate_authority_graph_references,
    validate_product_coverage_bindings,
    validate_ux_coverage_bindings,
)
from approval_v2 import (
    approval_manifest_digest,
    approval_metrics,
    compute_approval_manifest,
    definition_digest,
    semantic_readiness_metrics,
    validate_approval,
)
from discovery_v2 import validate_discovery_baseline
from grill_v2 import (
    grill_unknown_metrics,
    validate_decision_authority_policy,
    validate_grill_coverage,
    validate_unknown_decision_integrity,
)
from materiality_v2 import validate_materiality_classification


SCHEMA_VERSION = "0.2.0"
ROOT_KEYS = {
    "schema_version", "project", "migration", "evidence", "surface_manifest",
    "contradictions", "objects", "coverage", "ux_coverage", "grill_coverage",
    "discovery_baseline", "approval", "approval_history",
}
PROJECT_KEYS = {"slug", "definition_status", "definition_revision", "bootstrap_mode", "closure_contract"}
OBJECT_GROUPS = {
    "goals", "users", "requirements", "unknowns", "decisions", "rules",
    "flows", "screens", "states", "data", "integrations",
    "acceptance_criteria", "tasks",
}
DEFINITION_STATUSES = {"OPEN", "READY_FOR_REVIEW", "CLOSED", "BLOCKED"}
NORMAL_AUTHORITY_STATUSES = {"CURRENT", "STALE", "SUPERSEDED", "RETIRED"}
UNKNOWN_STATUSES = {"OPEN", "RESOLVED", "DEFERRED", "BLOCKED", "SUPERSEDED", "RETIRED"}
EVIDENCE_STATUSES = {"CURRENT", "STALE", "SUPERSEDED", "UNAVAILABLE"}
STALE_CONSUMED_EVIDENCE_STATUSES = {"STALE", "SUPERSEDED", "UNAVAILABLE"}
EVIDENCE_CONFIDENCE = {"DIRECT", "CORROBORATED", "INFERRED"}
EVIDENCE_AUTHORITY_CLASSES = {"FACTUAL", "INTENT", "CONSTRAINT", "BEHAVIORAL", "PREFERENCE"}
CONTRADICTION_STATUSES = {"OPEN", "RESOLVED", "SUPERSEDED", "RETIRED"}
SURFACE_KINDS = {
    "ACTOR", "FEATURE_AREA", "ENTRY_POINT", "MAJOR_ACTION", "DOMAIN_ENTITY",
    "INTEGRATION", "ASYNC_PROCESS", "NOTIFICATION", "PERSISTENT_STATE",
    "SENSITIVE_DATA", "PERMISSION", "MONEY_FLOW", "DESTRUCTIVE_OPERATION",
    "LIFECYCLE_OBJECT",
}
SURFACE_STATUSES = {"IN_SCOPE", "OUT_OF_SCOPE", "OPEN", "SUPERSEDED", "RETIRED"}
SURFACE_AUTHORITY_PREFIXES = {"REQ", "RULE", "FLOW", "DATA", "INT"}
BOOTSTRAP_MODES = {"NEW_PRODUCT", "EXISTING_PRODUCT_RECONCILIATION"}
INTENT_CLASSIFICATIONS = {"AUTHORITATIVE", "OBSERVED_ONLY", "CONFLICTING", "UNEXPLAINED"}
OBSERVED_SOURCE_KINDS = {"OBSERVED_IMPLEMENTATION", "OBSERVED_RUNTIME", "TEST_ASSERTION"}
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
CANDIDATE_ONLY_SOURCE_KINDS = {"INFERRED_INTENT", "DESIGN_ARTIFACT"}
GROUP_PREFIXES = {
    "goals": "GOAL", "users": "USR", "requirements": "REQ",
    "unknowns": "UNK", "decisions": "DEC", "rules": "RULE",
    "flows": "FLOW", "screens": "SCR", "states": "STATE",
    "data": "DATA", "integrations": "INT",
    "acceptance_criteria": "AC", "tasks": "TASK",
}
TYPE_MINIMA = {
    "goals": frozenset({"statement"}),
    "users": frozenset({"description", "actor_kind"}),
    "requirements": frozenset({"statement", "scope", "ui_required", "materiality"}),
    "unknowns": frozenset({
        "question", "why_it_matters", "required_authority_class", "question_category",
        "materiality", "decision_authority", "affects", "blocks_unknown_refs",
        "origin", "response_mode", "options", "recommendation", "evidence_refs",
        "resolved_by", "resolution_mode", "resolution_summary", "deferral", "blocked_reason",
    }),
    "decisions": frozenset({
        "statement", "decision_type", "resolution_mode", "decision_authority",
        "source_unknown_refs", "evidence_refs", "materiality", "affects",
        "decided_by", "accepted_recommendation",
    }),
    "rules": frozenset({"statement", "applies_to"}),
    "flows": frozenset({"goal_refs", "entry", "preconditions", "paths", "outcomes"}),
    "screens": frozenset({"purpose", "requirement_refs", "interaction_mode", "major_actions"}),
    "states": frozenset({"owner_refs", "state_name", "conditions"}),
    "data": frozenset({"name", "purpose", "ownership"}),
    "integrations": frozenset({"name", "purpose"}),
    "acceptance_criteria": frozenset({"requirement_refs", "assertion"}),
    "tasks": frozenset({"implements", "acceptance_refs"}),
}
MIGRATION_APPLY_VERSION = "0.2.0-m6.1"
MIGRATION_FIELDS = {
    "mode", "from_schema", "to_schema", "migration_version", "source_digest",
    "source_revision", "source_legacy_status", "source_legacy_approval_digest",
    "plan_digest", "preserved_ids", "promoted_ids", "generated_ids",
    "legacy_records", "reconciliation_gaps", "reconciliation_gap_count",
}
MIGRATION_LEGACY_RECORD_FIELDS = {
    "source_id", "source_group", "source_record", "source_record_sha256",
}
MIGRATION_GAP_FIELDS = {
    "source_id", "source_path", "missing_v2_fields", "reason_code",
}

_LIFECYCLE_FIELDS = {"superseded_by", "retired_by", "retired_at_revision", "retirement_reason"}
_TEXT_FIELDS = {
    "statement", "description", "actor_kind", "scope", "question",
    "decision_authority", "decision_type", "entry",
    "purpose", "interaction_mode", "state_name", "name", "ownership", "assertion",
}
_ARRAY_FIELDS = {
    "source_unknown_refs", "evidence_refs", "affects", "applies_to", "goal_refs",
    "preconditions", "paths", "outcomes", "requirement_refs", "major_actions",
    "owner_refs", "conditions", "implements", "acceptance_refs",
}
_DECISION_AUTHORITIES = {
    "EVIDENCE_RESOLVABLE", "AGENT_AUTONOMOUS", "USER_CONFIRMATION",
    "USER_DECISION_REQUIRED", "EXTERNAL_AUTHORITY_REQUIRED",
}
_RESOLUTION_MODES = {
    "EVIDENCE", "USER_DECISION", "USER_ACCEPTED_RECOMMENDATION",
    "AGENT_NON_MATERIAL_DEFAULT", "EXTERNAL_CONSTRAINT", "MIGRATION_RECONCILIATION",
}
_MATERIALITY_KEYS = {
    "outcome_divergence", "fan_out", "user_visible", "reversibility",
    "risk_flags", "classification",
}
_RISK_FLAG_KEYS = {
    "security", "privacy", "money", "legal_or_policy", "destructive",
    "data_loss", "external_commitment",
}
_MEANINGLESS = {"none", "false", "n/a", "na", "later", "tbd"}

SEMANTIC_READINESS_BLOCKING_METRICS = frozenset({
    "open_material_surfaces",
    "unbound_material_surfaces",
    "unresolved_material_contradictions",
    "stale_selected_authority",
    "stale_consumed_evidence",
    "discovery_baseline_gaps",
    "unassessed_materiality",
    "open_material_unknowns",
    "blocked_material_unknowns",
    "unresolved_unknown_provenance",
    "invalid_resolution_authority",
    "unauthorized_agent_decisions",
    "missing_required_user_decisions",
    "active_grill_pack_gaps",
    "unresolved_pack_axes",
    "umbrella_unknown_compression",
    "pack_materiality_floor_violations",
    "invalid_authority_binding",
    "stale_authority_binding",
    "coverage_without_authority",
    "open_coverage_without_unknown",
    "unjustified_na_without_basis",
    "invalid_coverage_authority_type",
    "core_coverage_gaps",
    "specialist_binding_gaps",
    "ux_coverage_gaps",
    "screen_state_gaps",
    "screen_action_inventory_gaps",
    "ux_invalid_authority_binding",
    "ux_stale_authority_binding",
    "ux_open_without_unknown",
    "ux_unjustified_na",
    "orphan_material_authority",
    "unconsumed_material_decision",
    "requirement_acceptance_gaps",
    "task_mapping_gaps",
    "invalid_authority_graph_reference",
    "semantic_change_without_revision_increment",
    "approved_record_missing_from_state",
    "minimum_definition_gaps",
    "discovery_procedure_gaps",
})

APPROVAL_BLOCKING_METRICS = frozenset({
    "missing_user_approval",
    "stale_approval",
    "missing_or_stale_approval_manifest",
    "approval_history_gaps",
    "semantic_change_without_revision_increment",
    "approved_record_missing_from_state",
})

CLOSURE_BLOCKING_METRICS = (
    SEMANTIC_READINESS_BLOCKING_METRICS | APPROVAL_BLOCKING_METRICS
)


def _error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _is_stable_id(value: Any, *, expected_prefix: str | None = None) -> bool:
    if not isinstance(value, str) or "-" not in value:
        return False
    prefix, number = value.rsplit("-", 1)
    return (
        bool(prefix)
        and prefix.isascii()
        and prefix.isalpha()
        and prefix.isupper()
        and (expected_prefix is None or prefix == expected_prefix)
        and len(number) >= 3
        and number.isascii()
        and number.isdigit()
    )


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_migration_metadata(state: dict[str, Any]) -> list[dict[str, str]]:
    migration = state.get("migration")
    if not isinstance(migration, dict):
        return [_error("schema_error", "migration must be an object", "migration")]
    if migration == {"mode": "NATIVE"}:
        return []
    if set(migration) != MIGRATION_FIELDS or migration.get("mode") != "MIGRATED":
        return [_error(
            "schema_error",
            "migrated metadata fields do not match the 0.2.0 M6 contract",
            "migration",
        )]

    errors: list[dict[str, str]] = []
    exact_values = {
        "from_schema": "0.1.2.1",
        "to_schema": "0.2.0",
        "migration_version": MIGRATION_APPLY_VERSION,
    }
    for field, expected in exact_values.items():
        if migration.get(field) != expected:
            errors.append(_error(
                "schema_error", f"migration.{field} has the wrong value", f"migration.{field}"
            ))
    for field in ("source_digest", "plan_digest"):
        if not _is_sha256(migration.get(field)):
            errors.append(_error(
                "schema_error", f"migration.{field} must be lowercase sha256", f"migration.{field}"
            ))
    approval_digest = migration.get("source_legacy_approval_digest")
    if approval_digest is not None and not _is_sha256(approval_digest):
        errors.append(_error(
            "schema_error",
            "migration.source_legacy_approval_digest must be lowercase sha256 or null",
            "migration.source_legacy_approval_digest",
        ))
    revision = migration.get("source_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append(_error(
            "schema_error", "migration.source_revision must be a positive integer",
            "migration.source_revision",
        ))
    if migration.get("source_legacy_status") not in DEFINITION_STATUSES:
        errors.append(_error(
            "schema_error", "migration.source_legacy_status is invalid",
            "migration.source_legacy_status",
        ))

    for field in ("preserved_ids", "promoted_ids", "generated_ids"):
        values = migration.get(field)
        if (
            not isinstance(values, list)
            or values != sorted(values)
            or len(values) != len(set(values))
            or any(not _is_stable_id(value) for value in values)
        ):
            errors.append(_error(
                "schema_error", f"migration.{field} must be sorted unique stable ids",
                f"migration.{field}",
            ))

    legacy_records = migration.get("legacy_records")
    if not isinstance(legacy_records, list):
        errors.append(_error(
            "schema_error", "migration.legacy_records must be an array",
            "migration.legacy_records",
        ))
    else:
        for position, record in enumerate(legacy_records):
            path = f"migration.legacy_records[{position}]"
            if (
                not isinstance(record, dict)
                or set(record) != MIGRATION_LEGACY_RECORD_FIELDS
                or not (
                    record.get("source_id") is None
                    or _is_stable_id(record.get("source_id"))
                )
                or record.get("source_group") not in OBJECT_GROUPS | {"contradictions"}
                or not isinstance(record.get("source_record"), dict)
                or not _is_sha256(record.get("source_record_sha256"))
            ):
                errors.append(_error(
                    "schema_error", "legacy archive entry has invalid shape", path
                ))

    gaps = migration.get("reconciliation_gaps")
    if not isinstance(gaps, dict):
        errors.append(_error(
            "schema_error", "migration.reconciliation_gaps must be an object",
            "migration.reconciliation_gaps",
        ))
    else:
        for key, gap in gaps.items():
            path = f"migration.reconciliation_gaps.{key}"
            valid_key = (
                isinstance(key, str)
                and key.startswith("gap:")
                and len(key) == 28
                and all(character in "0123456789abcdef" for character in key[4:])
            )
            if (
                not valid_key
                or not isinstance(gap, dict)
                or set(gap) != MIGRATION_GAP_FIELDS
                or not (gap.get("source_id") is None or _is_stable_id(gap.get("source_id")))
                or not isinstance(gap.get("source_path"), str)
                or not gap["source_path"].startswith("/")
                or not isinstance(gap.get("missing_v2_fields"), list)
                or gap["missing_v2_fields"] != sorted(set(gap["missing_v2_fields"]))
                or not gap["missing_v2_fields"]
                or any(not isinstance(field, str) or not field for field in gap["missing_v2_fields"])
                or gap.get("reason_code") != "MISSING_V2_SEMANTIC_AUTHORITY"
            ):
                errors.append(_error(
                    "schema_error", "reconciliation gap has invalid shape", path
                ))
    gap_count = migration.get("reconciliation_gap_count")
    if (
        not isinstance(gap_count, int)
        or isinstance(gap_count, bool)
        or not isinstance(gaps, dict)
        or gap_count != len(gaps)
    ):
        errors.append(_error(
            "schema_error", "migration.reconciliation_gap_count must equal gap count",
            "migration.reconciliation_gap_count",
        ))
    return errors


def _iter_records(state: dict[str, Any]):
    objects = state.get("objects")
    if not isinstance(objects, dict):
        return
    for group in TYPE_MINIMA:
        records = objects.get(group)
        if not isinstance(records, list):
            continue
        for position, record in enumerate(records):
            yield group, position, record


def _collect_ids(
    state: dict[str, Any],
) -> tuple[dict[str, tuple[str, dict[str, Any]]], list[dict[str, str]]]:
    index: dict[str, tuple[str, dict[str, Any]]] = {}
    errors: list[dict[str, str]] = []

    def add_reserved(record: Any, path: str) -> None:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            return
        object_id = record["id"]
        if object_id in index:
            errors.append(_error("duplicate_id", f"duplicate id {object_id}", f"{path}.id"))
        else:
            index[object_id] = ("reserved", record)

    for group, position, record in _iter_records(state):
        if not isinstance(record, dict):
            continue
        path = f"objects.{group}[{position}].id"
        object_id = record.get("id")
        if not _is_stable_id(object_id):
            errors.append(_error("invalid_id", "object id must use PREFIX-NNN form", path))
            continue
        prefix = object_id.split("-", 1)[0]
        if prefix != GROUP_PREFIXES[group]:
            errors.append(_error("invalid_id_type", f"objects.{group} requires {GROUP_PREFIXES[group]}-* ids", path))
        if object_id in index:
            errors.append(_error("duplicate_id", f"duplicate id {object_id}", path))
        else:
            index[object_id] = (group, record)

    contradictions = state.get("contradictions")
    if isinstance(contradictions, list):
        for position, record in enumerate(contradictions):
            add_reserved(record, f"contradictions[{position}]")
    evidence = state.get("evidence")
    if isinstance(evidence, list):
        for position, record in enumerate(evidence):
            add_reserved(record, f"evidence[{position}]")
    surface_manifest = state.get("surface_manifest")
    if isinstance(surface_manifest, dict) and isinstance(surface_manifest.get("records"), list):
        for position, record in enumerate(surface_manifest["records"]):
            add_reserved(record, f"surface_manifest.records[{position}]")
    return index, errors


def _collect_evidence(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    evidence = state.get("evidence")
    if not isinstance(evidence, list):
        return {}
    return {
        record["id"]: record
        for record in evidence
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }


def _collect_surfaces(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    surface_manifest = state.get("surface_manifest")
    records = surface_manifest.get("records") if isinstance(surface_manifest, dict) else None
    if not isinstance(records, list):
        return {}
    return {
        record["id"]: record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }


def _collect_contradictions(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contradictions = state.get("contradictions")
    if not isinstance(contradictions, list):
        return {}
    return {
        record["id"]: record
        for record in contradictions
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }


def _evidence_is_current_closure_eligible(record: dict[str, Any]) -> bool:
    authority_classes = record.get("authority_classes")
    source_kind = record.get("source_kind")
    return (
        record.get("status") == "CURRENT"
        and isinstance(source_kind, str)
        and source_kind not in CANDIDATE_ONLY_SOURCE_KINDS
        and isinstance(authority_classes, list)
        and bool(authority_classes)
        and all(isinstance(authority_class, str) for authority_class in authority_classes)
    )


def _evidence_can_support(
    record: dict[str, Any], authority_class: str, *, for_closure: bool,
) -> bool:
    source_kind = record.get("source_kind")
    authority_classes = record.get("authority_classes")
    if (
        not isinstance(source_kind, str)
        or source_kind not in SOURCE_KIND_CAPABILITIES
        or not isinstance(authority_classes, list)
        or authority_class not in authority_classes
        or authority_class not in SOURCE_KIND_CAPABILITIES[source_kind]
    ):
        return False
    return not for_closure or _evidence_is_current_closure_eligible(record)


def _validate_evidence(state: dict[str, Any]) -> list[dict[str, str]]:
    evidence = state.get("evidence")
    if not isinstance(evidence, list):
        return []

    evidence_index = _collect_evidence(state)
    errors: list[dict[str, str]] = []
    allowed_fields = {
        "id", "status", "source_kind", "locator", "claim", "confidence",
        "authority_classes", "observed_version", "content_hash",
        "superseded_by", "unavailable_reason",
    }
    required_fields = allowed_fields - {"superseded_by", "unavailable_reason"}

    for position, record in enumerate(evidence):
        path = f"evidence[{position}]"
        if not isinstance(record, dict):
            errors.append(_error("invalid_evidence_shape", "evidence record must be an object", path))
            continue
        if set(record) - allowed_fields or required_fields - set(record):
            errors.append(_error("invalid_evidence_shape", "evidence fields do not match the 0.2.0 contract", path))

        evidence_id = record.get("id")
        if not _is_stable_id(evidence_id, expected_prefix="EVD"):
            errors.append(_error("invalid_evidence_id", "evidence id must use EVD-NNN form", f"{path}.id"))

        status = record.get("status")
        source_kind = record.get("source_kind")
        confidence = record.get("confidence")
        authority_classes = record.get("authority_classes")
        shape_valid = (
            isinstance(status, str)
            and status in EVIDENCE_STATUSES
            and isinstance(source_kind, str)
            and source_kind in SOURCE_KIND_CAPABILITIES
            and isinstance(confidence, str)
            and confidence in EVIDENCE_CONFIDENCE
            and _meaningful_text(record.get("locator"))
            and _meaningful_text(record.get("claim"))
            and isinstance(authority_classes, list)
            and bool(authority_classes)
            and all(isinstance(authority_class, str) for authority_class in authority_classes)
            and len(authority_classes) == len(set(authority_classes))
            and all(authority_class in EVIDENCE_AUTHORITY_CLASSES for authority_class in authority_classes)
            and all(
                value is None or _meaningful_text(value)
                for value in (record.get("observed_version"), record.get("content_hash"))
            )
        )
        if not shape_valid:
            errors.append(_error("invalid_evidence_shape", "invalid evidence semantic shape", path))

        if isinstance(source_kind, str) and source_kind in SOURCE_KIND_CAPABILITIES and isinstance(authority_classes, list):
            if any(
                not isinstance(authority_class, str)
                or authority_class not in SOURCE_KIND_CAPABILITIES[source_kind]
                for authority_class in authority_classes
            ):
                errors.append(_error("invalid_evidence_authority_class", "authority class is not supported by source kind", f"{path}.authority_classes"))

        if status == "SUPERSEDED":
            target_id = record.get("superseded_by")
            target = evidence_index.get(target_id) if isinstance(target_id, str) else None
            if (
                not _is_stable_id(target_id, expected_prefix="EVD")
                or target_id == evidence_id
                or target is None
                or target.get("status") != "CURRENT"
            ):
                errors.append(_error("invalid_evidence_supersession", "SUPERSEDED requires a different current EVD-* superseded_by target", path))
        if status == "UNAVAILABLE" and not _meaningful_text(record.get("unavailable_reason")):
            errors.append(_error("invalid_evidence_unavailable", "UNAVAILABLE requires a meaningful unavailable_reason", path))

    graph = {
        record["id"]: record["superseded_by"]
        for record in evidence
        if isinstance(record, dict)
        and record.get("status") == "SUPERSEDED"
        and isinstance(record.get("id"), str)
        and isinstance(record.get("superseded_by"), str)
    }
    visited: set[str] = set()
    for start in graph:
        trail: list[str] = []
        current = start
        while current in graph and current not in visited:
            if current in trail:
                cycle = trail[trail.index(current):] + [current]
                errors.append(_error("evidence_supersession_cycle", " -> ".join(cycle), "evidence"))
                break
            trail.append(current)
            current = graph[current]
        visited.update(trail)
    return errors


def _surface_has_current_authority(
    record: dict[str, Any], id_index: dict[str, tuple[str, dict[str, Any]]],
) -> bool:
    authority_refs = record.get("authority_refs")
    if not isinstance(authority_refs, list):
        return False
    for authority_ref in authority_refs:
        target_entry = id_index.get(authority_ref) if isinstance(authority_ref, str) else None
        if target_entry is None:
            continue
        group, target = target_entry
        prefix = authority_ref.split("-", 1)[0]
        if (
            group != "reserved"
            and prefix in SURFACE_AUTHORITY_PREFIXES
            and target.get("status") == "CURRENT"
        ):
            return True
    return False


def _validate_surface_manifest(
    state: dict[str, Any],
    id_index: dict[str, tuple[str, dict[str, Any]]],
    evidence_index: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    surface_manifest = state.get("surface_manifest")
    if (
        not isinstance(surface_manifest, dict)
        or set(surface_manifest) != {"records", "grill_profile"}
        or not isinstance(surface_manifest.get("records"), list)
    ):
        return [_error(
            "invalid_surface_manifest",
            "surface_manifest must contain records and the complete Grill Topology Profile",
            "surface_manifest",
        )]
    records = surface_manifest["records"]

    errors: list[dict[str, str]] = []
    surfaces = _collect_surfaces(state)
    contradictions = _collect_contradictions(state)
    allowed_fields = {
        "id", "kind", "name", "status", "materiality", "evidence_refs",
        "authority_refs", "unknown_refs", "decision_refs", "contradiction_refs",
        "rationale", "intent_classification", "superseded_by", "retired_by",
        "retired_at_revision", "retirement_reason",
    }
    required_fields = allowed_fields - _LIFECYCLE_FIELDS
    project = state.get("project")
    project_revision = project.get("definition_revision") if isinstance(project, dict) else None
    bootstrap_mode = project.get("bootstrap_mode") if isinstance(project, dict) else None

    for position, record in enumerate(records):
        path = f"surface_manifest.records[{position}]"
        if not isinstance(record, dict):
            errors.append(_error("invalid_surface_shape", "surface record must be an object", path))
            continue
        if set(record) - allowed_fields or required_fields - set(record):
            errors.append(_error("invalid_surface_shape", "surface fields do not match the 0.2.0 contract", path))

        surface_id = record.get("id")
        if not _is_stable_id(surface_id, expected_prefix="SURF"):
            errors.append(_error("invalid_surface_id", "surface id must use SURF-NNN form", f"{path}.id"))

        shape_valid = (
            isinstance(record.get("kind"), str)
            and record["kind"] in SURFACE_KINDS
            and isinstance(record.get("status"), str)
            and record["status"] in SURFACE_STATUSES
            and _meaningful_text(record.get("name"))
            and all(
                isinstance(record.get(field), list)
                and all(isinstance(value, str) for value in record[field])
                and len(record[field]) == len(set(record[field]))
                for field in (
                    "evidence_refs", "authority_refs", "unknown_refs", "decision_refs",
                    "contradiction_refs",
                )
            )
            and (record.get("rationale") is None or _meaningful_text(record.get("rationale")))
            and (
                record.get("intent_classification") is None
                or (
                    isinstance(record.get("intent_classification"), str)
                    and record["intent_classification"] in INTENT_CLASSIFICATIONS
                )
            )
        )
        if not shape_valid:
            errors.append(_error("invalid_surface_shape", "invalid surface semantic shape", path))
        if "materiality" in record:
            errors.extend(_validate_materiality(record["materiality"], f"{path}.materiality"))

        reference_specs = (
            ("evidence_refs", "EVD", lambda reference: reference in evidence_index),
            ("authority_refs", None, lambda reference: (
                reference in id_index
                and id_index[reference][0] != "reserved"
                and reference.split("-", 1)[0] in SURFACE_AUTHORITY_PREFIXES
            )),
            ("unknown_refs", "UNK", lambda reference: (
                reference in id_index and id_index[reference][0] == "unknowns"
            )),
            ("decision_refs", "DEC", lambda reference: (
                reference in id_index and id_index[reference][0] == "decisions"
            )),
            ("contradiction_refs", "CON", lambda reference: (
                reference in id_index and id_index[reference][0] == "reserved"
            )),
        )
        for field, expected_prefix, resolves in reference_specs:
            values = record.get(field)
            if not isinstance(values, list):
                continue
            for reference in values:
                if (
                    not _is_stable_id(reference, expected_prefix=expected_prefix)
                    if expected_prefix is not None
                    else not _is_stable_id(reference)
                ) or not resolves(reference):
                    errors.append(_error("invalid_surface_reference", f"{field} must resolve to its required record type", f"{path}.{field}"))

        status = record.get("status")
        materiality = record.get("materiality")
        is_material = isinstance(materiality, dict) and materiality.get("classification") == "MATERIAL"
        intent_classification = record.get("intent_classification")
        evidence_refs = record.get("evidence_refs")
        decision_refs = record.get("decision_refs")
        has_open_unknown = isinstance(record.get("unknown_refs"), list) and any(
            (entry := id_index.get(reference)) is not None
            and entry[0] == "unknowns"
            and entry[1].get("status") == "OPEN"
            for reference in record["unknown_refs"]
            if isinstance(reference, str)
        )
        has_closure_capable_intent_evidence = isinstance(evidence_refs, list) and any(
            (evidence := evidence_index.get(reference)) is not None
            and (
                _evidence_can_support(evidence, "INTENT", for_closure=True)
                or _evidence_can_support(evidence, "PREFERENCE", for_closure=True)
            )
            for reference in evidence_refs
            if isinstance(reference, str)
        )
        has_observed_evidence = isinstance(evidence_refs, list) and any(
            (evidence := evidence_index.get(reference)) is not None
            and isinstance(evidence.get("source_kind"), str)
            and evidence.get("source_kind") in OBSERVED_SOURCE_KINDS
            for reference in evidence_refs
            if isinstance(reference, str)
        )
        has_current_decision = isinstance(decision_refs, list) and any(
            (entry := id_index.get(reference)) is not None
            and entry[0] == "decisions"
            and entry[1].get("status") == "CURRENT"
            for reference in decision_refs
            if isinstance(reference, str)
        )
        has_contradiction = isinstance(record.get("contradiction_refs"), list) and any(
            reference in contradictions
            for reference in record["contradiction_refs"]
            if isinstance(reference, str)
        )
        if bootstrap_mode == "NEW_PRODUCT" and intent_classification is not None:
            errors.append(_error("invalid_surface_intent_classification", "NEW_PRODUCT surfaces require a null intent_classification", f"{path}.intent_classification"))
        elif bootstrap_mode == "EXISTING_PRODUCT_RECONCILIATION":
            if not isinstance(intent_classification, str) or intent_classification not in INTENT_CLASSIFICATIONS:
                errors.append(_error("invalid_surface_intent_classification", "existing-product surfaces require an exact intent_classification", f"{path}.intent_classification"))
            elif intent_classification == "AUTHORITATIVE" and (
                not record.get("authority_refs")
                or not (has_closure_capable_intent_evidence or has_current_decision)
            ):
                errors.append(_error("invalid_authoritative_surface", "AUTHORITATIVE requires an authority ref and current closure-capable intent or preference evidence or a current decision", path))
            elif intent_classification == "OBSERVED_ONLY" and (
                not has_observed_evidence or (is_material and not has_open_unknown)
            ):
                errors.append(_error("invalid_observed_only_surface", "OBSERVED_ONLY requires observed evidence and an OPEN unknown when material", path))
            elif intent_classification == "CONFLICTING" and not has_contradiction:
                errors.append(_error("invalid_conflicting_surface", "CONFLICTING requires a CON-* contradiction ref", path))
            elif intent_classification == "UNEXPLAINED" and (
                (is_material and not has_open_unknown) or has_closure_capable_intent_evidence
            ):
                errors.append(_error("invalid_unexplained_surface", "UNEXPLAINED cannot have authoritative intent evidence and requires an OPEN unknown when material", path))
        if status == "IN_SCOPE" and is_material and not _surface_has_current_authority(record, id_index):
            errors.append(_error("UNBOUND_PRODUCT_SURFACE", "material IN_SCOPE surface requires a current typed authority reference", path))
        if status == "OPEN" and is_material:
            if not has_open_unknown:
                errors.append(_error("OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN", "material OPEN surface requires an OPEN UNK-* reference", path))
        if status == "OUT_OF_SCOPE":
            if not _meaningful_text(record.get("rationale")) or not (has_closure_capable_intent_evidence or has_current_decision):
                errors.append(_error("invalid_out_of_scope_surface", "OUT_OF_SCOPE requires rationale and closure-capable intent evidence or a current decision", path))
        if status == "SUPERSEDED":
            target = record.get("superseded_by")
            target_entry = surfaces.get(target) if isinstance(target, str) else None
            if (
                not _is_stable_id(target, expected_prefix="SURF")
                or target == surface_id
                or target_entry is None
            ):
                errors.append(_error("invalid_surface_supersession", "SUPERSEDED requires a different existing SURF-* superseded_by target", path))
        if status == "RETIRED":
            retired_by = record.get("retired_by")
            target_entry = id_index.get(retired_by) if isinstance(retired_by, str) else None
            retired_at_revision = record.get("retired_at_revision")
            if (
                not _is_stable_id(retired_by, expected_prefix="DEC")
                or target_entry is None
                or target_entry[0] != "decisions"
                or not isinstance(retired_at_revision, int)
                or isinstance(retired_at_revision, bool)
                or retired_at_revision < 1
                or not isinstance(project_revision, int)
                or retired_at_revision > project_revision
                or not _meaningful_text(record.get("retirement_reason"))
            ):
                errors.append(_error("invalid_surface_retirement", "RETIRED requires decision provenance, a valid revision, and a meaningful reason", path))

    graph = {
        record["id"]: record["superseded_by"]
        for record in records
        if isinstance(record, dict)
        and record.get("status") == "SUPERSEDED"
        and isinstance(record.get("id"), str)
        and isinstance(record.get("superseded_by"), str)
    }
    visited: set[str] = set()
    for start in graph:
        trail: list[str] = []
        current = start
        while current in graph and current not in visited:
            if current in trail:
                cycle = trail[trail.index(current):] + [current]
                errors.append(_error("surface_supersession_cycle", " -> ".join(cycle), "surface_manifest"))
                break
            trail.append(current)
            current = graph[current]
        visited.update(trail)
    return errors


def _validate_contradictions(
    state: dict[str, Any],
    id_index: dict[str, tuple[str, dict[str, Any]]],
    evidence_index: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    contradictions = state.get("contradictions")
    if not isinstance(contradictions, list):
        return []

    errors: list[dict[str, str]] = []
    contradiction_index = _collect_contradictions(state)
    allowed_fields = {
        "id", "status", "claim_a_refs", "claim_b_refs", "scope_refs",
        "materiality", "resolution", "resolved_by", "selected_authority_refs",
        "superseded_by", "retired_by", "retired_at_revision", "retirement_reason",
    }
    required_fields = allowed_fields - _LIFECYCLE_FIELDS
    project = state.get("project")
    project_revision = project.get("definition_revision") if isinstance(project, dict) else None

    for position, record in enumerate(contradictions):
        path = f"contradictions[{position}]"
        if not isinstance(record, dict):
            errors.append(_error("invalid_contradiction_shape", "contradiction record must be an object", path))
            continue
        if set(record) - allowed_fields or required_fields - set(record):
            errors.append(_error("invalid_contradiction_shape", "contradiction fields do not match the 0.2.0 contract", path))

        contradiction_id = record.get("id")
        if not _is_stable_id(contradiction_id, expected_prefix="CON"):
            errors.append(_error("invalid_contradiction_id", "contradiction id must use CON-NNN form", f"{path}.id"))

        shape_valid = (
            isinstance(record.get("status"), str)
            and record["status"] in CONTRADICTION_STATUSES
            and all(
                isinstance(record.get(field), list)
                and all(isinstance(value, str) for value in record[field])
                and len(record[field]) == len(set(record[field]))
                and (field not in {"claim_a_refs", "claim_b_refs", "scope_refs"} or bool(record[field]))
                for field in (
                    "claim_a_refs", "claim_b_refs", "scope_refs", "resolved_by",
                    "selected_authority_refs",
                )
            )
            and (
                record.get("resolution") is None
                or (isinstance(record.get("resolution"), str) and bool(record["resolution"]))
            )
        )
        if not shape_valid:
            errors.append(_error("invalid_contradiction_shape", "invalid contradiction semantic shape", path))
        if "materiality" in record:
            errors.extend(_validate_materiality(record["materiality"], f"{path}.materiality"))

        for field in ("claim_a_refs", "claim_b_refs"):
            values = record.get(field)
            if not isinstance(values, list):
                continue
            for reference in values:
                if (
                    not _is_stable_id(reference, expected_prefix="EVD")
                    or reference not in evidence_index
                ):
                    errors.append(_error("invalid_contradiction_reference", f"{field} must resolve to EVD-* evidence", f"{path}.{field}"))

        scope_refs = record.get("scope_refs")
        if isinstance(scope_refs, list):
            for reference in scope_refs:
                if not _is_stable_id(reference) or reference not in id_index:
                    errors.append(_error("invalid_contradiction_reference", "scope_refs must resolve to existing stable ids", f"{path}.scope_refs"))

        resolved_by = record.get("resolved_by")
        current_decisions = []
        if isinstance(resolved_by, list):
            for reference in resolved_by:
                target_entry = id_index.get(reference) if isinstance(reference, str) else None
                if (
                    not _is_stable_id(reference, expected_prefix="DEC")
                    or target_entry is None
                    or target_entry[0] != "decisions"
                ):
                    errors.append(_error("invalid_contradiction_reference", "resolved_by must resolve to DEC-* decisions", f"{path}.resolved_by"))
                elif target_entry[1].get("status") == "CURRENT":
                    current_decisions.append(reference)

        selected_authority_refs = record.get("selected_authority_refs")
        selected_authorities = []
        if isinstance(selected_authority_refs, list):
            for reference in selected_authority_refs:
                evidence = evidence_index.get(reference) if isinstance(reference, str) else None
                if not _is_stable_id(reference, expected_prefix="EVD") or evidence is None:
                    errors.append(_error("invalid_contradiction_reference", "selected_authority_refs must resolve to EVD-* evidence", f"{path}.selected_authority_refs"))
                elif evidence.get("status") != "CURRENT":
                    errors.append(_error("invalid_selected_authority", "selected authority must be current evidence", f"{path}.selected_authority_refs"))
                elif (
                    isinstance(evidence.get("source_kind"), str)
                    and evidence.get("source_kind") in CANDIDATE_ONLY_SOURCE_KINDS
                ):
                    continue
                elif _evidence_is_current_closure_eligible(evidence):
                    selected_authorities.append(reference)
                else:
                    errors.append(_error("invalid_selected_authority", "selected authority must be current closure-eligible evidence", f"{path}.selected_authority_refs"))

        if record.get("status") == "RESOLVED":
            if not _meaningful_text(record.get("resolution")):
                errors.append(_error("invalid_contradiction_resolution", "RESOLVED requires a meaningful resolution", f"{path}.resolution"))
            if not current_decisions and not selected_authorities:
                errors.append(_error("unresolved_contradiction_authority", "RESOLVED requires a current decision or selected authority", path))

        if record.get("status") == "SUPERSEDED":
            target = record.get("superseded_by")
            if (
                not _is_stable_id(target, expected_prefix="CON")
                or target == contradiction_id
                or target not in contradiction_index
            ):
                errors.append(_error("invalid_contradiction_supersession", "SUPERSEDED requires a different existing CON-* target", path))
        if record.get("status") == "RETIRED":
            retired_by = record.get("retired_by")
            target_entry = id_index.get(retired_by) if isinstance(retired_by, str) else None
            retired_at_revision = record.get("retired_at_revision")
            if (
                not _is_stable_id(retired_by, expected_prefix="DEC")
                or target_entry is None
                or target_entry[0] != "decisions"
                or not isinstance(retired_at_revision, int)
                or isinstance(retired_at_revision, bool)
                or retired_at_revision < 1
                or not isinstance(project_revision, int)
                or retired_at_revision > project_revision
                or not _meaningful_text(record.get("retirement_reason"))
            ):
                errors.append(_error("invalid_contradiction_retirement", "RETIRED requires decision provenance, a valid revision, and a meaningful reason", path))

    graph = {
        record["id"]: record["superseded_by"]
        for record in contradictions
        if isinstance(record, dict)
        and record.get("status") == "SUPERSEDED"
        and isinstance(record.get("id"), str)
        and isinstance(record.get("superseded_by"), str)
    }
    visited: set[str] = set()
    for start in graph:
        trail: list[str] = []
        current = start
        while current in graph and current not in visited:
            if current in trail:
                cycle = trail[trail.index(current):] + [current]
                errors.append(_error("contradiction_supersession_cycle", " -> ".join(cycle), "contradictions"))
                break
            trail.append(current)
            current = graph[current]
        visited.update(trail)
    return errors


def _validate_materiality_shape(value: Any, path: str) -> list[dict[str, str]]:
    if not isinstance(value, dict) or set(value) != _MATERIALITY_KEYS:
        return [_error("invalid_materiality", "materiality fields do not match the M1 contract", path)]
    valid = (
        isinstance(value["outcome_divergence"], str)
        and value["outcome_divergence"] in {"NONE", "LOW", "MEDIUM", "HIGH"}
        and isinstance(value["fan_out"], str)
        and value["fan_out"] in {"LOCAL", "MULTI_OBJECT", "MULTI_FLOW", "SYSTEMIC"}
        and isinstance(value["user_visible"], bool)
        and isinstance(value["reversibility"], str)
        and value["reversibility"] in {
            "TRIVIALLY_REVERSIBLE", "REVERSIBLE", "COSTLY_TO_REVERSE", "IRREVERSIBLE",
        }
        and isinstance(value["classification"], str)
        and value["classification"] in {"MATERIAL", "NON_MATERIAL"}
    )
    risk_flags = value["risk_flags"]
    valid = valid and (
        isinstance(risk_flags, dict)
        and set(risk_flags) == _RISK_FLAG_KEYS
        and all(isinstance(risk_flags[field], bool) for field in _RISK_FLAG_KEYS)
    )
    return [] if valid else [_error("invalid_materiality", "invalid materiality shape", path)]


def _validate_materiality(value: Any, path: str) -> list[dict[str, str]]:
    errors = _validate_materiality_shape(value, path)
    if not errors and not validate_materiality_classification(value):
        errors.append(_error(
            "materiality_classification_mismatch",
            "materiality classification must match its deterministic inputs",
            path,
        ))
    return errors


def _validate_typed_semantic_minima(state: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for group, position, record in _iter_records(state):
        path = f"objects.{group}[{position}]"
        if not isinstance(record, dict):
            errors.append(_error("schema_error", "typed authority record must be an object", path))
            continue
        missing = TYPE_MINIMA[group] - set(record)
        if missing:
            errors.append(_error("missing_semantic_fields", f"missing semantic fields: {', '.join(sorted(missing))}", path))
        allowed = {"id", "status"} | TYPE_MINIMA[group] | _LIFECYCLE_FIELDS
        if set(record) - allowed:
            errors.append(_error("schema_error", "typed authority record has unknown fields", path))

        status = record.get("status")
        allowed_statuses = UNKNOWN_STATUSES if group == "unknowns" else NORMAL_AUTHORITY_STATUSES
        if not isinstance(status, str) or status not in allowed_statuses:
            errors.append(_error("invalid_status", f"invalid {group} status", f"{path}.status"))

        for field in TYPE_MINIMA[group] & _TEXT_FIELDS:
            if field in record and (not isinstance(record[field], str) or len(record[field]) < 1):
                errors.append(_error("schema_error", f"{field} must be a non-empty string", f"{path}.{field}"))
        for field in TYPE_MINIMA[group] & _ARRAY_FIELDS:
            if field not in record:
                continue
            value = record[field]
            if (
                not isinstance(value, list)
                or any(not isinstance(item, str) for item in value)
                or len(value) != len(set(value))
                or (group == "tasks" and not value)
            ):
                errors.append(_error("schema_error", f"{field} must be a valid unique string array", f"{path}.{field}"))
        if "ui_required" in record and not isinstance(record["ui_required"], bool):
            errors.append(_error("schema_error", "ui_required must be a boolean", f"{path}.ui_required"))
        if "decision_authority" in record and (
            not isinstance(record["decision_authority"], str)
            or record["decision_authority"] not in _DECISION_AUTHORITIES
        ):
            errors.append(_error("schema_error", "invalid decision_authority", f"{path}.decision_authority"))
        if "resolution_mode" in record and record["resolution_mode"] is not None and (
            not isinstance(record["resolution_mode"], str)
            or record["resolution_mode"] not in _RESOLUTION_MODES
        ):
            errors.append(_error("schema_error", "invalid resolution_mode", f"{path}.resolution_mode"))
        if "superseded_by" in record and (
            not _is_stable_id(record["superseded_by"])
        ):
            errors.append(_error("schema_error", "superseded_by must be a stable id", f"{path}.superseded_by"))
        if "retired_by" in record and (
            not _is_stable_id(record["retired_by"], expected_prefix="DEC")
        ):
            errors.append(_error("schema_error", "retired_by must be a DEC-* stable id", f"{path}.retired_by"))
        if "retired_at_revision" in record and (
            not isinstance(record["retired_at_revision"], int)
            or isinstance(record["retired_at_revision"], bool)
            or record["retired_at_revision"] < 1
        ):
            errors.append(_error("schema_error", "retired_at_revision must be a positive integer", f"{path}.retired_at_revision"))
        if "retirement_reason" in record and (
            not isinstance(record["retirement_reason"], str)
            or len(record["retirement_reason"]) < 1
        ):
            errors.append(_error("schema_error", "retirement_reason must be a non-empty string", f"{path}.retirement_reason"))
        if "materiality" in record:
            errors.extend(_validate_materiality(record["materiality"], f"{path}.materiality"))
    return errors


def _meaningful_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in _MEANINGLESS


def _validate_lifecycle(
    state: dict[str, Any], index: dict[str, tuple[str, dict[str, Any]]],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    project = state.get("project")
    project_revision = project.get("definition_revision") if isinstance(project, dict) else None
    for group, position, record in _iter_records(state):
        if not isinstance(record, dict):
            continue
        path = f"objects.{group}[{position}]"
        object_id = record.get("id")
        if record.get("status") == "SUPERSEDED":
            target = record.get("superseded_by")
            target_entry = index.get(target) if isinstance(target, str) else None
            if (
                not isinstance(object_id, str)
                or not isinstance(target, str)
                or target == object_id
                or target_entry is None
                or target_entry[0] != group
                or target.split("-", 1)[0] != object_id.split("-", 1)[0]
            ):
                errors.append(_error("invalid_supersession", "SUPERSEDED requires a different existing same-prefix superseded_by", path))
        if record.get("status") == "RETIRED":
            retired_by = record.get("retired_by")
            target_entry = index.get(retired_by) if isinstance(retired_by, str) else None
            retired_at_revision = record.get("retired_at_revision")
            if (
                not isinstance(retired_by, str)
                or not retired_by
                or target_entry is None
                or target_entry[0] != "decisions"
                or not isinstance(retired_at_revision, int)
                or isinstance(retired_at_revision, bool)
                or retired_at_revision < 1
                or not isinstance(project_revision, int)
                or retired_at_revision > project_revision
                or not _meaningful_text(record.get("retirement_reason"))
            ):
                errors.append(_error("invalid_retirement", "RETIRED requires decision provenance, a valid revision, and a meaningful reason", path))
    return errors


def _validate_supersession_cycles(state: dict[str, Any]) -> list[dict[str, str]]:
    graph = {
        record["id"]: record["superseded_by"]
        for _, _, record in _iter_records(state)
        if isinstance(record, dict)
        and record.get("status") == "SUPERSEDED"
        and isinstance(record.get("id"), str)
        and isinstance(record.get("superseded_by"), str)
    }
    errors: list[dict[str, str]] = []
    visited: set[str] = set()
    for start in graph:
        trail: list[str] = []
        current = start
        while current in graph and current not in visited:
            if current in trail:
                cycle = trail[trail.index(current):] + [current]
                errors.append(_error("supersession_cycle", " -> ".join(cycle), "objects"))
                break
            trail.append(current)
            current = graph[current]
        visited.update(trail)
    return errors


def _validate_stale_consumed_evidence(state: dict[str, Any]) -> list[dict[str, str]]:
    evidence_index = _collect_evidence(state)
    errors: list[dict[str, str]] = []

    def validate_refs(refs: Any, path: str) -> None:
        if not isinstance(refs, list):
            return
        for reference in refs:
            evidence = evidence_index.get(reference) if isinstance(reference, str) else None
            evidence_status = evidence.get("status") if evidence is not None else None
            if (
                evidence is not None
                and isinstance(evidence_status, str)
                and evidence_status in STALE_CONSUMED_EVIDENCE_STATUSES
            ):
                errors.append(_error(
                    "stale_consumed_evidence",
                    "current authority cannot consume stale, superseded, or unavailable evidence",
                    path,
                ))

    for group, position, record in _iter_records(state):
        if group == "decisions" and isinstance(record, dict) and record.get("status") == "CURRENT":
            validate_refs(record.get("evidence_refs"), f"objects.decisions[{position}].evidence_refs")
    surface_manifest = state.get("surface_manifest")
    records = surface_manifest.get("records") if isinstance(surface_manifest, dict) else None
    if isinstance(records, list):
        for position, record in enumerate(records):
            status = record.get("status") if isinstance(record, dict) else None
            if (
                isinstance(record, dict)
                and isinstance(status, str)
                and status not in {"SUPERSEDED", "RETIRED"}
            ):
                validate_refs(record.get("evidence_refs"), f"surface_manifest.records[{position}].evidence_refs")
    return errors


def _validate_state_v2(
    state: dict[str, Any], *, check_discovery_baseline: bool,
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(_error("schema_error", "schema_version must equal 0.2.0", "schema_version"))
    if set(state) != ROOT_KEYS:
        errors.append(_error("schema_error", "state root fields do not match the 0.2.0 foundation contract", ""))

    project = state.get("project")
    if not isinstance(project, dict) or set(project) != PROJECT_KEYS:
        errors.append(_error("schema_error", "project fields do not match the 0.2.0 foundation contract", "project"))
    else:
        if not isinstance(project["slug"], str):
            errors.append(_error("schema_error", "project.slug must be a string", "project.slug"))
        if (
            not isinstance(project["definition_status"], str)
            or project["definition_status"] not in DEFINITION_STATUSES
        ):
            errors.append(_error("invalid_status", "invalid definition_status", "project.definition_status"))
        if (
            not isinstance(project["definition_revision"], int)
            or isinstance(project["definition_revision"], bool)
            or project["definition_revision"] < 1
        ):
            errors.append(_error("schema_error", "project.definition_revision must be an integer at least 1", "project.definition_revision"))
        if not isinstance(project["bootstrap_mode"], str) or project["bootstrap_mode"] not in BOOTSTRAP_MODES:
            errors.append(_error("schema_error", "project.bootstrap_mode must be a supported bootstrap mode", "project.bootstrap_mode"))
        closure_contract = project["closure_contract"]
        try:
            identities = binding_contract_identity()
        except BindingError:
            identities = None
        expected_closure_contract = None if identities is None else {
            "level": "SEMANTIC_CLOSURE",
            "product_binding_contract": identities["product"],
            "ux_binding_contract": identities["ux"],
        }
        if closure_contract != expected_closure_contract:
            errors.append(_error(
                "binding_contract_identity_mismatch",
                "project.closure_contract must bind the frozen product and UX contract identities",
                "project.closure_contract",
            ))

    objects = state.get("objects")
    if not isinstance(objects, dict) or set(objects) != OBJECT_GROUPS:
        errors.append(_error("schema_error", "objects must contain all 13 canonical groups", "objects"))
    elif any(not isinstance(objects[name], list) for name in OBJECT_GROUPS):
        errors.append(_error("schema_error", "every canonical object group must be an array", "objects"))

    for field, expected_type in (
        ("migration", dict),
        ("evidence", list),
        ("surface_manifest", dict),
        ("contradictions", list),
        ("coverage", list),
        ("ux_coverage", list),
        ("grill_coverage", list),
        ("discovery_baseline", dict),
        ("approval", dict),
        ("approval_history", list),
    ):
        if not isinstance(state.get(field), expected_type):
            errors.append(_error("schema_error", f"{field} must be a {expected_type.__name__}", field))
    errors.extend(_validate_migration_metadata(state))
    index, id_errors = _collect_ids(state)
    errors.extend(id_errors)
    evidence_index = _collect_evidence(state)
    errors.extend(_validate_evidence(state))
    errors.extend(_validate_typed_semantic_minima(state))
    errors.extend(_validate_lifecycle(state, index))
    errors.extend(_validate_supersession_cycles(state))
    errors.extend(_validate_surface_manifest(state, index, evidence_index))
    errors.extend(_validate_contradictions(state, index, evidence_index))
    errors.extend(_validate_stale_consumed_evidence(state))
    errors.extend(validate_unknown_decision_integrity(
        state, id_index=index, evidence_index=evidence_index,
    ))
    errors.extend(validate_decision_authority_policy(
        state, evidence_index=evidence_index,
    ))
    errors.extend(validate_grill_coverage(state))
    errors.extend(validate_product_coverage_bindings(state))
    errors.extend(validate_ux_coverage_bindings(state))
    errors.extend(validate_authority_graph_references(state))
    errors.extend(validate_discovery_baseline(
        state, check_freshness=check_discovery_baseline,
    ))
    errors.extend(validate_approval(state))
    return errors


def validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]:
    return _validate_state_v2(state, check_discovery_baseline=True)


def _current_semantic_digest(state: dict[str, Any]) -> str | None:
    try:
        return definition_digest(state)
    except (BindingError, KeyError, TypeError, ValueError):
        return None


def _approval_control_matches(
    state: dict[str, Any], current_definition_digest: str | None,
) -> bool:
    project = state.get("project")
    approval = state.get("approval")
    if not isinstance(project, dict) or not isinstance(approval, dict):
        return False
    if (
        project.get("definition_status") != "CLOSED"
        or approval.get("status") != "APPROVED"
        or approval.get("approved_revision") != project.get("definition_revision")
        or current_definition_digest is None
        or approval.get("approved_definition_digest") != current_definition_digest
    ):
        return False
    try:
        current_manifest_digest = approval_manifest_digest(
            compute_approval_manifest(state)
        )
    except (BindingError, KeyError, TypeError, ValueError):
        return False
    return approval.get("approved_manifest_digest") == current_manifest_digest


def evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]:
    try:
        errors = validate_state_v2(state)
    except BindingError:
        _, errors = _collect_ids(state)
    metrics: dict[str, int] = {}
    projection_unsafe = False

    def unsafe_projection(stage: str) -> None:
        nonlocal projection_unsafe
        projection_unsafe = True
        errors.append(_error(
            "unsafe_semantic_projection",
            f"structural validation prevents safe {stage} projection",
            stage,
        ))

    try:
        unknown_metrics = grill_unknown_metrics(state)
        metrics["deferred_unknowns"] = unknown_metrics["deferred_unknowns"]
    except (BindingError, KeyError, TypeError, ValueError):
        unsafe_projection("unknown_metrics")
    try:
        metrics.update(semantic_readiness_metrics(state))
    except (BindingError, KeyError, TypeError, ValueError):
        unsafe_projection("semantic_readiness_metrics")
    try:
        metrics.update(approval_metrics(state))
    except (BindingError, KeyError, TypeError, ValueError):
        unsafe_projection("approval_metrics")
    try:
        current_definition_digest = definition_digest(state)
    except (BindingError, KeyError, TypeError, ValueError):
        current_definition_digest = None
        unsafe_projection("definition_digest")
    if projection_unsafe:
        current_definition_digest = None
    closed = (
        not errors
        and _approval_control_matches(state, current_definition_digest)
        and all(metrics.get(name, 0) == 0 for name in CLOSURE_BLOCKING_METRICS)
    )
    return {
        "errors": errors,
        "metrics": metrics,
        "closed": closed,
        "definition_digest": current_definition_digest,
    }
