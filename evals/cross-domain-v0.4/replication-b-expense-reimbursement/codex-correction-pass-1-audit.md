# Codex Correction Pass 1 Audit — Replication B Expense Reimbursement

## Verdict

**FAIL — CODEX_DRIFT_UNRESOLVED. Critical failure exists: yes.**

Correction pass 1 resolves **8** of the 21 initial findings, partially resolves **5**, and leaves **8** open. This fresh audit also found **2 BLOCKING** defects that were present in the initial implementation but were not separately identified by the initial audit.

Exact remaining severity counts, including the two new findings:

| Severity | Count |
|---|---:|
| BLOCKING | **2** |
| MAJOR | **10** |
| MINOR | **3** |
| **Total remaining** | **15** |

Critical failure exists because a deactivated account still reads governed claim and attachment data, and because Finance can create a second adjustment before resolving whether a failed adjustment executed externally. The second path can create duplicate money movement.

No new BLOCKING or MAJOR regression was introduced by correction pass 1. `B-CODEX-022` and `B-CODEX-023` are newly discovered but source comparison proves both existed at initial source `4881528`. Pass 1 introduced one MINOR regression within `m-CODEX-020`: category definitions were corrected to English while the seeded submitted-revision snapshot remained Korean.

## Frozen authority and inspected target

| Item | Fresh readback |
|---|---|
| Canonical Product Definition | `product-definition/expense-reimbursement-dogfood/state.json`, revision `55`, approved digest `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f` |
| Canonical file SHA-256 | `c0e790c3a8c35f0cdc894110f069ab4d7919aed388f0a4fad2c54e5ae8193395` |
| Implementation handoff | `product-definition/expense-reimbursement-dogfood/CODEX_IMPLEMENTATION_HANDOFF.md` |
| Corrected source commit | `465831be07d0b857b8642cd18ed3ae2e8b681029` |
| Corrected implementation subtree | `a0410ea06cdcb9a49e7ed17d1eb0914580c14ae6` |
| Audit branch / inspected HEAD | `eval/v0.4-replication-b-codex` / `bb04ff7e10504e48bc5fce88d87ea5e9f67d7028` |
| Source drift after corrected commit | `git diff 465831be..HEAD -- codex-implementation` returned no difference |
| Audited Figma authority | file `fyow2BHoAXzpkzpozDGWXf`; desktop root `1:6`; corrected UX root `4:69`; mobile roots `4:73`, `4:91`, `4:109`, `4:127`; state matrix `4:146`; action matrix `4:195` |

The supplied `a0410ea...` value is the `codex-implementation/` subtree of `465831be`, not the full repository tree. Git readback confirms the binding exactly.

## Fresh verification

| Check | Result | What it proves / does not prove |
|---|---|---|
| `python skills/joewrks-product-definition/scripts/validate_state.py product-definition/expense-reimbursement-dogfood/state.json` | exit `0`; `valid: true`; errors `[]` | Canonical structural validity only |
| `python skills/joewrks-product-definition/scripts/validate_closure.py product-definition/expense-reimbursement-dogfood/state.json` | exit `0`; `closed: true`; computed digest exact; every reported metric `0` | Canonical closure only |
| `npm test -- --run` | exit `0`; **6/6 files, 55/55 tests passed** | Covered unit/component behavior only |
| `npm run build` | exit `0`; TypeScript/Vite passed; 39 modules transformed | Buildability only |
| `PLAYWRIGHT_BROWSERS_PATH=<worktree>/codex-implementation/.playwright-browsers; npx playwright test` | exit `0`; **11/11 Chromium tests passed**; port 4173 free before and after | The existing E2E scenarios only |
| Fresh task-owned runtime at 1440×900 and 320×700 | Employee, Manager, Finance, and Admin each measured **0 px page-level horizontal overflow** at both widths; all eight captures were opened and inspected | Sampled Chromium layout; not domain correctness or native iOS/Android engines |
| Public mutation probes | Unsaved edit was saved before role switch and before submit; deactivated-read and failed-adjustment bypass defects reproduced below | Exact tested states only |

The final browser evidence used only the existing worktree-local `.playwright-browsers` directory. The task-owned Vite process lineage was recorded and stopped through its exact exec session; all recorded PIDs and listener 4174 were absent afterward.

