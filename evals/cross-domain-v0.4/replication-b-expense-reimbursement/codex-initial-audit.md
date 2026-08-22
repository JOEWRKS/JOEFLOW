# Codex Initial Audit — Replication B Expense Reimbursement

## Overall verdict

**FAIL—CODEX_DRIFT_UNRESOLVED. Critical failure exists: yes.**

The frozen implementation has verified BLOCKING drift in access scope, approval reversal, revision recovery, manager routing, draft durability, concurrency/idempotency, Finance ownership, settlement amount truth, and duplicate-receipt prevention. Passing implementation tests do not cover—and in two places explicitly assert—the contradicted canonical behavior.

## Frozen target and authority

| Item | Frozen value / fresh readback |
|---|---|
| Audit source commit | `4881528083e97a5bbe6a9bc8b8941b343c1a503c` |
| Full source tree | `3bcfe045ee7400303bbd64e77449fddf7cc793e2` |
| `codex-implementation/` subtree | `03bfbea19e466446ac1471de13791bb8fed0820d` |
| Audit branch / inspected HEAD | `eval/v0.4-replication-b-codex` / `365478b5944d74e2c4ad90f228a338395823b73a` |
| Implementation drift from frozen source | `git diff 4881528..HEAD -- codex-implementation` returned no path; the implementation subtree is unchanged |
| Canonical Product Definition | revision `55`, approved digest `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f` |
| Canonical `state.json` SHA-256 | `c0e790c3a8c35f0cdc894110f069ab4d7919aed388f0a4fad2c54e5ae8193395` |
| Implementation handoff SHA-256 | `b2430dfc88db9135a861ea7f7eebc6181a5141f0233b432c670a856cadb927e0` |
| Audited design authority | Figma file `fyow2BHoAXzpkzpozDGWXf`; desktop `1:6`; corrected UX `4:69`; mobile `4:73`, `4:91`, `4:109`, `4:127`; state matrix `4:146`; action matrix `4:195` |

`state.json` revision 55 was treated as primary authority, its projections as clarification, and the audited Figma as downstream structural/visual authority. Implementation-plan/report claims were not used to establish correctness.

## Methods and fresh command results

The audit read the complete allowlisted implementation source and tests, mapped all current `RULE-001..201`, traced each rendered mutation to `executeCommand`, and inspected committed state, audit IDs, delivery IDs, and visible recovery. It then used task-owned Chromium from `codex-implementation/.playwright-browsers` against a task-owned Vite server. The server was stopped after inspection; temporary fresh screenshots were opened, inspected, and deleted.

| Fresh check | Result | Boundary |
|---|---|---|
| `python skills/joewrks-product-definition/scripts/validate_state.py product-definition/expense-reimbursement-dogfood/state.json` | exit `0`; `valid: true`; errors `[]` | Verifies canonical state, not implementation fidelity |
| `python skills/joewrks-product-definition/scripts/validate_closure.py product-definition/expense-reimbursement-dogfood/state.json` | exit `0`; `closed: true`; digest exact; all reported metrics `0` | Verifies canonical closure, not implementation fidelity |
| `npm test -- --run --reporter=dot` | exit `0`; 6 files, `47/47` tests passed | Several canonical paths are absent; tests also encode wrong revocation and zero-category expectations |
| `npm run build` | exit `0`; TypeScript/Vite passed; 39 modules transformed | Buildability only |
| `PLAYWRIGHT_BROWSERS_PATH=<absolute codex-implementation/.playwright-browsers>; npm run test:e2e` | exit `0`; `11/11` Chromium tests passed | Only one happy path per role, Employee-only responsive checks, and no Safari/Android engine |
| Independent browser runtime at `1440×900` and `320×700` | Source/runtime mismatches below reproduced; all four role pages measured `0px` page overflow at 320 | Chromium rendering verified; current iOS Safari and Android Chrome remain unverified |
| Preserved visual captures | Opened and inspected all three attempt-1 PNGs; hashes match the implementation report | Captures show sampled states only and do not establish domain correctness |

