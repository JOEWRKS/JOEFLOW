import base64
import dataclasses
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.backend import (  # noqa: E402
    BackendEvent,
    REQUIRED_CAPABILITIES,
)
from reviewer_runner.identity import (  # noqa: E402
    CapabilityClass,
    RunnerState,
    sha256_bytes,
)
from tests.reviewer_runner_support import DeterministicFakeBackend  # noqa: E402

try:
    from reviewer_runner.preflight import (  # noqa: E402
        PROBE_SCHEMA_VERSION,
        build_per_run_isolation_receipt,
        build_preflight_freshness,
        classify_backend_eligibility,
        run_isolation_preflight,
        validate_preflight_freshness,
    )
except ModuleNotFoundError:
    _PREFLIGHT_IMPORT_ERROR = True
else:
    _PREFLIGHT_IMPORT_ERROR = False


PATH_SAMPLES = (
    r"D:\repository\secret.txt",
    r"\\server\share\secret.txt",
    "/workspace/repository/secret.txt",
    "../secret.txt",
    "%2e%2e%2fsecret.txt",
    ".git/HEAD",
    "D:/worktree/sibling/output.json",
    "/tmp/prior-output.json",
    "symlink->../secret",
    "junction->D:\\repository",
)

FORBIDDEN_FAMILIES = (
    "repository-only",
    ".git/history",
    "golden/oracle",
    "evaluator-only",
    "sibling-package",
    "sibling-output",
    "prior-output",
    "environment-only",
    "parent/common-temp",
)


def nonce_bytes(label: str) -> bytes:
    return bytes.fromhex(sha256_bytes(("nonce:" + label).encode("utf-8")))


