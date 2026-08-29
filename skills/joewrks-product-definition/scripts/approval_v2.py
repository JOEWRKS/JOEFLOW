"""Pure semantic approval, digest, manifest, and history commitments for V2 state."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from authority_binding_v2 import (
    authority_consumption_metrics,
    canonical_json,
    canonical_record_index,
    product_binding_metrics,
    sha256_json,
    ux_binding_metrics,
)
from grill_v2 import compile_active_grill_packs, grill_pack_metrics, grill_unknown_metrics
from materiality_v2 import is_high_risk, validate_materiality_classification


MANIFEST_SCHEMA_VERSION = "joewrks.approval-manifest/1.0"
OBJECT_GROUPS = (
    "goals", "users", "requirements", "unknowns", "decisions", "rules",
    "flows", "screens", "states", "data", "integrations",
    "acceptance_criteria", "tasks",
)
HISTORICAL_STATUSES = {"SUPERSEDED", "RETIRED"}
BASELINE_SEMANTIC_FIELDS = (
    "definition_revision",
    "surface_manifest_digest",
    "open_material_surface_count",
    "unresolved_material_contradiction_count",
    "procedure_complete",
    "applicable_surface_classes_complete",
    "active_grill_packs",
    "active_grill_packs_complete",
    "unknown_unknown_exhaustiveness_claimed",
)
COMMITMENT_FIELDS = (
    "revision", "definition_digest", "manifest_digest", "record_hashes",
    "coverage_digest", "surface_digest", "grill_pack_set_digest",
)
SEMANTIC_COMMITMENT_FIELDS = COMMITMENT_FIELDS[1:]
RISK_FLAGS = (
    "security", "privacy", "money", "legal_or_policy", "destructive",
    "data_loss", "external_commitment",
)
_MATERIALITY_KEYS = {
    "outcome_divergence", "fan_out", "user_visible", "reversibility",
    "risk_flags", "classification",
}
_SET_FIELDS = {
    "evidence_refs", "authority_refs", "unknown_refs", "decision_refs",
    "contradiction_refs", "source_unknown_refs", "affects", "blocks_unknown_refs",
    "resolved_by", "claim_a_refs", "claim_b_refs", "scope_refs",
    "selected_authority_refs", "requirement_refs", "goal_refs", "owner_refs",
    "applies_to", "implements", "acceptance_refs", "reasoning_refs",
    "basis_refs", "surface_refs", "authority_classes", "target_refs",
}
_BINDING_FIELDS = {"authority_bindings", "basis_bindings"}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_UTC_TIMESTAMP = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


def _error(code: str, message: str, path: str) -> dict[str, str]:
    return {"code": code, "message": message, "path": path}


def _normalized(
    value: object, *, field: str | None = None, drop_operational: bool = False,
) -> object:
    """Copy JSON data while normalizing only contractually unordered collections."""
    if isinstance(value, dict):
        return {
            key: _normalized(item, field=key, drop_operational=drop_operational)
            for key, item in value.items()
            if not (drop_operational and key == "accepted_at")
        }
    if isinstance(value, list):
        items = [_normalized(item, drop_operational=drop_operational) for item in value]
        if field in _SET_FIELDS or field in _BINDING_FIELDS:
            return sorted(items, key=canonical_json)
        return items
    canonical_json(value)
    return value


def _sorted_records(
    value: object, *, current_only: bool, drop_operational: bool = False,
) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    records = [
        record for record in value
        if isinstance(record, dict)
        and isinstance(record.get("id"), str)
        and (
            not current_only
            or record.get("status") not in HISTORICAL_STATUSES
        )
    ]
    return [
        _normalized(record, drop_operational=drop_operational)  # type: ignore[list-item]
        for record in sorted(records, key=lambda item: item["id"])
    ]


def _coverage_projection(state: dict[str, object]) -> dict[str, object]:
    core = state.get("coverage") if isinstance(state.get("coverage"), list) else []
    specialist = state.get("grill_coverage") if isinstance(state.get("grill_coverage"), list) else []
    ux = state.get("ux_coverage") if isinstance(state.get("ux_coverage"), list) else []

    normalized_core = [_normalized(row) for row in core]
    normalized_core.sort(key=lambda row: (
        row.get("feature_id", "") if isinstance(row, dict) else "",
        canonical_json(row),
    ))
    normalized_specialist = [_normalized(row) for row in specialist]
    normalized_specialist.sort(key=lambda row: (
        row.get("target_ref", "") if isinstance(row, dict) else "",
        row.get("pack_id", "") if isinstance(row, dict) else "",
        canonical_json(row),
    ))
    normalized_ux = []
    for row in ux:
        normalized = _normalized(row)
        if isinstance(normalized, dict) and isinstance(normalized.get("actions"), list):
            normalized["actions"] = sorted(
                normalized["actions"],
                key=lambda action: (
                    action.get("key", "") if isinstance(action, dict) else "",
                    canonical_json(action),
                ),
            )
        normalized_ux.append(normalized)
    normalized_ux.sort(key=lambda row: (
        row.get("screen_id", "") if isinstance(row, dict) else "",
        canonical_json(row),
    ))
    return {"core": normalized_core, "specialist": normalized_specialist, "ux": normalized_ux}


def _binding_contracts(state: dict[str, object]) -> dict[str, object]:
    project = state.get("project")
    closure = project.get("closure_contract") if isinstance(project, dict) else None
    closure = closure if isinstance(closure, dict) else {}
    return {
        "product_binding_contract": _normalized(closure.get("product_binding_contract")),
        "ux_binding_contract": _normalized(closure.get("ux_binding_contract")),
    }


def _active_grill_packs(state: dict[str, object]) -> list[dict[str, object]]:
    packs = [_normalized(pack) for pack in compile_active_grill_packs(state)]
    return sorted(packs, key=lambda pack: (
        pack.get("pack_id", "") if isinstance(pack, dict) else "",
        canonical_json(pack),
    ))  # type: ignore[return-value]


def consumed_evidence_ids(state: dict[str, object]) -> list[str]:
    """Return stable EVD IDs consumed by current semantic authority."""
    consumed: set[str] = set()

    def add(refs: object) -> None:
        if not isinstance(refs, list):
            return
        consumed.update(
            reference for reference in refs
            if isinstance(reference, str) and reference.startswith("EVD-")
        )

    objects = state.get("objects")
    objects = objects if isinstance(objects, dict) else {}
    decisions = objects.get("decisions")
    if isinstance(decisions, list):
        for record in decisions:
            if isinstance(record, dict) and record.get("status") == "CURRENT":
                add(record.get("evidence_refs"))
    unknowns = objects.get("unknowns")
    if isinstance(unknowns, list):
        for record in unknowns:
            if (
                isinstance(record, dict)
                and record.get("status") == "RESOLVED"
                and record.get("resolution_mode") in {"EVIDENCE", "EXTERNAL_CONSTRAINT"}
            ):
                add(record.get("evidence_refs"))

    manifest = state.get("surface_manifest")
    records = manifest.get("records") if isinstance(manifest, dict) else None
    if isinstance(records, list):
        for record in records:
            if isinstance(record, dict) and record.get("status") not in HISTORICAL_STATUSES:
                add(record.get("evidence_refs"))
    profile = manifest.get("grill_profile") if isinstance(manifest, dict) else None
    if isinstance(profile, dict):
        for cell in profile.values():
            if isinstance(cell, dict):
                add(cell.get("basis_refs"))

    contradictions = state.get("contradictions")
    if isinstance(contradictions, list):
        for record in contradictions:
            if isinstance(record, dict) and record.get("status") == "RESOLVED":
                add(record.get("claim_a_refs"))
                add(record.get("claim_b_refs"))
                add(record.get("selected_authority_refs"))

    def add_na_basis(value: object) -> None:
        if isinstance(value, dict):
            if value.get("status") == "N/A":
                bindings = value.get("basis_bindings")
                if isinstance(bindings, list):
                    add([
                        binding.get("record_id")
                        for binding in bindings
                        if isinstance(binding, dict)
                    ])
            for item in value.values():
                add_na_basis(item)
        elif isinstance(value, list):
            for item in value:
                add_na_basis(item)

    for field in ("coverage", "grill_coverage", "ux_coverage"):
        add_na_basis(state.get(field))
    return sorted(consumed)


def semantic_projection(state: dict[str, object]) -> dict[str, object]:
    """Project only current product meaning and exact consumed authority."""
    project = state.get("project")
    project = project if isinstance(project, dict) else {}
    objects = state.get("objects")
    objects = objects if isinstance(objects, dict) else {}
    semantic_objects: dict[str, object] = {}
    for group in OBJECT_GROUPS:
        records = objects.get(group)
        current = _sorted_records(records, current_only=True, drop_operational=True)
        if group not in {"unknowns"}:
            current = [record for record in current if record.get("status") == "CURRENT"]
        semantic_objects[group] = current

    evidence = state.get("evidence")
    evidence = evidence if isinstance(evidence, list) else []
    consumed = set(consumed_evidence_ids(state))
    semantic_evidence = [
        _normalized(record, drop_operational=True)
        for record in sorted(
            (
                record for record in evidence
                if isinstance(record, dict) and record.get("id") in consumed
            ),
            key=lambda item: item["id"],
        )
    ]

    manifest = state.get("surface_manifest")
    manifest = manifest if isinstance(manifest, dict) else {}
    baseline = state.get("discovery_baseline")
    baseline = baseline if isinstance(baseline, dict) else {}
    projection = {
        "schema_version": _normalized(state.get("schema_version")),
        "project": {
            "slug": _normalized(project.get("slug")),
            "definition_revision": _normalized(project.get("definition_revision")),
            "bootstrap_mode": _normalized(project.get("bootstrap_mode")),
            "closure_contract": _normalized(project.get("closure_contract")),
        },
        "objects": semantic_objects,
        "surface_manifest": {
            "records": _sorted_records(
                manifest.get("records"), current_only=True, drop_operational=True,
            ),
            "grill_profile": _normalized(manifest.get("grill_profile")),
        },
        "contradictions": [
            record for record in _sorted_records(
                state.get("contradictions"), current_only=True, drop_operational=True,
            )
            if record.get("status") == "RESOLVED"
        ],
        "coverage": _coverage_projection(state),
        "discovery_baseline": {
            field: _normalized(baseline[field])
            for field in BASELINE_SEMANTIC_FIELDS
            if field in baseline
        },
        "evidence": semantic_evidence,
        "active_grill_packs": _active_grill_packs(state),
    }
    canonical_json(projection)
    return projection


def definition_digest(state: dict[str, object]) -> str:
    return sha256_json(semantic_projection(state))


def semantic_record_hashes(state: dict[str, object]) -> dict[str, str]:
    """Hash every stable product record and only consumed evidence records."""
    index = canonical_record_index(state)
    consumed = set(consumed_evidence_ids(state))
    hashes = {
        record_id: sha256_json(_normalized(record))
        for record_id, (record_type, record) in index.items()
        if record_type in {
            "GOAL", "USR", "REQ", "UNK", "DEC", "RULE", "FLOW", "SCR",
            "STATE", "DATA", "INT", "AC", "TASK", "SURF", "CON",
        }
        or (record_type == "EVD" and record_id in consumed)
    }
    return {record_id: hashes[record_id] for record_id in sorted(hashes)}


def _history(state: dict[str, object]) -> list[dict[str, object]]:
    history = state.get("approval_history")
    return [entry for entry in history if isinstance(entry, dict)] if isinstance(history, list) else []


def current_approval_commitment(state: dict[str, object]) -> dict[str, object] | None:
    project = state.get("project")
    revision = project.get("definition_revision") if isinstance(project, dict) else None
    matches = [entry for entry in _history(state) if entry.get("revision") == revision]
    return matches[0] if len(matches) == 1 else None


def previous_approval_commitment(state: dict[str, object]) -> dict[str, object] | None:
    project = state.get("project")
    revision = project.get("definition_revision") if isinstance(project, dict) else None
    if not isinstance(revision, int) or isinstance(revision, bool):
        return None
    eligible = [
        entry for entry in _history(state)
        if isinstance(entry.get("revision"), int)
        and not isinstance(entry.get("revision"), bool)
        and entry["revision"] < revision
    ]
    if not eligible:
        return None
    greatest = max(entry["revision"] for entry in eligible)
    matches = [entry for entry in eligible if entry["revision"] == greatest]
    return matches[0] if len(matches) == 1 else None


def _record_summary(record_id: str, record: dict[str, object]) -> str:
    record_type = record_id.split("-", 1)[0]
    field_by_type = {
        "GOAL": "statement", "REQ": "statement", "DEC": "statement", "RULE": "statement",
        "UNK": "question", "USR": "description", "FLOW": "entry", "SCR": "purpose",
        "STATE": "state_name", "DATA": "name", "INT": "name", "AC": "assertion",
        "SURF": "name", "EVD": "claim", "CON": "resolution",
    }
    field = field_by_type.get(record_type)
    value = record.get(field) if field is not None else None
    if isinstance(value, str) and value.strip():
        return value
    if record_type == "TASK":
        implements = record.get("implements")
        if isinstance(implements, list) and implements:
            return f"Implements {', '.join(str(item) for item in implements)}"
    return record_id


def _manifest_row(record_id: str, record: dict[str, object]) -> dict[str, str]:
    return {
        "id": record_id,
        "type": record_id.split("-", 1)[0],
        "summary": _record_summary(record_id, record),
    }


def _semantic_product_readiness_metrics(state: dict[str, object]) -> dict[str, int]:
    index = canonical_record_index(state)
    evidence = {
        record_id: record
        for record_id, (record_type, record) in index.items()
        if record_type == "EVD"
    }
    surfaces = [
        record for _, (record_type, record) in index.items()
        if record_type == "SURF"
    ]
    material_surfaces = [
        record for record in surfaces
        if isinstance(record.get("materiality"), dict)
        and record["materiality"].get("classification") == "MATERIAL"
    ]
    authority_prefixes = {"REQ", "RULE", "FLOW", "DATA", "INT"}

    def has_current_authority(record: dict[str, object]) -> bool:
        refs = record.get("authority_refs")
        if not isinstance(refs, list):
            return False
        for reference in refs:
            target = index.get(reference) if isinstance(reference, str) else None
            if (
                target is not None
                and target[0] in authority_prefixes
                and target[1].get("status") == "CURRENT"
            ):
                return True
        return False

    contradictions = state.get("contradictions")
    contradiction_records = [record for record in contradictions if isinstance(record, dict)] if isinstance(contradictions, list) else []
    stale_selected = sum(
        isinstance(reference, str)
        and reference in evidence
        and evidence[reference].get("status") != "CURRENT"
        for record in contradiction_records
        for reference in (
            record.get("selected_authority_refs")
            if isinstance(record.get("selected_authority_refs"), list)
            else []
        )
    )

    materiality_records: list[object] = []
    objects = state.get("objects")
    if isinstance(objects, dict):
        for group in ("requirements", "unknowns", "decisions"):
            records = objects.get(group)
            if isinstance(records, list):
                materiality_records.extend(records)
    materiality_records.extend(surfaces)
    materiality_records.extend(contradiction_records)

    def invalid_materiality(record: object) -> bool:
        if not isinstance(record, dict):
            return True
        value = record.get("materiality")
        if not isinstance(value, dict) or set(value) != _MATERIALITY_KEYS:
            return True
        flags = value.get("risk_flags")
        shape_valid = (
            isinstance(value.get("outcome_divergence"), str)
            and value.get("outcome_divergence") in {"NONE", "LOW", "MEDIUM", "HIGH"}
            and value.get("fan_out") in {"LOCAL", "MULTI_OBJECT", "MULTI_FLOW", "SYSTEMIC"}
            and isinstance(value.get("user_visible"), bool)
            and value.get("reversibility") in {
                "TRIVIALLY_REVERSIBLE", "REVERSIBLE", "COSTLY_TO_REVERSE", "IRREVERSIBLE",
            }
            and value.get("classification") in {"MATERIAL", "NON_MATERIAL"}
            and isinstance(flags, dict)
            and set(flags) == set(RISK_FLAGS)
            and all(isinstance(flags[flag], bool) for flag in RISK_FLAGS)
        )
        return not shape_valid or not validate_materiality_classification(value)

    unknown_metrics = grill_unknown_metrics(state)
    baseline = state.get("discovery_baseline")
    return {
        "open_material_surfaces": sum(record.get("status") == "OPEN" for record in material_surfaces),
        "unbound_material_surfaces": sum(
            record.get("status") == "IN_SCOPE" and not has_current_authority(record)
            for record in material_surfaces
        ),
        "unresolved_material_contradictions": sum(
            record.get("status") == "OPEN"
            and isinstance(record.get("materiality"), dict)
            and record["materiality"].get("classification") == "MATERIAL"
            for record in contradiction_records
        ),
        "stale_selected_authority": stale_selected,
        "stale_consumed_evidence": sum(
            reference in evidence
            and evidence[reference].get("status") in {"STALE", "SUPERSEDED", "UNAVAILABLE"}
            for reference in consumed_evidence_ids(state)
        ),
        "discovery_baseline_gaps": int(
            isinstance(baseline, dict) and baseline.get("status") != "CURRENT"
        ),
        "unassessed_materiality": sum(invalid_materiality(record) for record in materiality_records),
        **{name: count for name, count in unknown_metrics.items() if name != "deferred_unknowns"},
        **grill_pack_metrics(state),
        **product_binding_metrics(state),
        **ux_binding_metrics(state),
        **authority_consumption_metrics(state),
    }


def _history_metrics(state: dict[str, object]) -> dict[str, int]:
    project = state.get("project")
    revision = project.get("definition_revision") if isinstance(project, dict) else None
    current_entries = [entry for entry in _history(state) if entry.get("revision") == revision]
    semantic_change = 0
    if len(current_entries) == 1:
        try:
            manifest = compute_approval_manifest(state)
            expected = build_approval_commitment(state, manifest)
            semantic_change = int(any(
                current_entries[0].get(field) != expected[field]
                for field in SEMANTIC_COMMITMENT_FIELDS
            ))
        except (KeyError, TypeError, ValueError):
            semantic_change = 1

    previous = previous_approval_commitment(state)
    missing = 0
    if previous is not None and isinstance(previous.get("record_hashes"), dict):
        try:
            current_ids = set(canonical_record_index(state))
        except (TypeError, ValueError):
            current_ids = set()
        missing = sum(record_id not in current_ids for record_id in previous["record_hashes"])
    return {
        "semantic_change_without_revision_increment": semantic_change,
        "approved_record_missing_from_state": missing,
    }


def semantic_readiness_metrics(state: dict[str, object]) -> dict[str, int]:
    """Return semantic blockers shared by review compilation and public validation."""
    return {**_semantic_product_readiness_metrics(state), **_history_metrics(state)}


def _semantic_closure_summary(state: dict[str, object]) -> dict[str, int]:
    metrics = _semantic_product_readiness_metrics(state)
    return {"semantic_readiness_blockers": sum(metrics.values()), **metrics}


def compute_approval_manifest(state: dict[str, object]) -> dict[str, object]:
    """Build a pure semantic manifest independent of current approval control state."""
    project = state.get("project")
    revision = project.get("definition_revision") if isinstance(project, dict) else None
    current_hashes = semantic_record_hashes(state)
    previous = previous_approval_commitment(state)
    previous_hashes = previous.get("record_hashes") if isinstance(previous, dict) else None
    previous_hashes = previous_hashes if isinstance(previous_hashes, dict) else {}
    index = canonical_record_index(state)

    changes: dict[str, list[dict[str, str]]] = {
        "added": [], "changed": [], "superseded": [], "retired": [],
    }
    for record_id in sorted(current_hashes):
        record = index[record_id][1]
        if record_id not in previous_hashes:
            changes["added"].append(_manifest_row(record_id, record))
        elif current_hashes[record_id] != previous_hashes[record_id]:
            status = record.get("status")
            category = "superseded" if status == "SUPERSEDED" else "retired" if status == "RETIRED" else "changed"
            changes[category].append(_manifest_row(record_id, record))
    for record_id in sorted(set(previous_hashes) - set(current_hashes)):
        if record_id not in index:
            continue
        record = index[record_id][1]
        status = record.get("status")
        category = "superseded" if status == "SUPERSEDED" else "retired" if status == "RETIRED" else "changed"
        changes[category].append(_manifest_row(record_id, record))

    objects = state.get("objects")
    objects = objects if isinstance(objects, dict) else {}
    decisions = objects.get("decisions")
    high_risk = []
    if isinstance(decisions, list):
        for record in decisions:
            materiality = record.get("materiality") if isinstance(record, dict) else None
            if (
                isinstance(record, dict)
                and record.get("status") == "CURRENT"
                and isinstance(materiality, dict)
                and is_high_risk(materiality)
            ):
                flags = materiality.get("risk_flags")
                high_risk.append({
                    "id": record.get("id"),
                    "statement": record.get("statement"),
                    "reversibility": materiality.get("reversibility"),
                    "risk_flags": sorted(
                        flag for flag in RISK_FLAGS
                        if isinstance(flags, dict) and flags.get(flag) is True
                    ),
                })
    high_risk.sort(key=lambda row: str(row["id"]))

    deferred = []
    unknowns = objects.get("unknowns")
    if isinstance(unknowns, list):
        for record in unknowns:
            deferral = record.get("deferral") if isinstance(record, dict) else None
            if isinstance(record, dict) and record.get("status") == "DEFERRED" and isinstance(deferral, dict):
                deferred.append({
                    "id": record.get("id"), "question": record.get("question"),
                    "reason": deferral.get("reason"),
                })
    deferred.sort(key=lambda row: str(row["id"]))

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "from_revision": previous.get("revision") if previous is not None else None,
        "to_revision": revision,
        **changes,
        "high_risk_decisions": high_risk,
        "deferred_non_blocking": deferred,
        "active_grill_packs": _active_grill_packs(state),
        "binding_contracts": _binding_contracts(state),
        "semantic_closure_summary": _semantic_closure_summary(state),
        "definition_digest": definition_digest(state),
    }
    canonical_json(manifest)
    return manifest


def build_approval_manifest(state: dict[str, object]) -> dict[str, object]:
    """Compatibility name for the pure manifest projection."""
    return compute_approval_manifest(state)


def build_approval_manifest_for_review(state: dict[str, object]) -> dict[str, object]:
    project = state.get("project")
    approval = state.get("approval")
    if not isinstance(project, dict) or project.get("definition_status") != "READY_FOR_REVIEW":
        raise ValueError("approval manifest requires READY_FOR_REVIEW")
    if approval != {"status": "UNAPPROVED"}:
        raise ValueError("approval manifest requires canonical UNAPPROVED state")
    baseline = state.get("discovery_baseline")
    if not isinstance(baseline, dict) or baseline.get("status") != "CURRENT":
        raise ValueError("approval manifest requires a CURRENT discovery baseline")
    blockers = {name: count for name, count in semantic_readiness_metrics(state).items() if count != 0}
    if blockers:
        raise ValueError(f"approval manifest semantic blockers: {canonical_json(blockers)}")
    return compute_approval_manifest(state)


def approval_manifest_digest(manifest: dict[str, object]) -> str:
    return sha256_json(manifest)


def build_approval_commitment(
    state: dict[str, object], manifest: dict[str, object],
) -> dict[str, object]:
    project = state.get("project")
    revision = project.get("definition_revision") if isinstance(project, dict) else None
    coverage = _coverage_projection(state)
    surface = semantic_projection(state)["surface_manifest"]
    packs = _active_grill_packs(state)
    return {
        "revision": revision,
        "definition_digest": definition_digest(state),
        "manifest_digest": approval_manifest_digest(manifest),
        "record_hashes": semantic_record_hashes(state),
        "coverage_digest": sha256_json({
            "coverage": coverage, "binding_contracts": _binding_contracts(state),
        }),
        "surface_digest": sha256_json(surface),
        "grill_pack_set_digest": sha256_json(packs),
    }


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not _UTC_TIMESTAMP.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _HEX64.fullmatch(value) is not None


def _valid_commitment(entry: object) -> bool:
    if not isinstance(entry, dict) or set(entry) != set(COMMITMENT_FIELDS):
        return False
    revision = entry.get("revision")
    hashes = entry.get("record_hashes")
    return (
        isinstance(revision, int) and not isinstance(revision, bool) and revision >= 1
        and all(_valid_digest(entry.get(field)) for field in SEMANTIC_COMMITMENT_FIELDS if field != "record_hashes")
        and isinstance(hashes, dict)
        and all(isinstance(record_id, str) and _valid_digest(digest) for record_id, digest in hashes.items())
    )


def _approval_analysis(state: dict[str, object]) -> tuple[list[dict[str, str]], dict[str, int]]:
    errors: list[dict[str, str]] = []
    project = state.get("project")
    definition_status = project.get("definition_status") if isinstance(project, dict) else None
    revision = project.get("definition_revision") if isinstance(project, dict) else None
    approval = state.get("approval")
    approved_shape = isinstance(approval, dict) and set(approval) == {
        "status", "approved_revision", "approved_definition_digest",
        "approved_manifest_digest", "approved_at", "approved_by",
    } and approval.get("status") == "APPROVED"
    unapproved_shape = approval == {"status": "UNAPPROVED"}

    if not approved_shape and not unapproved_shape:
        errors.append(_error(
            "invalid_approval", "approval must be the exact UNAPPROVED or APPROVED form", "approval",
        ))
    if definition_status == "CLOSED" and not approved_shape:
        errors.append(_error("invalid_approval_status", "CLOSED requires APPROVED", "approval.status"))
    if (
        isinstance(definition_status, str)
        and definition_status in {"OPEN", "BLOCKED", "READY_FOR_REVIEW"}
        and not unapproved_shape
    ):
        errors.append(_error("invalid_approval_status", f"{definition_status} requires UNAPPROVED", "approval.status"))

    history_value = state.get("approval_history")
    history = history_value if isinstance(history_value, list) else []
    malformed_history = not isinstance(history_value, list) or any(not _valid_commitment(entry) for entry in history)
    revisions = [
        entry.get("revision") for entry in history
        if isinstance(entry, dict)
        and isinstance(entry.get("revision"), int)
        and not isinstance(entry.get("revision"), bool)
    ]
    duplicate_revisions = len(revisions) != len(set(revisions))
    if malformed_history or duplicate_revisions:
        errors.append(_error(
            "approval_history_gaps", "approval_history commitments must be exact with unique revisions", "approval_history",
        ))

    history_metrics = _history_metrics(state)
    if history_metrics["semantic_change_without_revision_increment"]:
        errors.append(_error(
            "semantic_change_without_revision_increment",
            "current semantic commitment changed without incrementing definition_revision",
            "project.definition_revision",
        ))
    if history_metrics["approved_record_missing_from_state"]:
        errors.append(_error(
            "approved_record_missing_from_state",
            "a previously approved stable record is missing from canonical state",
            "approval_history",
        ))

    exact_definition = False
    exact_manifest = False
    exact_history = False
    user_recorded = False
    if approved_shape:
        user_recorded = approval.get("approved_by") == "user" and _valid_timestamp(approval.get("approved_at"))
        if not user_recorded:
            errors.append(_error(
                "missing_user_approval", "APPROVED requires approved_by=user and a supplied UTC approval time", "approval",
            ))
        try:
            manifest = compute_approval_manifest(state)
            expected = build_approval_commitment(state, manifest)
            exact_definition = (
                approval.get("approved_revision") == revision
                and approval.get("approved_definition_digest") == expected["definition_digest"]
            )
            exact_manifest = approval.get("approved_manifest_digest") == expected["manifest_digest"]
            current_entries = [
                entry for entry in history
                if isinstance(entry, dict) and entry.get("revision") == revision
            ]
            exact_history = len(current_entries) == 1 and current_entries[0] == expected
        except (KeyError, TypeError, ValueError):
            exact_definition = exact_manifest = exact_history = False
        if not exact_definition:
            errors.append(_error(
                "stale_approval", "approved revision and definition digest must match current semantics", "approval",
            ))
        if not exact_manifest:
            errors.append(_error(
                "missing_or_stale_approval_manifest", "approved manifest digest must match the pure current manifest", "approval.approved_manifest_digest",
            ))
        if not exact_history and not any(error["code"] == "approval_history_gaps" for error in errors):
            errors.append(_error(
                "approval_history_gaps", "APPROVED requires one exact current-revision history commitment", "approval_history",
            ))

    metrics = {
        "missing_user_approval": int(not (approved_shape and user_recorded)),
        "stale_approval": int(not (approved_shape and exact_definition)),
        "missing_or_stale_approval_manifest": int(not (approved_shape and exact_manifest)),
        "approval_history_gaps": int(
            malformed_history or duplicate_revisions or (approved_shape and not exact_history)
        ),
        **history_metrics,
    }
    return errors, metrics


def validate_approval(state: dict[str, object]) -> list[dict[str, str]]:
    return _approval_analysis(state)[0]


def approval_metrics(state: dict[str, object]) -> dict[str, int]:
    return _approval_analysis(state)[1]
