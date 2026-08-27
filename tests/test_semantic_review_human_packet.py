import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_ROOT = (
    ROOT / "evals" / "semantic-review-v0.4.3" / "calibration"
)
FIXTURE_ROOT = CALIBRATION_ROOT / "semantic-review-calibration-v1"
PAYLOAD_PATH = FIXTURE_ROOT / "human-adjudication-common-evidence.json"
MANIFEST_PATH = FIXTURE_ROOT / "human-adjudication-manifest.json"
FORM_A_PATH = FIXTURE_ROOT / "human-adjudicator-a-response-form.json"
FORM_B_PATH = FIXTURE_ROOT / "human-adjudicator-b-response-form.json"
PROTOCOL_PATH = CALIBRATION_ROOT / "cohort-protocol-v1.json"
AUDIT_PATH = CALIBRATION_ROOT / "semantic_review_calibration_audit.py"
TASK2_TEXT_PATHS = (
    CALIBRATION_ROOT / "CALIBRATION_CONTROLLER_PROTOCOL.md",
    CALIBRATION_ROOT / "cohort-protocol-v1.json",
    CALIBRATION_ROOT / "official_calibration_controller.py",
    CALIBRATION_ROOT / "semantic_review_calibration_audit.py",
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
            "responsibility_rule_id",
            "completeness_mode",
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
                canonical_value_hash = hashlib.sha256(
                    json.dumps(
                        case["canonical_clause"],
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                self.assertEqual(
                    case["canonical_evidence"]["value_sha256"],
                    canonical_value_hash,
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


if __name__ == "__main__":
    unittest.main()
