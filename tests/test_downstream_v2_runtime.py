import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream.protocol import PROTOCOL_VERSION, validate_execution_record  # noqa: E402
from downstream_v2.contracts import semantic_contract_hash  # noqa: E402
from integration_v2.runtime import (  # noqa: E402
    RuntimeVerificationError,
    semantic_value,
    verify_action_execution,
    verify_lifecycle_execution,
)


COMPONENTS = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)
RUNTIME_CONTRACT_HASH = "447635509f9ec0599f2b14cf5c31db04055d58601c25d293922e9a663aa75fe2"
STRUCTURED_LIFECYCLE_CONTRACT_HASH = "eff01a5744f3d02d149b0f5f6a01d9d8a6e8d9c9d44eda0e359ca05d1db9383e"


def semantic(value):
    return {
        "value": value,
        "source_seed_refs": ["SEED-000000000000000000000000"],
        "derivation": {"kind": "DIRECT_AUTHORITY"},
    }


def no_change_expectation(*, assertions=None):
    value = {component: "UNCHANGED" for component in COMPONENTS}
    if assertions is not None:
        value["assertions"] = assertions
    return value


def success_expectation():
    return {
        "authoritative_state": "CHANGED",
        "revision": "CHANGED",
        "history": "CHANGED",
        "business_side_effects": "ANY",
        "delivery_effects": "ANY",
    }


def runtime_contract():
    expectations = {
        "SUCCESS": success_expectation(),
        "REJECTED": no_change_expectation(),
        "STALE": no_change_expectation(),
        "IDEMPOTENT_REPLAY": no_change_expectation(),
    }
    return {
        "contract_schema_version": "joewrks.action-conformance/2.0",
        "source_authority": {
            "product_slug": "runtime-product",
            "approved_revision": 7,
            "approved_definition_digest": "d" * 64,
        },
        "semantic_contract_hash": RUNTIME_CONTRACT_HASH,
        "artifact_hash": "a" * 64,
        "actions": [{
            "action_id": "submit-request",
            "fields": {
                "input_invariants": semantic([]),
                "default_result": semantic("SUCCESS"),
                "result_expectations": semantic(expectations),
                "test_obligations": semantic([
                    "happy-path",
                    "idempotent-replay",
                    "invalid-input",
                    "stale-version",
                ]),
            },
        }],
        "lifecycles": [],
    }


def refresh_semantic_hash(contract):
    contract["semantic_contract_hash"] = semantic_contract_hash(contract)
    return contract


def snapshot(*, state=None, revision=1, history=None, business=None, delivery=None):
    return {
        "authoritative_state": {"status": "READY"} if state is None else state,
        "revision": revision,
        "history": [] if history is None else history,
        "business_side_effects": [] if business is None else business,
        "delivery_effects": [] if delivery is None else delivery,
    }


def execution_record(
    *,
    test_id="happy-path",
    action_id="submit-request",
    expected_result=None,
    command_input=None,
    result=None,
    before=None,
    after=None,
    contract=None,
):
    command = {
        "action_id": action_id,
        "input": {} if command_input is None else command_input,
    }
    if expected_result is not None:
        command["expected_result"] = expected_result
    before = snapshot() if before is None else before
    after = (
        snapshot(
            state={"status": "SUBMITTED"},
            revision=2,
            history=[{"action": "submit-request"}],
        )
        if after is None
        else after
    )
    record = {
        "protocol_version": PROTOCOL_VERSION,
        "record_kind": "execution_result",
        "sequence_id": "SEQ-001",
        "test_id": test_id,
        "product_slug": "runtime-product",
        "contract_hash": RUNTIME_CONTRACT_HASH,
        "authority": {
            "approved_revision": 7,
            "approved_digest": "d" * 64,
        },
        "adapter": {"name": "unit-fixture", "version": "1.0"},
        "frozen_source": {"commit": "f" * 40, "tree": "e" * 40},
        "command": command,
        "result": (
            {"status": "committed", "code": "SUBMITTED", "replay": False}
            if result is None
            else result
        ),
        "before": before,
        "after": after,
        "deltas": {
            "history": [],
            "business_side_effects": [],
            "delivery_effects": [],
        },
    }
    if contract is not None:
        authority = contract["source_authority"]
        record["product_slug"] = authority["product_slug"]
        record["contract_hash"] = contract["semantic_contract_hash"]
        record["authority"] = {
            "approved_revision": authority["approved_revision"],
            "approved_digest": authority["approved_definition_digest"],
        }
    validate_execution_record(record)
    return record


