# Post-M6 Real Backend Capability Enablement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement one explicitly registered Anthropic Messages API adapter and the local, offline proof infrastructure needed to prepare the existing Reviewer Runner for a later PM-authorized P1/P2 capability proof, while keeping real backend capability unavailable until provisioning and that proof exist.

**Architecture:** Preserve the current bytes-in/bytes-out ToollessInferenceBackend contract. Add one Anthropic-specific provider package that validates and projects the exact four-role canonical request, compiles a hash-bound pre-call admission descriptor, makes one direct standard-library HTTPS request, and translates one closed Anthropic response into the existing BackendResponse. Extend the read-only runner capability audit so it can truthfully distinguish an implemented registered adapter from a provisioned and externally proven backend.

**Tech Stack:** Python 3 standard library only; immutable dataclasses and enums; canonical UTF-8 JSON; base64 and SHA-256; http.client.HTTPSConnection with the default verified TLS context; unittest; Git object and source-byte verification.

**Spec:** docs/superpowers/specs/2026-09-05-post-m6-real-backend-capability-enablement-design.md

**Candidate audit:** evals/post-m6-real-backend-capability-enablement/BACKEND_CANDIDATE_CAPABILITY_AUDIT.md

## Global Constraints

- Execute from an isolated canonical-LF Git worktree created from exact approved planning commit c1c06dca65ae007cb59353a75788eaf2096bd219, tree 7444b53a69520e629a4f828eab8f3727a03e5ebe. The authoritative main remains ab95074704af0e93248d56344d6a220dfec88a93, tree 867bec6fcfe5f4dc9927beaaf143087178e09e7c.
- Create the implementation branch as codex/post-m6-real-backend-capability-enablement. Do not merge or push main.
- Use superpowers:using-git-worktrees before Task 1, then superpowers:subagent-driven-development with a fresh implementation subagent and a separate fresh reviewer for every Task. Use superpowers:test-driven-development for each behavior change, superpowers:requesting-code-review after each GREEN commit, superpowers:verification-before-completion before the final claim, and superpowers:finishing-a-development-branch only after every evidence gate passes.
- The approved design controls. This plan controls execution beneath it. If implementing this plan would require changing ToollessInferenceBackend, BackendDescriptor, BackendResponse, REQUIRED_CAPABILITIES, run_isolation_preflight, the four-role CanonicalRequest, or either semantic output schema, stop with REAL_BACKEND_IMPLEMENTATION_BLOCKED — DESIGN_CONTRACT_CONFLICT.
- A RED run must import and discover successfully, execute the intended test, and fail through a controlled assertion. ModuleNotFoundError, import-time unittest ERROR, syntax error, typo, and collection failure are invalid RED evidence. Do not create production scaffolding merely to manufacture a valid RED.
- Keep exactly the current 17 REQUIRED_CAPABILITIES entries and their order. Do not add, remove, rename, or reorder them.
- A future real preflight descriptor must contain OBSERVED_PASS for all 17 observations, use methods beginning with direct:, be non-test, and bind an IMMUTABLE model identity before run_isolation_preflight can invoke the provider. P1 and P2 never mutate the descriptor; its canonical bytes and backend_descriptor_sha256 must be identical before and after both calls.
- OBSERVED_PASS in an Anthropic descriptor means its direct pre-call structural, contract, local measurement, and provisioning prerequisite was frozen and verified. It does not mean external isolation passed. Only the later PM-authorized P1/P2 evidence can establish the overall real-backend capability.
- This implementation wave performs no provider provisioning, no authenticated Anthropic request, no Token Counting request, no Admin API request, no P1, no P2, no semantic reviewer run, no calibration, and no v0.4.4 work.
- Do not read, request, print, hash, persist, or log a real API-key value. ANTHROPIC_API_KEY is the only inference credential source. Credential presence never triggers execution.
- Use one provider and one transport only: Anthropic Messages at https://api.anthropic.com/v1/messages through Python http.client.HTTPSConnection. Do not add an SDK, requests, httpx, a provider registry framework, discovery, routing, fallback, proxy, secret manager, credential UI, or account-management subsystem.
- Keep APPLICATION_RETRIES = 0, streaming disabled, one new connection per invoke, one POST request, Connection: close, no redirect following, no proxy, and no automatic same-run repetition after any failure or ambiguous outcome.
- A fake or injected transport is test-only and must force BackendIdentity.is_test_double = true and non-authoritative observations. It can never produce a production preflight receipt or committed real capability PASS.
- Product Definition, M6 authority/evidence, semantic-review/1.0, semantic-review/2.1, v0.4.3, oracle, goldens, thresholds, action-conformance semantics, runtime-conformance semantics, calibration counters, the current four-role request contract, and current semantic output schemas are frozen.
- Preserve REAL_CALIBRATION_ATTEMPTS = 1, VALID_REAL_CALIBRATION_RUNS = 0, semantic-review/2.1 reliability = NOT_MEASURED, and v0.4.4 = BLOCKED.
- Preserve the historical runner evidence file evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json byte-for-byte. It is truthful evidence for the earlier zero-adapter revision. Record the new one-adapter/unprovisioned state in the new Post-M6 real-backend evidence paths defined below.
- Every Task ends with focused tests, declared regressions, a GREEN commit, an independent review of the exact Task diff, and separate review-fix commits for all Critical or Important findings. Do not squash review-fix commits.
- Before Task 1, prove that every live tracked file under skills/joewrks-product-definition/reviewer_runner has raw bytes equal to its Git blob. Do not change global or repository Git configuration and do not normalize source files to repair a bad checkout. If this proof fails, stop with REAL_BACKEND_IMPLEMENTATION_BLOCKED — NONCANONICAL_WORKTREE.
- Any test invocation containing tests.test_downstream_v21_dogfood_replay or full discovery must bind JOEWRKS_M6_PHASE_B_WORKTREE to a canonical-LF detached worktree at d38b0ca04768888c47e658c79f41e1cec0a7a1ce, tree 40749d900b98936cf694b0c96db7897011cddae8. Never use force cleanup.

---

## Scope and terminal truth

### Included

1. Anthropic fixed settings, deployment identity, and four-role message projection.
2. Small immutable provisioning and admission-evidence records.
3. Pre-call generation of exactly 17 direct capability observations.
4. One-request standard-library HTTPS transport.
5. Closed response, workspace, request-ID, model, stop, and content-block validation.
6. One explicit Anthropic production-adapter registration.
7. Backward-compatible read-only capability-audit evolution.
8. Offline adversarial tests and new implementation evidence.

### Explicitly deferred

1. Account/workspace/key/billing provisioning.
2. Contract, Console, administrator, or Admin API evidence collection.
3. Authenticated Token Counting.
4. P1 and P2.
5. Any real semantic-review/2.1 reviewer run or calibration authority.
6. Reliability measurement and v0.4.4.

The implementation terminal result is:

~~~text
REAL_BACKEND_ADAPTER_IMPLEMENTED — BACKEND_PROVISIONING_REQUIRED
registered real adapters = 1
real backend capability = UNAVAILABLE
runner state = ISOLATION_CAPABILITY_UNAVAILABLE
real synthetic preflight = NOT_RUN
real provider requests = 0
calibration = CALIBRATION_NOT_RUN
semantic-review/2.1 reliability = NOT_MEASURED
v0.4.4 = BLOCKED
~~~

## File architecture

### New production files

| Path | Single responsibility |
| --- | --- |
| skills/joewrks-product-definition/reviewer_runner/providers/__init__.py | Explicitly register the single unprovisioned Anthropic production adapter; no discovery and no execution side effect. |
| skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py | Fixed Anthropic settings, exact four-role projection, direct HTTPS transport, response validation, and ToollessInferenceBackend implementation. |
| skills/joewrks-product-definition/reviewer_runner/providers/anthropic_admission.py | Closed provisioning/admission records, deployment identity, exact 17-observation compilation, and fail-closed provisioning disposition. |

### Modified production/audit files

| Path | Change |
| --- | --- |
| skills/joewrks-product-definition/scripts/audit_reviewer_runner.py | Load the exact provider registration from the verified revision snapshot, preserve v1.0 historical output, and emit v1.1 for the implemented-but-unprovisioned adapter state. |

No change is planned to reviewer_runner/backend.py, preflight.py, request.py, response.py, identity.py, controller.py, evidence.py, semantic_review.py, reviewer_runner/__init__.py, or the receipt schema.

### New tests

| Path | Responsibility |
| --- | --- |
| tests/test_reviewer_runner_anthropic_projection.py | Settings, canonical-request validation, exact role/media projection, deterministic provider body, and pre-network rejection. |
| tests/test_reviewer_runner_anthropic_admission.py | Provisioning schema, deployment identity, 17-observation matrix, readiness, failure, and descriptor immutability. |
| tests/test_reviewer_runner_anthropic_transport.py | Default TLS, one request, no retry/redirect/proxy, response size bound, and controlled failure mapping. |
| tests/test_reviewer_runner_anthropic_response.py | Message envelope, exact raw text bytes, workspace/request-ID/model/stop/content binding, and secret exclusion. |
| tests/test_reviewer_runner_anthropic_registration.py | One explicit real registration, no import execution, unprovisioned non-admission, and test-transport non-authority. |
| tests/test_reviewer_runner_anthropic_offline.py | Structural no-network guarantee, unexpected credential safety, forbidden dependency/import scan, and adversarial secret/error checks. |

