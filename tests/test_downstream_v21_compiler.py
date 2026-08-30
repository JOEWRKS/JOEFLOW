import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream.schema_validation import validate_instance  # noqa: E402
from downstream_v2.authority import DownstreamV2Error  # noqa: E402
from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from downstream_v2.contracts import validate_action_contract_v2  # noqa: E402
from downstream_v2.seeds import (  # noqa: E402
    build_closed_source_seed_inventory,
    source_seed_index,
)
from downstream_v21.compiler import (  # noqa: E402
    compile_handoff_definition_v21,
    validate_verification_basis,
)
from downstream_v21.contracts import (  # noqa: E402
    artifact_hash_v21,
    semantic_contract_hash_v21,
    validate_action_contract_v21,
)
from downstream_v21.derivation import seed_matches_selector_v21  # noqa: E402
from downstream_v21.responsibility import load_responsibility_profile_v21  # noqa: E402
from tests.downstream_v21_support import (  # noqa: E402
    closed_v2_state,
    source_seed_by_location,
)
from tests.test_downstream_v2_compiler import complete_definition  # noqa: E402


ACTION_FIELDS = (
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
    "trace",
)
REMOVED_RUNTIME_FIELDS = {
    "default_result",
    "result_expectations",
    "test_obligations",
}
LIFECYCLE_FIELDS = (
    "current_states",
    "allowed_transitions",
    "forbidden_transitions",
    "boundary_conditions",
    "reversibility",
    "reversal_window",
    "object_outcome",
    "required_reason",
    "required_confirmation",
    "required_evidence",
    "authority",
    "history_preservation",
)


ACTION_CONTRACT_SCHEMA = json.loads(
    (
        PACKAGE_ROOT
        / "downstream_v21"
        / "schemas"
        / "action-contract-v21.schema.json"
    ).read_text(encoding="utf-8")
)
HANDOFF_DEFINITION_SCHEMA = json.loads(
    (
        PACKAGE_ROOT
        / "downstream_v21"
        / "schemas"
        / "handoff-definition-v21.schema.json"
    ).read_text(encoding="utf-8")
)


