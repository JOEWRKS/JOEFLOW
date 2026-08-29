import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.v020_support import (
    foundation_state,
    materiality,
    surface_record,
    unknown_record,
)


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL_ROOT / "scripts"
PACKS = SKILL_ROOT / "references" / "grill-packs"
STATE_SCHEMA = SKILL_ROOT / "schemas" / "state-v0.2.0.schema.json"
sys.path.insert(0, str(SCRIPTS))

import grill_v2 as grill  # noqa: E402
from authority_binding_v2 import sha256_json  # noqa: E402
from discovery_v2 import (  # noqa: E402
    build_discovery_baseline,
    canonical_json_bytes,
    validate_discovery_baseline,
)
from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402


def current_baseline(state):
    return build_discovery_baseline(
        state,
        procedure_complete=True,
        applicable_surface_classes_complete=True,
    )


def active_profile_cell(*surface_refs):
    return {
        "status": "ACTIVE",
        "surface_refs": list(surface_refs),
        "unknown_refs": [],
        "basis_refs": [],
        "rationale": None,
    }


def activate(state, domain, *surface_refs):
    state["surface_manifest"]["grill_profile"][domain] = active_profile_cell(
        *surface_refs,
    )


def specialist_row(pack_id, target_ref):
    pack = grill.load_grill_packs()[pack_id]
    return {
        "target_ref": target_ref,
        "pack_id": pack_id,
        "pack_version": pack["version"],
        "pack_digest": grill.canonical_pack_digest(pack),
        "axes": {
            axis["id"]: {
                "status": "N/A",
                "authority_bindings": [],
                "unknown_refs": [],
                "basis_bindings": [{
                    "record_id": "EVD-900", "pointer": "/claim",
                    "value_sha256": sha256_json("The six specialist topology domains were explicitly classified."),
                }],
                "rationale": "This axis does not apply to the classified surface.",
            }
            for axis in pack["axes"]
        },
    }


def add_open_axis(state, row, axis_id, unknown_id="UNK-901"):
    state["objects"]["unknowns"].append(unknown_record(
        unknown_id,
        classification="NON_MATERIAL",
        decision_authority="AGENT_AUTONOMOUS",
        origin={
            "kind": "GRILL_PACK_AXIS",
            "surface_ref": row["target_ref"],
            "pack_id": row["pack_id"],
            "axis_id": axis_id,
            "source_path": None,
        },
    ))
    row["axes"][axis_id] = {
        "status": "OPEN",
        "authority_bindings": [],
        "unknown_refs": [unknown_id],
        "basis_bindings": [],
        "rationale": None,
    }


