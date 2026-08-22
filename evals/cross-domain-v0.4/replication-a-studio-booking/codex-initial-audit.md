# Replication A Codex Implementation — Initial Blind Audit

## Audit boundary and blindness attestation

This is a fresh, independent, source-and-behavior audit of Replication A's Codex implementation. I read only the authorized canonical Studio Booking artifacts, the three authorized Codex reports/plans, and source/tests/README/package files under `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/`. I did not read `evals/end-to-end-v0.3.1`, any historical Make drift/audit report, any Replication B path, `FIGMA_DESIGN_AUDIT.md`, `figma-generation-report.md`, `aggregate-results.md`, previous correction/audit files, or the web. I did not mutate implementation, canonical artifacts, git state, or external state; this report is the only write.

Canonical authority readback is `state.json` status `CLOSED`, definition revision `62`, approved digest `8ebb472aa66a5b680961e102db950214cea2d0be3b644164f23712030b9d8a7c` (`state.json:5-10`; `CODEX_IMPLEMENTATION_HANDOFF.md:5-18`).

## Exact commands and checks

All commands ran from `D:\JOEWRKS\.worktrees\joewrks-product-definition-v0.3-publish` unless stated otherwise.

1. Authorized inventory/readback: `rg --files evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation` plus `Get-Content -Raw`/numbered `Get-Content` of each authorized source, test, README, plan, report, handoff, and uppercase projection. Exit `0`.
2. Fresh tests, from `...\codex-implementation`: `npm test`. Exit `0`: 10 tests, 10 pass, 0 fail.
3. Canonical inventory comparison: a Node ES-module one-liner parsed each `SCR-*` / `Major actions` entry from `SCREEN_SPEC.md`, imported `src/catalog.js`, and compared the resulting objects. Exit `0`: `canonicalScreens=27`, `implementationScreens=27`, `canonicalActions=78`, `implementationActions=78`, `uniqueImplementationActions=78`, `exactRegistry=true`.
4. Browser-domain wiring search: `rg -n "createBooking|changeBooking|createPriceSnapshot|managementLinkResponse|deliveryOutcome|replayMutation|canChangeOrCancel|updateRate" evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation/src/app.js`; the expected no-match exit `1` was normalized by the audit wrapper to exit `0`, output `NO_DOMAIN_JOURNEY_CALLS`.
5. Focused Node behavior probe imported `src/domain.js` and exercised invalid quantities/attendees, policy representation, link neutrality, authorization, and snapshot mutation. Exit `0`, output: `fractionalEquipmentAccepted=true`, `negativeAttendeesAccepted=true`, `booleanOnlyPolicyAccepted=true`, `unknownEmailReportedSent="SENT"`, `staffPublishAuthorized=true`, `customerOperatorProposalAuthorized=true`, `unknownActionAuthorized=true`, `nestedSnapshotMutable=true`.
6. Authority-pin search: `rg -n "8ebb472aa66a5b680961e102db950214cea2d0be3b644164f23712030b9d8a7c|approved_digest|approved digest" <implementation> <codex-implementation-report.md>`; expected no-match exit `1` was normalized to exit `0`, output `NO_IMPLEMENTATION_DIGEST_PIN`.
7. Server check: preflight `Get-NetTCPConnection -LocalPort 4173 -State Listen` found `NO_LISTENER`; `node server.mjs` printed `Studio Booking prototype: http://127.0.0.1:4173`. Fresh `Invoke-WebRequest` readback exited `0`: `{"RootStatus":200,"RootTitle":"스튜디오 예약 운영","RootHasActionHost":true,"DomainStatus":200,"DomainHasBooking":true,"MissingStatus":404}`. The audit-owned listener was stopped with Ctrl-C (server exit `1`, expected interrupt); a final listener check exited `0` with `LISTENER_STOPPED`.

## Strengths

