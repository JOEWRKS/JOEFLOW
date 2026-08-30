import copy
import importlib
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

from downstream.schema_validation import (  # noqa: E402
    SchemaValidationError,
    validate_instance,
)
from downstream_v2.authority import sha256_json  # noqa: E402
from downstream_v21.compiler import compile_handoff_definition_v21  # noqa: E402
from downstream_v21.contracts import (  # noqa: E402
    artifact_hash_v21,
    semantic_contract_hash_v21,
    validate_action_contract_v21,
)
from downstream_v21.semantic_review import (  # noqa: E402
    build_semantic_review_package_v21,
)
from tests.downstream_v21_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v21_compiler import complete_definition_v21  # noqa: E402
from tests.test_downstream_v21_semantic_review import (  # noqa: E402
    contract_with_action_ids,
    reviewed_output,
)


try:
    runtime_profile = importlib.import_module("downstream_v21.runtime_profile")
    runtime_plan = importlib.import_module("downstream_v21.runtime_plan")
except ModuleNotFoundError:
    runtime_profile = None
    runtime_plan = None


ACTION_RUNTIME_CRITICAL = (
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
    "superseded_rules",
)
ACTION_NON_RUNTIME_PRESENTATION = ("visible_success", "visible_error")
ACTION_ASSURANCE_ONLY = ("trace",)


def _action_refs(contract):
    return [
        f"actions/{action['action_id']}/{field_name}"
        for action in contract["actions"]
        for field_name in ACTION_RUNTIME_CRITICAL
    ]


def _lifecycle_refs(contract):
    return [
        f"lifecycles/{lifecycle['lifecycle_id']}/{field_name}"
        for lifecycle in contract["lifecycles"]
        for field_name in sorted(lifecycle["fields"])
    ]


def complete_runtime_draft(contract):
    actions = []
    for action in contract["actions"]:
        prefix = f"actions/{action['action_id']}"
        actions.append(
            {
                "action_id": action["action_id"],
                "cases": [
                    {
                        "result_expectation": {
                            "result_class": "SUCCESS",
                            "contract_field_refs": [
                                f"{prefix}/{field_name}"
                                for field_name in ACTION_RUNTIME_CRITICAL
                            ],
                        },
                        "component_expectations": [],
                        "evidence_assertions": [],
                        "fixture_requirements": ["OPAQUE_ID"],
                    }
                ],
            }
        )
    lifecycles = []
    for lifecycle in contract["lifecycles"]:
        prefix = f"lifecycles/{lifecycle['lifecycle_id']}"
        transition_refs = [
            f"{prefix}/current_states",
            f"{prefix}/allowed_transitions",
        ]
        remaining_refs = sorted(
            set(f"{prefix}/{field_name}" for field_name in lifecycle["fields"])
            - set(transition_refs)
        )
        lifecycles.append(
            {
                "lifecycle_id": lifecycle["lifecycle_id"],
                "cases": [
                    {
                        "transition_expectation": {
                            "from_state_source": {
                                "source": "CONTRACT_DERIVED",
                                "contract_field_path": transition_refs[0],
                                "pointer": "/value",
                            },
                            "to_state_source": {
                                "source": "CONTRACT_DERIVED",
                                "contract_field_path": transition_refs[1],
                                "pointer": "/value",
                            },
                            "contract_field_refs": transition_refs,
                        },
                        "component_expectations": [
                            {
                                "component": "authoritative_state",
                                "expectation": "CHANGED",
                                "contract_field_refs": remaining_refs,
                            }
                        ],
                        "evidence_assertions": [],
                        "fixture_requirements": ["REVISION_INSTANCE"],
                    }
                ],
            }
        )
    return {"actions": actions, "lifecycles": lifecycles}


