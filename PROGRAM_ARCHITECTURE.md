# JOEWRKS Product Definition System

**JOEWRKS Product Definition System** is the program-level name for this repository and its integrated product-definition, downstream-conformance, semantic-review, and evaluation tooling.

The existing runtime skill/package identifier remains **`joewrks-product-definition`**. The identifier is not renamed by this document.

## Identity

| Item | Value |
| --- | --- |
| Program name | `JOEWRKS Product Definition System` |
| Repository | `JOEWRKS/joewrks-product-definition` |
| Runtime skill/package ID | `joewrks-product-definition` |
| Canonical Product Definition authority | `product-definition/<project-slug>/state.json` |
| Current integrated development line | `v0.4.3` |
| Current protected `main` baseline | `efd96410f6401cbf9624328e94b795c315164b7f` |
| Repaired v0.4.3 calibration input | `748254d6def81080a2fd2736115a3ab5e0bde5a3` |
| v0.4.3 environment-blocked disposition | `6a0674c5d00a40790afef78cfa19494314b894e3` |

## Purpose

The system exists to close material product and UX ambiguity before implementation, preserve those decisions as explicit authority, compile them into downstream implementation obligations, detect implementation drift, and evaluate whether semantic interpretation is repeatable enough to trust.

It is not a single document generator. It is a staged authority-and-verification system.

## System structure

```text
JOEWRKS Product Definition System
│
├─ 1. Product Definition Core
│  ├─ evidence discovery
│  ├─ unknown / decision ledgers
│  ├─ canonical state.json authority
│  ├─ requirements / rules / data / flows / screens / states
│  ├─ stale + ripple propagation
│  ├─ Product / UX compilation
│  └─ deterministic Closure Gate
│
├─ 2. Downstream Conformance
│  ├─ joewrks.action-conformance/1.0
│  ├─ source provenance + derivation binding
│  ├─ implementation / Figma handoff obligations
│  ├─ runtime execution protocol
│  ├─ sequence verification
│  └─ implementation-drift evidence
│
├─ 3. Semantic Review
│  ├─ joewrks.semantic-review/1.0
│  ├─ reviewer brief
│  ├─ responsibility profile
│  ├─ semantic obligation index
│  ├─ review identity inventory
│  ├─ deterministic golden cases + normative oracle
│  └─ reliability gate
│
└─ 4. Evaluation & Calibration Harness
   ├─ behavioral / dogfood evaluations
   ├─ official calibration controller
   ├─ calibration control plane
   ├─ frozen raw-output evidence
   ├─ disagreement / reliability metrics
   └─ isolated reviewer execution boundary
```

## 1. Product Definition Core

The Product Definition Core converts an incomplete product request into explicit, reviewable authority.

Its central rule is that material product decisions are never silently invented. Missing decisions become unknowns, explicit answers become decisions, and every material change propagates through dependent requirements, flows, screens, states, rules, acceptance criteria, and implementation mappings.

The authoritative artifact is always:

```text
product-definition/<project-slug>/state.json
```

Markdown PRDs, plans, wireflows, handoffs, and summaries are projections of that state and do not replace it.

The core lifecycle is:

```text
Discover
→ Register Unknown
→ Rank Materiality
→ Ask / Resolve
→ Record Decision
→ Propagate Impact
→ Recompile
→ Discover Again
→ Closure Gate
```

Closure requires deterministic validation plus explicit approval of the current definition revision.

## 2. Downstream Conformance

After Product Definition Closure, the system compiles approved canonical clauses into executable downstream obligations.

The production handoff contract is:

```text
joewrks.action-conformance/1.0
```

This layer binds implementation obligations to exact canonical source IDs, JSON pointers, source hashes, derivation modes, runtime sequence expectations, and verification evidence.

It separates:

- product authority from implementation behavior;
- business state from delivery effects;
- structural validity from semantic proof;
- machine-derived semantics from review-required semantics.

It is read-only with respect to Product Definition authority.

## 3. Semantic Review

Some downstream semantic fields cannot be proven by deterministic extraction alone. Those fields remain `REVIEW_REQUIRED` and are evaluated through the semantic-review sidecar:

```text
joewrks.semantic-review/1.0
```

The semantic-review system binds every review decision to:

- exact reviewer package bytes;
- reviewer brief hash;
- responsibility rule;
- semantic obligation;
- expected review identity;
- canonical evidence;
- provenance hashes;
- required test references;
- explicit verdict and rationale code.

The responsibility model currently covers **26 action semantic fields + 12 lifecycle semantic fields = 38 responsibility rules**.