- The canonical registry is exact: 27 unique stable screen IDs and 78 unique major action identifiers match `SCREEN_SPEC.md` exactly (`src/catalog.js:1-4`; `tests/catalog.test.mjs:5-40`).
- The static shell clearly disclaims production authentication, storage, delivery, encryption, and integration claims (`index.html:3`; `README.md:3-5`), which respects the prototype boundary in `CODEX_IMPLEMENTATION_HANDOFF.md:20-34`.
- The domain layer correctly demonstrates several isolated rules: 30-minute start/end checks, 1–8 hour duration, two-hour lead time, inclusive 90th Seoul calendar day, 30-minute occupancy expansion, exact 48-hour comparison, even-integer-won update validation, Korean won formatting, and a simple stale/conflict no-op (`src/domain.js:1-33`).
- Semantic landmarks, native buttons/select/textarea/dialog, a skip link, live status, visible focus styling, 44px minimum controls, responsive CSS, and reduced-motion CSS are present (`index.html:2-3`; `app.js:8-12`; `styles.css:1`).
- The dependency-free Node test/server workflow runs cleanly, and the fresh static-server readback served this implementation with correct 200/404 behavior (`package.json:1-6`; `server.mjs:1-5`).

## Findings

### BLOCKING

#### A-CODEX-DRIFT-001 — The browser is a stateless action-name demonstrator, not the required substantive prototype

- **Implementation evidence:** `app.js:4` stores only role, screen, scenario, and pending action. `app.js:7-12` renders the same generic panel, one generic reason textarea, and action-ID buttons for every screen; every allowed action either opens a generic dialog or replaces status text. The SPA imports only `authorize` and `transitionWithReason` (`app.js:1-2`), and the focused wiring search found no calls to booking, change, pricing, link, delivery, 48-hour, rate, or idempotency APIs. There are no customer configuration fields, booking/occupancy records, policy documents, management tokens/sessions/drafts, delivery attempts, operator accounts, resources, inquiries, incidents, or attendance state.
- **Canonical authority:** The prototype must provide substantive stateful Customer, Staff, and Owner journeys and make failure/recovery/concurrency/idempotency observable (`CODEX_IMPLEMENTATION_HANDOFF.md:22-31`), including nine concrete scenarios (`:134-144`) and 27 separate desktop surfaces plus three 360px role journeys (`:123-132`).
- **Observed impact:** A click on `confirm_booking`, `publish_policy_version`, `create_resource`, `reply_booking_inquiry`, or `mark_booking_no_show` is behaviorally the same: a generic status sentence, with no canonical state transition to inspect. The primary implementation objective is therefore absent even though identifiers are present.
- **Minimum correction:** Implement deterministic in-memory domain state and screen-specific forms/readbacks for at least the required nine scenarios, wiring actions to real guarded transitions. Customer booking/management, Staff operations, and Owner administration must each change and display canonical state, with failures preserving/returning the exact required state and recovery affordance.

### MAJOR

#### A-CODEX-DRIFT-002 — Screen-level `Shared` access and allow-by-default authorization grant forbidden actions

- **Implementation evidence:** `catalog.js:2-4` invents a visible `Shared` access category and gives every Customer/Owner/Staff role every action on SCR-014, SCR-016, and SCR-017. It also gives Staff every SCR-019 action and every SCR-012 action. `domain.js:36-37` denies only six hard-coded actions and authorizes every other action, including unknown actions. Fresh probes returned `staffPublishAuthorized=true`, `customerOperatorProposalAuthorized=true`, and `unknownActionAuthorized=true`. `app.js:8-10` gates only at screen level plus this incomplete action check.
- **Canonical authority:** The only actors/permissions are Customer, Studio operator umbrella, Owner, and Staff; Staff has no operator-account or legal-hold authority, complete audit is Owner-only, and customer actions are bound to the authenticated reservation (`CODEX_IMPLEMENTATION_HANDOFF.md:36-45`). Policy publication/withdrawal is Owner work and late proposals are Owner/Staff work while consent/rejection is customer work (`USER_FLOWS.md`, FLOW-011 and FLOW-014; registry at handoff `:68-71`). No extra role/access concept may be invented (`CODEX_IMPLEMENTATION_HANDOFF.md:154-156`).
- **Observed impact:** Staff can publish/withdraw policy versions and open complete-audit actions; Customer can propose/commit operator changes; operators can exercise customer consent/rejection; any unrecognized action is authorized. This violates role and reservation authority, and the UI displays the noncanonical label `Shared 접근`.
- **Minimum correction:** Replace coarse screen access with an explicit deny-by-default role/action/context matrix. Split mixed-audience actions by authenticated context while keeping the canonical screen/action IDs, require reservation/proposal binding for customer actions, restrict Owner-only actions (including publish/withdraw and complete audit), and remove `Shared` as a user-visible authority.