### Modified tests

| Path | Change |
| --- | --- |
| tests/test_reviewer_runner_audit.py | Preserve historical v1.0 evidence readback and verify new v1.1 one-adapter/unprovisioned audit truth. |

### New implementation evidence

| Path | Responsibility |
| --- | --- |
| evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_CAPABILITY_EVIDENCE.json | Canonical machine-readable v1.1 implementation state bound to the final code-only revision. |
| evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_AUDIT.md | Human-readable implementation, offline-test, frozen-boundary, and no-request evidence. |

## Interface compatibility table

| Existing interface | Current contract | Adapter use | Compatibility ruling |
| --- | --- | --- | --- |
| ToollessInferenceBackend.describe() | Returns BackendDescriptor | AnthropicBackend returns a complete valid descriptor without I/O | Unchanged |
| ToollessInferenceBackend.invoke(request_bytes, timeout_seconds) | Exact bytes in, one BackendResponse out or controlled exception | AnthropicBackend accepts no path, tools, file, retrieval, continuation, or provider options | Unchanged |
| REQUIRED_CAPABILITIES | Exact ordered tuple of 17 names | anthropic_admission.py emits exactly one observation per existing name in the same order | Unchanged |
| BackendDescriptor | BackendIdentity, max_request_bytes, ordered observations | Pre-call identity/evidence only; no run-specific P1 result is inserted | Unchanged |
| BackendResponse | Raw bytes, provider request ID, request/run/context/backend bindings, one RESPONSE event, no continuation IDs | The sole Anthropic final text becomes raw_bytes; request-id becomes provider_request_id | Unchanged |
| build_preflight_freshness() | Hashes descriptor, runner Python sources, request shape, capability policy, and runtime | New provider Python files automatically enter runner source freshness | Unchanged |
| classify_backend_eligibility() | Requires non-test, stable model, all OBSERVED_PASS, and direct: methods | Admission builder satisfies or fails the existing gate; the gate is not weakened | Unchanged |
| run_isolation_preflight() | Stops before invoke when prerequisites are not observed | Unprovisioned registration stops before network; future frozen ready descriptor permits P1 | Unchanged |
| build_canonical_request() | Exactly four inline base64 roles | Adapter revalidates and decodes those bytes into one fixed Anthropic projection | Unchanged |
| execute_review() | Rechecks descriptor/freshness immediately before invoke | Future semantic execution uses the same controller without provider-specific parameters | Unchanged |
| freeze_validate_bind_response() | Freezes exact raw bytes before parsing and binds replay identities | Receives exact sole text-block UTF-8 bytes and server request-id | Unchanged |
| audit_reviewer_runner.py | Revision-bound source snapshot and frozen-path audit | Snapshot allowlist gains only providers, anthropic, and anthropic_admission; output schema dispatches by audited revision | Narrow audit-only evolution |

## New interfaces

Task 1 defines:

~~~python
ANTHROPIC_ADAPTER_ID = "anthropic-direct-messages"
ANTHROPIC_ADAPTER_VERSION = "1.0.0"
ANTHROPIC_API_VERSION = "2023-06-01"
ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
ANTHROPIC_HOST = "api.anthropic.com"
ANTHROPIC_PATH = "/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-5"
ANTHROPIC_PROJECTION_VERSION = "joewrks.anthropic-message-projection/1.0"
ANTHROPIC_MAX_TOKENS = 65536
ANTHROPIC_MAX_PROVIDER_BODY_BYTES = 32000000
ANTHROPIC_MAX_RESPONSE_BYTES = 16777216
ANTHROPIC_CREDENTIAL_SOURCE = "ANTHROPIC_API_KEY"

@dataclass(frozen=True, slots=True)
class AnthropicProjection:
    canonical_request_sha256: str
    reviewer_id: str
    review_run_id: str
    context_id: str
    provider_body: bytes
    provider_body_sha256: str

def anthropic_settings_record() -> dict[str, object]
def anthropic_settings_bytes() -> bytes
def anthropic_settings_sha256() -> str
def project_anthropic_request(request_bytes: bytes) -> AnthropicProjection
~~~

Task 2 defines:

~~~python
ANTHROPIC_PROVISIONING_SCHEMA_VERSION = "joewrks.anthropic-provisioning-evidence/1.0"
ANTHROPIC_ADMISSION_SCHEMA_VERSION = "joewrks.anthropic-admission-evidence/1.0"
ANTHROPIC_CAPABILITY_EVIDENCE_SCHEMA_VERSION = "joewrks.anthropic-capability-evidence/1.0"
ANTHROPIC_CAPACITY_SCHEMA_VERSION = "joewrks.anthropic-local-capacity-measurement/1.0"

class AnthropicProvisioningStatus(str, Enum):
    READY_FOR_PREFLIGHT = "READY_FOR_PREFLIGHT"
    BACKEND_PROVISIONING_REQUIRED = "BACKEND_PROVISIONING_REQUIRED"

@dataclass(frozen=True, slots=True)
class AnthropicProvisioningEvidence:
    schema_version: str
    expected_anthropic_workspace_id_sha256: str | None
    workspace_key_scope: str | None
    workspace_evidence_channel: str | None
    workspace_evidence_sha256: str | None
    retention_privacy_evidence_channel: str | None
    retention_privacy_evidence_sha256: str | None
    retention_privacy_approval: str | None
    inference_geo_evidence_sha256: str | None
    model_entitlement_evidence_sha256: str | None
    capacity_and_quota_evidence_sha256: str | None
    spend_approval_evidence_sha256: str | None
    provider_policy_approval_evidence_sha256: str | None
    credential_readiness_evidence_sha256: str | None

@dataclass(frozen=True, slots=True)
class AnthropicAdmissionEvidence:
    schema_version: str
    adapter_source_manifest_sha256: str | None
    local_conformance_evidence_sha256: str | None
    canonical_provider_body_sha256: str | None
    provider_official_contract_sha256: str | None
    local_capacity_measurement_sha256: str | None
    provisioning: AnthropicProvisioningEvidence

@dataclass(frozen=True, slots=True)
class AnthropicBackendConfiguration:
    provisioning_status: AnthropicProvisioningStatus
    descriptor: BackendDescriptor
    expected_anthropic_workspace_id_sha256: str | None
    admission_evidence_sha256: str

def unprovisioned_anthropic_admission() -> AnthropicAdmissionEvidence
def build_anthropic_backend_configuration(
    evidence: AnthropicAdmissionEvidence,
) -> AnthropicBackendConfiguration
~~~

Task 3 defines:

~~~python
@dataclass(frozen=True, slots=True)
class AnthropicHttpResponse:
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes

class StdlibAnthropicTransport:
    @property
    def is_test_double(self) -> bool

    def post(
        self,
        body: bytes,
        *,
        api_key: str,
        timeout_seconds: int,
    ) -> AnthropicHttpResponse
~~~

Task 4 defines:

~~~python
class AnthropicProvisioningRequired(RuntimeError):
    code = "BACKEND_PROVISIONING_REQUIRED"

class AnthropicBackend:
    def __init__(
        self,
        configuration: AnthropicBackendConfiguration,
        *,
        transport: StdlibAnthropicTransport | None = None,
        credential_reader: Callable[[str], str | None] | None = None,
    )

    def describe(self) -> BackendDescriptor

    def invoke(
        self,
        request_bytes: bytes,
        *,
        timeout_seconds: int,
    ) -> BackendResponse
~~~

Passing a custom transport or custom credential_reader is a test seam. AnthropicBackend must then expose a derived descriptor with is_test_double = true and every observation downgraded to UNTESTED. The production constructor uses a direct StdlibAnthropicTransport and reads ANTHROPIC_API_KEY only inside invoke. An unprovisioned configuration raises AnthropicProvisioningRequired before reading the credential or constructing a connection.

anthropic.py uses postponed annotations and imports AnthropicBackendConfiguration only inside AnthropicBackend construction/validation. anthropic_admission.py may import the already defined Anthropic constants and pure settings functions. This one-way runtime loading rule prevents a providers → anthropic → anthropic_admission → anthropic import cycle.

Task 5 defines:

~~~python
REGISTERED_PRODUCTION_ADAPTERS: tuple[AnthropicBackend, ...]
~~~

The tuple contains exactly one AnthropicBackend built from unprovisioned_anthropic_admission(). Importing it reads no environment value and performs no DNS, socket, TLS, HTTP, filesystem write, or evidence mutation.

Task 7 defines:

~~~python
def build_anthropic_offline_guard_report(
    repository: Path | str,
    revision: str,
) -> dict[str, object]
~~~

The report is canonical, source-snapshot-bound local conformance evidence. It contains the audited revision/tree, exact provider source manifest hash, exact REQUIRED_CAPABILITIES hash, forbidden-import result, registration count, registered descriptor classification, import/describe side-effect result, and overall PASS/FAIL. It never inspects environment values or opens a network connection.

## Exact closed evidence records

