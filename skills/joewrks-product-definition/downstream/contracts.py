"""Compilation of structurally enforced, provenance-bound downstream contracts."""

from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .provenance import (
    ProvenanceError,
    make_source_ref,
    resolve_pointer,
    sha256_json,
    verify_source_ref,
)
from .schema_validation import SchemaValidationError, validate_instance


COMPILER_ID = "joewrks-product-definition/downstream"
COMPILER_VERSION = "0.4.1.1"
FULL_CONTRACT_VERSION = "joewrks.action-conformance/1.0"
REGRESSION_SLICE_VERSION = "joewrks.downstream.regression-slice/1.0"
SUPPORTED_RESULT_CLASSES = {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"}
COMPONENTS = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)
SCHEMA_FILES = {
    FULL_CONTRACT_VERSION: "action-contract.schema.json",
    REGRESSION_SLICE_VERSION: "regression-slice.schema.json",
}


class ContractError(ValueError):
    """A downstream contract cannot be derived from the approved authority."""


@lru_cache(maxsize=None)
def _load_schema(filename: str) -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "schemas" / filename
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot load downstream schema {filename}: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"downstream schema {filename} must be an object")
    return value


def _materialize_sources(
    state: dict[str, Any],
    sources: Any,
    *,
    default_active: bool,
) -> list[dict[str, Any]]:
    if not isinstance(sources, list):
        raise ContractError("source collection must be an array")
    materialized = []
    for source in sources:
        if not isinstance(source, dict):
            raise ContractError("source reference must be an object")
        if "value_sha256" in source:
            materialized.append(copy.deepcopy(source))
            continue
        try:
            materialized.append(
                make_source_ref(
                    state,
                    source["object_id"],
                    source["pointer"],
                    active=source.get("active", default_active),
                )
            )
        except (KeyError, ProvenanceError) as error:
            raise ContractError(f"cannot materialize source: {error}") from error
    return materialized


def materialize_definition(
    state: dict[str, Any], definition: dict[str, Any]
) -> dict[str, Any]:
    """Attach exact value hashes/status to pointer-only product adapter sources."""

    materialized = copy.deepcopy(definition)
    for action in materialized.get("actions", []):
        action["sources"] = _materialize_sources(
            state, action.get("sources", []), default_active=True
        )
    for lifecycle in materialized.get("lifecycles", []):
        lifecycle["sources"] = _materialize_sources(
            state, lifecycle.get("sources", []), default_active=True
        )
        lifecycle["superseded_sentinels"] = _materialize_sources(
            state,
            lifecycle.get("superseded_sentinels", []),
            default_active=False,
        )
    return materialized


def semantic_value(field: Any) -> Any:
    """Return an already-compiled semantic value without approving its derivation."""

    if not isinstance(field, dict) or "value" not in field:
        raise ContractError("compiled semantic field is missing value")
    return field["value"]


def is_full_handoff_contract(bundle: Any) -> bool:
    """Return whether a compiled bundle is eligible for production handoff."""

    if not isinstance(bundle, dict):
        return False
    if bundle.get("contract_schema_version") != FULL_CONTRACT_VERSION:
        return False
    try:
        _validate_bundle(bundle, FULL_CONTRACT_VERSION)
    except ContractError:
        return False
    unhashed = copy.deepcopy(bundle)
    declared_hash = unhashed.pop("contract_hash", None)
    if not isinstance(declared_hash, str) or sha256_json(unhashed) != declared_hash:
        return False
    assessment = bundle.get("authority_assessment")
    return (
        isinstance(assessment, dict)
        and assessment.get("structurally_valid") is True
        and assessment.get("provenance_valid") is True
        and assessment.get("machine_derived_obligations_verified") is True
    )