class GrillBaselineV020Test(unittest.TestCase):
    def run_builder(self, state):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "build_discovery_baseline.py"), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def active_auth_state(self, *surface_ids):
        state = foundation_state()
        state["surface_manifest"]["records"] = [
            surface_record(
                surface_id,
                name=f"Authentication surface {surface_id}",
                classification="NON_MATERIAL",
            )
            for surface_id in surface_ids
        ]
        activate(state, "AUTH", *surface_ids)
        state["grill_coverage"] = [
            specialist_row("GRILL-AUTH-1", surface_id)
            for surface_id in surface_ids
        ]
        return state

    def test_identical_state_and_pack_files_produce_byte_identical_baselines(self):
        state = self.active_auth_state("SURF-001")

        first = current_baseline(state)
        second = current_baseline(copy.deepcopy(state))

        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        self.assertEqual(
            [pack["pack_id"] for pack in first["active_grill_packs"]],
            ["GRILL-AUTH-1", "GRILL-CORE-1"],
        )

    def test_current_m3_baseline_satisfies_the_canonical_state_schema_contract(self):
        state = self.active_auth_state("SURF-001")
        state["discovery_baseline"] = current_baseline(state)
        schema = json.loads(STATE_SCHEMA.read_text(encoding="utf-8"))
        current_schema = next(
            branch for branch in schema["$defs"]["discovery_baseline"]["oneOf"]
            if branch.get("properties", {}).get("status", {}).get("const") == "CURRENT"
        )
        expected_pack_schema = {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["pack_id", "version", "digest", "target_refs"],
                "properties": {
                    "pack_id": {
                        "type": "string",
                        "pattern": "^GRILL-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]+$",
                    },
                    "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+$"},
                    "digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "target_refs": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "pattern": "^(REQ|SURF)-[0-9]{3,}$",
                        },
                        "uniqueItems": True,
                    },
                },
            },
        }

        self.assertEqual(
            current_schema["properties"]["active_grill_packs"],
            expected_pack_schema,
        )
        self.assertEqual(
            current_schema["properties"]["active_grill_packs_complete"],
            {"type": "boolean"},
        )
        self.assertEqual(
            current_schema["properties"]["unknown_unknown_exhaustiveness_claimed"],
            {"const": False},
        )
        self.assertEqual(validate_state_v2(state), [])
        packs = state["discovery_baseline"]["active_grill_packs"]
        self.assertGreaterEqual(len(packs), expected_pack_schema["minItems"])
        self.assertEqual(len(packs), len({canonical_json_bytes(pack) for pack in packs}))
        for pack in packs:
            with self.subTest(pack=pack["pack_id"]):
                self.assertEqual(set(pack), set(expected_pack_schema["items"]["required"]))
                for field in ("pack_id", "version", "digest"):
                    field_schema = expected_pack_schema["items"]["properties"][field]
                    self.assertIsInstance(pack[field], str)
                    self.assertRegex(pack[field], field_schema["pattern"])
                targets = pack["target_refs"]
                self.assertEqual(len(targets), len(set(targets)))
                for target in targets:
                    self.assertRegex(
                        target,
                        expected_pack_schema["items"]["properties"]["target_refs"][
                            "items"
                        ]["pattern"],
                    )

    def test_schema_and_runtime_reject_old_or_malformed_pack_instances(self):
        state = self.active_auth_state("SURF-001")
        state["discovery_baseline"] = current_baseline(state)
        malformed = []

        old_empty = copy.deepcopy(state)
        old_empty["discovery_baseline"]["active_grill_packs"] = []
        malformed.append(old_empty)

        extra_field = copy.deepcopy(state)
        extra_field["discovery_baseline"]["active_grill_packs"][0]["extra"] = True
        malformed.append(extra_field)

        bad_pack_id = copy.deepcopy(state)
        bad_pack_id["discovery_baseline"]["active_grill_packs"][0]["pack_id"] = (
            "GRILL-auth-1"
        )
        malformed.append(bad_pack_id)

        bad_version = copy.deepcopy(state)
        bad_version["discovery_baseline"]["active_grill_packs"][0]["version"] = "v1"
        malformed.append(bad_version)

        bad_target = copy.deepcopy(state)
        bad_target["discovery_baseline"]["active_grill_packs"][0]["target_refs"] = [
            "not-a-ref"
        ]
        malformed.append(bad_target)

        duplicate_target = copy.deepcopy(state)
        duplicate_target["discovery_baseline"]["active_grill_packs"][0][
            "target_refs"
        ] = ["SURF-001", "SURF-001"]
        malformed.append(duplicate_target)

        for invalid in malformed:
            with self.subTest(packs=invalid["discovery_baseline"]["active_grill_packs"]):
                errors = validate_discovery_baseline(invalid, check_freshness=False)
                self.assertEqual(
                    {error["code"] for error in errors},
                    {"invalid_discovery_baseline"},
                )

    def test_complete_profile_activation_and_exact_target_set_change_baseline_bytes(self):
        inactive = foundation_state()
        inactive["surface_manifest"]["records"] = [
            surface_record("SURF-001", classification="NON_MATERIAL"),
            surface_record("SURF-002", classification="NON_MATERIAL"),
        ]
        one_target = self.active_auth_state("SURF-001")
        two_targets = self.active_auth_state("SURF-001", "SURF-002")

        inactive_baseline = current_baseline(inactive)
        one_baseline = current_baseline(one_target)
        two_baseline = current_baseline(two_targets)

        self.assertNotEqual(canonical_json_bytes(inactive_baseline), canonical_json_bytes(one_baseline))
        self.assertNotEqual(canonical_json_bytes(one_baseline), canonical_json_bytes(two_baseline))
        packs_by_id = {
            pack["pack_id"]: pack for pack in two_baseline["active_grill_packs"]
        }
        self.assertIn("GRILL-AUTH-1", packs_by_id)
        auth_instance = packs_by_id["GRILL-AUTH-1"]
        self.assertEqual(auth_instance["target_refs"], ["SURF-001", "SURF-002"])

    def test_pack_semantic_change_changes_digest_and_makes_stored_baseline_stale(self):
        state = self.active_auth_state("SURF-001")
        state["discovery_baseline"] = current_baseline(state)
        stored_by_id = {
            pack["pack_id"]: pack
            for pack in state["discovery_baseline"]["active_grill_packs"]
        }
        self.assertIn("GRILL-AUTH-1", stored_by_id)
        stored_auth = stored_by_id["GRILL-AUTH-1"]
        original_loader = grill.load_grill_packs

        with tempfile.TemporaryDirectory() as directory:
            copied_packs = Path(directory) / "grill-packs"
            shutil.copytree(PACKS, copied_packs)
            auth_path = copied_packs / "auth.json"
            changed_pack = json.loads(auth_path.read_text(encoding="utf-8"))
            changed_pack["axes"][0]["description"] += " Updated semantic authority."
            auth_path.write_text(
                json.dumps(changed_pack, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            with patch.object(
                grill,
                "load_grill_packs",
                side_effect=lambda: original_loader(copied_packs),
            ):
                recomputed = current_baseline(state)
                current_auth = next(
                    pack for pack in recomputed["active_grill_packs"]
                    if pack["pack_id"] == "GRILL-AUTH-1"
                )
                errors = validate_discovery_baseline(state)

        self.assertNotEqual(stored_auth["digest"], current_auth["digest"])
        self.assertEqual({error["code"] for error in errors}, {"stale_discovery_baseline"})

    def test_complete_pack_inventory_remains_complete_with_open_axes(self):
        state = self.active_auth_state("SURF-001")
        add_open_axis(state, state["grill_coverage"][0], "registration")

        self.assertEqual(validate_state_v2(state), [])
        baseline = current_baseline(state)
        closure = evaluate_closure_v2(state)

        self.assertTrue(baseline["active_grill_packs_complete"])
        self.assertEqual(closure["metrics"]["active_grill_pack_gaps"], 0)
        self.assertEqual(closure["metrics"]["unresolved_pack_axes"], 1)

    def test_missing_or_mismatched_required_pack_row_makes_inventory_incomplete(self):
        missing = self.active_auth_state("SURF-001")
        missing["grill_coverage"] = []
        mismatched = self.active_auth_state("SURF-001")
        mismatched["grill_coverage"][0]["pack_digest"] = "0" * 64

        for state in (missing, mismatched):
            with self.subTest(row=state["grill_coverage"]):
                baseline = current_baseline(state)
                metrics = evaluate_closure_v2(state)["metrics"]
                self.assertFalse(baseline["active_grill_packs_complete"])
                self.assertGreater(metrics["active_grill_pack_gaps"], 0)

    def test_unknown_unknown_exhaustiveness_is_immutable_false(self):
        state = foundation_state()
        baseline = current_baseline(state)
        self.assertFalse(baseline["unknown_unknown_exhaustiveness_claimed"])

        state["discovery_baseline"] = baseline
        state["discovery_baseline"]["unknown_unknown_exhaustiveness_claimed"] = True
        self.assertIn(
            "invalid_discovery_baseline",
            {error["code"] for error in validate_discovery_baseline(state)},
        )

    def test_builder_bypasses_only_freshness_not_m3_semantic_validation(self):
        stale_only = foundation_state()
        stale_only["discovery_baseline"] = current_baseline(stale_only)
        stale_only["project"]["definition_revision"] = 2
        regenerated = self.run_builder(stale_only)
        self.assertEqual(regenerated.returncode, 0, regenerated.stdout + regenerated.stderr)

        invalid_materiality = copy.deepcopy(stale_only)
        invalid_materiality["objects"]["requirements"] = [{
            "id": "REQ-001",
            "status": "CURRENT",
            "statement": "Use the local reversible default.",
            "scope": "LOCAL",
            "ui_required": False,
            "materiality": materiality(classification="NON_MATERIAL"),
        }]
        invalid_materiality["objects"]["requirements"][0]["materiality"]["classification"] = "MATERIAL"

        invalid_unknown = copy.deepcopy(stale_only)
        invalid_unknown["objects"]["unknowns"] = [unknown_record(
            status="RESOLVED",
            classification="MATERIAL",
            decision_authority="USER_DECISION_REQUIRED",
        )]

        invalid_autonomy = copy.deepcopy(stale_only)
        invalid_autonomy["objects"]["unknowns"] = [unknown_record(
            classification="NON_MATERIAL",
            decision_authority="USER_DECISION_REQUIRED",
        )]

        invalid_pack = copy.deepcopy(stale_only)
        invalid_pack["surface_manifest"]["records"] = [
            surface_record("SURF-001", classification="NON_MATERIAL"),
        ]
        activate(invalid_pack, "AUTH", "SURF-001")

        cases = (
            (invalid_materiality, "materiality_classification_mismatch"),
            (invalid_unknown, "unresolved_unknown_provenance"),
            (invalid_autonomy, "invalid_decision_authority_derivation"),
            (invalid_pack, "missing_grill_coverage"),
        )
        for state, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                result = self.run_builder(state)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                payload = json.loads(result.stdout)
                self.assertIn(expected_code, {error["code"] for error in payload["errors"]})


if __name__ == "__main__":
    unittest.main()
