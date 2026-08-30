"""Deterministic runtime-conformance-plan/1.0 materialization and validation."""

import copy
import re

from downstream_v2.authority import sha256_json

from .contracts import validate_action_contract_v21
from .field_refs import canonical_field_ref, encode_item_id
from .identity import ACTION_CONTRACT_VERSION, RUNTIME_PLAN_VERSION, RUNTIME_PROFILE_ID
from .runtime_profile import (
    load_runtime_responsibility_profile,
    runtime_responsibility_digest,
)
from .semantic_review import (
    build_semantic_review_package_v21,
    semantic_review_completion_v21,
    validate_semantic_review_output_v21,
)
from .semantic_review.package import validate_semantic_review_package_v21


PLANNER_ID = "joewrks-product-definition/runtime-plan-v1"
PLANNER_VERSION = "core-semantic-closure-v2-m5.1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_RESULT_CLASSES = {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"}
_COMPONENTS = {
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
}
_COMPONENT_EXPECTATIONS = {"CHANGED", "UNCHANGED", "ANY"}
_ASSERTION_TYPES = {
    "path_present",
    "path_absent",
    "path_equals",
    "collection_item_field_equals",
}
_FIXTURE_REQUIREMENTS = {
    "OPAQUE_ID",
    "ATTEMPT_ID",
    "ORDERING_TIMESTAMP",
    "REVISION_INSTANCE",
}
_PLAN_KEYS = {
    "plan_schema_version",
    "planner",
    "source_contract",
    "runtime_profile",
    "review_commitments",
    "actions",
    "lifecycles",
    "coverage_summary",
    "mapping_gaps",
    "plan_hash",
}
_REVIEW_COMMITMENT_KEYS = {
    "package_hash",
    "output_hash",
    "completion",
    "reliability_status",
}


def _fail(code: str):
    raise ValueError(code)


def _runtime_field_ref(collection: str, item_id: str, field_name: str) -> str:
    return canonical_field_ref(collection, item_id, field_name)


def _runtime_item_prefix(collection: str, item_id: str) -> str:
    return f"{collection}/{encode_item_id(item_id)}/"


def _require_contract(contract: object) -> dict[str, object]:
    if (
        not isinstance(contract, dict)
        or contract.get("contract_schema_version") != ACTION_CONTRACT_VERSION
        or validate_action_contract_v21(contract)
    ):
        _fail("INVALID_ACTION_CONTRACT_V21")
    return contract


def _resolve_pointer(value: object, pointer: object) -> object:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        _fail("UNRESOLVED_EXPECTED_VALUE_SOURCE")
    current = value
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif (
            isinstance(current, list)
            and token.isdigit()
            and int(token) < len(current)
        ):
            current = current[int(token)]
        else:
            _fail("UNRESOLVED_EXPECTED_VALUE_SOURCE")
    return current


def _contract_indexes(contract: dict[str, object]):
    fields: dict[str, dict[str, object]] = {}
    raw_aliases: dict[str, set[str]] = {}
    owners: dict[tuple[str, str], dict[str, object]] = {}
    for collection, id_key in (
        ("actions", "action_id"),
        ("lifecycles", "lifecycle_id"),
    ):
        for item in contract[collection]:
            item_id = item[id_key]
            owners[(collection, item_id)] = item
            for field_name, field in item["fields"].items():
                canonical_ref = _runtime_field_ref(collection, item_id, field_name)
                fields[canonical_ref] = field
                raw_ref = f"{collection}/{item_id}/{field_name}"
                raw_aliases.setdefault(raw_ref, set()).add(canonical_ref)
    seeds = {seed["seed_key"]: seed for seed in contract["source_seed_inventory"]}
    return fields, owners, seeds, raw_aliases


def _canonical_field_ref(
    ref: str,
    *,
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
    prefix: str | None = None,
) -> str:
    candidates = set(raw_aliases.get(ref, set()))
    if ref in field_index:
        candidates.add(ref)
    if prefix is not None:
        candidates = {
            candidate for candidate in candidates if candidate.startswith(prefix)
        }
    if len(candidates) != 1:
        _fail("INVALID_CONTRACT_FIELD_REFERENCE")
    return next(iter(candidates))


