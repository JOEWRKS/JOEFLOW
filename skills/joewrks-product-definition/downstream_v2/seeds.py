"""Deterministically compile and audit M4 positive authority bindings as source seeds."""

from authority_binding_v2 import canonical_record_index, resolve_record_pointer

from .authority import DownstreamV2Error, require_closed_authority, sha256_json


_SEED_KEYS = {"seed_key", "location", "record_id", "record_type", "pointer", "value_sha256", "source_status", "value"}
_LOCATION_KEYS = {"scope", "owner_ref", "axis", "pack_id", "action_key"}
_OBJECT_CONTAINERS = (
    "goals", "users", "requirements", "unknowns", "decisions", "rules", "flows",
    "screens", "states", "data", "integrations", "acceptance_criteria", "tasks",
)


def _fail(code: str, detail: object):
    raise DownstreamV2Error(code, detail)


def _binding_seed(index, location, binding):
    if not isinstance(binding, dict) or set(binding) != {"record_id", "pointer", "value_sha256"}:
        _fail("INVALID_SOURCE_SEED_BINDING", binding)
    record_id = binding["record_id"]
    pointer = binding["pointer"]
    if not isinstance(record_id, str) or not isinstance(pointer, str) or record_id not in index:
        _fail("INVALID_SOURCE_SEED_BINDING", binding)
    record_type, record = index[record_id]
    value = resolve_record_pointer(record, pointer)
    value_hash = sha256_json(value)
    if binding["value_sha256"] != value_hash or record.get("status") != "CURRENT":
        _fail("INVALID_SOURCE_SEED_BINDING", binding)
    seed_key = "SEED-" + sha256_json({
        "location": location,
        "record_id": record_id,
        "pointer": pointer,
        "value_sha256": value_hash,
    })[:24]
    return {
        "seed_key": seed_key,
        "location": location,
        "record_id": record_id,
        "record_type": record_type,
        "pointer": pointer,
        "value_sha256": value_hash,
        "source_status": "CURRENT",
        "value": value,
    }


def _positive_locations(state):
    coverage = state.get("coverage") if isinstance(state, dict) else None
    for row in coverage if isinstance(coverage, list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("feature_id"), str) or not isinstance(row.get("cells"), dict):
            continue
        for axis, cell in row["cells"].items():
            if isinstance(axis, str) and isinstance(cell, dict) and cell.get("status") == "COVERED":
                yield {"scope": "CORE", "owner_ref": row["feature_id"], "axis": axis, "pack_id": None, "action_key": None}, cell.get("authority_bindings")
    coverage = state.get("grill_coverage") if isinstance(state, dict) else None
    for row in coverage if isinstance(coverage, list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("target_ref"), str) or not isinstance(row.get("pack_id"), str) or not isinstance(row.get("axes"), dict):
            continue
        for axis, cell in row["axes"].items():
            if isinstance(axis, str) and isinstance(cell, dict) and cell.get("status") == "ADDRESSED":
                yield {"scope": "GRILL", "owner_ref": row["target_ref"], "axis": axis, "pack_id": row["pack_id"], "action_key": None}, cell.get("authority_bindings")
    coverage = state.get("ux_coverage") if isinstance(state, dict) else None
    for row in coverage if isinstance(coverage, list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("screen_id"), str):
            continue
        states = row.get("states")
        for axis, cell in states.items() if isinstance(states, dict) else []:
            if isinstance(axis, str) and isinstance(cell, dict) and cell.get("status") == "COVERED":
                yield {"scope": "UX_STATE", "owner_ref": row["screen_id"], "axis": axis, "pack_id": None, "action_key": None}, cell.get("authority_bindings")
        actions = row.get("actions")
        for action in actions if isinstance(actions, list) else []:
            if not isinstance(action, dict) or not isinstance(action.get("key"), str) or not isinstance(action.get("cells"), dict):
                continue
            for axis, cell in action["cells"].items():
                if isinstance(axis, str) and isinstance(cell, dict) and cell.get("status") == "COVERED":
                    yield {"scope": "UX_ACTION", "owner_ref": row["screen_id"], "axis": axis, "pack_id": None, "action_key": action["key"]}, cell.get("authority_bindings")


