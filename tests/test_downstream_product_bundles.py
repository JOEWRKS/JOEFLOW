import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
DOWNSTREAM = SKILL_ROOT / "downstream"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.contracts import (
    ContractError,
    FULL_CONTRACT_VERSION,
    REGRESSION_SLICE_VERSION,
    compile_contract,
    is_full_handoff_contract,
    materialize_definition,
    semantic_value,
)


ACTION_FIELDS = {
    "action_id",
    "sources",
    "actor",
    "authentication",
    "relationship_predicate",
    "object_binding",
    "concurrency",
    "preconditions",
    "allowed_current_states",
    "forbidden_states",
    "input_invariants",
    "command",
    "expected_domain_mutation",
    "forbidden_mutations",
    "default_result",
    "result_expectations",
    "version_result",
    "history_result",
    "business_side_effects",
    "delivery_effects",
    "idempotency",
    "rejection",
    "recovery",
    "visible_success",
    "visible_error",
    "superseded_rules",
    "test_obligations",
    "trace",
}


class ProductBundleTest(unittest.TestCase):
    def test_contract_schemas_are_machine_readable_and_require_material_fields(self):
        action_schema = json.loads((DOWNSTREAM / "schemas" / "action-contract.schema.json").read_text(encoding="utf-8"))
        lifecycle_schema = json.loads((DOWNSTREAM / "schemas" / "lifecycle-contract.schema.json").read_text(encoding="utf-8"))
        execution_schema = json.loads((DOWNSTREAM / "schemas" / "execution-record.schema.json").read_text(encoding="utf-8"))
        regression_schema = json.loads((DOWNSTREAM / "schemas" / "regression-slice.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(ACTION_FIELDS, set(action_schema["$defs"]["action"]["required"]))
        self.assertIn("superseded_sentinels", lifecycle_schema["$defs"]["lifecycle"]["required"])
        self.assertEqual(FULL_CONTRACT_VERSION, action_schema["properties"]["contract_schema_version"]["const"])
        self.assertEqual(REGRESSION_SLICE_VERSION, regression_schema["properties"]["contract_schema_version"]["const"])
        for field_name in ACTION_FIELDS - {"action_id", "sources"}:
            self.assertEqual(
                "#/$defs/semanticField",
                action_schema["$defs"]["action"]["properties"][field_name]["$ref"],
            )
        self.assertEqual("joewrks.downstream.execution/1.0", execution_schema["properties"]["protocol_version"]["const"])
        for phase in ("before", "after"):
            required = set(execution_schema["properties"][phase]["required"])
            self.assertTrue({"authoritative_state", "revision", "history", "business_side_effects", "delivery_effects"} <= required)

    def test_materialization_adds_exact_hashes_to_every_source(self):
        state = {
            "project": {
                "slug": "sample",
                "status": "CLOSED",
                "definition_revision": 1,
                "approval": {"approved_revision": 1, "approved_digest": "digest"},
            },
            "objects": {
                "rules": [{"id": "RULE-001", "status": "CURRENT", "statement": "must"}],
                "states": [
                    {"id": "STATE-001", "status": "CURRENT", "values": ["A", "B"]},
                    {
                        "id": "STATE-000",
                        "status": "SUPERSEDED",
                        "values": ["OLD"],
                        "superseded_by": "STATE-001",
                    },
                ],
            },
        }
        blueprint = {
            "product_slug": "sample",
            "actions": [{"action_id": "act", "sources": [{"object_id": "RULE-001", "pointer": "/objects/rules/0/statement"}]}],
            "lifecycles": [
                {
                    "lifecycle_id": "life",
                    "sources": [{"object_id": "STATE-001", "pointer": "/objects/states/0/values"}],
                    "superseded_sentinels": [
                        {"object_id": "STATE-000", "pointer": "/objects/states/1/values", "active": False}
                    ],
                }
            ],
        }
        materialized = materialize_definition(state, blueprint)
        refs = (
            materialized["actions"][0]["sources"]
            + materialized["lifecycles"][0]["sources"]
            + materialized["lifecycles"][0]["superseded_sentinels"]
        )
        self.assertTrue(all(len(ref["value_sha256"]) == 64 for ref in refs))
        self.assertEqual("must", state["objects"]["rules"][0]["statement"])

    def test_revision_44_blueprint_compiles_from_read_only_canonical_state(self):
        state_path = ROOT / "product-definition" / "client-feedback-portal-dogfood" / "state.json"
        blueprint_path = DOWNSTREAM / "products" / "client-feedback-rev44.json"
        state_bytes_before = state_path.read_bytes()
        state = json.loads(state_bytes_before)
        blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
        bundle = compile_contract(state, materialize_definition(state, blueprint))
        self.assertEqual(FULL_CONTRACT_VERSION, bundle["contract_schema_version"])
        self.assertTrue(is_full_handoff_contract(bundle))
        self.assertEqual(44, bundle["source_authority"]["approved_revision"])
        self.assertEqual(
            "2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1",
            bundle["source_authority"]["approved_digest"],
        )
        assessment = bundle["authority_assessment"]
        self.assertTrue(assessment["structurally_valid"])
        self.assertTrue(assessment["provenance_valid"])
        self.assertTrue(assessment["machine_derived_obligations_verified"])
        self.assertEqual(1, assessment["machine_derived_field_count"])
        self.assertEqual(37, assessment["review_required_field_count"])
        self.assertTrue(assessment["review_required_obligations_present"])
        self.assertAlmostEqual(1 / 38, assessment["machine_verifiable_coverage"])
        obligations = {
            obligation
            for action in bundle["actions"]
            for obligation in semantic_value(action["test_obligations"])
        }
        self.assertTrue(
            {"authority-loss", "exact-version-stale", "idempotent-replay", "delivery-separation", "append-only-history"}
            <= obligations
        )
        self.assertEqual(state_bytes_before, state_path.read_bytes())

    def test_full_schema_rejects_removal_of_every_required_action_field(self):
        state_path = ROOT / "product-definition" / "client-feedback-portal-dogfood" / "state.json"
        blueprint_path = DOWNSTREAM / "products" / "client-feedback-rev44.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
        compile_contract(state, materialize_definition(state, blueprint))
        for field_name in sorted(ACTION_FIELDS):
            with self.subTest(field_name=field_name):
                invalid = copy.deepcopy(blueprint)
                invalid["actions"][0].pop(field_name)
                with self.assertRaises(ContractError):
                    compile_contract(state, materialize_definition(state, invalid))


if __name__ == "__main__":
    unittest.main()