class RuntimePlanV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = closed_v2_state()
        cls.contract = compile_handoff_definition_v21(
            cls.state,
            complete_definition_v21(cls.state),
        )["contract"]
        cls.review_contract = compile_handoff_definition_v21(
            cls.state,
            complete_definition_v21(cls.state, review=True),
        )["contract"]
        cls.review_package = build_semantic_review_package_v21(cls.review_contract)

    def require_api(self):
        self.assertIsNotNone(runtime_profile, "runtime responsibility API is missing")
        self.assertIsNotNone(runtime_plan, "runtime conformance-plan API is missing")

    def materialize(self, contract=None, draft=None, **review):
        self.require_api()
        contract = copy.deepcopy(contract or self.contract)
        draft = copy.deepcopy(draft or complete_runtime_draft(contract))
        return runtime_plan.materialize_runtime_plan(contract, draft, **review)

    def test_profile_has_exact_frozen_classification_and_digest(self):
        self.require_api()
        profile = runtime_profile.load_runtime_responsibility_profile()
        self.assertEqual(profile["profile_id"], "joewrks.runtime-responsibility/1.0")
        self.assertEqual(
            sorted(
                field_name
                for field_name, classification in profile["action_fields"].items()
                if classification == "RUNTIME_CRITICAL"
            ),
            sorted(ACTION_RUNTIME_CRITICAL),
        )
        self.assertEqual(
            sorted(
                field_name
                for field_name, classification in profile["action_fields"].items()
                if classification == "NON_RUNTIME_PRESENTATION"
            ),
            sorted(ACTION_NON_RUNTIME_PRESENTATION),
        )
        self.assertEqual(
            sorted(
                field_name
                for field_name, classification in profile["action_fields"].items()
                if classification == "ASSURANCE_ONLY"
            ),
            sorted(ACTION_ASSURANCE_ONLY),
        )
        self.assertTrue(profile["lifecycle_fields"])
        self.assertEqual(
            set(profile["lifecycle_fields"].values()), {"RUNTIME_CRITICAL"}
        )
        self.assertEqual(runtime_profile.runtime_responsibility_digest(), sha256_json(profile))

        profile["action_fields"]["actor"] = "ASSURANCE_ONLY"
        self.assertEqual(
            runtime_profile.load_runtime_responsibility_profile()["action_fields"]["actor"],
            "RUNTIME_CRITICAL",
        )

    def test_plan_rejects_caller_runtime_field_reclassification(self):
        draft = complete_runtime_draft(self.contract)
        draft["runtime_profile"] = {
            "action_fields": {"actor": "ASSURANCE_ONLY"}
        }
        with self.assertRaisesRegex(ValueError, "INVALID_RUNTIME_PLAN_DRAFT"):
            self.materialize(draft=draft)

    def test_plan_binds_exact_semantic_contract_hash_and_profile_digest(self):
        plan = self.materialize()
        self.assertEqual(
            plan["source_contract"],
            {
                "contract_schema_version": "joewrks.action-conformance/2.1",
                "semantic_contract_hash": self.contract["semantic_contract_hash"],
                "approved_definition_digest": self.contract["source_authority"][
                    "approved_definition_digest"
                ],
                "product_slug": self.contract["source_authority"]["product_slug"],
            },
        )
        self.assertEqual(
            plan["runtime_profile"]["digest"],
            runtime_profile.runtime_responsibility_digest(),
        )
        self.assertEqual(runtime_plan.validate_runtime_plan(plan, self.contract), [])
        schema = json.loads(
            (
                PACKAGE_ROOT
                / "downstream_v21"
                / "schemas"
                / "runtime-conformance-plan.schema.json"
            ).read_text(encoding="utf-8")
        )
        validate_instance(plan, schema)

    def test_plan_rejects_product_literal_expected_value(self):
        draft = complete_runtime_draft(self.contract)
        draft["actions"][0]["cases"][0]["evidence_assertions"].append(
            {
                "type": "path_equals",
                "pointer": "/result/status",
                "expected_value": "APPROVED",
                "contract_field_refs": [
                    "actions/submit-request/delivery_effects"
                ],
            }
        )
        with self.assertRaisesRegex(ValueError, "PRODUCT_LITERAL_FORBIDDEN"):
            self.materialize(draft=draft)

    def test_contract_derived_expected_value_must_resolve_exactly(self):
        draft = complete_runtime_draft(self.contract)
        assertion = {
            "type": "path_equals",
            "pointer": "/result/notification",
            "expected_value_source": {
                "source": "CONTRACT_DERIVED",
                "contract_field_path": "actions/submit-request/delivery_effects",
                "pointer": "/value/0",
            },
            "contract_field_refs": ["actions/submit-request/delivery_effects"],
        }
        draft["actions"][0]["cases"][0]["evidence_assertions"].append(assertion)
        self.materialize(draft=draft)

        assertion["expected_value_source"]["pointer"] = "/value/99"
        with self.assertRaisesRegex(ValueError, "UNRESOLVED_EXPECTED_VALUE_SOURCE"):
            self.materialize(draft=draft)

    def test_verification_basis_source_must_belong_to_same_action(self):
        draft = complete_runtime_draft(self.contract)
        action = self.contract["actions"][0]
        committed = {
            ref for refs in action["verification_basis"].values() for ref in refs
        }
        foreign = next(
            seed["seed_key"]
            for seed in self.contract["source_seed_inventory"]
            if seed["seed_key"] not in committed
        )
        assertion = {
            "type": "path_equals",
            "pointer": "/result/outcome",
            "expected_value_source": {
                "source": "VERIFICATION_BASIS",
                "seed_ref": foreign,
                "pointer": "/value",
            },
            "contract_field_refs": ["actions/submit-request/version_result"],
        }
        draft["actions"][0]["cases"][0]["evidence_assertions"].append(assertion)
        with self.assertRaisesRegex(ValueError, "INVALID_VERIFICATION_BASIS_SOURCE"):
            self.materialize(draft=draft)

        assertion["expected_value_source"]["seed_ref"] = next(iter(committed))
        self.materialize(draft=draft)

    def test_any_does_not_cover_runtime_critical_field(self):
        draft = complete_runtime_draft(self.contract)
        missing = "actions/submit-request/actor"
        result_refs = draft["actions"][0]["cases"][0]["result_expectation"][
            "contract_field_refs"
        ]
        result_refs.remove(missing)
        draft["actions"][0]["cases"][0]["component_expectations"].append(
            {
                "component": "authoritative_state",
                "expectation": "ANY",
                "contract_field_refs": [missing],
            }
        )
        plan = self.materialize(draft=draft)
        self.assertEqual(plan["coverage_summary"]["status"], "INCOMPLETE")
        self.assertIn(missing, plan["coverage_summary"]["missing_field_refs"])
        self.assertNotIn(missing, plan["coverage_summary"]["covered_field_refs"])

    def test_bare_contract_field_ref_does_not_count_as_coverage(self):
        draft = complete_runtime_draft(self.contract)
        case = draft["actions"][0]["cases"][0]
        case["result_expectation"]["contract_field_refs"].remove(
            "actions/submit-request/actor"
        )
        case["contract_field_refs"] = ["actions/submit-request/actor"]
        with self.assertRaisesRegex(ValueError, "INVALID_RUNTIME_PLAN_DRAFT"):
            self.materialize(draft=draft)

    def test_concrete_component_or_assertion_relationship_counts_as_coverage(self):
        draft = complete_runtime_draft(self.contract)
        case = draft["actions"][0]["cases"][0]
        moved = "actions/submit-request/actor"
        case["result_expectation"]["contract_field_refs"].remove(moved)
        case["component_expectations"].append(
            {
                "component": "authoritative_state",
                "expectation": "UNCHANGED",
                "contract_field_refs": [moved],
            }
        )
        plan = self.materialize(draft=draft)
        self.assertEqual(plan["coverage_summary"]["status"], "COMPLETE")
        self.assertIn(moved, plan["coverage_summary"]["covered_field_refs"])

    def test_missing_runtime_critical_field_produces_runtime_mapping_gap_and_incomplete(self):
        draft = complete_runtime_draft(self.contract)
        missing = "actions/submit-request/actor"
        draft["actions"][0]["cases"][0]["result_expectation"][
            "contract_field_refs"
        ].remove(missing)
        plan = self.materialize(draft=draft)
        self.assertEqual(plan["coverage_summary"]["status"], "INCOMPLETE")
        self.assertEqual(
            plan["mapping_gaps"],
            [
                {
                    "code": "RUNTIME_MAPPING_GAP",
                    "field_ref": missing,
                    "remediation": "RUNTIME_PLAN",
                }
            ],
        )
        self.assertNotIn("reentry", json.dumps(plan["mapping_gaps"]).lower())

    def test_empty_case_inventory_materializes_complete_runtime_mapping_diagnostics(self):
        draft = complete_runtime_draft(self.contract)
        draft["actions"][0]["cases"] = []
        draft["lifecycles"][0]["cases"] = []
        try:
            plan = self.materialize(draft=draft)
        except ValueError as error:
            self.fail(f"empty case inventories must materialize diagnostics: {error}")
        critical = sorted(_action_refs(self.contract) + _lifecycle_refs(self.contract))
        self.assertEqual(plan["coverage_summary"]["status"], "INCOMPLETE")
        self.assertEqual(plan["coverage_summary"]["missing_field_refs"], critical)
        self.assertEqual(
            [gap["field_ref"] for gap in plan["mapping_gaps"]], critical
        )

    def test_runtime_critical_review_required_field_blocks_complete_until_confirmed(self):
        self.require_api()
        self.assertTrue(
            hasattr(runtime_plan, "_review_gated_coverage"),
            "runtime-critical review coverage gate is missing",
        )
        field_ref = "actions/example/reviewed_runtime_rule"
        fields = {
            field_ref: {"derivation": {"kind": "REVIEW_REQUIRED"}}
        }
        covered, missing, blocked = runtime_plan._review_gated_coverage(
            [field_ref], {field_ref}, fields, set()
        )
        self.assertEqual(covered, [])
        self.assertEqual(missing, [])
        self.assertEqual(blocked, [field_ref])

        covered, missing, blocked = runtime_plan._review_gated_coverage(
            [field_ref], {field_ref}, fields, {field_ref}
        )
        self.assertEqual(covered, [field_ref])
        self.assertEqual(missing, [])
        self.assertEqual(blocked, [])

    def test_frozen_review_required_presentation_fields_are_not_reclassified(self):
        self.require_api()
        profile = runtime_profile.load_runtime_responsibility_profile()
        review_paths = set(self.review_contract["semantic_debt"]["review_required_fields"])
        critical_review_paths = {
            path
            for path in review_paths
            if profile["action_fields"][path.rsplit("/", 1)[1]]
            == "RUNTIME_CRITICAL"
        }
        self.assertEqual(
            critical_review_paths,
            set(),
            "profile 1.0 must not silently reclassify review-only presentation fields",
        )

        pending = self.materialize(
            contract=self.review_contract,
            draft=complete_runtime_draft(self.review_contract),
            review_package=self.review_package,
        )
        self.assertEqual(pending["review_commitments"]["completion"], "PENDING")
        self.assertEqual(pending["coverage_summary"]["review_blocked_field_refs"], [])

        confirmed_output = reviewed_output(self.review_package)
        confirmed = self.materialize(
            contract=self.review_contract,
            draft=complete_runtime_draft(self.review_contract),
            review_package=self.review_package,
            review_output=confirmed_output,
        )
        self.assertEqual(
            confirmed["review_commitments"]["completion"],
            "REVIEW_OUTPUT_RECORDED",
        )

    def test_review_completion_does_not_change_not_measured_reliability(self):
        pending = self.materialize(
            contract=self.review_contract,
            draft=complete_runtime_draft(self.review_contract),
            review_package=self.review_package,
        )
        output = reviewed_output(self.review_package)
        complete = self.materialize(
            contract=self.review_contract,
            draft=complete_runtime_draft(self.review_contract),
            review_package=self.review_package,
            review_output=output,
        )
        self.assertEqual(
            pending["review_commitments"]["reliability_status"], "NOT_MEASURED"
        )
        self.assertEqual(
            complete["review_commitments"]["reliability_status"], "NOT_MEASURED"
        )
        self.assertEqual(
            complete["review_commitments"]["output_hash"], sha256_json(output)
        )
        self.assertNotEqual(complete["review_commitments"]["output_hash"], output["output_hash"])
        self.assertNotEqual(pending["plan_hash"], complete["plan_hash"])

    def test_rejected_review_routes_to_reentry_not_runtime_mapping_workaround(self):
        output = reviewed_output(self.review_package, "REJECTED_INTERPRETATION")
        plan = self.materialize(
            contract=self.review_contract,
            draft=complete_runtime_draft(self.review_contract),
            review_package=self.review_package,
            review_output=output,
        )
        self.assertEqual(plan["review_commitments"]["completion"], "REENTRY_REQUIRED")
        self.assertEqual(plan["coverage_summary"]["status"], "INCOMPLETE")
        self.assertEqual(plan["mapping_gaps"], [])

    def test_plan_case_and_test_ids_are_deterministic_and_unique(self):
        first = self.materialize()
        second = self.materialize()
        self.assertEqual(first, second)
        cases = [
            case
            for collection in (first["actions"], first["lifecycles"])
            for item in collection
            for case in item["cases"]
        ]
        case_ids = [case["case_id"] for case in cases]
        test_ids = [case["test_id"] for case in cases]
        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertEqual(len(test_ids), len(set(test_ids)))
        self.assertTrue(all(value.startswith("CASE-") and len(value) == 29 for value in case_ids))
        self.assertTrue(all(value.startswith("TEST-") and len(value) == 29 for value in test_ids))

    def test_plan_mutation_changes_plan_hash_not_semantic_contract_hash(self):
        first = self.materialize()
        changed_draft = complete_runtime_draft(self.contract)
        changed_draft["actions"][0]["cases"][0]["result_expectation"][
            "result_class"
        ] = "REJECTED"
        changed = self.materialize(draft=changed_draft)
        self.assertNotEqual(first["plan_hash"], changed["plan_hash"])
        self.assertNotEqual(
            first["actions"][0]["cases"][0]["test_id"],
            changed["actions"][0]["cases"][0]["test_id"],
        )
        self.assertEqual(
            first["source_contract"]["semantic_contract_hash"],
            changed["source_contract"]["semantic_contract_hash"],
        )
        self.assertEqual(
            first["source_contract"]["approved_definition_digest"],
            changed["source_contract"]["approved_definition_digest"],
        )

    def test_lifecycle_state_values_must_be_contract_derived(self):
        draft = complete_runtime_draft(self.contract)
        transition = draft["lifecycles"][0]["cases"][0]["transition_expectation"]
        transition["from_state_source"] = {
            "source": "FIXTURE_ONLY",
            "value": "REQUEST_READY",
        }
        with self.assertRaisesRegex(ValueError, "PRODUCT_LITERAL_FORBIDDEN"):
            self.materialize(draft=draft)

    def test_lifecycle_from_source_must_be_exact_current_states_field(self):
        draft = complete_runtime_draft(self.contract)
        transition = draft["lifecycles"][0]["cases"][0]["transition_expectation"]
        wrong = "lifecycles/request-lifecycle/forbidden_transitions"
        transition["from_state_source"]["contract_field_path"] = wrong
        transition["contract_field_refs"].append(wrong)
        with self.assertRaisesRegex(ValueError, "INVALID_TRANSITION_EXPECTATION"):
            self.materialize(draft=draft)

    def test_lifecycle_to_source_must_be_exact_allowed_transitions_field(self):
        draft = complete_runtime_draft(self.contract)
        transition = draft["lifecycles"][0]["cases"][0]["transition_expectation"]
        transition["to_state_source"]["contract_field_path"] = (
            "lifecycles/request-lifecycle/current_states"
        )
        with self.assertRaisesRegex(ValueError, "INVALID_TRANSITION_EXPECTATION"):
            self.materialize(draft=draft)

    def test_schema_rejects_wrong_lifecycle_transition_source_field(self):
        plan = self.materialize()
        transition = plan["lifecycles"][0]["cases"][0]["transition_expectation"]
        transition["from_state_source"]["contract_field_path"] = (
            "lifecycles/request-lifecycle/forbidden_transitions"
        )
        schema = json.loads(
            (
                PACKAGE_ROOT
                / "downstream_v21"
                / "schemas"
                / "runtime-conformance-plan.schema.json"
            ).read_text(encoding="utf-8")
        )
        with self.assertRaises(SchemaValidationError):
            validate_instance(plan, schema)

    def test_lifecycle_bare_ref_does_not_count_as_coverage(self):
        draft = complete_runtime_draft(self.contract)
        case = draft["lifecycles"][0]["cases"][0]
        case["contract_field_refs"] = [
            "lifecycles/request-lifecycle/current_states"
        ]
        with self.assertRaisesRegex(ValueError, "INVALID_RUNTIME_PLAN_DRAFT"):
            self.materialize(draft=draft)

    def test_lifecycle_complete_concrete_mapping_reaches_full_plan_coverage(self):
        plan = self.materialize()
        lifecycle = plan["lifecycles"][0]
        self.assertEqual(
            lifecycle["covered_contract_field_refs"], _lifecycle_refs(self.contract)
        )
        self.assertEqual(plan["coverage_summary"]["status"], "COMPLETE")

    def test_lifecycle_ambiguous_mapping_remains_runtime_mapping_gap(self):
        draft = complete_runtime_draft(self.contract)
        missing = "lifecycles/request-lifecycle/reversibility"
        component = draft["lifecycles"][0]["cases"][0][
            "component_expectations"
        ][0]
        component["contract_field_refs"].remove(missing)
        plan = self.materialize(draft=draft)
        self.assertEqual(plan["coverage_summary"]["status"], "INCOMPLETE")
        self.assertIn(missing, plan["coverage_summary"]["missing_field_refs"])
        self.assertEqual(
            next(gap for gap in plan["mapping_gaps"] if gap["field_ref"] == missing)[
                "remediation"
            ],
            "RUNTIME_PLAN",
        )

    def test_fixture_requirements_are_categories_without_values(self):
        draft = complete_runtime_draft(self.contract)
        draft["actions"][0]["cases"][0]["fixture_requirements"] = [
            {"category": "OPAQUE_ID", "value": "request-123"}
        ]
        with self.assertRaisesRegex(ValueError, "INVALID_FIXTURE_REQUIREMENT"):
            self.materialize(draft=draft)

    def test_valid_contract_identifiers_materialize_schema_valid_runtime_refs(self):
        contract = copy.deepcopy(self.contract)
        old_action_id = contract["actions"][0]["action_id"]
        old_lifecycle_id = contract["lifecycles"][0]["lifecycle_id"]
        new_action_id = "submit/request with space"
        new_lifecycle_id = "request/lifecycle with space"
        contract["actions"][0]["action_id"] = new_action_id
        contract["lifecycles"][0]["lifecycle_id"] = new_lifecycle_id
        for inventory_name in (
            "direct_authority_fields",
            "machine_derived_fields",
            "review_required_fields",
        ):
            contract["semantic_debt"][inventory_name] = [
                path.replace(
                    f"actions/{old_action_id}/",
                    f"actions/{new_action_id}/",
                ).replace(
                    f"lifecycles/{old_lifecycle_id}/",
                    f"lifecycles/{new_lifecycle_id}/",
                )
                for path in contract["semantic_debt"][inventory_name]
            ]
        contract["semantic_contract_hash"] = semantic_contract_hash_v21(contract)
        contract["artifact_hash"] = artifact_hash_v21(contract)
        self.assertEqual(validate_action_contract_v21(contract), [])

        draft = complete_runtime_draft(contract)
        original_contract = copy.deepcopy(contract)
        original_draft = copy.deepcopy(draft)
        plan = runtime_plan.materialize_runtime_plan(contract, draft)
        self.assertEqual(contract, original_contract)
        self.assertEqual(draft, original_draft)
        self.assertEqual(runtime_plan.validate_runtime_plan(plan, contract), [])
        schema = json.loads(
            (
                PACKAGE_ROOT
                / "downstream_v21"
                / "schemas"
                / "runtime-conformance-plan.schema.json"
            ).read_text(encoding="utf-8")
        )
        try:
            validate_instance(plan, schema)
        except SchemaValidationError as error:
            self.fail(f"runtime validator and published schema disagree: {error}")

        refs = plan["coverage_summary"]["runtime_critical_field_refs"]
        self.assertTrue(any("submit%2Frequest%20with%20space" in ref for ref in refs))
        self.assertTrue(
            any("request%2Flifecycle%20with%20space" in ref for ref in refs)
        )
        self.assertFalse(any(" " in ref for ref in refs))
        transition = plan["lifecycles"][0]["cases"][0]["transition_expectation"]
        encoded_lifecycle = "request%2Flifecycle%20with%20space"
        self.assertEqual(
            transition["from_state_source"]["contract_field_path"],
            f"lifecycles/{encoded_lifecycle}/current_states",
        )
        self.assertEqual(
            transition["to_state_source"]["contract_field_path"],
            f"lifecycles/{encoded_lifecycle}/allowed_transitions",
        )

    def test_review_bearing_special_identifier_supports_all_review_states(self):
        contract = contract_with_action_ids(
            self.review_contract,
            ["submit/request with space"],
        )
        draft = complete_runtime_draft(contract)
        original_contract = copy.deepcopy(contract)
        original_draft = copy.deepcopy(draft)
        try:
            package = build_semantic_review_package_v21(contract)
            original_package = copy.deepcopy(package)
            pending_without_package = runtime_plan.materialize_runtime_plan(
                contract,
                draft,
            )
            pending_with_package = runtime_plan.materialize_runtime_plan(
                contract,
                draft,
                review_package=package,
            )
            output = reviewed_output(package)
            original_output = copy.deepcopy(output)
            confirmed = runtime_plan.materialize_runtime_plan(
                contract,
                draft,
                review_package=package,
                review_output=output,
            )
        except ValueError as error:
            self.fail(f"valid review-bearing action ID cannot materialize: {error}")

        self.assertEqual(contract, original_contract)
        self.assertEqual(draft, original_draft)
        self.assertEqual(package, original_package)
        self.assertEqual(output, original_output)
        self.assertEqual(
            pending_without_package["review_commitments"]["completion"],
            "PENDING",
        )
        self.assertEqual(
            pending_with_package["review_commitments"]["completion"],
            "PENDING",
        )
        self.assertEqual(
            confirmed["review_commitments"]["completion"],
            "REVIEW_OUTPUT_RECORDED",
        )
        schema = json.loads(
            (
                PACKAGE_ROOT
                / "downstream_v21"
                / "schemas"
                / "runtime-conformance-plan.schema.json"
            ).read_text(encoding="utf-8")
        )
        for plan in (pending_without_package, pending_with_package, confirmed):
            self.assertEqual(
                runtime_plan.validate_runtime_plan(
                    plan,
                    contract,
                    review_package=(
                        package if plan is not pending_without_package else None
                    ),
                    review_output=(output if plan is confirmed else None),
                ),
                [],
            )
            validate_instance(plan, schema)

    def test_percent_looking_identifiers_keep_confirmed_review_paths_owned(self):
        contract = contract_with_action_ids(
            self.review_contract,
            ["a%2Fb", "a%252Fb"],
        )
        draft = complete_runtime_draft(contract)
        package = build_semantic_review_package_v21(contract)
        original_contract = copy.deepcopy(contract)
        original_draft = copy.deepcopy(draft)
        original_package = copy.deepcopy(package)
        pending = runtime_plan.materialize_runtime_plan(
            contract,
            draft,
            review_package=package,
        )
        output = reviewed_output(package)
        original_output = copy.deepcopy(output)
        try:
            confirmed = runtime_plan.materialize_runtime_plan(
                contract,
                draft,
                review_package=package,
                review_output=output,
            )
        except ValueError as error:
            self.fail(f"confirmed review field ownership is ambiguous: {error}")

        self.assertEqual(pending["review_commitments"]["completion"], "PENDING")
        self.assertEqual(
            confirmed["review_commitments"]["completion"],
            "REVIEW_OUTPUT_RECORDED",
        )
        self.assertEqual(
            {item["field_path"] for item in package["review_obligations"]},
            {
                "actions/a%252Fb/visible_error",
                "actions/a%252Fb/visible_success",
                "actions/a%25252Fb/visible_error",
                "actions/a%25252Fb/visible_success",
            },
        )
        self.assertEqual(
            runtime_plan.validate_runtime_plan(
                confirmed,
                contract,
                review_package=package,
                review_output=output,
            ),
            [],
        )
        schema = json.loads(
            (
                PACKAGE_ROOT
                / "downstream_v21"
                / "schemas"
                / "runtime-conformance-plan.schema.json"
            ).read_text(encoding="utf-8")
        )
        validate_instance(pending, schema)
        validate_instance(confirmed, schema)
        self.assertEqual(contract, original_contract)
        self.assertEqual(draft, original_draft)
        self.assertEqual(package, original_package)
        self.assertEqual(output, original_output)

    def test_schema_rejects_overencoded_unreserved_item_id_segment(self):
        plan = self.materialize()
        overencoded = copy.deepcopy(plan)
        refs = overencoded["coverage_summary"]["runtime_critical_field_refs"]
        refs[refs.index("actions/submit-request/actor")] = (
            "actions/%73ubmit-request/actor"
        )
        self.assertTrue(runtime_plan.validate_runtime_plan(overencoded, self.contract))
        schema = json.loads(
            (
                PACKAGE_ROOT
                / "downstream_v21"
                / "schemas"
                / "runtime-conformance-plan.schema.json"
            ).read_text(encoding="utf-8")
        )
        with self.assertRaises(SchemaValidationError):
            validate_instance(overencoded, schema)

    def test_validate_runtime_plan_rejects_identity_or_case_weakening(self):
        plan = self.materialize()
        weakened = copy.deepcopy(plan)
        weakened["actions"][0]["cases"][0]["result_expectation"][
            "contract_field_refs"
        ].remove("actions/submit-request/actor")
        self.assertTrue(runtime_plan.validate_runtime_plan(weakened, self.contract))
        wrong_source = copy.deepcopy(plan)
        wrong_source["source_contract"]["contract_schema_version"] = (
            "joewrks.action-conformance/2.0"
        )
        self.assertTrue(runtime_plan.validate_runtime_plan(wrong_source, self.contract))


if __name__ == "__main__":
    unittest.main()