#### A-CODEX-DRIFT-003 — Booking confirmation does not atomically recheck actual availability, hours, buffers, price, or complete valid input

- **Implementation evidence:** `createBooking` accepts only caller-supplied `room`, `equipment[].available`, and a Boolean policy flag (`domain.js:13-24`); it has no existing bookings/holds/blocks/hours/exceptions input and performs no room-conflict or aggregate equipment calculation. `changeBooking` trusts a caller-supplied `conflicts` array rather than deriving conflicts from state (`domain.js:26-30`). The probe showed fractional equipment quantity and negative attendee count are accepted. The UI never calls either function (`app.js:1-13`).
- **Canonical authority:** Final confirmation must atomically recheck room and aggregate equipment availability, compatibility, hours, buffers, lead time, capacity, policies, and price, creating neither booking nor partial occupancy on failure and showing alternatives (`CODEX_IMPLEMENTATION_HANDOFF.md:83-92`, `:136-139`).
- **Observed impact:** The model can confirm invalid configurations, cannot detect a conflicting second confirmation from state, cannot enforce operating hours/blocks, and cannot demonstrate an atomic booking commit or alternatives. Its `available`/`conflicts` inputs merely trust the answer the transition is required to compute.
- **Minimum correction:** Make confirmation a single state transition over authoritative resources, bookings, holds, blocks, hours/exceptions, policies, and version. Validate positive integer attendees/quantities and all boundaries; derive buffered conflicts and aggregate quantities; compare price at commit; return unchanged state plus preserved compatible input, invalid-selection removals, and current alternatives on any failure.

#### A-CODEX-DRIFT-004 — Price snapshot and policy-version semantics are materially incomplete

- **Implementation evidence:** `domain.js:6-10` shallow-freezes only the snapshot's outer object; nested room/equipment data remains mutable (`nestedSnapshotMutable=true`). `createBooking` reduces all policy authority to `policiesCurrent: true|false` and snapshots no document IDs, versions, or consent times (`domain.js:14,21,24`). There is no old/new snapshot delta model, publication/withdrawal state, or no-auto-revival behavior in source or UI.
- **Canonical authority:** Prices are integer KRW, prorated in 30-minute units, with even-integer hourly rates; confirmation freezes component rates, quantities, duration, line totals, and total; change review shows old/new/delta; all five current policy versions and versioned consents are required and withdrawal does not revive an older version (`CODEX_IMPLEMENTATION_HANDOFF.md:94-101`).
- **Observed impact:** A Boolean can authorize confirmation without the five publications/consents, historical price facts can be mutated, and change/policy screens cannot demonstrate the required review or version lifecycle.
- **Minimum correction:** Store immutable copied component/quantity/rate/duration/total snapshots and versioned consent records for exactly five policy types. Add old/new/delta review, even-won validation on every rate path, and draft/review/publish/withdraw transitions where only the current published version qualifies and withdrawal leaves no current version.

#### A-CODEX-DRIFT-005 — Management-link neutrality, token/session lifecycle, and two-hour draft recovery are absent and one result is misleading

- **Implementation evidence:** `managementLinkResponse` is a one-line status mapper with no email-format validation, token, expiry, one-time use, older-token revocation, session, reservation binding, request history, or draft (`domain.js:34`). It ignores `known`; for an unknown email outside supplied limits the fresh probe returns `SENT`, contradicting no-send semantics. `app.js:7-10` treats `expired` as generic message text and does not reject a mutation or retain/recover/delete a draft.
- **Canonical authority:** Links last 15 minutes and are one-time, successful use creates a 30-minute session, newer issuance revokes an older unused token, rate limits are 60 seconds/five per hour, valid unknown emails get the same neutral response without token/email mutation, and the latest encrypted reservation-bound draft lasts two hours across reauthentication (`CODEX_IMPLEMENTATION_HANDOFF.md:109-112`, `:140`).
- **Observed impact:** Reservation-existence neutrality, issuance side effects, one-time semantics, expiry, session enforcement, and draft recovery cannot be inspected. `SENT` for an unknown address misstates a side effect the contract forbids.
- **Minimum correction:** Add a stateful neutral link-request command that separates public response from internal issuance, validates format, records rate-limit windows, issues/revokes one-time tokens only for known addresses, converts valid use to a 30-minute reservation-bound session, and implements latest-only two-hour draft save/restore/discard/expiry behavior.

