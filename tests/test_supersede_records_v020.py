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

from revision_v2 import open_revision  # noqa: E402
from supersede_records import supersede  # noqa: E402
from tests.test_revision_v020 import _approved_rev1, _covered_binding, _record  # noqa: E402


def _run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          cwd=ROOT, capture_output=True, check=False)


def _replacement(state, old_id):
    """A new CURRENT record copied from old_id under a new ID, with changed bound text."""
    group, old = _record(state, old_id)
    new = copy.deepcopy(old)
    new["id"] = f"{old_id.split('-')[0]}-900"
    for key in ("statement", "assertion", "description", "purpose"):
        if isinstance(new.get(key), str):
            new[key] += " (replaced)"
    return group, new


class SupersedeRecordsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path, self.state = _approved_rev1(self.directory.name)

    def test_bound_record_moves_bindings_and_revision_validates(self):
        feature, axis, old_id = _covered_binding(self.state)
        group, new = _replacement(self.state, old_id)
        patch = {"objects": {group: [new]}}

        report = supersede(self.state, patch, {old_id: new["id"]})
        candidate, revision = open_revision(self.state, patch)

        self.assertEqual(report["superseded"], [{"id": old_id, "superseded_by": new["id"]}])
        self.assertIn(f"coverage[{feature}].cells.{axis}", report["cells"])
        self.assertEqual(revision["unresolved"], [])
        cell = next(r for r in candidate["coverage"] if r["feature_id"] == feature)["cells"][axis]
        bound = {b["record_id"] for b in cell["authority_bindings"]}
        self.assertIn(new["id"], bound)
        self.assertNotIn(old_id, bound)
        _, old = _record(candidate, old_id)
        self.assertEqual((old["status"], old["superseded_by"]), ("SUPERSEDED", new["id"]))

    def test_reference_fields_move_but_provenance_and_free_text_stay(self):
        state = copy.deepcopy(self.state)
        _, _, old_id = _covered_binding(state)
        group, new = _replacement(state, old_id)
        holder = state["objects"]["unknowns"][0]
        holder["affects"] = list(holder.get("affects", [])) + [old_id]
        holder["resolved_by"] = list(holder.get("resolved_by", [])) + [old_id]
        holder["options"][0]["consequences"] = [old_id]
        patch = {"objects": {group: [new]}}

        report = supersede(state, patch, {old_id: new["id"]})

        rewritten = next(u for u in patch["objects"]["unknowns"] if u["id"] == holder["id"])
        self.assertIn(new["id"], rewritten["affects"])
        self.assertNotIn(old_id, rewritten["affects"])
        self.assertIn(old_id, rewritten["resolved_by"])
        self.assertEqual(rewritten["options"][0]["consequences"], [old_id])
        self.assertIn({"id": holder["id"], "field": "resolved_by", "refs": [old_id]}, report["provenance_to_review"])

    def test_missing_new_record_is_refused(self):
        _, _, old_id = _covered_binding(self.state)
        with self.assertRaises(ValueError):
            supersede(self.state, {}, {old_id: "RULE-999"})

    def test_cli_extends_patch_for_open_revision(self):
        _, _, old_id = _covered_binding(self.state)
        group, new = _replacement(self.state, old_id)
        patch_path = Path(self.directory.name) / "patch.json"
        patch_path.write_text(json.dumps({"objects": {group: [new]}}, ensure_ascii=False), encoding="utf-8")

        result = _run("supersede_records.py", self.path, "--patch", patch_path, "--replace", f"{old_id}={new['id']}")
        self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8"))
        opened = _run("open_revision.py", self.path, "--patch", patch_path, "--write")

        report = json.loads(opened.stdout)
        self.assertEqual(opened.returncode, 0, json.dumps(report["validation_errors"], ensure_ascii=False)[:1500])
        self.assertTrue(report["written"])


if __name__ == "__main__":
    unittest.main()
