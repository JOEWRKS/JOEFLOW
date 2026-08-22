# v0.4 Ranked Refinement Candidates

## Executive Summary

- **Do not modify Product Definition generation or Closure from this evidence.** All three canonical definitions were valid, explicit, and closed; no repeated missing-unknown failure was identified.
- **Prioritize executable downstream verification over more prose.** The strongest actionable evidence is that material state drift survived detailed handoffs and green suites.
- **Apply the predeclared threshold conservatively.** The ranked candidates below either replicate materially in 3/3 products or in 2/3 different domains at BLOCKING/MAJOR severity. Product-specific and cosmetic findings are excluded.

## Ownership Decision

| Layer | Refinement decision | Reason |
|---|---|---|
| Product Definition generation | **No change justified** | Three Product Definitions and Closure gates passed; canonical reversals and authority rules were explicit. |
| Implementation / Figma-Make handoff | **Refine** | Generators repeatedly lost authority, lifecycle, reversal, concurrency, delivery, and provenance semantics. |
| Drift audit | **Refine** | Cross-layer sequence tracing found failures that labels, source presence, and green tests missed. |
| Test / verification contract | **Refine first** | Both Codex runs retained material drift behind passing suites. |

## 1. Require Executable Action-to-State Conformance Tests

- **Owning layer:** test/verification contract.
- **Evidence count:** 2/3 products, two domains, Codex generator; BLOCKING/MAJOR.
- **Affected products:** `studio-booking-dogfood`, `expense-reimbursement-dogfood`.
- **Generators:** Codex.
- **Exact problem:** A's 14/14 tests did not detect the systematic UI-to-domain disconnect (`A-CODEX-DRIFT-001`, `A-CODEX-DRIFT-009`). B's 85/85 unit/component and 11/11 E2E tests did not detect final `B030`, `B031`, `M006`, `M012`, `M013`, `M014`, or `M027`.
- **Proposed contract-level improvement:** every material visible action must have at least one executable sequence that starts from canonical preconditions, invokes the public UI/action path, and asserts domain state, version, audit/history, side effects, visible result, and recovery. Rejected, stale, unauthorized, duplicate, and expired paths must assert a deep unchanged-state/no-side-effect result.
- **What NOT to change:** do not raise required test counts, accept handler/source presence as coverage, add product-specific fixtures to the Product Agent schema, or treat build success as semantic evidence.
- **Regression/evaluation strategy:** replay a generated action matrix; fail on any missing public path or mismatched postcondition. Include later-state idempotent replay, rejected-command atomicity, authority loss after initial access, historical event projection, and time-worker stop conditions. Re-run against the frozen A and B implementations and require the harness to fail on their known final findings.

## 2. Add an Authority and Exact-Object Invariant Pack to Downstream Handoffs

- **Owning layer:** implementation/Figma-Make handoff, with generator adapters.
- **Evidence count:** 3/3 products; actual Figma Make plus Codex; BLOCKING/MAJOR.
- **Affected products:** all three.
- **Generators:** actual Figma Make and Codex.
- **Exact problem:** Make `DRIFT-001`, `DRIFT-002`, `DRIFT-003`, A `A-CODEX-DRIFT-002`, `A-CODEX-DRIFT-005`, `A-CODEX-DRIFT-007`, and B `B-CODEX-001`, `B-CODEX-004`, `B-CODEX-007`, `B-CODEX-022`, `B-CODEX-024`, `B-CODEX-025` each lost some combination of authenticated actor, current relationship, exact object/revision, or immediate authority-loss behavior.
- **Proposed contract-level improvement:** emit a compact per-action authority record: actor role, authenticated/session requirement, exact object/revision/file binding, relationship predicate, self-action exclusion, reauthorization point, and authority-loss result. Mark read projections and downloads separately from mutation authority.
- **What NOT to change:** do not add new roles, permissions, or unknown taxonomy; do not duplicate full Product Definition prose; do not weaken dynamic least privilege to make generated UI simpler.
- **Regression/evaluation strategy:** for every protected action, test valid authority, wrong role, wrong object/revision, self-action, deactivated account, reassignment, and post-generation authority loss. Require both mutation and historical/download visibility to disappear where the canonical contract says so.

