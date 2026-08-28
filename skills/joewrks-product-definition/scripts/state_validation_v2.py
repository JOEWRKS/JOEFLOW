from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "0.2.0"
ROOT_KEYS = {
    "schema_version", "project", "migration", "evidence", "surface_manifest",
    "contradictions", "objects", "coverage", "ux_coverage",
    "discovery_baseline", "approval", "approval_history",
}
PROJECT_KEYS = {"slug", "definition_status", "definition_revision", "closure_contract"}
OBJECT_GROUPS = {
    "goals", "users", "requirements", "unknowns", "decisions", "rules",
    "flows", "screens", "states", "data", "integrations",
    "acceptance_criteria", "tasks",
}
DEFINITION_STATUSES = {"OPEN", "READY_FOR_REVIEW", "CLOSED", "BLOCKED"}
NORMAL_AUTHORITY_STATUSES = {"CURRENT", "STALE", "SUPERSEDED", "RETIRED"}
UNKNOWN_STATUSES = {"OPEN", "RESOLVED", "DEFERRED", "BLOCKED", "SUPERSEDED", "RETIRED"}
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
    "unknowns": frozenset({"question", "materiality", "decision_authority"}),
    "decisions": frozenset({"statement", "decision_type", "resolution_mode", "decision_authority", "source_unknown_refs", "evidence_refs", "materiality", "affects"}),
    "rules": frozenset({"statement", "applies_to"}),
    "flows": frozenset({"goal_refs", "entry", "preconditions", "paths", "outcomes"}),
    "screens": frozenset({"purpose", "requirement_refs", "interaction_mode", "major_actions"}),
    "states": frozenset({"owner_refs", "state_name", "conditions"}),
    "data": frozenset({"name", "purpose", "ownership"}),
    "integrations": frozenset({"name", "purpose"}),
    "acceptance_criteria": frozenset({"requirement_refs", "assertion"}),
    "tasks": frozenset({"implements", "acceptance_refs"}),
}

_LIFECYCLE_FIELDS = {"superseded_by", "retired_by", "retired_at_revision", "retirement_reason"}
_TEXT_FIELDS = {
    "statement", "description", "actor_kind", "scope", "question",
    "decision_authority", "decision_type", "resolution_mode", "entry",
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
        if "resolution_mode" in record and (
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
            errors.extend(_validate_materiality_shape(record["materiality"], f"{path}.materiality"))
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


def validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]:
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
        closure_contract = project["closure_contract"]
        if not isinstance(closure_contract, dict) or closure_contract.get("level") != "SEMANTIC_CLOSURE":
            errors.append(_error("schema_error", "project.closure_contract.level must equal SEMANTIC_CLOSURE", "project.closure_contract"))

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
        ("discovery_baseline", dict),
        ("approval", dict),
        ("approval_history", list),
    ):
        if not isinstance(state.get(field), expected_type):
            errors.append(_error("schema_error", f"{field} must be a {expected_type.__name__}", field))
    index, id_errors = _collect_ids(state)
    errors.extend(id_errors)
    errors.extend(_validate_typed_semantic_minima(state))
    errors.extend(_validate_lifecycle(state, index))
    errors.extend(_validate_supersession_cycles(state))
    return errors


def evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "errors": validate_state_v2(state),
        "metrics": {"semantic_closure_not_implemented": 1},
        "closed": False,
        "definition_digest": None,
    }
