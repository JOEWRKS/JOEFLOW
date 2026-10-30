import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT))

from approval_v2 import definition_digest  # noqa: E402
from projection_check import check  # noqa: E402
from update_projection import adopt, facts, refresh  # noqa: E402
from tests.test_semantic_closure_v020 import literal_approved_state  # noqa: E402


def run(*args):
    result = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "update_projection.py"), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return json.loads(result.stdout)


class UpdateProjectionTest(unittest.TestCase):
    def setUp(self):
        self.state = literal_approved_state()
        self.facts = facts(self.state)
        self.spec = (SKILL / "templates" / "master-planning-spec.md").read_text(encoding="utf-8")
        self.review = (SKILL / "templates" / "planning-review-core.html").read_text(encoding="utf-8")

    def test_template_blocks_are_regenerated_and_pass_projection_check(self):
        spec, notes = refresh(self.spec, self.facts, self.state, html=False)
        review, _ = refresh(self.review, self.facts, self.state, html=True)
        self.assertIn("identity block regenerated", notes)
        self.assertIn("source map block regenerated", notes)
        self.assertIn(f"Definition digest: `{definition_digest(self.state)}`", spec)
        self.assertIn(f"<code>{definition_digest(self.state)}</code>", review)
        self.assertIn("| Requirements (`/objects/requirements`) | REQ-001 |", spec)
        report = check(self.state, spec, review, {"REQ"})
        self.assertEqual(report["spec"]["stale_identity"], [])
        self.assertEqual(report["review"]["stale_identity"], [])

    def test_second_run_changes_nothing(self):
        once, _ = refresh(self.spec, self.facts, self.state, html=False)
        twice, _ = refresh(once, self.facts, self.state, html=False)
        self.assertEqual(once, twice)

    def test_label_lines_without_blocks_are_updated_and_trailing_text_is_flagged(self):
        text = "# Spec\n\n- Revision: `0` (approved yesterday)\n- Definition digest: `old`\n"
        updated, notes = refresh(text, self.facts, self.state, html=False)
        self.assertIn("- Revision: `1` (approved yesterday)", updated)
        self.assertIn(f"- Definition digest: `{definition_digest(self.state)}`", updated)
        self.assertTrue(any(note.startswith("line 3:") for note in notes))
        self.assertFalse(any(note.startswith("line 4:") for note in notes))

    def test_adopt_wraps_consecutive_identity_lines_once(self):
        text = "# Spec\n\n- Revision: `0` (old note)\n- Definition digest: `old`\n- Status: `OPEN`\n\nBody\n"
        adopted, changed = adopt(text)
        self.assertTrue(changed)
        self.assertIn("<!-- JOEFLOW:IDENTITY:BEGIN -->\n- Revision: `0` (old note)", adopted)
        self.assertIn("- Status: `OPEN`\n<!-- JOEFLOW:IDENTITY:END -->\n\nBody", adopted)
        self.assertEqual(adopt(adopted), (adopted, False))
        refreshed, _ = refresh(text, self.facts, self.state, html=False, adopt_identity=True)
        self.assertNotIn("old note", refreshed)

    def test_cli_is_read_only_without_write_and_lists_rows_to_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "state.json").write_text(json.dumps(self.state), encoding="utf-8")
            spec = base / "MASTER_PLANNING_SPEC.md"
            spec.write_text(self.spec + "\n| REQ-001 | condensed text |\n", encoding="utf-8")
            before = spec.read_bytes()
            report = run(base / "state.json", "--spec", spec)
            self.assertEqual(spec.read_bytes(), before)
            self.assertGreater(report["changed_lines"]["spec"], 0)
            rows = {row["id"]: row for row in report["records_to_edit_by_hand"]}
            self.assertEqual(rows["REQ-001"]["category"], "added")
            self.assertEqual(len(rows["REQ-001"]["lines"]["spec"]), 1)
            run(base / "state.json", "--spec", spec, "--write")
            self.assertNotEqual(spec.read_bytes(), before)
            self.assertEqual(run(base / "state.json", "--spec", spec)["changed_lines"]["spec"], 0)


if __name__ == "__main__":
    unittest.main()
