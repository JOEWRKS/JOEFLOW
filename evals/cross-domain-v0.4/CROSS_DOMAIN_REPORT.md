# v0.4 Cross-Domain / Cross-Generator Evidence Report

## Executive Summary

- **Overall verdict: `PARTIAL — CROSS_DOMAIN_PRODUCT_DEFINITION_VERIFIED; DOWNSTREAM_CONFORMANCE_UNRESOLVED`.** All three Product Definitions and native Figma stages passed, but only the actual Figma Make run converged to zero material implementation drift. Both independent Codex implementations stopped after three correction passes with material drift.
- **Replication C: `NOT REQUIRED — SKIP`.** The predeclared stopping threshold is already met by multiple material families across three different products and both generator identities, and by additional two-domain Codex-only replication. A fourth product would add cost without changing the immediate ownership decision.
- **Product Agent refinement: not justified by this evidence.** Canonical Product Definitions, decision supersession, Closure, and Figma authority were correct in all three runs. The failures arose after Closure, principally in generator behavior, executable handoff consumption, UI-to-domain wiring, and verification/test coverage.
- **Downstream refinement: justified.** v0.4.x should add an executable conformance contract and sequence-based audit/test gate for authority, lifecycle/reversal, no-op integrity, idempotency, delivery separation, and provenance before changing Product Definition interrogation or Closure rules.

## Evidence Boundary and Comparison Basis

This report compares frozen evidence only. No implementation branch was merged and no Product Definition, Figma artifact, Skill, validator, schema, or implementation source was changed.

| Run | Product | Generator identity | Frozen evidence pin | Product/Figma authority |
|---|---|---|---|---|
| v0.3.1 | `client-feedback-portal-dogfood` | **Actual Figma Make** | `16fc6edc362321ea03613339e224472b98bc1a04` | Product Definition rev 44; native Figma and actual Make evidence |
| Replication A | `studio-booking-dogfood` | **Codex** | `9408434e640b9cf0bf6afaadd8f9d1f5f52e8943` | Product Definition rev 62; native Figma `fClM2GgNhwEDIiqZcIWhNZ` |
| Replication B | `expense-reimbursement-dogfood` | **Codex** | `5155a0a348b43804b703b79004bd0bbebff35c0a` | Product Definition rev 55; native Figma `fyow2BHoAXzpkzpozDGWXf` |

Replication B's final implementation source is separately pinned at `eecebc28701006dd2c7be4045a22542e34719705`. The unit of comparison is a material violated invariant, not a raw finding count: product scopes and audit surfaces differ, so severity totals are not added into a synthetic cross-run score. Exact tables are used instead of a chart because there are only three fixed runs and stage/finding semantics are not commensurable as a continuous metric.

## Three Runs Establish a Mixed but Decisive Outcome

The Product Definition and design pipeline replicated; implementation conformance did not. The Make run converged after correction, while both Codex runs exhausted the same three-pass budget without reaching the material gate.

| Run | Product Definition | Figma | Initial implementation audit | Correction passes | Final implementation audit | Critical Failure | Run verdict |
|---|---|---|---:|---:|---:|---:|---|
| v0.3.1 / Actual Figma Make | PASS | PASS | 5 BLOCKING / 7 MAJOR / 1 MINOR | 3 | 0 BLOCKING / 0 MAJOR; intentional MINOR residuals | 0 | `PASS — END_TO_END_VERIFIED`; 94/100 |
| Replication A / Codex | rev 62 PASS | PASS | 1 BLOCKING / 8 MAJOR / 1 MINOR | 3 | 1 BLOCKING / 8 MAJOR / 1 MINOR | 0 | `FAIL — CODEX_DRIFT_UNRESOLVED` |
| Replication B / Codex | rev 55 PASS | PASS | 9 BLOCKING / 9 MAJOR / 3 MINOR | 3 | 2 BLOCKING / 5 MAJOR / 2 MINOR | Yes | `FAIL — CODEX_DRIFT_UNRESOLVED` |

Replication B's final suite was green—85/85 unit/component tests, 11/11 Playwright tests, and a passing build—while two BLOCKING and five MAJOR findings remained. Replication A similarly ended with 14/14 tests passing while its dominant UI-to-domain disconnect remained. Passing test counts therefore cannot serve as the implementation-conformance gate.

## Classification Rules

