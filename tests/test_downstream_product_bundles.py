import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
DOWNSTREAM = SKILL_ROOT / "downstream"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.contracts import compile_contract, materialize_definition


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
        self.assertEqual(ACTION_FIELDS, set(action_schema["$defs"]["action"]["required"]))
        self.assertIn("superseded_sentinels", lifecycle_schema["$defs"]["lifecycle"]["required"])
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
        bundle = compile_contract(state, materialized)
        self.assertEqual("sample", bundle["source_authority"]["product_slug"])

    def test_revision_44_blueprint_compiles_from_read_only_canonical_state(self):
        state_path = ROOT / "product-definition" / "client-feedback-portal-dogfood" / "state.json"
        blueprint_path = DOWNSTREAM / "products" / "client-feedback-rev44.json"
        state_bytes_before = state_path.read_bytes()
        state = json.loads(state_bytes_before)
        blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
        bundle = compile_contract(state, materialize_definition(state, blueprint))
        self.assertEqual(44, bundle["source_authority"]["approved_revision"])
        self.assertEqual(
            "2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1",
            bundle["source_authority"]["approved_digest"],
        )
        obligations = {obligation for action in bundle["actions"] for obligation in action["test_obligations"]}
        self.assertTrue(
            {"authority-loss", "exact-version-stale", "idempotent-replay", "delivery-separation", "append-only-history"}
            <= obligations
        )
        self.assertEqual(state_bytes_before, state_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
