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

from downstream_v2.authority import DownstreamV2Error, require_closed_authority  # noqa: E402
from downstream_v2.semantic_debt import semantic_debt_report  # noqa: E402
from downstream_v21.compiler import compile_handoff_definition_v21  # noqa: E402
from downstream_v21.derivation import (  # noqa: E402
    ContractExpressivenessGap,
    SemanticAuthorityGap,
    classify_exact_collection_request,
)
from downstream_v21.gaps import (  # noqa: E402
    CONTRACT_EXPRESSIVENESS_GAP,
    RUNTIME_MAPPING_GAP,
    SEMANTIC_AUTHORITY_GAP,
    expressiveness_gap_record,
    route_compilation_gaps,
    semantic_gap_record,
)
from downstream_v21.responsibility import load_responsibility_profile_v21  # noqa: E402
from tests.downstream_v21_support import closed_v2_state  # noqa: E402
from tests.test_downstream_v21_compiler import complete_definition_v21  # noqa: E402


class GapRoutingTests(unittest.TestCase):
    def setUp(self):
        self.state = closed_v2_state()
        self.definition = complete_definition_v21(self.state)

    def compile(self, definition=None):
        return compile_handoff_definition_v21(
            self.state,
            self.definition if definition is None else definition,
        )

    def test_gap_taxonomy_codes_are_distinct(self):
        self.assertEqual(SEMANTIC_AUTHORITY_GAP, "SEMANTIC_AUTHORITY_GAP")
        self.assertEqual(
            CONTRACT_EXPRESSIVENESS_GAP, "CONTRACT_EXPRESSIVENESS_GAP"
        )
        self.assertEqual(RUNTIME_MAPPING_GAP, "RUNTIME_MAPPING_GAP")
        self.assertEqual(len({SEMANTIC_AUTHORITY_GAP, CONTRACT_EXPRESSIVENESS_GAP, RUNTIME_MAPPING_GAP}), 3)

    def test_explicit_unresolved_product_meaning_returns_reentry_required_and_affected_only_event(self):
        changed = copy.deepcopy(self.definition)
        changed["actions"][0]["fields"]["authentication"] = {
            "kind": "UNRESOLVED",
            "gap_type": "AMBIGUITY_FOUND",
            "description": "Authentication behavior is not authoritative.",
            "required_authority_class": "CONSTRAINT",
            "evidence_refs": ["EVD-001"],
        }
        result = self.compile(changed)
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertIsNone(result["contract"])
        self.assertEqual(len(result["semantic_gaps"]), 1)
        self.assertEqual(result["expressiveness_gaps"], [])
        self.assertEqual(result["semantic_gaps"][0]["code"], SEMANTIC_AUTHORITY_GAP)
        self.assertEqual(len(result["reentry_events"]), 1)
        event = result["reentry_events"][0]
        self.assertEqual(event["halt_scope"]["mode"], "AFFECTED_ONLY")
        self.assertEqual(event["halt_scope"]["action_ids"], ["submit-request"])
        self.assertEqual(event["halt_scope"]["lifecycle_ids"], [])

    def controlled_expressiveness_gap(self):
        policy = {
            "expectation": "DETERMINISTIC_REQUIRED",
            "required_authority_class": "INTENT",
            "collection_semantics": "CONJUNCTIVE_SET",
            "allowed_derivations": ["DIRECT_AUTHORITY", "extract", "select"],
        }
        refs = ["SEED-A", "SEED-B"]
        with self.assertRaises(ContractExpressivenessGap) as raised:
            classify_exact_collection_request(
                field_policy=policy,
                eligible_seed_refs=refs,
                requested_collection_semantics="CONJUNCTIVE_SET",
            )
        return expressiveness_gap_record(
            field_path="actions/submit-request/input_invariants",
            spec={
                "kind": "MACHINE_DERIVED",
                "operator": "collect_exact",
                "source_seed_refs": refs,
            },
            error=raised.exception,
            policy=policy,
            authority_scope_refs=["REQ-001", "SCR-001", "SURF-001"],
        )

    def test_expressiveness_gap_returns_contract_evolution_required_without_reentry_event(self):
        gap = self.controlled_expressiveness_gap()
        result = route_compilation_gaps(
            source_authority=require_closed_authority(self.state),
            definition=self.definition,
            semantic_debt=semantic_debt_report(derived_fields=[], gaps=[]),
            semantic_gaps=[],
            expressiveness_gaps=[gap],
        )
        self.assertEqual(result["status"], "CONTRACT_EVOLUTION_REQUIRED")
        self.assertIsNone(result["contract"])
        self.assertEqual(result["semantic_gaps"], [])
        self.assertEqual(result["expressiveness_gaps"], [gap])
        self.assertEqual(result["reentry_events"], [])
        self.assertEqual(gap["code"], CONTRACT_EXPRESSIVENESS_GAP)
        self.assertEqual(gap["candidate_seed_refs"], ["SEED-A", "SEED-B"])
        self.assertEqual(gap["required_semantic_form"], "CONJUNCTIVE_SET")

    def test_invalid_unknown_operator_fails_closed_not_expressiveness_gap(self):
        changed = copy.deepcopy(self.definition)
        changed["actions"][0]["fields"]["authentication"] = {
            "kind": "MACHINE_DERIVED",
            "operator": "compose",
            "source_seed_ref": "SEED-not-authority",
            "pointer": "/value",
        }
        with self.assertRaises(DownstreamV2Error) as raised:
            self.compile(changed)
        self.assertTrue(raised.exception.code.startswith("INVALID_"))

    def test_disallowed_collect_on_none_field_is_invalid_not_expressiveness_gap(self):
        changed = copy.deepcopy(self.definition)
        actor_ref = changed["actions"][0]["fields"]["actor"]["source_seed_ref"]
        changed["actions"][0]["fields"]["authentication"] = {
            "kind": "MACHINE_DERIVED",
            "operator": "collect_exact",
            "source_seed_refs": [actor_ref, "SEED-not-authority"],
        }
        with self.assertRaises(DownstreamV2Error) as raised:
            self.compile(changed)
        self.assertTrue(raised.exception.code.startswith("INVALID_"))

    def test_mixed_semantic_and_expressiveness_gaps_reports_both_and_reentry_wins(self):
        policy = load_responsibility_profile_v21()["action_fields"]["authentication"]
        unresolved = {
            "kind": "UNRESOLVED",
            "gap_type": "AMBIGUITY_FOUND",
            "description": "Authentication meaning is missing.",
            "required_authority_class": "INTENT",
            "evidence_refs": ["EVD-001"],
        }
        semantic_error = SemanticAuthorityGap(unresolved)
        semantic = semantic_gap_record(
            field_path="actions/submit-request/authentication",
            spec=unresolved,
            error=semantic_error,
            policy=policy,
            authority_scope_refs=["REQ-001", "SCR-001", "SURF-001"],
        )
        expressiveness = self.controlled_expressiveness_gap()
        debt = semantic_debt_report(derived_fields=[], gaps=[semantic])
        result = route_compilation_gaps(
            source_authority=require_closed_authority(self.state),
            definition=self.definition,
            semantic_debt=debt,
            semantic_gaps=[semantic],
            expressiveness_gaps=[expressiveness],
        )
        self.assertEqual(result["status"], "REENTRY_REQUIRED")
        self.assertEqual(result["semantic_gaps"], [semantic])
        self.assertEqual(result["expressiveness_gaps"], [expressiveness])
        self.assertEqual(len(result["reentry_events"]), 1)
        self.assertEqual(
            result["reentry_events"][0]["halt_scope"]["action_ids"],
            ["submit-request"],
        )


if __name__ == "__main__":
    unittest.main()
