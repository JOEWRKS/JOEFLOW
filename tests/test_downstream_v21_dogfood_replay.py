import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tests.downstream_v21_support import make_seed_v21  # noqa: E402
from approval_v2 import (  # noqa: E402
    approval_manifest_digest,
    compute_approval_manifest,
    definition_digest,
)
from downstream_v2.seeds import build_closed_source_seed_inventory  # noqa: E402
from downstream_v21.audit import (  # noqa: E402
    audit_action_contract_v21_against_state,
)
from downstream_v21.compiler import validate_verification_basis  # noqa: E402
from downstream_v21.compiler import compile_handoff_definition_v21  # noqa: E402
from downstream_v21.contracts import validate_action_contract_v21  # noqa: E402
from downstream_v21.responsibility import (  # noqa: E402
    load_responsibility_profile_v21,
)
from downstream_v21.runtime_plan import (  # noqa: E402
    materialize_runtime_plan,
    validate_runtime_plan,
)
from downstream_v21.runtime_profile import (  # noqa: E402
    load_runtime_responsibility_profile,
    runtime_responsibility_digest,
)
from downstream_v21.semantic_review import (  # noqa: E402
    RELIABILITY_STATUS,
    SEMANTIC_REVIEW_VERSION,
    build_semantic_review_package_v21,
)
from state_validation_v2 import evaluate_closure_v2  # noqa: E402


REMOVED_RUNTIME_FIELDS = {
    "default_result",
    "result_expectations",
    "test_obligations",
}

