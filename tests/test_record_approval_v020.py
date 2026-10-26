import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from approval_status import approval_status  # noqa: E402
from approval_v2 import (  # noqa: E402
    approval_manifest_digest,
    build_approval_commitment,
    build_approval_manifest_for_review,
)
from state_contract_dispatch import evaluate_closure_for_version  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_approval_manifest_v020 import approved_state, unicode_ready_state  # noqa: E402
from tests.v020_support import review_ready_state  # noqa: E402


APPROVED_AT = "2026-08-29T00:00:00Z"


def _run(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        cwd=ROOT, capture_output=True, check=False,
    )


class RecordApprovalV020Test(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        # Closable fixture with Korean and non-BMP text, so the write path is also an encoding check.
        self.state = unicode_ready_state()
        self.manifest = build_approval_manifest_for_review(self.state)
        self.digest = approval_manifest_digest(self.manifest)
        self.path = Path(self.directory.name) / "state.json"
        self.path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.original = self.path.read_bytes()

    def record(self, *extra, revision=1, digest=None, at=APPROVED_AT):
        return _run(
            "record_approval.py", self.path, "--revision", revision,
            "--manifest-digest", digest or self.digest, "--at", at, *extra,
        )

    def test_write_records_the_exact_approval_layers_and_reaches_closure(self):
        result = self.record("--write")

        self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8"))
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["recorded"])
        self.assertEqual(receipt["approved_at_source"], "user_message")
        written = json.loads(self.path.read_text(encoding="utf-8"))
        expected = copy.deepcopy(self.state)
        commitment = build_approval_commitment(self.state, self.manifest)
        expected["project"]["definition_status"] = "CLOSED"
        expected["approval"] = {
            "status": "APPROVED", "approved_revision": 1,
            "approved_definition_digest": commitment["definition_digest"],
            "approved_manifest_digest": self.digest,
            "approved_at": APPROVED_AT, "approved_by": "user",
        }
        expected["approval_history"] = [commitment]
        self.assertEqual(written, expected)
        self.assertEqual(validate_state_v2(written), [])
        self.assertTrue(evaluate_closure_for_version(written)["closed"])
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["state.json"])

    def test_without_write_it_only_reports(self):
        result = self.record()

        self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8"))
        receipt = json.loads(result.stdout)
        self.assertFalse(receipt["recorded"])
        self.assertTrue(receipt["dry_run"])
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_observed_time_is_marked_as_recording_time(self):
        result = self.record("--write", at="observed")

        self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8"))
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["approved_at_source"], "observed_at_recording")
        self.assertRegex(receipt["approved_at"], re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"))
        written = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(written["approval"]["approved_at"], receipt["approved_at"])
        self.assertEqual(validate_state_v2(written), [])

    def test_mismatches_and_bad_time_are_refused_without_writing(self):
        cases = (
            ({"digest": "0" * 64}, "manifest_digest_mismatch"),
            ({"revision": 2}, "revision_mismatch"),
            ({"at": "2026-08-29 00:00"}, "invalid_approval_time"),
        )
        for overrides, code in cases:
            with self.subTest(code=code):
                result = self.record("--write", **overrides)
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertFalse(payload["recorded"])
                self.assertIn(code, {error["code"] for error in payload["errors"]})
                self.assertEqual(self.path.read_bytes(), self.original)

    def test_already_approved_state_is_not_ready_for_approval(self):
        self.assertEqual(self.record("--write").returncode, 0)
        before = self.path.read_bytes()

        result = self.record("--write")

        self.assertEqual(result.returncode, 1)
        codes = {error["code"] for error in json.loads(result.stdout)["errors"]}
        self.assertEqual(codes, {"not_ready_for_approval"})
        self.assertEqual(self.path.read_bytes(), before)

    def test_read_error_exits_two(self):
        result = _run("record_approval.py", self.path.with_name("missing.json"),
                      "--revision", 1, "--manifest-digest", self.digest, "--at", APPROVED_AT)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["errors"][0]["code"], "read_error")


class ApprovalStatusV020Test(unittest.TestCase):
    def test_approved_current_revision_has_nothing_pending(self):
        status = approval_status(approved_state())

        self.assertTrue(status["current_revision_approved"])
        self.assertEqual(status["approved_revisions"], [1])
        self.assertEqual(status["pending_revisions"], [])
        self.assertIsNone(status["pending_changes"])
        self.assertEqual(status["revisions_without_own_approval"], [])

    def test_pending_and_bundled_revisions_are_reported(self):
        state = copy.deepcopy(approved_state())
        first = state["approval_history"][0]
        state["approval_history"] = [dict(first, revision=1), dict(first, revision=3)]
        state["project"]["definition_revision"] = 5
        state["project"]["definition_status"] = "READY_FOR_REVIEW"
        state["approval"] = {"status": "UNAPPROVED"}

        status = approval_status(state)

        self.assertFalse(status["current_revision_approved"])
        self.assertEqual(status["revisions_without_own_approval"], [2])
        self.assertEqual(status["pending_revisions"], [4, 5])
        self.assertEqual(status["pending_changes"]["from_revision"], 3)
        self.assertEqual(status["pending_changes"]["to_revision"], 5)
        self.assertIn("NOT approved", status["summary"])

    def test_cli_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps(review_ready_state()), encoding="utf-8")
            before = path.read_bytes()
            result = _run("approval_status.py", path)
            self.assertEqual(path.read_bytes(), before)

        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        payload = json.loads(result.stdout)
        self.assertEqual(payload["pending_revisions"], [1])
        self.assertEqual(payload["approved_revisions"], [])


if __name__ == "__main__":
    unittest.main()
