"""Versioned JSONL protocol and lossless non-finite number sentinels."""

from __future__ import annotations

import json
import math
from typing import Any


PROTOCOL_VERSION = "joewrks.downstream.execution/1.0"
NUMBER_SENTINELS = {
    "NaN": math.nan,
    "+Infinity": math.inf,
    "-Infinity": -math.inf,
}
SNAPSHOT_COMPONENTS = (
    "authoritative_state",
    "revision",
    "history",
    "business_side_effects",
    "delivery_effects",
)


class ProtocolError(ValueError):
    """A JSONL record violates the downstream execution protocol."""


def encode_typed_numbers(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return {"$number": "NaN"}
        return {"$number": "+Infinity" if value > 0 else "-Infinity"}
    if isinstance(value, list):
        return [encode_typed_numbers(item) for item in value]
    if isinstance(value, tuple):
        return [encode_typed_numbers(item) for item in value]
    if isinstance(value, dict):
        return {key: encode_typed_numbers(item) for key, item in value.items()}
    return value


def decode_typed_numbers(value: Any) -> Any:
    if isinstance(value, list):
        return [decode_typed_numbers(item) for item in value]
    if isinstance(value, dict):
        if "$number" in value:
            if set(value) != {"$number"} or value["$number"] not in NUMBER_SENTINELS:
                raise ProtocolError("invalid typed-number sentinel")
            return NUMBER_SENTINELS[value["$number"]]
        return {key: decode_typed_numbers(item) for key, item in value.items()}
    return value


def _require_mapping(record: dict[str, Any], field: str) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        raise ProtocolError(f"{field} must be an object")
    return value


def validate_execution_record(record: Any) -> None:
    if not isinstance(record, dict):
        raise ProtocolError("execution record must be an object")
    if record.get("protocol_version") != PROTOCOL_VERSION:
        raise ProtocolError(f"unsupported protocol version: {record.get('protocol_version')!r}")
    for field in ("record_kind", "sequence_id", "test_id", "product_slug", "contract_hash"):
        if not isinstance(record.get(field), str) or not record[field]:
            raise ProtocolError(f"{field} is required")
    authority = _require_mapping(record, "authority")
    if not isinstance(authority.get("approved_revision"), int) or not isinstance(
        authority.get("approved_digest"), str
    ):
        raise ProtocolError("authority requires approved_revision and approved_digest")
    adapter = _require_mapping(record, "adapter")
    if not all(isinstance(adapter.get(field), str) and adapter[field] for field in ("name", "version")):
        raise ProtocolError("adapter requires name and version")
    frozen = _require_mapping(record, "frozen_source")
    if not all(isinstance(frozen.get(field), str) and frozen[field] for field in ("commit", "tree")):
        raise ProtocolError("frozen_source requires commit and tree")
    _require_mapping(record, "command")
    _require_mapping(record, "result")
    _require_mapping(record, "deltas")
    for phase in ("before", "after"):
        snapshot = _require_mapping(record, phase)
        missing = [field for field in SNAPSHOT_COMPONENTS if field not in snapshot]
        if missing:
            raise ProtocolError(f"{phase} snapshot is missing: {', '.join(missing)}")
    try:
        json.dumps(record, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ProtocolError("protocol records must encode non-finite values as typed sentinels") from error


def dumps_record(record: dict[str, Any]) -> str:
    encoded = encode_typed_numbers(record)
    validate_execution_record(encoded)
    return json.dumps(encoded, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n"


def loads_record(line: str) -> dict[str, Any]:
    if not isinstance(line, str) or len(line.splitlines()) != 1:
        raise ProtocolError("exactly one JSONL record is required")
    try:
        record = json.loads(line)
    except json.JSONDecodeError as error:
        raise ProtocolError("invalid JSONL record") from error
    validate_execution_record(record)
    return record