M6_BRANCH = "feat/core-semantic-closure-v2-m6-integration-adoption"
M6_HEAD = "d38b0ca04768888c47e658c79f41e1cec0a7a1ce"
M6_TREE = "40749d900b98936cf694b0c96db7897011cddae8"
M6_DEFINITION_DIGEST = (
    "e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c"
)
M6_MANIFEST_DIGEST = (
    "60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705"
)
M6_APPROVED_AT = "2026-08-30T11:54:26Z"
M6_APPROVED_BY = "user"
M6_REPLY_ACTOR_REFS = [
    "SEED-65b2a6c9b4932974b3b60496",
    "SEED-85cdd056577c5a7b55b59c5a",
]
M6_EXPECTED_INPUT_REFS = {
    "create_pin": [
        "SEED-8074b355d815df0963221327",
        "SEED-9968346c37f09b10b8a89d89",
        "SEED-d4f8428a81f5d608960c174f",
    ],
    "reply_thread": [
        "SEED-23f1071f8cd9cf14d4ce3e72",
        "SEED-257257f91c773cfe5dfe3347",
        "SEED-ed9c757cbc28c40044dfd8aa",
    ],
    "resend_review_request": [
        "SEED-2179f7c6d433e0f01ceedaec",
        "SEED-3511c07413b4b2a8e48bc8ef",
        "SEED-87ed156646ff86f1a94ffcb6",
        "SEED-95b7ebff04f98f2585cdd450",
        "SEED-c1f73501db4b81ff52c0bada",
    ],
    "resolve_thread": [
        "SEED-1c58ea9c18b9adce056ad8d8",
        "SEED-f8a9b7a517767afe06918391",
    ],
    "revoke_review_link": [
        "SEED-0bbd614e466ba57d43091942",
        "SEED-337c7bfafd892f3dee5ca3ed",
        "SEED-5e73bd1a9391c6af52805a5f",
        "SEED-96e026ef7e47422ef9be1926",
        "SEED-ca488ac48f7609e656897031",
    ],
    "send_review_request": [
        "SEED-1cb3f22fadee73e021bb733b",
        "SEED-40f8e56657681c5a85b5badf",
        "SEED-857bd5c346bdb334d2ba5c12",
        "SEED-88b34506701b1ac0726ce8a8",
        "SEED-f77a81284fea9021dd14872a",
    ],
}
M6_EXPECTED_BASIS = {
    "create_pin": {
        "outcome_basis_seed_refs": [
            "SEED-07c3ee5fc8648b578e618f5b",
            "SEED-41684fac7ad6bc4a99009bde",
        ],
        "acceptance_basis_seed_refs": ["SEED-ba5ac85922b87e8fb415dab0"],
    },
    "reply_thread": {
        "outcome_basis_seed_refs": [
            "SEED-2383c2533e4e5ad83e8b8b2d",
            "SEED-276e712f11f6a6869f367df0",
        ],
        "acceptance_basis_seed_refs": ["SEED-ba5ac85922b87e8fb415dab0"],
    },
    "resend_review_request": {
        "outcome_basis_seed_refs": [
            "SEED-0154fce39c180e44109a6f33",
            "SEED-3b6a182fe085e1ffac13e56e",
        ],
        "acceptance_basis_seed_refs": ["SEED-0154fce39c180e44109a6f33"],
    },
    "resolve_thread": {
        "outcome_basis_seed_refs": [
            "SEED-241c81dc3215aff557671dda",
            "SEED-276e712f11f6a6869f367df0",
        ],
        "acceptance_basis_seed_refs": ["SEED-ba5ac85922b87e8fb415dab0"],
    },
    "revoke_review_link": {
        "outcome_basis_seed_refs": [
            "SEED-0154fce39c180e44109a6f33",
            "SEED-192daff597cf35694c577113",
        ],
        "acceptance_basis_seed_refs": ["SEED-0154fce39c180e44109a6f33"],
    },
    "send_review_request": {
        "outcome_basis_seed_refs": [
            "SEED-0154fce39c180e44109a6f33",
            "SEED-3b6a182fe085e1ffac13e56e",
        ],
        "acceptance_basis_seed_refs": ["SEED-0154fce39c180e44109a6f33"],
    },
}
M6_ARTIFACT_SHA256 = {
    "approval-manifest.json": (
        "f354e7baf1001bf1cd2a763569b310947ca2fd1ae4e6eb57c6f1573d9ec2eef1"
    ),
    "dogfood-summary.md": (
        "79859d308f71eefb426fa8876c1f707f1d4fd579862e40aae87dad962c0b43ce"
    ),
    "handoff-definition.json": (
        "11fdce0fdce90d8c2f5e069cd766aa338e5f4efd7653d38e2d152509653fbaef"
    ),
    "reentry-probe.json": (
        "b6e0b4960211456a6dacf521a407667c0b838b5b1dee50db9ab02f2b9534e211"
    ),
    "product-definition/client-feedback-portal-dogfood-v2/state.json": (
        "728744301bc0ea2a1766852b7b46bab3c610215b31f63c0a784dd804fa3ce49d"
    ),
}


class TrueSemanticGapFound(ValueError):
    pass


class M6ReplayEvidenceUnavailable(ValueError):
    pass


def _exact_seed_index(seed_inventory):
    if not isinstance(seed_inventory, list):
        raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")
    index = {}
    for seed in seed_inventory:
        if not isinstance(seed, dict) or not isinstance(seed.get("seed_key"), str):
            raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")
        ref = seed["seed_key"]
        if ref in index:
            raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")
        index[ref] = seed
    return index


def _collect_spec(refs):
    refs = sorted(set(refs))
    if not refs:
        raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")
    if len(refs) == 1:
        return {"kind": "DIRECT_AUTHORITY", "source_seed_ref": refs[0]}
    return {
        "kind": "MACHINE_DERIVED",
        "operator": "collect_exact",
        "source_seed_refs": refs,
    }


