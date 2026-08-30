"""Deterministic semantic-review/2.1 package construction and validation."""

import copy
import re

from downstream_v2.authority import sha256_json

from ..contracts import validate_action_contract_v21
from ..field_refs import canonical_field_ref, parse_canonical_field_ref
from ..identity import ACTION_CONTRACT_VERSION, SEMANTIC_REVIEW_VERSION
from ..responsibility import (
    load_responsibility_profile_v21,
    responsibility_profile_digest_v21,
)


RELIABILITY_STATUS = "NOT_MEASURED"
_HASH = re.compile(r"^[0-9a-f]{64}$")
_SEED_KEY = re.compile(r"^SEED-[0-9a-f]{24}$")
_SCOPE_REF = re.compile(r"^(?:REQ|SURF|SCR)-[^\s]+$")
_SEED_KEYS = {
    "seed_key",
    "location",
    "record_id",
    "record_type",
    "pointer",
    "value_sha256",
    "source_status",
    "value",
}
_LOCATION_KEYS = {"scope", "owner_ref", "axis", "pack_id", "action_key"}
_SEED_SCOPES = {"CORE", "GRILL", "UX_STATE", "UX_ACTION"}
_PACKAGE_KEYS = {
    "review_schema_version",
    "reliability_status",
    "source_semantic_contract_hash",
    "source_definition_digest",
    "responsibility_profile",
    "review_obligations",
    "package_hash",
}
_OBLIGATION_KEYS = {
    "obligation_id",
    "field_path",
    "proposed_value",
    "proposed_value_sha256",
    "source_seed_refs",
    "source_seeds",
    "why_structuring_is_insufficient",
    "interpretation_scope",
}


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _hash(value: object) -> str | None:
    try:
        return sha256_json(value)
    except (TypeError, ValueError, RecursionError):
        return None


def _package_content(package: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in package.items() if key != "package_hash"}


def _valid_profile(profile: object) -> bool:
    return profile == {
        "profile_id": "joewrks.downstream-responsibility/2.0",
        "digest": responsibility_profile_digest_v21(),
    }


def _permitted_review_field(field_path: object) -> bool:
    try:
        collection, _item_id, field_name = parse_canonical_field_ref(field_path)
    except ValueError:
        return False
    group_name = "action_fields" if collection == "actions" else "lifecycle_fields"
    profile = load_responsibility_profile_v21()
    entry = profile[group_name].get(field_name)
    return (
        isinstance(entry, dict)
        and "REVIEW_REQUIRED" in entry.get("allowed_derivations", [])
    )


def _valid_seed_snapshot(seed: object, source_ref: object) -> bool:
    if (
        not isinstance(seed, dict)
        or set(seed) != _SEED_KEYS
        or not isinstance(source_ref, str)
        or _SEED_KEY.fullmatch(source_ref) is None
        or seed.get("seed_key") != source_ref
        or not isinstance(seed.get("record_id"), str)
        or not seed["record_id"].strip()
        or not isinstance(seed.get("record_type"), str)
        or not seed["record_type"].strip()
        or not isinstance(seed.get("pointer"), str)
        or not seed["pointer"].startswith("/")
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
        or _SCOPE_REF.fullmatch(location["owner_ref"]) is None
        or not isinstance(location.get("axis"), str)
        or not location["axis"].strip()
        or location.get("pack_id") is not None
        and (
            not isinstance(location.get("pack_id"), str)
            or not location["pack_id"].strip()
        )
        or location.get("action_key") is not None
        and (
            not isinstance(location.get("action_key"), str)
            or not location["action_key"].strip()
        )
    ):
        return False
    if location["scope"] == "GRILL" and not location.get("pack_id"):
        return False
    if location["scope"] == "UX_ACTION" and not location.get("action_key"):
        return False
    value_hash = _hash(seed.get("value"))
    if value_hash is None or value_hash != seed["value_sha256"]:
        return False
    identity_hash = _hash(
        {
            "location": location,
            "record_id": seed["record_id"],
            "pointer": seed["pointer"],
            "value_sha256": value_hash,
        }
    )
    return (
        identity_hash is not None
        and seed["seed_key"] == "SEED-" + identity_hash[:24]
    )


