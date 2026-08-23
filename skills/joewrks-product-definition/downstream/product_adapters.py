"""Product-specific canonical clause mappings for the frozen v0.4.1 probes."""

from __future__ import annotations

import copy
from typing import Any

from .provenance import find_object_pointer


REGRESSION_SLICE_VERSION = "joewrks.downstream.regression-slice/1.0"
COMPONENTS = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)
NO_OP = {component: "UNCHANGED" for component in COMPONENTS}
SUCCESS_DEFAULT = {
    "authoritative_state": "CHANGED",
    "revision": "ANY",
    "history": "ANY",
    "business_side_effects": "ANY",
    "delivery_effects": "ANY",
}


def _review(value: Any, source_refs: list[int], explanation: str) -> dict[str, Any]:
    return {
        "value": value,
        "source_refs": source_refs,
        "derivation": {
            "kind": "REVIEW_REQUIRED",
            "explanation": explanation,
        },
    }


def _explicit_expectation(result_class: str, configured: dict[str, Any]) -> dict[str, Any]:
    defaults = SUCCESS_DEFAULT if result_class == "SUCCESS" else NO_OP
    expectation = {**defaults, **copy.deepcopy(configured)}
    return expectation


def _regression_action(action: dict[str, Any]) -> dict[str, Any]:
    """Make every evaluator semantic explicit without claiming machine derivation."""

    compiled = copy.deepcopy(action)
    all_refs = list(range(len(compiled["sources"])))
    default_result = compiled.pop("default_result", "SUCCESS")
    required_results = set(compiled.pop("required_results", []))
    raw_invariants = compiled.pop("input_invariants", [])
    invariant_refs = sorted(
        {
            ref
            for invariant in raw_invariants
            if isinstance(invariant, dict)
            for ref in invariant.get("source_refs", [])
        }
    )
    invariants = [
        {key: value for key, value in invariant.items() if key != "source_refs"}
        for invariant in raw_invariants
    ]
    raw_expectations = compiled.pop("result_expectations", {})
    result_classes = set(raw_expectations) | required_results | {default_result}
    expectations = {
        result_class: _explicit_expectation(
            result_class,
            raw_expectations.get(result_class, {}),
        )
        for result_class in sorted(result_classes)
    }
    obligations = compiled.pop(
        "test_obligations",
        [f"frozen-regression:{compiled['action_id']}"],
    )
    compiled["default_result"] = _review(
        default_result,
        all_refs,
        "The harness result-class enum is a reviewed interpretation of the cited frozen product clauses.",
    )
    compiled["input_invariants"] = _review(
        invariants,
        invariant_refs or all_refs,
        "The input constraint list requires interpretation of the cited canonical clauses.",
    )
    compiled["result_expectations"] = _review(
        expectations,
        all_refs,
        "The result class and five-component change table are reviewed evaluator expectations, not exact canonical values.",
    )
    compiled["test_obligations"] = _review(
        obligations,
        all_refs,
        "Known-defect regression scope is a reviewed mapping from the cited clauses to executable evaluator coverage.",
    )
    return compiled


def _source(state: dict[str, Any], object_id: str, field: str) -> dict[str, str]:
    return {"object_id": object_id, "pointer": f"{find_object_pointer(state, object_id)}/{field}"}


def replication_a_definition(state: dict[str, Any]) -> dict[str, Any]:
    definition = {
        "contract_schema_version": REGRESSION_SLICE_VERSION,
        "product_slug": "studio-booking-dogfood",
        "actions": [
            {
                "action_id": "confirm_booking",
                "sources": [
                    _source(state, "SCR-001", "major_actions"),
                    _source(state, "REQ-001", "behavior"),
                    _source(state, "RULE-001", "rule"),
                    _source(state, "STATE-001", "meaning"),
                    _source(state, "AC-001", "criterion"),
                    _source(state, "AC-002", "criterion"),
                ],
                "default_result": "SUCCESS",
                "input_invariants": [],
                "result_expectations": {
                    "SUCCESS": {
                        "authoritative_state": "CHANGED",
                        "revision": "CHANGED",
                        "history": "ANY",
                        "business_side_effects": "UNCHANGED",
                        "delivery_effects": "ANY",
                    }
                },
                "test_obligations": ["ui-to-domain-trace", "atomic-booking-creation"],
            }
        ],
        "lifecycles": [],
    }
    definition["actions"] = [_regression_action(action) for action in definition["actions"]]
    return definition