def _input_invariant_refs(action, seed_inventory):
    locator = action["ux_action_locator"]
    scope_refs = set(action["authority_scope_refs"])
    refs = []
    for seed in seed_inventory:
        location = seed.get("location") if isinstance(seed, dict) else None
        if not isinstance(location, dict):
            continue
        if (
            location.get("scope") == "UX_ACTION"
            and location.get("owner_ref") == locator["screen_ref"]
            and location.get("owner_ref") in scope_refs
            and location.get("action_key") == locator["action_key"]
            and location.get("axis") in {"input", "validation"}
            and seed.get("source_status") in {None, "CURRENT"}
        ):
            refs.append(seed["seed_key"])
    return sorted(refs)


def _validated_actor_refs(action, refs, seed_index):
    normalized = sorted(set(refs)) if isinstance(refs, list) else []
    if len(normalized) < 2 or len(normalized) != len(refs):
        raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")
    scope_refs = set(action["authority_scope_refs"])
    for ref in normalized:
        seed = seed_index.get(ref)
        location = seed.get("location") if isinstance(seed, dict) else None
        if (
            not isinstance(location, dict)
            or seed.get("source_status") not in {None, "CURRENT"}
            or location.get("scope") != "CORE"
            or location.get("axis") != "actor"
            or location.get("owner_ref") not in scope_refs
        ):
            raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")
    return normalized


def translate_handoff_v20_to_v21(
    definition,
    seed_inventory,
    *,
    known_multi_actor_refs,
):
    """Translate the fixed 2.0 replay slice without inventing product values."""
    if (
        not isinstance(definition, dict)
        or definition.get("definition_schema_version")
        != "joewrks.handoff-definition/2.0"
        or not isinstance(definition.get("actions"), list)
        or not isinstance(definition.get("lifecycles"), list)
    ):
        raise ValueError("INVALID_M6_HANDOFF_DEFINITION")
    seed_index = _exact_seed_index(seed_inventory)
    profile = load_responsibility_profile_v21()
    translated = copy.deepcopy(definition)
    translated["definition_schema_version"] = "joewrks.handoff-definition/2.1"
    action_audits = []
    selected_basis_refs = set()

    for source_action, action in zip(definition["actions"], translated["actions"]):
        source_fields = source_action["fields"]
        fields = {
            name: copy.deepcopy(spec)
            for name, spec in source_fields.items()
            if name not in REMOVED_RUNTIME_FIELDS
        }
        actor = fields.get("actor")
        if isinstance(actor, dict) and actor.get("kind") == "UNRESOLVED":
            refs = _validated_actor_refs(
                action,
                known_multi_actor_refs.get(action["action_id"]),
                seed_index,
            )
            fields["actor"] = _collect_spec(refs)

        input_spec = fields.get("input_invariants")
        if isinstance(input_spec, dict) and input_spec.get("kind") == "UNRESOLVED":
            input_refs = _input_invariant_refs(action, seed_inventory)
            fields["input_invariants"] = _collect_spec(input_refs)
        else:
            input_refs = []

        unresolved = [
            name
            for name, spec in fields.items()
            if isinstance(spec, dict) and spec.get("kind") == "UNRESOLVED"
        ]
        if unresolved:
            raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")

        try:
            outcome_refs = sorted(
                {
                    source_fields[name]["source_seed_ref"]
                    for name in ("visible_success", "visible_error")
                }
            )
            acceptance_refs = [source_fields["trace"]["source_seed_ref"]]
        except (KeyError, TypeError) as error:
            raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND") from error
        context = {
            "authority_scope_refs": list(action["authority_scope_refs"]),
            "current_scope_refs": list(action["authority_scope_refs"]),
            "ux_action_locator": copy.deepcopy(action["ux_action_locator"]),
        }
        basis = validate_verification_basis(
            {
                "outcome_basis_seed_refs": outcome_refs,
                "acceptance_basis_seed_refs": acceptance_refs,
            },
            context=context,
            seeds=seed_index,
            profile=profile,
        )
        selected_basis_refs.update(outcome_refs)
        selected_basis_refs.update(acceptance_refs)
        action["fields"] = fields
        action["verification_basis"] = basis
        action_audits.append(
            {
                "action_id": action["action_id"],
                "actor_seed_refs": (
                    fields["actor"].get("source_seed_refs")
                    or [fields["actor"].get("source_seed_ref")]
                ),
                "input_invariant_seed_refs": (
                    fields["input_invariants"].get("source_seed_refs")
                    or [fields["input_invariants"].get("source_seed_ref")]
                ),
                "verification_basis": copy.deepcopy(basis),
            }
        )

    return translated, {
        "actions": action_audits,
        "selected_verification_basis_refs": sorted(selected_basis_refs),
    }


