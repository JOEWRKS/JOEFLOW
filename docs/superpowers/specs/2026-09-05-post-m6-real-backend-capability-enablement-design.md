# Post-M6 Real Backend Capability Enablement — Architecture Design

Status: `READY_FOR_PM_REVIEW`

Date: 2026-09-05

Repository baseline: `ab95074704af0e93248d56344d6a220dfec88a93`

Baseline tree: `867bec6fcfe5f4dc9927beaaf143087178e09e7c`

Planning branch: `plan/post-m6-real-backend-capability-enablement`

Disposition: `RECOMMENDED_PROVIDER_CANDIDATE = Anthropic API`

Current production capability remains: `UNAVAILABLE`

## 1. Context

The Post-M6 Reviewer Runner is implemented on the authoritative baseline. It
already owns request construction, capability preflight, response freezing,
response binding, replay defense, cleanup, receipts, and fail-closed state
transitions. It deliberately has no real provider adapter.

This design selects the smallest credible path from that closed runner boundary
to one real hosted inference endpoint. It is a capability-enablement design,
not a semantic-review calibration design, and it does not create an `M7`.

Phase 0 performed repository inspection, local capability inspection, DNS-only
endpoint discovery, and official-document research. It made no inference call,
created no provider resource, exposed no credential value, and generated no
semantic output.

## 2. Current blocker

The remaining blocker is not runner correctness. It is the absence of a
registered, non-test `ToollessInferenceBackend` whose complete descriptor and
real synthetic execution demonstrate every existing required capability.

The authoritative state therefore remains:

- registered real adapters: `0`;
- real backend capability: `UNAVAILABLE`;
- runner state: `ISOLATION_CAPABILITY_UNAVAILABLE`;
- real reviewer requests: `0`;
- calibration: `CALIBRATION_NOT_RUN`;
- semantic-review/2.1 reliability: `NOT_MEASURED`;
- v0.4.4: `BLOCKED`;
- real calibration attempts / valid runs: `1 / 0`.

A documented provider feature is not execution evidence. A selected provider
and an implemented adapter would still not be capability PASS until the
existing synthetic preflight produces valid, frozen evidence.

## 3. Goals

1. Select one narrow transport architecture and one preferred hosted provider.
2. Preserve the current bytes-in/bytes-out runner interface without a second
   runner or a provider framework.
3. Define deterministic translation from the canonical four-role request to a
   provider request.
4. Bind endpoint, model, generation settings, request, response, and provider
   request identity strongly enough for later evidence to be interpretable.
5. Define controller-only authentication and accepted retention as explicit
   provisioning gates.
6. Define the first product-neutral, charge-bearing capability proof without
   performing it.
7. Keep every missing fact fail-closed.

## 4. Non-goals

This phase does not:

- implement or register any adapter;
- call any inference endpoint or token-count endpoint;
- create an account, workspace, project, API key, deployment, or billing object;
- add a provider registry, router, failover path, gateway, or credentials UI;
- change Reviewer Runner code, tests, schemas, receipts, or capability evidence;
- change Product Definition, M6, semantic-review/1.0, or semantic-review/2.1;
- create calibration authority, packages, cohorts, scores, or thresholds;
- resume v0.4.4;
- claim semantic quality, repeatability, or real isolation capability.

## 5. Existing Reviewer Runner architecture

The existing path is authoritative:

```text
controller
  -> build exact four-role canonical request
  -> verify frozen BackendDescriptor and freshness
  -> run synthetic capability preflight when eligible
  -> ToollessInferenceBackend.invoke(request_bytes, timeout_seconds)
  -> freeze the returned semantic JSON bytes
  -> validate one JSON object and frozen output schema
  -> bind request/run/context/backend/provider-request identities
  -> reject provider-request replay
  -> write receipts and verify cleanup/source immutability
```

`CanonicalRequest` contains exactly these roles, once each, inline as base64:

- `reviewer_brief`;
- `review_package`;
- `run_envelope`;
- `output_schema`.

`BackendDescriptor` binds backend identity, request capacity, and the complete
ordered capability observation set. `BackendResponse` contains exact semantic
output bytes, one provider request ID, request/run/context/backend bindings,
exactly one `RESPONSE` event, and no continuation identifiers.

The future adapter is an implementation of this interface. It is not allowed
to change the interface because a provider SDK or API is more convenient.

