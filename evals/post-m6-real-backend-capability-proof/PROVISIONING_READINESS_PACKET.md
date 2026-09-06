# Anthropic provisioning readiness packet

Status: `READY_FOR_PM_REVIEW`

Prepared: `2026-09-06`

This packet tells the PM/user what must be supplied and approved before a
future P1 capability-proof call. It performs no provisioning, reads no
credential, and authorizes no provider request.

## Frozen JOEFLOW authority

- main: `9c4f3f7c09aa391645a3f298bc113976f2c8c185`
- tree: `a68c606587b67d1931f49f96c10f78c578784d90`
- implementation code: `2b137125ad87fafabc93e7492729da441c9b9cce`
- implementation tree: `bd5ffa19203561b3c73432933be4ea77cfa54efd`
- adapter: `anthropic-direct-messages/1.0.0`
- endpoint: `https://api.anthropic.com/v1/messages`
- model: `claude-sonnet-5`
- inference geography: `us`
- application retries: `0`
- current capability: `UNAVAILABLE`
- synthetic preflight: `NOT_RUN`

The cross-system boundary comes from
`JOEWRKS_CROSS_SYSTEM_AUTHORITY_V1.md` at exact work-harness commit
`5e7497bd104527d5e6dbfc36011f0f5ee3668ff5`. This packet is JOEFLOW
progression evidence only and creates no Product Definition or JOEDESIGN
authority.

## Decisions requested from PM/user

The next authorization must resolve all of these without supplying a secret in
chat or Git:

1. Select the exact Anthropic commercial organization.
2. Select or create a dedicated workspace and verify its `wrkspc_...` ID.
3. Confirm that a service account is permitted and is a member of that
   workspace.
4. Choose one retention posture:
   `STANDARD_RETENTION_ACCEPTED` or `ZDR_VERIFIED`.
5. Accept the documented commercial data-use/privacy posture, including the
   feedback/opt-in and flagged/legal-retention exceptions.
6. Confirm that explicit US-only inference is permitted and accept its `1.1x`
   token-price multiplier.
7. Verify that `claude-sonnet-5` is available to the selected workspace.
8. Verify that account/workspace rate limits and quota can accommodate one
   separately authorized Token Counting request followed by exactly two
   full-size synthetic Messages requests.
9. Approve or replace the proposed `$5.00 USD` P1+P2 spend ceiling.
10. Approve option C for the current provider-policy authority: the exact
    PM-approved freshness snapshot, not the historical candidate audit alone.

Until all ten are resolved, `BACKEND_PROVISIONING_REQUIRED` remains truthful.

## Credential operation — future task only

Recommended credential type for this automated workload:

`SINGLE_WORKSPACE_IDENTITY_BACKED_SERVICE_ACCOUNT_API_KEY`

The future organization administrator should create or select a service
account, grant it access only to the approved workspace, and create an API key
scoped to that workspace. A personal key is appropriate for one person's own
tooling or development; a service-account key is appropriate for this shared,
unattended workload. WIF is preferable when a production workload already has
a federatable platform identity and long-lived static secrets should be
avoided, but it is not selected here because it would change the frozen static-
key adapter boundary. This recommendation is not a universal preference for
static service-account keys over WIF. A legacy workspace key should not be
created for a new integration.

The key operation must obey all of these rules:

- provide the value to the authorized controller only through
  `ANTHROPIC_API_KEY`;
- never paste it into a prompt, issue, document, log, test, or evidence file;
- never commit it;
- never print it or expose its prefix;
- never hash it as deployment or credential identity;
- do not use a multi-workspace key, because the frozen adapter intentionally
  omits request-time `anthropic-workspace-id` selection;
- keep any Admin API credential separate from inference; and
- rotate/disable/delete it through Anthropic's supported controls if exposure
  is suspected.

Current credential readiness: `NOT_PROVISIONED`.

Current official renderings differ in whether `Authorization: Bearer` or
`x-api-key` is presented for direct API-key use. Both support the frozen
adapter's `x-api-key` header, so the rendering conflict is non-normative and no
adapter change is required.

`AUTH_HEADER_COMPATIBILITY = DOCUMENTED_COMPATIBLE`

`AUTH_PRIMARY_PRESENTATION = OFFICIAL_SOURCE_RENDERING_CONFLICT_NON_NORMATIVE`

## Machine evidence versus admin evidence

### Available from documented runtime/API fields after separate authorization

- `request-id` on every provider response;
- `anthropic-workspace-id` on workspace-resolved responses;
- response model identity;
- `usage.input_tokens` and `usage.output_tokens`;
- response `usage.inference_geo`;
- exact HTTP status and response envelope;
- optional Admin API workspace ID and documented `data_residency` fields;
- optional Admin/Rate Limits API key scope/status/expiry and limit evidence.

