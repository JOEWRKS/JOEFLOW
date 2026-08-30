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

from downstream.schema_validation import (  # noqa: E402
    SchemaValidationError,
    validate_instance,
)
from downstream_v2.authority import sha256_json  # noqa: E402
from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from downstream_v2.semantic_review import (  # noqa: E402
    build_semantic_review_package as build_semantic_review_package_v20,
    validate_semantic_review_output as validate_semantic_review_output_v20,
)
from downstream_v2.semantic_review.package import (  # noqa: E402
    validate_semantic_review_package as validate_semantic_review_package_v20,
)
from downstream_v21.compiler import compile_handoff_definition_v21  # noqa: E402
from downstream_v21.contracts import (  # noqa: E402
    artifact_hash_v21,
    semantic_contract_hash_v21,
    validate_action_contract_v21,
)
from downstream_v21.identity import SEMANTIC_REVIEW_VERSION  # noqa: E402
from downstream_v21.field_refs import canonical_field_ref  # noqa: E402
from downstream_v21.semantic_review import (  # noqa: E402
    RELIABILITY_STATUS,
    build_semantic_review_package_v21,
    review_results_to_reentry_events_v21,
    semantic_review_completion_v21,
    validate_semantic_review_output_v21,
)
from downstream_v21.semantic_review.package import (  # noqa: E402
    validate_semantic_review_package_v21,
)
from tests.downstream_v21_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v2_compiler import complete_definition  # noqa: E402
from tests.test_downstream_v21_compiler import complete_definition_v21  # noqa: E402


INPUT_SCHEMA = json.loads(
    (
        PACKAGE_ROOT
        / "downstream_v21"
        / "schemas"
        / "semantic-review-input-v21.schema.json"
    ).read_text(encoding="utf-8")
)
OUTPUT_SCHEMA = json.loads(
    (
        PACKAGE_ROOT
        / "downstream_v21"
        / "schemas"
        / "semantic-review-output-v21.schema.json"
    ).read_text(encoding="utf-8")
)
REENTRY_SCHEMA = json.loads(
    (
        PACKAGE_ROOT
        / "downstream_v2"
        / "schemas"
        / "reentry-event.schema.json"
    ).read_text(encoding="utf-8")
)


def reviewed_output(package, verdict="CONFIRMED_INTERPRETATION"):
    output = {
        "review_schema_version": SEMANTIC_REVIEW_VERSION,
        "input_package_hash": package["package_hash"],
        "reliability_status": RELIABILITY_STATUS,
        "results": [
            {
                "obligation_id": obligation["obligation_id"],
                "verdict": verdict,
                "reviewed_value_sha256": obligation["proposed_value_sha256"],
                "rationale": "The interpretation was reviewed without changing its value.",
            }
            for obligation in package["review_obligations"]
        ],
    }
    output["output_hash"] = sha256_json(output)
    return output


def rehash(value, hash_key):
    value.pop(hash_key, None)
    value[hash_key] = sha256_json(value)


def contract_with_action_ids(contract, action_ids):
    rebound = copy.deepcopy(contract)
    original_id = rebound["actions"][0]["action_id"]
    template = rebound["actions"][0]
    rebound["actions"] = []
    for action_id in sorted(action_ids):
        action = copy.deepcopy(template)
        action["action_id"] = action_id
        rebound["actions"].append(action)
    debt = rebound["semantic_debt"]
    for prefix in (
        "direct_authority",
        "machine_derived",
        "review_required",
    ):
        original_paths = debt[f"{prefix}_fields"]
        action_paths = [
            path
            for path in original_paths
            if path.startswith(f"actions/{original_id}/")
        ]
        lifecycle_paths = [
            path for path in original_paths if not path.startswith("actions/")
        ]
        rebound_paths = lifecycle_paths + [
            canonical_field_ref("actions", action_id, path.rsplit("/", 1)[1])
            for action_id in action_ids
            for path in action_paths
        ]
        debt[f"{prefix}_fields"] = sorted(rebound_paths)
        debt[f"{prefix}_count"] = len(rebound_paths)
    rebound["semantic_contract_hash"] = semantic_contract_hash_v21(rebound)
    rebound["artifact_hash"] = artifact_hash_v21(rebound)
    if validate_action_contract_v21(rebound):
        raise AssertionError("test helper produced an invalid action-conformance/2.1")
    return rebound


