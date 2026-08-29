import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL_ROOT / "scripts"
PACKS = SKILL_ROOT / "references" / "grill-packs"
STATE_SCHEMA = SKILL_ROOT / "schemas" / "state-v0.2.0.schema.json"
TEMPLATE = SKILL_ROOT / "templates" / "state-v0.2.0.example.json"
QUESTION_CLI = SCRIPTS / "next_product_question.py"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SKILL_ROOT))

import grill_v2 as grill  # noqa: E402
from authority_binding_v2 import make_authority_binding, sha256_json  # noqa: E402
from downstream.schema_validation import (  # noqa: E402
    SchemaValidationError,
    validate_instance,
)
from state_validation_v2 import evaluate_closure_v2, validate_state_v2  # noqa: E402
from tests.v020_support import (  # noqa: E402
    evidence_record,
    foundation_state,
    materiality,
    surface_record,
    unknown_record,
)


DOMAINS = (
    "AUTH", "MONEY", "FILE_UPLOAD", "ASYNC", "PERMISSION",
    "DESTRUCTIVE_ACTION",
)
DOMAIN_PACKS = {
    "AUTH": "GRILL-AUTH-1",
    "MONEY": "GRILL-MONEY-1",
    "FILE_UPLOAD": "GRILL-FILE-UPLOAD-1",
    "ASYNC": "GRILL-ASYNC-1",
    "PERMISSION": "GRILL-PERMISSION-1",
    "DESTRUCTIVE_ACTION": "GRILL-DESTRUCTIVE-ACTION-1",
}
FORCED_KINDS = {
    "MONEY_FLOW": "MONEY",
    "ASYNC_PROCESS": "ASYNC",
    "PERMISSION": "PERMISSION",
    "DESTRUCTIVE_OPERATION": "DESTRUCTIVE_ACTION",
}
CORE_AXES = (
    "actor", "goal", "entry_point", "precondition", "happy_path",
    "alternative_path", "error", "recovery", "permission", "state",
    "data", "side_effect", "notification", "validation", "boundary",
    "persistence", "security", "privacy", "analytics", "acceptance",
)
PACK_AXES = {
    "GRILL-CORE-1": CORE_AXES,
    "GRILL-AUTH-1": (
        "registration", "verification", "login", "logout", "session_expiry",
        "session_renewal", "password_reset", "account_recovery", "revocation",
        "role_change", "provider_failure", "duplicate_identity", "account_linking",
    ),
    "GRILL-MONEY-1": (
        "currency", "price_authority", "tax", "discount", "payment_failure",
        "duplicate_payment", "refund", "partial_refund", "cancellation",
        "chargeback", "settlement", "receipt",
    ),
    "GRILL-FILE-UPLOAD-1": (
        "type", "size", "quota", "malware", "processing", "partial_failure",
        "resume", "retention", "deletion", "ownership", "download_permission",
    ),
    "GRILL-ASYNC-1": (
        "pending", "polling", "timeout", "retry", "idempotency",
        "duplicate_execution", "late_completion", "partial_completion", "cancel",
        "reconciliation",
    ),
    "GRILL-PERMISSION-1": (
        "role", "resource_ownership", "read", "write", "delete", "delegation",
        "revocation", "role_change_mid_flow", "stale_permission", "audit",
    ),
    "GRILL-DESTRUCTIVE-ACTION-1": (
        "confirmation", "reason", "undo", "grace_period", "dependency_effects",
        "irreversible_boundary", "audit", "notification",
    ),
}
MATERIAL_FLOORS = {
    "GRILL-CORE-1": set(),
    "GRILL-AUTH-1": {
        "session_expiry", "password_reset", "account_recovery", "revocation",
        "role_change", "duplicate_identity", "account_linking",
    },
    "GRILL-MONEY-1": set(PACK_AXES["GRILL-MONEY-1"]),
    "GRILL-FILE-UPLOAD-1": {
        "malware", "retention", "deletion", "ownership", "download_permission",
    },
    "GRILL-ASYNC-1": {
        "idempotency", "duplicate_execution", "partial_completion", "reconciliation",
    },
    "GRILL-PERMISSION-1": set(PACK_AXES["GRILL-PERMISSION-1"]),
    "GRILL-DESTRUCTIVE-ACTION-1": set(PACK_AXES["GRILL-DESTRUCTIVE-ACTION-1"]),
}
PACK_FILENAMES = {
    "core.json", "auth.json", "money.json", "file-upload.json", "async.json",
    "permission.json", "destructive-action.json",
}
INTERFACES = (
    "PACK_DIR", "load_grill_packs", "canonical_pack_digest",
    "compile_active_grill_packs", "validate_grill_coverage",
    "grill_pack_metrics",
)


