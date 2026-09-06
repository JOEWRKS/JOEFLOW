# Anthropic provider-policy freshness audit

Status: `READY_FOR_PM_REVIEW`

Retrieval date: `2026-09-06`

Repository authority:

- main: `9c4f3f7c09aa391645a3f298bc113976f2c8c185`
- tree: `a68c606587b67d1931f49f96c10f78c578784d90`
- provider implementation authority: `2b137125ad87fafabc93e7492729da441c9b9cce`
- provider implementation tree: `bd5ffa19203561b3c73432933be4ea77cfa54efd`

This is provider-policy research and compatibility evidence only. It does not
provision an account or credential, call a provider endpoint, establish an
`OBSERVED_PASS`, authorize P1/P2, or change production code. The promoted
capability remains `UNAVAILABLE`.

## Scope and authority boundary

The exact cross-system authority contract was read from
`JOEWRKS/joewrks-work-harness` commit
`5e7497bd104527d5e6dbfc36011f0f5ee3668ff5`. Under that contract, JOEFLOW owns
lifecycle progression, not provider or product truth. Provider documentation
and account evidence can prove a progression gate; they do not create Product
Definition or JOEDESIGN authority.

Only current first-party Anthropic documentation was used. No Anthropic API,
Token Counting, Admin API, Console automation, credential source, or environment
variable was accessed. When official pages differ, the promoted design's source
policy controls: prefer a current model-specific or explicitly dated source,
record the conflict, and fail closed when it cannot be resolved.

## Current compatibility conclusion

The promoted direct-HTTPS adapter remains compatible with the current official
contract. Its `x-api-key` header is still supported, a single-workspace key may
omit request-time workspace selection, `claude-sonnet-5` remains a pinned model
ID with the required capacity, and an inference request does not require an
Admin credential.

The historical candidate audit is no longer sufficient as the sole future
`provider_official_contract_sha256` authority. Current documentation adds
material authentication-key guidance and a more precise retention model. The
smallest evidence-safe choice is option C: bind a PM-approved freshness and
compatibility snapshot, while retaining the historical candidate audit
unchanged as design evidence.

## Authentication

Current official facts:

- Direct Claude API requests accept `Authorization: Bearer <API key>` as the
  primary API-key form. `x-api-key` remains supported as a legacy fallback.
- `anthropic-version` and `content-type: application/json` remain required for
  the direct Messages request.
- A personal or service-account API key can be scoped to exactly one workspace.
  Such a key always runs in that workspace and can omit
  `anthropic-workspace-id` on the request.
- A multi-workspace identity-backed key requires
  `anthropic-workspace-id` on every request. The promoted adapter does not send
  that request header, so such a key is not eligible for this closed adapter.
- Legacy workspace keys still work, but Anthropic recommends identity-backed
  personal/service-account keys or Workload Identity Federation for new
  integrations.
- Personal keys are appropriate for one developer's own development work.
  Service-account keys are the current recommended API-key type for shared or
  unattended automation. For JOEFLOW, the future credential should therefore
  be a service-account key scoped to the approved single workspace.
- The Messages inference adapter requires no Admin API credential. Admin access
  is optional and separate when an administrator chooses machine-readable
  provisioning evidence instead of Console/contract evidence.

Compatibility result:

`INFERENCE_ADAPTER_REQUIRES_ADMIN_CREDENTIAL = NO`

The current `x-api-key` implementation remains supported. Moving to the newer
`Authorization` preference or Workload Identity Federation would change the
frozen adapter/authentication boundary and is not required for P1/P2 readiness.

Sources:

