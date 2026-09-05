import dataclasses
import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "joewrks-product-definition"
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from reviewer_runner.backend import REQUIRED_CAPABILITIES, backend_descriptor_sha256, hash_evidence_record
from reviewer_runner.identity import CapabilityClass, canonical_json_bytes, sha256_bytes
from reviewer_runner.preflight import classify_backend_eligibility

try:
    from reviewer_runner.providers import anthropic_admission as admission
except ImportError:
    admission = None


def _digest(label):
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _provisioning(**changes):
    values = {
        "schema_version": "joewrks.anthropic-provisioning-evidence/1.0",
        "expected_anthropic_workspace_id_sha256": _digest("workspace-id"),
        "workspace_key_scope": "WORKSPACE_SCOPED",
        "workspace_evidence_channel": "MACHINE_READABLE",
        "workspace_evidence_sha256": _digest("workspace-evidence"),
        "retention_privacy_evidence_channel": "CONTRACT_CONSOLE_OR_ADMINISTRATOR",
        "retention_privacy_evidence_sha256": _digest("privacy-evidence"),
        "retention_privacy_approval": "ZDR_VERIFIED",
        "inference_geo_evidence_sha256": _digest("geo-evidence"),
        "model_entitlement_evidence_sha256": _digest("model-entitlement"),
        "capacity_and_quota_evidence_sha256": _digest("quota-evidence"),
        "spend_approval_evidence_sha256": _digest("spend-approval"),
        "provider_policy_approval_evidence_sha256": _digest("provider-policy"),
        "credential_readiness_evidence_sha256": _digest("credential-readiness"),
    }
    values.update(changes)
    return admission.AnthropicProvisioningEvidence(**values)


def _complete_evidence(**changes):
    values = {
        "schema_version": "joewrks.anthropic-admission-evidence/1.0",
        "adapter_source_manifest_sha256": _digest("adapter-source"),
        "local_conformance_evidence_sha256": _digest("local-conformance"),
        "canonical_provider_body_sha256": _digest("canonical-provider-body"),
        "provider_official_contract_sha256": _digest("official-contract"),
        "local_capacity_measurement_sha256": _digest("local-capacity"),
        "provisioning": _provisioning(),
    }
    values.update(changes)
    return admission.AnthropicAdmissionEvidence(**values)


