"""Hash projections and structural validation for action-conformance/2.0."""

import copy
import re

from .authority import sha256_json
from .derivation import (
    RESPONSIBILITY_PROFILE_ID,
    derive_semantic_field,
    load_responsibility_profile,
    responsibility_profile_digest,
)
from .seeds import source_seed_inventory_digest, source_seed_index


COMPILER_ID = "joewrks-product-definition/downstream-v2"
COMPILER_VERSION = "core-semantic-closure-v2-m5.1"
CONTRACT_VERSION = "joewrks.action-conformance/2.0"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_SCOPE_REF = re.compile(r"^(?:REQ|SURF|SCR)-[^\s]+$")
_TOP_LEVEL = {
    "contract_schema_version", "compiler", "source_authority",
    "responsibility_profile", "scope_commitments", "source_seed_inventory",
    "actions", "lifecycles", "semantic_debt", "handoff_status",
    "semantic_assurance", "semantic_contract_hash", "artifact_hash",
}
_AUTHORITY_KEYS = {
    "state_schema_version", "product_slug", "approved_revision",
    "approved_definition_digest", "approved_manifest_digest",
    "product_binding_contract", "ux_binding_contract", "snapshot_state_sha256",
    "consumed_seed_inventory_digest",
}
_SEED_KEYS = {
    "seed_key", "location", "record_id", "record_type", "pointer",
    "value_sha256", "source_status", "value",
}
_DEBT_KEYS = {
    "direct_authority_count", "machine_derived_count", "review_required_count",
    "authority_gap_count", "direct_authority_fields", "machine_derived_fields",
    "review_required_fields", "authority_gaps",
}


def semantic_contract_projection(contract: dict[str, object]) -> dict[str, object]:
    """Return the semantic identity projection, excluding observation-only state."""
    if not isinstance(contract, dict):
        raise ValueError("INVALID_ACTION_CONTRACT_V2")
    projection = copy.deepcopy(contract)
    projection.pop("semantic_contract_hash", None)
    projection.pop("artifact_hash", None)
    authority = projection.get("source_authority")
    if isinstance(authority, dict):
        authority.pop("snapshot_state_sha256", None)
    return projection


def semantic_contract_hash(contract: dict[str, object]) -> str:
    return sha256_json(semantic_contract_projection(contract))


def artifact_hash(contract: dict[str, object]) -> str:
    if not isinstance(contract, dict):
        raise ValueError("INVALID_ACTION_CONTRACT_V2")
    projection = copy.deepcopy(contract)
    projection.pop("artifact_hash", None)
    return sha256_json(projection)


def _normalized_field(derived: dict[str, object]) -> dict[str, object]:
    spec = derived["derivation"]
    kind = spec["kind"]
    if kind == "DIRECT_AUTHORITY":
        derivation = {"kind": kind}
    elif kind == "MACHINE_DERIVED":
        derivation = {key: copy.deepcopy(value) for key, value in spec.items() if key != "source_seed_ref"}
    else:
        derivation = {
            "kind": kind,
            "why_structuring_is_insufficient": spec["why_structuring_is_insufficient"],
            "interpretation_scope": spec["interpretation_scope"],
        }
    return {
        "value": copy.deepcopy(derived["value"]),
        "source_seed_refs": list(derived["source_seed_refs"]),
        "derivation": derivation,
    }


def _definition_spec(field: dict[str, object]) -> dict[str, object]:
    derivation = field.get("derivation")
    refs = field.get("source_seed_refs")
    if not isinstance(derivation, dict) or not isinstance(refs, list):
        raise ValueError("INVALID_SEMANTIC_FIELD")
    kind = derivation.get("kind")
    if kind == "DIRECT_AUTHORITY" and set(derivation) == {"kind"} and len(refs) == 1:
        return {"kind": kind, "source_seed_ref": refs[0]}
    if kind == "MACHINE_DERIVED" and len(refs) == 1:
        return {**copy.deepcopy(derivation), "source_seed_ref": refs[0]}
    if kind == "REVIEW_REQUIRED":
        return {
            **copy.deepcopy(derivation),
            "source_seed_refs": list(refs),
            "proposed_value": copy.deepcopy(field.get("value")),
        }
    raise ValueError("INVALID_SEMANTIC_FIELD")