AnthropicProvisioningEvidence serializes as canonical JSON with exactly the 14 declared fields. Null means missing and keeps the associated observation UNAVAILABLE. A non-null digest must be lowercase SHA-256. workspace_key_scope must be WORKSPACE_SCOPED. workspace_evidence_channel is MACHINE_READABLE or CONSOLE_OR_ADMINISTRATOR. retention_privacy_evidence_channel is exactly CONTRACT_CONSOLE_OR_ADMINISTRATOR. retention_privacy_approval is STANDARD_RETENTION_ACCEPTED or ZDR_VERIFIED. No raw workspace ID, API key, key hash/prefix/name/path, Admin credential, account token, or Console contents enter this record.

AnthropicAdmissionEvidence serializes as canonical JSON with exactly the seven declared fields. adapter_source_manifest_sha256 commits the provider modules' exact Git modes/blob IDs. local_conformance_evidence_sha256 commits the offline Task 1–7 test result record. canonical_provider_body_sha256 commits the deterministic 319,066-byte inert local projection fixture, not a future nonce-bearing P1 body. provider_official_contract_sha256 commits the approved candidate-audit bytes. local_capacity_measurement_sha256 commits the closed capacity record. provisioning commits the exact provisioning record.

The local capacity record contains exactly:

~~~text
schema_version
required_package_bytes = 319066
canonical_request_bytes
projected_provider_body_bytes
provider_body_limit_bytes = 32000000
configured_max_output_tokens = 65536
documented_context_tokens = 1000000
documented_model_max_output_tokens = 128000
exact_provider_input_tokens
account_quota_evidence_sha256
measurement_result
~~~

During this implementation wave exact_provider_input_tokens and account_quota_evidence_sha256 are null and measurement_result is BACKEND_PROVISIONING_REQUIRED. A future separately authorized Token Counting/provisioning task may create a complete record; this plan never does.

Each CapabilityObservation.evidence_sha256 is hash_evidence_record() over one exact canonical record:

~~~text
schema_version = joewrks.anthropic-capability-evidence/1.0
capability
method
classification
adapter_source_sha256
canonical_provider_body_sha256
provisioning_evidence_sha256
provider_official_contract_sha256
workspace_commitment_sha256
local_capacity_measurement_sha256
local_conformance_evidence_sha256
settings_sha256
~~~

Every unused dependency field is null rather than omitted. Missing required evidence produces UNAVAILABLE. Present evidence that is malformed, hash-inconsistent, contradictory, failed, or not PM-approved produces OBSERVED_FAIL. Only a complete consistent record produces OBSERVED_PASS.

## Preflight Admission Evidence Matrix

| Capability | Exact producer and method | Exact hash input | Why direct before a call | OBSERVED_PASS condition | UNAVAILABLE / OBSERVED_FAIL condition | Dependencies | Freshness invalidation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stateless_fresh_request | build_anthropic_backend_configuration; direct:anthropic-single-message-body | Capability evidence record with adapter source, local fixture body, official contract, local conformance, and settings hashes | Fixed POST body has one Message request and no conversation identifier; source and exact fixture bytes are frozen | Source audit proves one body/one request shape and official Messages contract is bound | Missing source/body/contract/conformance = UNAVAILABLE; extra state or failed fixture = OBSERVED_FAIL | adapter source, canonical body, official contract | Any provider source, settings, projection, contract, or conformance hash change |
| no_continuation_id | build_anthropic_backend_configuration; direct:anthropic-no-continuation-fields | Same closed record, binding the exact provider-body key set | Body key allowlist excludes continuation, previous response, and conversation fields | Exact fixture and source scan contain none of those fields | Missing proof = UNAVAILABLE; any forbidden key = OBSERVED_FAIL | adapter source, canonical body, official contract | Source/body/contract/conformance change |
| no_reviewer_memory | build_anthropic_backend_configuration; direct:anthropic-direct-messages-stateless-contract | Closed record binding endpoint/path, single-message body, and provider contract | Direct Messages endpoint receives no managed-agent/container/thread identity | Fixed endpoint/body plus accepted official stateless contract all verify | Missing contract/body = UNAVAILABLE; stateful endpoint or memory field = OBSERVED_FAIL | adapter source, canonical body, official contract | Endpoint, API version, source, body, or contract change |
| no_tools | build_anthropic_backend_configuration; direct:anthropic-tool-fields-absent | Closed record binding source/body/conformance/contract | Exact request key set omits tools and response allowlist rejects tool_use/server_tool_use | Source and fixture omit tool configuration; adversarial response tests pass | Missing proof = UNAVAILABLE; tool field/block accepted = OBSERVED_FAIL | adapter source, canonical body, official contract | Source/body/contract/conformance change |
| no_retrieval | build_anthropic_backend_configuration; direct:anthropic-retrieval-fields-absent | Closed record binding source/body/conformance/contract | No retrieval, search, data source, or external-content field exists in the body | Omission scan and rejection tests pass against the fixed provider contract | Missing proof = UNAVAILABLE; retrieval surface appears = OBSERVED_FAIL | adapter source, canonical body, official contract | Source/body/contract/conformance change |
| no_web_or_browser | build_anthropic_backend_configuration; direct:anthropic-web-fields-absent | Closed record binding source/body/conformance/contract | Web/search/browser server tools require explicit configuration, which the fixed body omits | Source/body omission and unexpected block rejection both pass | Missing proof = UNAVAILABLE; web/search/browser field or block = OBSERVED_FAIL | adapter source, canonical body, official contract | Source/body/contract/conformance change |
| no_connectors_or_mcp | build_anthropic_backend_configuration; direct:anthropic-connector-mcp-fields-absent | Closed record binding source/body/conformance/contract | No MCP server, connector, integration, or tool definition can be supplied through the adapter interface | Exact body omission and adversarial block rejection pass | Missing proof = UNAVAILABLE; connector/MCP surface accepted = OBSERVED_FAIL | adapter source, canonical body, official contract | Source/body/contract/conformance change |
| no_host_filesystem | build_anthropic_backend_configuration; direct:anthropic-inline-text-only | Closed record binding adapter source, canonical body, and local conformance | Projection accepts bytes only and emits inline text; adapter accepts no path or file handle | Four inline texts and no path/URI/file fields are proven | Missing proof = UNAVAILABLE; path/file dereference or API field = OBSERVED_FAIL | adapter source, canonical body | Source/body/conformance change |
| no_code_execution | build_anthropic_backend_configuration; direct:anthropic-code-execution-fields-absent | Closed record binding source/body/conformance/contract | Containers, skills, bash, text-editor, and code-execution tools are absent and active blocks are rejected | Omission scan and adversarial response tests pass | Missing proof = UNAVAILABLE; executable feature or active block = OBSERVED_FAIL | adapter source, canonical body, official contract | Source/body/contract/conformance change |
| no_file_by_reference | build_anthropic_backend_configuration; direct:anthropic-no-file-reference | Closed record binding projection source/body and local conformance | Adapter decodes existing inline role bytes and cannot accept file IDs, uploads, URLs, or attachments | Exact inline projection and malformed/file-field rejection pass | Missing proof = UNAVAILABLE; reference/upload/chunk/split path = OBSERVED_FAIL | adapter source, canonical body | Source/body/conformance change |
| immutable_model_or_deployment_identity | build_anthropic_backend_configuration; direct:anthropic-pinned-model-workspace-commitment | Closed record binding source, official contract, provisioning hash, and workspace commitment | Pinned model ID and preverified workspace hash define identity before P1; response can only verify it | model is claude-sonnet-5, stability IMMUTABLE, provisioning is approved, workspace digest valid, deployment record hashes exact provider/platform/workspace/endpoint/API/geo/adapter fields | Missing contract/workspace/provisioning = UNAVAILABLE; floating model, malformed digest, or conflicting deployment = OBSERVED_FAIL | adapter source, provisioning, official contract, workspace commitment | Model/endpoint/API/geo/adapter/source/contract/provisioning hash change |
| immutable_inference_settings | build_anthropic_backend_configuration; direct:anthropic-canonical-settings | Closed record binding anthropic_settings_sha256, source, body, and conformance | All selected settings and all forbidden sampling/tool/state absences are canonical before P1 | Recomputed settings hash and exact body settings agree and omission tests pass | Missing source/conformance = UNAVAILABLE; hash/body drift or forbidden setting = OBSERVED_FAIL | adapter source, canonical body | Settings/source/body/conformance change |
| sufficient_payload_capacity | build_anthropic_backend_configuration; direct:anthropic-capacity-and-quota-record | Closed record binding local capacity measurement, official limits, canonical body, provisioning quota/token/spend proof | Exact inert size, projected body bytes, provider limits, token count, quota, and spend are frozen before P1 | All closed capacity fields are present, body below 32,000,000 bytes, token input plus 65,536 output fits 1,000,000 context, output below 128,000, and account quota/spend evidence is approved | Missing token/quota/spend record = UNAVAILABLE; any exceeded or contradictory bound = OBSERVED_FAIL | canonical body, provisioning, official contract, local capacity measurement | Body/settings/contract/capacity/provisioning change |
| exact_structured_output | build_anthropic_backend_configuration; direct:anthropic-one-text-existing-json-validator | Closed record binding response allowlist source, local conformance, canonical body, and official plain-text contract | Adapter allows one final text block and existing runner freezes/parses one exact JSON document against the unchanged schema | Sole-text extraction, exact-byte preservation, malformed/multiple/truncated/refusal/tool rejection, and existing response regressions pass | Missing source/contract/conformance = UNAVAILABLE; any response bypass = OBSERVED_FAIL | adapter source, canonical body, official contract | Source/body/contract/conformance or existing response-validator freshness change |
| controller_only_authentication | build_anthropic_backend_configuration; direct:anthropic-workspace-key-controller-boundary | Closed record binding source, provisioning record, workspace commitment, and conformance | Only invoke reads ANTHROPIC_API_KEY; only x-api-key receives it; descriptor/body/events/audit do not | Workspace-scoped credential-readiness evidence is approved, source has one auth header, and secret-exclusion tests pass | Missing credential readiness/key scope = UNAVAILABLE; alternate auth, leak, raw workspace selector, or invalid evidence = OBSERVED_FAIL | adapter source, provisioning, official contract, workspace commitment | Source/provisioning/contract/conformance change |
| accepted_retention_and_privacy | build_anthropic_backend_configuration; direct:anthropic-approved-account-policy | Closed record binding official contract and PM-approved contract/Console/administrator evidence | Account policy is an explicit frozen prerequisite and is not inferred from runtime header or docs alone | Exact policy evidence channel/hash and STANDARD_RETENTION_ACCEPTED or ZDR_VERIFIED approval exist with provider-policy and data-use evidence | Missing approval/evidence = UNAVAILABLE; contradicted, unapproved, or undocumented API claim = OBSERVED_FAIL | provisioning, official contract, workspace commitment | Contract/provisioning/approval/workspace change |
| request_response_commitments | build_anthropic_backend_configuration; direct:anthropic-request-response-hash-binding | Closed record binding source/body/settings/workspace/local conformance and response-event schema | Canonical request hash, provider body hash, backend identity, server request-id, workspace hash, and exact text bytes are defined before/at one response without changing descriptor | Binding tests pass; event record is secret-free; server ID non-empty; workspace/model/settings agree; existing replay/freeze validators remain unchanged | Missing structural proof/workspace = UNAVAILABLE; mismatch, missing/reused ID, descriptor drift, or normalized raw bytes = OBSERVED_FAIL | adapter source, canonical body, provisioning, workspace commitment | Any source/body/settings/provisioning/conformance change |

