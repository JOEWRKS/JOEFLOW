import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from approval_v2 import definition_digest  # noqa: E402
from projection_check import check, draft  # noqa: E402
from tests.test_revision_v020 import _approved_rev1, _covered_binding, _record  # noqa: E402

TYPES = {"REQ", "RULE", "FLOW", "SCR", "STATE", "DATA", "INT", "AC", "TASK"}


def _spec_for(state, *extra_ids):
    approval = state["approval"]
    return (
        f"- Revision: `{state['project']['definition_revision']}`\n"
        f"- Definition digest: `{definition_digest(state)}`\n"
        f"- Approval Manifest digest: `{approval['approved_manifest_digest']}`\n"
        + "".join(f"| {record_id} | text |\n" for record_id in extra_ids)
    )


class ProjectionCheckTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path, self.state = _approved_rev1(self.directory.name)

    def test_current_identity_and_all_added_records_pass(self):
        added = [r["id"] for g in self.state["objects"].values() for r in g
                 if isinstance(r, dict) and r.get("id", "").split("-")[0] in TYPES]

        report = check(self.state, _spec_for(self.state, *added), _spec_for(self.state), TYPES)

        self.assertTrue(report["ok"], report)
        self.assertEqual(report["spec"]["stale_identity"], [])
        self.assertEqual(report["review"]["stale_identity"], [])

    def test_stale_identity_and_missing_records_are_reported(self):
        spec ="- Revision: `1`\nwidth 7px\n"

        report = check(self.state, spec, spec.replace("1", "x"), TYPES)

        self.assertFalse(report["ok"])
        self.assertIn("revision 1 is not mentioned", report["review"]["stale_identity"])
        self.assertTrue(any("definition_digest" in f for f in report["spec"]["stale_identity"]))
        self.assertTrue(report["spec"]["missing_added_records"])

    def test_bare_number_does_not_count_as_revision(self):
        report = check(self.state, "padding 1px\n", None, TYPES)
        self.assertIn("revision 1 is not mentioned", report["spec"]["stale_identity"])

    def test_changed_records_since_previous_approval_are_listed_to_reread(self):
        _, _, record_id = _covered_binding(self.state)
        group, record = _record(self.state, record_id)
        patch = Path(self.directory.name) / "patch.json"
        changed = copy.deepcopy(record)
        for key in ("statement", "assertion", "description"):
            if isinstance(changed.get(key), str):
                changed[key] += " (rev 2)"
        patch.write_text(json.dumps({"objects": {group: [changed]}}, ensure_ascii=False), encoding="utf-8")
        run = lambda *a: subprocess.run([sys.executable, str(SCRIPTS / a[0]), *map(str, a[1:])], cwd=ROOT, capture_output=True)
        self.assertEqual(run("open_revision.py", self.path, "--patch", patch, "--write").returncode, 0)
        state = json.loads(self.path.read_text(encoding="utf-8"))

        report = check(state, f"rev 2 mentions {record_id}", None, TYPES)

        self.assertEqual(report["compared_with_revision"], 1)
        self.assertIn(record_id, report["spec"]["changed_records_to_reread"])
        self.assertIn(f"`{record_id}`", draft(state))

    def test_cli_exit_codes(self):
        spec = Path(self.directory.name) / "spec.md"
        spec.write_text("nothing here", encoding="utf-8")
        run = lambda *a: subprocess.run([sys.executable, str(SCRIPTS / "projection_check.py"), *map(str, a)], cwd=ROOT, capture_output=True)
        self.assertEqual(run(self.path, "--spec", spec).returncode, 1)
        self.assertEqual(run(self.path, "--spec", spec, "--draft").returncode, 0)
        self.assertEqual(run(self.path, "--spec", spec.with_name("missing.md")).returncode, 2)


TEMPLATES = ROOT / "skills" / "joewrks-product-definition" / "templates"


def _review(head: str, body: str = "", title: str = "요청 폼 · Planning Review",
            identity: str = "<li>Revision: <code>1</code></li>") -> str:
    return (f"<!doctype html>\n<html lang=\"ko\">\n<head>\n<title>{title}</title>\n</head>\n<body>\n<main>\n"
            f"<header>\n{head}\n</header>\n<nav><a href=\"#s\">s</a></nav>\n"
            f"<section id=\"s\"><h2>상태</h2>\n{body}\n<ul>\n<!-- JOEFLOW:IDENTITY:BEGIN -->\n"
            f"{identity}\n<!-- JOEFLOW:IDENTITY:END -->\n</ul></section>\n</main>\n</body>\n</html>\n")


