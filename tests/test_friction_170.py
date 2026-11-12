"""JOEFLOW 1.7.0 candidate: Gomoku friction A-D (2026-11-11)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from approval_v2 import approval_manifest_digest, build_approval_manifest_for_review  # noqa: E402
from grill_v2 import options_problems, recommendation_problems  # noqa: E402
from tests.test_approval_manifest_v020 import unicode_ready_state  # noqa: E402
from tests.test_revision_v020 import _approved_rev1  # noqa: E402


def _run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          cwd=ROOT, capture_output=True, check=False)


def _out(result):
    return result.stdout.decode("utf-8") + result.stderr.decode("utf-8")


OPTION = ("--option", "SHOW=보인다|평가가 보인다")


class OptionDiagnosticsTest(unittest.TestCase):
    """A: a rejected option names its index, field and value."""

    def test_reserved_option_id_is_named(self):
        options = [{"id": "SHOW", "statement": "보인다", "consequences": ["x"]},
                   {"id": "NONE", "statement": "안 보인다", "consequences": ["y"]}]
        problems = options_problems("MUTUALLY_EXCLUSIVE", options)
        self.assertEqual(len(problems), 1)
        self.assertIn("options[1].id 'NONE'", problems[0])
        self.assertIn("reserved", problems[0])

    def test_duplicate_and_missing_fields_are_named(self):
        options = [{"id": "A", "statement": "a", "consequences": []},
                   {"id": "A", "statement": "b", "consequences": ["c"], "extra": 1}]
        problems = options_problems("MUTUALLY_EXCLUSIVE", options)
        self.assertTrue(any("options[0].consequences must be a non-empty list" in p for p in problems))
        self.assertTrue(any("options[1] fields" in p and "unexpected ['extra']" in p for p in problems))

    def test_valid_options_have_no_problems(self):
        options = [{"id": "A", "statement": "a", "consequences": ["c"]},
                   {"id": "B", "statement": "b", "consequences": ["d"]}]
        self.assertEqual(options_problems("MUTUALLY_EXCLUSIVE", options), [])
        self.assertEqual(options_problems("OPEN_RESPONSE_REQUIRED", []), [])

    def test_recommendation_problems_name_missing_reason_and_tradeoff(self):
        options = [{"id": "A", "statement": "a", "consequences": ["c"]}]
        problems = recommendation_problems(
            {"recommended_option": "A", "reasoning_refs": [], "tradeoffs": [], "confidence": "HIGH"}, options)
        self.assertEqual(len(problems), 2)
        self.assertIn("--reason", problems[0])
        self.assertIn("--tradeoff", problems[1])
        self.assertIn("is not an option ID", recommendation_problems(
            {"recommended_option": "Z", "reasoning_refs": ["EVD-1"], "tradeoffs": ["t"], "confidence": "HIGH"},
            options)[0])

    def test_open_revision_message_names_the_option(self):
        with tempfile.TemporaryDirectory() as directory:
            path, state = _approved_rev1(directory)
            requirement = state["objects"]["requirements"][0]["id"]
            evidence = state["evidence"][0]["id"]
            patch = Path(directory) / "patch.json"
            # Built by hand: new_records.py now refuses the reserved ID before the patch exists.
            from record_builders import option, unknown
            question = unknown("UNK-950", question="평가를 보일까?", why="공정성", category="CORE_FLOW",
                               options=[option("SHOW", "보인다", "x"), option("NONE", "안 보인다", "y")],
                               affects=[requirement], evidence_refs=[evidence])
            patch.write_text(json.dumps({"objects": {"unknowns": [question]}}, ensure_ascii=False), encoding="utf-8")
            result = _run("open_revision.py", path, "--patch", patch)
            self.assertEqual(result.returncode, 1)
            messages = [error["message"] for error in json.loads(result.stdout)["validation_errors"]]
            self.assertTrue(any("options[1].id 'NONE' is a reserved non-answer word" in m for m in messages), messages)


class NewRecordsGuardsTest(unittest.TestCase):
    """A and B at generation time: new_records.py refuses what open_revision.py would reject."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.patch = Path(self.directory.name) / "patch.json"

    def run_records(self, *args):
        return _run("new_records.py", "--patch", self.patch, *args)

    def question(self, *extra, kind="question"):
        return self.run_records(kind, "--unknown", "UNK-960", "--question", "q?", "--why", "w", *OPTION,
                                "--affects", "REQ-001", "--evidence", "EVD-001", *extra)

    def test_reserved_option_id_is_refused(self):
        result = self.question("--option", "none=안 보인다|평가 없음")
        self.assertEqual(result.returncode, 2)
        self.assertIn("option ID 'none' is a reserved non-answer word", _out(result))
        self.assertFalse(self.patch.exists())

    def test_recommend_without_reason_or_tradeoff_is_refused(self):
        result = self.question("--option", "HIDE=안 보인다|평가 없음", "--recommend", "HIDE")
        self.assertEqual(result.returncode, 1)
        self.assertIn("needs --reason and --tradeoff", _out(result))
        self.assertFalse(self.patch.exists())

    def test_recommend_must_name_an_option(self):
        result = self.question("--option", "HIDE=안 보인다|평가 없음", "--recommend", "OTHER",
                               "--reason", "EVD-001", "--tradeoff", "t")
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not one of the --option IDs", _out(result))

    def test_accepted_without_recommend_is_refused(self):
        result = self.question("--option", "HIDE=안 보인다|평가 없음", "--decision", "DEC-960",
                               "--statement", "s", "--summary", "x", "--accepted", kind="user-decision")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--accepted records that the user accepted", _out(result))

    def test_help_marks_reason_and_tradeoff_required_with_recommend(self):
        text = " ".join(_out(_run("new_records.py", "--patch", self.patch, "user-decision", "--help")).split())
        self.assertIn("required (at least one) with --recommend", text)
        self.assertIn("requires --recommend, --reason and --tradeoff", text)
        self.assertIn("reserved non-answer word", " ".join(_out(_run("new_records.py", "--help")).split()))

    def test_relayed_records_the_question_it_answered(self):
        result = self.run_records("relayed", "--id", "EVD-961", "--relayer", "session X", "--quote", "A로 ㄱ",
                                  "--asked", "범위는 A·B·C 중 무엇인가요?")
        self.assertEqual(result.returncode, 0, _out(result))
        claim = json.loads(self.patch.read_text(encoding="utf-8"))["evidence"][0]["claim"]
        self.assertEqual(claim, '사용자 원문: "A로 ㄱ" — 답한 질문 원문: "범위는 A·B·C 중 무엇인가요?"')
        result = self.run_records("relayed", "--id", "EVD-962", "--relayer", "session X", "--quote", "끔 고정",
                                  "--asked-summary", "도우미를 어떻게 할지 물음")
        claim = json.loads(self.patch.read_text(encoding="utf-8"))["evidence"][1]["claim"]
        self.assertIn("답한 질문(전달자 요약, 원문 없음): 도우미를 어떻게 할지 물음", claim)


