import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.v020_support import evidence_record, foundation_state, materiality, unknown_record
except ModuleNotFoundError:
    from v020_support import evidence_record, foundation_state, materiality, unknown_record


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
CLI = SCRIPTS / "next_product_question.py"
sys.path.insert(0, str(SCRIPTS))

import grill_v2
from state_validation_v2 import validate_state_v2


def _missing_feature(*_args, **_kwargs):
    raise AssertionError("Task 4 question selection is not implemented")


question_priority_key = getattr(grill_v2, "question_priority_key", _missing_feature)
select_next_user_question = getattr(grill_v2, "select_next_user_question", _missing_feature)
project_user_question = getattr(grill_v2, "project_user_question", _missing_feature)


def recommendation():
    return {
        "recommended_option": "OPT-B",
        "reasoning_refs": ["EVD-001"],
        "tradeoffs": ["The alternative changes the user-visible product behavior."],
        "confidence": "HIGH",
    }


def make_unknown(
    unknown_id,
    *,
    authority="USER_DECISION_REQUIRED",
    category="CORE_FLOW",
    fan_out="MULTI_OBJECT",
    high_risk=False,
    status="OPEN",
):
    classification = "NON_MATERIAL" if authority == "AGENT_AUTONOMOUS" else "MATERIAL"
    required_authority_class = "FACTUAL" if authority == "EXTERNAL_AUTHORITY_REQUIRED" else "INTENT"
    record = unknown_record(
        unknown_id,
        status=status,
        classification=classification,
        decision_authority=authority,
        required_authority_class=required_authority_class,
        question_category=category,
    )
    if classification == "MATERIAL":
        record["materiality"]["fan_out"] = fan_out
    if high_risk:
        record["materiality"]["risk_flags"]["security"] = True
    if authority == "USER_CONFIRMATION":
        record["recommendation"] = recommendation()
    if authority == "EVIDENCE_RESOLVABLE":
        record["evidence_refs"] = ["EVD-001"]
    if status == "BLOCKED":
        record["blocked_reason"] = "The required product authority is unavailable."
    return record


def state_with_unknowns(*unknowns):
    state = foundation_state()
    state["objects"]["unknowns"] = [copy.deepcopy(unknown) for unknown in unknowns]
    state["evidence"] = [evidence_record(
        source_kind="USER_CONFIRMED_INTENT",
        authority_classes=["INTENT"],
        claim="The user-confirmed intent supports this product choice.",
    )]
    return state


