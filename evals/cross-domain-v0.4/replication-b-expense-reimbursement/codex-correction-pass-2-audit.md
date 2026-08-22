# Codex Correction Pass 2 Blind Audit — Replication B Expense Reimbursement

## Overall verdict

**FAIL — CODEX_DRIFT_UNRESOLVED. Critical failure exists: yes.**

Pass 2 resolves the two BLOCKING findings from the previous audit, but fresh public-action testing found three new BLOCKING regressions: related-user timeline authorization/masking fails after Finance authority loss, a generated Finance CSV remains downloadable after its row scope is lost, and the daily retention action deletes a legally held draft and its evidence. The passing 71-test suite does not exercise any of those action sequences.

Final material drift:

| Severity | Count |
|---|---:|
| BLOCKING | **3** |
| MAJOR | **8** |
| MINOR | **1** |

## Frozen target and authority

| Item | Frozen value / fresh readback |
|---|---|
| Corrected source commit | `24a139ff6d97b62a7512150e86f3ec9bf6a5a368` |
| Corrected `codex-implementation/` subtree | `9a788f6269160d6a76b715a50b98a390a8663e33` |
| Evidence HEAD inspected | `8eeef3ca7ffea402087009f020b516b02e9a65c8` |
| Branch | `eval/v0.4-replication-b-codex` |
| Canonical Product Definition | revision `55`; approved digest `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f` |
| Canonical `state.json` SHA-256 | `c0e790c3a8c35f0cdc894110f069ab4d7919aed388f0a4fad2c54e5ae8193395` |
| Audited design authority | Figma file `fyow2BHoAXzpkzpozDGWXf`; desktop `1:6`; corrected coverage `4:69`; mobile `4:73`, `4:91`, `4:109`, `4:127`; state matrix `4:146`; action matrix `4:195` |

Only the canonical revision-55 Product Definition, its implementation handoff, and the named B Figma evidence were used as authority. The implementation and tests were read-only during this audit.

## Fresh verification

| Check | Fresh result | Boundary |
|---|---|---|
| State validator | PASS, exit `0`, `valid: true`, errors `[]` | Canonical state validity only |
| Closure validator | PASS, exit `0`, `closed: true`, digest exact, all metrics `0` | Canonical closure only |
| `npm test -- --run --reporter=dot` | PASS, 7 files, `71/71` tests | Does not cover the three BLOCKING sequences below |
| `npm run build` | PASS, 40 modules transformed | Buildability only |
| Worktree-local Chromium E2E | PASS, `11/11`; explicit `PLAYWRIGHT_BROWSERS_PATH` used | Desktop Chromium and Employee-only responsive assertions; no iOS Safari/Android engine |
| E2E process cleanup | No new Node PID after suite; port `4173` absent | Confirms suite server cleanup |
| Independent public-action run | Reproduced both prior BLOCKING fixes and all three new BLOCKING findings | Task-owned Vite server PID `34332`, port `4186` |
| Independent server cleanup | Exact exec session stopped; PID `34332` absent; port `4186` absent | No process or listener remained |
| Temporary evidence cleanup | Exact task-owned temp directory absent after inspected PNG/CSV deletion | No temporary screenshot or export artifact remained |

The first validator invocation was accidentally issued from `codex-implementation/` and returned an exact path-not-found error. It was retried once from the repository root with the corrected path and passed as recorded above.

## Public mutation-to-domain audit

Presentation-only role switching and 16-state selection do not mutate domain state. The workspace reset is an explicitly labeled simulation control. Every public business mutation is listed below.

