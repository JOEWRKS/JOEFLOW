"""Downstream 2.1 semantic responsibility and exact derivation core."""

from .audit import audit_action_contract_v21_against_state
from .compiler import compile_handoff_definition_v21, validate_verification_basis
from .contracts import (
    artifact_hash_v21,
    semantic_contract_hash_v21,
    semantic_contract_projection_v21,
    validate_action_contract_v21,
)
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
from .gaps import (
    CONTRACT_EXPRESSIVENESS_GAP,
    RUNTIME_MAPPING_GAP,
    SEMANTIC_AUTHORITY_GAP,
)
from .responsibility import (
    load_responsibility_profile_v21,
    responsibility_profile_digest_v21,
)


__all__ = [
    "ACTION_CONTRACT_VERSION",
    "CONTRACT_EXPRESSIVENESS_GAP",
    "ContractExpressivenessGap",
    "HANDOFF_DEFINITION_VERSION",
    "RESPONSIBILITY_PROFILE_ID",
    "RUNTIME_EVIDENCE_BUNDLE_VERSION",
    "RUNTIME_MAPPING_GAP",
    "RUNTIME_PLAN_VERSION",
    "RUNTIME_PROFILE_ID",
    "SEMANTIC_REVIEW_VERSION",
    "SEMANTIC_AUTHORITY_GAP",
    "SemanticAuthorityGap",
    "artifact_hash_v21",
    "audit_action_contract_v21_against_state",
    "compile_handoff_definition_v21",
    "derive_semantic_field_v21",
    "load_responsibility_profile_v21",
    "responsibility_profile_digest_v21",
    "semantic_contract_hash_v21",
    "semantic_contract_projection_v21",
    "validate_action_contract_v21",
    "validate_verification_basis",
]
