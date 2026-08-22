# Replication A Codex Correction Pass 2 — Scoped Re-audit

## Boundary and fresh evidence

This pass is limited to the nine current findings `A-CODEX-DRIFT-001`, `002`, `003`, `004`, `005`, `007`, `008`, `009`, and `011`, plus regression-checking closed `006`. I read only the pass-1 audit, pass-2 correction report, updated implementation report, and current implementation source/tests. Excluded historical Make, Replication B, Figma audit/generation, aggregate, and unrelated files were not read. `A-CODEX-DRIFT-010` and native visual verification were not triaged.

Fresh checks:

- `npm test`: exit `0`, 13 tests / 13 pass / 0 fail.
- Application wiring search for `executeAction`: expected no-match normalized to exit `0`, output `APP_DOES_NOT_USE_EXECUTE_ACTION`.
- Focused domain probe: exit `0`; `staffCanAcceptInvite=false`, `staffCanViewInquiry=false`, `customerArbitraryReservation=true`, `outsideHoursAccepted=true`, `saveAtExpiredSession="SESSION_EXPIRED"`, `restoreWithExpiredSameSession=true`, `missingResendCode="DELIVERY"`, `missingResendSameState=true`, `legalHoldWithoutReasonAccepted=true`, `legalHoldStateOnlyAudit=true`.
- Booking-idempotency replay after cancellation: exit `0`; current was `cancelled` version 8 but replay returned `confirmed` version 7.
- Static-server readback: initially no listener; root/domain/missing returned `200/200/404`, and domain readback contained `executeAction`. Audit listener cleanup ended with `LISTENER_STOPPED`.

## Finding adjudication

### A-CODEX-DRIFT-001 — BLOCKING — NOT ADDRESSED

Pass 2 adds a deny-by-default `executeAction` registry (`src/domain.js:43-51`), but the SPA neither imports nor calls it (`src/app.js:1-14`; fresh search `APP_DOES_NOT_USE_EXECUTE_ACTION`). The browser still has specific paths only for booking, management-link issue/use, policy publish/withdraw, delivery, and cancellation; all other actions fall through to a generic status sentence without state change (`src/app.js:13`). Even within `executeAction`, only resource creation, room block, equipment outage, and operator sign-in have specific transitions (`src/domain.js:46-49`); all remaining allowed actions merely append a generic audit record (`:50-51`). Hours/exceptions, account security, legal hold, late consent, inquiry, assisted hold, conflict disposition, deletion/lifecycle, incidents, and attendance are still not substantive stateful journeys. The primary blocking finding remains open.

### A-CODEX-DRIFT-002 — MAJOR — NOT ADDRESSED

The stricter nonempty-string context check closes authorization with no context (`src/domain.js:14`; `tests/pass2.test.mjs:10-14`), but it does not bind the supplied reservation to an authenticated management session; the focused probe accepted arbitrary `reservationId:'ANY'`, and the SPA always supplies hard-coded `R-001` (`src/app.js:9,13`). The action matrix is unchanged: Staff remains denied its own invite/password/TOTP/recovery onboarding and `view_booking_inquiry_thread` (`src/domain.js:11-13`), confirmed by `staffCanAcceptInvite=false` and `staffCanViewInquiry=false`. The correction is partial, so the finding stays open.

### A-CODEX-DRIFT-003 — MAJOR — NOT ADDRESSED

The booking validator is unchanged (`src/domain.js:16,20-23`). It still never checks room `open`/`close`; a 04:00–06:00 booking was accepted against 09:00–18:00 configured hours. Pass-2 `create_resource_block` and `mark_equipment_unavailable` merely add state (`src/domain.js:47-48`): `validate` only considers room blocks and never reads equipment `outage`, so an unavailable camera remains bookable (`src/domain.js:21`). Assisted holds and complete block/outage conflict semantics are absent, and the SPA still auto-publishes missing policies during confirmation (`src/app.js:13`). The atomic availability/guard finding remains open.

### A-CODEX-DRIFT-004 — MAJOR — NOT ADDRESSED

No relevant correction was made. Deep freezing and current-version checks remain strengths, but booking consents are still stored only as type/version pairs without document ID or consent timestamp (`src/domain.js:22`), the change delta exists only after commit rather than as a pre-commit review (`src/domain.js:23`), and `confirm_booking_change` still has no specific browser path (`src/app.js:13`). Customer confirmation still silently publishes missing policy versions as Owner (`src/app.js:13`), preventing the required missing-policy block from being observed. The finding remains open.

