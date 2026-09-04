import dataclasses
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

try:
    from reviewer_runner.identity import (
        BackendIdentity,
        InputCommitment,
        ResponseIdentity,
        RunIdentity,
        RunnerIdentityError,
        RunnerState,
        build_runner_receipt,
        canonical_json_bytes,
        receipt_content,
        receipt_document,
        sha256_bytes,
        validate_receipt_document,
        validate_runner_receipt,
    )
except ModuleNotFoundError:
    _IDENTITY_IMPORT_ERROR = True
else:
    _IDENTITY_IMPORT_ERROR = False


def _digest(label: str) -> str:
    return sha256_bytes(label.encode("utf-8"))


def valid_receipt_parts() -> dict:
    if _IDENTITY_IMPORT_ERROR:
        raise AssertionError("reviewer_runner.identity must implement the receipt contract")
    run_identity = RunIdentity(
        semantic_review_contract_version="joewrks.semantic-review/1.0",
        package_schema_version="joewrks.semantic-review-input/1.0",
        package_digest=_digest("package"),
        source_action_contract_hash=_digest("action-contract"),
        source_definition_digest=_digest("definition"),
        reviewer_id="reviewer-001",
        review_run_id="run-001",
        context_id="context-001",
        cohort_id=None,
        case_id=None,
    )
    backend_identity = BackendIdentity(
        backend_kind="STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
        adapter_id="external-inference-adapter",
        adapter_version="1.0.0",
        endpoint_identity="https://inference.example.invalid/v1",
        deployment_identity="reviewer-production",
        model_revision_identity="example-model@2026-09-03",
        model_identity_stability="IMMUTABLE",
        inference_settings_sha256=_digest("settings"),
        retention_policy_identity="no-retention",
        privacy_policy_identity="privacy-v1",
        is_test_double=False,
    )
    inventory = (
        InputCommitment("reviewer_brief", "text/markdown", 13, _digest("brief")),
        InputCommitment("review_package", "application/json", 14, _digest("package")),
        InputCommitment("run_envelope", "application/json", 15, _digest("envelope")),
        InputCommitment("output_schema", "application/schema+json", 16, _digest("schema")),
    )
    response_identity = {
        "provider_request_id": "provider-request-001",
        "request_sha256": _digest("request"),
        "reviewer_id": run_identity.reviewer_id,
        "review_run_id": run_identity.review_run_id,
        "context_id": run_identity.context_id,
        "backend_identity_sha256": sha256_bytes(canonical_json_bytes(dataclasses.asdict(backend_identity))),
        "response_count": 1,
        "raw_response_byte_count": 17,
        "raw_response_sha256": _digest("response"),
        "parsed_output_sha256": _digest("output"),
    }
    return {
        "state": RunnerState.REVIEW_COMPLETED,
        "run_identity": run_identity,
        "backend_identity": backend_identity,
        "permitted_input_inventory": inventory,
        "request_sha256": response_identity["request_sha256"],
        "capability_preflight_sha256": _digest("preflight"),
        "isolation_receipt_sha256": _digest("isolation"),
        "response_identity": response_identity,
    }