#### A-CODEX-DRIFT-006 — Delivery independence is reduced to a label; attempts, retry schedule, queueing, and resend idempotency do not exist

- **Implementation evidence:** `deliveryOutcome` directly maps a failed Boolean to `FAILED_QUEUE` (`domain.js:35`), with no delivery event/attempt record or 1/5/30-minute schedule. `replayMutation` is a generic standalone helper (`domain.js:39`) and is not used by delivery or UI. `app.js:7` only prints a delivery-failure sentence; SCR-006/SCR-023 actions do not display attempts or mutate a queue.
- **Canonical authority:** Delivery state is independent from business state, must record the initial attempt and retries at 1, 5, and 30 minutes, queue only final failure, and suppress duplicate sends on success/manual resend (`CODEX_IMPLEMENTATION_HANDOFF.md:114-117`, `:142`).
- **Observed impact:** A first failure is incorrectly presented as a final queue state, operators cannot inspect attempt history, and idempotent resend cannot be demonstrated. Business-state independence is asserted but not exercised through a transaction.
- **Minimum correction:** Model unique delivery events and ordered attempts with deterministic time advancement; preserve committed business state, schedule 1/5/30 retries, enqueue only after final failure, expose attempt inspection, and apply idempotency keys to automatic and manual resend side effects.

#### A-CODEX-DRIFT-007 — Stale no-op, destructive atomicity/reason rules, and authority-loss revocation are not wired into application state

- **Implementation evidence:** `app.js:10` routes the `authority` scenario to a status message without changing `role`, session, screen access, or subsequent authorization. Conflict/expiry/delivery scenarios also only choose message text (`app.js:7,10`). `app.js:5` uses an ad hoc destructive list; actions such as `release_legal_hold`, `deactivate_resource`, and `release_resource_block` never receive the confirmation path, while `app.js:10-12` applies only a generic `{reason}` result and changes no business/occupancy state. The stale/idempotency helpers in `domain.js:26-30,39` are never invoked by the browser.
- **Canonical authority:** Permission loss immediately revokes the operator session; all mutations use optimistic versions and stale requests return latest state without mutation; destructive operations require canonical reason/confirmation; cancellation/resource release and booking occupancy swaps are atomic (`CODEX_IMPLEMENTATION_HANDOFF.md:45`, `:105-112`, `:116-121`, `:141-143`).
- **Observed impact:** The named scenarios do not prove their claimed semantics. After an authority-loss message the same operator context remains selected, stale requests cannot occur, retries cannot replay an original result, and a confirmed destructive click does not cancel/release/deactivate anything atomically.
- **Minimum correction:** Route every mutation through versioned, idempotent commands returning latest state on stale input. Implement action-specific reason/confirmation requirements and atomic state transitions. Authority loss must clear the active operator session immediately and prevent further privileged navigation/mutation until a fresh authorized sign-in.

#### A-CODEX-DRIFT-008 — Required accessible, Korean, focus-managed interaction semantics are incomplete

- **Implementation evidence:** Action buttons expose raw English snake-case IDs as their only visible/accessibility label and the screen meta exposes `Customer`, `Staff`, `Owner`, or `Shared` (`app.js:6,8`), despite a Korean-only product. Every screen gets the same reason textarea, and validation only writes a live status; it never sets `aria-invalid` or links the error to the field (`app.js:8-12`). Screen navigation replaces the focused navigation DOM and the main content but never moves focus to `#content` or the new heading (`app.js:8`). Scenario selection re-renders without marking the current scenario option selected, so the displayed value resets to `normal` while internal state can remain non-normal (`app.js:8`).
- **Canonical authority:** The implementation must be Korean-only and provide complete labels, error-field association, keyboard operation, visible focus, and live status (`CODEX_IMPLEMENTATION_HANDOFF.md:30-32`, `:127-132`).
- **Observed impact:** Korean users and screen-reader/keyboard users receive implementation identifiers instead of localized actions, field errors are not programmatically attached to the failing input, focus can be lost after navigation, and scenario UI can display a value different from the active state.
- **Minimum correction:** Give every action a Korean user-facing label while retaining stable IDs in `data-action`; localize role/access labels; render only action-specific fields; set/clear `aria-invalid` and error descriptions; move focus to the new screen heading/main after navigation; preserve selected control values; add keyboard/focus/browser tests.