- [Authentication — Claude Platform Docs](https://platform.claude.com/docs/en/manage-claude/authentication)
- [API overview — Claude Platform Docs](https://platform.claude.com/docs/en/api/overview)
- [Versions — Claude Platform Docs](https://platform.claude.com/docs/en/api/versioning)

## Workspace identity and evidence channels

Current official facts:

- Workspace IDs use the `wrkspc_` prefix.
- A single-workspace personal/service-account key selects its workspace at key
  creation and can omit request-time workspace selection.
- Successful Claude API responses identify the resolved workspace in
  `anthropic-workspace-id`, alongside `request-id` and
  `anthropic-organization-id`.
- Console Settings -> Workspaces exposes workspace identity and configuration.
- The Admin API can supply workspace identity and the documented
  `data_residency` fields when separately authorized. Admin credentials are not
  needed by the inference adapter and must never enter it.
- Workspace restrictions expose `allowed_inference_geos` and
  `default_inference_geo`; workspace geo is currently `us` and is fixed at
  workspace creation.
- Workspace spend and rate limits are visible/configurable in Console. A
  dedicated non-default workspace is preferable because the Default Workspace
  cannot receive workspace limit overrides.

Runtime `anthropic-workspace-id` proves only which workspace served that
request. It does not prove retention, privacy, model entitlement, quota, or
spend approval. Those channels remain separate.

Sources:

- [Workspaces — Claude Platform Docs](https://platform.claude.com/docs/en/manage-claude/workspaces)
- [Data residency — Claude Platform Docs](https://platform.claude.com/docs/en/manage-claude/data-residency)
- [Admin API — Claude Platform Docs](https://platform.claude.com/docs/en/manage-claude/overview)
- [Rate Limits API — Claude Platform Docs](https://platform.claude.com/docs/en/manage-claude/rate-limits-api)

## Model identity and capacity

Current official facts:

- `claude-sonnet-5` is the canonical API ID for Claude Sonnet 5.
- Model IDs in the 4.6 generation and later are pinned snapshots. Anthropic does
  not change the weights or configuration behind an existing ID, although the
  surrounding serving infrastructure may change.
- Sonnet 5 has a 1,000,000-token context window and a 128,000-token maximum
  output. The promoted adapter's `max_tokens = 65,536` remains inside that
  output limit.
- Messages and Token Counting requests each have a documented 32 MB request
  limit.
- Sonnet 5 uses a newer tokenizer that may produce about 30% more tokens for the
  same text than Sonnet 4.6. Existing rough byte-to-token estimates therefore
  remain planning evidence, not an exact token measurement.
- Sonnet 5 is available on the direct Claude API, but the selected account's
  actual entitlement and rate/quota headroom remain account evidence.

No model or capacity contradiction was found. Actual account entitlement and
quota stay `ACCOUNT_EVIDENCE_REQUIRED`.

Sources:

- [What's new in Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5)
- [Model IDs and versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
- [Claude API errors and request-size limits](https://platform.claude.com/docs/en/api/errors)
- [Rate limits](https://platform.claude.com/docs/en/api/rate-limits)

## Pricing

Current controlling official sources state:

- Sonnet 5 base input: `$2.00 / MTok`.
- Sonnet 5 base output: `$10.00 / MTok`.
- Explicit `inference_geo = us` applies a `1.1x` multiplier to all token
  categories, making the effective planning rates `$2.20 / MTok` input and
  `$11.00 / MTok` output.

An English generic pricing rendering still exposed the superseded scheduled
September 1 increase to `$3/$15`. The current Sonnet 5 model page and the dated
release notes state that `$2/$10` became the standard rate on August 10, 2026;
those more specific/current sources control. The promoted rate conclusion is
therefore unchanged.

No exact bill is claimed. The exact input token count has not been measured,
and the output can terminate below the configured maximum.

Sources:

- [What's new in Claude Sonnet 5 — pricing](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#pricing)
- [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- [Data residency pricing](https://platform.claude.com/docs/en/manage-claude/data-residency#pricing)

## Retention and privacy

The old promoted summary, considered alone, is incomplete. The current official
sources distinguish the standard commercial deletion window, feature-level
storage, Covered Models, contractual ZDR, and exceptional retention.

Current official facts:

1. The commercial retention policy still says Anthropic API inputs and outputs
   are automatically deleted from backend systems within 30 days, subject to
   longer-lived customer-controlled features, a different agreement, Usage
   Policy enforcement, and legal obligations.
2. The current API-specific retention page additionally says conversation
   content is not retained by default, except for Covered Models that require
   30-day retention. The commercial 30-day statement is therefore an outer
   deletion bound, not sufficient proof that every normal Messages payload is
   stored for 30 days.
3. Under a ZDR arrangement, Anthropic does not store prompts or responses at
   rest after the response returns. ZDR is enabled per organization; it does
   not automatically extend to other organizations.
4. Direct Messages, Token Counting, 1M context, adaptive thinking, effort, and
   data residency are listed as ZDR-eligible when used with an eligible model
   and feature set.
5. The current Covered Model list names Claude Fable 5.1, Claude Mythos 5.1,
   Claude Fable 5, and Claude Mythos 5. It does not name Sonnet 5. The Sonnet 5
   model page separately states that Sonnet 5 supports ZDR for organizations
   with ZDR agreements.
6. In a ZDR organization, a workspace can enable a 30-day retention override
   to use Covered Models; workspaces without an override continue following the
   organization default. This override is not presently required for Sonnet 5.
7. Legal holds and trust-and-safety flags remain exceptions under every
   arrangement. Flagged inputs/outputs may be retained for up to two years; the
   commercial policy also states trust-and-safety classification scores may be
   retained for up to seven years.
8. Commercial API inputs/outputs are not used for model training by default.
   Explicit opt-in or feedback can permit use. Feedback submissions may retain
   the related content for up to five years.

The exact organization's contract, ZDR state, workspace override, feedback or
data-use settings, and acceptance are not exposed by an inference response.
They remain `ACCOUNT_EVIDENCE_REQUIRED` and must be frozen through
contract/Console/administrator evidence before P1.

Sources:

- [Commercial data retention policy](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data)
- [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- [Covered Model retention practices](https://privacy.claude.com/en/articles/15425996-data-retention-practices-for-covered-models)
- [Commercial training and feedback policy](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)
- [Sonnet 5 availability and ZDR](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5#availability)

## Promoted claim versus current official claim

| Fact | `PROMOTED_2026_09_05_CLAIM` | `CURRENT_OFFICIAL_PROVIDER_CLAIM` | Classification | Impact |
| --- | --- | --- | --- | --- |
| Direct API-key header | Adapter sends `x-api-key` | `Authorization: Bearer` is now primary; `x-api-key` remains a supported legacy fallback | `CLARIFIED` | No code change; the existing header remains compatible |
| Credential type | Use one key scoped to the approved workspace | Prefer a single-workspace identity-backed service-account key for unattended automation; legacy workspace keys still work | `CLARIFIED` | Provision a service-account key, not a new legacy workspace key |
| Workspace selection | A workspace-scoped key can omit request workspace selection | A single-workspace personal/service-account key can omit the header; a multi-workspace key cannot | `CLARIFIED` | Multi-workspace keys remain ineligible for the closed adapter |
| Inference Admin credential | Not required | Not required; Admin access is separate and optional for provisioning evidence | `UNCHANGED` | Preserve the adapter boundary |
| Workspace identity | `wrkspc_` ID and response header | Same, with `anthropic-workspace-id` on workspace-resolved responses | `UNCHANGED` | Existing pre-call hash and response check remain valid |
| Model identity | `claude-sonnet-5` is pinned | Same canonical pinned snapshot; serving infrastructure may evolve | `UNCHANGED` | No adapter/model change |
| Model capacity | 1M context / 128K output | Same; new tokenizer warning remains material | `UNCHANGED` | Keep account quota and exact-use proof separate |
| Base price | `$2/$10` per MTok | `$2/$10` is the standard Sonnet 5 rate | `UNCHANGED` | Use `$2.20/$11.00` with US-only multiplier |
| Standard API retention | Inputs/outputs deleted within 30 days, with exceptions | Commercial policy retains that upper bound; API-specific guidance says conversation content is not retained by default except Covered Models | `CLARIFIED` | The old sentence alone cannot be future policy authority |
| Sonnet 5 Covered Model status | Not listed as Covered | Still not listed; model page explicitly says Sonnet 5 supports ZDR | `CLARIFIED` | No Covered-Model override is presently required |
| ZDR enablement | Per organization; Messages eligible | Same, with current feature-level table and workspace override behavior | `UNCHANGED` | Contract/Console verification still required |
| Training default | Commercial API data not used by default | Same; explicit opt-in and feedback remain exceptions | `UNCHANGED` | Freeze account data-use/feedback acceptance |
| Actual workspace/account state | Unproven | Not inferable from public docs | `ACCOUNT_EVIDENCE_REQUIRED` | Blocks P1 until supplied and approved |
| Entitlement, quota, and spend | Unproven | Account-specific | `ACCOUNT_EVIDENCE_REQUIRED` | Blocks P1 until supplied and approved |

No current official claim contradicts the frozen adapter request shape. The
policy clarifications do make the historical candidate audit alone an
insufficient freshness commitment for a future paid proof.

## `provider_official_contract_sha256` ruling recommendation

### Current historical expectation

The implementation plan expected this field to hash the approved bytes of
`BACKEND_CANDIDATE_CAPABILITY_AUDIT.md`. That artifact must remain unchanged as
historical design evidence.

### Options

- **A — historical candidate audit unchanged:** rejected. It would bind an
  incomplete current authentication/retention description and would not prove
  that the PM saw the 2026-09-06 compatibility findings.
- **B — rewrite or replace the candidate audit:** rejected as larger and
  history-blurring. The candidate selection itself did not change.
- **C — PM-approved provider-policy freshness snapshot:** recommended. Keep the
  historical audit intact and bind the exact approved bytes of this freshness
  audit as the current provider-policy compatibility authority.

### Exact future authority rule

After PM review, a separate approval operation must identify the exact commit,
Git blob, byte count, and SHA-256 of
`PROVIDER_POLICY_FRESHNESS_AUDIT.md`. The value written to
`provider_official_contract_sha256` must be SHA-256 of those exact file bytes,
not a caller-supplied summary and not a digest copied before approval. The
approval record must state that:

- the historical candidate audit remains design evidence;
- the current snapshot is compatible with the unchanged adapter;
- option C is accepted;
- the standard-retention or ZDR account posture is still a separate
  provisioning decision; and
- any later provider-policy change invalidates freshness and requires a new
  snapshot/digest before another capability proof.

`PM_COMPATIBILITY_APPROVAL_REQUIRED = YES`

The template deliberately leaves `provider_official_contract_sha256 = null`
until that approval is recorded.

## Audit disposition

- Production code change required: `NO`
- Provider policy compatibility: `DOCUMENTED_COMPATIBLE`
- Account evidence complete: `NO`
- Credential provisioned: `NO`
- P1/P2 authorized: `NO`
- Real backend capability: `UNAVAILABLE`
- Readiness disposition: `READY_FOR_PM_REVIEW`