| Surface | Public mutation | Handler and actual state/effect | Audit result |
|---|---|---|---|
| Global | Reset simulated workspace | `resetState()` removes local fixture state and recreates revision 55; no business audit/delivery | Correctly labeled non-canonical simulation control |
| Employee | Create new claim | `CREATE_DRAFT` creates an owned blank Draft and generic audit | Connected; special register transition does not independently validate a register version |
| Employee | Save draft / blur / two-second autosave | `UPDATE_DRAFT` writes editable fields and claim version; UI has bounded retry generations | Connected; stale comparison remains incomplete under `M-CODEX-006` |
| Employee | Capture receipt | File input hashes bytes, then `LINK_ATTACHMENT` links or records timeout/discard | Connected; automatic scan timing and governed download remain incomplete |
| Employee | Choose receipt file | Same command with `source=file` | Same limitation |
| Employee | Add FX evidence | Same command with `purpose=FX_EVIDENCE` | Connected; evidence subtype and six-decimal validation are absent |
| Employee | Retry scan | `RETRY_ATTACHMENT_SCAN` mutates scan attempt/link/discard state | Public control is immediately enabled and ignores its future retry time |
| Employee | Submit claim / submit revision | `SUBMIT_CLAIM` validates fields, receipt hash, manager, category, date, basic FX, then snapshots manager/category and queues Manager delivery | Connected; FX evidence/precision and review-evidence gaps remain |
| Employee | Withdraw claim | `WITHDRAW_CLAIM` commits terminal Withdrawn and Manager delivery | Connected |
| Employee | Delete draft | Confirmed `DELETE_DRAFT` removes claim and all claim file records, then audits deletion | Connected |
| Employee | Create next revision | `REVISE_CLAIM` clones history into a separate editable Draft revision | Connected |
| Manager | Approve exact revision | `APPROVE_CLAIM` creates Payment pending, approval metadata, audit, and Employee delivery | State connected; shared-Finance notification missing |
| Manager | Request changes | Required dialog comment; `REQUEST_CHANGES` commits status/comment/audit and Employee delivery | Connected |
| Manager | Final reject | Required dialog reason; `FINAL_REJECT_CLAIM` commits terminal state/audit and Employee delivery | Connected |
| Manager | Revoke approval | Required reason; `REVOKE_APPROVAL` returns the same revision to Submitted | Connected; prior superseded behavior is fixed |
| Finance | Claim and schedule payment | `SCHEDULE_PAYMENT` atomically assigns acting owner/date and queues Employee delivery | Connected |
| Finance | Record payment completed | `COMPLETE_PAYMENT` checks owner, date, method/detail, unique reference and commits immutable completed state | Connected |
| Finance | Record payment failed | `FAIL_PAYMENT` checks owner/reason and commits failure | Connected |
| Finance | Place payment on hold | `HOLD_PAYMENT` is limited to owned Scheduled and records execution-possible flag/reason | Connected |
| Finance | Verify failed payment | `VERIFY_FAILED_PAYMENT` stores structured verification | Connected |
| Finance | Reschedule verified payment | `RESCHEDULE_PAYMENT` requires `Not paid` | Connected |
| Finance | Verify held payment | `VERIFY_HELD_PAYMENT` stores structured held-payment verification | Connected |
| Finance | Create adjustment | `CREATE_ADJUSTMENT` enforces owner and no unresolved active/failed adjustment | Connected; prior bypass is fixed |
| Finance | Complete adjustment | `COMPLETE_ADJUSTMENT` checks owner/date/reference and commits actual outcome | Connected; audit captures the claim wrapper rather than changed adjustment values |
| Finance | Record adjustment failed | `FAIL_ADJUSTMENT` leaves unresolved Failed active for creation gating | Connected; prior bypass is fixed |
| Finance | Resolve adjustment uncertainty | `RESOLVE_ADJUSTMENT` handles Unclear, Executed actuals, or Not-executed replacement | State connected; Employee result delivery and child-object audit provenance are incomplete |
| Finance | Generate current-filter CSV | `EXPORT_CSV` scopes requested IDs to current Finance authority and stores actual allowlisted CSV bytes | Generation connected |
| Finance | Download authorized CSV | `DOWNLOAD_EXPORT` checks current role and export ownership only | **BLOCKING:** does not revalidate row scope at download |
| Admin | Issue invitation | `ISSUE_INVITATION` creates seven-day Pending invitation and delivery | Connected |
| Invite fixture | Activate invited account | `ACCEPT_INVITATION` checks exact email, current pending version and expiry, then activates roles | Connected; atomic losing race is tested |
| Admin | Reissue invitation | Invalidates Pending prior link and creates a new Pending link | State connected; old-link before/after provenance is not in its own target audit |
| Admin | Revoke invitation | Required reason; current Pending version becomes Revoked | Connected |
| Admin | Run invitation expiry check | `EXPIRE_INVITATIONS` mutates elapsed Pending invitations | State connected; one job-target audit does not identify each expired invitation's before/after values |
| Admin | Save account roles | `UPDATE_ACCOUNT` writes multi-role set, auth version, and audit | Connected |
| Admin | Activate/deactivate account | Same command; latest role surfaces hide governed claim/attachment data | Connected; prior deactivation read leak is fixed |
| Admin | Assign direct manager | `ASSIGN_MANAGER` validates a distinct active Manager and audits reason | Connected |
| Admin | Create category | `CREATE_CATEGORY` creates the next stable ID with required reason | Connected |
| Admin | Rename/activate/deactivate category | `UPDATE_CATEGORY` preserves submitted snapshots | Connected |
| Admin | Set/release legal hold | `SET_LEGAL_HOLD` / `RELEASE_LEGAL_HOLD` mutate claim hold with reason | Connected; the retention job ignores the hold |
| Admin | Reassign Manager | `REASSIGN_MANAGER` checks inactive old Manager and required reason | Public action lacks the canonical unfinished-revision state guard |
| Admin | Reassign Finance owner | `REASSIGN_FINANCE` writes current owner and reason | Connected; old Finance timeline/export authority is not fully revoked |
| Admin | Reopen held claim | `REOPEN_HOLD` requires `Not paid` when execution was possible, clears current payment/approval and moves to Changes requested | Connected |
| Admin | Run deterministic daily operations | `RUN_DAILY_OPERATIONS` derives overdue/reminders/warnings and deletes aged drafts | **BLOCKING:** deletes aged legally held draft and files |
| Admin | Simulate queued delivery failures | `RUN_DELIVERY_RETRIES` increments passed queued deliveries | Connected as a manual fixture, not the canonical automatic due-time schedule |
| Admin | Retry delivery once | `RETRY_DELIVERY` allows one manual retry after Permanent failure | Connected |
| Admin | Generate CSV | `EXPORT_CSV` creates all-current-scope Admin CSV | Connected |
| Admin | Download CSV | `DOWNLOAD_EXPORT` rechecks current Admin role | Connected for Admin; denied-result auditing remains incomplete |