Fresh browser facts used below include: Manager queue labels for all eight seeded claims; approval revocation ending in `Changes requested`; revision 3 byte-for-field equal to revision 2 for editable fields; unsaved merchant input disappearing after a role switch while the page continued to say `Saved`; zero file inputs before and after “Choose receipt file”; Admin panels exposing only the controls described below; no browser download from “Generate current-filter CSV”; and modal focus remaining on the background trigger with Escape leaving the dialog open.

## Action-to-domain coverage

Every user-visible mutating action was traced. “Audit” below means the generic single event created by `commit`; it does not imply the event satisfies canonical before/after/revision provenance.

| Surface | Visible mutation | Actual handler and committed state/effects | Coverage assessment |
|---|---|---|---|
| Global | Reset simulated workspace | `resetState()` removes browser state and restores the fixture; no command, audit, or delivery | Explicit simulation control, not a canonical business action |
| Employee | Save draft | `UPDATE_DRAFT`; writes allowed revision fields, increments claim version, one audit, no delivery | Connected, but manual-only and falsely presented as autosave |
| Employee | Capture receipt / Choose receipt file / Add FX evidence | All call `LINK_ATTACHMENT` with canned metadata; create an immediately `Linked` file, increment claim version, one audit, no delivery | Connected to a simulation, not to a file/camera input or canonical scan/limit behavior |
| Employee | Submit claim | `SUBMIT_CLAIM`; basic guards, category-name snapshot, `Submitted`, timestamp, one audit, two Manager deliveries | Partial; wrong manager-binding and duplicate/file/FX guards |
| Employee | Withdraw claim | `WITHDRAW_CLAIM`; public UI exposes it for `Submitted`; commits terminal `Withdrawn`, one audit, two Manager deliveries | UI boundary is correct; engine additionally permits `Changes requested` |
| Employee | Delete draft | `DELETE_DRAFT`; removes the claim, leaves linked file records, then creates one generic audit; no delivery | Connected but destructive persistence is incomplete |
| Employee | Create and submit revision N | `REVISE_CLAIM`; clones the prior revision unchanged, timestamps it, and immediately sets `Submitted`; one audit, two deliveries | Canonically wrong; no editable revision step |
| Manager | Approve revision N | `APPROVE_CLAIM`; `Payment pending`, approval revision/time, one audit, two Employee deliveries | Connected and revision/version guarded for this transition |
| Manager | Request changes | `REQUEST_CHANGES`; `Changes requested`, stores one comment on the revision, one audit, two deliveries | Connected; review history/projection remains incomplete |
| Manager | Final reject | `FINAL_REJECT_CLAIM`; `Final rejected` and time, reason only in generic audit, two deliveries | Connected; durable review comment/history is incomplete |
| Manager | Revoke approval | `REVOKE_APPROVAL`; commits `Changes requested`, deletes approval fields, one audit, two deliveries | BLOCKING canonical reversal error |
| Finance | Claim and schedule payment | `SCHEDULE_PAYMENT`; owner/date/`Scheduled`, one audit, two Employee deliveries | Connected and guarded for the seeded owner path |
| Finance | Record payment completed | `COMPLETE_PAYMENT`; date/method/reference/`Payment completed`, one audit, two deliveries | Partial; `Cash` is impossible |
| Finance | Record payment failed | `FAIL_PAYMENT`; reason/`Payment failed`, clears verification, one audit, two deliveries | Connected for seeded owner |
| Finance | Place payment on hold | `HOLD_PAYMENT`; owner/reason/`Payment hold`, one audit, two deliveries | Public UI shows it for Scheduled, but the handler also commits from forbidden pending/failed states |
| Finance | Verify execution / Reschedule verified payment | `VERIFY_FAILED_PAYMENT` then `RESCHEDULE_PAYMENT`; structured record then `Scheduled`, one audit per command; reschedule sends two deliveries | Partial; evidence and repeat/recovery semantics are absent |
| Finance | Start adjustment | `CREATE_ADJUSTMENT`; creates `In progress`, links ID, one audit, no delivery | Connected but owner relationship is not checked |
| Finance | Complete adjustment | `COMPLETE_ADJUSTMENT`; marks completed with date/reference, one audit, two deliveries | Connected but owner relationship is not checked |
| Finance | Record adjustment failed | `FAIL_ADJUSTMENT`; marks failed and concatenates reason, one audit, two deliveries | Connected but owner relationship is not checked |
| Finance | Resolve adjustment uncertainty | `RESOLVE_ADJUSTMENT`; Unclear→Needs verification, Executed→Completed, Not executed→Cancelled plus automatic replacement; one audit, no delivery | Money and recovery semantics are wrong/partial |
| Admin | Issue / reissue / revoke invitation | `ISSUE_INVITATION`, `REISSUE_INVITATION`, `REVOKE_INVITATION`; invitation records plus generic audit; issue/reissue queue two deliveries | Partial; acceptance and actual expiry transition do not exist |
| Admin | Activate / deactivate account | `UPDATE_ACCOUNT`; active/roles/auth version, generic audit, no delivery | Only active toggle is exposed; multi-role editing is not |
| Admin | Rename / activate / deactivate category | `UPDATE_CATEGORY`; category values/version and generic audit | Rename/toggle connected; create is absent and last active category is wrongly protected |
| Admin | Set / release legal hold | `SET_LEGAL_HOLD`, `RELEASE_LEGAL_HOLD`; claim hold value, generic audit | Connected at claim pointer only; governed deletion lifecycle is absent |
| Admin | Retry delivery once | `RETRY_DELIVERY`; queues the seeded permanent failure and resolves its warning, generic audit | Connected only to a pre-seeded warning; automatic retry lifecycle is absent |
| Admin | Generate current-filter CSV | `EXPORT_CSV`; appends export metadata for every claim and generic audit; no CSV bytes/download | Label and handler outcome overstate what happened |