def _normalize_refs(
    refs: object,
    *,
    prefix: str,
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
) -> list[str]:
    if (
        not isinstance(refs, list)
        or not refs
        or any(not isinstance(ref, str) for ref in refs)
        or len(refs) != len(set(refs))
    ):
        _fail("INVALID_CONTRACT_FIELD_REFERENCE")
    normalized = [
        _canonical_field_ref(
            ref,
            field_index=field_index,
            raw_aliases=raw_aliases,
            prefix=prefix,
        )
        for ref in refs
    ]
    if len(normalized) != len(set(normalized)) or any(
        not ref.startswith(prefix) for ref in normalized
    ):
        _fail("INVALID_CONTRACT_FIELD_REFERENCE")
    return sorted(normalized)


def _normalize_expected_source(
    source: object,
    *,
    collection: str,
    item_id: str,
    item: dict[str, object],
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
    seed_index: dict[str, dict[str, object]],
    contract_only: bool = False,
) -> dict[str, object]:
    if not isinstance(source, dict):
        _fail("PRODUCT_LITERAL_FORBIDDEN")
    source_kind = source.get("source")
    if source_kind == "CONTRACT_DERIVED":
        if set(source) != {"source", "contract_field_path", "pointer"}:
            _fail("PRODUCT_LITERAL_FORBIDDEN")
        field_path = source.get("contract_field_path")
        prefix = _runtime_item_prefix(collection, item_id)
        if not isinstance(field_path, str):
            _fail("INVALID_CONTRACT_FIELD_REFERENCE")
        canonical_path = _canonical_field_ref(
            field_path,
            field_index=field_index,
            raw_aliases=raw_aliases,
            prefix=prefix,
        )
        if (
            not canonical_path.startswith(prefix)
            or canonical_path not in field_index
        ):
            _fail("INVALID_CONTRACT_FIELD_REFERENCE")
        _resolve_pointer(field_index[canonical_path], source.get("pointer"))
        return {
            "source": "CONTRACT_DERIVED",
            "contract_field_path": canonical_path,
            "pointer": source["pointer"],
        }
    if source_kind == "VERIFICATION_BASIS" and not contract_only:
        if collection != "actions" or set(source) != {
            "source",
            "seed_ref",
            "pointer",
        }:
            _fail("INVALID_VERIFICATION_BASIS_SOURCE")
        basis = item.get("verification_basis")
        committed = {
            ref
            for values in basis.values()
            for ref in values
        } if isinstance(basis, dict) else set()
        seed_ref = source.get("seed_ref")
        if not isinstance(seed_ref, str) or seed_ref not in committed or seed_ref not in seed_index:
            _fail("INVALID_VERIFICATION_BASIS_SOURCE")
        _resolve_pointer(seed_index[seed_ref], source.get("pointer"))
        return copy.deepcopy(source)
    if source_kind in {"FIXTURE_ONLY", None} or "value" in source:
        _fail("PRODUCT_LITERAL_FORBIDDEN")
    _fail("INVALID_EXPECTED_VALUE_SOURCE")


def _normalize_components(
    components: object,
    *,
    prefix: str,
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
) -> tuple[list[dict[str, object]], set[str]]:
    if not isinstance(components, list):
        _fail("INVALID_RUNTIME_PLAN_DRAFT")
    normalized = []
    covered: set[str] = set()
    identities = set()
    for component in components:
        if not isinstance(component, dict) or set(component) != {
            "component",
            "expectation",
            "contract_field_refs",
        }:
            _fail("INVALID_RUNTIME_PLAN_DRAFT")
        name = component.get("component")
        expectation = component.get("expectation")
        if name not in _COMPONENTS or expectation not in _COMPONENT_EXPECTATIONS:
            _fail("INVALID_COMPONENT_EXPECTATION")
        refs = _normalize_refs(
            component.get("contract_field_refs"),
            prefix=prefix,
            field_index=field_index,
            raw_aliases=raw_aliases,
        )
        identity = (name, expectation, tuple(refs))
        if identity in identities:
            _fail("INVALID_COMPONENT_EXPECTATION")
        identities.add(identity)
        normalized.append(
            {
                "component": name,
                "expectation": expectation,
                "contract_field_refs": refs,
            }
        )
        if expectation != "ANY":
            covered.update(refs)
    normalized.sort(
        key=lambda item: (
            item["component"],
            item["expectation"],
            item["contract_field_refs"],
        )
    )
    return normalized, covered