class StaleTitleRevisionTest(unittest.TestCase):
    """1.7.1: a hand-written title/header naming an old revision is reported even when the identity block is current."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path, self.state = _approved_rev1(self.directory.name)
        self.spec = _spec_for(self.state)
        self.identity = "\n".join(f"<li>{line[2:]}</li>" for line in self.spec.strip().split("\n"))

    def _titles(self, review, spec=None):
        report = check(self.state, spec or self.spec, review, TYPES)
        return report, report.get("review", {}).get("stale_title_revision"), report["spec"]["stale_title_revision"]

    def test_templates_refreshed_by_update_projection_pass(self):
        from update_projection import facts, refresh
        f = facts(self.state)
        review_template = (TEMPLATES / "planning-review-core.html").read_text(encoding="utf-8")
        review_template = review_template.replace("REVIEW VIEW · {{APPROVAL_STATUS}}",
                                                  "REVIEW VIEW · {{APPROVAL_STATUS}} · revision 0")
        review, _ = refresh(review_template, f, self.state, html=True)
        spec, _ = refresh((TEMPLATES / "master-planning-spec.md").read_text(encoding="utf-8"), f, self.state, html=False)

        self.assertIn("REVIEW VIEW · {{APPROVAL_STATUS}} · revision 1", review)
        report, review_findings, spec_findings = self._titles(review, spec)
        self.assertEqual((review_findings, spec_findings), ([], []), report)

    def test_review_view_form_with_current_revision_passes(self):
        _, findings, _ = self._titles(_review('<p class="note">JOEFLOW HUMAN REVIEW VIEW · APPROVED · revision 1</p>\n<h1>요청 폼</h1>'))
        self.assertEqual(findings, [])

    def test_hand_written_title_with_stale_revision_is_reported(self):
        review = _review("<h1>요청 폼 기획 검토 (revision 0)</h1>", title="요청 폼 · 기획 검토 화면 revision 0",
                         identity=self.identity)

        report, findings, _ = self._titles(review)

        self.assertFalse(report["ok"])
        self.assertEqual(report["review"]["stale_identity"], [])  # the identity block alone still passes
        self.assertEqual([(x["code"], x["where"], x["expected"], x["actual"]) for x in findings], [
            ("stale_review_title_revision", "<title>", 1, 0),
            ("stale_review_title_revision", "header", 1, 0),
        ])
        self.assertEqual(findings[0]["line"], 4)
        self.assertIn("change revision 0 to 1", findings[0]["next_action"])

    def test_spellings_used_in_hand_written_headers(self):
        for head in ("<h1>Spec Rev. 0</h1>", "<h1>검토 rev <code>0</code></h1>", "<h1>기획 개정 0</h1>",
                     "<h1>기획 개정판 0</h1>", "<p>리비전: 0</p>", "<p>REVISION #0</p>"):
            with self.subTest(head=head):
                _, findings, _ = self._titles(_review(head))
                self.assertEqual([x["actual"] for x in findings], [0])

    def test_earlier_revisions_in_body_comments_and_ranges_are_not_reported(self):
        review = _review(
            "<h1>요청 폼 (rev 0→1)</h1>\n<p>이전 승인 rev 0 · since revision 0</p>\n<!-- draft revision 0 -->\n"
            "<p>width 0px, approval-manifest-r0.json, prevision 0</p>",
            body="<p>변경 이력: rev 0에서 처음 작성, revision 0 기록</p>", identity=self.identity)
        report, findings, _ = self._titles(review)
        self.assertEqual(findings, [])
        self.assertEqual(report["review"]["stale_identity"], [])

    def test_markdown_spec_heading_is_checked_but_history_sections_are_not(self):
        spec = "# MASTER PLANNING SPEC — 요청 폼 revision 0\n\n> 설명\n\n## 승인 식별\n\n" + self.spec + "\n## 변경 이력\n\n- rev 0: 초안\n"
        report, _, findings = self._titles(None, spec)
        self.assertFalse(report["ok"])
        self.assertEqual([(x["code"], x["line"], x["actual"]) for x in findings], [("stale_spec_title_revision", 1, 0)])

        clean = spec.replace("revision 0\n", "\n", 1)
        self.assertEqual(self._titles(None, clean)[2], [])

    def test_cli_exits_1_on_stale_title(self):
        directory = Path(self.directory.name)
        (directory / "spec.md").write_text(self.spec, encoding="utf-8")
        (directory / "review.html").write_text(_review("<h1>검토 revision 0</h1>"), encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPTS / "projection_check.py"), str(self.path),
                                 "--spec", str(directory / "spec.md"), "--review", str(directory / "review.html")],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(json.loads(result.stdout)["review"]["stale_title_revision"][0]["code"],
                         "stale_review_title_revision")


if __name__ == "__main__":
    unittest.main()
