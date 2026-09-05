# Backend Candidate Capability Audit

Audit status: `COMPLETE — DESIGN EVIDENCE ONLY`

Candidate disposition: `RECOMMENDED_PROVIDER_CANDIDATE = Anthropic API`

Production capability disposition: `UNAVAILABLE`

No provider received an inference request during this audit.

## Evidence vocabulary

Every capability statement in this audit uses one of these Phase-0 classes:

| Class | Meaning |
| --- | --- |
| `OBSERVED_LOCAL` | Directly inspected on the local planning runtime or repository without provider inference |
| `DOCUMENTED` | Supported by a cited current official provider source |
| `ACCOUNT_EVIDENCE_REQUIRED` | Depends on the eventual account, workspace, project, quota, or contract |
| `UNTESTED` | Not executed against a real provider in Phase 0 |
| `UNAVAILABLE` | Not present in the inspected runtime/repository |
| `CONTRADICTED` | Current evidence conflicts with a required runner property |

The production pass classification is intentionally absent. It belongs to
production capability evidence after an authorized real synthetic preflight.

## Runtime inspection date

- `OBSERVED_LOCAL` — runtime inspection date: `2026-09-05`.
- `OBSERVED_LOCAL` — timezone: `Asia/Seoul`.
- `OBSERVED_LOCAL` — provider-document retrieval date: `2026-09-05`.
- `UNTESTED` — real inference requests: `0`.
- `UNTESTED` — authenticated model, token-count, account-policy, and quota
  requests: `0`.

## Repository baseline

- `OBSERVED_LOCAL` — authoritative main commit:
  `ab95074704af0e93248d56344d6a220dfec88a93`.
- `OBSERVED_LOCAL` — authoritative main tree:
  `867bec6fcfe5f4dc9927beaaf143087178e09e7c`.
- `OBSERVED_LOCAL` — planning branch:
  `plan/post-m6-real-backend-capability-enablement`.
- `OBSERVED_LOCAL` — `RUNNER_CAPABILITY_EVIDENCE.json` reports registered real
  adapters `0`, backend `UNAVAILABLE`, runner
  `ISOLATION_CAPABILITY_UNAVAILABLE`, calibration `CALIBRATION_NOT_RUN`,
  semantic-review/2.1 reliability `NOT_MEASURED`, and v0.4.4 `BLOCKED`.
- `OBSERVED_LOCAL` — real calibration attempts / valid real runs remain `1 / 0`.
- `UNAVAILABLE` — no OpenAI, Anthropic, or Gemini real adapter or provider
  configuration exists in `reviewer_runner`.

## Local capability observations

| Observation | Classification | Evidence |
| --- | --- | --- |
| Python | `OBSERVED_LOCAL` | `3.14.5` |
| Git | `OBSERVED_LOCAL` | `2.54.0.windows.1` |
| curl | `OBSERVED_LOCAL` | `8.13.0`, Windows Schannel TLS backend |
| Python TLS | `OBSERVED_LOCAL` | OpenSSL `3.0.20` reported by Python |
| Current runner request interface | `OBSERVED_LOCAL` | one canonical JSON document with exactly four inline base64 roles |
| Current backend interface | `OBSERVED_LOCAL` | `describe()` and one `invoke(request_bytes, timeout_seconds)`; no provider implementation |
| Current response contract | `OBSERVED_LOCAL` | one semantic JSON byte stream, one provider request ID, one `RESPONSE` event, no continuation IDs |
| Local container engines | `UNAVAILABLE` | Docker, Podman, and nerdctl executables not found |
| WSL executable | `OBSERVED_LOCAL` | executable present; not evidence of an eligible backend or isolation boundary |

### Local regression observation

- `OBSERVED_LOCAL` — the 87 backend, preflight, controller, and response
  behavior tests selected for inspection passed.
- `OBSERVED_LOCAL` — the adjacent 15-test live-byte audit group produced four
  passes, four failures, and seven errors because this new Windows worktree
  materialized committed LF source blobs as CRLF while system Git configuration
  has `core.autocrlf=true`.
- `OBSERVED_LOCAL` — for `reviewer_runner/identity.py`, the committed blob and
  Git-filtered live blob were
  `f476b1da1d075d1495880483d40fdad2b49f1424`; the raw live blob was
  `f063299c77fa0392d62a2b0d8729e06ef56789ce`.
- `OBSERVED_LOCAL` — the worktree remained clean before the two planning files
  were created. The audit correctly failed closed on raw-byte mismatch.
- `OBSERVED_LOCAL` — one evidence-based `checkout-index` retry with command-local
  `core.autocrlf=false` did not change the already materialized raw bytes. No
  second retry was attempted.
- `UNAVAILABLE` — a full live-byte audit PASS in this worktree. This is an EOL
  materialization limitation of the local checkout, not evidence of a runner
  semantic defect or a provider capability defect. The committed baseline audit
  remains historical authority; this Phase-0 task makes no new runner-verification
  claim.

### Canonical request-size observation

The authoritative synthetic request builder was executed locally with the
historical package-size class and inert bytes.

