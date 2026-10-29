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

from approval_v2 import definition_digest  # noqa: E402
from projection_check import check, draft  # noqa: E402
from tests.test_revision_v020 import _approved_rev1, _covered_binding, _record  # noqa: E402

TYPES = {"REQ", "RULE", "FLOW", "SCR", "STATE", "DATA", "INT", "AC", "TASK"}


def _spec_for(state, *extra_ids):
    approval = state["approval"]
    return (
        f"- Revision: `{state['project']['definition_revision']}`\n"
        f"- Definition digest: `{definition_digest(state)}`\n"
        f"- Approval Manifest digest: `{approval['approved_manifest_digest']}`\n"
        + "".join(f"| {record_id} | text |\n" for record_id in extra_ids)
    )


class ProjectionCheckTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path, self.state = _approved_rev1(self.directory.name)

    def test_current_identity_and_all_added_records_pass(self):
        added = [r["id"] for g in self.state["objects"].values() for r in g
                 if isinstance(r, dict) and r.get("id", "").split("-")[0] in TYPES]

        report = check(self.state, _spec_for(self.state, *added), _spec_for(self.state), TYPES)

        self.assertTrue(report["ok"], report)
        self.assertEqual(report["spec"]["stale_identity"], [])
        self.assertEqual(report["review"]["stale_identity"], [])

    def test_stale_identity_and_missing_records_are_reported(self):
        spec ="- Revision: `1`\nwidth 7px\n"

        report = check(self.state, spec, spec.replace("1", "x"), TYPES)

        self.assertFalse(report["ok"])
        self.assertIn("revision 1 is not mentioned", report["review"]["stale_identity"])
        self.assertTrue(any("definition_digest" in f for f in report["spec"]["stale_identity"]))
        self.assertTrue(report["spec"]["missing_added_records"])

    def test_bare_number_does_not_count_as_revision(self):
        report = check(self.state, "padding 1px\n", None, TYPES)
        self.assertIn("revision 1 is not mentioned", report["spec"]["stale_identity"])

    def test_changed_records_since_previous_approval_are_listed_to_reread(self):
        _, _, record_id = _covered_binding(self.state)
        group, record = _record(self.state, record_id)
        patch = Path(self.directory.name) / "patch.json"
        changed = copy.deepcopy(record)
        for key in ("statement", "assertion", "description"):
            if isinstance(changed.get(key), str):
                changed[key] += " (rev 2)"
        patch.write_text(json.dumps({"objects": {group: [changed]}}, ensure_ascii=False), encoding="utf-8")
        run = lambda *a: subprocess.run([sys.executable, str(SCRIPTS / a[0]), *map(str, a[1:])], cwd=ROOT, capture_output=True)
        self.assertEqual(run("open_revision.py", self.path, "--patch", patch, "--write").returncode, 0)
        state = json.loads(self.path.read_text(encoding="utf-8"))

        report = check(state, f"rev 2 mentions {record_id}", None, TYPES)

        self.assertEqual(report["compared_with_revision"], 1)
        self.assertIn(record_id, report["spec"]["changed_records_to_reread"])
        self.assertIn(f"`{record_id}`", draft(state))

    def test_cli_exit_codes(self):
        spec = Path(self.directory.name) / "spec.md"
        spec.write_text("nothing here", encoding="utf-8")
        run = lambda *a: subprocess.run([sys.executable, str(SCRIPTS / "projection_check.py"), *map(str, a)], cwd=ROOT, capture_output=True)
        self.assertEqual(run(self.path, "--spec", spec).returncode, 1)
        self.assertEqual(run(self.path, "--spec", spec, "--draft").returncode, 0)
        self.assertEqual(run(self.path, "--spec", spec.with_name("missing.md")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
