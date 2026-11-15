"""Collect run artifacts into runs/rNN/ (paths masked), post-check with 1.7.2, scan for version leaks.

Usage: python collect.py SCRATCH ORIG_DIR FINAL_DIR CHECKER_172
"""
import difflib, json, os, re, shutil, subprocess, sys
from pathlib import Path

scratch, orig, final, checker = map(Path, sys.argv[1:5])
here = Path(__file__).resolve().parent
runs = here / "runs"
key = {"r01": (1, "B"), "r02": (1, "A"), "r03": (1, "A"), "r04": (1, "B"), "r05": (1, "A"), "r06": (1, "B"),
       "r07": (1, "A"), "r08": (1, "B"), "r09": (2, "B"), "r10": (2, "A"), "r11": (2, "A"), "r12": (2, "A"),
       "r13": (2, "B"), "r14": (2, "B"), "r15": (2, "A"), "r16": (2, "B")}
own = {(1, "A"): "1.7.0", (2, "A"): "1.7.1", (1, "B"): "1.7.2", (2, "B"): "1.7.2"}
home = str(Path.home())
masks = [(str(scratch), "<SCRATCH>"), (str(scratch).replace("\\", "/"), "<SCRATCH>"),
         ("/d/JOEWRKS/.claude-worktrees/_data/2026-11-15-joeflow-v172-behavior", "<SCRATCH>"),
         (home, "<HOME>"), (home.replace("\\", "/"), "<HOME>"),
         ("/" + home[0].lower() + home[2:].replace("\\", "/"), "<HOME>")]
def mask(s):
    for a, b in masks:
        s = s.replace(a, b)
    return s.replace(Path.home().name, "<USER>")

env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
summary = {}
for r, (scene, arm) in key.items():
    d = runs / r
    (d / "changed").mkdir(parents=True, exist_ok=True)
    pf = scratch / r / "project/product-definition/request-form"
    log = (scratch / r / "commands.log").read_text(encoding="utf-8", errors="replace") if (scratch / r / "commands.log").exists() else ""
    (d / "commands.log").write_text(mask(log), encoding="utf-8")
    fm = (final / f"{r}.md").read_text(encoding="utf-8")
    (d / "final-message.md").write_text(mask(fm), encoding="utf-8")
    diffs, stat, extra = [], {}, sorted(p.name for p in pf.iterdir() if not (orig / r / p.name).exists())
    for name in ("state.json", "MASTER_PLANNING_SPEC.md", "planning-review-core.html"):
        a = (orig / r / name).read_text(encoding="utf-8").splitlines(keepends=True)
        b = (pf / name).read_text(encoding="utf-8").splitlines(keepends=True)
        ud = list(difflib.unified_diff(a, b, f"orig/{name}", f"after/{name}", n=1))
        plus = sum(1 for l in ud if l.startswith("+") and not l.startswith("+++"))
        minus = sum(1 for l in ud if l.startswith("-") and not l.startswith("---"))
        stat[name] = [plus, minus]
        if ud:
            diffs += ud
            shutil.copy(pf / name, d / "changed" / name)
    (d / "changed/diff.txt").write_text(mask("".join(diffs)), encoding="utf-8")
    (d / "changed/diff-stat.txt").write_text("".join(f"{k}: +{v[0]} -{v[1]}\n" for k, v in stat.items()) +
                                            (f"extra files: {extra}\n" if extra else ""), encoding="utf-8")
    p = subprocess.run([sys.executable, str(checker), str(pf / "state.json"), "--spec", str(pf / "MASTER_PLANNING_SPEC.md"),
                        "--review", str(pf / "planning-review-core.html")], capture_output=True, text=True, encoding="utf-8", env=env)
    (d / "post-check-172.json").write_text(mask(p.stdout), encoding="utf-8")
    pc = json.loads(p.stdout)
    titles = sum(len(pc.get(k, {}).get("stale_title_revision", []) or []) for k in ("spec", "review") if isinstance(pc.get(k), dict))
    vers = sorted(set(re.findall(r"1\.7\.\d", fm + log)))
    foreign = [v for v in vers if v != own[(scene, arm)]]
    repo = re.findall(r"JOEWRKS[\\/]+JOEFLOW|CHANGELOG|git log|evals[\\/]", fm + log)
    spec_l5 = (pf / "MASTER_PLANNING_SPEC.md").read_text(encoding="utf-8").splitlines()[4]
    rv = (pf / "planning-review-core.html").read_text(encoding="utf-8")
    t = re.search(r"<title>(.*?)</title>", rv).group(1); h = re.search(r"<h1>(.*?)</h1>", rv).group(1)
    summary[r] = dict(scene=scene, arm=arm, own_version=own[(scene, arm)], versions_mentioned=vers, foreign_versions=foreign,
                      repo_traces=repo, first_log_line=mask(log.splitlines()[0]) if log else "", post_ok=pc.get("ok"),
                      post_title_findings=titles, diff_stat=stat, extra_files=extra, spec_line5=spec_l5, title=t, h1=h)
(runs / "arm-key.json").write_text(json.dumps({r: {"scene": s, "arm": a, "skill": own[(s, a)]} for r, (s, a) in key.items()},
                                              ensure_ascii=False, indent=1), encoding="utf-8")
(here / "collect-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
for r, s in summary.items():
    print(r, s["scene"], s["arm"], "ok", s["post_ok"], "tf", s["post_title_findings"], s["diff_stat"], s["extra_files"],
          "vers", s["versions_mentioned"], "foreign", s["foreign_versions"], "repo", s["repo_traces"], "|", s["first_log_line"][-12:])
    print("    L5:", s["spec_line5"][:90], "| title:", s["title"], "| h1:", s["h1"])
