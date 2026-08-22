# Codex correction pass 1

Behavior-first red: `node --test tests/correction.test.mjs` exited `1` before correction production code because `src/domain.js` did not export `POLICY_TYPES`.

Green: `npm test` exited `0`: 11 pass, 0 fail. Fresh static readback exited `0`: `{"Root":200,"Title":true,"Domain":200,"Stateful":true,"Missing":404}`; the disposable listener was stopped.

| Finding | Correction |
| --- | --- |
| A-CODEX-DRIFT-001 | Deterministic in-memory resources, bookings, policies, management state, deliveries, versions, and idempotency; SPA calls booking, policy, link, delivery, and cancellation transitions. |
| A-CODEX-DRIFT-002 | Explicit deny-by-default `authorizeAction`; no user-visible `Shared` authority. |
| A-CODEX-DRIFT-003 | Derived room/equipment/buffer/block conflicts, positive integers, preserved state/input, alternatives. |
| A-CODEX-DRIFT-004 | Deep-frozen snapshots, five versioned policy records/consents, no withdrawal revival. |
| A-CODEX-DRIFT-005 | Neutral known-only link mutation, one-time token/session and two-hour draft. |
| A-CODEX-DRIFT-006 | Initial plus 1/5/30 attempts, final queue, idempotent resend. |
| A-CODEX-DRIFT-007 | Stale no-op/latest state, reason/confirmation and atomic cancellation/release; authority-loss UI reset. |
| A-CODEX-DRIFT-008 | Korean labels, action fields/errors, focus change, preserved selects. |
| A-CODEX-DRIFT-009 | Behavior-level correction tests for all above transitions. |

The minor A-CODEX-DRIFT-010 was intentionally untouched. Native-browser 320/375 visual verification remains unverified.
