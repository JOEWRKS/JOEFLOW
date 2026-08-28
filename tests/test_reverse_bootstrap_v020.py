import copy
import base64
import json
import subprocess
import sys
import unittest
from pathlib import Path

try:
    from tests.v020_support import (
        decision_record as canonical_decision_record,
        evidence_record,
        foundation_state,
        materiality,
        surface_record,
        unknown_record as canonical_unknown_record,
    )
except ModuleNotFoundError:
    from v020_support import (
        decision_record as canonical_decision_record,
        evidence_record,
        foundation_state,
        materiality,
        surface_record,
        unknown_record as canonical_unknown_record,
    )


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
sys.path.insert(0, str(SCRIPTS))


def unknown_record():
    record = canonical_unknown_record(
        classification="NON_MATERIAL", decision_authority="USER_CONFIRMATION",
    )
    record["question"] = "Which product intent should govern this observed behavior?"
    return record


def requirement_record():
    return {
        "id": "REQ-001",
        "status": "CURRENT",
        "statement": "Save feedback.",
        "scope": "CORE",
        "ui_required": True,
        "materiality": materiality(),
    }


def decision_record(*, status="CURRENT"):
    record = canonical_decision_record(
        status=status,
        source_unknown_refs=["UNK-002"],
        classification="NON_MATERIAL",
    )
    record["statement"] = "Keep feedback as an explicitly approved product behavior."
    return record


def decision_source_unknown():
    record = canonical_unknown_record(
        "UNK-002",
        status="RESOLVED",
        classification="NON_MATERIAL",
        decision_authority="USER_DECISION_REQUIRED",
    )
    record.update({
        "resolved_by": ["DEC-001"],
        "resolution_mode": "USER_DECISION",
        "resolution_summary": "The user approved this product behavior.",
    })
    return record


def add_decision(state, *, status="CURRENT"):
    state["objects"]["decisions"] = [decision_record(status=status)]
    state["objects"]["unknowns"].append(decision_source_unknown())


def contradiction_record():
    return {
        "id": "CON-001",
        "status": "OPEN",
        "claim_a_refs": ["EVD-001"],
        "claim_b_refs": ["EVD-002"],
        "scope_refs": ["SURF-001"],
        "materiality": materiality(),
        "resolution": None,
        "resolved_by": [],
        "selected_authority_refs": [],
    }