#### A-CODEX-DRIFT-009 — Passing tests materially overstate coverage and do not test the required browser behaviors

- **Implementation evidence:** `source-contract.test.mjs:9-17` asserts only regex presence of `<main>`, `<nav>`, `aria-live`, `<dialog`, `data-*`, media queries, focus CSS, and a disclaimer. It never renders or operates the SPA. `catalog.test.mjs:42-48` checks one Owner screen exclusion but not action-level authorization. `domain.test.mjs:12-62` does not exercise actual occupancy calculation from state, hours/exceptions, policy versions/consents, management tokens/sessions/drafts, delivery attempts/retries, assisted holds, late proposals, resource conflicts, operator security, lifecycle, incidents, or attendance. Several test titles claim buffers, frozen snapshots, neutral links, and delivery behavior more broadly than their assertions establish (`domain.test.mjs:12,38,47`; implementation report `:46-55,78-81`). The reported red phase is missing-module/ENOENT evidence only (`codex-implementation-report.md:7-28`).
- **Canonical authority:** Unit/contract tests must cover booking, permission, version, idempotency, and inventory invariants, and final evidence must include real browser readback at desktop/375px and reduced motion (`CODEX_IMPLEMENTATION_HANDOFF.md:146-152`).
- **Observed impact:** `npm test` passes while all blocking/major defects above remain. The suite verifies token presence and narrow helpers, not the acceptance behavior or user journeys it names; the current TDD record establishes test-before-file sequencing but not behavior-level red/green coverage.
- **Minimum correction:** Add behavior-first tests for every required observable scenario and authorization edge, including negative preservation/atomicity assertions and action-level browser interactions. Add real DOM/browser checks for forms, focus, errors, 320/375 reflow, and reduced motion. Record behavior-specific failing evidence before each correction and green evidence after it.

### MINOR

#### A-CODEX-DRIFT-010 — The generated implementation is not pinned to the approved digest

- **Implementation evidence:** `README.md:3` and `codex-implementation-report.md:5` mention revision 62, but the approved digest is absent from implementation source/README/package and the implementation report; the focused search returned `NO_IMPLEMENTATION_DIGEST_PIN`.
- **Canonical authority:** The binding authority is exact revision 62 and digest `8ebb472aa66a5b680961e102db950214cea2d0be3b644164f23712030b9d8a7c` (`state.json:6-10`; `CODEX_IMPLEMENTATION_HANDOFF.md:5-18`).
- **Observed impact:** The artifact cannot self-identify the precise approved state it claims to implement, weakening stale-authority detection. The exact registry comparison found no screen/action drift, and no prohibited payment/account/calendar feature was found; the noncanonical `Shared` authority invention is covered separately in A-CODEX-DRIFT-002.
- **Minimum correction:** Add one tested implementation metadata constant/readback containing product slug, CLOSED revision 62, and the exact approved digest, and report it in README/server evidence without turning it into a production route contract.

## Environmental / visual UNVERIFIED (not code-defect findings)

- Fresh direct HTTP readback on an initially free port 4173 served this implementation (`<title>스튜디오 예약 운영</title>`) and its domain module, and a missing path returned 404. Thus the implementation report's prior native-browser observation of unrelated `몽글팜 — 과일 합체 게임` content (`codex-implementation-report.md:83-92`) was not reproduced at the server/readback layer and is not evidence of a source/server defect in this audit.
- A trustworthy native-browser render of this exact artifact at desktop, 375px, and 320px, including horizontal overflow, focus sequence, dialog focus restoration, contrast, and reduced-motion behavior, remains **UNVERIFIED**. Responsive/focus/reduced-motion source hooks are present, but source presence is not visual acceptance. The prior browser-target mismatch must be resolved by binding visual verification to the confirmed audit-owned listener/artifact identity.

## Counts and initial verdict

- BLOCKING: 1
- MAJOR: 8
- MINOR: 1
- Environmental/visual UNVERIFIED: 2 (not counted as code findings)

**Initial verdict: FAIL — CURRENT BLOCKING/MAJOR FOUND**