## Prior finding dispositions

### Initial audit findings

| Finding | Current disposition | Remaining classification | Fresh basis |
|---|---|---|---|
| `B-CODEX-001` | RESOLVED | — | Manager/Finance primary lists use current processing authority. |
| `B-CODEX-002` | RESOLVED | — | Revocation returns the same revision to Submitted. |
| `B-CODEX-003` | RESOLVED | — | Public draft creation and separate editable revision/resubmission exist. |
| `B-CODEX-004` | RESOLVED | — | Submission reads and snapshots the latest direct Manager. |
| `B-CODEX-005` | RESOLVED | — | Truthful save states, 1/2/4/8/16 retry generations, cancellation and manual retry exist. |
| `B-CODEX-006` | PARTIAL | MAJOR | Actual intervening field names are derived, but public reconciliation still lacks latest values beside preserved browser input. |
| `B-CODEX-007` | RESOLVED | — | Finance owner and Scheduled-only hold guards exist. |
| `B-CODEX-008` | RESOLVED | — | Executed adjustment resolution requires actual amount/date/reference and totals use actual amount. |
| `B-CODEX-009` | RESOLVED | — | Company-retained receipt SHA-256 duplication blocks without leaking another claim ID. |
| `M-CODEX-010` | PARTIAL | MAJOR | Timeout state/retry counters exist, but retry remains immediate/manual instead of automatic and due-time enforced. |
| `M-CODEX-011` | RESOLVED | — | Public roles, manager, category creation, both reassignment, and hold-reopen controls exist. |
| `M-CODEX-012` | PARTIAL | MAJOR | Some daily outcomes and retry counters exist; full schedule, failure and retention contracts do not. |
| `M-CODEX-013` | PARTIAL | MAJOR | Timelines and before/after fields exist, but governed file download and complete child-object provenance do not. |
| `M-CODEX-014` | PARTIAL | MAJOR | Search/filter/sort and actual CSV exist; date/late semantics and download reauthorization are incomplete. |
| `M-CODEX-015` | RESOLVED | — | Payment methods and verified hold reopen path exist. |
| `M-CODEX-016` | RESOLVED | — | Invitation acceptance, exact email, expiry and revoke race exist. |
| `M-CODEX-017` | RESOLVED | — | All 16 named states replace the active role workflow with deterministic outcome/recovery presentation, which the canonical contract permits. |
| `M-CODEX-018` | RESOLVED | — | Draft deletion removes every claim-owned file record. |
| `m-CODEX-019` | RESOLVED | — | Dialog initial focus, Tab containment, Escape and trigger restoration exist. |
| `m-CODEX-020` | RESOLVED | — | Seed category and immutable snapshot both read `Business lodging`. |
| `m-CODEX-021` | OPEN | MINOR | Page overflow is fixed, but mobile density/discoverability and CSV guidance remain weak. |