def structured_lifecycle_fields():
    return {
        "current_states": semantic(["DRAFT", "DONE"]),
        "allowed_transitions": semantic([{
            "case_id": "submit",
            "from_state": "DRAFT",
            "to_state": "DONE",
        }]),
        "forbidden_transitions": semantic([{
            "case_id": "reopen",
            "from_state": "DONE",
            "to_state": "DRAFT",
        }]),
        "boundary_conditions": semantic({"submit": [], "reopen": []}),
        "reversibility": semantic({"reversible": False}),
        "reversal_window": semantic(None),
        "object_outcome": semantic({"submit": "DONE", "reopen": "UNCHANGED"}),
        "required_reason": semantic([]),
        "required_confirmation": semantic([]),
        "required_evidence": semantic({"submit": ["commit-readback"], "reopen": []}),
        "authority": semantic({"submit": "REQUESTER", "reopen": "REQUESTER"}),
        "history_preservation": semantic({"required": True}),
    }


def lifecycle_record(*, case_id="submit", allowed=True, contract=None):
    record = execution_record(
        test_id=f"lifecycle-{case_id}",
        after=snapshot(),
        result={
            "status": "observed",
            "code": "LIFECYCLE_OBSERVATION",
            "allowed": allowed,
            "object_outcome": "DONE" if case_id == "submit" else "UNCHANGED",
            "authority": "REQUESTER",
            "confirmed": False,
            "reason": None,
            "evidence_refs": ["commit-readback"] if case_id == "submit" else [],
            "history_preserved": True,
        },
    )
    record["record_kind"] = "lifecycle_observation"
    record["command"] = {
        "lifecycle_id": "request-lifecycle",
        "case_id": case_id,
        "from_state": "DRAFT" if case_id == "submit" else "DONE",
        "to_state": "DONE" if case_id == "submit" else "DRAFT",
        "input": {},
    }
    if contract is not None:
        authority = contract["source_authority"]
        record["product_slug"] = authority["product_slug"]
        record["contract_hash"] = contract["semantic_contract_hash"]
        record["authority"] = {
            "approved_revision": authority["approved_revision"],
            "approved_digest": authority["approved_definition_digest"],
        }
    validate_execution_record(record)
    return record


