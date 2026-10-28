import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "joewrks-product-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from state_validation_v2 import validate_state_v2  # noqa: E402
from tests.test_revision_v020 import _approved_rev1  # noqa: E402


def _run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          cwd=ROOT, capture_output=True, check=False)


class NewRecordsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path, self.state = _approved_rev1(self.directory.name)
        self.patch = Path(self.directory.name) / "patch.json"
        self.requirement = self.state["objects"]["requirements"][0]["id"]

    def add(self, *args):
        result = _run("new_records.py", "--patch", self.patch, *args)
        self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8") + result.stderr.decode("utf-8"))
        return json.loads(result.stdout)

    def add_user_evidence(self):
        self.add("evidence", "--id", "EVD-701", "--source-kind", "USER_CONFIRMED_INTENT", "--class", "INTENT",
                 "--locator", "채팅 2026-10-28", "--claim", "사용자가 기본값을 바꾸라고 했다.")

    def add_observed_evidence(self):
        self.add("evidence", "--id", "EVD-702", "--source-kind", "OBSERVED_IMPLEMENTATION", "--class", "FACTUAL",
                 "--locator", "src/app.ts", "--claim", "현재 구현은 알림을 보내지 않는다.")

    def test_user_decision_and_authoring_records_open_a_valid_revision(self):
        self.add_user_evidence()
        self.add("user-decision", "--unknown", "UNK-701", "--decision", "DEC-701",
                 "--question", "기본값을 무엇으로 할까요?", "--why", "승인된 동작이 바뀐다.",
                 "--option", "A=새 기본값|사용자 지시", "--option", "B=그대로|바뀌지 않음",
                 "--affects", self.requirement, "--evidence", "EVD-701",
                 "--statement", "기본값을 새 값으로 바꾼다.", "--summary", "사용자 지시: \"기본값 바꿔\"")
        self.add("authoring", "--unknown", "UNK-702", "--decision", "DEC-702",
                 "--task", "rev 2 결정을 레코드로 옮기기", "--why", "작성 작업이다.", "--summary", "DEC-701을 옮겼다.",
                 "--statement", "DEC-701을 기록한다.", "--affects", self.requirement, "--evidence", "EVD-701")

        result = _run("open_revision.py", self.path, "--patch", self.patch, "--write")

        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, json.dumps(report["validation_errors"], ensure_ascii=False)[:2000])
        self.assertEqual(sorted(report["added"]), ["DEC-701", "DEC-702", "EVD-701", "UNK-701", "UNK-702"])
        written = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(validate_state_v2(written), [])
        decision = next(d for d in written["objects"]["decisions"] if d["id"] == "DEC-701")
        self.assertEqual((decision["decided_by"], decision["resolution_mode"]), ("USER", "USER_DECISION"))

    def test_open_question_with_recommendation_is_asked_next(self):
        # Intent evidence goes in --reason; --evidence holding it would make the question EVIDENCE_RESOLVABLE.
        self.add_user_evidence()
        self.add_observed_evidence()
        self.add("question", "--unknown", "UNK-703", "--question", "알림을 켤까요?", "--why", "사용자에게 보인다.",
                 "--option", "A=켠다|알림이 생긴다", "--option", "B=끈다|지금과 같다", "--affects", self.requirement,
                 "--evidence", "EVD-702", "--recommend", "A", "--reason", "EVD-701", "--tradeoff", "알림이 늘어난다.")
        self.assertEqual(_run("open_revision.py", self.path, "--patch", self.patch, "--status", "OPEN", "--write").returncode, 0)

        question = json.loads(_run("next_product_question.py", self.path).stdout)["next_question"]

        self.assertEqual(question["unknown_id"], "UNK-703")

    def test_accepted_recommendation_reproduces_presented_options(self):
        self.add_user_evidence()
        self.add("user-decision", "--unknown", "UNK-704", "--decision", "DEC-704", "--question", "q?", "--why", "w",
                 "--option", "A=첫째|결과 1", "--option", "B=둘째|결과 2", "--option", "C=셋째|결과 3", "--affects", self.requirement,
                 "--evidence", "EVD-701", "--recommend", "B", "--reason", "EVD-701", "--tradeoff", "둘째는 느리다.",
                 "--accepted", "--statement", "B를 쓴다.", "--summary", "추천에 \"좋아\"")
        decision = json.loads(self.patch.read_text(encoding="utf-8"))["objects"]["decisions"][0]
        self.assertEqual(decision["accepted_recommendation"]["alternatives_presented"], ["A", "B", "C"])
        self.assertEqual(decision["resolution_mode"], "USER_ACCEPTED_RECOMMENDATION")
        self.assertEqual(_run("open_revision.py", self.path, "--patch", self.patch).returncode, 0)

    def test_duplicate_ids_and_bad_options_are_refused(self):
        self.add_user_evidence()
        duplicate = _run("new_records.py", "--patch", self.patch, "evidence", "--id", "EVD-701", "--source-kind",
                         "USER_CONFIRMED_INTENT", "--class", "INTENT", "--locator", "x", "--claim", "y")
        self.assertEqual(duplicate.returncode, 1)
        self.assertIn("EVD-701", json.loads(duplicate.stdout)["error"])
        for option in ("A", "A=no consequence"):
            bad = _run("new_records.py", "--patch", self.patch, "question", "--unknown", "UNK-9", "--question", "q",
                       "--why", "w", "--option", option, "--option", "B=b|c", "--affects", "X", "--evidence", "E")
            self.assertEqual(bad.returncode, 2)
            self.assertIn(b"ID=statement|consequence", bad.stderr)

    def test_intent_evidence_on_a_question_gets_an_explained_error(self):
        self.add_user_evidence()
        self.add("question", "--unknown", "UNK-705", "--question", "알림을 켤까요?", "--why", "사용자에게 보인다.",
                 "--option", "A=켠다|알림이 생긴다", "--option", "B=끈다|지금과 같다", "--affects", self.requirement,
                 "--evidence", "EVD-701")
        report = json.loads(_run("open_revision.py", self.path, "--patch", self.patch, "--status", "OPEN").stdout)
        messages = [e["message"] for e in report["validation_errors"] if e["code"] == "invalid_decision_authority_derivation"]
        self.assertTrue(messages, report["validation_errors"])
        self.assertIn("evidence_refs ['EVD-701'] already support 'INTENT'", messages[0])


if __name__ == "__main__":
    unittest.main()
