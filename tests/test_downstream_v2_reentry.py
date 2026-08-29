import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from approval_v2 import definition_digest  # noqa: E402
from authority_binding_v2 import canonical_record_index, sha256_json  # noqa: E402
from downstream.schema_validation import validate_instance  # noqa: E402
from downstream_v2.authority import require_closed_authority  # noqa: E402
from downstream_v2.compiler import compile_handoff_definition  # noqa: E402
from downstream_v2.contracts import artifact_hash, semantic_contract_hash  # noqa: E402
from downstream_v2.derivation import load_responsibility_profile, seed_matches_selector  # noqa: E402
from downstream_v2.reentry import (  # noqa: E402
    audit_contract_against_state,
    build_reentry_events,
)
from downstream_v2.seeds import build_closed_source_seed_inventory  # noqa: E402
from tests.downstream_v2_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v2_compiler import complete_definition  # noqa: E402


EVENT_SCHEMA = json.loads(
    (PACKAGE_ROOT / "downstream_v2" / "schemas" / "reentry-event.schema.json").read_text(
        encoding="utf-8"
    )
)


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def event_hash(event):
    content = copy.deepcopy(event)
    content.pop("event_id")
    return hashlib.sha256(canonical_bytes(content)).hexdigest()[:24]


def gap(
    *,
    field_path="actions/submit-request/authentication",
    gap_type="AMBIGUITY_FOUND",
    authority_class="CONSTRAINT",
    reason="Authentication behavior has no approved deterministic meaning.",
    candidate_seed_refs=None,
    evidence_refs=None,
):
    return {
        "code": "SEMANTIC_AUTHORITY_GAP",
        "field_path": field_path,
        "reason": reason,
        "gap_type": gap_type,
        "required_expectation": "DETERMINISTIC_REQUIRED",
        "required_authority_class": authority_class,
        "authority_scope_refs": ["REQ-001", "SCR-001", "SURF-001"],
        "candidate_seed_refs": [] if candidate_seed_refs is None else candidate_seed_refs,
        "evidence_refs": [] if evidence_refs is None else evidence_refs,
    }


def rehash_contract(contract):
    contract["semantic_contract_hash"] = semantic_contract_hash(contract)
    contract["artifact_hash"] = artifact_hash(contract)


def make_in_progress(state, *, increment_revision=False):
    state["project"]["definition_status"] = "OPEN"
    if increment_revision:
        state["project"]["definition_revision"] += 1
    state["approval"] = {"status": "UNAPPROVED"}
    state["discovery_baseline"] = {"status": "STALE"}


def binding_cell(state, location):
    if location["scope"] == "CORE":
        row = next(row for row in state["coverage"] if row["feature_id"] == location["owner_ref"])
        return row["cells"][location["axis"]]
    if location["scope"] == "GRILL":
        row = next(
            row
            for row in state["grill_coverage"]
            if row["target_ref"] == location["owner_ref"]
            and row["pack_id"] == location["pack_id"]
        )
        return row["axes"][location["axis"]]
    row = next(row for row in state["ux_coverage"] if row["screen_id"] == location["owner_ref"])
    if location["scope"] == "UX_STATE":
        return row["states"][location["axis"]]
    action = next(action for action in row["actions"] if action["key"] == location["action_key"])
    return action["cells"][location["axis"]]


