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

- Action Conformance Contract: `{{ACTION_CONTRACT_PATH}}`
- Lifecycle/Reversal Contract: `{{LIFECYCLE_CONTRACT_PATH}}`
- Executable contract SHA-256: `{{EXECUTABLE_CONTRACT_SHA256}}`
- Runtime adapter identity/version: `{{ADAPTER_IDENTITY}}`
- Frozen implementation commit/tree: `{{FROZEN_SOURCE_COMMIT_TREE}}`
- Sequence runner: `{{SEQUENCE_RUNNER_COMMAND}}`
- Required sequence/test IDs: `{{REQUIRED_SEQUENCE_IDS}}`

These files are derived verification projections. The approved Product Definition revision/digest remains authority. Adapters invoke and read back the actual runtime; they do not decide expected behavior.

## Forbidden invention

Do not create new product features, roles, business rules, navigation destinations, data fields, or user-flow branches unless explicitly present in this specification.

If implementation requires an unresolved product decision, stop and surface the decision instead of inventing one.
