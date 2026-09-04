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
    BackendResponse,
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


def ascii_nonce_bytes(label: str) -> bytes:
    return sha256_bytes(("ascii-nonce:" + label).encode("utf-8"))[:32].encode(
        "ascii"
    )


def reviewer_repro_encoding_variants(canary: bytes) -> dict[str, str]:
    standard_base64 = base64.b64encode(canary).decode("ascii")
    urlsafe_base64 = base64.urlsafe_b64encode(canary).decode("ascii")
    return {
        "uppercase-hex": canary.hex().upper(),
        "standard-base64-unpadded": standard_base64.rstrip("="),
        "urlsafe-base64-padded": urlsafe_base64,
        "urlsafe-base64-unpadded": urlsafe_base64.rstrip("="),
    }


def near_miss(value: str) -> str:
    index = next(index for index, character in enumerate(value) if character != "=")
    replacement = "A" if value[index] != "A" else "B"
    return value[:index] + replacement + value[index + 1 :]


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


def response_with_duplicate_key(
    *,
    allowed_nonce: str,
    duplicate_key: str,
    first_value: object,
    second_value: object,
) -> bytes:
    pairs = [("probe_schema_version", PROBE_SCHEMA_VERSION)]
    if duplicate_key == "allowed_nonce":
        pairs.extend(((duplicate_key, first_value), (duplicate_key, second_value)))
    else:
        pairs.append(("allowed_nonce", allowed_nonce))
    if duplicate_key == "response_count":
        pairs.extend(((duplicate_key, first_value), (duplicate_key, second_value)))
    else:
        pairs.append(("response_count", 1))
    return (
        "{" + ",".join(
            json.dumps(key) + ":" + json.dumps(value)
            for key, value in pairs
        ) + "}"
    ).encode("utf-8")


def package_from_request(request_bytes: bytes) -> bytes:
    request = json.loads(request_bytes)
    package = next(
        item for item in request["inputs"] if item["logical_role"] == "review_package"
    )
    return base64.b64decode(package["content_base64"], validate=True)


def unit_only_eligible_external_adapter(**kwargs):
    from tests.reviewer_runner_support import (
        unit_only_eligible_external_adapter as build_backend,
    )

    return build_backend(**kwargs)


def unit_only_eligible_external_descriptor():
    from tests.reviewer_runner_support import (
        unit_only_eligible_external_descriptor as build_descriptor,
    )

    return build_descriptor()