def _normalize_assertions(
    assertions: object,
    *,
    collection: str,
    item_id: str,
    item: dict[str, object],
    prefix: str,
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
    seed_index: dict[str, dict[str, object]],
) -> tuple[list[dict[str, object]], set[str]]:
    if not isinstance(assertions, list):
        _fail("INVALID_RUNTIME_PLAN_DRAFT")
    normalized = []
    covered: set[str] = set()
    for assertion in assertions:
        if not isinstance(assertion, dict):
            _fail("INVALID_RUNTIME_PLAN_DRAFT")
        if "expected_value" in assertion or "value" in assertion:
            _fail("PRODUCT_LITERAL_FORBIDDEN")
        assertion_type = assertion.get("type")
        if assertion_type not in _ASSERTION_TYPES:
            _fail("INVALID_EVIDENCE_ASSERTION")
        if not isinstance(assertion.get("pointer"), str) or not assertion["pointer"].startswith("/"):
            _fail("INVALID_EVIDENCE_ASSERTION")
        refs = _normalize_refs(
            assertion.get("contract_field_refs"),
            prefix=prefix,
            field_index=field_index,
            raw_aliases=raw_aliases,
        )
        if assertion_type in {"path_present", "path_absent"}:
            if set(assertion) != {"type", "pointer", "contract_field_refs"}:
                _fail("INVALID_EVIDENCE_ASSERTION")
            normalized_assertion = {
                "type": assertion_type,
                "pointer": assertion["pointer"],
                "contract_field_refs": refs,
            }
        else:
            if set(assertion) != {
                "type",
                "pointer",
                "expected_value_source",
                "contract_field_refs",
            }:
                _fail("PRODUCT_LITERAL_FORBIDDEN")
            source = _normalize_expected_source(
                assertion.get("expected_value_source"),
                collection=collection,
                item_id=item_id,
                item=item,
                field_index=field_index,
                raw_aliases=raw_aliases,
                seed_index=seed_index,
            )
            if (
                source["source"] == "CONTRACT_DERIVED"
                and source["contract_field_path"] not in refs
            ):
                _fail("INVALID_CONTRACT_FIELD_REFERENCE")
            normalized_assertion = {
                "type": assertion_type,
                "pointer": assertion["pointer"],
                "expected_value_source": source,
                "contract_field_refs": refs,
            }
        normalized.append(normalized_assertion)
        covered.update(refs)
    normalized.sort(key=sha256_json)
    return normalized, covered


def _normalize_fixtures(requirements: object) -> list[str]:
    if (
        not isinstance(requirements, list)
        or any(not isinstance(value, str) or value not in _FIXTURE_REQUIREMENTS for value in requirements)
        or len(requirements) != len(set(requirements))
    ):
        _fail("INVALID_FIXTURE_REQUIREMENT")
    return sorted(requirements)


def _case_identity(collection: str, item_id: str, case: dict[str, object]) -> str:
    return sha256_json(
        {
            "collection": collection,
            "item_id": item_id,
            "case": case,
        }
    )[:24]


