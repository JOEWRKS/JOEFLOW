def foundation_state():
    return {
        "schema_version": "0.2.0",
        "project": {
            "slug": "v2-foundation",
            "definition_status": "OPEN",
            "definition_revision": 1,
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


def materiality(*, classification="NON_MATERIAL"):
    return {
        "outcome_divergence": "LOW",
        "fan_out": "LOCAL",
        "user_visible": False,
        "reversibility": "TRIVIALLY_REVERSIBLE",
        "risk_flags": {
            "security": False, "privacy": False, "money": False,
            "legal_or_policy": False, "destructive": False,
            "data_loss": False, "external_commitment": False,
        },
        "classification": classification,
    }