| Role | Source bytes | Base64 characters | Classification |
| --- | ---: | ---: | --- |
| `output_schema` | 266 | 356 | `OBSERVED_LOCAL` |
| `review_package` | 319,066 | 425,424 | `OBSERVED_LOCAL` |
| `reviewer_brief` | 126 | 168 | `OBSERVED_LOCAL` |
| `run_envelope` | 39 | 52 | `OBSERVED_LOCAL` |

- `OBSERVED_LOCAL` — input role count: `4`.
- `OBSERVED_LOCAL` — canonical request byte count: `427,220`.
- `OBSERVED_LOCAL` — canonical request SHA-256:
  `d5bb3119b765d1632a2dde1f66fc687a0ed14cfc5649c99a566e51a654656137`.
- `UNTESTED` — provider token count. The planning band of approximately
  107,000–214,000 tokens assumes two to four ASCII bytes per token and is not a
  tokenizer result.
- `DOCUMENTED` — Sonnet 5 current standard pricing is $2/MTok input and
  $10/MTok output (A5/A10); US-only inference is a separate 1.1x multiplier
  (A9).
- `UNTESTED` — exact charge. At those documented rates, the rough input-only
  planning band is about $0.21–$0.43 at base rates and $0.24–$0.47 with US-only
  inference. This is not a bill or tokenizer measurement.
- `UNTESTED` — provider wire-body byte count after deterministic role
  projection. It is expected to remain far below the smallest documented HTTP
  request limit, but the exact implementation bytes must be measured.

## Network/tool observations

| Observation | Classification | Result |
| --- | --- | --- |
| `api.openai.com` DNS A lookup | `OBSERVED_LOCAL` | resolved; two A records observed, addresses intentionally not recorded |
| `api.anthropic.com` DNS A lookup | `OBSERVED_LOCAL` | resolved; one A record observed, address intentionally not recorded |
| `generativelanguage.googleapis.com` DNS A lookup | `OBSERVED_LOCAL` | resolved; eight A records observed, addresses intentionally not recorded |
| HTTPS client executable | `OBSERVED_LOCAL` | curl available with Schannel |
| Python standard-library HTTPS | `OBSERVED_LOCAL` | `http.client`, `ssl`, and default verified TLS context available |
| `HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY` names | `OBSERVED_LOCAL` | no configured value observed; values were not printed |
| Provider TLS handshake | `UNTESTED` | no endpoint request or handshake probe was made |
| Authenticated API reachability | `UNTESTED` | no provider request was made |

DNS resolution proves only name resolution. It does not prove provider
authentication, model access, rate limit, request capacity, or inference.

## Installed SDK/executable observations

| Component | Classification | Observed version/state |
| --- | --- | --- |
| OpenAI Python SDK (`openai`) | `UNAVAILABLE` | not installed |
| Anthropic Python SDK (`anthropic`) | `UNAVAILABLE` | not installed |
| Google Gen AI SDK (`google-genai`) | `UNAVAILABLE` | not installed |
| Legacy Google Generative AI SDK | `UNAVAILABLE` | not installed |
| `requests` | `UNAVAILABLE` | not installed |
| `httpx` | `OBSERVED_LOCAL` | `0.28.1` installed, but not selected |
| Python standard-library HTTPS | `OBSERVED_LOCAL` | available; no new dependency needed |

- `DOCUMENTED` — the OpenAI Python SDK retries selected connection, timeout,
  408, 409, 429, and 5xx errors twice by default and supports
  `max_retries=0` (source O4).
- `DOCUMENTED` — the Anthropic Python SDK also retries selected connection,
  408, 409, 429, and 5xx errors twice by default and supports disabling retries
  (source A6).
- `OBSERVED_LOCAL` — because neither SDK is installed, Approach B would add a
  pinned dependency and transitive transport surface.
- `OBSERVED_LOCAL` — direct `http.client.HTTPSConnection` can be instantiated
  fresh for each invocation and has no application-level retry loop unless the
  adapter writes one.

## Credential-source presence classification

No value was read, copied, hashed, logged, tested, or included in this audit.

| Candidate source name | Classification | Presence |
| --- | --- | --- |
| `OPENAI_API_KEY` | `OBSERVED_LOCAL` | `NOT_CONFIGURED` |
| `ANTHROPIC_API_KEY` | `OBSERVED_LOCAL` | `NOT_CONFIGURED` |
| `GOOGLE_API_KEY` | `OBSERVED_LOCAL` | `NOT_CONFIGURED` |
| `GEMINI_API_KEY` | `OBSERVED_LOCAL` | `NOT_CONFIGURED` |
| `GOOGLE_APPLICATION_CREDENTIALS` | `OBSERVED_LOCAL` | `NOT_CONFIGURED` |

- `ACCOUNT_EVIDENCE_REQUIRED` — existence of any usable provider account,
  project/workspace, billing status, model entitlement, quota, retention
  setting, or organizational policy.
- `UNAVAILABLE` — a currently provisioned candidate credential source.
- `UNTESTED` — credential validity.

## Provider candidate table

