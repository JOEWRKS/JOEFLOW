"""Compact coverage rows (U2-12): shape and default_authority declarations imply omitted cells."""
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
sys.path.insert(0, str(ROOT))

from approval_v2 import approval_manifest_digest, compute_approval_manifest, definition_digest  # noqa: E402
from coverage_inheritance import TAG, compact_coverage, expand_coverage, load_shapes  # noqa: E402
from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402
from tests.test_semantic_closure_v020 import literal_approved_state, literal_ready_state  # noqa: E402


def codes(state):
    return {error["code"] for error in validate_state_v2(state)}


def action(state):
    return state["ux_coverage"][0]["actions"][0]


class ShapeInheritanceTest(unittest.TestCase):
    # An inherited N/A has no basis or rationale, so declaring a shape changes the digest of an
    # already approved definition; these tests use the unapproved READY_FOR_REVIEW fixture.
    def test_shape_axes_may_be_omitted_and_expand_to_tagged_na(self):
        state = literal_ready_state()
        act = action(state)
        act["shape"] = "navigate"
        for axis in load_shapes()["navigate"]["not_applicable"]:
            del act["cells"][axis]
        self.assertEqual(codes(state), set())
        expanded = action(expand_coverage(state))
        self.assertEqual(expanded["cells"]["undo"][TAG], "shape:navigate")
        self.assertEqual(expanded["cells"]["undo"]["status"], "N/A")
        self.assertNotIn(TAG, action(expand_coverage(state, strip=True))["cells"]["undo"])

    def test_unknown_shape_and_unrelated_omission_are_errors(self):
        state = literal_ready_state()
        act = action(state)
        act["shape"] = "made_up"
        self.assertIn("unknown_action_shape", codes(state))
        act["shape"] = "navigate"
        del act["cells"]["submit"]
        self.assertIn("action_axis_inventory_mismatch", codes(state))

    def test_written_cell_wins_over_shape(self):
        state = literal_ready_state()
        act = action(state)
        act["shape"] = "navigate"
        self.assertEqual(action(expand_coverage(state))["cells"]["undo"], act["cells"]["undo"])


class DefaultAuthorityTest(unittest.TestCase):
    def compact_fixture(self):
        state = literal_approved_state()
        compact, removed = compact_coverage(state)
        return state, compact, removed

    def test_compact_expands_to_the_original_and_keeps_every_digest(self):
        state, compact, removed = self.compact_fixture()
        self.assertGreater(sum(removed.values()), 0)
        self.assertEqual(expand_coverage(compact, strip=True), state)
        self.assertEqual(definition_digest(compact), definition_digest(state))
        self.assertEqual(approval_manifest_digest(compute_approval_manifest(compact)),
                         approval_manifest_digest(compute_approval_manifest(state)))
        self.assertEqual(validate_state_v2(compact), [])
        self.assertTrue(evaluate_closure_v2(compact)["closed"])

    def test_inherited_cell_must_fit_the_axis_allowed_types(self):
        state = literal_ready_state()
        row = state["coverage"][0]
        # AC records are allowed on the acceptance axis only; as a row default they fail elsewhere.
        row["default_authority"] = copy.deepcopy(row["cells"]["acceptance"]["authority_bindings"])
        del row["cells"]["actor"]
        errors = validate_state_v2(state)
        self.assertTrue(any(e["path"] == "coverage[0].cells.actor" and "default_authority" in e["message"] for e in errors), errors)

    def test_omission_without_a_declaration_is_still_a_gap(self):
        state = literal_ready_state()
        del state["coverage"][0]["cells"]["actor"]
        self.assertIn("core_coverage_axis_inventory_mismatch", codes(state))

    def test_default_authority_is_rehashed_with_its_record(self):
        state, compact, _ = self.compact_fixture()
        declared = next(r for r in compact["coverage"] + compact["ux_coverage"] if "default_authority" in r)
        binding = declared["default_authority"][0]
        group = {"REQ": "requirements", "RULE": "rules", "FLOW": "flows", "SCR": "screens", "STATE": "states", "AC": "acceptance_criteria"}[binding["record_id"].split("-")[0]]
        record = next(r for r in compact["objects"][group] if r["id"] == binding["record_id"])
        field = binding["pointer"].strip("/")
        patch = {"objects": {group: [{**record, field: record[field] + " (changed)"}]}}
        with tempfile.TemporaryDirectory() as directory:
            path, patch_path = Path(directory) / "state.json", Path(directory) / "patch.json"
            path.write_text(json.dumps(compact), encoding="utf-8")
            patch_path.write_text(json.dumps(patch), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "open_revision.py"), str(path), "--patch", str(patch_path), "--write"],
                                    capture_output=True, text=True, encoding="utf-8")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, json.dumps(report.get("validation_errors"), ensure_ascii=False)[:1500])
            written = json.loads(path.read_text(encoding="utf-8"))
        after = next(r for r in written["coverage"] + written["ux_coverage"] if "default_authority" in r)["default_authority"][0]
        self.assertNotEqual(after["value_sha256"], binding["value_sha256"])
        self.assertEqual(validate_state_v2(written), [])


if __name__ == "__main__":
    unittest.main()
