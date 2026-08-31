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
| Current Product Definition state contract | `0.2.0` |
| Current downstream authority contract | `joewrks.action-conformance/2.1` |
| Current semantic-review boundary | `joewrks.semantic-review/2.1` / reliability `NOT_MEASURED` |
| Current protected `main` baseline | `efd96410f6401cbf9624328e94b795c315164b7f` |
| Repaired v0.4.3 calibration input | `748254d6def81080a2fd2736115a3ab5e0bde5a3` |
| v0.4.3 environment-blocked disposition | `6a0674c5d00a40790afef78cfa19494314b894e3` |

Installed routing markers:

```text
PRODUCT_DEFINITION_STATE_V2_DEFAULT
LEGACY_0_1_2_1_COMPATIBILITY_PRESERVED
DOWNSTREAM_V2_INSTALLED_ROUTING
SEMANTIC_REVIEW_V2_RELIABILITY_NOT_MEASURED
```

Current Product Definition state contract: `0.2.0`

Current V2 downstream authority contract: `joewrks.action-conformance/2.1`

Current V2 semantic review boundary: `joewrks.semantic-review/2.1` / reliability `NOT_MEASURED`

Historical compatibility: state `0.1.2.1`, `joewrks.action-conformance/1.0`, `joewrks.semantic-review/1.0`, and v0.4.3 evidence

These are contract identities, not an overall program release number.

## Purpose

The system exists to close material product and UX ambiguity before implementation, preserve those decisions as explicit authority, compile them into downstream implementation obligations, detect implementation drift, and evaluate whether semantic interpretation is repeatable enough to trust.

It is not a single document generator. It is a staged authority-and-verification system.

## System structure

```text
JOEWRKS Product Definition System
│
├─ 1. Product Definition Core
│  ├─ state contract 0.2.0 (installed default)
│  ├─ evidence discovery
│  ├─ Product Surface + Evidence + Contradictions
│  ├─ unknown / Materiality / decision authority
│  ├─ canonical state.json authority
│  ├─ requirements / rules / data / flows / screens / states
│  ├─ Core + specialist Grill coverage bindings
│  ├─ Approval Manifest + definition digest
│  └─ deterministic Semantic Closure Gate
│
├─ 2. Downstream Conformance
│  ├─ joewrks.handoff-definition/2.1 → joewrks.action-conformance/2.1
│  ├─ exact M4 source seeds + scope commitments
│  ├─ DIRECT_AUTHORITY / MACHINE_DERIVED / REVIEW_REQUIRED
│  ├─ hard SEMANTIC_AUTHORITY_GAP re-entry
│  ├─ implementation / Figma handoff obligations
│  └─ dependency-scoped audit
│
├─ 3. Semantic Review
│  ├─ joewrks.semantic-review/2.1 only for REVIEW_REQUIRED obligations
│  ├─ only legitimate REVIEW_REQUIRED obligations
│  ├─ exact obligation/value binding
│  ├─ assurance, never Product Definition authority
│  └─ reliability NOT_MEASURED
│
└─ 4. Evaluation & Calibration Harness
   ├─ behavioral / dogfood evaluations
   ├─ official calibration controller
   ├─ calibration control plane
   ├─ frozen raw-output evidence
   ├─ disagreement / reliability metrics
   └─ isolated reviewer execution boundary
```

Historical State `0.1.2.1`, downstream v1, semantic-review/1.0, the frozen execution transport, and v0.4.3 evidence remain available under their exact original identities. They are compatibility boundaries, not the installed V2 default.

## 1. Product Definition Core

The Product Definition Core converts an incomplete product request into explicit, reviewable authority.

Its central rule is that material product decisions are never silently invented. Missing decisions become unknowns, explicit answers become decisions, and every material change propagates through dependent requirements, flows, screens, states, rules, acceptance criteria, and implementation mappings.

The authoritative artifact is always:

```text
product-definition/<project-slug>/state.json
```

Markdown PRDs, plans, wireflows, handoffs, and summaries are projections of that state and do not replace it.

The current core lifecycle is:

```text
DISCOVER
→ CLOSE
→ FREEZE
→ APPROVE
→ HANDOFF
→ VERIFY
```

Semantic Closure requires deterministic validation, exact coverage-to-authority bindings, a matching Approval Manifest and definition digest, plus explicit approval of the current definition revision. It does not claim implementation completion.

## 2. Downstream Conformance

After Product Definition Closure, the system compiles approved canonical clauses into executable downstream obligations.

The current V2 handoff contract is:

```text
joewrks.action-conformance/2.1
```

This layer reuses exact M4 coverage bindings as source seeds, commits consumed seed and authority-scope identities, and materializes only handoffs with zero semantic authority gaps.

It separates:

- product authority from implementation behavior;
- direct authority from closed deterministic derivation;
- legitimate qualitative review from upstream authority gaps;
- global definition state from dependency-local contract validity.

Installed wrappers compile and audit from any consumer working directory without a persistent `PYTHONPATH`. This layer is read-only with respect to Product Definition authority.

Historical `joewrks.action-conformance/1.0` remains frozen and reproducible under its own contract.

## 3. Semantic Review

Some downstream semantic fields cannot be represented safely as structured Product Definition authority or closed derivation. Only responsibility-profile-approved fields may remain `REVIEW_REQUIRED` and enter the V2 semantic-review sidecar:

```text
joewrks.semantic-review/2.1
```

The semantic-review/2.1 package binds every obligation to the exact action contract, source obligations, proposed value hash, and responsibility rule. Review output is assurance evidence and may emit read-only affected-scope re-entry; it never modifies Product Definition or the action contract.

Semantic-review/2.1 reliability begins and remains `NOT_MEASURED` in this integration task. It does not inherit the v0.4.3 calibration disposition or any semantic-review/1.0 reliability claim.

Historical `joewrks.semantic-review/1.0`, its **26 action + 12 lifecycle = 38** responsibility rules, and v0.4.3 evidence remain factual frozen compatibility.

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
Semantic Closure + exact approval
        ↓
Downstream V2 compiler
        ↓
handoff-definition/2.1 → action-conformance/2.1 contract
        ↓
Implementation / Figma Make
        ↓
dependency audit + implementation evidence
        ↓
semantic-review/2.1 for legitimate REVIEW_REQUIRED fields
        ↓
re-entry for affected authority gaps or ambiguity
```

Any material ambiguity discovered during implementation re-enters Product Definition instead of being decided silently downstream.

## Repository mapping

```text
skills/joewrks-product-definition/
├─ SKILL.md                         # Product Definition entrypoint
├─ references/                      # authority and workflow rules
├─ schemas/                         # canonical schemas
├─ templates/                       # generated projection templates
├─ scripts/                         # validators + installed V2 wrappers
├─ downstream_v2/                   # frozen action-conformance/2.0 authority
├─ downstream_v21/                  # frozen current 2.1 semantic/package authority
├─ integration_v2/                  # M6 runtime verifier/report outside frozen packages
└─ downstream/                      # historical v1 compatibility
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

## Historical v0.4.3 calibration boundary

This frozen historical status is deliberately narrower than a calibration PASS and does not define the current V2 contract identities:

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

## Historical calibration execution boundary

The next valid real calibration run starts only after an isolated reviewer runner proves that each fresh reviewer context can read its assigned package and envelope while the repository, Run-01 evidence, golden answers, seed oracle, prior outputs, and sibling packages are unavailable.

The isolation runner is infrastructure around this system; it does not become Product Definition authority and must not modify the semantic-review core merely to satisfy the environment.