| Requirement | OpenAI API | Anthropic API | Google Gemini API |
| --- | --- | --- | --- |
| One request without stored conversation | `DOCUMENTED` — Responses can be created directly; prior/conversation fields are optional | `DOCUMENTED` — Messages explicitly supports a single query | `DOCUMENTED` — unary `generateContent` returns one full response |
| Prior/continuation ID absent | `DOCUMENTED` — `previous_response_id` can be omitted | `DOCUMENTED` — no prior ID is required for a single query | `DOCUMENTED` — one `contents` request needs no session ID |
| Stored conversation absent | `DOCUMENTED` — omit conversation and set `store=false` | `DOCUMENTED` — direct Messages is stateless; do not use managed agents/containers | `DOCUMENTED` — use `generateContent`, not stateful Interactions/Live APIs |
| Tools absent | `DOCUMENTED` — tools are attached explicitly and may be omitted | `DOCUMENTED` — `tools` is optional and only activates tools when included | `DOCUMENTED` — `tools[]` is optional |
| Full inline text | `DOCUMENTED` — text input supported without Files API | `DOCUMENTED` — one inline user message supported | `DOCUMENTED` — inline `contents` supported |
| Context/input capacity | `DOCUMENTED` — GPT-4.1 1,047,576 context | `DOCUMENTED` — Sonnet 5 1M context and Messages body limit 32 MB | `DOCUMENTED` — Gemini 3.8 Flash input 1,048,576 |
| Output capacity | `DOCUMENTED` — GPT-4.1 max 32,768 tokens | `DOCUMENTED` — Sonnet 5 max 128K; design caps at 65,536 | `DOCUMENTED` — Gemini 3.8 Flash max 65,536 |
| Pinned model | `DOCUMENTED` — `gpt-4.1-2025-04-14` snapshot | `DOCUMENTED` — `claude-sonnet-5` is a canonical pinned ID | `CONTRADICTED` — reviewed docs say stable IDs usually do not change; actual `modelVersion` is output-only, not a pre-call immutable guarantee |
| Provider request identity | `DOCUMENTED` — unique `x-request-id` header | `DOCUMENTED` — unique `request-id` header | `DOCUMENTED` — response `responseId` |
| One raw response without follow-up | `DOCUMENTED` — one non-streaming Responses result; no prior ID required | `DOCUMENTED` — one non-streaming Message result | `DOCUMENTED` — unary `generateContent` returns the full result |
| Generation settings bindable | `DOCUMENTED` — model, max output, text format, reasoning and sampling fields are request settings | `DOCUMENTED` — model, max tokens, stream, effort/thinking, service tier and inference geo are request settings | `DOCUMENTED` — generation config includes max output, candidate count, response format and supported sampling/thinking settings |
| Structured output | `DOCUMENTED` — JSON schema supported with subset restrictions | `DOCUMENTED` — `output_config.format` accepts JSON schema | `DOCUMENTED` — schema output supported with subset/complexity restrictions |
| Exact frozen schema compatibility | `UNTESTED` | `UNTESTED` | `UNTESTED` |
| Commercial training default | `DOCUMENTED` — API data not used for training unless opted in | `DOCUMENTED` — commercial API inputs/outputs not used for training by default | `DOCUMENTED` — paid-service prompts/responses not used to improve products |
| Retention/account posture | `ACCOUNT_EVIDENCE_REQUIRED` — standard abuse logging and ZDR/MAM status need exact account evidence | `ACCOUNT_EVIDENCE_REQUIRED` — standard policy/exceptions or ZDR require accepted contract/Console/admin evidence; only documented workspace fields are API-readable | `ACCOUNT_EVIDENCE_REQUIRED` — paid billing, logging, features, and ZDR approval need exact project evidence |
| Phase-0 real behavior | `UNTESTED` | `UNTESTED` | `UNTESTED` |
| Credential source | `UNAVAILABLE` | `UNAVAILABLE` | `UNAVAILABLE` |
| First-target disposition | documented fallback | **recommended candidate** | not currently eligible under immutable pre-call identity gate |

## Official sources

All sources were retrieved on `2026-09-05`.

### OpenAI

| ID | Exact source title | URL | Supported claim |
| --- | --- | --- | --- |
| O1 | GPT-4.1 Model | https://developers.openai.com/api/docs/models/gpt-4.1 | 1,047,576 context, 32,768 max output, Responses support, structured-output support, price, and dated `gpt-4.1-2025-04-14` snapshot |
| O2 | API Reference — Introduction / Debugging requests | https://platform.openai.com/docs/api-reference/introduction | bearer authentication, unique `x-request-id`, client request ID, pinned-model guidance |
| O3 | Data controls in the OpenAI platform | https://platform.openai.com/docs/models/default-usage-policies-by-endpoint | no API training by default, abuse-monitoring retention, Responses application-state behavior, ZDR/MAM eligibility and regional/account caveats |
| O4 | OpenAI Python library — Retries | https://github.com/openai/openai-python#retries | SDK retries twice by default for listed transient/error classes and can set `max_retries=0` |
| O5 | Developer quickstart | https://platform.openai.com/docs/quickstart/make-your-first-api-request | direct Responses creation and tools supplied explicitly when wanted |

### Anthropic