Disposition count for the 21 initial findings: **15 RESOLVED, 5 PARTIAL, 1 OPEN**.

### Findings first reported after pass 1

| Finding | Current disposition | Fresh evidence |
|---|---|---|
| `B-CODEX-022` | **RESOLVED** | Public Admin deactivation followed by Employee switch showed Access unavailable, zero claim IDs, and zero receipt names. |
| `B-CODEX-023` | **RESOLVED** | Public Finance failure of a new adjustment left Create adjustment disabled; engine regression also rejects the second creation. |

## Remaining and new findings

### B-CODEX-024 — BLOCKING — Related-user timeline bypasses current Finance scope and the fixed masking allowlist

- **Authority:** `RULE-118`, `RULE-140`, `RULE-185`, `RULE-186`; handoff current-processing and timeline projection contract.
- **Source:** `Timeline.tsx:5-11` treats every claim currently in any Finance lifecycle status as Finance-visible and never checks `claim.payment.ownerId === actorId` or shared-queue authority. `Timeline.tsx:23` renders every `event.reason` to non-Admin users. `App.tsx:47` also exposes the simulated internal actor ID in each related-user header.
- **Fresh public result:** Admin reassigned `clm-completed` from `usr-finance` to `usr-finance-other`. The claim correctly disappeared from the Finance queue (`0` matching queue controls), but Finance still saw one `REASSIGN FINANCE` timeline event and its `Owner unavailable` reason. In a separate reset, Admin set a legal hold with reason `Tax inquiry private note`; Finance saw both `SET LEGAL HOLD` and the exact Admin-only reason.
- **Effect:** loss of current relationship authority does not revoke history, and related-user projection exposes an explicitly forbidden Admin-only/legal-hold note. This is active unauthorized disclosure.
- **Test gap:** selector tests cover queue scope only. The timeline test uses an empty/benign projection and checks only that a few forbidden words are absent from static text.
- **Regression assessment:** the related timeline became public without a relationship-safe, allowlist-specific projection. This is a new material regression in the pass-2 correction surface.

### B-CODEX-025 — BLOCKING — Finance can download stale-scope CSV rows after relationship authority is lost