Canonical actions absent from the public UI include creating a fresh draft, editing a changes-requested revision before resubmission, real attachment selection/download, Finance export, invitation acceptance, multiple-role assignment, direct-manager assignment, category creation, Manager/Finance reassignment, and Admin reopening a Payment hold. Search/filter/sort is absent on every list.

## Findings

### B-CODEX-001 — BLOCKING — Manager scope exposes drafts, decided claims, and Finance history

- **Canonical authority:** `RULE-016`, `RULE-118`, `RULE-138..140`; `AC-002` list/revision visibility and `AC-003` processing-scope expectations.
- **Source evidence:** `src/domain/selectors.ts:3-8` filters Manager claims only by `claim.managerId`; `src/features/manager/ManagerSurface.tsx:10-20` renders that full result without a submitted/latest-processing-state guard.
- **Fresh runtime evidence:** the Manager “Assigned queue” contained `clm-draft`, `clm-changes`, `clm-approved`, `clm-scheduled`, `clm-failed`, and `clm-completed` in addition to submitted work. The 1440 render visibly showed Draft through Payment completed in the Manager rail.
- **User effect:** a Manager can read employee draft data and payment/terminal history outside current review authority. This is a current public access-control failure.
- **Test gap:** Manager tests intentionally select the out-of-scope self-review fixture but never assert that Draft, decided, or Finance-state claims are absent.
- **Verification:** source + live runtime verified.

### B-CODEX-002 — BLOCKING — Approval revocation implements the superseded outcome

- **Canonical authority:** `DEC-022`, `RULE-061`, `AC-001` and `AC-002` approval-revocation expectations: the same revision must return to `Submitted`; no new revision is created.
- **Source evidence:** `src/domain/engine.ts:528-535` sets `Changes requested`, deletes approval fields, and says a new revision is required; `ReviewPanel.tsx:9-13` labels the confirmation “Revoke and request revision.”
- **Fresh runtime evidence:** revoking `clm-approved` produced `status: Changes requested`, revision `1`, and Employee action “Create and submit revision 2.”
- **User effect:** the implementation changes approval truth and forces an unauthorized revision cycle instead of reopening the approved revision for review.
- **Test gap:** `engine.test.ts:140-176` explicitly expects `Changes requested`; `ManagerSurface.test.tsx:57-65` checks only the success message, thereby locking in drift rather than detecting it.
- **Verification:** source + live runtime verified.

### B-CODEX-003 — BLOCKING — Employee cannot create or correctly revise a claim