| ID | Exact source title | URL | Supported claim |
| --- | --- | --- | --- |
| A1 | Create a Message | https://platform.claude.com/docs/en/api/messages/create | single-query Messages request, required/optional fields, non-streaming option, optional tools, output configuration, response Message shape |
| A2 | Claude API errors | https://platform.claude.com/docs/en/api/errors | 32 MB Messages request limit, error shape, unique `request-id` header |
| A3 | Model IDs and versioning | https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions | 4.6-and-later IDs such as `claude-sonnet-5` are pinned canonical snapshots; serving infrastructure may still change |
| A4 | Context windows | https://platform.claude.com/docs/en/build-with-claude/context-windows | Sonnet 5 1M context and 128K maximum output |
| A5 | Claude Platform release notes — August 10, 2026 | https://platform.claude.com/docs/en/release-notes/overview | Sonnet 5 $2/MTok input and $10/MTok output became standard; scheduled September 1 increase to $3/$15 did not occur |
| A6 | Python SDK | https://platform.claude.com/docs/en/api/sdks/python | SDK request-ID access and two default retries with configurable retry count |
| A7 | Is my data used for model training? | https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training | commercial/API input and output are not used for model training by default; opt-in/feedback exceptions |
| A8 | How long do you store my organization's data? | https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data | API inputs/outputs deleted within 30 days with Files, ZDR agreement, usage-policy, legal, Covered Model, and feedback exceptions |
| A9 | Data residency | https://platform.claude.com/docs/en/manage-claude/data-residency | explicit `inference_geo` values `us`/`global`, response usage readback, workspace restrictions, and US 1.1x pricing |
| A10 | What's new in Claude Sonnet 5 | https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5 | current model-specific $2/MTok input and $10/MTok output pricing |
| A11 | Workspaces | https://platform.claude.com/docs/en/manage-claude/workspaces | workspace IDs, scoped-key behavior, and `anthropic-workspace-id` response binding |
| A12 | Workspaces — Claude API Reference | https://platform.claude.com/docs/en/api/beta/organization/workspaces | Admin/Workspace API exposes workspace `id` and `data_residency` fields including allowed/default inference geos and workspace geo; separate admin authorization required |
| A13 | API and data retention | https://platform.claude.com/docs/en/manage-claude/api-and-data-retention | organization-level ZDR, Messages feature eligibility, feature-specific retention, and current Covered Model list |
| A14 | Authentication | https://platform.claude.com/docs/en/manage-claude/authentication | workspace-scoped keys select one workspace without a request workspace selector; multi-workspace keys require a workspace ID header |

### Google Gemini

| ID | Exact source title | URL | Supported claim |
| --- | --- | --- | --- |
| G1 | Generating content | https://ai.google.dev/api/generate-content | unary generate request, optional tools, generation settings, output-only `modelVersion`, and unique `responseId` |
| G2 | Gemini 3.8 Flash | https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash | current stable Flash model as of 2026-09-02; 1,048,576 input limit, 65,536 output limit, text/structured-output capabilities |
| G3 | Gemini models | https://ai.google.dev/gemini-api/docs/models | stable/latest/preview/experimental naming; latest aliases hot-swap; stable models “usually” do not change |
| G4 | Understand and count tokens | https://ai.google.dev/gemini-api/docs/tokens | context is combined input/output and exact count-token mechanism exists |
| G5 | Zero data retention in the Gemini Developer API | https://ai.google.dev/gemini-api/docs/zdr | paid-service training restriction, abuse logging, ZDR approval, and state/storage feature caveats |
| G6 | Data logging and sharing | https://ai.google.dev/gemini-api/docs/logs-policy | billing-enabled project log controls, 7/14/28/55-day choices, default non-training of paid logs, opt-in sharing caveat |
| G7 | Gemini Developer API pricing | https://ai.google.dev/gemini-api/docs/pricing | Gemini 3.8 Flash current input/output price dimensions and paid/free training distinction |
| G8 | Structured outputs | https://ai.google.dev/gemini-api/docs/structured-output | JSON schema mode and subset/complexity limitations |

## Official Source Conflict Handling

When two official provider sources conflict:

1. prefer the source with the most recent explicit publication/update date;
2. prefer a product/model-specific current page over an undated cached generic
   page when the provider explicitly announces a newer policy;
3. record both sources and the conflict;
4. classify the claim `DOCUMENTED` only after resolving it; and
5. if freshness cannot be resolved, classify it `UNTESTED` or
   `ACCOUNT_EVIDENCE_REQUIRED` as appropriate.

Applied pricing conflict: a cached generic Anthropic Pricing rendering retrieved
from `https://platform.claude.com/docs/en/about-claude/pricing` still stated the
previously scheduled September 1, 2026 Sonnet 5 increase to $3/$15. The
explicitly dated 2026-08-10 release note (A5) says that increase would not occur,
and the current Sonnet 5 model-specific page (A10) states $2/$10. A5/A10
therefore control, the stale value is rejected, and the resolved price claim is
`DOCUMENTED`.

## Request-state capability

### OpenAI API

- `DOCUMENTED` — a Responses request can be created from direct input without a
  conversation or prior response (O5).
- `DOCUMENTED` — `previous_response_id` and provider conversation state are
  optional API features and can be absent (O2/O5).
- `DOCUMENTED` — setting `store=false` avoids application-state storage for the
  request subject to the documented endpoint/account caveats (O3).
- `UNTESTED` — one actual account/model request with all state fields absent.

### Anthropic API

- `DOCUMENTED` — Messages supports a single query with one user message (A1).
- `DOCUMENTED` — no thread, conversation, previous-response, file, or
  continuation object is required (A1).
