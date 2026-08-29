import copy
import hashlib
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

from approval_v2 import definition_digest  # noqa: E402
from authority_binding_v2 import sha256_json  # noqa: E402
from downstream_v2.authority import DownstreamV2Error  # noqa: E402
from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from downstream_v2.contracts import (  # noqa: E402
    artifact_hash,
    semantic_contract_hash,
    validate_action_contract_v2,
)
from downstream_v2.derivation import (  # noqa: E402
    load_responsibility_profile,
    seed_matches_selector,
)
from downstream_v2.seeds import build_closed_source_seed_inventory  # noqa: E402
from tests.downstream_v2_support import closed_v2_state  # noqa: E402


ACTION_FIELDS = (
    "actor", "authentication", "relationship_predicate", "object_binding",
    "concurrency", "preconditions", "allowed_current_states", "forbidden_states",
    "input_invariants", "command", "expected_domain_mutation", "forbidden_mutations",
    "default_result", "result_expectations", "version_result", "history_result",
    "business_side_effects", "delivery_effects", "idempotency", "rejection",
    "recovery", "visible_success", "visible_error", "superseded_rules",
    "test_obligations", "trace",
)
LIFECYCLE_FIELDS = (
    "current_states", "allowed_transitions", "forbidden_transitions",
    "boundary_conditions", "reversibility", "reversal_window", "object_outcome",
    "required_reason", "required_confirmation", "required_evidence", "authority",
    "history_preservation",
)


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def literal_sha256(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def complete_definition(state, *, review=False):
    seeds = build_closed_source_seed_inventory(state)
    profile = load_responsibility_profile()
    context = {
        "authority_scope_refs": ["REQ-001", "SCR-001", "SURF-001"],
        "current_scope_refs": ["REQ-001", "SCR-001", "SURF-001"],
        "ux_action_locator": {"screen_ref": "SCR-001", "action_key": "submit"},
    }

    def spec(field_name, group):
        entry = profile[group][field_name]
        matches = [
            seed for seed in seeds
            if any(
                seed_matches_selector(seed, selector, context)
                for selector in entry["allowed_seed_selectors"]
            )
        ]
        if not matches:
            raise AssertionError(f"fixture has no permitted seed for {group}/{field_name}")
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
        "definition_schema_version": "joewrks.handoff-definition/2.0",
        "product_slug": "semantic-closure-v2",
        "actions": [{
            "action_id": "submit-request",
            "authority_scope_refs": ["SURF-001", "REQ-001", "SCR-001"],
            "ux_action_locator": {"screen_ref": "SCR-001", "action_key": "submit"},
            "fields": {field: spec(field, "action_fields") for field in ACTION_FIELDS},
        }],
        "lifecycles": [{
            "lifecycle_id": "request-lifecycle",
            "authority_scope_refs": ["SCR-001", "REQ-001", "SURF-001"],
            "fields": {field: spec(field, "lifecycle_fields") for field in LIFECYCLE_FIELDS},
        }],
    }


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.definition = complete_definition(self.state)

    def compile(self, definition=None, state=None):
        return compile_handoff_definition(
            self.state if state is None else state,
            self.definition if definition is None else definition,
        )

    def assert_rejected(self, definition, code):
        with self.assertRaises(DownstreamV2Error) as raised:
            self.compile(definition)
        self.assertEqual(raised.exception.code, code)

    def test_closed_m4_and_complete_definition_produce_valid_v2_contract(self):
        result = self.compile()
        self.assertEqual(result["status"], "AUTHORITY_READY_MACHINE_VERIFIED")
        self.assertEqual(result["gaps"], [])
        self.assertEqual(result["reentry_events"], [])
        contract = result["contract"]
        self.assertEqual(contract["contract_schema_version"], "joewrks.action-conformance/2.0")
        self.assertEqual(set(contract), {
            "contract_schema_version", "compiler", "source_authority",
            "responsibility_profile", "scope_commitments", "source_seed_inventory",
            "actions", "lifecycles", "semantic_debt", "handoff_status",
            "semantic_assurance", "semantic_contract_hash", "artifact_hash",
        })
        self.assertEqual(validate_action_contract_v2(contract), [])
        self.assertEqual(contract["semantic_debt"]["authority_gap_count"], 0)
        self.assertEqual(contract["semantic_debt"]["authority_gaps"], [])

    def test_wrong_product_slug_is_rejected(self):
        changed = copy.deepcopy(self.definition)
        changed["product_slug"] = "another-product"
        self.assert_rejected(changed, "PRODUCT_SLUG_MISMATCH")

    def test_duplicate_action_and_lifecycle_ids_are_rejected(self):
        for collection, code in (
            ("actions", "DUPLICATE_ACTION_ID"),
            ("lifecycles", "DUPLICATE_LIFECYCLE_ID"),
        ):
            with self.subTest(collection=collection):
                changed = copy.deepcopy(self.definition)
                changed[collection].append(copy.deepcopy(changed[collection][0]))
                self.assert_rejected(changed, code)

    def test_missing_and_extra_semantic_fields_are_rejected(self):
        missing = copy.deepcopy(self.definition)
        del missing["actions"][0]["fields"]["command"]
        self.assert_rejected(missing, "INVALID_SEMANTIC_FIELD_INVENTORY")
        extra = copy.deepcopy(self.definition)
        extra["lifecycles"][0]["fields"]["invented"] = {
            "kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-invented"
        }
        self.assert_rejected(extra, "INVALID_SEMANTIC_FIELD_INVENTORY")

    def test_seed_must_be_permitted_in_the_actions_exact_scope(self):
        changed = copy.deepcopy(self.definition)
        changed["actions"][0]["authority_scope_refs"] = ["SCR-001"]
        result = self.compile(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertIsNone(result["contract"])
        self.assertGreater(result["semantic_debt"]["authority_gap_count"], 0)
        self.assertTrue(all(gap["code"] == "SEMANTIC_AUTHORITY_GAP" for gap in result["gaps"]))

    def test_direct_output_is_the_exact_seed_value_and_inventory_is_consumed_only(self):
        result = self.compile()
        contract = result["contract"]
        actor_spec = self.definition["actions"][0]["fields"]["actor"]
        available = {seed["seed_key"]: seed for seed in build_closed_source_seed_inventory(self.state)}
        actor = contract["actions"][0]["fields"]["actor"]
        self.assertEqual(actor["value"], available[actor_spec["source_seed_ref"]]["value"])
        consumed_refs = {
            ref
            for collection in (contract["actions"], contract["lifecycles"])
            for item in collection
            for field in item["fields"].values()
            for ref in field["source_seed_refs"]
        }
        self.assertEqual(
            [seed["seed_key"] for seed in contract["source_seed_inventory"]],
            sorted(consumed_refs),
        )
        self.assertLess(len(contract["source_seed_inventory"]), len(available))
        self.assertEqual(
            contract["source_authority"]["consumed_seed_inventory_digest"],
            literal_sha256(contract["source_seed_inventory"]),
        )
        self.assertNotIn("source_seed_inventory_digest", contract["source_authority"])

    def test_machine_output_is_recomputed_from_the_seed(self):
        changed = copy.deepcopy(self.definition)
        seed = next(
            item for item in build_closed_source_seed_inventory(self.state)
            if item["location"] == {
                "scope": "CORE", "owner_ref": "REQ-001", "axis": "alternative_path",
                "pack_id": None, "action_key": None,
            }
        )
        changed["actions"][0]["fields"]["concurrency"] = {
            "kind": "MACHINE_DERIVED", "operator": "extract",
            "source_seed_ref": seed["seed_key"], "pointer": "/0",
        }
        field = self.compile(changed)["contract"]["actions"][0]["fields"]["concurrency"]
        self.assertEqual(field["value"], seed["value"][0])
        self.assertEqual(field["source_seed_refs"], [seed["seed_key"]])
        self.assertEqual(field["derivation"], {
            "kind": "MACHINE_DERIVED", "operator": "extract", "pointer": "/0"
        })

    def test_review_exists_only_where_responsibility_profile_permits_it(self):
        reviewed = complete_definition(self.state, review=True)
        contract = self.compile(reviewed)["contract"]
        self.assertEqual(contract["handoff_status"], "AUTHORITY_READY_REVIEW_PENDING")
        self.assertEqual(contract["semantic_assurance"], {"status": "NOT_MEASURED"})
        self.assertEqual(contract["semantic_debt"]["review_required_count"], 2)
        self.assertEqual(
            contract["semantic_debt"]["review_required_fields"],
            ["actions/submit-request/visible_error", "actions/submit-request/visible_success"],
        )

    def test_review_on_deterministic_field_is_a_gap_and_never_a_contract(self):
        changed = copy.deepcopy(self.definition)
        permitted_review = complete_definition(self.state, review=True)["actions"][0]["fields"]["visible_success"]
        changed["actions"][0]["fields"]["authentication"] = permitted_review
        result = self.compile(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertIsNone(result["contract"])
        gap = next(gap for gap in result["gaps"] if gap["field_path"].endswith("/authentication"))
        self.assertEqual(gap["required_expectation"], "DETERMINISTIC_REQUIRED")
        self.assertEqual(gap["required_authority_class"], "INTENT")
        self.assertNotIn(gap["field_path"], result["semantic_debt"]["review_required_fields"])
        self.assertEqual(result["reentry_events"], [])

    def test_unresolved_field_returns_exact_gap_without_materializing_contract(self):
        changed = copy.deepcopy(self.definition)
        changed["actions"][0]["fields"]["authentication"] = {
            "kind": "UNRESOLVED",
            "gap_type": "AMBIGUITY_FOUND",
            "description": "Authentication behavior is not authoritative.",
            "required_authority_class": "CONSTRAINT",
            "evidence_refs": ["EVD-001"],
        }
        result = self.compile(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertIsNone(result["contract"])
        self.assertEqual(result["semantic_debt"]["authority_gap_count"], 1)
        self.assertEqual(result["gaps"][0]["gap_type"], "AMBIGUITY_FOUND")
        self.assertEqual(result["gaps"][0]["required_authority_class"], "CONSTRAINT")
        self.assertEqual(result["gaps"][0]["evidence_refs"], ["EVD-001"])

    def test_production_contract_never_contains_a_gap(self):
        contract = self.compile()["contract"]
        self.assertEqual(contract["semantic_debt"]["authority_gap_count"], 0)
        self.assertEqual(contract["semantic_debt"]["authority_gaps"], [])
        invalid = copy.deepcopy(contract)
        invalid["semantic_debt"]["authority_gap_count"] = 1
        invalid["semantic_debt"]["authority_gaps"] = [{"code": "SEMANTIC_AUTHORITY_GAP"}]
        self.assertTrue(validate_action_contract_v2(invalid))

    def test_scope_commitments_are_exact_current_records_sorted_and_unique(self):
        contract = self.compile()["contract"]
        expected_records = {
            "REQ-001": self.state["objects"]["requirements"][0],
            "SCR-001": self.state["objects"]["screens"][0],
            "SURF-001": self.state["surface_manifest"]["records"][0],
        }
        self.assertEqual(contract["scope_commitments"], [
            {"record_id": record_id, "record_type": record_id.split("-", 1)[0], "record_sha256": literal_sha256(expected_records[record_id])}
            for record_id in sorted(expected_records)
        ])
        self.assertNotIn("scope_commitments_digest", contract)
        missing = copy.deepcopy(self.definition)
        missing["actions"][0]["authority_scope_refs"] = ["REQ-MISSING"]
        self.assert_rejected(missing, "INVALID_AUTHORITY_SCOPE_REF")
        duplicate = copy.deepcopy(self.definition)
        duplicate["lifecycles"][0]["authority_scope_refs"].append("REQ-001")
        self.assert_rejected(duplicate, "INVALID_AUTHORITY_SCOPE_REFS")


class ContractHashTests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.definition = complete_definition(self.state)

    def contract(self, state=None, definition=None):
        return compile_handoff_definition(
            self.state if state is None else state,
            self.definition if definition is None else definition,
        )["contract"]

    def test_repeated_compilation_is_byte_deterministic(self):
        first = self.contract()
        second = self.contract()
        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        self.assertEqual(first["semantic_contract_hash"], semantic_contract_hash(first))
        self.assertEqual(first["artifact_hash"], artifact_hash(first))

    def test_semantic_change_changes_both_hashes(self):
        first_definition = complete_definition(self.state, review=True)
        second_definition = copy.deepcopy(first_definition)
        second_definition["actions"][0]["fields"]["visible_success"]["proposed_value"] = "A changed interpretation"
        first = self.contract(definition=first_definition)
        second = self.contract(definition=second_definition)
        self.assertNotEqual(first["semantic_contract_hash"], second["semantic_contract_hash"])
        self.assertNotEqual(first["artifact_hash"], second["artifact_hash"])

    def test_snapshot_only_change_changes_artifact_but_not_semantic_hash(self):
        changed = copy.deepcopy(self.state)
        changed["evidence"].append({
            "id": "EVD-901", "status": "CURRENT", "source_kind": "USER_CONFIRMED_INTENT",
            "locator": "product-definition/unconsumed-observation", "claim": "A nonsemantic observation.",
            "confidence": "DIRECT", "authority_classes": ["INTENT"],
            "observed_version": None, "content_hash": None,
        })
        changed["discovery_baseline"]["evidence_commitment_digest"] = sha256_json(changed["evidence"])
        self.assertEqual(definition_digest(changed), definition_digest(self.state))
        first = self.contract()
        second = self.contract(state=changed)
        self.assertEqual(first["semantic_contract_hash"], second["semantic_contract_hash"])
        self.assertNotEqual(first["artifact_hash"], second["artifact_hash"])

    def test_seed_inventory_and_responsibility_profile_are_semantically_committed(self):
        contract = self.contract()
        changed_seed_digest = copy.deepcopy(contract)
        changed_seed_digest["source_authority"]["consumed_seed_inventory_digest"] = "0" * 64
        self.assertNotEqual(semantic_contract_hash(contract), semantic_contract_hash(changed_seed_digest))
        changed_profile = copy.deepcopy(contract)
        changed_profile["responsibility_profile"]["digest"] = "0" * 64
        self.assertNotEqual(semantic_contract_hash(contract), semantic_contract_hash(changed_profile))
        changed_scope = copy.deepcopy(contract)
        changed_scope["scope_commitments"][0]["record_sha256"] = "0" * 64
        self.assertNotEqual(semantic_contract_hash(contract), semantic_contract_hash(changed_scope))

    def test_malformed_or_nonlowercase_hashes_are_rejected(self):
        contract = self.contract()
        paths = (
            ("semantic_contract_hash",),
            ("artifact_hash",),
            ("source_authority", "approved_definition_digest"),
            ("source_authority", "approved_manifest_digest"),
            ("source_authority", "snapshot_state_sha256"),
            ("source_authority", "consumed_seed_inventory_digest"),
            ("responsibility_profile", "digest"),
            ("scope_commitments", 0, "record_sha256"),
        )
        for path in paths:
            with self.subTest(path=path):
                invalid = copy.deepcopy(contract)
                target = invalid
                for token in path[:-1]:
                    target = target[token]
                target[path[-1]] = "A" * 64
                self.assertTrue(validate_action_contract_v2(invalid))


if __name__ == "__main__":
    unittest.main()
