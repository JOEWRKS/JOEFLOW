import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))

import authority_binding_v2 as binding  # noqa: E402
from tests.v020_support import foundation_state, materiality  # noqa: E402


make_authority_binding = binding.make_authority_binding


def validate_product_coverage_bindings(state):
    return getattr(
        binding, "validate_product_coverage_bindings",
        lambda _: [{"code": "missing_product_binding_api"}],
    )(state)


def product_binding_metrics(state):
    return getattr(
        binding, "product_binding_metrics",
        lambda _: {key: 0 for key in (
            "invalid_authority_binding", "stale_authority_binding",
            "coverage_without_authority", "open_coverage_without_unknown",
            "unjustified_na_without_basis", "invalid_coverage_authority_type",
            "core_coverage_gaps", "specialist_binding_gaps",
        )},
    )(state)


CORE_AXES = (
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state",
    "data", "side_effect", "notification", "validation", "boundary",
    "persistence", "security", "privacy", "analytics", "acceptance",
)


def material_requirement():
    return {
        "id": "REQ-001", "status": "CURRENT", "statement": "Users submit a request.",
        "scope": "The material product workflow.", "ui_required": True,
        "materiality": materiality(classification="MATERIAL"),
    }


def state_with_authorities():
    state = foundation_state()
    state["objects"]["requirements"] = [material_requirement()]
    state["objects"]["rules"] = [{
        "id": "RULE-001", "status": "CURRENT", "statement": "The workflow is controlled.",
        "applies_to": [],
    }]
    state["objects"]["acceptance_criteria"] = [{
        "id": "AC-001", "status": "CURRENT", "assertion": "A valid request completes.",
    }]
    return state


def exact_core_cells(state, *, status="COVERED"):
    cells = {}
    for axis in CORE_AXES:
        record_id = "AC-001" if axis == "acceptance" else "REQ-001" if axis in {"goal", "happy_path"} else "RULE-001"
        pointer = "/assertion" if record_id == "AC-001" else "/statement"
        cells[axis] = {
            "status": status,
            "authority_bindings": [make_authority_binding(state, record_id, pointer)] if status == "COVERED" else [],
            "unknown_refs": [], "basis_bindings": [], "rationale": None,
        }
    return cells


def exact_core_coverage(state):
    return {"feature_id": "REQ-001", "cells": exact_core_cells(state)}


