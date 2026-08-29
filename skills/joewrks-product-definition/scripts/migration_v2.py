"""Deterministic, read-only planning for legacy state 0.1.2.1 migration."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

import state_validation as legacy
from authority_binding_v2 import binding_contract_identity, load_binding_contracts
from materiality_v2 import validate_materiality_classification
from state_validation_v2 import validate_state_v2


MIGRATION_VERSION = "0.2.0-foundation.1"
MIGRATION_APPLY_VERSION = "0.2.0-m6.1"
FROM_SCHEMA = "0.1.2.1"
TO_SCHEMA = "0.2.0"
PLAN_SCHEMA = "joewrks.state-migration-plan/1.0"
RECEIPT_SCHEMA = "joewrks.state-migration-receipt/1.0"
OBJECT_GROUPS = (
    "goals", "users", "requirements", "unknowns", "decisions", "rules",
    "flows", "screens", "states", "data", "integrations",
    "acceptance_criteria", "tasks",
)
MIGRATION_KEYS = {
    "mode", "from_schema", "to_schema", "migration_version", "source_digest",
    "source_revision", "source_legacy_status", "source_legacy_approval_digest",
    "plan_digest", "preserved_ids", "promoted_ids", "generated_ids",
    "legacy_records", "reconciliation_gaps", "reconciliation_gap_count",
}
GRILL_PROFILE_DOMAINS = (
    "AUTH", "MONEY", "FILE_UPLOAD", "ASYNC", "PERMISSION",
    "DESTRUCTIVE_ACTION",
)
MISSING_AUTHORITY = "MISSING_V2_SEMANTIC_AUTHORITY"
ABSENT_COVERAGE_CELL_FIELDS = (
    "authority_bindings", "basis_bindings", "rationale", "status", "unknown_refs",
)
NORMAL_STATUSES = {"CURRENT", "STALE", "SUPERSEDED"}
UNKNOWN_STATUS_MAP = {
    "OPEN": "OPEN",
    "ANSWERED": "RESOLVED",
    "DEFERRED_NON_BLOCKING": "DEFERRED",
    "BLOCKED_EXTERNAL": "BLOCKED",
    "SUPERSEDED": "SUPERSEDED",
}
MATERIALITY_KEYS = {
    "outcome_divergence", "fan_out", "user_visible", "reversibility",
    "risk_flags", "classification",
}
RISK_FLAG_KEYS = {
    "security", "privacy", "money", "legal_or_policy", "destructive",
    "data_loss", "external_commitment",
}
UNKNOWN_FIELDS = {
    "question", "why_it_matters", "required_authority_class",
    "question_category", "materiality", "decision_authority", "affects",
    "blocks_unknown_refs", "origin", "response_mode", "options",
    "recommendation", "evidence_refs", "resolved_by", "resolution_mode",
    "resolution_summary", "deferral", "blocked_reason",
}
DECISION_FIELDS = {
    "statement", "decision_type", "resolution_mode", "decision_authority",
    "source_unknown_refs", "evidence_refs", "materiality", "affects",
    "decided_by", "accepted_recommendation",
}
_LIFECYCLE_SOURCE_FIELDS = {"id", "status", "superseded_by"}
SOURCE_FIELDS_BY_GROUP = {
    "goals": _LIFECYCLE_SOURCE_FIELDS | {"text"},
    "users": _LIFECYCLE_SOURCE_FIELDS | {"role", "cardinality", "identity"},
    "requirements": _LIFECYCLE_SOURCE_FIELDS | {
        "text", "scope", "ui_required", "materiality",
    },
    "unknowns": _LIFECYCLE_SOURCE_FIELDS | UNKNOWN_FIELDS,
    "decisions": _LIFECYCLE_SOURCE_FIELDS
    | (DECISION_FIELDS - {"statement"})
    | {"decision", "answer"},
    "rules": _LIFECYCLE_SOURCE_FIELDS | {"statement", "text", "applies_to"},
    "flows": _LIFECYCLE_SOURCE_FIELDS | {
        "goal_refs", "entry", "preconditions", "paths", "outcomes",
    },
    "screens": _LIFECYCLE_SOURCE_FIELDS | {
        "purpose", "requirement_refs", "requirements", "interaction_mode",
        "major_actions",
    },
    "states": _LIFECYCLE_SOURCE_FIELDS | {"owner_refs", "name", "conditions"},
    "data": _LIFECYCLE_SOURCE_FIELDS | {"name", "purpose", "ownership"},
    "integrations": _LIFECYCLE_SOURCE_FIELDS | {"name", "purpose"},
    "acceptance_criteria": _LIFECYCLE_SOURCE_FIELDS | {
        "requirement_refs", "requirements", "assertion", "text",
    },
    "tasks": _LIFECYCLE_SOURCE_FIELDS | {
        "implements", "acceptance_refs", "acceptance",
    },
}
ALIAS_GROUPS = {
    "decisions": (("statement", ("decision", "answer"), "text"),),
    "rules": (("statement", ("statement", "text"), "text"),),
    "screens": (
        ("requirement_refs", ("requirement_refs", "requirements"), "strings"),
    ),
    "acceptance_criteria": (
        ("requirement_refs", ("requirement_refs", "requirements"), "strings"),
        ("assertion", ("assertion", "text"), "text"),
    ),
    "tasks": (
        ("acceptance_refs", ("acceptance_refs", "acceptance"), "strings"),
    ),
}


class MigrationError(ValueError):
    def __init__(self, code: str, detail: object = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}: {detail}")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def allocate_generated_ids(
    prefix: str,
    existing_ids: set[str],
    canonical_paths: list[str],
) -> dict[str, str]:
    marker = f"{prefix}-"
    suffixes = [
        int(existing_id[len(marker):])
        for existing_id in existing_ids
        if existing_id.startswith(marker)
        and existing_id[len(marker):].isdecimal()
    ]
    next_suffix = max(suffixes, default=0) + 1
    return {
        path: f"{prefix}-{next_suffix + offset:03d}"
        for offset, path in enumerate(sorted(set(canonical_paths)))
    }


def _pointer_token(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _preserved_ids(state: dict[str, object]) -> set[str]:
    preserved: set[str] = set()
    objects = state.get("objects", {})
    if isinstance(objects, dict):
        for items in objects.values():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    preserved.add(item["id"])
    contradictions = state.get("contradictions", [])
    if isinstance(contradictions, list):
        for item in contradictions:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                preserved.add(item["id"])
    return preserved


def _reconciliation_paths(state: dict[str, object]) -> dict[str, str]:
    reasons = {
        "COVERED": "COVERED_BINDING_REQUIRED",
        "N/A": "NA_BASIS_BINDING_REQUIRED",
        "OPEN": "OPEN_UNKNOWN_BINDING_REQUIRED",
    }
    sites: dict[str, str] = {}

    coverage = state.get("coverage", [])
    if isinstance(coverage, list):
        for row in coverage:
            if not isinstance(row, dict) or not isinstance(row.get("cells"), dict):
                continue
            feature_id = _pointer_token(row.get("feature_id"))
            for axis, cell in row["cells"].items():
                if isinstance(cell, dict):
                    path = f"/coverage/{feature_id}/cells/{_pointer_token(axis)}"
                    sites[path] = reasons[cell["status"]]

    ux_coverage = state.get("ux_coverage", [])
    if isinstance(ux_coverage, list):
        for row in ux_coverage:
            if not isinstance(row, dict):
                continue
            screen_id = _pointer_token(row.get("screen_id"))
            states = row.get("states", {})
            if isinstance(states, dict):
                for axis, cell in states.items():
                    if isinstance(cell, dict):
                        path = f"/ux_coverage/{screen_id}/states/{_pointer_token(axis)}"
                        sites[path] = reasons[cell["status"]]
            actions = row.get("actions", [])
            if isinstance(actions, list):
                for action in actions:
                    if not isinstance(action, dict) or not isinstance(action.get("cells"), dict):
                        continue
                    action_key = _pointer_token(action.get("key"))
                    for axis, cell in action["cells"].items():
                        if isinstance(cell, dict):
                            path = (
                                f"/ux_coverage/{screen_id}/actions/{action_key}"
                                f"/cells/{_pointer_token(axis)}"
                            )
                            sites[path] = reasons[cell["status"]]
    return sites


def _legacy_validation_errors(state: dict[str, object]) -> list[dict[str, str]]:
    try:
        return legacy.validate_state(state)
    except Exception as exc:
        raise MigrationError(
            "MIGRATION_SOURCE_INVALID",
            {"validator_exception": {"type": type(exc).__name__}},
        ) from None


def build_migration_plan(state: dict[str, object]) -> dict[str, object]:
    if state.get("schema_version") != FROM_SCHEMA:
        raise MigrationError("MIGRATION_SOURCE_INVALID", _legacy_validation_errors(state))

    errors = _legacy_validation_errors(state)
    if errors:
        raise MigrationError("MIGRATION_SOURCE_INVALID", errors)

    preserved_ids = _preserved_ids(state)
    paths = _reconciliation_paths(state)
    generated_ids = allocate_generated_ids("UNK", preserved_ids, list(paths))
    reconciliation_sites: list[dict[str, Any]] = [
        {
            "path": path,
            "reason": paths[path],
            "generated_unknown_id": generated_ids[path],
        }
        for path in sorted(paths)
    ]

    return {
        "schema_version": PLAN_SCHEMA,
        "status": "FOUNDATION_PLAN_ONLY",
        "from_schema": FROM_SCHEMA,
        "to_schema": TO_SCHEMA,
        "migration_version": MIGRATION_VERSION,
        "source_digest": hashlib.sha256(canonical_json_bytes(state)).hexdigest(),
        "preserved_ids": sorted(preserved_ids),
        "reconciliation_sites": reconciliation_sites,
    }


def _sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and bool(value.strip()) else None


def _strings(value: object, *, nonempty: bool = False) -> list[str] | None:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or any(not isinstance(item, str) for item in value)
        or len(value) != len(set(value))
    ):
        return None
    return copy.deepcopy(value)


def _materiality(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict) or set(value) != MATERIALITY_KEYS:
        return None
    risk_flags = value.get("risk_flags")
    if (
        not isinstance(risk_flags, dict)
        or set(risk_flags) != RISK_FLAG_KEYS
        or any(not isinstance(risk_flags[key], bool) for key in RISK_FLAG_KEYS)
        or value.get("outcome_divergence") not in {"NONE", "LOW", "MEDIUM", "HIGH"}
        or value.get("fan_out") not in {"LOCAL", "MULTI_OBJECT", "MULTI_FLOW", "SYSTEMIC"}
        or not isinstance(value.get("user_visible"), bool)
        or value.get("reversibility") not in {
            "TRIVIALLY_REVERSIBLE", "REVERSIBLE", "COSTLY_TO_REVERSE",
            "IRREVERSIBLE",
        }
        or value.get("classification") not in {"MATERIAL", "NON_MATERIAL"}
        or not validate_materiality_classification(value)
    ):
        return None
    return copy.deepcopy(value)


def _normal_status(record: dict[str, object]) -> str | None:
    status = record.get("status")
    if status not in NORMAL_STATUSES:
        return None
    if status == "SUPERSEDED" and not isinstance(record.get("superseded_by"), str):
        return None
    return str(status)


def _with_lifecycle(
    source: dict[str, object], target: dict[str, object], status: str,
) -> dict[str, object]:
    target["status"] = status
    if status == "SUPERSEDED":
        target["superseded_by"] = source["superseded_by"]
    return target


def _missing(values: dict[str, object | None]) -> list[str]:
    return sorted(field for field, value in values.items() if value is None)


def _normalized_alias_value(value: object, kind: str) -> object:
    if kind == "text":
        text = _text(value)
        return text.strip() if text is not None else None
    strings = _strings(value)
    return tuple(item.strip() for item in strings) if strings is not None else None


def _source_fidelity_issues(
    group: str, record: dict[str, object],
) -> list[str]:
    issues = {
        f"source_field:{field}"
        for field in set(record) - SOURCE_FIELDS_BY_GROUP[group]
    }
    if "superseded_by" in record and record.get("status") != "SUPERSEDED":
        issues.add("source_field:superseded_by")
    if group == "users":
        issues.update(
            f"source_field:{field}"
            for field in ("cardinality", "identity")
            if field in record and _text(record[field]) is None
        )
    for target_field, aliases, kind in ALIAS_GROUPS.get(group, ()):
        present = [alias for alias in aliases if alias in record]
        if len(present) < 2:
            continue
        normalized = [
            _normalized_alias_value(record[alias], kind) for alias in present
        ]
        if any(value is None for value in normalized) or len(set(normalized)) != 1:
            issues.add(target_field)
    return sorted(issues)


def _map_goal(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    values = {"statement": _text(record.get("text")), "status": _normal_status(record)}
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(
        record,
        {"id": record["id"], "statement": values["statement"]},
        str(values["status"]),
    ), []


def _map_user(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    role = _text(record.get("role"))
    labels = [
        f"{field}: {record[field]}"
        for field in ("role", "cardinality", "identity")
        if _text(record.get(field)) is not None
    ]
    description = "; ".join(labels) if labels else None
    values = {
        "actor_kind": role,
        "description": description,
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(
        record,
        {
            "id": record["id"],
            "description": values["description"],
            "actor_kind": values["actor_kind"],
        },
        str(values["status"]),
    ), []


def _map_requirement(
    record: dict[str, object],
) -> tuple[dict[str, object] | None, list[str]]:
    values = {
        "statement": _text(record.get("text")),
        "scope": _text(record.get("scope")),
        "ui_required": (
            record.get("ui_required")
            if isinstance(record.get("ui_required"), bool)
            else None
        ),
        "materiality": _materiality(record.get("materiality")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(
        record,
        {"id": record["id"], **{field: values[field] for field in (
            "statement", "scope", "ui_required", "materiality",
        )}},
        str(values["status"]),
    ), []


def _valid_unknown_origin(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != {
        "kind", "surface_ref", "pack_id", "axis_id", "source_path",
    }:
        return False
    kind = value.get("kind")
    surface = value.get("surface_ref")
    pack = value.get("pack_id")
    axis = value.get("axis_id")
    source_path = value.get("source_path")
    if kind == "MANUAL":
        return surface is None and pack is None and axis is None and source_path is None
    if kind == "MIGRATION_RECONCILIATION":
        return (
            surface is None and pack is None and axis is None
            and _text(source_path) is not None
        )
    if kind == "PRODUCT_SURFACE":
        return (
            isinstance(surface, str) and surface.startswith("SURF-")
            and pack is None and axis is None and source_path is None
        )
    if kind == "GRILL_TOPOLOGY":
        return (
            surface is None and isinstance(pack, str) and pack.startswith("GRILL-")
            and axis is None and source_path is None
        )
    if kind == "GRILL_PACK_AXIS":
        return (
            isinstance(surface, str) and surface.startswith("SURF-")
            and isinstance(pack, str) and pack.startswith("GRILL-")
            and _text(axis) is not None and source_path is None
        )
    return False


def _valid_unknown_option(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"id", "statement", "consequences"}
        and _text(value.get("id")) is not None
        and _text(value.get("statement")) is not None
        and _strings(value.get("consequences"), nonempty=True) is not None
        and all(_text(item) is not None for item in value["consequences"])
    )


def _valid_unknown_recommendation(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {
            "recommended_option", "reasoning_refs", "tradeoffs", "confidence",
        }
        and _text(value.get("recommended_option")) is not None
        and _strings(value.get("reasoning_refs"), nonempty=True) is not None
        and _strings(value.get("tradeoffs"), nonempty=True) is not None
        and all(_text(item) is not None for item in value["tradeoffs"])
        and value.get("confidence") in {"LOW", "MEDIUM", "HIGH"}
    )


def _valid_unknown_deferral(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != {"reason", "accepted_by", "impact_review"}:
        return False
    impact = value.get("impact_review")
    impact_fields = {
        "scope", "rules", "flows", "states", "privacy", "money", "security",
        "acceptance",
    }
    return (
        _text(value.get("reason")) is not None
        and value.get("accepted_by") == "user"
        and isinstance(impact, dict)
        and set(impact) == impact_fields
        and all(_text(impact[field]) is not None for field in impact_fields)
    )


def _valid_accepted_recommendation(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {
            "recommended_option", "alternatives_presented", "tradeoffs_presented",
            "accepted_by", "accepted_at",
        }
        and _text(value.get("recommended_option")) is not None
        and _strings(value.get("alternatives_presented"), nonempty=True) is not None
        and _strings(value.get("tradeoffs_presented"), nonempty=True) is not None
        and all(_text(item) is not None for item in value["tradeoffs_presented"])
        and value.get("accepted_by") == "user"
        and (value.get("accepted_at") is None or _text(value.get("accepted_at")) is not None)
    )


def _valid_unknown_field(field: str, value: object) -> bool:
    if field in {"question", "why_it_matters"}:
        return _text(value) is not None
    if field == "required_authority_class":
        return value in {"FACTUAL", "INTENT", "CONSTRAINT", "BEHAVIORAL", "PREFERENCE"}
    if field == "question_category":
        return value in {
            "CORE_FLOW", "SCOPE_BOUNDARY", "STATE_RECOVERY",
            "SECONDARY_BEHAVIOR", "PREFERENCE", "COSMETIC",
        }
    if field == "materiality":
        return _materiality(value) is not None
    if field == "decision_authority":
        return value in {
            "EVIDENCE_RESOLVABLE", "AGENT_AUTONOMOUS", "USER_CONFIRMATION",
            "USER_DECISION_REQUIRED", "EXTERNAL_AUTHORITY_REQUIRED",
        }
    if field in {"affects", "blocks_unknown_refs", "evidence_refs", "resolved_by"}:
        return _strings(value) is not None
    if field == "origin":
        return _valid_unknown_origin(value)
    if field == "response_mode":
        return value in {"MUTUALLY_EXCLUSIVE", "OPEN_RESPONSE_REQUIRED"}
    if field == "options":
        return isinstance(value, list) and all(_valid_unknown_option(item) for item in value)
    if field == "recommendation":
        return value is None or _valid_unknown_recommendation(value)
    if field == "deferral":
        return value is None or _valid_unknown_deferral(value)
    if field == "resolution_mode":
        return value is None or value in {
            "EVIDENCE", "USER_DECISION", "USER_ACCEPTED_RECOMMENDATION",
            "AGENT_NON_MATERIAL_DEFAULT", "EXTERNAL_CONSTRAINT",
            "MIGRATION_RECONCILIATION",
        }
    if field in {"resolution_summary", "blocked_reason"}:
        return value is None or _text(value) is not None
    return False


def _map_unknown(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    status = UNKNOWN_STATUS_MAP.get(str(record.get("status")))
    missing = [field for field in sorted(UNKNOWN_FIELDS) if not _valid_unknown_field(field, record.get(field))]
    if status is None:
        missing.append("status")
    if status == "RESOLVED" and (
        record.get("resolution_mode") is None
        or _text(record.get("resolution_summary")) is None
        or not _strings(record.get("resolved_by"), nonempty=True)
    ):
        missing.extend(
            field for field in ("resolution_mode", "resolution_summary", "resolved_by")
            if field not in missing
        )
    response_mode = record.get("response_mode")
    options = record.get("options")
    if (
        (response_mode == "MUTUALLY_EXCLUSIVE" and (
            not isinstance(options, list) or len(options) < 2
        ))
        or (response_mode == "OPEN_RESPONSE_REQUIRED" and options != [])
    ) and "options" not in missing:
        missing.append("options")
    if status == "DEFERRED" and not _valid_unknown_deferral(record.get("deferral")):
        if "deferral" not in missing:
            missing.append("deferral")
    if status != "DEFERRED" and record.get("deferral") is not None:
        if "deferral" not in missing:
            missing.append("deferral")
    if status == "BLOCKED" and _text(record.get("blocked_reason")) is None:
        if "blocked_reason" not in missing:
            missing.append("blocked_reason")
    if status != "BLOCKED" and record.get("blocked_reason") is not None:
        if "blocked_reason" not in missing:
            missing.append("blocked_reason")
    if missing:
        return None, sorted(missing)
    target = {"id": record["id"], "status": status}
    target.update({field: copy.deepcopy(record[field]) for field in UNKNOWN_FIELDS})
    if status == "SUPERSEDED":
        superseded_by = record.get("superseded_by")
        if not isinstance(superseded_by, str):
            return None, ["superseded_by"]
        target["superseded_by"] = superseded_by
    return target, []


def _valid_decision_field(field: str, value: object) -> bool:
    if field in {"statement", "decision_type"}:
        return _text(value) is not None
    if field == "resolution_mode":
        return value in {
            "EVIDENCE", "USER_DECISION", "USER_ACCEPTED_RECOMMENDATION",
            "AGENT_NON_MATERIAL_DEFAULT", "EXTERNAL_CONSTRAINT",
            "MIGRATION_RECONCILIATION",
        }
    if field == "decision_authority":
        return value in {
            "EVIDENCE_RESOLVABLE", "AGENT_AUTONOMOUS", "USER_CONFIRMATION",
            "USER_DECISION_REQUIRED", "EXTERNAL_AUTHORITY_REQUIRED",
        }
    if field in {"source_unknown_refs", "evidence_refs", "affects"}:
        return _strings(value) is not None
    if field == "materiality":
        return _materiality(value) is not None
    if field == "decided_by":
        return value in {"USER", "AGENT", "EXTERNAL_AUTHORITY"}
    if field == "accepted_recommendation":
        return value is None or _valid_accepted_recommendation(value)
    return False


def _map_decision(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    statement = _text(record.get("decision")) or _text(record.get("answer"))
    status = "CURRENT" if record.get("status") == "ANSWERED" else _normal_status(record)
    values = {
        "statement": statement,
        **{field: record.get(field) for field in DECISION_FIELDS - {"statement"}},
    }
    missing = [field for field in sorted(DECISION_FIELDS) if not _valid_decision_field(field, values[field])]
    if status is None:
        missing.append("status")
    if status == "CURRENT" and not _strings(values["source_unknown_refs"], nonempty=True):
        if "source_unknown_refs" not in missing:
            missing.append("source_unknown_refs")
    if values["resolution_mode"] == "USER_ACCEPTED_RECOMMENDATION":
        if not _valid_accepted_recommendation(values["accepted_recommendation"]):
            if "accepted_recommendation" not in missing:
                missing.append("accepted_recommendation")
    elif values["accepted_recommendation"] is not None:
        if "accepted_recommendation" not in missing:
            missing.append("accepted_recommendation")
    if missing:
        return None, sorted(missing)
    target = {"id": record["id"], "status": status}
    target.update({field: copy.deepcopy(values[field]) for field in DECISION_FIELDS})
    if status == "SUPERSEDED":
        target["superseded_by"] = record["superseded_by"]
    return target, []


def _map_rule(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    values = {
        "statement": _text(record.get("statement")) or _text(record.get("text")),
        "applies_to": _strings(record.get("applies_to")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {
        "id": record["id"], "statement": values["statement"],
        "applies_to": values["applies_to"],
    }, str(values["status"])), []


def _map_flow(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    values = {
        "goal_refs": _strings(record.get("goal_refs")),
        "entry": _text(record.get("entry")),
        "preconditions": _strings(record.get("preconditions")),
        "paths": _strings(record.get("paths")),
        "outcomes": _strings(record.get("outcomes")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {"id": record["id"], **{
        field: values[field]
        for field in ("goal_refs", "entry", "preconditions", "paths", "outcomes")
    }}, str(values["status"])), []


def _map_screen(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    requirements = record.get("requirement_refs", record.get("requirements"))
    values = {
        "purpose": _text(record.get("purpose")),
        "requirement_refs": _strings(requirements),
        "interaction_mode": _text(record.get("interaction_mode")),
        "major_actions": _strings(record.get("major_actions")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {"id": record["id"], **{
        field: values[field]
        for field in ("purpose", "requirement_refs", "interaction_mode", "major_actions")
    }}, str(values["status"])), []


def _map_state(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    values = {
        "owner_refs": _strings(record.get("owner_refs")),
        "state_name": _text(record.get("name")),
        "conditions": _strings(record.get("conditions")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {"id": record["id"], **{
        field: values[field] for field in ("owner_refs", "state_name", "conditions")
    }}, str(values["status"])), []


def _map_data(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    values = {
        "name": _text(record.get("name")),
        "purpose": _text(record.get("purpose")),
        "ownership": _text(record.get("ownership")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {"id": record["id"], **{
        field: values[field] for field in ("name", "purpose", "ownership")
    }}, str(values["status"])), []


def _map_integration(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    values = {
        "name": _text(record.get("name")),
        "purpose": _text(record.get("purpose")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {"id": record["id"], **{
        field: values[field] for field in ("name", "purpose")
    }}, str(values["status"])), []


def _map_acceptance(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    requirements = record.get("requirement_refs", record.get("requirements"))
    values = {
        "requirement_refs": _strings(requirements),
        "assertion": _text(record.get("assertion")) or _text(record.get("text")),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {"id": record["id"], **{
        field: values[field] for field in ("requirement_refs", "assertion")
    }}, str(values["status"])), []


def _map_task(record: dict[str, object]) -> tuple[dict[str, object] | None, list[str]]:
    acceptance = record.get("acceptance_refs", record.get("acceptance"))
    values = {
        "implements": _strings(record.get("implements"), nonempty=True),
        "acceptance_refs": _strings(acceptance, nonempty=True),
        "status": _normal_status(record),
    }
    missing = _missing(values)
    if missing:
        return None, missing
    return _with_lifecycle(record, {"id": record["id"], **{
        field: values[field] for field in ("implements", "acceptance_refs")
    }}, str(values["status"])), []


MAPPERS = {
    "goals": _map_goal,
    "users": _map_user,
    "requirements": _map_requirement,
    "unknowns": _map_unknown,
    "decisions": _map_decision,
    "rules": _map_rule,
    "flows": _map_flow,
    "screens": _map_screen,
    "states": _map_state,
    "data": _map_data,
    "integrations": _map_integration,
    "acceptance_criteria": _map_acceptance,
    "tasks": _map_task,
}


def _archive_entry(group: str, record: dict[str, object]) -> dict[str, object]:
    return {
        "source_id": record.get("id") if isinstance(record.get("id"), str) else None,
        "source_group": group,
        "source_record": copy.deepcopy(record),
        "source_record_sha256": _sha256(record),
    }


def _pointer_token_v2(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _add_gap(
    gaps: dict[str, dict[str, object]],
    *,
    source_id: str | None,
    source_path: str,
    missing_v2_fields: list[str],
) -> None:
    metadata: dict[str, object] = {
        "source_id": source_id,
        "source_path": source_path,
        "missing_v2_fields": sorted(set(missing_v2_fields)),
        "reason_code": MISSING_AUTHORITY,
    }
    key = f"gap:{_sha256(metadata)[:24]}"
    gaps[key] = metadata


def _open_cell() -> dict[str, object]:
    return {
        "status": "OPEN",
        "authority_bindings": [],
        "unknown_refs": [],
        "basis_bindings": [],
        "rationale": None,
    }


def _coverage_gap_field(status: object) -> str:
    return {
        "COVERED": "authority_bindings",
        "N/A": "basis_bindings",
        "OPEN": "unknown_refs",
    }[str(status)]


def _migrate_records(
    state: dict[str, object], gaps: dict[str, dict[str, object]],
) -> tuple[dict[str, list[dict[str, object]]], list[dict[str, object]], list[str]]:
    objects = state["objects"]
    assert isinstance(objects, dict)
    promoted: dict[str, list[dict[str, object]]] = {group: [] for group in OBJECT_GROUPS}
    archived: list[dict[str, object]] = []
    promoted_ids: list[str] = []
    for group in OBJECT_GROUPS:
        records = objects[group]
        assert isinstance(records, list)
        for position, record in enumerate(records):
            assert isinstance(record, dict)
            mapped, missing = MAPPERS[group](record)
            fidelity_issues = _source_fidelity_issues(group, record)
            if fidelity_issues:
                mapped = None
                missing = sorted(set(missing) | set(fidelity_issues))
            if mapped is not None:
                promoted[group].append(mapped)
                promoted_ids.append(str(record["id"]))
                continue
            archived.append(_archive_entry(group, record))
            _add_gap(
                gaps,
                source_id=str(record["id"]),
                source_path=f"/objects/{group}/{position}",
                missing_v2_fields=missing or ["status"],
            )
    return promoted, archived, sorted(promoted_ids)


def _migrate_coverage(
    state: dict[str, object], gaps: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    core_axes = set(load_binding_contracts()["product"]["core_axis_types"])
    result: list[dict[str, object]] = []
    coverage = state["coverage"]
    assert isinstance(coverage, list)
    for row_position, row in enumerate(coverage):
        assert isinstance(row, dict)
        feature_id = str(row["feature_id"])
        source_cells = row["cells"]
        assert isinstance(source_cells, dict)
        cells: dict[str, object] = {}
        for axis, source_cell in source_cells.items():
            assert isinstance(source_cell, dict)
            cells[str(axis)] = _open_cell()
            missing_fields = [_coverage_gap_field(source_cell["status"])]
            if axis not in core_axes:
                missing_fields.append("axis_inventory")
            _add_gap(
                gaps,
                source_id=feature_id,
                source_path=(
                    f"/coverage/{row_position}/cells/{_pointer_token_v2(axis)}"
                ),
                missing_v2_fields=missing_fields,
            )
        for axis in sorted(core_axes - set(source_cells)):
            _add_gap(
                gaps,
                source_id=feature_id,
                source_path=f"/coverage/{row_position}/cells/{_pointer_token_v2(axis)}",
                missing_v2_fields=list(ABSENT_COVERAGE_CELL_FIELDS),
            )
        result.append({"feature_id": feature_id, "cells": cells})
    return result


def _migrate_ux_coverage(
    state: dict[str, object], gaps: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    ux_contract = load_binding_contracts()["ux"]
    state_axes = set(ux_contract["state_axis_types"])
    action_axes = set(ux_contract["action_axis_types"])
    result: list[dict[str, object]] = []
    coverage = state["ux_coverage"]
    assert isinstance(coverage, list)
    for row_position, row in enumerate(coverage):
        assert isinstance(row, dict)
        screen_id = str(row["screen_id"])
        source_states = row["states"]
        assert isinstance(source_states, dict)
        states: dict[str, object] = {}
        for axis, source_cell in source_states.items():
            assert isinstance(source_cell, dict)
            states[str(axis)] = _open_cell()
            missing_fields = [_coverage_gap_field(source_cell["status"])]
            if axis not in state_axes:
                missing_fields.append("axis_inventory")
            _add_gap(
                gaps,
                source_id=screen_id,
                source_path=(
                    f"/ux_coverage/{row_position}/states/{_pointer_token_v2(axis)}"
                ),
                missing_v2_fields=missing_fields,
            )
        for axis in sorted(state_axes - set(source_states)):
            _add_gap(
                gaps,
                source_id=screen_id,
                source_path=(
                    f"/ux_coverage/{row_position}/states/{_pointer_token_v2(axis)}"
                ),
                missing_v2_fields=list(ABSENT_COVERAGE_CELL_FIELDS),
            )
        actions: list[dict[str, object]] = []
        source_actions = row["actions"]
        assert isinstance(source_actions, list)
        for action_position, action in enumerate(source_actions):
            assert isinstance(action, dict)
            source_cells = action["cells"]
            assert isinstance(source_cells, dict)
            action_cells: dict[str, object] = {}
            for axis, source_cell in source_cells.items():
                assert isinstance(source_cell, dict)
                action_cells[str(axis)] = _open_cell()
                missing_fields = [_coverage_gap_field(source_cell["status"])]
                if axis not in action_axes:
                    missing_fields.append("axis_inventory")
                _add_gap(
                    gaps,
                    source_id=screen_id,
                    source_path=(
                        f"/ux_coverage/{row_position}/actions/{action_position}"
                        f"/cells/{_pointer_token_v2(axis)}"
                    ),
                    missing_v2_fields=missing_fields,
                )
            for axis in sorted(action_axes - set(source_cells)):
                _add_gap(
                    gaps,
                    source_id=screen_id,
                    source_path=(
                        f"/ux_coverage/{row_position}/actions/{action_position}"
                        f"/cells/{_pointer_token_v2(axis)}"
                    ),
                    missing_v2_fields=list(ABSENT_COVERAGE_CELL_FIELDS),
                )
            actions.append({"key": action["key"], "cells": action_cells})
        result.append({"screen_id": screen_id, "states": states, "actions": actions})
    return result


def _build_candidate(legacy_state: dict[str, object]) -> dict[str, object]:
    plan = build_migration_plan(legacy_state)
    project = legacy_state["project"]
    assert isinstance(project, dict)
    gaps: dict[str, dict[str, object]] = {}
    objects, archived, promoted_ids = _migrate_records(legacy_state, gaps)
    coverage = _migrate_coverage(legacy_state, gaps)
    ux_coverage = _migrate_ux_coverage(legacy_state, gaps)
    coverage_targets = {
        row["feature_id"] for row in coverage
        if isinstance(row.get("feature_id"), str)
    }
    for requirement in objects["requirements"]:
        requirement_id = requirement.get("id")
        materiality = requirement.get("materiality")
        if (
            requirement.get("status") == "CURRENT"
            and isinstance(requirement_id, str)
            and isinstance(materiality, dict)
            and materiality.get("classification") == "MATERIAL"
            and requirement_id not in coverage_targets
        ):
            _add_gap(
                gaps,
                source_id=requirement_id,
                source_path=f"/coverage/{_pointer_token_v2(requirement_id)}",
                missing_v2_fields=["cells"],
            )
    ux_targets = {
        row["screen_id"] for row in ux_coverage
        if isinstance(row.get("screen_id"), str)
    }
    for screen in objects["screens"]:
        screen_id = screen.get("id")
        if (
            screen.get("status") == "CURRENT"
            and isinstance(screen_id, str)
            and screen_id not in ux_targets
        ):
            _add_gap(
                gaps,
                source_id=screen_id,
                source_path=f"/ux_coverage/{_pointer_token_v2(screen_id)}",
                missing_v2_fields=["actions", "states"],
            )
    contradictions = legacy_state["contradictions"]
    assert isinstance(contradictions, list)
    for position, record in enumerate(contradictions):
        if not isinstance(record, dict):
            continue
        archived.append(_archive_entry("contradictions", record))
        source_id = record.get("id") if isinstance(record.get("id"), str) else None
        _add_gap(
            gaps,
            source_id=source_id,
            source_path=f"/contradictions/{position}",
            missing_v2_fields=[
                "claim_a_refs", "claim_b_refs", "materiality", "resolution",
                "resolved_by", "scope_refs", "selected_authority_refs",
            ],
        )
    for domain in GRILL_PROFILE_DOMAINS:
        _add_gap(
            gaps,
            source_id=None,
            source_path=f"/surface_manifest/grill_profile/{domain}",
            missing_v2_fields=[
                "status", "surface_refs", "unknown_refs", "basis_refs", "rationale",
            ],
        )
    archived.sort(key=lambda entry: (
        str(entry["source_id"] or ""), str(entry["source_group"]),
        str(entry["source_record_sha256"]),
    ))
    preserved_ids = sorted(_preserved_ids(legacy_state))
    approval = project["approval"]
    ordered_gaps = {key: gaps[key] for key in sorted(gaps)}
    migration = {
        "mode": "MIGRATED",
        "from_schema": FROM_SCHEMA,
        "to_schema": TO_SCHEMA,
        "migration_version": MIGRATION_APPLY_VERSION,
        "source_digest": plan["source_digest"],
        "source_revision": project["definition_revision"],
        "source_legacy_status": project["status"],
        "source_legacy_approval_digest": (
            _sha256(approval) if isinstance(approval, dict) else None
        ),
        "plan_digest": _sha256(plan),
        "preserved_ids": preserved_ids,
        "promoted_ids": promoted_ids,
        "generated_ids": [],
        "legacy_records": archived,
        "reconciliation_gaps": ordered_gaps,
        "reconciliation_gap_count": len(ordered_gaps),
    }
    return {
        "schema_version": TO_SCHEMA,
        "project": {
            "slug": project["slug"],
            "definition_status": "OPEN",
            "definition_revision": project["definition_revision"] + 1,
            "bootstrap_mode": "EXISTING_PRODUCT_RECONCILIATION",
            "closure_contract": _closure_contract(),
        },
        "migration": migration,
        "evidence": [],
        "surface_manifest": {"records": [], "grill_profile": {}},
        "contradictions": [],
        "objects": objects,
        "coverage": coverage,
        "ux_coverage": ux_coverage,
        "grill_coverage": [],
        "discovery_baseline": {"status": "NOT_ESTABLISHED"},
        "approval": {"status": "UNAPPROVED"},
        "approval_history": [],
    }


def _closure_contract() -> dict[str, object]:
    identities = binding_contract_identity()
    return {
        "level": "SEMANTIC_CLOSURE",
        "product_binding_contract": identities["product"],
        "ux_binding_contract": identities["ux"],
    }


def _receipt_for(
    candidate: dict[str, object],
) -> dict[str, object]:
    migration = candidate["migration"]
    assert isinstance(migration, dict)
    archived_ids = sorted(
        entry["source_id"]
        for entry in migration["legacy_records"]
        if isinstance(entry, dict) and isinstance(entry.get("source_id"), str)
    )
    return {
        "schema_version": RECEIPT_SCHEMA,
        "migration_version": MIGRATION_APPLY_VERSION,
        "source_digest": migration["source_digest"],
        "plan_digest": migration["plan_digest"],
        "candidate_state_sha256": _sha256(candidate),
        "preserved_ids": migration["preserved_ids"],
        "promoted_ids": migration["promoted_ids"],
        "generated_ids": migration["generated_ids"],
        "archived_ids": archived_ids,
        "reconciliation_gap_count": migration["reconciliation_gap_count"],
    }


def migrate_state_v020(
    legacy_state: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    """Return a deterministic V2 reconciliation candidate and receipt."""
    candidate = _build_candidate(legacy_state)
    return candidate, _receipt_for(candidate)


def _integrity_error(code: str, path: str) -> dict[str, object]:
    return {"code": code, "path": path}


def _resolve_validation_path(candidate: dict[str, object], path: str) -> object:
    value: object = candidate
    for field, index in re.findall(r"(?:^|\.)([^.\[]+)|\[([0-9]+)\]", path):
        if field:
            if not isinstance(value, dict) or field not in value:
                return None
            value = value[field]
        else:
            if not isinstance(value, list) or int(index) >= len(value):
                return None
            value = value[int(index)]
    return value


def _semantic_error_has_gap(
    error: dict[str, object], candidate: dict[str, object],
) -> bool:
    migration = candidate.get("migration")
    gaps = migration.get("reconciliation_gaps") if isinstance(migration, dict) else None
    if not isinstance(gaps, dict):
        return False
    gap_values = [gap for gap in gaps.values() if isinstance(gap, dict)]
    gap_paths = {
        gap.get("source_path") for gap in gap_values
        if isinstance(gap.get("source_path"), str)
    }
    code = error.get("code")
    path = error.get("path")
    if not isinstance(code, str) or not isinstance(path, str):
        return False
    if code == "invalid_grill_profile" and path == "surface_manifest.grill_profile":
        return sum(
            isinstance(gap_path, str)
            and gap_path.startswith("/surface_manifest/grill_profile/")
            for gap_path in gap_paths
        ) == len(GRILL_PROFILE_DOMAINS)
    if code == "open_coverage_without_unknown":
        match = re.fullmatch(r"coverage\[([0-9]+)\]\.cells\.(.+)", path)
        return bool(
            match
            and f"/coverage/{match[1]}/cells/{_pointer_token_v2(match[2])}" in gap_paths
        )
    if code == "ux_open_without_unknown":
        state_match = re.fullmatch(r"ux_coverage\[([0-9]+)\]\.states\.(.+)", path)
        if state_match:
            return (
                f"/ux_coverage/{state_match[1]}/states/"
                f"{_pointer_token_v2(state_match[2])}"
            ) in gap_paths
        action_match = re.fullmatch(
            r"ux_coverage\[([0-9]+)\]\.actions\[([0-9]+)\]\.cells\.(.+)",
            path,
        )
        return bool(
            action_match
            and (
                f"/ux_coverage/{action_match[1]}/actions/{action_match[2]}/cells/"
                f"{_pointer_token_v2(action_match[3])}"
            ) in gap_paths
        )
    inventory_prefix: str | None = None
    inventory_source_id: object = None
    required_axes: set[str] | None = None
    if code == "core_coverage_axis_inventory_mismatch":
        match = re.fullmatch(r"coverage\[([0-9]+)\]\.cells", path)
        if match:
            inventory_prefix = f"/coverage/{match[1]}/cells/"
            inventory_source_id = _resolve_validation_path(
                candidate, f"coverage[{match[1]}].feature_id",
            )
            required_axes = set(
                load_binding_contracts()["product"]["core_axis_types"]
            )
    elif code == "screen_state_axis_inventory_mismatch":
        match = re.fullmatch(r"ux_coverage\[([0-9]+)\]\.states", path)
        if match:
            inventory_prefix = f"/ux_coverage/{match[1]}/states/"
            inventory_source_id = _resolve_validation_path(
                candidate, f"ux_coverage[{match[1]}].screen_id",
            )
            required_axes = set(
                load_binding_contracts()["ux"]["state_axis_types"]
            )
    elif code == "action_axis_inventory_mismatch":
        match = re.fullmatch(
            r"ux_coverage\[([0-9]+)\]\.actions\[([0-9]+)\]\.cells", path,
        )
        if match:
            inventory_prefix = (
                f"/ux_coverage/{match[1]}/actions/{match[2]}/cells/"
            )
            inventory_source_id = _resolve_validation_path(
                candidate, f"ux_coverage[{match[1]}].screen_id",
            )
            required_axes = set(
                load_binding_contracts()["ux"]["action_axis_types"]
            )
    if inventory_prefix is not None and required_axes is not None:
        cells = _resolve_validation_path(candidate, path)
        if not isinstance(cells, dict) or not isinstance(inventory_source_id, str):
            return False
        actual_axes = set(cells)
        missing_axes = required_axes - actual_axes
        extra_axes = actual_axes - required_axes
        if not missing_axes and not extra_axes:
            return False

        def exact_axis_gap(axis: str, *, extra: bool) -> bool:
            source_path = f"{inventory_prefix}{_pointer_token_v2(axis)}"
            matches = [
                gap for gap in gap_values
                if gap.get("source_id") == inventory_source_id
                and gap.get("source_path") == source_path
            ]
            if len(matches) != 1:
                return False
            fields = matches[0].get("missing_v2_fields")
            if not extra:
                return fields == list(ABSENT_COVERAGE_CELL_FIELDS)
            return fields in (
                ["authority_bindings", "axis_inventory"],
                ["axis_inventory", "basis_bindings"],
                ["axis_inventory", "unknown_refs"],
            )

        return all(exact_axis_gap(axis, extra=False) for axis in missing_axes) and all(
            exact_axis_gap(axis, extra=True) for axis in extra_axes
        )
    if code == "core_coverage_target_mismatch":
        match = re.fullmatch(r"coverage\[([0-9]+)\]\.feature_id", path)
        return bool(
            match
            and any(
                isinstance(gap_path, str)
                and gap_path.startswith(f"/coverage/{match[1]}/cells/")
                for gap_path in gap_paths
            )
        )
    if code in {"invalid_ux_coverage_row", "screen_action_inventory_mismatch"}:
        match = re.match(r"ux_coverage\[([0-9]+)\]", path)
        return bool(
            match
            and any(
                isinstance(gap_path, str)
                and gap_path.startswith(f"/ux_coverage/{match[1]}/")
                for gap_path in gap_paths
            )
        )
    if code in {
        "missing_authority_graph_reference",
        "historical_authority_graph_reference",
        "invalid_authority_graph_reference",
    }:
        target_id = _resolve_validation_path(candidate, path)
        return isinstance(target_id, str) and any(
            gap.get("source_id") == target_id
            and isinstance(gap.get("source_path"), str)
            and gap["source_path"].startswith("/objects/")
            for gap in gap_values
        )
    if code in {"invalid_decision_provenance", "invalid_unknown_contract"}:
        references = _resolve_validation_path(candidate, path)
        return isinstance(references, list) and any(
            isinstance(reference, str)
            and any(gap.get("source_id") == reference for gap in gap_values)
            for reference in references
        )
    if code == "unresolved_unknown_provenance":
        record = _resolve_validation_path(candidate, path)
        references = record.get("resolved_by") if isinstance(record, dict) else None
        return isinstance(references, list) and any(
            isinstance(reference, str)
            and any(gap.get("source_id") == reference for gap in gap_values)
            for reference in references
        )
    if code in {"missing_core_coverage", "missing_core_grill_coverage"}:
        match = re.fullmatch(r"coverage\.(.+)", path)
        return bool(
            match
            and f"/coverage/{_pointer_token_v2(match[1])}" in gap_paths
        )
    if code == "missing_ux_coverage":
        match = re.fullmatch(r"ux_coverage\.(.+)", path)
        return bool(
            match
            and f"/ux_coverage/{_pointer_token_v2(match[1])}" in gap_paths
        )
    return False


def verify_migration_result(
    legacy_state: dict[str, object],
    candidate: dict[str, object],
    receipt: dict[str, object],
) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    try:
        expected_candidate = _build_candidate(legacy_state)
        project = legacy_state["project"]
        assert isinstance(project, dict)
    except (AssertionError, KeyError, MigrationError, TypeError):
        return [_integrity_error("source_invalid", "")]

    if candidate != expected_candidate:
        errors.append(_integrity_error("candidate_derivation_mismatch", ""))
    if receipt != _receipt_for(expected_candidate):
        errors.append(_integrity_error("receipt_mismatch", "receipt"))

    expected_invariants = {
        "schema_version": TO_SCHEMA,
        "project.definition_status": "OPEN",
        "project.definition_revision": project["definition_revision"] + 1,
        "project.bootstrap_mode": "EXISTING_PRODUCT_RECONCILIATION",
        "project.closure_contract": _closure_contract(),
        "approval": {"status": "UNAPPROVED"},
        "approval_history": [],
        "discovery_baseline": {"status": "NOT_ESTABLISHED"},
    }

    def resolve(path: str) -> object:
        value: object = candidate
        for token in path.split("."):
            if not isinstance(value, dict) or token not in value:
                return object()
            value = value[token]
        return value

    for path, expected in expected_invariants.items():
        if resolve(path) != expected:
            errors.append(_integrity_error("candidate_invariant_mismatch", path))

    migration = candidate.get("migration")
    if not isinstance(migration, dict) or set(migration) != MIGRATION_KEYS:
        errors.append(_integrity_error("migration_metadata_mismatch", "migration"))
    else:
        expected_migration = expected_candidate["migration"]
        assert isinstance(expected_migration, dict)
        for field in MIGRATION_KEYS - {"reconciliation_gaps"}:
            if migration.get(field) != expected_migration.get(field):
                errors.append(_integrity_error(
                    "migration_metadata_mismatch", f"migration.{field}"
                ))
        if migration.get("reconciliation_gaps") != expected_migration.get("reconciliation_gaps"):
            errors.append(_integrity_error(
                "reconciliation_gap_mismatch", "migration.reconciliation_gaps"
            ))

    if receipt.get("candidate_state_sha256") != _sha256(candidate):
        errors.append(_integrity_error(
            "candidate_digest_mismatch", "receipt.candidate_state_sha256"
        ))
    candidate_validation = validate_state_v2(candidate)
    for validation_error in candidate_validation:
        if validation_error.get("code") == "schema_error":
            errors.append({
                "code": "structural_schema_error",
                "path": validation_error.get("path", ""),
                "validation_code": "schema_error",
            })
        elif not _semantic_error_has_gap(validation_error, candidate):
            errors.append({
                "code": "unattributed_semantic_error",
                "path": validation_error.get("path", ""),
                "validation_code": validation_error.get("code"),
            })
    return errors
