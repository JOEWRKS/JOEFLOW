import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.contracts import ContractError, compile_contract
from downstream.provenance import make_source_ref


FULL_VERSION = "joewrks.action-conformance/1.0"
SLICE_VERSION = "joewrks.downstream.regression-slice/1.0"
COMPONENTS = {
    "authoritative_state": "CHANGED",
    "revision": "CHANGED",
    "history": "CHANGED",
    "business_side_effects": "UNCHANGED",
    "delivery_effects": "UNCHANGED",
}


def authority_state():
    return {
        "schema_version": "0.1.2.1",
        "project": {
            "slug": "authority-test",
            "status": "CLOSED",
            "definition_revision": 3,
            "approval": {"approved_revision": 3, "approved_digest": "digest-3"},
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
                }
            ],
        },
    }


def review(value, source_refs=(0,), explanation="Canonical prose requires reviewer interpretation."):
    return {
        "value": value,
        "source_refs": list(source_refs),
        "derivation": {"kind": "REVIEW_REQUIRED", "explanation": explanation},
    }


def machine(value, source_refs=(0,), operator="exact", pointer=None):
    derivation = {"kind": "MACHINE_DERIVED", "operator": operator}
    if pointer is not None:
        derivation["pointer"] = pointer
    return {"value": value, "source_refs": list(source_refs), "derivation": derivation}


def current_rule(state):
    return make_source_ref(state, "RULE-001", "/objects/rules/0/text")


def slice_definition(state):
    return {
        "contract_schema_version": SLICE_VERSION,
        "product_slug": "authority-test",
        "actions": [
            {
                "action_id": "approve",
                "sources": [current_rule(state)],
                "default_result": review("SUCCESS"),
                "input_invariants": review([]),
                "result_expectations": review({"SUCCESS": copy.deepcopy(COMPONENTS)}),
                "test_obligations": review(["authority-hardening"]),
            }
        ],
        "lifecycles": [],
    }


class DownstreamAuthorityNegativeTest(unittest.TestCase):
    def test_full_contract_missing_required_semantic_field_fails(self):
        state = authority_state()
        definition = slice_definition(state)
        definition["contract_schema_version"] = FULL_VERSION
        with self.assertRaises(ContractError):
            compile_contract(state, definition)

    def test_machine_derived_fake_expectation_with_current_source_fails(self):
        state = authority_state()
        definition = slice_definition(state)
        definition["actions"][0]["result_expectations"] = machine(
            {"SUCCESS": copy.deepcopy(COMPONENTS)}
        )
        with self.assertRaises(ContractError):
            compile_contract(state, definition)

    def test_semantic_source_ref_out_of_range_fails(self):
        state = authority_state()
        definition = slice_definition(state)
        definition["actions"][0]["default_result"] = review("SUCCESS", source_refs=(1,))
        with self.assertRaises(ContractError):
            compile_contract(state, definition)

    def test_semantic_field_without_provenance_fails(self):
        state = authority_state()
        definition = slice_definition(state)
        definition["actions"][0]["default_result"] = review("SUCCESS", source_refs=())
        with self.assertRaises(ContractError):
            compile_contract(state, definition)

    def test_active_semantic_field_with_only_superseded_source_fails(self):
        state = authority_state()
        definition = slice_definition(state)
        definition["actions"][0]["sources"] = [
            make_source_ref(
                state,
                "RULE-002",
                "/objects/rules/1/text",
                active=False,
            )
        ]
        with self.assertRaisesRegex(
            ContractError,
            "active semantic field derives exclusively from SUPERSEDED authority",
        ):
            compile_contract(state, definition)

    def test_changed_extract_value_with_unchanged_canonical_hash_fails(self):
        state = authority_state()
        definition = slice_definition(state)
        definition["actions"][0]["sources"] = [
            make_source_ref(state, "STATE-001", "/objects/states/0")
        ]
        definition["actions"][0]["test_obligations"] = machine(
            ["OPEN"], operator="extract", pointer="/values"
        )
        with self.assertRaises(ContractError):
            compile_contract(state, definition)

    def test_regression_slice_cannot_claim_full_contract_version(self):
        state = authority_state()
        definition = slice_definition(state)
        definition["contract_schema_version"] = FULL_VERSION
        definition["fixture_purpose"] = "known-defect reproduction"
        with self.assertRaises(ContractError):
            compile_contract(state, definition)


if __name__ == "__main__":
    unittest.main()
