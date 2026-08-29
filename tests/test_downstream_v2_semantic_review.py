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

from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from downstream_v2.semantic_review import (  # noqa: E402
    RELIABILITY_STATUS,
    SEMANTIC_REVIEW_VERSION,
    build_semantic_review_package,
    review_results_to_reentry_events,
    semantic_assurance_result,
    validate_semantic_review_output,
)
from downstream_v2.semantic_review.package import validate_semantic_review_package  # noqa: E402
from tests.downstream_v2_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v2_compiler import complete_definition  # noqa: E402


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def output_hash(output):
    content = copy.deepcopy(output)
    content.pop("output_hash", None)
    return hashlib.sha256(canonical_bytes(content)).hexdigest()


class SemanticReviewV2Tests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.machine_contract = compile_handoff_definition(
            self.state, complete_definition(self.state)
        )["contract"]
        self.review_contract = compile_handoff_definition(
            self.state, complete_definition(self.state, review=True)
        )["contract"]

    def package(self):
        package = build_semantic_review_package(self.review_contract)
        self.assertIsNotNone(package)
        return package

    def confirmed_output(self, package=None):
        package = self.package() if package is None else package
        output = {
            "review_schema_version": SEMANTIC_REVIEW_VERSION,
            "input_package_hash": package["package_hash"],
            "reliability_status": RELIABILITY_STATUS,
            "results": [
                {
                    "obligation_id": obligation["obligation_id"],
                    "verdict": "CONFIRMED_INTERPRETATION",
                    "reviewed_value_sha256": obligation["proposed_value_sha256"],
                    "rationale": "The supplied interpretation is recorded without changing its value.",
                }
                for obligation in package["review_obligations"]
            ],
        }
        output["output_hash"] = output_hash(output)
        return output

    def test_machine_only_contract_produces_no_review_package(self):
        self.assertIsNone(build_semantic_review_package(self.machine_contract))
        self.assertEqual(
            semantic_assurance_result(self.machine_contract, None, None),
            {"review_completion": "NOT_REQUIRED"},
        )

    def test_review_required_contract_package_contains_exactly_review_fields(self):
        package = self.package()
        self.assertEqual(package["review_schema_version"], SEMANTIC_REVIEW_VERSION)
        self.assertEqual(package["reliability_status"], "NOT_MEASURED")
        self.assertEqual(
            [item["field_path"] for item in package["review_obligations"]],
            self.review_contract["semantic_debt"]["review_required_fields"],
        )
        self.assertEqual(len(package["review_obligations"]), 2)

    def test_package_is_byte_and_hash_deterministic(self):
        first = self.package()
        second = build_semantic_review_package(copy.deepcopy(self.review_contract))
        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        content = copy.deepcopy(first)
        content.pop("package_hash")
        self.assertEqual(first["package_hash"], hashlib.sha256(canonical_bytes(content)).hexdigest())

    def test_package_binds_contract_definition_digest_and_exact_source_seeds(self):
        package = self.package()
        self.assertEqual(
            package["source_semantic_contract_hash"],
            self.review_contract["semantic_contract_hash"],
        )
        self.assertEqual(
            package["source_definition_digest"],
            self.review_contract["source_authority"]["approved_definition_digest"],
        )
        self.assertEqual(package["responsibility_profile"], self.review_contract["responsibility_profile"])
        inventory = {item["seed_key"]: item for item in self.review_contract["source_seed_inventory"]}
        for obligation in package["review_obligations"]:
            self.assertEqual(
                obligation["source_seeds"],
                [inventory[ref] for ref in obligation["source_seed_refs"]],
            )

    def test_output_must_cover_every_obligation_exactly_once(self):
        package = self.package()
        incomplete = self.confirmed_output(package)
        incomplete["results"] = incomplete["results"][:-1]
        incomplete["output_hash"] = output_hash(incomplete)
        self.assertTrue(validate_semantic_review_output(package, incomplete))
        duplicate = self.confirmed_output(package)
        duplicate["results"].append(copy.deepcopy(duplicate["results"][0]))
        duplicate["output_hash"] = output_hash(duplicate)
        self.assertTrue(validate_semantic_review_output(package, duplicate))

    def test_output_reviewed_value_hash_must_match_proposed_value_hash(self):
        output = self.confirmed_output()
        output["results"][0]["reviewed_value_sha256"] = "0" * 64
        output["output_hash"] = output_hash(output)
        self.assertTrue(validate_semantic_review_output(self.package(), output))

    def test_output_cannot_replace_proposed_value(self):
        output = self.confirmed_output()
        output["results"][0]["replacement_value"] = "different"
        output["output_hash"] = output_hash(output)
        self.assertTrue(validate_semantic_review_output(self.package(), output))

    def test_confirmed_output_records_completion_without_reliability(self):
        package = self.package()
        output = self.confirmed_output(package)
        self.assertEqual(validate_semantic_review_output(package, output), [])
        self.assertEqual(
            semantic_assurance_result(self.review_contract, package, output),
            {"review_completion": "REVIEW_OUTPUT_RECORDED", "reliability_status": "NOT_MEASURED"},
        )

    def test_rejected_interpretation_creates_contract_conflict_reentry_data(self):
        package = self.package()
        output = self.confirmed_output(package)
        output["results"][0]["verdict"] = "REJECTED_INTERPRETATION"
        output["results"][0]["rationale"] = "The interpretation conflicts with the approved source material."
        output["output_hash"] = output_hash(output)
        events = review_results_to_reentry_events(self.review_contract, package, output)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "CONTRACT_CONFLICT")
        self.assertEqual(
            semantic_assurance_result(self.review_contract, package, output)["review_completion"],
            "REENTRY_REQUIRED",
        )

    def test_upstream_authority_gap_creates_ambiguity_reentry_data(self):
        package = self.package()
        output = self.confirmed_output(package)
        output["results"][0]["verdict"] = "UPSTREAM_AUTHORITY_GAP"
        output["results"][0]["rationale"] = "Approved Product Definition authority does not resolve this interpretation."
        output["output_hash"] = output_hash(output)
        events = review_results_to_reentry_events(self.review_contract, package, output)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "AMBIGUITY_FOUND")

    def test_v1_calibration_is_never_imported_as_reliability_evidence(self):
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((PACKAGE_ROOT / "downstream_v2" / "semantic_review").glob("*.py"))
        )
        self.assertNotIn("semantic_review_v1", source)
        self.assertNotIn("calibration", source.lower())

    def test_m5_reliability_rejects_pass_reliable_and_calibrated(self):
        package = self.package()
        for invalid in ("PASS", "RELIABLE", "CALIBRATED"):
            with self.subTest(invalid=invalid):
                output = self.confirmed_output(package)
                output["reliability_status"] = invalid
                output["output_hash"] = output_hash(output)
                self.assertTrue(validate_semantic_review_output(package, output))

    def test_rehashed_forged_package_is_rejected_by_both_public_validators(self):
        forged = self.package()
        forged["responsibility_profile"] = {}
        forged["review_obligations"][0]["obligation_id"] = "REVIEW-" + "0" * 24
        forged["review_obligations"][0]["source_seeds"] = [{
            "seed_key": forged["review_obligations"][0]["source_seed_refs"][0],
        }]
        content = copy.deepcopy(forged)
        content.pop("package_hash")
        forged["package_hash"] = hashlib.sha256(canonical_bytes(content)).hexdigest()
        output = self.confirmed_output(forged)
        self.assertTrue(validate_semantic_review_package(forged))
        self.assertTrue(validate_semantic_review_output(forged, output))

    def test_public_validators_return_errors_for_non_object_inputs(self):
        for package in (None, [], "package", 42):
            with self.subTest(package=package):
                errors = validate_semantic_review_package(package)
                self.assertIsInstance(errors, list)
                self.assertTrue(errors)
                for output in (None, [], "output", 42, {}):
                    with self.subTest(output=output):
                        combined = validate_semantic_review_output(package, output)
                        self.assertIsInstance(combined, list)
                        self.assertTrue(combined)


if __name__ == "__main__":
    unittest.main()