class QuestionPolicyV020Test(unittest.TestCase):
    def assert_valid(self, state):
        self.assertEqual(validate_state_v2(state), [])

    def assert_selected(self, expected_id, *unknowns):
        state = state_with_unknowns(*unknowns)
        self.assert_valid(state)
        selected = select_next_user_question(state)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["unknown_id"], expected_id)
        return selected

    def test_eligibility_returns_one_open_user_authority_across_all_authorities_and_categories(self):
        unknowns = [
            make_unknown("UNK-010", authority="USER_DECISION_REQUIRED", category="COSMETIC"),
            make_unknown("UNK-011", authority="USER_CONFIRMATION", category="PREFERENCE"),
            make_unknown("UNK-012", authority="EVIDENCE_RESOLVABLE", category="CORE_FLOW"),
            make_unknown("UNK-013", authority="AGENT_AUTONOMOUS", category="SCOPE_BOUNDARY"),
            make_unknown("UNK-014", authority="EXTERNAL_AUTHORITY_REQUIRED", category="STATE_RECOVERY"),
            make_unknown("UNK-015", authority="EVIDENCE_RESOLVABLE", category="SECONDARY_BEHAVIOR"),
            make_unknown("UNK-016", authority="AGENT_AUTONOMOUS", category="COSMETIC"),
            make_unknown("UNK-017", authority="EXTERNAL_AUTHORITY_REQUIRED", category="PREFERENCE"),
            make_unknown("UNK-018", authority="USER_DECISION_REQUIRED", category="CORE_FLOW"),
        ]
        unknowns[-1]["blocks_unknown_refs"] = ["UNK-010", "UNK-011"]

        selected = self.assert_selected("UNK-018", *unknowns)

        self.assertEqual(set(selected), {
            "unknown_id", "question", "why_it_matters", "evidence_refs",
            "affected_ids", "response_mode", "options", "recommendation",
        })

    def test_only_open_status_is_eligible(self):
        open_unknown = make_unknown("UNK-001", category="PREFERENCE")
        blocked = make_unknown("UNK-002", category="CORE_FLOW", status="BLOCKED")

        self.assert_selected("UNK-001", blocked, open_unknown)

    def test_more_blocked_unknown_refs_rank_first(self):
        fewer = make_unknown("UNK-001")
        more = make_unknown("UNK-002")
        target_one = make_unknown("UNK-003", category="COSMETIC")
        target_two = make_unknown("UNK-004", category="COSMETIC")
        fewer["blocks_unknown_refs"] = ["UNK-003"]
        more["blocks_unknown_refs"] = ["UNK-003", "UNK-004"]

        self.assert_selected("UNK-002", fewer, more, target_one, target_two)

    def test_high_risk_ranks_before_non_high_risk(self):
        normal = make_unknown("UNK-001", category="CORE_FLOW", fan_out="SYSTEMIC")
        risky = make_unknown(
            "UNK-002", category="COSMETIC", fan_out="LOCAL", high_risk=True,
        )

        self.assert_selected("UNK-002", normal, risky)

    def test_fan_out_uses_the_frozen_order(self):
        records = [
            make_unknown("UNK-001", fan_out="LOCAL"),
            make_unknown("UNK-002", fan_out="MULTI_OBJECT"),
            make_unknown("UNK-003", fan_out="MULTI_FLOW"),
            make_unknown("UNK-004", fan_out="SYSTEMIC"),
        ]

        self.assert_selected("UNK-004", *records)

    def test_category_uses_the_frozen_order(self):
        records = [
            make_unknown("UNK-001", category="COSMETIC"),
            make_unknown("UNK-002", category="PREFERENCE"),
            make_unknown("UNK-003", category="SECONDARY_BEHAVIOR"),
            make_unknown("UNK-004", category="STATE_RECOVERY"),
            make_unknown("UNK-005", category="SCOPE_BOUNDARY"),
            make_unknown("UNK-006", category="CORE_FLOW"),
        ]

        self.assert_selected("UNK-006", *records)

    def test_stable_unknown_id_is_the_final_ascending_tie_break(self):
        later = make_unknown("UNK-020")
        earlier = make_unknown("UNK-003")

        self.assertLess(question_priority_key(earlier), question_priority_key(later))
        self.assert_selected("UNK-003", later, earlier)

    def test_projection_is_an_exact_deep_copied_subset_and_transform(self):
        canonical = make_unknown("UNK-012", authority="USER_CONFIRMATION")
        canonical["affects"] = ["REQ-007"]
        expected = {
            "unknown_id": "UNK-012",
            "question": canonical["question"],
            "why_it_matters": canonical["why_it_matters"],
            "evidence_refs": [],
            "affected_ids": ["REQ-007"],
            "response_mode": "MUTUALLY_EXCLUSIVE",
            "options": copy.deepcopy(canonical["options"]),
            "recommendation": copy.deepcopy(canonical["recommendation"]),
        }
        before = copy.deepcopy(canonical)

        projected = project_user_question(canonical)

        self.assertEqual(projected, expected)
        self.assertEqual(canonical, before)
        projected["options"][0]["consequences"].append("Injected consequence")
        projected["recommendation"]["tradeoffs"].append("Injected tradeoff")
        projected["affected_ids"].append("REQ-999")
        self.assertEqual(canonical, before)

    def test_selector_validates_before_selection_without_repairing_state(self):
        invalid = state_with_unknowns(make_unknown(
            "UNK-001", authority="AGENT_AUTONOMOUS",
        ))
        invalid["objects"]["unknowns"][0]["materiality"] = materiality(classification="MATERIAL")
        before = copy.deepcopy(invalid)

        with self.assertRaises(ValueError) as raised:
            select_next_user_question(invalid)

        self.assertEqual(invalid, before)
        self.assertIn(
            "invalid_decision_authority_derivation",
            {error["code"] for error in raised.exception.args[0]},
        )

    def test_selector_returns_none_when_no_user_question_is_eligible(self):
        state = state_with_unknowns(
            make_unknown("UNK-001", authority="AGENT_AUTONOMOUS"),
            make_unknown("UNK-002", authority="EXTERNAL_AUTHORITY_REQUIRED"),
        )
        self.assert_valid(state)

        self.assertIsNone(select_next_user_question(state))

    def test_cli_is_byte_deterministic_and_does_not_change_input_bytes(self):
        state = state_with_unknowns(make_unknown("UNK-001"))
        self.assert_valid(state)
        input_bytes = json.dumps(
            state, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        expected_hash = hashlib.sha256(input_bytes).hexdigest()

        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_bytes(input_bytes)
            command = [sys.executable, str(CLI), str(state_path)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
            second = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)

            self.assertEqual(first.returncode, 0, first.stderr.decode())
            self.assertEqual(second.returncode, 0, second.stderr.decode())
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(first.stderr, b"")
            self.assertEqual(hashlib.sha256(state_path.read_bytes()).hexdigest(), expected_hash)
            self.assertEqual(
                json.loads(first.stdout),
                {"next_question": project_user_question(state["objects"]["unknowns"][0])},
            )

    def test_cli_invalid_state_exits_one_with_validation_errors(self):
        state = foundation_state()
        state["project"]["slug"] = 42

        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "invalid.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), str(state_path)],
                cwd=ROOT,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stderr.decode())
        payload = json.loads(result.stdout)
        self.assertIsNone(payload["next_question"])
        self.assertTrue(payload["errors"])
        self.assertTrue(all(set(error) == {"code", "message", "path"} for error in payload["errors"]))

    def test_cli_argument_and_read_errors_exit_two(self):
        cases = (
            [sys.executable, str(CLI)],
            [sys.executable, str(CLI), str(ROOT / "does-not-exist.json")],
        )
        for command in cases:
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stdout, result.stderr.decode())
                payload = json.loads(result.stdout)
                self.assertIsNone(payload["next_question"])
                self.assertEqual(len(payload["errors"]), 1)
                self.assertIn(payload["errors"][0]["code"], {"usage_error", "read_error"})


if __name__ == "__main__":
    unittest.main()
