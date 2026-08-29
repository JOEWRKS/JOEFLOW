import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from approval_v2 import (  # noqa: E402
    approval_manifest_digest,
    compute_approval_manifest,
    definition_digest,
    validate_approval,
)
from authority_binding_v2 import sha256_json  # noqa: E402
from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402
from tests.v020_support import materiality  # noqa: E402


CORE_AXES = (
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state",
    "data", "side_effect", "notification", "validation", "boundary",
    "persistence", "security", "privacy", "analytics", "acceptance",
)
UX_STATE_AXES = (
    "default", "loading", "empty", "partial", "success", "error", "disabled",
    "permission_denied", "unauthenticated", "offline", "timeout", "retrying",
    "submitting", "completed", "cancelled", "expired",
)
UX_ACTION_AXES = (
    "entry", "precondition", "input", "validation", "submit", "success", "failure",
    "retry", "cancel", "back", "refresh", "duplicate_concurrent_action", "timeout",
    "offline", "permission", "session_expiration", "data_mutation", "side_effect",
    "notification", "persistence", "undo", "destructive_confirmation",
)
AUTH_AXES = (
    "registration", "verification", "login", "logout", "session_expiry",
    "session_renewal", "password_reset", "account_recovery", "revocation",
    "role_change", "provider_failure", "duplicate_identity", "account_linking",
)

PACKS = {
    "GRILL-AUTH-1": {
        "pack_id": "GRILL-AUTH-1", "version": "1.0",
        "digest": "e938ee7a52a4039d1b636f9dbd113a46bb9a94a616b890687b3c1b30554cb4f6",
        "target_refs": ["SURF-001"],
    },
    "GRILL-CORE-1": {
        "pack_id": "GRILL-CORE-1", "version": "1.0",
        "digest": "45b87b1d77916ae5a6e0d624b3a8452f787a7754daf18635157157c4497b951e",
        "target_refs": ["REQ-001"],
    },
}


def binding(record_id, pointer, value):
    """Literal record/pointer/value proof; it never resolves through production code."""
    return {
        "record_id": record_id,
        "pointer": pointer,
        "value_sha256": sha256_json(value),
    }


def covered(record_id, pointer, value):
    return {
        "status": "COVERED",
        "authority_bindings": [binding(record_id, pointer, value)],
        "unknown_refs": [], "basis_bindings": [], "rationale": None,
    }


def na_cell():
    return {
        "status": "N/A", "authority_bindings": [], "unknown_refs": [],
        "basis_bindings": [binding(
            "EVD-900", "/claim",
            "The specialist topology and non-applicable axes were explicitly classified.",
        )],
        "rationale": "The user-confirmed product topology makes this axis inapplicable.",
    }


def _profile_cell(status):
    if status == "ACTIVE":
        return {
            "status": "ACTIVE", "surface_refs": ["SURF-001"],
            "unknown_refs": [], "basis_refs": [], "rationale": None,
        }
    return {
        "status": "N/A", "surface_refs": [], "unknown_refs": [],
        "basis_refs": ["EVD-900"],
        "rationale": "The user confirmed this topology is not applicable.",
    }


