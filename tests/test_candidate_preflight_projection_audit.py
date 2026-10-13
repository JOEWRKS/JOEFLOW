import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

try:
    import candidate_preflight_v2
except ModuleNotFoundError:
    candidate_preflight_v2 = None

try:
    import projection_audit_v2
except ModuleNotFoundError:
    projection_audit_v2 = None

from approval_v2 import (  # noqa: E402
    approval_manifest_digest,
    build_approval_commitment,
    compute_approval_manifest,
    definition_digest,
)
from authority_binding_v2 import make_authority_binding  # noqa: E402
from tests.test_semantic_closure_v020 import literal_ready_state  # noqa: E402
from tests.v020_support import establish_current_baseline, materiality  # noqa: E402


def require(module, name):
    value = getattr(module, name, None) if module else None
    if value is None:
        raise AssertionError(f"missing implementation: {name}")
    return value


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approved_literal_state():
    state = literal_ready_state()
    manifest = compute_approval_manifest(state)
    commitment = build_approval_commitment(state, manifest)
    state["approval_history"] = [commitment]
    state["approval"] = {
        "status": "APPROVED",
        "approved_revision": 1,
        "approved_definition_digest": commitment["definition_digest"],
        "approved_manifest_digest": approval_manifest_digest(manifest),
        "approved_at": "2026-10-13T00:00:00Z",
        "approved_by": "user",
    }
    state["project"]["definition_status"] = "CLOSED"
    return state


def review(
    status, *, findings, scope=("RULE-001/statement",), reviewer=None,
    evidence=None, projection_sha256=None, source_sha256=None,
    render_required=False, render_status="NOT_REQUIRED", render_findings=(),
    render_reviewer=None, render_evidence=None, render_scope=(),
    rendered_projection_sha256=None, rendered_source_sha256=None,
):
    return {
        "scope": list(scope),
        "semantic_status": status,
        "semantic_findings": findings,
        "reviewer": reviewer,
        "review_evidence": evidence,
        "reviewed_projection_sha256": projection_sha256,
        "reviewed_source_sha256": source_sha256,
        "render_required": render_required,
        "render_status": render_status,
        "render_findings": list(render_findings) if render_findings is not None else None,
        "render_reviewer": render_reviewer,
        "render_evidence": render_evidence,
        "render_scope": list(render_scope),
        "rendered_projection_sha256": rendered_projection_sha256,
        "rendered_source_sha256": rendered_source_sha256,
    }