def _git(worktree, *args, binary=False):
    completed = subprocess.run(
        ["git", "-C", str(worktree), *args],
        check=False,
        capture_output=True,
        text=not binary,
    )
    if completed.returncode != 0:
        raise M6ReplayEvidenceUnavailable("M6_REPLAY_EVIDENCE_UNAVAILABLE")
    return completed.stdout if binary else completed.stdout.strip()


def _tracked_worktree_bytes(worktree):
    paths = [
        value.decode("utf-8")
        for value in _git(worktree, "ls-files", "-z", binary=True).split(b"\0")
        if value
    ]
    return {
        path: hashlib.sha256((worktree / path).read_bytes()).hexdigest()
        for path in paths
    }


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _require_m6(condition):
    if not condition:
        raise M6ReplayEvidenceUnavailable("M6_REPLAY_EVIDENCE_UNAVAILABLE")


def runtime_draft_for_contract(contract):
    profile = load_runtime_responsibility_profile()
    critical = sorted(
        field_name
        for field_name, classification in profile["action_fields"].items()
        if classification == "RUNTIME_CRITICAL"
    )
    return {
        "actions": [
            {
                "action_id": action["action_id"],
                "cases": [
                    {
                        "result_expectation": {
                            "result_class": "SUCCESS",
                            "contract_field_refs": [
                                f"actions/{action['action_id']}/{field_name}"
                                for field_name in critical
                            ],
                        },
                        "component_expectations": [],
                        "evidence_assertions": [],
                        "fixture_requirements": ["OPAQUE_ID"],
                    }
                ],
            }
            for action in contract["actions"]
        ],
        "lifecycles": [],
    }


