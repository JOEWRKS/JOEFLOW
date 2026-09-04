import base64
import dataclasses
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
sys.path.insert(0, str(SKILL_ROOT))

try:
    from reviewer_runner.identity import RunIdentity, canonical_json_bytes, sha256_bytes
    from reviewer_runner.request import (
        CanonicalRequest,
        InputArtifact,
        build_canonical_request,
        build_permitted_inventory,
    )
except ModuleNotFoundError:
    _REQUEST_IMPORT_ERROR = True
else:
    _REQUEST_IMPORT_ERROR = False


REQUIRED_ROLES = (
    "reviewer_brief",
    "review_package",
    "run_envelope",
    "output_schema",
)


def run_identity():
    if _REQUEST_IMPORT_ERROR:
        raise AssertionError("reviewer_runner.request must implement canonical requests")
    return RunIdentity(
        semantic_review_contract_version="joewrks.semantic-review/1.0",
        package_schema_version="joewrks.semantic-review-input/1.0",
        package_digest=sha256_bytes(b"package"),
        source_action_contract_hash=sha256_bytes(b"action-contract"),
        source_definition_digest=sha256_bytes(b"definition"),
        reviewer_id="reviewer-001",
        review_run_id="run-001",
        context_id="context-001",
        cohort_id=None,
        case_id=None,
    )


def artifacts():
    if _REQUEST_IMPORT_ERROR:
        raise AssertionError("reviewer_runner.request must implement canonical requests")
    return (
        InputArtifact("reviewer_brief", "text/markdown", b"brief \xce\x84"),
        InputArtifact("review_package", "application/json", b'{"package":true}'),
        InputArtifact("run_envelope", "application/json", b'{"run":true}'),
        InputArtifact("output_schema", "application/schema+json", b'{"type":"object"}'),
    )


