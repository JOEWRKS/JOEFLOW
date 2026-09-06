# Figma Make Implementation Contract

Figma visualization: {{VERIFIED_OR_NOT_VERIFIED}}

## Objective, scope, and non-goals

## Target environment and user roles

## Locked decisions and feature inventory

## Routes, screens, flows, and states

Use stable IDs for every item and branch.

## Business, permission, validation, and data rules

## Errors, recovery, responsive behavior, and accessibility

## Acceptance criteria and non-blocking assumptions

## Executable downstream conformance

### Current native V2 handoff — default for State 0.2.0

- Approved Product Definition revision: `{{APPROVED_DEFINITION_REVISION}}`
- Approved definition digest: `{{APPROVED_DEFINITION_DIGEST}}`
- Approval Manifest digest: `{{APPROVED_MANIFEST_DIGEST}}`
- Handoff definition schema: `{{HANDOFF_DEFINITION_SCHEMA_VERSION}}` (must be `joewrks.handoff-definition/2.1`)
- Handoff definition: `{{HANDOFF_DEFINITION_PATH}}`
- Contract schema version: `{{CONTRACT_SCHEMA_VERSION}}` (must be `joewrks.action-conformance/2.1`)
- Action Conformance Contract: `{{ACTION_CONTRACT_PATH}}`
- Contract artifact hash: `{{ACTION_CONTRACT_ARTIFACT_HASH}}`
- Semantic contract hash: `{{SEMANTIC_CONTRACT_HASH}}`
- Semantic assurance status: `{{SEMANTIC_ASSURANCE_STATUS}}`
- Direct-authority / machine-derived / review-required counts: `{{SEMANTIC_DEBT_COUNTS}}`
- Lifecycle entries: embedded in the handoff/action contract `lifecycles` arrays; do not require a separate lifecycle-contract file.

Populate these only after the corresponding post-implementation artifacts
exist:

- Runtime conformance plan path/hash: `{{RUNTIME_PLAN_PATH_AND_HASH_OR_NOT_MATERIALIZED}}`
- Runtime evidence bundle path/hash: `{{RUNTIME_EVIDENCE_BUNDLE_PATH_AND_HASH_OR_NOT_MATERIALIZED}}`
- Runtime conformance report/verifier: `{{RUNTIME_REPORT_AND_VERIFIER_OR_NOT_RUN}}`
- Runtime adapter identity/version: `{{ADAPTER_IDENTITY}}`
- Frozen implementation commit/tree: `{{FROZEN_SOURCE_COMMIT_TREE}}`
- Sequence runner: `{{SEQUENCE_RUNNER_COMMAND}}`
- Required sequence/test IDs: `{{REQUIRED_SEQUENCE_IDS}}`

### Historical compatibility only

Use this block only when the exact selected historical authority is a frozen
`joewrks.action-conformance/1.0` handoff. It is not the current V2 default.

- Legacy Action Conformance Contract: `{{ACTION_CONTRACT_PATH}}`
- Legacy Lifecycle/Reversal Contract: `{{LIFECYCLE_CONTRACT_PATH}}`
- Legacy executable contract SHA-256: `{{EXECUTABLE_CONTRACT_SHA256}}`

For an exact historical `joewrks.action-conformance/2.0` artifact, follow its
frozen 2.0 contract documentation instead of filling either the current 2.1
or legacy 1.0 metadata by analogy.

These files are derived verification projections. The approved Product
Definition revision/digest remains authority. Adapters invoke and read back
the actual runtime; they do not decide expected behavior. Do not use
`joewrks.downstream.regression-slice/1.0` here; it is evaluator-only and is not
a production implementation/Figma-Make handoff artifact. Report
direct-authority, machine-derived, and review-required obligations separately.

## Forbidden invention

Do not create new product features, roles, business rules, navigation destinations, data fields, or user-flow branches unless explicitly present in this specification.

If implementation requires an unresolved product decision, stop and surface the decision instead of inventing one.