def _review_fields(contract: dict[str, object]):
    for collection, id_key in (
        ("actions", "action_id"),
        ("lifecycles", "lifecycle_id"),
    ):
        for item in contract[collection]:
            for field_name, field in item["fields"].items():
                if field["derivation"]["kind"] == "REVIEW_REQUIRED":
                    yield (
                        f"{collection}/{item[id_key]}/{field_name}",
                        canonical_field_ref(collection, item[id_key], field_name),
                        field,
                    )


def _require_contract(contract: object) -> dict[str, object]:
    if (
        not isinstance(contract, dict)
        or contract.get("contract_schema_version") != ACTION_CONTRACT_VERSION
        or validate_action_contract_v21(contract)
    ):
        raise ValueError("INVALID_ACTION_CONTRACT_V21")
    return contract


def validate_semantic_review_package_v21(
    package: object,
) -> list[dict[str, str]]:
    """Return deterministic identity, provenance, and hash errors."""
    errors: list[dict[str, str]] = []

    def add(path: str, message: str):
        errors.append({"path": path, "message": message})

    if not isinstance(package, dict):
        return [{"path": "/", "message": "review package must be an object"}]
    if set(package) != _PACKAGE_KEYS:
        add("/", "review package has missing or extra fields")
    if package.get("review_schema_version") != SEMANTIC_REVIEW_VERSION:
        add("/review_schema_version", "unsupported review schema version")
    if package.get("reliability_status") != RELIABILITY_STATUS:
        add("/reliability_status", "reliability must be NOT_MEASURED")
    if not _valid_profile(package.get("responsibility_profile")):
        add("/responsibility_profile", "responsibility profile identity does not match")
    for key in (
        "source_semantic_contract_hash",
        "source_definition_digest",
        "package_hash",
    ):
        if not _is_hash(package.get(key)):
            add(f"/{key}", "must be a lowercase SHA-256")

    obligations = package.get("review_obligations")
    seen_ids: list[str] = []
    field_paths: list[str] = []
    if not isinstance(obligations, list) or not obligations:
        add("/review_obligations", "must be a nonempty array")
        obligations = []
    for index, obligation in enumerate(obligations):
        path = f"/review_obligations/{index}"
        if not isinstance(obligation, dict) or set(obligation) != _OBLIGATION_KEYS:
            add(path, "obligation has missing or extra fields")
            continue
        obligation_id = obligation.get("obligation_id")
        if (
            not isinstance(obligation_id, str)
            or re.fullmatch(r"REVIEW-[0-9a-f]{24}", obligation_id) is None
        ):
            add(f"{path}/obligation_id", "invalid obligation ID")
        elif obligation_id in seen_ids:
            add(f"{path}/obligation_id", "duplicate obligation ID")
        else:
            seen_ids.append(obligation_id)

        field_path = obligation.get("field_path")
        if not _permitted_review_field(field_path):
            add(f"{path}/field_path", "field is not review-permitted by profile 2.0")
        elif field_path in field_paths:
            add(f"{path}/field_path", "duplicate field path")
        else:
            field_paths.append(field_path)

        proposed_value_hash = _hash(obligation.get("proposed_value"))
        if (
            not _is_hash(obligation.get("proposed_value_sha256"))
            or proposed_value_hash is None
            or proposed_value_hash != obligation.get("proposed_value_sha256")
        ):
            add(f"{path}/proposed_value_sha256", "proposed value hash does not match")

        refs = obligation.get("source_seed_refs")
        seeds = obligation.get("source_seeds")
        valid_refs = (
            isinstance(refs, list)
            and bool(refs)
            and all(
                isinstance(ref, str) and _SEED_KEY.fullmatch(ref) is not None
                for ref in refs
            )
            and refs == sorted(set(refs))
        )
        if not valid_refs:
            add(
                f"{path}/source_seed_refs",
                "must be sorted unique nonempty source seed references",
            )
        if (
            not isinstance(seeds, list)
            or not isinstance(refs, list)
            or len(seeds) != len(refs)
        ):
            add(f"{path}/source_seeds", "must align with source seed references")
        elif any(
            not _valid_seed_snapshot(seed, ref)
            for ref, seed in zip(refs, seeds)
        ):
            add(
                f"{path}/source_seeds",
                "seed snapshots do not match exact source seed identities",
            )

        if (
            isinstance(obligation_id, str)
            and isinstance(field_path, str)
            and proposed_value_hash is not None
            and valid_refs
        ):
            identity_hash = _hash(
                {
                    "field_path": field_path,
                    "proposed_value_sha256": proposed_value_hash,
                    "source_seed_refs": refs,
                }
            )
            if (
                identity_hash is None
                or obligation_id != "REVIEW-" + identity_hash[:24]
            ):
                add(
                    f"{path}/obligation_id",
                    "does not match the deterministic obligation identity",
                )
        for key in (
            "why_structuring_is_insufficient",
            "interpretation_scope",
        ):
            if (
                not isinstance(obligation.get(key), str)
                or not obligation[key].strip()
            ):
                add(f"{path}/{key}", "must be meaningful")

    if field_paths != sorted(field_paths):
        add("/review_obligations", "obligations must have sorted field paths")
    if _is_hash(package.get("package_hash")):
        package_hash = _hash(_package_content(package))
        if package_hash is None:
            add("/package_hash", "package is not canonical JSON")
        elif package["package_hash"] != package_hash:
            add("/package_hash", "package hash does not match")
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