def replay_m6_phase_b(worktree):
    """Read the preserved M6 Phase-B tree and replay only its known 2.1 slice."""
    worktree = Path(worktree).resolve()
    _require_m6(worktree.is_dir())
    _require_m6(_git(worktree, "branch", "--show-current") == M6_BRANCH)
    _require_m6(_git(worktree, "rev-parse", "HEAD") == M6_HEAD)
    _require_m6(_git(worktree, "rev-parse", "HEAD^{tree}") == M6_TREE)
    _require_m6(_git(worktree, "status", "--porcelain=v1") == "")
    pre_bytes = _tracked_worktree_bytes(worktree)
    dogfood = worktree / "evals" / "core-semantic-closure-v2-m6" / "dogfood"

    try:
        artifact_hashes = {
            relative: _sha256(dogfood / relative)
            for relative in M6_ARTIFACT_SHA256
        }
        _require_m6(artifact_hashes == M6_ARTIFACT_SHA256)
        state = _json(
            dogfood
            / "product-definition"
            / "client-feedback-portal-dogfood-v2"
            / "state.json"
        )
        persisted_manifest = _json(dogfood / "approval-manifest.json")
        handoff_v20 = _json(dogfood / "handoff-definition.json")
        old_reentry = _json(dogfood / "reentry-probe.json")

        project = state.get("project", {})
        approval = state.get("approval", {})
        history = state.get("approval_history", [])
        closure = evaluate_closure_v2(state)
        computed_manifest = compute_approval_manifest(state)
        _require_m6(project.get("definition_revision") == 1)
        _require_m6(project.get("definition_status") == "CLOSED")
        _require_m6(approval.get("status") == "APPROVED")
        _require_m6(approval.get("approved_revision") == 1)
        _require_m6(
            approval.get("approved_definition_digest") == M6_DEFINITION_DIGEST
        )
        _require_m6(approval.get("approved_manifest_digest") == M6_MANIFEST_DIGEST)
        _require_m6(approval.get("approved_at") == M6_APPROVED_AT)
        _require_m6(approval.get("approved_by") == M6_APPROVED_BY)
        _require_m6(definition_digest(state) == M6_DEFINITION_DIGEST)
        _require_m6(computed_manifest == persisted_manifest)
        _require_m6(
            approval_manifest_digest(persisted_manifest) == M6_MANIFEST_DIGEST
        )
        _require_m6(closure.get("closed") is True)
        _require_m6(closure.get("errors") == [])
        _require_m6(closure.get("definition_digest") == M6_DEFINITION_DIGEST)
        _require_m6(isinstance(history, list) and len(history) == 1)
        _require_m6(history[0].get("revision") == 1)
        _require_m6(history[0].get("definition_digest") == M6_DEFINITION_DIGEST)
        _require_m6(history[0].get("manifest_digest") == M6_MANIFEST_DIGEST)

        seeds = build_closed_source_seed_inventory(state)
        handoff_v21, translation_audit = translate_handoff_v20_to_v21(
            handoff_v20,
            seeds,
            known_multi_actor_refs={"reply_thread": M6_REPLY_ACTOR_REFS},
        )
        compiled = compile_handoff_definition_v21(state, handoff_v21)
        contract = compiled.get("contract")
        if contract is None:
            semantic = len(compiled.get("semantic_gaps", []))
            expressiveness = len(compiled.get("expressiveness_gaps", []))
            if semantic:
                raise TrueSemanticGapFound("TRUE_SEMANTIC_GAP_FOUND")
            raise AssertionError(
                f"2.1 replay did not materialize: semantic={semantic}, "
                f"expressiveness={expressiveness}"
            )
        contract_audit = audit_action_contract_v21_against_state(contract, state)
        review_package = build_semantic_review_package_v21(contract)
        draft = runtime_draft_for_contract(contract)
        runtime_plan = materialize_runtime_plan(contract, draft)
        return {
            "artifact_hashes": artifact_hashes,
            "closure": closure,
            "old_handoff": handoff_v20,
            "old_reentry": old_reentry,
            "handoff": handoff_v21,
            "translation_audit": translation_audit,
            "compile_result": compiled,
            "contract": contract,
            "contract_audit": contract_audit,
            "semantic_review": {
                "identity": SEMANTIC_REVIEW_VERSION,
                "reliability_status": RELIABILITY_STATUS,
                "package": review_package,
            },
            "runtime_draft": draft,
            "runtime_plan": runtime_plan,
        }
    finally:
        post_identity = {
            "branch": _git(worktree, "branch", "--show-current"),
            "head": _git(worktree, "rev-parse", "HEAD"),
            "tree": _git(worktree, "rev-parse", "HEAD^{tree}"),
            "status": _git(worktree, "status", "--porcelain=v1"),
            "tracked_bytes": _tracked_worktree_bytes(worktree),
        }
        if post_identity != {
            "branch": M6_BRANCH,
            "head": M6_HEAD,
            "tree": M6_TREE,
            "status": "",
            "tracked_bytes": pre_bytes,
        }:
            raise AssertionError("preserved M6 worktree changed during replay")