class ReviewerRunnerAnthropicAdmissionTests(unittest.TestCase):
    def require_admission(self):
        self.assertIsNotNone(admission, "Anthropic admission module must be importable")
        return admission

    def test_unprovisioned_record_has_closed_schema_and_no_secret_or_raw_workspace_id(self):
        module = self.require_admission()
        evidence = module.unprovisioned_anthropic_admission()
        provisioning = evidence.provisioning
        self.assertEqual(tuple(field.name for field in dataclasses.fields(provisioning)), (
            "schema_version", "expected_anthropic_workspace_id_sha256", "workspace_key_scope",
            "workspace_evidence_channel", "workspace_evidence_sha256",
            "retention_privacy_evidence_channel", "retention_privacy_evidence_sha256",
            "retention_privacy_approval", "inference_geo_evidence_sha256",
            "model_entitlement_evidence_sha256", "capacity_and_quota_evidence_sha256",
            "spend_approval_evidence_sha256", "provider_policy_approval_evidence_sha256",
            "credential_readiness_evidence_sha256",
        ))
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(evidence)),
            ("schema_version", "adapter_source_manifest_sha256", "local_conformance_evidence_sha256",
             "canonical_provider_body_sha256", "provider_official_contract_sha256",
             "local_capacity_measurement_sha256", "provisioning"),
        )
        self.assertTrue(all(value is None for field, value in vars_or_fields(provisioning).items() if field != "schema_version"))
        self.assertNotIn("api_key", canonical_json_bytes(module.admission_record(evidence)).decode("utf-8").lower())

    def test_deployment_identity_hashes_exact_provider_platform_workspace_endpoint_api_geo_adapter_record(self):
        module = self.require_admission()
        configuration = module.build_anthropic_backend_configuration(_complete_evidence())
        expected = sha256_bytes(canonical_json_bytes({
            "adapter_id": "anthropic-direct-messages", "adapter_version": "1.0.0",
            "api_version": "2023-06-01", "endpoint": "https://api.anthropic.com/v1/messages",
            "expected_anthropic_workspace_id_sha256": _digest("workspace-id"),
            "inference_geo_policy": "us", "platform": "direct_claude_api", "provider": "anthropic",
        }))
        self.assertEqual(configuration.descriptor.identity.deployment_identity, expected)

    def test_observations_match_required_capabilities_exactly_once_and_in_order(self):
        module = self.require_admission()
        descriptor = module.build_anthropic_backend_configuration(_complete_evidence()).descriptor
        self.assertEqual(tuple(item.capability for item in descriptor.observations), REQUIRED_CAPABILITIES)
        self.assertEqual(len(descriptor.observations), 17)

    def test_every_observation_hashes_the_closed_capability_evidence_record(self):
        module = self.require_admission()
        evidence = _complete_evidence()
        configuration = module.build_anthropic_backend_configuration(evidence)
        provisioning_hash = sha256_bytes(canonical_json_bytes(module.provisioning_record(evidence.provisioning)))
        for observation in configuration.descriptor.observations:
            record = {
                "schema_version": module.ANTHROPIC_CAPABILITY_EVIDENCE_SCHEMA_VERSION,
                "capability": observation.capability, "method": observation.method,
                "classification": observation.classification.value,
                "adapter_source_sha256": evidence.adapter_source_manifest_sha256,
                "canonical_provider_body_sha256": evidence.canonical_provider_body_sha256,
                "provisioning_evidence_sha256": provisioning_hash,
                "provider_official_contract_sha256": evidence.provider_official_contract_sha256,
                "workspace_commitment_sha256": evidence.provisioning.workspace_evidence_sha256,
                "local_capacity_measurement_sha256": evidence.local_capacity_measurement_sha256,
                "local_conformance_evidence_sha256": evidence.local_conformance_evidence_sha256,
                "settings_sha256": module.anthropic_settings_sha256(),
            }
            self.assertEqual(observation.evidence_sha256, hash_evidence_record(record))

    def test_missing_required_dependency_is_unavailable_and_preflight_ineligible(self):
        module = self.require_admission()
        configuration = module.build_anthropic_backend_configuration(
            _complete_evidence(provider_official_contract_sha256=None)
        )
        self.assertEqual(classify_backend_eligibility(configuration.descriptor), CapabilityClass.UNAVAILABLE)
        self.assertIn(CapabilityClass.UNAVAILABLE, {item.classification for item in configuration.descriptor.observations})

    def test_present_contradictory_dependency_is_observed_fail(self):
        module = self.require_admission()
        evidence = _complete_evidence(provisioning=_provisioning(
            provider_policy_approval_evidence_sha256=_digest("privacy-evidence"),
        ))
        configuration = module.build_anthropic_backend_configuration(evidence)
        self.assertIn(CapabilityClass.OBSERVED_FAIL, {item.classification for item in configuration.descriptor.observations})
        self.assertEqual(classify_backend_eligibility(configuration.descriptor), CapabilityClass.OBSERVED_FAIL)

    def test_complete_frozen_inputs_are_observed_pass_with_direct_methods(self):
        module = self.require_admission()
        configuration = module.build_anthropic_backend_configuration(_complete_evidence())
        self.assertEqual(configuration.provisioning_status, module.AnthropicProvisioningStatus.READY_FOR_PREFLIGHT)
        self.assertTrue(all(item.classification is CapabilityClass.OBSERVED_PASS for item in configuration.descriptor.observations))
        self.assertTrue(all(item.method.startswith("direct:") for item in configuration.descriptor.observations))
        self.assertEqual(classify_backend_eligibility(configuration.descriptor), CapabilityClass.OBSERVED_PASS)

    def test_descriptor_hash_is_deterministic_and_input_mutation_changes_freshness(self):
        module = self.require_admission()
        baseline = module.build_anthropic_backend_configuration(_complete_evidence()).descriptor
        changed = module.build_anthropic_backend_configuration(
            _complete_evidence(adapter_source_manifest_sha256=_digest("changed-source"))
        ).descriptor
        self.assertEqual(backend_descriptor_sha256(baseline), backend_descriptor_sha256(module.build_anthropic_backend_configuration(_complete_evidence()).descriptor))
        self.assertNotEqual(backend_descriptor_sha256(baseline), backend_descriptor_sha256(changed))

    def test_capacity_stays_unavailable_without_token_quota_and_spend_evidence(self):
        module = self.require_admission()
        evidence = _complete_evidence(provisioning=_provisioning(capacity_and_quota_evidence_sha256=None, spend_approval_evidence_sha256=None))
        configuration = module.build_anthropic_backend_configuration(evidence)
        observation = next(item for item in configuration.descriptor.observations if item.capability == "sufficient_payload_capacity")
        self.assertIs(observation.classification, CapabilityClass.UNAVAILABLE)

    def test_policy_channels_are_distinct_and_runtime_workspace_header_cannot_approve_privacy(self):
        module = self.require_admission()
        configuration = module.build_anthropic_backend_configuration(
            _complete_evidence(provisioning=_provisioning(
                retention_privacy_evidence_channel="MACHINE_READABLE",
            ))
        )
        privacy = next(item for item in configuration.descriptor.observations if item.capability == "accepted_retention_and_privacy")
        self.assertIs(privacy.classification, CapabilityClass.OBSERVED_FAIL)
        header_configuration = module.build_anthropic_backend_configuration(
            _complete_evidence(provisioning=_provisioning(
                retention_privacy_evidence_sha256="x-anthropic-workspace-id",
            ))
        )
        self.assertIs(
            next(item for item in header_configuration.descriptor.observations if item.capability == "accepted_retention_and_privacy").classification,
            CapabilityClass.OBSERVED_FAIL,
        )

    def test_api_key_value_hash_prefix_name_and_path_are_rejected_from_evidence(self):
        module = self.require_admission()
        for bad_value in ("sk-ant-secret", _digest("secret")[:12], "primary-api-key", "/secure/key/path"):
            with self.subTest(bad_value=bad_value):
                try:
                    configuration = module.build_anthropic_backend_configuration(
                        _complete_evidence(provisioning=_provisioning(
                            credential_readiness_evidence_sha256=bad_value,
                        ))
                    )
                except ValueError:
                    continue
                authentication = next(item for item in configuration.descriptor.observations if item.capability == "controller_only_authentication")
                self.assertIs(authentication.classification, CapabilityClass.OBSERVED_FAIL)


def vars_or_fields(value):
    return {field.name: getattr(value, field.name) for field in dataclasses.fields(value)}


if __name__ == "__main__":
    unittest.main()