- **Canonical authority:** `REQ-001`, `RULE-005`, `RULE-057`, `RULE-129..132`, `AC-001`; SCR-001 actions “청구 작성,” “수정 요청 청구 개정,” and “개정 청구 재제출.”
- **Source evidence:** `DomainCommandType` (`src/domain/types.ts:164-197`) has no create-draft command; the empty state in `EmployeeSurface.tsx:22` has no action. `ClaimEditor.tsx:41-47` makes Changes requested read-only. `engine.ts:555-561` clones the prior revision, sets `submittedAt` immediately, and returns to `Submitted`; the only UI action is the combined button at `EmployeeSurface.tsx:53`.
- **Fresh runtime evidence:** revision 3 of `clm-changes` had identical merchant, category, date, currency, amounts, purpose, duplicate/late reasons, receipt IDs, and FX evidence IDs to revision 2, then immediately became `Submitted`.
- **User effect:** a new employee cannot start without the fixture, and an employee cannot address a Manager’s requested change. This makes a core recovery path unusable.
- **Test gap:** the Employee and engine tests assert only the revision number/status after copying unchanged data.
- **Verification:** source + live runtime verified.

### B-CODEX-004 — BLOCKING — Submission/resubmission does not bind the current direct manager

- **Canonical authority:** `RULE-001`, `RULE-023..025`, `AC-001`, `AC-002`: current direct manager is snapshotted at submission; normal manager change affects future claims and the next resubmitted revision.
- **Source evidence:** `ASSIGN_MANAGER` changes only `user.managerId` (`engine.ts:381-389`). `SUBMIT_CLAIM` keeps the draft’s pre-existing `claim.managerId` (`engine.ts:542-545`), and `REVISE_CLAIM` also sends to the existing claim manager (`engine.ts:555-561`). No code copies the employee’s latest manager into the submitted revision.
- **User effect:** after an Admin manager change, a future submission or resubmission can be routed to the old Manager, committing wrong approval authority.
- **Test gap:** no test changes a user’s manager and then submits/resubmits; the public Admin UI does not expose manager assignment, so this handler defect is not runtime-reachable through the current UI.
- **Verification:** deterministic source path verified; public-runtime exercise unavailable because the required Admin control is missing.

### B-CODEX-005 — BLOCKING — Unsaved draft input is labeled Saved and is silently lost

- **Canonical authority:** `RULE-100..108`, `AC-001` autosave/retry expectations: 2-second/blur saves, latest generation, visible Saving/Saved/Failed truth, input preservation, and navigation warning.
- **Source evidence:** `ClaimEditor.tsx:54` always renders “Saved · generation {claim.version}”; the only persistence trigger is the manual button at `ClaimEditor.tsx:35-39,71`. There is no debounce, blur save, retry state, generation guard, or navigation blocker.
- **Fresh runtime evidence:** after changing Merchant to “Unsaved merchant value,” UI still read “Saved · generation 1”; switching to Manager and back raised zero dialogs and restored “Seoul Business Hotel.”
- **User effect:** the UI falsely assures durability and loses governed draft input on ordinary in-app navigation.
- **Test gap:** Employee tests click Save explicitly and never edit-then-navigate, wait for debounce, induce failure, or verify retry generations.
- **Verification:** source + live runtime verified.

### B-CODEX-006 — BLOCKING — Rejected idempotency and stale-conflict semantics are not implemented

- **Canonical authority:** `RULE-133..136`, `AC-001..004` concurrency expectations: committed **or rejected** exact replays return the original result; stale no-op returns latest state and changed fields while preserving input.
- **Source evidence:** `rejected()` always returns `changedFields: []` (`engine.ts:21-28`); stale rejection at `engine.ts:596-603` does not calculate a diff. Idempotency records are written only inside `outcome.status === 'committed'` branches (`engine.ts:585-614`), so rejected keys are not remembered.
- **User effect:** a retry with the same key can be re-evaluated and later commit after conditions change, including money/access/approval commands; stale users receive no field-diff reconciliation despite the UI contract.
- **Test gap:** `engine.test.ts:56-75` tests only committed replay; its stale test checks input preservation but never `changedFields` or rejected replay. No UI renders latest-vs-browser comparison.
- **Verification:** deterministic source path verified; no inference from tests.

### B-CODEX-007 — BLOCKING — Finance relationship guards permit unauthorized money mutations and invalid hold transitions

