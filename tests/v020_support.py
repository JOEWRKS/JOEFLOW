def foundation_state():
    return {
        "schema_version": "0.2.0",
        "project": {
            "slug": "v2-foundation",
            "definition_status": "OPEN",
            "definition_revision": 1,
            "bootstrap_mode": "NEW_PRODUCT",
            "closure_contract": {"level": "SEMANTIC_CLOSURE"},
        },
        "migration": {"mode": "NATIVE"},
        "evidence": [],
        "surface_manifest": {"records": []},
        "contradictions": [],
        "objects": {
            "goals": [], "users": [], "requirements": [], "unknowns": [],
            "decisions": [], "rules": [], "flows": [], "screens": [],
            "states": [], "data": [], "integrations": [],
            "acceptance_criteria": [], "tasks": [],
        },
        "coverage": [],
        "ux_coverage": [],
        "discovery_baseline": {"status": "NOT_ESTABLISHED"},
        "approval": {"status": "UNAPPROVED"},
        "approval_history": [],
    }


def evidence_record(
    evidence_id="EVD-001",
    *,
    source_kind="OBSERVED_IMPLEMENTATION",
    authority_classes=None,
    confidence="DIRECT",
    status="CURRENT",
    claim="The current implementation rejects duplicate submissions.",
    locator="src/submit.py",
):
    if authority_classes is None:
        authority_classes = ["FACTUAL", "BEHAVIORAL"]
    return {
        "id": evidence_id,
        "status": status,
        "source_kind": source_kind,
        "locator": locator,
        "claim": claim,
        "confidence": confidence,
        "authority_classes": list(authority_classes),
        "observed_version": None,
        "content_hash": None,
    }


def materiality(*, classification="NON_MATERIAL", user_visible=False):
    if classification == "NON_MATERIAL":
        return {
            "outcome_divergence": "LOW",
            "fan_out": "LOCAL",
            "user_visible": user_visible,
            "reversibility": "TRIVIALLY_REVERSIBLE",
            "risk_flags": {
                "security": False, "privacy": False, "money": False,
                "legal_or_policy": False, "destructive": False,
                "data_loss": False, "external_commitment": False,
            },
            "classification": "NON_MATERIAL",
        }
    if classification == "MATERIAL":
        return {
            "outcome_divergence": "MEDIUM",
            "fan_out": "MULTI_OBJECT",
            "user_visible": True,
            "reversibility": "REVERSIBLE",
            "risk_flags": {
                "security": False, "privacy": False, "money": False,
                "legal_or_policy": False, "destructive": False,
                "data_loss": False, "external_commitment": False,
            },
            "classification": "MATERIAL",
        }
    raise ValueError(classification)


def surface_record(
    surface_id="SURF-001",
    *,
    kind="FEATURE_AREA",
    status="IN_SCOPE",
    name="Feedback submission",
    classification="MATERIAL",
):
    return {
        "id": surface_id,
        "kind": kind,
        "name": name,
        "status": status,
        "materiality": materiality(classification=classification),
        "evidence_refs": [],
        "authority_refs": [],
        "unknown_refs": [],
        "decision_refs": [],
        "contradiction_refs": [],
        "rationale": None,
        "intent_classification": None,
    }


def unknown_record(
    unknown_id="UNK-001",
    *,
    status="OPEN",
    classification="MATERIAL",
    decision_authority="USER_DECISION_REQUIRED",
    required_authority_class="INTENT",
    question_category="CORE_FLOW",
    response_mode="MUTUALLY_EXCLUSIVE",
    origin=None,
):
    if origin is None:
        origin = {
            "kind": "MANUAL",
            "surface_ref": None,
            "pack_id": None,
            "axis_id": None,
            "source_path": None,
        }
    options = [
        {
            "id": "OPT-A",
            "statement": "Keep the current product behavior.",
            "consequences": ["The current behavior remains authoritative."],
        },
        {
            "id": "OPT-B",
            "statement": "Adopt the alternative product behavior.",
            "consequences": ["The alternative behavior becomes authoritative."],
        },
    ]
    if response_mode == "OPEN_RESPONSE_REQUIRED":
        options = []
    return {
        "id": unknown_id,
        "status": status,
        "question": "Which product behavior should be authoritative?",
        "why_it_matters": "The answer changes the product behavior users receive.",
        "required_authority_class": required_authority_class,
        "question_category": question_category,
        "materiality": materiality(classification=classification),
        "decision_authority": decision_authority,
        "affects": [],
        "blocks_unknown_refs": [],
        "origin": origin,
        "response_mode": response_mode,
        "options": options,
        "recommendation": None,
        "evidence_refs": [],
        "resolved_by": [],
        "resolution_mode": None,
        "resolution_summary": None,
        "deferral": None,
        "blocked_reason": None,
    }


def decision_record(
    decision_id="DEC-001",
    *,
    status="CURRENT",
    source_unknown_refs=None,
    resolution_mode="USER_DECISION",
    decision_authority="USER_DECISION_REQUIRED",
    decided_by="USER",
    classification="MATERIAL",
    accepted_recommendation=None,
):
    if source_unknown_refs is None:
        source_unknown_refs = ["UNK-001"]
    return {
        "id": decision_id,
        "status": status,
        "statement": "Use the selected product behavior.",
        "decision_type": "PRODUCT_POLICY",
        "resolution_mode": resolution_mode,
        "decision_authority": decision_authority,
        "source_unknown_refs": list(source_unknown_refs),
        "evidence_refs": [],
        "materiality": materiality(classification=classification),
        "affects": [],
        "decided_by": decided_by,
        "accepted_recommendation": accepted_recommendation,
    }
