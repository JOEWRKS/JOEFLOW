"""Hash-bound reviewer input package and run-envelope validation."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from downstream.schema_validation import SchemaValidationError, validate_instance

from .hashing import (
    canonical_json_bytes,
    manifest_hash,
    package_hash,
    sha256_bytes,
    sha256_file,
)


REQUIRED_ROLES = {
    "canonical_authority",
    "action_contract",
    "provenance_inventory",
    "responsibility_profile",
    "semantic_obligation_index",
    "reviewer_brief",
    "review_output_schema",
    "review_identity_inventory",
    "exclusion_manifest",
}
TEXT_SUFFIXES = {".json", ".md", ".txt"}
FORBIDDEN_NAME_MARKERS = {
    "prior-review",
    "prior_verdict",
    "previous-verdict",
    "hidden-answer",
    "answer-bank",
    "confusion-matrix",
    "correction-hint",
    "implementation-result",
    "efficacy-result",
}


class PackageError(ValueError):
    """A deterministic reviewer-package preflight failure."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / (
        "semantic-review-input-manifest.schema.json"
    )


def _safe_path(root: Path, relative: str) -> Path:
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or relative.startswith("/")
        or PurePosixPath(relative).is_absolute()
        or ".." in PurePosixPath(relative).parts
    ):
        raise PackageError("INVALID_PACKAGE_PATH", str(relative))
    resolved = (root / relative).resolve()
    resolved_root = root.resolve()
    if resolved_root not in (resolved, *resolved.parents):
        raise PackageError("INVALID_PACKAGE_PATH", relative)
    return resolved


def _read_text_bytes(path: Path, data: bytes) -> str:
    if data.startswith(b"\xef\xbb\xbf"):
        raise PackageError("PACKAGE_HASH_MISMATCH", f"UTF-8 BOM forbidden: {path.name}")
    if b"\r" in data:
        raise PackageError("PACKAGE_HASH_MISMATCH", f"LF line endings required: {path.name}")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PackageError("PACKAGE_HASH_MISMATCH", f"invalid UTF-8: {path.name}") from error


def _read_json(path: Path, data: bytes) -> Any:
    text = _read_text_bytes(path, data)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError) as error:
        raise PackageError("PACKAGE_HASH_MISMATCH", f"invalid JSON: {path.name}") from error


def _validate_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise PackageError("PACKAGE_HASH_MISMATCH", "manifest must be an object")
    if manifest.get("reviewer_input_package_hash") is not None:
        raise PackageError(
            "PACKAGE_HASH_MISMATCH", "package hash must not be stored in the manifest"
        )
    if manifest.get("previous_reviewer_verdicts_present") is not False:
        raise PackageError(
            "PREVIOUS_VERDICT_EXPOSURE",
            "previous_reviewer_verdicts_present must be false",
        )
    try:
        schema = json.loads(_schema_path().read_text(encoding="utf-8"))
        validate_instance(manifest, schema)
    except (OSError, json.JSONDecodeError, SchemaValidationError) as error:
        raise PackageError("PACKAGE_HASH_MISMATCH", f"invalid manifest: {error}") from error
    return manifest


def verify_exclusions(root: Path, manifest: dict[str, Any]) -> None:
    """Reject undeclared prior-review or hidden-answer material in the package root."""

    declared = {PurePosixPath(item["path"]).as_posix() for item in manifest["files"]}
    declared.add("manifest.json")
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in declared:
            continue
        normalized = relative.lower().replace("_", "-")
        if any(marker.replace("_", "-") in normalized for marker in FORBIDDEN_NAME_MARKERS):
            raise PackageError("PREVIOUS_VERDICT_EXPOSURE", relative)
        raise PackageError("PACKAGE_HASH_MISMATCH", f"undeclared package file: {relative}")


