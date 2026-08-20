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
    "screens", "supersedes", "superseded_by", "rules", "flows", "states", "tasks",
}
COVERAGE_DIMENSIONS = {
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state",
    "data", "side_effect", "notification", "validation", "boundary",
    "persistence", "security", "privacy", "analytics", "acceptance",
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
GLOBAL_TYPED_EDGES = {"acceptance":{"AC"},"requirements":{"REQ"},"screens":{"SCR"},"rules":{"RULE"},"flows":{"FLOW"},"states":{"STATE"},"tasks":{"TASK"}}
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
IMPACT_AXES = {"scope", "rules", "flows", "states", "privacy", "money", "security", "acceptance"}
MEANINGLESS = {"none", "false", "n/a", "na", "later", "tbd"}


def is_active(item: dict[str, Any]) -> bool:
    return item.get("status") != "SUPERSEDED"


def is_meaningful_text(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text) and text.lower() not in MEANINGLESS


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
    if state.get("schema_version") != "0.1.2.1":
        errors.append(error("schema_error", "schema_version must equal 0.1.2.1", "schema_version"))
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
            else:
                allowed_types = TYPED_EDGES.get((group, field), GLOBAL_TYPED_EDGES.get(field))
                if field in {"supersedes", "superseded_by"}:
                    allowed_types = {str(source).split("-", 1)[0]}
                if allowed_types and target.split("-", 1)[0] not in allowed_types:
                    allowed = ", ".join(sorted(allowed_types))
                    errors.append(error("invalid_reference_type", f"{group}.{field} requires {allowed} targets, got {target}", path))
            if target in index and field == "depends_on" and source in graph:
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
    seen_screens: set[str] = set()
    screens_by_id = {item.get("id"): item for group, _, item in iter_objects(state) if group == "screens"}
    for position, row in enumerate(state.get("ux_coverage", [])):
        path = f"ux_coverage[{position}]"
        if not isinstance(row, dict):
            errors.append(error("schema_error", "screen coverage row must be an object", path))
            continue
        screen_id = row.get("screen_id")
        if screen_id in seen_screens:
            errors.append(error("duplicate_ux_coverage", f"duplicate UX coverage row for {screen_id}", f"{path}.screen_id"))
        seen_screens.add(screen_id)
        if screen_id not in index:
            errors.append(error("broken_reference", f"screen coverage references missing {screen_id}", f"{path}.screen_id"))
        elif not str(screen_id).startswith("SCR-"):
            errors.append(error("invalid_reference_type", "screen_coverage.screen_id requires SCR-*", f"{path}.screen_id"))
        errors.extend(_validate_axis_cells(row.get("states"), f"{path}.states"))
        actions = row.get("actions")
        if not isinstance(actions, list):
            errors.append(error("schema_error", "ux actions must be an array", f"{path}.actions"))
        else:
            covered_keys = [action.get("key") for action in actions if isinstance(action, dict)]
            if len(covered_keys) != len(set(covered_keys)):
                errors.append(error("duplicate_action_coverage", "duplicate major-action coverage key", f"{path}.actions"))
            screen = screens_by_id.get(screen_id, {})
            declared = screen.get("major_actions", [])
            if not isinstance(declared, list) or len(declared) != len(set(declared)) or set(declared) != set(covered_keys):
                errors.append(error("action_inventory_mismatch", "screen.major_actions must equal UX coverage action keys", f"{path}.actions"))
            if not actions and not str(screen.get("no_major_actions_reason", "")).strip():
                errors.append(error("missing_no_major_actions_reason", "zero major actions require screen.no_major_actions_reason", f"{path}.actions"))
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
        def explanatory_review():
            review=item.get("non_blocking_impact_review")
            return isinstance(review,dict) and IMPACT_AXES <= set(review) and all(isinstance(review[a],str) and review[a].strip().lower() not in MEANINGLESS and len(review[a].strip())>8 for a in IMPACT_AXES)
        if status == "SUPERSEDED":
            target=item.get("superseded_by")
            if not isinstance(target,str) or target == item.get("id") or target not in {x.get("id") for _,_,x in iter_objects(state)} or target.split("-",1)[0] != str(item.get("id","")).split("-",1)[0]:
                errors.append(error("invalid_supersession","SUPERSEDED requires existing same-type superseded_by",path))
        if group == "unknowns":
            if status == "ANSWERED" and not (str(item.get("resolution","")).strip() and str(item.get("source","")).strip()): errors.append(error("invalid_answered_unknown","ANSWERED unknown requires resolution and source",path))
            if status == "ASSUMED_ACCEPTED" and not all([str(item.get("resolution","")).strip(),str(item.get("recommendation","")).strip(),str(item.get("source","")).strip(),item.get("accepted_by")=="user",str(item.get("accepted_at","")).strip()]): errors.append(error("invalid_assumed_unknown","ASSUMED_ACCEPTED unknown requires explicit user evidence",path))
            if status == "DEFERRED_NON_BLOCKING" and not (str(item.get("source","")).strip() and is_meaningful_text(item.get("deferral_reason")) and explanatory_review()): errors.append(error("invalid_deferred_unknown","deferred unknown requires source, meaningful reason, and 8-axis explanatory review",path))
        if group == "decisions":
            base=all([str(item.get("decision","")).strip(),str(item.get("reason","")).strip(),str(item.get("source","")).strip()])
            if status == "ANSWERED" and not base: errors.append(error("invalid_answered_decision","ANSWERED decision requires decision, reason, source",path))
            if status == "ASSUMED_ACCEPTED" and not (base and str(item.get("recommendation","")).strip() and item.get("accepted_by")=="user" and str(item.get("accepted_at","")).strip()): errors.append(error("invalid_assumed_decision","ASSUMED_ACCEPTED decision requires explicit user evidence",path))
            if status == "DEFERRED_NON_BLOCKING" and not (str(item.get("source","")).strip() and is_meaningful_text(item.get("deferral_reason")) and explanatory_review()): errors.append(error("invalid_deferred_decision","deferred decision requires source, meaningful reason, and 8-axis explanatory review",path))
    supersession = {
        item.get("id"): item.get("superseded_by")
        for _, _, item in iter_objects(state)
        if item.get("status") == "SUPERSEDED" and isinstance(item.get("id"), str) and isinstance(item.get("superseded_by"), str)
    }
    visited: set[str] = set()
    for start in supersession:
        chain: set[str] = set()
        current = start
        while current in supersession and current not in visited:
            if current in chain:
                errors.append(error("supersession_cycle", f"supersession cycle includes {current}", "objects"))
                break
            chain.add(current)
            current = supersession[current]
        visited.update(chain)
    for group, position, item in iter_objects(state):
        if group == "screens" and item.get("interactive") is False and not str(item.get("non_interactive_reason","")).strip(): errors.append(error("missing_non_interactive_reason","interactive:false requires rationale",f"objects.screens[{position}]"))
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
    goals = [x for x in objects.get("goals", []) if is_active(x)]
    requirements = [x for x in objects.get("requirements", []) if is_active(x)]
    material_requirements = [x for x in requirements if x.get("material", True)]
    screens = [x for x in objects.get("screens", []) if is_active(x)]
    interactive_screens = [x for x in screens if x.get("interactive") is not False]
    acceptance = [x for x in objects.get("acceptance_criteria", []) if is_active(x)]
    tasks = [x for x in objects.get("tasks", []) if is_active(x)]
    contradictions = state.get("contradictions", [])
    coverage = state.get("coverage", [])
    screen_coverage = state.get("ux_coverage", [])

    coverage_gaps = 0
    covered_requirement_ids: set[str] = set()
    active_material_ids = {str(item.get("id")) for item in material_requirements}
    for row in coverage:
        if not isinstance(row, dict):
            continue
        feature_id = str(row.get("feature_id"))
        if feature_id not in active_material_ids:
            continue
        cells = row.get("cells", {})
        covered_requirement_ids.add(feature_id)
        if not isinstance(cells, dict):
            coverage_gaps += len(COVERAGE_DIMENSIONS)
            continue
        coverage_gaps += len(COVERAGE_DIMENSIONS - set(cells))
        coverage_gaps += sum(1 for value in cells.values() if isinstance(value, dict) and value.get("status") == "OPEN")
    missing_requirement_rows = sum(1 for item in material_requirements if item.get("id") not in covered_requirement_ids)
    coverage_gaps += missing_requirement_rows * len(COVERAGE_DIMENSIONS)

    screen_state_gaps = 0
    screen_action_gaps = 0
    covered_screen_ids: set[str] = set()
    active_screens_by_id = {item.get("id"): item for item in interactive_screens}
    for row in screen_coverage:
        if not isinstance(row, dict):
            screen_state_gaps += len(SCREEN_STATE_AXES)
            screen_action_gaps += len(SCREEN_ACTION_AXES)
            continue
        screen_id = str(row.get("screen_id"))
        if screen_id not in active_screens_by_id:
            continue
        covered_screen_ids.add(screen_id)
        states = row.get("states", {}) if isinstance(row.get("states"), dict) else {}
        actions = row.get("actions", []) if isinstance(row.get("actions"), list) else []
        screen_state_gaps += len(SCREEN_STATE_AXES - set(states))
        if not actions and not str(active_screens_by_id[screen_id].get("no_major_actions_reason", "")).strip():
            screen_action_gaps += len(SCREEN_ACTION_AXES)
        for action in actions:
            cells = action.get("cells", {}) if isinstance(action, dict) and isinstance(action.get("cells"), dict) else {}
            screen_action_gaps += len(SCREEN_ACTION_AXES - set(cells))
            screen_action_gaps += sum(1 for value in cells.values() if isinstance(value, dict) and value.get("status") == "OPEN")
        screen_state_gaps += sum(1 for value in states.values() if isinstance(value, dict) and value.get("status") == "OPEN")
    missing_screen_rows = sum(1 for item in interactive_screens if item.get("id") not in covered_screen_ids)
    screen_state_gaps += missing_screen_rows * len(SCREEN_STATE_AXES)
    screen_action_gaps += missing_screen_rows * len(SCREEN_ACTION_AXES)

    missing_active_goal = 0 if goals else 1
    missing_material_requirement = 0 if material_requirements else 1
    missing_acceptance_criterion = 0 if acceptance else 1
    minimum_definition_gaps = missing_active_goal + missing_material_requirement + missing_acceptance_criterion

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
        "missing_active_goal": missing_active_goal,
        "missing_material_requirement": missing_material_requirement,
        "missing_acceptance_criterion": missing_acceptance_criterion,
        "orphan_requirements": sum(1 for item in requirements if not item.get("acceptance") or (not item.get("screens") and not (item.get("ui_required") is False and str(item.get("no_screen_reason", "")).strip()))),
        "orphan_screens": sum(1 for item in screens if not item.get("requirements")),
        "orphan_acceptance_criteria": sum(1 for item in acceptance if not item.get("requirements")),
        "unmapped_implementation_tasks": sum(1 for item in tasks if not item.get("implements") or not item.get("acceptance")),
        "missing_user_approval": 0 if project.get("user_approved") is True and str(approval.get("approved_at", "")).strip() else 1,
        "stale_approval": 0 if approval.get("approved_revision") == revision and isinstance(revision, int) and revision > 0 else 1,
        "stale_user_approval": 0 if approval.get("approved_digest") == digest else 1,
        "invalid_closed_status": 0 if state.get("project", {}).get("status") == "CLOSED" else 1,
    }
