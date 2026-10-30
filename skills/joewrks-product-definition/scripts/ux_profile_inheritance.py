"""UX axes a screen may omit because the grill topology profile already marks the domain N/A.

An omitted axis is read as an N/A inherited from surface_manifest.grill_profile.<DOMAIN>, whose
status, basis and rationale are validated by grill_v2. A written cell is always validated as before.
"""
from __future__ import annotations

import json
from pathlib import Path

INHERITANCE_PATH = Path(__file__).resolve().parents[1] / "references" / "ux-profile-inheritance-v1.json"
_EXPECTED = {
    "contract_id": "joewrks.ux-profile-inheritance",
    "version": "1.0",
    "domains": {
        "AUTH": {"state_axes": ["expired", "unauthenticated"], "action_axes": ["session_expiration"]},
        "PERMISSION": {"state_axes": ["permission_denied"], "action_axes": ["permission"]},
    },
}
_MEANINGLESS = {"none", "false", "n/a", "na", "later", "tbd"}


def load_inheritance() -> dict[str, object]:
    contract = json.loads(INHERITANCE_PATH.read_text(encoding="utf-8"))
    if contract != _EXPECTED:
        raise ValueError("ux_profile_inheritance_drift")
    return contract


def _profile_cell_is_na(cell: object) -> bool:
    if not isinstance(cell, dict) or cell.get("status") != "N/A":
        return False
    basis, rationale = cell.get("basis_refs"), cell.get("rationale")
    text = rationale.strip() if isinstance(rationale, str) else ""
    return (
        isinstance(basis, list) and bool(basis) and all(isinstance(ref, str) for ref in basis)
        and bool(text) and text.lower() not in _MEANINGLESS
    )


def inheritable_ux_axes(state: dict[str, object]) -> tuple[set[str], set[str]]:
    """Return (state axes, action axes) a UX row may omit for this state."""
    manifest = state.get("surface_manifest") if isinstance(state, dict) else None
    profile = manifest.get("grill_profile") if isinstance(manifest, dict) else None
    state_axes: set[str] = set()
    action_axes: set[str] = set()
    if not isinstance(profile, dict):
        return state_axes, action_axes
    for domain, axes in load_inheritance()["domains"].items():
        if _profile_cell_is_na(profile.get(domain)):
            state_axes.update(axes["state_axes"])
            action_axes.update(axes["action_axes"])
    return state_axes, action_axes
