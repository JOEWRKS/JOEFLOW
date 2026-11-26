#!/usr/bin/env python3
"""One derivation of decision authority, resolution mode and Materiality for builders and validator.

The validator (grill_v2.validate_decision_authority_policy) derives the authority of every
OPEN unknown with grill_v2.derive_decision_authority and classifies Materiality with
materiality_v2.classify_materiality. The record builders call the same two functions through
this module, so a builder cannot emit an OPEN question the validator rejects, and it refuses a
resolution whose mode the derivation does not allow, naming the reason.

Resolution policy (an unknown answered by the user):

  derived authority of the OPEN question   mode the builder records
  ---------------------------------------  ------------------------------------------------
  USER_CONFIRMATION                        USER_ACCEPTED_RECOMMENDATION when the chosen option is
                                           the recommended one (unless the caller asks for
                                           USER_DECISION); USER_DECISION otherwise
  USER_DECISION_REQUIRED                   USER_DECISION; --accepted is refused (the question is
                                           high-risk or its recommendation is not HIGH confidence,
                                           so the answer is the user's decision, not a confirmation)
  AGENT_AUTONOMOUS                         USER_DECISION (the user may still decide a non-material
                                           detail); --accepted as for USER_CONFIRMATION
  EVIDENCE_RESOLVABLE                      refused: evidence_refs already answer the question
  EXTERNAL_AUTHORITY_REQUIRED              refused: a FACTUAL/CONSTRAINT/BEHAVIORAL question needs
                                           external authority, not a user answer

The decision authority of a RESOLVED unknown follows its mode (grill_v2.MODE_AUTHORITIES).
"""

from __future__ import annotations

import copy
from typing import Any

from grill_v2 import (
    MODE_AUTHORITIES,
    derive_decision_authority,
    derivation_reason,
    recommendation_is_confirmation_ready,
)
from materiality_v2 import classify_materiality, is_high_risk


RISK_FLAGS = ("security", "privacy", "money", "legal_or_policy", "destructive", "data_loss", "external_commitment")
DIVERGENCES = ("NONE", "LOW", "MEDIUM", "HIGH")
FAN_OUTS = ("LOCAL", "MULTI_OBJECT", "MULTI_FLOW", "SYSTEMIC")
REVERSIBILITIES = ("TRIVIALLY_REVERSIBLE", "REVERSIBLE", "COSTLY_TO_REVERSE", "IRREVERSIBLE")
CLASSIFICATIONS = ("MATERIAL", "NON_MATERIAL")
NON_MATERIAL_RULE = ("NON_MATERIAL exactly when outcome_divergence is NONE or LOW, fan_out LOCAL, reversibility "
                     "TRIVIALLY_REVERSIBLE and every risk flag false; anything else is MATERIAL")


class PolicyError(ValueError):
    """A combination the derivation does not allow; the message says why and what to do."""


