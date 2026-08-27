import json
import unittest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL))

from downstream import contracts


class DownstreamHandoffTest(unittest.TestCase):
    def test_production_handoff_gate_rejects_regression_slice(self):
        gate = getattr(contracts, "is_full_handoff_contract", lambda bundle: None)
        assessment = {
            "structurally_valid": True,
            "provenance_valid": True,
            "machine_derived_obligations_verified": True,
            "machine_derived_field_count": 1,
            "review_required_field_count": 1,
            "review_required_obligations_present": True,
            "machine_verifiable_coverage": 0.5,
        }
        full = json.loads(
            (
                ROOT
                / "evals"
                / "downstream-conformance-v0.4.1"
                / "evidence"
                / "client-feedback-rev44-contract.json"
            ).read_text(encoding="utf-8")
        )
        forged_partial_full = {
            "contract_schema_version": "joewrks.action-conformance/1.0",
            "authority_assessment": assessment,
        }
        regression_slice = {
            "contract_schema_version": "joewrks.downstream.regression-slice/1.0",
            "authority_assessment": assessment,
        }
        self.assertTrue(gate(full))
        self.assertFalse(gate(forged_partial_full))
        self.assertFalse(gate(regression_slice))

    def test_handoff_template_keeps_prose_and_names_executable_bundle(self):
        template = (SKILL / "templates" / "figma-make-handoff.md").read_text(encoding="utf-8")
        self.assertIn("## Objective, scope, and non-goals", template)
        self.assertIn("## Executable downstream conformance", template)
        for placeholder in (
            "{{CONTRACT_SCHEMA_VERSION}}",
            "{{ACTION_CONTRACT_PATH}}",
            "{{LIFECYCLE_CONTRACT_PATH}}",
            "{{EXECUTABLE_CONTRACT_SHA256}}",
            "{{ADAPTER_IDENTITY}}",
            "{{SEQUENCE_RUNNER_COMMAND}}",
        ):
            self.assertIn(placeholder, template)

    def test_handoff_reference_routes_post_closure_conformance_without_changing_authority(self):
        reference = (SKILL / "references" / "figma-make-handoff.md").read_text(encoding="utf-8")
        self.assertIn("downstream/README.md", reference)
        self.assertIn("Canonical Product Definition remains authority", reference)
        self.assertIn("joewrks.downstream.execution/1.0", reference)
        self.assertIn("blind", reference.lower())

    def test_downstream_reference_lists_every_required_sequence_class(self):
        readme = (SKILL / "downstream" / "README.md").read_text(encoding="utf-8")
        required = (
            "valid happy transition",
            "wrong role",
            "wrong object/revision",
            "authority lost after initial access",
            "stale expected version",
            "validation rejection",
            "repeated same idempotency key",
            "same-key replay after later state changes",
            "reversal before boundary",
            "reversal at boundary",
            "reversal after boundary",
            "superseded transition sentinel",
            "delivery failure after successful business commit",
            "manual delivery retry",
            "stop-after-terminal-state",
            "destructive action without confirmation/reason",
            "rejected command followed by a related second command",
            "historical projection after later state change",
        )
        for sequence in required:
            with self.subTest(sequence=sequence):
                self.assertIn(sequence, readme)

    def test_blind_audit_procedure_requires_end_to_end_trace_and_rejects_self_report(self):
        audit = (SKILL / "downstream" / "references" / "drift-audit-procedure.md").read_text(encoding="utf-8")
        for stage in ("precondition", "public action", "handler", "state", "provenance", "visible recovery"):
            self.assertIn(stage, audit.lower())
        self.assertIn("self-report", audit.lower())
        self.assertIn("green test counts", audit.lower())

    def test_downstream_reference_requires_semantic_review_sidecar_before_reliable_review(self):
        readme = (SKILL / "downstream" / "README.md").read_text(encoding="utf-8")
        self.assertIn("joewrks.semantic-review/1.0", readme)
        self.assertIn("No majority-vote escape hatch", readme)
        self.assertIn("joewrks.action-conformance/1.0 remains unchanged", readme)
        for outcome in (
            "APPROVED",
            "REJECTED_CANDIDATE",
            "RUBRIC_ERROR",
            "INPUT_PACKAGE_ERROR",
        ):
            self.assertIn(outcome, readme)

    def test_blind_audit_requires_hash_bound_sidecar_and_calibration_gate_evidence(self):
        audit = (
            SKILL / "downstream" / "references" / "drift-audit-procedure.md"
        ).read_text(encoding="utf-8")
        self.assertIn("reviewer input package hash", audit.lower())
        self.assertIn("reviewer brief hash", audit.lower())
        self.assertIn("responsibility profile hash", audit.lower())
        self.assertIn("semantic obligation index hash", audit.lower())
        self.assertIn("SEMANTIC_REVIEW_RELIABILITY_GATE — PASS", audit)
        self.assertIn("HUMAN_ADJUDICATION_COMPLETE", audit)


if __name__ == "__main__":
    unittest.main()
