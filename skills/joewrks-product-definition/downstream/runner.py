"""Sequence evaluation using executable contracts as semantic authority."""

from __future__ import annotations

from typing import Any

from .verifier import VerificationError, verify_execution


SEQUENCE_CLASSES = {
    "valid_happy_transition",
    "wrong_role",
    "wrong_object_revision",
    "authority_lost_after_initial_access",
    "stale_expected_version",
    "validation_rejection",
    "repeated_same_idempotency_key",
    "same_key_replay_after_later_state_changes",
    "reversal_before_boundary",
    "reversal_at_boundary",
    "reversal_after_boundary",
    "superseded_transition_sentinel",
    "delivery_failure_after_successful_business_commit",
    "manual_delivery_retry",
    "stop_after_terminal_state",
    "destructive_action_without_confirmation_reason",
    "rejected_command_followed_by_related_second_command",
    "historical_projection_after_later_state_change",
}


def validate_sequence(sequence: dict[str, Any]) -> None:
    if not isinstance(sequence.get("sequence_id"), str) or not sequence["sequence_id"]:
        raise ValueError("sequence_id is required")
    sequence_class = sequence.get("sequence_class")
    if sequence_class not in SEQUENCE_CLASSES:
        raise ValueError(f"unsupported sequence class: {sequence_class}")
    if not isinstance(sequence.get("steps"), list):
        raise ValueError("sequence steps must be an array")


def evaluate_sequence(
    bundle: dict[str, Any],
    sequence: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    if "sequence_class" in sequence:
        validate_sequence(sequence)
    steps = sequence.get("steps")
    if not isinstance(steps, list) or len(steps) != len(records):
        raise VerificationError("sequence steps and evidence records must have equal length")
    actions = {item.get("action_id"): item for item in bundle.get("actions", [])}
    reports = []
    for index, (step, record) in enumerate(zip(steps, records, strict=True)):
        action_id = step.get("action_id")
        action = actions.get(action_id)
        if action is None:
            raise VerificationError(f"unknown action contract: {action_id}")
        report = verify_execution(action, record, expected_result=step.get("expected_result"))
        report["step_index"] = index
        report["test_id"] = record.get("test_id")
        reports.append(report)
    failures = [
        {"step_index": report["step_index"], "action_id": report["action_id"], "failures": report["failures"]}
        for report in reports
        if not report["conformant"]
    ]
    return {
        "sequence_id": sequence.get("sequence_id"),
        "conformant": not failures,
        "steps": reports,
        "failures": failures,
    }