- `DOCUMENTED` — direct Messages and managed-agent/container capabilities are
  separate; the design uses only direct Messages (A1).
- `UNTESTED` — actual one-query execution and response shape.

### Google Gemini API

- `DOCUMENTED` — `generateContent` is a standard unary endpoint returning the
  full result in one response (G1).
- `DOCUMENTED` — a single `contents` input needs no provider conversation or
  continuation object; repeated history is caller-supplied only for multi-turn
  use (G1).
- `DOCUMENTED` — the design would avoid the stateful Interactions and Live APIs
  identified in the ZDR guidance (G5).
- `UNTESTED` — actual unary execution.

## Tools capability

### OpenAI API

- `DOCUMENTED` — tools are attached in a request only when explicitly supplied
  (O5).
- `DOCUMENTED` — a text-only Responses request can omit web search, file search,
  code interpreter, computer use, functions, connectors, and MCP (O2/O5).
- `UNTESTED` — raw outgoing body and provider events for a real request.

### Anthropic API

- `DOCUMENTED` — `tools` is optional; tool use is available only when tool
  definitions are included (A1).
- `DOCUMENTED` — `skills`, containers, prompt-cache breakpoints, and server
  tools are optional and can be absent (A1).
- `UNTESTED` — raw outgoing body and returned content-block types.

### Google Gemini API

- `DOCUMENTED` — `tools[]` and tool configuration are optional (G1).
- `DOCUMENTED` — function, code execution, search, file search, URL context, and
  MCP mechanisms are separate configured tool/features and can be omitted (G1,
  G8).
- `UNTESTED` — raw outgoing body and candidate metadata.

No provider's documentation alone proves that a future adapter omitted the
fields. The synthetic evidence must commit the exact sanitized wire body.

## Context/capacity

### Common measured need

- `OBSERVED_LOCAL` — source package class: `319,066` bytes / `10` historical
  files.
- `OBSERVED_LOCAL` — current canonical four-role request: `427,220` bytes.
- `UNTESTED` — provider token count: planning band 107K–214K.
- `UNTESTED` — maximum real semantic output. The current output schema permits a
  result array and does not itself cap rationale length.

### OpenAI API

- `DOCUMENTED` — GPT-4.1 supports a 1,047,576-token context and 32,768 output
  tokens (O1).
- `DOCUMENTED` — the pinned snapshot `gpt-4.1-2025-04-14` supports Responses
  (O1).
- `UNTESTED` — account rate limit and exact full-size token count. The model page
  indicates long-context TPM varies by usage tier, so account quota is not
  assumed.
- `ACCOUNT_EVIDENCE_REQUIRED` — tier/quota sufficient for the projected request.

### Anthropic API

- `DOCUMENTED` — Sonnet 5 supports a 1M-token context and up to 128K output (A4).
- `DOCUMENTED` — Messages accepts HTTP bodies up to 32 MB (A2).
- `DOCUMENTED` — the design's 65,536 output cap is below the model maximum (A4).
- `UNTESTED` — exact token count and wire-body size.
- `ACCOUNT_EVIDENCE_REQUIRED` — token/request quota and spend limit.

### Google Gemini API

- `DOCUMENTED` — Gemini 3.8 Flash supports 1,048,576 input and 65,536 output
  tokens (G2).
- `DOCUMENTED` — an official count-token endpoint exists (G4).
- `UNTESTED` — exact token count, HTTP body limit, and account quota.
- `ACCOUNT_EVIDENCE_REQUIRED` — paid project quota and billing.

All three appear to have context margin. Only an exact inert provider projection
and provider token/usage result can convert that appearance to runtime evidence.

## Output and structured-output capability

### OpenAI API

- `DOCUMENTED` — GPT-4.1 supports Structured Outputs and Responses (O1).
- `DOCUMENTED` — schema mode supports a subset of JSON Schema (O2).
- `UNTESTED` — exact semantic-review/2.1 schema compatibility.

### Anthropic API

- `DOCUMENTED` — `output_config.format` accepts a JSON schema (A1).
- `UNTESTED` — exact frozen schema compatibility.
- `DOCUMENTED` — plain text output is available without structured-output mode
  (A1).
- `UNTESTED` — one exact text block containing one JSON document.

### Google Gemini API

- `DOCUMENTED` — structured output accepts a JSON Schema subset and may reject
  large or complex schemas (G8).
- `UNTESTED` — exact frozen schema compatibility.

The recommended first adapter uses plain JSON text and the existing runner's
strict parser/schema validator. This avoids treating any provider subset as a
silent rewrite of the frozen schema. Native structured output remains an
untested alternative settings identity, not a requirement.

## Model identity

### OpenAI API

- `DOCUMENTED` — `gpt-4.1-2025-04-14` is a listed snapshot intended to lock a
  specific model version (O1).
- `DOCUMENTED` — OpenAI recommends pinned model versions for consistent
  behavior and distinguishes model-family changes from snapshots (O2).
- `DOCUMENTED` — `gpt-4.1` is an alias and is not selected as immutable (O1).
- `UNTESTED` — model entitlement and returned model field for the candidate
  account.

### Anthropic API

- `DOCUMENTED` — `claude-sonnet-5` is a 4.6-or-later canonical model ID, not an
  evergreen alias, and maps to fixed model weights/configuration (A3).
