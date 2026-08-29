"""Assurance-only semantic review boundary for action-conformance/2.0."""

from .build_package import build_semantic_review_package
from .output import (
    review_results_to_reentry_events,
    semantic_assurance_result,
    validate_semantic_review_output,
)


SEMANTIC_REVIEW_VERSION = "joewrks.semantic-review/2.0"
RELIABILITY_STATUS = "NOT_MEASURED"

__all__ = [
    "RELIABILITY_STATUS",
    "SEMANTIC_REVIEW_VERSION",
    "build_semantic_review_package",
    "review_results_to_reentry_events",
    "semantic_assurance_result",
    "validate_semantic_review_output",
]