- **Canonical authority:** `RULE-062`, `RULE-080..082`, `RULE-118`, `AC-003` Finance owner/payment-hold expectations; handoff rule that role possession alone is insufficient.
- **Source evidence:** Finance authorization checks only active `FINANCE` role (`engine.ts:90-92`). `paymentOwnerDenied` exists (`engine.ts:108-112`) but is not applied to `CREATE_ADJUSTMENT`, `COMPLETE_ADJUSTMENT`, `FAIL_ADJUSTMENT`, or `RESOLVE_ADJUSTMENT` (`engine.ts:204-274`). `HOLD_PAYMENT` accepts `Payment pending`, `Scheduled`, and `Payment failed` and self-assigns an owner (`engine.ts:166-174`) although the canonical correction path starts from Scheduled.
- **User effect:** a non-owner Finance user can create/complete/fail/resolve monetary adjustments, and a direct command can bypass scheduling/failure recovery to put an item on hold.
- **Test gap:** ownership tests cover only `COMPLETE_PAYMENT`; no adjustment-owner or pending/failed-hold negative test exists.
- **Verification:** deterministic source path verified; current UI uses the seeded owner for visible adjustment actions, so the cross-Finance case was not exposed by the fixture.

### B-CODEX-008 — BLOCKING — Executed adjustment resolution can commit the wrong settled amount

- **Canonical authority:** `RULE-150`, `RULE-152..156`, `AC-003`: Executed resolution requires actual amount, completion date, and unique reference; totals use completed actual outcomes.
- **Source evidence:** `Adjustment` has no actual-amount field (`types.ts:80-97`). The Executed branch accepts only date/reference and marks the existing requested amount Completed (`engine.ts:253-261`); it does not bound the date there. `adjustmentTotals` sums `amountKrw` (`selectors.ts:10-15`). The UI offers no actual-amount control (`AdjustmentPanel.tsx:50-54`).
- **User effect:** a failed adjustment executed for a different amount can become Completed and change net settled money by the originally requested amount; an invalid date can also be recorded.
- **Test gap:** tests cover only the Unclear branch and ordinary in-progress completion, never Executed resolution or actual-amount variance.
- **Verification:** deterministic source/UI path verified.

### B-CODEX-009 — BLOCKING — Exact receipt-hash duplicate blocking is absent

- **Canonical authority:** `RULE-043..046`, `AC-001`: an identical receipt hash across active/retained company claims blocks submission without leaking unauthorized claim identity.
- **Source evidence:** `FileRecord` has no hash (`types.ts:47-56`); `LINK_ATTACHMENT` records no hash (`engine.ts:488-508`). `validateSubmission` performs only the same-employee date/merchant/amount/currency warning (`engine.ts:308-313`) and has no company-wide exact-file check.
- **User effect:** the domain can commit a second reimbursement claim using the same receipt, bypassing the money-protection rule.
- **Test gap:** no file-hash field, exact-duplicate fixture, privacy assertion, or submit-negative test exists.
- **Verification:** absence verified across the complete implementation source; public multi-claim creation is itself missing.

### M-CODEX-010 — MAJOR — Attachment actions synthesize files and violate size/count/scan recovery rules

- **Canonical authority:** `RULE-047..051`, `RULE-092..095`, `RULE-198..199`, `AC-001` mobile/draft recovery expectations.
- **Source evidence:** `AttachmentPanel.tsx:9-16` sends canned filename/MIME/size; there is no `<input type="file">`. `engine.ts:495-508` allows 100 MB, checks a combined 10-file limit instead of receipt 10/FX 5, does not compare extension to actual MIME, and immediately sets `Linked`. The helper repeats simulated retry text without a retry state machine.
- **Fresh runtime evidence:** file-input count was `0` before and after “Choose receipt file”; clicking it appended canned `receipt.pdf` immediately.
- **User effect:** users cannot actually choose/capture evidence, invalid 10–100 MB files are accepted by the handler, and scan timeout/failure recovery is unreachable.
- **Test gap:** tests assert only that the canned file becomes Linked and that recovery copy exists.
- **Verification:** source + live runtime verified.

### M-CODEX-011 — MAJOR — Admin control plane omits required mutations and reverses zero-category policy