A preliminary environment mistake downloaded four Playwright directories to the user cache. The four exact task-created directories were removed after their creation times were bound to this run; readback confirmed each absent and preserved the parent cache directory. None of the verdict evidence above depends on that installation.

## Public action-to-state/audit/effect trace

Passing tests were not treated as proof. Every rendered mutating action was traced through `dispatch` to `executeCommand` and its state, audit, and delivery effects.

| Surface | Public mutations | State / audit / effect trace | Remaining boundary |
|---|---|---|---|
| Employee | Create, save, link receipt/FX evidence, submit, withdraw, delete, create revision | `CREATE_DRAFT`, `UPDATE_DRAFT`, `LINK_ATTACHMENT`, `SUBMIT_CLAIM`, `WITHDRAW_CLAIM`, `DELETE_DRAFT`, `REVISE_CLAIM`; each commit writes one generic audit event. Submit/withdraw create simulated APP+EMAIL Manager delivery; other listed actions do not. Draft deletion now removes claim-owned files. | Scan retries, retention jobs, download grants, review history, and real stale reconciliation remain absent/partial. |
| Manager | Approve, request changes, final reject, revoke approval | Exact revision/version commands; each commit writes one generic audit event and APP+EMAIL Employee delivery. Revocation now returns the same revision to `Submitted`. | Generic audit lacks canonical before/after provenance; related history/download and inactive-account read revocation remain absent. |
| Finance | Schedule, complete, fail, hold, verify/reschedule, create/complete/fail/resolve adjustment | Payment and adjustment commands mutate claim/payment/adjustment state and write one generic audit each. Payment transitions and adjustment completion/failure create APP+EMAIL Employee deliveries; verification, creation, and resolution do not. Owner guards now cover visible adjustment actions. | Failed-adjustment gating is unsafe (`B-CODEX-023`); Finance CSV, hold reopen, scheduled jobs, secure downloads, and full history remain absent. |
| Admin | Issue/reissue/revoke invitation, toggle account, rename/toggle category, set/release hold, retry delivery, generate export metadata | Public commands commit governed records plus one generic audit. Invitation issue/reissue queue two simulated deliveries. Manual retry updates the seeded delivery/warning. Export appends metadata only. | Multiple-role editing, direct-manager assignment, both reassignments, hold reopen, invitation acceptance/expiry, actual CSV bytes/download, and canonical audit provenance remain absent. |

Engine command symbols without public controls do not satisfy the public action contract. `ASSIGN_MANAGER`, `REASSIGN_MANAGER`, and `REASSIGN_FINANCE` exist only behind source-level dispatch; `REOPEN_HOLD` is declared but is neither Admin-routed nor implemented. Finance never renders `ExportPanel`. Search/filter/sort controls are absent from every role list.

## Initial finding disposition

