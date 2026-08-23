import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"


class DownstreamHandoffTest(unittest.TestCase):
    def test_handoff_template_keeps_prose_and_names_executable_bundle(self):
        template = (SKILL / "templates" / "figma-make-handoff.md").read_text(encoding="utf-8")
        self.assertIn("## Objective, scope, and non-goals", template)
        self.assertIn("## Executable downstream conformance", template)
        for placeholder in (
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


if __name__ == "__main__":
    unittest.main()
