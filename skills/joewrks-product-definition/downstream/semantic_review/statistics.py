"""Exact-rational nominal reliability statistics for semantic review."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Any


APPROVED = "APPROVED"
REJECTED = "REJECTED_CANDIDATE"
CANDIDATE_CLASSES = (APPROVED, REJECTED)
ERROR_VERDICTS = {"RUBRIC_ERROR", "INPUT_PACKAGE_ERROR"}


@dataclass(frozen=True)
class MetricResult:
    """One exact metric or one stable null reason, never both."""

    value: Fraction | None
    null_reason: str | None = None

    def __post_init__(self) -> None:
        if (self.value is None) == (self.null_reason is None):
            raise ValueError("exactly one of value or null_reason is required")
        if self.value is not None and not isinstance(self.value, Fraction):
            raise TypeError("metric values must be fractions.Fraction")


class _InputFailure(ValueError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _normalize_run(run: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if isinstance(run, Mapping):
        pairs = list(run.items())
    elif isinstance(run, Sequence) and not isinstance(run, (str, bytes, bytearray)):
        items = list(run)
        if not items:
            return (), ()
        if all(isinstance(item, str) for item in items):
            pairs = [(f"{index:012d}", value) for index, value in enumerate(items)]
        elif all(isinstance(item, Mapping) for item in items):
            pairs = [
                (item.get("review_identity"), item.get("verdict")) for item in items
            ]
        elif all(
            isinstance(item, Sequence)
            and not isinstance(item, (str, bytes, bytearray))
            and len(item) == 2
            for item in items
        ):
            pairs = [(item[0], item[1]) for item in items]
        else:
            raise _InputFailure("IDENTITY_SET_MISMATCH")
    else:
        raise _InputFailure("IDENTITY_SET_MISMATCH")

    identities = [pair[0] for pair in pairs]
    if (
        not all(isinstance(identity, str) and identity for identity in identities)
        or len(identities) != len(set(identities))
    ):
        raise _InputFailure("IDENTITY_SET_MISMATCH")
    verdicts = [pair[1] for pair in pairs]
    if any(verdict in ERROR_VERDICTS for verdict in verdicts):
        raise _InputFailure("UNEXPECTED_ERROR_VERDICT")
    if any(verdict not in CANDIDATE_CLASSES for verdict in verdicts):
        raise _InputFailure("UNKNOWN_VERDICT")
    ordered = sorted(zip(identities, verdicts), key=lambda item: item[0])
    return tuple(item[0] for item in ordered), tuple(item[1] for item in ordered)


def _aligned_runs(
    runs: list[Any], *, minimum_runs: int
) -> tuple[tuple[str, ...], list[tuple[str, ...]]]:
    if len(runs) < minimum_runs:
        raise _InputFailure("INSUFFICIENT_INDEPENDENT_RUNS")
    normalized = [_normalize_run(run) for run in runs]
    identities = normalized[0][0]
    if not identities:
        raise _InputFailure("ZERO_ALIGNED_IDENTITIES")
    if any(item[0] != identities for item in normalized[1:]):
        raise _InputFailure("IDENTITY_SET_MISMATCH")
    return identities, [item[1] for item in normalized]


def _null(error: _InputFailure) -> MetricResult:
    return MetricResult(None, error.reason)


def cohen_kappa(left: list[Any], right: list[Any]) -> MetricResult:
    """Pairwise unweighted nominal Cohen kappa with pair-specific marginals."""

    try:
        _, runs = _aligned_runs([left, right], minimum_runs=2)
    except _InputFailure as error:
        return _null(error)
    left_values, right_values = runs
    count = len(left_values)
    observed = Fraction(
        sum(a == b for a, b in zip(left_values, right_values)), count
    )
    expected = sum(
        Fraction(left_values.count(category), count)
        * Fraction(right_values.count(category), count)
        for category in CANDIDATE_CLASSES
    )
    denominator = 1 - expected
    if denominator == 0:
        return MetricResult(None, "ALL_ONE_CLASS_CHANCE_DENOMINATOR")
    return MetricResult((observed - expected) / denominator)


def pairwise_cohen_kappas(runs: list[list[Any]]) -> list[MetricResult]:
    """Return Cohen kappa for every unordered pair in reviewer order."""

    try:
        _, aligned = _aligned_runs(runs, minimum_runs=3)
    except _InputFailure as error:
        return [MetricResult(None, error.reason)]
    return [cohen_kappa(list(left), list(right)) for left, right in combinations(aligned, 2)]


def _multi_rater_inputs(
    runs: list[list[Any]],
) -> tuple[list[tuple[str, ...]], int, int]:
    _, aligned = _aligned_runs(runs, minimum_runs=3)
    return aligned, len(aligned), len(aligned[0])


def _pair_agreement(aligned: list[tuple[str, ...]], m: int, count: int) -> Fraction:
    total = Fraction(0, 1)
    for index in range(count):
        category_counts = Counter(run[index] for run in aligned)
        total += Fraction(
            sum(value * (value - 1) for value in category_counts.values()),
            m * (m - 1),
        )
    return total / count


def _pooled_shares(
    aligned: list[tuple[str, ...]], m: int, count: int
) -> dict[str, Fraction]:
    pooled = Counter(value for run in aligned for value in run)
    return {
        category: Fraction(pooled[category], count * m)
        for category in CANDIDATE_CLASSES
    }


def fleiss_kappa(runs: list[list[Any]]) -> MetricResult:
    """Multi-rater unweighted nominal Fleiss kappa."""

    try:
        aligned, m, count = _multi_rater_inputs(runs)
    except _InputFailure as error:
        return _null(error)
    observed = _pair_agreement(aligned, m, count)
    shares = _pooled_shares(aligned, m, count)
    expected = sum((share * share for share in shares.values()), Fraction(0, 1))
    denominator = 1 - expected
    if denominator == 0:
        return MetricResult(None, "ALL_ONE_CLASS_CHANCE_DENOMINATOR")
    return MetricResult((observed - expected) / denominator)


def gwet_ac1(runs: list[list[Any]]) -> MetricResult:
    """The frozen multi-rater unweighted nominal two-category Gwet AC1."""

    try:
        aligned, m, count = _multi_rater_inputs(runs)
    except _InputFailure as error:
        return _null(error)
    observed = _pair_agreement(aligned, m, count)
    shares = _pooled_shares(aligned, m, count)
    expected = sum(
        (share * (1 - share) for share in shares.values()), Fraction(0, 1)
    ) / (len(CANDIDATE_CLASSES) - 1)
    denominator = 1 - expected
    if denominator == 0:
        return MetricResult(None, "AC1_CHANCE_DENOMINATOR")
    return MetricResult((observed - expected) / denominator)


def minority_class_agreement(runs: list[list[Any]]) -> MetricResult:
    """Exact unanimity among identities where the pooled minority is observed."""

    try:
        aligned, m, count = _multi_rater_inputs(runs)
    except _InputFailure as error:
        return _null(error)
    pooled = Counter(value for run in aligned for value in run)
    if pooled[APPROVED] == pooled[REJECTED]:
        return MetricResult(None, "NO_UNIQUE_MINORITY")
    minority = min(CANDIDATE_CLASSES, key=lambda category: pooled[category])
    if pooled[minority] == 0:
        return MetricResult(None, "MINORITY_CLASS_UNOBSERVED")
    detected = [
        index
        for index in range(count)
        if any(run[index] == minority for run in aligned)
    ]
    if not detected:
        return MetricResult(None, "MINORITY_CLASS_UNOBSERVED")
    unanimous = sum(
        all(run[index] == minority for run in aligned) for index in detected
    )
    return MetricResult(Fraction(unanimous, len(detected)))


def is_balanced(
    runs: list[list[Any]], floor: Fraction = Fraction(1, 20)
) -> bool:
    """Classify balance using exact per-reviewer category shares."""

    if not isinstance(floor, Fraction):
        raise TypeError("balance floor must be fractions.Fraction")
    try:
        _, aligned = _aligned_runs(runs, minimum_runs=3)
    except _InputFailure:
        return False
    count = len(aligned[0])
    return all(
        Fraction(run.count(category), count) >= floor
        for run in aligned
        for category in CANDIDATE_CLASSES
    )


def format_metric(value: Fraction, places: int = 6) -> str:
    """Render exact round-half-even decimal text without floating point."""

    if not isinstance(value, Fraction):
        raise TypeError("metric display requires fractions.Fraction")
    if not isinstance(places, int) or isinstance(places, bool) or places < 0:
        raise ValueError("places must be a non-negative integer")
    negative = value < 0
    absolute = abs(value)
    scale = 10**places
    quotient, remainder = divmod(absolute.numerator * scale, absolute.denominator)
    doubled = remainder * 2
    if doubled > absolute.denominator or (
        doubled == absolute.denominator and quotient % 2 == 1
    ):
        quotient += 1
    sign = "-" if negative and quotient else ""
    if places == 0:
        return f"{sign}{quotient}"
    whole, fractional = divmod(quotient, scale)
    return f"{sign}{whole}.{fractional:0{places}d}"


def serialize_metric(result: MetricResult) -> dict[str, Any]:
    """Serialize exact reduced fractions and diagnostic display separately."""

    if result.value is None:
        return {"value": None, "display": None, "null_reason": result.null_reason}
    return {
        "value": {
            "numerator": result.value.numerator,
            "denominator": result.value.denominator,
        },
        "display": format_metric(result.value),
        "null_reason": None,
    }
