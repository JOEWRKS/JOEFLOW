import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

from downstream.semantic_review.hashing import (
    canonical_json_bytes,
    manifest_hash,
    package_hash,
    sha256_bytes,
    sha256_file,
)


class SemanticReviewHashingTest(unittest.TestCase):
    def test_canonical_json_bytes_are_stable_utf8_and_reject_nan(self):
        self.assertEqual(
            canonical_json_bytes({"z": "한글", "a": [2, 1]}),
            b'{"a":[2,1],"z":"\xed\x95\x9c\xea\xb8\x80"}',
        )
        with self.assertRaises(ValueError):
            canonical_json_bytes({"invalid": float("nan")})

    def test_sha256_file_reports_digest_and_exact_byte_count(self):
        payload = b"semantic-review\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.bin"
            path.write_bytes(payload)
            self.assertEqual(sha256_file(path), (sha256_bytes(payload), len(payload)))

    def test_manifest_hash_ignores_declared_self_hash_but_not_other_bytes(self):
        base = {"schema_version": "joewrks.semantic-review-input/1.0", "files": []}
        with_self = {**base, "reviewer_input_manifest_hash": "0" * 64}
        self.assertEqual(manifest_hash(base), manifest_hash(with_self))
        self.assertNotEqual(
            manifest_hash({**base, "files": [{"path": "a", "sha256": "1" * 64}]}),
            manifest_hash(base),
        )

    def test_package_hash_sorts_by_logical_role_and_path(self):
        files = [
            {
                "logical_role": "reviewer_brief",
                "path": "z",
                "sha256": "2" * 64,
                "bytes": 2,
            },
            {
                "logical_role": "action_contract",
                "path": "a",
                "sha256": "1" * 64,
                "bytes": 1,
            },
        ]
        self.assertEqual(
            package_hash("3" * 64, files),
            package_hash("3" * 64, list(reversed(files))),
        )


if __name__ == "__main__":
    unittest.main()