def build_source_seed_inventory(state: dict[str, object]) -> list[dict[str, object]]:
    """Compile all positive M4 bindings from a safely inspectable V2 state."""
    try:
        index = canonical_record_index(state)
        seeds = []
        for location, bindings in _positive_locations(state):
            if not isinstance(bindings, list):
                _fail("INVALID_SOURCE_SEED_BINDING", location)
            seeds.extend(_binding_seed(index, location, binding) for binding in bindings)
        seeds.sort(key=lambda seed: seed["seed_key"])
        if len({seed["seed_key"] for seed in seeds}) != len(seeds):
            _fail("DUPLICATE_SOURCE_SEED", [seed["seed_key"] for seed in seeds])
        return seeds
    except DownstreamV2Error:
        raise
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise DownstreamV2Error("INVALID_SOURCE_SEED_STATE", str(error)) from error


def build_closed_source_seed_inventory(state: dict[str, object]) -> list[dict[str, object]]:
    require_closed_authority(state)
    return build_source_seed_inventory(state)


def source_seed_inventory_digest(seeds: list[dict[str, object]]) -> str:
    return sha256_json(seeds)


def source_seed_index(seeds: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    index = {}
    for seed in seeds:
        if not isinstance(seed, dict) or not isinstance(seed.get("seed_key"), str) or seed["seed_key"] in index:
            _fail("DUPLICATE_SOURCE_SEED", seed)
        index[seed["seed_key"]] = seed
    return index


def _location_bindings(state, location):
    if not isinstance(location, dict) or set(location) != _LOCATION_KEYS:
        _fail("INVALID_SOURCE_SEED", location)
    matches = []
    for candidate, bindings in _positive_locations(state):
        if candidate == location:
            matches.append(bindings)
    if len(matches) != 1 or not isinstance(matches[0], list):
        _fail("SOURCE_SEED_LOCATION_DRIFT", location)
    return matches[0]


def _raw_record_id_count(state, record_id):
    objects = state.get("objects") if isinstance(state, dict) else None
    containers = [state.get("evidence"), state.get("contradictions")] if isinstance(state, dict) else []
    if isinstance(objects, dict):
        containers.extend(objects.get(name) for name in _OBJECT_CONTAINERS)
    surface_manifest = state.get("surface_manifest") if isinstance(state, dict) else None
    containers.append(surface_manifest.get("records") if isinstance(surface_manifest, dict) else None)
    return sum(
        isinstance(record, dict) and record.get("id") == record_id
        for container in containers if isinstance(container, list)
        for record in container
    )


def verify_source_seed(state: dict[str, object], seed: dict[str, object]) -> dict[str, object]:
    """Verify one stored seed against current source authority and semantic location."""
    try:
        if not isinstance(seed, dict) or set(seed) != _SEED_KEYS:
            _fail("INVALID_SOURCE_SEED", seed)
        location = seed["location"]
        bindings = _location_bindings(state, location)
        binding = {"record_id": seed["record_id"], "pointer": seed["pointer"], "value_sha256": seed["value_sha256"]}
        if sum(item == binding for item in bindings) != 1:
            _fail("SOURCE_SEED_BINDING_DRIFT", location)
        if _raw_record_id_count(state, seed["record_id"]) != 1:
            _fail("SOURCE_SEED_RECORD_CARDINALITY", seed["record_id"])
        index = canonical_record_index(state)
        expected = _binding_seed(index, location, binding)
        if expected != seed:
            _fail("SOURCE_SEED_DRIFT", seed.get("seed_key"))
        return seed
    except DownstreamV2Error:
        raise
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise DownstreamV2Error("SOURCE_SEED_DRIFT", str(error)) from error