## 3. Make Current-Only Lifecycle and Reversal Semantics Machine-Explicit

- **Owning layer:** implementation/Figma-Make handoff plus generator behavior.
- **Evidence count:** 3/3 products; both generator identities; BLOCKING/MAJOR.
- **Affected products:** all three.
- **Generators:** actual Figma Make and Codex.
- **Exact problem:** Make `DRIFT-004`, `DRIFT-005`, A `A-CODEX-DRIFT-005`, `A-CODEX-DRIFT-007`, and B `B-CODEX-002`, `B-CODEX-008`, `B-CODEX-023`, `B030` lost expiry, irreversible/bounded-reversal, or recovery constraints. B's Critical Failure activated superseded `DEC-021` even though current `DEC-022`, `RULE-061`, projections, and handoff were correct.
- **Proposed contract-level improvement:** handoffs should export current lifecycle states and allowed transitions as a versioned graph, with explicit reversal windows, required reason/confirmation/evidence, same-object versus new-object result, history preservation, and a machine-readable list of superseded rules that must never drive active behavior.
- **What NOT to change:** do not remove historical decisions from canonical provenance, rewrite old records, or add a Closure rule merely because a downstream generator ignored a current rule.
- **Regression/evaluation strategy:** generate forward, boundary, forbidden, and reversal sequences from the graph. Include before/at/after boundary probes, old-link/object resurrection checks, and a sentinel test that fails if any superseded transition becomes active.

## 4. Gate Concurrency, Idempotency, and Rejected-Command No-Op as One Atomicity Suite

- **Owning layer:** test/verification contract and domain-engine adapter.
- **Evidence count:** concurrency/idempotency in 3/3 products; explicit rejected-command mutation in 2/3 Codex products; BLOCKING/MAJOR.
- **Affected products:** all three.
- **Generators:** actual Figma Make and Codex.
- **Exact problem:** Make `DRIFT-006`, A `A-CODEX-DRIFT-006`, `A-CODEX-DRIFT-007`, and B `B-CODEX-006`, `M006`, `M027`, `B030` show that partial version checks or duplicate handling do not prove atomic behavior. B030 mutated verification on a rejected command without version/audit and then bypassed a safety guard.
- **Proposed contract-level improvement:** define a standard command-result envelope with expected version, idempotency key, committed-result replay identity, latest values/changed fields for stale responses, and a deep no-op checksum spanning domain state, version, audit, and side effects on rejection.
- **What NOT to change:** do not encode database/vendor mechanics, assume last-write-wins, or accept an error response as proof of no mutation.
- **Regression/evaluation strategy:** run paired concurrent commands, repeated same-key calls before and after later state changes, stale commands, validation failures after partial input, and delivery/manual-retry duplication. Compare complete pre/post snapshots and event identities.

## 5. Standardize Business-State, Delivery, and Provenance Separation

- **Owning layer:** implementation/Figma-Make handoff and integration-test contract.
- **Evidence count:** 3/3 products; both generator identities; MAJOR, with BLOCKING consequences in combined paths.
- **Affected products:** all three.
- **Generators:** actual Figma Make and Codex.
- **Exact problem:** Make `DRIFT-008`, `DRIFT-010`, A `A-CODEX-DRIFT-001`, `A-CODEX-DRIFT-004`, `A-CODEX-DRIFT-006`, `A-CODEX-DRIFT-007`, and B `M012`, `M013`, `M014`, `M027` mixed or omitted delivery retries, event-time history, immutable snapshots, recipients, stop conditions, and current-versus-historical projection truth.
- **Proposed contract-level improvement:** provide separate schemas for business events, delivery attempts, immutable snapshots, and authorized projections. Each action contract should state business commit result, delivery recipients/event key/retry-stop policy, append-only provenance, and user-safe versus raw-audit fields.
- **What NOT to change:** do not roll back business state on delivery failure, project current state onto historical events, expose raw diagnostic fields, or turn audit append into a substitute for the required domain mutation.
- **Regression/evaluation strategy:** test success plus delivery failure, duplicate/retry, stop-after-terminal-state, recipient matrices, immutable snapshot after later rename/change, event-time status reconstruction, masking, and authority loss for history/downloads.