def _normalize_action_case(
    raw_case: object,
    *,
    action_id: str,
    action: dict[str, object],
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
    seed_index: dict[str, dict[str, object]],
) -> dict[str, object]:
    if not isinstance(raw_case, dict) or set(raw_case) != {
        "result_expectation",
        "component_expectations",
        "evidence_assertions",
        "fixture_requirements",
    }:
        _fail("INVALID_RUNTIME_PLAN_DRAFT")
    prefix = _runtime_item_prefix("actions", action_id)
    result = raw_case.get("result_expectation")
    if not isinstance(result, dict) or set(result) != {
        "result_class",
        "contract_field_refs",
    }:
        _fail("INVALID_RESULT_EXPECTATION")
    result_class = result.get("result_class")
    if result_class not in _RESULT_CLASSES:
        _fail("INVALID_RESULT_EXPECTATION")
    result_refs = _normalize_refs(
        result.get("contract_field_refs"),
        prefix=prefix,
        field_index=field_index,
        raw_aliases=raw_aliases,
    )
    components, component_refs = _normalize_components(
        raw_case.get("component_expectations"),
        prefix=prefix,
        field_index=field_index,
        raw_aliases=raw_aliases,
    )
    assertions, assertion_refs = _normalize_assertions(
        raw_case.get("evidence_assertions"),
        collection="actions",
        item_id=action_id,
        item=action,
        prefix=prefix,
        field_index=field_index,
        raw_aliases=raw_aliases,
        seed_index=seed_index,
    )
    case = {
        "result_expectation": {
            "result_class": result_class,
            "contract_field_refs": result_refs,
        },
        "component_expectations": components,
        "evidence_assertions": assertions,
        "fixture_requirements": _normalize_fixtures(
            raw_case.get("fixture_requirements")
        ),
        "contract_field_refs": sorted(
            set(result_refs) | component_refs | assertion_refs
        ),
    }
    identity = _case_identity("actions", action_id, case)
    return {"case_id": f"CASE-{identity}", "test_id": f"TEST-{identity}", **case}


def _normalize_lifecycle_case(
    raw_case: object,
    *,
    lifecycle_id: str,
    lifecycle: dict[str, object],
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
    seed_index: dict[str, dict[str, object]],
) -> dict[str, object]:
    if not isinstance(raw_case, dict) or set(raw_case) != {
        "transition_expectation",
        "component_expectations",
        "evidence_assertions",
        "fixture_requirements",
    }:
        _fail("INVALID_RUNTIME_PLAN_DRAFT")
    prefix = _runtime_item_prefix("lifecycles", lifecycle_id)
    transition = raw_case.get("transition_expectation")
    if not isinstance(transition, dict) or set(transition) != {
        "from_state_source",
        "to_state_source",
        "contract_field_refs",
    }:
        _fail("INVALID_TRANSITION_EXPECTATION")
    refs = _normalize_refs(
        transition.get("contract_field_refs"),
        prefix=prefix,
        field_index=field_index,
        raw_aliases=raw_aliases,
    )
    from_source = _normalize_expected_source(
        transition.get("from_state_source"),
        collection="lifecycles",
        item_id=lifecycle_id,
        item=lifecycle,
        field_index=field_index,
        raw_aliases=raw_aliases,
        seed_index=seed_index,
        contract_only=True,
    )
    to_source = _normalize_expected_source(
        transition.get("to_state_source"),
        collection="lifecycles",
        item_id=lifecycle_id,
        item=lifecycle,
        field_index=field_index,
        raw_aliases=raw_aliases,
        seed_index=seed_index,
        contract_only=True,
    )
    if (
        from_source["contract_field_path"] != f"{prefix}current_states"
        or to_source["contract_field_path"] != f"{prefix}allowed_transitions"
    ):
        _fail("INVALID_TRANSITION_EXPECTATION")
    if (
        from_source["contract_field_path"] not in refs
        or to_source["contract_field_path"] not in refs
    ):
        _fail("INVALID_CONTRACT_FIELD_REFERENCE")
    components, component_refs = _normalize_components(
        raw_case.get("component_expectations"),
        prefix=prefix,
        field_index=field_index,
        raw_aliases=raw_aliases,
    )
    assertions, assertion_refs = _normalize_assertions(
        raw_case.get("evidence_assertions"),
        collection="lifecycles",
        item_id=lifecycle_id,
        item=lifecycle,
        prefix=prefix,
        field_index=field_index,
        raw_aliases=raw_aliases,
        seed_index=seed_index,
    )
    case = {
        "transition_expectation": {
            "from_state_source": from_source,
            "to_state_source": to_source,
            "contract_field_refs": refs,
        },
        "component_expectations": components,
        "evidence_assertions": assertions,
        "fixture_requirements": _normalize_fixtures(
            raw_case.get("fixture_requirements")
        ),
        "contract_field_refs": sorted(set(refs) | component_refs | assertion_refs),
    }
    identity = _case_identity("lifecycles", lifecycle_id, case)
    return {"case_id": f"CASE-{identity}", "test_id": f"TEST-{identity}", **case}


