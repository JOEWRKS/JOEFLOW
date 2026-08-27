"""Canonical byte and SHA-256 helpers for semantic-review artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    """Return stable UTF-8 JSON bytes with no non-standard numeric values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 hex digest of *data*."""

    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> tuple[str, int]:
    """Hash a file's exact bytes and return its digest and byte count."""

    data = path.read_bytes()
    return sha256_bytes(data), len(data)


def manifest_hash(manifest: dict[str, Any]) -> str:
    """Hash a manifest while excluding its self-reported hash field."""

    unhashed = dict(manifest)
    unhashed.pop("reviewer_input_manifest_hash", None)
    return sha256_bytes(canonical_json_bytes(unhashed))


def package_hash(manifest_hash_value: str, files: list[dict[str, Any]]) -> str:
    """Hash an ordered logical package independent of manifest file order."""

    ordered = sorted(
        (
            {
                "logical_role": item["logical_role"],
                "path": item["path"],
                "sha256": item["sha256"],
                "bytes": item["bytes"],
            }
            for item in files
        ),
        key=lambda item: (item["logical_role"], item["path"]),
    )
    return sha256_bytes(
        canonical_json_bytes(
            {"manifest_hash": manifest_hash_value, "ordered_files": ordered}
        )
    )
