import base64
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.identity import RunIdentity, canonical_json_bytes, sha256_bytes
from reviewer_runner.request import InputArtifact, build_canonical_request

try:
    from reviewer_runner.providers.anthropic import (
        ANTHROPIC_MAX_PROVIDER_BODY_BYTES,
        AnthropicProjection,
        anthropic_settings_bytes,
        anthropic_settings_record,
        anthropic_settings_sha256,
        project_anthropic_request,
    )
except ImportError:
    ANTHROPIC_MAX_PROVIDER_BODY_BYTES = None
    AnthropicProjection = None
    anthropic_settings_bytes = None
    anthropic_settings_record = None
    anthropic_settings_sha256 = None
    project_anthropic_request = None


def _run_identity():
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


def _artifacts(*, review_package=b'{"package":true}'):
    return (
        InputArtifact("reviewer_brief", "text/markdown", b"Review only the declared inputs. \xce\x94"),
        InputArtifact("review_package", "application/json", review_package),
        InputArtifact("run_envelope", "application/json", b'{"run":true}'),
        InputArtifact("output_schema", "application/schema+json", b'{"type":"object"}'),
    )


def _request_bytes(*, review_package=b'{"package":true}'):
    return build_canonical_request(
        _run_identity(), _artifacts(review_package=review_package), controller_only_hashes={}
    ).content


def _request_document(*, review_package=b'{"package":true}'):
    return json.loads(_request_bytes(review_package=review_package))


def _canonical_request_bytes(document):
    return canonical_json_bytes(document)


def _header_and_content(block):
    header, separator, content = block["text"].partition("\n")
    if separator != "\n":
        raise AssertionError("projected user block has no canonical header separator")
    return json.loads(header), content