- **Authority:** `RULE-183`, `RULE-184`, `RULE-140`; handoff rule that every action checks latest target relationship.
- **Source:** `engine.ts:542-547` authorizes `DOWNLOAD_EXPORT` only by export existence, original export actor, current Finance/Admin role, and export version. It never revalidates the stored row IDs against current Finance scope. `ExportPanel.tsx:6,11-18` keeps the latest generated export and downloads its old bytes after the command commits.
- **Fresh public result:** Finance generated a four-row current-scope CSV. Admin reassigned `clm-completed` to the other Finance user. Finance then showed `3 of 3 authorized claims`, but Download authorized CSV still committed, and the saved bytes still contained `clm-completed`.
- **Effect:** a current role holder can export data for a claim whose relationship authority has been revoked. The explicit download-time reauthorization contract is false.
- **Test gap:** the Finance test generates and downloads immediately without changing role or row scope between actions; it asserts only the success message.
- **Regression assessment:** downloadable CSV was added in pass 2 without the required second scope check. This is a new material regression.

### B-CODEX-026 — BLOCKING — Daily retention deletes a legally held draft and its evidence

- **Authority:** retention/legal-hold handoff: legal hold protects every revision, attachment, and audit until required-reason release; `RULE-096..112` job contract.
- **Source:** `engine.ts:571-580` selects every Draft aged at least 90 days and deletes its files and claim without checking `claim.legalHold`.
- **Fresh public result:** through the Admin UI, `clm-draft` received legal hold reason `Preserve this draft`. The deterministic browser clock/last-save fixture was then advanced to the 02:00 KST 90-day boundary. Clicking Run deterministic daily operations produced `claimExists: false`, `files: 0`, and both prior `legalHold` plus later `expiredDraft.deleted/files.deleted` audits.
- **Effect:** the simulation irreversibly removes state the legal-hold action promises to preserve. This is destructive business-state corruption.
- **Test gap:** legal-hold tests cover set/release only; daily deletion tests use an unheld draft. No cross-feature invariant test exists.
- **Regression assessment:** the daily deletion action was added without integrating the already-existing hold invariant. This is a new material regression.

### M-CODEX-006 — MAJOR — Stale-form reconciliation still cannot show browser values against latest server values

- `engine.ts:820-825` now derives intervening changed field names from audit target versions, and `FeedbackRegion.tsx:10` renders those names.
- The feedback does not render the latest server values, while the form continues to show preserved browser input. A user cannot perform the canonical side-by-side comparison required by `RULE-134..135`; only field names are supplied.
- Tests assert `['version', 'revision.merchant']` and the preservation phrase, not a rendered old/new comparison and retry with a reconciled expected version.

### M-CODEX-010 — MAJOR — Scan retries are counters behind an immediate manual button, not the 30-second/two-minute automatic schedule

- **Authority:** `RULE-093..095`, SCR-001 and handoff scan recovery.
- `engine.ts:673-696` never checks `state.now >= nextScanRetryAt`. `AttachmentPanel.tsx:51` immediately renders an enabled Retry scan button.
- Fresh public evidence recorded `nextScanRetryAt: 2026-08-22T00:00:30.000Z`, yet the button was immediately enabled and an immediate click advanced `scanAttempts` from 0 to 1 and moved the time to `00:02:00.000Z`.
- The test named “retries at 30s/2m” directly dispatches both commands without advancing time, so it proves counters, not scheduling.

### M-CODEX-012 — MAJOR — Scheduled operations remain a manual approximation without the full retry/deletion/retention contract

- **Authority:** `RULE-075..112`, `RULE-170..174`, TASK-006/007.
- `RUN_DELIVERY_RETRIES` accepts any passed queued IDs immediately. The first failure sets the next time to 10 minutes, so the required initial one-minute retry is neither scheduled nor enforced; subsequent clicks also ignore due time.
- `RUN_DAILY_OPERATIONS` has no deletion-failure result/retriable undeleted path, no seven-year fiscal-year retention processing, and no public clock/scheduler that can cause the seeded workspace to reach the modeled dates. Review warnings are not reconciled as assignment state changes.
- Tests mutate `state.now` directly and call commands in a loop without asserting due-time refusal, job time, deletion failure, seven-year retention, or stop conditions.

### M-CODEX-013 — MAJOR — Governed attachment access and complete append-only provenance remain absent