The matrix has exactly 17 rows. A local fixture may satisfy structural rows, but the implementation's registered unprovisioned instance still has missing account/capacity rows, so classify_backend_eligibility cannot return OBSERVED_PASS and run_isolation_preflight cannot call invoke.

## Baseline and canonical-LF worktree setup

- [ ] Fetch and verify remote authority from the planning worktree:

~~~powershell
git fetch origin
$expectedMain = "ab95074704af0e93248d56344d6a220dfec88a93"
$expectedPlan = "c1c06dca65ae007cb59353a75788eaf2096bd219"
$expectedPlanTree = "7444b53a69520e629a4f828eab8f3727a03e5ebe"
if ((git rev-parse origin/main) -ne $expectedMain) { throw "REAL_BACKEND_IMPLEMENTATION_BLOCKED — BASELINE_MOVED" }
if ((git rev-parse origin/plan/post-m6-real-backend-capability-enablement) -ne $expectedPlan) { throw "REAL_BACKEND_IMPLEMENTATION_BLOCKED — BASELINE_MOVED" }
if ((git rev-parse "$expectedPlan^{tree}") -ne $expectedPlanTree) { throw "REAL_BACKEND_IMPLEMENTATION_BLOCKED — BASELINE_MOVED" }
git status --short
~~~

Expected: all three identities match and status is empty.

- [ ] Create the implementation worktree with command-scoped LF settings:

~~~powershell
$implementationWorktree = "D:/JOEWRKS/JOEWRKS-Product-post-m6-real-backend-implementation"
git -c core.autocrlf=false -c core.eol=lf worktree add -b codex/post-m6-real-backend-capability-enablement $implementationWorktree $expectedPlan
Set-Location -LiteralPath $implementationWorktree
~~~

Expected: the new branch points exactly to c1c06dca65ae007cb59353a75788eaf2096bd219. Do not reuse a non-empty or pre-existing ambiguous path.

- [ ] Verify raw runner bytes against Git blobs:

~~~powershell
$runnerFiles = git ls-tree -r --name-only HEAD -- skills/joewrks-product-definition/reviewer_runner
$mismatches = @()
foreach ($path in $runnerFiles) {
    $expectedBlob = git rev-parse "HEAD:$path"
    $liveBlob = git hash-object --no-filters -- $path
    if ($liveBlob -ne $expectedBlob) { $mismatches += $path }
}
if ($mismatches.Count -ne 0) {
    $mismatches
    throw "REAL_BACKEND_IMPLEMENTATION_BLOCKED — NONCANONICAL_WORKTREE"
}
git status --short
~~~

Expected: zero mismatches and clean status. Do not retry by rewriting or normalizing source.

## Shared Task review protocol

For each Task, record the Task base SHA before edits. After the focused GREEN commit:

~~~powershell
git diff --check $taskBase..HEAD
git diff --name-status $taskBase..HEAD
git diff --stat $taskBase..HEAD
git log --oneline $taskBase..HEAD
~~~

Give a fresh independent reviewer the exact Task requirements, these outputs, the complete diff from git diff $taskBase..HEAD, and the exact test outputs. Require a severity-ranked report. Fix every Critical and Important finding, rerun the Task tests and declared regressions, commit each fix with message fix: address Task N review findings, and rerun review until Critical = 0 and Important = 0. Minor findings may remain only when the reviewer states they do not affect correctness, security, evidence truth, or the frozen contract, and they must be listed in the final implementation audit.

### Task 1: Freeze settings and the exact four-role Anthropic projection

**Files:**

- Create: skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py
- Create: tests/test_reviewer_runner_anthropic_projection.py

**Produces:** AnthropicProjection and the Task 1 constants/settings/projection functions declared above.

- [ ] Write controlled-RED tests with these exact methods:

1. test_settings_record_and_hash_are_canonical_and_deterministic
2. test_projection_has_one_system_block_and_three_ordered_user_blocks
3. test_user_block_header_is_canonical_json_newline_exact_content
4. test_projection_rejects_duplicate_missing_extra_or_wrong_media_roles
5. test_projection_rejects_bad_counts_hash_base64_utf8_and_duplicate_json_keys
6. test_provider_body_has_exact_fixed_settings_and_forbidden_fields_absent
7. test_projection_is_unsplit_untruncated_and_size_bounded

The test module catches ImportError only to set each missing symbol to None. The first behavioral assertion uses assertIsNotNone. It must not raise at test loading.

- [ ] Run RED:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_projection -v
~~~

Expected: the module is discovered; at least one named test reports FAIL from a controlled assertion; ERROR count is zero.

- [ ] Implement exact request validation and projection.

Accept only canonical UTF-8 JSON with the exact current top-level request keys and versions. Reject duplicate JSON keys and non-JSON numbers. Require one each of reviewer_brief/text/markdown, review_package/application/json, run_envelope/application/json, and output_schema/application/schema+json. Verify each content_base64 with validate=True, byte_count, SHA-256, and re-encoding equality.

Require the input bytes to equal canonical_json_bytes of the parsed document. Require top-level keys inputs, request_schema_version, response_contract, run_identity, and runner_contract_version; current exact version values; response_contract exactly logical_response_count 1 and media_type application/json; and run_identity keys semantic_review_contract_version, package_schema_version, reviewer_id, review_run_id, and context_id with valid non-empty identifier/version strings. Require the inputs array to retain the current canonical logical-role sort order before projecting it into Anthropic's explicit user-block order.

Use reviewer_brief strict UTF-8 as:

~~~python
"system": [{"type": "text", "text": reviewer_brief_text}]
~~~

Use one user message with blocks in this exact order: review_package, run_envelope, output_schema. Each text is:

~~~text
canonical_json_bytes({"byte_count": byte_count, "logical_role": logical_role, "media_type": media_type, "sha256": sha256}).decode("utf-8")
+ one LF byte
+ strict UTF-8 decoded content
~~~

The complete provider body has exactly these keys and values:

~~~python
{
    "inference_geo": "us",
    "max_tokens": 65536,
    "messages": [{"role": "user", "content": ordered_user_blocks}],
    "model": "claude-sonnet-5",
    "output_config": {"effort": "high"},
    "service_tier": "standard_only",
    "stream": False,
    "system": [{"type": "text", "text": reviewer_brief_text}],
    "thinking": {"type": "adaptive"},
}
~~~

Serialize with canonical_json_bytes. Reject a body larger than 32,000,000 bytes. No temperature, top_p, top_k, seed field, tools, files, containers, skills, MCP, retrieval, cache, conversation, continuation, or output_config.format key is present.

anthropic_settings_record returns the exact design identity record, including endpoint, API version, projection, output mode, explicit settings, and named ABSENT markers. Tests recompute its SHA-256 from anthropic_settings_bytes; no precomputed digest literal is copied into code or plan.

The exact settings identity record is:

~~~json
{
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
  "stream": false,
  "temperature": "ABSENT",
  "thinking": {"type": "adaptive"},
  "tools": "ABSENT",
  "top_k": "ABSENT",
  "top_p": "ABSENT"
}
~~~

- [ ] Run GREEN and request regressions:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_projection tests.test_reviewer_runner_request tests.test_reviewer_runner_backend -v
~~~

Expected: exit 0, final unittest status OK, zero skip, zero network.

- [ ] Commit:

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py tests/test_reviewer_runner_anthropic_projection.py
git commit -m "feat: add anthropic request projection"
~~~

- [ ] Apply the Shared Task review protocol for Task 1 before Task 2.

### Task 2: Compile immutable provisioning and 17-capability admission evidence

**Files:**

- Create: skills/joewrks-product-definition/reviewer_runner/providers/anthropic_admission.py
- Create: tests/test_reviewer_runner_anthropic_admission.py

**Produces:** AnthropicProvisioningStatus, AnthropicProvisioningEvidence, AnthropicAdmissionEvidence, AnthropicBackendConfiguration, unprovisioned_anthropic_admission, and build_anthropic_backend_configuration.

- [ ] Write controlled-RED tests with these exact methods:

1. test_unprovisioned_record_has_closed_schema_and_no_secret_or_raw_workspace_id
2. test_deployment_identity_hashes_exact_provider_platform_workspace_endpoint_api_geo_adapter_record
3. test_observations_match_required_capabilities_exactly_once_and_in_order
4. test_every_observation_hashes_the_closed_capability_evidence_record
5. test_missing_required_dependency_is_unavailable_and_preflight_ineligible
6. test_present_contradictory_dependency_is_observed_fail
7. test_complete_frozen_inputs_are_observed_pass_with_direct_methods
8. test_descriptor_hash_is_deterministic_and_input_mutation_changes_freshness
9. test_capacity_stays_unavailable_without_token_quota_and_spend_evidence
10. test_policy_channels_are_distinct_and_runtime_workspace_header_cannot_approve_privacy
11. test_api_key_value_hash_prefix_name_and_path_are_rejected_from_evidence

Use locally invented lowercase digests and explicit synthetic approval records. They are non-authoritative unit fixtures and contain no real account fact.

- [ ] Run RED:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_admission -v
~~~

Expected: tests load and at least one named assertion FAILS; ERROR count is zero.

- [ ] Implement the closed records and matrix.

Validate exact dataclass types, exact enum values, lowercase SHA-256 strings, and canonical serialization. Compute deployment_identity as SHA-256 of canonical JSON with exactly:

~~~text
adapter_id
adapter_version
api_version
endpoint
expected_anthropic_workspace_id_sha256
inference_geo_policy
platform = direct_claude_api
provider = anthropic
~~~

Build BackendIdentity with backend kind STATELESS_TOOLLESS_EXTERNAL_INFERENCE, adapter/model/settings constants, model stability IMMUTABLE, the canonical deployment hash, policy identities derived from approved provisioning evidence, and is_test_double false.

Emit exactly one observation per REQUIRED_CAPABILITIES entry using the matrix above. A complete unit fixture can exercise the OBSERVED_PASS branch, but its synthetic evidence must never be registered or persisted. The unprovisioned production registration remains ineligible.

- [ ] Run GREEN plus eligibility/preflight regressions:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_admission tests.test_reviewer_runner_backend tests.test_reviewer_runner_preflight -v
~~~

Expected: exit 0, OK, zero skip. The unprovisioned descriptor causes run_isolation_preflight to return without invoke and reason capability-prerequisite-not-observed.

- [ ] Commit:

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/providers/anthropic_admission.py tests/test_reviewer_runner_anthropic_admission.py
git commit -m "feat: bind anthropic preflight admission evidence"
~~~

- [ ] Apply the Shared Task review protocol for Task 2 before Task 3.

### Task 3: Implement the one-request standard-library HTTPS transport

**Files:**

- Modify: skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py
- Create: tests/test_reviewer_runner_anthropic_transport.py

**Produces:** AnthropicHttpResponse and StdlibAnthropicTransport.

- [ ] Write controlled-RED tests with these exact methods:

1. test_default_transport_uses_fresh_https_connection_verified_default_context_and_fixed_host
2. test_exact_post_path_headers_body_and_connection_close
3. test_success_performs_one_request_and_closes_connection
4. test_redirect_408_409_429_and_5xx_fail_without_second_request
5. test_timeout_eof_tls_and_connection_loss_fail_without_retry
6. test_oversized_or_incomplete_response_fails_closed
7. test_proxy_environment_is_not_consulted_and_caller_url_is_impossible
8. test_custom_transport_factory_is_marked_test_only

The fake connection object counts constructor, request, getresponse, read, and close calls. It never opens a socket.

- [ ] Run RED:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_transport -v
~~~

Expected: controlled assertion FAIL, zero test-loading ERROR, zero DNS/socket activity.

- [ ] Implement direct transport.

Create ssl.create_default_context() for verified certificate and hostname validation. Construct one http.client.HTTPSConnection with host api.anthropic.com, port 443, the caller timeout, and that context. Send exactly one POST to /v1/messages with body bytes and exactly these explicit headers:

~~~text
anthropic-version: 2023-06-01
connection: close
content-type: application/json
x-api-key: the invoke-time credential
~~~

x-api-key is the only authentication header. Do not support Authorization or anthropic-workspace-id request selection. Read at most 16,777,217 bytes and reject more than 16,777,216. Close in finally. Never loop, retry, follow Location, consult proxy variables, or issue model/token/status/account calls.

Map timeout to BackendInvocationError(TIMEOUT); socket/TLS/EOF/http.client failures to TRANSPORT_ERROR or NO_RESPONSE according to whether an HTTP response object existed. Use constant messages without endpoint payload, headers, credential, or exception repr. HTTP non-200 is a single controlled NO_RESPONSE and never includes body text.

- [ ] Run GREEN plus backend failure regressions:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_transport tests.test_reviewer_runner_backend tests.test_reviewer_runner_controller -v
~~~

Expected: exit 0, OK, zero skip, every transport case records exactly one request call at most.

- [ ] Commit:

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py tests/test_reviewer_runner_anthropic_transport.py
git commit -m "feat: add one-request anthropic https transport"
~~~

- [ ] Apply the Shared Task review protocol for Task 3 before Task 4.

### Task 4: Bind the Anthropic response to the existing BackendResponse

**Files:**

- Modify: skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py
- Create: tests/test_reviewer_runner_anthropic_response.py

**Produces:** AnthropicProvisioningRequired and AnthropicBackend.

- [ ] Write controlled-RED tests with these exact methods:

1. test_unprovisioned_invoke_returns_backend_provisioning_required_before_credential_or_transport
2. test_missing_or_empty_api_key_fails_before_transport_without_echo
3. test_valid_message_returns_exact_text_utf8_bytes_without_strip_or_reserialization
4. test_request_id_is_nonempty_server_header_and_workspace_hash_matches_commitment
5. test_missing_duplicate_or_mismatched_request_and_workspace_headers_fail_closed
6. test_wrong_model_role_type_message_id_or_stop_reason_fails_closed
7. test_zero_multiple_or_nonfinal_text_blocks_fail_closed
8. test_tool_server_tool_refusal_truncation_and_unexpected_active_blocks_fail_closed
9. test_thinking_and_redacted_thinking_are_metadata_only_before_one_final_text
10. test_response_event_hash_binds_only_sanitized_closed_metadata
11. test_secret_and_raw_workspace_id_are_absent_from_response_event_error_and_repr
12. test_custom_transport_or_credential_reader_forces_test_double_non_authority
13. test_existing_freeze_parser_replay_and_controller_binding_accept_valid_translation

- [ ] Run RED:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_response -v
~~~

Expected: controlled FAIL, no import/collection ERROR, no network.

- [ ] Implement response and invocation binding.

AnthropicBackend.describe returns the configuration descriptor without I/O. invoke performs this exact order: validate timeout; require READY_FOR_PREFLIGHT; project and validate request bytes; read ANTHROPIC_API_KEY once; reject missing/empty; make one transport post; parse the envelope with strict UTF-8, duplicate-key rejection, and non-finite-number rejection; validate headers/envelope/content; return BackendResponse.

Require exactly one request-id header and one anthropic-workspace-id header. Values must be non-empty and must not be stripped before validation or hashing. Encode the exact returned workspace header string with strict UTF-8 and compare its SHA-256 with the pre-call commitment. The request-id string becomes provider_request_id; the existing controller/evidence replay index owns cross-run uniqueness.

Require HTTP 200 and a Message object with type message, role assistant, model claude-sonnet-5, non-empty id, stop_reason end_turn, and exactly one text block as the final content block. Allow only thinking and redacted_thinking blocks before it. Reject every other block type, refusal, max_tokens, tool_use, pause_turn, malformed usage, or extra active content.

Require the Message envelope to have exactly id, type, role, content, model, stop_reason, stop_sequence, and usage. stop_sequence must be null. usage must have non-negative integer input_tokens and output_tokens, service_tier standard, and inference_geo us; it may additionally contain non-negative integer cache_creation_input_tokens and cache_read_input_tokens. Reject every other usage key or non-integer value. This closed normalized usage object is the one committed into event metadata.

