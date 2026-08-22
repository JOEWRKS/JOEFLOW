# Replication B Codex Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans` for inline execution. A separate fresh subagent is reserved for the blind audit. Steps use checkbox syntax for tracking.

**Goal:** Build and independently audit a working React/TypeScript/Vite expense-reimbursement SPA whose visible actions agree with a deterministic revision-55 domain model.

**Architecture:** `codex-implementation/` contains a pure command-driven domain engine and a React adapter. Commands return committed/rejected domain results plus audit and simulated-delivery effects; React renders four role surfaces from selectors and never owns business truth. Browser storage is an explicitly simulated repository with a deterministic reset fixture.

**Tech Stack:** React, TypeScript, Vite, Vitest, React Testing Library, Playwright, CSS custom properties/plain CSS.

**Spec:** `product-definition/expense-reimbursement-dogfood/CODEX_IMPLEMENTATION_HANDOFF.md`

## Global constraints

- Exact baseline: `585325a6fb76658d54ec631e224bf6aeb96137d8`; branch: `eval/v0.4-replication-b-codex`.
- Canonical revision/digest remain `55` / `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`.
- No Product Definition, Skill, interrogation engine, validator, schema, Closure, Figma, Replication A, or hidden-answer-bank input may be modified or used.
- No real payment, email, authentication-security, encryption, immutable-database, provider, or production-concurrency claim.
- Every implemented mutation must be tested for domain state, audit/effect behavior, and visible result—not button presence alone.

---

### Task 1: Scaffold the isolated application and test harness

**Files:**
- Create: `codex-implementation/package.json`
- Create: `codex-implementation/package-lock.json`
- Create: `codex-implementation/index.html`
- Create: `codex-implementation/vite.config.ts`
- Create: `codex-implementation/tsconfig.json`
- Create: `codex-implementation/playwright.config.ts`
- Create: `codex-implementation/src/main.tsx`
- Create: `codex-implementation/src/test/setup.ts`

**Interfaces:**
- Produces scripts `dev`, `build`, `test`, `test:e2e` and a browser entry at `/`.

- [ ] Create the Vite/React/TypeScript package with pinned lockfile and no Tailwind dependency.
- [ ] Add Vitest jsdom setup and Playwright Chromium configuration using a task-owned preview command.
- [ ] Add a failing smoke test that expects the four canonical role choices.
- [ ] Run `npm test -- --run` and confirm the smoke test fails because `App` is absent.
- [ ] Add the minimal application entry and re-run the smoke test to pass.

### Task 2: Implement the pure domain contract

**Files:**
- Create: `codex-implementation/src/domain/types.ts`
- Create: `codex-implementation/src/domain/seed.ts`
- Create: `codex-implementation/src/domain/commands.ts`
- Create: `codex-implementation/src/domain/engine.ts`
- Create: `codex-implementation/src/domain/selectors.ts`
- Create: `codex-implementation/src/domain/persistence.ts`
- Test: `codex-implementation/src/domain/engine.test.ts`

**Interfaces:**
- Produces `DomainState`, `DomainCommand`, `CommandResult`, `createSeedState()`, `executeCommand(state, command)`, `loadState()`, `saveState()`, and role-scoped selectors.
- `DomainCommand` always includes `{ actorId, targetId, expectedVersion, idempotencyKey, type, input }`.
- `CommandResult` is `{ state, outcome, auditEventIds, deliveryEventIds, changedFields }`.

- [ ] Write failing tests for role/relationship denial, self-approval denial, stale no-op, exact idempotency replay, latest-revision guard, and append-only audit.
- [ ] Implement shared authorization, version, fingerprint, idempotency, audit, and separate simulated delivery primitives.
- [ ] Write failing lifecycle tests for submit/change/resubmit/final reject/withdraw/approve/revoke and payment pending/scheduled/completed/failed/hold.
- [ ] Implement only the transitions and guards pinned in the handoff.
- [ ] Write failing tests for failed-payment verification, one-active adjustment, completed-only net totals, and Needs verification blocking.
- [ ] Implement the Finance verification and adjustment commands, then run all domain tests.

### Task 3: Build the shared application shell and state presentation

**Files:**
- Create: `codex-implementation/src/app/App.tsx`
- Create: `codex-implementation/src/app/App.test.tsx`
- Create: `codex-implementation/src/app/useDomain.ts`
- Create: `codex-implementation/src/components/RoleSwitcher.tsx`
- Create: `codex-implementation/src/components/StatusBadge.tsx`
- Create: `codex-implementation/src/components/FeedbackRegion.tsx`
- Create: `codex-implementation/src/components/CommandDialog.tsx`
- Create: `codex-implementation/src/components/StateLab.tsx`
- Create: `codex-implementation/src/styles.css`

**Interfaces:**
- `useDomain()` exposes `{ state, dispatch, reset, feedback }`.
- `CommandDialog` returns validated structured input and restores focus to its trigger.
- `StateLab` selects deterministic presentations for all 16 canonical UX states without mutating business truth.

- [ ] Write failing integration tests for role switching, current-state text, live feedback, dialog labels, focus restoration, and status-not-color-only.
- [ ] Implement the neutral operational shell and shared components.
- [ ] Implement deterministic loading/empty/partial/error/permission/offline/timeout/retrying/submitting/completed/cancelled/expired presentations.
- [ ] Run component tests and an accessibility-name query for every interactive control.

### Task 4: Implement Employee workflows

**Files:**
- Create: `codex-implementation/src/features/employee/EmployeeSurface.tsx`
- Create: `codex-implementation/src/features/employee/ClaimEditor.tsx`
- Create: `codex-implementation/src/features/employee/AttachmentPanel.tsx`
- Create: `codex-implementation/src/features/employee/RevisionTimeline.tsx`
- Test: `codex-implementation/src/features/employee/EmployeeSurface.test.tsx`

