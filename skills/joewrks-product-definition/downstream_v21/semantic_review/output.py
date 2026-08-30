"""Read-only semantic-review/2.1 output validation and completion."""

import copy
import re

from downstream_v2.authority import sha256_json
from downstream_v2.reentry import build_reentry_events

from ..contracts import validate_action_contract_v21
from ..derivation import SemanticAuthorityGap
from ..gaps import semantic_gap_record
from ..identity import SEMANTIC_REVIEW_VERSION
from ..responsibility import load_responsibility_profile_v21
from .package import (
    RELIABILITY_STATUS,
    build_semantic_review_package_v21,
    validate_semantic_review_package_v21,
)


_HASH = re.compile(r"^[0-9a-f]{64}$")
_VERDICTS = {
    "CONFIRMED_INTERPRETATION",
    "REJECTED_INTERPRETATION",
    "UPSTREAM_AUTHORITY_GAP",
}
_OUTPUT_KEYS = {
    "review_schema_version",
    "input_package_hash",
    "reliability_status",
    "results",
    "output_hash",
}
_RESULT_KEYS = {
    "obligation_id",
    "verdict",
    "reviewed_value_sha256",
    "rationale",
}


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _hash(value: object) -> str | None:
    try:
        return sha256_json(value)
    except (TypeError, ValueError, RecursionError):
        return None


def _output_content(output: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in output.items() if key != "output_hash"}


def validate_semantic_review_output_v21(
    package: dict[str, object],
    output: object,
) -> list[dict[str, str]]:
    """Validate exact package binding without permitting value replacement."""
    errors = list(validate_semantic_review_package_v21(package))

    def add(path: str, message: str):
        errors.append({"path": path, "message": message})

    if not isinstance(output, dict):
        return sorted(
            errors + [{"path": "/", "message": "review output must be an object"}],
            key=lambda error: (error["path"], error["message"]),
        )
    if set(output) != _OUTPUT_KEYS:
        add("/", "review output has missing or extra fields")
    if output.get("review_schema_version") != SEMANTIC_REVIEW_VERSION:
        add("/review_schema_version", "unsupported review schema version")
    if output.get("reliability_status") != RELIABILITY_STATUS:
        add("/reliability_status", "reliability must be NOT_MEASURED")
    package_hash = package.get("package_hash") if isinstance(package, dict) else None
    if output.get("input_package_hash") != package_hash:
        add("/input_package_hash", "does not bind the supplied review package")
    if not _is_hash(output.get("output_hash")):
        add("/output_hash", "must be a lowercase SHA-256")
    else:
        output_hash = _hash(_output_content(output))
        if output_hash is None:
            add("/output_hash", "output is not canonical JSON")
        elif output["output_hash"] != output_hash:
            add("/output_hash", "output hash does not match")

    raw_obligations = (
        package.get("review_obligations") if isinstance(package, dict) else []
    )
    if not isinstance(raw_obligations, list):
        raw_obligations = []
    expected = {
        obligation["obligation_id"]: obligation
        for obligation in raw_obligations
        if isinstance(obligation, dict)
        and isinstance(obligation.get("obligation_id"), str)
    }
    results = output.get("results")
    seen: list[str] = []
    if not isinstance(results, list):
        add("/results", "must be an array")
        results = []
    for index, result in enumerate(results):
        path = f"/results/{index}"
        if not isinstance(result, dict) or set(result) != _RESULT_KEYS:
            add(path, "result has missing or extra fields")
            continue
        obligation_id = result.get("obligation_id")
        if not isinstance(obligation_id, str):
            add(f"{path}/obligation_id", "must be a string package obligation")
            continue
        seen.append(obligation_id)
        obligation = expected.get(obligation_id)
        if obligation is None:
            add(f"{path}/obligation_id", "is not a package obligation")
        elif result.get("reviewed_value_sha256") != obligation.get(
            "proposed_value_sha256"
        ):
            add(
                f"{path}/reviewed_value_sha256",
                "must equal the proposed value hash",
            )
        verdict = result.get("verdict")
        if not isinstance(verdict, str) or verdict not in _VERDICTS:
            add(f"{path}/verdict", "is not a permitted interpretation verdict")
        rationale = result.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            add(f"{path}/rationale", "must be meaningful")
    if (
        len(results) != len(expected)
        or set(seen) != set(expected)
        or len(seen) != len(set(seen))
    ):
        add("/results", "must cover every package obligation exactly once")
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


