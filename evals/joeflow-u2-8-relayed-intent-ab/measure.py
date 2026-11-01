# U2-8 A/B: how did each agent record a relayed instruction? Usage: python -B measure.py <ab root>
import json, subprocess, sys
from pathlib import Path
ROOT = Path(sys.argv[1]).resolve()
SKILL = ROOT / "skill-B/skills/joewrks-product-definition"
FX = json.load(open("D:/JOEWRKS/.claude-worktrees/_data/2026-10-31-joeflow-u2-12-ab/fixture/product-definition/ai-coach/state.json", encoding="utf-8"))
known_evd = {e["id"] for e in FX["evidence"]}
known = {x["id"] for g in FX["objects"].values() for x in g}


def validate(path):
    r = subprocess.run([sys.executable, "-B", str(SKILL / "scripts/validate_state.py"), str(path)], capture_output=True, text=True, encoding="utf-8")
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None, r.stdout[-200:] + r.stderr[-200:]
    return d.get("valid"), [e.get("code") for e in d.get("errors", [])][:6]


rows = []
for t in json.load(open(ROOT / "trials.json", encoding="utf-8")):
    path = Path(t["root"]) / "product-definition/ai-coach/state.json"
    s = json.load(open(path, encoding="utf-8"))
    valid, errs = validate(path)
    new_evd = [e for e in s["evidence"] if e["id"] not in known_evd]
    new_unk = [u for u in s["objects"]["unknowns"] if u["id"] not in known]
    new_dec = [d for d in s["objects"]["decisions"] if d["id"] not in known]
    new_rules = [r["id"] for r in s["objects"]["rules"] if r["id"] not in known]
    rows.append({
        "id": t["id"], "arm": t["arm"], "variant": t["variant"],
        "revision": s["project"]["definition_revision"], "status": s["project"]["definition_status"], "valid": valid, "errors": errs,
        "evidence": [(e["id"], e["source_kind"], e["confidence"]) for e in new_evd],
        "questions": [(u["id"], u["status"], u.get("decision_authority"), u.get("resolution_mode")) for u in new_unk],
        "decisions": [(d["id"], d["status"], d.get("resolution_mode"), d.get("decided_by"), sorted(d.get("evidence_refs") or [])) for d in new_dec],
        "rules": new_rules,
    })
json.dump(rows, open(ROOT / "measure-result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in rows:
    closed = [d for d in r["decisions"] if d[1] == "CURRENT" and d[2] in ("USER_DECISION", "USER_ACCEPTED_RECOMMENDATION")]
    print(f"{r['id']} {r['arm']} {r['variant']:7s} rev={r['revision']} {r['status']} valid={r['valid']} evidence={r['evidence']} questions={[(q[0], q[1]) for q in r['questions']]} user-closed={[d[0] for d in closed]} agent-decisions={[d[0] for d in r['decisions'] if d not in closed]} rules={r['rules']} errs={r['errors']}")
