"""Deterministic canonical JSON and exact canonical-source provenance."""

from __future__ import annotations

import hashlib
import json
from typing import Any


class ProvenanceError(ValueError):
    """A source reference does not resolve to the declared canonical authority."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _decode_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def resolve_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ProvenanceError(f"invalid JSON Pointer: {pointer!r}")
    value = document
    for raw_token in pointer[1:].split("/"):
        token = _decode_token(raw_token)
        try:
            if isinstance(value, list):
                if token == "-" or not token.isdigit():
                    raise KeyError(token)
                value = value[int(token)]
            elif isinstance(value, dict):
                value = value[token]
            else:
                raise KeyError(token)
        except (IndexError, KeyError, TypeError) as error:
            raise ProvenanceError(f"JSON Pointer does not resolve: {pointer}") from error
    return value


def _escape_token(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def find_object_pointer(document: dict[str, Any], object_id: str) -> str:
    objects = document.get("objects")
    if not isinstance(objects, dict):
        raise ProvenanceError("canonical authority has no objects map")
    matches: list[str] = []
    for group_name, group in objects.items():
        if not isinstance(group, list):
            continue
        for index, item in enumerate(group):
            if isinstance(item, dict) and item.get("id") == object_id:
                matches.append(f"/objects/{_escape_token(str(group_name))}/{index}")
    if len(matches) != 1:
        raise ProvenanceError(
            f"stable object ID must resolve exactly once: {object_id} ({len(matches)} matches)"
        )
    return matches[0]


def make_source_ref(
    document: dict[str, Any],
    object_id: str,
    pointer: str,
    *,
    active: bool = True,
) -> dict[str, Any]:
    object_pointer = find_object_pointer(document, object_id)
    if pointer != object_pointer and not pointer.startswith(f"{object_pointer}/"):
        raise ProvenanceError(f"pointer {pointer} is outside stable object {object_id}")
    source_object = resolve_pointer(document, object_pointer)
    value = resolve_pointer(document, pointer)
    return {
        "object_id": object_id,
        "pointer": pointer,
        "value_sha256": sha256_json(value),
        "source_status": source_object.get("status"),
        "active": active,
    }


def verify_source_ref(
    document: dict[str, Any],
    reference: dict[str, Any],
    *,
    require_current: bool | None = None,
) -> dict[str, Any]:
    try:
        object_id = reference["object_id"]
        pointer = reference["pointer"]
        expected_hash = reference["value_sha256"]
    except (KeyError, TypeError) as error:
        raise ProvenanceError("source reference is missing object_id, pointer, or value_sha256") from error
    if not isinstance(object_id, str) or not isinstance(pointer, str) or not isinstance(expected_hash, str):
        raise ProvenanceError("source reference identity fields must be strings")
    object_pointer = find_object_pointer(document, object_id)
    if pointer != object_pointer and not pointer.startswith(f"{object_pointer}/"):
        raise ProvenanceError(f"pointer {pointer} is outside stable object {object_id}")
    source_object = resolve_pointer(document, object_pointer)
    source_status = source_object.get("status")
    active = reference.get("active", True)
    if require_current is None:
        require_current = bool(active)
    if require_current and source_status != "CURRENT":
        raise ProvenanceError(f"active source {object_id} is {source_status}, not CURRENT")
    if reference.get("source_status") not in (None, source_status):
        raise ProvenanceError(f"source status drift for {object_id}")
    actual_hash = sha256_json(resolve_pointer(document, pointer))
    if actual_hash != expected_hash:
        raise ProvenanceError(f"source hash drift for {object_id} at {pointer}")
    verified = dict(reference)
    verified["source_status"] = source_status
    verified["active"] = bool(active)
    return verified
