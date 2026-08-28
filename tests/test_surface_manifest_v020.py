import copy
import json
import sys
import unittest
from pathlib import Path

try:
    from tests.v020_support import (
        decision_record as canonical_decision_record,
        evidence_record,
        foundation_state,
        materiality,
        surface_record,
        unknown_record as canonical_unknown_record,
    )
except ModuleNotFoundError:
    from v020_support import (
        decision_record as canonical_decision_record,
        evidence_record,
        foundation_state,
        materiality,
        surface_record,
        unknown_record as canonical_unknown_record,
    )


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
sys.path.insert(0, str(SCRIPTS))

import state_validation_v2
from state_validation_v2 import evaluate_closure_v2, validate_state_v2


SURFACE_KINDS = {
    "ACTOR", "FEATURE_AREA", "ENTRY_POINT", "MAJOR_ACTION", "DOMAIN_ENTITY",
    "INTEGRATION", "ASYNC_PROCESS", "NOTIFICATION", "PERSISTENT_STATE",
    "SENSITIVE_DATA", "PERMISSION", "MONEY_FLOW", "DESTRUCTIVE_OPERATION",
    "LIFECYCLE_OBJECT",
}
SURFACE_STATUSES = {"IN_SCOPE", "OUT_OF_SCOPE", "OPEN", "SUPERSEDED", "RETIRED"}


def authority_record(prefix="REQ", record_id="REQ-001", status="CURRENT"):
    if prefix == "REQ":
        return "requirements", {
            "id": record_id, "status": status, "statement": "Save feedback",
            "scope": "CORE", "ui_required": True, "materiality": materiality(),
        }
    if prefix == "RULE":
        return "rules", {"id": record_id, "status": status, "statement": "Validate feedback", "applies_to": []}
    if prefix == "FLOW":
        return "flows", {
            "id": record_id, "status": status, "goal_refs": [], "entry": "Open form",
            "preconditions": [], "paths": [], "outcomes": [],
        }
    if prefix == "DATA":
        return "data", {"id": record_id, "status": status, "name": "Feedback", "purpose": "Store feedback", "ownership": "USER"}
    return "integrations", {"id": record_id, "status": status, "name": "Mail", "purpose": "Send feedback"}


def unknown_record(record_id="UNK-001", status="OPEN"):
    record = canonical_unknown_record(
        record_id,
        status=status,
        classification="NON_MATERIAL",
        decision_authority="USER_CONFIRMATION",
    )
    record["question"] = "Which recipients receive feedback?"
    return record


def decision_record(record_id="DEC-001", status="CURRENT"):
    record = canonical_decision_record(
        record_id,
        status=status,
        source_unknown_refs=["UNK-002"],
        classification="NON_MATERIAL",
    )
    record.update({"statement": "Exclude legacy feedback import", "decision_type": "SCOPE"})
    return record


def decision_source_unknown():
    record = canonical_unknown_record(
        "UNK-002",
        status="RESOLVED",
        classification="NON_MATERIAL",
        decision_authority="USER_DECISION_REQUIRED",
    )
    record.update({
        "resolved_by": ["DEC-001"],
        "resolution_mode": "USER_DECISION",
        "resolution_summary": "The user approved this scope decision.",
    })
    return record


def add_decision(state, *, status="CURRENT"):
    state["objects"]["decisions"] = [decision_record(status=status)]
    state["objects"]["unknowns"].append(decision_source_unknown())


