import copy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from state_validation_v2 import evaluate_closure_v2  # noqa: E402
from tests.test_semantic_closure_v020 import literal_approved_state  # noqa: E402


def closed_v2_state() -> dict[str, object]:
    """Return an independently fixed, evaluator-verified M4 closed state."""
    state = copy.deepcopy(literal_approved_state())
    if not evaluate_closure_v2(state)["closed"]:
        raise AssertionError("literal M4 closed fixture no longer closes")
    return state


def source_seed_by_location(seeds, *, scope, owner_ref, axis, pack_id=None, action_key=None):
    matches = [
        seed for seed in seeds
        if seed["location"] == {
            "scope": scope,
            "owner_ref": owner_ref,
            "axis": axis,
            "pack_id": pack_id,
            "action_key": action_key,
        }
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one seed at {scope}/{owner_ref}/{axis}, found {len(matches)}")
    return matches[0]
