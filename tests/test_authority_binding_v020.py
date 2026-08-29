import copy
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
CONTRACTS = ROOT / "skills" / "joewrks-product-definition" / "references" / "binding-contracts"
sys.path.insert(0, str(SCRIPTS))

from authority_binding_v2 import (  # noqa: E402
    BindingError,
    binding_contract_identity,
    canonical_json,
    canonical_record_index,
    load_binding_contracts,
    make_authority_binding,
    resolve_record_pointer,
    sha256_json,
    verify_authority_binding,
)
from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.v020_support import evidence_record, foundation_state, surface_record  # noqa: E402


PRODUCT_AXIS_TYPES = {
    "actor": {"USR", "DEC", "RULE"}, "goal": {"GOAL", "REQ"},
    "entry_point": {"FLOW", "SCR", "RULE"}, "precondition": {"RULE", "STATE", "FLOW"},
    "happy_path": {"FLOW", "REQ"}, "alternative_path": {"FLOW", "RULE"},
    "error": {"FLOW", "STATE", "RULE"}, "recovery": {"FLOW", "STATE", "RULE"},
    "permission": {"RULE", "DEC", "USR"}, "state": {"STATE", "RULE"},
    "data": {"DATA", "RULE"}, "side_effect": {"RULE", "DATA", "INT"},
    "notification": {"RULE", "FLOW", "INT"}, "validation": {"RULE", "DATA", "AC"},
    "boundary": {"RULE", "DEC"}, "persistence": {"DATA", "RULE"},
    "security": {"RULE", "DEC"}, "privacy": {"RULE", "DEC", "DATA"},
    "analytics": {"RULE", "DATA", "INT"}, "acceptance": {"AC"},
}
SPECIALIST_TYPES = {
    "GRILL-AUTH-1": {"USR", "DEC", "RULE", "FLOW", "STATE", "DATA", "AC"},
    "GRILL-MONEY-1": {"DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"},
    "GRILL-FILE-UPLOAD-1": {"DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"},
    "GRILL-ASYNC-1": {"DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"},
    "GRILL-PERMISSION-1": {"USR", "DEC", "RULE", "FLOW", "STATE", "DATA", "AC"},
    "GRILL-DESTRUCTIVE-ACTION-1": {"DEC", "RULE", "FLOW", "STATE", "DATA", "INT", "AC"},
}
SEMANTIC_ROOTS = {
    "GOAL": {"statement"}, "USR": {"description", "actor_kind"},
    "REQ": {"statement", "scope", "ui_required"},
    "DEC": {"statement", "accepted_recommendation"}, "RULE": {"statement"},
    "FLOW": {"entry", "preconditions", "paths", "outcomes"},
    "SCR": {"purpose", "interaction_mode", "major_actions"},
    "STATE": {"state_name", "conditions"}, "DATA": {"name", "purpose", "ownership"},
    "INT": {"name", "purpose"}, "AC": {"assertion"},
}
UX_STATE_TYPES = {
    "default": {"SCR", "STATE", "FLOW", "RULE"}, "loading": {"STATE", "FLOW"},
    "empty": {"STATE", "FLOW", "RULE"}, "partial": {"STATE", "FLOW", "RULE"},
    "success": {"STATE", "FLOW", "AC"}, "error": {"STATE", "FLOW", "RULE", "AC"},
    "disabled": {"STATE", "RULE"}, "permission_denied": {"STATE", "RULE", "DEC", "USR"},
    "unauthenticated": {"STATE", "RULE", "FLOW"}, "offline": {"STATE", "FLOW", "RULE"},
    "timeout": {"STATE", "FLOW", "RULE"}, "retrying": {"STATE", "FLOW", "RULE"},
    "submitting": {"STATE", "FLOW"}, "completed": {"STATE", "FLOW", "AC"},
    "cancelled": {"STATE", "FLOW", "RULE"}, "expired": {"STATE", "RULE", "FLOW"},
}
UX_ACTION_TYPES = {
    "entry": {"FLOW", "SCR", "RULE"}, "precondition": {"RULE", "STATE", "FLOW"},
    "input": {"DATA", "SCR", "RULE"}, "validation": {"RULE", "DATA", "AC"},
    "submit": {"FLOW", "SCR", "RULE"}, "success": {"FLOW", "STATE", "AC"},
    "failure": {"FLOW", "STATE", "RULE", "AC"}, "retry": {"FLOW", "STATE", "RULE"},
    "cancel": {"FLOW", "STATE", "RULE"}, "back": {"FLOW", "SCR", "RULE"},
    "refresh": {"FLOW", "STATE", "RULE"}, "duplicate_concurrent_action": {"RULE", "STATE", "FLOW"},
    "timeout": {"FLOW", "STATE", "RULE"}, "offline": {"STATE", "FLOW", "RULE"},
    "permission": {"RULE", "DEC", "USR"}, "session_expiration": {"STATE", "RULE", "FLOW"},
    "data_mutation": {"DATA", "RULE", "FLOW"}, "side_effect": {"RULE", "DATA", "INT"},
    "notification": {"RULE", "FLOW", "INT"}, "persistence": {"DATA", "RULE"},
    "undo": {"FLOW", "STATE", "RULE"}, "destructive_confirmation": {"RULE", "DEC", "FLOW"},
}


