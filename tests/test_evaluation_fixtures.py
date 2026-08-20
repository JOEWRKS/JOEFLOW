import json
import subprocess
import sys
import unittest
from pathlib import Path


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

    def test_closed_fixture_passes_both_validators(self):
        state_code, state_payload = self.run_fixture("validate_state.py", "closed.json")
        closure_code, closure_payload = self.run_fixture("validate_closure.py", "closed.json")
        self.assertEqual((state_code, closure_code), (0, 0))
        self.assertTrue(state_payload["valid"])
        self.assertTrue(closure_payload["closed"])

    def test_open_and_stale_fixtures_fail_closure_only(self):
        for name, metric in (("open.json", "blocking_unknowns"), ("stale.json", "stale_artifacts")):
            with self.subTest(name=name):
                state_code, _ = self.run_fixture("validate_state.py", name)
                closure_code, payload = self.run_fixture("validate_closure.py", name)
                self.assertEqual(state_code, 0)
                self.assertEqual(closure_code, 1)
                self.assertGreater(payload["metrics"][metric], 0)

    def test_broken_reference_fixture_fails_structure(self):
        code, payload = self.run_fixture("validate_state.py", "broken-reference.json")
        self.assertEqual(code, 1)
        self.assertIn("broken_reference", {item["code"] for item in payload["errors"]})


if __name__ == "__main__":
    unittest.main()
