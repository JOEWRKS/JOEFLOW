import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from authority_binding_v2 import canonical_record_index, sha256_json  # noqa: E402
from downstream_v21.audit import audit_action_contract_v21_against_state  # noqa: E402
from downstream_v21.compiler import compile_handoff_definition_v21  # noqa: E402
from tests.downstream_v21_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v21_compiler import complete_definition_v21  # noqa: E402


def make_in_progress(state, *, increment_revision=False):
    state["project"]["definition_status"] = "OPEN"
    if increment_revision:
        state["project"]["definition_revision"] += 1
    state["approval"] = {"status": "UNAPPROVED"}
    state["discovery_baseline"] = {"status": "STALE"}


def binding_cell(state, location):
    if location["scope"] == "CORE":
        row = next(
            row
            for row in state["coverage"]
            if row["feature_id"] == location["owner_ref"]
        )
        return row["cells"][location["axis"]]
    if location["scope"] == "GRILL":
        row = next(
            row
            for row in state["grill_coverage"]
            if row["target_ref"] == location["owner_ref"]
            and row["pack_id"] == location["pack_id"]
        )
        return row["axes"][location["axis"]]
    row = next(
        row
        for row in state["ux_coverage"]
        if row["screen_id"] == location["owner_ref"]
    )
    if location["scope"] == "UX_STATE":
        return row["states"][location["axis"]]
    action = next(
        action
        for action in row["actions"]
        if action["key"] == location["action_key"]
    )
    return action["cells"][location["axis"]]


def replace_pointer_value(record, pointer):
    tokens = [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]
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
    binding = next(
        binding for binding in cell["authority_bindings"] if binding == old_binding
    )
    binding["value_sha256"] = sha256_json(new_value)


class DependencyScopedAuditTests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.definition = complete_definition_v21(self.state)
        self.contract = compile_handoff_definition_v21(
            self.state, self.definition
        )["contract"]

    def audit(self, state=None, contract=None):
        return audit_action_contract_v21_against_state(
            self.contract if contract is None else contract,
            self.state if state is None else state,
        )

    def test_unchanged_contract_is_conformant_with_exact_result_shape(self):
        self.assertEqual(
            self.audit(),
            {
                "status": "CONFORMANT",
                "authority_revision_relation": "SAME_APPROVED_REVISION",
                "affected_consumers": [],
                "semantic_gaps": [],
                "errors": [],
            },
        )

    def test_v21_audit_unrelated_newer_open_revision_remains_conformant(self):
        changed = copy.deepcopy(self.state)
        unrelated = copy.deepcopy(changed["objects"]["requirements"][0])
        unrelated["id"] = "REQ-902"
        unrelated["statement"] = "A future unrelated workflow may be considered."
        unrelated["status"] = "CURRENT"
        changed["objects"]["requirements"].append(unrelated)
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed)
        self.assertEqual(result["status"], "CONFORMANT")
        self.assertEqual(
            result["authority_revision_relation"],
            "OLDER_APPROVED_REVISION_UNAFFECTED",
        )
        self.assertEqual(result["affected_consumers"], [])
        self.assertEqual(result["semantic_gaps"], [])
        self.assertEqual(result["errors"], [])

    def test_v21_audit_used_field_seed_drift_requires_affected_reentry(self):
        target_ref = self.contract["actions"][0]["fields"]["delivery_effects"][
            "source_seed_refs"
        ][0]
        target = next(
            seed
            for seed in self.contract["source_seed_inventory"]
            if seed["seed_key"] == target_ref
        )
        changed = copy.deepcopy(self.state)
        drift_seed(changed, target)
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertEqual(
            [item["consumer_id"] for item in result["affected_consumers"]],
            ["submit-request"],
        )
        self.assertEqual(
            result["affected_consumers"][0]["dependency_paths"],
            ["actions/submit-request/delivery_effects"],
        )
        self.assertTrue(
            all(gap["code"] == "SEMANTIC_AUTHORITY_GAP" for gap in result["semantic_gaps"])
        )
        self.assertEqual(result["errors"], [])

    def test_v21_audit_verification_basis_seed_drift_requires_affected_reentry(self):
        target_ref = self.contract["actions"][0]["verification_basis"][
            "acceptance_basis_seed_refs"
        ][0]
        ordinary_refs = {
            ref
            for collection in (self.contract["actions"], self.contract["lifecycles"])
            for item in collection
            for field in item["fields"].values()
            for ref in field["source_seed_refs"]
        }
        self.assertNotIn(target_ref, ordinary_refs)
        target = next(
            seed
            for seed in self.contract["source_seed_inventory"]
            if seed["seed_key"] == target_ref
        )
        changed = copy.deepcopy(self.state)
        cell = binding_cell(changed, target["location"])
        binding = next(
            binding
            for binding in cell["authority_bindings"]
            if binding
            == {
                "record_id": target["record_id"],
                "pointer": target["pointer"],
                "value_sha256": target["value_sha256"],
            }
        )
        binding["value_sha256"] = "0" * 64
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertEqual(
            [item["consumer_id"] for item in result["affected_consumers"]],
            ["submit-request"],
        )
        self.assertEqual(
            result["affected_consumers"][0]["dependency_paths"],
            ["actions/submit-request/verification_basis/acceptance_basis_seed_refs"],
        )

    def test_v21_audit_scope_commitment_drift_requires_affected_reentry(self):
        changed = copy.deepcopy(self.state)
        changed["surface_manifest"]["records"][0]["name"] += " revised"
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertEqual(
            {(item["consumer_kind"], item["consumer_id"]) for item in result["affected_consumers"]},
            {("ACTION", "submit-request"), ("LIFECYCLE", "request-lifecycle")},
        )
        self.assertTrue(
            all(
                "authority_scope_refs" in item["dependency_paths"]
                for item in result["affected_consumers"]
            )
        )

    def test_v21_audit_unconsumed_evidence_change_does_not_stale_contract(self):
        changed = copy.deepcopy(self.state)
        changed["evidence"].append(
            {
                "id": "EVD-901",
                "status": "CURRENT",
                "source_kind": "USER_CONFIRMED_INTENT",
                "locator": "product-definition/unconsumed-observation",
                "claim": "A nonsemantic observation.",
                "confidence": "DIRECT",
                "authority_classes": ["INTENT"],
                "observed_version": None,
                "content_hash": None,
            }
        )
        make_in_progress(changed, increment_revision=True)
        result = self.audit(changed)
        self.assertEqual(result["status"], "CONFORMANT")
        self.assertEqual(result["affected_consumers"], [])
        self.assertEqual(result["semantic_gaps"], [])
        self.assertEqual(result["errors"], [])

    def test_v21_audit_duplicate_id_fails_closed_definition_not_ready(self):
        changed = copy.deepcopy(self.state)
        changed["objects"]["goals"].append(
            copy.deepcopy(changed["objects"]["goals"][0])
        )
        result = self.audit(changed)
        self.assertEqual(result["status"], "DEFINITION_NOT_READY")
        self.assertEqual(
            result["authority_revision_relation"], "NOT_APPLICABLE"
        )
        self.assertEqual(result["affected_consumers"], [])
        self.assertEqual(result["semantic_gaps"], [])
        self.assertTrue(result["errors"])

    def test_audit_is_read_only(self):
        contract_before = copy.deepcopy(self.contract)
        state_before = copy.deepcopy(self.state)
        self.audit()
        self.assertEqual(self.contract, contract_before)
        self.assertEqual(self.state, state_before)


if __name__ == "__main__":
    unittest.main()