BackendResponse.raw_bytes is text.encode("utf-8") with no strip, parse, dump, normalization, or newline change. continuation_id and previous_response_id remain None; response_count is 1.

The sole RESPONSE event hashes canonical JSON with exactly:

~~~text
schema_version = joewrks.anthropic-response-event/1.0
http_body_byte_count
http_body_sha256
message_id
model
stop_reason
content_block_types
usage
inference_geo = us
provider_request_body_sha256
provider_request_id_sha256
anthropic_workspace_id_sha256
~~~

No request/response header map, API key, raw request ID, raw workspace ID, credential source, provider error body, or unvalidated envelope field enters the event.

- [ ] Run GREEN and exact-byte/binding regressions:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_response tests.test_reviewer_runner_response tests.test_reviewer_runner_preflight tests.test_reviewer_runner_controller -v
~~~

Expected: exit 0, OK, zero skip. Exact raw response freeze, replay defense, and descriptor-before/after equality remain intact.

- [ ] Commit:

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py tests/test_reviewer_runner_anthropic_response.py
git commit -m "feat: bind anthropic provider responses"
~~~

- [ ] Apply the Shared Task review protocol for Task 4 before Task 5.

### Task 5: Register exactly one unprovisioned production adapter

**Files:**

- Create: skills/joewrks-product-definition/reviewer_runner/providers/__init__.py
- Modify: skills/joewrks-product-definition/scripts/audit_reviewer_runner.py
- Create: tests/test_reviewer_runner_anthropic_registration.py

**Produces:** REGISTERED_PRODUCTION_ADAPTERS and revision-snapshot provider loading.

- [ ] Write controlled-RED tests with these exact methods:

1. test_registration_contains_exactly_one_anthropic_backend
2. test_registered_adapter_is_non_test_but_preflight_ineligible_while_unprovisioned
3. test_registration_import_reads_no_environment_and_opens_no_network
4. test_registration_has_no_discovery_router_fallback_or_second_provider
5. test_audit_snapshot_loader_reads_exact_provider_modules_from_target_revision
6. test_revision_without_provider_package_retains_empty_registration
7. test_injected_transport_registration_cannot_count_as_authoritative

- [ ] Run RED:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_registration -v
~~~

Expected: controlled FAIL, no loading ERROR, zero network.

- [ ] Implement explicit registration and exact audit snapshot loading.

providers/__init__.py imports only AnthropicBackend, unprovisioned_anthropic_admission, and build_anthropic_backend_configuration, constructs one unprovisioned backend, and exposes the one-element tuple. Do not export a mutable registry or registration function.

Update the audit snapshot finder with an exact allowlist for reviewer_runner, identity, backend, request, providers, providers.anthropic, and providers.anthropic_admission. Require every imported module's loader, source bytes, filename, and revision blob to match the audited snapshot. A revision without providers/__init__.py has an empty registration. Any unexpected transitive reviewer_runner import fails closed.

Add a private verified-snapshot registration loader used directly by the Task 5 tests, but keep build_capability_audit's existing empty default behavior until Task 6 changes the audit schema and its assertions in the same GREEN scope. An explicit iterable remains a test-only injection path and never bypasses descriptor validation.

- [ ] Run GREEN and audit-source regressions:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_registration tests.test_reviewer_runner_audit -v
~~~

Expected: exit 0, OK. Historical zero-provider revision loading remains supported; current working revision discovers exactly one provider object without invoke.

- [ ] Commit:

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/providers/__init__.py skills/joewrks-product-definition/scripts/audit_reviewer_runner.py tests/test_reviewer_runner_anthropic_registration.py
git commit -m "feat: register anthropic backend candidate"
~~~

- [ ] Apply the Shared Task review protocol for Task 5 before Task 6.

### Task 6: Evolve the capability audit without rewriting historical evidence

**Files:**

- Modify: skills/joewrks-product-definition/scripts/audit_reviewer_runner.py
- Modify: tests/test_reviewer_runner_audit.py

**Produces:** joewrks.reviewer-runner-capability-audit/1.1 output for revisions containing the Anthropic registration.

- [ ] Write controlled-RED audit tests with these exact methods:

1. test_registered_unprovisioned_anthropic_revision_reports_v11_bounded_truth
2. test_v11_reports_adapter_implemented_count_one_and_provider_anthropic
3. test_v11_keeps_capability_unavailable_preflight_not_run_and_request_count_zero
4. test_v11_keeps_calibration_not_run_reliability_not_measured_and_v044_blocked
5. test_v11_contains_no_environment_value_raw_workspace_or_credential_material
6. test_historical_v10_revision_and_frozen_evidence_remain_byte_exact
7. test_fake_or_injected_adapter_cannot_promote_capability

- [ ] Run RED:

~~~powershell
python -m unittest tests.test_reviewer_runner_audit -v
~~~

Expected: tests load; new v1.1 assertions FAIL; historical tests do not ERROR.

- [ ] Implement deterministic audit schema dispatch.

Change build_capability_audit registered_adapters default to None. None means load REGISTERED_PRODUCTION_ADAPTERS from the verified target revision. A revision without the provider package supplies an empty tuple. An explicit iterable remains a test-only injection path and cannot bypass exact descriptor rehydration and validation.

For a revision with no provider package, emit the existing v1.0 document byte-for-byte. For the new registered unprovisioned Anthropic revision, emit canonical v1.1 JSON with exactly:

~~~json
{
  "adapter_implementation": "IMPLEMENTED",
  "backend_kind": "STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
  "backend_provisioning": "REQUIRED",
  "calibration_status": "CALIBRATION_NOT_RUN",
  "fake_backend_authoritative": false,
  "implementation_code_commit": "revision argument resolved commit",
  "implementation_code_tree": "tree of that commit",
  "implementation_status": "RUNNER_IMPLEMENTED",
  "provider_candidate": "anthropic",
  "provider_selected": "anthropic",
  "real_backend_capability": "UNAVAILABLE",
  "real_calibration_attempts": 1,
  "real_provider_request_count": 0,
  "real_synthetic_preflight": "NOT_RUN",
  "registered_real_adapter_count": 1,
  "runner_contract_version": "joewrks.reviewer-runner/1.0",
  "runner_state": "ISOLATION_CAPABILITY_UNAVAILABLE",
  "schema_version": "joewrks.reviewer-runner-capability-audit/1.1",
  "semantic_review_21_reliability": "NOT_MEASURED",
  "v044_status": "BLOCKED",
  "valid_real_calibration_runs": 0
}
~~~

Derive adapter implementation/count/provider from the verified registration and descriptor. Hard-code only the bounded no-proof facts for this implementation audit: provisioning required, preflight not run, request count zero, and capability unavailable. Do not inspect ANTHROPIC_API_KEY or any account surface. A future proof must use a separately versioned evidence update; this audit cannot infer PASS from files, environment, or fake transport.

- [ ] Run GREEN, historical readback, and no-write CLI checks:

~~~powershell
python -m unittest tests.test_reviewer_runner_audit tests.test_reviewer_runner_anthropic_registration -v
python skills/joewrks-product-definition/scripts/audit_reviewer_runner.py --repository . --revision 0b754bdc2502be35a7f657275f17fe117e8c49bd --json
~~~

Expected: tests OK. CLI bytes for 0b754bdc2502be35a7f657275f17fe117e8c49bd equal evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json exactly; no bytecode or tracked/untracked file is created.

- [ ] Commit:

~~~powershell
git add skills/joewrks-product-definition/scripts/audit_reviewer_runner.py tests/test_reviewer_runner_audit.py
git commit -m "test: evolve real backend capability audit"
~~~

- [ ] Apply the Shared Task review protocol for Task 6 before Task 7.

### Task 7: Harden offline, secret, and fake-authority boundaries

**Files:**

- Create: tests/test_reviewer_runner_anthropic_offline.py
- Modify: skills/joewrks-product-definition/scripts/audit_reviewer_runner.py
- Modify only if a named test exposes a defect: skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py
- Modify only if a named test exposes a defect: skills/joewrks-product-definition/reviewer_runner/providers/anthropic_admission.py
- Modify only if a named test exposes a defect: skills/joewrks-product-definition/reviewer_runner/providers/__init__.py

**Produces:** build_anthropic_offline_guard_report in the audit module; no new runner public interface.

- [ ] Write controlled-RED tests with these exact methods:

1. test_import_describe_registration_and_audit_never_resolve_dns_or_open_socket
2. test_unexpected_real_named_credential_never_triggers_integration_execution
3. test_only_invoke_can_read_anthropic_api_key_and_reads_it_once
4. test_fake_key_is_absent_from_descriptor_response_event_audit_error_and_repr
5. test_raw_workspace_value_is_absent_from_persistable_objects
6. test_source_import_graph_contains_no_sdk_requests_httpx_proxy_or_admin_client
7. test_all_failure_classes_make_zero_or_one_request_and_zero_retries
8. test_test_transport_descriptor_is_ineligible_and_preflight_does_not_invoke
9. test_no_provider_call_exists_in_unit_test_or_audit_entry_points
10. test_required_capability_tuple_and_generic_runner_interfaces_are_unchanged

