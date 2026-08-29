import copy
import hashlib
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

from downstream_v2.derivation import (  # noqa: E402
    RESPONSIBILITY_PROFILE_ID,
    SemanticGap,
    derive_semantic_field,
    load_responsibility_profile,
    responsibility_profile_digest,
    seed_matches_selector,
)


ACTION = {
    "actor": ("DIRECT_REQUIRED", "INTENT", ["CORE:actor"]),
    "authentication": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:permission", "CORE:security", "GRILL:GRILL-AUTH-1:login", "GRILL:GRILL-AUTH-1:session_expiry", "GRILL:GRILL-AUTH-1:session_renewal"]),
    "relationship_predicate": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:permission", "CORE:boundary", "GRILL:GRILL-PERMISSION-1:role", "GRILL:GRILL-PERMISSION-1:resource_ownership"]),
    "object_binding": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:data", "CORE:state"]),
    "concurrency": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:alternative_path", "CORE:error", "CORE:recovery", "GRILL:GRILL-ASYNC-1:idempotency", "GRILL:GRILL-ASYNC-1:duplicate_execution", "UX_ACTION:duplicate_concurrent_action"]),
    "preconditions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:precondition", "UX_ACTION:precondition"]),
    "allowed_current_states": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state"]),
    "forbidden_states": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:boundary"]),
    "input_invariants": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:validation", "CORE:data", "UX_ACTION:input", "UX_ACTION:validation"]),
    "command": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:happy_path", "CORE:entry_point", "UX_ACTION:submit"]),
    "expected_domain_mutation": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:side_effect", "CORE:data", "CORE:persistence", "UX_ACTION:data_mutation"]),
    "forbidden_mutations": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary", "CORE:side_effect"]),
    "default_result": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:happy_path", "UX_ACTION:success", "UX_STATE:success"]),
    "result_expectations": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:happy_path", "CORE:alternative_path", "CORE:error", "CORE:recovery", "CORE:acceptance", "UX_ACTION:success", "UX_ACTION:failure", "UX_STATE:success", "UX_STATE:error"]),
    "version_result": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:persistence"]),
    "history_result": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:persistence", "CORE:data"]),
    "business_side_effects": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:side_effect"]),
    "delivery_effects": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:notification", "CORE:side_effect", "UX_ACTION:notification"]),
    "idempotency": ("DETERMINISTIC_REQUIRED", "INTENT", ["GRILL:GRILL-ASYNC-1:idempotency", "CORE:recovery", "CORE:side_effect"]),
    "rejection": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:error", "CORE:validation", "CORE:permission", "UX_ACTION:failure", "UX_ACTION:permission"]),
    "recovery": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:recovery", "GRILL:GRILL-ASYNC-1:retry", "GRILL:GRILL-ASYNC-1:reconciliation", "UX_ACTION:retry"]),
    "visible_success": ("REVIEW_PERMITTED", "PREFERENCE", ["UX_STATE:success", "UX_STATE:completed", "UX_ACTION:success", "CORE:acceptance"]),
    "visible_error": ("REVIEW_PERMITTED", "PREFERENCE", ["UX_STATE:error", "UX_ACTION:failure", "CORE:error"]),
    "superseded_rules": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary"]),
    "test_obligations": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:acceptance"]),
    "trace": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:goal", "CORE:acceptance"]),
}
LIFECYCLE = {
    "current_states": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state"]),
    "allowed_transitions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:happy_path", "CORE:alternative_path"]),
    "forbidden_transitions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:boundary"]),
    "boundary_conditions": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary", "CORE:precondition"]),
    "reversibility": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:recovery", "CORE:boundary", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:undo", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:irreversible_boundary"]),
    "reversal_window": ("DETERMINISTIC_REQUIRED", "INTENT", ["GRILL:GRILL-DESTRUCTIVE-ACTION-1:grace_period", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:undo", "CORE:boundary"]),
    "object_outcome": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:state", "CORE:side_effect"]),
    "required_reason": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:validation", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:reason"]),
    "required_confirmation": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:boundary", "CORE:permission", "GRILL:GRILL-DESTRUCTIVE-ACTION-1:confirmation"]),
    "required_evidence": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:validation", "CORE:data"]),
    "authority": ("DIRECT_REQUIRED", "INTENT", ["CORE:actor", "CORE:permission", "GRILL:GRILL-PERMISSION-1:role"]),
    "history_preservation": ("DETERMINISTIC_REQUIRED", "INTENT", ["CORE:persistence", "CORE:data"]),
}