- `DOCUMENTED` — serving infrastructure around a fixed model ID may still
  change; endpoint/API/settings commitments remain necessary (A3).
- `UNTESTED` — model access and returned model field.

### Google Gemini API

- `DOCUMENTED` — `gemini-3.8-flash` is the current stable Flash model ID and
  `*-latest` aliases hot-swap (G3).
- `DOCUMENTED` — stable models “usually” do not change, which is weaker than an
  immutable guarantee (G3).
- `DOCUMENTED` — `modelVersion` is returned only in the generation response
  (G1).
- `CONTRADICTED` — current evidence does not provide the immutable pre-call
  identity required by `BackendDescriptor`; output-only discovery is too late
  for preflight freshness authorization.

## Deployment/workspace identity

### Anthropic pre-call contract

- `ACCOUNT_EVIDENCE_REQUIRED` — before P1, a user/admin must verify the exact
  Anthropic workspace ID and provisioning must freeze
  `expected_anthropic_workspace_id_sha256 = SHA-256(exact UTF-8 workspace ID)`.
- `DOCUMENTED` — workspace-scoped API keys always run in their selected
  workspace and need no workspace selector in the inference request (A14). The
  first adapter therefore requires a workspace-scoped `ANTHROPIC_API_KEY`; an
  otherwise valid multi-workspace key is not eligible for this narrow adapter.
- `UNTESTED` — the future `BackendIdentity.deployment_identity` is determined
  before P1 from a canonical record binding provider `anthropic`, platform
  `direct_claude_api`, expected workspace-ID SHA-256, endpoint, API version,
  inference-geo policy, and adapter identity/version. The later implementation
  plan must freeze the exact serialization.
- `DOCUMENTED` — every authenticated inference response that resolves to a
  workspace includes `anthropic-workspace-id` (A5/A11). P1 and P2 must hash its
  exact UTF-8 value and compare it with the pre-frozen commitment.
- `UNTESTED` — actual header presence and equality for the future workspace.
- `CONTRADICTED` — defining deployment identity from an API-key hash or prefix,
  credential path/name, or a workspace ID first discovered after inference.

The raw workspace ID need not be stored in Git and may exist transiently only
in controller provisioning state. The persisted runner/audit identity contains
the commitment, not the raw ID. The returned header verifies the descriptor; it
cannot define or mutate it after P1. A missing or mismatched header fails closed
as `ISOLATION_CAPABILITY_UNAVAILABLE` and produces no valid capability
observation.

`INFERENCE_ADAPTER_REQUIRES_ADMIN_CREDENTIAL = NO`. The inference adapter needs
only controller-supplied `ANTHROPIC_API_KEY`. Any Admin API use is a separate,
optional controller/admin provisioning operation and credential boundary; it is
outside `ToollessInferenceBackend.invoke(...)`, never sent to the model, never
retained by the adapter, and unnecessary when equivalent PM-approved Console or
contract evidence is available.

## Inference settings identity

### OpenAI API

- `DOCUMENTED` — model, maximum output, response format, reasoning effort, and
  supported sampling settings can be explicit request values (O1/O2).
- `DOCUMENTED` — tools and state fields can be absent (O2/O5).
- `UNTESTED` — exact canonical request-body hash and default-free configuration.

### Anthropic API

- `DOCUMENTED` — model, `max_tokens`, `stream`, `service_tier`, `inference_geo`,
  adaptive thinking/effort, and output format can be explicit (A1/A9).
- `DOCUMENTED` — Sonnet 5 rejects non-default sampling settings; the design
  omits temperature, top-p, and top-k and binds their absence (A1).
- `UNTESTED` — exact canonical settings hash and provider acceptance.

### Google Gemini API

- `DOCUMENTED` — generation config exposes candidate count, maximum output,
  response format, and model-supported sampling/thinking controls (G1/G2).
- `UNTESTED` — exact supported setting set and settings hash for the selected
  model/account.

## Request ID

### OpenAI API

- `DOCUMENTED` — each API response exposes a unique `x-request-id` header (O2).
- `UNTESTED` — header presence on the candidate endpoint/account.

### Anthropic API

- `DOCUMENTED` — every API response includes a unique `request-id` header; error
  bodies repeat it as `request_id` (A2).
- `UNTESTED` — header presence and uniqueness across P1/P2.

### Google Gemini API

- `DOCUMENTED` — each generate response exposes `responseId` (G1).
- `UNTESTED` — presence and uniqueness across two calls.

The server-issued ID is the only eligible `provider_request_id`. A client UUID
or provider message ID cannot be substituted when the documented request ID is
missing.

## Retention/privacy

### OpenAI API

- `DOCUMENTED` — API data is not used to train OpenAI models unless the customer
  opts in (O3).
- `DOCUMENTED` — abuse-monitoring logs are retained up to 30 days by default,
  subject to legal requirements; eligible organizations can apply for Modified
  Abuse Monitoring or Zero Data Retention (O3).
- `DOCUMENTED` — `/v1/responses` application-state behavior depends on `store`
  and account controls; background, conversations, tools, and some caching
  features add state/eligibility caveats (O3).
- `ACCOUNT_EVIDENCE_REQUIRED` — actual project retention mode, opt-ins, region,
  and model/endpoint availability.

### Anthropic API

