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

from downstream_v21.derivation import (  # noqa: E402
    ContractExpressivenessGap,
    SemanticAuthorityGap,
    classify_exact_collection_request,
    derive_semantic_field_v21,
)
from downstream_v21.responsibility import (  # noqa: E402
    load_responsibility_profile_v21,
    responsibility_profile_digest_v21,
)
from tests.downstream_v21_support import (  # noqa: E402
    derivation_context_v21,
    make_seed_v21,
)


REMOVED_ACTION_FIELDS = {"default_result", "result_expectations", "test_obligations"}
COLLECTION_SEMANTICS = {
    ("action_fields", "actor"): "MEMBERSHIP_SET",
    ("action_fields", "input_invariants"): "CONJUNCTIVE_SET",
    ("lifecycle_fields", "authority"): "MEMBERSHIP_SET",
}


def expected_allowed_derivations(expectation, collection_semantics):
    if collection_semantics != "NONE":
        values = ["DIRECT_AUTHORITY"]
        if expectation == "DETERMINISTIC_REQUIRED":
            values.extend(["extract", "select"])
        values.append("collect_exact")
        return values
    if expectation == "DIRECT_REQUIRED":
        return ["DIRECT_AUTHORITY"]
    if expectation == "DETERMINISTIC_REQUIRED":
        return ["DIRECT_AUTHORITY", "extract", "select"]
    if expectation == "REVIEW_PERMITTED":
        return ["DIRECT_AUTHORITY", "extract", "select", "REVIEW_REQUIRED"]
    raise AssertionError(f"unexpected frozen expectation: {expectation}")


def expected_profile_projection():
    path = (
        PACKAGE_ROOT
        / "downstream_v2"
        / "references"
        / "field-responsibility-v1.json"
    )
    frozen = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "profile_id": "joewrks.downstream-responsibility/2.0",
        "action_fields": {},
        "lifecycle_fields": {},
    }
    for group_name in ("action_fields", "lifecycle_fields"):
        for field_name, frozen_entry in frozen[group_name].items():
            if group_name == "action_fields" and field_name in REMOVED_ACTION_FIELDS:
                continue
            collection = COLLECTION_SEMANTICS.get((group_name, field_name), "NONE")
            expected[group_name][field_name] = {
                "expectation": frozen_entry["expectation"],
                "required_authority_class": frozen_entry["required_authority_class"],
                "allowed_seed_selectors": frozen_entry["allowed_seed_selectors"],
                "allowed_derivations": expected_allowed_derivations(
                    frozen_entry["expectation"], collection,
                ),
                "collection_semantics": collection,
            }
    return expected