class ReviewerRunnerPreflightTests(unittest.TestCase):
    def setUp(self):
        if _PREFLIGHT_IMPORT_ERROR:
            self.fail("reviewer_runner.preflight must implement the synthetic isolation preflight")

    def _freshness(self, backend):
        return build_preflight_freshness(backend.describe())

    def test_positive_probe_returns_exact_allowed_nonce_once(self):
        backend = unit_only_eligible_external_adapter(nonce_source=nonce_bytes)
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

        # This receipt exists only in memory to cover the trusted-adapter branch;
        # the unit-only simulation never writes or commits capability evidence.
        ephemeral_receipt = build_per_run_isolation_receipt(
            result,
            current_freshness=freshness,
            backend_identity=backend.describe().identity,
            request_sha256=sha256_bytes(b"bound semantic request"),
        )
        self.assertEqual(
            ephemeral_receipt.classification, CapabilityClass.OBSERVED_PASS
        )
        self.assertEqual(
            ephemeral_receipt.preflight_evidence_sha256, result.evidence_sha256
        )
        self.assertEqual(len(ephemeral_receipt.receipt_sha256), 64)

    def test_unit_only_eligible_fixture_is_separate_from_runtime_fake_evidence(self):
        try:
            from tests.reviewer_runner_support import (
                UnitOnlyEligibleExternalAdapterSimulation,
                unit_only_eligible_external_adapter,
            )
        except ImportError:
            self.fail("eligible-branch simulation must be explicitly unit-only")

        simulated = unit_only_eligible_external_adapter(nonce_source=nonce_bytes)
        self.assertIsInstance(simulated, UnitOnlyEligibleExternalAdapterSimulation)
        self.assertEqual(type(simulated).__module__, "tests.reviewer_runner_support")
        self.assertFalse(simulated.describe().identity.is_test_double)

        fake = DeterministicFakeBackend(
            response_bytes(nonce_bytes("allowed-package-brief").hex())
        )
        self.assertTrue(fake.describe().identity.is_test_double)
        self.assertEqual(
            classify_backend_eligibility(fake.describe()),
            CapabilityClass.UNTESTED,
        )

    def test_each_forbidden_canary_family_fails_if_leaked(self):
        try:
            from reviewer_runner.preflight import _detect_forbidden_canary_leak
        except ImportError:
            self.fail("raw forbidden-canary detection must be independently reachable")

        allowed_nonce = nonce_bytes("allowed-package-brief").hex()
        for family in FORBIDDEN_FAMILIES:
            with self.subTest(family=family):
                leaked_nonce = nonce_bytes(family).hex()
                raw_response = response_with_duplicate_key(
                    allowed_nonce=allowed_nonce,
                    duplicate_key="allowed_nonce",
                    first_value=leaked_nonce,
                    second_value=allowed_nonce,
                )
                collapsed = json.loads(raw_response)
                self.assertEqual(
                    collapsed,
                    {
                        "probe_schema_version": PROBE_SCHEMA_VERSION,
                        "allowed_nonce": allowed_nonce,
                        "response_count": 1,
                    },
                )
                self.assertTrue(
                    _detect_forbidden_canary_leak(
                        raw_response,
                        events=(),
                        forbidden_nonces=(nonce_bytes(family),),
                    )
                )
                backend = unit_only_eligible_external_adapter(
                    nonce_source=nonce_bytes,
                    response_factory=lambda allowed, raw=raw_response: raw,
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                self.assertEqual(result.classification, CapabilityClass.OBSERVED_FAIL)
                self.assertIn(sha256_bytes(nonce_bytes(family)), result.forbidden_canary_hashes)

    def test_provider_request_id_leak_for_every_canary_family_and_encoding_prevents_observed_pass(self):
        unexpected_passes = []
        for family in FORBIDDEN_FAMILIES:
            canary = ascii_nonce_bytes(family)
            representations = {
                "raw": canary.decode("ascii"),
                "hex": canary.hex(),
                "base64": base64.b64encode(canary).decode("ascii"),
            }
            for encoding, leaked_value in representations.items():
                backend = unit_only_eligible_external_adapter(
                    nonce_source=ascii_nonce_bytes,
                    metadata_drift={"provider_request_id": leaked_value},
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=ascii_nonce_bytes,
                )
                if result.classification is CapabilityClass.OBSERVED_PASS:
                    unexpected_passes.append((family, encoding))

        self.assertEqual(
            unexpected_passes,
            [],
            "provider_request_id canary leakage must never authorize OBSERVED_PASS",
        )

    def test_reviewer_repro_equivalent_provider_id_encodings_never_observed_pass(self):
        unexpected_passes = []
        for family in FORBIDDEN_FAMILIES:
            canary = nonce_bytes(family)
            for encoding, leaked_value in reviewer_repro_encoding_variants(
                canary
            ).items():
                backend = unit_only_eligible_external_adapter(
                    nonce_source=nonce_bytes,
                    metadata_drift={"provider_request_id": leaked_value},
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                if result.classification is CapabilityClass.OBSERVED_PASS:
                    unexpected_passes.append((family, encoding))

        self.assertEqual(
            unexpected_passes,
            [],
            "equivalent provider_request_id encodings must never authorize OBSERVED_PASS",
        )

    def test_closed_backend_response_metadata_projection_scans_every_field(self):
        try:
            from reviewer_runner.preflight import _detect_forbidden_canary_leak
        except ImportError:
            self.fail("closed BackendResponse metadata projection must be scanable")

        baseline = BackendResponse(
            raw_bytes=b'{}',
            provider_request_id="provider-request",
            request_sha256="0" * 64,
            reviewer_id="reviewer",
            review_run_id="run",
            context_id="context",
            backend_identity_sha256="1" * 64,
            response_count=1,
            continuation_id=None,
            previous_response_id=None,
            events=(),
        )
        metadata_fields = (
            "provider_request_id",
            "request_sha256",
            "reviewer_id",
            "review_run_id",
            "context_id",
            "backend_identity_sha256",
            "response_count",
            "continuation_id",
            "previous_response_id",
            "event.kind",
            "event.metadata_sha256",
        )
        missed = []
        for family in FORBIDDEN_FAMILIES:
            canary = ascii_nonce_bytes(family)
            representations = {
                "raw": canary.decode("ascii"),
                "hex": canary.hex(),
                "base64": base64.b64encode(canary).decode("ascii"),
            }
            for encoding, leaked_value in representations.items():
                for field in metadata_fields:
                    if field == "event.kind":
                        response = dataclasses.replace(
                            baseline,
                            events=(BackendEvent(leaked_value, "2" * 64),),
                        )
                    elif field == "event.metadata_sha256":
                        response = dataclasses.replace(
                            baseline,
                            events=(BackendEvent("RESPONSE", leaked_value),),
                        )
                    else:
                        response = dataclasses.replace(
                            baseline,
                            **{field: leaked_value},
                        )
                    try:
                        detected = _detect_forbidden_canary_leak(
                            response,
                            forbidden_nonces=(canary,),
                        )
                    except TypeError:
                        detected = False
                    if not detected:
                        missed.append((family, encoding, field))

        self.assertEqual(
            missed,
            [],
            "the forbidden-canary scan must cover every permitted response metadata field",
        )

    def test_reviewer_repro_equivalent_encodings_cover_every_closed_metadata_field(self):
        try:
            from reviewer_runner.preflight import _detect_forbidden_canary_leak
        except ImportError:
            self.fail("closed BackendResponse metadata projection must be scanable")

        baseline = BackendResponse(
            raw_bytes=b'{}',
            provider_request_id="provider-request",
            request_sha256="0" * 64,
            reviewer_id="reviewer",
            review_run_id="run",
            context_id="context",
            backend_identity_sha256="1" * 64,
            response_count=1,
            continuation_id=None,
            previous_response_id=None,
            events=(),
        )
        metadata_fields = (
            "provider_request_id",
            "request_sha256",
            "reviewer_id",
            "review_run_id",
            "context_id",
            "backend_identity_sha256",
            "response_count",
            "continuation_id",
            "previous_response_id",
            "event.kind",
            "event.metadata_sha256",
        )

        def with_metadata_value(field: str, value: str) -> BackendResponse:
            if field == "event.kind":
                return dataclasses.replace(
                    baseline,
                    events=(BackendEvent(value, "2" * 64),),
                )
            if field == "event.metadata_sha256":
                return dataclasses.replace(
                    baseline,
                    events=(BackendEvent("RESPONSE", value),),
                )
            return dataclasses.replace(baseline, **{field: value})

        missed = []
        false_positives = []
        allowed = nonce_bytes("allowed-package-brief")
        self.assertFalse(
            _detect_forbidden_canary_leak(
                baseline,
                forbidden_nonces=tuple(
                    nonce_bytes(family) for family in FORBIDDEN_FAMILIES
                ),
            )
        )
        for family in FORBIDDEN_FAMILIES:
            canary = nonce_bytes(family)
            for encoding, leaked_value in reviewer_repro_encoding_variants(
                canary
            ).items():
                allowed_value = reviewer_repro_encoding_variants(allowed)[encoding]
                for field in metadata_fields:
                    if not _detect_forbidden_canary_leak(
                        with_metadata_value(field, leaked_value),
                        forbidden_nonces=(canary,),
                    ):
                        missed.append((family, encoding, field))
                    for control, control_value in (
                        ("allowed", allowed_value),
                        ("near-miss", near_miss(leaked_value)),
                    ):
                        if _detect_forbidden_canary_leak(
                            with_metadata_value(field, control_value),
                            forbidden_nonces=(canary,),
                        ):
                            false_positives.append(
                                (family, encoding, field, control)
                            )

        self.assertEqual(missed, [])
        self.assertEqual(
            false_positives,
            [],
            "clean, allowed, and one-character near-miss controls must remain accepted",
        )

    def test_non_default_package_size_cannot_authorize_or_issue_receipt(self):
        backend = unit_only_eligible_external_adapter(nonce_source=nonce_bytes)
        freshness = self._freshness(backend)

        result = run_isolation_preflight(
            backend,
            freshness=freshness,
            nonce_source=nonce_bytes,
            required_package_bytes=319_065,
        )

        self.assertNotEqual(result.classification, CapabilityClass.OBSERVED_PASS)
        self.assertEqual(backend.received_request_bytes, [])
        with self.assertRaises(ValueError):
            build_per_run_isolation_receipt(
                result,
                current_freshness=freshness,
                backend_identity=backend.describe().identity,
                request_sha256=sha256_bytes(b"semantic request"),
            )

    def test_duplicate_json_keys_or_repeated_allowed_nonce_fail_preflight(self):
        allowed_nonce = nonce_bytes("allowed-package-brief").hex()
        for duplicate_key, first_value, second_value in (
            ("allowed_nonce", allowed_nonce, allowed_nonce),
            ("response_count", 1, 1),
        ):
            with self.subTest(duplicate_key=duplicate_key):
                raw_response = response_with_duplicate_key(
                    allowed_nonce=allowed_nonce,
                    duplicate_key=duplicate_key,
                    first_value=first_value,
                    second_value=second_value,
                )
                backend = unit_only_eligible_external_adapter(
                    nonce_source=nonce_bytes,
                    response_factory=lambda allowed, raw=raw_response: raw,
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                self.assertEqual(result.classification, CapabilityClass.OBSERVED_FAIL)

    def test_serialized_allowed_nonce_must_occur_exactly_once(self):
        try:
            from reviewer_runner.preflight import (
                _has_exactly_one_serialized_allowed_nonce,
            )
        except ImportError:
            self.fail("serialized allowed-nonce count must be independently enforced")

        allowed_nonce = nonce_bytes("allowed-package-brief")
        exact_response = response_bytes(allowed_nonce.hex())
        repeated_response = response_bytes(
            allowed_nonce.hex(),
            repeated_nonce=allowed_nonce.hex(),
        )
        self.assertTrue(
            _has_exactly_one_serialized_allowed_nonce(exact_response, allowed_nonce)
        )
        self.assertFalse(
            _has_exactly_one_serialized_allowed_nonce(repeated_response, allowed_nonce)
        )

    def test_windows_unix_unc_traversal_git_symlink_and_junction_strings_are_inert(self):
        resolver_calls = []
        backend = unit_only_eligible_external_adapter(
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
                backend = unit_only_eligible_external_adapter(
                    nonce_source=nonce_bytes, events=(event,)
                )
                result = run_isolation_preflight(
                    backend,
                    freshness=self._freshness(backend),
                    nonce_source=nonce_bytes,
                )
                self.assertEqual(result.classification, CapabilityClass.OBSERVED_FAIL)

    def test_continuation_or_previous_response_id_fails_preflight(self):
        for field in ("continuation_id", "previous_response_id"):
            with self.subTest(field=field):
                backend = unit_only_eligible_external_adapter(
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
                descriptor = unit_only_eligible_external_descriptor()
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
                backend = unit_only_eligible_external_adapter(
                    nonce_source=nonce_bytes, descriptor=changed
                )
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
        backend = unit_only_eligible_external_adapter(nonce_source=nonce_bytes)
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
                changed_backend = unit_only_eligible_external_adapter(
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
        policy_backend = unit_only_eligible_external_adapter(nonce_source=nonce_bytes)
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

    def test_full_backend_descriptor_drift_after_probe_fails_observed_proof(self):
        baseline_descriptor = unit_only_eligible_external_descriptor()
        drifts = {
            "capacity": dataclasses.replace(
                baseline_descriptor,
                max_request_bytes=baseline_descriptor.max_request_bytes + 1,
            ),
            "observation-method": dataclasses.replace(
                baseline_descriptor,
                observations=(
                    dataclasses.replace(
                        baseline_descriptor.observations[0],
                        method="direct:changed-method",
                    ),
                    *baseline_descriptor.observations[1:],
                ),
            ),
            "observation-evidence": dataclasses.replace(
                baseline_descriptor,
                observations=(
                    dataclasses.replace(
                        baseline_descriptor.observations[0],
                        evidence_sha256=sha256_bytes(b"changed-evidence"),
                    ),
                    *baseline_descriptor.observations[1:],
                ),
            ),
            "observation-classification": dataclasses.replace(
                baseline_descriptor,
                observations=(
                    dataclasses.replace(
                        baseline_descriptor.observations[0],
                        classification=CapabilityClass.UNTESTED,
                    ),
                    *baseline_descriptor.observations[1:],
                ),
            ),
        }

        unexpected_passes = []
        for label, changed_descriptor in drifts.items():
            delegate = unit_only_eligible_external_adapter(
                nonce_source=nonce_bytes,
                descriptor=baseline_descriptor,
            )

            class DescriptorDriftAfterProbe:
                received_request_bytes = delegate.received_request_bytes

                def describe(self):
                    if self.received_request_bytes:
                        return changed_descriptor
                    return baseline_descriptor

                def invoke(self, request_bytes: bytes, *, timeout_seconds: int):
                    return delegate.invoke(
                        request_bytes,
                        timeout_seconds=timeout_seconds,
                    )

            backend = DescriptorDriftAfterProbe()
            result = run_isolation_preflight(
                backend,
                freshness=self._freshness(backend),
                nonce_source=nonce_bytes,
            )
            if result.classification is CapabilityClass.OBSERVED_PASS:
                unexpected_passes.append(label)
            self.assertEqual(len(backend.received_request_bytes), 1)

        self.assertEqual(
            unexpected_passes,
            [],
            "the descriptor compared after the probe must include capacity and observations",
        )

    def test_exact_319066_package_capacity_is_sent_without_split(self):
        backend = unit_only_eligible_external_adapter(nonce_source=nonce_bytes)
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
        descriptor = dataclasses.replace(
            unit_only_eligible_external_descriptor(), max_request_bytes=319_066
        )
        backend = unit_only_eligible_external_adapter(
            nonce_source=nonce_bytes, descriptor=descriptor
        )

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
            freshness=build_preflight_freshness(fake.describe()),
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
