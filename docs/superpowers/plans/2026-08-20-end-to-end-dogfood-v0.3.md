# End-to-End Product Definition Dogfood v0.3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute one isolated, multi-turn product-definition dogfood from vague idea through approved closure, native Figma design, Figma Make execution when available, and specification drift audit.

**Architecture:** A root evaluator owns the hidden user bank and sends only answers requested by one persistent fresh Product Agent. The Agent owns the canonical dogfood state and projections. Figma capability is discovered only after closure; every external claim requires write/readback evidence. Frozen behavioral and deterministic baselines are verified by blob SHA.

**Tech Stack:** JOEWRKS Product Definition Skill, JSON canonical state, Markdown projections/audits, Python validators, Figma native tools when available, GitHub tree/commit API.

**Spec:** `C:/Users/tjdwo/.codex/attachments/e14f30b7-be20-4db8-8bb2-a4e47d03bb1f/pasted-text.txt`

## Global Constraints

- Baseline commit is `0c5048f336ac9ba028d066a48c9ca60e4b85f5a8`; deterministic contract remains `0.1.2.1`.
- Product Agent may read only the current Skill package and its dedicated project directory, never the hidden bank, evaluator rubric, plans, or previous evals.
- Do not modify Skill, interrogation engine, validator, schema, state contract, taxonomies, stable IDs, or Closure metrics during the first run.
- Never simulate Figma-native or Figma Make execution.
- User-approved Product Definition remains authority over design and Make output.

---

### Task 1: Isolation and Frozen Baseline

**Files:**
- Create after run: `evals/end-to-end-v0.3/methodology.md`
- Create after run: `evals/end-to-end-v0.3/hidden-user-answer-bank.md`

**Interfaces:**
- Consumes: v0.3 specification and baseline remote commit.
- Produces: one fresh Product Agent execution ID and frozen-file SHA evidence.

- [ ] Record baseline blobs for Skill, interrogation engine, validators, schema, state contract, and taxonomies.
- [ ] Spawn Product Agent with `fork_turns="none"`, initial prompt only, and explicit evidence boundary.

### Task 2: Multi-turn Interrogation and Snapshots

**Files:**
- Create: `product-definition/client-feedback-portal-dogfood/state.json` and required projections.
- Create after run: `evals/end-to-end-v0.3/interrogation-transcript.md`, `emergent-decisions.md`, `decision-reversal.md`.

**Interfaces:**
- Consumes: Agent questions and only matching hidden-bank answers.
- Produces: complete decisions, rediscovered unknowns, monotonic revisions, and snapshots at required milestones.

- [ ] Continue the same Agent turn-by-turn until material blockers reach zero.
- [ ] Inject the 7-day to 30-day reversal only after the original expiry is persisted.
- [ ] Record each visible question, answer, state change, rediscovery, repetition, and emergent question.

### Task 3: Closure and Cross-Artifact Audit

**Files:**
- Create: all eight required product-definition artifacts.
- Create: `evals/end-to-end-v0.3/closure-report.md` and `PRE_FIGMA_AUDIT.md`.

**Interfaces:**
- Consumes: READY_FOR_REVIEW revision/digest and complete projections.
- Produces: explicit simulated human approval, validator exit 0, closed true, and zero blocking pre-Figma drift.

- [ ] Withhold approval until the Agent presents exact revision and digest.
- [ ] Approve that exact pair, rerun both validators, and independently verify them.
- [ ] Audit every typed mapping, route/status/role/version rule, and implementation-plan task evidence.

### Task 4: Figma Capability, Native Design, and Audit

**Files:**
- Create: `evals/end-to-end-v0.3/figma-generation-report.md` and `FIGMA_DESIGN_AUDIT.md`.

**Interfaces:**
- Consumes: closed state and zero-blocking pre-Figma audit.
- Produces: actual editable native frames with stable SCR IDs and readback evidence, or an explicit capability blocker.

- [ ] Discover callable Figma write/create capabilities without assuming availability.
- [ ] If possible, create the five required pages and native low-fi frames; otherwise stop the Figma branch with exact required user action.
- [ ] Read back metadata/context, audit screen/state/action fidelity, correct supported drift, and re-audit.

### Task 5: Figma Make Execution and Drift Audit

**Files:**
- Create: `FIGMA_MAKE_HANDOFF.md`, `evals/end-to-end-v0.3/figma-make-execution.md`, and `MAKE_REVIEW.md`.

**Interfaces:**
- Consumes: audited native design and final handoff.
- Produces: actual Make output/readback and DRIFT findings, or `BLOCKED_AT_FIGMA_MAKE_EXECUTION` with manual bridge.

- [ ] Discover actual Make creation capability.
- [ ] Execute only if callable; record real URL/key and retrieve result context.
- [ ] Audit all required drift categories and correct Blocking/Major findings when tools permit.

### Task 6: Aggregate, Verification, and Publication

**Files:**
- Create: `evals/end-to-end-v0.3/README.md` and `aggregate-results.md`.

**Interfaces:**
- Consumes: all run evidence and audits.
- Produces: honest PASS/PARTIAL/FAIL verdict and remotely readable commit.

- [ ] Calculate the 100-point score and user-burden metrics.
- [ ] Verify frozen baseline hashes, validators, artifacts, and required evidence files.
- [ ] Commit `test: dogfood end-to-end product definition v0.3` to existing private `main` and read back required remote artifacts.
