from __future__ import annotations

import hashlib
import json
from typing import Any

from grill_v2 import compile_active_grill_packs, grill_pack_metrics


DISCOVERY_BASELINE_STATUSES = {"NOT_ESTABLISHED", "CURRENT", "STALE"}
_CURRENT_BASELINE_KEYS = {
    "status",
    "definition_revision",
    "surface_manifest_digest",
    "evidence_commitment_digest",
    "open_material_surface_count",
    "unresolved_material_contradiction_count",
    "procedure_complete",
    "applicable_surface_classes_complete",
    "active_grill_packs",
    "active_grill_packs_complete",
    "unknown_unknown_exhaustiveness_claimed",
}


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _is_material_open(record: object) -> bool:
    return (
        isinstance(record, dict)
        and record.get("status") == "OPEN"
        and isinstance(record.get("materiality"), dict)
        and record["materiality"].get("classification") == "MATERIAL"
    )


def _surface_records(state: dict[str, Any]) -> list[Any]:
    manifest = state.get("surface_manifest")
    return manifest.get("records", []) if isinstance(manifest, dict) else []


def _evidence_records(state: dict[str, Any]) -> list[Any]:
    evidence = state.get("evidence")
    return evidence if isinstance(evidence, list) else []


def _contradiction_records(state: dict[str, Any]) -> list[Any]:
    contradictions = state.get("contradictions")
    return contradictions if isinstance(contradictions, list) else []


def _is_lower_hex_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_pack_id(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split("-")
    return (
        len(parts) >= 3
        and parts[0] == "GRILL"
        and all(
            part
            and part.isascii()
            and part.isalnum()
            and part.upper() == part
            for part in parts[1:-1]
        )
        and parts[-1].isascii()
        and parts[-1].isdigit()
    )


def _is_pack_version(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split(".")
    return (
        len(parts) == 2
        and all(part and part.isascii() and part.isdigit() for part in parts)
    )


def _is_target_ref(value: object) -> bool:
    if not isinstance(value, str) or "-" not in value:
        return False
    prefix, number = value.split("-", 1)
    return (
        prefix in {"REQ", "SURF"}
        and len(number) >= 3
        and number.isascii()
        and number.isdigit()
    )


def _valid_active_grill_packs(value: object) -> bool:
    if not isinstance(value, list) or not value:
        return False
    pack_ids: list[str] = []
    for pack in value:
        if not isinstance(pack, dict) or set(pack) != {
            "pack_id", "version", "digest", "target_refs",
        }:
            return False
        pack_id = pack.get("pack_id")
        version = pack.get("version")
        target_refs = pack.get("target_refs")
        if (
            not _is_pack_id(pack_id)
            or not _is_pack_version(version)
            or not _is_lower_hex_digest(pack.get("digest"))
            or not isinstance(target_refs, list)
            or any(not _is_target_ref(reference) for reference in target_refs)
            or target_refs != sorted(set(target_refs))
        ):
            return False
        pack_ids.append(pack_id)
    return pack_ids == sorted(set(pack_ids)) and "GRILL-CORE-1" in pack_ids


def build_discovery_baseline(
    state: dict[str, Any], *, procedure_complete: bool,
    applicable_surface_classes_complete: bool,
) -> dict[str, Any]:
    project = state.get("project")
    definition_revision = project.get("definition_revision") if isinstance(project, dict) else None
    surfaces = _surface_records(state)
    evidence = _evidence_records(state)
    contradictions = _contradiction_records(state)
    active_grill_packs = compile_active_grill_packs(state)
    pack_metrics = grill_pack_metrics(state)
    return {
        "status": "CURRENT",
        "definition_revision": definition_revision,
        "surface_manifest_digest": _digest(surfaces),
        "evidence_commitment_digest": _digest(evidence),
        "open_material_surface_count": sum(_is_material_open(record) for record in surfaces),
        "unresolved_material_contradiction_count": sum(
            _is_material_open(record) for record in contradictions
        ),
        "procedure_complete": procedure_complete,
        "applicable_surface_classes_complete": applicable_surface_classes_complete,
        "active_grill_packs": active_grill_packs,
        "active_grill_packs_complete": pack_metrics["active_grill_pack_gaps"] == 0,
        "unknown_unknown_exhaustiveness_claimed": False,
    }


def validate_discovery_baseline(
    state: dict[str, Any], *, check_freshness: bool = True,
) -> list[dict[str, str]]:
    baseline = state.get("discovery_baseline")
    if not isinstance(baseline, dict):
        return [{
            "code": "invalid_discovery_baseline",
            "message": "discovery_baseline must be an object",
            "path": "discovery_baseline",
        }]
    status = baseline.get("status")
    if not isinstance(status, str) or status not in DISCOVERY_BASELINE_STATUSES:
        return [{
            "code": "invalid_discovery_baseline",
            "message": "discovery_baseline.status must be a supported status",
            "path": "discovery_baseline.status",
        }]
    if status in {"NOT_ESTABLISHED", "STALE"}:
        if set(baseline) != {"status"}:
            return [{
                "code": "invalid_discovery_baseline",
                "message": f"{status} baseline must contain only status",
                "path": "discovery_baseline",
            }]
        return []

    errors: list[dict[str, str]] = []
    if set(baseline) != _CURRENT_BASELINE_KEYS:
        errors.append({
            "code": "invalid_discovery_baseline",
            "message": "CURRENT baseline fields do not match the 0.2.0 contract",
            "path": "discovery_baseline",
        })
        return errors
    expected = build_discovery_baseline(
        state,
        procedure_complete=baseline.get("procedure_complete"),
        applicable_surface_classes_complete=baseline.get("applicable_surface_classes_complete"),
    )
    shape_valid = (
        isinstance(baseline["definition_revision"], int)
        and not isinstance(baseline["definition_revision"], bool)
        and baseline["definition_revision"] >= 1
        and all(
            _is_lower_hex_digest(baseline[field])
            for field in ("surface_manifest_digest", "evidence_commitment_digest")
        )
        and all(
            isinstance(baseline[field], int)
            and not isinstance(baseline[field], bool)
            and baseline[field] >= 0
            for field in (
                "open_material_surface_count",
                "unresolved_material_contradiction_count",
            )
        )
        and isinstance(baseline["procedure_complete"], bool)
        and isinstance(baseline["applicable_surface_classes_complete"], bool)
        and _valid_active_grill_packs(baseline["active_grill_packs"])
        and isinstance(baseline["active_grill_packs_complete"], bool)
        and baseline["unknown_unknown_exhaustiveness_claimed"] is False
    )
    if not shape_valid:
        errors.append({
            "code": "invalid_discovery_baseline",
            "message": "CURRENT baseline has invalid values",
            "path": "discovery_baseline",
        })
    elif check_freshness and baseline != expected:
        errors.append({
            "code": "stale_discovery_baseline",
            "message": "CURRENT baseline does not match deterministic recomputation",
            "path": "discovery_baseline",
        })
    return errors