class ReviewerRunnerIdentityTests(unittest.TestCase):
    def setUp(self):
        if _IDENTITY_IMPORT_ERROR:
            self.fail("reviewer_runner.identity must implement the receipt contract")

    def test_receipt_is_canonical_and_deterministic(self):
        first = build_runner_receipt(**valid_receipt_parts())
        second = build_runner_receipt(**valid_receipt_parts())
        self.assertEqual(receipt_document(first), receipt_document(second))
        self.assertEqual(
            first.receipt_sha256,
            sha256_bytes(canonical_json_bytes(receipt_content(first))),
        )

    def test_receipt_schema_rejects_missing_or_extra_field(self):
        document = receipt_document(build_runner_receipt(**valid_receipt_parts()))
        missing = dict(document)
        missing.pop("request_sha256")
        extra = {**document, "unexpected": True}
        for candidate in (missing, extra):
            with self.assertRaises(RunnerIdentityError) as raised:
                validate_receipt_document(candidate)
            self.assertEqual(raised.exception.code, "RECEIPT_SCHEMA_INVALID")

    def test_nested_identity_subclasses_are_rejected_before_receipt_serialization(self):
        @dataclasses.dataclass(frozen=True)
        class ExtendedRunIdentity(RunIdentity):
            controller_secret: str

        @dataclasses.dataclass(frozen=True)
        class ExtendedBackendIdentity(BackendIdentity):
            controller_secret: str

        @dataclasses.dataclass(frozen=True)
        class ExtendedInputCommitment(InputCommitment):
            controller_secret: str

        @dataclasses.dataclass(frozen=True)
        class ExtendedResponseIdentity(ResponseIdentity):
            controller_secret: str

        secret = "controller-only-oracle-material"
        base_parts = valid_receipt_parts()
        base_response = ResponseIdentity(**base_parts["response_identity"])
        cases = (
            (
                "run_identity",
                ExtendedRunIdentity(
                    **dataclasses.asdict(base_parts["run_identity"]),
                    controller_secret=secret,
                ),
                "RUN_IDENTITY_INVALID",
            ),
            (
                "backend_identity",
                ExtendedBackendIdentity(
                    **dataclasses.asdict(base_parts["backend_identity"]),
                    controller_secret=secret,
                ),
                "BACKEND_IDENTITY_INVALID",
            ),
            (
                "permitted_input_inventory",
                (
                    ExtendedInputCommitment(
                        **dataclasses.asdict(base_parts["permitted_input_inventory"][0]),
                        controller_secret=secret,
                    ),
                    *base_parts["permitted_input_inventory"][1:],
                ),
                "INPUT_INVENTORY_INVALID",
            ),
            (
                "response_identity",
                ExtendedResponseIdentity(
                    **dataclasses.asdict(base_response),
                    controller_secret=secret,
                ),
                "RESPONSE_IDENTITY_INVALID",
            ),
        )

        valid_receipt = build_runner_receipt(**valid_receipt_parts())
        for field_name, extended_value, code in cases:
            with self.subTest(field_name=field_name, boundary="build"):
                parts = valid_receipt_parts()
                parts[field_name] = extended_value
                with self.assertRaises(RunnerIdentityError) as raised:
                    build_runner_receipt(**parts)
                self.assertEqual(raised.exception.code, code)

            extended_receipt = dataclasses.replace(
                valid_receipt,
                **{field_name: extended_value},
            )
            with self.subTest(field_name=field_name, boundary="validate"):
                with self.assertRaises(RunnerIdentityError) as raised:
                    validate_runner_receipt(extended_receipt)
                self.assertEqual(raised.exception.code, code)

            with self.subTest(field_name=field_name, boundary="serialize"):
                with self.assertRaises(RunnerIdentityError) as raised:
                    receipt_document(extended_receipt)
                self.assertEqual(raised.exception.code, code)

        self.assertNotIn(
            secret.encode("utf-8"),
            canonical_json_bytes(receipt_document(valid_receipt)),
        )

    def test_package_digest_mismatch_is_rejected(self):
        parts = valid_receipt_parts()
        receipt = build_runner_receipt(**parts)
        changed = dataclasses.replace(
            receipt.run_identity, package_digest=_digest("different-package")
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            validate_runner_receipt(
                dataclasses.replace(receipt, run_identity=changed),
                expected_run_identity=receipt.run_identity,
            )
        self.assertEqual(raised.exception.code, "PACKAGE_DIGEST_MISMATCH")

    def test_package_schema_version_mismatch_is_rejected(self):
        receipt = build_runner_receipt(**valid_receipt_parts())
        changed = dataclasses.replace(
            receipt.run_identity,
            package_schema_version="joewrks.semantic-review-input/2.0",
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            validate_runner_receipt(
                dataclasses.replace(receipt, run_identity=changed),
                expected_run_identity=receipt.run_identity,
            )
        self.assertEqual(raised.exception.code, "PACKAGE_SCHEMA_VERSION_MISMATCH")

    def test_brief_and_output_schema_digest_mismatch_are_rejected(self):
        receipt = build_runner_receipt(**valid_receipt_parts())
        changed_inventory = tuple(
            dataclasses.replace(item, sha256=_digest("different-brief"))
            if item.logical_role == "reviewer_brief"
            else item
            for item in receipt.permitted_input_inventory
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            validate_runner_receipt(
                dataclasses.replace(receipt, permitted_input_inventory=changed_inventory),
                expected_input_inventory=receipt.permitted_input_inventory,
            )
        self.assertEqual(raised.exception.code, "BRIEF_DIGEST_MISMATCH")

        changed_inventory = tuple(
            dataclasses.replace(item, sha256=_digest("different-schema"))
            if item.logical_role == "output_schema"
            else item
            for item in receipt.permitted_input_inventory
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            validate_runner_receipt(
                dataclasses.replace(receipt, permitted_input_inventory=changed_inventory),
                expected_input_inventory=receipt.permitted_input_inventory,
            )
        self.assertEqual(raised.exception.code, "OUTPUT_SCHEMA_DIGEST_MISMATCH")

    def test_backend_model_and_settings_identity_mismatch_are_rejected(self):
        receipt = build_runner_receipt(**valid_receipt_parts())
        changed_backend = dataclasses.replace(
            receipt.backend_identity, model_revision_identity="other-model@2026-09-03"
        )
        changed_response = dataclasses.replace(
            receipt.response_identity,
            backend_identity_sha256=sha256_bytes(
                canonical_json_bytes(dataclasses.asdict(changed_backend))
            ),
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            validate_runner_receipt(
                dataclasses.replace(
                    receipt,
                    backend_identity=changed_backend,
                    response_identity=changed_response,
                ),
                expected_backend_identity=receipt.backend_identity,
            )
        self.assertEqual(raised.exception.code, "MODEL_IDENTITY_MISMATCH")

        changed_backend = dataclasses.replace(
            receipt.backend_identity, inference_settings_sha256=_digest("other-settings")
        )
        changed_response = dataclasses.replace(
            receipt.response_identity,
            backend_identity_sha256=sha256_bytes(
                canonical_json_bytes(dataclasses.asdict(changed_backend))
            ),
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            validate_runner_receipt(
                dataclasses.replace(
                    receipt,
                    backend_identity=changed_backend,
                    response_identity=changed_response,
                ),
                expected_backend_identity=receipt.backend_identity,
            )
        self.assertEqual(raised.exception.code, "INFERENCE_SETTINGS_MISMATCH")

    def test_reviewer_run_context_cohort_and_case_mismatch_are_rejected(self):
        receipt = build_runner_receipt(**valid_receipt_parts())
        for field, value, code in (
            ("reviewer_id", "other-reviewer", "REVIEWER_ID_MISMATCH"),
            ("review_run_id", "other-run", "REVIEW_RUN_ID_MISMATCH"),
            ("context_id", "other-context", "CONTEXT_ID_MISMATCH"),
            ("cohort_id", "cohort-001", "COHORT_ID_MISMATCH"),
            ("case_id", "case-001", "CASE_ID_MISMATCH"),
        ):
            changed = dataclasses.replace(receipt.run_identity, **{field: value})
            with self.assertRaises(RunnerIdentityError) as raised:
                validate_runner_receipt(
                    dataclasses.replace(receipt, run_identity=changed),
                    expected_run_identity=receipt.run_identity,
                )
            self.assertEqual(raised.exception.code, code)

    def test_wrong_semantic_review_contract_version_is_rejected(self):
        receipt = build_runner_receipt(**valid_receipt_parts())
        changed = dataclasses.replace(
            receipt.run_identity,
            semantic_review_contract_version="joewrks.semantic-review/2.0",
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            validate_runner_receipt(
                dataclasses.replace(receipt, run_identity=changed),
                expected_run_identity=receipt.run_identity,
            )
        self.assertEqual(raised.exception.code, "SEMANTIC_REVIEW_CONTRACT_VERSION_MISMATCH")

    def test_expected_semantic_review_contract_version_mismatch_is_rejected_bidirectionally(self):
        for actual_version, expected_version in (
            ("joewrks.semantic-review/1.0", "joewrks.semantic-review/2.1"),
            ("joewrks.semantic-review/2.1", "joewrks.semantic-review/1.0"),
        ):
            with self.subTest(actual=actual_version, expected=expected_version):
                parts = valid_receipt_parts()
                parts["run_identity"] = dataclasses.replace(
                    parts["run_identity"],
                    semantic_review_contract_version=actual_version,
                )
                receipt = build_runner_receipt(**parts)
                expected = dataclasses.replace(
                    receipt.run_identity,
                    semantic_review_contract_version=expected_version,
                )
                with self.assertRaises(RunnerIdentityError) as raised:
                    validate_runner_receipt(
                        receipt,
                        expected_run_identity=expected,
                    )
                self.assertEqual(
                    raised.exception.code,
                    "SEMANTIC_REVIEW_CONTRACT_VERSION_MISMATCH",
                )

    def test_v21_receipt_accepts_distinct_semantic_and_artifact_digests(self):
        parts = valid_receipt_parts()
        semantic_package_digest = _digest("semantic-package-v21")
        exact_package_bytes_digest = _digest("exact-package-bytes-v21")
        parts["run_identity"] = dataclasses.replace(
            parts["run_identity"],
            semantic_review_contract_version="joewrks.semantic-review/2.1",
            package_schema_version="joewrks.semantic-review/2.1",
            package_digest=semantic_package_digest,
        )
        parts["permitted_input_inventory"] = tuple(
            dataclasses.replace(item, sha256=exact_package_bytes_digest)
            if item.logical_role == "review_package"
            else item
            for item in parts["permitted_input_inventory"]
        )
        parts["response_identity"] = {
            **parts["response_identity"],
            "reviewer_id": parts["run_identity"].reviewer_id,
            "review_run_id": parts["run_identity"].review_run_id,
            "context_id": parts["run_identity"].context_id,
        }

        try:
            receipt = build_runner_receipt(**parts)
        except RunnerIdentityError as error:
            self.fail(f"semantic-review/2.1 receipt must be accepted: {error.code}")

        self.assertEqual(receipt.run_identity.package_digest, semantic_package_digest)
        package_commitment = next(
            item
            for item in receipt.permitted_input_inventory
            if item.logical_role == "review_package"
        )
        self.assertEqual(package_commitment.sha256, exact_package_bytes_digest)
        self.assertNotEqual(
            receipt.run_identity.package_digest,
            package_commitment.sha256,
        )
        schema = json.loads(
            (
                SKILL_ROOT
                / "reviewer_runner"
                / "schemas"
                / "reviewer-runner-receipt-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            schema["$defs"]["runIdentity"]["properties"][
                "semantic_review_contract_version"
            ],
            {
                "enum": [
                    "joewrks.semantic-review/1.0",
                    "joewrks.semantic-review/2.1",
                ]
            },
        )

    def test_floating_model_name_cannot_be_promoted_to_immutable_identity(self):
        parts = valid_receipt_parts()
        parts["backend_identity"] = dataclasses.replace(
            parts["backend_identity"],
            model_revision_identity="example-model",
            model_identity_stability="FLOATING",
        )
        with self.assertRaises(RunnerIdentityError) as raised:
            build_runner_receipt(**parts)
        self.assertEqual(raised.exception.code, "MODEL_IDENTITY_NOT_IMMUTABLE")

    def test_response_count_rejects_boolean_and_float_values(self):
        document = receipt_document(build_runner_receipt(**valid_receipt_parts()))
        for response_count in (True, 1.0):
            response_identity = dict(document["response_identity"])
            response_identity["response_count"] = response_count
            candidate = {**document, "response_identity": response_identity}
            with self.assertRaises(RunnerIdentityError) as raised:
                validate_receipt_document(candidate)
            self.assertEqual(raised.exception.code, "RESPONSE_COUNT_INVALID")


if __name__ == "__main__":
    unittest.main()