class RuntimeAdmissionTest(unittest.TestCase):
    def test_frozen_execution_protocol_is_still_the_transport(self):
        record = execution_record()
        validate_execution_record(record)
        self.assertEqual(PROTOCOL_VERSION, "joewrks.downstream.execution/1.0")

    def test_runtime_record_requires_semantic_contract_hash(self):
        record = execution_record()
        record["contract_hash"] = "b" * 64
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(runtime_contract(), record)
        self.assertEqual(raised.exception.code, "RUNTIME_CONTRACT_IDENTITY_MISMATCH")

    def test_runtime_record_rejects_artifact_hash_as_contract_identity(self):
        contract = runtime_contract()
        record = execution_record()
        record["contract_hash"] = contract["artifact_hash"]
        validate_execution_record(record)

        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(contract, record)

        self.assertEqual(raised.exception.code, "RUNTIME_CONTRACT_IDENTITY_MISMATCH")
        self.assertEqual(raised.exception.detail["field"], "contract_hash")

    def test_runtime_record_requires_exact_approved_definition_digest(self):
        record = execution_record()
        record["authority"]["approved_digest"] = "9" * 64
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(runtime_contract(), record)
        self.assertEqual(raised.exception.code, "RUNTIME_AUTHORITY_IDENTITY_MISMATCH")
        self.assertEqual(raised.exception.detail["field"], "authority.approved_digest")

    def test_runtime_record_requires_exact_product_slug(self):
        record = execution_record()
        record["product_slug"] = "different-product"
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(runtime_contract(), record)
        self.assertEqual(raised.exception.code, "RUNTIME_AUTHORITY_IDENTITY_MISMATCH")
        self.assertEqual(raised.exception.detail["field"], "product_slug")

    def test_runtime_record_requires_exact_approved_revision(self):
        record = execution_record()
        record["authority"]["approved_revision"] = 8
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(runtime_contract(), record)
        self.assertEqual(raised.exception.code, "RUNTIME_AUTHORITY_IDENTITY_MISMATCH")
        self.assertEqual(raised.exception.detail["field"], "authority.approved_revision")

    def test_runtime_record_rejects_bool_approved_revision_when_contract_revision_is_one(self):
        contract = runtime_contract()
        contract["source_authority"]["approved_revision"] = 1
        refresh_semantic_hash(contract)
        record = execution_record(contract=contract)
        record["authority"]["approved_revision"] = True

        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(contract, record)

        self.assertEqual(raised.exception.code, "RUNTIME_AUTHORITY_IDENTITY_MISMATCH")
        self.assertEqual(raised.exception.detail["field"], "authority.approved_revision")

    def test_runtime_record_requires_exact_action_id(self):
        record = execution_record(action_id="missing-action")
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(runtime_contract(), record)
        self.assertEqual(raised.exception.code, "RUNTIME_ACTION_NOT_FOUND")

    def test_duplicate_action_ids_fail_closed_instead_of_selecting_first(self):
        contract = runtime_contract()
        contract["actions"].append(copy.deepcopy(contract["actions"][0]))
        refresh_semantic_hash(contract)
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(contract, execution_record(contract=contract))
        self.assertEqual(raised.exception.code, "RUNTIME_DUPLICATE_ACTION_ID")

    def test_semantic_value_requires_an_envelope_with_value(self):
        self.assertEqual(semantic_value(semantic(["x"])), ["x"])
        for malformed in (None, [], {}, {"value": "   "}):
            with self.subTest(malformed=malformed):
                with self.assertRaises(RuntimeVerificationError) as raised:
                    semantic_value(malformed)
                self.assertEqual(raised.exception.code, "RUNTIME_CONTRACT_NOT_EXECUTABLE")

    def test_malformed_contract_identity_values_fail_closed_even_when_record_matches(self):
        cases = (
            ("semantic_contract_hash", "not-a-sha256", "contract_hash"),
            ("approved_definition_digest", "not-a-sha256", "approved_digest"),
            ("approved_revision", True, "approved_revision"),
            ("product_slug", "   ", "product_slug"),
        )
        for contract_key, malformed, record_key in cases:
            with self.subTest(contract_key=contract_key):
                contract = runtime_contract()
                record = execution_record()
                if contract_key == "semantic_contract_hash":
                    contract[contract_key] = malformed
                    record[record_key] = malformed
                else:
                    contract["source_authority"][contract_key] = malformed
                    if record_key == "product_slug":
                        record[record_key] = malformed
                    else:
                        record["authority"][record_key] = malformed
                with self.assertRaises(RuntimeVerificationError) as raised:
                    verify_action_execution(contract, record)
                self.assertEqual(raised.exception.code, "RUNTIME_CONTRACT_NOT_EXECUTABLE")


