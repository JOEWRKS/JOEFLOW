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

from approval_v2 import definition_digest  # noqa: E402
from authority_binding_v2 import sha256_json  # noqa: E402
from downstream_v2.authority import (  # noqa: E402
    DownstreamV2Error,
    canonical_state_sha256,
    require_closed_authority,
)
from tests.downstream_v2_support import closed_v2_state  # noqa: E402


class AuthorityTests(unittest.TestCase):
    def assert_not_closed(self, state):
        with self.assertRaises(DownstreamV2Error) as raised:
            require_closed_authority(state)
        self.assertEqual(raised.exception.code, "PRODUCT_DEFINITION_NOT_CLOSED")

    def test_closed_approved_state_yields_the_exact_authority_envelope(self):
        state = closed_v2_state()
        self.assertEqual(require_closed_authority(state), {
            "state_schema_version": "0.2.0",
            "product_slug": "semantic-closure-v2",
            "approved_revision": 1,
            "approved_definition_digest": "dd1a16a678b431fc971d65e61eef77b68edef26c33b8d5891f3f9b5f888d8876",
            "approved_manifest_digest": "dd1e837be6e1b79048905773b1563a2f8c07aa9f47bb7e1c0e5fc99b3e32b222",
            "product_binding_contract": state["project"]["closure_contract"]["product_binding_contract"],
            "ux_binding_contract": state["project"]["closure_contract"]["ux_binding_contract"],
            "snapshot_state_sha256": canonical_state_sha256(state),
        })

    def test_nonclosed_or_invalid_states_are_rejected(self):
        cases = {}
        open_state = closed_v2_state()
        open_state["project"]["definition_status"] = "OPEN"
        cases["open"] = open_state
        ready = closed_v2_state()
        ready["project"]["definition_status"] = "READY_FOR_REVIEW"
        cases["ready"] = ready
        stale = closed_v2_state()
        stale["approval"]["approved_revision"] = 2
        cases["stale"] = stale
        mutated = closed_v2_state()
        mutated["objects"]["requirements"][0]["statement"] = "A requester can submit a changed request."
        cases["semantic_mutation"] = mutated
        invalid = closed_v2_state()
        del invalid["project"]["slug"]
        cases["invalid"] = invalid
        for name, state in cases.items():
            with self.subTest(case=name):
                self.assert_not_closed(state)

    def test_snapshot_changes_for_unconsumed_evidence_without_changing_definition_identity(self):
        original = closed_v2_state()
        changed = copy.deepcopy(original)
        changed["evidence"].append({
            "id": "EVD-901", "status": "CURRENT", "source_kind": "USER_CONFIRMED_INTENT",
            "locator": "product-definition/unconsumed-observation", "claim": "A nonsemantic observation.",
            "confidence": "DIRECT", "authority_classes": ["INTENT"],
            "observed_version": None, "content_hash": None,
        })
        changed["discovery_baseline"]["evidence_commitment_digest"] = sha256_json(changed["evidence"])
        self.assertEqual(definition_digest(changed), definition_digest(original))
        self.assertEqual(require_closed_authority(changed)["approved_definition_digest"], require_closed_authority(original)["approved_definition_digest"])
        self.assertNotEqual(canonical_state_sha256(changed), canonical_state_sha256(original))

    def test_require_closed_authority_does_not_repair_or_rewrite_state(self):
        state = closed_v2_state()
        before = copy.deepcopy(state)
        require_closed_authority(state)
        self.assertEqual(state, before)
