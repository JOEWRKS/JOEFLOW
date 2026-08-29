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

Read [workflow-v0.2.0.md](references/workflow-v0.2.0.md) before running the V2 lifecycle.

## State-contract dispatch

- **New project:** create `state.json` from `templates/state-v0.2.0.example.json`, validate it through `scripts/validate_state.py` against the V2 dispatcher and `schemas/state-v0.2.0.schema.json`, and continue under [state-contract-v0.2.0.md](references/state-contract-v0.2.0.md).
- **Existing `0.2.0` state:** resume the V2 workflow at the current canonical state. Do not replace it with a fresh template.
- **Existing `0.1.2.1` state:** validate it with the frozen legacy dispatcher, `schemas/state.schema.json`, `templates/state.example.json`, and [state-contract.md](references/state-contract.md). Preserve it as legacy; never silently migrate. Run `scripts/migrate_state.py --apply` only when the user explicitly asks to adopt V2.

## Non-negotiable rules

- Do not invent a material product decision. Register it as an unknown; close it only from evidence, an explicit user answer, or an explicitly accepted recommendation.
- Inspect available evidence before asking. V2 uses first-class evidence, surface, contradiction, unknown, Materiality, decision-authority, and Grill Pack records.
- Keep stable IDs forever. Never renumber or reuse an ID.
- On any material semantic change, increment `definition_revision`, set approval to `UNAPPROVED`, and stale only affected authority and downstream dependencies before recompiling.
- Treat migration gaps as uncertainty, never as Product Definition authority. Migration cannot promote legacy Closure or approval to V2 Semantic Closure.
- Do not claim Semantic Closure until V2 state validation, closure evaluation, the deterministic Approval Manifest, and exact user approval all bind the current definition.
- `joewrks.semantic-review/2.0` may record review results but remains reliability `NOT_MEASURED`; review never creates product authority.
- If implementation exposes a material ambiguity or `SEMANTIC_AUTHORITY_GAP`, re-enter DISCOVER/CLOSE for the affected scope; do not decide inside implementation.

## V2 workflow

1. **DISCOVER:** inspect repository evidence and intended-product sources; disposition surfaces and contradictions without treating observed implementation as intent.
2. **CLOSE:** resolve evidence-answerable gaps first, then ask one highest-leverage material question at a time. Record truthful Materiality and decision authority.
3. **FREEZE:** bind Core, specialist Grill, and UX coverage to exact current authority; build the deterministic Approval Manifest.
4. **APPROVE:** show the exact current manifest and wait for explicit user approval. Do not manufacture approval or timestamps.
5. **HANDOFF:** after validated Semantic Closure, compile `joewrks.action-conformance/2.0` using `scripts/compile_downstream_v2.py`.
6. **VERIFY:** audit contract dependencies with `scripts/audit_downstream_v2.py`; build `joewrks.semantic-review/2.0` packages with `scripts/build_semantic_review_v2.py` only when legitimate `REVIEW_REQUIRED` obligations exist.

Resolve the absolute directory containing this loaded `SKILL.md`; never resolve scripts from the consumer project's working directory and never require the caller to persist `PYTHONPATH`.

## Quick reference

| Situation | Required action |
|---|---|
| Evidence answers a question | Record evidence, resolution provenance, and affected IDs |
| Human judgment is required | Create a truthful material `UNK`; ask with options and a recommendation when appropriate |
| Recommendation accepted | Record `USER_ACCEPTED_RECOMMENDATION` |
| Material semantic state changes | Increment revision, set approval `UNAPPROVED`, and stale affected dependencies |
| Coverage item does not apply | Record `N/A` with rationale and exact basis binding |
| Figma unavailable | Produce Markdown/Mermaid handoff and `NOT VERIFIED` |
| Material ambiguity during build | Re-enter DISCOVER/CLOSE and block only affected work |
| Legacy `0.1.2.1` project | Validate frozen legacy state; migrate only on explicit V2 adoption request |

## Common mistakes

- Asking for facts already available in code or docs.
- Treating a Markdown projection or chat memory as newer than `state.json`.
- Treating observed implementation as intended product meaning.
- Turning legacy `COVERED`, approval, or a migration gap into V2 authority.
- Sending an upstream authority gap to Semantic Review instead of reopening Product Definition.
- Treating a workaround, deferred blocker, attractive wireframe, or validator availability as Semantic Closure.
- Allowing Figma Make or an implementation agent to add fields, roles, routes, rules, or branches.

Use the templates in `templates/` for projections. Preserve additional project-specific fields when updating state.