def replace_pointer_value(record, pointer):
    tokens = [token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/")]
    target = record
    for token in tokens[:-1]:
        target = target[int(token)] if isinstance(target, list) else target[token]
    final = tokens[-1]
    old = target[int(final)] if isinstance(target, list) else target[final]
    if isinstance(old, str):
        new = old + " changed"
    elif isinstance(old, bool):
        new = not old
    elif isinstance(old, list):
        new = [*old, "changed"]
    elif isinstance(old, dict):
        new = {**old, "changed": True}
    elif isinstance(old, int):
        new = old + 1
    else:
        new = {"changed_from": old}
    if isinstance(target, list):
        target[int(final)] = new
    else:
        target[final] = new
    return new


def drift_seed(state, seed):
    record = canonical_record_index(state)[seed["record_id"]][1]
    new_value = replace_pointer_value(record, seed["pointer"])
    cell = binding_cell(state, seed["location"])
    old_binding = {
        "record_id": seed["record_id"],
        "pointer": seed["pointer"],
        "value_sha256": seed["value_sha256"],
    }
    binding = next(binding for binding in cell["authority_bindings"] if binding == old_binding)
    binding["value_sha256"] = sha256_json(new_value)


class ReentryEventTests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.definition = complete_definition(self.state)
        self.source_authority = require_closed_authority(self.state)

    def build(self, one_gap):
        return build_reentry_events(
            source_authority=self.source_authority,
            definition=self.definition,
            gaps=[one_gap],
            source_contract_hash=None,
        )

    def assert_event_identity(self, event):
        validate_instance(event, EVENT_SCHEMA)
        self.assertRegex(event["event_id"], r"^REENTRY-[0-9a-f]{24}$")
        self.assertEqual(event["event_id"], "REENTRY-" + event_hash(event))

    def test_ambiguity_gap_builds_deterministic_affected_only_event(self):
        first = self.build(gap())
        second = self.build(gap())
        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        self.assertEqual(len(first), 1)
        event = first[0]
        self.assert_event_identity(event)
        self.assertEqual(event["event_type"], "AMBIGUITY_FOUND")
        self.assertEqual(event["affected_action_ids"], ["submit-request"])
        self.assertEqual(event["affected_lifecycle_ids"], [])
        self.assertEqual(event["halt_scope"], {
            "mode": "AFFECTED_ONLY",
            "action_ids": ["submit-request"],
            "lifecycle_ids": [],
        })
        self.assertNotIn("request-lifecycle", event["candidate_unknown"]["affected_ids"])

    def test_explicit_out_of_scope_gap_keeps_its_event_type(self):
        event = self.build(gap(
            gap_type="OUT_OF_SCOPE_REQUEST",
            field_path="lifecycles/request-lifecycle/reversal_window",
            reason="A reversal window is explicitly outside the approved scope.",
        ))[0]
        self.assert_event_identity(event)
        self.assertEqual(event["event_type"], "OUT_OF_SCOPE_REQUEST")
        self.assertEqual(event["affected_action_ids"], [])
        self.assertEqual(event["affected_lifecycle_ids"], ["request-lifecycle"])

    def test_mismatched_seed_gap_builds_contract_conflict(self):
        event = self.build(gap(
            gap_type="CONTRACT_CONFLICT",
            candidate_seed_refs=["SEED-does-not-match"],
            reason="The selected source seed is incompatible with this field.",
        ))[0]
        self.assert_event_identity(event)
        self.assertEqual(event["event_type"], "CONTRACT_CONFLICT")

    def test_candidate_unknown_is_only_a_proposal_and_inputs_are_not_mutated(self):
        source_before = canonical_bytes(self.source_authority)
        definition_before = canonical_bytes(self.definition)
        one_gap = gap(evidence_refs=["EVD-001"])
        gap_before = canonical_bytes(one_gap)
        event = self.build(one_gap)[0]
        self.assertEqual(canonical_bytes(self.source_authority), source_before)
        self.assertEqual(canonical_bytes(self.definition), definition_before)
        self.assertEqual(canonical_bytes(one_gap), gap_before)
        self.assertEqual(event["candidate_unknown"]["required_authority_class"], "CONSTRAINT")
        self.assertFalse(any(
            re.fullmatch(r"UNK-[0-9]+", value)
            for value in event["candidate_unknown"].values()
            if isinstance(value, str)
        ))
        self.assertNotIn("id", event["candidate_unknown"])

    def test_compiler_attaches_formal_events_without_materializing_a_contract(self):
        changed = copy.deepcopy(self.definition)
        changed["actions"][0]["fields"]["authentication"] = {
            "kind": "UNRESOLVED",
            "gap_type": "AMBIGUITY_FOUND",
            "description": "Authentication behavior is not authoritative.",
            "required_authority_class": "CONSTRAINT",
            "evidence_refs": ["EVD-001"],
        }
        state_before = canonical_bytes(self.state)
        result = compile_handoff_definition(self.state, changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertIsNone(result["contract"])
        self.assertEqual(len(result["reentry_events"]), 1)
        self.assertEqual(result["reentry_events"][0]["event_type"], "AMBIGUITY_FOUND")
        self.assertEqual(
            result["reentry_events"][0]["candidate_unknown"]["required_authority_class"],
            "CONSTRAINT",
        )
        self.assertEqual(canonical_bytes(self.state), state_before)

    def test_compiler_classifies_missing_meaning_and_seed_mismatch_differently(self):
        missing_meaning = copy.deepcopy(self.definition)
        missing_meaning["actions"][0]["fields"]["authentication"] = copy.deepcopy(
            complete_definition(self.state, review=True)["actions"][0]["fields"]["visible_success"]
        )
        ambiguity = compile_handoff_definition(self.state, missing_meaning)
        self.assertTrue(ambiguity["reentry_events"])
        self.assertTrue(all(
            event["event_type"] == "AMBIGUITY_FOUND"
            for event in ambiguity["reentry_events"]
        ))

        mismatched_seed = copy.deepcopy(self.definition)
        mismatched_seed["actions"][0]["fields"]["authentication"] = {
            "kind": "DIRECT_AUTHORITY",
            "source_seed_ref": "SEED-does-not-exist",
        }
        conflict = compile_handoff_definition(self.state, mismatched_seed)
        self.assertTrue(conflict["reentry_events"])
        self.assertTrue(all(
            event["event_type"] == "CONTRACT_CONFLICT"
            for event in conflict["reentry_events"]
        ))


class ContractDriftAuditTests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.definition = complete_definition(self.state)
        self.contract = compile_handoff_definition(self.state, self.definition)["contract"]

    def audit(self, state=None, contract=None):
        return audit_contract_against_state(
            self.contract if contract is None else contract,
            self.state if state is None else state,
        )

    def test_unchanged_closed_authority_is_conformant(self):
        result = self.audit()
        self.assertEqual(result, {
            "status": "CONFORMANT",
            "global_definition_closed": True,
            "authority_revision_relation": "SAME_APPROVED_REVISION",
            "reentry_events": [],
        })

    def test_unconsumed_evidence_and_rebuilt_baseline_change_only_snapshot_identity(self):
        changed = copy.deepcopy(self.state)
        changed["evidence"].append({
            "id": "EVD-901",
            "status": "CURRENT",
            "source_kind": "USER_CONFIRMED_INTENT",
            "locator": "product-definition/unconsumed-observation",
            "claim": "A nonsemantic observation.",
            "confidence": "DIRECT",
            "authority_classes": ["INTENT"],
            "observed_version": None,
            "content_hash": None,
        })
        changed["discovery_baseline"]["evidence_commitment_digest"] = sha256_json(changed["evidence"])
        self.assertEqual(definition_digest(changed), definition_digest(self.state))
        result = self.audit(changed)
        self.assertEqual(result["status"], "CONFORMANT")
        self.assertEqual(result["reentry_events"], [])
        self.assertNotEqual(
            self.contract["source_authority"]["snapshot_state_sha256"], sha256_json(changed)
        )
        self.assertEqual(self.contract["semantic_contract_hash"], semantic_contract_hash(self.contract))

    def test_stale_baseline_and_open_status_do_not_halt_exact_local_dependencies(self):
        changed = copy.deepcopy(self.state)
        make_in_progress(changed)
        result = self.audit(changed)
        self.assertEqual(result, {
            "status": "CONFORMANT",
            "global_definition_closed": False,
            "authority_revision_relation": "SAME_APPROVED_REVISION",
            "reentry_events": [],
        })

    def test_newer_unrelated_revision_and_digest_leave_old_contract_conformant(self):
        changed = copy.deepcopy(self.state)
        unrelated = copy.deepcopy(changed["objects"]["requirements"][0])
        unrelated["id"] = "REQ-902"
        unrelated["statement"] = "A future unrelated workflow may be considered."
        unrelated["status"] = "CURRENT"
        changed["objects"]["requirements"].append(unrelated)
        make_in_progress(changed, increment_revision=True)
        self.assertNotEqual(definition_digest(changed), definition_digest(self.state))
        result = self.audit(changed)
        self.assertEqual(result, {
            "status": "CONFORMANT",
            "global_definition_closed": False,
            "authority_revision_relation": "OLDER_APPROVED_REVISION_UNAFFECTED",
            "reentry_events": [],
        })

    def test_consumed_seed_value_change_requires_dependency_scoped_reentry(self):
        changed = copy.deepcopy(self.state)
        target = self.contract["source_seed_inventory"][0]
        consumers = {
            item["action_id"]
            for item in self.contract["actions"]
            if any(
                target["seed_key"] in field["source_seed_refs"]
                for field in item["fields"].values()
            )
        }
        drift_seed(changed, target)
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertTrue(result["reentry_events"])
        halted_actions = {
            action_id
            for event in result["reentry_events"]
            for action_id in event["halt_scope"]["action_ids"]
        }
        self.assertEqual(halted_actions, consumers)
        self.assertTrue(all(event["event_type"] == "CONTRACT_CONFLICT" for event in result["reentry_events"]))

    def test_one_actions_seed_drift_does_not_halt_an_unrelated_action(self):
        definition = copy.deepcopy(self.definition)
        seeds = build_closed_source_seed_inventory(self.state)
        profile = load_responsibility_profile()
        current_scope_refs = ["REQ-001", "SCR-001", "SURF-001"]
        first_context = {
            "authority_scope_refs": current_scope_refs,
            "current_scope_refs": current_scope_refs,
            "ux_action_locator": {"screen_ref": "SCR-001", "action_key": "submit"},
        }
        second = copy.deepcopy(definition["actions"][0])
        second["action_id"] = "unrelated-action"
        second["authority_scope_refs"] = ["REQ-001"]
        second["ux_action_locator"] = None
        second_context = {
            "authority_scope_refs": ["REQ-001"],
            "current_scope_refs": current_scope_refs,
        }
        candidates = [
            (field_name, seed)
            for field_name, policy in profile["action_fields"].items()
            for seed in seeds
            if any(
                seed_matches_selector(seed, selector, first_context)
                for selector in policy["allowed_seed_selectors"]
            )
        ]
        target_field = None
        target_seed = None
        second_fields = None
        for candidate_field, candidate in candidates:
            candidate_dependency = (candidate["record_id"], candidate["pointer"])
            proposed_fields = {}
            for field_name, policy in profile["action_fields"].items():
                alternatives = [
                    seed
                    for seed in seeds
                    if (seed["record_id"], seed["pointer"]) != candidate_dependency
                    and any(
                        seed_matches_selector(seed, selector, second_context)
                        for selector in policy["allowed_seed_selectors"]
                    )
                ]
                if not alternatives:
                    break
                proposed_fields[field_name] = {
                    "kind": "DIRECT_AUTHORITY",
                    "source_seed_ref": alternatives[0]["seed_key"],
                }
            if len(proposed_fields) == len(profile["action_fields"]):
                target_field = candidate_field
                target_seed = candidate
                second_fields = proposed_fields
                break
        if target_field is None or target_seed is None or second_fields is None:
            raise AssertionError("fixture requires one action-local source dependency")
        second["fields"] = second_fields
        definition["actions"][0]["fields"][target_field] = {
            "kind": "DIRECT_AUTHORITY",
            "source_seed_ref": target_seed["seed_key"],
        }
        definition["actions"].append(second)
        definition["actions"].sort(key=lambda action: action["action_id"])
        compiled = compile_handoff_definition(self.state, definition)
        self.assertIsNotNone(compiled["contract"], compiled)
        contract = compiled["contract"]
        target = next(
            seed for seed in contract["source_seed_inventory"]
            if seed["seed_key"] == target_seed["seed_key"]
        )
        changed = copy.deepcopy(self.state)
        drift_seed(changed, target)
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed, contract)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        halted = {
            action_id
            for event in result["reentry_events"]
            for action_id in event["halt_scope"]["action_ids"]
        }
        self.assertIn("submit-request", halted)
        self.assertNotIn("unrelated-action", halted)
        all_actions = {action["action_id"] for action in contract["actions"]}
        self.assertEqual(all_actions - halted, {"unrelated-action"})

    def test_scope_commitment_change_halts_only_its_declared_consumers(self):
        changed = copy.deepcopy(self.state)
        changed["surface_manifest"]["records"][0]["name"] += " revised"
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertTrue(any(
            "SURF-001" in event["affected_authority_ids"]
            for event in result["reentry_events"]
        ))
        self.assertTrue(all(
            event["halt_scope"]["mode"] == "AFFECTED_ONLY"
            for event in result["reentry_events"]
        ))

    def test_missing_or_stale_consumed_source_record_requires_reentry(self):
        seed = self.contract["source_seed_inventory"][0]
        for mutation in ("missing", "stale"):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(self.state)
                record_type, record = canonical_record_index(changed)[seed["record_id"]]
                if mutation == "stale":
                    record["status"] = "STALE"
                else:
                    for records in changed["objects"].values():
                        if isinstance(records, list):
                            records[:] = [item for item in records if item.get("id") != seed["record_id"]]
                    changed["evidence"][:] = [item for item in changed["evidence"] if item.get("id") != seed["record_id"]]
                    changed["contradictions"][:] = [item for item in changed["contradictions"] if item.get("id") != seed["record_id"]]
                    changed["surface_manifest"]["records"][:] = [
                        item
                        for item in changed["surface_manifest"]["records"]
                        if item.get("id") != seed["record_id"]
                    ]
                make_in_progress(changed, increment_revision=True)
                result = self.audit(changed)
                self.assertEqual(result["status"], "REENTRY_REQUIRED")
                self.assertTrue(result["reentry_events"])

    def test_forged_contract_authority_provenance_fails_closed_without_recompile(self):
        forged = copy.deepcopy(self.contract)
        forged["source_authority"]["approved_revision"] += 7
        forged["source_authority"]["approved_definition_digest"] = "0" * 64
        rehash_contract(forged)
        before = canonical_bytes(forged)
        result = self.audit(contract=forged)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertTrue(result["reentry_events"])
        self.assertEqual(canonical_bytes(forged), before)

    def test_malformed_contract_fails_closed_and_never_reports_conformant(self):
        malformed = copy.deepcopy(self.contract)
        malformed["semantic_contract_hash"] = "0" * 64
        result = self.audit(contract=malformed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertTrue(result["reentry_events"])

    def test_duplicate_state_ids_are_not_ready_and_emit_no_semantic_event(self):
        changed = copy.deepcopy(self.state)
        changed["objects"]["goals"].append(copy.deepcopy(changed["objects"]["goals"][0]))
        result = self.audit(changed)
        self.assertEqual(result["status"], "DEFINITION_NOT_READY")
        self.assertEqual(result["reentry_events"], [])

    def test_malformed_binding_structure_is_not_ready_and_emit_no_semantic_event(self):
        changed = copy.deepcopy(self.state)
        location = self.contract["source_seed_inventory"][0]["location"]
        binding_cell(changed, location)["authority_bindings"] = "malformed"
        result = self.audit(changed)
        self.assertEqual(result["status"], "DEFINITION_NOT_READY")
        self.assertEqual(result["reentry_events"], [])

    def test_audit_never_mutates_contract_or_state(self):
        contract_before = canonical_bytes(self.contract)
        state_before = canonical_bytes(self.state)
        self.audit()
        self.assertEqual(canonical_bytes(self.contract), contract_before)
        self.assertEqual(canonical_bytes(self.state), state_before)


if __name__ == "__main__":
    unittest.main()