## 6. Trust boundaries

### Controller boundary

The controller owns source/package selection, the four canonical input roles,
run identity, evidence paths, backend selection, timeout, credential-source
selection, and used-provider-request-ID history.

### Adapter boundary

The adapter may parse and validate canonical request bytes in memory, create one
deterministic provider wire request, authenticate separately, make one HTTPS
attempt, and translate one provider response into `BackendResponse`. It receives
no repository path, arbitrary tool configuration, conversation identifier,
file handle, or retry policy.

### Provider boundary

The provider sees only the four allowed role contents plus fixed adapter
framing. It receives no local filesystem access, retrieval source, tool,
connector, MCP server, previous response, conversation, or external memory.
Provider retention and safety infrastructure remain external trust surfaces and
must be covered by accepted account evidence.

### Evidence boundary

The runner freezes model output bytes and identity commitments. Credential
bytes, authorization headers, and secret paths are excluded from requests,
events, receipts, logs, tests, and evidence.

## 7. Backend eligibility requirements

The existing `REQUIRED_CAPABILITIES` tuple remains exact. A future real
descriptor is eligible only when all entries have the existing production pass
classification backed by implementation/runtime evidence, the adapter is not a
test double, and model identity stability is `IMMUTABLE` or
`STABLE_DEPLOYMENT`.

Phase 0 uses only the research vocabulary `OBSERVED_LOCAL`, `DOCUMENTED`,
`ACCOUNT_EVIDENCE_REQUIRED`, `UNTESTED`, `UNAVAILABLE`, and `CONTRADICTED`.
It does not pre-award any production capability observation.

Required properties are:

- fresh stateless request, no continuation ID, no reviewer memory;
- no tools, retrieval, web/browser, connectors/MCP, host filesystem, code
  execution, or file-by-reference;
- immutable model/deployment and immutable settings identities;
- sufficient inline payload and output capacity;
- one exact structured semantic output;
- controller-only authentication and accepted retention/privacy;
- exact request/response commitments and unique provider request identity.

Any absent account evidence, floating alias, capacity failure, unexpected
content block, hidden retry, or identity drift keeps the backend ineligible.

## 8. Transport approaches

| Approach | Trust surface | Dependencies | Determinism and retry risk | Complexity | Disposition |
| --- | --- | --- | --- | --- | --- |
| A. Direct provider HTTPS with Python standard library | Adapter, Python TLS stack, provider endpoint | No new package | Highest visibility over exact body and headers; a new connection and one request can have zero application retry | Low | **Recommended** |
| B. Official provider SDK | Adapter, SDK and transitive HTTP/model stack, provider endpoint | New pinned dependency; none of the three SDKs is installed locally | SDK serialization and defaults enter the evidence surface; OpenAI and Anthropic Python SDKs document two automatic retries by default, although they can be disabled | Medium | Viable fallback only with exact SDK pin and retry-disable tests |
| C. User-controlled stateless proxy | Adapter, deployed gateway, gateway logging/auth/config, provider endpoint | New service and deployment | Can enforce policy but adds a second request ID, retention surface, and failure domain | High | Rejected for the first proof; no requirement justifies it |

Approach A uses `http.client.HTTPSConnection` with the default verified TLS
context, a fresh connection per invocation, `Connection: close`, a fixed host,
and no redirect or proxy handling. It performs exactly one `request()` call.
After any timeout, EOF, HTTP error, or ambiguous transport outcome it returns a
closed runner error and does not retry. A TLS connection failure before the
HTTP request is accepted is still not retried by the adapter.

## 9. Provider candidate matrix

Research detail and source mapping are frozen in
`BACKEND_CANDIDATE_CAPABILITY_AUDIT.md`. The summary is:

