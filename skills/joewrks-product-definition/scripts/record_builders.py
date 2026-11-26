#!/usr/bin/env python3
"""Build complete V2 evidence, unknown, and decision records from the few fields an author decides.

Decision authority and Materiality come from decision_policy.py, which calls the
validator's own derivation, so a built record never disagrees with validation.
"""

from __future__ import annotations

from typing import Any

import decision_policy as policy
from materiality_v2 import classify_materiality


RISK_FLAGS = policy.RISK_FLAGS
DEFAULT_MATERIALITY = ("HIGH", "MULTI_FLOW", True, "REVERSIBLE")
AUTHORING_MATERIALITY = ("LOW", "LOCAL", False, "TRIVIALLY_REVERSIBLE")
AUTHORING_OPTIONS = (
    ("A", "Agent writes the decided meaning into records as stated", "No new product meaning"),
    ("B", "Do not write the records", "Semantic Closure is not possible"),
)
__all__ = ["classify_materiality"]


def materiality(divergence: str, fan_out: str, user_visible: bool, reversibility: str,
                risk_flags: tuple[str, ...] = (), *, claimed: str | None = None) -> dict[str, Any]:
    """A Materiality record with the derived classification (claimed must match it)."""
    return policy.materiality(divergence, fan_out, user_visible, reversibility, tuple(risk_flags), claimed=claimed)


def option(option_id: str, statement: str, *consequences: str) -> dict[str, Any]:
    return {"id": option_id, "statement": statement, "consequences": list(consequences)}


def recommendation(option_id: str, reasoning_refs: list[str], tradeoffs: list[str], confidence: str = "HIGH") -> dict[str, Any]:
    return {"recommended_option": option_id, "reasoning_refs": list(reasoning_refs), "tradeoffs": list(tradeoffs), "confidence": confidence}


def evidence(evidence_id: str, *, source_kind: str, authority_classes: list[str], locator: str, claim: str,
             confidence: str = "DIRECT") -> dict[str, Any]:
    return {"id": evidence_id, "status": "CURRENT", "source_kind": source_kind, "locator": locator, "claim": claim,
            "confidence": confidence, "authority_classes": list(authority_classes),
            "observed_version": None, "content_hash": None}


def origin(surface: str | None = None, pack: str | None = None, axis: str | None = None) -> dict[str, Any]:
    """PRODUCT_SURFACE (surface), GRILL_PACK_AXIS (pack, axis, surface = pack target), GRILL_TOPOLOGY (pack only) or MANUAL."""
    if pack and axis:
        return {"kind": "GRILL_PACK_AXIS", "surface_ref": surface, "pack_id": pack, "axis_id": axis, "source_path": None}
    if pack:
        return {"kind": "GRILL_TOPOLOGY", "surface_ref": None, "pack_id": pack, "axis_id": None, "source_path": None}
    return {"kind": "PRODUCT_SURFACE" if surface else "MANUAL", "surface_ref": surface,
            "pack_id": None, "axis_id": None, "source_path": None}


def unknown(unknown_id: str, *, question: str, why: str, category: str, options: list[dict[str, Any]],
            affects: list[str], evidence_refs: list[str], surface: str | None = None,
            rec: dict[str, Any] | None = None, mat: dict[str, Any] | None = None,
            required_authority_class: str = "INTENT", pack: str | None = None, axis: str | None = None,
            index: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """An OPEN unknown whose decision_authority is the validator's derivation.

    `index` is the state's evidence by ID; without it, evidence_refs are assumed not to answer the question.
    """
    record = {
        "id": unknown_id, "status": "OPEN", "question": question, "why_it_matters": why,
        "required_authority_class": required_authority_class, "question_category": category,
        "materiality": mat or materiality(*DEFAULT_MATERIALITY),
        "decision_authority": None,
        "affects": list(affects), "blocks_unknown_refs": [],
        "origin": origin(surface, pack, axis),
        "response_mode": "MUTUALLY_EXCLUSIVE", "options": options, "recommendation": rec,
        "evidence_refs": list(evidence_refs), "resolved_by": [], "resolution_mode": None,
        "resolution_summary": None, "deferral": None, "blocked_reason": None,
    }
    record["decision_authority"] = policy.open_authority(record, index or {})
    return record


def user_decision(record: dict[str, Any], decision_id: str, *, statement: str, summary: str,
                  decision_type: str = "PRODUCT_BEHAVIOR", accepted: bool = False,
                  index: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Resolve `record` in place from the user's own words and return the CURRENT decision.

    accepted=True records that the user accepted the presented recommendation; decision_policy
    refuses it (PolicyError, a ValueError) when the question derives USER_DECISION_REQUIRED.
    """
    if accepted and not record.get("recommendation"):
        raise ValueError(f"{record['id']} has no recommendation to accept")
    chosen = record["recommendation"]["recommended_option"] if accepted else (
        (record.get("recommendation") or {}).get("recommended_option") or record["options"][0]["id"])
    mode, authority = policy.user_resolution(record, chosen, index or {}, accepted=True if accepted else False)
    record.update({"status": "RESOLVED", "decision_authority": authority, "resolved_by": [decision_id],
                   "resolution_mode": mode, "resolution_summary": summary})
    acceptance = None
    if accepted:
        rec = record["recommendation"]
        acceptance = {"recommended_option": rec["recommended_option"],
                      "alternatives_presented": [item["id"] for item in record["options"]],
                      "tradeoffs_presented": rec["tradeoffs"], "accepted_by": "user", "accepted_at": None}
    return {"id": decision_id, "status": "CURRENT", "statement": statement, "decision_type": decision_type,
            "resolution_mode": mode, "decision_authority": authority, "source_unknown_refs": [record["id"]],
            "evidence_refs": list(record["evidence_refs"]), "materiality": record["materiality"],
            "affects": list(record["affects"]), "decided_by": "USER", "accepted_recommendation": acceptance}


def authoring_pair(unknown_id: str, decision_id: str, *, task: str, why: str, summary: str, statement: str,
                   affects: list[str], evidence_refs: list[str], surface: str | None = None,
                   options: list[dict[str, Any]] | None = None,
                   ) -> tuple[dict[str, Any], dict[str, Any]]:
    """A RESOLVED non-material authoring unknown and its AGENT decision (writing decided meaning into records)."""
    record = unknown(unknown_id, question=task, why=why, category="SECONDARY_BEHAVIOR",
                     options=options or [option(*item) for item in AUTHORING_OPTIONS], affects=affects,
                     evidence_refs=evidence_refs, surface=surface, mat=materiality(*AUTHORING_MATERIALITY))
    record.update({"decision_authority": "AGENT_AUTONOMOUS", "status": "RESOLVED", "resolved_by": [decision_id],
                   "resolution_mode": "AGENT_NON_MATERIAL_DEFAULT", "resolution_summary": summary})
    decision = {"id": decision_id, "status": "CURRENT", "statement": statement, "decision_type": "AUTHORING",
                "resolution_mode": "AGENT_NON_MATERIAL_DEFAULT", "decision_authority": "AGENT_AUTONOMOUS",
                "source_unknown_refs": [unknown_id], "evidence_refs": list(evidence_refs),
                "materiality": record["materiality"], "affects": list(affects), "decided_by": "AGENT",
                "accepted_recommendation": None}
    return record, decision