def replication_b_definition(state: dict[str, Any]) -> dict[str, Any]:
    stale_sources = [
        _source(state, "RULE-133", "statement"),
        _source(state, "RULE-134", "statement"),
    ]
    adjustment_sources = [
        _source(state, "RULE-148", "statement"),
        _source(state, "RULE-149", "statement"),
        _source(state, "RULE-153", "statement"),
        _source(state, "RULE-155", "statement"),
    ]
    money_sources = [
        _source(state, "RULE-010", "statement"),
        _source(state, "RULE-015", "statement"),
    ]
    actions = [
        {
            "action_id": "create_adjustment",
            "sources": adjustment_sources[:2],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                }
            },
        },
        {
            "action_id": "fail_adjustment",
            "sources": adjustment_sources,
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "CHANGED",
                }
            },
        },
        {
            "action_id": "resolve_adjustment_executed",
            "sources": adjustment_sources + stale_sources,
            "required_results": ["REJECTED"],
            "input_invariants": [
                {"type": "required", "pointer": "/actualAmountKrw", "source_refs": [3]},
                {"type": "required", "pointer": "/actualDate", "source_refs": [3]},
                {"type": "required", "pointer": "/externalReference", "source_refs": [3]},
            ],
        },
        {
            "action_id": "create_adjustment_after_rejection",
            "sources": adjustment_sources[:2] + stale_sources,
            "required_results": ["REJECTED"],
        },
        {
            "action_id": "update_draft_money",
            "sources": money_sources,
            "required_results": ["REJECTED"],
            "input_invariants": [
                {"type": "finite_number", "pointer": "/originalAmount", "source_refs": [0, 1]},
                {"type": "finite_number", "pointer": "/krwAmount", "source_refs": [0, 1]},
            ],
        },
        {
            "action_id": "submit_invalid_money",
            "sources": money_sources,
            "default_result": "REJECTED",
        },
        {
            "action_id": "admin_stale",
            "sources": stale_sources,
            "default_result": "STALE",
            "result_expectations": {
                "STALE": {
                    "assertions": [
                        {"type": "path_present", "pointer": "/result/latestValues/user.active"}
                    ]
                }
            },
        },
        {
            "action_id": "timeline_query",
            "sources": [
                _source(state, "RULE-130", "statement"),
                _source(state, "RULE-138", "statement"),
            ],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "UNCHANGED",
                    "revision": "UNCHANGED",
                    "history": "UNCHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                    "assertions": [
                        {
                            "type": "collection_item_field_equals",
                            "pointer": "/result/query",
                            "match_field": "action",
                            "match_value": "APPROVE_CLAIM",
                            "field": "businessStatus",
                            "value": "Payment pending",
                        }
                    ],
                }
            },
        },
        {
            "action_id": "complete_payment_terminal",
            "sources": [
                _source(state, "RULE-075", "statement"),
                _source(state, "RULE-077", "statement"),
            ],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "CHANGED",
                    "assertions": [
                        {
                            "type": "path_equals",
                            "pointer": "/after/authoritative_state/claims/clm-scheduled/payment/overdue",
                            "value": False,
                        }
                    ],
                }
            },
        },
        {
            "action_id": "terminal_reminder_retry",
            "sources": [
                _source(state, "RULE-172", "statement"),
                _source(state, "RULE-173", "statement"),
            ],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "UNCHANGED",
                    "revision": "UNCHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                }
            },
        },
        {
            "action_id": "issue_file_access",
            "sources": [
                _source(state, "RULE-165", "statement"),
                _source(state, "RULE-169", "statement"),
            ],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "UNCHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                }
            },
        },
        {
            "action_id": "download_after_authority_loss",
            "sources": [
                _source(state, "RULE-138", "statement"),
                _source(state, "RULE-169", "statement"),
            ],
            "default_result": "REJECTED",
            "result_expectations": {
                "REJECTED": {
                    "authoritative_state": "UNCHANGED",
                    "revision": "UNCHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                }
            },
        },
        {
            "action_id": "update_draft",
            "sources": stale_sources + [_source(state, "RULE-136", "statement")],
            "required_results": ["STALE", "IDEMPOTENT_REPLAY"],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "UNCHANGED",
                }
            },
        },
        {
            "action_id": "reassign_manager",
            "sources": [
                _source(state, "RULE-193", "statement"),
                _source(state, "RULE-196", "statement"),
            ],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "CHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "UNCHANGED",
                    "delivery_effects": "CHANGED",
                }
            },
        },
        {
            "action_id": "delivery_failure_after_commit",
            "sources": [
                _source(state, "RULE-194", "statement"),
                _source(state, "RULE-196", "statement"),
            ],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "UNCHANGED",
                    "revision": "UNCHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "CHANGED",
                    "delivery_effects": "CHANGED",
                }
            },
        },
        {
            "action_id": "manual_delivery_retry",
            "sources": [
                _source(state, "RULE-194", "statement"),
                _source(state, "RULE-195", "statement"),
                _source(state, "RULE-196", "statement"),
            ],
            "result_expectations": {
                "SUCCESS": {
                    "authoritative_state": "UNCHANGED",
                    "revision": "CHANGED",
                    "history": "CHANGED",
                    "business_side_effects": "CHANGED",
                    "delivery_effects": "CHANGED",
                }
            },
        },
    ]
    return {
        "contract_schema_version": REGRESSION_SLICE_VERSION,
        "product_slug": "expense-reimbursement-dogfood",
        "actions": [_regression_action(action) for action in actions],
        "lifecycles": [],
    }