Runtime response fields cannot prove the account's retention agreement,
training/feedback setting, organizational provider approval, or PM spend
approval.

### Requires contract, Console, administrator, or user evidence

- selected organization and workspace ownership;
- service-account membership and single-workspace key scope;
- standard-retention acceptance or organization-level ZDR enablement;
- any workspace retention override;
- contractual/legal retention qualifications;
- commercial data-use and feedback/opt-in posture;
- permission for US-only inference;
- current model entitlement;
- quota/rate-limit headroom;
- approved spend ceiling; and
- current provider-policy compatibility approval.

Console/contract evidence may be used instead of Admin API calls. An Admin
credential is not a dependency of `AnthropicBackend.invoke()`.

## Exact provisioning fields

Every field below is non-secret. A digest is a commitment to an approved
non-secret evidence artifact; it is never an API-key hash. All 14 fields are
required before P1.

| # | Field | Evidence source | Current state | Supplier | Secret? | Required before P1? |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `schema_version` | Promoted admission code constant | `AVAILABLE` as `joewrks.anthropic-provisioning-evidence/1.0` | JOEFLOW/controller | No | Yes |
| 2 | `expected_anthropic_workspace_id_sha256` | SHA-256 of the exact admin/user-verified UTF-8 workspace ID | `UNAVAILABLE` | User/admin supplies ID to later controller operation; controller retains only digest | No; raw ID is not committed | Yes |
| 3 | `workspace_key_scope` | Console or API-key metadata | `UNAVAILABLE`; must be `WORKSPACE_SCOPED` | Organization admin | No | Yes |
| 4 | `workspace_evidence_channel` | Declared channel for the workspace proof | `UNAVAILABLE`; `MACHINE_READABLE` or `CONSOLE_OR_ADMINISTRATOR` | PM/user + controller | No | Yes |
| 5 | `workspace_evidence_sha256` | Exact approved workspace evidence bytes | `UNAVAILABLE` | Controller after user/admin evidence | No | Yes |
| 6 | `retention_privacy_evidence_channel` | Contract/Console/admin record | `UNAVAILABLE`; must be `CONTRACT_CONSOLE_OR_ADMINISTRATOR` | User/admin | No | Yes |
| 7 | `retention_privacy_evidence_sha256` | Exact approved retention/privacy record bytes | `UNAVAILABLE` | Controller after user/admin evidence | No | Yes |
| 8 | `retention_privacy_approval` | Explicit PM/user decision | `UNAVAILABLE`; choose `STANDARD_RETENTION_ACCEPTED` or `ZDR_VERIFIED` | PM/user | No | Yes |
| 9 | `inference_geo_evidence_sha256` | Console/Admin geo policy plus accepted `us` request policy | `UNAVAILABLE` | User/admin + controller | No | Yes |
| 10 | `model_entitlement_evidence_sha256` | Console/account evidence for `claude-sonnet-5` | `UNAVAILABLE` | User/admin + controller | No | Yes |
| 11 | `capacity_and_quota_evidence_sha256` | Account/workspace rate/quota evidence plus the closed capacity record containing the exact frozen body measurement and pre-P1 Token Counting result | `UNAVAILABLE` | User/admin + controller | No | Yes |
| 12 | `spend_approval_evidence_sha256` | Exact PM/user spend approval record | `UNAVAILABLE`; proposal only | PM/user + controller | No | Yes |
| 13 | `provider_policy_approval_evidence_sha256` | Exact PM-approved provider freshness/compatibility record | `UNAVAILABLE` | PM/user + controller | No | Yes |
| 14 | `credential_readiness_evidence_sha256` | Deterministic controller-boundary commitment over the other non-secret provisioning bindings | `UNAVAILABLE` until later credential readiness is established | Authorized controller | No; never derived from key bytes | Yes |

The admission wrapper additionally requires the exact schema version and these
five non-secret commitments, all still `null` in the template:

| Field | Required evidence before P1 |
| --- | --- |
| `adapter_source_manifest_sha256` | Exact promoted adapter/audit source manifest |
| `local_conformance_evidence_sha256` | Exact accepted offline conformance evidence |
| `canonical_provider_body_sha256` | Exact frozen synthetic P1 provider-body bytes |
| `provider_official_contract_sha256` | Exact PM-approved current freshness snapshot bytes (recommended option C) |
| `local_capacity_measurement_sha256` | Exact non-secret capacity record binding request/body bytes, separately authorized Token Counting request identity and `exact_provider_input_tokens`, documented limits, configured maximum output, and the resulting inequality proof |

## Spend readiness

Current official Sonnet 5 rates are `$2.00/MTok` input and `$10.00/MTok`
output. US-only inference applies `1.1x`, so the planning rates are
`$2.20/MTok` input and `$11.00/MTok` output.

