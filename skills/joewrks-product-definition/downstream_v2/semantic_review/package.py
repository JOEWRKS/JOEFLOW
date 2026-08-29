"""Deterministic semantic-review/2.0 input package construction."""

import copy
import re

from ..authority import sha256_json
from ..contracts import CONTRACT_VERSION, validate_action_contract_v2
from ..derivation import RESPONSIBILITY_PROFILE_ID, responsibility_profile_digest


SEMANTIC_REVIEW_VERSION = "joewrks.semantic-review/2.0"
RELIABILITY_STATUS = "NOT_MEASURED"
_FIELD_PATH = re.compile(r"^(actions|lifecycles)/([^/\s]+)/([^/\s]+)$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_SEED_KEYS = {
    "seed_key", "location", "record_id", "record_type", "pointer",
    "value_sha256", "source_status", "value",
}
_LOCATION_KEYS = {"scope", "owner_ref", "axis", "pack_id", "action_key"}
_SEED_SCOPES = {"CORE", "GRILL", "UX_STATE", "UX_ACTION"}


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _hash(value: object) -> str | None:
    try:
        return sha256_json(value)
    except (TypeError, ValueError):
        return None


def _review_fields(contract: dict[str, object]):
    for collection, id_key in (("actions", "action_id"), ("lifecycles", "lifecycle_id")):
        for item in contract[collection]:
            for field_name, field in item["fields"].items():
                if field["derivation"]["kind"] == "REVIEW_REQUIRED":
                    yield (
                        f"{collection}/{item[id_key]}/{field_name}",
                        field,
                    )


def _require_contract(contract: object) -> dict[str, object]:
    if not isinstance(contract, dict) or contract.get("contract_schema_version") != CONTRACT_VERSION:
        raise ValueError("INVALID_ACTION_CONTRACT_V2")
    if validate_action_contract_v2(contract):
        raise ValueError("INVALID_ACTION_CONTRACT_V2")
    return contract


def _package_content(package: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in package.items() if key != "package_hash"}


def _valid_profile(profile: object) -> bool:
    return profile == {
        "profile_id": RESPONSIBILITY_PROFILE_ID,
        "digest": responsibility_profile_digest(),
    }


def _valid_seed_snapshot(seed: object, source_ref: object) -> bool:
    if (
        not isinstance(seed, dict)
        or set(seed) != _SEED_KEYS
        or not isinstance(source_ref, str)
        or seed.get("seed_key") != source_ref
        or not isinstance(seed.get("record_id"), str)
        or not seed["record_id"]
        or not isinstance(seed.get("record_type"), str)
        or not seed["record_type"]
        or not isinstance(seed.get("pointer"), str)
        or not seed["pointer"]
        or seed.get("source_status") != "CURRENT"
        or not _is_hash(seed.get("value_sha256"))
    ):
        return False
    location = seed.get("location")
    if (
        not isinstance(location, dict)
        or set(location) != _LOCATION_KEYS
        or location.get("scope") not in _SEED_SCOPES
        or not isinstance(location.get("owner_ref"), str)
        or not location["owner_ref"]
        or not isinstance(location.get("axis"), str)
        or not location["axis"]
        or location.get("pack_id") is not None and not isinstance(location.get("pack_id"), str)
        or location.get("action_key") is not None and not isinstance(location.get("action_key"), str)
    ):
        return False
    if location["scope"] == "GRILL" and not location.get("pack_id"):
        return False
    if location["scope"] == "UX_ACTION" and not location.get("action_key"):
        return False
    value_hash = _hash(seed.get("value"))
    if value_hash is None or value_hash != seed["value_sha256"]:
        return False
    expected_key_hash = _hash({
        "location": location,
        "record_id": seed["record_id"],
        "pointer": seed["pointer"],
        "value_sha256": value_hash,
    })
    return expected_key_hash is not None and seed["seed_key"] == "SEED-" + expected_key_hash[:24]


