import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "skills/joewrks-product-definition/schemas/state.schema.json": "6a03894cc2164a9bfabbe8627a8468124d19b1f7",
    "skills/joewrks-product-definition/scripts/state_validation.py": "9a3b44359bddfd64c98392f235cb815a0b777cce",
    "skills/joewrks-product-definition/references/state-contract.md": "05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf",
    "skills/joewrks-product-definition/templates/state.example.json": "5fed7e87da243b3d234148bbbbf3baf7350d8ab0",
}


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class LegacyV0121FrozenTest(unittest.TestCase):
    def test_frozen_legacy_contract_bytes(self):
        for relative, expected in FROZEN.items():
            with self.subTest(relative=relative):
                self.assertEqual(git_blob_sha1((ROOT / relative).read_bytes()), expected)
