import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_validators import closed_state


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"


class StateContractDispatchTest(unittest.TestCase):
    def invoke(self, kind, state):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / f"validate_{kind}.py"), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        return result.returncode, json.loads(result.stdout)

    def test_legacy_version_still_validates_and_closes(self):
        state_code, state_payload = self.invoke("state", closed_state())
        closure_code, closure_payload = self.invoke("closure", closed_state())

        self.assertEqual(state_code, 0, state_payload)
        self.assertTrue(state_payload["valid"])
        self.assertEqual(closure_code, 0, closure_payload)
        self.assertTrue(closure_payload["closed"])

    def test_unsupported_version_is_rejected_by_both_clis(self):
        state = closed_state()
        state["schema_version"] = "9.9.9"

        for kind in ("state", "closure"):
            with self.subTest(kind=kind):
                code, payload = self.invoke(kind, state)
                self.assertEqual(code, 1, payload)
                self.assertIn(
                    "unsupported_schema_version",
                    {error["code"] for error in payload["errors"]},
                )
