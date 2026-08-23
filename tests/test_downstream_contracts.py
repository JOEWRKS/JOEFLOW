import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.contracts import (
    ContractError,
    FULL_CONTRACT_VERSION,
    REGRESSION_SLICE_VERSION,
    compile_contract,
)
from downstream.provenance import make_source_ref, resolve_pointer, sha256_json


def authority_state():
    return {
        "schema_version": "0.1.2.1",
        "project": {
            "slug": "test-product",
            "status": "CLOSED",
            "definition_revision": 7,
            "approval": {
                "approved_revision": 7,
                "approved_digest": "abc123",
            },
        },
        "objects": {
            "rules": [
                {"id": "RULE-001", "status": "CURRENT", "text": "Only owners may approve."},
                {
                    "id": "RULE-002",
                    "status": "SUPERSEDED",
                    "text": "Any member may approve.",
                    "superseded_by": "RULE-001",
                },
            ],
            "states": [
                {
                    "id": "STATE-001",
                    "status": "CURRENT",
                    "values": ["OPEN", "APPROVED"],
                    "transitions": [{"from": "OPEN", "to": "APPROVED", "actor": "owner"}],
                }
            ],
        },
    }


def review(value):
    return {
        "value": value,
        "source_refs": [0],
        "derivation": {
            "kind": "REVIEW_REQUIRED",
            "explanation": "The unit fixture requires reviewed semantic interpretation.",
        },
    }


def no_op_expectation():
    return {
        "authoritative_state": "UNCHANGED",
        "revision": "UNCHANGED",
        "history": "UNCHANGED",
        "business_side_effects": "UNCHANGED",
        "delivery_effects": "UNCHANGED",
    }


def slice_action(source):
    return {
        "action_id": "approve",
        "sources": [source],
        "default_result": review("REJECTED"),
        "input_invariants": review([]),
        "result_expectations": review({"REJECTED": no_op_expectation()}),
        "test_obligations": review(["authority-unit"]),
    }


def full_action(source):
    action = {
        "action_id": "approve",
        "sources": [source],
        "actor": review("owner"),
        "authentication": review("authenticated owner"),
        "relationship_predicate": review("owns target"),
        "object_binding": review("target ID"),
        "concurrency": review("expected revision"),
        "preconditions": review(["OPEN"]),
        "allowed_current_states": review(["OPEN"]),
        "forbidden_states": review(["APPROVED"]),
        "input_invariants": review([]),
        "command": review("APPROVE"),
        "expected_domain_mutation": review("OPEN -> APPROVED"),
        "forbidden_mutations": review([]),
        "default_result": review("SUCCESS"),
        "result_expectations": review(
            {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                }
            }
        ),
        "version_result": review("advance"),
        "history_result": review("append"),
        "business_side_effects": review("none"),
        "delivery_effects": review("none"),
        "idempotency": review("replay"),
        "rejection": review("no-op"),
        "recovery": review("read latest"),
        "visible_success": review("approved"),
        "visible_error": review("conflict"),
        "superseded_rules": review("inactive"),
        "test_obligations": review(["happy", "wrong_role"]),
        "trace": review(["control", "handler", "state"]),
    }
    return action


def full_lifecycle(source, superseded):
    return {
        "lifecycle_id": "approval",
        "sources": [source],
        "current_states": review(["OPEN", "APPROVED"]),
        "allowed_transitions": review(["OPEN -> APPROVED"]),
        "forbidden_transitions": review(["APPROVED -> OPEN"]),
        "boundary_conditions": review(["expected revision"]),
        "reversibility": review("terminal"),
        "reversal_window": review("none"),
        "object_outcome": review("approved"),
        "required_reason": review("none"),
        "required_confirmation": review("required"),
        "required_evidence": review("readback"),
        "authority": review("owner"),
        "history_preservation": review("append-only"),
        "superseded_sentinels": [superseded],
    }


class ProvenanceTest(unittest.TestCase):
    def test_json_pointer_and_hash_are_exact_and_deterministic(self):
        state = authority_state()
        pointer = "/objects/rules/0/text"
        self.assertEqual("Only owners may approve.", resolve_pointer(state, pointer))
        self.assertEqual(sha256_json("Only owners may approve."), sha256_json(resolve_pointer(state, pointer)))
        self.assertEqual(
            sha256_json({"b": 2, "a": 1}),
            sha256_json({"a": 1, "b": 2}),
        )

    def test_compiler_pins_approved_authority_and_current_sources(self):
        state = authority_state()
        rule = make_source_ref(state, "RULE-001", "/objects/rules/0/text")
        lifecycle = make_source_ref(state, "STATE-001", "/objects/states/0/transitions")
        superseded = make_source_ref(
            state,
            "RULE-002",
            "/objects/rules/1/text",
            active=False,
        )
        bundle = compile_contract(
            state,
            {
                "contract_schema_version": FULL_CONTRACT_VERSION,
                "product_slug": "test-product",
                "actions": [full_action(rule)],
                "lifecycles": [full_lifecycle(lifecycle, superseded)],
            },
        )
        self.assertEqual(7, bundle["source_authority"]["approved_revision"])
        self.assertEqual("abc123", bundle["source_authority"]["approved_digest"])
        self.assertEqual("CURRENT", bundle["actions"][0]["sources"][0]["source_status"])
        self.assertEqual("SUPERSEDED", bundle["lifecycles"][0]["superseded_sentinels"][0]["source_status"])
        self.assertEqual(64, len(bundle["contract_hash"]))

    def test_compiler_rejects_hash_drift_and_active_superseded_source(self):
        state = authority_state()
        current = make_source_ref(state, "RULE-001", "/objects/rules/0/text")
        drifted = copy.deepcopy(current)
        drifted["value_sha256"] = "0" * 64
        superseded = make_source_ref(state, "RULE-002", "/objects/rules/1/text", active=False)
        superseded["active"] = True

        for source in (drifted, superseded):
            with self.subTest(source=source["object_id"]):
                with self.assertRaises(ContractError):
                    compile_contract(
                        state,
                        {
                            "contract_schema_version": REGRESSION_SLICE_VERSION,
                            "product_slug": "test-product",
                            "actions": [slice_action(source)],
                            "lifecycles": [],
                        },
                    )

    def test_compiler_rejects_pointer_outside_declared_object(self):
        state = authority_state()
        mismatched = {
            "object_id": "RULE-001",
            "pointer": "/objects/states/0/values",
            "value_sha256": sha256_json(["OPEN", "APPROVED"]),
            "active": True,
        }
        with self.assertRaises(ContractError):
            compile_contract(
                state,
                {
                    "contract_schema_version": REGRESSION_SLICE_VERSION,
                    "product_slug": "test-product",
                    "actions": [slice_action(mismatched)],
                    "lifecycles": [],
                },
            )


if __name__ == "__main__":
    unittest.main()