| Requirement | OpenAI API | Anthropic API | Google Gemini API |
| --- | --- | --- | --- |
| Stateless one-shot API | Documented with Responses API when conversation and previous-response fields are omitted | Documented single-query Messages API | Documented unary `generateContent` |
| Tools can be absent | Documented optional tools | Documented optional tools; tools activate only when included | Documented optional `tools[]` |
| Inline, no file/RAG | Documented text input | Documented single inline user content | Documented inline `contents` |
| Candidate capacity | GPT-4.1: 1,047,576 input context / 32,768 max output | Sonnet 5: 1M context / 128K max output; Messages request limit 32 MB | Gemini 3.6 Flash: 1,048,576 input / 65,536 output |
| Immutable identity | Dated `gpt-4.1-2025-04-14` snapshot documented | `claude-sonnet-5` documented as a pinned canonical ID | Stable ID documented as usually unchanged, but no equivalent immutable guarantee found; response `modelVersion` is output-only |
| Unique provider request ID | `x-request-id` header | `request-id` header | `responseId` body field |
| Default commercial training use | API data not used for training unless opted in | Commercial API input/output not used for training by default | Paid Service prompt/response not used to improve products |
| Standard retention caveat | Abuse logs up to 30 days; Responses state controlled by endpoint/settings and ZDR eligibility | API input/output deleted within 30 days, with policy/legal/files/ZDR exceptions | Limited abuse logging; logging/ZDR behavior depends on paid project and selected features |
| Phase-0 capability result | `UNTESTED` | `UNTESTED` | `UNTESTED`; current pre-call identity fit is contradicted |

All three can represent one tool-free inline call. Anthropic has the cleanest
combination of a documented pinned current ID, a 1M input context, a 128K
output ceiling, a 32 MB HTTP request limit, and a unique request header.

## 10. Provider research/evidence methodology

Provider facts were taken only from current official API, model, SDK, pricing,
and privacy documentation retrieved on 2026-09-05. Each source is named and
linked in the candidate audit with its supported claim.

No inference, authentication, model-list, token-count, or account-setting call
was made. Thus provider feature statements are `DOCUMENTED`; credential names,
installed packages, executable versions, and DNS resolution are
`OBSERVED_LOCAL`; account policy and quota facts are
`ACCOUNT_EVIDENCE_REQUIRED`; actual behavior is `UNTESTED`.

Documentation can eliminate candidates with a contradiction. It cannot create
real capability PASS.

## 11. Model identity strategy

### Recommended identity

Use Anthropic model ID `claude-sonnet-5`. Anthropic documents that 4.6-and-later
dateless model IDs are canonical pinned snapshots whose model weights and
configuration are not changed under the same ID. It separately warns that
serving infrastructure can change. Evidence therefore binds:

- `model_revision_identity = claude-sonnet-5`;
- `model_identity_stability = IMMUTABLE` for the provider's pinned model ID;
- endpoint and API version separately from model identity;
- deployment identity containing only a SHA-256 commitment to the observed
  workspace identifier, never the raw workspace or credential identifier;
- explicit per-request inference geography and service tier;
- adapter version and canonical settings hash;
- provider response identity and sanitized transport-envelope commitment.

The identity claim covers the pinned model ID, not immutable global serving
infrastructure. A later provider model retirement or API-version change
invalidates freshness and requires a new capability proof.

### Fallback identities

OpenAI fallback uses only `gpt-4.1-2025-04-14`, not the floating `gpt-4.1`
alias. Google `gemini-3.6-flash` is a stable model name, but the reviewed docs
say stable models “usually” do not change and return actual `modelVersion` only
after inference. That is insufficient for the current descriptor's pre-call
immutable identity gate, so Gemini is not an eligible first implementation
target without new official evidence. No runner-interface change is authorized.

## 12. Authentication boundary

The future adapter accepts credentials through one controller-only environment
source named `ANTHROPIC_API_KEY`. The value is read only at invocation time and
placed only in the `x-api-key` HTTPS header. The canonical reviewer request and
provider-visible role payload contain no credential, credential name, secret
identifier, or credential path.

Rules:

1. Missing or empty credential source yields `BACKEND_PROVISIONING_REQUIRED`
   before an inference request.
2. The adapter never prints, returns, hashes, persists, or includes the value in
   an exception.
3. Tests use an unmistakably fake value and assert it is absent from every
   receipt, request fixture, error string, and evidence artifact.
4. No general secret manager is introduced.

## 13. Retry/streaming policy

The policy is `ONE_HTTP_REQUEST`, `APPLICATION_RETRIES = 0`, and
`NON_STREAMING`.

- A new HTTPS connection is created for each runner invocation.
- Redirects are rejected rather than followed.
- HTTP 408, 409, 429, and 5xx are returned as controlled failures; none is
  retried.
- Timeout or connection loss after request transmission is an ambiguous failed
  attempt, never grounds to repeat the same context.