The current model-specific Sonnet 5 page plus the explicitly dated release
note control these rates. Generic pricing renderings may be stale or
inconsistent and do not override those sources under the frozen
source-conflict policy.

The promoted measurements are:

- inert source package: `319,066` bytes;
- canonical runner request: `427,220` bytes;
- prior planning band: approximately `107,000–214,000` input tokens;
- adapter maximum output: `65,536` tokens per call;
- billable inference calls: exactly `2` (P1 and P2), with zero application
  retries;
- separately governed Token Counting calls: exactly `1` before P1, free of
  token charges under the current provider documentation but still an
  authenticated external request.

To account conservatively for Sonnet 5's newer tokenizer without pretending it
is an exact measurement, this proposal uplifts the old high estimate by 30%:

```text
input planning bound per call = 214,000 * 1.30 = 278,200 tokens
US input maximum for two calls = 0.2782 MTok * $2.20 * 2 = $1.22408
US output maximum for two calls = 0.065536 MTok * $11.00 * 2 = $1.441792
calculated two-call bound = $2.665872
proposed operational ceiling = $5.00 USD
```

`PROPOSED_P1_P2_SPEND_CEILING_USD = 5.00`

`SPEND_APPROVAL_STATUS = PENDING_USER_APPROVAL`

The proposal covers only the two Messages calls, not retries, calibration,
provisioning fees, taxes, or later work. The required Token Counting request
has no token charge under current provider documentation, but remains an
external authenticated interaction. Actual Messages billing depends on
provider token usage; no exact bill is asserted.

Sources:

