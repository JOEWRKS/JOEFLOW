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
sys.path.insert(0, str(SCRIPTS.parent))  # downstream_v2 package
sys.path.insert(0, str(ROOT))

from approval_v2 import approval_manifest_digest, compute_approval_manifest, definition_digest  # noqa: E402
from coverage_inheritance import TAG, compact_coverage, expand_coverage, inheritable_grill_axes, load_shapes  # noqa: E402
from grill_v2 import compile_active_grill_packs, load_grill_packs  # noqa: E402
from revision_v2 import apply_patch  # noqa: E402
from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402
from tests.test_semantic_closure_v020 import literal_approved_state, literal_ready_state  # noqa: E402
from tests.v020_support import establish_current_baseline  # noqa: E402


def codes(state):
    return {error["code"] for error in validate_state_v2(state)}


def action(state):
    return state["ux_coverage"][0]["actions"][0]


def _spec(cell):
    bindings = cell["authority_bindings"] or cell["basis_bindings"]
    return {"status": cell["status"], "unknown_refs": cell["unknown_refs"], "rationale": cell["rationale"],
            "bind": [{"record_id": b["record_id"], "pointer": b["pointer"]} for b in bindings]}


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
        for axis in load_shapes()["navigate"]["not_applicable"]:
            self.assertEqual(expanded["cells"][axis][TAG], "shape:navigate")
            self.assertEqual(expanded["cells"][axis]["status"], "N/A")
            self.assertNotIn(TAG, action(expand_coverage(state, strip=True))["cells"][axis])

    def test_a_rows_patch_carries_shape_and_default_authority(self):
        # The patch route is the only way an author writes a new row; a declaration must survive it.
        state = literal_ready_state()
        row = state["ux_coverage"][0]
        trimmed = copy.deepcopy(state)
        trimmed["ux_coverage"] = []
        spec = {"screen_id": row["screen_id"], "states": {a: _spec(c) for a, c in row["states"].items()}, "actions": []}
        for act in row["actions"]:
            cells = {a: _spec(c) for a, c in act["cells"].items()}
            action_spec = {"key": act["key"], "cells": cells}
            if act is row["actions"][0]:
                action_spec["shape"] = "navigate"
                default = _spec(act["cells"]["entry"])["bind"]
                action_spec["default_authority"] = default
                for axis in load_shapes()["navigate"]["not_applicable"]:
                    cells.pop(axis, None)
                for axis, cell in list(cells.items()):
                    if cell["status"] == "COVERED" and cell["bind"] == default:
                        del cells[axis]
            spec["actions"].append(action_spec)
        report = apply_patch(trimmed, {"rows": [{"ux_coverage": spec}]})
        self.assertEqual(report["rows"], [f"ux_coverage[{row['screen_id']}]"])
        self.assertEqual(codes(trimmed), set())
        built = trimmed["ux_coverage"][0]["actions"][0]
        self.assertEqual(built["shape"], "navigate")
        self.assertTrue(all("value_sha256" in b for b in built["default_authority"]))
        expanded = expand_coverage(trimmed)["ux_coverage"][0]["actions"][0]
        self.assertEqual(expanded["cells"]["validation"][TAG], "shape:navigate")
        self.assertEqual(expanded["cells"]["entry"][TAG], "row")
        self.assertEqual(set(expanded["cells"]), set(action(state)["cells"]))

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
        self.assertEqual(action(expand_coverage(state))["cells"]["validation"], act["cells"]["validation"])


def async_ready_state():
    """literal_ready_state plus an ACTIVE ASYNC domain: SURF-002 (ASYNC_PROCESS) and its fully answered row."""
    state = literal_ready_state()
    auth = state["surface_manifest"]["grill_profile"]["AUTH"]
    surface = copy.deepcopy(state["surface_manifest"]["records"][0])
    surface.update({"id": "SURF-002", "kind": "ASYNC_PROCESS", "name": "Background scoring"})
    state["surface_manifest"]["records"].append(surface)
    state["surface_manifest"]["grill_profile"]["ASYNC"] = {"status": "ACTIVE", "surface_refs": ["SURF-002"], "unknown_refs": [],
                                                           "basis_refs": list(auth["basis_refs"]), "rationale": None}
    instance = next(i for i in compile_active_grill_packs(state) if i["pack_id"] == "GRILL-ASYNC-1")
    axes = [axis["id"] for axis in load_grill_packs()["GRILL-ASYNC-1"]["axes"]]
    addressed = state["grill_coverage"][0]["axes"]["registration"]
    state["grill_coverage"].append({"target_ref": "SURF-002", "pack_id": "GRILL-ASYNC-1", "pack_version": instance["version"],
                                    "pack_digest": instance["digest"], "axes": {axis: copy.deepcopy(addressed) for axis in axes}})
    return establish_current_baseline(state)


class AsyncProfileInheritanceTest(unittest.TestCase):
    def test_declared_local_pure_execution_implies_four_na_axes(self):
        state = async_ready_state()
        self.assertEqual(codes(state), set())
        profile = state["surface_manifest"]["grill_profile"]["ASYNC"]
        profile["execution"] = "LOCAL_PURE"
        row = state["grill_coverage"][1]
        implied = inheritable_grill_axes(state)["GRILL-ASYNC-1"]
        self.assertEqual(set(implied), {"polling", "reconciliation", "idempotency", "duplicate_execution"})
        for axis in implied:
            del row["axes"][axis]
        self.assertEqual(codes(state), set())
        expanded = expand_coverage(state)["grill_coverage"][1]["axes"]
        self.assertEqual(expanded["polling"]["status"], "N/A")
        self.assertEqual(expanded["polling"][TAG], "profile:ASYNC.LOCAL_PURE")
        stripped = expand_coverage(state, strip=True)
        self.assertNotIn(TAG, stripped["grill_coverage"][1]["axes"]["polling"])
        self.assertNotIn("execution", stripped["surface_manifest"]["grill_profile"]["ASYNC"])
        self.assertEqual(definition_digest(stripped), definition_digest(state))

    def test_declaration_needs_an_active_known_value_and_covers_only_its_axes(self):
        state = async_ready_state()
        profile = state["surface_manifest"]["grill_profile"]["ASYNC"]
        profile["execution"] = "REMOTE"
        self.assertIn("invalid_grill_profile_declaration", codes(state))
        profile["execution"] = "LOCAL"
        self.assertEqual(codes(state), set())
        del state["grill_coverage"][1]["axes"]["idempotency"]
        self.assertIn("grill_pack_axis_inventory_mismatch", codes(state))
        state["surface_manifest"]["grill_profile"]["MONEY"]["execution"] = "LOCAL"
        self.assertIn("invalid_grill_profile_declaration", codes(state))


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

    def test_downstream_seeds_are_identical_for_the_compact_twin(self):
        # downstream_v2 is a frozen tree; v2.1 callers expand the state at the boundary.
        from downstream_v2.seeds import build_closed_source_seed_inventory
        state, compact, _ = self.compact_fixture()
        self.assertEqual(build_closed_source_seed_inventory(expand_coverage(compact, strip=True)),
                         build_closed_source_seed_inventory(state))

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
