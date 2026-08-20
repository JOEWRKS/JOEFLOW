"""Shared validation primitives for product-definition state files."""

from __future__ import annotations

import json
import copy
import hashlib
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
COVERAGE_DIMENSIONS = {
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state",
    "data", "side_effect", "notification", "validation", "boundary",
    "persistence", "security", "privacy", "analytics", "acceptance",
}
CORE_NONEMPTY_GROUPS = {
    "goals", "users", "requirements", "decisions", "flows", "screens",
    "acceptance_criteria", "tasks",
}
GROUP_PREFIXES = {
    "goals": "GOAL", "users": "USR", "requirements": "REQ",
    "unknowns": "UNK", "decisions": "DEC", "rules": "RULE",
    "flows": "FLOW", "screens": "SCR", "states": "STATE",
    "data": "DATA", "integrations": "INT",
    "acceptance_criteria": "AC", "tasks": "TASK",
}
TYPED_EDGES = {
    ("requirements", "acceptance"): {"AC"},
    ("requirements", "screens"): {"SCR"},
    ("flows", "screens"): {"SCR"},
    ("screens", "requirements"): {"REQ"},
    ("acceptance_criteria", "requirements"): {"REQ"},
    ("tasks", "implements"): {"REQ", "RULE", "DEC"},
    ("tasks", "acceptance"): {"AC"},
}
SCREEN_STATE_AXES = {
    "default", "loading", "empty", "partial", "success", "error",
    "disabled", "permission_denied", "unauthenticated", "offline",
    "timeout", "retrying", "submitting", "completed", "cancelled", "expired",
}
SCREEN_ACTION_AXES = {
    "entry", "precondition", "input", "validation", "submit", "success",
    "failure", "retry", "cancel", "back", "refresh", "duplicate_concurrent_action",
    "timeout", "offline", "permission",
    "session_expiration", "data_mutation", "side_effect", "notification",
    "persistence", "undo", "destructive_confirmation",
}
IMPACT_AXES = {"scope", "rules", "flows", "privacy", "money", "security", "acceptance"}


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
    if state.get("schema_version") != "0.1.1":
        errors.append(error("schema_error", "schema_version must equal 0.1.1", "schema_version"))
    project = state.get("project")
    if not isinstance(project, dict):
        errors.append(error("schema_error", "project must be an object", "project"))
    elif project.get("status") not in PROJECT_STATUSES:
        errors.append(error("invalid_status", "invalid project status", "project.status"))
    if not isinstance(state.get("objects"), dict):
        errors.append(error("schema_error", "objects must be an object", "objects"))
    else:
        for group in GROUP_PREFIXES:
            if group not in state["objects"] or not isinstance(state["objects"].get(group), list):
                errors.append(error("schema_error", f"objects.{group} must be an array", f"objects.{group}"))
    if not isinstance(project, dict) or not isinstance(project.get("definition_revision"), int) or project.get("definition_revision", 0) < 1:
        errors.append(error("schema_error", "project.definition_revision must be a positive integer", "project.definition_revision"))
    if not isinstance(project, dict) or not isinstance(project.get("approval"), dict):
        errors.append(error("schema_error", "project.approval must be an object", "project.approval"))
    if not isinstance(state.get("coverage", []), list):
        errors.append(error("schema_error", "coverage must be an array", "coverage"))
    if not isinstance(state.get("contradictions", []), list):
        errors.append(error("schema_error", "contradictions must be an array", "contradictions"))
    if not isinstance(state.get("ux_coverage", []), list):
        errors.append(error("schema_error", "ux_coverage must be an array", "ux_coverage"))
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
        expected_prefix = GROUP_PREFIXES.get(group)
        if expected_prefix and prefix != expected_prefix:
            errors.append(error("invalid_id_type", f"objects.{group} requires {expected_prefix}-* ids", path))
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
            elif (group, field) in TYPED_EDGES and target.split("-", 1)[0] not in TYPED_EDGES[(group, field)]:
                allowed = ", ".join(sorted(TYPED_EDGES[(group, field)]))
                errors.append(error("invalid_reference_type", f"{group}.{field} requires {allowed} targets, got {target}", path))
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


def _validate_axis_cells(cells: Any, path: str) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(cells, dict):
        return [error("schema_error", "coverage cells must be an object", path)]
    for axis, cell in cells.items():
        cell_path = f"{path}.{axis}"
        if not isinstance(cell, dict) or cell.get("status") not in {"COVERED", "N/A", "OPEN"}:
            errors.append(error("invalid_coverage_status", "coverage cell requires COVERED, N/A, or OPEN", cell_path))
        elif cell.get("status") == "N/A" and not str(cell.get("rationale", "")).strip():
            errors.append(error("missing_rationale", "N/A coverage requires rationale", cell_path))
    return errors