class CandidatePreflightTests(unittest.TestCase):
    def run_preflight(self, state, canonical=None):
        function = require(candidate_preflight_v2, "preflight_state")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate_path = root / "candidate.json"
            write_json(candidate_path, state)
            before = sha256(candidate_path)
            canonical_path = None
            canonical_before = None
            if canonical is not None:
                canonical_path = root / "canonical.json"
                write_json(canonical_path, canonical)
                canonical_before = sha256(canonical_path)
            result = function(candidate_path, canonical_path)
            after = sha256(candidate_path)
            canonical_after = sha256(canonical_path) if canonical_path else None
        self.assertEqual(before, after)
        self.assertEqual(canonical_before, canonical_after)
        return result

    def test_ready_unapproved_candidate_passes_without_fabricating_user_approval(self):
        result = self.run_preflight(literal_ready_state(), approved_literal_state())

        self.assertEqual(result["schema_version"], "joewrks.state-candidate-preflight/1.0")
        self.assertEqual(result["overall_status"], "PASS")
        self.assertEqual(result["stages"], {
            "state_validation": "PASS",
            "semantic_readiness": "PASS",
            "manifest_review_readiness": "PASS",
            "user_approval": "UNAPPROVED",
        })
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["next_action"], "PRESENT_EXACT_MANIFEST_FOR_USER_REVIEW")
        self.assertTrue(result["source_unchanged"])
        self.assertTrue(result["canonical_unchanged"])

    def test_orphan_reports_exact_id_pointer_cause_and_next_action(self):
        state = literal_ready_state()
        state["objects"]["rules"].append({
            "id": "RULE-055",
            "status": "CURRENT",
            "statement": "A new material boundary remains connected to its requirement.",
            "applies_to": ["REQ-001"],
        })
        establish_current_baseline(state)

        result = self.run_preflight(state)
        finding = next(item for item in result["findings"] if item["code"] == "orphan_material_authority")
        self.assertEqual(finding["object_id"], "RULE-055")
        self.assertEqual(finding["pointer"], "/objects/rules/1")
        self.assertIn("semantic sink", finding["cause"])
        self.assertEqual(finding["next_action"], "CONNECT_EXISTING_MEANING_TO_AN_ALLOWED_SEMANTIC_SINK_THEN_RERUN")
        self.assertEqual(result["overall_status"], "FAIL")

    def test_wrong_binding_type_reports_actual_and_allowed_types(self):
        state = literal_ready_state()
        state["coverage"][0]["cells"]["goal"]["authority_bindings"] = [
            make_authority_binding(state, "RULE-001", "/statement")
        ]
        establish_current_baseline(state)

        result = self.run_preflight(state)
        finding = next(item for item in result["findings"] if item["code"] == "invalid_authority_binding_type")
        self.assertEqual(finding["object_id"], "RULE-001")
        self.assertEqual(finding["pointer"], "/coverage/0/cells/goal/authority_bindings/0")
        self.assertEqual(finding["actual"], {"record_id": "RULE-001", "record_type": "RULE"})
        self.assertEqual(finding["allowed_types"], ["GOAL", "REQ"])
        self.assertEqual(finding["next_action"], "SELECT_AUTHORITY_OF_AN_ALLOWED_TYPE_WITHOUT_CHANGING_PRODUCT_MEANING")

    def test_wrong_binding_type_after_valid_binding_reports_the_actual_violation(self):
        state = literal_ready_state()
        valid = state["coverage"][0]["cells"]["goal"]["authority_bindings"][0]
        invalid = make_authority_binding(state, "RULE-001", "/statement")
        state["coverage"][0]["cells"]["goal"]["authority_bindings"] = [valid, invalid]
        establish_current_baseline(state)

        result = self.run_preflight(state)
        finding = next(item for item in result["findings"] if item["code"] == "invalid_authority_binding_type")
        self.assertEqual(finding["object_id"], "RULE-001")
        self.assertEqual(finding["actual"], {"record_id": "RULE-001", "record_type": "RULE"})
        self.assertEqual(finding["pointer"], "/coverage/0/cells/goal/authority_bindings/1")

    def test_duplicate_and_lifecycle_errors_are_concrete_and_fail_closed(self):
        duplicate = literal_ready_state()
        duplicate["objects"]["rules"].append(copy.deepcopy(duplicate["objects"]["rules"][0]))
        duplicate_result = self.run_preflight(duplicate)
        duplicate_finding = next(item for item in duplicate_result["findings"] if "duplicate" in item["code"])
        self.assertEqual(duplicate_finding["object_id"], "RULE-001")
        self.assertIsNotNone(duplicate_finding["pointer"])

        lifecycle = literal_ready_state()
        lifecycle["objects"]["rules"][0]["status"] = "SUPERSEDED"
        lifecycle_result = self.run_preflight(lifecycle)
        self.assertEqual(lifecycle_result["overall_status"], "FAIL")
        self.assertTrue(any("supersed" in item["code"] or "lifecycle" in item["cause"].lower() for item in lifecycle_result["findings"]))

    def test_non_contiguous_long_id_is_not_rejected_for_sequence_gap(self):
        state = literal_ready_state()
        state["objects"]["rules"][0]["id"] = "RULE-1000"
        for row in state["coverage"]:
            for cell in row["cells"].values():
                for binding in cell.get("authority_bindings", []):
                    if binding["record_id"] == "RULE-001":
                        binding.update(make_authority_binding(state, "RULE-1000", binding["pointer"]))
        result = self.run_preflight(state)
        self.assertFalse(any(item["code"] == "non_contiguous_id" for item in result["findings"]))