def literal_ready_state():
    """One independently specified M4-semantic state before user approval."""
    mat = materiality(classification="MATERIAL")
    non_mat = materiality(classification="NON_MATERIAL")
    evidence = [{
        "id": "EVD-900", "status": "CURRENT",
        "source_kind": "USER_CONFIRMED_INTENT",
        "locator": "product-definition/topology-classification",
        "claim": "The specialist topology and non-applicable axes were explicitly classified.",
        "confidence": "DIRECT", "authority_classes": ["INTENT"],
        "observed_version": None, "content_hash": None,
    }]
    surface = {
        "id": "SURF-001", "kind": "FEATURE_AREA", "name": "Request submission",
        "status": "IN_SCOPE", "materiality": copy.deepcopy(mat),
        "evidence_refs": [], "authority_refs": ["REQ-001"], "unknown_refs": [],
        "decision_refs": [], "contradiction_refs": [], "rationale": None,
        "intent_classification": None,
    }
    state = {
        "schema_version": "0.2.0",
        "project": {
            "slug": "semantic-closure-v2", "definition_status": "READY_FOR_REVIEW",
            "definition_revision": 1, "bootstrap_mode": "NEW_PRODUCT",
            "closure_contract": {
                "level": "SEMANTIC_CLOSURE",
                "product_binding_contract": {
                    "contract_id": "joewrks.product-coverage-binding", "version": "1.0",
                    "digest": "b57459533247de52038aacb158e785c2184edcdd2fa6831f0edc3db713775f3c",
                },
                "ux_binding_contract": {
                    "contract_id": "joewrks.ux-coverage-binding", "version": "1.0",
                    "digest": "8fc84057a4a6f0f0ce329a58d11b8e208989800147d703665cea52088de0be0d",
                },
            },
        },
        "migration": {"mode": "NATIVE"},
        "evidence": evidence,
        "surface_manifest": {
            "records": [surface],
            "grill_profile": {
                "AUTH": _profile_cell("ACTIVE"),
                "MONEY": _profile_cell("N/A"),
                "FILE_UPLOAD": _profile_cell("N/A"),
                "ASYNC": _profile_cell("N/A"),
                "PERMISSION": _profile_cell("N/A"),
                "DESTRUCTIVE_ACTION": _profile_cell("N/A"),
            },
        },
        "contradictions": [],
        "objects": {
            "goals": [{
                "id": "GOAL-001", "status": "CURRENT",
                "statement": "A requester completes a valid submission.",
            }],
            "users": [{
                "id": "USR-001", "status": "CURRENT",
                "description": "A signed-in requester.", "actor_kind": "REQUESTER",
            }],
            "requirements": [{
                "id": "REQ-001", "status": "CURRENT",
                "statement": "A requester can submit a valid request.",
                "scope": "The primary request workflow.", "ui_required": True,
                "materiality": copy.deepcopy(mat),
            }],
            "unknowns": [{
                "id": "UNK-001", "status": "RESOLVED",
                "question": "Which submission policy should control?",
                "why_it_matters": "The answer changes visible request behavior.",
                "required_authority_class": "INTENT", "question_category": "CORE_FLOW",
                "materiality": copy.deepcopy(mat),
                "decision_authority": "USER_DECISION_REQUIRED",
                "affects": ["RULE-001"], "blocks_unknown_refs": [],
                "origin": {"kind": "MANUAL", "surface_ref": None, "pack_id": None, "axis_id": None, "source_path": None},
                "response_mode": "MUTUALLY_EXCLUSIVE",
                "options": [
                    {"id": "OPT-A", "statement": "Use validated submission.", "consequences": ["Invalid requests are rejected."]},
                    {"id": "OPT-B", "statement": "Allow any submission.", "consequences": ["Invalid requests may enter the system."]},
                ],
                "recommendation": None, "evidence_refs": [], "resolved_by": ["DEC-001"],
                "resolution_mode": "USER_DECISION",
                "resolution_summary": "The user selected validated submission.",
                "deferral": None, "blocked_reason": None,
            }],
            "decisions": [{
                "id": "DEC-001", "status": "CURRENT",
                "statement": "Validate the request before submission.",
                "decision_type": "PRODUCT_POLICY", "resolution_mode": "USER_DECISION",
                "decision_authority": "USER_DECISION_REQUIRED",
                "source_unknown_refs": ["UNK-001"], "evidence_refs": [],
                "materiality": copy.deepcopy(mat), "affects": ["RULE-001"],
                "decided_by": "USER", "accepted_recommendation": None,
            }],
            "rules": [{
                "id": "RULE-001", "status": "CURRENT",
                "statement": "Only valid requests may be submitted.",
                "applies_to": ["REQ-001"],
            }],
            "flows": [{
                "id": "FLOW-001", "status": "CURRENT", "goal_refs": ["GOAL-001"],
                "entry": "Open the request form.", "preconditions": ["The requester is signed in."],
                "paths": ["Validate and submit."], "outcomes": ["The request is accepted."],
            }],
            "screens": [{
                "id": "SCR-001", "status": "CURRENT", "purpose": "Submit a request.",
                "requirement_refs": ["REQ-001"], "interaction_mode": "INTERACTIVE",
                "major_actions": ["submit"],
            }],
            "states": [{
                "id": "STATE-001", "status": "CURRENT", "owner_refs": ["SCR-001"],
                "state_name": "REQUEST_READY", "conditions": ["Required input is valid."],
            }],
            "data": [{
                "id": "DATA-001", "status": "CURRENT", "name": "Request",
                "purpose": "Carry request input.", "ownership": "REQUESTER",
            }],
            "integrations": [{
                "id": "INT-001", "status": "CURRENT", "name": "Request API",
                "purpose": "Persist accepted requests.",
            }],
            "acceptance_criteria": [{
                "id": "AC-001", "status": "CURRENT", "requirement_refs": ["REQ-001"],
                "assertion": "A valid request is accepted and persisted.",
            }],
            "tasks": [{
                "id": "TASK-001", "status": "CURRENT", "implements": ["REQ-001"],
                "acceptance_refs": ["AC-001"],
            }],
        },
        "coverage": [], "ux_coverage": [], "grill_coverage": [],
        "discovery_baseline": {},
        "approval": {"status": "UNAPPROVED"}, "approval_history": [],
    }

    core_sources = {
        "actor": ("USR-001", "/description", "A signed-in requester."),
        "goal": ("GOAL-001", "/statement", "A requester completes a valid submission."),
        "entry_point": ("FLOW-001", "/entry", "Open the request form."),
        "precondition": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "happy_path": ("REQ-001", "/statement", "A requester can submit a valid request."),
        "alternative_path": ("FLOW-001", "/paths", ["Validate and submit."]),
        "error": ("STATE-001", "/conditions", ["Required input is valid."]),
        "recovery": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "permission": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "state": ("STATE-001", "/state_name", "REQUEST_READY"),
        "data": ("DATA-001", "/name", "Request"),
        "side_effect": ("INT-001", "/purpose", "Persist accepted requests."),
        "notification": ("FLOW-001", "/outcomes", ["The request is accepted."]),
        "validation": ("AC-001", "/assertion", "A valid request is accepted and persisted."),
        "boundary": ("DEC-001", "/statement", "Validate the request before submission."),
        "persistence": ("DATA-001", "/purpose", "Carry request input."),
        "security": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "privacy": ("DATA-001", "/ownership", "REQUESTER"),
        "analytics": ("INT-001", "/name", "Request API"),
        "acceptance": ("AC-001", "/assertion", "A valid request is accepted and persisted."),
    }
    state["coverage"] = [{
        "feature_id": "REQ-001",
        "cells": {axis: covered(*core_sources[axis]) for axis in CORE_AXES},
    }]

    state_sources = {
        "default": ("SCR-001", "/purpose", "Submit a request."),
        "loading": ("FLOW-001", "/entry", "Open the request form."),
        "empty": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "partial": ("STATE-001", "/conditions", ["Required input is valid."]),
        "success": ("AC-001", "/assertion", "A valid request is accepted and persisted."),
        "error": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "disabled": ("STATE-001", "/state_name", "REQUEST_READY"),
        "permission_denied": ("DEC-001", "/statement", "Validate the request before submission."),
        "unauthenticated": ("FLOW-001", "/preconditions", ["The requester is signed in."]),
        "offline": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "timeout": ("STATE-001", "/conditions", ["Required input is valid."]),
        "retrying": ("FLOW-001", "/paths", ["Validate and submit."]),
        "submitting": ("FLOW-001", "/entry", "Open the request form."),
        "completed": ("AC-001", "/assertion", "A valid request is accepted and persisted."),
        "cancelled": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "expired": ("STATE-001", "/state_name", "REQUEST_READY"),
    }
    action_sources = {
        "entry": ("SCR-001", "/purpose", "Submit a request."),
        "precondition": ("FLOW-001", "/preconditions", ["The requester is signed in."]),
        "input": ("DATA-001", "/name", "Request"),
        "validation": ("AC-001", "/assertion", "A valid request is accepted and persisted."),
        "submit": ("FLOW-001", "/paths", ["Validate and submit."]),
        "success": ("AC-001", "/assertion", "A valid request is accepted and persisted."),
        "failure": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "retry": ("FLOW-001", "/paths", ["Validate and submit."]),
        "cancel": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "back": ("SCR-001", "/purpose", "Submit a request."),
        "refresh": ("FLOW-001", "/entry", "Open the request form."),
        "duplicate_concurrent_action": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "timeout": ("STATE-001", "/conditions", ["Required input is valid."]),
        "offline": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "permission": ("DEC-001", "/statement", "Validate the request before submission."),
        "session_expiration": ("FLOW-001", "/preconditions", ["The requester is signed in."]),
        "data_mutation": ("DATA-001", "/purpose", "Carry request input."),
        "side_effect": ("INT-001", "/purpose", "Persist accepted requests."),
        "notification": ("FLOW-001", "/outcomes", ["The request is accepted."]),
        "persistence": ("DATA-001", "/ownership", "REQUESTER"),
        "undo": ("RULE-001", "/statement", "Only valid requests may be submitted."),
        "destructive_confirmation": ("DEC-001", "/statement", "Validate the request before submission."),
    }
    state["ux_coverage"] = [{
        "screen_id": "SCR-001",
        "states": {axis: covered(*state_sources[axis]) for axis in UX_STATE_AXES},
        "actions": [{
            "key": "submit",
            "cells": {axis: covered(*action_sources[axis]) for axis in UX_ACTION_AXES},
        }],
    }]

    axes = {axis: na_cell() for axis in AUTH_AXES}
    axes["registration"] = {
        "status": "ADDRESSED",
        "authority_bindings": [binding(
            "RULE-001", "/statement", "Only valid requests may be submitted.",
        )],
        "unknown_refs": [], "basis_bindings": [], "rationale": None,
    }
    state["grill_coverage"] = [{
        "target_ref": "SURF-001", "pack_id": "GRILL-AUTH-1", "pack_version": "1.0",
        "pack_digest": PACKS["GRILL-AUTH-1"]["digest"], "axes": axes,
    }]

    state["discovery_baseline"] = {
        "status": "CURRENT", "definition_revision": 1,
        "surface_manifest_digest": sha256_json([surface]),
        "evidence_commitment_digest": sha256_json(evidence),
        "open_material_surface_count": 0,
        "unresolved_material_contradiction_count": 0,
        "procedure_complete": True, "applicable_surface_classes_complete": True,
        "active_grill_packs": [copy.deepcopy(PACKS[key]) for key in sorted(PACKS)],
        "active_grill_packs_complete": True,
        "unknown_unknown_exhaustiveness_claimed": False,
    }
    return state


