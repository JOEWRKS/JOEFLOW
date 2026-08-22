# Replication B — Codex correction pass 3 final audit

## Verdict

**FAIL — CODEX_DRIFT_UNRESOLVED**

| Severity | Count |
|---|---:|
| BLOCKING | **2** |
| MAJOR | **5** |
| MINOR | **2** |
| Critical Failure | **Yes** |

The pass gate is not met: BLOCKING and MAJOR are non-zero, and two public mutation paths can corrupt authoritative business state. The fresh deterministic suite is green, but it does not cover those paths.

## Frozen audit basis and independence

- Evidence `HEAD`: `a48fc51a01bc716fb70458b1a1a3d324c3de7d34` on `eval/v0.4-replication-b-codex`.
- Corrected source commit: `eecebc28701006dd2c7be4045a22542e34719705`.
- `HEAD:codex-implementation` tree: `6294fc9072521fdb762808b87203a7e8bac4f7f5`.
- Canonical state: expense-reimbursement rev 55, approved digest `18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f`.
- Canonical `state.json` SHA-256 observed: `c0e790c3a8c35f0cdc894110f069ab4d7919aed388f0a4fad2c54e5ae8193395`.
- Design authority: Replication B Figma file `fyow2BHoAXzpkzpozDGWXf`, page `Low-fi — Rev 55`, including the role/state boards and mobile frames.
- Authority read before prior-audit anchoring: canonical markdown, `CODEX_IMPLEMENTATION_HANDOFF.md`, RULE-001..RULE-201, AC-001..AC-004, DATA-001, implementation source, and the Figma evidence were traced before reading pass 2 and the pass 3 correction report.
- No Replication A artifact/path/branch, hidden answer bank content, or cross-domain comparison was read.
- Audit was read-only except for this report. No implementation, canonical state, test, or other evidence file was changed.

## Findings

### B030 — rejected adjustment resolution mutates state and bypasses the one-active-adjustment guard — BLOCKING

`RESOLVE_ADJUSTMENT` writes `adjustment.verification` before validating the mandatory Executed amount/date/reference (`engine.ts:288-305`). A rejected result therefore returns a changed state with no version increment and no committed audit. That leaked verification also changes the active-adjustment predicate: a Failed adjustment with verification is no longer treated as active, so `CREATE_ADJUSTMENT` accepts a second In progress adjustment.

Fresh reproduction:

1. Complete payment and create/fail an adjustment.
2. Dispatch `RESOLVE_ADJUSTMENT` with `result=Executed` and a note but without completion evidence.
3. Result is rejected with `COMPLETION_EVIDENCE_REQUIRED`, target version remains 4, audit count does not increase, yet the failed adjustment now contains an Executed verification.
4. Dispatch `CREATE_ADJUSTMENT` at version 4.
5. It commits at version 5, leaving the verified Failed adjustment plus a new In progress adjustment.

This violates the rejected/stale no-op contract (RULE-133/134), the one-active-adjustment safety invariant, and the audit/version model. It also reopens the safety objective behind B023 through a different public sequence.

### B031 — non-finite money values can be saved and submitted — BLOCKING

`UPDATE_DRAFT` converts numeric inputs with `Number(value)` without finite-number validation (`engine.ts:711-731`). Submission checks only `originalAmount <= 0`; that comparison is false for `NaN`, and KRW amount has no finite check in the KRW branch (`engine.ts:333-377`).

Fresh reproduction dispatched `UPDATE_DRAFT` with non-numeric `originalAmount` and `krwAmount`; it committed at version 2 with both values non-finite. `SUBMIT_CLAIM` then committed at version 3 with final status Submitted. The HTML number controls also admit an overflow representation such as `1e309`; conversion produces `Infinity`, while JSON persistence turns the corrupted values into `null` after the in-memory submit.

This permits an authoritative submitted claim whose total is not a finite amount, corrupting the money, approval, export, and payment basis.

### M006 — Admin stale comparisons still omit latest server values — MAJOR

The draft stale comparison is fixed, but Admin audit fields use paths such as `user.active`, `user.roles`, `user.authVersion`, `category.*`, and `invitation.*`. `latestValuesForStale` traverses those prefixes against already-flat target records (`engine.ts:977-988`), producing `undefined` values. Fresh stale `UPDATE_ACCOUNT` reproduction returned changed fields `version,user.active,user.roles,user.authVersion` but serialized `latestValues` as `{}`. The user sees the changed field names without the authoritative values required for a safe comparison.

Disposition: **M006 PARTIAL**.

### M012 — time-driven stop/clear and retention-clock semantics remain incomplete — MAJOR

Three authority-bearing timing behaviors remain wrong:

- Fresh `COMPLETE_PAYMENT` on an overdue Scheduled claim committed Payment completed while `payment.overdue` remained true. The Finance surface renders the claim as Payment overdue whenever that flag is true, even in a terminal state (`FinanceSurface.tsx:28`).
- A queued `MANAGER_REVIEW_REMINDER` delivery was allowed to retry after the Manager decided the claim. Attempts advanced from 1 to 2, contrary to the stop-after-decision rule.
- `commit` updates a claim's `updatedAt` for every committed command, while draft retention is calculated from that same field (`engine.ts:77`, `625-630`). Scan worker/retry commands and same-value draft saves therefore reset the 90-day clock even though RULE-098 limits reset to an actual saved draft change.

The corrected daily job does now retain held drafts and related files and records `SKIPPED_LEGAL_HOLD`; the remaining defects are the terminal clear/stop and clock semantics above.

Disposition: **M012 PARTIAL**.

### M013 — related timeline projects current status onto historical events — MAJOR

The corrected timeline is scoped to related audit/delivery events and current authority, and file grants now have explicit issuance/download audit. However, the projection assigns `claim.status` to every historical entry (`selectors.ts:45-56`). Fresh approval then revocation produced both the historical `APPROVE_CLAIM` and `REVOKE_APPROVAL` entries with business status Submitted. The approval event is therefore presented with a status that was only true after the later reversal.

This is materially misleading provenance: an authorized reviewer cannot reconstruct the business state at the event being audited.

Disposition: **M013 PARTIAL**.

### M014 — Admin current-filter export semantics remain incomplete — MAJOR

Role list filter predicates now compose correctly, and stale generated exports are reauthorized at download. The Admin surface still exposes no claim filter controls before a button labelled `Generate current-filter CSV`; it exports the whole Admin-authorized scope. In addition, the CSV chooses the current category name before the immutable submitted snapshot (`engine.ts:568-573`). Fresh reproduction renamed a submitted claim's category from `Business lodging` to `Renamed lodging`; the claim retained the immutable snapshot but CSV emitted `Renamed lodging`.

The mobile Audit & export rendering is also not the authority's single-column composition: at 390 px the raw-audit card collapses to a narrow clipped strip beside the export card. CSV guidance, reauthorization wording, exclusions, 10,000-row cap, and “desktop recommended” text are present, but the adjacent audit content is not practically readable.

Disposition: **M014 PARTIAL**.

### M027 — approval-revocation and stopped-reminder notification semantics remain incomplete — MAJOR

Fresh approval revocation produced the required two Employee deliveries but zero Manager deliveries. RULE-084 includes the Manager for the approval-revocation result. Separately, a queued Manager review reminder continued retrying after a claim decision (attempts 1 → 2), violating the stop condition. Delivery failure/manual retry behavior otherwise remains implemented and audited.

Disposition: **M027 PARTIAL**.

### m021 — mobile Admin navigation remains dense and horizontally hidden — MINOR

At 390 px the six Admin tabs remain a horizontal scroller, with later destinations hidden until horizontal movement. The page itself has no horizontal overflow and the primary controls remain reachable, but the state/navigation density still diverges from the clearer mobile authority.

Disposition: **m021 OPEN**.

### m030 — two seeded category labels drift from DATA-001 — MINOR

Seed data uses `Software & subscriptions` and `Training & books` (`seed.ts:117-118`); canonical DATA-001/RULE-189 specify `Software/subscriptions` and `Education/books`. IDs and active state are correct, but the visible taxonomy is not exact.

Disposition: **NEWLY DETECTED**.

## Pass 2 targeted finding dispositions

| Finding | Final disposition | Fresh evidence |
|---|---|---|
| B024 | **RESOLVED** | Related timeline excludes unrelated target events; revoked Manager/Finance authority yields zero related timeline entries. |
| B025 | **RESOLVED** | After Finance reassignment, `DOWNLOAD_EXPORT` rejects `EXPORT_SCOPE_REVOKED` and records a DENIED audit. No stale rows were returned. Residual CSV content/filter defects are counted under M014. |
| B026 | **RESOLVED** | A 90-day held draft, its linked file, and its evidence were retained; `SKIPPED_LEGAL_HOLD` was recorded. |
| M006 | **PARTIAL** | Draft latest values work; Admin prefixed fields remain blank. |
| M010 | **RESOLVED** | First timeout schedules +2 minutes, early retry rejects `SCAN_RETRY_NOT_DUE`, and bounded retry/discard paths pass. |
| M012 | **PARTIAL** | Legal-hold retention and deletion retry are present; overdue clearing, reminder stop, and actual-change retention clock remain wrong. |
| M013 | **PARTIAL** | File grant issuance/download denial and related scoping work; historical status provenance is false. |
| M014 | **PARTIAL** | Role filters compose; Admin current-filter controls, immutable snapshot export, and mobile audit composition remain incomplete. |
| M027 | **PARTIAL** | Most delivery contracts pass; revoke Manager recipient and stopped reminder retry do not. |
| M028 | **RESOLVED** | FX check uses `originalAmount × exchangeRate`, ±1 KRW tolerance, six-decimal limit, and linked evidence. |
| M029 | **RESOLVED** | Completed-claim Manager reassignment rejects `REASSIGNMENT_STATUS_DENIED`; open-claim reassignment and old-authority removal pass. |