class ReviewerRunnerAnthropicProjectionTests(unittest.TestCase):
    def test_settings_record_and_hash_are_canonical_and_deterministic(self):
        self.assertIsNotNone(anthropic_settings_record)
        if anthropic_settings_record is None:
            return
        expected = {
            "api_version": "2023-06-01",
            "containers": "ABSENT",
            "effort": "high",
            "endpoint": "https://api.anthropic.com/v1/messages",
            "files": "ABSENT",
            "inference_geo": "us",
            "max_tokens": 65536,
            "mcp": "ABSENT",
            "model": "claude-sonnet-5",
            "output_mode": "plain_text_expected_to_be_exact_json",
            "projection": "joewrks.anthropic-message-projection/1.0",
            "retrieval": "ABSENT",
            "seed": "ABSENT_NO_API_FIELD_DOCUMENTED",
            "service_tier": "standard_only",
            "skills": "ABSENT",
            "stream": False,
            "temperature": "ABSENT",
            "thinking": {"type": "adaptive"},
            "tools": "ABSENT",
            "top_k": "ABSENT",
            "top_p": "ABSENT",
        }
        self.assertEqual(anthropic_settings_record(), expected)
        self.assertEqual(anthropic_settings_bytes(), canonical_json_bytes(expected))
        self.assertEqual(anthropic_settings_sha256(), sha256_bytes(anthropic_settings_bytes()))
        self.assertEqual(anthropic_settings_bytes(), anthropic_settings_bytes())

    def test_projection_has_one_system_block_and_three_ordered_user_blocks(self):
        self.assertIsNotNone(project_anthropic_request)
        if project_anthropic_request is None:
            return
        projection = project_anthropic_request(_request_bytes())
        self.assertIsInstance(projection, AnthropicProjection)
        body = json.loads(projection.provider_body)
        self.assertEqual(body["system"], [{"type": "text", "text": "Review only the declared inputs. Δ"}])
        self.assertEqual(len(body["messages"]), 1)
        self.assertEqual(body["messages"][0]["role"], "user")
        blocks = body["messages"][0]["content"]
        self.assertEqual(len(blocks), 3)
        self.assertEqual([_header_and_content(block)[0]["logical_role"] for block in blocks], ["review_package", "run_envelope", "output_schema"])
        self.assertTrue(all(block["type"] == "text" for block in blocks))
        self.assertEqual(projection.canonical_request_sha256, sha256_bytes(_request_bytes()))
        self.assertEqual((projection.reviewer_id, projection.review_run_id, projection.context_id), ("reviewer-001", "run-001", "context-001"))

    def test_user_block_header_is_canonical_json_newline_exact_content(self):
        self.assertIsNotNone(project_anthropic_request)
        if project_anthropic_request is None:
            return
        document = _request_document()
        projection = project_anthropic_request(_canonical_request_bytes(document))
        body = json.loads(projection.provider_body)
        input_by_role = {item["logical_role"]: item for item in document["inputs"]}
        for block in body["messages"][0]["content"]:
            header, content = _header_and_content(block)
            item = input_by_role[header["logical_role"]]
            expected_header = {
                "byte_count": item["byte_count"],
                "logical_role": item["logical_role"],
                "media_type": item["media_type"],
                "sha256": item["sha256"],
            }
            self.assertEqual(block["text"], canonical_json_bytes(expected_header).decode("utf-8") + "\n" + base64.b64decode(item["content_base64"], validate=True).decode("utf-8"))
            self.assertEqual(header, expected_header)
            self.assertEqual(content, base64.b64decode(item["content_base64"], validate=True).decode("utf-8"))

    def test_projection_rejects_duplicate_missing_extra_or_wrong_media_roles(self):
        self.assertIsNotNone(project_anthropic_request)
        if project_anthropic_request is None:
            return
        document = _request_document()
        cases = []
        duplicate = json.loads(json.dumps(document))
        duplicate["inputs"][1]["logical_role"] = "reviewer_brief"
        cases.append(duplicate)
        missing = json.loads(json.dumps(document))
        missing["inputs"] = missing["inputs"][:-1]
        cases.append(missing)
        extra = json.loads(json.dumps(document))
        extra["inputs"].append(json.loads(json.dumps(extra["inputs"][0])))
        extra["inputs"][-1]["logical_role"] = "unapproved"
        cases.append(extra)
        wrong_media = json.loads(json.dumps(document))
        wrong_media["inputs"][0]["media_type"] = "text/plain"
        cases.append(wrong_media)
        wrong_order = json.loads(json.dumps(document))
        wrong_order["inputs"] = list(reversed(wrong_order["inputs"]))
        cases.append(wrong_order)
        for candidate in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    project_anthropic_request(_canonical_request_bytes(candidate))

    def test_projection_rejects_bad_counts_hash_base64_utf8_and_duplicate_json_keys(self):
        self.assertIsNotNone(project_anthropic_request)
        if project_anthropic_request is None:
            return
        document = _request_document()
        bad_count = json.loads(json.dumps(document))
        bad_count["inputs"][0]["byte_count"] += 1
        bad_hash = json.loads(json.dumps(document))
        bad_hash["inputs"][1]["sha256"] = "0" * 64
        bad_base64 = json.loads(json.dumps(document))
        bad_base64["inputs"][2]["content_base64"] = "not*base64"
        bad_utf8 = json.loads(json.dumps(document))
        bad_utf8["inputs"][0]["content_base64"] = base64.b64encode(b"\xff").decode("ascii")
        bad_utf8["inputs"][0]["byte_count"] = 1
        bad_utf8["inputs"][0]["sha256"] = sha256_bytes(b"\xff")
        non_json_number = json.loads(json.dumps(document))
        non_json_number["inputs"][0]["byte_count"] = 1.0
        candidates = [bad_count, bad_hash, bad_base64, bad_utf8, non_json_number]
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    project_anthropic_request(_canonical_request_bytes(candidate))
        duplicate_keys = b'{"inputs":[],"inputs":[]}'
        with self.assertRaises(ValueError):
            project_anthropic_request(duplicate_keys)

    def test_provider_body_has_exact_fixed_settings_and_forbidden_fields_absent(self):
        self.assertIsNotNone(project_anthropic_request)
        if project_anthropic_request is None:
            return
        body = json.loads(project_anthropic_request(_request_bytes()).provider_body)
        self.assertEqual(
            body,
            {
                "inference_geo": "us",
                "max_tokens": 65536,
                "messages": [{"role": "user", "content": body["messages"][0]["content"]}],
                "model": "claude-sonnet-5",
                "output_config": {"effort": "high"},
                "service_tier": "standard_only",
                "stream": False,
                "system": [{"type": "text", "text": "Review only the declared inputs. Δ"}],
                "thinking": {"type": "adaptive"},
            },
        )
        self.assertEqual(project_anthropic_request(_request_bytes()).provider_body, canonical_json_bytes(body))
        serialized = projection_text = project_anthropic_request(_request_bytes()).provider_body.decode("utf-8")
        self.assertEqual(serialized, projection_text)
        for forbidden in ("temperature", "top_p", "top_k", "seed", "tools", "files", "containers", "skills", "mcp", "retrieval", "cache", "conversation", "continuation", "format"):
            self.assertNotIn(forbidden, serialized)

    def test_projection_is_unsplit_untruncated_and_size_bounded(self):
        self.assertIsNotNone(project_anthropic_request)
        if project_anthropic_request is None:
            return
        package = b"P" * 319_066
        projection = project_anthropic_request(_request_bytes(review_package=package))
        body = json.loads(projection.provider_body)
        blocks = body["messages"][0]["content"]
        package_blocks = [block for block in blocks if _header_and_content(block)[0]["logical_role"] == "review_package"]
        self.assertEqual(len(package_blocks), 1)
        self.assertEqual(_header_and_content(package_blocks[0])[1], package.decode("utf-8"))
        self.assertLessEqual(len(projection.provider_body), ANTHROPIC_MAX_PROVIDER_BODY_BYTES)
        too_large_package = b"P" * ANTHROPIC_MAX_PROVIDER_BODY_BYTES
        with self.assertRaises(ValueError):
            project_anthropic_request(_request_bytes(review_package=too_large_package))


if __name__ == "__main__":
    unittest.main()
