# For actions whose shape is known from their mechanism, how often did authors write each axis
# N/A? States are expanded first so an inherited N/A counts as the author's answer.
# Usage: python -B axis_freq.py
import json, sys, collections
from pathlib import Path
sys.path.insert(0, "D:/JOEWRKS/.claude-worktrees/JOEFLOW-reinforce/skills/joewrks-product-definition/scripts")
from coverage_inheritance import expand_coverage
RUNS = Path("D:/JOEWRKS/.claude-worktrees/_data/2026-10-31-joeflow-u2-12-ab/runs")
LABEL = {"back-to-final": "navigate", "new-game": "discard", "new-game-from-review": "discard",
         "step-move": "browse", "jump-to-move": "browse", "choose-color": "local_choice", "choose-strength": "local_choice",
         "start-game": "submit", "preview-then-place": "submit"}
SOURCES = [("AI-Gomoku", "D:/JOEWRKS/.claude-worktrees/AI-Gomoku/product-definition/ai-coach/state.json", None)]
SOURCES += [(d.name, str(d / "product-definition/ai-coach/state.json"), "SCR-003") for d in sorted(RUNS.iterdir())]
PROFILE = {"permission", "session_expiration"}
freq = collections.defaultdict(collections.Counter); n = collections.Counter()
for name, path, only in SOURCES:
    s = expand_coverage(json.load(open(path, encoding="utf-8")))
    for r in s["ux_coverage"]:
        if only and r["screen_id"] != only: continue
        for a in r["actions"]:
            shape = LABEL.get(a["key"])
            if not shape: continue
            n[shape] += 1
            for ax, c in a["cells"].items():
                if ax not in PROFILE and c["status"] == "N/A": freq[shape][ax] += 1
for shape in ("navigate", "browse", "discard", "local_choice", "submit"):
    print(f"== {shape} ({n[shape]} actions)")
    print("   " + ", ".join(f"{ax} {c}/{n[shape]}" for ax, c in freq[shape].most_common()))