def response_bytes(allowed_nonce: str, **extra: object) -> bytes:
    return json.dumps(
        {
            "probe_schema_version": PROBE_SCHEMA_VERSION,
            "allowed_nonce": allowed_nonce,
            "response_count": 1,
            **extra,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def package_from_request(request_bytes: bytes) -> bytes:
    request = json.loads(request_bytes)
    package = next(
        item for item in request["inputs"] if item["logical_role"] == "review_package"
    )
    return base64.b64decode(package["content_base64"], validate=True)


def observed_probe_backend(**kwargs):
    from tests.reviewer_runner_support import observed_probe_backend as build_backend

    return build_backend(**kwargs)


def observed_probe_descriptor():
    from tests.reviewer_runner_support import observed_probe_descriptor as build_descriptor

    return build_descriptor()


class ReviewerRunnerPreflightTests(unittest.TestCase):
    def setUp(self):
        if _PREFLIGHT_IMPORT_ERROR:
            self.fail("reviewer_runner.preflight must implement the synthetic isolation preflight")

    def _freshness(self, backend):
        return build_preflight_freshness(backend.describe().identity)

    def test_positive_probe_returns_exact_allowed_nonce_once(self):
        backend = observed_probe_backend(nonce_source=nonce_bytes)
        freshness = self._freshness(backend)

        result = run_isolation_preflight(
            backend,
            freshness=freshness,
            nonce_source=nonce_bytes,
        )

        self.assertEqual(result.classification, CapabilityClass.OBSERVED_PASS)
        self.assertEqual(len(backend.received_request_bytes), 1)
        allowed_nonce = nonce_bytes("allowed-package-brief").hex()
        self.assertEqual(
            result.response_sha256,
            sha256_bytes(response_bytes(allowed_nonce)),
        )
        self.assertEqual(response_bytes(allowed_nonce).decode("utf-8").count(allowed_nonce), 1)
        self.assertEqual(
            tuple(observation.capability for observation in result.observations),
            REQUIRED_CAPABILITIES,
        )
        self.assertTrue(all(
            observation.classification is CapabilityClass.OBSERVED_PASS
            for observation in result.observations
        ))
        self.assertEqual(len(result.forbidden_canary_hashes), 9)
        self.assertEqual(len(set(result.forbidden_canary_hashes)), 9)
        request_bytes = backend.received_request_bytes[0]
        for family in FORBIDDEN_FAMILIES:
            self.assertNotIn(nonce_bytes(family).hex().encode("ascii"), request_bytes)

        receipt = build_per_run_isolation_receipt(
            result,
            current_freshness=freshness,
            backend_identity=backend.describe().identity,
            request_sha256=sha256_bytes(b"bound semantic request"),
        )
        self.assertEqual(receipt.classification, CapabilityClass.OBSERVED_PASS)
        self.assertEqual(receipt.preflight_evidence_sha256, result.evidence_sha256)
        self.assertEqual(len(receipt.receipt_sha256), 64)

    def test_each_forbidden_canary_family_fails_if_leaked(self):
        for family in FORBIDDEN_FAMILIES:
            with self.subTest(family=family):
                leaked_nonce = nonce_bytes(family).hex()
                backend = observed_probe_backend(
                    nonce_source=nonce_bytes,
                    response_factory=lambda allowed, leak=leaked_nonce: response_bytes(
                        allowed, leaked_forbidden_nonce=leak
                    ),
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                self.assertEqual(result.classification, CapabilityClass.OBSERVED_FAIL)
                self.assertIn(sha256_bytes(nonce_bytes(family)), result.forbidden_canary_hashes)

    def test_windows_unix_unc_traversal_git_symlink_and_junction_strings_are_inert(self):
        resolver_calls = []
        backend = observed_probe_backend(
            nonce_source=nonce_bytes,
            resolver_callback=lambda value: resolver_calls.append(value),
        )

        result = run_isolation_preflight(
            backend,
            freshness=self._freshness(backend),
            nonce_source=nonce_bytes,
        )

        self.assertEqual(result.classification, CapabilityClass.OBSERVED_PASS)
        package = json.loads(package_from_request(backend.received_request_bytes[0]))
        self.assertEqual(tuple(package["path_samples"]), PATH_SAMPLES)
        self.assertEqual(resolver_calls, [])
        self.assertEqual(backend.returned_events, ())

    def test_tool_or_retrieval_event_fails_preflight(self):
        for kind in ("tool", "retrieval", "file"):
            with self.subTest(kind=kind):
                event = BackendEvent(kind, sha256_bytes(("event:" + kind).encode("utf-8")))
                backend = observed_probe_backend(nonce_source=nonce_bytes, events=(event,))
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                self.assertEqual(result.classification, CapabilityClass.OBSERVED_FAIL)

    def test_continuation_or_previous_response_id_fails_preflight(self):
        for field in ("continuation_id", "previous_response_id"):
            with self.subTest(field=field):
                backend = observed_probe_backend(
                    nonce_source=nonce_bytes,
                    metadata_drift={field: "prior-response"},
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                self.assertEqual(result.classification, CapabilityClass.OBSERVED_FAIL)

    def test_unknown_or_inferred_capability_never_passes(self):
        for classification, method in (
            (CapabilityClass.UNTESTED, "unknown"),
            (CapabilityClass.OBSERVED_PASS, "inferred-from-provider-docs"),
        ):
            with self.subTest(classification=classification, method=method):
                descriptor = observed_probe_descriptor()
                changed = dataclasses.replace(
                    descriptor,
                    observations=(
                        dataclasses.replace(
                            descriptor.observations[0],
                            classification=classification,
                            method=method,
                        ),
                        *descriptor.observations[1:],
                    ),
                )
                backend = observed_probe_backend(nonce_source=nonce_bytes, descriptor=changed)
                self.assertNotEqual(
                    classify_backend_eligibility(backend.describe()),
                    CapabilityClass.OBSERVED_PASS,
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                self.assertNotEqual(result.classification, CapabilityClass.OBSERVED_PASS)

    def test_backend_model_settings_or_policy_drift_invalidates_preflight(self):
        backend = observed_probe_backend(nonce_source=nonce_bytes)
        freshness = self._freshness(backend)
        for field, replacement in (
            ("model_revision_identity", "different-model@2026-09-03"),
            ("inference_settings_sha256", sha256_bytes(b"different-settings")),
            ("retention_policy_identity", "different-retention"),
        ):
            with self.subTest(field=field):
                changed_descriptor = dataclasses.replace(
                    backend.describe(),
                    identity=dataclasses.replace(
                        backend.describe().identity, **{field: replacement}
                    ),
                )
                changed_backend = observed_probe_backend(
                    nonce_source=nonce_bytes, descriptor=changed_descriptor
                )
                result = run_isolation_preflight(
                    changed_backend,
                    freshness=freshness,
                    nonce_source=nonce_bytes,
                )
                self.assertEqual(result.classification, CapabilityClass.UNAVAILABLE)
                self.assertEqual(changed_backend.received_request_bytes, [])
                self.assertEqual(
                    validate_preflight_freshness(result, self._freshness(changed_backend)),
                    RunnerState.ISOLATION_PREFLIGHT_FAILED,
                )

        policy_drift = dataclasses.replace(
            freshness, capability_policy_sha256=sha256_bytes(b"different-policy")
        )
        policy_backend = observed_probe_backend(nonce_source=nonce_bytes)
        policy_result = run_isolation_preflight(
            policy_backend,
            freshness=policy_drift,
            nonce_source=nonce_bytes,
        )
        self.assertEqual(policy_result.classification, CapabilityClass.UNAVAILABLE)
        self.assertEqual(policy_backend.received_request_bytes, [])

        baseline = run_isolation_preflight(
            backend,
            freshness=freshness,
            nonce_source=nonce_bytes,
        )
        self.assertEqual(
            validate_preflight_freshness(baseline, policy_drift),
            RunnerState.ISOLATION_PREFLIGHT_FAILED,
        )

    def test_exact_319066_package_capacity_is_sent_without_split(self):
        backend = observed_probe_backend(nonce_source=nonce_bytes)
        result = run_isolation_preflight(
            backend,
            freshness=self._freshness(backend),
            nonce_source=nonce_bytes,
        )

        self.assertEqual(result.required_package_bytes, 319_066)
        self.assertEqual(len(package_from_request(backend.received_request_bytes[0])), 319_066)
        request = json.loads(backend.received_request_bytes[0])
        self.assertEqual(
            len([item for item in request["inputs"] if item["logical_role"] == "review_package"]),
            1,
        )
        self.assertNotIn("chunks", request)
        self.assertNotIn("continuation_id", request)
        self.assertEqual(result.actual_request_bytes, len(backend.received_request_bytes[0]))
        self.assertGreater(result.actual_request_bytes, result.required_package_bytes)

    def test_package_too_large_fails_before_semantic_execution(self):
        descriptor = dataclasses.replace(observed_probe_descriptor(), max_request_bytes=319_066)
        backend = observed_probe_backend(nonce_source=nonce_bytes, descriptor=descriptor)

        result = run_isolation_preflight(
            backend,
            freshness=self._freshness(backend),
            nonce_source=nonce_bytes,
        )

        self.assertEqual(result.classification, CapabilityClass.UNAVAILABLE)
        self.assertGreater(result.actual_request_bytes, descriptor.max_request_bytes)
        self.assertEqual(backend.received_request_bytes, [])

    def test_fake_success_remains_untested_and_no_backend_is_unavailable(self):
        allowed = nonce_bytes("allowed-package-brief").hex()
        fake = DeterministicFakeBackend(response_bytes(allowed))
        fake_result = run_isolation_preflight(
            fake,
            freshness=build_preflight_freshness(fake.describe().identity),
            nonce_source=nonce_bytes,
        )
        self.assertEqual(fake_result.classification, CapabilityClass.UNTESTED)

        unavailable = run_isolation_preflight(
            None,
            freshness=build_preflight_freshness(None),
            nonce_source=nonce_bytes,
        )
        self.assertEqual(unavailable.classification, CapabilityClass.UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()