def _review_state(
    contract: dict[str, object],
    review_package: dict[str, object] | None,
    review_output: dict[str, object] | None,
):
    expected_package = build_semantic_review_package_v21(contract)
    confirmed_paths: set[str] = set()
    if expected_package is None:
        if review_package is not None or review_output is not None:
            _fail("UNEXPECTED_SEMANTIC_REVIEW_ARTIFACT")
        completion = "NOT_REQUIRED"
        package_hash = None
        output_hash = None
    elif review_package is None:
        if review_output is not None:
            _fail("INVALID_SEMANTIC_REVIEW_OUTPUT_V21")
        completion = "PENDING"
        package_hash = None
        output_hash = None
    else:
        if (
            review_package != expected_package
            or validate_semantic_review_package_v21(review_package)
        ):
            _fail("INVALID_SEMANTIC_REVIEW_PACKAGE_V21")
        package_hash = review_package["package_hash"]
        if review_output is None:
            completion = "PENDING"
            output_hash = None
        else:
            if validate_semantic_review_output_v21(review_package, review_output):
                _fail("INVALID_SEMANTIC_REVIEW_OUTPUT_V21")
            completion = semantic_review_completion_v21(review_package, review_output)
            output_hash = sha256_json(review_output)
            obligations = {
                obligation["obligation_id"]: obligation["field_path"]
                for obligation in review_package["review_obligations"]
            }
            confirmed_paths = {
                obligations[result["obligation_id"]]
                for result in review_output["results"]
                if result["verdict"] == "CONFIRMED_INTERPRETATION"
            }
    commitments = {
        "package_hash": package_hash,
        "output_hash": output_hash,
        "completion": completion,
        "reliability_status": "NOT_MEASURED",
    }
    return commitments, confirmed_paths


def _persisted_review_state(
    contract: dict[str, object],
    raw_commitments: object,
) -> tuple[dict[str, object], set[str]]:
    """Validate persisted commitments without fabricating absent review artifacts."""
    if (
        not isinstance(raw_commitments, dict)
        or set(raw_commitments) != _REVIEW_COMMITMENT_KEYS
        or raw_commitments.get("reliability_status") != "NOT_MEASURED"
    ):
        _fail("INVALID_RUNTIME_REVIEW_COMMITMENTS")
    commitments = copy.deepcopy(raw_commitments)
    expected_package = build_semantic_review_package_v21(contract)
    if expected_package is None:
        if commitments != {
            "package_hash": None,
            "output_hash": None,
            "completion": "NOT_REQUIRED",
            "reliability_status": "NOT_MEASURED",
        }:
            _fail("INVALID_RUNTIME_REVIEW_COMMITMENTS")
        return commitments, set()

    expected_package_hash = expected_package["package_hash"]
    package_hash = commitments.get("package_hash")
    output_hash = commitments.get("output_hash")
    completion = commitments.get("completion")
    if completion == "PENDING":
        if package_hash not in {None, expected_package_hash} or output_hash is not None:
            _fail("INVALID_RUNTIME_REVIEW_COMMITMENTS")
        return commitments, set()
    if completion not in {"REVIEW_OUTPUT_RECORDED", "REENTRY_REQUIRED"}:
        _fail("INVALID_RUNTIME_REVIEW_COMMITMENTS")
    if (
        package_hash != expected_package_hash
        or not isinstance(output_hash, str)
        or _HASH.fullmatch(output_hash) is None
    ):
        _fail("INVALID_RUNTIME_REVIEW_COMMITMENTS")
    confirmed_paths = (
        {
            obligation["field_path"]
            for obligation in expected_package["review_obligations"]
        }
        if completion == "REVIEW_OUTPUT_RECORDED"
        else set()
    )
    return commitments, confirmed_paths