- **Canonical authority:** `REQ-004`, `RULE-053`, `RULE-063..065`, `RULE-157..160`, `RULE-189..196`, `AC-004` admin-scope/category expectations.
- **Source evidence:** `AdminSurface.tsx:50-70` exposes only active toggle, category rename/toggle, and legal hold. It has no role editor, direct-manager assignment, category creation, Manager/Finance reassignment, or Payment-hold reopen control; its reassignment section is copy only. `UPDATE_CATEGORY` rejects deactivation of the last active category (`engine.ts:391-401`), while canonical policy permits zero active and blocks submission. UI copy at `AdminSurface.tsx:61` states the wrong policy.
- **Fresh runtime evidence:** Accounts & roles had one user selector and only “Deactivate account”; Holds & reassignment had one claim selector and only “Set legal hold.”
- **User effect:** Admin cannot perform material governance/recovery actions, and cannot intentionally reach the canonical zero-active-category state.
- **Test gap:** category test explicitly expects `LAST_ACTIVE_CATEGORY`; no public-control tests cover the absent commands.
- **Verification:** source + live runtime verified.

### M-CODEX-012 — MAJOR — Time-driven notification, retention, escalation, and recovery behavior is copy/fixture only

- **Canonical authority:** `RULE-075..078`, `RULE-083..112`, `RULE-170..174`, `AC-001..004` notification, overdue, approval-delay, draft retention/deletion expectations.
- **Source evidence:** the complete domain state/command inventory has no clock jobs, draft retention timestamps, autosave attempts/generations, deletion runs, reminder/escalation records, or overdue processor. `seed.ts:106-110` supplies one pre-made permanent-failure warning; `queueDelivery` (`engine.ts:37-48`) only enqueues attempts `0` and has no 1/10/60-minute processor.
- **User effect:** permanent failures, daily reminders, overdue markers, 83/90-day draft behavior, scan retries, and deletion recovery cannot arise from real state transitions.
- **Test gap:** the only warning test retries the seeded event; no test advances time or verifies schedules/stop conditions.
- **Verification:** absence verified across the complete source and command inventory.

### M-CODEX-013 — MAJOR — Audit, related timelines, and governed downloads are not implemented to the canonical projection

- **Canonical authority:** `RULE-029..031`, `RULE-137..140`, `RULE-165..169`, `RULE-185..188`, `AC-001..004` masking/download/audit expectations.
- **Source evidence:** `AuditEvent` stores only action/time/actor/target/changed-field names/reason (`types.ts:135-143`), not before/after values or target revision. Admin raw audit renders the same thin record (`Timeline.tsx:20-24`). Related `Timeline` is not mounted by Employee, Manager, or Finance; Employee history (`RevisionTimeline.tsx:9-13`) shows only revision number, merchant, amount, and time, with no reviews. There is no download command/token/grant or download UI in `DomainCommandType` or the feature surfaces.
- **User effect:** users cannot inspect required business history or reauthorized evidence; Admin cannot inspect full provenance; access-loss/download auditing cannot be exercised.
- **Test gap:** the “allowlist” test merely asserts forbidden words are absent from current page text and never seeds hidden fields or mounts a related-user timeline/download.
- **Verification:** source/runtime surface verified.

### M-CODEX-014 — MAJOR — Lists and CSV are missing or materially disconnected

- **Canonical authority:** `RULE-179..184`, `RULE-187`, `AC-001..004` list/export expectations.
- **Source evidence:** role lists only map fixed arrays; no search/filter/sort inputs exist. Finance does not render `ExportPanel`. `EXPORT_CSV` uses `Object.values(state.claims)` without role scope or filter (`engine.ts:450-455`) and appends only metadata. `ExportPanel.tsx:12-16` reports “CSV export” but has no bytes or download action.
- **Fresh runtime evidence:** Admin export reported 8 rows (every seeded claim), started no browser download, and persisted only ID/actor/time/row count/columns. The Manager queue scope defect is separately BLOCKING above.
- **User effect:** current-filter export cannot be produced, Finance export is unavailable, and the hidden Finance-capable handler would include out-of-scope claims.
- **Test gap:** tests check only that “Export generated” text appears and forbidden words are absent.
- **Verification:** source + live runtime verified.