def validate_action_contract_v2(contract: dict[str, object]) -> list[dict[str, str]]:
    """Return deterministic structural, provenance, responsibility, and hash errors."""
    errors: list[dict[str, str]] = []

    def add(path: str, message: str):
        errors.append({"path": path, "message": message})

    if not isinstance(contract, dict):
        return [{"path": "/", "message": "contract must be an object"}]
    if set(contract) != _TOP_LEVEL:
        add("/", "contract has missing or extra top-level fields")
    if contract.get("contract_schema_version") != CONTRACT_VERSION:
        add("/contract_schema_version", "unsupported contract schema version")
    if contract.get("compiler") != {"id": COMPILER_ID, "version": COMPILER_VERSION}:
        add("/compiler", "compiler identity does not match")

    authority = contract.get("source_authority")
    if not isinstance(authority, dict) or set(authority) != _AUTHORITY_KEYS:
        add("/source_authority", "source authority shape does not match")
        authority = {}
    for key in (
        "approved_definition_digest", "approved_manifest_digest", "snapshot_state_sha256",
        "consumed_seed_inventory_digest",
    ):
        if _HASH.fullmatch(authority.get(key, "")) is None:
            add(f"/source_authority/{key}", "must be a lowercase SHA-256")
    for key in ("product_binding_contract", "ux_binding_contract"):
        binding = authority.get(key)
        if (
            not isinstance(binding, dict)
            or set(binding) != {"contract_id", "version", "digest"}
            or not isinstance(binding.get("contract_id"), str)
            or not binding["contract_id"]
            or not isinstance(binding.get("version"), str)
            or not binding["version"]
            or _HASH.fullmatch(binding.get("digest", "")) is None
        ):
            add(f"/source_authority/{key}", "binding identity is invalid")

    responsibility = contract.get("responsibility_profile")
    if responsibility != {
        "profile_id": RESPONSIBILITY_PROFILE_ID,
        "digest": responsibility_profile_digest(),
    }:
        add("/responsibility_profile", "responsibility profile identity does not match")

    commitments = contract.get("scope_commitments")
    commitment_ids = []
    if not isinstance(commitments, list):
        add("/scope_commitments", "scope commitments must be an array")
        commitments = []
    for index, commitment in enumerate(commitments):
        path = f"/scope_commitments/{index}"
        if not isinstance(commitment, dict) or set(commitment) != {
            "record_id", "record_type", "record_sha256"
        }:
            add(path, "scope commitment shape does not match")
            continue
        record_id = commitment.get("record_id")
        record_type = commitment.get("record_type")
        if (
            not isinstance(record_id, str)
            or _SCOPE_REF.fullmatch(record_id) is None
            or record_type != record_id.split("-", 1)[0]
            or _HASH.fullmatch(commitment.get("record_sha256", "")) is None
        ):
            add(path, "scope commitment identity is invalid")
        commitment_ids.append(record_id)
    if commitment_ids != sorted(set(commitment_ids)):
        add("/scope_commitments", "scope commitments must be sorted and unique")

    inventory = contract.get("source_seed_inventory")
    seed_keys = []
    if not isinstance(inventory, list):
        add("/source_seed_inventory", "source seed inventory must be an array")
        inventory = []
    for index, seed in enumerate(inventory):
        path = f"/source_seed_inventory/{index}"
        if not isinstance(seed, dict) or set(seed) != _SEED_KEYS:
            add(path, "source seed shape does not match")
            continue
        seed_keys.append(seed.get("seed_key"))
        if (
            not isinstance(seed.get("seed_key"), str)
            or not seed["seed_key"].startswith("SEED-")
            or _HASH.fullmatch(seed.get("value_sha256", "")) is None
            or seed.get("source_status") != "CURRENT"
        ):
            add(path, "source seed identity is invalid")
        try:
            if sha256_json(seed.get("value")) != seed.get("value_sha256"):
                add(path, "source seed value hash does not match")
        except (TypeError, ValueError):
            add(path, "source seed value is not canonical JSON")
    if seed_keys != sorted(set(seed_keys)):
        add("/source_seed_inventory", "source seed inventory must be sorted and unique")
    try:
        if authority.get("consumed_seed_inventory_digest") != source_seed_inventory_digest(inventory):
            add("/source_authority/consumed_seed_inventory_digest", "consumed seed digest does not match")
        seeds = source_seed_index(inventory)
    except (TypeError, ValueError):
        seeds = {}
        add("/source_seed_inventory", "source seed inventory cannot be indexed")

    profile = load_responsibility_profile()
    used_scope_refs = set()
    used_seed_refs = set()
    derived_paths = []
    for collection_name, id_key, field_kind, profile_key, expected_item_keys in (
        ("actions", "action_id", "ACTION", "action_fields", {"action_id", "authority_scope_refs", "ux_action_locator", "fields"}),
        ("lifecycles", "lifecycle_id", "LIFECYCLE", "lifecycle_fields", {"lifecycle_id", "authority_scope_refs", "fields"}),
    ):
        collection = contract.get(collection_name)
        if not isinstance(collection, list):
            add(f"/{collection_name}", "collection must be an array")
            continue
        ids = []
        for item_index, item in enumerate(collection):
            item_path = f"/{collection_name}/{item_index}"
            if not isinstance(item, dict) or set(item) != expected_item_keys:
                add(item_path, "item shape does not match")
                continue
            item_id = item.get(id_key)
            ids.append(item_id)
            refs = item.get("authority_scope_refs")
            if (
                not isinstance(item_id, str) or not item_id
                or not isinstance(refs, list) or not refs
                or any(not isinstance(ref, str) or _SCOPE_REF.fullmatch(ref) is None for ref in refs)
                or refs != sorted(set(refs))
                or any(ref not in commitment_ids for ref in refs)
            ):
                add(item_path, "item identity or authority scope refs are invalid")
                continue
            used_scope_refs.update(refs)
            context = {"authority_scope_refs": refs, "current_scope_refs": commitment_ids}
            if collection_name == "actions":
                locator = item.get("ux_action_locator")
                if locator is not None:
                    if (
                        not isinstance(locator, dict)
                        or set(locator) != {"screen_ref", "action_key"}
                        or locator.get("screen_ref") not in refs
                        or not isinstance(locator.get("action_key"), str)
                        or not locator["action_key"]
                    ):
                        add(f"{item_path}/ux_action_locator", "UX action locator is invalid")
                    else:
                        context["ux_action_locator"] = locator
            fields = item.get("fields")
            expected_fields = set(profile[profile_key])
            if not isinstance(fields, dict) or set(fields) != expected_fields:
                add(f"{item_path}/fields", "semantic field inventory does not match")
                continue
            for field_name in sorted(expected_fields):
                field = fields[field_name]
                field_path = f"{collection_name}/{item_id}/{field_name}"
                try:
                    spec = _definition_spec(field)
                    recomputed = derive_semantic_field(
                        spec, field_name=field_name, field_kind=field_kind,
                        context=context, seeds=seeds, profile=profile,
                    )
                    if _normalized_field(recomputed) != field:
                        raise ValueError("semantic field is not the recomputed output")
                    used_seed_refs.update(field["source_seed_refs"])
                    derived_paths.append((field_path, field["derivation"]["kind"]))
                except (KeyError, TypeError, ValueError) as error:
                    add(f"{item_path}/fields/{field_name}", str(error))
        if ids != sorted(set(ids)):
            add(f"/{collection_name}", "IDs must be sorted and unique")

    if set(commitment_ids) != used_scope_refs:
        add("/scope_commitments", "scope commitments must equal referenced scope records")
    if set(seed_keys) != used_seed_refs:
        add("/source_seed_inventory", "source seed inventory must equal consumed seeds")

    debt = contract.get("semantic_debt")
    if not isinstance(debt, dict) or set(debt) != _DEBT_KEYS:
        add("/semantic_debt", "semantic debt shape does not match")
    else:
        expected_fields = {
            "DIRECT_AUTHORITY": sorted(path for path, kind in derived_paths if kind == "DIRECT_AUTHORITY"),
            "MACHINE_DERIVED": sorted(path for path, kind in derived_paths if kind == "MACHINE_DERIVED"),
            "REVIEW_REQUIRED": sorted(path for path, kind in derived_paths if kind == "REVIEW_REQUIRED"),
        }
        for kind, prefix in (
            ("DIRECT_AUTHORITY", "direct_authority"),
            ("MACHINE_DERIVED", "machine_derived"),
            ("REVIEW_REQUIRED", "review_required"),
        ):
            if debt.get(f"{prefix}_fields") != expected_fields[kind] or debt.get(f"{prefix}_count") != len(expected_fields[kind]):
                add("/semantic_debt", f"{prefix} inventory does not match fields")
        if debt.get("authority_gap_count") != 0 or debt.get("authority_gaps") != []:
            add("/semantic_debt", "production contract cannot contain authority gaps")
        reviews = len(expected_fields["REVIEW_REQUIRED"])
        expected_status = "AUTHORITY_READY_REVIEW_PENDING" if reviews else "AUTHORITY_READY_MACHINE_VERIFIED"
        expected_assurance = {"status": "NOT_MEASURED" if reviews else "NOT_REQUIRED"}
        if contract.get("handoff_status") != expected_status:
            add("/handoff_status", "handoff status does not match semantic debt")
        if contract.get("semantic_assurance") != expected_assurance:
            add("/semantic_assurance", "semantic assurance does not match semantic debt")

    for key in ("semantic_contract_hash", "artifact_hash"):
        if _HASH.fullmatch(contract.get(key, "")) is None:
            add(f"/{key}", "must be a lowercase SHA-256")
    try:
        if contract.get("semantic_contract_hash") != semantic_contract_hash(contract):
            add("/semantic_contract_hash", "semantic contract hash does not match")
        if contract.get("artifact_hash") != artifact_hash(contract):
            add("/artifact_hash", "artifact hash does not match")
    except (TypeError, ValueError):
        add("/", "contract is not canonical JSON")
    return sorted(errors, key=lambda error: (error["path"], error["message"]))
