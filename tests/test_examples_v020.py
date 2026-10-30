"""The shipped example states stay valid and equal to what these builders produce.

Regenerate after an intended change: python -B tests/test_examples_v020.py --write
"""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"
EXAMPLES = SKILL / "templates" / "examples"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT))

from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402
from tests.test_semantic_closure_v020 import literal_approved_state  # noqa: E402
from tests.v020_support import (  # noqa: E402
    evidence_record, evidence_with_grill_basis, foundation_state, materiality, surface_record, unknown_record,
)


def discover_one_question():
    """DISCOVER: one brief, one open surface, one question the user should answer next."""
    state = foundation_state()
    state["project"]["slug"] = "example-feedback"
    state["evidence"] = evidence_with_grill_basis(evidence_record(
        "EVD-001", source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
        locator="chat 2026-10-31 (project brief)",
        claim="Customers send feedback from the app; the team wants to reply within a day.",
    ))
    surface = surface_record("SURF-001", status="OPEN", name="Feedback submission", classification="MATERIAL")
    surface["evidence_refs"] = ["EVD-001"]
    surface["unknown_refs"] = ["UNK-001"]
    question = unknown_record("UNK-001")
    question.update({
        "question": "Can a customer send feedback without signing in?",
        "why_it_matters": "Anonymous feedback changes the submission flow, spam handling and how the team replies.",
        "affects": ["SURF-001"],
        "options": [
            {"id": "OPT-A", "statement": "Signed-in customers only.",
             "consequences": ["Every message has an account to reply to."]},
            {"id": "OPT-B", "statement": "Anyone, with an optional email for replies.",
             "consequences": ["More feedback arrives; some cannot be answered."]},
        ],
        # The brief (user intent) supports the recommendation; it is not evidence that answers the question.
        "recommendation": {"recommended_option": "OPT-A", "reasoning_refs": ["EVD-001"],
                           "tradeoffs": ["Anonymous visitors cannot send feedback."], "confidence": "MEDIUM"},
    })
    question["origin"] = {"kind": "PRODUCT_SURFACE", "surface_ref": "SURF-001", "pack_id": None,
                          "axis_id": None, "source_path": None}
    question["materiality"] = materiality(classification="MATERIAL", user_visible=True)
    state["surface_manifest"]["records"] = [surface]
    state["objects"]["unknowns"] = [question]
    return state


def closed_minimal():
    """CLOSED: the smallest definition that passes semantic closure after the user's approval."""
    return copy.deepcopy(literal_approved_state())


BUILDERS = {"discover-one-question.state.json": discover_one_question, "closed-minimal.state.json": closed_minimal}


def render(state):
    return json.dumps(state, ensure_ascii=False, indent=2) + "\n"


class ExampleStatesTest(unittest.TestCase):
    def test_examples_match_their_builders(self):
        for name, build in BUILDERS.items():
            with self.subTest(name=name):
                self.assertEqual((EXAMPLES / name).read_text(encoding="utf-8").replace("\r\n", "\n"), render(build()))

    def test_discover_example_is_valid_and_asks_its_question(self):
        state = discover_one_question()
        self.assertEqual(validate_state_v2(state), [])
        result = subprocess.run(
            [sys.executable, "-B", str(SKILL / "scripts" / "next_product_question.py"), str(EXAMPLES / "discover-one-question.state.json")],
            capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertEqual(json.loads(result.stdout)["next_question"]["unknown_id"], "UNK-001")

    def test_closed_example_closes(self):
        self.assertTrue(evaluate_closure_v2(closed_minimal())["closed"])


if __name__ == "__main__":
    if "--write" in sys.argv:
        EXAMPLES.mkdir(exist_ok=True)
        for name, build in BUILDERS.items():
            (EXAMPLES / name).write_bytes(render(build()).encode("utf-8"))
        print("written", sorted(BUILDERS))
    else:
        unittest.main()