class ResponsibilityProfileTests(unittest.TestCase):
    def test_profile_is_exact_frozen_projection_with_only_three_fields_removed(self):
        profile = load_responsibility_profile_v21()
        self.assertEqual(profile, expected_profile_projection())
        self.assertEqual(
            set(profile["action_fields"]),
            set(expected_profile_projection()["action_fields"]),
        )
        self.assertTrue(REMOVED_ACTION_FIELDS.isdisjoint(profile["action_fields"]))

    def test_profile_collection_allowlist_and_derivation_vocabulary_are_exact(self):
        profile = load_responsibility_profile_v21()
        actual_collection = {
            (group_name, field_name): entry["collection_semantics"]
            for group_name in ("action_fields", "lifecycle_fields")
            for field_name, entry in profile[group_name].items()
            if entry["collection_semantics"] != "NONE"
        }
        self.assertEqual(actual_collection, COLLECTION_SEMANTICS)
        self.assertEqual(
            profile["action_fields"]["actor"]["allowed_derivations"],
            ["DIRECT_AUTHORITY", "collect_exact"],
        )
        self.assertEqual(
            profile["action_fields"]["input_invariants"]["allowed_derivations"],
            ["DIRECT_AUTHORITY", "extract", "select", "collect_exact"],
        )
        self.assertEqual(
            profile["lifecycle_fields"]["authority"]["allowed_derivations"],
            ["DIRECT_AUTHORITY", "collect_exact"],
        )

    def test_profile_digest_is_canonical_and_caller_profile_drift_is_rejected(self):
        profile = load_responsibility_profile_v21()
        canonical = json.dumps(
            profile,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(
            responsibility_profile_digest_v21(),
            hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )
        seed = make_seed_v21()
        direct = {"kind": "DIRECT_AUTHORITY", "source_seed_ref": seed["seed_key"]}
        for mutation in ("extra", "missing"):
            with self.subTest(mutation=mutation):
                drifted = copy.deepcopy(profile)
                if mutation == "extra":
                    drifted["action_fields"]["actor"]["unexpected"] = True
                else:
                    del drifted["action_fields"]["actor"]
                with self.assertRaisesRegex(ValueError, "RESPONSIBILITY_PROFILE_DRIFT"):
                    derive_semantic_field_v21(
                        direct,
                        field_name="actor",
                        field_kind="ACTION",
                        context=derivation_context_v21("REQ-001"),
                        seeds={seed["seed_key"]: seed},
                        profile=drifted,
                    )


class DerivationTests(unittest.TestCase):
    def setUp(self):
        self.profile = load_responsibility_profile_v21()
        self.context = derivation_context_v21("REQ-001", "SCR-001")

    def derive(self, spec, *, field="actor", kind="ACTION", seeds=None, context=None):
        seeds = [make_seed_v21(axis="actor")] if seeds is None else seeds
        return derive_semantic_field_v21(
            spec,
            field_name=field,
            field_kind=kind,
            context=self.context if context is None else context,
            seeds={seed["seed_key"]: seed for seed in seeds},
            profile=self.profile,
        )

    def test_collect_exact_actor_two_sources_returns_lexically_aligned_exact_values(self):
        first = make_seed_v21("SEED-B", value={"actor": ["second"]})
        second = make_seed_v21("SEED-A", value={"actor": ["first"]})
        spec = {
            "kind": "MACHINE_DERIVED",
            "operator": "collect_exact",
            "source_seed_refs": ["SEED-B", "SEED-A"],
        }
        result = self.derive(spec, seeds=[first, second])
        self.assertEqual(
            result,
            {
                "value": [{"actor": ["first"]}, {"actor": ["second"]}],
                "source_seed_refs": ["SEED-A", "SEED-B"],
                "derivation": {
                    "kind": "MACHINE_DERIVED",
                    "operator": "collect_exact",
                    "source_seed_refs": ["SEED-A", "SEED-B"],
                },
            },
        )
        second["value"]["actor"].append("mutated-after-derive")
        self.assertEqual(result["value"][0], {"actor": ["first"]})

    def test_single_actor_remains_direct_authority(self):
        seed = make_seed_v21(value="one actor")
        result = self.derive(
            {"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"},
            seeds=[seed],
        )
        self.assertEqual(
            result,
            {
                "value": "one actor",
                "source_seed_refs": ["SEED-001"],
                "derivation": {
                    "kind": "DIRECT_AUTHORITY",
                    "source_seed_ref": "SEED-001",
                },
            },
        )

    def test_collect_exact_rejects_duplicate_refs(self):
        with self.assertRaisesRegex(ValueError, "INVALID_COLLECT_EXACT_SPEC"):
            self.derive(
                {
                    "kind": "MACHINE_DERIVED",
                    "operator": "collect_exact",
                    "source_seed_refs": ["SEED-001", "SEED-001"],
                },
            )

    def test_collect_exact_rejects_unknown_or_stale_source(self):
        valid = make_seed_v21("SEED-A")
        unknown = {
            "kind": "MACHINE_DERIVED",
            "operator": "collect_exact",
            "source_seed_refs": ["SEED-A", "SEED-UNKNOWN"],
        }
        with self.assertRaisesRegex(ValueError, "UNKNOWN_SOURCE_SEED"):
            self.derive(unknown, seeds=[valid])

        stale = make_seed_v21("SEED-STALE", owner_ref="REQ-STALE")
        stale_spec = {
            "kind": "MACHINE_DERIVED",
            "operator": "collect_exact",
            "source_seed_refs": ["SEED-A", "SEED-STALE"],
        }
        with self.assertRaisesRegex(ValueError, "SOURCE_SEED_NOT_PERMITTED"):
            self.derive(stale_spec, seeds=[valid, stale])

    def test_collect_exact_rejects_selector_mismatch(self):
        actor = make_seed_v21("SEED-A", axis="actor")
        wrong = make_seed_v21("SEED-B", axis="permission")
        with self.assertRaisesRegex(ValueError, "SOURCE_SEED_NOT_PERMITTED"):
            self.derive(
                {
                    "kind": "MACHINE_DERIVED",
                    "operator": "collect_exact",
                    "source_seed_refs": ["SEED-A", "SEED-B"],
                },
                seeds=[actor, wrong],
            )

    def test_collect_exact_rejects_field_with_collection_semantics_none(self):
        seeds = [
            make_seed_v21("SEED-A", axis="permission"),
            make_seed_v21("SEED-B", axis="permission"),
        ]
        with self.assertRaisesRegex(ValueError, "DERIVATION_NOT_PERMITTED"):
            self.derive(
                {
                    "kind": "MACHINE_DERIVED",
                    "operator": "collect_exact",
                    "source_seed_refs": ["SEED-A", "SEED-B"],
                },
                field="authentication",
                seeds=seeds,
            )

    def test_malformed_disallowed_specs_remain_invalid_not_permission_failures(self):
        permission = make_seed_v21(axis="permission")
        malformed_collect = {
            "kind": "MACHINE_DERIVED",
            "operator": "collect_exact",
            "source_seed_refs": ["SEED-001"],
        }
        with self.assertRaisesRegex(ValueError, "INVALID_COLLECT_EXACT_SPEC"):
            self.derive(
                malformed_collect,
                field="authentication",
                seeds=[permission],
            )
        malformed_review = {
            "kind": "REVIEW_REQUIRED",
            "source_seed_refs": [],
        }
        with self.assertRaisesRegex(ValueError, "INVALID_REVIEW_SPEC"):
            self.derive(
                malformed_review,
                field="authentication",
                seeds=[permission],
            )

    def test_collect_exact_does_not_deduplicate_equal_values_from_distinct_refs(self):
        equal = {"same": [1, 2]}
        seeds = [
            make_seed_v21("SEED-A", value=equal),
            make_seed_v21("SEED-B", value=equal),
        ]
        result = self.derive(
            {
                "kind": "MACHINE_DERIVED",
                "operator": "collect_exact",
                "source_seed_refs": ["SEED-A", "SEED-B"],
            },
            seeds=seeds,
        )
        self.assertEqual(result["value"], [equal, equal])
        self.assertEqual(result["source_seed_refs"], ["SEED-A", "SEED-B"])
        self.assertIsNot(result["value"][0], result["value"][1])

    def test_collect_exact_adds_no_labels_or_caller_literals(self):
        values = ["reader", {"role": "editor"}]
        seeds = [
            make_seed_v21("SEED-A", value=values[0]),
            make_seed_v21("SEED-B", value=values[1]),
        ]
        result = self.derive(
            {
                "kind": "MACHINE_DERIVED",
                "operator": "collect_exact",
                "source_seed_refs": ["SEED-A", "SEED-B"],
            },
            seeds=seeds,
        )
        self.assertEqual(result["value"], values)
        self.assertEqual(set(result), {"value", "source_seed_refs", "derivation"})

    def test_input_invariants_collect_exact_is_conjunctive_and_lifecycle_authority_is_membership(self):
        invariant_seeds = [
            make_seed_v21("SEED-A", axis="validation", value="must be present"),
            make_seed_v21("SEED-B", axis="data", value={"max": 5}),
        ]
        collect = {
            "kind": "MACHINE_DERIVED",
            "operator": "collect_exact",
            "source_seed_refs": ["SEED-B", "SEED-A"],
        }
        self.assertEqual(
            self.derive(collect, field="input_invariants", seeds=invariant_seeds)["value"],
            ["must be present", {"max": 5}],
        )
        authority_seeds = [
            make_seed_v21("SEED-A", axis="actor", value="owner"),
            make_seed_v21("SEED-B", axis="permission", value="admin"),
        ]
        self.assertEqual(
            self.derive(
                collect,
                field="authority",
                kind="LIFECYCLE",
                seeds=authority_seeds,
            )["value"],
            ["owner", "admin"],
        )

    def test_direct_extract_select_and_review_preserve_frozen_v2_behavior(self):
        direct_seed = make_seed_v21(axis="actor", value={"nested": ["한글"]})
        direct = self.derive(
            {"kind": "DIRECT_AUTHORITY", "source_seed_ref": "SEED-001"},
            seeds=[direct_seed],
        )
        self.assertEqual(direct["value"], {"nested": ["한글"]})

        machine_seed = make_seed_v21(
            axis="permission",
            value={"a/b": {"~key": "selected"}, "a": 1, "b": {"v": 2}},
        )
        extracted = self.derive(
            {
                "kind": "MACHINE_DERIVED",
                "operator": "extract",
                "source_seed_ref": "SEED-001",
                "pointer": "/a~1b/~0key",
            },
            field="authentication",
            seeds=[machine_seed],
        )
        self.assertEqual(extracted["value"], "selected")
        selected = self.derive(
            {
                "kind": "MACHINE_DERIVED",
                "operator": "select",
                "source_seed_ref": "SEED-001",
                "keys": ["a", "b"],
            },
            field="authentication",
            seeds=[machine_seed],
        )
        self.assertEqual(selected["value"], {"a": 1, "b": {"v": 2}})

        review_spec = {
            "kind": "REVIEW_REQUIRED",
            "source_seed_refs": ["SEED-001"],
            "proposed_value": "reviewed wording",
            "why_structuring_is_insufficient": "A human interpretation is required.",
            "interpretation_scope": "Visible success wording.",
        }
        review_seed = make_seed_v21(
            scope="UX_STATE",
            owner_ref="SCR-001",
            axis="success",
            value="approved source wording",
        )
        reviewed = self.derive(
            review_spec,
            field="visible_success",
            seeds=[review_seed],
        )
        self.assertEqual(reviewed["value"], "reviewed wording")

    def test_machine_language_and_extract_select_validation_remain_closed(self):
        permission = make_seed_v21(axis="permission", value={"a": 1, "b": 2})
        for operator in (
            "exact",
            "eval",
            "expression",
            "template",
            "compose",
            "callback",
            "parse this natural language",
        ):
            with self.subTest(operator=operator):
                with self.assertRaisesRegex(ValueError, "INVALID_MACHINE_SPEC"):
                    self.derive(
                        {
                            "kind": "MACHINE_DERIVED",
                            "operator": operator,
                            "source_seed_ref": "SEED-001",
                            "pointer": "/a",
                        },
                        field="authentication",
                        seeds=[permission],
                    )
        for pointer in ("", "/missing", "/a~2"):
            with self.subTest(pointer=pointer):
                with self.assertRaises(ValueError):
                    self.derive(
                        {
                            "kind": "MACHINE_DERIVED",
                            "operator": "extract",
                            "source_seed_ref": "SEED-001",
                            "pointer": pointer,
                        },
                        field="authentication",
                        seeds=[permission],
                    )
        for keys in (["a", "a"], ["b", "a"], ["missing"]):
            with self.subTest(keys=keys):
                with self.assertRaisesRegex(ValueError, "INVALID_SELECT_SPEC"):
                    self.derive(
                        {
                            "kind": "MACHINE_DERIVED",
                            "operator": "select",
                            "source_seed_ref": "SEED-001",
                            "keys": keys,
                        },
                        field="authentication",
                        seeds=[permission],
                    )

    def test_unresolved_raises_semantic_authority_gap_with_exact_metadata(self):
        spec = {
            "kind": "UNRESOLVED",
            "gap_type": "AMBIGUITY_FOUND",
            "description": "The permitted actor is unclear.",
            "required_authority_class": "INTENT",
            "evidence_refs": ["EVD-001"],
        }
        with self.assertRaises(SemanticAuthorityGap) as raised:
            self.derive(spec)
        self.assertEqual(raised.exception.code, "SEMANTIC_AUTHORITY_GAP")
        self.assertEqual(raised.exception.detail, spec)
        self.assertIsNot(raised.exception.detail, spec)

    def test_malformed_unresolved_is_invalid_not_semantic_gap(self):
        spec = {
            "kind": "UNRESOLVED",
            "gap_type": "AMBIGUITY_FOUND",
            "description": "The permitted actor is unclear.",
            "required_authority_class": "INTENT",
            "evidence_refs": ["EVD-001", "EVD-001"],
        }
        with self.assertRaises(ValueError) as raised:
            self.derive(spec)
        self.assertNotIsInstance(raised.exception, SemanticAuthorityGap)


class ExactCollectionClassifierTests(unittest.TestCase):
    def test_classifier_returns_when_exact_collection_is_representable(self):
        classify_exact_collection_request(
            field_policy={
                "collection_semantics": "MEMBERSHIP_SET",
                "allowed_derivations": ["DIRECT_AUTHORITY", "collect_exact"],
            },
            eligible_seed_refs=["SEED-A", "SEED-B"],
            requested_collection_semantics="MEMBERSHIP_SET",
        )

    def test_classifier_raises_only_for_proven_eligible_unrepresentable_exact_set(self):
        policy = {
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
        self.assertEqual(raised.exception.code, "CONTRACT_EXPRESSIVENESS_GAP")
        self.assertEqual(
            raised.exception.detail,
            {
                "collection_semantics": "CONJUNCTIVE_SET",
                "eligible_seed_refs": refs,
            },
        )

    def test_classifier_rejects_none_mismatch_or_unproven_refs_as_invalid(self):
        cases = (
            (
                {"collection_semantics": "NONE", "allowed_derivations": []},
                ["SEED-A", "SEED-B"],
                "MEMBERSHIP_SET",
            ),
            (
                {
                    "collection_semantics": "MEMBERSHIP_SET",
                    "allowed_derivations": ["DIRECT_AUTHORITY"],
                },
                ["SEED-A", "SEED-B"],
                "CONJUNCTIVE_SET",
            ),
            (
                {
                    "collection_semantics": "MEMBERSHIP_SET",
                    "allowed_derivations": ["DIRECT_AUTHORITY"],
                },
                ["SEED-A"],
                "MEMBERSHIP_SET",
            ),
            (
                {
                    "collection_semantics": "MEMBERSHIP_SET",
                    "allowed_derivations": ["DIRECT_AUTHORITY"],
                },
                ["SEED-A", "SEED-A"],
                "MEMBERSHIP_SET",
            ),
        )
        for policy, refs, requested in cases:
            with self.subTest(policy=policy, refs=refs, requested=requested):
                with self.assertRaises(ValueError) as raised:
                    classify_exact_collection_request(
                        field_policy=policy,
                        eligible_seed_refs=refs,
                        requested_collection_semantics=requested,
                    )
                self.assertNotIsInstance(raised.exception, ContractExpressivenessGap)


if __name__ == "__main__":
    unittest.main()
