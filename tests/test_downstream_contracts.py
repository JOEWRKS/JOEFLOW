import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.contracts import ContractError, compile_contract
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
                "product_slug": "test-product",
                "actions": [
                    {
                        "action_id": "approve",
                        "sources": [rule],
                        "command": "APPROVE",
                        "input_invariants": [],
                        "result_expectations": {},
                        "test_obligations": ["happy", "wrong_role"],
                    }
                ],
                "lifecycles": [
                    {
                        "lifecycle_id": "approval",
                        "sources": [lifecycle],
                        "superseded_sentinels": [superseded],
                    }
                ],
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
                            "product_slug": "test-product",
                            "actions": [{"action_id": "approve", "sources": [source]}],
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
                    "product_slug": "test-product",
                    "actions": [{"action_id": "approve", "sources": [mismatched]}],
                    "lifecycles": [],
                },
            )


if __name__ == "__main__":
    unittest.main()