def profile_cell(status="N/A", *, surface_refs=None, unknown_refs=None, basis_refs=None):
    if surface_refs is None:
        surface_refs = []
    if unknown_refs is None:
        unknown_refs = []
    if basis_refs is None:
        basis_refs = ["EVD-900"] if status == "N/A" else []
    return {
        "status": status,
        "surface_refs": list(surface_refs),
        "unknown_refs": list(unknown_refs),
        "basis_refs": list(basis_refs),
        "rationale": "Discovery found no applicable topology in this domain." if status == "N/A" else None,
    }


def base_state():
    state = foundation_state()
    state["evidence"] = [evidence_record(
        "EVD-900",
        source_kind="USER_CONFIRMED_INTENT",
        authority_classes=["INTENT"],
        claim="The six specialist topology domains were explicitly classified.",
        locator="product-definition/topology-classification",
    )]
    state["surface_manifest"] = {
        "records": [],
        "grill_profile": {domain: profile_cell() for domain in DOMAINS},
    }
    state["grill_coverage"] = []
    return state


def current_surface(surface_id="SURF-001", *, kind="FEATURE_AREA", name="Checkout"):
    return surface_record(
        surface_id,
        kind=kind,
        name=name,
        classification="NON_MATERIAL",
    )


def activate(state, domain, *surface_ids):
    state["surface_manifest"]["grill_profile"][domain] = profile_cell(
        "ACTIVE", surface_refs=surface_ids,
    )


def current_rule(rule_id="RULE-900"):
    return {
        "id": rule_id,
        "status": "CURRENT",
        "statement": "The product behavior is explicitly defined.",
        "applies_to": [],
    }


def material_requirement(requirement_id="REQ-001"):
    return {
        "id": requirement_id,
        "status": "CURRENT",
        "statement": "Users can complete the material product flow.",
        "scope": "Core product flow",
        "ui_required": True,
        "materiality": materiality(classification="MATERIAL"),
    }


def core_coverage(requirement_id="REQ-001", *, status="COVERED"):
    return {
        "feature_id": requirement_id,
        "cells": {axis: {"status": status} for axis in CORE_AXES},
    }


def specialist_row(pack_id, target_ref, *, status="N/A", basis_ref="EVD-900"):
    packs = grill.load_grill_packs()
    pack = packs[pack_id]
    cells = {}
    for axis in PACK_AXES[pack_id]:
        cells[axis] = {
            "status": status,
            "authority_bindings": [],
            "unknown_refs": [],
            "basis_bindings": [{
                "record_id": basis_ref, "pointer": "/claim",
                "value_sha256": sha256_json("The six specialist topology domains were explicitly classified."),
            }] if status == "N/A" else [],
            "rationale": "This axis does not apply to the classified surface." if status == "N/A" else None,
        }
    return {
        "target_ref": target_ref,
        "pack_id": pack_id,
        "pack_version": pack["version"],
        "pack_digest": grill.canonical_pack_digest(pack),
        "axes": cells,
    }


def axis_unknown(state, target_ref, pack_id, axis_id, *, unknown_id="UNK-901", classification="MATERIAL"):
    authority = "USER_DECISION_REQUIRED" if classification == "MATERIAL" else "AGENT_AUTONOMOUS"
    record = unknown_record(
        unknown_id,
        classification=classification,
        decision_authority=authority,
        origin={
            "kind": "GRILL_PACK_AXIS",
            "surface_ref": target_ref,
            "pack_id": pack_id,
            "axis_id": axis_id,
            "source_path": None,
        },
    )
    state["objects"]["unknowns"].append(record)
    return record


def open_axis(row, axis_id, unknown_id):
    row["axes"][axis_id] = {
        "status": "OPEN",
        "authority_bindings": [],
        "unknown_refs": [unknown_id],
        "basis_bindings": [],
        "rationale": None,
    }


