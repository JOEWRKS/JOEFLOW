---
name: joewrks-product-definition
description: Use when a product, feature, website, app, workflow, or redesign needs product and UX decisions resolved before implementation, especially when requirements contain ambiguity, assumptions, missing states, policy gaps, edge cases, or conflicting expectations.
---

# JOEWRKS Product Definition

Close the product definition before implementation. Persist authority in `product-definition/<project-slug>/state.json`; conversation history and generated Markdown are never authoritative.

Installed routing status:

- `PRODUCT_DEFINITION_STATE_V2_DEFAULT`
- `LEGACY_0_1_2_1_COMPATIBILITY_PRESERVED`
- `DOWNSTREAM_V2_INSTALLED_ROUTING`
- `SEMANTIC_REVIEW_V2_RELIABILITY_NOT_MEASURED`

Read [workflow-v0.2.0.md](references/workflow-v0.2.0.md) before running the V2 lifecycle. When implementation or downstream verification reports a mismatch, ambiguity, conflict, or scope request, use [reentry-workflow-v0.2.0.md](references/reentry-workflow-v0.2.0.md) before changing Product Definition.

Use a tool-independent implementation handoff. Start with the common human-readable
specification in [figma-make-handoff.md](templates/figma-make-handoff.md) and
its [handoff guidance](references/figma-make-handoff.md); the historical file
name does not make Figma mandatory. Preserve the same approved product
meaning for every implementation consumer, and include optional Figma Design
or Figma Make guidance only when that work was selected.

## State-contract dispatch

- **New project:** create `state.json` from `templates/state-v0.2.0.example.json`, validate it through `scripts/validate_state.py` against the V2 dispatcher and `schemas/state-v0.2.0.schema.json`, and continue under [state-contract-v0.2.0.md](references/state-contract-v0.2.0.md).
- **Existing `0.2.0` state:** resume the V2 workflow at the current canonical state. Do not replace it with a fresh template.
- **Existing `0.1.2.1` state:** validate it with the frozen legacy dispatcher, `schemas/state.schema.json`, `templates/state.example.json`, and [state-contract.md](references/state-contract.md). Preserve it as legacy; never silently migrate. Run `scripts/migrate_state.py --apply` only when the user explicitly asks to adopt V2.

## Non-negotiable rules

- Do not invent a material product decision. Register it as an unknown; close it only from evidence, an explicit user answer, or an explicitly accepted recommendation.
- Inspect available evidence before asking. V2 uses first-class evidence, surface, contradiction, unknown, Materiality, decision-authority, and Grill Pack records.
- Keep stable IDs forever. Never renumber or reuse an ID.
- Before any material semantic state mutation, prepare and validate the complete affected records off-state. Commit the revision increment, truthful non-`CLOSED` lifecycle state, `UNAPPROVED` approval, affected-only staleness, and complete records as one canonical mutation before recompiling.
- Treat migration gaps as uncertainty, never as Product Definition authority. Migration cannot promote legacy Closure or approval to V2 Semantic Closure.
- Do not claim Semantic Closure until V2 state validation, closure evaluation, the deterministic Approval Manifest, and exact user approval all bind the current definition.
- `joewrks.semantic-review/2.1` may record review results only for legitimate `REVIEW_REQUIRED` obligations and remains reliability `NOT_MEASURED`; review never creates product authority.
- If implementation exposes a material ambiguity or `SEMANTIC_AUTHORITY_GAP`, re-enter DISCOVER/CLOSE for the affected scope; do not decide inside implementation.

## Implementation re-entry routing

- **Clear Product Definition authority, incorrect runtime behavior:** implementation correction required; do not create a new Product Definition decision merely to explain a code bug. Observed implementation/runtime evidence may be recorded when useful, but no semantic authority change follows automatically.
- **Real downstream semantic gap or ambiguity:** inspect and resolve the exact affected authority and evidence, then assess Materiality and decision authority. Only when a real unresolved product question remains, independently author and prepare a complete V2 unknown record off-state. Then, as one canonical mutation, increment `definition_revision`, move to a truthful non-`CLOSED` state, set approval `UNAPPROVED`, stale only affected dependencies, and register the complete unknown under the new revision before re-running the affected Product Definition and approval flow.
- **`OUT_OF_SCOPE_REQUEST`:** resolve Product Definition scope first. An implementation request does not expand approved scope.

