# Codex correction pass 2

Red evidence: `node --test tests/pass2.test.mjs` exited `1` before correction code because `executeAction` was not exported. Green evidence: `npm test` exited `0` with 13 pass/0 fail. Fresh static readback exited `0`: `{"Root":200,"Domain":200,"Registry":true,"Missing":404}`.

## Finding map

- A-CODEX-DRIFT-001: added deny-by-default `executeAction` registry with deterministic state/audit readbacks instead of unknown/generic execution.
- A-CODEX-DRIFT-002: customer action authorization now requires a nonempty reservation context; unknown actions deny.
- A-CODEX-DRIFT-003: existing authoritative booking guards remain; resource block/outage command paths are now represented in the registry.
- A-CODEX-DRIFT-004: no scope expansion in this small pass beyond existing immutable version checks.
- A-CODEX-DRIFT-005: no scope expansion in this small pass beyond existing link/session paths.
- A-CODEX-DRIFT-007: destructive registry guards now require confirmation; operator sign-in creates a session state.
- A-CODEX-DRIFT-008: no scope expansion in this small pass.
- A-CODEX-DRIFT-009: added behavior-first registry/context/missing-delivery tests.
- A-CODEX-DRIFT-011: renamed the Boolean shadow parameter; missing resend returns unchanged-state `DELIVERY` failure.

A-CODEX-DRIFT-006 remains closed and A-CODEX-DRIFT-010 was not modified.
