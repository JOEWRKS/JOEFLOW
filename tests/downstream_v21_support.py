import copy

from tests.downstream_v2_support import closed_v2_state, source_seed_by_location


def make_seed_v21(
    key="SEED-001",
    *,
    scope="CORE",
    owner_ref="REQ-001",
    axis="actor",
    pack_id=None,
    action_key=None,
    value=None,
):
    """Return a minimal exact source seed for 2.1 derivation tests."""
    return {
        "seed_key": key,
        "location": {
            "scope": scope,
            "owner_ref": owner_ref,
            "axis": axis,
            "pack_id": pack_id,
            "action_key": action_key,
        },
        "value": (
            {"nested": {"item": ["exact", {"key": "value"}]}, "a": 1, "b": 2}
            if value is None
            else copy.deepcopy(value)
        ),
    }


def derivation_context_v21(*authority_scope_refs, **extra):
    refs = list(authority_scope_refs or ("REQ-001", "SCR-001"))
    return {
        "authority_scope_refs": refs,
        "current_scope_refs": list(refs),
        **copy.deepcopy(extra),
    }


__all__ = [
    "closed_v2_state",
    "derivation_context_v21",
    "make_seed_v21",
    "source_seed_by_location",
]