def _validate_required_roles(files: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    seen_paths: set[str] = set()
    for item in files:
        role = item["logical_role"]
        counts[role] = counts.get(role, 0) + 1
        if item["path"] in seen_paths:
            raise PackageError("PACKAGE_HASH_MISMATCH", f"duplicate path: {item['path']}")
        seen_paths.add(item["path"])
    invalid = sorted(role for role in REQUIRED_ROLES if counts.get(role) != 1)
    if invalid:
        raise PackageError(
            "PACKAGE_HASH_MISMATCH",
            f"required logical role count is not exactly one: {', '.join(invalid)}",
        )
    if counts.get("golden_suite_manifest", 0) > 1:
        raise PackageError("PACKAGE_HASH_MISMATCH", "duplicate golden_suite_manifest")


def _validate_pr_p01(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise PackageError("PACKAGE_HASH_MISMATCH", "action contract must be an object")
    lifecycles = contract.get("lifecycles", [])
    if not isinstance(lifecycles, list):
        raise PackageError("PACKAGE_HASH_MISMATCH", "lifecycles must be an array")
    for lifecycle in lifecycles:
        if not isinstance(lifecycle, dict):
            continue
        lifecycle_id = lifecycle.get("id", "<unknown>")
        sentinels = lifecycle.get("superseded_sentinels", [])
        if not isinstance(sentinels, list):
            raise PackageError(
                "PACKAGE_HASH_MISMATCH",
                f"{lifecycle_id} superseded_sentinels must be an array",
            )
        for index, sentinel in enumerate(sentinels):
            if not isinstance(sentinel, dict):
                raise PackageError(
                    "PACKAGE_HASH_MISMATCH",
                    f"{lifecycle_id} superseded sentinel {index} must be an object",
                )
            if sentinel.get("active") is True and sentinel.get("source_status") == "SUPERSEDED":
                raise PackageError(
                    "ACTIVE_SUPERSEDED_SOURCE",
                    f"PR-P01 {lifecycle_id} superseded_sentinels[{index}]",
                )


def load_and_verify_package(root: Path) -> dict[str, Any]:
    """Verify a reviewer package from exact bytes before semantic parsing."""

    root = root.resolve()
    manifest_path = root / "manifest.json"
    try:
        manifest_data = manifest_path.read_bytes()
    except OSError as error:
        raise PackageError("PACKAGE_HASH_MISMATCH", "manifest.json is required") from error
    manifest = _validate_manifest(_read_json(manifest_path, manifest_data))
    observed_manifest_hash = manifest_hash(manifest)
    if manifest["reviewer_input_manifest_hash"] != observed_manifest_hash:
        raise PackageError("PACKAGE_HASH_MISMATCH", "manifest self-hash mismatch")

    files = manifest["files"]
    _validate_required_roles(files)
    file_bytes: dict[str, bytes] = {}
    role_hashes: dict[str, str] = {}
    role_paths: dict[str, Path] = {}
    for item in files:
        path = _safe_path(root, item["path"])
        try:
            observed_hash, observed_size = sha256_file(path)
            data = path.read_bytes()
        except OSError as error:
            raise PackageError(
                "PACKAGE_HASH_MISMATCH", f"declared file missing: {item['path']}"
            ) from error
        if (observed_hash, observed_size) != (item["sha256"], item["bytes"]):
            raise PackageError("PACKAGE_HASH_MISMATCH", f"byte drift: {item['path']}")
        if path.suffix.lower() in TEXT_SUFFIXES:
            _read_text_bytes(path, data)
        file_bytes[item["path"]] = data
        if item["logical_role"] in REQUIRED_ROLES or item["logical_role"] == "golden_suite_manifest":
            role_hashes[item["logical_role"]] = observed_hash
            role_paths[item["logical_role"]] = path

    verify_exclusions(root, manifest)
    contract_path = role_paths["action_contract"]
    _validate_pr_p01(_read_json(contract_path, file_bytes[contract_path.relative_to(root).as_posix()]))

    return {
        "root": root,
        "manifest": manifest,
        "reviewer_input_manifest_hash": observed_manifest_hash,
        "reviewer_input_package_hash": package_hash(observed_manifest_hash, files),
        "role_hashes": role_hashes,
        "role_paths": role_paths,
    }


def verify_run_envelope(
    envelope: dict[str, Any], package: dict[str, Any]
) -> dict[str, Any]:
    """Verify non-normative run identity and isolation evidence."""

    required = {
        "review_run_id",
        "reviewer_context_id",
        "reviewer_input_package_hash",
        "reviewer_brief_hash",
        "isolation_attestation",
        "isolation_attestation_hash",
    }
    if set(envelope) != required:
        raise PackageError("PACKAGE_HASH_MISMATCH", "invalid run-envelope fields")
    if not all(
        isinstance(envelope.get(field), str) and envelope[field].strip()
        for field in ("review_run_id", "reviewer_context_id")
    ):
        raise PackageError("PACKAGE_HASH_MISMATCH", "run/context IDs are required")
    if envelope["reviewer_input_package_hash"] != package["reviewer_input_package_hash"]:
        raise PackageError("PACKAGE_HASH_MISMATCH", "run-envelope package hash mismatch")
    if envelope["reviewer_brief_hash"] != package["role_hashes"]["reviewer_brief"]:
        raise PackageError("BRIEF_HASH_MISMATCH", "run-envelope brief hash mismatch")
    attestation = envelope["isolation_attestation"]
    expected_attestation = {
        "fresh_context": True,
        "previous_verdict_access": False,
        "manifest_only_evidence": True,
    }
    if attestation.get("previous_verdict_access") is not False:
        raise PackageError("PREVIOUS_VERDICT_EXPOSURE", "prior verdict access declared")
    if attestation != expected_attestation:
        raise PackageError("PACKAGE_HASH_MISMATCH", "invalid isolation attestation")
    if envelope["isolation_attestation_hash"] != sha256_bytes(
        canonical_json_bytes(attestation)
    ):
        raise PackageError("PACKAGE_HASH_MISMATCH", "isolation attestation hash mismatch")
    return envelope