## 6. Make the Drift Audit a Required Cross-Layer Sequence Gate

- **Owning layer:** drift audit.
- **Evidence count:** 3/3 products; both generator identities; all material severities.
- **Affected products:** all three.
- **Generators:** actual Figma Make and Codex.
- **Exact problem:** labels, routes, screen inventories, handlers, helper tests, and build success repeatedly appeared correct while active behavior drifted. Material drift was found only when auditors traced canonical precondition → visible action → handler → domain state → side effects/history → visible recovery.
- **Proposed contract-level improvement:** require that trace for every material action family, with source readback and at least one fresh runtime probe for high-risk authority, reversal, concurrency, retention, money, and destructive paths. Preserve blind-auditor independence and exact source/artifact pins.
- **What NOT to change:** do not replace audit with static checklists, self-reported implementation summaries, test counts, or visual similarity; do not downgrade new findings because a correction budget is exhausted.
- **Regression/evaluation strategy:** apply the gate retroactively to v0.3.1, A, and B frozen artifacts. The audit should reproduce initial material findings, recognize corrected Make behavior, and still fail the frozen A/B final states.

## 7. Verify Responsive Behavior, Not Only Overflow

- **Owning layer:** Figma adapter, visual audit, and browser verification contract.
- **Evidence count:** 2/3 products across actual Figma Make and Codex; MAJOR.
- **Affected products:** `client-feedback-portal-dogfood`, `expense-reimbursement-dogfood`.
- **Generators:** actual Figma Make and Codex.
- **Exact problem:** Make `DRIFT-011` omitted mobile review behavior; B `M014` retained an unreadable mobile Audit/export composition while `m021` hid navigation in a dense scroller. Zero page overflow did not establish usable mobile parity.
- **Proposed contract-level improvement:** define mobile checks for action availability, single-column ordering, readable audit/data composition, recovery visibility, focus, and role/state parity in addition to viewport overflow.
- **What NOT to change:** do not impose final branding, promote cosmetic MINOR differences, or treat screenshot similarity as domain correctness.
- **Regression/evaluation strategy:** inspect canonical mobile journeys at 320/375/390 widths, run keyboard/focus and long-content cases, and assert that every material desktop action and recovery path has an authorized mobile presentation or an explicit canonical exception.

## Excluded from Permanent Refinement

- Product-specific rules: Make PDF annotation coordinates and Changes-request evidence; A operating hours/equipment and policy pricing; B receipt hash, FX, finite-money, and settlement-adjustment details except where they instantiate a promoted general invariant.
- Cosmetic MINORs: unsupported branding residue, category-label punctuation/wording, and minor navigation density when no material action is blocked.
- Tool capability boundaries: unavailable Make source export during finalization, unavailable Open Design in one run, and runtime/browser availability incidents.
- Evaluator mistakes or unverified observations: only frozen, reproduced findings support candidates.

## Recommended v0.4.x Scope

The next task should implement candidates 1–6 as a bounded **downstream conformance layer**, starting with a machine-readable action contract and a sequence-test runner against the existing frozen Product Definitions. Candidate 7 may follow in the same version only if it stays a presentation/behavior gate and does not introduce product semantics.

Do not modify Product Definition interrogation, taxonomy, schema, validators, or Closure until a refined downstream run demonstrates a repeated upstream information gap rather than downstream non-consumption of already-explicit truth.