- The adapter does not call a token-count, model, status, or follow-up endpoint
  inside `invoke()`.
- Streaming is not used because the existing runner requires one exact response
  object and one provider request identity.

Official SDK retry defaults are one reason Approach B is not preferred. If PM
later selects an SDK, a pinned version, `max_retries=0`, raw-response access,
and a one-request transport test are mandatory.

## 14. Request/response binding

### Deterministic request projection

The adapter validates the canonical request document and each role's byte count,
SHA-256, and base64 round trip. It then creates one provider message without a
conversation object.

The projection is fixed as `joewrks.anthropic-message-projection/1.0`:

1. `reviewer_brief` becomes the sole Anthropic `system` text block after strict
   UTF-8 decoding.
2. `review_package`, `run_envelope`, and `output_schema` become three ordered
   text content blocks in one `user` message. Each block has a fixed JSON
   header containing only logical role, media type, byte count, and SHA-256,
   followed by the strict UTF-8 content.
3. No additional instruction, product content, provider file, or remote handle
   is added.
4. Non-UTF-8 content or an unexpected media type fails before network I/O.
5. The canonical provider-body hash, excluding authorization, is included in
   the `RESPONSE` event's sanitized metadata commitment.

This translation makes the same exact four logical contents readable to the
model without asking it to decode a 425 KB base64 string. The original canonical
request hash remains the `BackendResponse.request_sha256` authority.

### Fixed provider settings

The first candidate settings identity is canonical JSON over:

```json
{
  "api_version": "2023-06-01",
  "endpoint": "https://api.anthropic.com/v1/messages",
  "inference_geo": "us",
  "max_tokens": 65536,
  "model": "claude-sonnet-5",
  "output_mode": "plain_text_expected_to_be_exact_json",
  "projection": "joewrks.anthropic-message-projection/1.0",
  "seed": "ABSENT_NO_API_FIELD_DOCUMENTED",
  "service_tier": "standard_only",
  "stream": false,
  "thinking": {"type": "adaptive"},
  "effort": "high",
  "temperature": "ABSENT",
  "tools": "ABSENT",
  "top_k": "ABSENT",
  "top_p": "ABSENT"
}
```

The implementation must compute and record the SHA-256 from canonical bytes; it
must not copy a digest from this design.

Provider-native schema output is not selected for the first proof. The frozen
schema is already one reviewer-visible role, and Anthropic structured output
supports a JSON Schema subset whose exact compatibility with this schema has
not been executed. Plain text must contain exactly one JSON object, which the
existing runner already freezes and validates. Native schema mode may be
considered only as a separately reviewed settings identity after exact-schema
compatibility is proven; it is not hidden tooling.

| Output mode | Effect on request semantics | Evidence/risk | Disposition |
| --- | --- | --- | --- |
| Plain text expected to be exact JSON | Sends the frozen output schema only as its existing reviewer-visible role; no provider grammar is added | Existing runner provides strict parse/schema enforcement; malformed model output fails closed | Selected for the first proof |
| Provider-native JSON schema | Sends the same schema again as provider output configuration and changes the inference-settings identity | Provider documents schema mode, but exact `$defs`, `$ref`, `const`, `pattern`, and `additionalProperties` compatibility is untested | Deferred; requires exact-schema proof and new frozen settings identity |

### Response translation

The adapter requires HTTP 200, one Anthropic Message object, one final text
block containing the semantic JSON, no tool-use/server-tool block, and a
non-empty `request-id` response header. Adaptive-thinking blocks may be present
but are not semantic output. Any refusal, truncation, malformed envelope,
multiple text results, missing request ID, or unexpected active-content block
fails closed.

`BackendResponse.raw_bytes` is the exact UTF-8 byte sequence of the sole final
text block, with no stripping or JSON reserialization. `provider_request_id` is
the `request-id` header. The sole `RESPONSE` event hashes sanitized metadata:
HTTP body byte count/hash, Message `id`, `model`, `stop_reason`, content-block
types, usage, inference geo, request-body hash, and request-id hash. No
authorization header is included. The event hash does not replace the runner's
raw semantic-output freeze.

## 15. Privacy/retention requirements