def synthetic_replay_authority():
    seeds = [
        make_seed_v21(
            "SEED-000000000000000000000001",
            scope="CORE",
            owner_ref="REQ-A",
            axis="actor",
            value="Designer",
        ),
        make_seed_v21(
            "SEED-000000000000000000000002",
            scope="CORE",
            owner_ref="REQ-B",
            axis="actor",
            value="Reviewer",
        ),
        make_seed_v21(
            "SEED-000000000000000000000003",
            scope="UX_ACTION",
            owner_ref="SCR-1",
            axis="input",
            action_key="reply_thread",
            value="Exact thread input",
        ),
        make_seed_v21(
            "SEED-000000000000000000000004",
            scope="UX_ACTION",
            owner_ref="SCR-1",
            axis="validation",
            action_key="reply_thread",
            value="Exact reply validation",
        ),
        make_seed_v21(
            "SEED-000000000000000000000005",
            scope="UX_ACTION",
            owner_ref="SCR-1",
            axis="success",
            action_key="reply_thread",
            value="Exact reply success",
        ),
        make_seed_v21(
            "SEED-000000000000000000000006",
            scope="UX_ACTION",
            owner_ref="SCR-1",
            axis="failure",
            action_key="reply_thread",
            value="Exact reply failure",
        ),
        make_seed_v21(
            "SEED-000000000000000000000007",
            scope="CORE",
            owner_ref="REQ-B",
            axis="acceptance",
            value="Exact reply acceptance",
        ),
        make_seed_v21(
            "SEED-000000000000000000000008",
            scope="CORE",
            owner_ref="REQ-A",
            axis="error",
            value="Eligible but not selected by the old handoff",
        ),
    ]
    definition = {
        "definition_schema_version": "joewrks.handoff-definition/2.0",
        "product_slug": "synthetic-replay",
        "actions": [
            {
                "action_id": "reply_thread",
                "authority_scope_refs": ["REQ-A", "REQ-B", "SCR-1"],
                "ux_action_locator": {
                    "screen_ref": "SCR-1",
                    "action_key": "reply_thread",
                },
                "fields": {
                    "actor": {
                        "kind": "UNRESOLVED",
                        "gap_type": "CONTRACT_CONFLICT",
                        "description": "Two approved actors require a lossless exact set.",
                        "required_authority_class": "INTENT",
                        "evidence_refs": ["EVD-1", "EVD-2"],
                    },
                    "authentication": {
                        "kind": "DIRECT_AUTHORITY",
                        "source_seed_ref": "SEED-000000000000000000000001",
                    },
                    "input_invariants": {
                        "kind": "UNRESOLVED",
                        "gap_type": "CONTRACT_CONFLICT",
                        "description": "Exact input and validation authority needs a set.",
                        "required_authority_class": "INTENT",
                        "evidence_refs": ["EVD-1"],
                    },
                    "default_result": {"kind": "UNRESOLVED"},
                    "result_expectations": {"kind": "UNRESOLVED"},
                    "test_obligations": {"kind": "UNRESOLVED"},
                    "visible_success": {
                        "kind": "DIRECT_AUTHORITY",
                        "source_seed_ref": "SEED-000000000000000000000005",
                    },
                    "visible_error": {
                        "kind": "DIRECT_AUTHORITY",
                        "source_seed_ref": "SEED-000000000000000000000006",
                    },
                    "trace": {
                        "kind": "DIRECT_AUTHORITY",
                        "source_seed_ref": "SEED-000000000000000000000007",
                    },
                },
            }
        ],
        "lifecycles": [],
    }
    return definition, seeds


