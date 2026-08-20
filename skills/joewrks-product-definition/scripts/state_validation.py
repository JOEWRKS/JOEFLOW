"""Shared validation primitives for product-definition state files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ID_PREFIXES = {
    "GOAL", "USR", "REQ", "UNK", "DEC", "RULE", "FLOW", "SCR",
    "STATE", "DATA", "INT", "AC", "TASK",
}
DECISION_STATUSES = {
    "OPEN", "ANSWERED", "ASSUMED_ACCEPTED", "DEFERRED_NON_BLOCKING",
    "BLOCKED_EXTERNAL", "SUPERSEDED",
}
UNKNOWN_STATUSES = {
    "OPEN", "ANSWERED", "ASSUMED_ACCEPTED", "DEFERRED_NON_BLOCKING",
    "BLOCKED_EXTERNAL", "SUPERSEDED",
}
ARTIFACT_STATUSES = {"CURRENT", "STALE", "SUPERSEDED"}
PROJECT_STATUSES = {"OPEN", "READY_FOR_REVIEW", "CLOSED", "BLOCKED"}
REFERENCE_FIELDS = {
    "acceptance", "affects", "depends_on", "implements", "requirements",
    "screens", "supersedes", "rules", "flows", "states", "tasks",
}


def load_state(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        state = json.load(handle)
    if not isinstance(state, dict):
        raise ValueError("state root must be a JSON object")
    return state


def error(code: str, message: str, path: str = "") -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def iter_objects(state: dict[str, Any]):
    groups = state.get("objects", {})
    if not isinstance(groups, dict):
        return
    for group, items in groups.items():
        if isinstance(items, list):
            for index, item in enumerate(items):
                if isinstance(item, dict):
                    yield group, index, item


def validate_structure(state: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(state.get("schema_version"), str):
        errors.append(error("schema_error", "schema_version must be a string", "schema_version"))
    project = state.get("project")
    if not isinstance(project, dict):
        errors.append(error("schema_error", "project must be an object", "project"))
    elif project.get("status") not in PROJECT_STATUSES:
        errors.append(error("invalid_status", "invalid project status", "project.status"))
    if not isinstance(state.get("objects"), dict):
        errors.append(error("schema_error", "objects must be an object", "objects"))
    if not isinstance(state.get("coverage", []), list):
        errors.append(error("schema_error", "coverage must be an array", "coverage"))
    if not isinstance(state.get("contradictions", []), list):
        errors.append(error("schema_error", "contradictions must be an array", "contradictions"))
    return errors


def collect_ids(state: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    index: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, str]] = []
    for group, position, item in iter_objects(state):
        path = f"objects.{group}[{position}].id"
        object_id = item.get("id")
        if not isinstance(object_id, str) or "-" not in object_id:
            errors.append(error("invalid_id", "object id must use PREFIX-NNN form", path))
            continue
        prefix, number = object_id.rsplit("-", 1)
        if prefix not in ID_PREFIXES or len(number) != 3 or not number.isdigit():
            errors.append(error("invalid_id", f"invalid stable id {object_id}", path))
        if object_id in index:
            errors.append(error("duplicate_id", f"duplicate id {object_id}", path))
        else:
            index[object_id] = item
    return index, errors


def validate_statuses(state: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for group, position, item in iter_objects(state):
        status = item.get("status")
        allowed = DECISION_STATUSES if group == "decisions" else UNKNOWN_STATUSES if group == "unknowns" else ARTIFACT_STATUSES
        if status not in allowed:
            errors.append(error("invalid_status", f"invalid {group} status {status!r}", f"objects.{group}[{position}].status"))
    return errors


def reference_values(item: dict[str, Any]):
    for field in REFERENCE_FIELDS:
        value = item.get(field)
        if isinstance(value, str):
            yield field, value
        elif isinstance(value, list):
            for referenced in value:
                if isinstance(referenced, str):
                    yield field, referenced


def validate_references(state: dict[str, Any], index: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    graph: dict[str, list[str]] = {object_id: [] for object_id in index}
    for group, position, item in iter_objects(state):
        source = item.get("id")
        for field, target in reference_values(item):
            path = f"objects.{group}[{position}].{field}"
            if target not in index:
                errors.append(error("broken_reference", f"{source} references missing {target}", path))
            elif field == "depends_on" and source in graph:
                graph[source].append(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            cycle = trail[trail.index(node):] + [node]
            errors.append(error("dependency_cycle", " -> ".join(cycle), f"objects.{node}"))
            return
        if node in visited:
            return
        visiting.add(node)
        for target in graph.get(node, []):
            visit(target, trail + [target])
        visiting.remove(node)
        visited.add(node)

    for object_id in graph:
        visit(object_id, [object_id])
    return errors


def validate_state(state: dict[str, Any]) -> list[dict[str, str]]:
    errors = validate_structure(state)
    index, id_errors = collect_ids(state)
    errors.extend(id_errors)
    errors.extend(validate_statuses(state))
    errors.extend(validate_references(state, index))
    return sorted(errors, key=lambda item: (item["code"], item["path"], item["message"]))


def closure_metrics(state: dict[str, Any]) -> dict[str, int]:
    objects = state.get("objects", {}) if isinstance(state.get("objects"), dict) else {}
    unknowns = objects.get("unknowns", [])
    decisions = objects.get("decisions", [])
    all_objects = [item for _, _, item in iter_objects(state)]
    requirements = objects.get("requirements", [])
    screens = objects.get("screens", [])
    acceptance = objects.get("acceptance_criteria", [])
    tasks = objects.get("tasks", [])
    contradictions = state.get("contradictions", [])
    coverage = state.get("coverage", [])

    return {
        "blocking_unknowns": sum(1 for item in unknowns if item.get("material", True) and item.get("status") not in {"ANSWERED", "ASSUMED_ACCEPTED", "DEFERRED_NON_BLOCKING", "SUPERSEDED"}),
        "open_material_decisions": sum(1 for item in decisions if item.get("material", True) and item.get("status") in {"OPEN", "BLOCKED_EXTERNAL"}),
        "contradictions": sum(1 for item in contradictions if isinstance(item, dict) and item.get("status", "OPEN") == "OPEN"),
        "stale_artifacts": sum(1 for item in all_objects if item.get("status") == "STALE"),
        "coverage_gaps": sum(1 for row in coverage if isinstance(row, dict) for value in row.get("cells", {}).values() if value == "OPEN"),
        "orphan_requirements": sum(1 for item in requirements if not item.get("acceptance") or not item.get("screens")),
        "orphan_screens": sum(1 for item in screens if not item.get("requirements")),
        "orphan_acceptance_criteria": sum(1 for item in acceptance if not item.get("requirements")),
        "unmapped_implementation_tasks": sum(1 for item in tasks if not item.get("implements") or not item.get("acceptance")),
        "missing_user_approval": 0 if state.get("project", {}).get("user_approved") is True else 1,
    }

