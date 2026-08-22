# Replication A Codex Correction Pass 1 — Scoped Re-audit

## Boundary and method

This re-audit is limited to initial BLOCKING/MAJOR findings `A-CODEX-DRIFT-001` through `A-CODEX-DRIFT-009`, the pass-1 correction report, the updated implementation report, and current implementation source/tests. I did not inspect excluded historical Make, Replication B, Figma audit/generation, aggregate, or unrelated files. `A-CODEX-DRIFT-010` is intentionally not triaged. Native visual verification remains environmental pending.

Fresh checks:

- `npm test` from `codex-implementation`: exit `0`, 11 tests / 11 pass / 0 fail.
- Focused domain probe: exit `0`; `staffCanAcceptInvite=false`, `staffCanViewInquiry=false`, `customerWithoutReservationContext=true`, `outsideHoursAccepted=true`, `saveAtExpiredSession="SESSION_EXPIRED"`, `restoreWithExpiredSameSession=true`; the stored consent snapshot was only five type/version pairs.
- Idempotency replay probe after a successful booking then cancellation: exit `0`; current state was `cancelled` at version 8, but replay returned `confirmed` at version 7.
- Missing-delivery resend probe: exit `1` with `TypeError: fail is not a function`.
- Static server: initially no listener; root/domain/missing readback exited `0` with `{"Root":200,"Title":true,"Domain":200,"Stateful":true,"Missing":404}`. The audit-owned listener was interrupted and final listener check exited `0` with `LISTENER_STOPPED`.

## Initial finding adjudication

### A-CODEX-DRIFT-001 — BLOCKING — NOT ADDRESSED

`src/app.js:4` now holds deterministic state, and `src/app.js:13` has specific branches for booking confirmation, management-link request/use, policy publish/withdraw, delivery creation/resend, and cancellation. However, every other canonical action still falls through to the final generic `status(...)` sentence at `src/app.js:13`; it neither invokes a domain transition nor changes screen-specific state. `src/app.js:9` still renders one largely generic panel/readback, with no substantive hours/exceptions, resources, security/accounts, legal hold, late proposal/consent, inquiry, assisted hold, equipment outage/block, deletion/lifecycle, incident, or attendance journey. The correction adds useful stateful slices but does not satisfy the initial finding's minimum Customer/Staff/Owner workflow boundary. The blocking finding remains open.

### A-CODEX-DRIFT-002 — MAJOR — NOT ADDRESSED

The visible `Shared` label is removed (`src/catalog.js:2-3`) and `authorizeAction` is now deny-by-default (`src/domain.js:11-14`), closing important portions of the finding. The action matrix and context binding remain incorrect: Staff is denied its own invite acceptance/password/TOTP/recovery-code onboarding and `view_booking_inquiry_thread`, because those actions are Owner-only or Customer-only (`src/domain.js:11-13`); the fresh probe returned `staffCanAcceptInvite=false` and `staffCanViewInquiry=false`. Conversely, customer authorization accepts a missing context because it checks only `context.reservationId !== false` (`src/domain.js:14`); the probe returned `customerWithoutReservationContext=true`, and the SPA passes a hard-coded `R-001` rather than a management-session/reservation binding (`src/app.js:9,13`). Action-level authority is therefore still materially wrong.

### A-CODEX-DRIFT-003 — MAJOR — NOT ADDRESSED

Positive-integer attendees/quantities, room/equipment buffered occupancy, aggregate equipment quantity, room blocks, preserved state/input, alternatives, and version checks are now implemented (`src/domain.js:20-23`) and tested (`tests/correction.test.mjs:14-22`). But `validate` never reads the room's `open`/`close` values from `createPrototypeState` (`src/domain.js:16,21`), so the focused probe confirmed a 04:00–06:00 booking while configured hours were 09:00–18:00 (`outsideHoursAccepted=true`). It also lacks equipment/whole-studio block or outage state and assisted holds, and the browser silently publishes all missing policies before customer confirmation (`src/app.js:13`) instead of exposing the complete commit guard. The required atomic recheck is still incomplete, so the finding remains open.

### A-CODEX-DRIFT-004 — MAJOR — NOT ADDRESSED

Deep-frozen component snapshots, five current policy types, exact current-version matching, withdrawal without revival, and a computed change delta now exist (`src/domain.js:1-3,17,19,22-25`); those are substantive corrections. The booking consent snapshot remains only `{type: version}` with no document ID or consent timestamp (`src/domain.js:22`; focused probe output), and `changeBookingState` computes `previousSnapshot`/`delta` only in the returned committed booking rather than providing a pre-commit old/new/delta review (`src/domain.js:23`). The SPA has no specific `confirm_booking_change` path and auto-publishes missing versions as Owner during customer confirmation (`src/app.js:13`), making the canonical missing-policy failure unobservable and improperly bypassed. The initial major finding is only partially corrected.

### A-CODEX-DRIFT-005 — MAJOR — NOT ADDRESSED

