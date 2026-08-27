"""Frozen golden-case scoring for semantic-review calibration."""

from __future__ import annotations

from fractions import Fraction
from typing import Any


class GoldenError(ValueError):
    """A deterministic golden-suite identity or answer failure."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


def _answer_items(answers: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    return answers["answers"] if isinstance(answers, dict) else answers


def evaluate_goldens(
    outputs: list[dict[str, Any]],
    answers: dict[str, Any] | list[dict[str, Any]],
) -> dict[str, Any]:
    """Score exact verdict/rationale pairs without exposing answers to reviewers."""

    answer_items = _answer_items(answers)
    expected = {item["case_id"]: item for item in answer_items}
    observed = {item["case_id"]: item for item in outputs}
    frozen_ids = {f"G-{index:03d}" for index in range(1, 16)}
    if (
        len(answer_items) != 15
        or len(expected) != 15
        or set(expected) != frozen_ids
        or len(observed) != len(outputs)
        or set(observed) != set(expected)
    ):
        raise GoldenError("GOLDEN_IDENTITY_SET_MISMATCH")
    verdict_hits = sum(
        observed[key]["verdict"] == expected[key]["verdict"] for key in expected
    )
    rationale_hits = sum(
        observed[key]["rationale_code"] == expected[key]["rationale_code"]
        for key in expected
    )
    unexpected_rubric = sum(
        item["verdict"] == "RUBRIC_ERROR"
        and expected[item["case_id"]]["verdict"] != "RUBRIC_ERROR"
        for item in outputs
    )
    unexpected_package = sum(
        item["verdict"] == "INPUT_PACKAGE_ERROR"
        and expected[item["case_id"]]["verdict"] != "INPUT_PACKAGE_ERROR"
        for item in outputs
    )
    count = len(expected)
    return {
        "case_count": count,
        "verdict_hits": verdict_hits,
        "rationale_code_hits": rationale_hits,
        "verdict_accuracy": Fraction(verdict_hits, count),
        "rationale_code_accuracy": Fraction(rationale_hits, count),
        "unexpected_rubric_error_count": unexpected_rubric,
        "unexpected_input_package_error_count": unexpected_package,
    }
