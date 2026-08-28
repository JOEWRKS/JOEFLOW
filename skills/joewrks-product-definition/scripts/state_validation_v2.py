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


def _error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


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
        if project["definition_status"] not in DEFINITION_STATUSES:
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
    return errors


def evaluate_closure_v2(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "errors": validate_state_v2(state),
        "metrics": {"semantic_closure_not_implemented": 1},
        "closed": False,
        "definition_digest": None,
    }
