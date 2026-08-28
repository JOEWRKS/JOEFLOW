import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_ROOT = (
    ROOT / "evals" / "semantic-review-v0.4.3" / "calibration"
)
FIXTURE_ROOT = CALIBRATION_ROOT / "semantic-review-calibration-v1"
GOLDEN_CASES_PATH = (
    ROOT / "tests" / "fixtures" / "semantic-review-v1" / "golden-cases.json"
)
PAYLOAD_PATH = FIXTURE_ROOT / "human-adjudication-common-evidence.json"
MANIFEST_PATH = FIXTURE_ROOT / "human-adjudication-manifest.json"
FORM_A_PATH = FIXTURE_ROOT / "human-adjudicator-a-response-form.json"
FORM_B_PATH = FIXTURE_ROOT / "human-adjudicator-b-response-form.json"
PROTOCOL_PATH = CALIBRATION_ROOT / "cohort-protocol-v1.json"
AUDIT_PATH = CALIBRATION_ROOT / "semantic_review_calibration_audit.py"
MATERIALIZER_PATH = CALIBRATION_ROOT / "materialize_human_adjudication_packet.py"
TASK2_TEXT_PATHS = (
    CALIBRATION_ROOT / "CALIBRATION_CONTROLLER_PROTOCOL.md",
    CALIBRATION_ROOT / "cohort-protocol-v1.json",
    CALIBRATION_ROOT / "official_calibration_controller.py",
    CALIBRATION_ROOT / "semantic_review_calibration_audit.py",
    MATERIALIZER_PATH,
    PAYLOAD_PATH,
    MANIFEST_PATH,
    FORM_A_PATH,
    FORM_B_PATH,
    ROOT / "tests" / "test_official_calibration_controller.py",
    Path(__file__).resolve(),
)

