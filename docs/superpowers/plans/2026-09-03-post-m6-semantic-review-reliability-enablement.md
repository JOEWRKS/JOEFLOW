# Post-M6 Semantic Review Reliability Enablement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest controller-owned reviewer runner that can bind exact semantic-review inputs and outputs, prove a stateless tool-free isolation boundary with synthetic evidence, and fail closed while the current runtime has no eligible real backend.

**Architecture:** Add a new `reviewer_runner` sibling package without changing the frozen semantic-review/1.0 or semantic-review/2.1 package/output contracts. The trusted controller constructs one canonical inline request, invokes one narrow bytes-in/bytes-out backend, freezes the single raw response before parsing, binds controller-only run metadata in an immutable receipt, and classifies real capability separately from deterministic fake-backend tests.

**Tech Stack:** Python 3 standard library, immutable dataclasses, JSON, base64, SHA-256 over canonical UTF-8 JSON, `unittest`, filesystem atomic replace, Git read-only source snapshots.

**Spec:** `docs/superpowers/specs/2026-09-03-post-m6-semantic-review-reliability-enablement-design.md`

**Capability audit:** `evals/post-m6-semantic-review-reliability-enablement/ISOLATION_CAPABILITY_AUDIT.md`

## Global Constraints

- Execute from an isolated Git worktree created with `superpowers:using-git-worktrees` from the PM-approved tip of `origin/plan/post-m6-semantic-review-reliability-enablement`.
- The approved design identity is commit `7e2d3f47dfc25341c4e4ff80f16770d95bb03d3d`, tree `ace23621924088fd97bf3a9ca7338eefa96fd092`, based on main `cdc0eb4a972020666f73f7d267a70a1972675054`.
- Implement only Reviewer Runner + Isolation Proof infrastructure. Do not execute a real semantic reviewer, C1/C2/C3, a golden case, oracle scoring, or a reliability gate.
- Do not create or infer semantic-review/2.1 golden truth, expected rationales, calibration authority, compatibility mapping, or reliability thresholds.
- Do not modify Product Definition schema `0.2.0`, Revision 2 authority, approval/Closure semantics, product/UX coverage, M6 outputs, `joewrks.action-conformance/2.1`, runtime-conformance semantics, semantic-review/1.0 semantics, semantic-review/2.1 semantics, either verdict vocabulary, the v0.4.3 corpus/oracle/thresholds, or historical calibration evidence.
- Preserve `semantic-review/2.1 reliability = NOT_MEASURED` and `v0.4.4 = BLOCKED`.
- The only primary backend kind is `STATELESS_TOOLLESS_EXTERNAL_INFERENCE`. Do not add a provider plug-in framework or select OpenAI, Anthropic, Gemini, Azure, Codex Cloud, a local model, or another provider without separately observed eligibility evidence.
- Current planning-time capability is `ISOLATION_CAPABILITY_UNAVAILABLE`: no eligible adapter or endpoint is installed/proven, Docker/Podman/nerdctl are absent, and the available local/Codex surfaces do not prove package-only reads.
- A deterministic fake exercises runner logic only. Its receipts must carry `is_test_double = true` and its capability classification can never be `OBSERVED_PASS`.
- Preserve exactly these runner states: `CALIBRATION_NOT_RUN`, `ISOLATION_CAPABILITY_UNAVAILABLE`, `ISOLATION_PREFLIGHT_FAILED`, `PACKAGE_BINDING_MISMATCH`, `REVIEWER_EXECUTION_FAILED`, `REVIEW_OUTPUT_INVALID`, `REVIEW_COMPLETED`. Do not add runner logic for `CALIBRATION_PASS` or `CALIBRATION_FAIL`.
- Capability classification is exactly `OBSERVED_PASS`, `OBSERVED_FAIL`, `UNAVAILABLE`, or `UNTESTED`. Unknown or inferred properties never become `OBSERVED_PASS`.
- One review context receives the complete approved input in one request. Never truncate, summarize, split, retrieve, use RAG, upload by opaque file reference, or continue a prior response.
- The historical v0.4.3 full-package capacity probe is `319,066` package bytes across ten files; test that exact source-payload size and the resulting larger inline request.
- Authentication remains controller-only and never appears in request bytes, response bytes, event records, receipts, logs, or reviewer-visible environment.
- Runner metadata belongs in controller receipts/envelopes. Do not add fields to frozen semantic-review/2.1 output.
- Cleanup may remove only resolved, marker-owned task paths after evidence freeze; it must read back absence, preserve siblings, and prove the repository source snapshot is unchanged.
- No automatic same-context retry is permitted. Transport or validation failure returns one terminal runner state.
- Every task follows RED → GREEN → REFACTOR and commits only a GREEN focused scope.

> Any test invocation that includes `tests.test_downstream_v21_dogfood_replay`, including `python -m unittest discover -s tests -v`, must provision a temporary clean detached worktree at exact M6 checkpoint `d38b0ca04768888c47e658c79f41e1cec0a7a1ce`, verify tree `40749d900b98936cf694b0c96db7897011cddae8`, bind it through `JOEWRKS_M6_PHASE_B_WORKTREE` for that test process, and remove the temporary worktree after execution. Absence of this fixture is an execution-environment failure, not a semantic/product failure.

This fixture rule applies to the starting implementation baseline, the Task 8 v2.1/M6 replay regression, and the final full repository verification. The historical checkpoint is mandatory and remains an independently read-only worktree; do not copy its evidence into the implementation worktree or change the replay test to skip when the environment variable is absent.

---

## Scope and frozen boundary

### Included in this plan

1. Runner identity and immutable receipt.
2. Exact four-role permitted-input inventory and canonical inline request.
3. Narrow stateless tool-free backend protocol and deterministic test fake.
4. Throwaway synthetic isolation preflight with positive, negative, path, event, drift, and capacity checks.
5. Atomic raw-response freeze, single-document parsing, schema validation, binding, and replay defense.
6. Task-owned evidence lifecycle, cleanup, and repository no-mutation checks.
7. Fail-closed controller integration with the existing semantic-review/1.0 and semantic-review/2.1 validators.
8. Synthetic regression, current capability classification, and implementation/capability audit.

### Explicitly separate future gates

1. A PM-frozen semantic-review/2.1 calibration authority or an explicit normative compatibility decision.
2. Real isolated calibration execution.
3. Controller-side oracle loading and scoring after raw-output freeze.
4. Reliability disposition.
5. Any v0.4.4 resume decision.

A completed runner and passing fake-backend suite are not a reliability result.

## Planning-time endpoint capability observation

The planning inspection found no repository adapter for a stateless tool-free inference endpoint and no configured endpoint identity. Environment inspection listed credential-like variable names only, never values; no eligible inference credential/adapter pair was found. `MOORCHEH_API_KEY` was the only provider-shaped name observed, and the repository contains no eligible tool-free inference adapter for it; a retrieval service is not the approved reviewer boundary. Docker, Podman, and nerdctl were absent. WSL executable presence does not reverse the committed audit's disabled/unproven isolation result.

Therefore Task 8 must end with:

~~~text
RUNNER_IMPLEMENTED — REAL_BACKEND_CAPABILITY_UNPROVEN
ISOLATION_CAPABILITY_UNAVAILABLE
CALIBRATION_NOT_RUN
semantic-review/2.1 reliability = NOT_MEASURED
v0.4.4 = BLOCKED
~~~

No provider-specific production adapter is part of this plan.

## File architecture

### New production files

| Path | Single responsibility |
| --- | --- |
| `skills/joewrks-product-definition/reviewer_runner/__init__.py` | Export the deliberately narrow public runner API. |
| `skills/joewrks-product-definition/reviewer_runner/identity.py` | Canonical hashes, enums, immutable run/backend/input/response identities, receipt construction and validation. |
| `skills/joewrks-product-definition/reviewer_runner/schemas/reviewer-runner-receipt-v1.schema.json` | Exact persisted receipt shape; controller metadata only. |
| `skills/joewrks-product-definition/reviewer_runner/request.py` | Exact four-role inventory validation and canonical inline request bytes. |
| `skills/joewrks-product-definition/reviewer_runner/backend.py` | One bytes-in/bytes-out backend protocol, descriptor, response metadata, and transport errors; no provider implementation. |
| `skills/joewrks-product-definition/reviewer_runner/preflight.py` | Synthetic canary probe, capability observation validation, freshness binding, and eligibility classification. |
| `skills/joewrks-product-definition/reviewer_runner/response.py` | Atomic raw response freeze, one-JSON-document parsing, output validation callback, response/run/backend binding, and replay checks. |
| `skills/joewrks-product-definition/reviewer_runner/evidence.py` | Source snapshots, task-workspace ownership, atomic evidence writes, exact cleanup, and no-mutation readback. |
| `skills/joewrks-product-definition/reviewer_runner/semantic_review.py` | Two explicit adapters to existing semantic-review/1.0 and /2.1 validators; no verdict translation or scoring. |
| `skills/joewrks-product-definition/reviewer_runner/controller.py` | Ordered fail-closed orchestration from source check through receipt freeze and cleanup. |
| `skills/joewrks-product-definition/scripts/audit_reviewer_runner.py` | Read-only registered-backend inventory and deterministic capability disposition output. |