### A-CODEX-DRIFT-005 — MAJOR — NOT ADDRESSED

No relevant correction was made. `saveDraft` still requires an active, unexpired old session (`src/domain.js:28`) and therefore rejects the canonical session-expiry capture path; `restoreDraft` still accepts the same expired old session without new reauthentication (`src/domain.js:29`). Fresh outputs remained `saveAtExpiredSession="SESSION_EXPIRED"` and `restoreWithExpiredSameSession=true`. Restore/discard/success/expiry deletion is absent and the SPA does not invoke draft functions (`src/app.js:2,13`). The finding remains open.

### A-CODEX-DRIFT-007 — MAJOR — NOT ADDRESSED

`executeAction` adds confirmation checks for six destructive identifiers and operator sign-in state (`src/domain.js:49-50`), but is not wired to the SPA. The browser still keeps an unused dialog string (`src/app.js:5`) and hard-codes `confirmed:true` on a single click (`src/app.js:13`). Authority loss still changes only the UI role, not `state.operatorSession` (`src/app.js:4,9`; `src/domain.js:16`). Generic `executeAction` accepts `set_legal_hold` without reason and only appends audit, as confirmed by `legalHoldWithoutReasonAccepted=true` and `legalHoldStateOnlyAudit=true`. Booking idempotency also still rolls current state backward: retry after cancellation returned confirmed version 7 instead of preserving cancelled version 8 (`src/domain.js:22`). Destructive confirmation, reason/atomic transition, session revocation, and safe replay remain open.

### A-CODEX-DRIFT-008 — MAJOR — NOT ADDRESSED

No relevant UI correction was made (`src/app.js:6-13`). Sixty-four actions still share the same `이 작업 실행` label, field errors still attach to the first attendees/email/reason field rather than the failing field, and SCR-019 still lacks `#field-error` although `error()` unconditionally dereferences it when a reason field exists (`src/app.js:9,12-13`). The new registry is not exposed through localized, action-specific controls or readbacks. Existing focus and semantic improvements do not close the accessible-label/error-association finding. Native viewport rendering remains separately unverified.

### A-CODEX-DRIFT-009 — MAJOR — NOT ADDRESSED

Pass 2 adds two behavior tests, but their scope is much narrower than their titles: the “records every canonical action” test exercises only unknown denial and `create_resource` (`tests/pass2.test.mjs:5-9`), while the second checks only empty customer context and missing delivery (`:10-15`). There is still no rendered SPA/browser test, and source-contract tests remain regex presence checks. The suite does not detect that `executeAction` is unwired, that generic actions append audit instead of implementing semantics, or any still-open defect above. Thirteen passing tests therefore continue to overstate behavior and browser coverage.

### A-CODEX-DRIFT-011 — MAJOR — ADDRESSED

`resendDelivery` now uses `shouldFail`, no longer shadows the `fail(...)` helper, returns a standard unchanged-state `DELIVERY` failure for a missing record, and stores only replay metadata rather than an old whole-state result (`src/domain.js:32`). The focused probe returned `missingResendCode="DELIVERY"` with identical state, and `tests/pass2.test.mjs:10-15` covers the negative path. The original missing-record crash is closed.

## Closed-finding regression check

`A-CODEX-DRIFT-006` remains **ADDRESSED/CLOSED**. Delivery creation, 1/5/30 retries, final queueing, and idempotent existing-record resend remain in `src/domain.js:30-32`, and the existing four-attempt/queue/idempotency test still passes (`tests/correction.test.mjs:49-56`). Pass 2 introduced no regression in that lifecycle.

## New pass-2 BLOCKING/MAJOR breakage

None. The generic/unwired registry behavior and reason/authority gaps are continuations of open `001`, `002`, `003`, `007`, `008`, and `009`, not distinct new finding families.

## Counts and scoped verdict

- Addressed among the nine current findings: 1 (`A-CODEX-DRIFT-011`)
- Still open: 8 (`A-CODEX-DRIFT-001`, `002`, `003`, `004`, `005`, `007`, `008`, `009`)
- Exact open severity: BLOCKING 1 (`001`), MAJOR 7 (`002`, `003`, `004`, `005`, `007`, `008`, `009`)
- New BLOCKING/MAJOR IDs: none
- Previously closed `A-CODEX-DRIFT-006`: remains closed

**Scoped verdict: FAIL — PASS 2 LEAVES CURRENT BLOCKING/MAJOR FINDINGS**