ALLOWED_VERDICTS = [
    "APPROVED",
    "REJECTED_CANDIDATE",
    "RUBRIC_ERROR",
    "INPUT_PACKAGE_ERROR",
]
ALLOWED_RATIONALE_CODES = [
    "SUPPORTED_EXACTLY",
    "MISSING_OWNED_SEMANTIC",
    "MISSING_REQUIRED_REFERENCE",
    "UNSUPPORTED_OVERREACH",
    "CONTRADICTS_OWNER",
    "INVALID_DUPLICATION",
    "INVALID_PROVENANCE",
    "ACTIVE_SUPERSEDED_SOURCE",
    "RESPONSIBILITY_UNDEFINED",
    "COMPLETENESS_UNDEFINED",
    "PACKAGE_HASH_MISMATCH",
    "BRIEF_HASH_MISMATCH",
    "CONTRACT_HASH_MISMATCH",
    "RESPONSIBILITY_PROFILE_HASH_MISMATCH",
    "OBLIGATION_INDEX_HASH_MISMATCH",
    "IDENTITY_SET_MISMATCH",
    "PREVIOUS_VERDICT_EXPOSURE",
    "OUTPUT_SCHEMA_VIOLATION",
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_audit():
    spec = importlib.util.spec_from_file_location(
        "semantic_review_calibration_audit", AUDIT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha256(value):
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def embedded_json(golden_case, logical_name):
    return json.loads(
        golden_case["reviewer_package"]["embedded_files"][logical_name]["text"]
    )


def resolve_pointer(document, pointer):
    value = document
    for token in pointer.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def owner_field(contract, review_identity):
    owner_kind, owner_id, semantic_field = review_identity.split(":")
    collection_name, id_key = (
        ("actions", "action_id")
        if owner_kind == "action"
        else ("lifecycles", "lifecycle_id")
    )
    owner = next(
        item for item in contract[collection_name] if item[id_key] == owner_id
    )
    return owner[semantic_field]


class SemanticReviewHumanPacketTest(unittest.TestCase):
    def test_common_payload_has_exact_answer_blind_case_evidence(self):
        payload = read_json(PAYLOAD_PATH)
        self.assertEqual(
            [item["case_id"] for item in payload["cases"]],
            [f"G-{index:03d}" for index in range(1, 16)],
        )
        required = {
            "case_id",
            "canonical_clause",
            "canonical_evidence",
            "candidate_semantic_value",
            "candidate_evidence",
            "candidate_comparison_facts",
            "semantic_obligation_evidence",
            "responsibility_rule_id",
            "completeness_mode",
            "responsibility_profile_evidence",
            "relevant_sibling_refs",
            "allowed_verdicts",
            "allowed_rationale_codes",
        }
        forbidden_key_fragments = ("expected", "correct", "defect", "seeded")
        for case in payload["cases"]:
            with self.subTest(case_id=case["case_id"]):
                self.assertEqual(set(case), required)
                self.assertEqual(case["allowed_verdicts"], ALLOWED_VERDICTS)
                self.assertEqual(
                    case["allowed_rationale_codes"], ALLOWED_RATIONALE_CODES
                )
                self.assertFalse(
                    any(
                        fragment in key.lower()
                        for key in case
                        for fragment in forbidden_key_fragments
                    )
                )
                self.assertNotIn("verdict", case)
                self.assertNotIn("rationale_code", case)
                authority_record = case["canonical_evidence"].get(
                    "authority_object", case["canonical_evidence"]
                )
                self.assertEqual(
                    authority_record["value_sha256"],
                    canonical_sha256(case["canonical_clause"]),
                )

    def test_all_15_cases_match_the_materialized_reviewer_packages_directly(self):
        packet_cases = {
            case["case_id"]: case for case in read_json(PAYLOAD_PATH)["cases"]
        }
        golden_cases = read_json(GOLDEN_CASES_PATH)
        self.assertEqual(set(packet_cases), {case["case_id"] for case in golden_cases})

        for golden_case in golden_cases:
            case_id = golden_case["case_id"]
            packet = packet_cases[case_id]
            authority = embedded_json(golden_case, "authority.json")
            contract = embedded_json(golden_case, "contract.json")
            provenance = embedded_json(golden_case, "provenance.json")["records"]
            obligations = embedded_json(golden_case, "obligations.json")["obligations"]
            identities = embedded_json(golden_case, "identities.json")["identities"]
            responsibility = embedded_json(golden_case, "responsibility.json")
            responsibility_text = golden_case["reviewer_package"]["embedded_files"][
                "responsibility.json"
            ]["text"]
            authority_rule = authority["objects"]["rules"][0]

            with self.subTest(case_id=case_id):
                self.assertEqual(packet["canonical_clause"], authority_rule["text"])
                canonical_refs = (
                    obligations[0]["canonical_refs"] if obligations else provenance[:1]
                )
                if canonical_refs:
                    self.assertEqual(packet["canonical_evidence"], canonical_refs[0])
                else:
                    self.assertEqual(
                        packet["canonical_evidence"],
                        {
                            "source_lookup_status": "ABSENT",
                            "authority_object": {
                                "object_id": authority_rule["id"],
                                "pointer": "/objects/rules/0/text",
                                "status": authority_rule["status"],
                                "value_sha256": canonical_sha256(authority_rule["text"]),
                            },
                        },
                    )

                if identities:
                    identity = identities[0]
                    obligation = obligations[0]
                    pointer = obligation["semantic_value_pointer"]
                    candidate_value = resolve_pointer(contract, pointer)
                    self.assertEqual(packet["candidate_semantic_value"], candidate_value)
                    self.assertEqual(
                        packet["candidate_evidence"],
                        {
                            "review_identity": identity["review_identity"],
                            "semantic_value_pointer": pointer,
                            "semantic_value_sha256": identity["semantic_value_hash"],
                        },
                    )
                    self.assertEqual(
                        canonical_sha256(candidate_value),
                        identity["semantic_value_hash"],
                    )
                    self.assertEqual(
                        packet["responsibility_rule_id"],
                        identity["responsibility_rule_id"],
                    )
                    self.assertEqual(
                        packet["completeness_mode"],
                        identity["completeness_mode"],
                    )
                    self.assertEqual(
                        packet["semantic_obligation_evidence"],
                        {
                            key: obligation[key]
                            for key in (
                                "obligation_id",
                                "obligation_type",
                                "owner_kind",
                                "owner_id",
                                "owning_field",
                                "responsibility_rule_id",
                                "completeness_mode",
                                "semantic_value_pointer",
                                "semantic_value_hash",
                                "canonical_refs",
                                "allowed_sibling_refs",
                                "required_test_refs",
                            )
                        },
                    )

                    owner_kind = identity["owner_kind"]
                    field = identity["semantic_field"]
                    profile = responsibility[owner_kind][field]
                    profile_evidence = packet["responsibility_profile_evidence"]
                    self.assertEqual(
                        profile_evidence["responsibility_profile_sha256"],
                        hashlib.sha256(responsibility_text.encode("utf-8")).hexdigest(),
                    )
                    self.assertEqual(
                        profile_evidence["responsibility_profile_sha256"],
                        next(
                            item["sha256"]
                            for item in golden_case["reviewer_package"]["manifest"][
                                "files"
                            ]
                            if item["logical_role"] == "responsibility_profile"
                        ),
                    )
                    self.assertEqual(
                        profile_evidence["field_lookup_path"],
                        f"/{owner_kind}/{field}",
                    )
                    self.assertEqual(profile_evidence["field_lookup_status"], "PRESENT")
                    self.assertEqual(profile_evidence["rule_semantics"], profile)
                    taxonomy_key = obligation["obligation_type"]
                    self.assertEqual(
                        profile_evidence["obligation_taxonomy_lookup"],
                        {
                            "lookup_path": f"/obligation_taxonomy/{taxonomy_key}",
                            "lookup_status": (
                                "PRESENT"
                                if taxonomy_key
                                in responsibility["obligation_taxonomy"]
                                else "ABSENT"
                            ),
                            "declared_responsibility_rule_id": identity[
                                "responsibility_rule_id"
                            ],
                        },
                    )
                else:
                    self.assertEqual(packet["responsibility_rule_id"], None)
                    self.assertEqual(packet["completeness_mode"], None)
                    self.assertEqual(
                        packet["semantic_obligation_evidence"],
                        {
                            "identity_lookup_status": "ABSENT",
                            "obligation_lookup_status": "ABSENT",
                        },
                    )
                    pointer = "/lifecycles/0/superseded_sentinels"
                    candidate_value = resolve_pointer(contract, pointer)
                    self.assertEqual(packet["candidate_semantic_value"], candidate_value)
                    self.assertEqual(
                        packet["candidate_evidence"],
                        {
                            "review_identity_lookup_status": "ABSENT",
                            "semantic_value_pointer": pointer,
                            "semantic_value_sha256": canonical_sha256(candidate_value),
                        },
                    )
                    self.assertEqual(
                        packet["responsibility_profile_evidence"],
                        {
                            "responsibility_profile_sha256": hashlib.sha256(
                                responsibility_text.encode("utf-8")
                            ).hexdigest(),
                            "field_lookup_path": None,
                            "field_lookup_status": "NOT_APPLICABLE",
                            "rule_semantics": None,
                            "obligation_taxonomy_lookup": {
                                "lookup_path": None,
                                "lookup_status": "NOT_APPLICABLE",
                                "declared_responsibility_rule_id": None,
                            },
                        },
                    )

                fixture = golden_case["candidate_fixture"]
                fixture_refs = list(fixture.get("sibling_references", []))
                if "sibling_reference" in fixture:
                    fixture_refs.insert(0, fixture["sibling_reference"])
                exact_sibling_refs = [
                    re.sub(r"\b(ACT|LC)-G(\d{3})\b", r"\1-G-\2", value)
                    for value in fixture_refs
                ]
                self.assertEqual(packet["relevant_sibling_refs"], exact_sibling_refs)

                for sibling_ref in packet["relevant_sibling_refs"]:
                    self.assertIsInstance(owner_field(contract, sibling_ref), dict)

    def test_g015_keeps_declared_identity_while_taxonomy_lookup_is_absent(self):
        packet = next(
            case
            for case in read_json(PAYLOAD_PATH)["cases"]
            if case["case_id"] == "G-015"
        )
        self.assertEqual(packet["responsibility_rule_id"], "FR-A06")
        self.assertEqual(packet["completeness_mode"], "LOCAL")
        self.assertEqual(
            packet["responsibility_profile_evidence"]["obligation_taxonomy_lookup"],
            {
                "lookup_path": "/obligation_taxonomy/deliberately unclassified",
                "lookup_status": "ABSENT",
                "declared_responsibility_rule_id": "FR-A06",
            },
        )

    def test_neutral_candidate_facts_make_opaque_values_reviewable(self):
        payload = read_json(PAYLOAD_PATH)
        forbidden_projection_words = (
            "expected",
            "correct",
            "correctly",
            "defect",
            "seeded",
            "unsupported",
            "contradictory",
            "deliberately incomplete",
        )
        for case in payload["cases"]:
            facts = case["candidate_comparison_facts"]
            with self.subTest(case_id=case["case_id"]):
                self.assertGreaterEqual(len(facts), 2)
                fact_text = json.dumps(facts, ensure_ascii=False).lower()
                for word in forbidden_projection_words:
                    self.assertNotIn(word, fact_text)
        by_id = {case["case_id"]: case for case in payload["cases"]}
        for case_id in (
            "G-008",
            "G-009",
            "G-010",
            "G-011",
            "G-013",
            "G-014",
            "G-015",
        ):
            with self.subTest(case_id=case_id):
                self.assertNotEqual(
                    by_id[case_id]["candidate_comparison_facts"],
                    [str(by_id[case_id]["candidate_semantic_value"])],
                )

    def test_manifest_records_exact_common_payload_hash_and_incomplete_status(self):
        manifest = read_json(MANIFEST_PATH)
        data = PAYLOAD_PATH.read_bytes()
        self.assertEqual(
            manifest["common_evidence_payload"],
            {
                "path": PAYLOAD_PATH.name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            },
        )
        self.assertEqual(manifest["HUMAN_ADJUDICATION_COMPLETE"], "NO")
        self.assertEqual(manifest["required_independent_human_responses"], 2)
        self.assertEqual(manifest["completed_independent_human_responses"], 0)
        self.assertEqual(
            manifest["external_validation_status"],
            "OPTIONAL_EXTERNAL_VALIDATION_NOT_REQUIRED_FOR_V043_CALIBRATION",
        )
        self.assertEqual(manifest["HUMAN_ADJUDICATION_REQUIRED"], "NO")

    def test_two_forms_share_payload_and_keep_all_responses_empty(self):
        forms = [read_json(FORM_A_PATH), read_json(FORM_B_PATH)]
        self.assertEqual(
            [form["non_normative_form_identity"] for form in forms],
            ["HUMAN-ADJUDICATOR-A", "HUMAN-ADJUDICATOR-B"],
        )
        comparable = []
        for form in forms:
            copy = dict(form)
            copy.pop("non_normative_form_identity")
            comparable.append(copy)
            self.assertEqual(form["HUMAN_ADJUDICATION_COMPLETE"], "NO")
            self.assertEqual(
                form["external_validation_status"],
                "OPTIONAL_EXTERNAL_VALIDATION_NOT_REQUIRED_FOR_V043_CALIBRATION",
            )
            self.assertEqual(form["HUMAN_ADJUDICATION_REQUIRED"], "NO")
            self.assertEqual(
                [item["case_id"] for item in form["responses"]],
                [f"G-{index:03d}" for index in range(1, 16)],
            )
            self.assertTrue(
                all(
                    item == {
                        "case_id": item["case_id"],
                        "verdict": None,
                        "rationale_code": None,
                    }
                    for item in form["responses"]
                )
            )
        self.assertEqual(comparable[0], comparable[1])
        combined = (FORM_A_PATH.read_text() + FORM_B_PATH.read_text()).lower()
        self.assertNotIn("codex", combined)
        self.assertNotIn("artificial intelligence", combined)

    def test_protocol_freezes_three_cohorts_and_exactly_48_unique_contexts(self):
        protocol = read_json(PROTOCOL_PATH)
        self.assertEqual(protocol["cohort_ids"], ["C1", "C2", "C3"])
        self.assertEqual(protocol["REAL_CALIBRATION_RUNS"], 0)
        self.assertEqual(protocol["HUMAN_ADJUDICATION_REQUIRED"], "NO")
        self.assertEqual(
            protocol["external_validation_status"],
            "OPTIONAL_EXTERNAL_VALIDATION_NOT_REQUIRED_FOR_V043_CALIBRATION",
        )
        self.assertEqual(
            protocol["frozen_normative_oracle"],
            {
                "status": "PM_APPROVED_NORMATIVE_ORACLE",
                "sha256": "4126bb8d316291d8362f04fe1160f53ad86adc73ec358effad7a84d104d7a173",
                "bytes": 1648,
                "tuple_set_sha256": "7ddc257c085f8e9de4722b01f09646c25891418fbc92d60e7a15425657acc4aa",
                "frozen_before_reviewer_run": True,
                "post_result_mutation": "NEW_RUBRIC_CALIBRATION_REVISION_AND_COMPLETE_RERUN_REQUIRED",
            },
        )
        self.assertEqual(
            protocol["future_blocker"],
            "BLOCKED — MANIFEST_ONLY_ISOLATION_UNAVAILABLE",
        )
        contexts = []
        for cohort in protocol["cohorts"]:
            self.assertEqual(len(cohort["golden_contexts"]), 15)
            self.assertEqual(
                [item["case_id"] for item in cohort["golden_contexts"]],
                [f"G-{index:03d}" for index in range(1, 16)],
            )
            contexts.append(cohort["full_review_context"]["planned_context_id"])
            contexts.extend(
                item["planned_context_id"] for item in cohort["golden_contexts"]
            )
        self.assertEqual(len(contexts), 48)
        self.assertEqual(len(set(contexts)), 48)

    def test_task2_text_artifacts_are_frozen_to_lf_checkout_bytes(self):
        for path in TASK2_TEXT_PATHS:
            relative = path.relative_to(ROOT).as_posix()
            result = subprocess.run(
                ["git", "check-attr", "eol", "--", relative],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            with self.subTest(path=relative):
                self.assertEqual(result.stdout.strip(), f"{relative}: eol: lf")

    def test_answer_leak_audit_accepts_full_allowed_enums_and_empty_response(self):
        audit = load_audit()
        value = {
            "case_id": "G-001",
            "allowed_verdicts": ALLOWED_VERDICTS,
            "allowed_rationale_codes": ALLOWED_RATIONALE_CODES,
            "verdict": None,
            "rationale_code": None,
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "empty-form.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            findings = audit.find_answer_leaks([path], allowed_exact_sha256=set())
        self.assertEqual(findings, [])

    def test_answer_leak_audit_rejects_filled_per_case_response(self):
        audit = load_audit()
        value = {
            "case_id": "G-001",
            "verdict": "APPROVED",
            "rationale_code": "SUPPORTED_EXACTLY",
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "filled-form.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            findings = audit.find_answer_leaks([path], allowed_exact_sha256=set())
        self.assertIn("PER_CASE_OUTCOME", {item["code"] for item in findings})

    def test_answer_leak_audit_rejects_partial_allowed_enumeration_hint(self):
        audit = load_audit()
        value = {
            "case_id": "G-001",
            "allowed_verdicts": ["APPROVED"],
            "allowed_rationale_codes": ["SUPPORTED_EXACTLY"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "hinted-form.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            findings = audit.find_answer_leaks([path], allowed_exact_sha256=set())
        self.assertIn("PER_CASE_OUTCOME", {item["code"] for item in findings})

    def test_answer_leak_audit_accepts_exact_hash_bound_rule_semantics(self):
        audit = load_audit()
        value = read_json(PAYLOAD_PATH)["cases"][0]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "normative-evidence.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            findings = audit.find_answer_leaks([path], allowed_exact_sha256=set())
        self.assertEqual(findings, [])

    def test_answer_leak_audit_rejects_modified_rule_semantics_hint(self):
        audit = load_audit()
        value = copy.deepcopy(read_json(PAYLOAD_PATH)["cases"][0])
        value["responsibility_profile_evidence"]["rule_semantics"][
            "owns"
        ] = "approved"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "modified-normative-evidence.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            findings = audit.find_answer_leaks([path], allowed_exact_sha256=set())
        self.assertIn("PER_CASE_OUTCOME", {item["code"] for item in findings})


if __name__ == "__main__":
    unittest.main()