| Initial finding | Disposition | Remaining severity | Fresh basis |
|---|---|---|---|
| `B-CODEX-001` | **RESOLVED** | — | Manager list now includes only non-self assigned `Submitted` and revocable `Payment pending`; Finance list is shared pending plus actor-owned downstream work. Unit/UI/E2E absence assertions pass. Inactive-account read revocation is tracked separately as `B-CODEX-022`. |
| `B-CODEX-002` | **RESOLVED** | — | `REVOKE_APPROVAL` clears approval metadata and returns the same current revision to `Submitted`; UI and tests assert revision identity remains 1. |
| `B-CODEX-003` | **RESOLVED** | — | Public `CREATE_DRAFT` exists. `REVISE_CLAIM` creates an editable Draft revision; editing and subsequent submission are separate actions. |
| `B-CODEX-004` | **RESOLVED** | — | Submission re-reads the employee's latest active direct Manager and writes both current routing and `managerIdSnapshot` before delivery. |
| `B-CODEX-005` | **PARTIAL** | MAJOR | Saving state is now truthful; blur and two-second idle save work, input survives role switching/submission, and unload warning exists. Required 1/2/4/8/16-second retry generations and automatic-stop recovery are not implemented. |
| `B-CODEX-006` | **PARTIAL** | MAJOR | Rejected results are remembered and exact replay works. Stale `changedFields` is fabricated from attempted input keys rather than actual server changes, and the UI discards the list instead of showing latest-versus-browser reconciliation. |
| `B-CODEX-007` | **RESOLVED** | — | Adjustment create/complete/fail/resolve now enforce Finance owner; hold accepts only owner-controlled `Scheduled`. Negative tests cover the corrected guards. |
| `B-CODEX-008` | **RESOLVED** | — | Executed resolution requires positive actual amount, bounded date, and unique reference; completed totals use actual amount. The distinct failed-adjustment gating defect is `B-CODEX-023`. |
| `B-CODEX-009` | **RESOLVED** | — | File records carry SHA-256 and submission blocks a company-retained exact receipt hash with a non-identifying message. |
| `M-CODEX-010` | **PARTIAL** | MAJOR | Real file/camera inputs, byte hashing, 10 MB size, MIME/extension, and independent 10-receipt/5-FX limits now exist. Malware-scan timeout/retry behavior is still copy only and accepted files become `Linked` immediately. |
| `M-CODEX-011` | **PARTIAL** | MAJOR | Zero active categories are now allowed and correctly block submission. Required public multiple-role, direct-manager, Manager/Finance reassignment, category-creation, and hold-reopen controls remain absent. |
| `M-CODEX-012` | **OPEN** | MAJOR | Notification retries, draft expiry/deletion, manager reminders, Admin escalation, overdue processing, and scan retry jobs still do not exist; one seeded warning remains the only retryable example. |
| `M-CODEX-013` | **OPEN** | MAJOR | Audit remains a thin action/time/actor/target/field-name record; related timelines are not mounted for roles; review history and governed download token/request flows remain absent. |
| `M-CODEX-014` | **OPEN** | MAJOR | Search/filter/sort is absent; Finance export is absent; Admin export counts all claims and creates metadata without filtered CSV bytes or a download. |
| `M-CODEX-015` | **OPEN** | MAJOR | Canonical payment-method support and Payment-hold recovery remain incomplete. `REOPEN_HOLD` is unreachable/unsupported and no possible-execution verification controls exist. |
| `M-CODEX-016` | **OPEN** | MAJOR | Invitation acceptance, invited-email activation, time expiry, and atomic acceptance-versus-revocation are still absent. |
| `M-CODEX-017` | **OPEN** | MAJOR | `StateLab` still changes one generic sentence instead of driving each role screen/action into the 16 canonical states. |
| `M-CODEX-018` | **RESOLVED** | — | `DELETE_DRAFT` now deletes every file whose `claimId` matches before removing the claim; the component test verifies the public deletion result, while source inspection verifies the evidence cleanup. Full provenance remains counted under `M-CODEX-013`. |
| `m-CODEX-019` | **OPEN** | MINOR | Dialog still does not move focus inside on open, trap focus, or handle Escape; tests cover only focus restoration after Cancel. |
| `m-CODEX-020` | **PARTIAL** | MINOR | Nine current category records now use the approved English names, but seeded revision snapshots still use `출장 숙박비`. This creates a list/snapshot mismatch after pass 1. |
| `m-CODEX-021` | **OPEN** | MINOR | All four roles remain page-overflow safe at 320, but the Employee page is 3,981 px tall and Admin tabs clip neighboring labels inside an un-signposted horizontal scroller. Mobile E2E remains Employee-only. |

Disposition counts: **8 RESOLVED, 5 PARTIAL, 8 OPEN**.

## Remaining findings

### B-CODEX-022 — BLOCKING — Account deactivation does not revoke visible claim or attachment access

- **Canonical authority:** `RULE-117..120`, `RULE-137..140`, `AC-001` and `AC-002` revision/access expectations. Every request checks latest active status and loss of authority immediately revokes revision, review, and attachment access.
- **Source evidence:** `src/domain/selectors.ts:3-15` scopes by supplied role/relationship but never verifies `state.users[actorId].active` or current role possession. `EmployeeSurface`, `ManagerSurface`, and `FinanceSurface` render those selectors directly. Mutation authorization in `engine.ts:16-19` does check active role, creating a read/write split.
- **Fresh runtime evidence:** after the public Admin control deactivated `usr-employee`, switching to Employee still rendered **7 claims and 1 linked receipt**. Deactivating `usr-manager` still rendered the two Manager queue claims. Mutations are denied later, but governed data is already visible.
- **User effect:** a revoked user retains immediate read access to claim, revision, and attachment metadata, violating the product's current-authority boundary.
- **Test gap:** account tests assert `active: false` and `authVersion: 2` only. No test switches back to the revoked role and asserts empty/permission-denied UI or hidden attachments.
- **Regression check:** initial `4881528` selectors also omitted active/role checks. This is newly discovered, not introduced by pass 1.