- `DOCUMENTED` — commercial API inputs and outputs are not used for training by
  default; feedback/explicit opt-in are exceptions (A7).
- `DOCUMENTED` — API inputs and outputs are automatically deleted within 30
  days under the standard commercial policy, with longer-lived features,
  agreements, usage-policy enforcement, legal obligations, Covered Models,
  feedback, and other stated exceptions (A8/A13).
- `DOCUMENTED` — ZDR is enabled per organization through Anthropic; each
  organization needs separate enablement. Direct Messages is ZDR-eligible when
  the selected model and features are eligible, while stateful and feature-
  specific services can have different retention (A13).
- `DOCUMENTED` — the current Covered Model list names Claude Fable 5.1, Claude
  Mythos 5.1, Claude Fable 5, and Claude Mythos 5. It does not list
  `claude-sonnet-5` as of the 2026-09-05 refresh (A13). This does not prove an
  eventual account's contract, workspace override, or future list membership.
- `DOCUMENTED` — explicit `inference_geo=us` constrains inference to US
  infrastructure and adds a 1.1x pricing multiplier (A9).
- `ACCOUNT_EVIDENCE_REQUIRED` — actual organization/workspace retention or ZDR
  arrangement, contractual exceptions, commercial data-use participation,
  feedback/privacy controls, allowed inference geography, and organizational
  acceptance must be established through the correct evidence channel below.

### Anthropic evidence channels

**A. Machine-readable provider account/workspace evidence** is limited to
officially exposed fields. The Workspace/Admin API documents workspace `id` and
`data_residency.allowed_inference_geos`, `default_inference_geo`, and
`workspace_geo` (A9/A12). A later authorized provisioning operation may collect
these with separate admin capability. No retention/ZDR/training field is
claimed as API-readable.

**B. Contract, Console, or administrator evidence** is a separately frozen,
PM/user/admin-approved provisioning record for organization ZDR, any workspace
30-day-retention override, contractual retention exceptions, explicit
commercial training/data-use participation, and applicable feedback/privacy
controls. These properties are not described as API readbacks unless a future
official endpoint exposes the exact field.

**C. Runtime response evidence** is the exact
`anthropic-workspace-id` returned by P1/P2. Its UTF-8 SHA-256 must equal the
pre-frozen expected workspace commitment. It proves which workspace the
inference credential resolved to, not retention or privacy configuration.

The three channels are not interchangeable. PM must accept the exact
retention/privacy provisioning evidence before a capability proof can run.

### Google Gemini API

- `DOCUMENTED` — paid-service prompts and responses are not used to improve
  products (G5/G7).
- `DOCUMENTED` — paid use includes limited abuse logging; ZDR requires approval
  and avoidance/configuration of stateful/storage features (G5).
- `DOCUMENTED` — optional developer logging in billing-enabled projects has a
  maximum retention setting of 7, 14, 28, or 55 days and is not used for product
  improvement by default unless shared (G6).
- `ACCOUNT_EVIDENCE_REQUIRED` — paid-project status, ZDR approval, logging
  setting, location availability, and absence of sharing/feature state.

No account privacy property was observed. All three remain unproven for real
Product Definition material.

## Endpoint stability

### OpenAI API

- `DOCUMENTED` — REST API major version is `v1`, and pinned model snapshots are
  the stated mechanism for model behavior stability (O2).
- `UNTESTED` — exact current endpoint response and account model visibility.

### Anthropic API

- `DOCUMENTED` — endpoint `POST /v1/messages` and explicit
  `anthropic-version: 2023-06-01` can be frozen (A1).
- `DOCUMENTED` — model ID `claude-sonnet-5` is pinned while serving
  infrastructure may evolve (A3).
- `UNTESTED` — endpoint/model readback for an actual workspace.

### Google Gemini API

- `DOCUMENTED` — `v1beta ...:generateContent` is a unary endpoint and stable
  model names are distinct from latest aliases (G1/G3).
- `CONTRADICTED` — the reviewed stable naming promise is not an immutable
  pre-call model revision guarantee for the current runner identity contract.

## Account-specific unknowns

| Unknown | Classification | Required future evidence |
| --- | --- | --- |
| Usable paid account/workspace | `ACCOUNT_EVIDENCE_REQUIRED` | PM/user/admin provisioning evidence; no secret output |
| Expected Anthropic workspace commitment | `ACCOUNT_EVIDENCE_REQUIRED` | SHA-256 of exact user/admin-verified UTF-8 workspace ID frozen before P1 |
| Workspace identity at runtime | `UNTESTED` | every P1/P2 `anthropic-workspace-id` response header hashes to the frozen commitment |
| Model entitlement | `ACCOUNT_EVIDENCE_REQUIRED` | exact candidate model accessible before inference |
| Long-context quota/rate limit | `ACCOUNT_EVIDENCE_REQUIRED` | exact token count plus account quota sufficient for P1/P2 |
| Retention mode | `ACCOUNT_EVIDENCE_REQUIRED` | PM-accepted contract/Console/admin record for standard policy/exceptions or verified organizational ZDR and any workspace override |
| Training/feedback/data-use controls | `ACCOUNT_EVIDENCE_REQUIRED` | PM-accepted contract/Console/admin record; no API readback claimed without an exact endpoint field |
| Inference geography | `ACCOUNT_EVIDENCE_REQUIRED` | documented Workspace/Admin fields or approved Console evidence plus explicit requested geo and response usage match |
| Spend approval | `ACCOUNT_EVIDENCE_REQUIRED` | PM-approved two-call ceiling before P1 |
| Organizational provider prohibition | `ACCOUNT_EVIDENCE_REQUIRED` | PM confirmation provider is permitted |