**Interfaces:**
- Consumes Employee selectors and `dispatch`.
- Produces actual create/edit/autosave/upload/submit/withdraw/delete/revise/resubmit mutations and read-only revision history.

- [ ] Write failing UI tests for required fields, future/late date, active category, foreign conversion ±1 KRW, duplicate reason, manager guard, and clean receipt guard.
- [ ] Implement the editor, upload/scan simulation, autosave states/retry disclosure, and input preservation.
- [ ] Write failing click-through tests for submit, withdraw, delete draft confirmation, Changes-requested revision, and resubmit.
- [ ] Connect every visible action to the domain engine and verify resulting state/audit/delivery output.

### Task 5: Implement Manager workflows

**Files:**
- Create: `codex-implementation/src/features/manager/ManagerSurface.tsx`
- Create: `codex-implementation/src/features/manager/ReviewPanel.tsx`
- Test: `codex-implementation/src/features/manager/ManagerSurface.test.tsx`

**Interfaces:**
- Produces approve, request-changes, final-reject, and pre-Scheduled revoke commands against the exact displayed revision/version.

- [ ] Write failing tests for scope, revision pinning, required comments/reason, stale conflict, self-approval denial, and post-Scheduled revoke denial.
- [ ] Implement queue/detail/history, late/duplicate/FX visibility, decision dialog, and approval reversal.
- [ ] Assert each visible result reflects the committed domain state and no stale/denied action writes audit or deliveries.

### Task 6: Implement Finance workflows

**Files:**
- Create: `codex-implementation/src/features/finance/FinanceSurface.tsx`
- Create: `codex-implementation/src/features/finance/PaymentPanel.tsx`
- Create: `codex-implementation/src/features/finance/AdjustmentPanel.tsx`
- Test: `codex-implementation/src/features/finance/FinanceSurface.test.tsx`

**Interfaces:**
- Produces atomic schedule/claim, complete, fail, hold, retry-verification, adjustment creation/completion/failure-resolution, and scoped export commands.

- [ ] Write failing tests for atomic owner claim, scheduled/actual date bounds, unique reference, Other description, failure reason, and hold reason.
- [ ] Implement payment queue/detail and transition forms.
- [ ] Write failing tests for structured Not-paid verification, one In-progress adjustment, net formula, Executed/Not executed/Unclear resolution, and new-adjustment blocking.
- [ ] Implement adjustment history/summary and visible uncertainty recovery.

### Task 7: Implement Admin, audit, delivery, and governed access workflows

**Files:**
- Create: `codex-implementation/src/features/admin/AdminSurface.tsx`
- Create: `codex-implementation/src/features/admin/AdminSurface.test.tsx`
- Create: `codex-implementation/src/components/Timeline.tsx`
- Create: `codex-implementation/src/components/ExportPanel.tsx`

**Interfaces:**
- Produces invitation issue/reissue/revoke, account/role state, direct manager, category, legal hold, reassignment, warning retry, raw audit, and Admin/Finance export commands.
- `Timeline` accepts a role-safe projection; raw audit is a distinct Admin-only input.

- [ ] Write failing tests for invitation expiry/reissue/revoke race, session invalidation, required Admin reasons, category snapshots/zero-active guard, and legal-hold atomicity.
- [ ] Implement the dedicated Admin modules and versioned command forms.
- [ ] Write failing tests for reassignment side-effect separation, one manual delivery retry, timeline hidden fields, export role/row/reauthorization limits, and raw-token absence.
- [ ] Implement governed timeline, raw audit, operational warnings, and CSV simulation.

### Task 8: Verify responsive behavior, accessibility, and runtime transitions

**Files:**
- Create: `codex-implementation/e2e/role-workflows.spec.ts`
- Create: `codex-implementation/e2e/responsive-accessibility.spec.ts`
- Modify: `codex-implementation/src/styles.css`

**Interfaces:**
- Browser tests use only public UI controls and assert visible plus persisted simulated domain outcomes.

- [ ] Write failing Playwright tests for one material end-to-end workflow per role and for stale/denied negative paths.
- [ ] Implement any missing UI adapter needed to make public interaction reach the correct domain command.
- [ ] Add 1440, 375, and 320 viewport checks for page-level overflow, reachable actions, labeled controls, error association, focus, and text status.
- [ ] Add reduced-motion media checks and run the complete unit/integration/E2E/build suite.

### Task 9: Produce implementation evidence and freeze the audit target

**Files:**
- Create: `evals/cross-domain-v0.4/replication-b-expense-reimbursement/codex-implementation-report.md`
- Create after blind audit: `evals/cross-domain-v0.4/replication-b-expense-reimbursement/codex-initial-audit.md`
- Create only when used: correction-pass and re-audit reports
- Create: `evals/cross-domain-v0.4/replication-b-expense-reimbursement/CODEX_IMPLEMENTATION_REVIEW.md`
- Modify: `evals/cross-domain-v0.4/replication-b-expense-reimbursement/aggregate-results.md`

- [ ] Record exact source, dependencies, commands, tests, runtime paths, boundaries, and baseline hashes.
- [ ] Dispatch a fresh evaluator that may read only B authority/Figma/handoff/source/tests/runtime and must derive findings independently.
- [ ] If BLOCKING/MAJOR exists, perform at most three targeted correction passes with source readback, tests, and fresh scoped re-audit after each.
- [ ] Run visual-check and final state/Closure/baseline-integrity verification.
- [ ] Commit the exact verdict state, push only `eval/v0.4-replication-b-codex`, and verify remote readback without merge or cross-domain comparison.