### B-CODEX-023 — BLOCKING — Failed adjustment verification can be bypassed by creating another adjustment

- **Canonical authority:** `RULE-148..156`, especially `RULE-153` (append verification before resolving a failed/uncertain adjustment), `RULE-154` (only Not executed permits a linked replacement), and `AC-003` settlement-failure expectation.
- **Source evidence:** `src/domain/engine.ts:204-208` blocks creation only for `In progress` or `Needs verification`; `FAIL_ADJUSTMENT` at `237-246` changes the item to `Failed`, immediately removing that guard. `src/features/finance/AdjustmentPanel.tsx:11,28` uses the same two-status definition and re-enables Create adjustment before the failed item has any verification.
- **Fresh runtime evidence:** the public Finance UI created `adjustment-0001`, failed it, then showed Create adjustment enabled. Starting another committed `adjustment-0006` as `In progress` while the first remained `Failed` with `verification: null`; audit actions were `CREATE_ADJUSTMENT`, `FAIL_ADJUSTMENT`, `CREATE_ADJUSTMENT`.
- **User effect:** Finance can start replacement money movement without establishing whether the failed movement executed, creating a duplicate-payment/recovery risk.
- **Test gap:** tests cover one active `In progress` item and `Needs verification`, but never assert that an unresolved plain `Failed` item blocks creation.
- **Regression check:** the identical two-status guard exists in initial `4881528`; this is newly discovered, not introduced by pass 1.

### M-CODEX-005 — MAJOR — Canonical autosave retry generations remain absent

- **Canonical authority:** `RULE-100..106`, `SCR-001` autosave retry display, and `AC-001` autosave/autosave-retry expectations.
- **Source evidence:** `ClaimEditor.tsx:62-66` schedules one two-second save. A rejection sets `Save failed` at `57-59`; there is no 1/2/4/8/16 retry schedule, attempt counter, stale-generation cancellation, or automatic-stop state.
- **User effect:** a transient simulated save failure receives no canonical automatic recovery sequence; users must manually press Save without attempt guidance.
- **Test gap:** component tests exercise successful save only and do not use fake timers or injected failures.

### M-CODEX-006 — MAJOR — Stale reconciliation is not an actual field diff and is not rendered

- **Canonical authority:** `RULE-133..136` and every `AC-001..004` concurrency expectation.
- **Source evidence:** `engine.ts:629-631` returns `version` plus each attempted input key, not fields changed since the caller's version. `useDomain.ts:21-24` reduces the result to one feedback message; `FeedbackRegion` cannot render `changedFields`, latest values, or preserved browser-versus-server comparison.
- **User effect:** writes remain atomic, but a stale user cannot identify the real conflicting fields or reconcile safely through the public UI.
- **Test gap:** the stale test checks only that `changedFields` contains `version`; it does not construct an actual intervening change or assert public comparison UI.

### M-CODEX-010 — MAJOR — Attachment scan/recovery remains representational copy

- **Canonical authority:** `RULE-047..051`, `RULE-092..095`, `RULE-198..199`, `SCR-001`, `AC-001`.
- **Source evidence:** `AttachmentPanel.tsx:14-24` labels hashing as `Scanning`, then `LINK_ATTACHMENT` immediately commits. `engine.ts:523-530` creates the file directly as `scanStatus: 'Linked'`. There is no timeout, 30-second/two-minute retry record, final scan block, or retry generation.
- **User effect:** timeout and malware-scan recovery cannot occur, although helper copy says the retries are simulated.
- **Test gap:** tests cover valid upload/limits, not timeout, failed-byte discard, retry timing, or submission while unresolved.

### M-CODEX-011 — MAJOR — Required Admin actions remain absent from the public console

