---
name: joewrks-product-definition
description: Use when a product, feature, website, app, workflow, or redesign needs product and UX decisions resolved before implementation, especially when requirements contain ambiguity, assumptions, missing states, policy gaps, edge cases, or conflicting expectations.
---

# JOEWRKS Product Definition

Close the product definition before implementation. Persist authority in `product-definition/<project-slug>/state.json`; conversation history and generated Markdown are never authoritative. Create state from `templates/state.example.json`, conform it to `schemas/state.schema.json`, and read [state-contract.md](references/state-contract.md).

## Non-negotiable rules

- Do not invent a material product decision. Register it as an unknown; close it only from evidence, an explicit user answer, or an explicitly accepted recommendation.
- Inspect available evidence before asking. Read [interrogation-engine.md](references/interrogation-engine.md) for discovery and questioning.
- Keep stable IDs forever. Never renumber or reuse an ID.
- On any material state change, increment `definition_revision`, clear `approval`, then follow [artifact-dependency-graph.md](references/artifact-dependency-graph.md) and mark every affected downstream object `STALE` before recompiling it.
- Do not claim completion until both validators pass and the user explicitly approves closure. Read [closure-gate.md](references/closure-gate.md).
- If implementation exposes ambiguity, re-enter this workflow; do not decide inside implementation.

## Workflow

1. Determine or create the project slug and artifact directory. If resuming, read `state.json` first, then reconcile Markdown projections.
2. Discover repository, documentation, tests, APIs, schemas, designs, prior decisions, current behavior, and relevant official constraints.
3. Register facts, contradictions, and unknowns using [unknown-taxonomy.md](references/unknown-taxonomy.md) and [requirement-taxonomy.md](references/requirement-taxonomy.md). Before the first question, sweep the applicable coverage areas and create one unknown record per independently answerable material decision; never hide several policies inside one umbrella unknown. This is state breadth, not permission to question-bomb the user.
4. Rank open material decisions and ask the highest-fan-out question. Record each answer and source immediately; then propagate and compile affected artifacts.
5. Compile product requirements, flows, screens, states, rules, acceptance criteria, and implementation mappings using the templates. For UX work, read [product-coverage-matrix.md](references/product-coverage-matrix.md), [ux-state-taxonomy.md](references/ux-state-taxonomy.md), and [failure-recovery-taxonomy.md](references/failure-recovery-taxonomy.md).
6. Repeat discovery after every answer until no new material unknown appears.
7. If Figma is available, use stable screen IDs for editable frames. Otherwise follow [figma-make-handoff.md](references/figma-make-handoff.md) and mark visualization unverified.
8. Resolve the absolute directory containing this loaded `SKILL.md`; do not resolve scripts from the consumer project's working directory. Run `python <skill-directory>/scripts/validate_state.py <state.json>` and `python <skill-directory>/scripts/validate_closure.py <state.json>`. Resolve reported failures, present the exact current revision for explicit approval, record `approval.approved_revision`, and rerun both validators.

## Quick reference

| Situation | Required action |
|---|---|
| Evidence answers a question | Record fact, source, and affected IDs |
| Human judgment is required | Create `UNK`, ask with options and recommendation |
| Recommendation accepted | Record `ASSUMED_ACCEPTED`, never `ANSWERED` |
| Material state changes | Increment revision, clear approval, mark dependents `STALE` |
| Coverage item does not apply | Record `N/A` with rationale; never leave blank |
| Figma unavailable | Produce Markdown/Mermaid handoff and `NOT VERIFIED` |
| Material ambiguity during build | Re-enter product definition and block affected work |

## Common mistakes

- Asking for facts already available in code or docs.
- Treating a Markdown projection or chat memory as newer than `state.json`.
- Generating a final PRD once instead of recompiling after decisions.
- Treating a workaround, deferred blocker, attractive wireframe, or validator availability as closure.
- Allowing Figma Make or an implementation agent to add fields, roles, routes, rules, or branches.

Use the templates in `templates/` for projections. Preserve additional project-specific fields when updating state.
