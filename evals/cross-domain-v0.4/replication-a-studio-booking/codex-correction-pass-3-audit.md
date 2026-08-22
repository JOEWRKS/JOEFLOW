# Replication A Codex Correction Pass 3 — Final Scoped Re-audit

## Boundary and fresh evidence

This final re-audit is limited to the eight findings open after pass 2 (`A-CODEX-DRIFT-001`, `002`, `003`, `004`, `005`, `007`, `008`, `009`), regression checks for closed `006` and `011`, the pass-3 correction report, updated implementation report, and current A implementation source/tests. Excluded historical Make, Replication B, Figma audit/generation, aggregate, and unrelated files were not read. Minor `010` and native visual verification were not triaged. This is the terminal audit at the authorized three-pass cap.

Fresh checks:

- `npm test`: exit `0`, 14 tests / 14 pass / 0 fail.
- Focused action/UI-domain probe: exit `0`; `confirm_booking` returned success but left `bookings=0` and only appended audit; `request_management_link` left `tokens=0`; `view_failed_deliveries` left `deliveries=0`; `staffCanAcceptInvite=false`; `staffCanViewInquiry=false`; `prebookingCancelAuthorized=true`; `outsideHoursAccepted=true`; `saveAtExpiredSession="SESSION_EXPIRED"`; `restoreWithExpiredSameSession=true`; missing resend returned `DELIVERY`.
- Booking-idempotency replay after cancellation: exit `0`; current state was `cancelled` version 8 but replay returned `confirmed` version 7.
- `SCREEN_SCHEMAS` use search found only the import at `src/app.js:3`; the schemas are not rendered or consumed.
- Static-server readback: initially no listener; root/UI-contract/missing returned `200/200/404`; cleanup ended with `LISTENER_STOPPED`.

## Open-finding adjudication

### A-CODEX-DRIFT-001 — BLOCKING — NOT ADDRESSED

The SPA now imports and calls `executeAction` for every click (`src/app.js:2,14`), but pass 3 removed all previously specific browser branches for booking, management links, policy, delivery, and cancellation. `executeAction` has specific state transitions only for resource creation, room block, equipment outage, and operator sign-in (`src/domain.js:46-49`); every other allowed action, including `confirm_booking`, `request_management_link`, policy operations, inquiries, lifecycle, incidents, and attendance, merely appends a generic audit row (`src/domain.js:50-51`). Fresh probes showed a successful UI-equivalent booking with zero bookings and a link request with zero tokens. The browser therefore remains—and is now more uniformly—a generic action recorder rather than substantive Customer/Staff/Owner journeys. The blocking finding remains open.

### A-CODEX-DRIFT-002 — MAJOR — NOT ADDRESSED

Authorization is unchanged (`src/domain.js:11-14`). Staff is still denied its own invite/password/TOTP/recovery onboarding and inquiry-thread viewing; fresh probes returned `staffCanAcceptInvite=false` and `staffCanViewInquiry=false`. Customer authority accepts any nonempty reservation string rather than a reservation bound to a valid management session. The SPA explicitly supplies `prebooking` whenever no session exists (`src/app.js:14`), so a pre-authenticated customer is authorized for cancellation and other reservation mutations (`prebookingCancelAuthorized=true`). Action/context authorization remains materially incorrect.

### A-CODEX-DRIFT-003 — MAJOR — NOT ADDRESSED

The booking validator is unchanged (`src/domain.js:16,20-23`). It still ignores room `open`/`close` and equipment `outage`; the focused probe again accepted a 04:00–06:00 booking against 09:00–18:00 hours. Assisted holds and complete equipment/whole-studio block semantics remain absent. More critically, the SPA no longer calls `confirmBooking` at all: `confirm_booking` is routed to generic audit (`src/app.js:14`; `src/domain.js:51`), so no booking/occupancy/alternative behavior is observable. The atomic availability finding remains open.

### A-CODEX-DRIFT-004 — MAJOR — NOT ADDRESSED

Price/policy domain code was not corrected (`src/domain.js:17,19,22-25`). Consent snapshots still omit document ID and consent timestamp, change delta still exists only after commit rather than pre-commit review, and no browser path displays old/new/delta. Pass 3 routes `publish_policy_version`, `withdraw_policy_version`, `confirm_booking`, and `confirm_booking_change` through generic `executeAction`; policy publish/withdraw therefore no longer invokes `managePolicy` in the browser (`src/app.js:14`; `src/domain.js:50-51`). Deep-freeze/current-version unit behavior remains, but the required price/policy experience and semantics stay open.

### A-CODEX-DRIFT-005 — MAJOR — NOT ADDRESSED