### New tests and test-only support

| Path | Responsibility |
| --- | --- |
| `tests/reviewer_runner_support.py` | Deterministic fake backend and synthetic bytes/metadata factories; always `is_test_double = true`. |
| `tests/test_reviewer_runner_identity.py` | Receipt determinism, exact fields, hash drift, and identity mismatch tests. |
| `tests/test_reviewer_runner_request.py` | Four-role inventory, controller-only exclusion, inline bytes, and no-splitting tests. |
| `tests/test_reviewer_runner_backend.py` | Protocol surface, one invocation/response, metadata, error, and fake non-authority tests. |
| `tests/test_reviewer_runner_preflight.py` | Positive/negative canaries, path inertness, forbidden events/state, drift, and capacity tests. |
| `tests/test_reviewer_runner_response.py` | Freeze-before-parse, malformed/duplicate output, binding drift, and replay tests. |
| `tests/test_reviewer_runner_evidence.py` | Marker ownership, exact cleanup, evidence survival, sibling safety, and repository snapshot tests. |
| `tests/test_reviewer_runner_controller.py` | State-machine ordering, no scoring/oracle access, version adapters, and terminal failure tests. |
| `tests/test_reviewer_runner_audit.py` | No-adapter classification, fake exclusion, redaction, and frozen-boundary audit tests. |

### New implementation evidence

| Path | Responsibility |
| --- | --- |
| `evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json` | Deterministic machine-readable implementation and current-runtime capability result. |
| `evals/post-m6-semantic-review-reliability-enablement/RUNNER_IMPLEMENTATION_CAPABILITY_AUDIT.md` | Human-readable read-only audit that distinguishes runner correctness from real isolation proof. |

### Existing files read but never modified

- `skills/joewrks-product-definition/downstream/semantic_review/**`
- `skills/joewrks-product-definition/downstream/schemas/semantic-review-*.json`
- `skills/joewrks-product-definition/downstream_v21/semantic_review/**`
- `skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-*-v21.schema.json`
- `evals/semantic-review-v0.4.3/**`
- `product-definition/**`
- current M6 dogfood/runtime evidence

## Shared interfaces

Task 1 defines these immutable values for every later task:

~~~python
RUNNER_CONTRACT_VERSION = "joewrks.reviewer-runner/1.0"
RECEIPT_SCHEMA_VERSION = "joewrks.reviewer-runner-receipt/1.0"

class RunnerState(str, Enum):
    CALIBRATION_NOT_RUN = "CALIBRATION_NOT_RUN"
    ISOLATION_CAPABILITY_UNAVAILABLE = "ISOLATION_CAPABILITY_UNAVAILABLE"
    ISOLATION_PREFLIGHT_FAILED = "ISOLATION_PREFLIGHT_FAILED"
    PACKAGE_BINDING_MISMATCH = "PACKAGE_BINDING_MISMATCH"
    REVIEWER_EXECUTION_FAILED = "REVIEWER_EXECUTION_FAILED"
    REVIEW_OUTPUT_INVALID = "REVIEW_OUTPUT_INVALID"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"

class CapabilityClass(str, Enum):
    OBSERVED_PASS = "OBSERVED_PASS"
    OBSERVED_FAIL = "OBSERVED_FAIL"
    UNAVAILABLE = "UNAVAILABLE"
    UNTESTED = "UNTESTED"

@dataclass(frozen=True)
class RunIdentity:
    semantic_review_contract_version: str
    package_schema_version: str
    package_digest: str
    source_action_contract_hash: str
    source_definition_digest: str | None
    reviewer_id: str
    review_run_id: str
    context_id: str
    cohort_id: str | None
    case_id: str | None

@dataclass(frozen=True)
class BackendIdentity:
    backend_kind: str
    adapter_id: str
    adapter_version: str
    endpoint_identity: str
    deployment_identity: str
    model_revision_identity: str
    model_identity_stability: str
    inference_settings_sha256: str
    retention_policy_identity: str
    privacy_policy_identity: str
    is_test_double: bool

@dataclass(frozen=True)
class InputCommitment:
    logical_role: str
    media_type: str
    byte_count: int
    sha256: str

@dataclass(frozen=True)
class ResponseIdentity:
    provider_request_id: str
    request_sha256: str
    reviewer_id: str
    review_run_id: str
    context_id: str
    backend_identity_sha256: str
    response_count: int
    raw_response_byte_count: int
    raw_response_sha256: str
    parsed_output_sha256: str

@dataclass(frozen=True)
class RunnerReceipt:
    state: RunnerState
    run_identity: RunIdentity
    backend_identity: BackendIdentity
    permitted_input_inventory: tuple[InputCommitment, ...]
    request_sha256: str
    capability_preflight_sha256: str
    isolation_receipt_sha256: str
    response_identity: ResponseIdentity
    receipt_sha256: str
~~~

Task 2 defines:

~~~python
@dataclass(frozen=True)
class InputArtifact:
    logical_role: str
    media_type: str
    content: bytes

@dataclass(frozen=True)
class CanonicalRequest:
    content: bytes
    sha256: str
    inventory: tuple[InputCommitment, ...]

def build_canonical_request(
    run_identity: RunIdentity,
    artifacts: Sequence[InputArtifact],
    *,
    controller_only_hashes: Mapping[str, str],
) -> CanonicalRequest:
    ...
~~~

The four and only four `logical_role` values are `reviewer_brief`, `review_package`, `run_envelope`, and `output_schema`. Each appears exactly once. Contents are inline base64 in canonical JSON; no path, URI, file ID, retrieval handle, provider option, or arbitrary metadata field exists.

Task 3 defines:

~~~python
@dataclass(frozen=True)
class CapabilityObservation:
    capability: str
    classification: CapabilityClass
    method: str
    evidence_sha256: str

@dataclass(frozen=True)
class BackendDescriptor:
    identity: BackendIdentity
    max_request_bytes: int
    observations: tuple[CapabilityObservation, ...]

@dataclass(frozen=True)
class BackendEvent:
    kind: str
    metadata_sha256: str

@dataclass(frozen=True)
class BackendResponse:
    raw_bytes: bytes
    provider_request_id: str
    request_sha256: str
    reviewer_id: str
    review_run_id: str
    context_id: str
    backend_identity_sha256: str
    response_count: int
    continuation_id: None
    previous_response_id: None
    events: tuple[BackendEvent, ...]

class ToollessInferenceBackend(Protocol):
    def describe(self) -> BackendDescriptor:
        ...

    def invoke(
        self,
        request_bytes: bytes,
        *,
        timeout_seconds: int,
    ) -> BackendResponse:
        ...
~~~

The protocol deliberately has no tool list, repository path, environment, retrieval index, attachment/file reference, continuation, conversation, sibling input, prior output, or oracle parameter.

Task 4 defines:

~~~python
@dataclass(frozen=True)
class PreflightResult:
    classification: CapabilityClass
    backend_identity_sha256: str
    freshness_sha256: str
    request_sha256: str
    response_sha256: str | None
    required_package_bytes: int
    actual_request_bytes: int
    observations: tuple[CapabilityObservation, ...]
    forbidden_canary_hashes: tuple[str, ...]
    evidence_sha256: str

@dataclass(frozen=True)
class PreflightFreshness:
    backend_identity_sha256: str
    runner_code_sha256: str
    request_schema_sha256: str
    capability_policy_sha256: str
    operating_environment_sha256: str

@dataclass(frozen=True)
class IsolationReceipt:
    classification: CapabilityClass
    preflight_evidence_sha256: str
    freshness_sha256: str
    backend_identity_sha256: str
    request_sha256: str
    receipt_sha256: str