class ReviewerRunnerRequestTests(unittest.TestCase):
    def setUp(self):
        if _REQUEST_IMPORT_ERROR:
            self.fail("reviewer_runner.request must implement canonical requests")

    def test_exact_four_roles_are_sorted_and_inlined(self):
        inventory = build_permitted_inventory(tuple(reversed(artifacts())))
        self.assertEqual(tuple(item.logical_role for item in inventory), tuple(sorted(REQUIRED_ROLES)))

        request = build_canonical_request(
            run_identity(),
            tuple(reversed(artifacts())),
            controller_only_hashes={},
        )
        self.assertEqual(
            set(dataclasses.asdict(request)),
            {"content", "sha256", "inventory"},
        )
        self.assertEqual(request.sha256, sha256_bytes(request.content))
        self.assertEqual(request.inventory, inventory)
        document = json.loads(request.content)
        self.assertEqual(
            set(document),
            {
                "request_schema_version",
                "runner_contract_version",
                "run_identity",
                "inputs",
                "response_contract",
            },
        )
        self.assertEqual(
            [item["logical_role"] for item in document["inputs"]], sorted(REQUIRED_ROLES)
        )
        self.assertEqual(
            set(document["run_identity"]),
            {
                "semantic_review_contract_version",
                "package_schema_version",
                "reviewer_id",
                "review_run_id",
                "context_id",
            },
        )
        for item, artifact in zip(document["inputs"], sorted(artifacts(), key=lambda item: item.logical_role)):
            self.assertEqual(
                set(item),
                {"logical_role", "media_type", "byte_count", "sha256", "content_base64"},
            )
            self.assertEqual(base64.b64decode(item["content_base64"], validate=True), artifact.content)
            self.assertEqual(item["byte_count"], len(artifact.content))
            self.assertEqual(item["sha256"], sha256_bytes(artifact.content))
        self.assertEqual(
            document["response_contract"],
            {"logical_response_count": 1, "media_type": "application/json"},
        )

    def test_missing_role_is_rejected(self):
        with self.assertRaises(ValueError):
            build_permitted_inventory(artifacts()[:-1])

    def test_extra_or_duplicate_role_is_rejected(self):
        duplicate = artifacts() + (artifacts()[0],)
        extra = artifacts() + (InputArtifact("unapproved", "text/plain", b"extra"),)
        for candidate in (duplicate, extra):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    build_permitted_inventory(candidate)

    def test_artifact_has_no_path_uri_file_id_or_arbitrary_metadata(self):
        self.assertEqual(
            {field.name for field in dataclasses.fields(InputArtifact)},
            {"logical_role", "media_type", "content"},
        )
        with self.assertRaises(TypeError):
            InputArtifact("reviewer_brief", "text/markdown", b"brief", path="C:/secret")

    def test_artifact_subclass_with_path_is_rejected(self):
        @dataclasses.dataclass(frozen=True, slots=True)
        class ExtendedArtifact(InputArtifact):
            path: str

        extended_artifacts = (
            ExtendedArtifact("reviewer_brief", "text/markdown", b"brief", "C:/secret"),
            *artifacts()[1:],
        )
        with self.assertRaises(ValueError):
            build_permitted_inventory(extended_artifacts)
        with self.assertRaises(ValueError):
            build_canonical_request(
                run_identity(),
                extended_artifacts,
                controller_only_hashes={},
            )

    def test_controller_only_oracle_sibling_and_prior_hashes_are_rejected(self):
        for artifact in artifacts():
            with self.subTest(role=artifact.logical_role):
                with self.assertRaises(ValueError):
                    build_canonical_request(
                        run_identity(),
                        artifacts(),
                        controller_only_hashes={
                            "oracle": sha256_bytes(artifact.content)
                        },
                    )

        request = build_canonical_request(
            run_identity(),
            artifacts(),
            controller_only_hashes={"oracle": sha256_bytes(b"other")},
        )
        serialized = request.content.decode("utf-8")
        self.assertNotIn("oracle", serialized)
        self.assertNotIn(sha256_bytes(b"other"), serialized)

    def test_request_has_no_tools_retrieval_environment_or_continuation_fields(self):
        document = json.loads(
            build_canonical_request(
                run_identity(),
                artifacts(),
                controller_only_hashes={},
            ).content
        )
        serialized = json.dumps(document, sort_keys=True)
        for forbidden in (
            "tools",
            "retrieval",
            "environment",
            "continuation",
            "path",
            "uri",
            "file_id",
            "metadata",
            "chunks",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_request_bytes_are_deterministic_for_unicode_and_binary_payloads(self):
        unicode_and_binary = (
            InputArtifact("reviewer_brief", "text/markdown", "한글 \xce\x84".encode("utf-8")),
            InputArtifact("review_package", "application/octet-stream", b"\x00\xff\x80package"),
            InputArtifact("run_envelope", "application/json", b'{"run":"\xe2\x9c\x93"}'),
            InputArtifact("output_schema", "application/schema+json", b'{"type":"object"}'),
        )
        first = build_canonical_request(
            run_identity(),
            unicode_and_binary,
            controller_only_hashes={},
        )
        second = build_canonical_request(
            run_identity(),
            tuple(reversed(unicode_and_binary)),
            controller_only_hashes={},
        )
        self.assertEqual(first, second)
        self.assertEqual(first.content, canonical_json_bytes(json.loads(first.content)))

    def test_controller_only_hashes_is_keyword_only(self):
        with self.assertRaises(TypeError):
            build_canonical_request(run_identity(), artifacts(), {})

    def test_319066_byte_package_is_one_unsplit_inline_artifact(self):
        large_artifacts = tuple(
            InputArtifact(item.logical_role, item.media_type, b"P" * 319_066)
            if item.logical_role == "review_package"
            else item
            for item in artifacts()
        )
        request = build_canonical_request(run_identity(), large_artifacts, controller_only_hashes={})
        document = json.loads(request.content)
        package = next(item for item in document["inputs"] if item["logical_role"] == "review_package")
        self.assertEqual(base64.b64decode(package["content_base64"]), b"P" * 319_066)
        self.assertEqual(len([item for item in document["inputs"] if item["logical_role"] == "review_package"]), 1)
        self.assertNotIn("chunks", document)
        self.assertNotIn("continuation_id", document)


if __name__ == "__main__":
    unittest.main()