class ReverseBootstrapV020Test(unittest.TestCase):
    def errors(self, state):
        from state_validation_v2 import validate_state_v2

        return {error["code"] for error in validate_state_v2(state)}

    def schema_valid(self, state):
        encoded_state = base64.b64encode(json.dumps(state).encode("utf-8")).decode("ascii")
        command = (
            "$json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("
            f"'{encoded_state}')); "
            f"Test-Json -Json $json -SchemaFile '{SCHEMA}'"
        )
        result = subprocess.run(
            ["pwsh.exe", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
        )
        if result.returncode == 1:
            self.assertIn("The JSON is not valid with the schema:", result.stderr)
            return False
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "True")
        return True

    def existing_state(self, surface=None):
        state = foundation_state()
        state["project"]["bootstrap_mode"] = "EXISTING_PRODUCT_RECONCILIATION"
        state["surface_manifest"]["records"] = [surface or surface_record(classification="NON_MATERIAL")]
        return state

    def test_existing_surfaces_require_exact_nonempty_intent_classifications(self):
        state = self.existing_state()
        for value in (None, "", "INFERRED", []):
            with self.subTest(value=value):
                candidate = copy.deepcopy(state)
                candidate["surface_manifest"]["records"][0]["intent_classification"] = value
                self.assertIn("invalid_surface_intent_classification", self.errors(candidate))

    def test_new_product_surfaces_require_a_null_intent_classification(self):
        state = foundation_state()
        state["surface_manifest"]["records"] = [surface_record(classification="NON_MATERIAL")]
        self.assertEqual(self.errors(state), set())

        state["surface_manifest"]["records"][0]["intent_classification"] = "OBSERVED_ONLY"
        self.assertIn("invalid_surface_intent_classification", self.errors(state))

    def test_schema_and_runtime_reject_bootstrap_mode_classification_mismatches(self):
        existing_null = self.existing_state()
        new_non_null = foundation_state()
        new_non_null["surface_manifest"]["records"] = [surface_record(classification="NON_MATERIAL")]
        new_non_null["surface_manifest"]["records"][0]["intent_classification"] = "OBSERVED_ONLY"

        for state in (existing_null, new_non_null):
            with self.subTest(bootstrap_mode=state["project"]["bootstrap_mode"]):
                self.assertFalse(self.schema_valid(state))
                self.assertIn("invalid_surface_intent_classification", self.errors(state))

    def test_authoritative_requires_product_authority_and_qualified_intent_evidence(self):
        surface = surface_record(classification="NON_MATERIAL")
        surface["intent_classification"] = "AUTHORITATIVE"
        state = self.existing_state(surface)
        self.assertIn("invalid_authoritative_surface", self.errors(state))

        state["objects"]["requirements"] = [requirement_record()]
        state["surface_manifest"]["records"][0]["authority_refs"] = ["REQ-001"]
        state["evidence"] = [evidence_record()]
        self.assertIn("invalid_authoritative_surface", self.errors(state))

        state["evidence"] = [
            evidence_record("EVD-001", source_kind="DESIGN_ARTIFACT", authority_classes=["INTENT"]),
            evidence_record("EVD-002", source_kind="INFERRED_INTENT", authority_classes=["PREFERENCE"]),
        ]
        state["surface_manifest"]["records"][0]["evidence_refs"] = ["EVD-001", "EVD-002"]
        self.assertIn("invalid_authoritative_surface", self.errors(state))

        state["evidence"].append(evidence_record(
            "EVD-003", source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
        ))
        state["surface_manifest"]["records"][0]["evidence_refs"].append("EVD-003")
        self.assertEqual(self.errors(state), set())

    def test_authoritative_allows_a_current_explicit_decision_instead_of_intent_evidence(self):
        surface = surface_record(classification="NON_MATERIAL")
        surface.update({
            "intent_classification": "AUTHORITATIVE",
            "authority_refs": ["REQ-001"],
            "decision_refs": ["DEC-001"],
        })
        state = self.existing_state(surface)
        state["objects"]["requirements"] = [requirement_record()]
        add_decision(state)
        self.assertEqual(self.errors(state), set())

        state["objects"]["decisions"][0]["status"] = "STALE"
        self.assertIn("invalid_authoritative_surface", self.errors(state))

    def test_observed_only_requires_observed_evidence_but_no_authority_ref(self):
        surface = surface_record(classification="NON_MATERIAL")
        surface["intent_classification"] = "OBSERVED_ONLY"
        state = self.existing_state(surface)
        self.assertIn("invalid_observed_only_surface", self.errors(state))

        state["evidence"] = [evidence_record(
            source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"],
        )]
        state["surface_manifest"]["records"][0]["evidence_refs"] = ["EVD-001"]
        self.assertIn("invalid_observed_only_surface", self.errors(state))

        state["evidence"][0] = evidence_record()
        self.assertEqual(self.errors(state), set())
        self.assertEqual(state["surface_manifest"]["records"][0]["authority_refs"], [])

    def test_material_observed_only_requires_an_open_unknown(self):
        surface = surface_record()
        surface["intent_classification"] = "OBSERVED_ONLY"
        surface["authority_refs"] = ["REQ-001"]
        surface["evidence_refs"] = ["EVD-001"]
        state = self.existing_state(surface)
        state["objects"]["requirements"] = [requirement_record()]
        state["evidence"] = [evidence_record()]
        self.assertIn("invalid_observed_only_surface", self.errors(state))

        state["objects"]["unknowns"] = [unknown_record()]
        state["surface_manifest"]["records"][0]["unknown_refs"] = ["UNK-001"]
        self.assertEqual(self.errors(state), set())

    def test_conflicting_requires_an_existing_contradiction(self):
        surface = surface_record()
        surface["intent_classification"] = "CONFLICTING"
        surface["authority_refs"] = ["REQ-001"]
        state = self.existing_state(surface)
        state["objects"]["requirements"] = [requirement_record()]
        self.assertIn("invalid_conflicting_surface", self.errors(state))

        state["evidence"] = [evidence_record("EVD-001"), evidence_record("EVD-002")]
        state["contradictions"] = [contradiction_record()]
        state["surface_manifest"]["records"][0]["contradiction_refs"] = ["CON-001"]
        self.assertEqual(self.errors(state), set())

    def test_unexplained_material_surface_requires_open_unknown_and_no_intent_evidence(self):
        surface = surface_record()
        surface["intent_classification"] = "UNEXPLAINED"
        surface["authority_refs"] = ["REQ-001"]
        state = self.existing_state(surface)
        state["objects"]["requirements"] = [requirement_record()]
        self.assertIn("invalid_unexplained_surface", self.errors(state))

        state["objects"]["unknowns"] = [unknown_record()]
        state["surface_manifest"]["records"][0]["unknown_refs"] = ["UNK-001"]
        self.assertEqual(self.errors(state), set())

        state["evidence"] = [evidence_record(
            source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"],
        )]
        state["surface_manifest"]["records"][0]["evidence_refs"] = ["EVD-001"]
        self.assertIn("invalid_unexplained_surface", self.errors(state))

    def test_switching_modes_never_promotes_observed_behavior_to_product_authority(self):
        surface = surface_record(classification="NON_MATERIAL")
        surface["intent_classification"] = "OBSERVED_ONLY"
        surface["evidence_refs"] = ["EVD-001"]
        state = self.existing_state(surface)
        state["evidence"] = [evidence_record()]
        self.assertEqual(self.errors(state), set())

        state["project"]["bootstrap_mode"] = "NEW_PRODUCT"
        state["surface_manifest"]["records"][0]["intent_classification"] = None
        self.assertEqual(self.errors(state), set())
        self.assertEqual(state["surface_manifest"]["records"][0]["authority_refs"], [])
        self.assertEqual(state["objects"]["requirements"], [])

        state["project"]["bootstrap_mode"] = "EXISTING_PRODUCT_RECONCILIATION"
        state["surface_manifest"]["records"][0]["intent_classification"] = "AUTHORITATIVE"
        self.assertIn("invalid_authoritative_surface", self.errors(state))


if __name__ == "__main__":
    unittest.main()
