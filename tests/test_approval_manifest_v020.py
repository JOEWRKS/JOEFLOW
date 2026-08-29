import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
SCHEMA = ROOT / "skills" / "joewrks-product-definition" / "schemas" / "state-v0.2.0.schema.json"
TEMPLATE = ROOT / "skills" / "joewrks-product-definition" / "templates" / "state-v0.2.0.example.json"
CLI = SCRIPTS / "build_approval_manifest.py"
sys.path.insert(0, str(SCRIPTS))

try:
    import approval_v2 as approval
except ModuleNotFoundError:
    approval = None

from discovery_v2 import build_discovery_baseline  # noqa: E402
from tests.v020_support import (  # noqa: E402
    establish_current_baseline,
    evidence_record,
    foundation_state,
    materiality,
    review_ready_state,
    unknown_record,
)


def api(name):
    if approval is None or not hasattr(approval, name):
        raise AssertionError(f"missing Task 5 API: {name}")
    return getattr(approval, name)


def record_change_state(revision=1):
    state = foundation_state()
    state["project"]["definition_revision"] = revision
    state["objects"]["requirements"] = [
        {
            "id": "REQ-001", "status": "CURRENT", "statement": "Users can submit feedback.",
            "scope": "Feedback", "ui_required": True, "materiality": materiality(),
        },
        {
            "id": "REQ-002", "status": "CURRENT", "statement": "Users can edit feedback.",
            "scope": "Feedback", "ui_required": True, "materiality": materiality(),
        },
    ]
    state["objects"]["rules"] = [{
        "id": "RULE-001", "status": "CURRENT", "statement": "Feedback is retained.", "applies_to": ["REQ-001"],
    }]
    state["objects"]["data"] = [{
        "id": "DATA-001", "status": "CURRENT", "name": "Feedback", "purpose": "Store feedback.", "ownership": "USER",
    }]
    establish_current_baseline(state)
    return state


def approved_state():
    state = review_ready_state()
    manifest = api("compute_approval_manifest")(state)
    commitment = api("build_approval_commitment")(state, manifest)
    state["approval_history"] = [commitment]
    state["approval"] = {
        "status": "APPROVED",
        "approved_revision": 1,
        "approved_definition_digest": commitment["definition_digest"],
        "approved_manifest_digest": commitment["manifest_digest"],
        "approved_at": "2026-08-29T00:00:00Z",
        "approved_by": "user",
    }
    state["project"]["definition_status"] = "CLOSED"
    return state


