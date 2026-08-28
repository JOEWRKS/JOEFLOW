from __future__ import annotations

from typing import Any

import state_validation as legacy


LEGACY_VERSION = "0.1.2.1"
V2_VERSION = "0.2.0"
SUPPORTED_SCHEMA_VERSIONS = (LEGACY_VERSION, V2_VERSION)


def _unsupported(version: Any) -> dict[str, str]:
    return {
        "code": "unsupported_schema_version",
        "message": f"unsupported schema_version {version!r}",
        "path": "schema_version",
    }


def validate_state_for_version(state: dict[str, Any]) -> list[dict[str, str]]:
    version = state.get("schema_version")
    if version == LEGACY_VERSION:
        return legacy.validate_state(state)
    if version == V2_VERSION:
        from state_validation_v2 import validate_state_v2

        return validate_state_v2(state)
    return [_unsupported(version)]


def evaluate_closure_for_version(state: dict[str, Any]) -> dict[str, Any]:
    version = state.get("schema_version")
    if version == LEGACY_VERSION:
        errors = legacy.validate_state(state)
        metrics = legacy.closure_metrics(state)
        return {
            "errors": errors,
            "metrics": metrics,
            "closed": not errors and all(value == 0 for value in metrics.values()),
            "definition_digest": legacy.definition_digest(state),
        }
    if version == V2_VERSION:
        from state_validation_v2 import evaluate_closure_v2

        return evaluate_closure_v2(state)
    return {
        "errors": [_unsupported(version)],
        "metrics": {},
        "closed": False,
        "definition_digest": None,
    }
