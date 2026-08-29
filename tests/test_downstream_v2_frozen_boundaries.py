import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN_TREES = {
    "skills/joewrks-product-definition/downstream": "b63568d8c4632b14bc806e7bff1908e94dea9669",
    "evals/semantic-review-v0.4.3": "a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43",
}
FROZEN_BLOBS = {
    "skills/joewrks-product-definition/scripts/authority_binding_v2.py": "03704ea991aa72d20c2dd8c251ea22cbda8640ce",
    "skills/joewrks-product-definition/scripts/approval_v2.py": "41a70074d483b4e10a5954d1828a8de316919abe",
    "skills/joewrks-product-definition/scripts/state_validation_v2.py": "7acf26af546d299879dff29d30ca98a5753025a2",
    "skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json": "2cea7b11800728be2cc705f43daab5cf11f7d923",
    "skills/joewrks-product-definition/references/semantic-freeze-contract-v0.2.0.md": "d4abccaa93377bce8f5eb6181fb80186eff14550",
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
                cwd=ROOT, text=True,
            ),
            "",
        )

    def test_historical_trees_and_m4_core_blobs_are_exact(self):
        for path, expected in FROZEN_TREES.items():
            with self.subTest(path=path):
                self.assertEqual(self.git_object(f"HEAD:{path}"), expected)
                self.assert_worktree_matches_head(path)
        for path, expected in FROZEN_BLOBS.items():
            with self.subTest(path=path):
                self.assertEqual(self.git_object(f"HEAD:{path}"), expected)
                self.assert_worktree_matches_head(path)
