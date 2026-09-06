# Implementation Handoff and Optional Figma Guidance

This historical file path remains stable, but following it does not make
Figma mandatory. Start with one common human-readable planning specification
for the implementation consumer. Add tool-specific guidance only for work the
user selected.

## Common implementation handoff

The common handoff preserves the same approved Product Definition meaning
regardless of implementation tool. It records or links:

- purpose, scope, and exclusions;
- the exact approved source path, revision, and applicable stable IDs;
- user roles and the distinction between view, action, and mutation authority;
- IA relationships: information hierarchy, each screen's purpose, entry, and
  connections;
- user flows: preconditions, actor actions, system decisions, branches,
  results, and postconditions;
- screen states, accepted inputs, validation effects, persisted data changes,
  and visible results;
- failures, cancellation, interruption, retry, and recovery;
- acceptance criteria, forbidden changes, and unresolved product decisions
  that still require evidence or a user answer.

When Product Definition, user-flow, or screen specifications already exist,
link their exact paths and IDs instead of independently redefining the same
planning meaning. Tool choice may change the delivery format, reading order,
execution instructions, and output location; delivery documents need not be
byte-identical. They must reference the same approved sources and must not
change requirements, IA, permissions, state transitions, data meaning,
recovery, or acceptance.

## Optional Figma guidance

### Figma is not selected

Deliver the common handoff to the implementation consumer. Do not require
Figma frames, Figma-specific file names, or Figma review documents. Omit the
optional block, or retain it as `NOT USED` when an explicit status is useful.

### Figma Design low-fi visualization is requested

Only then generate editable low-fi frames from the applicable screen and flow
specifications. Recommended pages are `00_PRODUCT_MAP`, `01_USER_FLOWS`,
`02_WIREFRAMES`, `03_SCREEN_STATES`, and `99_HANDOFF`. Name frames from stable
screen IDs, such as `SCR-001__LOGIN`, with state variants such as
`SCR-001__DEFAULT` and `SCR-001__ERROR`; preserve IDs exactly.

Do not invent brand style, decorative imagery, color identity, complex
animation, or high-fidelity styling before the applicable visual authority
decides them. Low-fi work may visualize hierarchy, layout, content,
interaction, navigation, state, and flow, but it does not create product
authority.

### Figma Make implementation is selected

Give Figma Make the same common approved planning meaning and add only the
execution instructions and artifact locations it needs. Figma Design
visualization and Figma Make implementation are distinct tasks: requesting or
verifying one does not request or verify the other.

After an actual Figma Make result exists, create a review record covering
missing or extra screens and flows, invented branches, missing states,
rule/permission/data/navigation drift, scope expansion, and acceptance
violations. Link each finding to expected stable IDs and evidence. Do not
require this review artifact when Figma Make was not selected.

### Human-readable status labels

These are human-readable status labels only, not runtime or schema enums:

- `NOT USED`: the optional tool was not selected; the block may instead be
  omitted.
- `NOT VERIFIED`: the result was requested, but the required artifact or
  observation was not available for verification.
- `VERIFIED`: record the exact observed scope and evidence. Do not imply that
  unobserved visual, interaction, runtime, or product behavior was verified.

Optional-tool non-use is not a Product Definition gap. Conversely, never hide
a requested but unverified result by relabeling it `NOT USED`. A connected tool
does not authorize its invocation or artifact creation.

## Tool capability boundary

If a selected tool cannot implement an approved requirement, preserve the
original requirement and identify the exact unmet role, screen, branch, data
effect, failure path, or acceptance criterion. A mock or simulation is not
implementation completion. Route the limitation to a tool change, separate
implementation, or explicit scope decision; the limitation itself does not
approve a product or scope change. Do not replace JOEDESIGN visual authority
or create its internal plan here.

## Executable downstream conformance

This document references the installed contract and verification rules; it
does not own a Figma-specific copy of them. Canonical Product Definition remains authority. Every downstream contract, runtime plan, and evidence
artifact is a read-only, provenance-pinned projection and does not change
Closure or `state.json`. A machine contract does not replace the common IA,
flows, screen/state behavior, recovery, or forbidden-invention boundary.
Select the contract version from the applicable approved state and contract,
not from the tool name. Do not delete, bypass, or weaken the installed
Closure, compiler, or runtime gates.

### Current native V2 route

For a current State `0.2.0` handoff, follow the installed V2 workflow in
[`workflow-v0.2.0.md`](workflow-v0.2.0.md) and the normative
[`downstream-v2.1-contract.md`](downstream-v2.1-contract.md):

```text
joewrks.handoff-definition/2.1
→ joewrks.action-conformance/2.1
```

Record the exact approved revision, definition digest, Approval Manifest
digest, handoff-definition path, action-contract path, action-contract
`artifact_hash`, `semantic_contract_hash`, semantic-assurance status, and
direct-authority / machine-derived / review-required counts. In 2.1,
lifecycles are entries in the handoff and action contract `lifecycles` arrays;
there is no required separate lifecycle-contract artifact.

A verification plan may be prepared before implementation when the actual
plan artifact has been materialized; record its exact path/hash at that time.
Record execution evidence and verification results only after the applicable
execution or verification occurred. Use `NOT_MATERIALIZED` for an artifact
that does not exist and `NOT_RUN` for an execution that did not occur; never
pre-fill a future result.

Adapter identity, frozen source commit/tree, sequence information, and runtime
evidence are selected-contract execution information, not Figma-specific
metadata. Record them only when the selected contract or verifier requires
them and the corresponding artifacts exist.

### Historical compatibility routes

- `joewrks.action-conformance/2.0` belongs to the frozen M5 compatibility
  boundary documented in
  [`downstream-v2-contract.md`](downstream-v2-contract.md) and
  [`downstream_v2/README.md`](../downstream_v2/README.md). It is not the
  installed current compilation default.
- `joewrks.action-conformance/1.0` belongs to the frozen legacy path in
  [`downstream/README.md`](../downstream/README.md). Use its exact documented
  action/lifecycle bundle, hash, adapter/source, and sequence requirements
  only for a selected historical 1.0 handoff.
- `joewrks.downstream.regression-slice/1.0` remains evaluator-only. It must
  never be supplied or described as a full implementation handoff contract.

Never mix metadata requirements across 1.0, 2.0, and 2.1. Runtime evidence
continues to use frozen `joewrks.downstream.execution/1.0` records where the
selected verifier requires them; generator adapters invoke and read back the
implementation and do not decide expected product behavior.

After implementation, use the downstream blind-audit procedure. Trace every
material action from precondition through public action, handler, domain
state, provenance/side effects, and visible result or recovery. A rendered
label, handler existence, helper test, build result, visual similarity,
implementation self-report, or green test count is not transition evidence.
