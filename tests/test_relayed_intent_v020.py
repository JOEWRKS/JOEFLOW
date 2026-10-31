"""Relayed user intent (U2-8): only the user's own words close a material question."""
import argparse
import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))
sys.path.insert(0, str(ROOT))

from new_records import build_records  # noqa: E402
from record_builders import evidence  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_semantic_closure_v020 import literal_ready_state  # noqa: E402


def codes(state):
    return {error["code"] for error in validate_state_v2(state)}


def relayed(confidence):
    return evidence("EVD-050", source_kind="RELAYED_USER_INTENT", authority_classes=["INTENT"],
                    locator="relayed by parent session", claim="사용자 원문: \"처음 3돌은 Swap2로\"", confidence=confidence)


class RelayedIntentTest(unittest.TestCase):
    def user_decision_backed_only_by(self, record):
        state = literal_ready_state()
        decision = next(d for d in state["objects"]["decisions"] if d["status"] == "CURRENT")
        decision["resolution_mode"] = "USER_DECISION"
        decision["evidence_refs"] = ["EVD-050"]
        state["evidence"].append(record)
        return state, decision

    def test_a_relayed_summary_cannot_back_a_user_decision(self):
        state, _ = self.user_decision_backed_only_by(relayed("INFERRED"))
        self.assertIn("relayed_intent_cannot_close", codes(state))

    def test_a_verbatim_relay_can(self):
        state, _ = self.user_decision_backed_only_by(relayed("DIRECT"))
        self.assertNotIn("relayed_intent_cannot_close", codes(state))

    def test_the_users_own_evidence_beside_a_summary_still_closes(self):
        state, decision = self.user_decision_backed_only_by(relayed("INFERRED"))
        state["evidence"].append(evidence("EVD-051", source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
                                          locator="chat", claim="처음 3돌은 Swap2로"))
        decision["evidence_refs"] = ["EVD-050", "EVD-051"]
        self.assertNotIn("relayed_intent_cannot_close", codes(state))

    def test_a_relayed_summary_cannot_be_selected_contradiction_authority(self):
        state = literal_ready_state()
        state["evidence"].append(relayed("INFERRED"))
        state["contradictions"].append({
            "id": "CON-050", "status": "RESOLVED", "summary": "relayed vs observed", "evidence_refs": ["EVD-050"],
            "resolution": "the relayed instruction wins", "resolved_by": [], "selected_authority_refs": ["EVD-050"],
        })
        self.assertIn("invalid_selected_authority", codes(state))

    def test_the_helper_builds_both_forms(self):
        quoted = build_records(argparse.Namespace(kind="relayed", id="EVD-060", relayer="parent session", when=None, quote="그렇게 해", summary=None, classes=None))
        summary = build_records(argparse.Namespace(kind="relayed", id="EVD-061", relayer="parent session", when="2026-10-31", quote=None, summary="start Swap2 first", classes=["PREFERENCE"]))
        self.assertEqual((quoted["evidence"][0]["confidence"], quoted["evidence"][0]["source_kind"]), ("DIRECT", "RELAYED_USER_INTENT"))
        self.assertEqual((summary["evidence"][0]["confidence"], summary["evidence"][0]["authority_classes"]), ("INFERRED", ["PREFERENCE"]))
        self.assertIn("said 2026-10-31", summary["evidence"][0]["locator"])


if __name__ == "__main__":
    unittest.main()
