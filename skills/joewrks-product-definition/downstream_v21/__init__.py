"""Downstream 2.1 semantic responsibility and exact derivation core."""

from .derivation import (
    ContractExpressivenessGap,
    SemanticAuthorityGap,
    derive_semantic_field_v21,
)
from .identity import (
    ACTION_CONTRACT_VERSION,
    HANDOFF_DEFINITION_VERSION,
    RESPONSIBILITY_PROFILE_ID,
    RUNTIME_EVIDENCE_BUNDLE_VERSION,
    RUNTIME_PLAN_VERSION,
    RUNTIME_PROFILE_ID,
    SEMANTIC_REVIEW_VERSION,
)
from .responsibility import (
    load_responsibility_profile_v21,
    responsibility_profile_digest_v21,
)


__all__ = [
    "ACTION_CONTRACT_VERSION",
    "ContractExpressivenessGap",
    "HANDOFF_DEFINITION_VERSION",
    "RESPONSIBILITY_PROFILE_ID",
    "RUNTIME_EVIDENCE_BUNDLE_VERSION",
    "RUNTIME_PLAN_VERSION",
    "RUNTIME_PROFILE_ID",
    "SEMANTIC_REVIEW_VERSION",
    "SemanticAuthorityGap",
    "derive_semantic_field_v21",
    "load_responsibility_profile_v21",
    "responsibility_profile_digest_v21",
]
