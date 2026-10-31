import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))
sys.path.insert(0, str(ROOT))

from draft_freeze import Drafter, _cells_of  # noqa: E402
from revision_v2 import RevisionError, apply_patch, open_revision  # noqa: E402
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_semantic_closure_v020 import literal_approved_state  # noqa: E402


def as_spec(cell):
    bindings = cell["authority_bindings"] or cell["basis_bindings"]
    return {"status": cell["status"], "unknown_refs": cell["unknown_refs"], "rationale": cell["rationale"],
            "bind": [{"record_id": b["record_id"], "pointer": b["pointer"]} for b in bindings]}


class RowsPatchTest(unittest.TestCase):
    def test_a_removed_core_row_is_rebuilt_exactly_from_cell_specs(self):
        state = literal_approved_state()
        row = state["coverage"][0]
        trimmed = copy.deepcopy(state)
        trimmed["coverage"] = []
        spec = {"coverage": {"feature_id": row["feature_id"], "cells": {a: as_spec(c) for a, c in row["cells"].items()}}}
        report = apply_patch(trimmed, {"rows": [spec]})
        self.assertEqual(report["rows"], [f"coverage[{row['feature_id']}]"])
        self.assertEqual(trimmed["coverage"], state["coverage"])

    def test_a_second_row_for_the_same_target_is_refused(self):
        state = literal_approved_state()
        row = state["coverage"][0]
        spec = {"coverage": {"feature_id": row["feature_id"], "cells": {}}}
        with self.assertRaises(RevisionError):
            apply_patch(copy.deepcopy(state), {"rows": [spec]})

    def test_patches_without_rows_report_as_before(self):
        self.assertNotIn("rows", apply_patch(literal_approved_state(), {}))


class DraftFreezeTest(unittest.TestCase):
    def setUp(self):
        self.state = literal_approved_state()
        self.bare = copy.deepcopy(self.state)
        self.bare["coverage"], self.bare["ux_coverage"] = [], []

    def drafted(self):
        return {address: cell for spec in Drafter(self.bare).missing_rows() for address, cell in _cells_of(spec)}

    def test_draft_has_the_exact_inventory_of_the_missing_rows(self):
        drafted = self.drafted()
        original = {address for table in ("coverage", "ux_coverage") for row in self.state[table]
                    for address, _ in _cells_of({table: row})}
        # The fixture marks PERMISSION N/A, so its two UX axes are inherited and left out.
        inherited = {a for a in original if a.endswith(".permission_denied") or a.endswith(".cells.permission")
                     and a.startswith("ux_coverage")}
        self.assertEqual(set(drafted), original - inherited)

    def test_only_graph_decided_cells_are_filled_and_the_rest_need_a_decision(self):
        drafted = self.drafted()
        filled = {a: c for a, c in drafted.items() if c["status"] != "DECIDE"}
        self.assertTrue(filled)
        for address, cell in filled.items():
            self.assertEqual(cell["why"], "follows from linked records", address)
        acceptance = drafted["coverage[REQ-001].cells.acceptance"]
        self.assertEqual([b["record_id"] for b in acceptance["bind"]],
                         [a["id"] for a in self.state["objects"]["acceptance_criteria"] if "REQ-001" in a["requirement_refs"]])

    def test_every_drafted_action_asks_for_its_shape(self):
        for spec in Drafter(self.bare).missing_rows():
            for action in spec.get("ux_coverage", {}).get("actions", []):
                self.assertEqual(action["shape"], "DECIDE")

    def test_an_unsettled_draft_cannot_be_applied(self):
        rows = Drafter(self.bare).missing_rows()
        candidate, _ = open_revision(self.bare, {"rows": rows}, status="READY_FOR_REVIEW")
        self.assertTrue(any(e["code"].startswith("invalid_") for e in validate_state_v2(candidate)))


if __name__ == "__main__":
    unittest.main()