class SemanticReviewV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = closed_v2_state()
        cls.machine_contract = compile_handoff_definition_v21(
            cls.state,
            complete_definition_v21(cls.state),
        )["contract"]
        cls.review_contract = compile_handoff_definition_v21(
            cls.state,
            complete_definition_v21(cls.state, review=True),
        )["contract"]
        cls.review_package = build_semantic_review_package_v21(cls.review_contract)
        cls.v20_contract = compile_handoff_definition(
            cls.state,
            complete_definition(cls.state, review=True),
        )["contract"]
        cls.v20_package = build_semantic_review_package_v20(cls.v20_contract)

    def package(self):
        self.assertIsNotNone(self.review_package)
        return copy.deepcopy(self.review_package)

    def test_review_21_accepts_only_action_contract_21(self):
        self.assertIsNone(build_semantic_review_package_v21(self.machine_contract))
        self.assertEqual(
            self.package()["source_semantic_contract_hash"],
            self.review_contract["semantic_contract_hash"],
        )
        with self.assertRaisesRegex(ValueError, "INVALID_ACTION_CONTRACT_V21"):
            build_semantic_review_package_v21(self.v20_contract)

    def test_review_20_package_does_not_validate_as_21(self):
        package_v21 = self.package()
        self.assertTrue(validate_semantic_review_package_v21(self.v20_package))
        self.assertTrue(validate_semantic_review_package_v20(package_v21))

        output_v21 = reviewed_output(package_v21)
        output_v20 = reviewed_output(self.v20_package)
        output_v20["review_schema_version"] = "joewrks.semantic-review/2.0"
        rehash(output_v20, "output_hash")
        self.assertTrue(validate_semantic_review_output_v21(self.v20_package, output_v20))
        self.assertTrue(validate_semantic_review_output_v20(package_v21, output_v21))

    def test_review_21_packages_only_review_required_fields(self):
        package = self.package()
        paths = [item["field_path"] for item in package["review_obligations"]]
        self.assertEqual(
            paths,
            self.review_contract["semantic_debt"]["review_required_fields"],
        )
        self.assertEqual(paths, [
            "actions/submit-request/visible_error",
            "actions/submit-request/visible_success",
        ])
        for removed in ("default_result", "result_expectations", "test_obligations"):
            self.assertFalse(any(path.endswith(f"/{removed}") for path in paths))

        forged = copy.deepcopy(package)
        forged["review_obligations"][0]["field_path"] = (
            "actions/submit-request/default_result"
        )
        rehash(forged, "package_hash")
        self.assertTrue(validate_semantic_review_package_v21(forged))

    def test_review_21_canonicalizes_paths_for_valid_special_action_id(self):
        contract = contract_with_action_ids(
            self.review_contract,
            ["submit/request with space"],
        )
        original_contract = copy.deepcopy(contract)
        try:
            package = build_semantic_review_package_v21(contract)
        except ValueError as error:
            self.fail(f"valid action ID cannot cross semantic review: {error}")
        self.assertEqual(contract, original_contract)
        self.assertEqual(validate_semantic_review_package_v21(package), [])
        validate_instance(package, INPUT_SCHEMA)
        self.assertEqual(
            [item["field_path"] for item in package["review_obligations"]],
            [
                "actions/submit%2Frequest%20with%20space/visible_error",
                "actions/submit%2Frequest%20with%20space/visible_success",
            ],
        )
        overencoded = copy.deepcopy(package)
        overencoded["review_obligations"][0]["field_path"] = (
            "actions/%73ubmit-request/visible_error"
        )
        with self.assertRaises(SchemaValidationError):
            validate_instance(overencoded, INPUT_SCHEMA)

    def test_review_21_schema_rejects_overencoded_tilde_identifier(self):
        contract = contract_with_action_ids(
            self.review_contract,
            ["~submit-request"],
        )
        package = build_semantic_review_package_v21(contract)
        overencoded = copy.deepcopy(package)
        obligation = overencoded["review_obligations"][0]
        self.assertEqual(
            obligation["field_path"],
            "actions/~submit-request/visible_error",
        )
        obligation["field_path"] = "actions/%7Esubmit-request/visible_error"
        identity = {
            "field_path": obligation["field_path"],
            "proposed_value_sha256": obligation["proposed_value_sha256"],
            "source_seed_refs": obligation["source_seed_refs"],
        }
        obligation["obligation_id"] = "REVIEW-" + sha256_json(identity)[:24]
        rehash(overencoded, "package_hash")
        errors = validate_semantic_review_package_v21(overencoded)
        self.assertTrue(
            any(error["path"].endswith("/field_path") for error in errors)
        )
        with self.assertRaises(SchemaValidationError):
            validate_instance(overencoded, INPUT_SCHEMA)

    def test_review_21_keeps_exact_seed_provenance_and_value_hash(self):
        package = self.package()
        validate_instance(package, INPUT_SCHEMA)
        self.assertEqual(validate_semantic_review_package_v21(package), [])
        self.assertEqual(
            package["source_definition_digest"],
            self.review_contract["source_authority"]["approved_definition_digest"],
        )
        self.assertEqual(
            package["responsibility_profile"],
            self.review_contract["responsibility_profile"],
        )
        inventory = {
            seed["seed_key"]: seed
            for seed in self.review_contract["source_seed_inventory"]
        }
        for obligation in package["review_obligations"]:
            self.assertEqual(
                obligation["source_seeds"],
                [inventory[ref] for ref in obligation["source_seed_refs"]],
            )
            self.assertEqual(
                obligation["proposed_value_sha256"],
                sha256_json(obligation["proposed_value"]),
            )

    def test_review_21_output_cannot_change_proposed_value(self):
        package = self.package()
        original_contract = copy.deepcopy(self.review_contract)
        output = reviewed_output(package)
        output["results"][0]["replacement_value"] = "different product meaning"
        rehash(output, "output_hash")
        self.assertTrue(validate_semantic_review_output_v21(package, output))

        wrong_hash = reviewed_output(package)
        wrong_hash["results"][0]["reviewed_value_sha256"] = "0" * 64
        rehash(wrong_hash, "output_hash")
        self.assertTrue(validate_semantic_review_output_v21(package, wrong_hash))
        self.assertEqual(self.review_contract, original_contract)

    def test_review_21_reliability_is_always_not_measured(self):
        package = self.package()
        self.assertEqual(RELIABILITY_STATUS, "NOT_MEASURED")
        self.assertEqual(package["reliability_status"], "NOT_MEASURED")
        for invalid in ("PASS", "RELIABLE", "CALIBRATED"):
            with self.subTest(invalid=invalid):
                changed_package = copy.deepcopy(package)
                changed_package["reliability_status"] = invalid
                rehash(changed_package, "package_hash")
                self.assertTrue(validate_semantic_review_package_v21(changed_package))

                output = reviewed_output(package)
                output["reliability_status"] = invalid
                rehash(output, "output_hash")
                self.assertTrue(validate_semantic_review_output_v21(package, output))

    def test_review_21_completion_is_structural_not_reliability(self):
        package = self.package()
        self.assertEqual(semantic_review_completion_v21(None, None), "NOT_REQUIRED")
        self.assertEqual(
            semantic_review_completion_v21(package, None),
            "PENDING",
        )
        confirmed = reviewed_output(package)
        validate_instance(confirmed, OUTPUT_SCHEMA)
        self.assertEqual(validate_semantic_review_output_v21(package, confirmed), [])
        self.assertEqual(
            semantic_review_completion_v21(package, confirmed),
            "REVIEW_OUTPUT_RECORDED",
        )
        rejected = reviewed_output(package, verdict="REJECTED_INTERPRETATION")
        self.assertEqual(
            semantic_review_completion_v21(package, rejected),
            "REENTRY_REQUIRED",
        )

    def test_review_21_nonconfirmed_verdicts_route_read_only_reentry_data(self):
        package = self.package()
        original_contract = copy.deepcopy(self.review_contract)
        original_package = copy.deepcopy(package)
        for verdict, event_type in (
            ("REJECTED_INTERPRETATION", "CONTRACT_CONFLICT"),
            ("UPSTREAM_AUTHORITY_GAP", "AMBIGUITY_FOUND"),
        ):
            with self.subTest(verdict=verdict):
                output = reviewed_output(package, verdict=verdict)
                original_output = copy.deepcopy(output)
                events = review_results_to_reentry_events_v21(
                    self.review_contract,
                    package,
                    output,
                )
                self.assertEqual(len(events), 2)
                for event in events:
                    self.assertEqual(event["event_type"], event_type)
                    self.assertEqual(
                        event["source_contract_hash"],
                        self.review_contract["semantic_contract_hash"],
                    )
                    self.assertEqual(
                        event["source_definition_digest"],
                        self.review_contract["source_authority"][
                            "approved_definition_digest"
                        ],
                    )
                    self.assertEqual(
                        event["affected_action_ids"],
                        ["submit-request"],
                    )
                    self.assertEqual(event["affected_lifecycle_ids"], [])
                    self.assertEqual(
                        event["halt_scope"],
                        {
                            "mode": "AFFECTED_ONLY",
                            "action_ids": ["submit-request"],
                            "lifecycle_ids": [],
                        },
                    )
                    self.assertEqual(
                        event["recommended_action"],
                        "REENTER_PRODUCT_DEFINITION",
                    )
                self.assertEqual(output, original_output)
        self.assertEqual(self.review_contract, original_contract)
        self.assertEqual(package, original_package)

    def test_special_ids_route_nonconfirmed_review_to_raw_owner_reentry(self):
        for action_ids in (
            ["submit/request with space"],
            ["a%2Fb", "a%252Fb"],
        ):
            with self.subTest(action_ids=action_ids):
                contract = contract_with_action_ids(
                    self.review_contract,
                    action_ids,
                )
                package = build_semantic_review_package_v21(contract)
                original_contract = copy.deepcopy(contract)
                original_package = copy.deepcopy(package)
                for verdict, event_type in (
                    ("REJECTED_INTERPRETATION", "CONTRACT_CONFLICT"),
                    ("UPSTREAM_AUTHORITY_GAP", "AMBIGUITY_FOUND"),
                ):
                    with self.subTest(verdict=verdict):
                        output = reviewed_output(package, verdict=verdict)
                        original_output = copy.deepcopy(output)
                        try:
                            events = review_results_to_reentry_events_v21(
                                contract,
                                package,
                                output,
                            )
                        except (StopIteration, ValueError) as error:
                            self.fail(
                                "valid special-ID review could not route re-entry: "
                                f"{type(error).__name__}: {error}"
                            )
                        self.assertEqual(len(events), 2 * len(action_ids))
                        self.assertEqual(
                            {
                                action_id: sum(
                                    event["affected_action_ids"] == [action_id]
                                    for event in events
                                )
                                for action_id in action_ids
                            },
                            {action_id: 2 for action_id in action_ids},
                        )
                        for event in events:
                            validate_instance(event, REENTRY_SCHEMA)
                            self.assertEqual(event["event_type"], event_type)
                            self.assertEqual(event["affected_lifecycle_ids"], [])
                            self.assertEqual(
                                event["halt_scope"],
                                {
                                    "mode": "AFFECTED_ONLY",
                                    "action_ids": event["affected_action_ids"],
                                    "lifecycle_ids": [],
                                },
                            )
                            self.assertIn(
                                event["affected_action_ids"][0],
                                action_ids,
                            )
                            raw_owner = event["affected_action_ids"][0]
                            self.assertIn(
                                raw_owner,
                                event["candidate_unknown"]["affected_ids"],
                            )
                            self.assertIn(
                                raw_owner,
                                event["candidate_unknown"]["suggested_question"],
                            )
                            event_content = {
                                key: value
                                for key, value in event.items()
                                if key != "event_id"
                            }
                            self.assertEqual(
                                event["event_id"],
                                "REENTRY-" + sha256_json(event_content)[:24],
                            )
                        self.assertEqual(output, original_output)
                self.assertEqual(contract, original_contract)
                self.assertEqual(package, original_package)


if __name__ == "__main__":
    unittest.main()