A `joewrks.product-definition-reentry/1.0` artifact and its `candidate_unknown` are read-only proposals, never canonical authority. Candidate wording must never be copied directly or verbatim into `state.json`, a decision, an unknown, or a user question; independently author any later record from inspected evidence and ordinary V2 semantics. Do not use a general-purpose re-entry state mutator.

The event itself has no consumed-seed or scope-commitment inventories. For a non-null `source_contract_hash`, resolve the exact matching action contract and inspect its inventories. For a null hash, inspect the exact pre-contract handoff definition plus affected current state authority and evidence.

## V2 workflow

1. **DISCOVER:** inspect repository evidence and intended-product sources; disposition surfaces and contradictions without treating observed implementation as intent.
2. **CLOSE:** resolve evidence-answerable gaps first, then ask one highest-leverage material question at a time. Record truthful Materiality and decision authority.
3. **FREEZE:** bind Core, specialist Grill, and UX coverage to exact current authority; build the deterministic Approval Manifest.
4. **APPROVE:** show the exact current manifest and wait for explicit user approval. Do not manufacture approval or timestamps.
5. **HANDOFF:** after validated Semantic Closure, compile a `joewrks.handoff-definition/2.1` into `joewrks.action-conformance/2.1` using `scripts/compile_downstream_v2.py`.
6. **VERIFY:** audit only current contract dependencies with `scripts/audit_downstream_v2.py`; build `joewrks.semantic-review/2.1` packages with `scripts/build_semantic_review_v2.py` only when legitimate `REVIEW_REQUIRED` obligations exist. Then materialize `joewrks.runtime-conformance-plan/1.0`, admit only frozen `joewrks.downstream.execution/1.0` evidence into a `joewrks.runtime-evidence-bundle/1.0`, and run `scripts/verify_runtime_v21.py CONTRACT_JSON RUNTIME_PLAN_JSON RUNTIME_EVIDENCE_BUNDLE_JSON [REVIEW_PACKAGE_JSON REVIEW_OUTPUT_JSON]`. The 2.1 verifier binds and rechecks the plan and admitted bundle; `verify_runtime_v2.py` is retained only for historical 2.0 contracts.

Resolve the absolute directory containing this loaded `SKILL.md`; never resolve scripts from the consumer project's working directory and never require the caller to persist `PYTHONPATH`.

## Quick reference

| Situation | Required action |
|---|---|
| Evidence answers a question | Record evidence, resolution provenance, and affected IDs |
| Human judgment is required | Create a truthful material `UNK`; ask with options and a recommendation when appropriate |
| Recommendation accepted | Record `USER_ACCEPTED_RECOMMENDATION` |
| Material semantic state changes | Prepare complete records off-state, then atomically increment revision, set non-`CLOSED`/`UNAPPROVED`, stale affected dependencies, and register the complete records |
| Coverage item does not apply | Record `N/A` with rationale and exact basis binding |
| No optional Figma work selected | Deliver the common implementation handoff; omit Figma-only artifacts or mark the optional block `NOT USED` |
| Requested Figma or Figma Make result not observed | Record `NOT VERIFIED` and the exact missing result; do not relabel it `NOT USED` |
| Requested optional-tool result verified | Record only the observed scope and exact evidence |
| Clear-authority runtime bug | Correct the implementation; do not create a product decision or change revision/approval automatically |
| Material ambiguity during build | Re-enter DISCOVER/CLOSE and block only affected work |
| `OUT_OF_SCOPE_REQUEST` | Resolve Product Definition scope before implementation |
| Legacy `0.1.2.1` project | Validate frozen legacy state; migrate only on explicit V2 adoption request |

## Common mistakes

- Asking for facts already available in code or docs.
- Treating a Markdown projection or chat memory as newer than `state.json`.
- Treating observed implementation as intended product meaning.
- Turning legacy `COVERED`, approval, or a migration gap into V2 authority.
- Sending an upstream authority gap to Semantic Review instead of reopening Product Definition.
- Treating every runtime mismatch as a new Product Definition question.
- Copying `candidate_unknown` suggestion text into canonical authority.
- Treating a workaround, deferred blocker, attractive wireframe, or validator availability as Semantic Closure.
- Treating a connected or unused optional tool as required, or conflating `NOT USED` with `NOT VERIFIED`.
- Reducing an approved role, screen, branch, data effect, failure path, or acceptance criterion because a selected tool cannot implement it.
- Allowing Figma Make or an implementation agent to add fields, roles, routes, rules, or branches.

Use the templates in `templates/` for projections. Preserve additional project-specific fields when updating state.