Management-link and draft functions are unchanged (`src/domain.js:26-29`). Expiry capture is still rejected and restore still accepts the old expired session, as confirmed by `SESSION_EXPIRED` on save and success through the same expired session. There are still no discard/success/expiry deletion transitions. Pass 3 also removed browser invocation of link issue/use; `request_management_link` now appends audit and produced zero tokens in the focused probe (`src/app.js:14`; `src/domain.js:51`). The finding remains open.

### A-CODEX-DRIFT-007 — MAJOR — NOT ADDRESSED

The dialog remains an unused string (`src/app.js:6`). The SPA always sends `confirmed:false` to `executeAction` and provides no confirmation continuation (`src/app.js:14`); listed destructive actions can only return `CONFIRMATION_REQUIRED`, while unlisted destructive/mutation actions such as cancellation fall through to generic audit (`src/domain.js:50-51`). Authority loss still changes only the UI role and does not revoke `state.operatorSession` (`src/app.js:5,10`). Safe idempotency is unchanged: replay after cancellation still returns the prior confirmed state/version (`src/domain.js:22`). Destructive reason/confirmation/atomicity, real session revocation, stale UI behavior, and replay safety remain open.

### A-CODEX-DRIFT-008 — MAJOR — NOT ADDRESSED

Pass 3 materially improves action names: `ACTION_LABELS` produces 78 distinct labels and the SPA uses them (`src/ui-contract.js:1-3`; `src/app.js:3,8,10`; `tests/pass3.test.mjs:1-5`). The rest of the finding remains. `SCREEN_SCHEMAS` assigns a generic reason field to almost every screen and is never used beyond import (`src/ui-contract.js:4`; `src/app.js:3`). The rendered UI still has specific fields only for four screens (`src/app.js:9-10`), and `error()` still attaches every error to the first attendees/email/reason field and can dereference missing `#field-error` on SCR-019 (`src/app.js:13`). Complete action-specific labels/fields/error association is therefore not achieved. Native viewport rendering remains separately unverified.

### A-CODEX-DRIFT-009 — MAJOR — NOT ADDRESSED

The new test checks only the count and uniqueness of generated labels and the count of schema objects (`tests/pass3.test.mjs:1-5`). It does not assert label quality, schema correctness, schema usage, rendered controls, action behavior, focus/errors, or any canonical transition. Existing tests still invoke domain helpers directly and never detect that pass 3 disconnected booking, links, policies, cancellation, and delivery from the SPA. Source-contract coverage remains regex presence. Fourteen passing tests continue to materially overstate end-to-end behavior and browser coverage.

## Closed-finding regression checks

### A-CODEX-DRIFT-006 — MAJOR — REGRESSED / NOT ADDRESSED

The isolated delivery model and unit test still implement initial plus 1/5/30 attempts, final queueing, and idempotent resend (`src/domain.js:30-32`; `tests/correction.test.mjs:49-56`). However, pass 3 replaced the browser's working delivery branches with generic `executeAction` dispatch (`src/app.js:14`). `view_failed_deliveries`, `inspect_delivery_attempts`, and `resend_failed_delivery` now append audit only (`src/domain.js:51`); the focused probe showed `view_failed_deliveries` left `deliveries=0`. The required observable delivery scenario has regressed, so `006` cannot remain closed.

### A-CODEX-DRIFT-011 — MAJOR — REMAINS ADDRESSED/CLOSED

`resendDelivery` still uses `shouldFail` and returns unchanged-state `DELIVERY` for a missing record (`src/domain.js:32`); the focused probe returned that guard without a crash and the negative regression test still passes (`tests/pass2.test.mjs:10-15`). The original Boolean-shadow crash remains closed. The unwired resend lifecycle is accounted for by regressed `006`, not a recurrence of `011`.

## New pass-3 BLOCKING/MAJOR IDs

None. Pass 3's generic-dispatch regression is adjudicated under still-open `001` and reopened `006`; it does not require a duplicative new finding ID.

## Final counts and verdict at the three-pass cap

- Addressed among the eight findings open entering pass 3: 0
- Still open from that set: 8 (`A-CODEX-DRIFT-001`, `002`, `003`, `004`, `005`, `007`, `008`, `009`)
- Regressed/reopened: 1 MAJOR (`A-CODEX-DRIFT-006`)
- Remains closed: `A-CODEX-DRIFT-011`
- Final current open severity: BLOCKING 1 (`001`), MAJOR 8 (`002`, `003`, `004`, `005`, `006`, `007`, `008`, `009`)
- New IDs: none

**Final scoped verdict: FAIL — THREE-PASS CAP REACHED WITH CURRENT BLOCKING/MAJOR FINDINGS**
