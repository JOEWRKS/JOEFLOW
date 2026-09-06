# Implementation Handoff

> Common human-readable planning handoff. This historical template path does
> not make Figma mandatory. Preserve the approved Product Definition meaning;
> include optional tool blocks only when the corresponding work was selected.

## Common planning specification

The following sections apply to every implementation consumer. Link existing
approved specifications by exact path and stable ID instead of independently
redefining the same product meaning.

## Objective, scope, and non-goals

State the user outcome, included requirement/action boundary, explicit
exclusions, and external dependencies. Do not use tool limitations as
automatic approval to change product scope; preserve already-approved
platform and environment constraints.

## Approved sources and identity

- Canonical Product Definition: `{{CANONICAL_STATE_PATH}}`
- Approved revision: `{{APPROVED_DEFINITION_REVISION}}`
- Approved definition digest: `{{APPROVED_DEFINITION_DIGEST}}`
- Approval identity:
  - State `0.2.0`: Approval Manifest digest
    `{{APPROVED_MANIFEST_DIGEST}}` is required; do not use `NOT_APPLICABLE`
    to bypass a missing current V2 Manifest.
  - Legacy: use the exact approval information from the selected frozen
    state/contract; do not require or generate a V2 Approval Manifest.
- Existing Product Definition / user-flow / screen specifications and
  applicable stable IDs: `{{APPROVED_SPEC_PATHS_AND_IDS}}`

Use these links as authority. Do not duplicate them as independently editable
planning definitions.

## Users, roles, and permissions

For each actor, state view access, available actions, mutation authority,
authentication/session conditions, and explicitly forbidden behavior.

## Target environment, responsive behavior, and accessibility

Link the exact approved sources for target platforms, devices, and execution
environments. Preserve approved responsive behavior and accessibility
requirements in this common specification; follow the applicable visual
authority for visual layout and expression. A different implementation tool
must not omit or change these product requirements. Do not invent new platform
support, breakpoints, accessibility metrics, or policy.

## IA and navigation relationships

Describe information hierarchy, each screen's purpose, entry conditions,
connections to other screens, and the stable IDs that bind those relationships.

## User flows and outcomes

For each flow/action, connect preconditions, actions, branches, and results to
postconditions, visible outcomes, side effects, and acceptance IDs. Separate
actor actions from system decisions.

## Screens, states, inputs, and data changes

For each screen/action, describe applicable domain and interaction states,
input acceptance/rejection, data read/write/persistence, and the visible
before/after result.

## Failures and recovery

Describe failures, cancellation, interruption, and recovery, including
permission loss, validation rejection, stale/conflict behavior, retry,
idempotent replay, and preservation of user input where authority requires it.

## Acceptance criteria and forbidden changes

Bind acceptance to requirements, flows, screens, states, data effects, and
failure/recovery branches. List product meanings the implementation must not
add, remove, merge, or reinterpret.

## Remaining decisions and questions

List only unresolved product choices that cannot be answered from current
evidence. For each, record affected IDs, inspected sources, why evidence is
insufficient, decision owner, options, and a recommendation when appropriate.
Do not present a question as an approval.

## Optional tool guidance

Remove this section when no optional tool was selected, or mark the applicable
block `NOT USED`. These statuses are human-readable only and are not
runtime/schema enums.

### Figma Design low-fi visualization — include only when requested

- Status: `{{FIGMA_DESIGN_STATUS_OR_OMIT}}`
- File/frame evidence when observed: `{{FIGMA_DESIGN_EVIDENCE_OR_NOT_VERIFIED}}`
- Stable screen/frame/state mapping: `{{FIGMA_STABLE_ID_MAPPING}}`

Apply stable IDs and the approved screen/flow meaning. Do not invent visual
authority or treat a low-fi visualization as Figma Make implementation.

### Figma Make implementation — include only when selected

- Status: `{{FIGMA_MAKE_STATUS_OR_OMIT}}`
- Execution instructions/output location: `{{FIGMA_MAKE_EXECUTION_AND_OUTPUT}}`
- Review evidence after an actual result exists:
  `{{FIGMA_MAKE_REVIEW_EVIDENCE_OR_NOT_VERIFIED}}`

