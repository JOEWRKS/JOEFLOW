import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.v020_support import evidence_record, evidence_with_grill_basis, foundation_state, unknown_record
except ModuleNotFoundError:
    from v020_support import evidence_record, evidence_with_grill_basis, foundation_state, unknown_record


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from state_validation_v2 import validate_state_v2


KOREAN_QUESTION = "AI가 어디에 둬도 지는 판에서 어떤 수를 둘까요 — 구석 수 방지"
MISSING_NAME = "없는—상태.json"
UTF8_CLIS = (
    "next_product_question.py",
    "authority_binding_value.py",
    "build_discovery_baseline.py",
    "migrate_state.py",
)


def _console_environment(**overrides):
    """Inherit the platform pipe encoding (cp949 on Korean Windows) instead of a UTF-8 override."""
    environment = {
        key: value for key, value in os.environ.items()
        if key not in {"PYTHONIOENCODING", "PYTHONUTF8"}
    }
    environment.update(overrides)
    return environment


def _run(script, *args, **overrides):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        check=False,
        env=_console_environment(**overrides),
    )


def _korean_question_state():
    state = foundation_state()
    unknown = unknown_record("UNK-001")
    unknown["question"] = KOREAN_QUESTION
    state["objects"]["unknowns"] = [unknown]
    state["evidence"] = evidence_with_grill_basis(evidence_record(
        source_kind="USER_CONFIRMED_INTENT",
        authority_classes=["INTENT"],
        claim="The user-confirmed intent supports this product choice.",
    ))
    return state


class CliUtf8OutputTest(unittest.TestCase):
    def test_next_question_with_korean_text_is_utf8_on_a_redirected_stream(self):
        state = _korean_question_state()
        self.assertEqual(validate_state_v2(state), [])
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = _run("next_product_question.py", state_path)

        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertEqual(result.stderr, b"")
        payload = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(payload["next_question"]["question"], KOREAN_QUESTION)

    def test_read_errors_with_korean_paths_are_utf8_on_stdout_and_stderr(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / MISSING_NAME
            cases = (
                ("next_product_question.py", (missing,), "stdout"),
                ("authority_binding_value.py", (missing, "RULE-001", "/statement"), "stdout"),
                ("migrate_state.py", ("--plan", missing), "stderr"),
            )
            for script, args, channel in cases:
                with self.subTest(script=script):
                    result = _run(script, *args)
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn(b"UnicodeEncodeError", result.stderr)
                    self.assertIn(MISSING_NAME, getattr(result, channel).decode("utf-8"))

    def test_explicit_pythonioencoding_is_respected(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "없는상태.json"
            result = _run("next_product_question.py", missing, PYTHONIOENCODING="cp949")

        self.assertEqual(result.returncode, 2)
        self.assertIn("없는상태.json", result.stdout.decode("cp949"))

    def test_discovery_baseline_success_output_is_unchanged_ascii(self):
        result = _run("build_discovery_baseline.py", SKILL / "templates" / "state-v0.2.0.example.json")

        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertTrue(result.stdout.isascii())
        self.assertEqual(json.loads(result.stdout)["status"], "CURRENT")

    def test_human_readable_clis_enable_utf8_stdio_before_main(self):
        for script in UTF8_CLIS:
            with self.subTest(script=script):
                tree = ast.parse((SCRIPTS / script).read_text(encoding="utf-8"))
                guard = next(
                    node for node in tree.body
                    if isinstance(node, ast.If)
                    and isinstance(node.test, ast.Compare)
                    and isinstance(node.test.left, ast.Name)
                    and node.test.left.id == "__name__"
                )
                first = guard.body[0]
                self.assertIsInstance(first, ast.Expr)
                self.assertEqual(first.value.func.id, "use_utf8_stdio")


if __name__ == "__main__":
    unittest.main()
