"""Build spec + review projections for the scratch rev 2 state, then hand-title the review with a stale revision."""
import json, re, subprocess, sys
from pathlib import Path
here = Path(__file__).parent
R = Path("D:/JOEWRKS/JOEFLOW"); T = R / "skills/joewrks-product-definition/templates"; SC = R / "skills/joewrks-product-definition/scripts"
state = json.loads((here / "state.json").read_text(encoding="utf-8"))
ids = [r["id"] for g in state["objects"].values() for r in g if isinstance(r, dict) and "id" in r]
spec = T.joinpath("master-planning-spec.md").read_text(encoding="utf-8").replace("{{project_name}}", "요청 폼")
spec += "\n## 레코드\n\n" + "".join(f"| {i} | text |\n" for i in ids) + "\n## 변경 이력\n\n- rev 1: 첫 승인\n- revision 1에서 rev 2로: 글자 수 표시\n"
(here / "MASTER_PLANNING_SPEC.md").write_text(spec, encoding="utf-8")
review = T.joinpath("planning-review-core.html").read_text(encoding="utf-8").replace("{{project_name}}", "요청 폼")
(here / "planning-review-core.html").write_text(review, encoding="utf-8")
subprocess.run([sys.executable, str(SC / "update_projection.py"), str(here / "state.json"), "--spec", str(here / "MASTER_PLANNING_SPEC.md"),
                "--review", str(here / "planning-review-core.html"), "--write"], check=True, capture_output=True)
# hand-written title and header, as in the 1.7.0 integration trial: not the REVIEW VIEW form
text = (here / "planning-review-core.html").read_text(encoding="utf-8")
text = text.replace("<title>요청 폼 · Planning Review</title>", "<title>요청 폼 · 기획 검토 화면 revision 0</title>")
text = text.replace("<h1>요청 폼</h1>", "<h1>요청 폼 기획 검토 (revision 0)</h1>")
(here / "planning-review-core.html").write_text(text, encoding="utf-8")
