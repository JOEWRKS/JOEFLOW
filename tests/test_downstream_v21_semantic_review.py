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
from downstream_v21.identity import SEMANTIC_REVIEW_VERSION  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