class ApprovalProvenanceTest(unittest.TestCase):
    """C: read-only check command, approval words and relay path kept next to state."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        state = unicode_ready_state()
        self.digest = approval_manifest_digest(build_approval_manifest_for_review(state))
        self.path = Path(self.directory.name) / "state.json"
        self.path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.original = self.path.read_bytes()

    def args(self, *extra):
        return (self.path, "--revision", 1, "--manifest-digest", self.digest, "--at", "2026-11-11T14:27:32Z", *extra)

    def test_check_approval_never_writes(self):
        result = _run("check_approval.py", *self.args())
        self.assertEqual(result.returncode, 0, _out(result))
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ready"])
        self.assertFalse(payload["written"])
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["state.json"])
        bad = json.loads(_run("check_approval.py", self.path, "--revision", 2, "--manifest-digest", "0" * 64).stdout)
        self.assertFalse(bad["ready"])
        self.assertEqual({e["code"] for e in bad["errors"]}, {"revision_mismatch", "manifest_digest_mismatch"})

    def test_relayed_approval_needs_the_users_words(self):
        for script, extra in (("check_approval.py", ()), ("record_approval.py", ("--write",))):
            result = _run(script, *self.args("--relayed-from", "session local_x", *extra))
            self.assertEqual(result.returncode, 1, script)
            self.assertIn("relayed_approval_needs_quote", _out(result))
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_write_with_quote_appends_provenance(self):
        result = _run("record_approval.py", *self.args("--quote", "이대로 승인", "--relayed-from", "session local_x", "--write"))
        self.assertEqual(result.returncode, 0, _out(result))
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["recorded"])
        self.assertIn("joeflow-project.json", receipt["next"])
        project = json.loads((self.path.parent / "joeflow-project.json").read_text(encoding="utf-8"))
        self.assertEqual(project["format"], "joeflow-project/1")
        entry = project["approvals"][0]
        self.assertEqual((entry["revision"], entry["manifest_digest"], entry["quote"], entry["relayed_from"],
                          entry["approved_at_source"]),
                         (1, self.digest, "이대로 승인", "session local_x", "user_message"))
        status = json.loads(_run("approval_status.py", self.path).stdout)
        self.assertEqual(status["approval_provenance"], [entry])

    def test_write_without_quote_leaves_no_sidecar(self):
        result = _run("record_approval.py", *self.args("--write"))
        self.assertEqual(result.returncode, 0, _out(result))
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["state.json"])


class VersionPinTest(unittest.TestCase):
    """D: the project records the JOEFLOW version it uses; scripts say when it differs."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path, self.state = _approved_rev1(self.directory.name)
        self.version = (SKILL / "VERSION").read_text(encoding="utf-8").strip()

    def test_skill_version_matches_program_version(self):
        self.assertEqual(self.version, (ROOT / "VERSION").read_text(encoding="utf-8").strip())

    def test_missing_pin_then_pin_then_mismatch(self):
        report = json.loads(_run("joeflow_version.py", self.path).stdout)
        self.assertIsNone(report["pinned_version"])
        self.assertIn("--pin", report["notice"])
        pinned = json.loads(_run("joeflow_version.py", self.path, "--pin").stdout)
        self.assertEqual((pinned["pinned_version"], pinned["notice"]), (self.version, None))
        status = json.loads(_run("approval_status.py", self.path).stdout)
        self.assertIsNone(status["joeflow_version"]["notice"])
        _run("joeflow_version.py", self.path, "--pin", "1.2.0")
        status = json.loads(_run("approval_status.py", self.path).stdout)
        self.assertIn("pins JOEFLOW 1.2.0", status["joeflow_version"]["notice"])
        project = json.loads((self.path.parent / "joeflow-project.json").read_text(encoding="utf-8"))
        self.assertEqual(project["joeflow_version"], "1.2.0")

    def test_open_revision_reports_version_notice_and_schema(self):
        patch = Path(self.directory.name) / "patch.json"
        patch.write_text("{}", encoding="utf-8")
        result = json.loads(_run("open_revision.py", self.path, "--patch", patch).stdout)
        self.assertIn("does not record which JOEFLOW version", result.get("version_notice", ""))
        legacy = Path(self.directory.name) / "legacy.json"
        legacy.write_text(json.dumps({"schema_version": "0.1.2.1"}), encoding="utf-8")
        result = json.loads(_run("open_revision.py", legacy, "--patch", patch).stdout)
        message = result["errors"][0]["message"]
        self.assertIn("found '0.1.2.1'", message)
        self.assertIn("migrate_state.py", message)