def validate_semantic_review_package(review_package: object) -> list[dict[str, str]]:
    """Return structural/hash errors for a semantic-review input package."""
    errors: list[dict[str, str]] = []

    def add(path: str, message: str):
        errors.append({"path": path, "message": message})

    if not isinstance(review_package, dict):
        return [{"path": "/", "message": "review package must be an object"}]
    required = {
        "review_schema_version", "reliability_status", "source_semantic_contract_hash",
        "source_definition_digest", "responsibility_profile", "review_obligations",
        "package_hash",
    }
    if set(review_package) != required:
        add("/", "review package has missing or extra fields")
    if review_package.get("review_schema_version") != SEMANTIC_REVIEW_VERSION:
        add("/review_schema_version", "unsupported review schema version")
    if review_package.get("reliability_status") != RELIABILITY_STATUS:
        add("/reliability_status", "reliability must be NOT_MEASURED")
    if not _valid_profile(review_package.get("responsibility_profile")):
        add("/responsibility_profile", "responsibility profile identity does not match")
    for key in ("source_semantic_contract_hash", "source_definition_digest", "package_hash"):
        if not _is_hash(review_package.get(key)):
            add(f"/{key}", "must be a lowercase SHA-256")
    obligations = review_package.get("review_obligations")
    seen_ids: list[str] = []
    field_paths: list[str] = []
    if not isinstance(obligations, list) or not obligations:
        add("/review_obligations", "must be a nonempty array")
        obligations = []
    for index, obligation in enumerate(obligations):
        path = f"/review_obligations/{index}"
        required_obligation = {
            "obligation_id", "field_path", "proposed_value", "proposed_value_sha256",
            "source_seed_refs", "source_seeds", "why_structuring_is_insufficient",
            "interpretation_scope",
        }
        if not isinstance(obligation, dict) or set(obligation) != required_obligation:
            add(path, "obligation has missing or extra fields")
            continue
        obligation_id = obligation.get("obligation_id")
        if not isinstance(obligation_id, str) or re.fullmatch(r"REVIEW-[0-9a-f]{24}", obligation_id) is None:
            add(f"{path}/obligation_id", "invalid obligation ID")
        elif obligation_id in seen_ids:
            add(f"{path}/obligation_id", "duplicate obligation ID")
        else:
            seen_ids.append(obligation_id)
        field_path = obligation.get("field_path")
        if not isinstance(field_path, str) or _FIELD_PATH.fullmatch(field_path) is None:
            add(f"{path}/field_path", "invalid field path")
        elif field_path in field_paths:
            add(f"{path}/field_path", "duplicate field path")
        else:
            field_paths.append(field_path)
        proposed_value_hash = _hash(obligation.get("proposed_value"))
        if not _is_hash(obligation.get("proposed_value_sha256")) or (
            proposed_value_hash is None
            or proposed_value_hash != obligation.get("proposed_value_sha256")
        ):
            add(f"{path}/proposed_value_sha256", "proposed value hash does not match")
        refs = obligation.get("source_seed_refs")
        seeds = obligation.get("source_seeds")
        valid_refs = (
            isinstance(refs, list)
            and bool(refs)
            and all(isinstance(ref, str) and ref for ref in refs)
            and len(refs) == len(set(refs))
        )
        if not valid_refs:
            add(f"{path}/source_seed_refs", "must be nonempty source seed references")
        if not isinstance(seeds, list) or not isinstance(refs, list) or len(seeds) != len(refs):
            add(f"{path}/source_seeds", "must align with source seed references")
        elif any(not _valid_seed_snapshot(seed, ref) for ref, seed in zip(refs, seeds)):
            add(f"{path}/source_seeds", "seed snapshots do not match exact source seed identities")
        if (
            isinstance(obligation_id, str)
            and isinstance(field_path, str)
            and proposed_value_hash is not None
            and valid_refs
        ):
            expected_id_hash = _hash({
                "field_path": field_path,
                "proposed_value_sha256": proposed_value_hash,
                "source_seed_refs": refs,
            })
            if expected_id_hash is None or obligation_id != "REVIEW-" + expected_id_hash[:24]:
                add(f"{path}/obligation_id", "does not match the deterministic obligation identity")
        for key in ("why_structuring_is_insufficient", "interpretation_scope"):
            if not isinstance(obligation.get(key), str) or not obligation[key].strip():
                add(f"{path}/{key}", "must be meaningful")
    if field_paths != sorted(field_paths):
        add("/review_obligations", "obligations must have sorted field paths")
    if _is_hash(review_package.get("package_hash")):
        try:
            if review_package["package_hash"] != _hash(_package_content(review_package)):
                add("/package_hash", "package hash does not match")
        except (TypeError, ValueError):
            add("/package_hash", "package is not canonical JSON")
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


def build_semantic_review_package(contract: dict[str, object]) -> dict[str, object] | None:
    """Build a review-only projection of a valid materialized v2 contract."""
    contract = _require_contract(contract)
    review_fields = sorted(_review_fields(contract), key=lambda item: item[0])
    expected_paths = contract["semantic_debt"]["review_required_fields"]
    if [path for path, _field in review_fields] != expected_paths:
        raise ValueError("INVALID_ACTION_CONTRACT_V2")
    if not review_fields:
        return None
    inventory = {seed["seed_key"]: seed for seed in contract["source_seed_inventory"]}
    obligations = []
    for field_path, field in review_fields:
        refs = list(field["source_seed_refs"])
        value_hash = sha256_json(field["value"])
        obligations.append({
            "obligation_id": "REVIEW-" + sha256_json({
                "field_path": field_path,
                "proposed_value_sha256": value_hash,
                "source_seed_refs": refs,
            })[:24],
            "field_path": field_path,
            "proposed_value": copy.deepcopy(field["value"]),
            "proposed_value_sha256": value_hash,
            "source_seed_refs": refs,
            "source_seeds": [copy.deepcopy(inventory[ref]) for ref in refs],
            "why_structuring_is_insufficient": field["derivation"]["why_structuring_is_insufficient"],
            "interpretation_scope": field["derivation"]["interpretation_scope"],
        })
    package = {
        "review_schema_version": SEMANTIC_REVIEW_VERSION,
        "reliability_status": RELIABILITY_STATUS,
        "source_semantic_contract_hash": contract["semantic_contract_hash"],
        "source_definition_digest": contract["source_authority"]["approved_definition_digest"],
        "responsibility_profile": copy.deepcopy(contract["responsibility_profile"]),
        "review_obligations": obligations,
    }
    package["package_hash"] = sha256_json(package)
    if validate_semantic_review_package(package):
        raise ValueError("INVALID_SEMANTIC_REVIEW_PACKAGE")
    return package