- [Sonnet 5 model and pricing](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5)
- [Data residency pricing](https://platform.claude.com/docs/en/manage-claude/data-residency#pricing)

## Token Counting decision

The previously recommended option A is rejected under the current promoted
admission contract. All 17 capability observations must already be pre-call
`OBSERVED_PASS`, and `sufficient_payload_capacity` depends on a closed capacity
record containing `exact_provider_input_tokens`. P1 cannot produce an
admission prerequisite needed to authorize P1 itself, and P1/P2 output never
backfills admission evidence.

Option B is required: make one separately authorized Token Counting request
after provisioning and before P1. Token Counting is authenticated, external,
provider-facing, free of token charges under current documentation, and
independently rate-limited. It is not inference, a reviewer execution, P1, P2,
or an application retry.

`TOKEN_COUNTING_BEFORE_P1 = REQUIRED`

`EXTERNAL_TOKEN_COUNT_REQUEST_REQUIRED = YES`

Required future order:

1. Freeze account, workspace, privacy, and spend provisioning evidence.
2. Freeze the exact P1 synthetic request and exact provider projection.
3. Separately authorize one Token Counting request.
4. Execute Token Counting against `claude-sonnet-5`.
5. Freeze the exact returned input-token estimate and request identity.
6. Complete the non-secret local capacity record.
7. Freeze account quota/capacity evidence.
8. Compile all 17 capability observations.
9. Require `17/17` pre-call `OBSERVED_PASS`.
10. Freeze the descriptor.
11. Only then authorize P1.
12. Follow a successful P1 with distinct P2.
13. Never use P1/P2 to backfill admission evidence.

No Token Counting request occurred in this readiness revision.

Source:

- [Token counting — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/token-counting)

## Capacity record ruling

Before P1, `local_capacity_measurement_sha256` must commit a non-secret record
with a non-null `exact_provider_input_tokens` obtained from the separately
authorized Token Counting request. It must bind the exact request/projection
identity and prove:

```text
exact_provider_input_tokens + 65,536 <= 1,000,000
65,536 <= 128,000
exact_provider_body_bytes < 32,000,000
```

The same closed evidence set must prove that account/workspace quota is
sufficient and that the approved spend ceiling covers the two Messages calls.
The 30%-uplift estimate is only pre-authorization cost planning and must not be
substituted for `exact_provider_input_tokens`.

## Future external request accounting

The future proof packet must distinguish these counters before execution:

| Interaction | Count | Accounting class |
| --- | ---: | --- |
| Token Counting before P1 | `1` | `external_control_plane_provider_requests` |
| P1 | `1` | `reviewer_inference_requests` |
| P2 after successful P1 | `1` | `reviewer_inference_requests` |

Expected maximum provider interactions for this capability-proof wave: `3`,
assuming zero retries, no Admin API call, and no additional provider call.
Console or contract evidence should be gathered manually where possible. Any
future Admin API request needs separate authorization and increases the count.

No v1.1 schema is changed here. If `real_provider_request_count` is used in the
future evidence packet, that packet must explicitly state whether it counts all
provider-facing requests or inference requests only; its semantics must not be
inferred.

## `provider_official_contract_sha256`

Current historical expectation: hash the approved bytes of
`BACKEND_CANDIDATE_CAPABILITY_AUDIT.md`.

Recommended future authority: option C, the exact PM-approved bytes of
`PROVIDER_POLICY_FRESHNESS_AUDIT.md`, identified by commit, Git blob, byte
count, and SHA-256 at approval time. The historical candidate audit remains
unchanged and continues to explain provider selection.

`PM_COMPATIBILITY_APPROVAL_REQUIRED = YES`

Until approval, both `provider_official_contract_sha256` and
`provider_policy_approval_evidence_sha256` remain `null`.

## Canonical-LF proof execution gate

This readiness worktree was materialized under a Windows CRLF configuration;
the resulting broad-suite runner source-byte/mode failures are an environment
limitation, not readiness-success evidence. The real capability proof must not
run from this worktree.

Before any credential presence check, credential read, Token Counting call, or
other provider request, the future proof executor must establish all of these:

- create the proof worktree with command-scoped `core.autocrlf=false` and
  `core.eol=lf`;
- verify that every tracked Reviewer Runner raw byte sequence equals its Git
  blob;
- verify that the worktree is clean; and
- pass the frozen freshness/audit baseline.

Failure terminates the wave as:

`REAL_BACKEND_CAPABILITY_PROOF_BLOCKED — NONCANONICAL_WORKTREE`

After that failure, credential access and provider requests are forbidden.

## P1/P2 readiness contract

Before P1 can be separately authorized, all of the following must be true:

1. Current main SHA/tree are re-frozen with no unexpected movement.
2. The canonical-LF worktree gate passes before any provider or credential
   operation.
3. Exact adapter source manifest and local conformance evidence are frozen.
4. The current provider-policy snapshot is exact, hash-bound, and PM-approved.
5. Exact organization/workspace selection is approved.
6. The verified workspace ID commitment is frozen before any provider request.
7. A single-workspace service-account API key is ready only in the authorized
   controller's `ANTHROPIC_API_KEY` environment source.
8. Standard retention is explicitly accepted, or organization-level ZDR is
   verified; applicable exceptions and workspace overrides are recorded.
9. Commercial data-use, feedback/opt-in, and privacy posture are accepted.
10. US inference is permitted and its evidence is frozen.
11. Sonnet 5 entitlement is verified for the workspace.
12. The P1+P2 spend ceiling is approved and hash-bound.
13. Credential readiness is committed without exposing, persisting, printing,
    or hashing the secret bytes into evidence.
14. The exact synthetic request and canonical provider projection are frozen.
15. One Token Counting request is separately authorized and executed against
    that exact projection; its request identity and non-null
    `exact_provider_input_tokens` are frozen.
16. The closed local capacity record proves the context, maximum-output, and
    body-size inequalities, and account/workspace quota evidence is complete.
17. All 17 required capability observations compile to pre-call
    `OBSERVED_PASS` from their exact evidence dependencies.
18. The backend descriptor is frozen and unchanged across the proof.
19. The package contains only the inert isolation probe and fresh nonce; no
    calibration, oracle, golden, Product Definition, customer, or prior-review
    content is present.

P2 remains a distinct fresh synthetic request after a successful P1. A failed
or ambiguous P1 stops the wave; P2 is not a retry. Neither P1 nor P2 can
backfill an admission or capacity prerequisite.

## Missing prerequisites and terminal status

Currently missing:

- organization/workspace selection and workspace commitment;
- service-account and workspace-scoped credential readiness;
- retention/privacy posture and account evidence;
- current provider-policy compatibility approval;
- model entitlement and quota/capacity evidence;
- US inference acceptance/evidence;
- spend approval;
- a canonical-LF proof worktree and passing raw-byte/audit baseline;
- exact admission commitments and frozen P1 provider projection;
- separate Token Counting authorization, execution, request identity, and exact
  token estimate;
- the closed capacity record and its inequality proof;
- pre-call 17-observation `OBSERVED_PASS` compilation; and
- separate P1/P2 execution authorization.

Current machine state remains:

- adapter implementation: `IMPLEMENTED`
- registered real adapters: `1`
- backend provisioning: `REQUIRED`
- real capability: `UNAVAILABLE`
- synthetic preflight: `NOT_RUN`
- provider requests: `0`
- calibration: `CALIBRATION_NOT_RUN`
- reliability: `NOT_MEASURED`
- v0.4.4: `BLOCKED`
- real calibration attempts / valid runs: `1 / 0`

`READINESS_STATUS = READY_FOR_PM_REVIEW`

This is not `READY_FOR_PREFLIGHT`.

## Safety attestation for this readiness wave

- Anthropic API calls: `0`
- Token Counting calls: `0`
- Admin API calls: `0`
- external control-plane provider requests: `0`
- reviewer inference requests: `0`
- credential presence checks: `0`
- credential reads: `0`
- provisioning actions: `0`
- P1/P2: `NOT_RUN`
- semantic calibration: `NOT_RUN`
