"""Deterministic, read-only planning for legacy state 0.1.2.1 migration."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import state_validation as legacy


MIGRATION_VERSION = "0.2.0-foundation.1"
FROM_SCHEMA = "0.1.2.1"
TO_SCHEMA = "0.2.0"
PLAN_SCHEMA = "joewrks.state-migration-plan/1.0"


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
