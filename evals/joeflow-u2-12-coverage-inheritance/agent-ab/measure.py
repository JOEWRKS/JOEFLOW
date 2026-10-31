# Measures each A/B run's state.json: did FREEZE land, how many cells were written by hand,
# how many were implied by a declaration (B only), how concentrated the bindings are.
# Usage: python -B measure.py <ab root>
import collections, json, subprocess, sys
from pathlib import Path
ROOT = Path(sys.argv[1]).resolve()
SKILL = ROOT / "skill-B/skills/joewrks-product-definition"
sys.path.insert(0, str(SKILL / "scripts"))
from coverage_inheritance import TAG, expand_coverage  # noqa: E402
FX = json.load(open(ROOT / "fixture/product-definition/ai-coach/state.json", encoding="utf-8"))
NEW_ROWS = {("coverage", "REQ-005"), ("ux_coverage", "SCR-003")}

def bkey(c):
    b = c.get("authority_bindings") or c.get("basis_bindings") or []
    return (c["status"], frozenset((x["record_id"], x.get("pointer")) for x in b))

def new_cells(state):
    """(table, owner, action, axis, cell) for the rows FREEZE had to write."""
    for r in state.get("coverage", []):
        if r.get("feature_id") == "REQ-005":
            for ax, c in r["cells"].items(): yield "core", "REQ-005", None, ax, c
    for r in state.get("ux_coverage", []):
        if r.get("screen_id") == "SCR-003":
            for ax, c in r["states"].items(): yield "ux_state", "SCR-003", None, ax, c
            for a in r.get("actions", []):
                for ax, c in a["cells"].items(): yield "ux_action", "SCR-003", a["key"], ax, c

def declarations(state):
    out = {}
    for r in state.get("coverage", []):
        if r.get("feature_id") == "REQ-005" and r.get("default_authority"): out["REQ-005"] = "default_authority"
    for r in state.get("ux_coverage", []):
        if r.get("screen_id") == "SCR-003":
            if r.get("default_authority"): out["SCR-003"] = "default_authority"
            for a in r.get("actions", []):
                d = [k for k in ("shape", "default_authority") if a.get(k)]
                if d: out[a["key"]] = "+".join(f"{k}={a[k]}" if k == "shape" else k for k in d)
    return out

def validate(path):
    r = subprocess.run([sys.executable, "-B", str(SKILL / "scripts/validate_state.py"), str(path)],
                       capture_output=True, text=True, encoding="utf-8")
    try: d = json.loads(r.stdout)
    except Exception: return None, r.stdout[-300] + r.stderr[-300:]
    return d.get("valid"), [e.get("code") for e in d.get("errors", [])][:8]

trials = json.load(open(ROOT / "trials.json", encoding="utf-8"))
rows = []
for t in trials:
    path = Path(t["root"]) / "product-definition/ai-coach/state.json"
    s = json.load(open(path, encoding="utf-8"))
    rev = s["project"].get("definition_revision")
    status = s["project"].get("definition_status")
    valid, errs = validate(path)
    compact = list(new_cells(s))
    exp = list(new_cells(expand_coverage(s)))
    hand = [c for c in compact if not c[4].get(TAG)]
    inherited = [c for c in exp if c[4].get(TAG)]
    by_tag = collections.Counter(c[4].get(TAG) for c in inherited)
    hand_na = [c for c in hand if c[4]["status"] == "N/A"]
    hand_cov = [c for c in hand if c[4]["status"] != "N/A"]
    # concentration: per row, share of hand-written non-N/A cells that carry the row's most common binding set
    per_row = collections.defaultdict(list)
    for tb, owner, act, ax, c in hand_cov: per_row[(tb, owner, act)].append(bkey(c))
    top_share, distinct = [], []
    for k, ks in per_row.items():
        cnt = collections.Counter(ks); top_share.append(cnt.most_common(1)[0][1] / len(ks)); distinct.append(len(cnt))
    records = collections.Counter(x["record_id"] for c in hand_cov for x in (c[4].get("authority_bindings") or []))
    rows.append({"id": t["id"], "arm": t["arm"], "revision": rev, "status": status, "valid": valid, "errors": errs,
                 "cells_total": len(exp), "hand": len(hand), "hand_covered": len(hand_cov), "hand_na": len(hand_na),
                 "inherited": len(inherited), "inherited_by": dict(by_tag), "declarations": declarations(s),
                 "top_binding_share": round(sum(top_share) / len(top_share), 2) if top_share else None,
                 "distinct_bindings_per_row": round(sum(distinct) / len(distinct), 1) if distinct else None,
                 "records_cited": len(records), "top_records": records.most_common(4)})
json.dump(rows, open(ROOT / "measure-result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in rows:
    print(f"{r['id']} {r['arm']} rev={r['revision']} {r['status']} valid={r['valid']} cells={r['cells_total']} hand={r['hand']} (cov {r['hand_covered']}, N/A {r['hand_na']}) inherited={r['inherited']} {r['inherited_by']} decl={r['declarations']} top_share={r['top_binding_share']} distinct/row={r['distinct_bindings_per_row']} records={r['records_cited']} errs={r['errors']}")
