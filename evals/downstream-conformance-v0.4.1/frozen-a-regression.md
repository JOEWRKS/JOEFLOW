# Frozen Replication A Regression

## Source

- commit: `9408434e640b9cf0bf6afaadd8f9d1f5f52e8943`
- implementation tree: `189d9f969d046ecf905680e090f65f15114aeeb4`
- adapter: `frozen-a-node-public-ui@1.0.0`
- evaluator contract version: `joewrks.downstream.regression-slice/1.0`
- executable slice: `3dc4aa1ff025e0b1c36d5470f226d46e8280d496e183fdd05da3790e1026639a`
- semantic authority: MACHINE_DERIVED `0`, REVIEW_REQUIRED `4`, production handoff `no`

## Executed sequence

`SEQ-A-UI-DOMAIN / A-PUBLIC-CONFIRM-BOOKING` loaded the actual `app.js` in Node with an external minimal DOM boundary and invoked the `confirm_booking` public click handler. The actual handler called `executeAction`; no frozen source was patched.

Observed:

- public result: `committed / PUBLIC_SUCCESS`;
- visible status: `confirm_booking 기록이 생성되었습니다.`;
- visible state revision: `1 -> 2`;
- bookings: `0 -> 0`;
- trace: public invocation → `handle` → `executeAction` → rendered readback.

Canonical `REQ-001`, `RULE-001`, `STATE-001`, `AC-001`, and `AC-002` require final confirmation to atomically create the booking when selected resources are available. The core required authoritative domain change and found none.

## Verdict

**DETECTED — A_UI_DOMAIN_DISCONNECT.**

The implementation's own green helper/source tests are not accepted because the executed public path reached the generic audit-only fallback instead of the canonical booking mutation.