if __name__ == "__main__":
    unittest.main()


class IntegrationTrialFixesTest(unittest.TestCase):
    """Defects found in the three-tool trial (evals/2026-11-12-friction-170)."""

    def test_ready_for_review_write_is_refused_while_a_rule_is_orphan(self):
        with tempfile.TemporaryDirectory() as directory:
            path, state = _approved_rev1(directory)
            requirement = state["objects"]["requirements"][0]["id"]
            patch = Path(directory) / "patch.json"
            rule = {"id": "RULE-950", "status": "CURRENT", "statement": "새 규칙이 아무 칸에도 묶이지 않았다.",
                    "applies_to": [requirement]}
            patch.write_text(json.dumps({"objects": {"rules": [rule]}}, ensure_ascii=False), encoding="utf-8")
            before = path.read_bytes()
            result = _run("open_revision.py", path, "--patch", patch, "--write")
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1, _out(result))
            self.assertFalse(payload["written"])
            self.assertEqual(path.read_bytes(), before)
            self.assertIn({"code": "orphan_material_authority", "object_id": "RULE-950"},
                          [{k: f[k] for k in ("code", "object_id")} for f in payload["readiness_findings"]])
            self.assertIn("--status OPEN", payload["readiness_message"])
            opened = _run("open_revision.py", path, "--patch", patch, "--status", "OPEN", "--write")
            self.assertEqual(opened.returncode, 0, _out(opened))
            manifest = _run("build_approval_manifest.py", path)
            self.assertEqual(manifest.returncode, 1)
            blocked = json.loads(manifest.stdout)
            self.assertEqual(blocked["semantic_readiness_metrics"], {"orphan_material_authority": 1})
            self.assertEqual([f["object_id"] for f in blocked["findings"]], ["RULE-950"])

    def test_empty_and_crlf_projection_blocks_are_regenerated(self):
        from tests.test_semantic_closure_v020 import literal_approved_state
        from update_projection import facts, refresh
        state = literal_approved_state()
        text = ("# Spec\n\n<!-- JOEFLOW:IDENTITY:BEGIN -->\n<!-- JOEFLOW:IDENTITY:END -->\n\n"
                "<!-- JOEFLOW:SOURCE-MAP:BEGIN -->\r\n<!-- JOEFLOW:SOURCE-MAP:END -->\n")
        refreshed, notes = refresh(text, facts(state), state, html=False)
        self.assertIn("identity block regenerated", notes)
        self.assertIn("source map block regenerated", notes)
        self.assertIn("Definition digest:", refreshed)