- **Authority:** `RULE-029..031`, `RULE-137..140`, `RULE-160`, `RULE-165..169`, TASK-007.
- `DomainCommandType` has no file-grant or file-download request. Employee attachment rows have no download control, and Manager/Finance detail surfaces render no attachment download or historical evidence list.
- Audit enrichment snapshots only the command target. Attachment and adjustment commands target the claim, so their file/adjustment before/after values are absent; invitation reissue audits the new invitation but not the prior link whose status changed; expiry writes one job-target event rather than target-specific invitation provenance.
- No denied file-download audit is possible, and raw tokens/grants are absent because the feature itself is absent.

### M-CODEX-014 — MAJOR — Role lists do not implement the canonical submission-date and late-claim filters

- **Authority:** `RULE-179..184`, `AC-001..004` list expectation.
- `ClaimExplorer.tsx:28-29` applies both date fields only to `revision.expenseDate`; no submission-date filter exists. `ClaimExplorer.tsx:21,30` labels a three-day pending review as `Delayed` instead of filtering the canonical late-expense flag represented by `lateReason`.
- Current-filter generation and CSV bytes are real, but those bytes inherit the wrong filter semantics. Download-time scope loss is separately BLOCKING under `B-CODEX-025`.
- Tests cover merchant search/status only and do not test submission date, old-expense late flag, or filter snapshot/row equivalence.

### M-CODEX-027 — MAJOR — Actionable notification recipients and event-key protection remain incomplete

- **Authority:** `RULE-083..090`; handoff notification matrix.
- `APPROVE_CLAIM` queues only the Employee recipient, so the newly approved claim creates no shared-Finance email/in-app event required by `RULE-085`. `RESOLVE_ADJUSTMENT` queues no Employee result delivery. Most ordinary `queueDelivery` calls omit a logical event `uniqueBase`, leaving `uniqueKey` undefined and relying only on command idempotency rather than the delivery-event dedupe contract.
- Unit tests count the deliveries that happen to be created but do not assert the complete recipient/template matrix or same-logical-event deduplication with a different command key.

### M-CODEX-028 — MAJOR — FX evidence type, six-decimal precision, and Manager evidence inspection are incomplete

- **Authority:** `RULE-013..015`, REQ-001/002, SCR-001/002.
- The data model distinguishes only generic `FX_EVIDENCE`; it never records card statement, bank exchange record, or official-rate capture/PDF type. Submission converts the rate to a number and checks arithmetic but not the maximum six decimal places.
- Manager Review facts show amount/rate text but no receipt/FX attachment list or governed evidence request. A Manager can approve through the public UI without seeing the attached evidence that the canonical review requires.
- Tests cover arithmetic mismatch and file count/MIME, not evidence subtype, seven-decimal rejection, or Manager receipt/FX visibility.

### M-CODEX-029 — MAJOR — Public Manager reassignment lacks the canonical unfinished-revision guard

- **Authority:** `RULE-026..028`; handoff “Only Admin may reassign an unfinished revision when its assigned manager is inactive.”
- `engine.ts:479-488` checks only claim existence, replacement Manager validity, old Manager inactivity, and reason. It accepts Draft, terminal, payment-processing, and completed claims. `AdminSurface.tsx:94-97` exposes the button for every claim in the selector.
- This can mutate historical routing on completed/final claims or bypass direct-manager assignment for a Draft instead of transferring only an unfinished submitted revision.
- Existing tests do not execute public or engine Manager reassignment and therefore do not assert allowed/denied lifecycle states.

### m-CODEX-021 — MINOR — Mobile remains very long and omits required desktop-recommended CSV guidance

- Fresh 320 px Chromium measurements showed 0 px page overflow for Employee, Manager, Finance, and Admin, so responsive clipping is resolved.
- The Employee page was 4,995 px high. Finance and Admin both kept CSV available, but exact visible `desktop recommended` guidance count was `0`, contrary to `RULE-200` and the handoff.
- This is a discoverability/guidance defect rather than a domain-state failure. Current iOS Safari, Android Chrome, actual camera/file-picker behavior, and user acceptance remain unverified.