def run_isolation_preflight(
    backend: ToollessInferenceBackend | None,
    *,
    freshness: PreflightFreshness,
    nonce_source: Callable[[str], bytes],
    required_package_bytes: int = 319_066,
    timeout_seconds: int = 60,
) -> PreflightResult:
    ...

def build_per_run_isolation_receipt(
    preflight: PreflightResult,
    *,
    current_freshness: PreflightFreshness,
    backend_identity: BackendIdentity,
    request_sha256: str,
) -> IsolationReceipt:
    ...
~~~

Task 5 defines:

~~~python
@dataclass(frozen=True)
class FrozenResponse:
    path: Path
    byte_count: int
    sha256: str

@dataclass(frozen=True)
class BoundResponse:
    frozen: FrozenResponse
    parsed: dict[str, object]
    identity: ResponseIdentity

OutputValidator = Callable[[dict[str, object]], None]

def freeze_validate_bind_response(
    response: BackendResponse,
    *,
    expected_run: RunIdentity,
    expected_backend: BackendIdentity,
    expected_request_sha256: str,
    evidence_root: Path,
    output_validator: OutputValidator,
    used_provider_request_ids: AbstractSet[str],
) -> BoundResponse:
    ...
~~~

Task 6 defines:

~~~python
@dataclass(frozen=True)
class SourceSnapshot:
    head_sha: str
    tree_sha: str
    status_sha256: str
    clean: bool

@dataclass(frozen=True)
class CleanupResult:
    removed_paths: tuple[str, ...]
    missing_after_cleanup: tuple[str, ...]
    sibling_paths_unchanged: tuple[str, ...]
    source_snapshot_unchanged: bool
    cleanup_sha256: str

class TaskWorkspace:
    @classmethod
    def create(cls, transient_parent: Path, review_run_id: str) -> "TaskWorkspace":
        ...

    def cleanup(
        self,
        *,
        preserved_evidence_paths: Sequence[Path],
        sibling_paths: Sequence[Path],
    ) -> CleanupResult:
        ...
~~~

Task 7 defines:

~~~python
@dataclass(frozen=True)
class PreparedReview:
    run_identity: RunIdentity
    artifacts: tuple[InputArtifact, ...]
    controller_only_hashes: tuple[tuple[str, str], ...]
    output_validator: OutputValidator

@dataclass(frozen=True)
class RunOutcome:
    state: RunnerState
    capability_classification: CapabilityClass
    execution_mode: str
    receipt_path: Path | None
    raw_response_path: Path | None
    errors: tuple[str, ...]

def prepare_semantic_review_v1(
    *,
    verified_package: dict[str, object],
    package_archive_bytes: bytes,
    reviewer_brief_bytes: bytes,
    run_envelope: dict[str, object],
    output_schema_bytes: bytes,
    run_identity: RunIdentity,
) -> PreparedReview:
    ...

def prepare_semantic_review_v21(
    *,
    package: dict[str, object],
    package_bytes: bytes,
    reviewer_brief_bytes: bytes,
    run_envelope_bytes: bytes,
    output_schema_bytes: bytes,
    run_identity: RunIdentity,
) -> PreparedReview:
    ...

def execute_review(
    prepared: PreparedReview,
    *,
    backend: ToollessInferenceBackend | None,
    preflight: PreflightResult,
    current_freshness: PreflightFreshness,
    evidence_root: Path,
    transient_parent: Path,
    repository_root: Path,
    timeout_seconds: int = 60,
    execution_mode: str = "REAL_REVIEW",
) -> RunOutcome:
    ...
~~~

`REAL_REVIEW` requires `OBSERVED_PASS` and `is_test_double = false` before request transmission. `SYNTHETIC_TEST` may use the deterministic fake, but its outcome remains `UNTESTED` and cannot update reliability or capability authority.

---

### Task 1: Runner identity and immutable receipt contract

**Files:**
- Create: `skills/joewrks-product-definition/reviewer_runner/identity.py`
- Create: `skills/joewrks-product-definition/reviewer_runner/schemas/reviewer-runner-receipt-v1.schema.json`
- Create: `tests/test_reviewer_runner_identity.py`

**Interfaces:**
- Consumes: Python standard-library `dataclasses`, `enum`, `hashlib`, and `json` only.
- Produces: every identity, enum, hash helper, receipt builder, and receipt validator listed in “Shared interfaces”.

- [ ] **Step 1: Write the eight failing identity tests**

Create `ReviewerRunnerIdentityTests` with these methods:

1. `test_receipt_is_canonical_and_deterministic`
2. `test_receipt_schema_rejects_missing_or_extra_field`
3. `test_package_digest_mismatch_is_rejected`
4. `test_brief_and_output_schema_digest_mismatch_are_rejected`
5. `test_backend_model_and_settings_identity_mismatch_are_rejected`
6. `test_reviewer_run_context_cohort_and_case_mismatch_are_rejected`
7. `test_wrong_semantic_review_contract_version_is_rejected`
8. `test_floating_model_name_cannot_be_promoted_to_immutable_identity`

Use this determinism assertion:

~~~python
first = build_runner_receipt(**valid_receipt_parts())
second = build_runner_receipt(**valid_receipt_parts())
self.assertEqual(receipt_document(first), receipt_document(second))
self.assertEqual(
    first.receipt_sha256,
    sha256_bytes(canonical_json_bytes(receipt_content(first))),
)
~~~

Mutations must rebuild the enclosing dataclass with `dataclasses.replace` and assert `RunnerIdentityError.code` equals the exact failing field code, such as `PACKAGE_DIGEST_MISMATCH` or `MODEL_IDENTITY_MISMATCH`.

- [ ] **Step 2: Run the identity tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_identity -v
~~~

Expected: import failure because `reviewer_runner.identity` does not exist; zero tests falsely reported as passing.

- [ ] **Step 3: Implement canonical primitives and exact enums**

Implement:

~~~python
def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
~~~

Define the seven-state and four-class enums exactly as shown in “Shared interfaces”. `RunnerIdentityError` carries a stable `code` and message. Validate all SHA-256 values as lowercase 64-hex. Validate IDs as non-empty strings without leading/trailing whitespace. Require `backend_kind == "STATELESS_TOOLLESS_EXTERNAL_INFERENCE"` for non-test backends.

- [ ] **Step 4: Implement receipt content, self-hash, and exact schema**

`receipt_content(receipt)` returns all receipt fields except `receipt_sha256` as JSON-compatible data. `build_runner_receipt(...)` computes the self-hash from that content, freezes tuple fields, then calls `validate_runner_receipt(...)`.

The JSON Schema must set `additionalProperties: false` at every object level and require every field from `RunnerReceipt` and its nested identities. It must constrain:

- all digest fields to `^[0-9a-f]{64}$`;
- `backend_kind` to `STATELESS_TOOLLESS_EXTERNAL_INFERENCE`;
- the seven runner states;
- `model_identity_stability` to `IMMUTABLE`, `STABLE_DEPLOYMENT`, `FLOATING`, or `UNKNOWN`;
- byte counts to non-negative integers;
- `response_count` to `1`;
- input inventory to exactly four unique role records.

Do not make `cohort_id` or `case_id` mandatory strings; they are nullable because runner infrastructure is not calibration aggregation.

- [ ] **Step 5: Run focused GREEN and regression**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_identity -v
python -m unittest tests.test_semantic_review_hashing tests.test_downstream_v21_semantic_review -v
~~~

Expected: `Ran 8 tests ... OK` for the focused module; both existing regression modules `OK`.

- [ ] **Step 6: Refactor and commit**

Keep serialization in `identity.py`; do not introduce a generic serialization package.

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/identity.py skills/joewrks-product-definition/reviewer_runner/schemas/reviewer-runner-receipt-v1.schema.json tests/test_reviewer_runner_identity.py
git commit -m "feat: add reviewer runner receipt identity"
~~~

---

### Task 2: Permitted inventory and canonical inline request

**Files:**
- Create: `skills/joewrks-product-definition/reviewer_runner/request.py`
- Create: `tests/test_reviewer_runner_request.py`

**Interfaces:**
- Consumes: `RunIdentity`, `InputCommitment`, `canonical_json_bytes`, and `sha256_bytes` from Task 1.
- Produces: `InputArtifact`, `CanonicalRequest`, `build_permitted_inventory(...)`, and `build_canonical_request(...)`.