Patch socket.create_connection, socket.getaddrinfo, and http.client.HTTPSConnection to raise AssertionError for the import/describe/registration/audit test. Patch os.environ with an unmistakably fake ANTHROPIC_API_KEY and prove the calls remain zero.

- [ ] Run RED:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_offline -v
~~~

Expected: the module loads and the missing build_anthropic_offline_guard_report assertion FAILS; ERROR count is zero.

- [ ] Implement the revision-bound offline guard report and make only evidence-backed hardening fixes.

build_anthropic_offline_guard_report uses the audit's already verified revision snapshot. It hashes the exact provider mode/blob manifest, validates the exact one-adapter registration and ineligible unprovisioned descriptor, parses imports to reject anthropic, requests, httpx, urllib.request, proxy, subprocess, Admin API, provider discovery, and non-standard-library HTTP clients, and reports the unchanged REQUIRED_CAPABILITIES hash. It exercises import and describe only through the verified loader; it neither invokes the backend nor reads environment values. The first RED assertion requires this missing function, so RED is guaranteed to be a controlled assertion failure.

Do not refactor unrelated runner code. Each provider fix must correspond to one named failing assertion. Constant error messages must not interpolate provider bodies, headers, environment values, raw workspace IDs, or underlying exception text.

- [ ] Run all Anthropic and existing runner tests:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_projection tests.test_reviewer_runner_anthropic_admission tests.test_reviewer_runner_anthropic_transport tests.test_reviewer_runner_anthropic_response tests.test_reviewer_runner_anthropic_registration tests.test_reviewer_runner_anthropic_offline tests.test_reviewer_runner_identity tests.test_reviewer_runner_request tests.test_reviewer_runner_backend tests.test_reviewer_runner_preflight tests.test_reviewer_runner_response tests.test_reviewer_runner_evidence tests.test_reviewer_runner_controller tests.test_reviewer_runner_audit -v
~~~

Expected: exit 0, OK, zero skip, zero real network, zero provider requests.

- [ ] Commit:

~~~powershell
git add -- tests/test_reviewer_runner_anthropic_offline.py skills/joewrks-product-definition/scripts/audit_reviewer_runner.py skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py skills/joewrks-product-definition/reviewer_runner/providers/anthropic_admission.py skills/joewrks-product-definition/reviewer_runner/providers/__init__.py
git diff --cached --name-only
git commit -m "test: harden anthropic adapter offline boundaries"
~~~

Expected staged paths are the new offline test plus only provider files directly fixed by its failing assertions.

- [ ] Apply the Shared Task review protocol for Task 7 before Task 8.

### Task 8: Freeze the local implementation audit and final bounded evidence

**Files:**

- Create: evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_CAPABILITY_EVIDENCE.json
- Create: evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_AUDIT.md

**Produces:** Canonical v1.1 implementation evidence bound to the Task 7 code revision and a human-readable verification record.

- [ ] Freeze the code-only revision identity:

~~~powershell
$adapterCodeRevision = git rev-parse HEAD
$adapterCodeTree = git rev-parse HEAD^{tree}
git status --short
~~~

Expected: status empty. The new JSON will bind these exact values, avoiding a self-referential final evidence commit.

- [ ] Run the complete focused runner suite:

~~~powershell
python -m unittest tests.test_reviewer_runner_anthropic_projection tests.test_reviewer_runner_anthropic_admission tests.test_reviewer_runner_anthropic_transport tests.test_reviewer_runner_anthropic_response tests.test_reviewer_runner_anthropic_registration tests.test_reviewer_runner_anthropic_offline tests.test_reviewer_runner_identity tests.test_reviewer_runner_request tests.test_reviewer_runner_backend tests.test_reviewer_runner_preflight tests.test_reviewer_runner_response tests.test_reviewer_runner_evidence tests.test_reviewer_runner_controller tests.test_reviewer_runner_audit -v
~~~

Expected: exit 0, OK, zero skip, no network.

- [ ] Run semantic-review/1.0 and calibration-controller regressions:

~~~powershell
python -m unittest tests.test_semantic_review_hashing tests.test_semantic_review_responsibility tests.test_semantic_review_package tests.test_semantic_review_output tests.test_semantic_review_goldens tests.test_semantic_review_gate tests.test_semantic_review_statistics tests.test_semantic_review_negative_regressions tests.test_semantic_review_calibration_corpus tests.test_semantic_review_calibration_control_plane tests.test_official_calibration_controller tests.test_semantic_review_human_packet -v
~~~

Expected: exit 0 and OK. No counter, oracle, golden, threshold, or semantic contract changes.

- [ ] Create and bind the historical M6 detached fixture:

~~~powershell
$m6FixtureCommit = "d38b0ca04768888c47e658c79f41e1cec0a7a1ce"
$m6FixtureTree = "40749d900b98936cf694b0c96db7897011cddae8"
$m6FixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("joewrks-m6-fixture-" + [guid]::NewGuid().ToString("N"))
$m6Fixture = Join-Path $m6FixtureRoot "worktree"
New-Item -ItemType Directory -Path $m6FixtureRoot | Out-Null
git -c core.autocrlf=false -c core.eol=lf worktree add --detach $m6Fixture $m6FixtureCommit
if ((git -C $m6Fixture rev-parse HEAD) -ne $m6FixtureCommit) { throw "M6 fixture commit mismatch" }
if ((git -C $m6Fixture rev-parse HEAD^{tree}) -ne $m6FixtureTree) { throw "M6 fixture tree mismatch" }
$priorM6Fixture = $env:JOEWRKS_M6_PHASE_B_WORKTREE
$env:JOEWRKS_M6_PHASE_B_WORKTREE = $m6Fixture
~~~

Expected: exact detached commit/tree and clean fixture. Keep it until both the M6 regression and full discovery complete.

- [ ] Run semantic-review/2.1, M6, runtime, and frozen-boundary regressions:

~~~powershell
python -m unittest tests.test_downstream_v21_derivation tests.test_downstream_v21_compiler tests.test_downstream_v21_gap_routing tests.test_downstream_v21_audit tests.test_downstream_v21_semantic_review tests.test_downstream_v21_runtime_plan tests.test_downstream_v21_runtime_evidence tests.test_downstream_v21_dogfood_replay tests.test_downstream_v21_frozen_boundaries tests.test_core_semantic_closure_v2_m6_dogfood_phase_a tests.test_core_semantic_closure_v2_m6_dogfood_phase_b tests.test_m6_runtime_v21_verification tests.test_m6_client_feedback_portal_fixture -v
~~~

Expected: exit 0 and OK. Record any pre-existing environment-dependent skip by exact test name and reason; no Anthropic/runner test may skip.

- [ ] Run legacy and full repository verification while the fixture remains bound:

~~~powershell
python -m unittest tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
python -m unittest discover -s tests -v
git diff --check
~~~

Expected: all commands exit 0; unittest final status OK; git diff --check has no output. Record the exact full-suite test and skip counts.

- [ ] Remove only the exact detached fixture without force and restore the prior environment value:

~~~powershell
git worktree remove $m6Fixture
if (Test-Path -LiteralPath $m6Fixture) { throw "M6 fixture cleanup not verified" }
if ($null -eq $priorM6Fixture) {
    Remove-Item Env:JOEWRKS_M6_PHASE_B_WORKTREE -ErrorAction SilentlyContinue
} else {
    $env:JOEWRKS_M6_PHASE_B_WORKTREE = $priorM6Fixture
}
Remove-Item -LiteralPath $m6FixtureRoot
if (Test-Path -LiteralPath $m6FixtureRoot) { throw "M6 fixture root cleanup not verified" }
~~~

If removal fails, leave the ambiguous path untouched, record it, and stop. Do not use --force.

- [ ] Generate and freeze exact v1.1 audit output for the code revision:

~~~powershell
$auditJson = python skills/joewrks-product-definition/scripts/audit_reviewer_runner.py --repository . --revision $adapterCodeRevision --json
if ($LASTEXITCODE -ne 0) { throw "runner capability audit failed" }
$auditJson
~~~

Expected: the exact bounded v1.1 object from Task 6, with registered count 1, provisioning REQUIRED, capability UNAVAILABLE, preflight NOT_RUN, request count 0, calibration NOT_RUN, reliability NOT_MEASURED, and v0.4.4 BLOCKED.

Create REAL_BACKEND_IMPLEMENTATION_CAPABILITY_EVIDENCE.json as those exact canonical UTF-8 bytes plus one LF. Create REAL_BACKEND_IMPLEMENTATION_AUDIT.md with the code commit/tree, all per-Task commits/reviews, exact file manifest, test commands/results/skips, admission-matrix count, descriptor non-admission proof, no-network proof, historical evidence readback, frozen-boundary results, and bounded terminal truth. Record no timestamp-derived canonical field and no credential value.

- [ ] Verify new evidence readback and frozen boundaries:

~~~powershell
python -m unittest tests.test_reviewer_runner_audit tests.test_reviewer_runner_anthropic_offline -v
git diff --exit-code c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD -- product-definition
git diff --exit-code c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD -- skills/joewrks-product-definition/downstream
git diff --exit-code c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD -- skills/joewrks-product-definition/downstream_v21
git diff --exit-code c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD -- evals/semantic-review-v0.4.3
git diff --exit-code c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD -- evals/core-semantic-closure-v2-m6
git diff --exit-code c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD -- evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json
git diff --check
~~~

