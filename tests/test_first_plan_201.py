"""JOEFLOW 2.0.1 candidate: a first plan reaches review from the empty template by scripts alone.

2.0.0 integration test (2026-11-19, D2): starting from templates/state-v0.2.0.example.json
(discovery_baseline NOT_ESTABLISHED), open_revision.py --status READY_FOR_REVIEW stopped on
discovery_baseline_gaps / discovery_procedure_gaps with no pointer, and the only way on was to
hand-edit state.json. D10: new_records.py question required --evidence, so a question whose only
evidence was the user's intent could not be recorded without becoming EVIDENCE_RESOLVABLE.
The fixtures are the two patches of that run (a one-page reading list).
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "first-plan-201"
sys.path.insert(0, str(SCRIPTS))

from approval_v2 import build_approval_manifest_for_review  # noqa: E402


def _run(script, *args):
    result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *map(str, args)],
                            cwd=ROOT, capture_output=True, check=False)
    return result.returncode, result.stdout.decode("utf-8"), result.stderr.decode("utf-8")


class FirstPlanFromEmptyTemplateTest(unittest.TestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory, True)
        self.state = self.directory / "state.json"
        shutil.copyfile(SKILL / "templates" / "state-v0.2.0.example.json", self.state)

    def load(self):
        return json.loads(self.state.read_text(encoding="utf-8"))

    def test_open_revision_keeps_the_baseline_unestablished_while_discovering(self):
        code, out, _ = _run("open_revision.py", self.state, "--patch", FIXTURES / "rev2-patch.json",
                            "--status", "OPEN", "--write")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.load()["discovery_baseline"], {"status": "NOT_ESTABLISHED"})

    def test_ready_for_review_is_reached_and_approvable_without_editing_state(self):
        code, out, _ = _run("open_revision.py", self.state, "--patch", FIXTURES / "rev2-patch.json",
                            "--status", "OPEN", "--write")
        self.assertEqual(code, 0, out)
        code, out, _ = _run("open_revision.py", self.state, "--patch", FIXTURES / "rev3-patch.json",
                            "--status", "READY_FOR_REVIEW", "--write")
        report = json.loads(out)
        self.assertEqual(code, 0, out)
        self.assertTrue(report["written"], out)
        self.assertNotIn("readiness_findings", report)
        self.assertEqual(report["discovery_baseline"], "ESTABLISHED")
        state = self.load()
        self.assertEqual(state["project"]["definition_revision"], 3)
        self.assertEqual(state["project"]["definition_status"], "READY_FOR_REVIEW")
        self.assertEqual(state["discovery_baseline"]["status"], "CURRENT")
        self.assertEqual(state["discovery_baseline"]["definition_revision"], 3)
        code, out, _ = _run("validate_state.py", self.state)
        self.assertEqual(code, 0, out)
        self.assertTrue(json.loads(out)["valid"])
        build_approval_manifest_for_review(state)  # raises when the definition is not reviewable


class QuestionWithIntentOnlyEvidenceTest(unittest.TestCase):
    """D10: --evidence is for facts that frame the question; intent goes in --reason."""

    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory, True)
        self.state = self.directory / "state.json"
        self.patch = self.directory / "patch.json"
        shutil.copyfile(SKILL / "templates" / "examples" / "discover-one-question.state.json", self.state)

    def test_a_question_needs_no_evidence_ref_and_stays_a_user_question(self):
        code, out, err = _run("new_records.py", "--patch", self.patch, "question", "--unknown", "UNK-002",
                              "--question", "Q?", "--why", "matters", "--option", "OPT-A=a|ca",
                              "--option", "OPT-B=b|cb", "--affects", "SURF-001",
                              "--recommend", "OPT-A", "--reason", "EVD-001", "--tradeoff", "t")
        self.assertEqual(code, 0, out + err)
        unknown = json.loads(self.patch.read_text(encoding="utf-8"))["objects"]["unknowns"][0]
        self.assertEqual(unknown["evidence_refs"], [])
        code, out, _ = _run("open_revision.py", self.state, "--patch", self.patch, "--status", "OPEN")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["validation_errors"], [])


if __name__ == "__main__":
    unittest.main()
