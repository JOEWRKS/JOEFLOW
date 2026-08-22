# Codex Correction Pass 3 — Replication B Expense Reimbursement

## Frozen correction target

- Final allowed correction pass: `3/3`
- Corrected source commit: `eecebc28701006dd2c7be4045a22542e34719705`
- Corrected `codex-implementation/` tree: `6294fc9072521fdb762808b87203a7e8bac4f7f5`
- Authority: Product Definition revision `55`, digest `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`
- Figma authority: `fyow2BHoAXzpkzpozDGWXf`
- Correction scope: the 3 BLOCKING and 8 MAJOR findings in `codex-correction-pass-2-audit.md` only
- Product re-entry: none
- New product decisions: none
- Protected Product Definition, Skill, interrogation, schema, validator, and Closure files changed: none

## Test-first failure evidence

Eleven focused regression tests were added before the corresponding corrections. The first focused run produced `71 PASS / 11 FAIL`. Each failure mapped to one of the pass-2 BLOCKING or MAJOR findings: timeline scope/masking, stale CSV scope, legal-hold retention, stale comparison, scan due time, delivery retry schedule, governed file access, list semantics, notification recipients/dedupe, FX evidence, and Manager reassignment state.

## Corrections

### B-CODEX-024 — related-user timeline authorization and masking

- Related timelines now resolve every event to its governed claim and reuse current active-role plus current-relationship authorization.
- Finance history disappears immediately after Finance ownership is reassigned; Manager history follows current unfinished review authority; inactive accounts return no entries.
- The related projection is an explicit allowlist: action, business status, time, revision, directly involved actor display name/role, and Manager review comment only.
- Internal actor IDs, legal-hold reasons, Admin-only notes, file/hash diagnostics, versions, and raw before/after structures remain exclusive to the separately authorized Admin raw audit.
- The global role header no longer renders simulated internal actor IDs.

### B-CODEX-025 — stale-scope CSV download

- Each export persists the exact generated claim-ID scope alongside its filter snapshot and row count.
- Finance download recomputes latest Finance scope and denies the request if any stored row is no longer authorized.
- Generation, successful download, and denied download audit filter snapshot, row count, result, actor, and time.
- Admin and Finance still require their latest active role at both generation and download.

### B-CODEX-026 — legal-hold retention corruption

- Draft and seven-fiscal-year retention candidates skip deletion whenever legal hold is active.
- The skip is auditable as `SKIPPED_LEGAL_HOLD`; the claim, files, adjustments, and existing audit remain intact.
- Deterministic deletion failures leave data undeleted, write an `ERROR` audit, raise an operational warning, and remain eligible for the next daily run.
- Successful unheld deletion removes governed files, adjustments, grants, and expired retained audit state while preserving the deletion-result audit.
- The deterministic public job explicitly models the canonical `02:00 KST` schedule.

### M-CODEX-006 — stale-form comparison

- Stale results now return the latest server values for every intervening changed field as well as preserved browser input.
- The feedback region renders browser and latest-server values side by side before retry.

### M-CODEX-010 — scan retry schedule

- The engine rejects a scan worker invocation before `nextScanRetryAt`.
- The first timeout schedules 30 seconds; the first due retry schedules the final retry two minutes later; a second indeterminate retry discards bytes without affecting the rest of the draft.
- The public manual retry button was removed. A task-owned worker timer invokes the due command automatically and the UI displays the scheduled time while submission remains blocked.

### M-CODEX-012 — scheduled operations, failure, and retention

- Delivery failure processing now models initial failure followed by due-time-gated retries at 1, 10, and 60 minutes, then Permanent failure and Admin warning after all three retries fail.
- Logical event/channel unique keys are present on ordinary notifications as well as daily jobs.
- Review warnings resolve after the claim leaves Submitted, overdue delivery remains daily-deduped, draft deletion failure is recoverable, and seven-fiscal-year terminal retention is modeled.

