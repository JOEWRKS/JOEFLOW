#!/usr/bin/env python3
"""Build complete V2 evidence, unknown, and decision records from the few fields an author decides."""

from __future__ import annotations

from typing import Any

from materiality_v2 import classify_materiality


RISK_FLAGS = ("security", "privacy", "money", "legal_or_policy", "destructive", "data_loss", "external_commitment")
DEFAULT_MATERIALITY = ("HIGH", "MULTI_FLOW", True, "REVERSIBLE")
AUTHORING_MATERIALITY = ("LOW", "LOCAL", False, "TRIVIALLY_REVERSIBLE")
AUTHORING_OPTIONS = (
    ("A", "Agent writes the decided meaning into records as stated", "No new product meaning"),
    ("B", "Do not write the records", "Semantic Closure is not possible"),
)


def materiality(divergence: str, fan_out: str, user_visible: bool, reversibility: str,
                risk_flags: tuple[str, ...] = ()) -> dict[str, Any]:
    record = {
        "outcome_divergence": divergence, "fan_out": fan_out, "user_visible": user_visible,
        "reversibility": reversibility, "risk_flags": {flag: flag in risk_flags for flag in RISK_FLAGS},
    }
    record["classification"] = classify_materiality(record)
    return record


def option(option_id: str, statement: str, *consequences: str) -> dict[str, Any]:
    return {"id": option_id, "statement": statement, "consequences": list(consequences)}


def recommendation(option_id: str, reasoning_refs: list[str], tradeoffs: list[str], confidence: str = "HIGH") -> dict[str, Any]:
    return {"recommended_option": option_id, "reasoning_refs": list(reasoning_refs), "tradeoffs": list(tradeoffs), "confidence": confidence}


def evidence(evidence_id: str, *, source_kind: str, authority_classes: list[str], locator: str, claim: str,
             confidence: str = "DIRECT") -> dict[str, Any]:
    return {"id": evidence_id, "status": "CURRENT", "source_kind": source_kind, "locator": locator, "claim": claim,
            "confidence": confidence, "authority_classes": list(authority_classes),
            "observed_version": None, "content_hash": None}


def unknown(unknown_id: str, *, question: str, why: str, category: str, options: list[dict[str, Any]],
            affects: list[str], evidence_refs: list[str], surface: str | None = None,
            rec: dict[str, Any] | None = None, mat: dict[str, Any] | None = None,
            required_authority_class: str = "INTENT") -> dict[str, Any]:
    """An OPEN unknown; USER_CONFIRMATION when it carries a HIGH-confidence recommendation."""
    return {
        "id": unknown_id, "status": "OPEN", "question": question, "why_it_matters": why,
        "required_authority_class": required_authority_class, "question_category": category,
        "materiality": mat or materiality(*DEFAULT_MATERIALITY),
        "decision_authority": "USER_CONFIRMATION" if rec and rec["confidence"] == "HIGH" else "USER_DECISION_REQUIRED",
        "affects": list(affects), "blocks_unknown_refs": [],
        "origin": {"kind": "PRODUCT_SURFACE" if surface else "MANUAL", "surface_ref": surface,
                   "pack_id": None, "axis_id": None, "source_path": None},
        "response_mode": "MUTUALLY_EXCLUSIVE", "options": options, "recommendation": rec,
        "evidence_refs": list(evidence_refs), "resolved_by": [], "resolution_mode": None,
        "resolution_summary": None, "deferral": None, "blocked_reason": None,
    }


def user_decision(record: dict[str, Any], decision_id: str, *, statement: str, summary: str,
                  decision_type: str = "PRODUCT_BEHAVIOR", accepted: bool = False) -> dict[str, Any]:
    """Resolve `record` in place from the user's own words and return the CURRENT decision.

    accepted=True records that the user accepted the presented recommendation.
    """
    mode = "USER_ACCEPTED_RECOMMENDATION" if accepted else "USER_DECISION"
    authority = "USER_CONFIRMATION" if accepted else "USER_DECISION_REQUIRED"
    if accepted and not record.get("recommendation"):
        raise ValueError(f"{record['id']} has no recommendation to accept")
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