# Frozen after independently specifying the READY state above. No production approval
# builder is called by the fixture. These constants are replaced only when semantics change.
LITERAL_APPROVAL = {
    "definition_digest": "dd1a16a678b431fc971d65e61eef77b68edef26c33b8d5891f3f9b5f888d8876",
    "manifest_digest": "6d42f238fbc862d2a566f8d3dab00432698b24b5d27db77ee54d6d233a5b2f5b",
    "record_hashes": {
        "AC-001": "6069e0f4208eb32433664c1414c3b226b9681fc9c3f2a47910be624dd4e227e4",
        "DATA-001": "afeb0f9a9e6e4dc51dba97efb88343b87b3a0996d73b6c31c3e568d391142844",
        "DEC-001": "880a8490bb39e7057f92cbfc601c280173ccc994bcf5fa6749a831b8cef18cc3",
        "EVD-900": "73fc5e74def3851e019e9527d778db033c5c1dd9f42f051fad6deb5842fe50ff",
        "FLOW-001": "64bc5bca6ffad05a166424e13461075824cbf66bd5135fb91bb16bd410f06314",
        "GOAL-001": "fe8efd106398ec95401f2a09621d61a6f891e72b58ada1015bdfc30836a4ac31",
        "INT-001": "d804d22e81148f55d0628efba8c782f0c9585216f6bc81771c50572937712509",
        "REQ-001": "29a3426a16f80c29aada6bca97956bbc90a46f9bbf29fadf6bc800dde8aeb355",
        "RULE-001": "c86964e89db53c8003787aaefa96dfd3f4a884507b5b581b84a5411d1c354ef7",
        "SCR-001": "ac6b53c60da38d8b1987012882bd16cebb50fd6d9557ea16b4e52ed5c7ee74d5",
        "STATE-001": "d1b4213d6185e631f6706023d75662b2b5c70e21dfedc63e6ab8d1799edd3999",
        "SURF-001": "07a87beeca7cc899c4efc3c74784b987445c5d58a67842832ee3b4fc60dc2ba7",
        "TASK-001": "1132f754b922908a81cdfb1fe0763b69b177a769301a77d80b9ba5aec523ddde",
        "UNK-001": "77eac108d178d2d2e29f264db4e5595510947d8eb86dafdc6082fe034fed7157",
        "USR-001": "b2510c2d3505f4de498193ffbdaf8882cf26235775e2ae6c46ecf985a36b8736",
    },
    "coverage_digest": "2d54e7889a2516ffe86c578b8f13ebbfbc310f8c9d882d5c6ef85f2ae3d0c365",
    "surface_digest": "1d2b55b30d985ea522c20b4bc1caebd117dc5bf7f2b0990038889aa429c13b5f",
    "grill_pack_set_digest": "d7f7e64053201db988d1376aa0ab8f07c5c27fb3cfee89a7d0210fcba86f17cf",
}