- `STRONG_CROSS_GENERATOR_REPLICATION`: materially present in all three products and both generator identities.
- `CROSS_GENERATOR_REPLICATION`: materially present in two products and includes both actual Figma Make and Codex.
- `CODEX_ONLY_REPLICATION`: materially present in both Codex products, with no safe Make match.
- `MAKE_ONLY_SO_FAR`: observed only in the Make run and not safely generalized.
- `PRODUCT_SPECIFIC`: depends on a domain-specific contract and should not be generalized by label alone.
- `NEW_PATTERN`: first identified in the latest/final evidence and not yet independently replicated.

A family groups findings only when the same invariant was violated. Similar-looking UI symptoms or domain nouns are not enough.

## Strongest Replicated Failure Families

| Failure family / classification | Supporting evidence: run, generator, stage, severity, exact IDs | Canonical contract involved | Likely owning layer | Refinement threshold |
|---|---|---|---|---|
| Authority, role, session, and exact-object binding — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial BLOCKING `DRIFT-001`, `DRIFT-002`, `DRIFT-003`; A Codex initial/final MAJOR `A-CODEX-DRIFT-002`, `A-CODEX-DRIFT-005`, `A-CODEX-DRIFT-007`; B Codex initial BLOCKING `B-CODEX-001`, `B-CODEX-004`, `B-CODEX-007`, pass-1 BLOCKING `B-CODEX-022`, pass-2 BLOCKING `B-CODEX-024`, `B-CODEX-025` | Authenticated actor, current role/relationship, exact Version/revision/file, immediate authority-loss revocation | Generator behavior plus implementation/Figma-Make handoff and conformance tests | **Met: 3/3, both generators** |
| Lifecycle, expiry, and recovery — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial BLOCKING `DRIFT-004`, `DRIFT-005` and MAJOR `DRIFT-007`; A Codex initial/final MAJOR `A-CODEX-DRIFT-005`, `A-CODEX-DRIFT-007`; B Codex initial BLOCKING `B-CODEX-003`, MAJOR `M-CODEX-016`, `M-CODEX-018`, pass-2 BLOCKING `B-CODEX-026`, final MAJOR `M012` | Current lifecycle state, expiry/retention clocks, recovery without resurrection or orphan state, legal hold | Generator behavior, executable handoff, sequence verification | **Met: 3/3, both generators** |
| Irreversible or bounded-reversal semantics — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial BLOCKING `DRIFT-004`, `DRIFT-005`; A Codex final MAJOR `A-CODEX-DRIFT-007`; B Codex initial BLOCKING `B-CODEX-002`, `B-CODEX-008`, pass-1 BLOCKING `B-CODEX-023`, final BLOCKING `B030` | Current-only reversal rule, required reason/confirmation, exact precondition, no resurrection, preserved history | Generator behavior and reversal-focused conformance tests | **Met: 3/3, both generators** |
| Optimistic concurrency — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial MAJOR `DRIFT-006`; A Codex final MAJOR `A-CODEX-DRIFT-007`; B Codex initial BLOCKING `B-CODEX-006`, final MAJOR `M006` | Expected version, stale atomic no-op, latest values and changed fields | Implementation handoff, generator adapter, negative-path integration tests | **Met: 3/3, both generators** |
| Idempotency and operation identity — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial MAJOR `DRIFT-006`; A Codex final MAJOR `A-CODEX-DRIFT-006`, `A-CODEX-DRIFT-007`; B Codex initial BLOCKING `B-CODEX-006`, final MAJOR `M027` | Same-key replay of the original committed result without duplicate mutation/delivery, bounded manual retry identity | Generator behavior and implementation verification contract | **Met: 3/3, both generators** |
| Rejected-command no-op integrity — `CODEX_ONLY_REPLICATION` | A Codex final MAJOR `A-CODEX-DRIFT-007`; B Codex initial BLOCKING `B-CODEX-006` and final BLOCKING `B030` | Rejected/stale commands mutate no domain state, version, audit, or side effect | Domain engine architecture and sequence-based tests | **Met: 2/3, two domains, BLOCKING/MAJOR** |
| Business state versus delivery/notification separation — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial MAJOR `DRIFT-008`; A Codex final MAJOR `A-CODEX-DRIFT-006`; B Codex final MAJOR `M012`, `M027` | Business commit independent from delivery attempts; recipient matrix; retry/stop/dedupe; no rollback on delivery failure | Handoff projection, generator behavior, operational-worker tests | **Met: 3/3, both generators** |
| Append-only audit, history, snapshot, and provenance — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial MAJOR `DRIFT-010`; A Codex final BLOCKING/MAJOR `A-CODEX-DRIFT-001`, `A-CODEX-DRIFT-004`, `A-CODEX-DRIFT-007`; B Codex final MAJOR `M013`, `M014` | Event-time truth, immutable revision/snapshot, before/after/actor/version provenance, authorized projections | Handoff plus audit projection and integration tests | **Met: 3/3, both generators** |
| UI-to-domain semantic wiring — `CODEX_ONLY_REPLICATION` | A Codex final BLOCKING `A-CODEX-DRIFT-001` and MAJOR `A-CODEX-DRIFT-008`; B Codex initial MAJOR `M-CODEX-010`, `M-CODEX-014`, `M-CODEX-017`, final MAJOR `M014` | Visible action must invoke its canonical handler and produce the required state, history, side effects, and recovery | Codex implementation architecture and browser integration tests | **Met: 2/3, two domains, BLOCKING/MAJOR** |
| Failure/recovery presentation versus actual state — `STRONG_CROSS_GENERATOR_REPLICATION` | Make initial MAJOR `DRIFT-007`, `DRIFT-008`; A Codex final MAJOR `A-CODEX-DRIFT-005`, `A-CODEX-DRIFT-006`, `A-CODEX-DRIFT-008`; B Codex initial/final MAJOR `M-CODEX-010`, `M-CODEX-012`, `M-CODEX-017` / `M012` | Visible error/retry/recovery must correspond to actual unchanged/changed state and operational status | Generator behavior, UI handoff, runtime audit | **Met: 3/3, both generators** |
| Verification and test blind spots — `CODEX_ONLY_REPLICATION` | A Codex final MAJOR `A-CODEX-DRIFT-009`; B Codex final BLOCKING `B030`, `B031` and MAJOR `M006`, `M012`, `M013`, `M014`, `M027` all survived 85/85 unit/component and 11/11 E2E | Action-to-handler-to-state sequence coverage, negative paths, authority loss, rejection atomicity, historical projection | Test/verification contract and audit gate | **Met: 2/3, two domains, BLOCKING/MAJOR** |
| Responsive behavioral composition — `CROSS_GENERATOR_REPLICATION` | Make initial MAJOR `DRIFT-011`; B Codex final MAJOR `M014` and MINOR `m021`; A responsive shell checks passed | Mobile availability, readable single-column composition, action/state parity, not merely zero overflow | Figma adapter, visual audit, browser checks | **Met: 2/3, both generators, material severity** |

