GRILL_PROFILE_DOMAINS = (
    "AUTH", "MONEY", "FILE_UPLOAD", "ASYNC", "PERMISSION",
    "DESTRUCTIVE_ACTION",
)


def grill_profile(*, basis_ref="EVD-900"):
    return {
        domain: {
            "status": "N/A",
            "surface_refs": [],
            "unknown_refs": [],
            "basis_refs": [basis_ref],
            "rationale": "Discovery found no applicable topology in this domain.",
        }
        for domain in GRILL_PROFILE_DOMAINS
    }


def grill_profile_basis_evidence():
    return {
        "id": "EVD-900",
        "status": "CURRENT",
        "source_kind": "USER_CONFIRMED_INTENT",
        "locator": "product-definition/topology-classification",
        "claim": "The six specialist topology domains were explicitly classified.",
        "confidence": "DIRECT",
        "authority_classes": ["INTENT"],
        "observed_version": None,
        "content_hash": None,
    }


def evidence_with_grill_basis(*records):
    return [
        record for record in records if record.get("id") != "EVD-900"
    ] + [grill_profile_basis_evidence()]


def foundation_state():
    return {
        "schema_version": "0.2.0",
        "project": {
            "slug": "v2-foundation",
            "definition_status": "OPEN",
            "definition_revision": 1,
            "bootstrap_mode": "NEW_PRODUCT",
            "closure_contract": {
                "level": "SEMANTIC_CLOSURE",
                "product_binding_contract": {"contract_id": "joewrks.product-coverage-binding", "version": "1.0", "digest": "b57459533247de52038aacb158e785c2184edcdd2fa6831f0edc3db713775f3c"},
                "ux_binding_contract": {"contract_id": "joewrks.ux-coverage-binding", "version": "1.0", "digest": "8fc84057a4a6f0f0ce329a58d11b8e208989800147d703665cea52088de0be0d"},
            },
        },
        "migration": {"mode": "NATIVE"},
        "evidence": evidence_with_grill_basis(),
        "surface_manifest": {"records": [], "grill_profile": grill_profile()},
        "contradictions": [],
        "objects": {
            "goals": [], "users": [], "requirements": [], "unknowns": [],
            "decisions": [], "rules": [], "flows": [], "screens": [],
            "states": [], "data": [], "integrations": [],
            "acceptance_criteria": [], "tasks": [],
        },
        "coverage": [],
        "ux_coverage": [],
        "grill_coverage": [],
        "discovery_baseline": {"status": "NOT_ESTABLISHED"},
        "approval": {"status": "UNAPPROVED"},
        "approval_history": [],
    }


def establish_current_baseline(state, *, procedure_complete=True, applicable_surface_classes_complete=True):
    """Install the real deterministic M3 baseline and return the same state."""
    from discovery_v2 import build_discovery_baseline

    state["discovery_baseline"] = build_discovery_baseline(
        state,
        procedure_complete=procedure_complete,
        applicable_surface_classes_complete=applicable_surface_classes_complete,
    )
    return state


def review_ready_state():
    state = foundation_state()
    state["project"]["definition_status"] = "READY_FOR_REVIEW"
    return establish_current_baseline(state)


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