def complete_definition_v21(state, *, review=False):
    seeds = build_closed_source_seed_inventory(state)
    profile = load_responsibility_profile_v21()
    scope_refs = ["REQ-001", "SCR-001", "SURF-001"]
    locator = {"screen_ref": "SCR-001", "action_key": "submit"}
    context = {
        "authority_scope_refs": scope_refs,
        "current_scope_refs": scope_refs,
        "ux_action_locator": locator,
    }
    outcome = source_seed_by_location(
        seeds,
        scope="CORE",
        owner_ref="REQ-001",
        axis="happy_path",
    )["seed_key"]
    acceptance = source_seed_by_location(
        seeds,
        scope="CORE",
        owner_ref="REQ-001",
        axis="acceptance",
    )["seed_key"]
    basis_refs = {outcome, acceptance}

    def spec(field_name, group):
        entry = profile[group][field_name]
        matches = [
            seed
            for seed in seeds
            if seed["seed_key"] not in basis_refs
            and any(
                seed_matches_selector_v21(seed, selector, context)
                for selector in entry["allowed_seed_selectors"]
            )
        ]
        if not matches:
            raise AssertionError(f"fixture has no non-basis seed for {group}/{field_name}")
        seed = matches[0]
        if review and entry["expectation"] == "REVIEW_PERMITTED":
            return {
                "kind": "REVIEW_REQUIRED",
                "source_seed_refs": [seed["seed_key"]],
                "proposed_value": f"reviewed {field_name}",
                "why_structuring_is_insufficient": "Presentation meaning requires human judgment.",
                "interpretation_scope": f"Only {field_name} wording.",
            }
        return {"kind": "DIRECT_AUTHORITY", "source_seed_ref": seed["seed_key"]}

    return {
        "definition_schema_version": "joewrks.handoff-definition/2.1",
        "product_slug": "semantic-closure-v2",
        "actions": [
            {
                "action_id": "submit-request",
                "authority_scope_refs": ["SURF-001", "REQ-001", "SCR-001"],
                "ux_action_locator": locator,
                "fields": {
                    field: spec(field, "action_fields") for field in ACTION_FIELDS
                },
                "verification_basis": {
                    "outcome_basis_seed_refs": [outcome],
                    "acceptance_basis_seed_refs": [acceptance],
                },
            }
        ],
        "lifecycles": [
            {
                "lifecycle_id": "request-lifecycle",
                "authority_scope_refs": ["SCR-001", "REQ-001", "SURF-001"],
                "fields": {
                    field: spec(field, "lifecycle_fields")
                    for field in LIFECYCLE_FIELDS
                },
            }
        ],
    }


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.definition = complete_definition_v21(self.state)

    def compile(self, definition=None, state=None):
        return compile_handoff_definition_v21(
            self.state if state is None else state,
            self.definition if definition is None else definition,
        )

    def assert_invalid_handoff(self, definition):
        with self.assertRaises(DownstreamV2Error) as raised:
            self.compile(definition)
        self.assertTrue(raised.exception.code.startswith("INVALID_"))

    def test_complete_definition_produces_schema_valid_v21_contract(self):
        validate_instance(self.definition, HANDOFF_DEFINITION_SCHEMA)
        result = self.compile()
        self.assertEqual(result["status"], "AUTHORITY_READY_MACHINE_VERIFIED")
        self.assertEqual(
            set(result),
            {
                "status",
                "contract",
                "semantic_debt",
                "semantic_gaps",
                "expressiveness_gaps",
                "reentry_events",
            },
        )
        self.assertEqual(result["semantic_gaps"], [])
        self.assertEqual(result["expressiveness_gaps"], [])
        self.assertEqual(result["reentry_events"], [])
        contract = result["contract"]
        validate_instance(contract, ACTION_CONTRACT_SCHEMA)
        self.assertEqual(validate_action_contract_v21(contract), [])
        self.assertEqual(
            contract["compiler"],
            {
                "id": "joewrks-product-definition/downstream-v2.1",
                "version": "core-semantic-closure-v2-m5.1",
            },
        )

    def test_v21_contract_rejects_2_0_identity(self):
        v20_contract = compile_handoff_definition(
            self.state,
            complete_definition(self.state),
        )["contract"]
        errors = validate_action_contract_v21(v20_contract)
        self.assertTrue(
            any(error["path"] == "/contract_schema_version" for error in errors)
        )

    def test_v20_validator_rejects_v21_contract(self):
        contract = self.compile()["contract"]
        errors = validate_action_contract_v2(contract)
        self.assertTrue(
            any(error["path"] == "/contract_schema_version" for error in errors)
        )

    def test_v21_action_inventory_excludes_runtime_only_fields(self):
        action = self.compile()["contract"]["actions"][0]
        self.assertEqual(set(action["fields"]), set(ACTION_FIELDS))
        self.assertTrue(REMOVED_RUNTIME_FIELDS.isdisjoint(action["fields"]))
        self.assertEqual(
            set(action),
            {
                "action_id",
                "authority_scope_refs",
                "ux_action_locator",
                "fields",
                "verification_basis",
            },
        )

    def test_v21_action_requires_verification_basis_and_exact_ux_locator(self):
        missing = copy.deepcopy(self.definition)
        del missing["actions"][0]["verification_basis"]
        self.assert_invalid_handoff(missing)
        no_locator = copy.deepcopy(self.definition)
        no_locator["actions"][0]["ux_action_locator"] = None
        self.assert_invalid_handoff(no_locator)

    def test_verification_basis_rejects_empty_unsorted_duplicate_or_wrong_selector_refs(self):
        inventory = build_closed_source_seed_inventory(self.state)
        seeds = source_seed_index(inventory)
        profile = load_responsibility_profile_v21()
        happy = source_seed_by_location(
            inventory,
            scope="CORE",
            owner_ref="REQ-001",
            axis="happy_path",
        )["seed_key"]
        acceptance = source_seed_by_location(
            inventory,
            scope="CORE",
            owner_ref="REQ-001",
            axis="acceptance",
        )["seed_key"]
        ux_success = source_seed_by_location(
            inventory,
            scope="UX_ACTION",
            owner_ref="SCR-001",
            axis="success",
            action_key="submit",
        )["seed_key"]
        actor = source_seed_by_location(
            inventory,
            scope="CORE",
            owner_ref="REQ-001",
            axis="actor",
        )["seed_key"]
        context = {
            "authority_scope_refs": ["REQ-001", "SCR-001", "SURF-001"],
            "current_scope_refs": ["REQ-001", "SCR-001", "SURF-001"],
            "ux_action_locator": {"screen_ref": "SCR-001", "action_key": "submit"},
        }
        valid = {
            "outcome_basis_seed_refs": [happy],
            "acceptance_basis_seed_refs": [acceptance],
        }
        cases = []
        empty = copy.deepcopy(valid)
        empty["outcome_basis_seed_refs"] = []
        cases.append((empty, context))
        duplicate = copy.deepcopy(valid)
        duplicate["outcome_basis_seed_refs"] = [happy, happy]
        cases.append((duplicate, context))
        unsorted = copy.deepcopy(valid)
        unsorted["outcome_basis_seed_refs"] = list(
            reversed(sorted([happy, ux_success]))
        )
        cases.append((unsorted, context))
        wrong_outcome = copy.deepcopy(valid)
        wrong_outcome["outcome_basis_seed_refs"] = [actor]
        cases.append((wrong_outcome, context))
        wrong_acceptance = copy.deepcopy(valid)
        wrong_acceptance["acceptance_basis_seed_refs"] = [happy]
        cases.append((wrong_acceptance, context))
        wrong_scope = copy.deepcopy(context)
        wrong_scope["authority_scope_refs"] = ["SCR-001", "SURF-001"]
        cases.append((valid, wrong_scope))
        wrong_locator = copy.deepcopy(context)
        wrong_locator["ux_action_locator"]["action_key"] = "other"
        ux_basis = copy.deepcopy(valid)
        ux_basis["outcome_basis_seed_refs"] = [ux_success]
        cases.append((ux_basis, wrong_locator))

        for basis, candidate_context in cases:
            with self.subTest(basis=basis, context=candidate_context):
                with self.assertRaisesRegex(ValueError, "INVALID_VERIFICATION_BASIS"):
                    validate_verification_basis(
                        basis,
                        context=candidate_context,
                        seeds=seeds,
                        profile=profile,
                    )

    def test_verification_basis_refs_remain_consumed_even_when_no_field_uses_them(self):
        contract = self.compile()["contract"]
        action = contract["actions"][0]
        ordinary_refs = {
            ref
            for collection in (contract["actions"], contract["lifecycles"])
            for item in collection
            for field in item["fields"].values()
            for ref in field["source_seed_refs"]
        }
        basis_refs = {
            ref
            for refs in action["verification_basis"].values()
            for ref in refs
        }
        self.assertTrue(basis_refs.isdisjoint(ordinary_refs))
        inventory_refs = {
            seed["seed_key"] for seed in contract["source_seed_inventory"]
        }
        self.assertTrue(basis_refs <= inventory_refs)
        self.assertEqual(
            action["verification_basis"],
            self.definition["actions"][0]["verification_basis"],
        )

    def test_semantic_hash_changes_when_verification_basis_changes(self):
        first = self.compile()["contract"]
        changed = copy.deepcopy(self.definition)
        inventory = build_closed_source_seed_inventory(self.state)
        ux_success = source_seed_by_location(
            inventory,
            scope="UX_ACTION",
            owner_ref="SCR-001",
            axis="success",
            action_key="submit",
        )["seed_key"]
        changed["actions"][0]["verification_basis"][
            "outcome_basis_seed_refs"
        ] = [ux_success]
        second = self.compile(changed)["contract"]
        self.assertNotEqual(
            first["semantic_contract_hash"], second["semantic_contract_hash"]
        )
        self.assertNotEqual(first["artifact_hash"], second["artifact_hash"])

    def test_only_snapshot_state_hash_is_excluded_from_semantic_projection(self):
        contract = self.compile()["contract"]
        snapshot_changed = copy.deepcopy(contract)
        snapshot_changed["source_authority"]["snapshot_state_sha256"] = "0" * 64
        self.assertEqual(
            semantic_contract_hash_v21(contract),
            semantic_contract_hash_v21(snapshot_changed),
        )
        self.assertNotEqual(
            artifact_hash_v21(contract), artifact_hash_v21(snapshot_changed)
        )


if __name__ == "__main__":
    unittest.main()