The most consequential result is not that generators make different UI mistakes. It is that both generator types repeatedly preserve visible structure more reliably than deep state authority, reversal, concurrency, delivery, and provenance semantics.

## Generator-Specific and Product-Specific Findings

### Codex-specific replication

The two Codex runs share two material patterns not safely attributable to Make:

- **Systematic UI-to-domain disconnect:** A's 78 action labels often ended in a generic audit-success path (`A-CODEX-DRIFT-001`), while B contained narrower synthetic/disconnected surfaces such as attachment, state lab, and CSV behavior (`M-CODEX-010`, `M-CODEX-014`, `M-CODEX-017`).
- **Green-suite false confidence:** A's 14/14 suite tested inventories, helpers, and source tokens rather than rendered transitions (`A-CODEX-DRIFT-009`). B's 85/85 unit/component and 11/11 E2E suites still missed `B030`, `B031`, and five final MAJOR sequences.

These are `CODEX_ONLY_REPLICATION`, not evidence that Product Definition generation failed.

### Make-only-so-far and convergence behavior

No material Make-only family is strong enough for permanent promotion after separating product-specific PDF annotation and presentation residue. The distinctive Make outcome is **convergence**: initial material drift reached 0 BLOCKING / 0 MAJOR after three passes. Current connector limitations prevented a fresh Make source export during finalization, so the result relies on preserved historical source readbacks plus fresh artifact/version readback. That tool boundary is not a product or generator failure family.

### Product-specific manifestations

- Client feedback portal: PDF page/normalized-coordinate annotation (`DRIFT-009`) and Changes-request evidence (`DRIFT-012`).
- Studio booking: operating-hours/equipment conflict enforcement (`A-CODEX-DRIFT-003`) and price/policy consent snapshots (`A-CODEX-DRIFT-004`).
- Expense reimbursement: exact receipt-hash duplicate handling (`B-CODEX-009`), finite-money validation (`B031`), and settlement-adjustment safety (`B030`). `B031` is also a `NEW_PATTERN`: it is material but has not been independently replicated outside this domain.
- Cosmetic presentation/copy observations such as Make `DRIFT-013` and B `m030` remain MINOR and are not refinement candidates.