- **Canonical authority:** `REQ-004`, `RULE-063..065`, `RULE-157..160`, `RULE-189..196`, `SCR-004`, `AC-004`.
- **Source/runtime evidence:** `AdminSurface.tsx:50-70` exposes account active toggle, category rename/toggle, and legal hold only. Fresh control enumeration found no role editor, direct-manager assignment, Manager/Finance reassignment, category creation, or hold reopen; “Reassignment boundary” remains prose.
- **User effect:** Admin cannot perform canonical access governance and correction flows from the product UI.
- **Test gap:** Admin tests cover invitation, deactivation, legal hold, seeded warning retry, and export metadata only.

### M-CODEX-012 — MAJOR — Scheduled operational behavior remains absent

- **Canonical authority:** `RULE-075..078`, `RULE-083..112`, `RULE-170..174`, `AC-001..004`.
- **Source evidence:** `DomainState` and command inventory contain no job runs, reminder/escalation clocks, retention timestamps, deletion attempts, or overdue processor. `queueDelivery` enqueues attempts `0`; only a seeded permanent-failure record exercises manual retry.
- **User effect:** daily reminders, overdue warnings, delivery retries, draft warnings/deletion, and scheduled recovery never arise from domain state.
- **Test gap:** no clock advancement or job/stop-condition tests exist.

### M-CODEX-013 — MAJOR — Audit, role history, and governed download projections remain incomplete

- **Canonical authority:** `RULE-029..031`, `RULE-137..140`, `RULE-165..169`, `RULE-185..188`, `AC-001..004`.
- **Source evidence:** `AuditEvent` in `types.ts:138-146` has no before/after values or target revision. `Timeline` is mounted only for Admin raw audit; Employee revision history omits review outcomes/comments; Manager/Finance history is badges/current facts only. No token/grant/download command exists.
- **User effect:** required history and evidence access cannot be inspected, reauthorized, or fully audited.
- **Test gap:** tests assert forbidden words are absent from a page; they do not seed hidden fields, verify allowlisted values, or perform token issue/success/denial.

### M-CODEX-014 — MAJOR — Lists and CSV do not implement current-filter governed export

- **Canonical authority:** `RULE-179..184`, `RULE-187`, `RULE-200`, `AC-001..004`.
- **Source evidence:** no role surface renders search/filter/sort. Finance never mounts `ExportPanel`. `engine.ts:465-470` exports `Object.values(state.claims)` and stores only ID/actor/time/row count/columns. There is no CSV payload or download action.
- **User effect:** users cannot narrow operational work; Finance cannot export; Admin's “current-filter CSV” claim produces metadata for all claims.
- **Test gap:** export tests check text and row count only, with no filter, scope-loss, bytes, browser download, or download audit.

### M-CODEX-015 — MAJOR — Payment-hold recovery and full payment-field contract remain incomplete

- **Canonical authority:** `RULE-062..065`, `RULE-072`, `RULE-145..147`, `AC-003`.
- **Source evidence:** `REOPEN_HOLD` is declared in `types.ts:185` but omitted from `ADMIN_COMMANDS` and all transition cases; the hold UI is informational only. There is no external-execution-possible flag or hold verification that gates reopen.
- **User effect:** a held claim cannot return through Admin to Changes requested, new employee revision, and current-manager approval.
- **Test gap:** no Admin reopen, possible-execution verification, or reapproval-chain test exists.

### M-CODEX-016 — MAJOR — Invitation account activation and races remain absent

- **Canonical authority:** `RULE-019..020`, `RULE-121..128`, `RULE-177`, `AC-001..004` invitation expectations.
- **Source evidence:** command/UI inventory supports issue, reissue, and revoke only. No acceptance command proves invited email, activates an account, expires a pending invite over time, or resolves acceptance-versus-revocation atomically.
- **User effect:** the v1 app-native invitation onboarding path is not usable.
- **Test gap:** no acceptance actor, email-match, expiry clock, deactivated-account guard, or concurrent acceptance test.

### M-CODEX-017 — MAJOR — The 16-state lab does not exercise role workflows

- **Canonical authority:** `SCR-001..004`, `screen-spec.md`, Figma state matrix `4:146`, handoff UX state contract.
- **Source evidence:** `StateLab.tsx:3-45` selects a generic sentence only; it does not change role data, controls, preservation, or recovery behavior.
- **User effect:** permission, unauthenticated, offline, timeout, retrying, submitting, partial, and expired role states remain demonstrations rather than usable product states.
- **Test gap:** tests assert option count and one sentence; E2E drives none of the role surfaces through these states.

