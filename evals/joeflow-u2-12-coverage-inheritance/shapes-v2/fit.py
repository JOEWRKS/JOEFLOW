# How much of the hand-written N/A of real actions does each shape table explain?
# For every action the best shape is the largest N/A set that is a subset of the hand-written
# N/A (plus the profile-inherited permission/session axes), so a shape never implies an N/A the
# author did not write. States are expanded first, so an N/A an author declared through a shape
# counts as written. Usage: python -B fit.py <shapes.json>... (each table scored on the same actions)
import json, sys, collections
from pathlib import Path
sys.path.insert(0, "D:/JOEWRKS/.claude-worktrees/JOEFLOW-reinforce/skills/joewrks-product-definition/scripts")
from coverage_inheritance import expand_coverage
RUNS = Path("D:/JOEWRKS/.claude-worktrees/_data/2026-10-31-joeflow-u2-12-ab/runs")
SOURCES = [("AI-Gomoku", "D:/JOEWRKS/.claude-worktrees/AI-Gomoku/product-definition/ai-coach/state.json", None),
           ("WebAppDev", "D:/JOEWRKS/WebAppDev/product-definition/curated-lifestyle-store/state.json", None)]
SOURCES += [(f"A/B {d.name}", str(d / "product-definition/ai-coach/state.json"), "SCR-003") for d in sorted(RUNS.iterdir())]
PROFILE = {"permission", "session_expiration"}

def actions():
    for name, path, only in SOURCES:
        s = expand_coverage(json.load(open(path, encoding="utf-8")))
        for r in s["ux_coverage"]:
            if only and r["screen_id"] != only: continue
            for a in r["actions"]:
                yield name, f"{r['screen_id']}/{a['key']}", {ax for ax, c in a["cells"].items() if c["status"] == "N/A"} - PROFILE

acts = list(actions())
for path in sys.argv[1:]:
    shapes = json.load(open(path, encoding="utf-8"))["shapes"]
    print(f"== {Path(path).name}: {len(acts)} actions, hand N/A {sum(len(na) for *_, na in acts)}")
    explained = 0; fits = collections.Counter(); unfit = []
    for name, key, na in acts:
        size = lambda sh: len(shapes[sh]["not_applicable"]) if set(shapes[sh]["not_applicable"]) <= na else 0
        best = max(shapes, key=lambda sh: (size(sh), sh))
        n = size(best)
        if n == 0: best = "-"
        explained += n; fits[best] += 1
        if "A/B" in name or name == "AI-Gomoku": print(f"   {name:10s} {key:30s} N/A {len(na):2d} -> {best:12s} explains {n}")
    print(f"   explained {explained} / {sum(len(na) for *_, na in acts)}  shapes used {dict(fits)}")