class CoreCoverageBindingV020Test(unittest.TestCase):
    def codes(self, state):
        return {error["code"] for error in validate_product_coverage_bindings(state)}

    def test_covered_cells_require_exact_axis_authority_proof(self):
        # Break caught: a bare COVERED claim being accepted without a record-relative proof.
        state = state_with_authorities()
        state["coverage"] = [{
            "feature_id": "REQ-001",
            "cells": {axis: {"status": "COVERED"} for axis in CORE_AXES},
        }]
        self.assertIn("invalid_core_coverage_cell", self.codes(state))
        self.assertEqual(product_binding_metrics(state)["coverage_without_authority"], len(CORE_AXES))

    def test_correct_type_pointer_and_hash_make_every_core_cell_valid(self):
        # Break caught: valid exact bindings being rejected or a Core axis accepting the wrong authority type.
        state = state_with_authorities()
        state["coverage"] = [exact_core_coverage(state)]
        self.assertEqual(validate_product_coverage_bindings(state), [])
        self.assertEqual(product_binding_metrics(state)["core_coverage_gaps"], 0)

    def test_binding_hash_lifecycle_type_and_pointer_fail_as_semantic_proof(self):
        # Break caught: stale, nonsemantic, or wrong-type values silently satisfying COVERED.
        state = state_with_authorities()
        state["coverage"] = [exact_core_coverage(state)]
        cases = []
        hash_drift = copy.deepcopy(state)
        hash_drift["coverage"][0]["cells"]["actor"]["authority_bindings"][0]["value_sha256"] = "0" * 64
        cases.append((hash_drift, "authority_binding_hash_mismatch", "invalid_authority_binding"))
        for status in ("SUPERSEDED", "STALE", "RETIRED"):
            stale = copy.deepcopy(state)
            stale["objects"]["acceptance_criteria"][0]["status"] = status
            cases.append((stale, "stale_authority_binding", "stale_authority_binding"))
        wrong_type = copy.deepcopy(state)
        wrong_type["coverage"][0]["cells"]["actor"]["authority_bindings"] = [make_authority_binding(wrong_type, "AC-001", "/assertion")]
        cases.append((wrong_type, "invalid_authority_binding_type", "invalid_coverage_authority_type"))
        wrong_acceptance = copy.deepcopy(state)
        wrong_acceptance["coverage"][0]["cells"]["acceptance"]["authority_bindings"] = [make_authority_binding(wrong_acceptance, "RULE-001", "/statement")]
        cases.append((wrong_acceptance, "invalid_authority_binding_type", "invalid_coverage_authority_type"))
        pointer = copy.deepcopy(state)
        pointer["coverage"][0]["cells"]["actor"]["authority_bindings"] = [make_authority_binding(pointer, "RULE-001", "/status")]
        cases.append((pointer, "nonsemantic_authority_binding_pointer", "invalid_authority_binding"))
        for candidate, code, metric in cases:
            with self.subTest(code=code):
                self.assertIn(code, self.codes(candidate))
                self.assertEqual(product_binding_metrics(candidate)[metric], 1)

    def test_open_and_na_cells_require_exact_unknown_or_basis_proof(self):
        # Break caught: OPEN without a current unknown or N/A without eligible exact basis being accepted.
        state = state_with_authorities()
        state["coverage"] = [exact_core_coverage(state)]
        state["coverage"][0]["cells"]["actor"] = {
            "status": "OPEN", "authority_bindings": [], "unknown_refs": [],
            "basis_bindings": [], "rationale": None,
        }
        self.assertEqual(product_binding_metrics(state)["open_coverage_without_unknown"], 1)
        state["coverage"][0]["cells"]["actor"]["unknown_refs"] = ["RULE-001"]
        self.assertEqual(product_binding_metrics(state)["open_coverage_without_unknown"], 1)
        state["coverage"][0]["cells"]["actor"] = {
            "status": "N/A", "authority_bindings": [], "unknown_refs": [],
            "basis_bindings": [], "rationale": None,
        }
        self.assertEqual(product_binding_metrics(state)["unjustified_na_without_basis"], 1)
        state["coverage"][0]["cells"]["actor"] = {
            "status": "N/A", "authority_bindings": [], "unknown_refs": [],
            "basis_bindings": [make_authority_binding(state, "EVD-900", "/claim")],
            "rationale": "The applicable evidence is candidate-only.",
        }
        state["evidence"][0]["source_kind"] = "DESIGN_ARTIFACT"
        self.assertEqual(product_binding_metrics(state)["unjustified_na_without_basis"], 1)

    def test_missing_or_duplicate_material_requirement_rows_are_core_gaps(self):
        # Break caught: material requirements losing their frozen 20-axis Core row without a gap.
        state = state_with_authorities()
        self.assertEqual(product_binding_metrics(state)["core_coverage_gaps"], 1)
        state["coverage"] = [exact_core_coverage(state), exact_core_coverage(state)]
        self.assertEqual(product_binding_metrics(state)["core_coverage_gaps"], 1)

    def test_malformed_non_target_core_row_still_requires_frozen_inventory(self):
        # Break caught: an extra Core row escaping inventory validation because it is not MATERIAL/CURRENT.
        state = state_with_authorities()
        state["coverage"] = [
            exact_core_coverage(state),
            {"feature_id": "REQ-999", "cells": {"actor": {"status": "COVERED"}}},
        ]
        errors = validate_product_coverage_bindings(state)
        self.assertIn("core_coverage_axis_inventory_mismatch", {error["code"] for error in errors})
        self.assertEqual(product_binding_metrics(state)["core_coverage_gaps"], 1)

    def test_malformed_second_duplicate_core_row_requires_exact_cell_shape(self):
        # Break caught: only the first duplicate Core row receiving exact five-key cell validation.
        state = state_with_authorities()
        malformed_second = exact_core_coverage(state)
        malformed_second["cells"]["actor"] = {"status": "COVERED"}
        state["coverage"] = [exact_core_coverage(state), malformed_second]
        errors = validate_product_coverage_bindings(state)
        self.assertIn("invalid_core_coverage_cell", {error["code"] for error in errors})
        self.assertEqual(product_binding_metrics(state)["coverage_without_authority"], 1)

    def test_core_row_identities_exactly_equal_current_material_requirements(self):
        # Break caught: unknown, historical, or non-material rows joining the canonical Core row set.
        base = state_with_authorities()
        base["coverage"] = [exact_core_coverage(base)]
        candidates = []

        unknown = copy.deepcopy(base)
        orphan = exact_core_coverage(unknown)
        orphan["feature_id"] = "REQ-999"
        unknown["coverage"].append(orphan)
        candidates.append(unknown)

        historical = copy.deepcopy(base)
        old_requirement = material_requirement()
        old_requirement.update({"id": "REQ-002", "status": "STALE"})
        historical["objects"]["requirements"].append(old_requirement)
        old_row = exact_core_coverage(historical)
        old_row["feature_id"] = "REQ-002"
        historical["coverage"].append(old_row)
        candidates.append(historical)

        non_material = copy.deepcopy(base)
        non_material_requirement = material_requirement()
        non_material_requirement.update({
            "id": "REQ-003",
            "materiality": materiality(classification="NON_MATERIAL"),
        })
        non_material["objects"]["requirements"].append(non_material_requirement)
        non_material_row = exact_core_coverage(non_material)
        non_material_row["feature_id"] = "REQ-003"
        non_material["coverage"].append(non_material_row)
        candidates.append(non_material)

        for candidate in candidates:
            with self.subTest(feature_id=candidate["coverage"][-1]["feature_id"]):
                self.assertIn("core_coverage_target_mismatch", self.codes(candidate))
                self.assertEqual(product_binding_metrics(candidate)["core_coverage_gaps"], 1)

    def test_core_row_requires_exact_feature_and_cells_keys(self):
        # Break caught: an extra row key allowing a noncanonical Core row shape into proof.
        state = state_with_authorities()
        row = exact_core_coverage(state)
        row["opaque"] = True
        state["coverage"] = [row]

        self.assertIn("invalid_core_coverage_row", self.codes(state))
        self.assertEqual(product_binding_metrics(state)["core_coverage_gaps"], 1)


if __name__ == "__main__":
    unittest.main()