- [ ] **Step 1: Write the eight failing request tests**

Create these methods:

1. `test_exact_four_roles_are_sorted_and_inlined`
2. `test_missing_role_is_rejected`
3. `test_extra_or_duplicate_role_is_rejected`
4. `test_artifact_has_no_path_uri_file_id_or_arbitrary_metadata`
5. `test_controller_only_oracle_sibling_and_prior_hashes_are_rejected`
6. `test_request_has_no_tools_retrieval_environment_or_continuation_fields`
7. `test_request_bytes_are_deterministic_for_unicode_and_binary_payloads`
8. `test_319066_byte_package_is_one_unsplit_inline_artifact`

The last test must create `b"P" * 319_066` as the `review_package` content and assert:

~~~python
request = build_canonical_request(run_identity(), artifacts, controller_only_hashes={})
document = json.loads(request.content)
package = next(item for item in document["inputs"] if item["logical_role"] == "review_package")
self.assertEqual(base64.b64decode(package["content_base64"]), b"P" * 319_066)
self.assertEqual(len([item for item in document["inputs"] if item["logical_role"] == "review_package"]), 1)
self.assertNotIn("chunks", document)
self.assertNotIn("continuation_id", document)
~~~

- [ ] **Step 2: Run request tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_request -v
~~~

Expected: import failure for `reviewer_runner.request`.

- [ ] **Step 3: Implement the exact request document**

Use this closed shape:

~~~json
{
  "request_schema_version": "joewrks.reviewer-runner-request/1.0",
  "runner_contract_version": "joewrks.reviewer-runner/1.0",
  "run_identity": {
    "semantic_review_contract_version": "exact bound value",
    "package_schema_version": "exact bound value",
    "reviewer_id": "exact bound value",
    "review_run_id": "exact bound value",
    "context_id": "exact bound value"
  },
  "inputs": [
    {
      "logical_role": "one of four closed roles",
      "media_type": "exact media type",
      "byte_count": 0,
      "sha256": "lowercase SHA-256",
      "content_base64": "inline exact bytes"
    }
  ],
  "response_contract": {
    "logical_response_count": 1,
    "media_type": "application/json"
  }
}
~~~

The actual document contains all four sorted input records. `package_digest` and source hashes remain in the controller receipt and the package/run-envelope bytes; do not duplicate semantic authority into an editable instruction field.

Reject if:

- the role set differs from the four allowed roles;
- any content hash equals a value in `controller_only_hashes`, whose keys are evidence labels only and are never serialized;
- any dataclass field or serialized key is outside the closed shape;
- base64 round-trip differs;
- JSON canonicalization or byte count fails.

The builder receives bytes, never `Path`. This is the enforcement that Windows, Unix, UNC, traversal, symlink, and junction-looking strings remain inert payload data.

- [ ] **Step 4: Run focused GREEN and inventory regression**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_request -v
python -m unittest tests.test_semantic_review_package tests.test_semantic_review_calibration_corpus -v
~~~

Expected: `Ran 8 tests ... OK`; existing package and corpus modules `OK`.

- [ ] **Step 5: Refactor and commit**

Keep role validation and request serialization in one module; do not add a package archive framework.

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/request.py tests/test_reviewer_runner_request.py
git commit -m "feat: build canonical reviewer requests"
~~~

---

### Task 3: Narrow tool-free backend boundary and deterministic fake

**Files:**
- Create: `skills/joewrks-product-definition/reviewer_runner/backend.py`
- Create: `tests/reviewer_runner_support.py`
- Create: `tests/test_reviewer_runner_backend.py`

**Interfaces:**
- Consumes: `BackendIdentity`, `CapabilityClass`, `canonical_json_bytes`, and `sha256_bytes`.
- Produces: `CapabilityObservation`, `BackendDescriptor`, `BackendEvent`, `BackendResponse`, `ToollessInferenceBackend`, and `BackendInvocationError`.

- [ ] **Step 1: Write the seven failing backend-boundary tests**

Create these methods:

1. `test_protocol_exposes_only_describe_and_bytes_invoke`
2. `test_fake_receives_one_exact_request_and_returns_one_raw_response`
3. `test_response_binds_request_run_context_reviewer_and_backend_identity`
4. `test_no_tool_path_environment_retrieval_or_file_reference_parameter_exists`
5. `test_no_continuation_or_previous_response_identifier_is_accepted`
6. `test_transport_timeout_and_cancellation_use_backend_invocation_error`
7. `test_deterministic_fake_is_always_non_authoritative`

Use `inspect.signature(ToollessInferenceBackend.invoke)` to assert the only call inputs are `self`, `request_bytes`, and keyword-only `timeout_seconds`.

- [ ] **Step 2: Run backend tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_backend -v
~~~

Expected: import failure for `reviewer_runner.backend`.

- [ ] **Step 3: Implement the protocol and closed metadata**

Define the dataclasses exactly as in “Shared interfaces”. `BackendInvocationError.code` is one of `TRANSPORT_ERROR`, `TIMEOUT`, `CANCELLED`, or `NO_RESPONSE`.

The required capability names in `BackendDescriptor.observations` are:

~~~python
REQUIRED_CAPABILITIES = (
    "stateless_fresh_request",
    "no_continuation_id",
    "no_reviewer_memory",
    "no_tools",
    "no_retrieval",
    "no_web_or_browser",
    "no_connectors_or_mcp",
    "no_host_filesystem",
    "no_code_execution",
    "no_file_by_reference",
    "immutable_model_or_deployment_identity",
    "immutable_inference_settings",
    "sufficient_payload_capacity",
    "exact_structured_output",
    "controller_only_authentication",
    "accepted_retention_and_privacy",
    "request_response_commitments",
)
~~~

Every observation has a non-empty method and a hash of its evidence record. A friendly model alias with `model_identity_stability = "FLOATING"` or `UNKNOWN` cannot be eligible, even if the alias string itself is hashed.

- [ ] **Step 4: Implement the test-only fake**

`DeterministicFakeBackend` lives only in `tests/reviewer_runner_support.py`. It accepts a precomputed raw JSON response and optional scripted error/events/metadata drift. Its descriptor must always contain `identity.is_test_double = True`. It records received request bytes for assertions but provides no filesystem, shell, retrieval, network, or provider behavior.

- [ ] **Step 5: Run focused GREEN and backend-free regressions**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_backend -v
python -m unittest tests.test_semantic_review_output tests.test_downstream_v21_semantic_review -v
~~~

Expected: `Ran 7 tests ... OK`; both existing semantic output modules `OK`.

- [ ] **Step 6: Refactor and commit**

Do not add a backend registry or provider subclass.

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/backend.py tests/reviewer_runner_support.py tests/test_reviewer_runner_backend.py
git commit -m "feat: define tool-free inference boundary"
~~~

---

### Task 4: Synthetic isolation preflight and adversarial canaries

**Files:**
- Create: `skills/joewrks-product-definition/reviewer_runner/preflight.py`
- Create: `tests/test_reviewer_runner_preflight.py`
- Modify: `tests/reviewer_runner_support.py`

**Interfaces:**
- Consumes: Task 1 capability/identity primitives, Task 2 canonical request builder, and Task 3 backend protocol/response.
- Produces: `PreflightFreshness`, `PreflightResult`, `IsolationReceipt`, `build_preflight_freshness(...)`, `run_isolation_preflight(...)`, `validate_preflight_freshness(...)`, `classify_backend_eligibility(...)`, and `build_per_run_isolation_receipt(...)`.

- [ ] **Step 1: Write the ten failing preflight tests**

Create these methods:

1. `test_positive_probe_returns_exact_allowed_nonce_once`
2. `test_each_forbidden_canary_family_fails_if_leaked`
3. `test_windows_unix_unc_traversal_git_symlink_and_junction_strings_are_inert`
4. `test_tool_or_retrieval_event_fails_preflight`
5. `test_continuation_or_previous_response_id_fails_preflight`
6. `test_unknown_or_inferred_capability_never_passes`
7. `test_backend_model_settings_or_policy_drift_invalidates_preflight`
8. `test_exact_319066_package_capacity_is_sent_without_split`
9. `test_package_too_large_fails_before_semantic_execution`
10. `test_fake_success_remains_untested_and_no_backend_is_unavailable`

The forbidden canary subtests must cover:

- repository-only;
- `.git`/history;
- golden/oracle;
- evaluator-only;
- sibling package;
- sibling output;
- prior output;
- environment-only;
- parent/common-temp.

The path-string subtests must include:

~~~python
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
~~~

Assert those strings survive as payload text and that no resolver callback, file event, tool event, or retrieval event exists. Do not assert that reviewer silence alone proves denial.

- [ ] **Step 2: Run preflight tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_preflight -v
~~~

Expected: import failure for `reviewer_runner.preflight`.

- [ ] **Step 3: Implement canary construction and the synthetic schema**

Generate independent 256-bit values through the injected `nonce_source(label)`. Production default uses `secrets.token_bytes(32)`. Only the allowed package/brief nonce enters the request. Persist only forbidden nonce hashes in `PreflightResult`.

The synthetic response schema is closed:

~~~json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["probe_schema_version", "allowed_nonce", "response_count"],
  "properties": {
    "probe_schema_version": {
      "const": "joewrks.throwaway-isolation-probe/1.0"
    },
    "allowed_nonce": {
      "type": "string"
    },
    "response_count": {
      "const": 1
    }
  }
}
~~~

The synthetic `review_package` content must be padded to exactly `319_066` bytes before canonical request construction. Record both `required_package_bytes` and `actual_request_bytes`.

- [ ] **Step 4: Implement classification and freshness**

`OBSERVED_PASS` requires all 17 capability names from Task 3 to be present exactly once as `OBSERVED_PASS`, a non-test backend, immutable/stable deployment identity, exact backend identity before/after invocation, one response, no forbidden event, no continuation IDs, allowed nonce equality, no forbidden nonce in response/event evidence, and adequate actual payload admission.

`OBSERVED_FAIL` means an invoked non-test backend produced direct contrary evidence. `UNAVAILABLE` means no backend/adapter or an identity/capacity prerequisite is absent before invocation. `UNTESTED` covers a fake or a real property not observed. Never promote `UNTESTED` through aggregate success.

`build_preflight_freshness(...)` hashes the exact backend identity; all runner `.py` files in sorted relative-path order; the fixed request shape; the sorted 17-capability policy including tool, memory, and retention observations; and safe operating-system/runtime identifiers that contain no environment values or credentials. `validate_preflight_freshness(...)` compares that canonical `PreflightFreshness` to `preflight.freshness_sha256`. Any endpoint, deployment, model revision, settings, runner code, request schema, tool/memory/retention policy, or operating-environment difference returns `ISOLATION_PREFLIGHT_FAILED` before semantic bytes are sent.

`build_per_run_isolation_receipt(...)` revalidates freshness and commits the exact preflight evidence, backend identity, and canonical request hash. Its self-hash becomes `RunnerReceipt.isolation_receipt_sha256`; the full synthetic proof's `evidence_sha256` becomes `RunnerReceipt.capability_preflight_sha256`.

- [ ] **Step 5: Run focused GREEN and adversarial regression**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_preflight -v
python -m unittest tests.test_reviewer_runner_backend tests.test_reviewer_runner_request tests.test_reviewer_runner_identity -v
~~~

Expected: `Ran 10 tests ... OK`; all earlier runner modules `OK`.

- [ ] **Step 6: Refactor and commit**

Keep canaries synthetic and product-neutral. No Product Definition or golden fixture may be imported.

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/preflight.py tests/reviewer_runner_support.py tests/test_reviewer_runner_preflight.py
git commit -m "feat: add synthetic isolation preflight"
~~~

---

### Task 5: Raw response freeze, validation, binding, and replay defense

**Files:**
- Create: `skills/joewrks-product-definition/reviewer_runner/response.py`
- Create: `tests/test_reviewer_runner_response.py`

**Interfaces:**
- Consumes: `RunIdentity`, `BackendIdentity`, `ResponseIdentity`, `BackendResponse`, canonical hashing, and an `OutputValidator` callback.
- Produces: `FrozenResponse`, `BoundResponse`, `atomic_freeze_raw_response(...)`, `parse_single_json_document(...)`, and `freeze_validate_bind_response(...)`.

- [ ] **Step 1: Write the ten failing response tests**

Create these methods:

1. `test_raw_bytes_are_atomically_frozen_before_parser_or_validator_runs`
2. `test_malformed_and_truncated_json_are_review_output_invalid`
3. `test_duplicate_or_extra_json_document_is_rejected`
4. `test_schema_invalid_output_is_rejected_without_scoring`
5. `test_package_contract_reviewer_run_and_context_mismatch_are_rejected`
6. `test_model_deployment_settings_or_request_metadata_mismatch_is_rejected`
7. `test_modified_frozen_bytes_fail_readback_hash`
8. `test_provider_request_id_replay_across_runs_is_rejected`
9. `test_missing_or_multiple_response_count_is_rejected`
10. `test_identical_semantic_bytes_from_distinct_provider_requests_are_not_false_replay`

The freeze-order test uses a validator closure:

~~~python
def validator(parsed):
    self.assertTrue(expected_raw_path.is_file())
    self.assertEqual(expected_raw_path.read_bytes(), raw_bytes)
    self.assertEqual(parsed["status"], "synthetic-ok")
~~~

The replay test must reject a reused `provider_request_id` or mismatched request/run/context metadata. It must not reject independently returned identical JSON bytes when provider request IDs and bound invocation identities differ.

- [ ] **Step 2: Run response tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_response -v
~~~

Expected: import failure for `reviewer_runner.response`.

- [ ] **Step 3: Implement atomic freeze before parse**

Write bytes to a unique sibling temporary file opened with exclusive creation, flush and `os.fsync`, then `os.replace` it to:

~~~text
<evidence_root>/runs/<review_run_id>/<context_id>/raw-response.json
~~~

Resolve and verify the target remains under the exact evidence root. Read the final bytes back and compare byte count and SHA-256 before invoking `json.JSONDecoder.raw_decode`. Reject non-whitespace trailing bytes, a second JSON document, non-object JSON, invalid UTF-8, malformed JSON, and truncated JSON as `REVIEW_OUTPUT_INVALID`.

- [ ] **Step 4: Implement exact response and replay binding**

Before the output validator runs, compare `BackendResponse` metadata to:

- request SHA-256;
- reviewer, run, and context IDs;
- canonical backend identity SHA-256;
- response count exactly one;
- continuation and previous-response IDs exactly `None`;
- event kinds exactly one `RESPONSE` and no `TOOL`, `RETRIEVAL`, `FILE`, `WEB`, `CODE_EXECUTION`, or extra response event;
- provider request ID absent from the frozen receipt index.

Then call the version adapter's output validator on the parsed object. Record `parsed_output_sha256` from canonical parsed JSON, while `raw_response_sha256` always covers exact returned bytes.

- [ ] **Step 5: Run focused GREEN and semantic-output regression**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_response -v
python -m unittest tests.test_semantic_review_output tests.test_downstream_v21_semantic_review -v
~~~

Expected: `Ran 10 tests ... OK`; existing semantic output modules `OK`.

- [ ] **Step 6: Refactor and commit**

Do not parse before freeze and do not normalize raw response bytes in place.

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/response.py tests/test_reviewer_runner_response.py
git commit -m "feat: freeze and bind reviewer responses"
~~~

---

### Task 6: Evidence lifecycle, exact cleanup, and source no-mutation guard

**Files:**
- Create: `skills/joewrks-product-definition/reviewer_runner/evidence.py`
- Create: `tests/test_reviewer_runner_evidence.py`

**Interfaces:**
- Consumes: canonical hashes, Task 2 request construction for the next-run leakage assertion, and Task 5 frozen response metadata.
- Produces: `SourceSnapshot`, `CleanupResult`, `TaskWorkspace`, `capture_source_snapshot(...)`, `atomic_freeze_evidence(...)`, `load_used_provider_request_ids(...)`, and `verify_source_unchanged(...)`.

- [ ] **Step 1: Write the eight failing lifecycle tests**

Create these methods:

1. `test_task_workspace_has_unique_owned_marker_and_resolved_paths`
2. `test_evidence_is_frozen_before_transient_package_response_and_canary_cleanup`
3. `test_cleanup_removes_only_exact_task_root_and_reads_back_absence`
4. `test_sibling_root_and_sibling_output_remain_byte_identical`
5. `test_ambiguous_or_mismatched_ownership_blocks_cleanup_and_next_execution`
6. `test_repository_head_tree_and_clean_status_are_unchanged`
7. `test_cleanup_failure_is_terminal_and_preserves_diagnostic_evidence`
8. `test_prior_output_bytes_do_not_enter_the_next_workspace_or_request`