class AuthorityBindingTest(unittest.TestCase):
    def state_with_rule(self):
        state = foundation_state()
        state["objects"]["rules"] = [{
            "id": "RULE-014", "status": "CURRENT", "statement": "Use / and ~ exactly.",
            "applies_to": [], "nested/key": {"~value": ["zero", "one"]},
        }]
        return state

    def assert_binding_error(self, code, callback):
        with self.assertRaises(BindingError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def test_canonical_json_and_hashes_are_literal_and_stable(self):
        # Break caught: a serializer changing spacing, sort order, UTF-8, or hash convention.
        values = {
            "string": ("한글/~", '"한글/~"', "8a0b1cb9322eed1a0f56bfe3ab2345e67676342873f647c867fbed6fd0584ec5"),
            "object": ({"z": 1, "a": "x"}, '{"a":"x","z":1}', "8d6a75ac86d8b51bb56acfbb96108ed81474aa3504c317f77c0c576bde387cd3"),
            "list": ([True, 0, None], '[true,0,null]', "3885b962d2639287de7b22661d662a1447b7097d1ed3cc934f8c49543f589128"),
        }
        for _, (value, expected_json, expected_hash) in values.items():
            self.assertEqual(canonical_json(value), expected_json)
            self.assertEqual(sha256_json(value), expected_hash)
            self.assertEqual(expected_hash, hashlib.sha256(expected_json.encode("utf-8")).hexdigest())

    def test_pointer_decodes_rfc6901_escapes_and_traverses_lists(self):
        # Break caught: record-relative pointer resolution that mishandles escaped keys or arrays.
        record = {"a/b": {"til~de": ["first", {"value": 0}]}}
        self.assertEqual(resolve_record_pointer(record, "/a~1b/til~0de/1/value"), 0)

    def test_invalid_pointers_are_rejected(self):
        # Break caught: malformed or unresolved paths silently binding another value.
        for pointer in ("missing-slash", "/missing", "/items/01", "/items/-", "/items/nope"):
            with self.subTest(pointer=pointer):
                self.assert_binding_error(
                    "invalid_record_pointer",
                    lambda pointer=pointer: resolve_record_pointer({"items": ["only"]}, pointer),
                )

    def test_non_ascii_array_index_tokens_are_structured_invalid_pointers(self):
        # Break caught: Unicode digit tokens resolving as array indexes or escaping as bare ValueError.
        for pointer in ("/items/١", "/items/²"):
            with self.subTest(pointer=pointer):
                self.assert_binding_error(
                    "invalid_record_pointer",
                    lambda pointer=pointer: resolve_record_pointer({"items": ["zero", "one"]}, pointer),
                )

    def test_record_index_uses_only_canonical_stable_record_collections(self):
        # Break caught: bindings resolving array positions or arbitrary document fragments as authority.
        state = self.state_with_rule()
        state["evidence"] = [evidence_record("EVD-001")]
        state["surface_manifest"]["records"] = [surface_record("SURF-001")]
        state["contradictions"] = [{"id": "CON-001"}]
        index = canonical_record_index(state)
        self.assertEqual(set(index), {"RULE-014", "EVD-001", "SURF-001", "CON-001"})
        self.assertEqual(index["RULE-014"][0], "RULE")
        self.assertEqual(index["EVD-001"][0], "EVD")

    def test_make_binding_is_exact_record_relative_hash(self):
        # Break caught: helper emitting an array path, record hash, or noncanonical hash.
        state = self.state_with_rule()
        self.assertEqual(make_authority_binding(state, "RULE-014", "/statement"), {
            "record_id": "RULE-014", "pointer": "/statement",
            "value_sha256": "0f0d2db91f976cd546ddae3f1161bd95a4643e023a61507a0adc996a073cf0b1",
        })

    def test_semantic_verification_rejects_empty_pointer_hash_drift_status_and_wrong_type(self):
        # Break caught: a positive proof being a whole-record/control-field hash or stale/wrong authority.
        state = self.state_with_rule()
        binding = make_authority_binding(state, "RULE-014", "/statement")
        self.assertEqual(
            verify_authority_binding(state, binding, allowed_types={"RULE"}, semantic_roots=SEMANTIC_ROOTS),
            ("RULE", state["objects"]["rules"][0]),
        )
        self.assert_binding_error("empty_authority_binding_pointer", lambda: verify_authority_binding(
            state, make_authority_binding(state, "RULE-014", ""), allowed_types={"RULE"}, semantic_roots=SEMANTIC_ROOTS,
        ))
        drift = dict(binding, value_sha256="0" * 64)
        self.assert_binding_error("authority_binding_hash_mismatch", lambda: verify_authority_binding(
            state, drift, allowed_types={"RULE"}, semantic_roots=SEMANTIC_ROOTS,
        ))
        status = make_authority_binding(state, "RULE-014", "/status")
        self.assert_binding_error("nonsemantic_authority_binding_pointer", lambda: verify_authority_binding(
            state, status, allowed_types={"RULE"}, semantic_roots=SEMANTIC_ROOTS,
        ))
        self.assert_binding_error("invalid_authority_binding_type", lambda: verify_authority_binding(
            state, binding, allowed_types={"DATA"}, semantic_roots=SEMANTIC_ROOTS,
        ))
        state["objects"]["rules"][0]["status"] = "STALE"
        self.assert_binding_error("stale_authority_binding", lambda: verify_authority_binding(
            state, binding, allowed_types={"RULE"}, semantic_roots=SEMANTIC_ROOTS,
        ))

    def test_positive_bindings_reject_empty_values_but_preserve_false_and_zero(self):
        # Break caught: hashes allowing empty semantic claims or rejecting meaningful false/zero values.
        state = foundation_state()
        state["objects"]["requirements"] = [{
            "id": "REQ-001", "status": "CURRENT", "statement": "Meaningful", "scope": "CORE",
            "ui_required": False, "materiality": {},
        }]
        for pointer in ("/statement", "/scope"):
            state["objects"]["requirements"][0][pointer[1:]] = " " if pointer == "/statement" else []
            binding = make_authority_binding(state, "REQ-001", pointer)
            self.assert_binding_error("empty_authority_binding_value", lambda binding=binding: verify_authority_binding(
                state, binding, allowed_types={"REQ"}, semantic_roots=SEMANTIC_ROOTS,
            ))
        state["objects"]["requirements"][0]["ui_required"] = False
        false_binding = make_authority_binding(state, "REQ-001", "/ui_required")
        verify_authority_binding(state, false_binding, allowed_types={"REQ"}, semantic_roots=SEMANTIC_ROOTS)
        state["objects"]["requirements"][0]["ui_required"] = 0
        zero_binding = make_authority_binding(state, "REQ-001", "/ui_required")
        verify_authority_binding(state, zero_binding, allowed_types={"REQ"}, semantic_roots=SEMANTIC_ROOTS)

    def test_basis_accepts_scoped_surface_status_and_only_eligible_evidence(self):
        # Break caught: N/A basis accepting control-free candidate evidence or arbitrary/non-current surfaces.
        state = foundation_state()
        state["surface_manifest"]["records"] = [surface_record("SURF-001", status="OUT_OF_SCOPE")]
        surface_binding = make_authority_binding(state, "SURF-001", "/status")
        verify_authority_binding(
            state, surface_binding, allowed_types={"SURF"}, semantic_roots={"SURF": {"status"}}, basis=True,
        )
        for source_kind in ("INFERRED_INTENT", "DESIGN_ARTIFACT"):
            state["evidence"] = [evidence_record("EVD-001", source_kind=source_kind, authority_classes=["INTENT"])]
            binding = make_authority_binding(state, "EVD-001", "/claim")
            self.assert_binding_error("ineligible_basis_authority", lambda binding=binding: verify_authority_binding(
                state, binding, allowed_types={"EVD"}, semantic_roots={"EVD": {"claim"}}, basis=True,
            ))
        state["evidence"] = [evidence_record("EVD-001", source_kind="USER_CONFIRMED_INTENT", authority_classes=["INTENT"])]
        binding = make_authority_binding(state, "EVD-001", "/claim")
        verify_authority_binding(state, binding, allowed_types={"EVD"}, semantic_roots={"EVD": {"claim"}}, basis=True)

    def test_nan_is_not_canonical_json(self):
        # Break caught: platform-specific NaN JSON tokens becoming portable authority hashes.
        with self.assertRaises(ValueError):
            canonical_json(math.nan)


class BindingContractTest(unittest.TestCase):
    def test_state_requires_the_exact_frozen_contract_identities(self):
        # Break caught: a state silently claiming semantic closure under a changed or absent binding policy.
        state = foundation_state()
        state["project"]["closure_contract"] = {
            "level": "SEMANTIC_CLOSURE",
            "product_binding_contract": {
                "contract_id": "joewrks.product-coverage-binding", "version": "1.0",
                "digest": "b57459533247de52038aacb158e785c2184edcdd2fa6831f0edc3db713775f3c",
            },
            "ux_binding_contract": {
                "contract_id": "joewrks.ux-coverage-binding", "version": "1.0",
                "digest": "8fc84057a4a6f0f0ce329a58d11b8e208989800147d703665cea52088de0be0d",
            },
        }
        self.assertEqual(validate_state_v2(state), [])
        for path, value in (
            (("product_binding_contract", "contract_id"), "joewrks.changed"),
            (("ux_binding_contract", "version"), "2.0"),
            (("product_binding_contract", "digest"), "0" * 64),
        ):
            candidate = copy.deepcopy(state)
            candidate["project"]["closure_contract"][path[0]][path[1]] = value
            self.assertIn("binding_contract_identity_mismatch", {
                error["code"] for error in validate_state_v2(candidate)
            })

    def test_contract_files_are_exact_frozen_authorities_with_canonical_digests(self):
        # Break caught: contract inventory/root/type drift changing the meaning of later coverage claims.
        self.assertEqual({path.name for path in CONTRACTS.glob("*.json")}, {
            "binding-contract.schema.json", "product-coverage-binding-v1.json", "ux-coverage-binding-v1.json",
        })
        contracts = load_binding_contracts()
        self.assertEqual(set(contracts), {"product", "ux"})
        product, ux = contracts["product"], contracts["ux"]
        self.assertEqual((product["contract_id"], product["version"]), ("joewrks.product-coverage-binding", "1.0"))
        self.assertEqual((ux["contract_id"], ux["version"]), ("joewrks.ux-coverage-binding", "1.0"))
        self.assertEqual({name: set(types) for name, types in product["core_axis_types"].items()}, PRODUCT_AXIS_TYPES)
        self.assertEqual({name: set(types) for name, types in product["specialist_pack_types"].items()}, SPECIALIST_TYPES)
        self.assertEqual({name: set(roots) for name, roots in product["semantic_roots"].items()}, SEMANTIC_ROOTS)
        self.assertEqual({name: set(types) for name, types in ux["state_axis_types"].items()}, UX_STATE_TYPES)
        self.assertEqual({name: set(types) for name, types in ux["action_axis_types"].items()}, UX_ACTION_TYPES)
        self.assertEqual({name: set(roots) for name, roots in ux["semantic_roots"].items()}, SEMANTIC_ROOTS)
        identities = binding_contract_identity()
        self.assertEqual(set(identities), {"product", "ux"})
        for key, contract in contracts.items():
            self.assertEqual(identities[key], {
                "contract_id": contract["contract_id"], "version": contract["version"],
                "digest": hashlib.sha256(canonical_json(contract).encode("utf-8")).hexdigest(),
            })

    def test_cli_is_read_only_and_reports_structured_invalid_binding_errors(self):
        # Break caught: helper mutating state or hiding an invalid record/pointer behind a traceback.
        state = foundation_state()
        state["objects"]["rules"] = [{"id": "RULE-001", "status": "CURRENT", "statement": "Keep", "applies_to": []}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            original = json.dumps(state, sort_keys=True)
            path.write_text(original, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPTS / "authority_binding_value.py"), str(path), "RULE-001", "/statement"], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), make_authority_binding(state, "RULE-001", "/statement"))
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            invalid = subprocess.run([sys.executable, str(SCRIPTS / "authority_binding_value.py"), str(path), "NOPE-001", "/statement"], capture_output=True, text=True, check=False)
            self.assertEqual(invalid.returncode, 1)
            self.assertEqual(json.loads(invalid.stdout)["code"], "unknown_authority_record")


if __name__ == "__main__":
    unittest.main()
