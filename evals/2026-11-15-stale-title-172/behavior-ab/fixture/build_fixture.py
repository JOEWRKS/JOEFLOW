"""Build the two scene fixtures for the 1.7.2 behavior A/B.

Usage: python build_fixture.py ARMS_DIR
ARMS_DIR holds `git archive` extracts: ARMS_DIR/v1.7.0, v1.7.1, v1.7.2 (each with skills/joewrks-product-definition).

Base documents: a fully written spec + review (body filled in: requirements, ACs, decisions, open
questions, change history "rev 1: 첫 승인 / rev 2: 글자 수 표시 추가"), adapted from a clean run of the
1.7.1 behavior test (evals/2026-11-13-stale-title-171/behavior-ab/runs/r2/changed/). State is the rev 2
state of the 1.7.1 repro (closed-minimal + trial rev 2 patch via open_revision.py --write).
Identity blocks are refreshed with the 1.7.2 update_projection.py --write, then:
  scene1: review <title> and <h1> hand-edited to "revision 0" (everything else current)
  scene2: titles current; spec header gets the plain fact sentence
          "> 승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)"
Each scene is checked with all three projection_check.py versions; outputs saved next to it.
"""
import json, shutil, subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
arms = Path(sys.argv[1])
ev = here.parents[2]  # evals/
src171 = ev / "2026-11-13-stale-title-171"
SK = "skills/joewrks-product-definition/scripts"
env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}

base = here / "base"
base.mkdir(exist_ok=True)
shutil.copy(src171 / "repro/state-rev2.json", base / "state.json")
spec = (src171 / "behavior-ab/runs/r2/changed/MASTER_PLANNING_SPEC.md").read_text(encoding="utf-8")
review = (src171 / "behavior-ab/runs/r2/changed/planning-review-core.html").read_text(encoding="utf-8")

# change history exactly as the task wants
head, _, _ = spec.partition("## 변경 이력")
spec = head + "## 변경 이력\n\n- rev 1: 첫 승인\n- rev 2: 글자 수 표시 추가 (`EVD-901`, `EVD-902`, `UNK-002`, `DEC-002`, `RULE-002`, `AC-002`, `TASK-002`) — 승인 대기\n"
# give the review page the same history, as a real page would
review = review.replace(
    '<section id="status">',
    '<section id="history"><h2>변경 이력</h2>\n<ul>\n<li>rev 1: 첫 승인</li>\n<li>rev 2: 글자 수 표시 추가 (승인 대기)</li>\n</ul>\n</section>\n\n<section id="status">')
review = review.replace('<a href="#status">상태</a>', '<a href="#history">이력</a><a href="#status">상태</a>')
(base / "MASTER_PLANNING_SPEC.md").write_text(spec, encoding="utf-8")
(base / "planning-review-core.html").write_text(review, encoding="utf-8")

def run(ver, script, *args):
    return subprocess.run([sys.executable, str(arms / ver / SK / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", env=env)

r = run("v1.7.2", "update_projection.py", base / "state.json", "--spec", base / "MASTER_PLANNING_SPEC.md",
        "--review", base / "planning-review-core.html", "--write")
assert r.returncode == 0, r.stdout + r.stderr

def scene(name, mutate_spec, mutate_review):
    d = here / name
    d.mkdir(exist_ok=True)
    shutil.copy(base / "state.json", d / "state.json")
    (d / "MASTER_PLANNING_SPEC.md").write_text(mutate_spec((base / "MASTER_PLANNING_SPEC.md").read_text(encoding="utf-8")), encoding="utf-8")
    (d / "planning-review-core.html").write_text(mutate_review((base / "planning-review-core.html").read_text(encoding="utf-8")), encoding="utf-8")
    for ver in ("v1.7.0", "v1.7.1", "v1.7.2"):
        r = run(ver, "projection_check.py", d / "state.json", "--spec", d / "MASTER_PLANNING_SPEC.md", "--review", d / "planning-review-core.html")
        out = r.stdout.replace(str(d), "<FIXTURE>").replace(str(d).replace("\\", "/"), "<FIXTURE>")
        (here / f"{name}-check-{ver[1:]}.json").write_text(out, encoding="utf-8")
        print(name, ver, "exit", r.returncode)

def s1_review(t):
    a = t.replace("<title>요청 폼 · 기획 검토 화면 revision 2</title>", "<title>요청 폼 · 기획 검토 화면 revision 0</title>")
    b = a.replace("<h1>요청 폼 기획 검토 (revision 2)</h1>", "<h1>요청 폼 기획 검토 (revision 0)</h1>")
    assert a != t and b != a
    return b

def s2_spec(t):
    old = "> Canonical authority remains `product-definition/request-form/state.json`.\n"
    assert old in t
    return t.replace(old, old + "> 승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)\n")

scene("scene1", lambda t: t, s1_review)
scene("scene2", s2_spec, lambda t: t)
shutil.rmtree(base)
