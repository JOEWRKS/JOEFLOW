from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from approval_v2 import build_approval_manifest_for_review, semantic_readiness_metrics
from authority_binding_v2 import (
    BindingError,
    authority_consumption_findings,
    canonical_record_index,
    load_binding_contracts,
)
from build_approval_manifest import _finish, _reject_constant
from state_validation_v2 import evaluate_closure_v2, validate_state_v2


SCHEMA_VERSION = "joewrks.state-candidate-preflight/1.0"
_PATH_TOKEN = re.compile(r"([^.\[\]]+)|\[(\d+)\]")
_DETAILED_METRICS = {
    "orphan_material_authority",
    "unconsumed_material_decision",
    "requirement_acceptance_gaps",
    "task_mapping_gaps",
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise ValueError("state must be an object")
    return value, raw


def _path_tokens(path: str) -> list[str | int]:
    return [int(index) if index else name for name, index in _PATH_TOKEN.findall(path)]


def _pointer(path: str) -> str:
    tokens = _path_tokens(path)
    return "/" + "/".join(str(token).replace("~", "~0").replace("/", "~1") for token in tokens)


def _resolve_path(value: object, path: str) -> object:
    current = value
    for token in _path_tokens(path):
        current = current[token]  # type: ignore[index]
    return current


def _record_pointer(state: dict[str, Any], record_id: str) -> str | None:
    objects = state.get("objects")
    if isinstance(objects, dict):
        for group, records in objects.items():
            if isinstance(records, list):
                for index, record in enumerate(records):
                    if isinstance(record, dict) and record.get("id") == record_id:
                        return f"/objects/{group}/{index}"
    for group in ("evidence", "contradictions"):
        records = state.get(group)
        if isinstance(records, list):
            for index, record in enumerate(records):
                if isinstance(record, dict) and record.get("id") == record_id:
                    return f"/{group}/{index}"
    records = state.get("surface_manifest", {}).get("records") if isinstance(state.get("surface_manifest"), dict) else None
    if isinstance(records, list):
        for index, record in enumerate(records):
            if isinstance(record, dict) and record.get("id") == record_id:
                return f"/surface_manifest/records/{index}"
    return None


def _allowed_types(state: dict[str, Any], path: str) -> list[str] | None:
    contracts = load_binding_contracts()
    tokens = _path_tokens(path)
    try:
        if len(tokens) >= 4 and tokens[0] == "coverage" and tokens[2] == "cells":
            return sorted(contracts["product"]["core_axis_types"][tokens[3]])
        if len(tokens) >= 4 and tokens[0] == "ux_coverage" and tokens[2] == "states":
            return sorted(contracts["ux"]["state_axis_types"][tokens[3]])
        if len(tokens) >= 6 and tokens[0] == "ux_coverage" and tokens[2] == "actions" and tokens[4] == "cells":
            return sorted(contracts["ux"]["action_axis_types"][tokens[5]])
        if len(tokens) >= 4 and tokens[0] == "grill_coverage" and tokens[2] == "axes":
            row = state["grill_coverage"][tokens[1]]
            return sorted(contracts["product"]["specialist_pack_types"][row["pack_id"]])
    except (KeyError, IndexError, TypeError):
        return None
    return None


def _binding_actual(
    state: dict[str, Any], path: str, code: str,
) -> tuple[str | None, object, list[str] | None, str | None]:
    allowed = _allowed_types(state, path)
    try:
        cell = _resolve_path(state, path)
    except (KeyError, IndexError, TypeError):
        return None, None, allowed, None
    if isinstance(cell, dict):
        bindings = cell.get("authority_bindings")
        if isinstance(bindings, list):
            candidates = [
                (index, binding)
                for index, binding in enumerate(bindings)
                if isinstance(binding, dict) and isinstance(binding.get("record_id"), str)
            ]
            if code == "invalid_authority_binding_type" and allowed is not None:
                candidates = [
                    item for item in candidates
                    if item[1]["record_id"].split("-", 1)[0] not in allowed
                ]
            if candidates:
                index, binding = candidates[0]
                record_id = binding["record_id"]
                return (
                    record_id,
                    {"record_id": record_id, "record_type": record_id.split("-", 1)[0]},
                    allowed,
                    f"{_pointer(path)}/authority_bindings/{index}",
                )
    return None, cell, allowed, None


def _next_action(code: str) -> str:
    if code == "orphan_material_authority":
        return "CONNECT_EXISTING_MEANING_TO_AN_ALLOWED_SEMANTIC_SINK_THEN_RERUN"
    if code == "invalid_authority_binding_type":
        return "SELECT_AUTHORITY_OF_AN_ALLOWED_TYPE_WITHOUT_CHANGING_PRODUCT_MEANING"
    if "duplicate" in code:
        return "ASSIGN_AN_UNUSED_STABLE_ID_AND_UPDATE_EXACT_REFERENCES_THEN_RERUN"
    if "lifecycle" in code or "supersed" in code or "retir" in code:
        return "COMPLETE_THE_REQUIRED_LIFECYCLE_FIELDS_AND_REFERENCES_THEN_RERUN"
    if code in {"requirement_acceptance_gaps", "task_mapping_gaps"}:
        return "ADD_THE_MISSING_EXISTING-SCOPE_DELIVERY_LINK_THEN_RERUN"
    return "CORRECT_THE_CANDIDATE_AT_THE_REPORTED_POINTER_THEN_RERUN"


def _validation_findings(state: dict[str, Any], errors: list[dict[str, str]]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for position, error in enumerate(errors, 1):
        code = error.get("code", "validation_error")
        path = error.get("path", "")
        object_id: str | None = None
        actual: object = None
        allowed: list[str] | None = None
        binding_pointer: str | None = None
        if path:
            object_id, actual, allowed, binding_pointer = _binding_actual(state, path, code)
            if actual is None:
                try:
                    actual = _resolve_path(state, path)
                except (KeyError, IndexError, TypeError):
                    actual = None
        if code == "duplicate_id":
            match = re.search(r"([A-Z]+-[0-9]+)", error.get("message", ""))
            object_id = match.group(1) if match else object_id
        if object_id is None and isinstance(actual, dict) and isinstance(actual.get("id"), str):
            object_id = actual["id"]
        cause = error.get("message", code)
        if code in {"invalid_supersession", "invalid_retirement"}:
            cause = f"lifecycle validation: {cause}"
        findings.append({
            "id": f"VALIDATION-{position:04d}",
            "code": code,
            "object_id": object_id,
            "pointer": binding_pointer or (_pointer(path) if path else None),
            "actual": actual,
            "allowed_types": allowed,
            "cause": cause,
            "next_action": _next_action(code),
        })
    return findings


def _readiness_findings(state: dict[str, Any], metrics: dict[str, int]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    try:
        detailed = authority_consumption_findings(state)
    except (BindingError, KeyError, TypeError, ValueError):
        detailed = {}
    for metric in sorted(metrics):
        count = metrics[metric]
        if not count:
            continue
        record_ids = detailed.get(metric, []) if metric in _DETAILED_METRICS else []
        if record_ids:
            for record_id in record_ids:
                findings.append({
                    "id": f"READINESS-{len(findings) + 1:04d}",
                    "code": metric,
                    "object_id": record_id,
                    "pointer": _record_pointer(state, record_id),
                    "actual": {"record_id": record_id, "counted_in_metric": metric},
                    "allowed_types": None,
                    "cause": f"{record_id} cannot reach an eligible semantic sink through the current typed authority graph" if metric == "orphan_material_authority" else f"{record_id} contributes to {metric}",
                    "next_action": _next_action(metric),
                })
        elif metric not in _DETAILED_METRICS:
            findings.append({
                "id": f"READINESS-{len(findings) + 1:04d}",
                "code": metric,
                "object_id": None,
                "pointer": None,
                "actual": count,
                "allowed_types": None,
                "cause": f"semantic readiness metric {metric} is nonzero",
                "next_action": _next_action(metric),
            })
    return findings


def preflight_state(candidate_path: Path | str, canonical_path: Path | str | None = None) -> dict[str, object]:
    candidate = Path(candidate_path).resolve()
    canonical = Path(canonical_path).resolve() if canonical_path is not None else None
    state, candidate_raw = _load_json(candidate)
    canonical_raw = canonical.read_bytes() if canonical is not None else None

    try:
        errors = validate_state_v2(state)
    except (BindingError, KeyError, TypeError, ValueError) as exc:
        errors = [{"code": "unsafe_state_validation", "message": str(exc), "path": ""}]
    try:
        metrics = semantic_readiness_metrics(state)
    except (BindingError, KeyError, TypeError, ValueError):
        closure = evaluate_closure_v2(state)
        metrics = {name: count for name, count in closure.get("metrics", {}).items() if isinstance(count, int)}
    blocking_metrics = {name: count for name, count in metrics.items() if count}
    findings = _validation_findings(state, errors) + _readiness_findings(state, blocking_metrics)

    manifest_ready = False
    if not errors and not blocking_metrics:
        try:
            build_approval_manifest_for_review(state)
            manifest_ready = True
        except (BindingError, KeyError, TypeError, ValueError) as exc:
            findings.append({
                "id": f"MANIFEST-{len(findings) + 1:04d}",
                "code": "manifest_review_not_ready",
                "object_id": None,
                "pointer": "/project/definition_status",
                "actual": state.get("project", {}).get("definition_status") if isinstance(state.get("project"), dict) else None,
                "allowed_types": None,
                "cause": str(exc),
                "next_action": "SATISFY_REVIEW_READINESS_WITHOUT_RECORDING_APPROVAL_THEN_RERUN",
            })

    approval = state.get("approval") if isinstance(state.get("approval"), dict) else {}
    project = state.get("project") if isinstance(state.get("project"), dict) else {}
    closure = evaluate_closure_v2(state)
    overall = "PASS" if not errors and not blocking_metrics and manifest_ready else "FAIL"
    candidate_after = candidate.read_bytes()
    canonical_after = canonical.read_bytes() if canonical is not None else None
    return {
        "schema_version": SCHEMA_VERSION,
        "source": {"path": str(candidate), "sha256": _sha256_bytes(candidate_raw)},
        "canonical": None if canonical is None else {"path": str(canonical), "sha256": _sha256_bytes(canonical_raw or b"")},
        "source_unchanged": candidate_after == candidate_raw,
        "canonical_unchanged": None if canonical is None else canonical_after == canonical_raw,
        "identity": {
            "schema_version": state.get("schema_version"),
            "definition_revision": project.get("definition_revision"),
            "definition_status": project.get("definition_status"),
            "approval_status": approval.get("status"),
            "definition_digest": closure.get("definition_digest"),
        },
        "stages": {
            "state_validation": "PASS" if not errors else "FAIL",
            "semantic_readiness": "PASS" if not blocking_metrics else "FAIL",
            "manifest_review_readiness": "PASS" if manifest_ready else "NOT_READY",
            "user_approval": "APPROVED" if approval.get("status") == "APPROVED" else "UNAPPROVED",
        },
        "overall_status": overall,
        "findings": findings,
        "summary": {
            "validation_error_count": len(errors),
            "blocking_metric_count": len(blocking_metrics),
            "finding_count": len(findings),
        },
        "next_action": "PRESENT_EXACT_MANIFEST_FOR_USER_REVIEW" if overall == "PASS" else "CORRECT_REPORTED_CANDIDATE_FINDINGS_AND_RERUN",
    }


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 4} or (len(argv) == 4 and argv[2] != "--canonical"):
        return _finish(
            {"error": "usage: preflight_state_candidate.py CANDIDATE_STATE_JSON [--canonical CANONICAL_STATE_JSON]"},
            stream=sys.stderr,
            return_code=2,
        )
    try:
        result = preflight_state(argv[1], argv[3] if len(argv) == 4 else None)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return _finish({"error": str(exc)}, stream=sys.stderr, return_code=2)
    return _finish(result, stream=sys.stdout, return_code=0 if result["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