def build_semantic_review_package_v21(
    contract: dict[str, object],
) -> dict[str, object] | None:
    """Build the review-only projection of a valid action-conformance/2.1."""
    contract = _require_contract(contract)
    review_fields = list(_review_fields(contract))
    expected_paths = contract["semantic_debt"]["review_required_fields"]
    raw_paths = sorted(
        raw_path for raw_path, _field_path, _field in review_fields
    )
    if raw_paths != expected_paths:
        raise ValueError("INVALID_ACTION_CONTRACT_V21")
    review_fields.sort(key=lambda item: item[1])
    if any(
        not _permitted_review_field(field_path)
        for _raw_path, field_path, _field in review_fields
    ):
        raise ValueError("INVALID_ACTION_CONTRACT_V21")
    if not review_fields:
        return None

    inventory = {
        seed["seed_key"]: seed for seed in contract["source_seed_inventory"]
    }
    obligations = []
    for _raw_path, field_path, field in review_fields:
        refs = list(field["source_seed_refs"])
        proposed_value_hash = sha256_json(field["value"])
        identity = {
            "field_path": field_path,
            "proposed_value_sha256": proposed_value_hash,
            "source_seed_refs": refs,
        }
        obligations.append(
            {
                "obligation_id": "REVIEW-" + sha256_json(identity)[:24],
                "field_path": field_path,
                "proposed_value": copy.deepcopy(field["value"]),
                "proposed_value_sha256": proposed_value_hash,
                "source_seed_refs": refs,
                "source_seeds": [copy.deepcopy(inventory[ref]) for ref in refs],
                "why_structuring_is_insufficient": field["derivation"][
                    "why_structuring_is_insufficient"
                ],
                "interpretation_scope": field["derivation"]["interpretation_scope"],
            }
        )

    package = {
        "review_schema_version": SEMANTIC_REVIEW_VERSION,
        "reliability_status": RELIABILITY_STATUS,
        "source_semantic_contract_hash": contract["semantic_contract_hash"],
        "source_definition_digest": contract["source_authority"][
            "approved_definition_digest"
        ],
        "responsibility_profile": copy.deepcopy(contract["responsibility_profile"]),
        "review_obligations": obligations,
    }
    package["package_hash"] = sha256_json(package)
    if validate_semantic_review_package_v21(package):
        raise ValueError("INVALID_SEMANTIC_REVIEW_PACKAGE_V21")
    return package


__all__ = [
    "RELIABILITY_STATUS",
    "build_semantic_review_package_v21",
    "validate_semantic_review_package_v21",
]
