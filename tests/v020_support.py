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