def make_seed(key="SEED-001", *, scope="CORE", owner="REQ-001", axis="actor", pack_id=None, action_key=None, value=None):
    return {"seed_key": key, "location": {"scope": scope, "owner_ref": owner, "axis": axis, "pack_id": pack_id, "action_key": action_key}, "value": {"nested": {"item": ["exact", {"key": "value"}]}, "a": 1, "b": 2} if value is None else value}


class ResponsibilityProfileTests(unittest.TestCase):
    def test_profile_freezes_exact_inventory_policy_and_authority_classes(self):
        profile = load_responsibility_profile()
        self.assertEqual(profile["profile_id"], RESPONSIBILITY_PROFILE_ID)
        self.assertEqual(RESPONSIBILITY_PROFILE_ID, "joewrks.downstream-responsibility/1.0")
        for group, expected in (("action_fields", ACTION), ("lifecycle_fields", LIFECYCLE)):
            self.assertEqual(set(profile[group]), set(expected))
            for field, (expectation, authority_class, selectors) in expected.items():
                entry = profile[group][field]
                self.assertEqual(set(entry), {"expectation", "required_authority_class", "allowed_seed_selectors"})
                self.assertEqual(entry["expectation"], expectation)
                self.assertEqual(entry["required_authority_class"], authority_class)
                actual = [self.selector_text(selector) for selector in entry["allowed_seed_selectors"]]
                self.assertEqual(actual, selectors)
                self.assertEqual(len(actual), len(set(actual)))

    @staticmethod
    def selector_text(selector):
        if selector["scope"] == "GRILL":
            return f"GRILL:{selector['pack_id']}:{selector['axis']}"
        return f"{selector['scope']}:{selector['axis']}"

    def test_profile_digest_is_canonical_and_profile_drift_is_rejected(self):
        profile = load_responsibility_profile()
        canonical = json.dumps(profile, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(responsibility_profile_digest(), hashlib.sha256(canonical.encode("utf-8")).hexdigest())
        profile["action_fields"]["actor"]["unexpected"] = True
        with self.assertRaises(ValueError):
            derive_semantic_field({"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}, field_name="actor", field_kind="ACTION", context={"authority_scope_refs": ["REQ-001"], "current_scope_refs": ["REQ-001"]}, seeds={"SEED-001": make_seed()}, profile=profile)
        profile = load_responsibility_profile()
        del profile["action_fields"]["actor"]
        with self.assertRaises(ValueError):
            derive_semantic_field({"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}, field_name="actor", field_kind="ACTION", context={"authority_scope_refs": ["REQ-001"], "current_scope_refs": ["REQ-001"]}, seeds={"SEED-001": make_seed()}, profile=profile)


class DerivationTests(unittest.TestCase):
    def setUp(self):
        self.profile = load_responsibility_profile()
        self.context = {"authority_scope_refs": ["REQ-001", "SCR-001"], "current_scope_refs": ["REQ-001", "SCR-001"]}

    def derive(self, spec, field="actor", kind="ACTION", seed=None, context=None):
        seed = make_seed(axis="actor") if seed is None else seed
        return derive_semantic_field(spec, field_name=field, field_kind=kind, context=self.context if context is None else context, seeds={seed["seed_key"]: seed}, profile=self.profile)

    def test_direct_copies_one_permitted_seed_value_without_transformation(self):
        source = {"unicode": "한글", "items": [1, {"two": True}]}
        result = self.derive({"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}, seed=make_seed(axis="actor", value=source))
        self.assertEqual(result, {"value": source, "source_seed_refs": ["SEED-001"], "derivation": {"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}})

    def test_responsibility_levels_accept_only_their_permitted_derivations(self):
        direct = {"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}
        machine = {"kind": "MACHINE_DERIVED", "operator": "extract", "source_seed_ref": "SEED-001", "pointer": "/nested"}
        review = {"kind": "REVIEW_REQUIRED", "source_seed_refs": ["SEED-001"], "proposed_value": "reviewed", "why_structuring_is_insufficient": "A human judgment is required.", "interpretation_scope": "Presentation wording."}
        self.assertEqual(self.derive(direct)["value"], make_seed(axis="actor")["value"])
        for spec in (machine, review):
            with self.subTest(level="DIRECT_REQUIRED", spec=spec["kind"]):
                with self.assertRaises(ValueError): self.derive(spec)
        self.assertEqual(self.derive(direct, field="authentication", seed=make_seed(axis="permission"))["value"], make_seed(axis="permission")["value"])
        self.assertEqual(self.derive(machine, field="authentication", seed=make_seed(axis="permission"))["value"], {"item": ["exact", {"key": "value"}]})
        with self.assertRaises(ValueError): self.derive(review, field="authentication", seed=make_seed(axis="permission"))
        for spec in (direct, machine, review):
            with self.subTest(level="REVIEW_PERMITTED", spec=spec["kind"]):
                self.assertIn("value", self.derive(spec, field="visible_success", seed=make_seed(axis="success", scope="UX_STATE", owner="SCR-001")))

    def test_extract_uses_rfc_6901_and_rejects_empty_or_missing_pointers(self):
        seed = make_seed(axis="permission", value={"a/b": {"~key": "selected"}})
        result = self.derive({"kind": "MACHINE_DERIVED", "operator": "extract", "source_seed_ref": "SEED-001", "pointer": "/a~1b/~0key"}, field="authentication", seed=seed)
        self.assertEqual(result["value"], "selected")
        for spec in ({"kind": "MACHINE_DERIVED", "operator": "extract", "source_seed_ref": "SEED-001", "pointer": ""}, {"kind": "MACHINE_DERIVED", "operator": "extract", "source_seed_ref": "SEED-001", "pointer": "/missing"}):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError): self.derive(spec, field="authentication", seed=seed)

    def test_select_requires_existing_sorted_unique_object_keys(self):
        seed = make_seed(axis="permission", value={"a": 1, "b": {"v": 2}, "c": 3})
        result = self.derive({"kind": "MACHINE_DERIVED", "operator": "select", "source_seed_ref": "SEED-001", "keys": ["a", "b"]}, field="authentication", seed=seed)
        self.assertEqual(result["value"], {"a": 1, "b": {"v": 2}})
        for value, keys in ((["not", "object"], ["a"]), ({"a": 1}, ["a", "a"]), ({"a": 1, "b": 2}, ["b", "a"]), ({"a": 1}, ["missing"])):
            with self.subTest(value=value, keys=keys):
                with self.assertRaises(ValueError):
                    self.derive({"kind": "MACHINE_DERIVED", "operator": "select", "source_seed_ref": "SEED-001", "keys": keys}, field="authentication", seed=make_seed(axis="permission", value=value))

    def test_machine_operator_language_is_closed(self):
        for operator in ("exact", "eval", "expression", "template", "compose", "callback", "parse this natural language"):
            with self.subTest(operator=operator):
                with self.assertRaises(ValueError):
                    self.derive({"kind": "MACHINE_DERIVED", "operator": operator, "source_seed_ref": "SEED-001", "pointer": "/nested"}, field="authentication", seed=make_seed(axis="permission"))

    def test_scope_selector_and_ux_action_locator_must_all_match(self):
        direct = {"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}
        with self.assertRaises(ValueError): self.derive(direct, context={"authority_scope_refs": ["SCR-001"], "current_scope_refs": ["SCR-001"]})
        with self.assertRaises(ValueError): self.derive(direct, seed=make_seed(axis="permission"))
        ux_seed = make_seed(scope="UX_ACTION", owner="SCR-001", axis="submit", action_key="submit", value="send")
        ok_context = {"authority_scope_refs": ["SCR-001"], "current_scope_refs": ["SCR-001"], "ux_action_locator": {"screen_ref": "SCR-001", "action_key": "submit"}}
        self.assertEqual(self.derive(direct, field="command", seed=ux_seed, context=ok_context)["value"], "send")
        bad_context = copy.deepcopy(ok_context); bad_context["ux_action_locator"]["action_key"] = "save"
        with self.assertRaises(ValueError): self.derive(direct, field="command", seed=ux_seed, context=bad_context)

    def test_current_scope_inventory_is_required(self):
        direct = {"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}
        with self.assertRaises(ValueError):
            self.derive(direct, context={"authority_scope_refs": ["REQ-001"]})

    def test_current_scope_inventory_rejects_stale_scope_references(self):
        direct = {"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"}
        stale_seed = make_seed(owner="REQ-STALE", axis="actor")
        with self.assertRaises(ValueError):
            self.derive(direct, seed=stale_seed, context={"authority_scope_refs": ["REQ-STALE"], "current_scope_refs": ["REQ-001"]})

    def test_review_needs_meaningful_explanation_scope_and_permitted_seed(self):
        base = {"kind": "REVIEW_REQUIRED", "source_seed_refs": ["SEED-001"], "proposed_value": "reviewed", "why_structuring_is_insufficient": "A human judgment is required.", "interpretation_scope": "Presentation wording."}
        self.assertEqual(self.derive(base, field="visible_success", seed=make_seed(scope="UX_STATE", owner="SCR-001", axis="success"))["value"], "reviewed")
        for changed in ({"source_seed_refs": []}, {"why_structuring_is_insufficient": " "}, {"interpretation_scope": ""}):
            spec = copy.deepcopy(base); spec.update(changed)
            with self.subTest(changed=changed):
                with self.assertRaises(ValueError): self.derive(spec, field="visible_success", seed=make_seed(scope="UX_STATE", owner="SCR-001", axis="success"))
        with self.assertRaises(ValueError): self.derive(base, field="visible_success", seed=make_seed(scope="UX_STATE", owner="SCR-001", axis="error"))

    def test_unresolved_is_a_semantic_gap_and_never_a_derived_field(self):
        spec = {"kind": "UNRESOLVED", "gap_type": "AMBIGUITY_FOUND", "description": "The permitted state is unclear.", "required_authority_class": "FACTUAL", "evidence_refs": []}
        with self.assertRaises(SemanticGap) as raised:
            self.derive(spec)
        self.assertEqual(raised.exception.code, "SEMANTIC_GAP")
        self.assertEqual(raised.exception.detail, spec)

    def test_selector_matching_uses_exact_scope_axis_pack_and_ux_action(self):
        selector = {"scope": "GRILL", "pack_id": "GRILL-AUTH-1", "axis": "login"}
        context = {"authority_scope_refs": ["SURF-001"], "current_scope_refs": ["SURF-001"]}
        self.assertTrue(seed_matches_selector(make_seed(scope="GRILL", owner="SURF-001", pack_id="GRILL-AUTH-1", axis="login"), selector, context))
        self.assertFalse(seed_matches_selector(make_seed(scope="GRILL", owner="SURF-001", pack_id="OTHER", axis="login"), selector, context))


if __name__ == "__main__":
    unittest.main()