Use a temporary parent with two sibling run roots. Put unique bytes in both and assert cleanup of one leaves the other tree and hashes unchanged.

- [ ] **Step 2: Run lifecycle tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_evidence -v
~~~

Expected: import failure for `reviewer_runner.evidence`.

- [ ] **Step 3: Implement source snapshots and atomic evidence**

`capture_source_snapshot(repository_root)` runs non-shell subprocess argument arrays for:

~~~text
git rev-parse HEAD
git rev-parse HEAD^{tree}
git status --porcelain=v1 -z
~~~

The snapshot records the exact status-bytes hash and requires clean status before `REAL_REVIEW`. `verify_source_unchanged` requires identical head, tree, status hash, and clean flag afterward.

`atomic_freeze_evidence` uses the same exclusive temp/write/fsync/replace/readback rule as raw responses. A pre-existing same path with different bytes is an immutable-evidence conflict; identical bytes are an idempotent readback, not a rewrite.

- [ ] **Step 4: Implement marker-owned cleanup**

`TaskWorkspace.create` makes exactly:

~~~text
<transient_parent>/joewrks-reviewer-runner/<review_run_id>/
  .joewrks-runner-owner.json
  inputs/
  response-working/
  synthetic-canaries/
~~~

The marker binds the resolved root and review-run ID. Cleanup must:

1. verify the marker and resolved descendant boundary;
2. verify every removable path belongs to the task root;
3. freeze diagnostic and receipt evidence first;
4. remove the exact task root;
5. read back that it is absent;
6. re-hash declared sibling paths;
7. verify the repository snapshot;
8. return deterministic `CleanupResult`.

Never delete the transient parent, repository root, evidence root, a glob, a symlink/junction target outside the task root, or an ambiguously owned path. Provider retention is recorded in backend eligibility, not claimed by local cleanup.

- [ ] **Step 5: Run focused GREEN and filesystem regression**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_evidence -v
python -m unittest tests.test_reviewer_runner_response tests.test_migration_v020_apply -v
~~~

Expected: `Ran 8 tests ... OK`; raw-response and existing migration filesystem modules `OK`.

- [ ] **Step 6: Refactor and commit**

Keep all destructive filesystem behavior in `evidence.py` and require resolved-path ownership checks before deletion.

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/evidence.py tests/test_reviewer_runner_evidence.py
git commit -m "feat: enforce reviewer evidence cleanup"
~~~

---

### Task 7: Fail-closed controller and existing semantic-review adapters

**Files:**
- Create: `skills/joewrks-product-definition/reviewer_runner/semantic_review.py`
- Create: `skills/joewrks-product-definition/reviewer_runner/controller.py`
- Create: `skills/joewrks-product-definition/reviewer_runner/__init__.py`
- Create: `tests/test_reviewer_runner_controller.py`

**Interfaces:**
- Consumes: all Task 1–6 public interfaces plus the existing v1 `verify_run_envelope` / `validate_review_output` and v2.1 `validate_semantic_review_package_v21` / `validate_semantic_review_output_v21`.
- Produces: `PreparedReview`, `RunOutcome`, the two explicit prepare functions, and `execute_review(...)`.

- [ ] **Step 1: Write the ten failing controller/integration tests**

Create these methods:

1. `test_real_review_without_backend_returns_isolation_capability_unavailable_before_invoke`
2. `test_failed_or_stale_preflight_returns_isolation_preflight_failed_before_semantic_bytes`
3. `test_v1_adapter_delegates_to_existing_envelope_and_output_validators`
4. `test_v21_adapter_delegates_to_existing_package_and_output_validators_without_changing_output_fields`
5. `test_package_binding_error_never_becomes_semantic_verdict`
6. `test_transport_timeout_and_cancellation_return_reviewer_execution_failed_without_retry`
7. `test_malformed_schema_invalid_or_duplicate_output_returns_review_output_invalid_without_scoring`
8. `test_valid_synthetic_test_flow_freezes_raw_response_receipt_and_cleanup_evidence`
9. `test_oracle_goldens_gate_and_reliability_modules_are_never_imported_or_called`
10. `test_fake_backend_cannot_execute_real_review_or_change_not_measured_status`

For v1, use `tests.semantic_review_support.make_run_set(["APPROVED"])` and the exact existing `downstream.semantic_review.output.validate_review_output`. For v2.1, use the synthetic REVIEW_REQUIRED fixture pattern already exercised by `tests.test_downstream_v21_semantic_review` and call the exact v2.1 validators. These are structural integration fixtures, not a golden corpus or a reliability authority.

- [ ] **Step 2: Run controller tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_controller -v
~~~

Expected: import failure for `reviewer_runner.controller` and `reviewer_runner.semantic_review`.

- [ ] **Step 3: Implement explicit version adapters**

`prepare_semantic_review_v1` must:

1. require `run_identity.semantic_review_contract_version == "joewrks.semantic-review/1.0"`;
2. verify the supplied already-loaded package and run envelope with the existing validator;
3. verify `run_identity.package_digest` equals `reviewer_input_package_hash`;
4. build the four input artifacts from exact supplied bytes;
5. return an output validator closure that calls existing `validate_review_output(verified_package, run_envelope, output)`.

`prepare_semantic_review_v21` must:

1. require `run_identity.semantic_review_contract_version == "joewrks.semantic-review/2.1"`;
2. parse `package_bytes` as one UTF-8 JSON object, require the parsed object to equal `package`, and preserve/hash the original bytes without rewriting them;
3. require zero errors from `validate_semantic_review_package_v21(package)`;
4. bind `package_digest` to `package["package_hash"]`, source semantic contract hash, and source definition digest;
5. construct exactly the four input artifacts;
6. return a closure that requires zero errors from `validate_semantic_review_output_v21(package, output)`.

Neither adapter translates verdicts, changes output shape, builds a reviewer brief, creates a 2.1 oracle, scores, or modifies authority.

- [ ] **Step 4: Implement the ordered controller**

Implement this exact order:

~~~python
def execute_review(prepared, *, backend, preflight, evidence_root,
                   current_freshness, transient_parent, repository_root,
                   timeout_seconds=60, execution_mode="REAL_REVIEW"):
    before = capture_source_snapshot(repository_root)
    validate_prepared_review(prepared)
    request = build_canonical_request(
        prepared.run_identity,
        prepared.artifacts,
        controller_only_hashes=dict(prepared.controller_only_hashes),
    )
    descriptor = None if backend is None else backend.describe()
    gate = authorize_execution(execution_mode, descriptor, preflight, request)
    if gate is not None:
        return gate
    isolation = build_per_run_isolation_receipt(
        preflight,
        current_freshness=current_freshness,
        backend_identity=descriptor.identity,
        request_sha256=request.sha256,
    )
    workspace = TaskWorkspace.create(
        transient_parent,
        prepared.run_identity.review_run_id,
    )
    try:
        response = backend.invoke(
            request.content,
            timeout_seconds=timeout_seconds,
        )
        bound = freeze_validate_bind_response(
            response,
            expected_run=prepared.run_identity,
            expected_backend=descriptor.identity,
            expected_request_sha256=request.sha256,
            evidence_root=evidence_root,
            output_validator=prepared.output_validator,
            used_provider_request_ids=load_used_provider_request_ids(evidence_root),
        )
        receipt = build_runner_receipt_from_bound_response(
            prepared, descriptor, preflight, isolation, request, bound
        )
        receipt_path = freeze_receipt(receipt, evidence_root)
        state = RunnerState.REVIEW_COMPLETED
    except BackendInvocationError as error:
        state = RunnerState.REVIEWER_EXECUTION_FAILED
        freeze_failure_evidence(error, evidence_root)
    except ResponseValidationError as error:
        state = error.runner_state
        freeze_failure_evidence(error, evidence_root)
    finally:
        cleanup = workspace.cleanup(
            preserved_evidence_paths=evidence_paths_for_run(evidence_root, prepared),
            sibling_paths=sibling_run_paths(transient_parent, prepared),
        )
        verify_source_unchanged(before, repository_root)
    return build_run_outcome(state, preflight.classification, execution_mode)
~~~