### m-CODEX-019 — MINOR — Modal keyboard context remains incomplete

- **Canonical authority:** handoff keyboard/focus contract.
- **Source evidence:** `CommandDialog.tsx:14-42` restores trigger focus only after close; it does not focus inside on open, trap focus, or handle Escape.
- **User effect:** modal context is less predictable for keyboard and screen-reader users.
- **Test gap:** E2E verifies only focus restoration after clicking Cancel.

### m-CODEX-020 — MINOR — Corrected category names leave stale seeded revision snapshots

- **Canonical authority:** `RULE-189..191`, `AC-001` category expectation.
- **Source evidence:** `seed.ts:8-11` still sets `categoryNameSnapshot: '출장 숙박비'`, while `seed.ts:110-119` now defines `CAT-002` as `Business lodging` and the other approved English names.
- **Fresh runtime evidence:** Employee category selector showed `Business lodging`; Manager review for the seeded submitted claim showed `출장 숙박비 · CAT-002` with no category rename audit explaining the difference.
- **User effect:** current category and immutable snapshot appear inconsistent in the approved fixture.
- **Test gap:** no seed-integrity test compares current seeded category snapshots to their initial category definitions.
- **Regression check:** pass 1 changed category records but not the snapshot, creating this visible mismatch; severity remains MINOR.

### m-CODEX-021 — MINOR — Mobile navigation remains dense and weakly discoverable

- **Canonical authority:** Figma mobile roots and handoff 320/375 responsive/touch contract.
- **Fresh visual evidence:** all four roles measured 0 px page overflow at 320 and controls remained legible. Employee full-page height was 3,981 px; Admin's tab strip clipped neighboring labels in an internal horizontal scroller without an explicit scroll affordance.
- **User effect:** core content is not page-clipped, but finding off-screen Admin modules and traversing the Employee workflow is unnecessarily difficult.
- **Test gap:** responsive E2E covers Employee only and does not exercise Manager, Finance, or Admin actions at 320/375.

## Visual completion gate

The check sources were fixed before judging the current render: canonical `CODEX_IMPLEMENTATION_HANDOFF.md`, `SCR-001..004`, approved Figma screenshots `figma-scr-001.png` through `figma-scr-004.png`, and `figma-coverage-rev55.png`.

| Check | Expected observable | Concrete fresh observation | Result |
|---|---|---|---|
| `V-B-P1-01` role structure | Four distinct operational role surfaces matching Figma/handoff hierarchy | Four explicit role buttons, role headings, and list/detail or Admin module surfaces rendered at 1440 and 320 | PASS |
| `V-B-P1-02` responsive reflow | Single-column mobile without page-level horizontal overflow | All four roles measured 0 px overflow at 320; desktop and mobile captures showed no overlap or page clipping | PASS for sampled Chromium |
| `V-B-P1-03` canonical action coverage | Required actions in Figma action matrix and SCR-001..004 | Admin role/manager/reassignment/reopen, Finance CSV, search/filter/sort, governed downloads, and several recovery actions remain absent | FAIL |
| `V-B-P1-04` state truth | Real or deterministic role-specific 16 states | Draft Saving/Saved truth improved, but the state lab remains generic and does not drive role workflows | FAIL |
| `V-B-P1-05` keyboard dialog | Focus enters modal, remains contained, Escape/cancel restores trigger | Source still lacks initial focus, trap, and Escape handling; only restoration after Cancel is tested | FAIL |
| `V-B-P1-06` simulation boundary | No claim of real payment/email/auth/provider execution | Header, authority note, reset/export copy consistently identify local deterministic simulation | PASS |

**Overall visual verdict: FAIL.** Required action and state checks fail, so overflow-safe sampled Chromium layout cannot establish visual/product acceptance. Current iOS Safari, Android Chrome, actual camera/file-picker behavior, and user acceptance remain unverified.

## Final counts

| Initial disposition | Count |
|---|---:|
| RESOLVED | **8** |
| PARTIAL | **5** |
| OPEN | **8** |

| Remaining severity, including new findings | Count |
|---|---:|
| BLOCKING | **2** |
| MAJOR | **10** |
| MINOR | **3** |

**Final verdict: FAIL — CODEX_DRIFT_UNRESOLVED. Critical failure exists: yes.**
