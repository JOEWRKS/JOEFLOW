import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.v020_support import evidence_record, foundation_state, materiality, surface_record
except ModuleNotFoundError:
    from v020_support import evidence_record, foundation_state, materiality, surface_record


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from discovery_v2 import build_discovery_baseline, canonical_json_bytes, validate_discovery_baseline
from state_validation_v2 import evaluate_closure_v2, validate_state_v2


def decision_record(*, evidence_refs=None):
    return {
        "id": "DEC-001",
        "status": "CURRENT",
        "statement": "Keep the explicitly approved behavior.",
        "decision_type": "PRODUCT_POLICY",
        "resolution_mode": "USER_DECISION",
        "decision_authority": "USER_CONFIRMATION",
        "source_unknown_refs": [],
        "evidence_refs": list(evidence_refs or []),
        "materiality": materiality(),
        "affects": [],
    }


def current_baseline(state):
    return build_discovery_baseline(
        state,
        procedure_complete=True,
        applicable_surface_classes_complete=True,
    )


class DiscoveryBaselineV020Test(unittest.TestCase):
    def error_codes(self, state):
        return {error["code"] for error in validate_state_v2(state)}

    def test_same_semantic_input_produces_identical_baseline_bytes(self):
        state = foundation_state()
        first = current_baseline(state)
        second = current_baseline(copy.deepcopy(state))

        self.assertEqual(first, second)
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        self.assertEqual(first, {
            "status": "CURRENT",
            "definition_revision": 1,
            "surface_manifest_digest": first["surface_manifest_digest"],
            "evidence_commitment_digest": first["evidence_commitment_digest"],
            "open_material_surface_count": 0,
            "unresolved_material_contradiction_count": 0,
            "procedure_complete": True,
            "applicable_surface_classes_complete": True,
            "active_grill_packs": [],
            "active_grill_packs_complete": False,
            "unknown_unknown_exhaustiveness_claimed": False,
        })

    def test_surface_and_evidence_changes_have_separate_commitment_digests(self):
        state = foundation_state()
        baseline = current_baseline(state)

        changed_surface = copy.deepcopy(state)
        changed_surface["surface_manifest"]["records"] = [
            surface_record(classification="NON_MATERIAL"),
        ]
        surface_baseline = current_baseline(changed_surface)
        self.assertNotEqual(baseline["surface_manifest_digest"], surface_baseline["surface_manifest_digest"])
        self.assertEqual(baseline["evidence_commitment_digest"], surface_baseline["evidence_commitment_digest"])

        changed_evidence = copy.deepcopy(state)
        changed_evidence["evidence"] = [evidence_record()]
        evidence_baseline = current_baseline(changed_evidence)
        self.assertEqual(baseline["surface_manifest_digest"], evidence_baseline["surface_manifest_digest"])
        self.assertNotEqual(baseline["evidence_commitment_digest"], evidence_baseline["evidence_commitment_digest"])

    def test_baseline_never_claims_m3_completeness_or_unknown_unknown_exhaustiveness(self):
        baseline = build_discovery_baseline(
            foundation_state(),
            procedure_complete=True,
            applicable_surface_classes_complete=True,
        )
        self.assertFalse(baseline["active_grill_packs_complete"])
        self.assertFalse(baseline["unknown_unknown_exhaustiveness_claimed"])

        invalid = copy.deepcopy(foundation_state())
        invalid["discovery_baseline"] = baseline
        invalid["discovery_baseline"]["unknown_unknown_exhaustiveness_claimed"] = True
        self.assertIn("invalid_discovery_baseline", self.error_codes(invalid))

    def test_current_baseline_mismatch_fails_and_builder_can_regenerate_it(self):
        state = foundation_state()
        state["discovery_baseline"] = current_baseline(state)
        state["project"]["definition_revision"] = 2

        self.assertIn("stale_discovery_baseline", self.error_codes(state))
        regenerated = current_baseline(state)
        self.assertEqual(regenerated["status"], "CURRENT")
        candidate = copy.deepcopy(state)
        candidate["discovery_baseline"] = regenerated
        self.assertEqual(validate_state_v2(candidate), [])

    def test_stale_baseline_is_structurally_valid_and_counted_as_a_gap(self):
        state = foundation_state()
        state["discovery_baseline"] = {"status": "STALE"}

        self.assertEqual(validate_discovery_baseline(state), [])
        self.assertEqual(validate_state_v2(state), [])
        self.assertEqual(evaluate_closure_v2(state)["metrics"]["discovery_baseline_gaps"], 1)

    def test_stale_consumed_evidence_is_counted_and_rejected_as_current_authority(self):
        state = foundation_state()
        state["evidence"] = [evidence_record(status="STALE")]
        state["objects"]["decisions"] = [decision_record(evidence_refs=["EVD-001"])]

        self.assertIn("stale_consumed_evidence", self.error_codes(state))
        self.assertEqual(evaluate_closure_v2(state)["metrics"]["stale_consumed_evidence"], 1)

    def test_stale_surface_evidence_is_counted_and_cannot_be_required_authority(self):
        state = foundation_state()
        state["project"]["bootstrap_mode"] = "EXISTING_PRODUCT_RECONCILIATION"
        surface = surface_record(classification="NON_MATERIAL")
        surface.update({
            "intent_classification": "AUTHORITATIVE",
            "authority_refs": ["REQ-001"],
            "evidence_refs": ["EVD-001"],
        })
        state["surface_manifest"]["records"] = [surface]
        state["objects"]["requirements"] = [{
            "id": "REQ-001", "status": "CURRENT", "statement": "Save feedback.",
            "scope": "CORE", "ui_required": True, "materiality": materiality(),
        }]
        state["evidence"] = [evidence_record(
            status="SUPERSEDED", source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"],
        )]
        state["evidence"][0]["superseded_by"] = "EVD-002"
        state["evidence"].append(evidence_record(
            "EVD-002", source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"],
        ))

        codes = self.error_codes(state)
        self.assertIn("stale_consumed_evidence", codes)
        self.assertIn("invalid_authoritative_surface", codes)
        self.assertEqual(evaluate_closure_v2(state)["metrics"]["stale_consumed_evidence"], 1)

    def test_unconsumed_stale_evidence_does_not_count_as_stale_consumption(self):
        state = foundation_state()
        state["evidence"] = [evidence_record(status="UNAVAILABLE")]
        state["evidence"][0]["unavailable_reason"] = "The source was removed."

        self.assertNotIn("stale_consumed_evidence", self.error_codes(state))
        self.assertEqual(evaluate_closure_v2(state)["metrics"]["stale_consumed_evidence"], 0)

    def test_cli_prints_a_baseline_without_mutating_the_source_file(self):
        state = foundation_state()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            original = json.dumps(state, ensure_ascii=False, indent=2)
            path.write_text(original, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "build_discovery_baseline.py"), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), current_baseline(state))
            self.assertEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