Pass 2 totals: **6 resolved, 5 partial, 0 still at their prior BLOCKING severity**. The audit still fails because B030/B031 are independently blocking.

## Initial and pass 1 disposition ledger

| Prior finding | Disposition |
|---|---|
| B001, B002, B003, B004, B005 | **RESOLVED** |
| B006 | **PARTIAL**, tracked as M006 |
| B007, B008, B009 | **RESOLVED** |
| M010, M011 | **RESOLVED** |
| M012, M013, M014 | **PARTIAL** |
| M015, M016, M017, M018 | **RESOLVED** |
| m019, m020 | **RESOLVED** |
| m021 | **OPEN MINOR** |
| B022 | **RESOLVED** |
| B023 | Direct failed-adjustment guard **RESOLVED**, but its invariant is bypassable via B030; B030 is counted once as the blocking regression expression. |

## Fresh verification

All commands were run against the frozen tree without installing dependencies.

| Check | Result |
|---|---|
| `python skills/joewrks-product-definition/scripts/validate_state.py product-definition/expense-reimbursement-dogfood/state.json` with `PYTHONDONTWRITEBYTECODE=1` | **PASS**, `valid: true`, `errors: []` |
| `python skills/joewrks-product-definition/scripts/validate_closure.py product-definition/expense-reimbursement-dogfood/state.json` with `PYTHONDONTWRITEBYTECODE=1` | **PASS**, `closed: true`, exact approved digest, all closure metrics 0 |
| `npm test -- --run --reporter=dot` | **PASS**, 7 files, 85/85 tests |
| `npm run build` | **PASS**, 41 modules transformed; production CSS/JS emitted |
| `PLAYWRIGHT_BROWSERS_PATH=<worktree>/codex-implementation/.playwright-browsers npm run test:e2e -- --reporter=line --workers=2` | **PASS**, 11/11, worktree-local Chromium only |

The successful suite is not accepted as proof against B030/B031 because fresh reproductions exercised mutation combinations absent from it.

## Required sequence coverage

- **Authority loss:** Finance export download after reassignment rejected `EXPORT_SCOPE_REVOKED` with DENIED audit; file download after relationship loss rejected `FILE_AUTHORITY_REVOKED` with DENIED audit; old Manager/Finance related timeline returned no claims/events.
- **File grants:** five-minute grant issuance committed; authorized download produced SUCCESS provenance; relationship loss and single-use/invalid grant paths denied access.
- **Legal hold and retention:** held draft/files retained with `SKIPPED_LEGAL_HOLD`; deterministic deletion failure retained records for a later daily retry and warning path.
- **Retry timing:** early scan retry rejected `SCAN_RETRY_NOT_DUE`; bounded timeout/discard behavior passed. Manager reminder stop failed as M027.
- **FX:** multiplicand, tolerance, precision, evidence type/linking, and resubmission flows passed.
- **Reassignment:** open-claim reassignment changed authority and notifications; completed-claim reassignment was denied. Old queued reminder stop remains wrong.
- **Filters/CSV:** combined role filters returned only the expected submitted claim. CSV authority recheck passed; Admin filter/snapshot semantics failed as M014.
- **Notifications:** core two-channel deliveries and deterministic failure/manual-retry paths passed; approval-revocation Manager delivery and post-decision retry stop failed as M027.

## Visual inspection

Implementation desktop (1440×1000) and mobile (390×844) were freshly rendered and compared with Figma role/state authority. Desktop hierarchy, cards, state fixture, focus styling, and governed CSV guidance are coherent. Mobile has no page-level horizontal overflow and displays the CSV availability/desktop recommendation text, but Admin tabs stay horizontally hidden and Audit & export retains a squeezed two-column body rather than the approved single-column composition. These observations inform M014 and m021; cosmetic differences alone were not escalated.

## No-new-regression assessment and boundaries

- **Newly detected material residuals:** B030, B031, and m030. Git blame places the unsafe B030 mutation and B031 numeric conversion before the pass 3 correction commit; there is no evidence that pass 3 introduced them, but their presence means the final no-uncovered-regression gate is not satisfied.
- **Pass 3 correction regressions introduced by the correction diff:** none independently proven.
- **Runtime boundary:** this implementation is a deterministic browser simulation. Real authentication, storage, malware scanning, email/delivery providers, bank execution, and operating-system deletion were not exercised. Claims are limited to the domain engine, browser UI, local persistence, and recorded audit/delivery projections.
- **Figma boundary:** the approved Replication B file/nodes were read and visually inspected; no design file was mutated.

## Exact final decision

**BLOCKING=2, MAJOR=5, MINOR=2, Critical Failure=Yes.**

Per the mandated gate (PASS only when BLOCKING=0, MAJOR=0, Critical Failure=0), the exact verdict is:

**FAIL — CODEX_DRIFT_UNRESOLVED**