The names called in this body must be the exact Task 1–6 functions. `PreparedReview` includes `controller_only_hashes` even when empty; those hashes are never serialized. If source pre-state is dirty, cleanup ownership is ambiguous, cleanup fails, or source readback changes, stop and return `REVIEWER_EXECUTION_FAILED` without another invocation; if cleanup/source readback fails after a valid response, it replaces `REVIEW_COMPLETED` so no successful run receipt is exposed.

Map failures exactly:

| Failure | Runner state |
| --- | --- |
| no backend/adapter, fake in `REAL_REVIEW`, floating identity, insufficient capacity | `ISOLATION_CAPABILITY_UNAVAILABLE` |
| synthetic/per-run capability evidence fails or drifts | `ISOLATION_PREFLIGHT_FAILED` |
| package/brief/schema/request/run/backend binding mismatch or replay | `PACKAGE_BINDING_MISMATCH` |
| transport, timeout, cancellation, no response | `REVIEWER_EXECUTION_FAILED` |
| invalid UTF-8/JSON, multiple JSON documents, schema/output-validator error | `REVIEW_OUTPUT_INVALID` |
| cleanup ambiguity/failure or repository source drift | `REVIEWER_EXECUTION_FAILED` |
| one frozen, bound, valid output | `REVIEW_COMPLETED` |

Do not import `goldens`, `gate`, `statistics`, `disagreement`, any oracle path, or any Product Definition writer. Add an import-graph/source-token test that fails if those dependencies enter `controller.py` or `semantic_review.py`.

- [ ] **Step 5: Run focused GREEN and semantic contract regressions**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_controller -v
python -m unittest tests.test_semantic_review_package tests.test_semantic_review_output tests.test_semantic_review_gate tests.test_official_calibration_controller tests.test_downstream_v21_semantic_review -v
~~~

Expected: `Ran 10 tests ... OK`; all five existing semantic-review/controller modules `OK`.

- [ ] **Step 6: Run all runner tests**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_identity tests.test_reviewer_runner_request tests.test_reviewer_runner_backend tests.test_reviewer_runner_preflight tests.test_reviewer_runner_response tests.test_reviewer_runner_evidence tests.test_reviewer_runner_controller -v
~~~

Expected: `Ran 61 tests ... OK` with no skip.

- [ ] **Step 7: Refactor and commit**

Keep `controller.py` orchestration-only; keep version-specific structural validation in `semantic_review.py`.

~~~powershell
git add skills/joewrks-product-definition/reviewer_runner/__init__.py skills/joewrks-product-definition/reviewer_runner/semantic_review.py skills/joewrks-product-definition/reviewer_runner/controller.py tests/test_reviewer_runner_controller.py
git commit -m "feat: integrate semantic review runner controller"
~~~

---

### Task 8: Full synthetic regression, capability classification, and implementation audit

**Files:**
- Create: `skills/joewrks-product-definition/scripts/audit_reviewer_runner.py`
- Create: `tests/test_reviewer_runner_audit.py`
- Create: `evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json`
- Create: `evals/post-m6-semantic-review-reliability-enablement/RUNNER_IMPLEMENTATION_CAPABILITY_AUDIT.md`

**Interfaces:**
- Consumes: public `reviewer_runner` exports, current registered production adapters (none), Git source snapshot, and test results supplied as exact audit inputs.
- Produces: deterministic JSON capability evidence and the bounded final implementation/capability verdict.

- [ ] **Step 1: Write the five failing audit tests**

Create these methods:

1. `test_no_registered_real_adapter_reports_unavailable_and_calibration_not_run`
2. `test_fake_backend_is_excluded_from_observed_pass`
3. `test_audit_contains_no_environment_values_or_credentials`
4. `test_audit_preserves_not_measured_v044_block_and_attempt_counters`
5. `test_frozen_product_semantic_review_and_m6_paths_are_unchanged`

The frozen-path test compares blob IDs from the implementation base for:

- `product-definition/**`;
- `skills/joewrks-product-definition/downstream/semantic_review/**`;
- `skills/joewrks-product-definition/downstream_v21/semantic_review/**`;
- semantic-review/1.0 and /2.1 schemas;
- `evals/semantic-review-v0.4.3/**`;
- current M6 evidence paths.

- [ ] **Step 2: Run audit tests and confirm RED**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_audit -v
~~~

Expected: import or missing-script failure because the audit entry point and evidence files do not exist.

- [ ] **Step 3: Implement a read-only deterministic audit command**

After Task 7, freeze the code revision identity without modifying it:

~~~powershell
$runnerCodeRevision = git rev-parse HEAD
python skills/joewrks-product-definition/scripts/audit_reviewer_runner.py --repository . --revision $runnerCodeRevision --json
~~~

It prints one canonical JSON object and writes nothing. The object has:

~~~json
{
  "schema_version": "joewrks.reviewer-runner-capability-audit/1.0",
  "runner_contract_version": "joewrks.reviewer-runner/1.0",
  "implementation_status": "RUNNER_IMPLEMENTED",
  "backend_kind": "STATELESS_TOOLLESS_EXTERNAL_INFERENCE",
  "registered_real_adapter_count": 0,
  "real_backend_capability": "UNAVAILABLE",
  "runner_state": "ISOLATION_CAPABILITY_UNAVAILABLE",
  "calibration_status": "CALIBRATION_NOT_RUN",
  "semantic_review_21_reliability": "NOT_MEASURED",
  "v044_status": "BLOCKED",
  "real_calibration_attempts": 1,
  "valid_real_calibration_runs": 0,
  "fake_backend_authoritative": false,
  "provider_selected": null,
  "implementation_code_commit": "Task-7 GREEN commit supplied by --revision",
  "implementation_code_tree": "tree of the exact --revision commit"
}
~~~

The code may inspect registered adapter objects and environment variable names, but never reads or prints environment values. With no production adapter module in this plan, the real adapter count must be zero.

- [ ] **Step 4: Run all focused tests and generate exact audit evidence**

Run:

~~~powershell
python -m unittest tests.test_reviewer_runner_identity tests.test_reviewer_runner_request tests.test_reviewer_runner_backend tests.test_reviewer_runner_preflight tests.test_reviewer_runner_response tests.test_reviewer_runner_evidence tests.test_reviewer_runner_controller tests.test_reviewer_runner_audit -v
$runnerCodeRevision = git rev-parse HEAD
python skills/joewrks-product-definition/scripts/audit_reviewer_runner.py --repository . --revision $runnerCodeRevision --json
~~~

Expected: `Ran 66 tests ... OK` with no skip. Audit JSON must report `registered_real_adapter_count = 0`, `real_backend_capability = UNAVAILABLE`, `CALIBRATION_NOT_RUN`, `NOT_MEASURED`, and `BLOCKED`.

Freeze that exact JSON as `RUNNER_CAPABILITY_EVIDENCE.json` using canonical UTF-8 JSON plus one newline. Write `RUNNER_IMPLEMENTATION_CAPABILITY_AUDIT.md` with:

- baseline/implementation commit and tree;
- exact modules and tests reviewed;
- deterministic fake results labeled non-authoritative;
- adversarial preflight results;
- capability inventory;
- no-provider-selection statement;
- current real-backend blocker;
- frozen path readback;
- regression/full-suite results and skips;
- final bounded verdict.

Do not record a timestamp in canonical JSON, secrets, credential values, a claimed provider-side deletion, or a real preflight PASS.

- [ ] **Step 5: Run the existing semantic-review/1.0 regression**

Run:

~~~powershell
python -m unittest tests.test_semantic_review_hashing tests.test_semantic_review_responsibility tests.test_semantic_review_package tests.test_semantic_review_output tests.test_semantic_review_goldens tests.test_semantic_review_gate tests.test_semantic_review_statistics tests.test_semantic_review_negative_regressions tests.test_semantic_review_calibration_corpus tests.test_semantic_review_calibration_control_plane tests.test_official_calibration_controller tests.test_semantic_review_human_packet -v
~~~

Expected: all existing semantic-review/1.0 and repaired calibration-controller tests `OK`; no new skip.

- [ ] **Step 6: Run semantic-review/2.1, action-conformance/2.1, M5.1/M6, runtime, and frozen-boundary regression**

Run:

