import copy
import importlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream.protocol import PROTOCOL_VERSION, ProtocolError  # noqa: E402
from downstream.schema_validation import validate_instance  # noqa: E402
from downstream_v2.authority import sha256_json  # noqa: E402
from downstream_v21.compiler import compile_handoff_definition_v21  # noqa: E402
from downstream_v21.runtime_plan import (  # noqa: E402
    materialize_runtime_plan,
    validate_runtime_plan,
)
from downstream_v21.semantic_review import (  # noqa: E402
    build_semantic_review_package_v21,
)
from tests.downstream_v21_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v21_compiler import complete_definition_v21  # noqa: E402
from tests.test_downstream_v21_runtime_plan import complete_runtime_draft  # noqa: E402


try:
    runtime_evidence = importlib.import_module("downstream_v21.runtime_evidence")
except ModuleNotFoundError:
    runtime_evidence = None


FROZEN_DOWNSTREAM_TREE = "b63568d8c4632b14bc806e7bff1908e94dea9669"
FROZEN_PROTOCOL_BLOB = "623f862547eb6d7ac3c87c11e8ba05ed91ed0ca5"


def execution_record(contract, test_id, *, sequence_id=None):
    return {
        "protocol_version": PROTOCOL_VERSION,
        "record_kind": "execution_evidence",
        "sequence_id": sequence_id or f"SEQ-{test_id}",
        "test_id": test_id,
        "product_slug": contract["source_authority"]["product_slug"],
        "authority": {
            "approved_revision": contract["source_authority"]["approved_revision"],
            "approved_digest": contract["source_authority"][
                "approved_definition_digest"
            ],
        },
        "contract_hash": contract["semantic_contract_hash"],
        "adapter": {"name": "task-5-fixture", "version": "1.0.0"},
        "frozen_source": {"commit": "b" * 40, "tree": "c" * 40},
        "command": {"type": "FIXTURE_COMMAND", "input": {}},
        "before": {
            "authoritative_state": {},
            "revision": 1,
            "history": [],
            "business_side_effects": [],
            "delivery_effects": [],
        },
        "result": {"status": "recorded"},
        "after": {
            "authoritative_state": {},
            "revision": 2,
            "history": [],
            "business_side_effects": [],
            "delivery_effects": [],
        },
        "deltas": {
            "history": [],
            "business_side_effects": [],
            "delivery_effects": [],
        },
    }


def planned_test_ids(plan):
    return sorted(
        case["test_id"]
        for collection in (plan["actions"], plan["lifecycles"])
        for item in collection
        for case in item["cases"]
    )


def bundle_with_recomputed_hash(bundle):
    value = copy.deepcopy(bundle)
    value.pop("bundle_hash", None)
    value["bundle_hash"] = sha256_json(value)
    return value