def validate_coverage(state: dict[str, Any], index: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    seen_features: set[str] = set()
    for position, row in enumerate(state.get("coverage", [])):
        path = f"coverage[{position}]"
        if not isinstance(row, dict):
            errors.append(error("schema_error", "coverage row must be an object", path))
            continue
        feature_id = row.get("feature_id")
        if feature_id in seen_features:
            errors.append(error("duplicate_coverage", f"duplicate coverage row for {feature_id}", f"{path}.feature_id"))
        seen_features.add(feature_id)
        if feature_id not in index:
            errors.append(error("broken_reference", f"coverage references missing {feature_id}", f"{path}.feature_id"))
        elif not str(feature_id).startswith("REQ-"):
            errors.append(error("invalid_reference_type", "coverage.feature_id requires REQ-*", f"{path}.feature_id"))
        errors.extend(_validate_axis_cells(row.get("cells"), f"{path}.cells"))
    for position, row in enumerate(state.get("ux_coverage", [])):
        path = f"ux_coverage[{position}]"
        if not isinstance(row, dict):
            errors.append(error("schema_error", "screen coverage row must be an object", path))
            continue
        screen_id = row.get("screen_id")
        if screen_id not in index:
            errors.append(error("broken_reference", f"screen coverage references missing {screen_id}", f"{path}.screen_id"))
        elif not str(screen_id).startswith("SCR-"):
            errors.append(error("invalid_reference_type", "screen_coverage.screen_id requires SCR-*", f"{path}.screen_id"))
        errors.extend(_validate_axis_cells(row.get("states"), f"{path}.states"))
        actions = row.get("actions")
        if not isinstance(actions, list):
            errors.append(error("schema_error", "ux actions must be an array", f"{path}.actions"))
        elif not actions and not str(row.get("no_major_actions_reason", "")).strip():
            errors.append(error("missing_no_major_actions_reason", "empty actions require no_major_actions_reason", f"{path}.actions"))
        else:
            for action_index, action in enumerate(actions):
                if not isinstance(action, dict) or not str(action.get("key", "")).strip():
                    errors.append(error("schema_error", "major action requires key and cells", f"{path}.actions[{action_index}]"))
                else:
                    errors.extend(_validate_axis_cells(action.get("cells"), f"{path}.actions[{action_index}].cells"))
    return errors


def validate_escape_hatches(state: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for group, position, item in iter_objects(state):
        path = f"objects.{group}[{position}]"
        status = item.get("status")
        if group == "unknowns" and status == "DEFERRED_NON_BLOCKING":
            impacts = item.get("impact_assessment")
            valid_impacts = isinstance(impacts, dict) and IMPACT_AXES <= set(impacts) and all(impacts.get(axis) is False for axis in IMPACT_AXES)
            if not str(item.get("non_blocking_rationale", "")).strip() or not str(item.get("source", "")).strip() or not valid_impacts:
                errors.append(error("invalid_deferred_unknown", "deferred unknown requires source, rationale, and explicit false impact assessment", path))
        if group == "decisions" and status in {"ANSWERED", "ASSUMED_ACCEPTED"}:
            base_valid = str(item.get("decision", "")).strip() and str(item.get("source", "")).strip()
            assumed_valid = status != "ASSUMED_ACCEPTED" or (str(item.get("accepted_by", "")).strip() and str(item.get("accepted_at", "")).strip())
            if not base_valid or not assumed_valid:
                code = "invalid_assumed_decision" if status == "ASSUMED_ACCEPTED" else "invalid_answered_decision"
                errors.append(error(code, "closed decision requires decision, source, and acceptance evidence when assumed", path))
    return errors


def validate_state(state: dict[str, Any]) -> list[dict[str, str]]:
    errors = validate_structure(state)
    index, id_errors = collect_ids(state)
    errors.extend(id_errors)
    errors.extend(validate_statuses(state))
    errors.extend(validate_references(state, index))
    errors.extend(validate_coverage(state, index))
    errors.extend(validate_escape_hatches(state))
    return sorted(errors, key=lambda item: (item["code"], item["path"], item["message"]))


def definition_digest(state: dict[str, Any]) -> str:
    canonical = copy.deepcopy(state)
    project = canonical.get("project", {})
    if isinstance(project, dict):
        project.pop("approval", None)
        project.pop("user_approved", None)
        project.pop("status", None)
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    screen_coverage = state.get("ux_coverage", [])

    coverage_gaps = 0
    covered_requirement_ids: set[str] = set()
    for row in coverage:
        if not isinstance(row, dict):
            coverage_gaps += len(COVERAGE_DIMENSIONS)
            continue
        cells = row.get("cells", {})
        covered_requirement_ids.add(str(row.get("feature_id")))
        if not isinstance(cells, dict):
            coverage_gaps += len(COVERAGE_DIMENSIONS)
            continue
        coverage_gaps += len(COVERAGE_DIMENSIONS - set(cells))
        coverage_gaps += sum(1 for value in cells.values() if isinstance(value, dict) and value.get("status") == "OPEN")
    missing_requirement_rows = sum(1 for item in requirements if item.get("id") not in covered_requirement_ids)
    coverage_gaps += missing_requirement_rows * len(COVERAGE_DIMENSIONS)

    screen_state_gaps = 0
    screen_action_gaps = 0
    covered_screen_ids: set[str] = set()
    for row in screen_coverage:
        if not isinstance(row, dict):
            screen_state_gaps += len(SCREEN_STATE_AXES)
            screen_action_gaps += len(SCREEN_ACTION_AXES)
            continue
        covered_screen_ids.add(str(row.get("screen_id")))
        states = row.get("states", {}) if isinstance(row.get("states"), dict) else {}
        actions = row.get("actions", []) if isinstance(row.get("actions"), list) else []
        screen_state_gaps += len(SCREEN_STATE_AXES - set(states))
        if not actions and not str(row.get("no_major_actions_reason", "")).strip():
            screen_action_gaps += len(SCREEN_ACTION_AXES)
        for action in actions:
            cells = action.get("cells", {}) if isinstance(action, dict) and isinstance(action.get("cells"), dict) else {}
            screen_action_gaps += len(SCREEN_ACTION_AXES - set(cells))
            screen_action_gaps += sum(1 for value in cells.values() if isinstance(value, dict) and value.get("status") == "OPEN")
        screen_state_gaps += sum(1 for value in states.values() if isinstance(value, dict) and value.get("status") == "OPEN")
    missing_screen_rows = sum(1 for item in screens if item.get("id") not in covered_screen_ids)
    screen_state_gaps += missing_screen_rows * len(SCREEN_STATE_AXES)
    screen_action_gaps += missing_screen_rows * len(SCREEN_ACTION_AXES)

    minimum_definition_gaps = sum(
        1 for group in CORE_NONEMPTY_GROUPS
        if not isinstance(objects.get(group), list) or len(objects.get(group, [])) == 0
    )
    if not coverage:
        minimum_definition_gaps += 1

    project = state.get("project", {}) if isinstance(state.get("project"), dict) else {}
    approval = project.get("approval", {}) if isinstance(project.get("approval"), dict) else {}
    revision = project.get("definition_revision")
    digest = definition_digest(state)

    return {
        "blocking_unknowns": sum(1 for item in unknowns if item.get("material", True) and item.get("status") not in {"ANSWERED", "ASSUMED_ACCEPTED", "DEFERRED_NON_BLOCKING", "SUPERSEDED"}),
        "open_material_decisions": sum(1 for item in decisions if item.get("material", True) and item.get("status") in {"OPEN", "BLOCKED_EXTERNAL"}),
        "contradictions": sum(1 for item in contradictions if isinstance(item, dict) and item.get("status", "OPEN") == "OPEN"),
        "stale_artifacts": sum(1 for item in all_objects if item.get("status") == "STALE"),
        "coverage_gaps": coverage_gaps,
        "screen_state_gaps": screen_state_gaps,
        "screen_action_gaps": screen_action_gaps,
        "minimum_definition_gaps": minimum_definition_gaps,
        "orphan_requirements": sum(1 for item in requirements if not item.get("acceptance") or (not item.get("screens") and not (item.get("ui_required") is False and str(item.get("no_screen_reason", "")).strip()))),
        "orphan_screens": sum(1 for item in screens if not item.get("requirements")),
        "orphan_acceptance_criteria": sum(1 for item in acceptance if not item.get("requirements")),
        "unmapped_implementation_tasks": sum(1 for item in tasks if not item.get("implements") or not item.get("acceptance")),
        "missing_user_approval": 0 if project.get("user_approved") is True and str(approval.get("approved_at", "")).strip() else 1,
        "stale_approval": 0 if approval.get("approved_revision") == revision and isinstance(revision, int) and revision > 0 else 1,
        "stale_user_approval": 0 if approval.get("approved_digest") == digest else 1,
        "invalid_closed_status": 0 if state.get("project", {}).get("status") == "CLOSED" else 1,
    }
