# Figma and Figma Make Handoff

When Figma is available, generate editable low-fi frames from screen and flow specifications. Recommended pages: `00_PRODUCT_MAP`, `01_USER_FLOWS`, `02_WIREFRAMES`, `03_SCREEN_STATES`, `99_HANDOFF`. Name frames `SCR-001__LOGIN` and variants `SCR-001__DEFAULT`, `SCR-001__ERROR`; preserve IDs exactly.

Do not invent brand style, decorative imagery, color identity, complex animation, or high-fidelity styling before the user decides them. Low-fi work validates hierarchy, layout, content, interaction, navigation, state, and flow.

Without Figma, produce Markdown wireframes, Mermaid flows, screen specifications, build instructions, and `FIGMA_MAKE_HANDOFF.md`; record `Figma visualization: NOT VERIFIED`.

After Figma Make output, create `MAKE_REVIEW.md` covering missing/extra screens and flows, invented branches, missing states, rule/permission/data/navigation drift, scope expansion, and acceptance violations. Link each drift to expected IDs and severity.

## Executable downstream conformance

Canonical Product Definition remains authority. Every downstream contract,
runtime plan, and evidence artifact is a read-only, provenance-pinned
projection and does not change Closure or `state.json`. Keep the
human-readable handoff; a machine contract does not replace the IA, flows,
screen/state behavior, recovery, or forbidden-invention boundary.

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

Runtime conformance is a later, non-authoritative verification stage. When it
has actually been materialized, record the exact
`joewrks.runtime-conformance-plan/1.0` path/hash, admitted
`joewrks.runtime-evidence-bundle/1.0` path/hash, verifier/report identity, and
the implementation adapter plus frozen source commit/tree. Do not populate
these as if they already exist before implementation.

### Historical compatibility routes

- `joewrks.action-conformance/2.0` belongs to the frozen M5 compatibility
  boundary documented in
  [`downstream-v2-contract.md`](downstream-v2-contract.md) and
  [`downstream_v2/README.md`](../downstream_v2/README.md). It is not the
  installed current compilation default.
- `joewrks.action-conformance/1.0` belongs to the frozen legacy path in
  [`downstream/README.md`](../downstream/README.md). Only an exact historical
  1.0 handoff should require its legacy action/lifecycle bundle metadata,
  adapter identity/version, frozen source commit/tree, and sequence-runner
  command.
- `joewrks.downstream.regression-slice/1.0` remains evaluator-only. It must
  never be supplied or described as a full implementation or Figma-Make
  handoff contract.

Never mix metadata requirements across 1.0, 2.0, and 2.1. Runtime evidence
continues to use frozen `joewrks.downstream.execution/1.0` records where the
selected verifier requires them; generator adapters invoke and read back the
implementation and do not decide expected product behavior.

After implementation, use the downstream blind-audit procedure. Trace every material action from precondition through public action, handler, domain state, provenance/side effects, and visible result or recovery. A rendered label, handler existence, helper test, build result, visual similarity, implementation self-report, or green test count is not transition evidence.