Give Figma Make the same approved planning specification. Add execution
instructions only; do not create a second product definition.

Use `NOT USED` only when an optional tool was not selected, `NOT VERIFIED`
when a requested result was not observed, and `VERIFIED` only with the exact
observed scope and evidence.

## Tool limitation handling

If a selected tool cannot implement an approved requirement, record the
original requirement, the exact unmet behavior, and the decision needed:
change tool, implement separately, or explicitly change scope. Do not report a
mock/simulation as completion or silently reduce roles, screens, branches,
data effects, failure handling, or acceptance.

## Executable downstream conformance

This is shared contract/verification metadata, not Figma-specific planning.
Follow [`workflow-v0.2.0.md`](../references/workflow-v0.2.0.md) and
[`downstream-v2.1-contract.md`](../references/downstream-v2.1-contract.md)
for current rules rather than redefining them here. Select the contract from
the applicable approved state and contract, not from the optional tool name.

### Current native V2 handoff — default for State 0.2.0

- Handoff definition schema: `{{HANDOFF_DEFINITION_SCHEMA_VERSION}}` (must be `joewrks.handoff-definition/2.1`)
- Handoff definition: `{{HANDOFF_DEFINITION_PATH}}`
- Contract schema version: `{{CONTRACT_SCHEMA_VERSION}}` (must be `joewrks.action-conformance/2.1`)
- Action Conformance Contract: `{{ACTION_CONTRACT_PATH}}`
- Contract artifact hash: `{{ACTION_CONTRACT_ARTIFACT_HASH}}`
- Semantic contract hash: `{{SEMANTIC_CONTRACT_HASH}}`
- Semantic assurance status: `{{SEMANTIC_ASSURANCE_STATUS}}`
- Direct-authority / machine-derived / review-required counts:
  `{{SEMANTIC_DEBT_COUNTS}}`
- Lifecycle entries: embedded in the handoff/action contract `lifecycles`
  arrays; do not require a separate lifecycle-contract file.

### Plan and execution record timing

A verification plan may be recorded whenever its actual artifact exists,
including before implementation. Do not pre-fill execution evidence or
verification results.

- Runtime conformance plan path/hash:
  `{{RUNTIME_PLAN_PATH_AND_HASH_OR_NOT_MATERIALIZED}}`
- Runtime evidence bundle path/hash:
  `{{RUNTIME_EVIDENCE_BUNDLE_PATH_AND_HASH_OR_NOT_MATERIALIZED}}`
- Runtime conformance report/verifier:
  `{{RUNTIME_REPORT_AND_VERIFIER_OR_NOT_RUN}}`
- Runtime adapter identity/version when required:
  `{{ADAPTER_IDENTITY}}`
- Frozen implementation commit/tree when available:
  `{{FROZEN_SOURCE_COMMIT_TREE}}`
- Sequence runner and required sequence/test IDs when required:
  `{{SEQUENCE_RUNNER_COMMAND}}` / `{{REQUIRED_SEQUENCE_IDS}}`

Use `NOT_MATERIALIZED` for a missing artifact and `NOT_RUN` for an execution
that did not occur.

### Historical compatibility only

For an exact historical `joewrks.action-conformance/2.0` artifact, follow
[`downstream-v2-contract.md`](../references/downstream-v2-contract.md) and
[`downstream_v2/README.md`](../downstream_v2/README.md).

For an exact historical `joewrks.action-conformance/1.0` handoff, follow
[`downstream/README.md`](../downstream/README.md). Record its required
metadata without applying it to 2.1 by analogy:

- Legacy Action Conformance Contract: `{{ACTION_CONTRACT_PATH}}`
- Legacy Lifecycle/Reversal Contract: `{{LIFECYCLE_CONTRACT_PATH}}`
- Legacy executable contract SHA-256: `{{EXECUTABLE_CONTRACT_SHA256}}`

Do not use `joewrks.downstream.regression-slice/1.0` as an implementation
handoff contract.

## Forbidden invention

Do not create new product features, roles, business rules, navigation
destinations, data fields, or user-flow branches unless explicitly present in
the approved specification.

If implementation requires an unresolved product decision, stop and surface
the decision instead of inventing one.