class RuntimeActionSemanticsTest(unittest.TestCase):
    def test_success_component_expectations_can_pass(self):
        result = verify_action_execution(runtime_contract(), execution_record())
        self.assertTrue(result["conformant"])
        self.assertEqual(result["expected_result"], "SUCCESS")
        self.assertEqual(result["observed_result"], "SUCCESS")
        self.assertEqual(result["test_id"], "happy-path")
        self.assertEqual(result["source_contract"], {
            "contract_schema_version": "joewrks.action-conformance/2.0",
            "semantic_contract_hash": RUNTIME_CONTRACT_HASH,
            "product_slug": "runtime-product",
            "approved_revision": 7,
            "approved_definition_digest": "d" * 64,
        })

    def test_rejected_invariant_is_verified(self):
        contract = runtime_contract()
        contract["actions"][0]["fields"]["input_invariants"] = semantic([
            {"type": "required", "pointer": "/title"},
        ])
        refresh_semantic_hash(contract)
        unchanged = snapshot()
        record = execution_record(
            test_id="invalid-input",
            command_input={},
            result={"status": "rejected", "code": "VALIDATION_FAILED", "replay": False},
            before=unchanged,
            after=copy.deepcopy(unchanged),
            contract=contract,
        )
        result = verify_action_execution(contract, record)
        self.assertTrue(result["conformant"])
        self.assertEqual(result["expected_result"], "REJECTED")
        self.assertEqual(result["input_invariant_failures"][0]["pointer"], "/title")

    def test_stale_result_is_verified(self):
        unchanged = snapshot()
        record = execution_record(
            test_id="stale-version",
            expected_result="STALE",
            result={"status": "rejected", "code": "STALE_VERSION", "replay": False},
            before=unchanged,
            after=copy.deepcopy(unchanged),
        )
        result = verify_action_execution(runtime_contract(), record)
        self.assertTrue(result["conformant"])
        self.assertEqual(result["expected_result"], "STALE")

    def test_idempotent_replay_is_verified(self):
        unchanged = snapshot()
        record = execution_record(
            test_id="idempotent-replay",
            expected_result="IDEMPOTENT_REPLAY",
            result={"status": "committed", "code": "OK", "replay": True},
            before=unchanged,
            after=copy.deepcopy(unchanged),
        )
        result = verify_action_execution(runtime_contract(), record)
        self.assertTrue(result["conformant"])
        self.assertEqual(result["observed_result"], "IDEMPOTENT_REPLAY")

    def test_unexpected_side_effect_fails_conformance(self):
        unchanged = snapshot()
        changed = snapshot(business=[{"type": "unexpected-charge"}])
        record = execution_record(
            test_id="invalid-input",
            expected_result="REJECTED",
            result={"status": "rejected", "code": "VALIDATION_FAILED", "replay": False},
            before=unchanged,
            after=changed,
        )
        result = verify_action_execution(runtime_contract(), record)
        self.assertFalse(result["conformant"])
        self.assertFalse(result["components"]["business_side_effects"]["passed"])

    def test_supported_evidence_assertion_is_checked(self):
        contract = runtime_contract()
        contract["actions"][0]["fields"]["result_expectations"] = semantic({
            "SUCCESS": {
                **success_expectation(),
                "assertions": [{
                    "type": "path_equals",
                    "pointer": "/result/code",
                    "value": "SUBMITTED",
                }],
            },
        })
        refresh_semantic_hash(contract)
        result = verify_action_execution(contract, execution_record(contract=contract))
        self.assertTrue(result["conformant"])
        self.assertTrue(result["assertions"][0]["passed"])

    def test_runtime_critical_prose_fails_closed_not_interpreted(self):
        contract = runtime_contract()
        contract["actions"][0]["fields"]["result_expectations"] = semantic(
            "A valid request changes the appropriate state."
        )
        refresh_semantic_hash(contract)
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(contract, execution_record(contract=contract))
        self.assertEqual(raised.exception.code, "RUNTIME_CONTRACT_NOT_EXECUTABLE")

    def test_malformed_or_duplicate_test_result_declaration_fails_closed(self):
        contract = runtime_contract()
        contract["actions"][0]["fields"]["result_expectations"] = semantic({
            "SUCCESS": {
                "authoritative_state": "CHANGED",
                "revision": "CHANGED",
            },
        })
        refresh_semantic_hash(contract)
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_action_execution(contract, execution_record(contract=contract))
        self.assertEqual(raised.exception.code, "RUNTIME_CONTRACT_NOT_EXECUTABLE")


class RuntimeLifecycleSemanticsTest(unittest.TestCase):
    def setUp(self):
        self.contract = runtime_contract()
        self.contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(self.contract)

    def test_structured_allowed_lifecycle_case_is_verified(self):
        result = verify_lifecycle_execution(
            self.contract,
            lifecycle_record(contract=self.contract),
        )
        self.assertTrue(result["conformant"])
        self.assertEqual(result["case_id"], "submit")
        self.assertTrue(result["expected_allowed"])
        self.assertEqual(result["source_contract"], {
            "contract_schema_version": "joewrks.action-conformance/2.0",
            "semantic_contract_hash": STRUCTURED_LIFECYCLE_CONTRACT_HASH,
            "product_slug": "runtime-product",
            "approved_revision": 7,
            "approved_definition_digest": "d" * 64,
        })

    def test_forbidden_lifecycle_case_requires_observed_rejection(self):
        result = verify_lifecycle_execution(
            self.contract,
            lifecycle_record(case_id="reopen", allowed=False, contract=self.contract),
        )
        self.assertTrue(result["conformant"])
        self.assertFalse(result["expected_allowed"])

    def test_duplicate_lifecycle_ids_fail_closed(self):
        self.contract["lifecycles"].append(copy.deepcopy(self.contract["lifecycles"][0]))
        refresh_semantic_hash(self.contract)
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_lifecycle_execution(self.contract, lifecycle_record(contract=self.contract))
        self.assertEqual(raised.exception.code, "RUNTIME_DUPLICATE_LIFECYCLE_ID")

    def test_prose_lifecycle_values_are_not_interpreted(self):
        self.contract["lifecycles"][0]["fields"]["allowed_transitions"] = semantic(
            "DRAFT may become DONE."
        )
        refresh_semantic_hash(self.contract)
        with self.assertRaises(RuntimeVerificationError) as raised:
            verify_lifecycle_execution(self.contract, lifecycle_record(contract=self.contract))
        self.assertEqual(raised.exception.code, "RUNTIME_CONTRACT_NOT_EXECUTABLE")


if __name__ == "__main__":
    unittest.main()
