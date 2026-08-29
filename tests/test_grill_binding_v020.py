import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "joewrks-product-definition" / "scripts"))

import grill_v2 as grill  # noqa: E402
import authority_binding_v2 as binding  # noqa: E402
from tests.test_grill_packs_v020 import activate, base_state, current_rule, current_surface  # noqa: E402


make_authority_binding = binding.make_authority_binding


def validate_product_coverage_bindings(state):
    return getattr(
        binding, "validate_product_coverage_bindings",
        lambda _: [{"code": "missing_product_binding_api"}],
    )(state)


def product_binding_metrics(state):
    return getattr(
        binding, "product_binding_metrics",
        lambda _: {"specialist_binding_gaps": 0},
    )(state)


def specialist_state():
    state = base_state()
    state["surface_manifest"]["records"] = [current_surface()]
    activate(state, "AUTH", "SURF-001")
    state["objects"]["rules"] = [current_rule()]
    pack = grill.load_grill_packs()["GRILL-AUTH-1"]
    basis = make_authority_binding(state, "EVD-900", "/claim")
    state["grill_coverage"] = [{
        "target_ref": "SURF-001", "pack_id": "GRILL-AUTH-1",
        "pack_version": pack["version"], "pack_digest": grill.canonical_pack_digest(pack),
        "axes": {
            axis["id"]: {
                "status": "N/A", "authority_bindings": [], "unknown_refs": [],
                "basis_bindings": [copy.deepcopy(basis)],
                "rationale": "This axis does not apply to the classified surface.",
            }
            for axis in pack["axes"]
        },
    }]
    return state


class GrillBindingV020Test(unittest.TestCase):
    def codes(self, state):
        return {error["code"] for error in validate_product_coverage_bindings(state)}

    def test_specialist_addressed_rejects_broad_refs_and_accepts_exact_binding(self):
        # Break caught: M3 broad authority_refs being mistaken for M4 semantic proof.
        state = specialist_state()
        cell = state["grill_coverage"][0]["axes"]["registration"]
        cell.update({"status": "ADDRESSED", "authority_refs": ["RULE-900"]})
        cell.pop("authority_bindings")
        self.assertIn("invalid_specialist_coverage_cell", self.codes(state))

        valid = specialist_state()
        cell = valid["grill_coverage"][0]["axes"]["registration"]
        cell.update({
            "status": "ADDRESSED",
            "authority_bindings": [make_authority_binding(valid, "RULE-900", "/statement")],
            "basis_bindings": [], "unknown_refs": [], "rationale": None,
        })
        self.assertEqual(validate_product_coverage_bindings(valid), [])

    def test_specialist_binding_failure_is_separate_from_m3_activation_completeness(self):
        # Break caught: exact proof failures changing the M3 active-pack inventory metric.
        state = specialist_state()
        cell = state["grill_coverage"][0]["axes"]["registration"]
        cell.update({
            "status": "ADDRESSED",
            "authority_bindings": [make_authority_binding(state, "RULE-900", "/statement")],
            "basis_bindings": [], "unknown_refs": [], "rationale": None,
        })
        invalid = copy.deepcopy(state)
        invalid["objects"]["rules"][0]["status"] = "STALE"
        self.assertEqual(grill.grill_pack_metrics(invalid)["active_grill_pack_gaps"], 0)
        self.assertEqual(product_binding_metrics(invalid)["specialist_binding_gaps"], 1)

        hash_drift = copy.deepcopy(state)
        hash_drift["grill_coverage"][0]["axes"]["registration"]["authority_bindings"][0]["value_sha256"] = "0" * 64
        self.assertEqual(product_binding_metrics(hash_drift)["specialist_binding_gaps"], 1)

        wrong_type = copy.deepcopy(state)
        wrong_type["objects"]["goals"] = [{"id": "GOAL-900", "status": "CURRENT", "statement": "A goal."}]
        wrong_type["grill_coverage"][0]["axes"]["registration"]["authority_bindings"] = [make_authority_binding(wrong_type, "GOAL-900", "/statement")]
        self.assertEqual(product_binding_metrics(wrong_type)["invalid_coverage_authority_type"], 1)

    def test_specialist_na_uses_exact_basis_bindings_and_open_keeps_m3_origin_rule(self):
        # Break caught: broad basis refs bypassing proof or OPEN axes bypassing their exact M3 origin.
        state = specialist_state()
        cell = state["grill_coverage"][0]["axes"]["registration"]
        cell["basis_refs"] = ["EVD-900"]
        cell.pop("basis_bindings")
        self.assertIn("invalid_specialist_coverage_cell", self.codes(state))

        opened = specialist_state()
        axis = opened["grill_coverage"][0]["axes"]["registration"]
        axis.update({"status": "OPEN", "authority_bindings": [], "basis_bindings": [], "unknown_refs": ["UNK-901"], "rationale": None})
        opened["objects"]["unknowns"] = [{"id": "UNK-901", "status": "OPEN", "origin": {"kind": "MANUAL"}}]
        self.assertIn("umbrella_unknown_compression", {error["code"] for error in grill.validate_grill_coverage(opened)})


if __name__ == "__main__":
    unittest.main()
