import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from authority_binding_v2 import canonical_record_index, resolve_record_pointer, sha256_json  # noqa: E402
from downstream_v2.authority import DownstreamV2Error  # noqa: E402
from downstream_v2.seeds import (  # noqa: E402
    build_source_seed_inventory,
    source_seed_index,
    source_seed_inventory_digest,
    verify_source_seed,
)
from tests.downstream_v2_support import closed_v2_state, source_seed_by_location  # noqa: E402


class SourceSeedTests(unittest.TestCase):
    def assert_seed_invalid(self, state, seed):
        with self.assertRaises(DownstreamV2Error):
            verify_source_seed(state, seed)

    def test_all_and_only_positive_m4_bindings_become_seeds(self):
        seeds = build_source_seed_inventory(closed_v2_state())
        self.assertEqual(len(seeds), 59)
        self.assertEqual(
            {scope: sum(seed["location"]["scope"] == scope for seed in seeds) for scope in ("CORE", "GRILL", "UX_STATE", "UX_ACTION")},
            {"CORE": 20, "GRILL": 1, "UX_STATE": 16, "UX_ACTION": 22},
        )
        state = closed_v2_state()
        state["coverage"][0]["cells"]["actor"] = {
            "status": "OPEN", "authority_bindings": [], "unknown_refs": ["UNK-001"], "basis_bindings": [], "rationale": None,
        }
        state["ux_coverage"][0]["states"]["default"] = {
            "status": "N/A", "authority_bindings": [], "unknown_refs": [],
            "basis_bindings": state["grill_coverage"][0]["axes"]["verification"]["basis_bindings"],
            "rationale": "Not applicable.",
        }
        self.assertEqual(len(build_source_seed_inventory(state)), 57)

    def test_inventory_is_deterministic_sorted_and_order_independent(self):
        state = closed_v2_state()
        first = build_source_seed_inventory(state)
        second = build_source_seed_inventory(copy.deepcopy(state))
        reordered = copy.deepcopy(state)
        reordered["coverage"][0]["cells"] = dict(reversed(list(reordered["coverage"][0]["cells"].items())))
        reordered["ux_coverage"][0]["states"] = dict(reversed(list(reordered["ux_coverage"][0]["states"].items())))
        reordered["ux_coverage"][0]["actions"][0]["cells"] = dict(reversed(list(reordered["ux_coverage"][0]["actions"][0]["cells"].items())))
        self.assertEqual(first, second)
        self.assertEqual(first, build_source_seed_inventory(reordered))
        self.assertEqual([seed["seed_key"] for seed in first], sorted(seed["seed_key"] for seed in first))
        self.assertEqual(json.dumps(first, sort_keys=True, separators=(",", ":")), json.dumps(second, sort_keys=True, separators=(",", ":")))

    def test_each_seed_carries_the_exact_resolved_m4_value_and_hash(self):
        state = closed_v2_state()
        records = canonical_record_index(state)
        for seed in build_source_seed_inventory(state):
            with self.subTest(seed=seed["seed_key"]):
                record_type, record = records[seed["record_id"]]
                self.assertEqual(seed["record_type"], record_type)
                self.assertEqual(seed["value"], resolve_record_pointer(record, seed["pointer"]))
                self.assertEqual(seed["value_sha256"], sha256_json(seed["value"]))
                self.assertEqual(verify_source_seed(state, seed), seed)

    def test_verification_fails_closed_for_source_or_location_drift(self):
        state = closed_v2_state()
        seed = source_seed_by_location(build_source_seed_inventory(state), scope="UX_ACTION", owner_ref="SCR-001", axis="submit", action_key="submit")
        value_changed = copy.deepcopy(state)
        value_changed["objects"]["flows"][0]["paths"] = ["A changed path."]
        self.assert_seed_invalid(value_changed, seed)
        stale = copy.deepcopy(state)
        stale["objects"]["flows"][0]["status"] = "STALE"
        self.assert_seed_invalid(stale, seed)
        removed = copy.deepcopy(state)
        removed["ux_coverage"][0]["actions"][0]["cells"]["submit"]["authority_bindings"] = []
        self.assert_seed_invalid(removed, seed)
        open_location = copy.deepcopy(state)
        open_location["ux_coverage"][0]["actions"][0]["cells"]["submit"]["status"] = "OPEN"
        self.assert_seed_invalid(open_location, seed)
        wrong_owner = copy.deepcopy(seed)
        wrong_owner["location"]["owner_ref"] = "SCR-999"
        self.assert_seed_invalid(state, wrong_owner)
        wrong_action = copy.deepcopy(seed)
        wrong_action["location"]["action_key"] = "save"
        self.assert_seed_invalid(state, wrong_action)
        grill_seed = source_seed_by_location(build_source_seed_inventory(state), scope="GRILL", owner_ref="SURF-001", axis="registration", pack_id="GRILL-AUTH-1")
        wrong_pack = copy.deepcopy(grill_seed)
        wrong_pack["location"]["pack_id"] = "GRILL-CORE-1"
        self.assert_seed_invalid(state, wrong_pack)

    def test_verification_rejects_a_record_id_duplicated_in_another_canonical_container(self):
        state = closed_v2_state()
        seed = source_seed_by_location(
            build_source_seed_inventory(state), scope="CORE", owner_ref="REQ-001", axis="happy_path",
        )
        state["objects"]["goals"].append(copy.deepcopy(state["objects"]["requirements"][0]))
        self.assert_seed_invalid(state, seed)

    def test_distinct_semantic_locations_keep_distinct_keys_for_one_binding(self):
        seeds = build_source_seed_inventory(closed_v2_state())
        precondition = source_seed_by_location(seeds, scope="CORE", owner_ref="REQ-001", axis="precondition")
        recovery = source_seed_by_location(seeds, scope="CORE", owner_ref="REQ-001", axis="recovery")
        self.assertEqual((precondition["record_id"], precondition["pointer"]), (recovery["record_id"], recovery["pointer"]))
        self.assertNotEqual(precondition["seed_key"], recovery["seed_key"])
        self.assertEqual(source_seed_index(seeds)[precondition["seed_key"]], precondition)

    def test_unconsumed_evidence_does_not_change_inventory_digest(self):
        original = closed_v2_state()
        changed = copy.deepcopy(original)
        changed["evidence"].append({
            "id": "EVD-901", "status": "CURRENT", "source_kind": "USER_CONFIRMED_INTENT",
            "locator": "product-definition/unconsumed-observation", "claim": "A nonsemantic observation.",
            "confidence": "DIRECT", "authority_classes": ["INTENT"],
            "observed_version": None, "content_hash": None,
        })
        self.assertEqual(
            source_seed_inventory_digest(build_source_seed_inventory(original)),
            source_seed_inventory_digest(build_source_seed_inventory(changed)),
        )