Expected: focused tests OK; all six frozen diffs empty; diff check empty.

- [ ] Commit the evidence:

~~~powershell
git add evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_CAPABILITY_EVIDENCE.json evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_AUDIT.md
git commit -m "test: audit anthropic backend implementation"
~~~

- [ ] Apply the Shared Task review protocol for Task 8. Require Critical = 0 and Important = 0, then rerun the full focused suite, full discovery with the exact M6 fixture, frozen diffs, and git diff --check against the final HEAD.

## Required test-family traceability

| Requirement | Exact coverage |
| --- | --- |
| Four roles and fixed media | Task 1 tests 2–5 |
| Deterministic settings/body/hash | Task 1 tests 1, 3, 6, 7 |
| No split/truncate/file/RAG/continuation | Task 1 tests 6–7; Task 7 tests 6 and 10 |
| Exact 17 pre-call observations | Task 2 tests 3–8 |
| Provisioning/policy/workspace separation | Task 2 tests 1, 9–11 |
| Descriptor immutable around proof | Task 2 test 8 plus existing preflight descriptor-drift tests |
| One direct HTTPS request/no retry | Task 3 tests 1–7; Task 7 test 7 |
| Exact authentication header/secret exclusion | Task 3 test 2; Task 4 tests 2 and 11; Task 7 tests 3–5 |
| Response/workspace/request-ID/model binding | Task 4 tests 3–10 and 13 |
| Test transport never authoritative | Task 3 test 8; Task 4 test 12; Task 5 test 7; Task 7 test 8 |
| No accidental network from environment | Task 5 test 3; Task 7 tests 1–3 and 9 |
| One explicit registration | Task 5 tests 1–4 |
| Audit history and bounded v1.1 truth | Task 5 tests 5–6; Task 6 tests 1–7 |
| Existing runner/freeze/replay behavior | Task 4 GREEN regressions; Task 7 full runner command |
| Semantic/M6/legacy/full regressions | Task 8 commands |

## Future P1/P2 gate — documentation only

This section defines no executable implementation-wave step.

A future separately authorized Post-M6 Real Backend Capability Proof task must supply a complete frozen AnthropicAdmissionEvidence, a workspace-scoped ANTHROPIC_API_KEY, accepted retention/privacy evidence, exact token/quota/cost proof, and explicit charge approval before any call.

P1 uses the existing run_isolation_preflight with the exact 319,066-byte inert package. The descriptor and descriptor hash are frozen before P1 and must be identical after invoke. The run-specific provider body hash is recorded in the sanitized RESPONSE event; it does not enter or mutate the descriptor.

P2 is a separately declared fresh synthetic invocation with new review_run_id, context_id, nonce, canonical request hash, and provider request ID; it uses the same descriptor and no previous-response identifier. A P1 failure or ambiguous result stops the proof. P2 is not an automatic retry.

Only accepted provisioning plus passing P1 and P2 may support a later capability-evidence revision. Neither local unit transport nor an all-OBSERVED_PASS synthetic fixture is real capability authority.

## Final verification and branch publication

- [ ] Invoke superpowers:verification-before-completion and independently verify:

1. exactly one real adapter is registered;
2. the registered instance is unprovisioned and preflight-ineligible;
3. every complete future descriptor observation has a direct: method and exact matrix record;
4. descriptor mutation after a future P1 is impossible through invoke;
5. real provider request count is zero;
6. ANTHROPIC_API_KEY presence alone cannot invoke;
7. no SDK/proxy/retry/streaming/provider fallback exists;
8. historical v1.0 evidence remains byte-identical;
9. Product Definition, M6, semantic-review, v0.4.3, oracle, counters, contracts, four-role request, and output schemas are unchanged;
10. origin/main remains ab95074704af0e93248d56344d6a220dfec88a93.

- [ ] Run a fresh final whole-branch review against c1c06dca65ae007cb59353a75788eaf2096bd219.

Give the reviewer the approved design, this complete plan, git diff c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD, the full changed-file manifest, every Task review result, all final test outputs, both audit JSON readbacks, and frozen-boundary output. Require separate architecture, security/privacy, evidence-truthfulness, offline/network, compatibility, and test-coverage findings. Fix every Critical and Important finding in separate commits, rerun its exact failing regression plus every Task 8 verification command, and repeat final review until Critical = 0 and Important = 0.

- [ ] Run final Git readback:

~~~powershell
git fetch origin
git status --short
git diff --check
git diff --name-status c1c06dca65ae007cb59353a75788eaf2096bd219..HEAD
git rev-parse HEAD
git rev-parse HEAD^{tree}
git rev-parse origin/main
~~~

Expected: clean worktree, diff check empty, only the planned provider/tests/audit/evidence files changed, and origin/main unchanged.

- [ ] Use superpowers:finishing-a-development-branch only to verify and publish the implementation branch:

~~~powershell
git push -u origin codex/post-m6-real-backend-capability-enablement
git fetch origin
if ((git rev-parse origin/codex/post-m6-real-backend-capability-enablement) -ne (git rev-parse HEAD)) { throw "remote implementation branch mismatch" }
if ((git rev-parse origin/main) -ne "ab95074704af0e93248d56344d6a220dfec88a93") { throw "main moved" }
~~~

Do not create a PR, merge, tag, push main, provision an account, or begin P1/P2.

## Implementation commit sequence

Preserve these eight GREEN commits in order, with separate review-fix commits when required:

1. feat: add anthropic request projection
2. feat: bind anthropic preflight admission evidence
3. feat: add one-request anthropic https transport
4. feat: bind anthropic provider responses
5. feat: register anthropic backend candidate
6. test: evolve real backend capability audit
7. test: harden anthropic adapter offline boundaries
8. test: audit anthropic backend implementation

## Definition of Done

All conditions are conjunctive:

- Every Task's controlled RED/GREEN evidence is recorded; no import or collection error counts as RED.
- All six new Anthropic test modules and all existing runner tests pass with no skip.
- All listed semantic-review/1.0, semantic-review/2.1, M6, runtime, legacy, and full repository regressions pass.
- The historical M6 fixture uses the exact commit/tree and is removed without force after readback.
- git diff --check passes.
- The interface compatibility table remains true; no generic runner interface or REQUIRED_CAPABILITIES change occurs.
- Exactly 17 admission observations exist, with exact order, closed hash input, direct: methods for complete evidence, and fail-closed missing/contradictory evidence.
- The registered production adapter count is 1, but missing provisioning keeps it ineligible and prevents invoke.
- Test transport and custom credential readers force test-double identity and cannot establish real authority.
- Application retries are 0, streaming is disabled, one invocation can issue at most one POST, and no real request occurs during implementation.
- No secret or raw workspace ID is present in canonical requests, provider-body hash evidence headers, descriptors, responses, events, receipts, audits, logs, exceptions, or committed fixtures.
- New v1.1 evidence reports implementation truth without changing the historical v1.0 evidence.
- P1/P2, account provisioning, Token Counting, Admin API, semantic calibration, reliability measurement, and v0.4.4 remain unstarted.
- Product Definition, M6, semantic-review/1.0, semantic-review/2.1, v0.4.3, oracle, goldens, thresholds, counters, action/runtime conformance, four-role request contract, and output schemas remain unchanged.
- Independent per-Task reviews and final whole-branch review have Critical = 0 and Important = 0.
- The implementation branch is pushed only after all gates pass; main remains unchanged.

## Plan self-review

| Check | Result |
| --- | --- |
| Every approved design requirement maps to a named Task or the explicit future P1/P2 gate | PASS |
| Preflight Admission Evidence Matrix contains exactly the current 17 capability names | PASS |
| Every capability maps to a producer, record/hash input, direct basis, pass/fail conditions, dependencies, and freshness | PASS |
| No descriptor mutation after P1/P2 is proposed | PASS |
| Every new type/function is defined before later use | PASS |
| Production, test, audit, and evidence paths have one responsibility each | PASS |
| No real credential, provider call, token count, provisioning action, calibration, or v0.4.4 work is included | PASS |
| No automatic retry, streaming, SDK, proxy, discovery, router, or fallback is introduced | PASS |
| Fake/injected transport cannot become real capability authority | PASS |
| Historical capability evidence and all frozen semantic/product boundaries remain explicit | PASS |
| Every RED is a controlled assertion failure and every GREEN has exact commands/outcomes | PASS |
| No unresolved implementation marker, unnamed helper, open schema, or unstated command remains | PASS |
| Terminal truth is implemented adapter plus provisioning required, not capability PASS | PASS |

## Completion report boundary

If every implementation and evidence gate passes, report:

~~~text
REAL_BACKEND_ADAPTER_IMPLEMENTED — BACKEND_PROVISIONING_REQUIRED
~~~

Include branch/base/final commit/tree/remote SHA, changed files, per-Task and review-fix commits, exact test counts/skips, full-suite result, admission matrix count, descriptor immutability proof, audit v1.1 readback, historical v1.0 evidence readback, zero provider requests, zero retries, frozen-boundary results, and unchanged main.

Then stop. Do not run P1/P2, provision Anthropic, start calibration, or resume v0.4.4.
