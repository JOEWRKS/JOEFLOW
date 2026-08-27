"""Hash-bound reviewer input package and run-envelope validation."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from downstream.schema_validation import (
    SchemaValidationError,
    _check_schema,
    validate_instance,
)
from downstream.provenance import ProvenanceError, verify_source_ref

from .hashing import (
    canonical_json_bytes,
    manifest_hash,
    package_hash,
    sha256_bytes,
    sha256_file,
)
from .responsibility import (
    EXPECTED_ACTION_FIELDS,
    EXPECTED_LIFECYCLE_FIELDS,
    ResponsibilityError,
    expected_responsibility,
    load_responsibility_profile,
    validate_obligation_index,
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
EXPECTED_SCHEMA_IDENTITIES = {
    role: f"joewrks.semantic-review-role/{role}" for role in REQUIRED_ROLES
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
    "golden-answer",
}
FORBIDDEN_JSON_KEYS = {
    "previous_reviewer_verdict",
    "previous_reviewer_verdicts",
    "prior_reviewer_verdict",
    "prior_review",
    "hidden_answer",
    "hidden_answers",
    "golden_answer",
    "golden_answers",
    "confusion_matrix",
    "correction_hint",
    "implementation_result",
    "efficacy_result",
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


def _downstream_schema_path(name: str) -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / name


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

    roles_by_path = {
        PurePosixPath(item["path"]).as_posix(): item["logical_role"]
        for item in manifest["files"]
    }
    declared = set(roles_by_path)
    declared.add("manifest.json")
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        normalized = relative.lower().replace("_", "-")
        if any(marker.replace("_", "-") in normalized for marker in FORBIDDEN_NAME_MARKERS):
            raise PackageError("PREVIOUS_VERDICT_EXPOSURE", relative)
        if relative in declared:
            if path.suffix.lower() == ".json":
                try:
                    value = _read_json(path, path.read_bytes())
                except OSError as error:
                    raise PackageError(
                        "PACKAGE_HASH_MISMATCH", f"cannot scan declared file: {relative}"
                    ) from error
                role = roles_by_path.get(relative)
                if role == "review_output_schema":
                    continue
                if _contains_forbidden_json(
                    value,
                    strict_review_scan=role
                    in {"supporting_projection", "golden_suite_manifest"},
                ):
                    raise PackageError("PREVIOUS_VERDICT_EXPOSURE", relative)
            continue
        raise PackageError("PACKAGE_HASH_MISMATCH", f"undeclared package file: {relative}")


def _contains_forbidden_json(value: Any, *, strict_review_scan: bool = False) -> bool:
    if isinstance(value, dict):
        normalized_keys = {
            str(key).lower().replace("-", "_") for key in value
        }
        if "review_identity" in normalized_keys and normalized_keys & {
            "verdict",
            "rationale",
            "rationale_code",
            "reviewer_explanation",
        }:
            return True
        if strict_review_scan and normalized_keys & {
            "review_identity",
            "verdict",
            "rationale",
            "rationale_code",
            "reviewer_explanation",
            "observed_verdict_rationale_pairs",
        }:
            return True
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_JSON_KEYS:
                return True
            if normalized in {
                "previous_reviewer_verdicts_present",
                "hidden_answers_present",
                "implementation_outcomes_present",
                "unrelated_product_evidence_present",
            } and child is not False:
                return True
            if _contains_forbidden_json(child, strict_review_scan=strict_review_scan):
                return True
        return False
    if isinstance(value, list):
        return any(
            _contains_forbidden_json(item, strict_review_scan=strict_review_scan)
            for item in value
        )
    return False


def _validate_required_roles(files: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    seen_paths: set[str] = set()
    for item in files:
        role = item["logical_role"]
        counts[role] = counts.get(role, 0) + 1
        if item["path"] in seen_paths:
            raise PackageError("PACKAGE_HASH_MISMATCH", f"duplicate path: {item['path']}")
        seen_paths.add(item["path"])
        expected_schema_identity = EXPECTED_SCHEMA_IDENTITIES.get(role)
        if (
            expected_schema_identity is not None
            and item.get("schema_identity") != expected_schema_identity
        ):
            raise PackageError(
                "PACKAGE_HASH_MISMATCH", f"schema identity drift: {role}"
            )
    invalid = sorted(role for role in REQUIRED_ROLES if counts.get(role) != 1)
    if invalid:
        raise PackageError(
            "PACKAGE_HASH_MISMATCH",
            f"required logical role count is not exactly one: {', '.join(invalid)}",
        )
    if counts.get("golden_suite_manifest", 0) > 1:
        raise PackageError("PACKAGE_HASH_MISMATCH", "duplicate golden_suite_manifest")


def _validate_pr_p01(authority: dict[str, Any], contract: Any) -> None:
    if not isinstance(contract, dict):
        raise PackageError("PACKAGE_HASH_MISMATCH", "action contract must be an object")
    lifecycles = contract.get("lifecycles", [])
    if not isinstance(lifecycles, list):
        raise PackageError("PACKAGE_HASH_MISMATCH", "lifecycles must be an array")
    for lifecycle in lifecycles:
        if not isinstance(lifecycle, dict):
            continue
        lifecycle_id = lifecycle.get("lifecycle_id", "<unknown>")
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
            if sentinel.get("active") is not False:
                raise PackageError(
                    "INVALID_PROVENANCE",
                    f"PR-P01 {lifecycle_id} sentinel must be inactive",
                )
            try:
                verified = verify_source_ref(
                    authority, sentinel, require_current=False
                )
            except ProvenanceError as error:
                raise PackageError("INVALID_PROVENANCE", str(error)) from error
            if verified.get("source_status") != "SUPERSEDED":
                raise PackageError(
                    "INVALID_PROVENANCE",
                    f"PR-P01 {lifecycle_id} sentinel is not superseded",
                )


def _verify_contract_hash(contract: dict[str, Any]) -> str:
    unhashed = dict(contract)
    declared = unhashed.pop("contract_hash", None)
    if (
        not isinstance(declared, str)
        or declared != sha256_bytes(canonical_json_bytes(unhashed))
    ):
        raise PackageError("CONTRACT_HASH_MISMATCH", "action contract self-hash")
    return declared


def _validate_contract_schemas(contract: dict[str, Any]) -> None:
    try:
        action_schema = json.loads(
            _downstream_schema_path("action-contract.schema.json").read_text(
                encoding="utf-8"
            )
        )
        lifecycle_schema = json.loads(
            _downstream_schema_path("lifecycle-contract.schema.json").read_text(
                encoding="utf-8"
            )
        )
        validate_instance(contract, action_schema)
        lifecycle_item_schema = lifecycle_schema["$defs"]["lifecycle"]
        for lifecycle in contract.get("lifecycles", []):
            validate_instance(
                lifecycle, lifecycle_item_schema, root_schema=lifecycle_schema
            )
    except (OSError, KeyError, json.JSONDecodeError, SchemaValidationError) as error:
        raise PackageError(
            "CONTRACT_HASH_MISMATCH", f"invalid frozen contract schema: {error}"
        ) from error


def _validate_contract_provenance(
    authority: dict[str, Any], contract: dict[str, Any]
) -> None:
    """Verify every active contract source and every semantic source index."""

    for collection_name, fields, id_key in (
        ("actions", EXPECTED_ACTION_FIELDS, "action_id"),
        ("lifecycles", EXPECTED_LIFECYCLE_FIELDS, "lifecycle_id"),
    ):
        seen_owner_ids = set()
        for owner in contract[collection_name]:
            owner_id = owner[id_key]
            if owner_id in seen_owner_ids:
                raise PackageError(
                    "CONTRACT_HASH_MISMATCH",
                    f"duplicate contract owner: {collection_name}:{owner_id}",
                )
            seen_owner_ids.add(owner_id)
            sources = owner["sources"]
            verified_sources = []
            seen_sources = set()
            for source in sources:
                if source.get("active") is True and source.get("source_status") == (
                    "SUPERSEDED"
                ):
                    raise PackageError(
                        "ACTIVE_SUPERSEDED_SOURCE", f"{collection_name}:{owner_id}"
                    )
                try:
                    verified = verify_source_ref(
                        authority, source, require_current=True
                    )
                except ProvenanceError as error:
                    raise PackageError("INVALID_PROVENANCE", str(error)) from error
                if verified.get("active") is not True:
                    raise PackageError(
                        "INVALID_PROVENANCE", f"inactive contract source: {owner_id}"
                    )
                key = canonical_json_bytes(verified)
                if key in seen_sources:
                    raise PackageError(
                        "INVALID_PROVENANCE", f"duplicate contract source: {owner_id}"
                    )
                seen_sources.add(key)
                verified_sources.append(verified)
            for field in fields:
                source_refs = owner[field]["source_refs"]
                if source_refs != sorted(set(source_refs)):
                    raise PackageError(
                        "INVALID_PROVENANCE", f"source ref order: {owner_id}.{field}"
                    )
                if any(index >= len(verified_sources) for index in source_refs):
                    raise PackageError(
                        "INVALID_PROVENANCE", f"source ref range: {owner_id}.{field}"
                    )


def _validate_provenance_inventory(
    authority: dict[str, Any], inventory: dict[str, Any]
) -> list[dict[str, Any]]:
    if inventory.get("schema_version") != (
        "joewrks.semantic-review-provenance-inventory/1.0"
    ):
        raise PackageError("INVALID_PROVENANCE", "provenance inventory version")
    records = inventory.get("records")
    if not isinstance(records, list) or not records:
        raise PackageError("INVALID_PROVENANCE", "empty provenance inventory")
    verified = []
    seen = set()
    for record in records:
        try:
            result = verify_source_ref(authority, record)
        except ProvenanceError as error:
            if isinstance(record, dict) and record.get("active") is True and record.get(
                "source_status"
            ) == "SUPERSEDED":
                raise PackageError("ACTIVE_SUPERSEDED_SOURCE", str(error)) from error
            raise PackageError("INVALID_PROVENANCE", str(error)) from error
        key = canonical_json_bytes(result)
        if key in seen:
            raise PackageError("INVALID_PROVENANCE", "duplicate provenance record")
        seen.add(key)
        verified.append(result)
    return verified


def _validate_brief_profile_consistency(
    brief_bytes: bytes, profile: dict[str, Any]
) -> None:
    try:
        text = brief_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PackageError("BRIEF_HASH_MISMATCH", "brief is not UTF-8") from error
    rows: dict[str, tuple[str, str, str]] = {}
    for line in text.splitlines():
        if not line.startswith("| `FR-"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            raise PackageError(
                "RESPONSIBILITY_PROFILE_HASH_MISMATCH", "invalid brief responsibility row"
            )
        rows[cells[0]] = (cells[1], cells[2], cells[3])
    expected = {}
    for kind in ("action", "lifecycle"):
        for field, rule in profile[kind].items():
            expected[rule["responsibility_rule_id"]] = (
                field,
                rule["completeness_mode"],
                rule["brief_owns_label"],
            )
    if rows != expected:
        raise PackageError(
            "RESPONSIBILITY_PROFILE_HASH_MISMATCH",
            "brief responsibility table differs from profile",
        )


def _validate_exclusion_manifest(value: dict[str, Any]) -> None:
    expected = {
        "previous_reviewer_verdicts_present": False,
        "hidden_answers_present": False,
        "implementation_outcomes_present": False,
        "unrelated_product_evidence_present": False,
    }
    if value != expected:
        raise PackageError(
            "PREVIOUS_VERDICT_EXPOSURE", "invalid exclusion-manifest declaration"
        )


def _semantic_review_identities(
    contract: dict[str, Any], profile: dict[str, Any]
) -> set[str]:
    identities = set()
    for kind, collection_name, id_key in (
        ("action", "actions", "action_id"),
        ("lifecycle", "lifecycles", "lifecycle_id"),
    ):
        for owner in contract.get(collection_name, []):
            if not isinstance(owner, dict) or not isinstance(owner.get(id_key), str):
                continue
            for field in profile[kind]:
                value = owner.get(field)
                if (
                    isinstance(value, dict)
                    and isinstance(value.get("derivation"), dict)
                    and value["derivation"].get("kind") == "REVIEW_REQUIRED"
                ):
                    identities.add(f"{kind}:{owner[id_key]}:{field}")
    return identities


def _validate_identity_inventory(
    contract: dict[str, Any],
    profile: dict[str, Any],
    obligation_index: dict[str, Any],
    inventory: dict[str, Any],
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if inventory.get("schema_version") != (
        "joewrks.semantic-review-identity-inventory/1.0"
    ):
        raise PackageError("IDENTITY_SET_MISMATCH", "identity inventory version")
    if inventory.get("contract_hash") != contract["contract_hash"]:
        raise PackageError("IDENTITY_SET_MISMATCH", "identity contract hash")
    identities = inventory.get("identities")
    if not isinstance(identities, list):
        raise PackageError("IDENTITY_SET_MISMATCH", "identity records")
    observed_order = [item.get("review_identity") for item in identities if isinstance(item, dict)]
    if (
        len(observed_order) != len(identities)
        or observed_order != sorted(set(observed_order))
    ):
        raise PackageError("IDENTITY_SET_MISMATCH", "identity order or duplicates")
    derived = _semantic_review_identities(contract, profile)
    if set(observed_order) != derived:
        raise PackageError("IDENTITY_SET_MISMATCH", "contract REVIEW_REQUIRED set")
    obligations_by_identity: dict[str, list[dict[str, Any]]] = {}
    for obligation in obligation_index["obligations"]:
        identity = (
            f"{obligation['owner_kind']}:{obligation['owner_id']}:{obligation['owning_field']}"
        )
        obligations_by_identity.setdefault(identity, []).append(obligation)
    result = {}
    for record in identities:
        identity = record["review_identity"]
        required = {
            "review_identity",
            "owner_kind",
            "owner_id",
            "semantic_field",
            "semantic_value_hash",
            "provenance_hashes",
            "provenance_set_hash",
            "responsibility_rule_id",
            "completeness_mode",
            "semantic_obligation_ids",
        }
        if set(record) != required:
            raise PackageError("IDENTITY_SET_MISMATCH", f"identity fields: {identity}")
        computed_identity = (
            f"{record['owner_kind']}:{record['owner_id']}:{record['semantic_field']}"
        )
        if computed_identity != identity:
            raise PackageError("IDENTITY_SET_MISMATCH", f"identity tuple: {identity}")
        try:
            expected_rule, expected_mode = expected_responsibility(
                profile, record["owner_kind"], record["semantic_field"]
            )
        except ResponsibilityError as error:
            raise PackageError("RESPONSIBILITY_PROFILE_HASH_MISMATCH", str(error)) from error
        if (record["responsibility_rule_id"], record["completeness_mode"]) != (
            expected_rule,
            expected_mode,
        ):
            raise PackageError(
                "RESPONSIBILITY_PROFILE_HASH_MISMATCH", f"identity rule: {identity}"
            )
        collection = contract[
            "actions" if record["owner_kind"] == "action" else "lifecycles"
        ]
        id_key = "action_id" if record["owner_kind"] == "action" else "lifecycle_id"
        owner = next(
            (item for item in collection if item.get(id_key) == record["owner_id"]), None
        )
        try:
            semantic_value = owner[record["semantic_field"]]["value"]
        except (TypeError, KeyError) as error:
            raise PackageError("IDENTITY_SET_MISMATCH", f"semantic value: {identity}") from error
        if record["semantic_value_hash"] != sha256_bytes(
            canonical_json_bytes(semantic_value)
        ):
            raise PackageError("IDENTITY_SET_MISMATCH", f"semantic hash: {identity}")
        provenance_hashes = record["provenance_hashes"]
        if (
            not isinstance(provenance_hashes, list)
            or not provenance_hashes
            or provenance_hashes != sorted(set(provenance_hashes))
            or record["provenance_set_hash"]
            != sha256_bytes(canonical_json_bytes(provenance_hashes))
        ):
            raise PackageError("INVALID_PROVENANCE", f"identity provenance: {identity}")
        owned_obligations = obligations_by_identity.get(identity, [])
        obligation_ids = sorted(item["obligation_id"] for item in owned_obligations)
        if record["semantic_obligation_ids"] != obligation_ids or not obligation_ids:
            raise PackageError("OBLIGATION_INDEX_HASH_MISMATCH", identity)
        expected_provenance_hashes = sorted(
            {
                sha256_bytes(canonical_json_bytes(reference))
                for obligation in owned_obligations
                for reference in obligation["canonical_refs"]
            }
        )
        if provenance_hashes != expected_provenance_hashes:
            raise PackageError("INVALID_PROVENANCE", f"obligation evidence: {identity}")
        result[identity] = record
    return observed_order, result


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

    def role_json(role: str) -> dict[str, Any]:
        path = role_paths[role]
        value = _read_json(path, file_bytes[path.relative_to(root).as_posix()])
        if not isinstance(value, dict):
            raise PackageError("PACKAGE_HASH_MISMATCH", f"{role} must be an object")
        return value

    authority = role_json("canonical_authority")
    contract = role_json("action_contract")
    contract_hash_value = _verify_contract_hash(contract)
    _validate_contract_schemas(contract)
    _validate_contract_provenance(authority, contract)
    _validate_pr_p01(authority, contract)
    provenance_inventory = role_json("provenance_inventory")
    verified_provenance = _validate_provenance_inventory(
        authority, provenance_inventory
    )
    try:
        responsibility_profile = load_responsibility_profile(
            role_paths["responsibility_profile"]
        )
    except ResponsibilityError as error:
        raise PackageError(
            "RESPONSIBILITY_PROFILE_HASH_MISMATCH", str(error)
        ) from error
    brief_path = role_paths["reviewer_brief"]
    _validate_brief_profile_consistency(
        file_bytes[brief_path.relative_to(root).as_posix()], responsibility_profile
    )
    semantic_obligation_index = role_json("semantic_obligation_index")
    try:
        validate_obligation_index(
            contract, responsibility_profile, semantic_obligation_index
        )
    except ResponsibilityError as error:
        raise PackageError("OBLIGATION_INDEX_HASH_MISMATCH", str(error)) from error
    provenance_keys = {canonical_json_bytes(item) for item in verified_provenance}
    for obligation in semantic_obligation_index["obligations"]:
        for reference in obligation["canonical_refs"]:
            if canonical_json_bytes(reference) not in provenance_keys:
                raise PackageError(
                    "INVALID_PROVENANCE",
                    f"obligation evidence absent: {obligation['obligation_id']}",
                )
    review_identity_inventory = role_json("review_identity_inventory")
    expected_identities, identity_inventory = _validate_identity_inventory(
        contract,
        responsibility_profile,
        semantic_obligation_index,
        review_identity_inventory,
    )
    review_output_schema = role_json("review_output_schema")
    if review_output_schema.get("$id") != (
        "https://joewrks.example/schemas/semantic-review-output-1.0.schema.json"
    ):
        raise PackageError("OUTPUT_SCHEMA_VIOLATION", "review output schema identity")
    output_schema_path = role_paths["review_output_schema"]
    packaged_output_schema_bytes = file_bytes[
        output_schema_path.relative_to(root).as_posix()
    ]
    try:
        frozen_output_schema_bytes = _downstream_schema_path(
            "semantic-review-output.schema.json"
        ).read_bytes()
        _check_schema(review_output_schema)
    except (OSError, SchemaValidationError) as error:
        raise PackageError("OUTPUT_SCHEMA_VIOLATION", str(error)) from error
    if packaged_output_schema_bytes != frozen_output_schema_bytes:
        raise PackageError(
            "OUTPUT_SCHEMA_VIOLATION", "review output schema differs from frozen bytes"
        )
    exclusion_manifest = role_json("exclusion_manifest")
    _validate_exclusion_manifest(exclusion_manifest)

    return {
        "root": root,
        "manifest": manifest,
        "previous_reviewer_verdicts_present": False,
        "reviewer_input_manifest_hash": observed_manifest_hash,
        "reviewer_input_package_hash": package_hash(observed_manifest_hash, files),
        "reviewer_brief_hash": role_hashes["reviewer_brief"],
        "contract": contract,
        "contract_hash": contract_hash_value,
        "responsibility_profile": responsibility_profile,
        "responsibility_profile_hash": role_hashes["responsibility_profile"],
        "semantic_obligation_index": semantic_obligation_index,
        "semantic_obligation_index_hash": role_hashes["semantic_obligation_index"],
        "review_identity_inventory": review_identity_inventory,
        "review_identity_inventory_hash": role_hashes["review_identity_inventory"],
        "expected_identities": expected_identities,
        "identity_inventory": identity_inventory,
        "review_output_schema": review_output_schema,
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
