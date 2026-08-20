import json
import subprocess
import sys
import unittest
import tempfile
from pathlib import Path

from test_validators import closed_state


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"


class EvaluationFixtureTest(unittest.TestCase):
    def run_fixture(self, validator, name):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / validator), str(FIXTURES / name)],
            capture_output=True, text=True, check=False,
        )
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def run_state(self, validator, state):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / validator), str(path)],
                capture_output=True, text=True, check=False,
            )
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_closed_fixture_passes_both_validators(self):
        state = closed_state()
        state_code, state_payload = self.run_state("validate_state.py", state)
        closure_code, closure_payload = self.run_state("validate_closure.py", state)
        self.assertEqual((state_code, closure_code), (0, 0))
        self.assertTrue(state_payload["valid"])
        self.assertTrue(closure_payload["closed"])

    def test_open_and_stale_fixtures_fail_closure_only(self):
        open_state = closed_state()
        open_state["project"]["status"] = "OPEN"
        open_state["project"]["user_approved"] = False
        open_state["project"]["approval"] = {"approved_revision": None, "approved_digest": None, "approved_at": None}
        open_state["objects"]["unknowns"] = [{"id": "UNK-001", "status": "OPEN", "material": True}]
        stale_state = closed_state()
        stale_state["objects"]["requirements"][0]["status"] = "STALE"
        for name, state, metric in (("open", open_state, "blocking_unknowns"), ("stale", stale_state, "stale_artifacts")):
            with self.subTest(name=name):
                state_code, _ = self.run_state("validate_state.py", state)
                closure_code, payload = self.run_state("validate_closure.py", state)
                self.assertEqual(state_code, 0)
                self.assertEqual(closure_code, 1)
                self.assertGreater(payload["metrics"][metric], 0)

    def test_broken_reference_fixture_fails_structure(self):
        code, payload = self.run_fixture("validate_state.py", "broken-reference.json")
        self.assertEqual(code, 1)
        self.assertIn("broken_reference", {item["code"] for item in payload["errors"]})


if __name__ == "__main__":
    unittest.main()