class ProjectionAuditTests(unittest.TestCase):
    def make_input(self, root, *, second_status="NOT_REVIEWED", second_exists=True, receipt=None):
        state = approved_literal_state()
        canonical = root / "state.json"
        write_json(canonical, state)
        digest = definition_digest(state)
        master = root / "MASTER_PLANNING_SPEC.md"
        master.write_text(
            f"Revision 1\nDefinition digest {digest}\nOnly valid requests may be submitted.\n",
            encoding="utf-8",
        )
        html = root / "planning-review-core.html"
        if second_exists:
            html.write_text(
                f"<p>Revision 1</p><p>Definition digest {digest}</p><p>Only valid requests may be submitted.</p>",
                encoding="utf-8",
            )
        scope = root / "approved-scope.json"
        write_json(scope, {
            "scope_id": "planning-delivery",
            "required_projection_ids": ["master", "review-html"],
            "semantic_review_required_ids": ["master", "review-html"],
            "render_review_required_ids": [],
            "projection_contracts": {
                "master": {
                    "kind": "MARKDOWN",
                    "required_markers": ["Revision 1", "Definition digest"],
                    "semantic_coverage": ["RULE-001/statement"],
                    "recovery_owner": "PRODUCT_DEFINITION_OWNER",
                },
                "review-html": {
                    "kind": "HTML",
                    "required_markers": ["<p>Revision 1</p>", "Definition digest"],
                    "semantic_coverage": ["RULE-001/statement"],
                    "recovery_owner": "PRODUCT_DEFINITION_OWNER",
                },
            },
        })
        master_evidence = root / "master-review.json"
        write_json(master_evidence, {
            "reviewer": "fixture-product-reviewer",
            "projection_sha256": sha256(master),
            "source_sha256": sha256(canonical),
            "scope": ["RULE-001/statement"],
            "coverage": ["RULE-001/statement"],
            "verdict": "PASS",
        })
        html_evidence = root / "review-html-review.json"
        if second_status != "NOT_REVIEWED" and second_exists:
            write_json(html_evidence, {
                "reviewer": "fixture-product-reviewer",
                "projection_sha256": sha256(html),
                "source_sha256": sha256(canonical),
                "scope": ["RULE-001/statement"],
                "coverage": ["RULE-001/statement"],
                "verdict": second_status,
            })

        def evidence_ref(projection_id):
            path = master_evidence if projection_id == "master" else html_evidence
            return {
                "path": path.name,
                "sha256": sha256(path),
                "pointer": "",
            }

        projections = [
            {
                "projection_id": "master",
                "kind": "MARKDOWN",
                "path": master.name,
                "sha256": sha256(master),
                "required": True,
                "recovery_owner": "PRODUCT_DEFINITION_OWNER",
                "source_identity_tokens": [
                    {"field": "definition_revision", "value": 1, "token": "Revision 1"},
                    {"field": "definition_digest", "value": digest, "token": digest},
                ],
                "semantic_claims": [{
                    "record_id": "RULE-001",
                    "pointer": "/statement",
                    "projection_quote": "Only valid requests may be submitted.",
                }],
                "review": review(
                    "PASS", findings=[], reviewer="fixture-product-reviewer",
                    evidence=evidence_ref("master"), projection_sha256=sha256(master),
                    source_sha256=sha256(canonical),
                ),
            },
            {
                "projection_id": "review-html",
                "kind": "HTML",
                "path": html.name,
                "sha256": sha256(html) if second_exists else "0" * 64,
                "required": True,
                "recovery_owner": "PRODUCT_DEFINITION_OWNER",
                "source_identity_tokens": [
                    {"field": "definition_revision", "value": 1, "token": "Revision 1"},
                    {"field": "definition_digest", "value": digest, "token": digest},
                ],
                "semantic_claims": [{
                    "record_id": "RULE-001",
                    "pointer": "/statement",
                    "projection_quote": "Only valid requests may be submitted.",
                }],
                "review": review(
                    second_status,
                    findings=None if second_status == "NOT_REVIEWED" else [],
                    reviewer=None if second_status == "NOT_REVIEWED" else "fixture-product-reviewer",
                    evidence=None if second_status == "NOT_REVIEWED" or not second_exists else evidence_ref("review-html"),
                    projection_sha256=None if second_status == "NOT_REVIEWED" or not second_exists else sha256(html),
                    source_sha256=None if second_status == "NOT_REVIEWED" else sha256(canonical),
                ),
            },
        ]
        value = {
            "schema_version": "joewrks.projection-audit-input/1.0",
            "canonical_state": {"path": canonical.name, "sha256": sha256(canonical)},
            "scope_authority": {
                "path": scope.name,
                "sha256": sha256(scope),
                "pointer": "",
            },
            "projections": projections,
            "resume_receipt": receipt,
        }
        input_path = root / "audit-input.json"
        write_json(input_path, value)
        return input_path, canonical, master, html

    def test_unreviewed_semantics_are_unknown_not_zero_or_pass(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            input_path, canonical, master, html = self.make_input(Path(directory))
            before = {path.name: sha256(path) for path in (input_path, canonical, master, html)}
            result = audit(input_path)
            after = {path.name: sha256(path) for path in (input_path, canonical, master, html)}

        self.assertEqual(before, after)
        self.assertEqual(result["overall_status"], "PARTIAL")
        html_result = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(html_result["semantic_review"], {
            "status": "UNKNOWN",
            "findings": None,
            "coverage": ["RULE-001/statement"],
        })
        self.assertNotEqual(html_result["semantic_review"]["status"], "PASS")
        self.assertEqual(result["completed_projection_ids"], ["master"])
        self.assertEqual(result["pending_projection_ids"], ["review-html"])

    def test_identity_only_refresh_cannot_hide_semantic_drift(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, html = self.make_input(root, second_status="PASS")
            html.write_text(html.read_text(encoding="utf-8").replace(
                "Only valid requests may be submitted.", "Any request may be submitted.",
            ), encoding="utf-8")
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["projections"][1]["sha256"] = sha256(html)
            write_json(input_path, value)
            result = audit(input_path)

        html_result = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(html_result["source_identity"], "PASS")
        self.assertEqual(html_result["semantic_review"]["status"], "FAIL")
        self.assertTrue(any(item["code"] == "projection_claim_missing" for item in html_result["findings"]))

    def test_partial_failure_receipt_resumes_only_unchanged_completed_projection(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_input, _, master, _ = self.make_input(root, second_exists=False)
            first = audit(first_input)
            receipt = root / "receipt.json"
            write_json(receipt, first)
            second_input, _, _, html = self.make_input(root, second_status="PASS", receipt=receipt.name)
            master_hash = sha256(master)
            html_hash = sha256(html)
            second = audit(second_input)

        self.assertEqual(first["overall_status"], "PARTIAL")
        self.assertEqual(second["overall_status"], "PASS")
        self.assertEqual(second["resumed_projection_ids"], ["master"])
        self.assertEqual(second["completed_projection_ids"], ["master", "review-html"])
        self.assertEqual(second["failed_projection_ids"], [])
        self.assertEqual(second["projections"][0]["sha256"], master_hash)
        self.assertEqual(second["projections"][1]["sha256"], html_hash)

    def test_render_and_materialization_are_separate_from_semantic_review(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, _ = self.make_input(root, second_status="PASS", second_exists=False)
            result = audit(input_path)

        html_result = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(html_result["materialization"], "FAIL")
        self.assertEqual(html_result["render_review"], {"status": "NOT_REQUIRED", "findings": []})
        self.assertNotEqual(html_result["structure"], "PASS")

    def test_required_render_pass_requires_evidence_bound_to_current_bytes(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, canonical, _, html = self.make_input(root, second_status="PASS")
            scope_path = root / "approved-scope.json"
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            scope["render_review_required_ids"] = ["review-html"]
            write_json(scope_path, scope)
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["scope_authority"]["sha256"] = sha256(scope_path)
            review_value = value["projections"][1]["review"]
            review_value.update({
                "render_required": True,
                "render_status": "PASS",
                "render_findings": [],
                "render_reviewer": "fixture-render-reviewer",
                "render_scope": ["desktop", "mobile"],
                "rendered_projection_sha256": sha256(html),
                "rendered_source_sha256": sha256(canonical),
            })
            write_json(input_path, value)
            unbound = audit(input_path)

            evidence_path = root / "review-html-render.json"
            write_json(evidence_path, {
                "reviewer": "fixture-render-reviewer",
                "projection_sha256": sha256(html),
                "source_sha256": sha256(canonical),
                "scope": ["desktop", "mobile"],
                "verdict": "PASS",
            })
            value["projections"][1]["review"]["render_evidence"] = {
                "path": evidence_path.name,
                "sha256": sha256(evidence_path),
                "pointer": "",
            }
            write_json(input_path, value)
            bound = audit(input_path)

        unbound_html = next(item for item in unbound["projections"] if item["projection_id"] == "review-html")
        bound_html = next(item for item in bound["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(unbound_html["render_review"]["status"], "FAIL")
        self.assertTrue(any(item["code"] == "render_review_evidence_invalid" for item in unbound_html["findings"]))
        self.assertEqual(bound_html["render_review"], {"status": "PASS", "findings": []})
        self.assertEqual(bound["overall_status"], "PASS")

    def test_approved_scope_prevents_omission_and_required_flag_downgrade(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, _ = self.make_input(root, second_status="PASS")
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["projections"][0]["required"] = False
            value["projections"] = value["projections"][:1]
            write_json(input_path, value)
            result = audit(input_path)

        self.assertEqual(result["overall_status"], "PARTIAL")
        master = next(item for item in result["projections"] if item["projection_id"] == "master")
        omitted = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertTrue(any(item["code"] == "scope_requirement_downgrade" for item in master["findings"]))
        self.assertTrue(any(item["code"] == "required_projection_missing" for item in omitted["findings"]))

    def test_structure_coverage_and_recovery_owner_are_bound_to_approved_scope(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, _ = self.make_input(root, second_status="PASS")
            value = json.loads(input_path.read_text(encoding="utf-8"))
            declaration = value["projections"][1]
            declaration["kind"] = "MARKDOWN"
            declaration["recovery_owner"] = "CALLER_SELECTED_OWNER"
            declaration["review"]["scope"] = []
            evidence_path = root / "review-html-review.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["scope"] = []
            write_json(evidence_path, evidence)
            declaration["review"]["review_evidence"]["sha256"] = sha256(evidence_path)
            write_json(input_path, value)
            result = audit(input_path)

        projection = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(projection["structure"], "FAIL")
        self.assertEqual(projection["coverage"]["status"], "FAIL")
        self.assertEqual(projection["recovery_owner"], "PRODUCT_DEFINITION_OWNER")
        self.assertTrue(any(item["code"] == "projection_kind_mismatch" for item in projection["findings"]))
        self.assertTrue(any(item["code"] == "semantic_coverage_mismatch" for item in projection["findings"]))

    def test_empty_approved_projection_scope_is_rejected(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, _ = self.make_input(root, second_status="PASS")
            scope_path = root / "approved-scope.json"
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            scope["required_projection_ids"] = []
            scope["semantic_review_required_ids"] = []
            write_json(scope_path, scope)
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["scope_authority"]["sha256"] = sha256(scope_path)
            write_json(input_path, value)
            with self.assertRaisesRegex(ValueError, "at least one required projection"):
                audit(input_path)

    def test_resume_revalidates_current_review_evidence_instead_of_trusting_receipt(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, _ = self.make_input(root, second_status="PASS")
            first = audit(input_path)
            receipt = root / "receipt.json"
            write_json(receipt, first)

            evidence_path = root / "master-review.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["reviewer"] = "replacement-fixture-reviewer"
            write_json(evidence_path, evidence)
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["resume_receipt"] = receipt.name
            value["projections"][0]["review"]["reviewer"] = "replacement-fixture-reviewer"
            value["projections"][0]["review"]["review_evidence"]["sha256"] = sha256(evidence_path)
            write_json(input_path, value)
            second = audit(input_path)

        self.assertEqual(first["overall_status"], "PASS")
        self.assertEqual(second["overall_status"], "PASS")
        self.assertNotIn("master", second["resumed_projection_ids"])
        self.assertIn("review-html", second["resumed_projection_ids"])

    def test_bound_review_record_mismatch_fails_even_when_input_self_reports_pass(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, _ = self.make_input(root, second_status="PASS")
            evidence_path = root / "review-html-review.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["coverage"] = []
            write_json(evidence_path, evidence)
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["projections"][1]["review"]["review_evidence"]["sha256"] = sha256(evidence_path)
            write_json(input_path, value)
            result = audit(input_path)

        html_result = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(html_result["semantic_review"]["status"], "FAIL")
        self.assertTrue(any(item["code"] == "semantic_review_evidence_mismatch" for item in html_result["findings"]))

    def test_non_object_review_evidence_cannot_preserve_self_reported_pass(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, _ = self.make_input(root, second_status="PASS")
            evidence_path = root / "review-html-review.json"
            write_json(evidence_path, [])
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["projections"][1]["review"]["review_evidence"]["sha256"] = sha256(evidence_path)
            write_json(input_path, value)
            result = audit(input_path)

        html_result = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(html_result["semantic_review"]["status"], "FAIL")
        self.assertTrue(any(item["code"] == "semantic_review_evidence_mismatch" for item in html_result["findings"]))

    def test_null_semantic_and_render_evidence_cannot_preserve_self_reported_pass(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, canonical, _, html = self.make_input(root, second_status="PASS")
            scope_path = root / "approved-scope.json"
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            scope["render_review_required_ids"] = ["review-html"]
            write_json(scope_path, scope)
            null_evidence = root / "null-evidence.json"
            write_json(null_evidence, None)
            null_ref = {"path": null_evidence.name, "sha256": sha256(null_evidence), "pointer": ""}
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["scope_authority"]["sha256"] = sha256(scope_path)
            review_value = value["projections"][1]["review"]
            review_value.update({
                "review_evidence": null_ref,
                "render_required": True,
                "render_status": "PASS",
                "render_findings": [],
                "render_reviewer": "fixture-render-reviewer",
                "render_evidence": null_ref,
                "render_scope": ["desktop", "mobile"],
                "rendered_projection_sha256": sha256(html),
                "rendered_source_sha256": sha256(canonical),
            })
            write_json(input_path, value)
            result = audit(input_path)

        projection = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(projection["semantic_review"]["status"], "FAIL")
        self.assertEqual(projection["render_review"]["status"], "FAIL")
        self.assertTrue(any(item["code"] == "semantic_review_evidence_mismatch" for item in projection["findings"]))
        self.assertTrue(any(item["code"] == "render_review_evidence_mismatch" for item in projection["findings"]))

    def test_source_identity_token_must_contain_the_actual_declared_value(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, _, _, html = self.make_input(root, second_status="PASS")
            false_digest = "0" * 64
            html.write_text(html.read_text(encoding="utf-8").replace(
                next(token["value"] for token in json.loads(input_path.read_text(encoding="utf-8"))["projections"][1]["source_identity_tokens"] if token["field"] == "definition_digest"),
                false_digest,
            ), encoding="utf-8")
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["projections"][1]["sha256"] = sha256(html)
            value["projections"][1]["source_identity_tokens"][1]["token"] = false_digest
            review_path = root / "review-html-review.json"
            review_value = json.loads(review_path.read_text(encoding="utf-8"))
            review_value["projection_sha256"] = sha256(html)
            write_json(review_path, review_value)
            value["projections"][1]["review"]["reviewed_projection_sha256"] = sha256(html)
            value["projections"][1]["review"]["review_evidence"]["sha256"] = sha256(review_path)
            write_json(input_path, value)
            result = audit(input_path)

        html_result = next(item for item in result["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(html_result["source_identity"], "FAIL")
        self.assertTrue(any(item["code"] == "source_identity_missing" for item in html_result["findings"]))

    def test_manifest_projection_is_compared_to_current_builder_output(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path, canonical_path, _, _ = self.make_input(root, second_status="PASS")
            state = json.loads(canonical_path.read_text(encoding="utf-8"))
            manifest = compute_approval_manifest(state)
            manifest_path = root / "approval-manifest.json"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            evidence_path = root / "manifest-review.json"
            write_json(evidence_path, {
                "reviewer": "fixture-product-reviewer",
                "projection_sha256": sha256(manifest_path),
                "source_sha256": sha256(canonical_path),
                "scope": ["RULE-001/statement"],
                "coverage": ["RULE-001/statement"],
                "verdict": "PASS",
            })
            scope_path = root / "approved-scope.json"
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            for key in ("required_projection_ids", "semantic_review_required_ids"):
                scope[key].append("manifest")
            scope["projection_contracts"]["manifest"] = {
                "kind": "APPROVAL_MANIFEST",
                "required_markers": ["\"to_revision\":1"],
                "semantic_coverage": ["RULE-001/statement"],
                "recovery_owner": "PRODUCT_DEFINITION_OWNER",
            }
            write_json(scope_path, scope)
            value = json.loads(input_path.read_text(encoding="utf-8"))
            value["scope_authority"]["sha256"] = sha256(scope_path)
            value["projections"].append({
                "projection_id": "manifest",
                "kind": "APPROVAL_MANIFEST",
                "path": manifest_path.name,
                "sha256": sha256(manifest_path),
                "required": True,
                "recovery_owner": "PRODUCT_DEFINITION_OWNER",
                "source_identity_tokens": [
                    {"field": "definition_revision", "value": 1, "token": "\"to_revision\":1"},
                    {"field": "definition_digest", "value": definition_digest(state), "token": definition_digest(state)},
                ],
                "semantic_claims": [{
                    "record_id": "RULE-001",
                    "pointer": "/statement",
                    "projection_quote": "Only valid requests may be submitted.",
                }],
                "review": review(
                    "PASS", findings=[], reviewer="fixture-product-reviewer",
                    evidence={"path": evidence_path.name, "sha256": sha256(evidence_path), "pointer": ""},
                    projection_sha256=sha256(manifest_path), source_sha256=sha256(canonical_path),
                ),
            })
            write_json(input_path, value)
            good = audit(input_path)

            manifest["to_revision"] = 999
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["projection_sha256"] = sha256(manifest_path)
            write_json(evidence_path, evidence)
            value["projections"][-1]["sha256"] = sha256(manifest_path)
            value["projections"][-1]["review"]["reviewed_projection_sha256"] = sha256(manifest_path)
            value["projections"][-1]["review"]["review_evidence"]["sha256"] = sha256(evidence_path)
            write_json(input_path, value)
            bad = audit(input_path)

        self.assertEqual(good["overall_status"], "PASS")
        manifest_result = next(item for item in bad["projections"] if item["projection_id"] == "manifest")
        self.assertTrue(any(item["code"] == "approval_manifest_projection_mismatch" for item in manifest_result["findings"]))


class CheckedInFixtureTests(unittest.TestCase):
    def test_f03_checked_in_pass_and_error_inputs_are_executable(self):
        preflight = require(candidate_preflight_v2, "preflight_state")
        fixture = ROOT / "evals" / "joeflow-f03-f04" / "fixtures" / "f03"
        passed = preflight(fixture / "ready-for-review-candidate.json")
        failed = preflight(fixture / "malformed-candidate.json")

        self.assertEqual(passed["overall_status"], "PASS")
        self.assertEqual(passed["stages"]["user_approval"], "UNAPPROVED")
        self.assertEqual(failed["overall_status"], "FAIL")
        self.assertGreater(failed["summary"]["validation_error_count"], 0)

    def test_f04_checked_in_pass_and_partial_inputs_are_executable(self):
        audit = require(projection_audit_v2, "audit_projection_input")
        fixture = ROOT / "evals" / "joeflow-f03-f04" / "fixtures" / "f04"
        passed = audit(fixture / "audit-input-pass.json")
        partial = audit(fixture / "audit-input-partial.json")

        self.assertEqual(passed["overall_status"], "PASS")
        self.assertEqual(partial["overall_status"], "PARTIAL")
        self.assertEqual(partial["pending_projection_ids"], ["review-html"])
        pending = next(item for item in partial["projections"] if item["projection_id"] == "review-html")
        self.assertEqual(pending["semantic_review"]["findings"], None)


if __name__ == "__main__":
    unittest.main()