### M-CODEX-013 — governed attachment access and provenance

- Employee, current Manager, and current Finance surfaces expose receipt/FX evidence through a five-minute user/file grant.
- Every download/range/retry request rechecks active account, latest roles, claim relationship, grant expiry, and exact file.
- Issuance, success, expiry denial, and authority-loss denial are append-only audited without any raw token field.
- Claim audit snapshots include changed child files and adjustments. Reissue and expiry also write target-specific invitation before/after events.

### M-CODEX-014 — list semantics

- Expense-date and submission-date ranges are independent.
- `Late expense` uses the canonical late-reason flag rather than Manager review delay; duplicate filtering remains separate.
- Expense date, submission date, amount, and recent-change sorts are explicit, and export rows use the exact filtered claim IDs.

### M-CODEX-027 — notification matrix and event dedupe

- Approval creates dual-channel Employee delivery and dual-channel shared-Finance-queue delivery.
- Settlement-adjustment resolution creates the required dual-channel Employee result delivery.
- Commit-generated notification events receive a deterministic logical-event key per target, recipient, version, and channel.

### M-CODEX-028 — FX evidence and Manager inspection

- FX evidence records one of card statement, bank exchange record, official-rate capture, or official-rate PDF.
- Submission rejects missing evidence type and exchange rates beyond six decimal places before applying the existing ±1 KRW calculation guard.
- Manager Review displays governed receipt/FX evidence and the same five-minute access controls before an approval action.

### M-CODEX-029 — Manager reassignment guard

- Domain and Admin UI permit reassignment only for an unfinished `Submitted` revision whose current Manager is inactive.
- Draft, terminal, approved, and payment-processing records reject reassignment without mutation.

## Fresh verification before source freeze

| Check | Result |
|---|---|
| State validator | PASS, exit `0`, `valid: true`, errors `[]` |
| Closure validator | PASS, exit `0`, `closed: true`, digest exact, every metric `0` |
| `npm test -- --run --reporter=dot` | PASS, 7 files, `85/85` tests |
| `npm run build` | PASS, 41 modules transformed |
| Worktree-local Chromium E2E | PASS, `11/11` |
| Dedicated visual capture test | PASS, `1/1`; Employee/Manager/Finance/Admin desktop plus Admin 320 px |
| Page-level mobile overflow | `0 px` at sampled Admin 320 px render |
| E2E server cleanup | port `4173` absent after both runs |

The five final screenshots were opened and inspected at native or tool-preserved detail. Role hierarchy, evidence controls, search/filter layout, CSV guidance, and Admin raw-audit separation were visible without overlap or clipping. The Admin mobile tab strip remains intentionally horizontally scrollable inside its own container; the page itself does not overflow.

Screenshot SHA-256 values:

- `employee-desktop.png`: `2604283cfaa9f24c9865b835c66e4494889833e319f2ed1ee7a04d8fb47cb57f`
- `manager-desktop.png`: `041fe62799d98e1e1652e387ffa694369316b1f25e96738952fd67231a74c39f`
- `finance-desktop.png`: `048d9e494e8c571db2b25a1e5a961547f9e3516886616cbcca66b5f1b1bc6a09`
- `admin-desktop.png`: `b39f4d0851c56d8d300e00bcf1dbab4e2f1e62e237af0caa71de6c61d8449ebe`
- `admin-mobile.png`: `51d83d7ea93204f36f66a45e27e6865fd4a145f154588ca738c35f8ef12a17ae`

## Verification boundary

This remains a deterministic local SPA and pure domain simulation. It does not claim production payment, email, authentication, malware scanning, encryption, object storage, immutable database, background infrastructure, current iOS Safari/Android Chrome engine behavior, or production concurrency. Figma remains design authority; Figma Make was not executed. Final BLOCKING/MAJOR counts are not asserted here and must come from the independent pass-3 blind audit of the frozen source commit above.
