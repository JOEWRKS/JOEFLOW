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

from downstream.schema_validation import (  # noqa: E402
    SchemaValidationError,
    validate_instance,
)
import downstream_v2.runtime_report as runtime_report  # noqa: E402
from downstream_v2.runtime import (  # noqa: E402
    RuntimeVerificationError,
    contained_runtime_error_result,
    verify_action_execution,
    verify_lifecycle_execution,
)
from downstream_v2.runtime_report import (  # noqa: E402
    RUNTIME_REPORT_VERSION,
    build_runtime_conformance_report,
)
from tests.test_downstream_v2_runtime import (  # noqa: E402
    RUNTIME_CONTRACT_HASH,
    execution_record,
    lifecycle_record,
    refresh_semantic_hash,
    runtime_contract,
    snapshot,
    structured_lifecycle_fields,
)


REPORT_SCHEMA = json.loads(
    (
        PACKAGE_ROOT
        / "downstream_v2"
        / "schemas"
        / "runtime-conformance-report.schema.json"
    ).read_text(encoding="utf-8")
)

SOURCE_CONTRACT = {
    "contract_schema_version": "joewrks.action-conformance/2.0",
    "semantic_contract_hash": RUNTIME_CONTRACT_HASH,
    "product_slug": "runtime-product",
    "approved_revision": 7,
    "approved_definition_digest": "d" * 64,
}


def source_contract_for(contract):
    return {
        "contract_schema_version": contract["contract_schema_version"],
        "semantic_contract_hash": contract["semantic_contract_hash"],
        "product_slug": contract["source_authority"]["product_slug"],
        "approved_revision": contract["source_authority"]["approved_revision"],
        "approved_definition_digest": contract["source_authority"]["approved_definition_digest"],
    }


def action_result(test_id, *, conformant=True, evidence_hash=None, contract=None):
    selected_contract = runtime_contract() if contract is None else contract
    if conformant:
        record = execution_record(test_id=test_id, contract=selected_contract)
    else:
        unchanged = snapshot()
        record = execution_record(
            test_id=test_id,
            expected_result="SUCCESS",
            result={"status": "rejected", "code": "VALIDATION_FAILED", "replay": False},
            before=unchanged,
            after=copy.deepcopy(unchanged),
            contract=selected_contract,
        )
    result = verify_action_execution(selected_contract, record)
    if evidence_hash is not None:
        result["evidence_sha256"] = evidence_hash
    return result


def lifecycle_result(case_id, *, conformant=True, contract=None):
    if contract is None:
        selected_contract = runtime_contract()
        selected_contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(selected_contract)
    else:
        selected_contract = contract
    record = lifecycle_record(
        case_id=case_id,
        allowed=(case_id == "submit") if conformant else (case_id != "submit"),
        contract=selected_contract,
    )
    return verify_lifecycle_execution(selected_contract, record)


def full_action_results(contract=None):
    return [
        action_result(test_id, contract=contract)
        for test_id in (
            "happy-path",
            "idempotent-replay",
            "invalid-input",
            "stale-version",
        )
    ]


def audit(status="CONFORMANT"):
    return {
        "status": status,
        "global_definition_closed": True,
        "authority_revision_relation": "SAME_APPROVED_REVISION",
        "reentry_events": [] if status == "CONFORMANT" else [{"event_id": "REENTRY-1"}],
    }


def assurance(*, scope="FULL_CONTRACT", completion="NOT_REQUIRED"):
    value = {
        "verification_scope": scope,
        "review_completion": completion,
    }
    if completion != "NOT_REQUIRED":
        value["reliability_status"] = "NOT_MEASURED"
    return value


def build(
    *,
    contract=None,
    audit_result=None,
    action_results=None,
    lifecycle_results=None,
    semantic_assurance=None,
):
    selected_contract = runtime_contract() if contract is None else contract
    return build_runtime_conformance_report(
        selected_contract,
        audit() if audit_result is None else audit_result,
        full_action_results(selected_contract) if action_results is None else action_results,
        [] if lifecycle_results is None else lifecycle_results,
        assurance() if semantic_assurance is None else semantic_assurance,
    )


