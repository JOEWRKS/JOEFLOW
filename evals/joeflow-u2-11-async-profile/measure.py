# U2-11 on AI-Gomoku rev 39: does ASYNC.execution = LOCAL_PURE imply exactly the axes the authors
# answered N/A, and does declaring it keep the approved digests? Usage: python -B measure.py <state.json>
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/joewrks-product-definition/scripts"))
from approval_v2 import approval_manifest_digest, compute_approval_manifest, definition_digest
from coverage_inheritance import expand_coverage, inheritable_grill_axes
from state_validation_v2 import validate_state_v2

base = json.load(open(sys.argv[1], encoding="utf-8"))
s = copy.deepcopy(base)
row = next(r for r in s["grill_coverage"] if r["pack_id"] == "GRILL-ASYNC-1")
hand_na = sorted(ax for ax, c in row["axes"].items() if c["status"] == "N/A")
s["surface_manifest"]["grill_profile"]["ASYNC"]["execution"] = "LOCAL_PURE"
implied = sorted(inheritable_grill_axes(s)["GRILL-ASYNC-1"])
print("hand-written N/A", hand_na)
print("implied by LOCAL_PURE", implied, "equal:", hand_na == implied)
print("declared, cells kept: errors", [e["code"] for e in validate_state_v2(s)],
      "| definition digest unchanged:", definition_digest(s) == definition_digest(base),
      "| manifest digest unchanged:", approval_manifest_digest(compute_approval_manifest(s)) == approval_manifest_digest(compute_approval_manifest(base)))
for ax in implied:
    del row["axes"][ax]
errors = [e["code"] for e in validate_state_v2(s)]
print("declared, 4 cells dropped (no revision opened): errors", sorted(set(errors)))
tags = {ax: c.get("inherited_from") for ax, c in next(r for r in expand_coverage(s)["grill_coverage"] if r["pack_id"] == "GRILL-ASYNC-1")["axes"].items() if c.get("inherited_from")}
print("expanded tags", tags)