Neutral public output, known-only token mutation, 60-second/five-hour limiting, older-token revocation, 15-minute one-time tokens, and 30-minute sessions are implemented (`src/domain.js:26-27`). Draft lifecycle is still inverted at the critical boundary: `saveDraft` rejects an expired session (`src/domain.js:28`), although the canonical flow retains the latest change/inquiry draft when the management session expires; `restoreDraft` accepts the same old session without requiring a new reauthenticated session (`src/domain.js:29`). The probe returned `saveAtExpiredSession="SESSION_EXPIRED"` and `restoreWithExpiredSameSession=true`. There is no restore/discard/success/expiry deletion transition, and the SPA never calls `saveDraft` or `restoreDraft` (`src/app.js:2,13`). The finding remains open.

### A-CODEX-DRIFT-006 — MAJOR — ADDRESSED

Unique delivery records now contain the initial attempt, deterministic 1/5/30-minute retry progression, final-failure queueing, success suppression, business-state-preserving state copies, and idempotent manual resend (`src/domain.js:30-32`). The test exercises four attempts, final queue state, and duplicate-resend suppression (`tests/correction.test.mjs:49-56`), while SCR-023 exposes attempt/queue counts and actions (`src/app.js:9,13`). These changes satisfy the minimum correction for the initial absence. A newly introduced missing-record crash is tracked separately as `A-CODEX-DRIFT-011`; it does not reopen the already-corrected normal delivery lifecycle finding.

### A-CODEX-DRIFT-007 — MAJOR — NOT ADDRESSED

Stale/version helpers and atomic cancellation with reason/confirmation parameters now exist (`src/domain.js:22-24,33`), but the browser does not present confirmation: `confirmationMarkup` is an unused string (`src/app.js:5`) and cancellation hard-codes `confirmed:true` directly from the action click (`src/app.js:13`). Authority loss merely changes the UI role to Customer (`src/app.js:9`); `state.operatorSession` is never activated or revoked (`src/domain.js:16`; `src/app.js:4,9,13`). Idempotency is unsafe across subsequent state: after confirmation then cancellation, replaying the original booking key returned the earlier confirmed version 7, replacing the current cancelled version 8. This occurs because stored results include their old whole-state result and `confirmBooking` returns it before current-version handling (`src/domain.js:22`). Thus destructive confirmation, genuine session revocation, and no-rollback idempotent replay remain unresolved.

### A-CODEX-DRIFT-008 — MAJOR — NOT ADDRESSED

Role labels are localized, navigation moves focus to the new heading, booking/email fields have labels, and one error path applies `aria-invalid` (`src/app.js:6-12`). But only 14 of 78 actions have distinct Korean labels; all other actions render as repeated `이 작업 실행` buttons (`src/app.js:6-9`), so their purpose is not discoverable to sighted or assistive-technology users. `error()` always associates the error with attendees, email, or reason rather than the actual failing start/end/quantity/policy field (`src/app.js:12`). On SCR-019 there is a reason field but no `#field-error`; a policy failure therefore dereferences `null.textContent` (`src/app.js:9,12-13`). Action-specific fields and meaningful accessible labels remain broadly absent. The source improvements do not close the finding; native 320/375 visual behavior remains environmental pending rather than adjudicated here.

### A-CODEX-DRIFT-009 — MAJOR — NOT ADDRESSED

The correction suite adds valuable domain assertions for booking conflicts, deep freezing/policies, links/drafts, delivery, stale state, and cancellation (`tests/correction.test.mjs:14-64`). It still has no rendered SPA/browser interaction test. The test named for “authority loss” contains no authority-loss assertion (`tests/correction.test.mjs:58-64`), and source-contract coverage remains regex token presence only (`tests/source-contract.test.mjs:9-17`). Tests do not catch the unused dialog, generic/unlabeled action fallthrough, missing hours guard, invalid draft reauthentication, idempotency rollback, missing-delivery crash, or policy-screen error crash. The reported red was a single missing export (`codex-correction-pass-1.md:3`), not behavior-specific red evidence for the claimed UI corrections. Passing 11/11 therefore still materially overstates the required behavior/browser coverage.

## New correction breakage

### A-CODEX-DRIFT-011 — MAJOR — NEW

`resendDelivery` names its Boolean outcome parameter `fail`, shadowing the module's `fail(...)` result helper; its missing-record branch therefore calls a Boolean as a function (`src/domain.js:4,32`). The fresh probe exited nonzero with `TypeError: fail is not a function`. SCR-023 enables `resend_failed_delivery` before any delivery exists and calls this path without a catch (`src/app.js:9,13`), so a normal user sequence can crash the action handler instead of returning a deterministic `DELIVERY` guard. Rename the Boolean parameter, return the standard failure object for a missing record, preserve state, and add a negative UI/domain regression test.

## Environmental visual status

Fresh HTTP readback confirms the corrected implementation is served at the expected root and module URLs with 200/200 and a missing-path 404. Native rendering at desktop/375/320, reduced motion, contrast, and overflow remains **UNVERIFIED** and is not counted as a code finding in this scoped pass.

## Counts and scoped verdict

- Initial findings addressed: 1 (`A-CODEX-DRIFT-006`)
- Initial findings still open: 8 (`A-CODEX-DRIFT-001`, `002`, `003`, `004`, `005`, `007`, `008`, `009`)
- Open initial severity: BLOCKING 1, MAJOR 7
- New BLOCKING/MAJOR: 1 MAJOR (`A-CODEX-DRIFT-011`)

**Scoped verdict: FAIL — PASS 1 LEAVES CURRENT BLOCKING/MAJOR FINDINGS**