def _approved_authority(state: dict[str, Any]) -> dict[str, Any]:
    project = state.get("project")
    if not isinstance(project, dict):
        raise ContractError("canonical authority is missing project metadata")
    approval = project.get("approval")
    revision = project.get("definition_revision")
    if project.get("status") != "CLOSED" or not isinstance(approval, dict):
        raise ContractError("downstream contracts require CLOSED approved authority")
    if approval.get("approved_revision") != revision:
        raise ContractError("approval revision does not match current definition revision")
    digest = approval.get("approved_digest")
    if not isinstance(digest, str) or not digest:
        raise ContractError("approved digest is missing")
    return {
        "product_slug": project.get("slug"),
        "approved_revision": revision,
        "approved_digest": digest,
        "canonical_state_sha256": sha256_json(state),
    }


def _verify_sources(
    state: dict[str, Any],
    sources: Any,
    *,
    require_current: bool,
    owner: str,
) -> list[dict[str, Any]]:
    if not isinstance(sources, list) or not sources:
        raise ContractError(f"{owner} requires at least one canonical source")
    verified: list[dict[str, Any]] = []
    for source in sources:
        try:
            verified.append(verify_source_ref(state, source, require_current=False))
        except ProvenanceError as error:
            raise ContractError(f"{owner}: {error}") from error
    if require_current:
        statuses = [source.get("source_status") for source in verified]
        if statuses and all(status == "SUPERSEDED" for status in statuses):
            raise ContractError(
                f"{owner}: active semantic field derives exclusively from SUPERSEDED authority"
            )
        for source in verified:
            if source.get("source_status") != "CURRENT":
                raise ContractError(
                    f"{owner}: active source {source.get('object_id')} is "
                    f"{source.get('source_status')}, not CURRENT"
                )
            if source.get("active") is not True:
                raise ContractError(
                    f"{owner}: current source {source.get('object_id')} must be active"
                )
    return verified


def _semantic_fields_for(
    contract_version: str,
    *,
    kind: str,
) -> set[str]:
    if kind == "lifecycle":
        schema = _load_schema("lifecycle-contract.schema.json")
        properties = schema["$defs"]["lifecycle"]["properties"]
    else:
        schema = _load_schema(SCHEMA_FILES[contract_version])
        properties = schema["$defs"]["action"]["properties"]
    return {
        name
        for name, field_schema in properties.items()
        if isinstance(field_schema, dict)
        and field_schema.get("$ref") == "#/$defs/semanticField"
    }


def validate_semantic_field(
    state: dict[str, Any],
    field: Any,
    sources: list[dict[str, Any]],
    *,
    owner: str,
) -> str:
    """Validate provenance and derivation, returning the derivation class."""

    if not isinstance(field, dict):
        raise ContractError(f"{owner}: semantic field must be an object")
    refs = field.get("source_refs")
    if not isinstance(refs, list) or not refs:
        raise ContractError(f"{owner}: semantic field requires non-empty source_refs")
    for ref in refs:
        if not isinstance(ref, int) or isinstance(ref, bool) or ref < 0 or ref >= len(sources):
            raise ContractError(f"{owner}: source_ref out of range: {ref!r}")
        source = sources[ref]
        if source.get("source_status") != "CURRENT" or source.get("active") is not True:
            raise ContractError(
                f"{owner}: active semantic field derives exclusively from SUPERSEDED authority"
            )
    derivation = field.get("derivation")
    if not isinstance(derivation, dict):
        raise ContractError(f"{owner}: semantic field requires derivation")
    kind = derivation.get("kind")
    if kind == "REVIEW_REQUIRED":
        explanation = derivation.get("explanation")
        if not isinstance(explanation, str) or not explanation.strip():
            raise ContractError(f"{owner}: REVIEW_REQUIRED needs a derivation explanation")
        return kind
    if kind != "MACHINE_DERIVED":
        raise ContractError(f"{owner}: unsupported derivation kind: {kind!r}")
    if len(refs) != 1:
        raise ContractError(f"{owner}: MACHINE_DERIVED requires exactly one source_ref")
    source_value = resolve_pointer(state, sources[refs[0]]["pointer"])
    operator = derivation.get("operator")
    if operator == "exact":
        if "pointer" in derivation:
            raise ContractError(f"{owner}: exact derivation does not accept pointer")
        computed = source_value
    elif operator == "extract":
        pointer = derivation.get("pointer")
        try:
            computed = resolve_pointer(source_value, pointer)
        except ProvenanceError as error:
            raise ContractError(f"{owner}: extract derivation failed: {error}") from error
    else:
        raise ContractError(f"{owner}: unsupported MACHINE_DERIVED operator: {operator!r}")
    try:
        matches = sha256_json(computed) == sha256_json(field.get("value"))
    except (TypeError, ValueError) as error:
        raise ContractError(f"{owner}: semantic value is not canonical JSON: {error}") from error
    if not matches:
        raise ContractError(f"{owner}: emitted value does not match compiler-derived value")
    return kind


