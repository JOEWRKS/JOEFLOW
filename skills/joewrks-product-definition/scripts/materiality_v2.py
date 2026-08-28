from __future__ import annotations


_RISK_FLAG_KEYS = (
    "security", "privacy", "money", "legal_or_policy", "destructive",
    "data_loss", "external_commitment",
)


def classify_materiality(materiality: dict[str, object]) -> str:
    risk_flags = materiality.get("risk_flags")
    is_non_material = (
        materiality.get("outcome_divergence") in {"NONE", "LOW"}
        and materiality.get("fan_out") == "LOCAL"
        and materiality.get("reversibility") == "TRIVIALLY_REVERSIBLE"
        and isinstance(risk_flags, dict)
        and set(risk_flags) == set(_RISK_FLAG_KEYS)
        and all(risk_flags[flag] is False for flag in _RISK_FLAG_KEYS)
    )
    return "NON_MATERIAL" if is_non_material else "MATERIAL"


def is_high_risk(materiality: dict[str, object]) -> bool:
    risk_flags = materiality.get("risk_flags")
    return (
        materiality.get("reversibility") in {"COSTLY_TO_REVERSE", "IRREVERSIBLE"}
        or (
            isinstance(risk_flags, dict)
            and any(risk_flags.get(flag) is True for flag in _RISK_FLAG_KEYS)
        )
    )


def validate_materiality_classification(materiality: dict[str, object]) -> bool:
    return materiality.get("classification") == classify_materiality(materiality)