### M-CODEX-015 — MAJOR — Payment method and Payment-hold recovery are incomplete

- **Canonical authority:** `RULE-062..065`, `RULE-072`, `RULE-145..147`, `AC-003` payment-field/hold expectations.
- **Source evidence:** `PaymentRecord`, completion validation, and UI options omit canonical `Cash` (`types.ts:58-77`, `engine.ts:143-151`, `PaymentPanel.tsx:40-45`). `REOPEN_HOLD` exists in the type union but is in neither Admin command routing nor a transition implementation; the Payment-hold UI is only a message (`PaymentPanel.tsx:77`). There is no `external_execution_possible` or required hold verification record.
- **User effect:** a valid Cash payment cannot complete, and a held claim cannot recover through Admin to Changes requested/new revision/current-manager approval.
- **Test gap:** tests use only Bank transfer/Other and do not attempt Admin reopen or possible-execution verification.
- **Verification:** source/UI path verified.

### M-CODEX-016 — MAJOR — Invitation activation/expiry and acceptance-vs-revocation race do not exist

- **Canonical authority:** `RULE-019..020`, `RULE-121..128`, `RULE-177`, `AC-001..004` invitation expectations.
- **Source evidence:** command types and Admin UI provide issue/reissue/revoke only. `Invitation.status` includes Accepted/Expired, but no acceptance command activates the invited email and no time transition expires a Pending invite. The tested “race” is reissue followed by stale revoke, not acceptance racing revocation.
- **User effect:** the canonical native-account onboarding path is unusable; expiry and first-atomic-commit acceptance semantics cannot be observed.
- **Test gap:** no acceptance actor, invited-email proof, active/deactivated-account guard, or concurrent acceptance test.
- **Verification:** absence verified across complete source/tests.

### M-CODEX-017 — MAJOR — The 16-state contract is a generic demo rather than per-screen state behavior

- **Canonical authority:** SCR-001..004 UX coverage and `screen-spec.md`; handoff responsive/accessibility contract requires default, loading, empty, partial, success, error, disabled, permission denied, unauthenticated, offline, timeout, retrying, submitting, completed, cancelled, and expired presentations through real state or deterministic scenario controls.
- **Source evidence:** `StateLab.tsx:3-45` changes one generic sentence and does not put any role screen/action into the selected state. Role mutations are synchronous; there are no loading/submitting/timeout/offline/permission/session-expiry adapters.
- **User effect:** role-specific recovery and preserved-input behavior cannot be inspected or used despite a visible “16-state” claim.
- **Test gap:** `App.test.tsx:28-37` checks option count and one sentence only; E2E never drives a role surface into any of these states.
- **Verification:** source + live UI verified.

### M-CODEX-018 — MAJOR — Draft deletion leaves governed evidence orphaned and cannot prove the promised deletion

- **Canonical authority:** `RULE-057`, `RULE-091..112`, `RULE-029`, and the handoff’s governed file/audit/retention contract.
- **Source evidence:** `DELETE_DRAFT` deletes only `state.claims[claim.id]` (`engine.ts:551-554`); `state.files` entries remain. The UI says deletion removes the draft “and its task-owned simulated evidence” (`EmployeeSurface.tsx:56-58`). The resulting audit has no before values/revision/file IDs.
- **User effect:** claim-to-file ownership is destroyed while file records remain inaccessible/orphaned, contradicting the destructive confirmation and governed retention story.
- **Test gap:** deletion test checks only that the claim button disappears; it does not assert file cleanup, audit provenance, or recoverability.
- **Verification:** deterministic source path verified.

### m-CODEX-019 — MINOR — Modal keyboard behavior is incomplete

- **Canonical authority:** handoff accessibility contract for keyboard dialogs, visible focus, and focus restoration.
- **Source evidence:** `CommandDialog.tsx:14-42` restores focus only after close; it does not focus inside on open, trap focus, or handle Escape.
- **Fresh runtime evidence:** opening Delete left focus on the background “Delete draft” trigger; Escape left one dialog open; the next Tab reached Cancel. Focus restoration after clicking Cancel did work.
- **User effect:** keyboard/screen-reader modal context is less predictable, though controls remain operable.
- **Test gap:** E2E tests cancellation focus restoration only.
- **Verification:** source + live runtime verified.