def _normalize_collection(
    raw_collection: object,
    *,
    collection: str,
    id_key: str,
    contract_items: list[dict[str, object]],
    field_index: dict[str, dict[str, object]],
    raw_aliases: dict[str, set[str]],
    seed_index: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    if not isinstance(raw_collection, list):
        _fail("INVALID_RUNTIME_PLAN_DRAFT")
    contract_index = {item[id_key]: item for item in contract_items}
    normalized = []
    ids = []
    for raw_item in raw_collection:
        if not isinstance(raw_item, dict) or set(raw_item) != {id_key, "cases"}:
            _fail("INVALID_RUNTIME_PLAN_DRAFT")
        item_id = raw_item.get(id_key)
        if not isinstance(item_id, str) or item_id not in contract_index:
            _fail("INVALID_RUNTIME_PLAN_DRAFT")
        ids.append(item_id)
        raw_cases = raw_item.get("cases")
        if not isinstance(raw_cases, list):
            _fail("INVALID_RUNTIME_PLAN_DRAFT")
        if collection == "actions":
            cases = [
                _normalize_action_case(
                    case,
                    action_id=item_id,
                    action=contract_index[item_id],
                    field_index=field_index,
                    raw_aliases=raw_aliases,
                    seed_index=seed_index,
                )
                for case in raw_cases
            ]
        else:
            cases = [
                _normalize_lifecycle_case(
                    case,
                    lifecycle_id=item_id,
                    lifecycle=contract_index[item_id],
                    field_index=field_index,
                    raw_aliases=raw_aliases,
                    seed_index=seed_index,
                )
                for case in raw_cases
            ]
        cases.sort(key=lambda case: case["case_id"])
        if len({case["case_id"] for case in cases}) != len(cases):
            _fail("DUPLICATE_RUNTIME_CASE")
        normalized.append(
            {
                id_key: item_id,
                "covered_contract_field_refs": sorted(
                    {
                        ref
                        for case in cases
                        for ref in case["contract_field_refs"]
                    }
                ),
                "cases": cases,
            }
        )
    if ids != sorted(set(ids)) or set(ids) != set(contract_index):
        _fail("INVALID_RUNTIME_PLAN_DRAFT")
    return normalized


def _critical_field_refs(
    contract: dict[str, object], profile: dict[str, object]
) -> list[str]:
    refs = []
    for action in contract["actions"]:
        for field_name, classification in profile["action_fields"].items():
            if classification == "RUNTIME_CRITICAL":
                refs.append(
                    _runtime_field_ref("actions", action["action_id"], field_name)
                )
    for lifecycle in contract["lifecycles"]:
        for field_name, classification in profile["lifecycle_fields"].items():
            if classification == "RUNTIME_CRITICAL":
                refs.append(
                    _runtime_field_ref(
                        "lifecycles",
                        lifecycle["lifecycle_id"],
                        field_name,
                    )
                )
    return sorted(refs)


def _review_gated_coverage(
    critical_refs: list[str],
    mapped_refs: set[str],
    field_index: dict[str, dict[str, object]],
    confirmed_paths: set[str],
) -> tuple[list[str], list[str], list[str]]:
    """Separate concrete, missing, and exact-review-blocked critical coverage."""
    review_blocked = sorted(
        ref
        for ref in critical_refs
        if ref in mapped_refs
        and field_index[ref]["derivation"]["kind"] == "REVIEW_REQUIRED"
        and ref not in confirmed_paths
    )
    covered_refs = sorted(set(critical_refs) & mapped_refs - set(review_blocked))
    missing_refs = sorted(set(critical_refs) - mapped_refs)
    return covered_refs, missing_refs, review_blocked


def materialize_runtime_plan(
    contract: dict[str, object],
    draft: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> dict[str, object]:
    """Materialize verification metadata from only a valid 2.1 semantic contract."""
    contract = _require_contract(contract)
    commitments, confirmed_paths = _review_state(
        contract,
        review_package,
        review_output,
    )
    return _materialize_runtime_plan(
        contract,
        draft,
        commitments=commitments,
        confirmed_paths=confirmed_paths,
    )


def _materialize_runtime_plan(
    contract: dict[str, object],
    draft: dict[str, object],
    *,
    commitments: dict[str, object],
    confirmed_paths: set[str],
) -> dict[str, object]:
    """Materialize from already validated review state."""
    contract = _require_contract(contract)
    if not isinstance(draft, dict) or set(draft) != {"actions", "lifecycles"}:
        _fail("INVALID_RUNTIME_PLAN_DRAFT")
    profile = load_runtime_responsibility_profile()
    field_index, _owners, seed_index, raw_aliases = _contract_indexes(contract)
    if any(path not in field_index for path in confirmed_paths):
        _fail("INVALID_CONTRACT_FIELD_REFERENCE")
    actions = _normalize_collection(
        draft["actions"],
        collection="actions",
        id_key="action_id",
        contract_items=contract["actions"],
        field_index=field_index,
        raw_aliases=raw_aliases,
        seed_index=seed_index,
    )
    lifecycles = _normalize_collection(
        draft["lifecycles"],
        collection="lifecycles",
        id_key="lifecycle_id",
        contract_items=contract["lifecycles"],
        field_index=field_index,
        raw_aliases=raw_aliases,
        seed_index=seed_index,
    )
    test_ids = [
        case["test_id"]
        for collection in (actions, lifecycles)
        for item in collection
        for case in item["cases"]
    ]
    if len(test_ids) != len(set(test_ids)):
        _fail("DUPLICATE_RUNTIME_TEST_ID")

    mapped_refs = {
        ref
        for collection in (actions, lifecycles)
        for item in collection
        for ref in item["covered_contract_field_refs"]
    }
    critical_refs = _critical_field_refs(contract, profile)
    covered_refs, missing_refs, review_blocked = _review_gated_coverage(
        critical_refs,
        mapped_refs,
        field_index,
        confirmed_paths,
    )
    for collection in (actions, lifecycles):
        for item in collection:
            item["covered_contract_field_refs"] = [
                ref
                for ref in item["covered_contract_field_refs"]
                if ref not in review_blocked
            ]
    status = (
        "COMPLETE"
        if not missing_refs
        and not review_blocked
        and commitments["completion"] != "REENTRY_REQUIRED"
        else "INCOMPLETE"
    )
    mapping_gaps = [
        {
            "code": "RUNTIME_MAPPING_GAP",
            "field_ref": ref,
            "remediation": "RUNTIME_PLAN",
        }
        for ref in missing_refs
    ]
    plan = {
        "plan_schema_version": RUNTIME_PLAN_VERSION,
        "planner": {"id": PLANNER_ID, "version": PLANNER_VERSION},
        "source_contract": {
            "contract_schema_version": ACTION_CONTRACT_VERSION,
            "semantic_contract_hash": contract["semantic_contract_hash"],
            "approved_definition_digest": contract["source_authority"][
                "approved_definition_digest"
            ],
            "product_slug": contract["source_authority"]["product_slug"],
        },
        "runtime_profile": {
            "profile_id": RUNTIME_PROFILE_ID,
            "digest": runtime_responsibility_digest(),
        },
        "review_commitments": commitments,
        "actions": actions,
        "lifecycles": lifecycles,
        "coverage_summary": {
            "status": status,
            "runtime_critical_field_refs": critical_refs,
            "covered_field_refs": covered_refs,
            "missing_field_refs": missing_refs,
            "review_blocked_field_refs": review_blocked,
        },
        "mapping_gaps": mapping_gaps,
    }
    plan["plan_hash"] = sha256_json(plan)
    return plan


def _draft_from_plan(plan: dict[str, object]) -> dict[str, object]:
    draft = {"actions": [], "lifecycles": []}
    for collection, id_key in (
        ("actions", "action_id"),
        ("lifecycles", "lifecycle_id"),
    ):
        for item in plan.get(collection, []):
            cases = []
            for case in item.get("cases", []):
                projection = copy.deepcopy(case)
                projection.pop("case_id", None)
                projection.pop("test_id", None)
                projection.pop("contract_field_refs", None)
                cases.append(projection)
            draft[collection].append({id_key: item.get(id_key), "cases": cases})
    return draft


def _validate_persisted_runtime_plan_structure(
    plan: object,
    contract: dict[str, object],
) -> list[dict[str, str]]:
    """Validate persisted shape/hash invariants without trusting artifact claims."""
    if not isinstance(plan, dict):
        return [{"path": "/", "message": "runtime plan must be an object"}]
    errors = []
    if set(plan) != _PLAN_KEYS:
        errors.append(
            {"path": "/", "message": "runtime plan has missing or extra fields"}
        )
    if plan.get("plan_schema_version") != RUNTIME_PLAN_VERSION:
        errors.append(
            {
                "path": "/plan_schema_version",
                "message": "unsupported runtime plan version",
            }
        )
    if (
        not isinstance(plan.get("plan_hash"), str)
        or _HASH.fullmatch(plan["plan_hash"]) is None
    ):
        errors.append(
            {"path": "/plan_hash", "message": "must be a lowercase SHA-256"}
        )
    try:
        contract = _require_contract(contract)
        commitments, confirmed_paths = _persisted_review_state(
            contract,
            plan.get("review_commitments"),
        )
        expected = _materialize_runtime_plan(
            contract,
            _draft_from_plan(plan),
            commitments=commitments,
            confirmed_paths=confirmed_paths,
        )
        if plan != expected:
            errors.append(
                {
                    "path": "/",
                    "message": "runtime plan does not match deterministic materialization",
                }
            )
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
        errors.append({"path": "/", "message": str(error)})
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


def validate_persisted_runtime_plan(
    plan: object,
    contract: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> list[dict[str, str]]:
    """Validate a persisted plan against its actual semantic-review artifacts."""
    structural_errors = _validate_persisted_runtime_plan_structure(plan, contract)
    if structural_errors:
        return structural_errors

    commitments = plan["review_commitments"]
    errors = []
    if commitments["package_hash"] is None:
        if review_package is not None:
            errors.append(
                {
                    "path": "/review_commitments/package_hash",
                    "message": "semantic review package is not committed by runtime plan",
                }
            )
    elif review_package is None:
        errors.append(
            {
                "path": "/review_commitments/package_hash",
                "message": "actual semantic review package is required",
            }
        )

    if commitments["output_hash"] is None:
        if review_output is not None:
            errors.append(
                {
                    "path": "/review_commitments/output_hash",
                    "message": "semantic review output is not committed by runtime plan",
                }
            )
    elif review_output is None:
        errors.append(
            {
                "path": "/review_commitments/output_hash",
                "message": "actual semantic review output is required",
            }
        )
    if errors:
        return sorted(errors, key=lambda error: (error["path"], error["message"]))

    return validate_runtime_plan(
        plan,
        contract,
        review_package=review_package,
        review_output=review_output,
    )


def validate_runtime_plan(
    plan: object,
    contract: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> list[dict[str, str]]:
    """Validate exact deterministic materialization against its supplied contract."""
    if not isinstance(plan, dict):
        return [{"path": "/", "message": "runtime plan must be an object"}]
    errors = []
    if set(plan) != _PLAN_KEYS:
        errors.append(
            {"path": "/", "message": "runtime plan has missing or extra fields"}
        )
    if plan.get("plan_schema_version") != RUNTIME_PLAN_VERSION:
        errors.append(
            {
                "path": "/plan_schema_version",
                "message": "unsupported runtime plan version",
            }
        )
    if not isinstance(plan.get("plan_hash"), str) or _HASH.fullmatch(plan["plan_hash"]) is None:
        errors.append({"path": "/plan_hash", "message": "must be a lowercase SHA-256"})
    try:
        expected = materialize_runtime_plan(
            contract,
            _draft_from_plan(plan),
            review_package=review_package,
            review_output=review_output,
        )
        if plan != expected:
            errors.append(
                {
                    "path": "/",
                    "message": "runtime plan does not match deterministic materialization",
                }
            )
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
        errors.append({"path": "/", "message": str(error)})
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


__all__ = [
    "PLANNER_ID",
    "PLANNER_VERSION",
    "RUNTIME_PLAN_VERSION",
    "RUNTIME_PROFILE_ID",
    "materialize_runtime_plan",
    "validate_persisted_runtime_plan",
    "validate_runtime_plan",
]