Anthropic documents that commercial API inputs and outputs are not used for
model training by default and are automatically deleted from its backend within
30 days, subject to Files API, negotiated ZDR, usage-policy enforcement, and
legal exceptions. It also documents account/workspace data-routing controls.

That documentation is not account evidence. Before implementation is enabled:

1. PM must accept either the documented standard 30-day policy and exceptions,
   or require a verified ZDR agreement.
2. The actual workspace must be read back without recording secrets, confirming
   the selected retention/privacy mode and that feedback/training opt-in is not
   enabled.
3. `inference_geo` is sent explicitly. The initial design chooses `us` for a
   stable request-level geography; the later account must allow it.
4. No Files API, prompt cache breakpoint, container, skill, search, or external
   data feature is used.
5. Only the synthetic probe may run before the account evidence is accepted.

If standard retention is not acceptable and ZDR cannot be verified, the
candidate becomes `UNAVAILABLE`; the design does not silently fall back.

## 16. Capacity requirements

The historical input package is 319,066 bytes across ten files. The current
runner's real construction was measured locally using the authoritative
synthetic builder:

- canonical request bytes: `427,220`;
- canonical request SHA-256:
  `d5bb3119b765d1632a2dde1f66fc687a0ed14cfc5649c99a566e51a654656137`;
- review-package source/base64: `319,066 / 425,424` bytes/characters;
- output-schema source/base64: `266 / 356`;
- reviewer-brief source/base64: `126 / 168`;
- run-envelope source/base64: `39 / 52`.

This is a byte measurement, not a token count. A deliberately conservative
planning band of about 107,000–214,000 input tokens follows from two to four
ASCII bytes per token; it is `UNTESTED` and may not match any provider's
tokenizer. Anthropic Sonnet 5's documented 1M-token context and 32 MB HTTP body
limit provide substantial apparent margin. The 128K output ceiling also exceeds
the chosen 65,536-token adapter maximum.

Before a semantic request, the future synthetic probe must obtain an actual
provider token count or usage readback for the exact inert projection and prove
that input plus configured maximum output fit without truncation. Automatic
truncation is forbidden.

At current official pricing retrieved on 2026-09-05, Sonnet 5 is $3 per million
input tokens and $15 per million output tokens; US-only inference is documented
at 1.1x. The planning band's input portion is therefore roughly $0.35–$0.71 per
full-size synthetic call before the small probe output. This is not a quote and
must be recomputed immediately before an authorized call.

## 17. Synthetic real-backend preflight

The first authorized real calls use only `THROWAWAY_ISOLATION_PROBE` with inert
padding and fresh random nonces. No semantic-review package, golden, customer
data, Product Definition, or prior reviewer result is included.

### Preconditions

1. The implementation branch and adapter bytes are frozen.
2. The selected endpoint, API version, model ID, projection version, settings,
   retention decision, workspace identity, and credential-source status are
   read back and hash-bound without secrets.
3. Static adapter/configuration evidence supports every descriptor observation.
4. The provider model and quota accept the exact projected token/request size.
5. The current runner capability evidence remains unchanged until the proof
   completes.

### Call P1 — positive and capacity proof

Run the existing synthetic preflight once with a 319,066-byte inert package.
Require:

- exactly one HTTPS request and one provider Message;
- exact allowed nonce once in the sole JSON output;
- all forbidden canaries absent;
- one non-empty, previously unused `request-id`;
- exact request/run/context/backend/settings binding;
- no tools, retrieval, web, code, files, containers, skills, continuation, or
  conversation state in sent bytes or response events;
- HTTP and token usage within frozen limits;
- descriptor identical before and after invocation;
- frozen evidence readback and an overall passing production preflight result.

### Call P2 — freshness proof

P2 is a separately declared fresh synthetic run, not a retry. It uses a new
review run, context, nonce, and provider request ID, the same frozen backend
identity, and no previous-response field. Require P2 to contain only its nonce,
not P1's nonce, and require both receipts to bind distinct request identities.
The existing full-preflight helper owns its fixed synthetic identity, so P2 is
constructed with the existing public `build_canonical_request`, backend
response validator, and evidence/receipt primitives under a separately named
capability-proof invocation. It does not require or authorize a generic runner
interface change.

If P1 fails or has an ambiguous transport outcome, stop; do not execute P2 as a
same-context repair. A later attempt requires explicit new-run authority and
preserves P1 evidence.

### Capability conclusion