~~~powershell
python -m unittest tests.test_downstream_v21_derivation tests.test_downstream_v21_compiler tests.test_downstream_v21_gap_routing tests.test_downstream_v21_audit tests.test_downstream_v21_semantic_review tests.test_downstream_v21_runtime_plan tests.test_downstream_v21_runtime_evidence tests.test_downstream_v21_dogfood_replay tests.test_downstream_v21_frozen_boundaries tests.test_core_semantic_closure_v2_m6_dogfood_phase_a tests.test_core_semantic_closure_v2_m6_dogfood_phase_b tests.test_m6_runtime_v21_verification tests.test_m6_client_feedback_portal_fixture -v
~~~

Expected: all listed existing 2.1, runtime, M5.1/M6, and frozen-boundary modules `OK`; only an already-documented environment-dependent skip is permitted, and the runner work must add no skip.

- [ ] **Step 7: Run legacy frozen regression and full repository suite**

Run:

~~~powershell
python -m unittest tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
python -m unittest discover -s tests -v
git diff --check
~~~

Expected:

- legacy frozen regression `OK`;
- full repository suite `OK`;
- any skip count and reason exactly recorded in the audit, with no runner-test skip;
- `git diff --check` exits `0` with no output.

- [ ] **Step 8: Perform frozen-boundary and scope readback**

Set the implementation base from the approved planning branch before implementation:

~~~powershell
$implementationBase = git merge-base HEAD origin/plan/post-m6-semantic-review-reliability-enablement
git diff --name-status $implementationBase..HEAD
git diff --exit-code $implementationBase..HEAD -- product-definition
git diff --exit-code $implementationBase..HEAD -- skills/joewrks-product-definition/downstream/semantic_review
git diff --exit-code $implementationBase..HEAD -- skills/joewrks-product-definition/downstream_v21/semantic_review
git diff --exit-code $implementationBase..HEAD -- evals/semantic-review-v0.4.3
git status --short
~~~

Expected:

- only the new runner, runner tests/support, audit script, and new post-M6 audit/evidence paths differ;
- all four frozen diff commands exit `0` with no output;
- Product Definition, M6, v0.4.3, oracle, goldens, thresholds, semantic-review contract files, and main are unchanged;
- worktree is clean after the Task 8 commit.

- [ ] **Step 9: Commit the implementation/capability audit**

~~~powershell
git add skills/joewrks-product-definition/scripts/audit_reviewer_runner.py tests/test_reviewer_runner_audit.py evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json evals/post-m6-semantic-review-reliability-enablement/RUNNER_IMPLEMENTATION_CAPABILITY_AUDIT.md
git commit -m "test: audit semantic review runner capability"
~~~

After the commit, set `$runnerCodeRevision = git rev-parse HEAD^` and rerun the focused audit command with `--revision $runnerCodeRevision`, then rerun the full suite, `git diff --check`, frozen diff commands, and remote/main identity checks before any completion claim. The evidence binds the Task-7 code tree, while the Task-8 commit binds that code identity together with its audit; it does not attempt a self-referential final-commit hash.

---

## Required test-family traceability

| Required family | Exact task/tests |
| --- | --- |
| Canonical receipt determinism | Task 1 `test_receipt_is_canonical_and_deterministic` |
| Package/brief/schema digest mismatch | Task 1 tests 3–4 |
| Model/settings identity mismatch | Task 1 test 5; Task 5 test 6 |
| Reviewer/run/context/cohort/case mismatch | Task 1 test 6; Task 5 test 5 |
| Wrong semantic-review version | Task 1 test 7; Task 7 adapter tests |
| Output replay | Task 5 tests 8 and 10 |
| Missing/extra/unexpected permitted input | Task 2 tests 2–4 |
| Oracle/sibling/prior material excluded | Task 2 test 5; Task 7 import-boundary test |
| Positive allowed nonce | Task 4 test 1 |
| Forbidden canary families | Task 4 test 2 |
| Path-string inertness | Task 4 test 3 |
| Tool/retrieval events | Task 4 test 4 |
| Continuation/previous response | Task 4 test 5 |
| Backend drift | Task 4 test 7 |
| Exact package size/too large | Task 4 tests 8–9 |
| Transport/timeout/cancellation | Task 3 test 6; Task 7 test 6 |
| Malformed/truncated/duplicate/schema-invalid output | Task 5 tests 2–4 and 9 |
| Package/backend metadata mismatch | Task 5 tests 5–6 |
| No scoring on infrastructure failure | Task 7 tests 5–7 and 9 |
| Exact cleanup/evidence/sibling/repository safety | Task 6 tests 2–7 |
| Fake never establishes capability | Task 3 test 7; Task 4 test 10; Task 8 test 2 |

## Implementation commit sequence

The future implementation branch is `feat/post-m6-semantic-review-reliability-runner`. Create it only after PM approves this plan, from the then-current remote tip containing this exact plan. Preserve these eight GREEN commits in order:

1. `feat: add reviewer runner receipt identity`
2. `feat: build canonical reviewer requests`
3. `feat: define tool-free inference boundary`
4. `feat: add synthetic isolation preflight`
5. `feat: freeze and bind reviewer responses`
6. `feat: enforce reviewer evidence cleanup`
7. `feat: integrate semantic review runner controller`
8. `test: audit semantic review runner capability`

Do not squash during implementation review. Do not merge or modify main.

## Definition of Done for this plan's implementation

All conditions are conjunctive:

- 66 new runner tests pass with no skip.
- Every listed semantic-review/1.0, semantic-review/2.1, action-conformance/2.1, M5.1/M6, runtime, legacy, calibration-controller, reliability-gate, and frozen-boundary regression passes.
- Full repository suite passes; only a pre-existing environment-dependent skip may remain and its exact reason is recorded.
- `git diff --check` passes.
- Runner receipt, request, backend, preflight, response, evidence, adapters, and controller implement the exact interfaces in this plan.
- Raw response freeze precedes parse, schema validation, receipt creation, and any future oracle eligibility.
- No oracle or scoring module is reachable from the runner controller.
- Fake backend tests are explicitly non-authoritative.
- No real provider adapter is created or selected.
- Current runtime remains `ISOLATION_CAPABILITY_UNAVAILABLE` until an actual backend earns `OBSERVED_PASS` through synthetic proof.
- No real semantic calibration request is sent.
- `REAL_CALIBRATION_ATTEMPTS = 1` and `VALID_REAL_CALIBRATION_RUNS = 0` remain unchanged.
- semantic-review/2.1 reliability remains `NOT_MEASURED`.
- v0.4.4 remains `BLOCKED`.
- Product Definition, frozen semantic-review contracts, v0.4.3 evidence, goldens/oracle/thresholds, and M6 evidence are byte-identical to the implementation base.
- The implementation branch is pushed only after final read-only audit passes; main is not merged or pushed.

## Plan self-review result

Verdict: `PASS`

| Check | Result |
| --- | --- |
| Every approved design requirement maps to Tasks 1–8 or an explicit future gate | `PASS` |
| Current endpoint absence and `ISOLATION_CAPABILITY_UNAVAILABLE` remain visible | `PASS` |
| File responsibilities are focused and no provider framework is introduced | `PASS` |
| Receipt, request, backend, preflight, response, cleanup, and controller types use consistent names | `PASS` |
| All required negative, adversarial, execution, replay, and cleanup families have named tests | `PASS` |
| Fake-backend evidence cannot become `OBSERVED_PASS` | `PASS` |
| Raw response freeze precedes parsing and any future scoring eligibility | `PASS` |
| semantic-review/1.0 and /2.1 semantics remain unchanged | `PASS` |
| 2.1 calibration authority and real calibration remain separate | `PASS` |
| Product Definition, v0.4.3 evidence, M6 evidence, and v0.4.4 status remain frozen | `PASS` |
| No unresolved implementation marker or unnamed interface remains | `PASS` |

## Post-run report boundary

If every code/test gate passes but no eligible backend exists, report:

~~~text
RUNNER_IMPLEMENTED — REAL_BACKEND_CAPABILITY_UNPROVEN
~~~

with `ISOLATION_CAPABILITY_UNAVAILABLE`, `CALIBRATION_NOT_RUN`, `NOT_MEASURED`, and `v0.4.4 = BLOCKED`. Do not convert implementation success into isolation, calibration, or reliability success.

If a future separately authorized capability task supplies a real adapter, run only the synthetic preflight first. Stop on `OBSERVED_FAIL`, `UNAVAILABLE`, or `UNTESTED`. Even `OBSERVED_PASS` authorizes only the next separately approved 2.1 authority/capability gate; it does not authorize real calibration.