### m-CODEX-020 — MINOR — Seed category names drift from the approved nine-category seed

- **Canonical authority:** `RULE-189`, `AC-001` category expectation.
- **Source evidence:** `seed.ts:93-102` uses Korean/localized names such as `교통비` and `출장 숙박비` instead of the approved initial names `Transportation`, `Business lodging`, `Meals`, and so on. Stable IDs remain correct.
- **User effect:** initial user-visible category snapshots differ from revision 55, although Admin rename is canonical and IDs are preserved.
- **Test gap:** tests assert the localized snapshot rather than the canonical seed names.
- **Verification:** source and preserved/live render verified.

### m-CODEX-021 — MINOR — Mobile navigation is overflow-safe but dense and weakly discoverable

- **Canonical authority:** audited Figma mobile roots and handoff single-column/touch-target contract.
- **Fresh observation:** all four role pages had `0px` page overflow at 320 and controls retained 44px minimum height. The Employee page was 3,914px tall; Admin tabs use an internal horizontal scroller and the 320 render visibly clipped neighboring tab labels with no explicit scroll affordance.
- **User effect:** no core content was clipped at page level, but reaching off-screen Admin modules is less discoverable and the task flow is unusually long.
- **Test gap:** E2E checks page overflow only for Employee and never exercises Manager/Finance/Admin actions at 320/375.
- **Verification:** live Chromium + preserved capture inspection; iOS Safari/Android Chrome unverified.

## Visual and runtime observations

The preserved captures were verified at these exact hashes:

- Employee 1440: `fcab98cdc87fa7d2fe09a82ea8d2f52dbb557269f98652a8efd320f598b7b73c`
- Admin 1440: `283f9c0553f642cadea54412efdadcdc5fe373b9e6d55f919747852b277bc9de`
- Employee 320: `c687f78c3dc353269da94bf7ea1fa8e46552209f7bbaf16583783cf08a88a145`

| Visual/runtime check | Expected observable and authority | Concrete fresh observation | Result |
|---|---|---|---|
| V-B-01 Role hierarchy | Four distinct role surfaces; Figma `1:6`/`4:69` and handoff | Four explicit role buttons, neutral operational cards, role-specific headings and list/detail workspaces | PASS |
| V-B-02 Desktop/mobile reflow | 1440 operational layout; 320/375 single column without page overflow | Preserved captures had legible cards/no overlap; fresh 320 measurements were 0px overflow for Employee, Manager, Finance, Admin | PASS for sampled Chromium layout |
| V-B-03 Canonical action visibility | Audited role matrices `4:195`, REQ-001..004 | Revision editing, real upload/download, Admin roles/manager/reassignment/reopen, Finance export, and several recovery actions are absent; Manager visibly lists out-of-scope states | FAIL |
| V-B-04 State feedback truth | State matrix `4:146`, RULE-100..108 | Draft says Saved while unsaved input is present and later lost; the generic lab does not change role screens | FAIL |
| V-B-05 Keyboard dialog | Handoff accessibility contract | Trigger retains focus on open; Escape does not close; no trap | FAIL |
| V-B-06 Simulation boundary | Implementation handoff evaluation boundary | Header/authority note and reset/export copy identify a local deterministic simulation; no real payment/email/auth/encryption/database/provider capability is claimed | PASS |

Visual layout is therefore verified only for sampled Chromium rendering. It cannot upgrade the implementation verdict because required controls and visible state truth fail. Native current iOS Safari/Android Chrome behavior, actual camera/file picker behavior, and user acceptance are **UNVERIFIED**.

## Counts and disposition

| Severity | Count |
|---|---:|
| BLOCKING | **9** |
| MAJOR | **9** |
| MINOR | **3** |

Critical failure exists because current public UI exposes governed claim data to a Manager outside processing scope and commits the wrong approval-revocation truth, while core Employee recovery loses/ignores edits. Source-verified Finance and settlement handlers can additionally commit unauthorized or incorrect money state.

**Final verdict: FAIL—CODEX_DRIFT_UNRESOLVED.**
