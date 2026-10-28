import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from approval_v2 import approval_manifest_digest, build_approval_manifest_for_review  # noqa: E402
from revision_v2 import RevisionError, open_revision  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_approval_manifest_v020 import unicode_ready_state  # noqa: E402


APPROVED_AT = "2026-08-29T00:00:00Z"


def _run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          cwd=ROOT, capture_output=True, check=False)


def _approved_rev1(directory):
    """Write an approved revision 1 through record_approval.py and return (path, state)."""
    state = unicode_ready_state()
    digest = approval_manifest_digest(build_approval_manifest_for_review(state))
    path = Path(directory) / "state.json"
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = _run("record_approval.py", path, "--revision", 1, "--manifest-digest", digest, "--at", APPROVED_AT, "--write")
    assert result.returncode == 0, result.stdout
    return path, json.loads(path.read_text(encoding="utf-8"))


def _covered_binding(state):
    """First COVERED Core cell whose first binding points at a text field."""
    for row in state["coverage"]:
        for axis, cell in row["cells"].items():
            if cell["status"] == "COVERED":
                binding = cell["authority_bindings"][0]
                _, record = _record(state, binding["record_id"])
                if isinstance(record.get(binding["pointer"].lstrip("/")), str):
                    return row["feature_id"], axis, binding["record_id"]
    raise AssertionError("no COVERED cell bound to a text field")


def _edit_bound_text(state, record, suffix):
    """Append to the text field that coverage binds for this record."""
    for row in state["coverage"]:
        for cell in row["cells"].values():
            for binding in cell["authority_bindings"]:
                if binding["record_id"] == record["id"]:
                    field = binding["pointer"].lstrip("/")
                    record[field] += suffix
                    return


def _record(state, record_id):
    for group, records in state["objects"].items():
        for record in records:
            if record.get("id") == record_id:
                return group, record
    raise AssertionError(record_id)


class OpenRevisionTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path, self.state = _approved_rev1(self.directory.name)

    def test_patched_record_rebinds_and_next_revision_validates_and_can_be_approved(self):
        _, _, record_id = _covered_binding(self.state)
        group, record = _record(self.state, record_id)
        changed = copy.deepcopy(record)
        _edit_bound_text(self.state, changed, " (rev 2)")
        patch_path = Path(self.directory.name) / "patch.json"
        patch_path.write_text(json.dumps({"objects": {group: [changed]}}, ensure_ascii=False), encoding="utf-8")

        result = _run("open_revision.py", self.path, "--patch", patch_path, "--write")

        self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8"))
        report = json.loads(result.stdout)
        self.assertTrue(report["written"])
        self.assertEqual((report["from_revision"], report["to_revision"]), (1, 2))
        self.assertEqual(report["changed"], [record_id])
        self.assertTrue(report["refreshed"])
        self.assertTrue(all(item["record_id"] == record_id for item in report["refreshed"]))
        written = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(validate_state_v2(written), [])
        self.assertEqual(written["approval"], {"status": "UNAPPROVED"})
        self.assertEqual(written["project"]["definition_status"], "READY_FOR_REVIEW")
        digest = approval_manifest_digest(build_approval_manifest_for_review(written))
        approve = _run("record_approval.py", self.path, "--revision", 2, "--manifest-digest", digest, "--at", APPROVED_AT, "--write")
        self.assertEqual(approve.returncode, 0, approve.stdout.decode("utf-8"))
        status = json.loads(_run("approval_status.py", self.path).stdout)
        self.assertEqual(status["approved_revisions"], [1, 2])

    def test_record_changed_outside_the_patch_blocks_the_write(self):
        _, _, record_id = _covered_binding(self.state)
        drifted = copy.deepcopy(self.state)
        _, record = _record(drifted, record_id)
        _edit_bound_text(drifted, record, " (silent edit)")

        candidate, report = open_revision(drifted, {})

        self.assertEqual(report["refreshed"], [])
        self.assertTrue(any(item["record_id"] == record_id and item["code"] == "authority_binding_hash_mismatch"
                            for item in report["unresolved"]))

    def test_superseded_record_still_bound_is_unresolved(self):
        _, _, record_id = _covered_binding(self.state)
        group, record = _record(self.state, record_id)
        retired = copy.deepcopy(record)
        retired["status"] = "SUPERSEDED"

        _, report = open_revision(self.state, {"objects": {group: [retired]}})

        self.assertTrue(any(item["record_id"] == record_id and item["code"] == "stale_authority_binding"
                            for item in report["unresolved"]))

    def test_cli_does_not_write_an_invalid_revision(self):
        _, _, record_id = _covered_binding(self.state)
        group, record = _record(self.state, record_id)
        retired = copy.deepcopy(record)
        retired["status"] = "SUPERSEDED"
        patch_path = Path(self.directory.name) / "patch.json"
        patch_path.write_text(json.dumps({"objects": {group: [retired]}}), encoding="utf-8")
        before = self.path.read_bytes()

        result = _run("open_revision.py", self.path, "--patch", patch_path, "--write")

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["written"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_cell_edits_add_bindings_by_stable_address(self):
        feature, axis, _ = _covered_binding(self.state)
        candidate, report = open_revision(self.state, {"cells": [
            {"cell": f"coverage[{feature}].cells.{axis}", "add": [{"record_id": "GOAL-001", "pointer": "/statement"}]},
        ]})
        cell = next(r for r in candidate["coverage"] if r["feature_id"] == feature)["cells"][axis]
        self.assertEqual(cell["authority_bindings"][-1]["record_id"], "GOAL-001")
        self.assertEqual(report["cells"], [f"coverage[{feature}].cells.{axis}"])

    def test_bad_cell_address_and_patch_keys_are_refused(self):
        with self.assertRaises(RevisionError) as bad_cell:
            open_revision(self.state, {"cells": [{"cell": "coverage[NOPE].cells.goal", "add": []}]})
        self.assertEqual(bad_cell.exception.error["code"], "unknown_cell")
        with self.assertRaises(RevisionError) as bad_key:
            open_revision(self.state, {"records": []})
        self.assertEqual(bad_key.exception.error["code"], "invalid_patch")

    def test_unapproved_base_revision_is_warned(self):
        patch_path = Path(self.directory.name) / "empty.json"
        patch_path.write_text("{}", encoding="utf-8")
        self.assertEqual(_run("open_revision.py", self.path, "--patch", patch_path, "--write").returncode, 0)

        second = json.loads(_run("open_revision.py", self.path, "--patch", patch_path).stdout)

        self.assertIn("revision 2 was never approved", second["warning"])
        self.assertFalse(second["written"])


class RefreshBindingsCliTest(unittest.TestCase):
    def test_lists_then_refreshes_only_accepted_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path, state = _approved_rev1(directory)
            _, _, record_id = _covered_binding(state)
            _, record = _record(state, record_id)
            _edit_bound_text(state, record, " (edited)")
            path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

            listed = _run("refresh_bindings.py", path)
            self.assertEqual(listed.returncode, 1)
            self.assertIn(record_id, {item["record_id"] for item in json.loads(listed.stdout)["unresolved"]})

            refreshed = _run("refresh_bindings.py", path, "--accept", record_id, "--write")
            self.assertEqual(refreshed.returncode, 0, refreshed.stdout.decode("utf-8"))
            self.assertTrue(json.loads(refreshed.stdout)["written"])
            self.assertEqual(json.loads(_run("refresh_bindings.py", path).stdout)["unresolved"], [])


if __name__ == "__main__":
    unittest.main()
