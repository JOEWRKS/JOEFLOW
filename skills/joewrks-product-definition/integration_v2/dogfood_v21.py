"""Deterministic M6 dogfood 2.1 materialization; never reads test helpers."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from downstream.protocol import PROTOCOL_VERSION, dumps_record
from downstream_v2.seeds import build_closed_source_seed_inventory
from downstream_v21.compiler import compile_handoff_definition_v21, validate_verification_basis
from downstream_v21.runtime_evidence import build_runtime_evidence_bundle
from downstream_v21.runtime_plan import materialize_runtime_plan
from downstream_v21.runtime_profile import load_runtime_responsibility_profile
from downstream_v21.responsibility import load_responsibility_profile_v21

from .client_feedback_portal_fixture import execute_fixture_scenario
from .runtime_v21 import verify_runtime_v21


REMOVED_RUNTIME_FIELDS = {"default_result", "result_expectations", "test_obligations"}
REPLY_ACTOR_REFS = ["SEED-65b2a6c9b4932974b3b60496", "SEED-85cdd056577c5a7b55b59c5a"]


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write(path: Path, value: object) -> None:
    path.write_bytes(_canonical(value) + b"\n")


def _collect(refs: list[str]) -> dict[str, object]:
    refs = sorted(set(refs))
    if not refs:
        raise ValueError("TRUE_SEMANTIC_GAP_FOUND")
    return ({"kind": "DIRECT_AUTHORITY", "source_seed_ref": refs[0]} if len(refs) == 1
            else {"kind": "MACHINE_DERIVED", "operator": "collect_exact", "source_seed_refs": refs})


def translate_handoff_v20_to_v21(definition: dict[str, object], seeds: list[dict[str, object]]) -> dict[str, object]:
    """Mechanical M5.1-approved translation for this exact dogfood slice."""
    translated = copy.deepcopy(definition)
    translated["definition_schema_version"] = "joewrks.handoff-definition/2.1"
    seed_index = {seed["seed_key"]: seed for seed in seeds}
    profile = load_responsibility_profile_v21()
    for action in translated["actions"]:
        source_fields = action["fields"]
        fields = {key: copy.deepcopy(value) for key, value in source_fields.items() if key not in REMOVED_RUNTIME_FIELDS}
        if action["action_id"] == "reply_thread":
            fields["actor"] = _collect(REPLY_ACTOR_REFS)
        locator, scope = action["ux_action_locator"], set(action["authority_scope_refs"])
        input_refs = sorted(seed["seed_key"] for seed in seeds if (
            seed.get("source_status") in {None, "CURRENT"}
            and seed.get("location", {}).get("scope") == "UX_ACTION"
            and seed["location"].get("owner_ref") == locator["screen_ref"]
            and seed["location"].get("owner_ref") in scope
            and seed["location"].get("action_key") == locator["action_key"]
            and seed["location"].get("axis") in {"input", "validation"}
        ))
        fields["input_invariants"] = _collect(input_refs)
        if any(spec.get("kind") == "UNRESOLVED" for spec in fields.values() if isinstance(spec, dict)):
            raise ValueError("TRUE_SEMANTIC_GAP_FOUND")
        outcome_refs = sorted({source_fields["visible_success"]["source_seed_ref"], source_fields["visible_error"]["source_seed_ref"]})
        acceptance_refs = [source_fields["trace"]["source_seed_ref"]]
        context = {"authority_scope_refs": action["authority_scope_refs"], "current_scope_refs": action["authority_scope_refs"], "ux_action_locator": locator}
        action["fields"] = fields
        action["verification_basis"] = validate_verification_basis(
            {"outcome_basis_seed_refs": outcome_refs, "acceptance_basis_seed_refs": acceptance_refs},
            context=context, seeds=seed_index, profile=profile,
        )
    return translated


def runtime_draft(contract: dict[str, object]) -> dict[str, object]:
    """Map every runtime-critical field to concrete, executable portal cases."""
    critical = {
        name
        for name, kind in load_runtime_responsibility_profile()["action_fields"].items()
        if kind == "RUNTIME_CRITICAL"
    }

    def action_cases(action: dict[str, object]) -> list[dict[str, object]]:
        action_id = action["action_id"]
        ref = lambda name: f"actions/{action_id}/{name}"

        def components(expectations: dict[str, str], refs: list[str]):
            return [
                {
                    "component": component,
                    "expectation": expectation,
                    "contract_field_refs": [ref(name) for name in refs],
                }
                for component, expectation in expectations.items()
            ]

        success_delivery = (
            "CHANGED"
            if action_id in {"send_review_request", "resend_review_request"}
            else "UNCHANGED"
        )
        success = {
            "result_expectation": {
                "result_class": "SUCCESS",
                "contract_field_refs": [
                    ref(name)
                    for name in (
                        "preconditions",
                        "allowed_current_states",
                        "input_invariants",
                        "version_result",
                    )
                ],
            },
            "component_expectations": components(
                {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "CHANGED",
                    "delivery_effects": success_delivery,
                },
                [
                    "object_binding",
                    "expected_domain_mutation",
                    "forbidden_mutations",
                    "superseded_rules",
                    "concurrency",
                    "version_result",
                    "history_result",
                    "business_side_effects",
                    "delivery_effects",
                ],
            ),
            "evidence_assertions": [
                {
                    "type": "path_equals",
                    "pointer": "/command/actor",
                    "expected_value_source": {
                        "source": "CONTRACT_DERIVED",
                        "contract_field_path": ref("actor"),
                        "pointer": "/value/0" if isinstance(action["fields"]["actor"]["value"], list) else "/value",
                    },
                    "contract_field_refs": [
                        ref("actor"),
                        ref("authentication"),
                        ref("relationship_predicate"),
                    ],
                },
                {
                    "type": "path_present",
                    "pointer": "/command/action_id",
                    "contract_field_refs": [ref("command")],
                },
            ],
            "fixture_requirements": ["OPAQUE_ID", "REVISION_INSTANCE"],
        }
        unchanged = {
            "authoritative_state": "UNCHANGED",
            "revision": "UNCHANGED",
            "history": "UNCHANGED",
            "business_side_effects": "UNCHANGED",
            "delivery_effects": "UNCHANGED",
        }
        rejected = {
            "result_expectation": {
                "result_class": "REJECTED",
                "contract_field_refs": [
                    ref(name)
                    for name in (
                        "authentication",
                        "relationship_predicate",
                        "preconditions",
                        "forbidden_states",
                        "input_invariants",
                        "rejection",
                    )
                ],
            },
            "component_expectations": components(
                unchanged,
                ["forbidden_mutations", "rejection"],
            ),
            "evidence_assertions": [
                {
                    "type": "path_present",
                    "pointer": "/result/error/code",
                    "contract_field_refs": [ref("rejection")],
                }
            ],
            "fixture_requirements": ["OPAQUE_ID"],
        }
        replay = {
            "result_expectation": {
                "result_class": "IDEMPOTENT_REPLAY",
                "contract_field_refs": [
                    ref("concurrency"),
                    ref("idempotency"),
                    ref("recovery"),
                ],
            },
            "component_expectations": components(
                unchanged,
                ["concurrency", "forbidden_mutations", "idempotency", "recovery"],
            ),
            "evidence_assertions": [
                {
                    "type": "path_present",
                    "pointer": "/result/committed_result",
                    "contract_field_refs": [ref("idempotency"), ref("recovery")],
                }
            ],
            "fixture_requirements": ["ATTEMPT_ID", "OPAQUE_ID", "REVISION_INSTANCE"],
        }
        cases = [success, rejected, replay]
        if action_id in {"send_review_request", "resend_review_request", "revoke_review_link"}:
            cases.append({
                "result_expectation": {
                    "result_class": "STALE",
                    "contract_field_refs": [
                        ref("allowed_current_states"),
                        ref("concurrency"),
                        ref("recovery"),
                        ref("version_result"),
                    ],
                },
                "component_expectations": components(
                    unchanged,
                    ["concurrency", "forbidden_mutations", "recovery"],
                ),
                "evidence_assertions": [
                    {
                        "type": "path_present",
                        "pointer": "/result/latest_review_link_revision",
                        "contract_field_refs": [ref("concurrency"), ref("version_result")],
                    },
                    {
                        "type": "path_present",
                        "pointer": "/result/latest_review_link",
                        "contract_field_refs": [ref("object_binding"), ref("recovery")],
                    },
                ],
                "fixture_requirements": ["ATTEMPT_ID", "OPAQUE_ID", "REVISION_INSTANCE"],
            })
        mapped = {
            field_ref.rsplit("/", 1)[-1]
            for case in cases
            for field_ref in (
                case["result_expectation"]["contract_field_refs"]
                + [
                    field_ref
                    for item in case["component_expectations"] + case["evidence_assertions"]
                    for field_ref in item["contract_field_refs"]
                ]
            )
        }
        if mapped != critical:
            raise ValueError("RUNTIME_DRAFT_FIELD_MAPPING_INCOMPLETE")
        return cases

    return {
        "actions": [
            {"action_id": action["action_id"], "cases": action_cases(action)}
            for action in sorted(contract["actions"], key=lambda item: item["action_id"])
        ],
        "lifecycles": [],
    }


def _fixture_record(
    contract: dict[str, object],
    test_id: str,
    execution: dict[str, object],
) -> dict[str, object]:
    """Wrap one real local-fixture execution in the frozen transport."""
    return {"protocol_version": PROTOCOL_VERSION, "record_kind": "execution_evidence", "sequence_id": f"M6-{test_id}", "test_id": test_id,
        "product_slug": contract["source_authority"]["product_slug"],
        "authority": {"approved_revision": contract["source_authority"]["approved_revision"], "approved_digest": contract["source_authority"]["approved_definition_digest"]},
        "contract_hash": contract["semantic_contract_hash"], "adapter": {"name": "m6-dogfood-local-fixture", "version": "1.0.0"},
        "frozen_source": {"commit": "b" * 40, "tree": "c" * 40},
        **copy.deepcopy(execution)}


def materialize_dogfood(root: Path) -> dict[str, object]:
    dogfood = root / "evals" / "core-semantic-closure-v2-m6" / "dogfood"
    state = _json(dogfood / "product-definition" / "client-feedback-portal-dogfood-v2" / "state.json")
    handoff = translate_handoff_v20_to_v21(_json(dogfood / "handoff-definition.json"), build_closed_source_seed_inventory(state))
    compiled = compile_handoff_definition_v21(state, handoff)
    contract = compiled["contract"]
    if contract is None:
        raise ValueError("TRUE_SEMANTIC_GAP_FOUND")
    plan = materialize_runtime_plan(contract, runtime_draft(contract))
    planned = {
        case["test_id"]: (
            action["action_id"],
            case["result_expectation"]["result_class"],
        )
        for action in plan["actions"]
        for case in action["cases"]
    }
    records = [
        _fixture_record(
            contract,
            test_id,
            execute_fixture_scenario(contract, *planned[test_id]),
        )
        for test_id in sorted(planned)
    ]
    bundle = build_runtime_evidence_bundle(contract, plan, records)
    report = verify_runtime_v21(contract, plan, bundle)
    return {"state": state, "handoff": handoff, "contract": contract, "plan": plan, "records": records, "bundle": bundle, "report": report}


def implementation_drift_probe(result: dict[str, object]) -> dict[str, object]:
    """Mutate one copied command and keep the probe scope partial end to end."""
    case_index = {
        case["test_id"]: (
            action["action_id"],
            case["result_expectation"]["result_class"],
        )
        for action in result["plan"]["actions"]
        for case in action["cases"]
    }
    drift_records = copy.deepcopy(result["records"])
    target = next(
        record
        for record in drift_records
        if case_index[record["test_id"]] == ("create_pin", "SUCCESS")
    )
    target["command"]["actor"] = "Workspace Owner / Designer"
    drift_bundle = build_runtime_evidence_bundle(
        result["contract"],
        result["plan"],
        drift_records,
    )
    report = verify_runtime_v21(
        result["contract"],
        result["plan"],
        drift_bundle,
        verification_scope="PARTIAL_PROBE",
    )
    return {
        "probe_status": "PARTIAL_PROBE",
        "report": report,
        "mutated_test_id": target["test_id"],
    }


def write_dogfood(root: Path) -> dict[str, object]:
    result = materialize_dogfood(root)
    dogfood = root / "evals" / "core-semantic-closure-v2-m6" / "dogfood"
    _write(dogfood / "handoff-definition-v21.json", result["handoff"])
    _write(dogfood / "action-contract-v21.json", result["contract"])
    _write(dogfood / "runtime-conformance-plan.json", result["plan"])
    (dogfood / "runtime-evidence.jsonl").write_text("".join(dumps_record(record) for record in result["records"]), encoding="utf-8")
    _write(dogfood / "runtime-evidence-bundle.json", result["bundle"])
    _write(dogfood / "runtime-conformance-report.json", result["report"])
    _write(dogfood / "final-state.json", result["state"])
    _write(
        dogfood / "implementation-drift-probe.json",
        implementation_drift_probe(result),
    )
    reentry_handoff = copy.deepcopy(result["handoff"])
    reentry_handoff["actions"][0]["fields"]["actor"] = {
        "kind": "UNRESOLVED", "gap_type": "AMBIGUITY_FOUND",
        "description": "Controlled 2.1 semantic-authority probe.",
        "required_authority_class": "INTENT", "evidence_refs": ["EVD-003"],
    }
    reentry = compile_handoff_definition_v21(result["state"], reentry_handoff)
    _write(dogfood / "reentry-probe-v21.json", reentry)
    return result


__all__ = [
    "implementation_drift_probe",
    "materialize_dogfood",
    "runtime_draft",
    "translate_handoff_v20_to_v21",
    "write_dogfood",
]