class RuntimeAggregateReportTest(unittest.TestCase):
    def test_verifiers_preserve_exact_canonical_runtime_evidence(self):
        action_contract = runtime_contract()
        action_record = execution_record(contract=action_contract)
        action_verified = verify_action_execution(action_contract, action_record)
        self.assertEqual(action_verified["runtime_evidence"], action_record)
        self.assertIsNot(action_verified["runtime_evidence"], action_record)

        lifecycle_contract = runtime_contract()
        lifecycle_contract["actions"] = []
        lifecycle_contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(lifecycle_contract)
        observation = lifecycle_record(contract=lifecycle_contract)
        lifecycle_verified = verify_lifecycle_execution(lifecycle_contract, observation)
        self.assertEqual(lifecycle_verified["runtime_evidence"], observation)
        self.assertIsNot(lifecycle_verified["runtime_evidence"], observation)

    def test_all_deterministic_runtime_evidence_produces_implementation_conformant(self):
        report = build()
        self.assertEqual(report["report_schema_version"], RUNTIME_REPORT_VERSION)
        self.assertEqual(report["verification_scope"], "FULL_CONTRACT")
        self.assertEqual(report["action_coverage_status"], "COMPLETE")
        self.assertEqual(report["lifecycle_coverage_status"], "COMPLETE")
        self.assertEqual(report["lifecycle_applicability"], "NOT_APPLICABLE")
        self.assertEqual(report["coverage_status"], "COMPLETE")
        self.assertEqual(report["contract_dependency_status"], "CONFORMANT")
        self.assertEqual(report["runtime_status"], "CONFORMANT")
        self.assertEqual(report["review_completion"], "NOT_REQUIRED")
        self.assertEqual(report["semantic_review_reliability"], "NOT_REQUIRED")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_CONFORMANT")
        self.assertEqual(report["missing_action_test_ids"], [])
        self.assertEqual(report["unexpected_action_test_ids"], [])
        validate_instance(report, REPORT_SCHEMA)

    def test_published_schema_rejects_malformed_action_and_lifecycle_results(self):
        action_report = build()
        malformed_action = copy.deepcopy(action_report)
        del malformed_action["action_results"][0]["components"]
        with self.assertRaises(SchemaValidationError):
            validate_instance(malformed_action, REPORT_SCHEMA)

        contract = runtime_contract()
        contract["actions"] = []
        contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(contract)
        lifecycle_report = build(
            contract=contract,
            action_results=[],
            lifecycle_results=[
                lifecycle_result("submit", contract=contract),
                lifecycle_result("reopen", contract=contract),
            ],
        )
        malformed_lifecycle = copy.deepcopy(lifecycle_report)
        malformed_lifecycle["lifecycle_results"][0]["expected_allowed"] = "true"
        with self.assertRaises(SchemaValidationError):
            validate_instance(malformed_lifecycle, REPORT_SCHEMA)

    def test_error_result_conformant_is_exact_boolean_false_in_both_shapes(self):
        contract = runtime_contract()
        contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(contract)
        error = RuntimeVerificationError("RUNTIME_EVIDENCE_PROTOCOL_INVALID", "invalid")
        report = build(contract=contract)
        report["action_results"].append(contained_runtime_error_result(
            contract,
            {},
            error,
            lifecycle=False,
        ))
        report["lifecycle_results"].append(contained_runtime_error_result(
            contract,
            {},
            error,
            lifecycle=True,
        ))
        validate_instance(report, REPORT_SCHEMA)
        for collection in ("action_results", "lifecycle_results"):
            for invalid in (0, 0.0, None, "false", ""):
                with self.subTest(collection=collection, invalid=invalid):
                    malformed = copy.deepcopy(report)
                    malformed[collection][0]["conformant"] = invalid
                    with self.assertRaises(SchemaValidationError):
                        validate_instance(malformed, REPORT_SCHEMA)

    def test_total_report_validator_rejects_every_corrupted_global_gate(self):
        validator = getattr(runtime_report, "validate_runtime_conformance_report", None)
        self.assertTrue(callable(validator), "missing total runtime report validator")
        validator(build(), runtime_contract())
        mutations = {
            "scope": lambda report: report.update(verification_scope="PARTIAL_PROBE"),
            "coverage": lambda report: report.update(coverage_status="INCOMPLETE"),
            "action_coverage": lambda report: report.update(action_coverage_status="INCOMPLETE"),
            "lifecycle_coverage": lambda report: report.update(lifecycle_coverage_status="INCOMPLETE"),
            "lifecycle_applicability": lambda report: report.update(lifecycle_applicability="APPLICABLE"),
            "dependency": lambda report: report.update(contract_dependency_status="DEFINITION_NOT_READY"),
            "runtime": lambda report: report.update(runtime_status="NON_CONFORMANT"),
            "review": lambda report: report.update(review_completion="PENDING"),
            "reliability": lambda report: report.update(semantic_review_reliability="NOT_MEASURED"),
            "reentry": lambda report: report["blocking_reentry_events"].append({"event_id": "REENTRY-1"}),
            "contract_errors": lambda report: report["contract_execution_errors"].append({
                "code": "CORRUPTED",
                "detail": "corrupted",
            }),
            "evidence_errors": lambda report: report["evidence_errors"].append({
                "code": "CORRUPTED",
                "detail": "corrupted",
            }),
        }
        for mutation_name, mutate in mutations.items():
            with self.subTest(mutation=mutation_name):
                report = build()
                mutate(report)
                with self.assertRaises(RuntimeVerificationError) as raised:
                    validator(report, runtime_contract())
                self.assertEqual(getattr(raised.exception, "code", None), "RUNTIME_REPORT_INVALID")

    def test_total_report_validator_recomputes_aggregate_implications(self):
        validator = getattr(runtime_report, "validate_runtime_conformance_report", None)
        self.assertTrue(callable(validator), "missing total runtime report validator")
        mutations = {
            "false_negative_global_status": lambda report: report.update(
                implementation_status="IMPLEMENTATION_NOT_CONFORMANT"
            ),
            "coverage_dimension_parity": lambda report: report.update(
                action_coverage_status="INCOMPLETE",
                implementation_status="IMPLEMENTATION_NOT_CONFORMANT",
            ),
            "runtime_result_parity": lambda report: report.update(
                runtime_status="NOT_RUN",
                implementation_status="IMPLEMENTATION_NOT_CONFORMANT",
            ),
            "observed_inventory": lambda report: report["observed_action_test_ids"].pop(),
        }
        for mutation_name, mutate in mutations.items():
            with self.subTest(mutation=mutation_name):
                report = build()
                mutate(report)
                with self.assertRaises(RuntimeVerificationError) as raised:
                    validator(report, runtime_contract())
                self.assertEqual(getattr(raised.exception, "code", None), "RUNTIME_REPORT_INVALID")

    def test_total_report_validator_reverifies_results_and_contract_inventory(self):
        contract = runtime_contract()
        report = build(contract=contract)
        report["action_results"][0]["runtime_evidence"]["result"]["code"] = "WRONG"
        with self.assertRaises(RuntimeVerificationError) as raised:
            runtime_report.validate_runtime_conformance_report(report, contract)
        self.assertEqual(raised.exception.code, "RUNTIME_REPORT_INVALID")

        report = build(contract=contract)
        report["action_results"].pop()
        report["required_action_test_ids"].pop()
        report["observed_action_test_ids"].pop()
        with self.assertRaises(RuntimeVerificationError) as raised:
            runtime_report.validate_runtime_conformance_report(report, contract)
        self.assertEqual(raised.exception.code, "RUNTIME_REPORT_INVALID")

    def test_total_report_validator_rejects_removed_nonexecutable_action_inventory_error(self):
        contract = runtime_contract()
        contract["actions"].append({
            "action_id": "non-executable-action",
            "fields": {
                "test_obligations": {
                    "value": "Prose is not an executable obligation inventory."
                }
            },
        })
        refresh_semantic_hash(contract)
        report = build(
            contract=contract,
            action_results=full_action_results(contract),
        )
        self.assertTrue(report["contract_execution_errors"])

        forged = copy.deepcopy(report)
        forged["contract_execution_errors"] = []
        forged["action_coverage_status"] = "COMPLETE"
        forged["coverage_status"] = "COMPLETE"
        forged["implementation_status"] = "IMPLEMENTATION_CONFORMANT"

        with self.assertRaises(RuntimeVerificationError) as raised:
            runtime_report.validate_runtime_conformance_report(forged, contract)
        self.assertEqual(raised.exception.code, "RUNTIME_REPORT_INVALID")

    def test_total_report_validator_rejects_removed_rejected_evidence_error(self):
        results = full_action_results()
        rejected = copy.deepcopy(results[0])
        rejected["evidence_sha256"] = "9" * 64
        report = build(action_results=[*results, rejected])
        self.assertTrue(report["evidence_errors"])

        forged = copy.deepcopy(report)
        forged["evidence_errors"] = []
        forged["action_coverage_status"] = "COMPLETE"
        forged["coverage_status"] = "COMPLETE"
        forged["runtime_status"] = "CONFORMANT"
        forged["implementation_status"] = "IMPLEMENTATION_CONFORMANT"

        with self.assertRaises(RuntimeVerificationError) as raised:
            runtime_report.validate_runtime_conformance_report(
                forged,
                runtime_contract(),
            )
        self.assertEqual(raised.exception.code, "RUNTIME_REPORT_INVALID")

    def test_total_report_validator_rejects_noncanonical_detail_values(self):
        report = build()
        report["evidence_errors"] = [{
            "code": "CORRUPTED",
            "detail": {"not-json"},
        }]
        report["runtime_status"] = "NON_CONFORMANT"
        report["implementation_status"] = "IMPLEMENTATION_NOT_CONFORMANT"

        with self.assertRaises(RuntimeVerificationError) as raised:
            runtime_report.validate_runtime_conformance_report(report, runtime_contract())

        self.assertEqual(raised.exception.code, "RUNTIME_REPORT_INVALID")

    def test_partial_probe_cannot_claim_global_implementation_conformance(self):
        report = build(semantic_assurance=assurance(scope="PARTIAL_PROBE"))
        self.assertEqual(report["verification_scope"], "PARTIAL_PROBE")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")

    def test_missing_required_action_evidence_keeps_coverage_incomplete(self):
        report = build(action_results=full_action_results()[:-1])
        self.assertEqual(report["action_coverage_status"], "INCOMPLETE")
        self.assertEqual(report["coverage_status"], "INCOMPLETE")
        self.assertEqual(report["missing_action_test_ids"], [{
            "action_id": "submit-request",
            "test_id": "stale-version",
        }])
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")

    def test_duplicate_conflicting_evidence_fails_closed(self):
        results = full_action_results()
        results.append(action_result("happy-path", evidence_hash="9" * 64))
        report = build(action_results=results)
        self.assertEqual(report["action_coverage_status"], "INCOMPLETE")
        self.assertEqual(report["runtime_status"], "NON_CONFORMANT")
        self.assertTrue(report["evidence_errors"])

    def test_malformed_verifier_result_cannot_satisfy_global_coverage(self):
        results = full_action_results()
        del results[0]["components"]
        report = build(action_results=results)
        self.assertEqual(report["action_coverage_status"], "INCOMPLETE")
        self.assertEqual(report["runtime_status"], "NON_CONFORMANT")
        self.assertTrue(report["evidence_errors"])

    def test_results_from_another_contract_are_invalid_before_coverage_or_deduplication(self):
        mutations = (
            ("semantic_contract_hash", "9" * 64),
            ("product_slug", "other-runtime-product"),
            ("approved_revision", 8),
            ("approved_definition_digest", "8" * 64),
        )
        result_factories = (
            ("action-conformant", lambda: action_result("happy-path"), "actions"),
            ("action-failed", lambda: action_result("happy-path", conformant=False), "actions"),
            ("lifecycle-conformant", lambda: lifecycle_result("submit"), "lifecycles"),
            ("lifecycle-failed", lambda: lifecycle_result("submit", conformant=False), "lifecycles"),
        )
        for identity_field, mutated_value in mutations:
            for result_name, result_factory, result_kind in result_factories:
                with self.subTest(identity_field=identity_field, result=result_name):
                    contract = runtime_contract()
                    contract["actions"][0]["fields"]["test_obligations"] = {
                        "value": ["happy-path"]
                    }
                    contract["lifecycles"] = [{
                        "lifecycle_id": "request-lifecycle",
                        "fields": structured_lifecycle_fields(),
                    }]
                    if identity_field == "semantic_contract_hash":
                        contract[identity_field] = mutated_value
                    else:
                        contract["source_authority"][identity_field] = mutated_value
                    kwargs = {
                        "contract": contract,
                        "action_results": [],
                        "lifecycle_results": [],
                    }
                    kwargs["action_results" if result_kind == "actions" else "lifecycle_results"] = [
                        result_factory()
                    ]

                    report = build(**kwargs)

                    self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
                    self.assertEqual(report["coverage_status"], "INCOMPLETE")
                    self.assertTrue(any(
                        error["code"] == "RUNTIME_EVIDENCE_INVALID"
                        and error["detail"] == f"{result_kind}/0 source_contract identity does not match contract"
                        for error in report["evidence_errors"]
                    ))

    def test_semantically_changed_contract_with_stale_hash_rejects_overlapping_results(self):
        contract = runtime_contract()
        prior_results = full_action_results(contract)
        contract["actions"][0]["fields"]["result_expectations"]["value"]["SUCCESS"][
            "revision"
        ] = "ANY"

        report = build(contract=contract, action_results=prior_results)

        self.assertEqual(report["coverage_status"], "INCOMPLETE")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
        self.assertIn({
            "code": "RUNTIME_CONTRACT_NOT_EXECUTABLE",
            "detail": "semantic_contract_hash does not match contract semantics",
        }, report["contract_execution_errors"])
        self.assertTrue(any(
            error["code"] == "RUNTIME_EVIDENCE_INVALID"
            for error in report["evidence_errors"]
        ))

    def test_contradictory_action_results_are_invalid_evidence(self):
        mutations = {
            "result_matches": lambda result: result.update(result_matches=False),
            "observed_result": lambda result: result.update(observed_result="REJECTED"),
            "input_invariant_verdict": lambda result: result["input_invariant_failures"].append({
                "type": "required",
                "pointer": "/title",
                "observed": None,
            }),
            "component_passed": lambda result: result["components"]["revision"].update(passed=False),
            "assertion_passed": lambda result: result["assertions"].append({
                "type": "path_equals",
                "pointer": "/result/code",
                "passed": False,
                "observed": "WRONG",
                "expected": "SUBMITTED",
            }),
            "failures": lambda result: result["failures"].append("corrupted failure"),
        }
        for mutation_name, mutate in mutations.items():
            with self.subTest(mutation=mutation_name):
                results = full_action_results()
                mutate(results[0])

                report = build(action_results=results)

                self.assertEqual(report["action_coverage_status"], "INCOMPLETE")
                self.assertEqual(report["runtime_status"], "NON_CONFORMANT")
                self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
                self.assertIn({
                    "code": "RUNTIME_EVIDENCE_INVALID",
                    "detail": "actions/0 verifier result does not match runtime evidence",
                }, report["evidence_errors"])

    def test_all_assertion_summaries_are_reverified_from_preserved_evidence(self):
        cases = (
            (
                "path_present",
                {"type": "path_present", "pointer": "/result/code"},
                lambda assertion: assertion.update(expected="CORRUPTED"),
            ),
            (
                "path_absent",
                {"type": "path_absent", "pointer": "/result/missing"},
                lambda assertion: assertion.update(expected="CORRUPTED"),
            ),
            (
                "path_equals",
                {"type": "path_equals", "pointer": "/result/code", "value": "SUBMITTED"},
                lambda assertion: assertion.update(observed="WRONG"),
            ),
            (
                "collection_item_field_equals",
                {
                    "type": "collection_item_field_equals",
                    "pointer": "/after/history",
                    "match_field": "action",
                    "match_value": "submit-request",
                    "field": "action",
                    "value": "submit-request",
                },
                lambda assertion: assertion.update(observed=[]),
            ),
        )
        for assertion_name, assertion, corrupt in cases:
            with self.subTest(assertion=assertion_name):
                contract = runtime_contract()
                contract["actions"][0]["fields"]["test_obligations"]["value"] = ["case"]
                contract["actions"][0]["fields"]["result_expectations"]["value"]["SUCCESS"][
                    "assertions"
                ] = [assertion]
                refresh_semantic_hash(contract)
                result = verify_action_execution(
                    contract,
                    execution_record(test_id="case", contract=contract),
                )
                self.assertTrue(result["conformant"])
                corrupt(result["assertions"][0])

                report = build(contract=contract, action_results=[result])

                self.assertEqual(report["action_coverage_status"], "INCOMPLETE")
                self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
                self.assertTrue(any(
                    error["code"] == "RUNTIME_EVIDENCE_INVALID"
                    for error in report["evidence_errors"]
                ))

    def test_action_summary_and_evidence_mutations_are_reverified_before_coverage(self):
        mutations = {
            "before": lambda result: result["runtime_evidence"]["before"].update(revision=99),
            "after": lambda result: result["runtime_evidence"]["after"].update(revision=1),
            "expected": lambda result: result.update(expected_result="REJECTED"),
            "component_changed": lambda result: result["components"]["revision"].update(changed=False),
            "component_passed": lambda result: result["components"]["revision"].update(passed=False),
            "result_matches": lambda result: result.update(result_matches=False),
        }
        for mutation_name, mutate in mutations.items():
            with self.subTest(mutation=mutation_name):
                results = full_action_results()
                mutate(results[0])

                report = build(action_results=results)

                self.assertEqual(report["action_coverage_status"], "INCOMPLETE")
                self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
                self.assertTrue(any(
                    error["code"] == "RUNTIME_EVIDENCE_INVALID"
                    for error in report["evidence_errors"]
                ))

    def test_contained_error_preserves_input_binding_and_never_counts_coverage(self):
        contract = runtime_contract()
        contract["actions"][0]["fields"]["test_obligations"]["value"] = ["case"]
        refresh_semantic_hash(contract)
        malformed = {
            "test_id": "case",
            "command": {"action_id": "submit-request"},
        }
        try:
            verify_action_execution(contract, malformed)
        except RuntimeVerificationError as error:
            contained = contained_runtime_error_result(
                contract,
                malformed,
                error,
                lifecycle=False,
            )
        else:  # pragma: no cover - this fixture must be rejected by the frozen protocol
            self.fail("malformed evidence unexpectedly verified")

        report = build(contract=contract, action_results=[contained])
        self.assertEqual(report["action_results"], [contained])
        self.assertEqual(report["observed_action_test_ids"], [])
        self.assertEqual(report["missing_action_test_ids"], [{
            "action_id": "submit-request",
            "test_id": "case",
        }])
        self.assertEqual(report["coverage_status"], "INCOMPLETE")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")

        for field, value in (
            ("test_id", "other"),
            ("evidence_sha256", "9" * 64),
            ("failures", ["CORRUPTED"]),
            ("runtime_evidence", {}),
        ):
            with self.subTest(field=field):
                corrupted = copy.deepcopy(contained)
                corrupted[field] = value
                rejected = build(contract=contract, action_results=[corrupted])
                self.assertEqual(rejected["action_results"], [])
                self.assertTrue(any(
                    error["code"] == "RUNTIME_EVIDENCE_INVALID"
                    for error in rejected["evidence_errors"]
                ))

    def test_contradictory_lifecycle_results_are_invalid_evidence(self):
        mutations = {
            "verdict": lambda result: result.update(observed_allowed=False),
            "boundary_failures": lambda result: result["boundary_failures"].append({
                "type": "required",
                "pointer": "/reason",
                "observed": None,
            }),
            "failures": lambda result: result["failures"].append("corrupted failure"),
        }
        contract = runtime_contract()
        contract["actions"] = []
        contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(contract)
        for mutation_name, mutate in mutations.items():
            with self.subTest(mutation=mutation_name):
                results = [
                    lifecycle_result("submit", contract=contract),
                    lifecycle_result("reopen", contract=contract),
                ]
                mutate(results[0])

                report = build(
                    contract=contract,
                    action_results=[],
                    lifecycle_results=results,
                )

                self.assertEqual(report["lifecycle_coverage_status"], "INCOMPLETE")
                self.assertEqual(report["runtime_status"], "NON_CONFORMANT")
                self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
                self.assertIn({
                    "code": "RUNTIME_EVIDENCE_INVALID",
                    "detail": "lifecycles/0 verifier result does not match runtime evidence",
                }, report["evidence_errors"])

    def test_every_lifecycle_failure_class_is_reverified_from_preserved_evidence(self):
        cases = {
            "from_state": lambda contract, record: record["command"].update(from_state="WRONG"),
            "to_state": lambda contract, record: record["command"].update(to_state="WRONG"),
            "allowed": lambda contract, record: record["result"].update(allowed=False),
            "boundary": lambda contract, record: (
                contract["lifecycles"][0]["fields"]["boundary_conditions"]["value"].update(
                    submit=[{"type": "required", "pointer": "/token"}]
                )
            ),
            "outcome": lambda contract, record: record["result"].update(object_outcome="WRONG"),
            "authority": lambda contract, record: record["result"].update(authority="WRONG"),
            "reason": lambda contract, record: contract["lifecycles"][0]["fields"][
                "required_reason"
            ].update(value=["submit"]),
            "confirmation": lambda contract, record: contract["lifecycles"][0]["fields"][
                "required_confirmation"
            ].update(value=["submit"]),
            "evidence": lambda contract, record: record["result"].update(evidence_refs=[]),
            "history": lambda contract, record: record["result"].update(history_preserved=False),
        }
        for failure_name, create_failure in cases.items():
            with self.subTest(failure=failure_name):
                contract = runtime_contract()
                contract["actions"] = []
                contract["lifecycles"] = [{
                    "lifecycle_id": "request-lifecycle",
                    "fields": structured_lifecycle_fields(),
                }]
                record = lifecycle_record(contract=contract)
                create_failure(contract, record)
                refresh_semantic_hash(contract)
                authority = contract["source_authority"]
                record["contract_hash"] = contract["semantic_contract_hash"]
                record["authority"] = {
                    "approved_revision": authority["approved_revision"],
                    "approved_digest": authority["approved_definition_digest"],
                }
                failed = verify_lifecycle_execution(contract, record)
                self.assertFalse(failed["conformant"])
                failed["failures"] = []
                failed["boundary_failures"] = []
                failed["observed_allowed"] = failed["expected_allowed"]
                failed["conformant"] = True

                report = build(
                    contract=contract,
                    action_results=[],
                    lifecycle_results=[
                        failed,
                        lifecycle_result("reopen", contract=contract),
                    ],
                )

                self.assertEqual(report["lifecycle_coverage_status"], "INCOMPLETE")
                self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
                self.assertTrue(any(
                    error["code"] == "RUNTIME_EVIDENCE_INVALID"
                    for error in report["evidence_errors"]
                ))

    def test_malformed_nested_failure_details_are_invalid_before_coverage(self):
        action_results = full_action_results()
        action_results[0]["input_invariant_failures"] = [{"type": "required"}]
        action_report = build(action_results=action_results)
        self.assertEqual(action_report["action_coverage_status"], "INCOMPLETE")
        self.assertIn({
            "code": "RUNTIME_EVIDENCE_INVALID",
            "detail": "actions/0 verifier result does not match runtime evidence",
        }, action_report["evidence_errors"])

        contract = runtime_contract()
        contract["actions"] = []
        contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(contract)
        lifecycle_results = [
            lifecycle_result("submit", contract=contract),
            lifecycle_result("reopen", contract=contract),
        ]
        lifecycle_results[0]["boundary_failures"] = [{
            "type": "unsupported-invariant",
            "pointer": "",
            "observed": None,
        }]
        lifecycle_results[0]["failures"] = ["lifecycle boundary conditions failed"]
        lifecycle_results[0]["conformant"] = False
        lifecycle_report = build(
            contract=contract,
            action_results=[],
            lifecycle_results=lifecycle_results,
        )
        self.assertEqual(lifecycle_report["lifecycle_coverage_status"], "INCOMPLETE")
        self.assertIn({
            "code": "RUNTIME_EVIDENCE_INVALID",
            "detail": "lifecycles/0 verifier result does not match runtime evidence",
        }, lifecycle_report["evidence_errors"])

    def test_byte_identical_duplicate_evidence_is_deduplicated_deterministically(self):
        results = full_action_results()
        results.append(copy.deepcopy(results[0]))
        report = build(action_results=results)
        self.assertEqual(report["action_coverage_status"], "COMPLETE")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_CONFORMANT")
        self.assertEqual(report["deduplicated_evidence_count"], 1)

    def test_local_dependency_reentry_blocks_implementation_conformance(self):
        report = build(audit_result=audit("REENTRY_REQUIRED"))
        self.assertEqual(report["contract_dependency_status"], "REENTRY_REQUIRED")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")
        self.assertEqual(report["blocking_reentry_events"], [{"event_id": "REENTRY-1"}])

    def test_runtime_failure_produces_non_conformant(self):
        results = full_action_results()
        results[0] = action_result("happy-path", conformant=False)
        report = build(action_results=results)
        self.assertEqual(report["runtime_status"], "NON_CONFORMANT")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_NOT_CONFORMANT")

    def test_review_recorded_does_not_change_not_measured_reliability(self):
        report = build(
            semantic_assurance=assurance(completion="REVIEW_OUTPUT_RECORDED"),
        )
        self.assertEqual(report["review_completion"], "REVIEW_OUTPUT_RECORDED")
        self.assertEqual(report["semantic_review_reliability"], "NOT_MEASURED")
        self.assertEqual(report["implementation_status"], "IMPLEMENTATION_CONFORMANT")

    def test_structured_lifecycle_inventory_must_be_complete(self):
        contract = runtime_contract()
        contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": structured_lifecycle_fields(),
        }]
        refresh_semantic_hash(contract)
        incomplete = build(
            contract=contract,
            lifecycle_results=[lifecycle_result("submit", contract=contract)],
        )
        self.assertEqual(incomplete["lifecycle_applicability"], "APPLICABLE")
        self.assertEqual(incomplete["lifecycle_coverage_status"], "INCOMPLETE")
        self.assertEqual(incomplete["missing_lifecycle_case_ids"], [{
            "case_id": "reopen",
            "lifecycle_id": "request-lifecycle",
        }])
        complete = build(
            contract=contract,
            lifecycle_results=[
                lifecycle_result("submit", contract=contract),
                lifecycle_result("reopen", contract=contract),
            ],
        )
        self.assertEqual(complete["lifecycle_coverage_status"], "COMPLETE")
        self.assertEqual(complete["implementation_status"], "IMPLEMENTATION_CONFORMANT")

    def test_prose_lifecycle_inventory_cannot_be_called_complete(self):
        contract = runtime_contract()
        fields = structured_lifecycle_fields()
        fields["allowed_transitions"] = {"value": "DRAFT may become DONE."}
        contract["lifecycles"] = [{
            "lifecycle_id": "request-lifecycle",
            "fields": fields,
        }]
        refresh_semantic_hash(contract)
        report = build(contract=contract)
        self.assertEqual(report["lifecycle_coverage_status"], "INCOMPLETE")
        self.assertEqual(report["coverage_status"], "INCOMPLETE")
        self.assertTrue(report["contract_execution_errors"])

    def test_action_execution_gap_does_not_falsely_make_empty_lifecycle_incomplete(self):
        contract = runtime_contract()
        contract["actions"][0]["fields"]["test_obligations"] = {
            "value": "Prose is not an executable obligation inventory."
        }
        refresh_semantic_hash(contract)
        report = build(contract=contract, action_results=[])
        self.assertEqual(report["action_coverage_status"], "INCOMPLETE")
        self.assertEqual(report["lifecycle_applicability"], "NOT_APPLICABLE")
        self.assertEqual(report["lifecycle_coverage_status"], "COMPLETE")
        self.assertEqual(report["coverage_status"], "INCOMPLETE")

    def test_report_is_byte_deterministic(self):
        first = build()
        second = build()
        encoded = lambda value: json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(encoded(first), encoded(second))


if __name__ == "__main__":
    unittest.main()