The four terminal review outcomes are:

```text
APPROVED
REJECTED_CANDIDATE
RUBRIC_ERROR
INPUT_PACKAGE_ERROR
```

The reliability gate is conjunctive. Majority vote is not an escape hatch.

## 4. Evaluation & Calibration Harness

The evaluation layer measures whether the system behaves consistently under fresh execution rather than merely passing deterministic unit tests.

It includes:

- behavioral A/B evaluations;
- end-to-end dogfood;
- downstream-conformance experiments;
- semantic-review golden calibration;
- official calibration controller;
- raw-output freezing and evidence binding;
- reliability statistics and disagreement classification.

A valid real semantic-review calibration requires reviewer contexts that can access only their assigned reviewer package, run envelope, and invocation wrapper. Isolation must be enforced by the execution environment, not by instructions telling a reviewer to ignore other files.

## End-to-end authority flow

```text
Vague idea / evidence
        ↓
Product Definition Core
        ↓
canonical state.json
        ↓
Closure Gate
        ↓
Downstream Conformance compiler
        ↓
action-conformance contract
        ↓
Implementation / Figma Make
        ↓
runtime + drift evidence
        ↓
Semantic Review for REVIEW_REQUIRED fields
        ↓
Reliability Calibration
        ↓
Trusted downstream execution / later efficacy evaluation
```

Any material ambiguity discovered during implementation re-enters Product Definition instead of being decided silently downstream.

## Repository mapping

```text
skills/joewrks-product-definition/
├─ SKILL.md                         # Product Definition entrypoint
├─ references/                      # authority and workflow rules
├─ schemas/                         # canonical schemas
├─ templates/                       # generated projection templates
├─ scripts/                         # deterministic validators
└─ downstream/
   ├─ contracts.py                  # downstream contract compilation
   ├─ provenance.py                 # source binding
   ├─ verifier.py / invariants.py   # runtime conformance
   ├─ protocol.py                   # execution protocol
   ├─ adapters/                     # runtime adapters
   └─ semantic_review/              # v0.4.3 semantic-review core

evals/
├─ behavioral-v0.2/                 # behavioral evaluation
├─ downstream-conformance-v0.4*/    # downstream experiments/evidence
└─ semantic-review-v0.4.3/          # semantic-review spec/calibration/evidence

tests/
└─ fixtures/semantic-review-v1/     # frozen golden packages/oracle fixtures
```

## Version progression

The repository evolved in layers rather than replacing its earlier core:

- **v0.1.x** — deterministic Product Definition authority, state contract, Closure Gate.
- **v0.2** — behavioral interrogation refinement and A/B evaluation.
- **v0.3.x** — end-to-end dogfood, Figma / Figma Make handoff and drift auditing.
- **v0.4 / v0.4.1.x** — cross-domain downstream conformance and executable action-contract authority.
- **v0.4.2** — fresh downstream-contract efficacy experiment; stopped before paired result after review-construction instability.
- **v0.4.3** — deterministic semantic-review contract, responsibility model, reliability gate, calibration controller, and control-plane hardening.

## Current v0.4.3 boundary

The current frozen status is deliberately narrower than a calibration PASS:

| Boundary | Status |
| --- | --- |
| v0.4.3 specification | `VERIFIED` |
| semantic-review implementation | `VERIFIED` |
| calibration control plane | `VERIFIED_AFTER_RUN_01_REPAIR` |
| Run-01 | `INVALID / CONTROL_PLANE_DEFECT` |
| valid real calibration runs | `0` |
| real reviewer reliability | `NOT_MEASURED` |
| calibration PASS | `NOT_CLAIMED` |
| calibration FAIL | `NOT_CLAIMED` |
| current blocker | `MANIFEST_ONLY_ISOLATION_UNAVAILABLE` |
| v0.4.4 | `BLOCKED_ON_VALID_V043_RELIABILITY_CALIBRATION` |

The capability probe established that the current collaboration/Codex execution environment can read repository-side Run-01 evidence, so it cannot truthfully provide package-only reviewer isolation. No semantic defect or rubric defect is inferred from that environment limitation.

## Future execution boundary

The next valid real calibration run starts only after an isolated reviewer runner proves that each fresh reviewer context can read its assigned package and envelope while the repository, Run-01 evidence, golden answers, seed oracle, prior outputs, and sibling packages are unavailable.

The isolation runner is infrastructure around this system; it does not become Product Definition authority and must not modify the semantic-review core merely to satisfy the environment.