class SurfaceManifestV020Test(unittest.TestCase):
    def errors(self, state):
        return validate_state_v2(state)

    def error_codes(self, state):
        return {error["code"] for error in self.errors(state)}

    def state_with(self, *surfaces):
        state = foundation_state()
        state["surface_manifest"]["records"] = [copy.deepcopy(surface) for surface in surfaces]
        return state

    def bind_current_authority(self, state, prefix="REQ"):
        authority_id = f"{prefix}-001"
        group, record = authority_record(prefix, authority_id)
        state["objects"][group] = [record]
        state["surface_manifest"]["records"][0]["authority_refs"] = [authority_id]

    def test_schema_defines_the_exact_surface_manifest_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        manifest = schema["properties"]["surface_manifest"]
        record = schema["$defs"]["surface_record"]

        self.assertEqual(manifest["required"], ["records"])
        self.assertFalse(manifest["additionalProperties"])
        self.assertEqual(manifest["properties"]["records"]["items"], {"$ref": "#/$defs/surface_record"})
        self.assertFalse(record["additionalProperties"])

    def test_surface_manifest_requires_only_a_records_array_at_runtime(self):
        for manifest in ({}, {"records": {}}, {"records": [], "unexpected": True}):
            with self.subTest(manifest=manifest):
                state = foundation_state()
                state["surface_manifest"] = manifest
                self.assertIn("invalid_surface_manifest", self.error_codes(state))

    def test_surface_ids_use_surf_prefix_and_are_global_unique(self):
        self.assertIn("invalid_surface_id", self.error_codes(self.state_with(surface_record("REQ-001"))))

        duplicate = self.state_with(surface_record(), surface_record())
        self.assertIn("duplicate_id", self.error_codes(duplicate))

        collision = self.state_with(surface_record())
        collision["objects"]["goals"] = [{"id": "SURF-001", "status": "CURRENT", "statement": "Collision"}]
        self.assertIn("duplicate_id", self.error_codes(collision))

    def test_surface_shape_enforces_enums_text_arrays_and_materiality(self):
        for field, value in (
            ("kind", "UNKNOWN"),
            ("status", "UNKNOWN"),
            ("name", ""),
            ("evidence_refs", ["EVD-001", "EVD-001"]),
            ("authority_refs", "REQ-001"),
            ("unknown_refs", ["UNK-001", 1]),
            ("decision_refs", [1]),
            ("contradiction_refs", ["CON-001", "CON-001"]),
            ("rationale", []),
            ("intent_classification", []),
            ("unexpected", True),
        ):
            with self.subTest(field=field, value=value):
                surface = surface_record(classification="NON_MATERIAL")
                surface[field] = value
                self.assertIn("invalid_surface_shape", self.error_codes(self.state_with(surface)))

        invalid_materiality = surface_record(classification="NON_MATERIAL")
        invalid_materiality["materiality"] = {"classification": "MATERIAL"}
        self.assertIn("invalid_materiality", self.error_codes(self.state_with(invalid_materiality)))

        for kind in SURFACE_KINDS:
            with self.subTest(kind=kind):
                surface = surface_record(kind=kind, classification="NON_MATERIAL")
                self.assertEqual(self.error_codes(self.state_with(surface)), set())
        for status in SURFACE_STATUSES:
            with self.subTest(status=status):
                surface = surface_record(status=status, classification="NON_MATERIAL")
                state = self.state_with(surface)
                if status == "SUPERSEDED":
                    replacement = surface_record("SURF-002", classification="NON_MATERIAL")
                    state["surface_manifest"]["records"][0]["superseded_by"] = "SURF-002"
                    state["surface_manifest"]["records"].append(replacement)
                elif status == "RETIRED":
                    add_decision(state)
                    state["surface_manifest"]["records"][0].update({
                        "retired_by": "DEC-001", "retired_at_revision": 1,
                        "retirement_reason": "This surface was removed by a scope decision.",
                    })
                elif status == "OPEN":
                    state["surface_manifest"]["records"][0]["unknown_refs"] = ["UNK-001"]
                    state["objects"]["unknowns"] = [unknown_record()]
                elif status == "OUT_OF_SCOPE":
                    state["surface_manifest"]["records"][0].update({
                        "rationale": "A current scope decision excludes this surface.",
                        "decision_refs": ["DEC-001"],
                    })
                    add_decision(state)
                self.assertEqual(self.error_codes(state), set())

    def test_surface_references_resolve_to_their_required_record_types(self):
        surface = surface_record(classification="NON_MATERIAL")
        surface.update({
            "evidence_refs": ["EVD-001"], "unknown_refs": ["UNK-001"],
            "decision_refs": ["DEC-001"], "contradiction_refs": ["CON-001"],
        })
        state = self.state_with(surface)
        state["evidence"] = [evidence_record(), evidence_record("EVD-002")]
        state["objects"]["unknowns"] = [unknown_record()]
        add_decision(state)
        state["contradictions"] = [{
            "id": "CON-001", "status": "OPEN",
            "claim_a_refs": ["EVD-001"], "claim_b_refs": ["EVD-002"],
            "scope_refs": ["SURF-001"],
            "materiality": materiality(classification="NON_MATERIAL"),
            "resolution": None, "resolved_by": [], "selected_authority_refs": [],
        }]
        self.assertEqual(self.error_codes(state), set())

        invalid_refs = (
            ("evidence_refs", "EVD-999"), ("evidence_refs", "REQ-001"),
            ("unknown_refs", "UNK-999"), ("unknown_refs", "EVD-001"),
            ("decision_refs", "DEC-999"), ("decision_refs", "REQ-001"),
            ("contradiction_refs", "CON-999"), ("contradiction_refs", "EVD-001"),
        )
        for field, invalid_ref in invalid_refs:
            with self.subTest(field=field, invalid_ref=invalid_ref):
                invalid = copy.deepcopy(state)
                invalid["surface_manifest"]["records"][0][field] = [invalid_ref]
                self.assertIn("invalid_surface_reference", self.error_codes(invalid))

    def test_material_in_scope_requires_current_typed_authority(self):
        unbound = surface_record()
        self.assertIn("UNBOUND_PRODUCT_SURFACE", self.error_codes(self.state_with(unbound)))

        for prefix in ("REQ", "RULE", "FLOW", "DATA", "INT"):
            with self.subTest(prefix=prefix):
                surface = surface_record()
                state = self.state_with(surface)
                self.bind_current_authority(state, prefix)
                self.assertEqual(self.error_codes(state), set())

        stale = surface_record()
        stale_state = self.state_with(stale)
        group, record = authority_record("REQ", "REQ-001", status="STALE")
        stale_state["objects"][group] = [record]
        stale_state["surface_manifest"]["records"][0]["authority_refs"] = ["REQ-001"]
        self.assertIn("UNBOUND_PRODUCT_SURFACE", self.error_codes(stale_state))

    def test_material_open_requires_a_current_open_unknown(self):
        surface = surface_record(status="OPEN")
        self.assertIn("OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN", self.error_codes(self.state_with(surface)))

        valid = surface_record(status="OPEN")
        valid["unknown_refs"] = ["UNK-001"]
        state = self.state_with(valid)
        state["objects"]["unknowns"] = [unknown_record()]
        self.assertEqual(self.error_codes(state), set())

        resolved = copy.deepcopy(state)
        resolved["objects"]["unknowns"][0]["status"] = "RESOLVED"
        self.assertIn("OPEN_PRODUCT_SURFACE_WITHOUT_UNKNOWN", self.error_codes(resolved))

    def test_out_of_scope_requires_rationale_and_closure_capable_intent_or_current_decision(self):
        invalid = surface_record(status="OUT_OF_SCOPE", classification="NON_MATERIAL")
        self.assertIn("invalid_out_of_scope_surface", self.error_codes(self.state_with(invalid)))

        intent_based = surface_record(status="OUT_OF_SCOPE", classification="NON_MATERIAL")
        intent_based.update({"rationale": "The feedback form is intentionally excluded.", "evidence_refs": ["EVD-001"]})
        intent_state = self.state_with(intent_based)
        intent_state["evidence"] = [evidence_record(source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"])]
        self.assertEqual(self.error_codes(intent_state), set())

        decision_based = surface_record(status="OUT_OF_SCOPE", classification="NON_MATERIAL")
        decision_based.update({"rationale": "A scope decision removed this form.", "decision_refs": ["DEC-001"]})
        decision_state = self.state_with(decision_based)
        add_decision(decision_state)
        self.assertEqual(self.error_codes(decision_state), set())

    def test_observed_implementation_cannot_justify_out_of_scope(self):
        surface = surface_record(status="OUT_OF_SCOPE", classification="NON_MATERIAL")
        surface.update({"rationale": "The implementation has no feedback form.", "evidence_refs": ["EVD-001"]})
        state = self.state_with(surface)
        state["evidence"] = [evidence_record()]

        self.assertIn("invalid_out_of_scope_surface", self.error_codes(state))

    def test_superseded_surfaces_require_distinct_targets_and_cycles_fail(self):
        old = surface_record(status="SUPERSEDED", classification="NON_MATERIAL")
        old["superseded_by"] = "SURF-002"
        replacement = surface_record("SURF-002", classification="NON_MATERIAL")
        self.assertEqual(self.error_codes(self.state_with(old, replacement)), set())

        for target in ("SURF-001", "SURF-999", "REQ-001"):
            with self.subTest(target=target):
                invalid = copy.deepcopy(old)
                invalid["superseded_by"] = target
                self.assertIn("invalid_surface_supersession", self.error_codes(self.state_with(invalid)))

        first = copy.deepcopy(old)
        second = surface_record("SURF-002", status="SUPERSEDED", classification="NON_MATERIAL")
        second["superseded_by"] = "SURF-001"
        self.assertIn("surface_supersession_cycle", self.error_codes(self.state_with(first, second)))

    def test_retired_surfaces_require_typed_retirement_provenance(self):
        retired = surface_record(status="RETIRED", classification="NON_MATERIAL")
        retired.update({
            "retired_by": "DEC-001", "retired_at_revision": 1,
            "retirement_reason": "This form was retired by a scope decision.",
        })
        valid = self.state_with(retired)
        add_decision(valid)
        self.assertEqual(self.error_codes(valid), set())

        for field, value in (
            ("retired_by", "REQ-001"), ("retired_by", "DEC-999"),
            ("retired_at_revision", 0), ("retired_at_revision", 2),
            ("retirement_reason", "TBD"),
        ):
            with self.subTest(field=field, value=value):
                invalid = copy.deepcopy(valid)
                invalid["surface_manifest"]["records"][0][field] = value
                self.assertIn("invalid_surface_retirement", self.error_codes(invalid))

    def test_surface_metrics_count_only_material_open_and_unbound_surfaces(self):
        material_open = surface_record("SURF-001", status="OPEN")
        material_open["unknown_refs"] = ["UNK-001"]
        non_material_open = surface_record("SURF-002", status="OPEN", classification="NON_MATERIAL")
        unbound = surface_record("SURF-003")
        state = self.state_with(material_open, non_material_open, unbound)
        state["objects"]["unknowns"] = [unknown_record()]

        metrics = evaluate_closure_v2(state)["metrics"]
        self.assertEqual(metrics["semantic_closure_not_implemented"], 1)
        self.assertEqual(metrics["open_material_surfaces"], 1)
        self.assertEqual(metrics["unbound_material_surfaces"], 1)


if __name__ == "__main__":
    unittest.main()
