# Behavioral Evaluation v0.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compare twelve genuinely isolated Control/Treatment agent runs, refine only behavioral Skill instructions when repeated transcript evidence warrants it, and publish reproducible v0.2 evidence.

**Architecture:** The root evaluator owns immutable prompts, fixtures, scoring, and repository writes. Each primary or rerun agent starts with `fork_turns="none"`, receives only its run input, and writes only to a unique run directory. Control never receives the Skill; Treatment explicitly loads the current Skill. Evaluation and refinement happen only after all primary runs.

**Tech Stack:** Markdown evidence, JSON fixtures, Codex fresh subagents, standard-library Python validators, GitHub blob/tree/commit API.

**Spec:** `C:/Users/tjdwo/.codex/attachments/a8757122-88e2-4898-b092-3670bdb26e63/pasted-text.txt`

## Global Constraints

- Baseline is commit `1121c9e33ef30335d9cb2af0b0c794621e33d6fd`, contract `0.1.2.1`.
- Never modify validators, canonical schema semantics, state contract semantics, coverage taxonomies, stable IDs, or closure metrics.
- Primary Control and Treatment contexts are isolated; evaluator rubrics are never shown to run agents.
- Behavioral refinements, if supported by repeated observable evidence, are limited first to `SKILL.md` and `references/interrogation-engine.md`.
- Do not run Figma-native generation or Figma Make.

---

### Task 1: Evaluation Harness and Immutable Fixtures

**Files:**
- Create: `evals/behavioral-v0.2/README.md`
- Create: `evals/behavioral-v0.2/methodology.md`
- Create: `evals/behavioral-v0.2/rubric.md`
- Create: `evals/behavioral-v0.2/fixtures/team-invitation/*`
- Create: `evals/behavioral-v0.2/fixtures/decision-change/*`
- Create: `evals/behavioral-v0.2/fixtures/figma-handoff/*`

**Interfaces:**
- Consumes: authoritative Phase 2 request and baseline repository.
- Produces: identical read-only inputs for paired Control/Treatment runs and documented isolation identifiers.

- [ ] Create minimal synthetic fixtures with no personal data or secrets.
- [ ] Record exact prompts, follow-up messages, runtime/model fields, and treatment-only Skill invocation.
- [ ] Record SHA-256 hashes for frozen deterministic files before runs.

### Task 2: Twelve Primary Fresh Runs

**Files:**
- Create: `evals/behavioral-v0.2/transcripts/eval-01-control.md` through `eval-06-treatment.md`
- Create: isolated Treatment state directories under `evals/behavioral-v0.2/run-state/`.

**Interfaces:**
- Consumes: Task 1 inputs only; each agent receives no evaluator answer key.
- Produces: raw observable transcripts, evidence-read lists, file mutations, and final statuses.

- [ ] Dispatch each run with `fork_turns="none"` and a unique execution identifier.
- [ ] Keep Control unaware of Skill content and explicitly invoke the Skill for Treatment.
- [ ] Apply identical scripted follow-ups for EVAL-04, EVAL-05, and EVAL-06 pairs.
- [ ] Preserve all observable outputs without inferring hidden reasoning.

### Task 3: Primary Scoring and Comparison

**Files:**
- Create: `evals/behavioral-v0.2/eval-01-control.md` through `eval-06-treatment.md`
- Create: `evals/behavioral-v0.2/eval-01-comparison.md` through `eval-06-comparison.md`
- Create: `evals/behavioral-v0.2/observed-rationalizations.md`

**Interfaces:**
- Consumes: all twelve primary transcripts and evaluator-only rubric.
- Produces: 100-point scores, 1–5 UX burden, critical failures, unknown coverage, and deltas.

- [ ] Score material coverage, unknown-unknown discovery, prioritization, evidence-first behavior, invention, premature behavior, and state discipline.
- [ ] Quote only observable run language and link transcript locations.
- [ ] Compare first question, ordering, evidence use, assumptions, build/closure, persistence, and rediscovery.

### Task 4: Rationalization-Driven Minimal Refinement

**Files:**
- Modify only if justified: `skills/joewrks-product-definition/SKILL.md`
- Modify only if justified: `skills/joewrks-product-definition/references/interrogation-engine.md`
- Create: `evals/behavioral-v0.2/refinement-log.md`

**Interfaces:**
- Consumes: repeated patterns across all six Treatment runs.
- Produces: minimal instruction changes explicitly mapped to transcript evidence, or a documented no-change decision.

- [ ] Identify cross-EVAL patterns before proposing any change.
- [ ] Reject taxonomy/validator/schema/state-contract changes.
- [ ] Apply the smallest behavioral wording that directly blocks an observed rationalization.
- [ ] Record before/after text and evidence links.

### Task 5: Fresh Treatment Regression

**Files:**
- Create: `evals/behavioral-v0.2/transcripts/rerun-eval-01-treatment.md` through `rerun-eval-06-treatment.md` when refinement occurs.
- Update: corresponding Treatment and comparison reports with final scores.

**Interfaces:**
- Consumes: refined Skill and the same immutable prompts/fixtures.
- Produces: six new isolated Treatment results and regression deltas.

- [ ] Dispatch every Treatment rerun with `fork_turns="none"`.
- [ ] Verify final Treatment has zero critical failures and measure UX burden.
- [ ] Record regressions as failures rather than masking them with score adjustments.

### Task 6: Aggregate Verification and Publication

**Files:**
- Create: `evals/behavioral-v0.2/aggregate-results.md`
- Update: `evals/behavioral-v0.2/README.md`

**Interfaces:**
- Consumes: all primary, comparison, refinement, and rerun evidence.
- Produces: final behavioral verdict and a remotely readable Git commit.

- [ ] Recompute aggregate scores and pass thresholds from report values.
- [ ] Compare frozen deterministic file hashes against baseline working copies.
- [ ] Run the existing 43-test suite, Skill quick validation, and `py_compile` without changing frozen files.
- [ ] Inspect every required artifact and scan for missing placeholders.
- [ ] Commit and push authorized artifacts to `JOEWRKS/joewrks-product-definition` `main`.
- [ ] Read back the commit, aggregate report, Skill files, and frozen-file hashes from remote.