def _validate_action_result_contract(action: dict[str, Any], *, owner: str) -> None:
    default_result = semantic_value(action.get("default_result"))
    if default_result not in SUPPORTED_RESULT_CLASSES:
        raise ContractError(f"{owner}: unsupported default result: {default_result!r}")
    expectations = semantic_value(action.get("result_expectations"))
    if not isinstance(expectations, dict) or not expectations:
        raise ContractError(f"{owner}: result_expectations must be a non-empty object")
    if default_result not in expectations:
        raise ContractError(f"{owner}: default result has no declared result expectation")
    for result_class, expectation in expectations.items():
        if result_class not in SUPPORTED_RESULT_CLASSES:
            raise ContractError(f"{owner}: unsupported result expectation: {result_class!r}")
        if not isinstance(expectation, dict):
            raise ContractError(f"{owner}: {result_class} expectation must be an object")
        for component in COMPONENTS:
            if component not in expectation:
                raise ContractError(
                    f"{owner}: {result_class} expectation missing component: {component}"
                )
            if expectation[component] not in {"CHANGED", "UNCHANGED", "ANY"}:
                raise ContractError(
                    f"{owner}: invalid {component} expectation: {expectation[component]!r}"
                )
        assertions = expectation.get("assertions", [])
        if not isinstance(assertions, list):
            raise ContractError(f"{owner}: result assertions must be an array")
    invariants = semantic_value(action.get("input_invariants"))
    if not isinstance(invariants, list):
        raise ContractError(f"{owner}: input_invariants must be an array")
    obligations = semantic_value(action.get("test_obligations"))
    if not isinstance(obligations, list) or not all(
        isinstance(obligation, str) and obligation for obligation in obligations
    ):
        raise ContractError(f"{owner}: test_obligations must be non-empty strings")


def _compile_items(
    state: dict[str, Any],
    items: Any,
    *,
    kind: str,
    id_key: str,
    contract_version: str,
    counts: dict[str, int],
) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        raise ContractError(f"{kind} collection must be an array")
    if contract_version == REGRESSION_SLICE_VERSION and kind == "lifecycle" and items:
        raise ContractError("regression slices do not support lifecycle handoff semantics")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    semantic_fields = _semantic_fields_for(contract_version, kind=kind)
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get(id_key), str):
            raise ContractError(f"every {kind} requires {id_key}")
        item_id = item[id_key]
        if item_id in seen:
            raise ContractError(f"duplicate {kind} ID: {item_id}")
        seen.add(item_id)
        compiled = copy.deepcopy(item)
        compiled["sources"] = _verify_sources(
            state,
            compiled.get("sources"),
            require_current=True,
            owner=f"{kind} {item_id}",
        )
        for field_name in sorted(semantic_fields & set(compiled)):
            derivation_class = validate_semantic_field(
                state,
                compiled[field_name],
                compiled["sources"],
                owner=f"{kind} {item_id}.{field_name}",
            )
            counts[derivation_class] += 1
        if kind == "action":
            _validate_action_result_contract(compiled, owner=f"action {item_id}")
        if kind == "lifecycle":
            sentinels = compiled.get("superseded_sentinels", [])
            if not isinstance(sentinels, list):
                raise ContractError(
                    f"lifecycle {item_id} superseded_sentinels must be an array"
                )
            verified_sentinels = []
            for sentinel in sentinels:
                if not isinstance(sentinel, dict) or sentinel.get("active", True):
                    raise ContractError(
                        f"lifecycle {item_id} superseded sentinel must be inactive"
                    )
                try:
                    verified = verify_source_ref(state, sentinel, require_current=False)
                except ProvenanceError as error:
                    raise ContractError(f"lifecycle {item_id}: {error}") from error
                if verified.get("source_status") != "SUPERSEDED":
                    raise ContractError(
                        f"lifecycle {item_id} sentinel source "
                        f"{verified.get('object_id')} is not SUPERSEDED"
                    )
                verified_sentinels.append(verified)
            compiled["superseded_sentinels"] = verified_sentinels
        result.append(compiled)
    return result


