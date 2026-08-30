import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "skills" / "joewrks-product-definition"
SCRIPTS = PACKAGE_ROOT / "scripts"
for path in (PACKAGE_ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from downstream_v2.authority import (  # noqa: E402
    ACTION_CONTRACT_VERSION as ACTION_CONTRACT_VERSION_V20,
    SEMANTIC_REVIEW_VERSION as SEMANTIC_REVIEW_VERSION_V20,
)
from downstream_v2.derivation import (  # noqa: E402
    RESPONSIBILITY_PROFILE_ID as RESPONSIBILITY_PROFILE_ID_V10,
)
from downstream_v21.identity import (  # noqa: E402
    ACTION_CONTRACT_VERSION,
    HANDOFF_DEFINITION_VERSION,
    RESPONSIBILITY_PROFILE_ID,
    RUNTIME_EVIDENCE_BUNDLE_VERSION,
    RUNTIME_PLAN_VERSION,
    RUNTIME_PROFILE_ID,
    SEMANTIC_REVIEW_VERSION,
)


FROZEN_TREES = {
    "skills/joewrks-product-definition/downstream": "b63568d8c4632b14bc806e7bff1908e94dea9669",
    "skills/joewrks-product-definition/downstream_v2": "33fb2653531fa85dcc8fd8c94cbbb7cc5c41d41e",
    "evals/semantic-review-v0.4.3": "a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43",
}


class FrozenBoundaryTests(unittest.TestCase):
    def git_object(self, spec):
        return subprocess.check_output(
            ["git", "rev-parse", spec], cwd=ROOT, text=True,
        ).strip()

    def assert_worktree_matches_head(self, path):
        subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, check=True,
        )
        self.assertEqual(
            subprocess.check_output(
                ["git", "status", "--porcelain", "--untracked-files=all", "--", path],
                cwd=ROOT,
                text=True,
            ),
            "",
        )

    def test_historical_and_m5_trees_are_exact_and_clean(self):
        for path, expected in FROZEN_TREES.items():
            with self.subTest(path=path):
                self.assertEqual(self.git_object(f"HEAD:{path}"), expected)
                self.assert_worktree_matches_head(path)


class IdentityTests(unittest.TestCase):
    def test_downstream_v21_identities_are_exact(self):
        self.assertEqual(ACTION_CONTRACT_VERSION, "joewrks.action-conformance/2.1")
        self.assertEqual(HANDOFF_DEFINITION_VERSION, "joewrks.handoff-definition/2.1")
        self.assertEqual(RESPONSIBILITY_PROFILE_ID, "joewrks.downstream-responsibility/2.0")
        self.assertEqual(SEMANTIC_REVIEW_VERSION, "joewrks.semantic-review/2.1")
        self.assertEqual(RUNTIME_PLAN_VERSION, "joewrks.runtime-conformance-plan/1.0")
        self.assertEqual(RUNTIME_PROFILE_ID, "joewrks.runtime-responsibility/1.0")
        self.assertEqual(RUNTIME_EVIDENCE_BUNDLE_VERSION, "joewrks.runtime-evidence-bundle/1.0")

    def test_every_identity_with_a_predecessor_changes_version(self):
        self.assertNotEqual(ACTION_CONTRACT_VERSION, ACTION_CONTRACT_VERSION_V20)
        self.assertNotEqual(HANDOFF_DEFINITION_VERSION, "joewrks.handoff-definition/2.0")
        self.assertNotEqual(RESPONSIBILITY_PROFILE_ID, RESPONSIBILITY_PROFILE_ID_V10)
        self.assertNotEqual(SEMANTIC_REVIEW_VERSION, SEMANTIC_REVIEW_VERSION_V20)


if __name__ == "__main__":
    unittest.main()