def evidence_index(state: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    evidence = (state or {}).get("evidence")
    return {record["id"]: record for record in evidence if isinstance(record, dict) and isinstance(record.get("id"), str)} \
        if isinstance(evidence, list) else {}


def materiality(divergence: str, fan_out: str, user_visible: bool, reversibility: str,
                risk_flags: tuple[str, ...] = (), *, claimed: str | None = None) -> dict[str, Any]:
    """A Materiality record whose classification is derived; refuse unknown values or a contradicting claim."""
    for label, value, allowed in (("outcome_divergence", divergence, DIVERGENCES), ("fan_out", fan_out, FAN_OUTS),
                                  ("reversibility", reversibility, REVERSIBILITIES)):
        if value not in allowed:
            raise PolicyError(f"materiality {label} {value!r} is not one of {list(allowed)}")
    unknown_flags = sorted(set(risk_flags) - set(RISK_FLAGS))
    if unknown_flags:
        raise PolicyError(f"unknown risk flag(s) {unknown_flags}; risk flags are {list(RISK_FLAGS)}")
    record = {
        "outcome_divergence": divergence, "fan_out": fan_out, "user_visible": user_visible,
        "reversibility": reversibility, "risk_flags": {flag: flag in risk_flags for flag in RISK_FLAGS},
    }
    record["classification"] = classify_materiality(record)
    if claimed is not None and claimed != record["classification"]:
        raise PolicyError(
            f"materiality {divergence},{fan_out},{reversibility} with risk flags {sorted(risk_flags) or 'none'} classifies as "
            f"{record['classification']}, not {claimed}: {NON_MATERIAL_RULE}"
        )
    return record


def open_form(unknown: dict[str, Any]) -> dict[str, Any]:
    """The unknown as it stood while OPEN: the form the validator derives authority for."""
    record = copy.deepcopy(unknown)
    record.update({"status": "OPEN", "resolved_by": [], "resolution_mode": None, "resolution_summary": None})
    return record


def open_authority(unknown: dict[str, Any], index: dict[str, dict[str, Any]]) -> str:
    return derive_decision_authority(open_form(unknown), evidence_index=index)


def user_resolution(unknown: dict[str, Any], option_id: str, index: dict[str, dict[str, Any]], *,
                    accepted: bool | None = None) -> tuple[str, str]:
    """(resolution_mode, decision_authority) for a user's answer `option_id`, or PolicyError.

    accepted=None derives the mode; True insists on USER_ACCEPTED_RECOMMENDATION; False on USER_DECISION.
    """
    unknown_id = unknown.get("id")
    option_ids = [item.get("id") for item in unknown.get("options") or [] if isinstance(item, dict)]
    if option_id not in option_ids:
        raise PolicyError(f"{unknown_id}: option {option_id!r} is not one of its options {option_ids}")
    derived = open_authority(unknown, index)
    reason = derivation_reason(open_form(unknown), evidence_index=index)
    if derived == "EVIDENCE_RESOLVABLE":
        raise PolicyError(f"{unknown_id} derives EVIDENCE_RESOLVABLE ({reason}): evidence answers it and the user is not "
                          "asked. Resolve it from that evidence, or move intent evidence from evidence_refs to "
                          "recommendation.reasoning_refs before recording a user answer")
    if derived == "EXTERNAL_AUTHORITY_REQUIRED":
        raise PolicyError(f"{unknown_id} derives EXTERNAL_AUTHORITY_REQUIRED ({reason}): a user answer cannot resolve it; "
                          "record the external constraint as evidence and resolve it as EXTERNAL_CONSTRAINT")
    recommendation = unknown.get("recommendation") if isinstance(unknown.get("recommendation"), dict) else None
    is_recommended = recommendation is not None and recommendation.get("recommended_option") == option_id
    if accepted is True:
        if recommendation is None:
            raise PolicyError(f"{unknown_id} has no recommendation to accept; record the answer as USER_DECISION (drop --accepted)")
        if not is_recommended:
            raise PolicyError(f"{unknown_id}: the user chose {option_id}, but the recommendation is "
                              f"{recommendation.get('recommended_option')}; accepting it records USER_DECISION (drop --accepted)")
        if derived == "USER_DECISION_REQUIRED":
            raise PolicyError(f"{unknown_id} derives USER_DECISION_REQUIRED ({reason}), so the answer is the user's own "
                              "decision even when it picks the recommended option: drop --accepted and the builder records "
                              "USER_DECISION with a summary saying the recommendation was chosen")
        mode = "USER_ACCEPTED_RECOMMENDATION"
    elif accepted is False:
        mode = "USER_DECISION"
    else:
        mode = ("USER_ACCEPTED_RECOMMENDATION" if is_recommended and derived == "USER_CONFIRMATION"
                and recommendation_is_confirmation_ready(open_form(unknown)) else "USER_DECISION")
    return mode, MODE_AUTHORITIES[mode]


def explain_authority(unknown: dict[str, Any], index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The derived authority of an unknown in its OPEN form and the reason, for builder reports."""
    record = open_form(unknown)
    mat = record.get("materiality") if isinstance(record.get("materiality"), dict) else {}
    return {"derived_authority": derive_decision_authority(record, evidence_index=index),
            "reason": derivation_reason(record, evidence_index=index),
            "high_risk": bool(mat) and is_high_risk(mat)}