def literal_approved_state():
    state = literal_ready_state()
    commitment = {
        "revision": 1,
        "definition_digest": LITERAL_APPROVAL["definition_digest"],
        "manifest_digest": LITERAL_APPROVAL["manifest_digest"],
        "record_hashes": copy.deepcopy(LITERAL_APPROVAL["record_hashes"]),
        "coverage_digest": LITERAL_APPROVAL["coverage_digest"],
        "surface_digest": LITERAL_APPROVAL["surface_digest"],
        "grill_pack_set_digest": LITERAL_APPROVAL["grill_pack_set_digest"],
    }
    state["approval_history"] = [commitment]
    state["approval"] = {
        "status": "APPROVED", "approved_revision": 1,
        "approved_definition_digest": LITERAL_APPROVAL["definition_digest"],
        "approved_manifest_digest": LITERAL_APPROVAL["manifest_digest"],
        "approved_at": "2026-08-29T00:00:00Z", "approved_by": "user",
    }
    state["project"]["definition_status"] = "CLOSED"
    return state


def error_codes(result):
    return {error["code"] for error in result["errors"]}


class SemanticClosureV020Test(unittest.TestCase):
    def assert_blocked(self, state, *, metric=None, code=None):
        result = evaluate_closure_v2(state)
        self.assertFalse(result["closed"])
        if metric is not None:
            self.assertGreater(result["metrics"].get(metric, 0), 0)
        if code is not None:
            self.assertIn(code, error_codes(result))
        return result

    def test_literal_complete_definition_closes_only_after_exact_user_approval(self):
        # Break caught: M3's hard guard never allowing a complete approved state to close.
        ready = literal_ready_state()
        self.assertEqual(validate_state_v2(ready), [])
        ready_result = evaluate_closure_v2(ready)
        self.assertFalse(ready_result["closed"])
        self.assertEqual(ready_result["definition_digest"], LITERAL_APPROVAL["definition_digest"])

        approved = literal_approved_state()
        self.assertEqual(validate_state_v2(approved), [])
        result = evaluate_closure_v2(approved)
        self.assertTrue(result["closed"])
        self.assertEqual(result["definition_digest"], LITERAL_APPROVAL["definition_digest"])
        self.assertNotIn("semantic_closure_not_implemented", result["metrics"])

    def test_exact_core_open_and_na_proof_failures_block_closure(self):
        # Break caught: Core proof hash/type/OPEN/N/A defects being treated as checkbox coverage.
        hash_drift = literal_approved_state()
        hash_drift["coverage"][0]["cells"]["actor"]["authority_bindings"][0]["value_sha256"] = "0" * 64
        self.assert_blocked(hash_drift, metric="invalid_authority_binding", code="authority_binding_hash_mismatch")

        wrong_type = literal_approved_state()
        wrong_type["coverage"][0]["cells"]["actor"]["authority_bindings"] = [binding("DATA-001", "/name", "Request")]
        self.assert_blocked(wrong_type, metric="invalid_coverage_authority_type", code="invalid_authority_binding_type")

        open_without_unknown = literal_approved_state()
        open_without_unknown["coverage"][0]["cells"]["actor"] = {
            "status": "OPEN", "authority_bindings": [], "unknown_refs": [],
            "basis_bindings": [], "rationale": None,
        }
        self.assert_blocked(open_without_unknown, metric="open_coverage_without_unknown")

        na_without_basis = literal_approved_state()
        na_without_basis["grill_coverage"][0]["axes"]["verification"]["basis_bindings"] = []
        self.assert_blocked(na_without_basis, metric="unjustified_na_without_basis")

    def test_ux_and_specialist_exact_binding_failures_block_closure(self):
        # Break caught: stale UX or specialist proof still satisfying semantic coverage.
        ux_state = literal_approved_state()
        ux_state["ux_coverage"][0]["states"]["default"]["authority_bindings"][0]["value_sha256"] = "1" * 64
        self.assert_blocked(ux_state, metric="ux_invalid_authority_binding")

        ux_action = literal_approved_state()
        ux_action["ux_coverage"][0]["actions"][0]["cells"]["submit"]["authority_bindings"][0]["value_sha256"] = "2" * 64
        self.assert_blocked(ux_action, metric="ux_invalid_authority_binding")

        specialist = literal_approved_state()
        specialist["grill_coverage"][0]["axes"]["registration"]["authority_bindings"][0]["value_sha256"] = "3" * 64
        self.assert_blocked(specialist, metric="specialist_binding_gaps")

    def test_material_discovery_consumption_and_delivery_failures_block_closure(self):
        # Break caught: unresolved meaning, stale discovery, or undelivered material authority closing.
        material_unknown = literal_approved_state()
        unknown = material_unknown["objects"]["unknowns"][0]
        unknown.update({
            "status": "OPEN", "resolved_by": [], "resolution_mode": None,
            "resolution_summary": None,
        })
        self.assert_blocked(material_unknown, metric="open_material_unknowns")

        contradiction = literal_approved_state()
        contradiction["contradictions"] = [{
            "id": "CON-001", "status": "OPEN", "claim_a_refs": ["EVD-900"],
            "claim_b_refs": ["EVD-900"], "scope_refs": ["SURF-001"],
            "materiality": materiality(classification="MATERIAL"),
            "resolution": None, "resolved_by": [], "selected_authority_refs": [],
        }]
        self.assert_blocked(contradiction, metric="unresolved_material_contradictions")

        baseline = literal_approved_state()
        baseline["discovery_baseline"]["surface_manifest_digest"] = "4" * 64
        self.assert_blocked(baseline, metric="discovery_baseline_gaps", code="stale_discovery_baseline")

        pack = literal_approved_state()
        pack["grill_coverage"][0]["pack_digest"] = "5" * 64
        self.assert_blocked(pack, metric="active_grill_pack_gaps", code="grill_pack_identity_mismatch")

        decision = literal_approved_state()
        decision["objects"]["decisions"][0]["affects"] = []
        decision["coverage"][0]["cells"]["boundary"] = covered(
            "RULE-001", "/statement", "Only valid requests may be submitted.",
        )
        decision["ux_coverage"][0]["states"]["permission_denied"] = covered(
            "RULE-001", "/statement", "Only valid requests may be submitted.",
        )
        for axis in ("permission", "destructive_confirmation"):
            decision["ux_coverage"][0]["actions"][0]["cells"][axis] = covered(
                "RULE-001", "/statement", "Only valid requests may be submitted.",
            )
        self.assert_blocked(decision, metric="unconsumed_material_decision")

        delivery = literal_approved_state()
        delivery["objects"]["tasks"] = []
        self.assert_blocked(delivery, metric="task_mapping_gaps")

    def test_every_approval_commitment_dimension_and_status_is_exact(self):
        # Break caught: any revision/digest/history/status mismatch being accepted as approval.
        definition = literal_approved_state()
        definition["approval"]["approved_definition_digest"] = "6" * 64
        self.assert_blocked(definition, metric="stale_approval", code="stale_approval")

        manifest = literal_approved_state()
        manifest["approval"]["approved_manifest_digest"] = "7" * 64
        self.assert_blocked(manifest, metric="missing_or_stale_approval_manifest", code="missing_or_stale_approval_manifest")

        revision = literal_approved_state()
        revision["approval"]["approved_revision"] = 2
        self.assert_blocked(revision, metric="stale_approval", code="stale_approval")

        history = literal_approved_state()
        history["approval_history"][0]["coverage_digest"] = "8" * 64
        self.assert_blocked(history, metric="approval_history_gaps", code="semantic_change_without_revision_increment")

        status = literal_approved_state()
        status["project"]["definition_status"] = "READY_FOR_REVIEW"
        self.assert_blocked(status, code="invalid_approval_status")

    def test_minimum_definition_and_procedure_are_explicit_blockers(self):
        # Break caught: empty authority or incomplete discovery procedure receiving Semantic Closure.
        no_goal = literal_approved_state()
        no_goal["objects"]["goals"] = []
        self.assert_blocked(no_goal, metric="minimum_definition_gaps")

        no_surface = literal_approved_state()
        no_surface["surface_manifest"]["records"] = []
        self.assert_blocked(no_surface, metric="minimum_definition_gaps")

        no_required_screen = literal_approved_state()
        no_required_screen["objects"]["screens"] = []
        no_required_screen["objects"]["states"][0]["owner_refs"] = []
        no_required_screen["ux_coverage"] = []
        self.assert_blocked(no_required_screen, metric="minimum_definition_gaps")

        incomplete = literal_approved_state()
        incomplete["discovery_baseline"]["procedure_complete"] = False
        self.assert_blocked(incomplete, metric="discovery_procedure_gaps")

    def test_unconsumed_evidence_stays_outside_approval_until_semantically_consumed(self):
        # Break caught: observational evidence churn invalidating approval, or consumed evidence failing to do so.
        original = literal_approved_state()
        original_definition = definition_digest(original)
        original_manifest = approval_manifest_digest(compute_approval_manifest(original))

        with_unconsumed = copy.deepcopy(original)
        with_unconsumed["evidence"].append({
            "id": "EVD-901", "status": "CURRENT", "source_kind": "OBSERVED_RUNTIME",
            "locator": "runtime/request-probe", "claim": "The request endpoint returned 200.",
            "confidence": "DIRECT", "authority_classes": ["FACTUAL", "BEHAVIORAL"],
            "observed_version": "probe-1", "content_hash": "9" * 64,
        })
        self.assertIn("stale_discovery_baseline", {error["code"] for error in validate_state_v2(with_unconsumed)})

        with_unconsumed["discovery_baseline"]["evidence_commitment_digest"] = sha256_json(with_unconsumed["evidence"])
        self.assertEqual(validate_state_v2(with_unconsumed), [])
        result = evaluate_closure_v2(with_unconsumed)
        self.assertTrue(result["closed"])
        self.assertEqual(definition_digest(with_unconsumed), original_definition)
        self.assertEqual(approval_manifest_digest(compute_approval_manifest(with_unconsumed)), original_manifest)
        self.assertEqual(validate_approval(with_unconsumed), [])

        consumed = copy.deepcopy(with_unconsumed)
        consumed["objects"]["decisions"][0]["evidence_refs"] = ["EVD-901"]
        self.assertNotEqual(definition_digest(consumed), original_definition)
        consumed_result = evaluate_closure_v2(consumed)
        self.assertFalse(consumed_result["closed"])
        self.assertGreater(consumed_result["metrics"]["stale_approval"], 0)


if __name__ == "__main__":
    unittest.main()
