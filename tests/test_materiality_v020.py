import sys
import unittest
from pathlib import Path

try:
    from tests.v020_support import evidence_record, foundation_state, materiality, surface_record
except ModuleNotFoundError:
    from v020_support import evidence_record, foundation_state, materiality, surface_record


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from materiality_v2 import (
    classify_materiality,
    is_high_risk,
    validate_materiality_classification,
)
from state_validation_v2 import validate_state_v2


RISK_FLAGS = (
    "security", "privacy", "money", "legal_or_policy", "destructive",
    "data_loss", "external_commitment",
)


def low_local_trivial_materiality(*, outcome="LOW", user_visible=False):
    return {
        "outcome_divergence": outcome,
        "fan_out": "LOCAL",
        "user_visible": user_visible,
        "reversibility": "TRIVIALLY_REVERSIBLE",
        "risk_flags": {
            "security": False, "privacy": False, "money": False,
            "legal_or_policy": False, "destructive": False,
            "data_loss": False, "external_commitment": False,
        },
        "classification": "NON_MATERIAL",
    }


def decision_record():
    return {
        "id": "DEC-001", "status": "CURRENT", "statement": "Record the product decision.",
        "decision_type": "SCOPE", "resolution_mode": "USER_DECISION",
        "decision_authority": "USER_DECISION_REQUIRED", "source_unknown_refs": [],
        "evidence_refs": [], "materiality": materiality(), "affects": [],
    }


def contradiction_record():
    return {
        "id": "CON-001", "status": "OPEN", "claim_a_refs": ["EVD-001"],
        "claim_b_refs": ["EVD-002"], "scope_refs": ["DEC-001"],
        "materiality": materiality(), "resolution": None, "resolved_by": [],
        "selected_authority_refs": [],
    }


class MaterialityV020Test(unittest.TestCase):
    def test_classifies_only_none_or_low_local_trivial_no_risk_as_non_material(self):
        for outcome in ("NONE", "LOW"):
            with self.subTest(outcome=outcome):
                candidate = low_local_trivial_materiality(outcome=outcome)
                self.assertEqual(classify_materiality(candidate), "NON_MATERIAL")
                self.assertFalse(is_high_risk(candidate))

    def test_classifies_medium_and_high_outcomes_as_material(self):
        for outcome in ("MEDIUM", "HIGH"):
            with self.subTest(outcome=outcome):
                candidate = low_local_trivial_materiality(outcome=outcome)
                self.assertEqual(classify_materiality(candidate), "MATERIAL")
                self.assertFalse(is_high_risk(candidate))

    def test_classifies_non_local_fan_out_as_material(self):
        for fan_out in ("MULTI_OBJECT", "MULTI_FLOW", "SYSTEMIC"):
            with self.subTest(fan_out=fan_out):
                candidate = low_local_trivial_materiality()
                candidate["fan_out"] = fan_out
                self.assertEqual(classify_materiality(candidate), "MATERIAL")
                self.assertFalse(is_high_risk(candidate))

    def test_classifies_nontrivial_reversibility_as_material_and_marks_costly_cases_high_risk(self):
        for reversibility, high_risk in (
            ("REVERSIBLE", False),
            ("COSTLY_TO_REVERSE", True),
            ("IRREVERSIBLE", True),
        ):
            with self.subTest(reversibility=reversibility):
                candidate = low_local_trivial_materiality()
                candidate["reversibility"] = reversibility
                self.assertEqual(classify_materiality(candidate), "MATERIAL")
                self.assertIs(is_high_risk(candidate), high_risk)

    def test_classifies_each_risk_flag_as_material_and_high_risk(self):
        for risk_flag in RISK_FLAGS:
            with self.subTest(risk_flag=risk_flag):
                candidate = low_local_trivial_materiality()
                candidate["risk_flags"][risk_flag] = True
                self.assertEqual(classify_materiality(candidate), "MATERIAL")
                self.assertTrue(is_high_risk(candidate))

    def test_keeps_user_visible_low_local_trivial_no_risk_materiality_non_material(self):
        candidate = low_local_trivial_materiality(user_visible=True)

        self.assertEqual(classify_materiality(candidate), "NON_MATERIAL")
        self.assertFalse(is_high_risk(candidate))

    def test_rejects_stored_classifications_that_disagree_with_recomputation(self):
        declared_material = low_local_trivial_materiality()
        declared_material["classification"] = "MATERIAL"
        declared_non_material = low_local_trivial_materiality(outcome="MEDIUM")

        self.assertFalse(validate_materiality_classification(declared_material))
        self.assertFalse(validate_materiality_classification(declared_non_material))

    def test_rejects_mismatches_for_each_canonical_materiality_bearing_record(self):
        state = foundation_state()
        state["objects"]["requirements"] = [{
            "id": "REQ-001", "status": "CURRENT", "statement": "Save feedback.",
            "scope": "CORE", "ui_required": True, "materiality": materiality(),
        }]
        state["objects"]["unknowns"] = [{
            "id": "UNK-001", "status": "OPEN", "question": "Which format?",
            "materiality": materiality(), "decision_authority": "USER_CONFIRMATION",
        }]
        state["objects"]["decisions"] = [decision_record()]
        state["surface_manifest"]["records"] = [surface_record(classification="NON_MATERIAL")]
        state["evidence"] = [evidence_record("EVD-001"), evidence_record("EVD-002")]
        state["contradictions"] = [contradiction_record()]

        materiality_paths = (
            "objects.requirements[0].materiality",
            "objects.unknowns[0].materiality",
            "objects.decisions[0].materiality",
            "surface_manifest.records[0].materiality",
            "contradictions[0].materiality",
        )
        for path in materiality_paths:
            target = state
            for part in path.replace("[0]", ".0").split("."):
                target = target[int(part)] if part == "0" else target[part]
            target["classification"] = "MATERIAL"

        mismatch_paths = {
            error["path"]
            for error in validate_state_v2(state)
            if error["code"] == "materiality_classification_mismatch"
        }
        self.assertEqual(mismatch_paths, set(materiality_paths))


if __name__ == "__main__":
    unittest.main()
