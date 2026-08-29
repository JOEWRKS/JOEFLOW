"""Structural review-output validation and read-only re-entry proposals."""

import copy
import re

from ..authority import sha256_json
from ..contracts import validate_action_contract_v2
from ..reentry import build_reentry_events
from .package import (
    RELIABILITY_STATUS,
    SEMANTIC_REVIEW_VERSION,
    build_semantic_review_package,
    validate_semantic_review_package,
)


_HASH = re.compile(r"^[0-9a-f]{64}$")
_VERDICTS = {
    "CONFIRMED_INTERPRETATION",
    "REJECTED_INTERPRETATION",
    "UPSTREAM_AUTHORITY_GAP",
}


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _output_content(output: dict[str, object]) -> dict[str, object]:
    content = copy.deepcopy(output)
    content.pop("output_hash", None)
    return content


def validate_semantic_review_output(
    review_package: dict[str, object], output: dict[str, object],
) -> list[dict[str, str]]:
    """Return deterministic structural errors; review output never changes a value."""
    errors = list(validate_semantic_review_package(review_package))

    def add(path: str, message: str):
        errors.append({"path": path, "message": message})

    if not isinstance(output, dict):
        return sorted(errors + [{"path": "/", "message": "review output must be an object"}], key=lambda item: (item["path"], item["message"]))
    required = {
        "review_schema_version", "input_package_hash", "reliability_status", "results", "output_hash",
    }
    if set(output) != required:
        add("/", "review output has missing or extra fields")
    if output.get("review_schema_version") != SEMANTIC_REVIEW_VERSION:
        add("/review_schema_version", "unsupported review schema version")
    if output.get("reliability_status") != RELIABILITY_STATUS:
        add("/reliability_status", "reliability must be NOT_MEASURED")
    if output.get("input_package_hash") != review_package.get("package_hash"):
        add("/input_package_hash", "does not bind the supplied review package")
    if not _is_hash(output.get("output_hash")):
        add("/output_hash", "must be a lowercase SHA-256")
    elif output["output_hash"] != sha256_json(_output_content(output)):
        add("/output_hash", "output hash does not match")
    expected = {
        obligation["obligation_id"]: obligation
        for obligation in review_package.get("review_obligations", [])
        if isinstance(obligation, dict) and isinstance(obligation.get("obligation_id"), str)
    }
    results = output.get("results")
    seen = []
    if not isinstance(results, list):
        add("/results", "must be an array")
        results = []
    for index, result in enumerate(results):
        path = f"/results/{index}"
        required_result = {"obligation_id", "verdict", "reviewed_value_sha256", "rationale"}
        if not isinstance(result, dict) or set(result) != required_result:
            add(path, "result has missing or extra fields")
            continue
        obligation_id = result.get("obligation_id")
        seen.append(obligation_id)
        obligation = expected.get(obligation_id)
        if obligation is None:
            add(f"{path}/obligation_id", "is not a package obligation")
        elif result.get("reviewed_value_sha256") != obligation.get("proposed_value_sha256"):
            add(f"{path}/reviewed_value_sha256", "must equal the proposed value hash")
        if result.get("verdict") not in _VERDICTS:
            add(f"{path}/verdict", "is not a permitted interpretation verdict")
        if not isinstance(result.get("rationale"), str) or not result["rationale"].strip():
            add(f"{path}/rationale", "must be meaningful")
    if len(results) != len(expected) or set(seen) != set(expected) or len(seen) != len(set(seen)):
        add("/results", "must cover every package obligation exactly once")
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


def semantic_assurance_result(
    contract: dict[str, object],
    review_package: dict[str, object] | None,
    output: dict[str, object] | None,
) -> dict[str, object]:
    """Report structural review completion without making a reliability claim."""
    expected_package = build_semantic_review_package(contract)
    if expected_package is None:
        return {"review_completion": "NOT_REQUIRED"}
    pending = {"review_completion": "PENDING", "reliability_status": RELIABILITY_STATUS}
    if review_package != expected_package or output is None:
        return pending
    if validate_semantic_review_output(review_package, output):
        return pending
    verdicts = {result["verdict"] for result in output["results"]}
    if verdicts - {"CONFIRMED_INTERPRETATION"}:
        return {"review_completion": "REENTRY_REQUIRED", "reliability_status": RELIABILITY_STATUS}
    return {"review_completion": "REVIEW_OUTPUT_RECORDED", "reliability_status": RELIABILITY_STATUS}


def _reentry_definition(contract: dict[str, object]) -> dict[str, object]:
    """Provide Task 4 only the immutable owner identities it requires."""
    return {
        "actions": [
            {
                "action_id": item["action_id"],
                "authority_scope_refs": list(item["authority_scope_refs"]),
            }
            for item in contract["actions"]
        ],
        "lifecycles": [
            {
                "lifecycle_id": item["lifecycle_id"],
                "authority_scope_refs": list(item["authority_scope_refs"]),
            }
            for item in contract["lifecycles"]
        ],
    }


def review_results_to_reentry_events(
    contract: dict[str, object],
    review_package: dict[str, object],
    output: dict[str, object],
) -> list[dict]:
    """Convert valid rejected/gap results into deterministic read-only re-entry events."""
    if validate_action_contract_v2(contract):
        raise ValueError("INVALID_ACTION_CONTRACT_V2")
    expected_package = build_semantic_review_package(contract)
    if expected_package is None or review_package != expected_package:
        raise ValueError("INVALID_SEMANTIC_REVIEW_PACKAGE")
    if validate_semantic_review_output(review_package, output):
        raise ValueError("INVALID_SEMANTIC_REVIEW_OUTPUT")
    obligations = {item["obligation_id"]: item for item in review_package["review_obligations"]}
    gaps = []
    for result in output["results"]:
        if result["verdict"] == "CONFIRMED_INTERPRETATION":
            continue
        obligation = obligations[result["obligation_id"]]
        collection, item_id, _field_name = obligation["field_path"].split("/", 2)
        item = next(
            item for item in contract[collection]
            if item["action_id" if collection == "actions" else "lifecycle_id"] == item_id
        )
        gaps.append({
            "field_path": obligation["field_path"],
            "gap_type": (
                "CONTRACT_CONFLICT"
                if result["verdict"] == "REJECTED_INTERPRETATION"
                else "AMBIGUITY_FOUND"
            ),
            "reason": f"Semantic Review recorded: {result['rationale'].strip()}",
            "required_authority_class": "PREFERENCE",
            "authority_scope_refs": list(item["authority_scope_refs"]),
            "evidence_refs": list(obligation["source_seed_refs"]),
        })
    return build_reentry_events(
        source_authority=contract["source_authority"],
        definition=_reentry_definition(contract),
        gaps=gaps,
        source_contract_hash=contract["semantic_contract_hash"],
    )