class ApprovalManifestV020Test(unittest.TestCase):
    def test_first_manifest_uses_literal_schema_summary_and_informed_added_rows(self):
        # Break caught: first approval showing opaque IDs or an unstable/generated summary instead of canonical meaning.
        state = record_change_state()
        manifest = api("compute_approval_manifest")(state)

        self.assertEqual(set(manifest), {
            "schema_version", "from_revision", "to_revision", "added", "changed",
            "superseded", "retired", "high_risk_decisions", "deferred_non_blocking",
            "active_grill_packs", "binding_contracts", "semantic_closure_summary",
            "definition_digest",
        })
        self.assertEqual(manifest["schema_version"], "joewrks.approval-manifest/1.0")
        self.assertIsNone(manifest["from_revision"])
        self.assertEqual(manifest["to_revision"], 1)
        self.assertIn({"id": "REQ-001", "type": "REQ", "summary": "Users can submit feedback."}, manifest["added"])
        self.assertEqual(manifest["changed"], [])
        self.assertEqual(manifest["superseded"], [])
        self.assertEqual(manifest["retired"], [])

    def test_later_manifest_uses_previous_revision_and_literal_change_classification(self):
        # Break caught: current-revision history or lifecycle transitions corrupting the previous-revision semantic diff.
        previous = record_change_state(1)
        previous_manifest = api("compute_approval_manifest")(previous)
        previous_commitment = api("build_approval_commitment")(previous, previous_manifest)

        state = copy.deepcopy(previous)
        state["project"]["definition_revision"] = 2
        state["approval_history"] = [previous_commitment]
        state["objects"]["requirements"][1].update({"status": "SUPERSEDED", "superseded_by": "REQ-003"})
        state["objects"]["requirements"].append({
            "id": "REQ-003", "status": "CURRENT", "statement": "Users can revise feedback.",
            "scope": "Feedback", "ui_required": True, "materiality": materiality(),
        })
        state["objects"]["rules"][0]["statement"] = "Feedback is retained for review."
        state["objects"]["data"][0].update({
            "status": "RETIRED", "retired_by": "DEC-999", "retired_at_revision": 2,
            "retirement_reason": "The product no longer stores this record.",
        })
        establish_current_baseline(state)
        manifest = api("compute_approval_manifest")(state)

        self.assertEqual(manifest["from_revision"], 1)
        self.assertEqual(manifest["added"], [
            {"id": "REQ-003", "type": "REQ", "summary": "Users can revise feedback."},
        ])
        self.assertEqual(manifest["changed"], [
            {"id": "RULE-001", "type": "RULE", "summary": "Feedback is retained for review."},
        ])
        self.assertEqual(manifest["superseded"], [
            {"id": "REQ-002", "type": "REQ", "summary": "Users can edit feedback."},
        ])
        self.assertEqual(manifest["retired"], [
            {"id": "DATA-001", "type": "DATA", "summary": "Feedback"},
        ])

    def test_manifest_exposes_high_risk_decisions_deferred_unknowns_packs_and_contracts(self):
        # Break caught: approval hiding risk/deferral meaning or the exact pack/contract identities from the user.
        state = record_change_state()
        high_risk = materiality(classification="MATERIAL")
        high_risk["reversibility"] = "IRREVERSIBLE"
        high_risk["risk_flags"]["privacy"] = True
        high_risk["risk_flags"]["data_loss"] = True
        state["objects"]["decisions"] = [{
            "id": "DEC-001", "status": "CURRENT", "statement": "Permanently delete expired feedback.",
            "decision_type": "RETENTION", "resolution_mode": "USER_DECISION",
            "decision_authority": "USER_DECISION_REQUIRED", "source_unknown_refs": [],
            "evidence_refs": [], "materiality": high_risk, "affects": [],
            "decided_by": "USER", "accepted_recommendation": None,
        }]
        deferred = unknown_record("UNK-001", status="DEFERRED", classification="NON_MATERIAL")
        deferred["question"] = "Should exports support custom colors?"
        deferred["deferral"] = {
            "reason": "The first release uses the default palette.", "accepted_by": "user",
            "impact_review": {key: "No current impact." for key in (
                "scope", "rules", "flows", "states", "privacy", "money", "security", "acceptance",
            )},
        }
        state["objects"]["unknowns"] = [deferred]
        manifest = api("compute_approval_manifest")(state)

        self.assertEqual(manifest["high_risk_decisions"], [{
            "id": "DEC-001", "statement": "Permanently delete expired feedback.",
            "reversibility": "IRREVERSIBLE", "risk_flags": ["data_loss", "privacy"],
        }])
        self.assertEqual(manifest["deferred_non_blocking"], [{
            "id": "UNK-001", "question": "Should exports support custom colors?",
            "reason": "The first release uses the default palette.",
        }])
        self.assertEqual(manifest["active_grill_packs"], state["discovery_baseline"]["active_grill_packs"])
        self.assertEqual(manifest["binding_contracts"], {
            "product_binding_contract": state["project"]["closure_contract"]["product_binding_contract"],
            "ux_binding_contract": state["project"]["closure_contract"]["ux_binding_contract"],
        })

    def test_manifest_digest_and_commitment_are_stable_non_recursive_and_exact(self):
        # Break caught: digest recursion, nondeterministic commitment bytes, or a missing semantic commitment layer.
        state = record_change_state()
        manifest = api("compute_approval_manifest")(state)
        first_digest = api("approval_manifest_digest")(manifest)
        second_digest = api("approval_manifest_digest")(copy.deepcopy(manifest))
        commitment = api("build_approval_commitment")(state, manifest)

        self.assertNotIn("manifest_digest", manifest)
        self.assertEqual(first_digest, second_digest)
        self.assertEqual(set(commitment), {
            "revision", "definition_digest", "manifest_digest", "record_hashes",
            "coverage_digest", "surface_digest", "grill_pack_set_digest",
        })
        self.assertEqual(commitment["revision"], 1)
        self.assertEqual(commitment["definition_digest"], manifest["definition_digest"])
        self.assertEqual(commitment["manifest_digest"], first_digest)
        for field in ("definition_digest", "manifest_digest", "coverage_digest", "surface_digest", "grill_pack_set_digest"):
            self.assertEqual(len(commitment[field]), 64, field)
            int(commitment[field], 16)

    def test_unconsumed_evidence_does_not_change_manifest_or_any_semantic_commitment(self):
        # Break caught: unrelated observation appearing as an approval change after the required baseline refresh.
        state = record_change_state()
        before_manifest = api("compute_approval_manifest")(state)
        before_commitment = api("build_approval_commitment")(state, before_manifest)
        state["evidence"].append(evidence_record("EVD-001"))
        establish_current_baseline(state)
        after_manifest = api("compute_approval_manifest")(state)
        after_commitment = api("build_approval_commitment")(state, after_manifest)

        self.assertEqual(after_manifest, before_manifest)
        self.assertEqual(after_commitment, before_commitment)
        self.assertNotIn("EVD-001", after_commitment["record_hashes"])
        self.assertNotIn("EVD-001", {row["id"] for row in after_manifest["added"]})

    def test_pure_manifest_is_identical_across_ready_unapproved_to_closed_approved_transition(self):
        # Break caught: approval control state feeding back into the manifest that the recorded approval must validate.
        ready = review_ready_state()
        before = api("compute_approval_manifest")(ready)
        commitment = api("build_approval_commitment")(ready, before)
        closed = copy.deepcopy(ready)
        closed["project"]["definition_status"] = "CLOSED"
        closed["approval_history"] = [commitment]
        closed["approval"] = {
            "status": "APPROVED", "approved_revision": 1,
            "approved_definition_digest": commitment["definition_digest"],
            "approved_manifest_digest": commitment["manifest_digest"],
            "approved_at": "2026-08-29T00:00:00Z", "approved_by": "user",
        }
        after = api("compute_approval_manifest")(closed)

        self.assertEqual(after, before)
        self.assertEqual(api("approval_manifest_digest")(after), commitment["manifest_digest"])
        self.assertNotIn("missing_user_approval", after["semantic_closure_summary"])
        self.assertNotIn("semantic_change_without_revision_increment", after["semantic_closure_summary"])

    def test_review_builder_requires_ready_unapproved_current_zero_blocker_state(self):
        # Break caught: the user-facing compiler producing an approval packet for stale, blocked, or already-approved input.
        ready = review_ready_state()
        self.assertEqual(api("build_approval_manifest_for_review")(ready), api("compute_approval_manifest")(ready))

        wrong_status = copy.deepcopy(ready)
        wrong_status["project"]["definition_status"] = "OPEN"
        stale = copy.deepcopy(ready)
        stale["discovery_baseline"] = {"status": "STALE"}
        fabricated = copy.deepcopy(ready)
        fabricated["approval"] = {"status": "APPROVED"}
        for candidate in (wrong_status, stale, fabricated):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    api("build_approval_manifest_for_review")(candidate)

    def test_read_only_cli_emits_compact_packet_and_never_fabricates_approval_time(self):
        # Break caught: CLI mutating state, pretty/noncanonical output, or silently authoring a user approval timestamp.
        state = review_ready_state()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            original = json.dumps(state, ensure_ascii=False, indent=2)
            path.write_text(original, encoding="utf-8")
            result = subprocess.run([sys.executable, str(CLI), str(path)], capture_output=True, text=True, check=False)
            after = path.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        self.assertEqual(set(packet), {"manifest", "manifest_digest", "approval_commitment"})
        self.assertEqual(result.stdout.strip(), json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        self.assertEqual(after, original)
        self.assertNotIn("approved_at", result.stdout)
        self.assertNotIn("approved_by", result.stdout)

    def test_cli_refuses_invalid_not_ready_and_malformed_input(self):
        # Break caught: command-line lifecycle gate bypass or Python accepting non-standard JSON constants.
        candidates = [foundation_state(), review_ready_state()]
        candidates[1]["approval"] = {"status": "UNAPPROVED", "fabricated": True}
        with tempfile.TemporaryDirectory() as directory:
            for position, state in enumerate(candidates):
                path = Path(directory) / f"state-{position}.json"
                path.write_text(json.dumps(state), encoding="utf-8")
                result = subprocess.run([sys.executable, str(CLI), str(path)], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 1, result)
            nan_path = Path(directory) / "nan.json"
            nan_path.write_text('{"value":NaN}', encoding="utf-8")
            nan_result = subprocess.run([sys.executable, str(CLI), str(nan_path)], capture_output=True, text=True, check=False)
        self.assertEqual(nan_result.returncode, 2)


class ApprovalValidationV020Test(unittest.TestCase):
    def codes(self, state):
        return {error["code"] for error in api("validate_approval")(state)}

    def test_exact_recorded_user_approval_and_current_commitment_validate(self):
        # Break caught: the canonical exact approval form being rejected after control-state transition.
        state = approved_state()
        self.assertEqual(api("validate_approval")(state), [])
        self.assertEqual(api("approval_metrics")(state), {
            "missing_user_approval": 0,
            "stale_approval": 0,
            "missing_or_stale_approval_manifest": 0,
            "approval_history_gaps": 0,
            "semantic_change_without_revision_increment": 0,
            "approved_record_missing_from_state": 0,
        })

    def test_digest_revision_manifest_and_human_fields_are_exact(self):
        # Break caught: any approximate or fabricated approval claim satisfying M4 validation.
        cases = []
        definition = approved_state()
        definition["approval"]["approved_definition_digest"] = "0" * 64
        cases.append((definition, "stale_approval"))
        revision = approved_state()
        revision["approval"]["approved_revision"] = 2
        cases.append((revision, "stale_approval"))
        manifest = approved_state()
        manifest["approval"]["approved_manifest_digest"] = "0" * 64
        cases.append((manifest, "missing_or_stale_approval_manifest"))
        actor = approved_state()
        actor["approval"]["approved_by"] = "agent"
        cases.append((actor, "missing_user_approval"))
        for timestamp in ("", "fabricated", None):
            candidate = approved_state()
            candidate["approval"]["approved_at"] = timestamp
            cases.append((candidate, "missing_user_approval"))

        for candidate, code in cases:
            with self.subTest(code=code, approval=candidate["approval"]):
                self.assertIn(code, self.codes(candidate))

    def test_unapproved_is_exact_and_cannot_carry_fabricated_approval_fields(self):
        # Break caught: stale approval fields surviving under an UNAPPROVED label.
        state = review_ready_state()
        self.assertEqual(api("validate_approval")(state), [])
        state["approval"]["approved_at"] = "2026-08-29T00:00:00Z"
        self.assertIn("invalid_approval", self.codes(state))

    def test_current_history_commitment_is_required_unique_and_not_replaced_by_previous_history(self):
        # Break caught: no current commitment, a duplicate, or an older commitment satisfying current approval.
        missing = approved_state()
        missing["approval_history"] = []
        self.assertIn("approval_history_gaps", self.codes(missing))

        duplicate = approved_state()
        duplicate["approval_history"].append(copy.deepcopy(duplicate["approval_history"][0]))
        self.assertIn("approval_history_gaps", self.codes(duplicate))

        previous_only = approved_state()
        previous_only["project"]["definition_revision"] = 2
        previous_only["approval"]["approved_revision"] = 2
        establish_current_baseline(previous_only)
        self.assertIn("approval_history_gaps", self.codes(previous_only))

    def test_malformed_history_revision_returns_a_finding_instead_of_crashing(self):
        # Break caught: an unhashable malformed revision escaping deterministic validation through a Python exception.
        state = review_ready_state()
        state["approval_history"] = [{"revision": []}]

        self.assertIn("approval_history_gaps", self.codes(state))

    def test_altered_current_commitment_and_same_revision_semantic_edit_are_blocked(self):
        # Break caught: exact historical/hash drift being accepted or re-approved without incrementing definition_revision.
        altered = approved_state()
        altered["approval_history"][0]["record_hashes"]["EVD-900"] = "0" * 64
        self.assertIn("approval_history_gaps", self.codes(altered))
        self.assertEqual(api("approval_metrics")(altered)["semantic_change_without_revision_increment"], 1)

        changed = approved_state()
        changed["surface_manifest"]["grill_profile"]["AUTH"]["rationale"] = "A changed semantic classification rationale."
        changed["discovery_baseline"] = build_discovery_baseline(
            changed, procedure_complete=True, applicable_surface_classes_complete=True,
        )
        self.assertIn("semantic_change_without_revision_increment", self.codes(changed))

    def test_unconsumed_evidence_refresh_preserves_approval_and_same_revision_commitment(self):
        # Break caught: unrelated EVD discovery falsely invalidating an exact recorded approval after freshness rebuild.
        state = approved_state()
        state["evidence"].append(evidence_record("EVD-001"))
        state["discovery_baseline"] = build_discovery_baseline(
            state, procedure_complete=True, applicable_surface_classes_complete=True,
        )
        self.assertEqual(api("validate_approval")(state), [])
        self.assertEqual(api("approval_metrics")(state)["semantic_change_without_revision_increment"], 0)

    def test_previous_approved_record_must_remain_even_if_evidence_is_no_longer_consumed(self):
        # Break caught: deleting an approved stable ID being treated as implicit retirement.
        revision_one = review_ready_state()
        revision_one["evidence"].append(evidence_record(
            "EVD-001", source_kind="DOCUMENTED_INTENT", authority_classes=["INTENT"],
        ))
        revision_one["objects"]["decisions"] = [{
            "id": "DEC-001", "status": "CURRENT", "statement": "Use the confirmed policy source.",
            "decision_type": "PRODUCT_POLICY", "resolution_mode": "EVIDENCE",
            "decision_authority": "EVIDENCE_RESOLVABLE", "source_unknown_refs": [],
            "evidence_refs": ["EVD-001"], "materiality": materiality(), "affects": [],
            "decided_by": "AGENT", "accepted_recommendation": None,
        }]
        establish_current_baseline(revision_one)
        manifest_one = api("compute_approval_manifest")(revision_one)
        commitment_one = api("build_approval_commitment")(revision_one, manifest_one)

        revision_two = copy.deepcopy(revision_one)
        revision_two["project"]["definition_revision"] = 2
        revision_two["objects"]["decisions"][0]["status"] = "STALE"
        revision_two["approval_history"] = [commitment_one]
        establish_current_baseline(revision_two)
        self.assertEqual(api("approval_metrics")(revision_two)["approved_record_missing_from_state"], 0)

        revision_two["evidence"] = [record for record in revision_two["evidence"] if record["id"] != "EVD-001"]
        self.assertEqual(api("approval_metrics")(revision_two)["approved_record_missing_from_state"], 1)
        self.assertIn("approved_record_missing_from_state", self.codes(revision_two))

    def test_schema_and_template_freeze_two_exact_approval_layers(self):
        # Break caught: schema accepting open-ended approval/history objects or the shared template becoming pre-approved.
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        approval_schema = schema["$defs"].get("approval")
        commitment_schema = schema["$defs"].get("approval_commitment")

        self.assertIsNotNone(approval_schema, "missing Task 5 approval schema")
        self.assertIsNotNone(commitment_schema, "missing Task 5 approval commitment schema")
        self.assertFalse(approval_schema.get("additionalProperties", True))
        self.assertEqual(len(approval_schema["oneOf"]), 2)
        self.assertEqual(set(commitment_schema["required"]), {
            "revision", "definition_digest", "manifest_digest", "record_hashes",
            "coverage_digest", "surface_digest", "grill_pack_set_digest",
        })
        self.assertEqual(template["project"]["definition_status"], "OPEN")
        self.assertEqual(template["approval"], {"status": "UNAPPROVED"})
        self.assertEqual(template["approval_history"], [])


if __name__ == "__main__":
    unittest.main()