class RuntimeEvidenceV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        state = closed_v2_state()
        cls.contract = compile_handoff_definition_v21(
            state,
            complete_definition_v21(state),
        )["contract"]
        cls.plan = materialize_runtime_plan(
            cls.contract,
            complete_runtime_draft(cls.contract),
        )
        cls.test_ids = planned_test_ids(cls.plan)
        cls.records = [
            execution_record(cls.contract, test_id) for test_id in cls.test_ids
        ]

    def require_api(self):
        self.assertIsNotNone(runtime_evidence, "runtime evidence API is missing")

    def build(self, records=None, contract=None, plan=None):
        self.require_api()
        return runtime_evidence.build_runtime_evidence_bundle(
            copy.deepcopy(contract or self.contract),
            copy.deepcopy(plan or self.plan),
            copy.deepcopy(self.records if records is None else records),
        )

    def assert_build_error(self, code, records=None, contract=None, plan=None):
        with self.assertRaisesRegex(ValueError, code):
            self.build(records=records, contract=contract, plan=plan)

    def test_bundle_requires_execution_v1_record_before_v21_admission(self):
        self.require_api()
        invalid_record = copy.deepcopy(self.records[0])
        invalid_record["protocol_version"] = "joewrks.downstream.execution/2.0"
        invalid_record["contract_hash"] = "f" * 64
        invalid_contract = copy.deepcopy(self.contract)
        invalid_contract["semantic_contract_hash"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "unsupported protocol version"):
            runtime_evidence.build_runtime_evidence_bundle(
                invalid_contract,
                copy.deepcopy(self.plan),
                [invalid_record],
            )
        invalid_bundle = {
            "bundle_schema_version": "wrong",
            "source_semantic_contract_hash": "f" * 64,
            "source_runtime_plan_hash": "f" * 64,
            "source_approved_definition_digest": "f" * 64,
            "records": [invalid_record],
            "bundle_hash": "f" * 64,
        }
        self.assertEqual(
            runtime_evidence.validate_runtime_evidence_bundle(
                invalid_bundle,
                invalid_contract,
                self.plan,
            ),
            [
                {
                    "path": "/records/0",
                    "message": (
                        "unsupported protocol version: "
                        "'joewrks.downstream.execution/2.0'"
                    ),
                }
            ],
        )

    def test_frozen_execution_transport_tree_and_blob_remain_exact(self):
        self.assertEqual(
            subprocess.check_output(
                [
                    "git",
                    "rev-parse",
                    "HEAD:skills/joewrks-product-definition/downstream",
                ],
                cwd=ROOT,
                text=True,
            ).strip(),
            FROZEN_DOWNSTREAM_TREE,
        )
        self.assertEqual(
            subprocess.check_output(
                [
                    "git",
                    "rev-parse",
                    "HEAD:skills/joewrks-product-definition/downstream/protocol.py",
                ],
                cwd=ROOT,
                text=True,
            ).strip(),
            FROZEN_PROTOCOL_BLOB,
        )
        subprocess.run(
            [
                "git",
                "diff",
                "--quiet",
                "HEAD",
                "--",
                "skills/joewrks-product-definition/downstream",
            ],
            cwd=ROOT,
            check=True,
        )
        self.assertEqual(
            subprocess.check_output(
                [
                    "git",
                    "status",
                    "--porcelain",
                    "--untracked-files=all",
                    "--",
                    "skills/joewrks-product-definition/downstream",
                ],
                cwd=ROOT,
                text=True,
            ),
            "",
        )

    def test_record_contract_hash_must_equal_semantic_contract_hash(self):
        records = copy.deepcopy(self.records)
        records[0]["contract_hash"] = "f" * 64
        self.assert_build_error("RECORD_CONTRACT_HASH_MISMATCH", records=records)

    def test_record_approved_digest_and_revision_must_match_source_authority(self):
        for field, wrong_value, code in (
            ("approved_digest", "f" * 64, "RECORD_APPROVED_DIGEST_MISMATCH"),
            ("approved_revision", 999, "RECORD_APPROVED_REVISION_MISMATCH"),
        ):
            with self.subTest(field=field):
                records = copy.deepcopy(self.records)
                records[0]["authority"][field] = wrong_value
                self.assert_build_error(code, records=records)

    def test_record_product_slug_must_match_contract(self):
        records = copy.deepcopy(self.records)
        records[0]["product_slug"] = "different-product"
        self.assert_build_error("RECORD_PRODUCT_SLUG_MISMATCH", records=records)

    def test_record_test_id_must_exist_in_runtime_plan(self):
        records = copy.deepcopy(self.records)
        records[0]["test_id"] = "TEST-UNPLANNED"
        self.assert_build_error("UNEXPECTED_RUNTIME_TEST_ID", records=records)

    def test_each_planned_test_id_has_exactly_one_record(self):
        duplicates = copy.deepcopy(self.records)
        duplicates.append(copy.deepcopy(duplicates[0]))
        duplicates[-1]["sequence_id"] = "SEQ-DUPLICATE"
        self.assert_build_error("DUPLICATE_RUNTIME_TEST_ID", records=duplicates)

    def test_missing_planned_record_is_incomplete(self):
        bundle = self.build()
        missing_id = bundle["records"].pop()["test_id"]
        bundle = bundle_with_recomputed_hash(bundle)
        inventory = runtime_evidence.runtime_evidence_inventory(bundle, self.plan)
        self.assertEqual(inventory["required_test_ids"], self.test_ids)
        self.assertEqual(inventory["missing_test_ids"], [missing_id])
        self.assertEqual(inventory["unexpected_test_ids"], [])
        self.assertEqual(inventory["coverage_status"], "INCOMPLETE")
        self.assertTrue(
            any(
                error["path"] == "/records"
                and "MISSING_RUNTIME_TEST_ID" in error["message"]
                for error in runtime_evidence.validate_runtime_evidence_bundle(
                    bundle,
                    self.contract,
                    self.plan,
                )
            )
        )

    def test_inventory_requires_execution_v1_record_before_reading_test_id(self):
        bundle = self.build()
        del bundle["records"][0]["before"]["delivery_effects"]
        original_bundle = copy.deepcopy(bundle)
        original_plan = copy.deepcopy(self.plan)
        with self.assertRaisesRegex(
            ProtocolError,
            "before snapshot is missing: delivery_effects",
        ):
            runtime_evidence.runtime_evidence_inventory(bundle, self.plan)
        self.assertEqual(bundle, original_bundle)
        self.assertEqual(self.plan, original_plan)

    def test_unexpected_test_id_is_reported(self):
        bundle = self.build()
        replaced_id = bundle["records"][0]["test_id"]
        bundle["records"][0]["test_id"] = "TEST-UNPLANNED"
        bundle = bundle_with_recomputed_hash(bundle)
        inventory = runtime_evidence.runtime_evidence_inventory(bundle, self.plan)
        self.assertEqual(inventory["missing_test_ids"], [replaced_id])
        self.assertEqual(inventory["unexpected_test_ids"], ["TEST-UNPLANNED"])
        self.assertEqual(inventory["coverage_status"], "INCOMPLETE")
        errors = runtime_evidence.validate_runtime_evidence_bundle(
            bundle,
            self.contract,
            self.plan,
        )
        self.assertTrue(
            any("UNEXPECTED_RUNTIME_TEST_ID" in error["message"] for error in errors)
        )

    def test_runtime_plan_hash_change_invalidates_old_bundle(self):
        bundle = self.build()
        changed_draft = complete_runtime_draft(self.contract)
        changed_draft["actions"][0]["cases"][0]["result_expectation"][
            "result_class"
        ] = "REJECTED"
        changed_plan = materialize_runtime_plan(self.contract, changed_draft)
        self.assertNotEqual(self.plan["plan_hash"], changed_plan["plan_hash"])
        errors = runtime_evidence.validate_runtime_evidence_bundle(
            bundle,
            self.contract,
            changed_plan,
        )
        self.assertTrue(
            any(
                error == {
                    "path": "/source_runtime_plan_hash",
                    "message": "SOURCE_RUNTIME_PLAN_HASH_MISMATCH",
                }
                for error in errors
            )
        )

    def test_bundle_build_and_validation_reject_self_hashed_noncanonical_runtime_plans(self):
        bundle = self.build()

        def wrong_schema(plan):
            plan["plan_schema_version"] = "joewrks.runtime-conformance-plan/9.9"

        def wrong_planner(plan):
            plan["planner"]["id"] = "shadow-planner"

        def drifted_coverage(plan):
            plan["coverage_summary"]["status"] = "INCOMPLETE"

        def drifted_assertion(plan):
            plan["actions"][0]["cases"][0]["evidence_assertions"].append(
                {
                    "type": "path_present",
                    "pointer": "/result/shadow",
                    "contract_field_refs": [
                        "actions/submit-request/authentication"
                    ],
                }
            )

        def product_literal(plan):
            plan["actions"][0]["cases"][0]["expected_value"] = "APPROVED"

        def extra_shadow_policy(plan):
            plan["shadow_policy"] = {"permission": "owner-only"}

        for name, mutation in (
            ("schema", wrong_schema),
            ("identity", wrong_planner),
            ("coverage", drifted_coverage),
            ("assertion", drifted_assertion),
            ("product_literal", product_literal),
            ("extra_field", extra_shadow_policy),
        ):
            with self.subTest(name=name):
                changed = copy.deepcopy(self.plan)
                mutation(changed)
                changed["plan_hash"] = sha256_json(
                    {
                        key: value
                        for key, value in changed.items()
                        if key != "plan_hash"
                    }
                )
                self.assertTrue(validate_runtime_plan(changed, self.contract))
                original_contract = copy.deepcopy(self.contract)
                original_plan = copy.deepcopy(changed)
                original_records = copy.deepcopy(self.records)
                self.assert_build_error("INVALID_RUNTIME_PLAN", plan=changed)
                self.assertEqual(
                    runtime_evidence.validate_runtime_evidence_bundle(
                        bundle,
                        self.contract,
                        changed,
                    ),
                    [{"path": "/plan", "message": "INVALID_RUNTIME_PLAN"}],
                )
                self.assertEqual(self.contract, original_contract)
                self.assertEqual(changed, original_plan)
                self.assertEqual(self.records, original_records)

    def test_bundle_admits_canonical_plan_with_valid_review_commitments(self):
        state = closed_v2_state()
        contract = compile_handoff_definition_v21(
            state,
            complete_definition_v21(state, review=True),
        )["contract"]
        review_package = build_semantic_review_package_v21(contract)
        plan = materialize_runtime_plan(
            contract,
            complete_runtime_draft(contract),
            review_package=review_package,
        )
        records = [
            execution_record(contract, test_id)
            for test_id in planned_test_ids(plan)
        ]
        original_contract = copy.deepcopy(contract)
        original_plan = copy.deepcopy(plan)
        original_records = copy.deepcopy(records)

        bundle = runtime_evidence.build_runtime_evidence_bundle(
            contract,
            plan,
            records,
        )

        self.assertEqual(
            runtime_evidence.validate_runtime_evidence_bundle(
                bundle,
                contract,
                plan,
            ),
            [],
        )
        self.assertEqual(
            plan["review_commitments"],
            {
                "package_hash": review_package["package_hash"],
                "output_hash": None,
                "completion": "PENDING",
                "reliability_status": "NOT_MEASURED",
            },
        )
        self.assertEqual(contract, original_contract)
        self.assertEqual(plan, original_plan)
        self.assertEqual(records, original_records)

    def test_bundle_hash_is_deterministic(self):
        original_records = copy.deepcopy(self.records)
        first = self.build(records=self.records)
        second = self.build(records=list(reversed(self.records)))
        self.assertEqual(first, second)
        self.assertEqual(self.records, original_records)
        self.assertEqual(
            {
                "source_semantic_contract_hash": first[
                    "source_semantic_contract_hash"
                ],
                "source_runtime_plan_hash": first["source_runtime_plan_hash"],
                "source_approved_definition_digest": first[
                    "source_approved_definition_digest"
                ],
            },
            {
                "source_semantic_contract_hash": self.contract[
                    "semantic_contract_hash"
                ],
                "source_runtime_plan_hash": self.plan["plan_hash"],
                "source_approved_definition_digest": self.contract[
                    "source_authority"
                ]["approved_definition_digest"],
            },
        )
        self.assertEqual(
            first["bundle_hash"],
            sha256_json(
                {
                    key: value
                    for key, value in first.items()
                    if key != "bundle_hash"
                }
            ),
        )
        self.assertEqual(
            first["records"],
            sorted(original_records, key=lambda record: record["test_id"]),
        )
        self.assertEqual(
            runtime_evidence.validate_runtime_evidence_bundle(
                first,
                self.contract,
                self.plan,
            ),
            [],
        )
        changed_digest = copy.deepcopy(first)
        changed_digest["source_approved_definition_digest"] = "f" * 64
        changed_digest = bundle_with_recomputed_hash(changed_digest)
        self.assertIn(
            {
                "path": "/source_approved_definition_digest",
                "message": "SOURCE_APPROVED_DEFINITION_DIGEST_MISMATCH",
            },
            runtime_evidence.validate_runtime_evidence_bundle(
                changed_digest,
                self.contract,
                self.plan,
            ),
        )

    def test_changing_only_bundle_hash_reports_invalid_runtime_evidence_bundle_hash(self):
        bundle = self.build()
        original = copy.deepcopy(bundle)
        bundle["bundle_hash"] = (
            "0" * 64 if bundle["bundle_hash"] != "0" * 64 else "1" * 64
        )

        self.assertEqual(
            runtime_evidence.validate_runtime_evidence_bundle(
                bundle,
                self.contract,
                self.plan,
            ),
            [
                {
                    "path": "/bundle_hash",
                    "message": "INVALID_RUNTIME_EVIDENCE_BUNDLE_HASH",
                }
            ],
        )
        self.assertEqual(
            {key: value for key, value in bundle.items() if key != "bundle_hash"},
            {key: value for key, value in original.items() if key != "bundle_hash"},
        )

    def test_bundle_matches_published_schema_without_redefining_record_shape(self):
        bundle = self.build()
        schema = json.loads(
            (
                PACKAGE_ROOT
                / "downstream_v21"
                / "schemas"
                / "runtime-evidence-bundle.schema.json"
            ).read_text(encoding="utf-8")
        )
        validate_instance(bundle, schema)
        self.assertEqual(schema["properties"]["records"]["items"], {"type": "object"})


if __name__ == "__main__":
    unittest.main()