class ReplayTranslationHelperTests(unittest.TestCase):
    def test_translation_preserves_exact_authority_without_selecting_all_candidates(self):
        definition, seeds = synthetic_replay_authority()
        translate = globals().get("translate_handoff_v20_to_v21")
        self.assertIsNotNone(translate, "replay translation helper is missing")

        translated, audit = translate(
            definition,
            seeds,
            known_multi_actor_refs={
                "reply_thread": [
                    "SEED-000000000000000000000002",
                    "SEED-000000000000000000000001",
                ]
            },
        )

        action = translated["actions"][0]
        self.assertEqual(
            translated["definition_schema_version"],
            "joewrks.handoff-definition/2.1",
        )
        self.assertEqual(action["action_id"], "reply_thread")
        self.assertEqual(
            action["authority_scope_refs"], ["REQ-A", "REQ-B", "SCR-1"]
        )
        self.assertEqual(
            action["ux_action_locator"],
            {"screen_ref": "SCR-1", "action_key": "reply_thread"},
        )
        self.assertEqual(
            action["fields"]["authentication"],
            definition["actions"][0]["fields"]["authentication"],
        )
        self.assertEqual(
            action["fields"]["actor"],
            {
                "kind": "MACHINE_DERIVED",
                "operator": "collect_exact",
                "source_seed_refs": [
                    "SEED-000000000000000000000001",
                    "SEED-000000000000000000000002",
                ],
            },
        )
        self.assertEqual(
            action["fields"]["input_invariants"],
            {
                "kind": "MACHINE_DERIVED",
                "operator": "collect_exact",
                "source_seed_refs": [
                    "SEED-000000000000000000000003",
                    "SEED-000000000000000000000004",
                ],
            },
        )
        self.assertTrue(REMOVED_RUNTIME_FIELDS.isdisjoint(action["fields"]))
        self.assertEqual(
            action["verification_basis"],
            {
                "outcome_basis_seed_refs": [
                    "SEED-000000000000000000000005",
                    "SEED-000000000000000000000006",
                ],
                "acceptance_basis_seed_refs": [
                    "SEED-000000000000000000000007"
                ],
            },
        )
        self.assertNotIn(
            "SEED-000000000000000000000008",
            audit["selected_verification_basis_refs"],
        )
        self.assertEqual(definition["definition_schema_version"], "joewrks.handoff-definition/2.0")
        self.assertEqual(seeds[-1]["value"], "Eligible but not selected by the old handoff")