Only P1 and P2 plus accepted account evidence may authorize a replacement of
the current `UNAVAILABLE` evidence. Passing them proves backend isolation
capability only. It does not prove reviewer quality or reliability.

## 18. Failure states

| Condition | Required result |
| --- | --- |
| Credential or paid workspace absent | `BACKEND_PROVISIONING_REQUIRED`; zero inference calls |
| Retention/privacy decision or account evidence absent | `BACKEND_PROVISIONING_REQUIRED`; zero inference calls |
| Model resolves to a floating/unknown identity | `ISOLATION_CAPABILITY_UNAVAILABLE`; zero inference calls |
| Model, endpoint, settings, projection, or account policy drift | freshness invalid; complete capability proof required again |
| Request/token/output capacity insufficient | `ISOLATION_CAPABILITY_UNAVAILABLE`; no semantic splitting or continuation |
| HTTP redirect, timeout, EOF, 4xx, 5xx, malformed response | controlled invocation failure; no automatic retry |
| Missing/reused request ID | package/response binding failure |
| Tool, retrieval, file, container, skill, code, web, or continuation evidence | observed capability failure |
| Multiple text responses, truncation, refusal, or invalid JSON | review output invalid; fail closed |
| Provider docs contradict the frozen runner | `BACKEND_CONTRACT_INCOMPATIBILITY`; PM review, no runner weakening |

No failure in this workstream mutates semantic authority or establishes a
semantic calibration failure.

## 19. Recommended architecture

Use Approach A: one provider-specific Python-standard-library adapter at
`skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py`, plus
the smallest explicit registration permitted by the current backend module.

The adapter's only job is to:

- accept canonical request bytes and controller-only authentication;
- validate and project exactly four inline roles;
- make one non-streaming `POST /v1/messages` request with no retry;
- use the frozen endpoint/model/settings identity;
- extract one exact JSON text result and the `request-id` header;
- return the existing `BackendResponse` with one `RESPONSE` event;
- expose no provider framework, tools, files, retrieval, or conversation state.

No generic plugin discovery or multi-provider fallback is designed.

## 20. Recommended provider candidate

`RECOMMENDED_PROVIDER_CANDIDATE = Anthropic API`

Preferred endpoint/model:

- endpoint: `https://api.anthropic.com/v1/messages`;
- API version header: `2023-06-01`;
- model: `claude-sonnet-5`;
- inference geography: explicit `us`;
- service tier: `standard_only`;
- response: non-streaming, plain JSON text, maximum 65,536 tokens;
- tool/file/retrieval/conversation fields: absent.

Reasons, in selection order:

1. direct fit to a stateless single-query request;
2. documented pinned current model ID;
3. documented unique request header;
4. largest documented output headroom of the three reviewed candidates;
5. ample request/body context margin;
6. simple direct HTTPS shape and explicit inference geography;
7. privacy posture that can be evaluated as one account provisioning gate.

This recommendation is not a capability PASS. Remaining gates are credential
and paid-workspace provisioning, account retention/privacy acceptance and
readback, model/quota access, exact token count, adapter implementation review,
and P1/P2 real synthetic evidence.

OpenAI with direct HTTPS and pinned `gpt-4.1-2025-04-14` is the documented
fallback. Gemini is not selected because the reviewed stable model naming does
not yet satisfy the runner's pre-call immutable identity requirement.

## 21. Provisioning requirements

The later provisioning gate requires all of the following, with no secret value
committed or printed:

1. a user-controlled Anthropic commercial API workspace with billing enabled;
2. access to `claude-sonnet-5` and enough token/request quota for two full-size
   synthetic requests;
3. an `ANTHROPIC_API_KEY` supplied to the controller process only;
4. PM acceptance of the observed account's retention/privacy mode, or verified
   contractual ZDR if standard retention is not accepted;
5. permission for explicit `inference_geo = us`;
6. a reviewed spend ceiling for the two synthetic calls;
7. confirmation that feedback/training opt-in and provider logging features are
   not enabled for the probe path.

No provisioning action is performed in Phase 0. Missing any item produces
`BACKEND_PROVISIONING_REQUIRED`.

## 22. Testing strategy

The future implementation must use test-first behavior changes and include:

### Pure unit tests