def malformed_enum_states():
    malformed_unknown_status = base_state()
    malformed_unknown_status["objects"]["unknowns"] = [unknown_record()]
    malformed_unknown_status["objects"]["unknowns"][0]["status"] = []

    malformed_authority_class = base_state()
    malformed_authority_class["objects"]["unknowns"] = [unknown_record()]
    malformed_authority_class["objects"]["unknowns"][0][
        "required_authority_class"
    ] = {}

    malformed_profile_status = base_state()
    malformed_profile_status["surface_manifest"]["grill_profile"]["AUTH"][
        "status"
    ] = []

    malformed_axis_status = base_state()
    malformed_axis_status["surface_manifest"]["records"] = [current_surface()]
    activate(malformed_axis_status, "AUTH", "SURF-001")
    row = specialist_row("GRILL-AUTH-1", "SURF-001")
    row["axes"]["registration"]["status"] = []
    malformed_axis_status["grill_coverage"] = [row]

    return (
        ("unknown_status", malformed_unknown_status),
        ("required_authority_class", malformed_authority_class),
        ("profile_status", malformed_profile_status),
        ("axis_status", malformed_axis_status),
    )


class GrillPacksV020Test(unittest.TestCase):
    def setUp(self):
        for interface in INTERFACES:
            self.assertTrue(hasattr(grill, interface), f"missing Grill Pack interface: {interface}")
        self.assertTrue(PACKS.is_dir(), "checked-in Grill Pack directory is missing")

    def error_codes(self, state):
        return {error["code"] for error in validate_state_v2(state)}

    def test_unhashable_enum_values_return_structured_validator_errors(self):
        for label, state in malformed_enum_states():
            with self.subTest(label=label):
                try:
                    errors = validate_state_v2(state)
                except Exception as exception:
                    self.fail(f"validation raised {type(exception).__name__}: {exception}")
                self.assertTrue(errors)
                self.assertTrue(
                    all(set(error) == {"code", "message", "path"} for error in errors),
                    errors,
                )

    def test_unhashable_enum_values_return_closure_payload_without_crash(self):
        for label, state in malformed_enum_states():
            with self.subTest(label=label):
                try:
                    result = evaluate_closure_v2(state)
                except Exception as exception:
                    self.fail(f"closure raised {type(exception).__name__}: {exception}")
                self.assertFalse(result["closed"])
                self.assertTrue(result["errors"])
                self.assertTrue(all(
                    set(error) == {"code", "message", "path"}
                    for error in result["errors"]
                ))

    def test_unhashable_enum_values_make_question_cli_return_json_errors(self):
        for label, state in malformed_enum_states():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                state_path = Path(directory) / "invalid.json"
                state_path.write_text(json.dumps(state), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(QUESTION_CLI), str(state_path)],
                    cwd=ROOT,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 1, result.stderr.decode())
                self.assertEqual(result.stderr, b"")
                payload = json.loads(result.stdout)
                self.assertIsNone(payload["next_question"])
                self.assertTrue(payload["errors"])
                self.assertTrue(all(
                    set(error) == {"code", "message", "path"}
                    for error in payload["errors"]
                ))

    def test_all_seven_declarative_pack_files_validate_and_freeze_identity_axes_and_floors(self):
        schema_path = PACKS / "grill-pack.schema.json"
        self.assertTrue(schema_path.is_file())
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        pack_files = {path.name for path in PACKS.glob("*.json")} - {schema_path.name}
        self.assertEqual(pack_files, PACK_FILENAMES)

        loaded = grill.load_grill_packs()
        self.assertEqual(set(loaded), set(PACK_AXES))
        for pack_id, expected_axes in PACK_AXES.items():
            with self.subTest(pack_id=pack_id):
                pack = loaded[pack_id]
                validate_instance(pack, schema)
                self.assertEqual(pack["pack_id"], pack_id)
                self.assertEqual(pack["version"], "1.0")
                self.assertEqual(tuple(axis["id"] for axis in pack["axes"]), expected_axes)
                self.assertEqual(len(expected_axes), len({axis["id"] for axis in pack["axes"]}))
                self.assertTrue(all(axis["independent_decision"] for axis in pack["axes"]))
                actual_material = {
                    axis["id"] for axis in pack["axes"]
                    if axis["materiality_floor"] == "MATERIAL"
                }
                self.assertEqual(actual_material, MATERIAL_FLOORS[pack_id])
                self.assertTrue(all(
                    axis["materiality_floor"] in {"INHERIT", "MATERIAL"}
                    and axis["description"].strip()
                    for axis in pack["axes"]
                ))

        self.assertTrue(loaded["GRILL-CORE-1"]["activation"]["always"])
        for domain, pack_id in DOMAIN_PACKS.items():
            self.assertFalse(loaded[pack_id]["activation"]["always"])
            self.assertEqual(loaded[pack_id]["activation"]["topology_tags"], [domain])

    def test_pack_digests_are_canonical_deterministic_and_not_stored_in_sources(self):
        loaded = grill.load_grill_packs()
        for pack_id, pack in loaded.items():
            with self.subTest(pack_id=pack_id):
                digest = grill.canonical_pack_digest(pack)
                self.assertRegex(digest, r"^[0-9a-f]{64}$")
                self.assertEqual(digest, grill.canonical_pack_digest(copy.deepcopy(pack)))
                reordered = {key: pack[key] for key in reversed(tuple(pack))}
                self.assertEqual(digest, grill.canonical_pack_digest(reordered))
                self.assertNotIn("digest", pack)

        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            for path in PACKS.glob("*.json"):
                (temporary / path.name).write_bytes(path.read_bytes())
            first = grill.load_grill_packs(temporary)
            second = grill.load_grill_packs(temporary)
            self.assertEqual(first, second)

    def test_pack_schema_rejects_malformed_contracts(self):
        schema = json.loads((PACKS / "grill-pack.schema.json").read_text(encoding="utf-8"))
        pack = copy.deepcopy(grill.load_grill_packs()["GRILL-AUTH-1"])
        pack["axes"][0]["materiality_floor"] = "OPTIONAL"
        with self.assertRaises(SchemaValidationError):
            validate_instance(pack, schema)

    def test_profile_is_mandatory_complete_exact_and_surface_topology_tags_are_forbidden(self):
        valid = base_state()
        self.assertEqual(validate_state_v2(valid), [])

        missing_profile = base_state()
        del missing_profile["surface_manifest"]["grill_profile"]
        self.assertIn("invalid_grill_profile", self.error_codes(missing_profile))

        missing_domain = base_state()
        del missing_domain["surface_manifest"]["grill_profile"]["AUTH"]
        self.assertIn("invalid_grill_profile", self.error_codes(missing_domain))

        extra_domain = base_state()
        extra_domain["surface_manifest"]["grill_profile"]["OTHER"] = profile_cell()
        self.assertIn("invalid_grill_profile", self.error_codes(extra_domain))

        tagged_surface = base_state()
        tagged = current_surface(name="Authentication")
        tagged["topology_tags"] = ["AUTH"]
        tagged_surface["surface_manifest"]["records"] = [tagged]
        self.assertIn("invalid_surface_shape", self.error_codes(tagged_surface))
        active_ids = {item["pack_id"] for item in grill.compile_active_grill_packs(tagged_surface)}
        self.assertNotIn("GRILL-AUTH-1", active_ids)

    def test_active_na_and_open_profile_cells_enforce_exact_authority_payloads(self):
        active = base_state()
        active["surface_manifest"]["records"] = [current_surface()]
        activate(active, "AUTH", "SURF-001")
        self.assertNotIn("invalid_grill_profile", self.error_codes(active))

        invalid_active = copy.deepcopy(active)
        invalid_active["surface_manifest"]["grill_profile"]["AUTH"]["unknown_refs"] = ["UNK-999"]
        self.assertIn("invalid_grill_profile", self.error_codes(invalid_active))

        bare_na = base_state()
        bare_na["surface_manifest"]["grill_profile"]["AUTH"]["basis_refs"] = []
        self.assertIn("invalid_grill_profile", self.error_codes(bare_na))

        stale_na = base_state()
        stale_na["evidence"][0]["status"] = "STALE"
        self.assertIn("invalid_grill_profile", self.error_codes(stale_na))

        opened = base_state()
        topology_unknown = unknown_record(
            "UNK-900",
            origin={
                "kind": "GRILL_TOPOLOGY",
                "surface_ref": None,
                "pack_id": "GRILL-AUTH-1",
                "axis_id": None,
                "source_path": None,
            },
        )
        opened["objects"]["unknowns"] = [topology_unknown]
        opened["surface_manifest"]["grill_profile"]["AUTH"] = profile_cell(
            "OPEN", unknown_refs=["UNK-900"], basis_refs=[],
        )
        self.assertNotIn("invalid_grill_profile", self.error_codes(opened))
        self.assertEqual(grill.grill_pack_metrics(opened)["active_grill_pack_gaps"], 1)

        wrong_origin = copy.deepcopy(opened)
        wrong_origin["objects"]["unknowns"][0]["origin"]["pack_id"] = "GRILL-MONEY-1"
        self.assertIn("invalid_grill_profile", self.error_codes(wrong_origin))

    def test_compile_uses_only_valid_active_profile_cells_and_sorts_unique_targets(self):
        state = base_state()
        state["surface_manifest"]["records"] = [
            current_surface("SURF-002", name="Identity"),
            current_surface("SURF-001", name="Identity settings"),
        ]
        activate(state, "AUTH", "SURF-002", "SURF-001")
        activate(state, "FILE_UPLOAD", "SURF-001")

        instances = grill.compile_active_grill_packs(state)
        self.assertEqual([item["pack_id"] for item in instances], sorted(item["pack_id"] for item in instances))
        by_id = {item["pack_id"]: item for item in instances}
        self.assertEqual(by_id["GRILL-AUTH-1"]["target_refs"], ["SURF-001", "SURF-002"])
        self.assertEqual(by_id["GRILL-FILE-UPLOAD-1"]["target_refs"], ["SURF-001"])
        self.assertEqual(len(instances), len(by_id))
        for instance in instances:
            self.assertEqual(instance["version"], "1.0")
            self.assertRegex(instance["digest"], r"^[0-9a-f]{64}$")

        vague = base_state()
        vague["surface_manifest"]["records"] = [current_surface(
            name="Authentication and file upload settings",
        )]
        active_ids = {item["pack_id"] for item in grill.compile_active_grill_packs(vague)}
        self.assertNotIn("GRILL-AUTH-1", active_ids)
        self.assertNotIn("GRILL-FILE-UPLOAD-1", active_ids)

    def test_every_forced_surface_kind_requires_active_profile_and_all_forced_targets(self):
        for kind, domain in FORCED_KINDS.items():
            with self.subTest(kind=kind, domain=domain):
                contradictory = base_state()
                contradictory["surface_manifest"]["records"] = [current_surface(kind=kind)]
                self.assertIn("grill_topology_contradiction", self.error_codes(contradictory))
                pack_id = DOMAIN_PACKS[domain]
                self.assertNotIn(
                    pack_id,
                    {item["pack_id"] for item in grill.compile_active_grill_packs(contradictory)},
                )

                missing_cell = base_state()
                missing_cell["surface_manifest"]["records"] = [current_surface(kind=kind)]
                del missing_cell["surface_manifest"]["grill_profile"][domain]
                self.assertIn("grill_topology_contradiction", self.error_codes(missing_cell))

                missing_profile = base_state()
                missing_profile["surface_manifest"]["records"] = [current_surface(kind=kind)]
                del missing_profile["surface_manifest"]["grill_profile"]
                self.assertIn("grill_topology_contradiction", self.error_codes(missing_profile))

                valid = base_state()
                valid["surface_manifest"]["records"] = [current_surface(kind=kind)]
                activate(valid, domain, "SURF-001")
                self.assertNotIn("grill_topology_contradiction", self.error_codes(valid))
                self.assertIn(
                    pack_id,
                    {item["pack_id"] for item in grill.compile_active_grill_packs(valid)},
                )

                omitted = base_state()
                omitted["surface_manifest"]["records"] = [
                    current_surface("SURF-001", kind=kind),
                    current_surface("SURF-002", kind=kind),
                ]
                activate(omitted, domain, "SURF-001")
                self.assertIn("grill_topology_contradiction", self.error_codes(omitted))
                self.assertNotIn(
                    pack_id,
                    {item["pack_id"] for item in grill.compile_active_grill_packs(omitted)},
                )

    def test_core_pack_targets_current_material_requirements_and_requires_exact_coverage(self):
        state = base_state()
        state["objects"]["requirements"] = [
            material_requirement("REQ-002"),
            material_requirement("REQ-001"),
            {
                **material_requirement("REQ-003"),
                "materiality": materiality(classification="NON_MATERIAL"),
            },
            {**material_requirement("REQ-004"), "status": "STALE"},
        ]
        core = {
            item["pack_id"]: item for item in grill.compile_active_grill_packs(state)
        }["GRILL-CORE-1"]
        self.assertEqual(core["target_refs"], ["REQ-001", "REQ-002"])

        missing = copy.deepcopy(state)
        self.assertEqual(grill.grill_pack_metrics(missing)["active_grill_pack_gaps"], 2)
        self.assertIn("missing_core_grill_coverage", {
            error["code"] for error in grill.validate_grill_coverage(missing)
        })

        valid = copy.deepcopy(state)
        valid["coverage"] = [core_coverage("REQ-002"), core_coverage("REQ-001")]
        self.assertEqual(grill.grill_pack_metrics(valid)["active_grill_pack_gaps"], 0)

        wrong_axes = copy.deepcopy(valid)
        del wrong_axes["coverage"][0]["cells"]["security"]
        self.assertEqual(grill.grill_pack_metrics(wrong_axes)["active_grill_pack_gaps"], 1)
        self.assertIn("core_grill_axis_inventory_mismatch", {
            error["code"] for error in grill.validate_grill_coverage(wrong_axes)
        })

        duplicate = copy.deepcopy(valid)
        duplicate["coverage"].append(core_coverage("REQ-001"))
        self.assertEqual(grill.grill_pack_metrics(duplicate)["active_grill_pack_gaps"], 1)
        self.assertIn("duplicate_core_grill_coverage", {
            error["code"] for error in grill.validate_grill_coverage(duplicate)
        })

    def test_specialist_rows_require_exact_identity_inventory_and_one_row_per_instance(self):
        state = base_state()
        state["surface_manifest"]["records"] = [current_surface()]
        activate(state, "AUTH", "SURF-001")

        missing = copy.deepcopy(state)
        self.assertEqual(grill.grill_pack_metrics(missing)["active_grill_pack_gaps"], 1)
        self.assertIn("missing_grill_coverage", {
            error["code"] for error in grill.validate_grill_coverage(missing)
        })

        valid = copy.deepcopy(state)
        valid["grill_coverage"] = [specialist_row("GRILL-AUTH-1", "SURF-001")]
        self.assertEqual(grill.validate_grill_coverage(valid), [])
        self.assertEqual(grill.grill_pack_metrics(valid)["active_grill_pack_gaps"], 0)

        for field, bad_value, code in (
            ("pack_version", "0.9", "grill_pack_identity_mismatch"),
            ("pack_digest", "0" * 64, "grill_pack_identity_mismatch"),
        ):
            with self.subTest(field=field):
                invalid = copy.deepcopy(valid)
                invalid["grill_coverage"][0][field] = bad_value
                self.assertEqual(grill.grill_pack_metrics(invalid)["active_grill_pack_gaps"], 1)
                self.assertIn(code, {error["code"] for error in grill.validate_grill_coverage(invalid)})

        for mutation in ("missing", "extra"):
            with self.subTest(mutation=mutation):
                invalid = copy.deepcopy(valid)
                if mutation == "missing":
                    del invalid["grill_coverage"][0]["axes"]["login"]
                else:
                    invalid["grill_coverage"][0]["axes"]["extra"] = copy.deepcopy(
                        invalid["grill_coverage"][0]["axes"]["login"]
                    )
                self.assertEqual(grill.grill_pack_metrics(invalid)["active_grill_pack_gaps"], 1)
                self.assertIn("grill_pack_axis_inventory_mismatch", {
                    error["code"] for error in grill.validate_grill_coverage(invalid)
                })

        duplicate = copy.deepcopy(valid)
        duplicate["grill_coverage"].append(copy.deepcopy(duplicate["grill_coverage"][0]))
        self.assertEqual(grill.grill_pack_metrics(duplicate)["active_grill_pack_gaps"], 1)
        self.assertIn("duplicate_grill_coverage", {
            error["code"] for error in grill.validate_grill_coverage(duplicate)
        })

    def test_inventory_gap_does_not_hide_present_open_axis_metric(self):
        state = base_state()
        state["surface_manifest"]["records"] = [current_surface()]
        activate(state, "AUTH", "SURF-001")
        row = specialist_row("GRILL-AUTH-1", "SURF-001")
        axis_unknown(state, "SURF-001", "GRILL-AUTH-1", "registration")
        open_axis(row, "registration", "UNK-901")
        del row["axes"]["login"]
        state["grill_coverage"] = [row]

        metrics = grill.grill_pack_metrics(state)
        self.assertEqual(metrics["active_grill_pack_gaps"], 1)
        self.assertEqual(metrics["unresolved_pack_axes"], 1)

    def test_specialist_axis_status_payloads_require_current_authority_unknown_or_basis(self):
        state = base_state()
        state["surface_manifest"]["records"] = [current_surface()]
        activate(state, "AUTH", "SURF-001")
        state["objects"]["rules"] = [current_rule()]
        row = specialist_row("GRILL-AUTH-1", "SURF-001")
        row["axes"]["registration"] = {
            "status": "ADDRESSED",
            "authority_bindings": [make_authority_binding(state, "RULE-900", "/statement")],
            "unknown_refs": [],
            "basis_bindings": [],
            "rationale": None,
        }
        axis_unknown(state, "SURF-001", "GRILL-AUTH-1", "login")
        open_axis(row, "login", "UNK-901")
        state["grill_coverage"] = [row]
        self.assertEqual(validate_state_v2(state), [])

        invalid_status = copy.deepcopy(state)
        invalid_status["grill_coverage"][0]["axes"]["registration"]["status"] = "COVERED"
        self.assertIn("invalid_grill_axis_coverage", self.error_codes(invalid_status))

        stale_authority = copy.deepcopy(state)
        stale_authority["objects"]["rules"][0]["status"] = "STALE"
        self.assertIn("stale_authority_binding", self.error_codes(stale_authority))

        noncanonical_authority = copy.deepcopy(state)
        noncanonical_authority["objects"]["goals"] = [{
            "id": "GOAL-900",
            "status": "CURRENT",
            "statement": "The product should be easy to use.",
        }]
        noncanonical_authority["grill_coverage"][0]["axes"]["registration"]["authority_bindings"] = [
            make_authority_binding(noncanonical_authority, "GOAL-900", "/statement")
        ]
        self.assertIn(
            "invalid_authority_binding_type",
            self.error_codes(noncanonical_authority),
        )

        stale_basis = copy.deepcopy(state)
        stale_basis["evidence"].append(evidence_record(
            "EVD-901", source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"], status="STALE",
        ))
        stale_basis["grill_coverage"][0]["axes"]["verification"]["basis_bindings"] = [
            make_authority_binding(stale_basis, "EVD-901", "/claim")
        ]
        self.assertIn("stale_authority_binding", self.error_codes(stale_basis))

        missing_unknown = copy.deepcopy(state)
        missing_unknown["grill_coverage"][0]["axes"]["login"]["unknown_refs"] = ["UNK-999"]
        self.assertIn("invalid_grill_axis_unknown", self.error_codes(missing_unknown))

    def test_independent_axes_require_one_unique_exact_origin_unknown(self):
        state = base_state()
        state["surface_manifest"]["records"] = [current_surface()]
        activate(state, "AUTH", "SURF-001")
        row = specialist_row("GRILL-AUTH-1", "SURF-001")
        axis_unknown(state, "SURF-001", "GRILL-AUTH-1", "registration")
        open_axis(row, "registration", "UNK-901")
        state["grill_coverage"] = [row]
        self.assertEqual(grill.grill_pack_metrics(state)["umbrella_unknown_compression"], 0)

        mismatch = copy.deepcopy(state)
        mismatch["objects"]["unknowns"][0]["origin"]["axis_id"] = "login"
        self.assertEqual(grill.grill_pack_metrics(mismatch)["umbrella_unknown_compression"], 1)
        self.assertIn("umbrella_unknown_compression", self.error_codes(mismatch))

        reused = copy.deepcopy(state)
        open_axis(reused["grill_coverage"][0], "login", "UNK-901")
        self.assertEqual(grill.grill_pack_metrics(reused)["umbrella_unknown_compression"], 2)
        self.assertIn("umbrella_unknown_compression", self.error_codes(reused))

        multiple = copy.deepcopy(state)
        second = axis_unknown(
            multiple, "SURF-001", "GRILL-AUTH-1", "registration", unknown_id="UNK-902",
        )
        self.assertEqual(second["origin"]["axis_id"], "registration")
        multiple["grill_coverage"][0]["axes"]["registration"]["unknown_refs"].append("UNK-902")
        self.assertEqual(grill.grill_pack_metrics(multiple)["umbrella_unknown_compression"], 1)

    def test_material_floor_recomputes_origin_unknown_materiality(self):
        state = base_state()
        state["surface_manifest"]["records"] = [current_surface()]
        activate(state, "AUTH", "SURF-001")
        row = specialist_row("GRILL-AUTH-1", "SURF-001")
        axis_unknown(
            state,
            "SURF-001",
            "GRILL-AUTH-1",
            "account_recovery",
            classification="NON_MATERIAL",
        )
        open_axis(row, "account_recovery", "UNK-901")
        state["grill_coverage"] = [row]

        metrics = grill.grill_pack_metrics(state)
        self.assertEqual(metrics["pack_materiality_floor_violations"], 1)
        self.assertIn("pack_materiality_floor_violation", self.error_codes(state))

        missing_origin = copy.deepcopy(state)
        missing_origin["grill_coverage"][0]["axes"]["account_recovery"]["unknown_refs"] = ["UNK-999"]
        self.assertEqual(
            grill.grill_pack_metrics(missing_origin)["pack_materiality_floor_violations"],
            1,
        )

        inherited = copy.deepcopy(state)
        inherited["objects"]["unknowns"][0]["origin"]["axis_id"] = "registration"
        del inherited["grill_coverage"][0]["axes"]["account_recovery"]
        inherited["grill_coverage"][0]["axes"]["account_recovery"] = copy.deepcopy(
            specialist_row("GRILL-AUTH-1", "SURF-001")["axes"]["account_recovery"]
        )
        open_axis(inherited["grill_coverage"][0], "registration", "UNK-901")
        self.assertEqual(grill.grill_pack_metrics(inherited)["pack_materiality_floor_violations"], 0)

    def test_material_floor_requires_exact_valid_axis_origin(self):
        state = base_state()
        state["surface_manifest"]["records"] = [current_surface()]
        activate(state, "AUTH", "SURF-001")
        row = specialist_row("GRILL-AUTH-1", "SURF-001")
        unknown = axis_unknown(
            state,
            "SURF-001",
            "GRILL-AUTH-1",
            "account_recovery",
            classification="MATERIAL",
        )
        unknown["origin"]["axis_id"] = "login"
        open_axis(row, "account_recovery", "UNK-901")
        state["grill_coverage"] = [row]

        metrics = grill.grill_pack_metrics(state)
        self.assertEqual(metrics["umbrella_unknown_compression"], 1)
        self.assertEqual(metrics["pack_materiality_floor_violations"], 1)

    def test_frozen_metrics_overlap_but_axis_resolution_does_not_change_activation_completeness(self):
        state = base_state()
        state["surface_manifest"]["records"] = [current_surface()]
        activate(state, "AUTH", "SURF-001")
        row = specialist_row("GRILL-AUTH-1", "SURF-001")
        axis_unknown(state, "SURF-001", "GRILL-AUTH-1", "account_recovery")
        open_axis(row, "account_recovery", "UNK-901")
        state["grill_coverage"] = [row]

        metrics = grill.grill_pack_metrics(state)
        self.assertEqual(
            set(metrics),
            {
                "active_grill_pack_gaps", "unresolved_pack_axes",
                "umbrella_unknown_compression", "pack_materiality_floor_violations",
            },
        )
        self.assertEqual(metrics, {
            "active_grill_pack_gaps": 0,
            "unresolved_pack_axes": 1,
            "umbrella_unknown_compression": 0,
            "pack_materiality_floor_violations": 0,
        })
        closure = evaluate_closure_v2(state)
        self.assertFalse(closure["closed"])
        self.assertRegex(closure["definition_digest"], r"^[0-9a-f]{64}$")
        self.assertNotIn("semantic_closure_not_implemented", closure["metrics"])
        self.assertEqual(closure["metrics"]["active_grill_pack_gaps"], 0)
        self.assertEqual(closure["metrics"]["unresolved_pack_axes"], 1)
        self.assertFalse(state["discovery_baseline"].get("unknown_unknown_exhaustiveness_claimed", False))

        core_open = base_state()
        core_open["objects"]["requirements"] = [material_requirement()]
        core_open["coverage"] = [core_coverage(status="OPEN")]
        self.assertEqual(grill.grill_pack_metrics(core_open)["unresolved_pack_axes"], len(CORE_AXES))

    def test_state_schema_root_and_template_require_profile_and_specialist_coverage_without_m4_bindings(self):
        schema = json.loads(STATE_SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("grill_coverage", schema["required"])
        manifest = schema["properties"]["surface_manifest"]
        self.assertEqual(set(manifest["required"]), {"records", "grill_profile"})
        profile_ref = manifest["properties"]["grill_profile"]["$ref"]
        profile_schema = schema["$defs"][profile_ref.rsplit("/", 1)[-1]]
        self.assertEqual(set(profile_schema["required"]), set(DOMAINS))
        self.assertEqual(
            schema["properties"]["grill_coverage"]["items"],
            {"$ref": "#/$defs/grill_coverage_row"},
        )
        cell = schema["$defs"]["grill_axis_coverage"]
        self.assertEqual(
            set(cell["required"]),
            {"status", "authority_bindings", "unknown_refs", "basis_bindings", "rationale"},
        )
        self.assertNotIn("authority_refs", cell["properties"])
        self.assertNotIn("basis_refs", cell["properties"])

        template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(set(template["surface_manifest"]["grill_profile"]), set(DOMAINS))
        self.assertEqual(template["grill_coverage"], [])
        self.assertEqual(validate_state_v2(template), [])


if __name__ == "__main__":
    unittest.main()
