"""Hash projections and validation for action-conformance/2.1."""

import copy
import re

from authority_binding_v2 import BindingError, binding_contract_identity
from downstream_v2.authority import sha256_json
from downstream_v2.seeds import source_seed_inventory_digest, source_seed_index

from .derivation import derive_semantic_field_v21, seed_matches_selector_v21
from .field_refs import canonical_field_ref
from .identity import ACTION_CONTRACT_VERSION, RESPONSIBILITY_PROFILE_ID
from .responsibility import (
    _validate_responsibility_profile_v21,
    load_responsibility_profile_v21,
    responsibility_profile_digest_v21,
)


COMPILER_ID = "joewrks-product-definition/downstream-v2.1"
COMPILER_VERSION = "core-semantic-closure-v2-m5.1"

OUTCOME_BASIS_SELECTORS = (
    {"scope": "CORE", "axis": "happy_path"},
    {"scope": "CORE", "axis": "alternative_path"},
    {"scope": "CORE", "axis": "error"},
    {"scope": "CORE", "axis": "recovery"},
    {"scope": "CORE", "axis": "acceptance"},
    {"scope": "UX_ACTION", "axis": "success"},
    {"scope": "UX_ACTION", "axis": "failure"},
    {"scope": "UX_STATE", "axis": "success"},
    {"scope": "UX_STATE", "axis": "error"},
)
ACCEPTANCE_BASIS_SELECTORS = ({"scope": "CORE", "axis": "acceptance"},)