- strict canonical request parsing and four-role projection;
- byte-count/hash/base64 and UTF-8 rejection;
- exact settings canonicalization and backend identity;
- deterministic provider body bytes;
- authorization exclusion from all returned/logged/evidence data;
- successful one-message/one-text/request-ID translation;
- rejection of redirects, missing/reused IDs, extra text, tools, server tools,
  truncation, refusals, malformed JSON, and identity drift.

### Local transport tests

Use a controller-owned loopback HTTPS or injected `HTTPConnection` test double
to count calls. Assert exactly one request on success, 408, 409, 429, 5xx,
timeout, EOF, and malformed response. Assert no redirect following and no
second socket/request. These are transport tests, not capability authority.

### Existing regressions

Run all Reviewer Runner tests and audit, including fake-backend non-authority,
source immutability, cleanup, replay, and response-byte freezing. No assertion
is weakened.

### Real synthetic proof

P1/P2 run only in a later PM-approved task after provisioning. Their evidence
is independently audited before changing the capability disposition.

## 23. Compatibility/frozen boundaries

The following remain unchanged:

- current Reviewer Runner protocol, identities, capability tuple, receipts,
  response parser, preflight, and failure states;
- exactly four logical input roles and full inline delivery;
- Product Definition and all M6 authority/evidence;
- `joewrks.action-conformance/1.0`;
- `joewrks.semantic-review/1.0`;
- semantic-review/2.1 implementation and `NOT_MEASURED` reliability;
- v0.4.3 calibration history and counters;
- current capability evidence (`registered_real_adapters = 0`, backend
  `UNAVAILABLE`);
- v0.4.4 `BLOCKED` state.

There is no `RUNNER_INTERFACE_CHANGE_REQUIRED` for the recommended path. Any
future discovery that requires one must stop for PM review instead of changing
the generic contract.

## 24. Security/privacy

- TLS certificate and hostname verification use Python's default trusted
  context; plaintext and custom trust bypasses are forbidden.
- The endpoint host and path are compile-time constants; redirects, caller URLs,
  proxies, and arbitrary headers are forbidden.
- The API key is controller-only and is redacted by construction, not by a
  logging convention.
- Request projection rejects unrecognized roles, media types, duplicate keys,
  invalid hashes, invalid UTF-8, and oversized inputs before network I/O.
- The adapter keeps provider envelopes in memory, returns only exact semantic
  output bytes plus closed metadata, and never writes outside runner evidence
  APIs.
- Response bytes are size-bounded, strictly decoded, frozen before parsing, and
  rejected on any extra document or schema mismatch.
- No tools, files, RAG, cache breakpoint, container, skill, URL context, search,
  connector, MCP, or code execution is configured.
- Provider retention remains an acknowledged external boundary; account proof
  and PM acceptance are required.

## 25. Calibration boundary

Adapter implementation and P1/P2 capability proof do not create or authorize
semantic-review/2.1 calibration. Calibration authority, goldens, compatibility
mapping, cohorts, and reliability thresholds remain a later, separate design
after real backend capability evidence is accepted.

The counters remain:

- real calibration attempts: `1`;
- valid real calibration runs: `0`.

No Phase-0 activity changes either counter.

## 26. v0.4.4 gate

v0.4.4 remains `BLOCKED`. Provider recommendation does not unblock it. Adapter
implementation does not unblock it. Synthetic isolation capability would only
remove the backend-capability prerequisite; semantic-review/2.1 reliability
would still have to be measured under separately frozen calibration authority.

## 27. Open questions

These are genuine PM/account decisions, each with a fail-closed default:

1. **Retention:** accept Anthropic's documented standard commercial API
   retention and exceptions, or require verified ZDR. Default: no real call
   until one is explicitly accepted and observed for the workspace.
2. **Provisioning/cost:** authorize creating or using an Anthropic paid workspace
   and funding two full-size synthetic calls. Default: no account or billing
   action.
3. **Inference geography:** accept explicit US-only inference and its documented
   1.1x price multiplier. Default: keep the adapter disabled if the workspace
   cannot or must not use `us`.
4. **Provider policy:** confirm that Anthropic is not organizationally forbidden.
   Default: `BACKEND_PROVISIONING_REQUIRED`.

Technical facts such as adapter request count, exact byte projection, token
usage, model access, response shape, and request-ID presence are not PM opinion
questions. They are future tests and must fail closed if unproven.