def semantic_review_completion_v21(
    package: dict[str, object] | None,
    output: dict[str, object] | None,
) -> str:
    """Return structural review completion, never a reliability claim."""
    if package is None:
        return "NOT_REQUIRED" if output is None else "PENDING"
    if validate_semantic_review_package_v21(package) or output is None:
        return "PENDING"
    if validate_semantic_review_output_v21(package, output):
        return "PENDING"
    verdicts = {result["verdict"] for result in output["results"]}
    if verdicts - {"CONFIRMED_INTERPRETATION"}:
        return "REENTRY_REQUIRED"
    return "REVIEW_OUTPUT_RECORDED"


def _reentry_definition(contract: dict[str, object]) -> dict[str, object]:
    """Project only immutable owner identities needed by the event builder."""
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


def review_results_to_reentry_events_v21(
    contract: dict[str, object],
    package: dict[str, object],
    output: dict[str, object],
) -> list[dict[str, object]]:
    """Route valid non-confirmed results to read-only affected-scope events."""
    if validate_action_contract_v21(contract):
        raise ValueError("INVALID_ACTION_CONTRACT_V21")
    expected_package = build_semantic_review_package_v21(contract)
    if expected_package is None or package != expected_package:
        raise ValueError("INVALID_SEMANTIC_REVIEW_PACKAGE_V21")
    if validate_semantic_review_output_v21(package, output):
        raise ValueError("INVALID_SEMANTIC_REVIEW_OUTPUT_V21")

    obligations = {
        item["obligation_id"]: item for item in package["review_obligations"]
    }
    profile = load_responsibility_profile_v21()
    gaps = []
    for result in output["results"]:
        if result["verdict"] == "CONFIRMED_INTERPRETATION":
            continue
        obligation = obligations[result["obligation_id"]]
        collection, item_id, field_name = obligation["field_path"].split("/", 2)
        id_key = "action_id" if collection == "actions" else "lifecycle_id"
        item = next(
            item for item in contract[collection] if item[id_key] == item_id
        )
        policy_group = (
            "action_fields" if collection == "actions" else "lifecycle_fields"
        )
        policy = profile[policy_group][field_name]
        gap_type = (
            "CONTRACT_CONFLICT"
            if result["verdict"] == "REJECTED_INTERPRETATION"
            else "AMBIGUITY_FOUND"
        )
        detail = {
            "kind": "UNRESOLVED",
            "gap_type": gap_type,
            "description": f"Semantic Review recorded: {result['rationale'].strip()}",
            "required_authority_class": policy["required_authority_class"],
            "evidence_refs": list(obligation["source_seed_refs"]),
        }
        gaps.append(
            semantic_gap_record(
                field_path=obligation["field_path"],
                spec={"source_seed_refs": list(obligation["source_seed_refs"])},
                error=SemanticAuthorityGap(detail),
                policy=policy,
                authority_scope_refs=list(item["authority_scope_refs"]),
            )
        )
    return build_reentry_events(
        source_authority=copy.deepcopy(contract["source_authority"]),
        definition=_reentry_definition(contract),
        gaps=gaps,
        source_contract_hash=contract["semantic_contract_hash"],
    )


__all__ = [
    "review_results_to_reentry_events_v21",
    "semantic_review_completion_v21",
    "validate_semantic_review_output_v21",
]