class M6DogfoodReplayTests(unittest.TestCase):
    def test_preserved_phase_b_replays_read_only_through_21(self):
        configured = os.environ.get("JOEWRKS_M6_PHASE_B_WORKTREE")
        if not configured:
            self.fail("M6_REPLAY_EVIDENCE_UNAVAILABLE")
        try:
            replay = replay_m6_phase_b(configured)
        except M6ReplayEvidenceUnavailable as error:
            self.fail(str(error))

        old = replay["old_reentry"]
        self.assertEqual(replay["old_handoff"]["definition_schema_version"], "joewrks.handoff-definition/2.0")
        self.assertEqual(old["status"], "REENTRY_REQUIRED")
        self.assertIsNone(old["contract"])
        self.assertEqual(old["semantic_debt"]["authority_gap_count"], 25)
        self.assertEqual(old["semantic_debt"]["direct_authority_count"], 131)
        self.assertEqual(len(old["gaps"]), 25)
        self.assertEqual(len(old["reentry_events"]), 25)
        self.assertEqual({gap["code"] for gap in old["gaps"]}, {"SEMANTIC_AUTHORITY_GAP"})
        self.assertEqual(
            {event["event_type"] for event in old["reentry_events"]},
            {"CONTRACT_CONFLICT"},
        )
        self.assertTrue(
            all(event["source_contract_hash"] is None for event in old["reentry_events"])
        )

        compiled = replay["compile_result"]
        contract = replay["contract"]
        self.assertEqual(compiled["status"], "AUTHORITY_READY_MACHINE_VERIFIED")
        self.assertEqual(compiled["semantic_gaps"], [])
        self.assertEqual(compiled["expressiveness_gaps"], [])
        self.assertEqual(compiled["reentry_events"], [])
        self.assertEqual(compiled["semantic_debt"]["authority_gap_count"], 0)
        self.assertEqual(compiled["semantic_debt"]["direct_authority_count"], 131)
        self.assertEqual(compiled["semantic_debt"]["machine_derived_count"], 7)
        self.assertEqual(contract["contract_schema_version"], "joewrks.action-conformance/2.1")
        self.assertEqual(validate_action_contract_v21(contract), [])
        self.assertEqual(
            replay["contract_audit"],
            {
                "status": "CONFORMANT",
                "authority_revision_relation": "SAME_APPROVED_REVISION",
                "affected_consumers": [],
                "semantic_gaps": [],
                "errors": [],
            },
        )
        self.assertEqual(
            contract["source_authority"]["approved_definition_digest"],
            M6_DEFINITION_DIGEST,
        )
        self.assertEqual(
            contract["source_authority"]["approved_manifest_digest"],
            M6_MANIFEST_DIGEST,
        )

        by_action = {action["action_id"]: action for action in contract["actions"]}
        definition_actions = {
            action["action_id"]: action for action in replay["handoff"]["actions"]
        }
        self.assertEqual(set(by_action), set(M6_EXPECTED_INPUT_REFS))
        for action_id, expected_refs in M6_EXPECTED_INPUT_REFS.items():
            handoff_action = definition_actions[action_id]
            action = by_action[action_id]
            self.assertTrue(REMOVED_RUNTIME_FIELDS.isdisjoint(handoff_action["fields"]))
            self.assertTrue(REMOVED_RUNTIME_FIELDS.isdisjoint(action["fields"]))
            self.assertEqual(
                handoff_action["fields"]["input_invariants"]["source_seed_refs"],
                expected_refs,
            )
            self.assertEqual(action["fields"]["input_invariants"]["source_seed_refs"], expected_refs)
            self.assertEqual(handoff_action["verification_basis"], M6_EXPECTED_BASIS[action_id])
            self.assertEqual(action["verification_basis"], M6_EXPECTED_BASIS[action_id])

        reply_actor = by_action["reply_thread"]["fields"]["actor"]
        self.assertEqual(reply_actor["source_seed_refs"], M6_REPLY_ACTOR_REFS)
        self.assertEqual(reply_actor["value"], ["Workspace Owner / Designer", "Client Reviewer"])
        self.assertEqual(
            reply_actor["derivation"],
            {
                "kind": "MACHINE_DERIVED",
                "operator": "collect_exact",
                "source_seed_refs": M6_REPLY_ACTOR_REFS,
            },
        )

        review = replay["semantic_review"]
        self.assertEqual(review["identity"], "joewrks.semantic-review/2.1")
        self.assertEqual(review["reliability_status"], "NOT_MEASURED")
        self.assertIsNone(review["package"])
        self.assertEqual(contract["semantic_debt"]["review_required_count"], 0)

        plan = replay["runtime_plan"]
        self.assertEqual(plan["plan_schema_version"], "joewrks.runtime-conformance-plan/1.0")
        self.assertEqual(plan["coverage_summary"]["status"], "COMPLETE")
        self.assertEqual(plan["coverage_summary"]["missing_field_refs"], [])
        self.assertEqual(plan["mapping_gaps"], [])
        self.assertEqual(validate_runtime_plan(plan, contract), [])
        self.assertEqual(
            plan["runtime_profile"],
            {
                "profile_id": "joewrks.runtime-responsibility/1.0",
                "digest": runtime_responsibility_digest(),
            },
        )
        self.assertEqual(plan["source_contract"]["semantic_contract_hash"], contract["semantic_contract_hash"])
        self.assertNotIn("expected_value", json.dumps(replay["runtime_draft"], sort_keys=True))
        self.assertEqual(replay["runtime_draft"]["lifecycles"], [])
        self.assertTrue(
            all(
                case["result_expectation"]["result_class"] == "SUCCESS"
                and case["component_expectations"] == []
                and case["evidence_assertions"] == []
                and case["fixture_requirements"] == ["OPAQUE_ID"]
                for action in replay["runtime_draft"]["actions"]
                for case in action["cases"]
            )
        )


if __name__ == "__main__":
    unittest.main()