def _validate_bundle(bundle: dict[str, Any], contract_version: str) -> None:
    schema = _load_schema(SCHEMA_FILES[contract_version])
    try:
        validate_instance(bundle, schema)
        if contract_version == FULL_CONTRACT_VERSION:
            lifecycle_schema = _load_schema("lifecycle-contract.schema.json")
            lifecycle_item_schema = lifecycle_schema["$defs"]["lifecycle"]
            for index, lifecycle in enumerate(bundle["lifecycles"]):
                try:
                    validate_instance(
                        lifecycle,
                        lifecycle_item_schema,
                        root_schema=lifecycle_schema,
                    )
                except SchemaValidationError as error:
                    raise SchemaValidationError(f"/lifecycles/{index}: {error}") from error
    except SchemaValidationError as error:
        raise ContractError(f"{contract_version} structural validation failed: {error}") from error


def compile_contract(
    state: dict[str, Any],
    definition: dict[str, Any],
    *,
    compiler_version: str = COMPILER_VERSION,
) -> dict[str, Any]:
    try:
        authority = _approved_authority(state)
        if definition.get("product_slug") != authority["product_slug"]:
            raise ContractError("downstream product slug does not match canonical authority")
        contract_version = definition.get("contract_schema_version")
        if contract_version not in SCHEMA_FILES:
            raise ContractError(
                f"unsupported or missing contract_schema_version: {contract_version!r}"
            )
        counts = {"MACHINE_DERIVED": 0, "REVIEW_REQUIRED": 0}
        bundle = {
            "contract_schema_version": contract_version,
            "compiler": {"id": COMPILER_ID, "version": compiler_version},
            "source_authority": authority,
            "actions": _compile_items(
                state,
                definition.get("actions", []),
                kind="action",
                id_key="action_id",
                contract_version=contract_version,
                counts=counts,
            ),
            "lifecycles": _compile_items(
                state,
                definition.get("lifecycles", []),
                kind="lifecycle",
                id_key="lifecycle_id",
                contract_version=contract_version,
                counts=counts,
            ),
        }
    except ProvenanceError as error:
        raise ContractError(str(error)) from error
    total = counts["MACHINE_DERIVED"] + counts["REVIEW_REQUIRED"]
    bundle["authority_assessment"] = {
        "structurally_valid": True,
        "provenance_valid": True,
        "machine_derived_obligations_verified": True,
        "machine_derived_field_count": counts["MACHINE_DERIVED"],
        "review_required_field_count": counts["REVIEW_REQUIRED"],
        "review_required_obligations_present": counts["REVIEW_REQUIRED"] > 0,
        "machine_verifiable_coverage": counts["MACHINE_DERIVED"] / total if total else 0.0,
    }
    bundle["contract_hash"] = sha256_json(bundle)
    _validate_bundle(bundle, contract_version)
    return bundle