_HASH = re.compile(r"^[0-9a-f]{64}$")
_SEED_KEY = re.compile(r"^SEED-[0-9a-f]{24}$")
_SCOPE_REF = re.compile(r"^(?:REQ|SURF|SCR)-[^\s]+$")
_TOP_LEVEL = {
    "contract_schema_version",
    "compiler",
    "source_authority",
    "responsibility_profile",
    "scope_commitments",
    "source_seed_inventory",
    "actions",
    "lifecycles",
    "semantic_debt",
    "handoff_status",
    "semantic_assurance",
    "semantic_contract_hash",
    "artifact_hash",
}
_AUTHORITY_KEYS = {
    "state_schema_version",
    "product_slug",
    "approved_revision",
    "approved_definition_digest",
    "approved_manifest_digest",
    "product_binding_contract",
    "ux_binding_contract",
    "snapshot_state_sha256",
    "consumed_seed_inventory_digest",
}
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
_DEBT_KEYS = {
    "direct_authority_count",
    "machine_derived_count",
    "review_required_count",
    "authority_gap_count",
    "direct_authority_fields",
    "machine_derived_fields",
    "review_required_fields",
    "authority_gaps",
}
_BASIS_KEYS = {"outcome_basis_seed_refs", "acceptance_basis_seed_refs"}


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _is_nonblank_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_seed_location(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != _LOCATION_KEYS:
        return False
    return (
        value.get("scope") in _SEED_SCOPES
        and isinstance(value.get("owner_ref"), str)
        and _SCOPE_REF.fullmatch(value["owner_ref"]) is not None
        and _is_nonblank_string(value.get("axis"))
        and (value.get("pack_id") is None or _is_nonblank_string(value.get("pack_id")))
        and (
            value.get("action_key") is None
            or _is_nonblank_string(value.get("action_key"))
        )
    )


def semantic_contract_projection_v21(
    contract: dict[str, object],
) -> dict[str, object]:
    """Exclude only observation-only full-state snapshot identity."""
    if not isinstance(contract, dict):
        raise ValueError("INVALID_ACTION_CONTRACT_V21")
    projection = copy.deepcopy(contract)
    projection.pop("semantic_contract_hash", None)
    projection.pop("artifact_hash", None)
    authority = projection.get("source_authority")
    if isinstance(authority, dict):
        authority.pop("snapshot_state_sha256", None)
    return projection


def semantic_contract_hash_v21(contract: dict[str, object]) -> str:
    return sha256_json(semantic_contract_projection_v21(contract))


def artifact_hash_v21(contract: dict[str, object]) -> str:
    if not isinstance(contract, dict):
        raise ValueError("INVALID_ACTION_CONTRACT_V21")
    projection = copy.deepcopy(contract)
    projection.pop("artifact_hash", None)
    return sha256_json(projection)


def validate_verification_basis(
    basis: object,
    *,
    context: dict[str, object],
    seeds: dict[str, dict[str, object]],
    profile: dict[str, object],
) -> dict[str, list[str]]:
    """Validate caller-selected exact refs without discovering extra authority."""
    try:
        _validate_responsibility_profile_v21(profile)
        if not isinstance(basis, dict) or set(basis) != _BASIS_KEYS:
            raise ValueError
        normalized = {}
        for key, selectors in (
            ("outcome_basis_seed_refs", OUTCOME_BASIS_SELECTORS),
            ("acceptance_basis_seed_refs", ACCEPTANCE_BASIS_SELECTORS),
        ):
            refs = basis.get(key)
            if (
                not isinstance(refs, list)
                or not refs
                or any(not isinstance(ref, str) or not ref for ref in refs)
                or refs != sorted(set(refs))
            ):
                raise ValueError
            for ref in refs:
                seed = seeds.get(ref) if isinstance(seeds, dict) else None
                if (
                    not isinstance(seed, dict)
                    or seed.get("seed_key") != ref
                    or seed.get("source_status") not in {None, "CURRENT"}
                    or not any(
                        seed_matches_selector_v21(seed, selector, context)
                        for selector in selectors
                    )
                ):
                    raise ValueError
            normalized[key] = list(refs)
        return normalized
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise ValueError("INVALID_VERIFICATION_BASIS") from error


def _normalized_field(derived: dict[str, object]) -> dict[str, object]:
    spec = derived["derivation"]
    kind = spec["kind"]
    if kind == "DIRECT_AUTHORITY":
        derivation = {"kind": kind}
    elif kind == "MACHINE_DERIVED":
        derivation = {
            key: copy.deepcopy(value)
            for key, value in spec.items()
            if key != "source_seed_ref"
        }
    else:
        derivation = {
            "kind": kind,
            "why_structuring_is_insufficient": spec[
                "why_structuring_is_insufficient"
            ],
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
    if kind == "MACHINE_DERIVED":
        if derivation.get("operator") == "collect_exact":
            if derivation.get("source_seed_refs") != refs:
                raise ValueError("INVALID_SEMANTIC_FIELD")
            return copy.deepcopy(derivation)
        if len(refs) == 1:
            return {**copy.deepcopy(derivation), "source_seed_ref": refs[0]}
    if kind == "REVIEW_REQUIRED":
        return {
            **copy.deepcopy(derivation),
            "source_seed_refs": list(refs),
            "proposed_value": copy.deepcopy(field.get("value")),
        }
    raise ValueError("INVALID_SEMANTIC_FIELD")


def validate_action_contract_v21(contract: object) -> list[dict[str, str]]:
    """Return deterministic structural, provenance, consumption, and hash errors."""
    errors: list[dict[str, str]] = []

    def add(path: str, message: str):
        errors.append({"path": path, "message": message})

    if not isinstance(contract, dict):
        return [{"path": "/", "message": "contract must be an object"}]
    if set(contract) != _TOP_LEVEL:
        add("/", "contract has missing or extra top-level fields")
    if contract.get("contract_schema_version") != ACTION_CONTRACT_VERSION:
        add("/contract_schema_version", "unsupported contract schema version")
    if contract.get("compiler") != {"id": COMPILER_ID, "version": COMPILER_VERSION}:
        add("/compiler", "compiler identity does not match")

    authority = contract.get("source_authority")
    if not isinstance(authority, dict) or set(authority) != _AUTHORITY_KEYS:
        add("/source_authority", "source authority shape does not match")
        authority = {}
    if authority.get("state_schema_version") != "0.2.0":
        add("/source_authority/state_schema_version", "must equal 0.2.0")
    if not _is_nonblank_string(authority.get("product_slug")):
        add("/source_authority/product_slug", "must be a nonblank string")
    revision = authority.get("approved_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        add("/source_authority/approved_revision", "must be an integer at least 1")
    for key in (
        "approved_definition_digest",
        "approved_manifest_digest",
        "snapshot_state_sha256",
        "consumed_seed_inventory_digest",
    ):
        if not _is_hash(authority.get(key)):
            add(f"/source_authority/{key}", "must be a lowercase SHA-256")
    try:
        expected_bindings = binding_contract_identity()
    except BindingError as error:
        expected_bindings = {}
        add("/source_authority", f"frozen binding identities are unavailable: {error.code}")
    for key, identity_key in (
        ("product_binding_contract", "product"),
        ("ux_binding_contract", "ux"),
    ):
        binding = authority.get(key)
        if (
            not isinstance(binding, dict)
            or set(binding) != {"contract_id", "version", "digest"}
            or not _is_hash(binding.get("digest"))
            or binding != expected_bindings.get(identity_key)
        ):
            add(f"/source_authority/{key}", "binding identity does not match frozen authority")

    responsibility = contract.get("responsibility_profile")
    if responsibility != {
        "profile_id": RESPONSIBILITY_PROFILE_ID,
        "digest": responsibility_profile_digest_v21(),
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
            "record_id",
            "record_type",
            "record_sha256",
        }:
            add(path, "scope commitment shape does not match")
            continue
        record_id = commitment.get("record_id")
        record_type = commitment.get("record_type")
        if (
            not isinstance(record_id, str)
            or _SCOPE_REF.fullmatch(record_id) is None
            or record_type != record_id.split("-", 1)[0]
            or not _is_hash(commitment.get("record_sha256"))
        ):
            add(path, "scope commitment identity is invalid")
        if isinstance(record_id, str) and _SCOPE_REF.fullmatch(record_id) is not None:
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
        seed_key = seed.get("seed_key")
        if isinstance(seed_key, str) and _SEED_KEY.fullmatch(seed_key) is not None:
            seed_keys.append(seed_key)
        location = seed.get("location")
        identity_valid = (
            isinstance(seed_key, str)
            and _SEED_KEY.fullmatch(seed_key) is not None
            and _valid_seed_location(location)
            and _is_nonblank_string(seed.get("record_id"))
            and _is_nonblank_string(seed.get("record_type"))
            and isinstance(seed.get("pointer"), str)
            and seed["pointer"].startswith("/")
            and _is_hash(seed.get("value_sha256"))
            and seed.get("source_status") == "CURRENT"
        )
        if not identity_valid:
            add(path, "source seed identity is invalid")
        try:
            value_hash = sha256_json(seed.get("value"))
            if value_hash != seed.get("value_sha256"):
                add(path, "source seed value hash does not match")
            expected_key = "SEED-" + sha256_json(
                {
                    "location": location,
                    "record_id": seed["record_id"],
                    "pointer": seed["pointer"],
                    "value_sha256": value_hash,
                }
            )[:24]
            if seed_key != expected_key:
                add(path, "source seed key does not match deterministic identity")
        except (KeyError, TypeError, ValueError, RecursionError):
            add(path, "source seed value or identity is not canonical JSON")
    if seed_keys != sorted(set(seed_keys)):
        add("/source_seed_inventory", "source seed inventory must be sorted and unique")
    try:
        if authority.get("consumed_seed_inventory_digest") != source_seed_inventory_digest(
            inventory
        ):
            add(
                "/source_authority/consumed_seed_inventory_digest",
                "consumed seed digest does not match",
            )
        seeds = source_seed_index(inventory)
    except (TypeError, ValueError, RecursionError):
        seeds = {}
        add("/source_seed_inventory", "source seed inventory cannot be indexed")

    profile = load_responsibility_profile_v21()
    used_scope_refs = set()
    used_seed_refs = set()
    derived_paths = []
    for collection_name, id_key, field_kind, profile_key, expected_keys in (
        (
            "actions",
            "action_id",
            "ACTION",
            "action_fields",
            {
                "action_id",
                "authority_scope_refs",
                "ux_action_locator",
                "fields",
                "verification_basis",
            },
        ),
        (
            "lifecycles",
            "lifecycle_id",
            "LIFECYCLE",
            "lifecycle_fields",
            {"lifecycle_id", "authority_scope_refs", "fields"},
        ),
    ):
        collection = contract.get(collection_name)
        if not isinstance(collection, list):
            add(f"/{collection_name}", "collection must be an array")
            continue
        ids = []
        for item_index, item in enumerate(collection):
            item_path = f"/{collection_name}/{item_index}"
            if not isinstance(item, dict) or set(item) != expected_keys:
                add(item_path, "item shape does not match")
                continue
            item_id = item.get(id_key)
            refs = item.get("authority_scope_refs")
            if (
                not _is_nonblank_string(item_id)
                or not isinstance(refs, list)
                or not refs
                or any(
                    not isinstance(ref, str) or _SCOPE_REF.fullmatch(ref) is None
                    for ref in refs
                )
                or refs != sorted(set(refs))
                or any(ref not in commitment_ids for ref in refs)
            ):
                add(item_path, "item identity or authority scope refs are invalid")
                continue
            ids.append(item_id)
            used_scope_refs.update(refs)
            context = {"authority_scope_refs": refs, "current_scope_refs": commitment_ids}
            if collection_name == "actions":
                locator = item.get("ux_action_locator")
                if (
                    not isinstance(locator, dict)
                    or set(locator) != {"screen_ref", "action_key"}
                    or locator.get("screen_ref") not in refs
                    or not _is_nonblank_string(locator.get("action_key"))
                ):
                    add(f"{item_path}/ux_action_locator", "UX action locator is invalid")
                else:
                    context["ux_action_locator"] = locator
                try:
                    basis = validate_verification_basis(
                        item.get("verification_basis"),
                        context=context,
                        seeds=seeds,
                        profile=profile,
                    )
                    used_seed_refs.update(
                        ref for values in basis.values() for ref in values
                    )
                except (TypeError, ValueError, AttributeError) as error:
                    add(f"{item_path}/verification_basis", str(error))
            fields = item.get("fields")
            expected_fields = set(profile[profile_key])
            if not isinstance(fields, dict) or set(fields) != expected_fields:
                add(f"{item_path}/fields", "semantic field inventory does not match")
                continue
            for field_name in sorted(expected_fields):
                field = fields[field_name]
                field_path = canonical_field_ref(
                    collection_name,
                    item_id,
                    field_name,
                )
                try:
                    recomputed = derive_semantic_field_v21(
                        _definition_spec(field),
                        field_name=field_name,
                        field_kind=field_kind,
                        context=context,
                        seeds=seeds,
                        profile=profile,
                    )
                    if _normalized_field(recomputed) != field:
                        raise ValueError("semantic field is not the recomputed output")
                    used_seed_refs.update(field["source_seed_refs"])
                    derived_paths.append((field_path, field["derivation"]["kind"]))
                except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
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
        counts = (
            "direct_authority_count",
            "machine_derived_count",
            "review_required_count",
            "authority_gap_count",
        )
        if any(type(debt.get(key)) is not int or debt[key] < 0 for key in counts):
            add("/semantic_debt", "semantic debt counts must be nonnegative integers")
        expected_fields = {
            kind: sorted(path for path, value in derived_paths if value == kind)
            for kind in ("DIRECT_AUTHORITY", "MACHINE_DERIVED", "REVIEW_REQUIRED")
        }
        for kind, prefix in (
            ("DIRECT_AUTHORITY", "direct_authority"),
            ("MACHINE_DERIVED", "machine_derived"),
            ("REVIEW_REQUIRED", "review_required"),
        ):
            if (
                debt.get(f"{prefix}_fields") != expected_fields[kind]
                or debt.get(f"{prefix}_count") != len(expected_fields[kind])
            ):
                add("/semantic_debt", f"{prefix} inventory does not match fields")
        if debt.get("authority_gap_count") != 0 or debt.get("authority_gaps") != []:
            add("/semantic_debt", "production contract cannot contain authority gaps")
        reviews = len(expected_fields["REVIEW_REQUIRED"])
        expected_status = (
            "AUTHORITY_READY_REVIEW_PENDING"
            if reviews
            else "AUTHORITY_READY_MACHINE_VERIFIED"
        )
        expected_assurance = {"status": "NOT_MEASURED" if reviews else "NOT_REQUIRED"}
        if contract.get("handoff_status") != expected_status:
            add("/handoff_status", "handoff status does not match semantic debt")
        if contract.get("semantic_assurance") != expected_assurance:
            add("/semantic_assurance", "semantic assurance does not match semantic debt")

    for key in ("semantic_contract_hash", "artifact_hash"):
        if not _is_hash(contract.get(key)):
            add(f"/{key}", "must be a lowercase SHA-256")
    try:
        if contract.get("semantic_contract_hash") != semantic_contract_hash_v21(contract):
            add("/semantic_contract_hash", "semantic contract hash does not match")
        if contract.get("artifact_hash") != artifact_hash_v21(contract):
            add("/artifact_hash", "artifact hash does not match")
    except (TypeError, ValueError, RecursionError):
        add("/", "contract is not canonical JSON")
    return sorted(errors, key=lambda error: (error["path"], error["message"]))


__all__ = [
    "ACCEPTANCE_BASIS_SELECTORS",
    "COMPILER_ID",
    "COMPILER_VERSION",
    "OUTCOME_BASIS_SELECTORS",
    "artifact_hash_v21",
    "semantic_contract_hash_v21",
    "semantic_contract_projection_v21",
    "validate_action_contract_v21",
    "validate_verification_basis",
]