The preserved Make range `DRIFT-014` through `DRIFT-017` is not assigned to families because the frozen v0.3.1 record explicitly lacks enough independent prose to reconstruct the intermediate IDs or their original meanings safely.

## Replication B Critical Failure Was an Implementation Failure and an Audit Success

Replication B's run-level Critical Failure remains recorded even though correction later fixed the specific behavior.

| Diagnostic question | Determination | Evidence |
|---|---|---|
| Product Agent failure? | **No** | Canonical rev 55 marks `DEC-021` SUPERSEDED by current `DEC-022`; current `RULE-061` requires pre-Scheduled revocation to return the same revision to Submitted. Closure passed. |
| Projection failure? | **No** | The decision ledger explicitly states `DEC-021` is superseded, and the product projection describes eligible approval revocation. |
| Implementation handoff failure? | **No** | `CODEX_IMPLEMENTATION_HANDOFF.md` explicitly says the approving Manager may revoke before Scheduled, with reason, and the same revision returns to Submitted. |
| Implementation failure? | **Yes** | Initial `B-CODEX-002` implemented the superseded Changes-requested/new-revision outcome and even encoded it in tests. |
| Audit-detection success? | **Yes** | The blind audit detected the active superseded behavior despite green tests; later correction resolved the specific implementation path without changing canonical truth. |

The Critical Failure is therefore not erased by correction. It is evidence that downstream consumers can activate superseded semantics even when canonical state, projections, and handoff are correct.

## Product Agent Versus Downstream Diagnosis

### Product Agent refinement: not justified

All three Product Definitions closed correctly, preserved explicit reversals/supersession, passed their validators, and reached audited native Figma. No run required Product Definition re-entry, and no frozen evidence identifies a missing material unknown whose absence caused the final implementation failures. Adding more interrogation questions, taxonomy axes, schema fields, or Closure rules would not have prevented a generator from ignoring or miswiring already-explicit truth.

### Downstream refinement: justified

The evidence implicates four downstream layers:

1. **Implementation/Figma-Make handoff:** human-readable truth needs a compact executable invariant/action-transition companion, especially for current-only decisions, authority loss, rejection no-op, reversal, and side-effect separation.
2. **Generator behavior:** both generator types simplified deep semantics; Codex additionally produced tested helpers or catalogs that were disconnected from public UI paths.
3. **Drift audit:** the successful audits traced precondition → visible action → handler → state → history/side effects → recovery. That trace must become a required gate rather than an evaluator technique.
4. **Implementation verification/test contract:** counts, builds, happy paths, and helper tests must not satisfy conformance without sequence tests for negative paths, authority changes, rejection atomicity, historical projections, and time-driven workers.

## Replication C Decision

**Replication C: `NOT REQUIRED — SKIP`.**

The original stopping rule is satisfied in both ways:

- multiple families appear materially in **3/3 products** across actual Figma Make and Codex; and
- Codex-only UI/domain and test-blindness families appear in **2/3 products**, across different domains, at BLOCKING/MAJOR severity.

Replication C is therefore unlikely to change the next ownership decision. It should be reconsidered only after the downstream conformance contract is implemented, when a new run could evaluate whether that refinement works rather than merely collect a fourth instance of the same failure.

## Recommended v0.4.x Next Task

Run **`v0.4.1 — Executable Downstream Conformance Contract & Sequence-Test Harness`**.

The task should project existing canonical truth into machine-checkable action contracts and require generator-specific adapters plus blind sequence audits. It should not change Product Definition interrogation, taxonomy, schema, validators, or Closure semantics. Ranked candidates and regression strategies are defined in `REFINEMENT_CANDIDATES.md`; no refinement is implemented in this aggregation branch.

## Caveats and Assumptions

- This is a three-run frozen-evidence comparison, not a statistical estimate of generator defect rates.
- A and B differ in domain complexity and implementation architecture; raw severity counts are descriptive, not normalized performance scores.
- v0.3.1 final Make source was not freshly exportable by the available connector; its convergence claim uses preserved source-readback evidence plus fresh artifact/version confirmation.
- Runtime boundaries recorded by each run remain in force; no production authentication, payment, email, storage, concurrency, security, or load claim is inferred.