## Tests versus behavior

The `71/71` unit/component result and `11/11` Chromium E2E result coexist with BLOCKING drift because the suite tests components in isolation and immediate happy paths:

1. Queue authorization tests stop at `claimsForRole`; no test reassigns Finance and then inspects the separate timeline projection.
2. The timeline allowlist test uses no seeded legal-hold/Admin-only reason and asserts only absence of a few literal secret words.
3. CSV tests generate and download immediately. No test changes row authority between generation and download or reads downloaded bytes against the new scope.
4. Legal-hold and retention tests are independent. No test holds an expiring draft and runs the deletion job.
5. Scan tests call retry commands immediately and therefore encode the missing timing guard while their title claims scheduled behavior.
6. Delivery retry tests loop commands without a clock and assert only attempt count/status.
7. Audit tests inspect the claim wrapper, not changed file, adjustment, old invitation, delivery, or denied-download targets.
8. E2E covers one happy mutation per role, Employee-only responsive checks, and no cross-role authority-loss sequence.

## Visual completion gate

The checks were fixed before judging the fresh render from revision-55 handoff, `SCR-001..004`, approved Figma screenshots, and the Figma coverage/state/action matrices. Fresh candidate screenshots were captured from source commit `24a139f`, opened at native pixels, inspected, then removed with the task-owned temp directory.

| Check | Expected observable | Fresh observation | Result |
|---|---|---|---|
| `V-B-P2-01` role structure | Four explicit role surfaces with operational list/detail or Admin modules | Employee, Finance, and Admin desktop renders preserve the approved low-fi hierarchy with clear role, status and actions | PASS |
| `V-B-P2-02` responsive reflow | 320/375 single column and no page-level overflow | All four roles measured 0 px overflow at 320; Employee full page was 4,995 px | PASS for sampled Chromium; density remains MINOR |
| `V-B-P2-03` action truth | Visible actions agree with current domain authority and effect | Timeline, stale export download, and held-draft deletion visibly/observably contradict authority/state | **FAIL** |
| `V-B-P2-04` state/recovery | 16 deterministic outcome/recovery presentations | Exactly 16 named presentations replace the active role workflow and provide outcome/recovery copy | PASS for deterministic presentation coverage |
| `V-B-P2-05` keyboard dialog | Focus enters, stays contained, Escape/cancel closes, trigger regains focus | Source and focused component/E2E checks cover all four behaviors | PASS in sampled Chromium |
| `V-B-P2-06` mobile CSV guidance | Finance/Admin CSV available with desktop recommendation | CSV remained available; required desktop-recommended text was absent on both surfaces | **FAIL** |
| `V-B-P2-07` simulation boundary | No real payment/email/auth/scan/immutable-storage claim | Headers and helper copy consistently identify local deterministic simulation | PASS |

**Overall visual/product verdict: FAIL.** The structural render and overflow checks pass, but required action truth and mobile guidance fail. Browser screenshots cannot establish current iOS Safari/Android Chrome behavior or full accessibility compliance.

## No-new-regression assessment

**FAIL.** Pass 2 introduced three material regressions while correcting adjacent gaps:

- mounting related-user timelines without a relationship-safe allowlist created `B-CODEX-024`;
- adding downloadable CSV without row-scope reauthorization created `B-CODEX-025`;
- adding daily deletion without legal-hold exclusion created `B-CODEX-026`.

The corrected source remains frozen; no audit-time correction was made.

## Final result

| Result | Value |
|---|---|
| Prior pass-1 BLOCKING findings | `B-CODEX-022` RESOLVED; `B-CODEX-023` RESOLVED |
| Current BLOCKING | **3** |
| Current MAJOR | **8** |
| Current MINOR | **1** |
| Critical failure | **Yes** |
| Implementation changed during audit | **No** |
| Verdict | **FAIL — CODEX_DRIFT_UNRESOLVED** |