Missing any required account fact yields `BACKEND_PROVISIONING_REQUIRED`, not a
default assumption.

## Implementation complexity

| Candidate/transport | Classification | Narrow implementation estimate | Principal risk |
| --- | --- | --- | --- |
| Anthropic + standard-library HTTPS | `DOCUMENTED` provider fit / `UNTESTED` implementation | one provider module, one explicit registration, unit/transport tests, capability evidence update only after P1/P2 | response block selection, pre-call workspace commitment/runtime header binding, account retention proof, no-retry enforcement |
| OpenAI + standard-library HTTPS | `DOCUMENTED` provider fit / `UNTESTED` implementation | comparable one-module adapter using pinned GPT-4.1 Responses request | smaller 32,768 output ceiling; Responses storage/settings details must be explicit |
| Gemini + standard-library HTTPS | `CONTRADICTED` identity fit | adapter otherwise appears small | stable name lacks current immutable pre-call guarantee |
| Any official SDK | `UNAVAILABLE` locally / `DOCUMENTED` retry behavior for OpenAI and Anthropic | new pinned dependency and raw transport tests | hidden serialization/default retry/state surface |
| User-controlled proxy | `UNAVAILABLE` locally | new service, deployment, auth, logs, identity and audit | unnecessary second trusted boundary |

The direct Anthropic adapter is the smallest path that has no known contract
contradiction. It is still `UNTESTED`.

## Candidate disposition

### Anthropic API

`RECOMMENDED_PROVIDER_CANDIDATE`

Rationale:

- `DOCUMENTED` — one stateless direct Messages request.
- `DOCUMENTED` — tools and all stateful features can be omitted.
- `DOCUMENTED` — 32 MB request body, 1M context, and 128K output capacity.
- `DOCUMENTED` — `claude-sonnet-5` is a pinned canonical model ID.
- `DOCUMENTED` — every response carries a unique `request-id` header.
- `DOCUMENTED` — authenticated responses identify the resolved workspace; a
  pre-call user/admin-verified workspace commitment can be checked after every
  response without changing the descriptor.
- `DOCUMENTED` — explicit API version and inference geography can be bound.
- `ACCOUNT_EVIDENCE_REQUIRED` — retention/privacy, billing, model access, quota,
  geo, and the pre-frozen expected workspace commitment must be verified and
  accepted through their applicable evidence channels.
- `UNTESTED` — adapter behavior and P1/P2 synthetic isolation.

### OpenAI API

`DOCUMENTED_FALLBACK_CANDIDATE`

Rationale:

- `DOCUMENTED` — pinned 1M-context `gpt-4.1-2025-04-14`, one Responses request,
  optional tools/state, unique request header.
- `DOCUMENTED` — output limit is 32,768 tokens, lower than the Anthropic
  candidate but plausibly sufficient.
- `ACCOUNT_EVIDENCE_REQUIRED` — project retention/ZDR, quota, model access, and
  region.
- `UNTESTED` — adapter and synthetic proof.

### Google Gemini API

`NOT_CURRENTLY_ELIGIBLE_FOR_FIRST_IMPLEMENTATION`

Rationale:

- `DOCUMENTED` — unary tool-optional request, ample context, structured output,
  and response ID.
- `CONTRADICTED` — reviewed documentation does not establish the stable model
  name as an immutable pre-call revision; output-only `modelVersion` cannot
  authorize the current descriptor before invocation.
- `ACCOUNT_EVIDENCE_REQUIRED` — paid-project privacy/logging/ZDR configuration.

### Overall

`RECOMMENDED_PROVIDER_CANDIDATE = Anthropic API`

`RECOMMENDED_TRANSPORT = PYTHON_STDLIB_DIRECT_HTTPS`

`REAL_BACKEND_CAPABILITY = UNAVAILABLE`

`REAL_SYNTHETIC_PREFLIGHT = NOT_RUN`

`SEMANTIC_CALIBRATION = NOT_RUN`

`SEMANTIC_REVIEW_2_1_RELIABILITY = NOT_MEASURED`

`V0_4_4 = BLOCKED`

Correction re-evaluation: the pricing correction changes cost planning but not
runner fit. The pre-call workspace commitment plus per-response workspace-ID
comparison supplies a non-secret deployment-binding path without weakening the
existing descriptor contract. The separated privacy evidence channels provide
a truthful provisioning path without a fictional retention API field or hidden
adapter admin credential. Gemini 3.8 Flash retains the same weaker “usually”
stable pre-call identity evidence. Anthropic therefore remains the preferred
candidate with no identified runner-contract contradiction, while all real
behavior and account gates remain `UNTESTED` or `ACCOUNT_EVIDENCE_REQUIRED`.

The next task, only after PM design approval, may write an implementation plan.
It must not infer that this candidate disposition authorizes provider
provisioning, paid calls, adapter implementation, or capability promotion.
