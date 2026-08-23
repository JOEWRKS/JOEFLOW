"""Compilation of provenance-pinned downstream action and lifecycle contracts."""

from __future__ import annotations

import copy
from typing import Any

from .provenance import ProvenanceError, make_source_ref, sha256_json, verify_source_ref


COMPILER_ID = "joewrks-product-definition/downstream"
COMPILER_VERSION = "0.4.1"


class ContractError(ValueError):
    """A downstream contract cannot be derived from the approved authority."""


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
            verified.append(verify_source_ref(state, source, require_current=require_current))
        except ProvenanceError as error:
            raise ContractError(f"{owner}: {error}") from error
    return verified


def _compile_items(
    state: dict[str, Any],
    items: Any,
    *,
    kind: str,
    id_key: str,
) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        raise ContractError(f"{kind} collection must be an array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
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
        if kind == "lifecycle":
            sentinels = compiled.get("superseded_sentinels", [])
            if not isinstance(sentinels, list):
                raise ContractError(f"lifecycle {item_id} superseded_sentinels must be an array")
            verified_sentinels = []
            for sentinel in sentinels:
                if not isinstance(sentinel, dict) or sentinel.get("active", True):
                    raise ContractError(f"lifecycle {item_id} superseded sentinel must be inactive")
                try:
                    verified = verify_source_ref(state, sentinel, require_current=False)
                except ProvenanceError as error:
                    raise ContractError(f"lifecycle {item_id}: {error}") from error
                if verified.get("source_status") != "SUPERSEDED":
                    raise ContractError(
                        f"lifecycle {item_id} sentinel source {verified.get('object_id')} is not SUPERSEDED"
                    )
                verified_sentinels.append(verified)
            compiled["superseded_sentinels"] = verified_sentinels
        result.append(compiled)
    return result


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
        bundle = {
            "contract_schema_version": "joewrks.action-conformance/1.0",
            "compiler": {"id": COMPILER_ID, "version": compiler_version},
            "source_authority": authority,
            "actions": _compile_items(
                state,
                definition.get("actions", []),
                kind="action",
                id_key="action_id",
            ),
            "lifecycles": _compile_items(
                state,
                definition.get("lifecycles", []),
                kind="lifecycle",
                id_key="lifecycle_id",
            ),
        }
    except ProvenanceError as error:
        raise ContractError(str(error)) from error
    bundle["contract_hash"] = sha256_json(bundle)
    return bundle
