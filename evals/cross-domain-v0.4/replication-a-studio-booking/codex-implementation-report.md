# Codex implementation evidence — Replication A Studio Booking

## Correction pass 1

Behavior-first correction tests are green: `npm test` exited `0` with 11 pass/0 fail. The corrected model adds authoritative booking/policy/link/session/draft/delivery state, deny-by-default action authorization, and Korean action-specific controls. Fresh static readback returned root 200, domain 200, and missing path 404. Full mapping and red evidence: `codex-correction-pass-1.md`. A-CODEX-DRIFT-010 remains intentionally outside this pass.

## Correction pass 2

`executeAction` provides a deny-by-default deterministic command registry and `resendDelivery` now safely returns a `DELIVERY` guard for missing records. `npm test` passed 13/13 and static readback served root/domain with 200 and a missing route with 404. Evidence: `codex-correction-pass-2.md`.

## Correction pass 3

The SPA imports the action dispatcher and a tested UI contract for all 78 Korean action labels and 27 screen schemas. Final tests passed 14/14. Evidence: `codex-correction-pass-3.md`.

## Result

Implemented the dependency-free, Korean-only Studio Booking evaluation prototype from the approved revision-62 handoff. The implementation exposes all 27 `SCR-*` screens and 78 canonical actions, includes deterministic scenario feedback, and keeps external behavior explicitly simulated.

## Red evidence before production files

Command (working directory: `evals/cross-domain-v0.4/replication-a-studio-booking/codex-implementation`):

```text
node --test tests/catalog.test.mjs tests/domain.test.mjs tests/source-contract.test.mjs
```

Exit: `1`

Exact decisive output:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find module 'D:\JOEWRKS\.worktrees\joewrks-product-definition-v0.3-publish\evals\cross-domain-v0.4\replication-a-studio-booking\codex-implementation\src\catalog.js' imported from D:\JOEWRKS\.worktrees\joewrks-product-definition-v0.3-publish\evals\cross-domain-v0.4\replication-a-studio-booking\codex-implementation\tests\catalog.test.mjs
Error [ERR_MODULE_NOT_FOUND]: Cannot find module 'D:\JOEWRKS\.worktrees\joewrks-product-definition-v0.3-publish\evals\cross-domain-v0.4\replication-a-studio-booking\codex-implementation\src\domain.js' imported from D:\JOEWRKS\.worktrees\joewrks-product-definition-v0.3-publish\evals\cross-domain-v0.4\replication-a-studio-booking\codex-implementation\tests\domain.test.mjs
Error: ENOENT: no such file or directory, open 'D:\JOEWRKS\.worktrees\joewrks-product-definition-v0.3-publish\evals\cross-domain-v0.4\replication-a-studio-booking\codex-implementation\index.html'
ℹ tests 4
ℹ pass 0
ℹ fail 4
```

This failure was observed immediately after creating only the three test files; no production implementation file existed.

## Green evidence

Command:

```text
npm test
```

Exit: `0`

Output:

```text
> test
> node --test tests/*.test.mjs

✔ catalog exposes exactly 27 unique stable screen IDs and 78 canonical actions
✔ catalog maps customer, staff, owner, and shared surfaces without granting owner actions to staff
✔ booking validates 30-minute boundaries, duration, buffers, lead time, horizon, capacity, compatibility, equipment totals and policy
✔ booking permits the inclusive 90th Asia/Seoul calendar day regardless of hour
✔ failed conflict transition is atomic and stale versions are no-ops
✔ rates, snapshots and policy boundary follow frozen won and 48-hour rules
✔ management links are neutral and rate limited, delivery is independent, role checks and reason guard are explicit
✔ idempotent replay returns its original result without duplicate effects
✔ browser source has semantic landmarks, live feedback, dialog confirmation, responsive and reduced-motion support
✔ browser source states its explicit prototype boundaries
ℹ tests 10
ℹ pass 10
ℹ fail 0
ℹ duration_ms 166.2767
```

Static-server command:

```text
node server.mjs
```

The server printed `Studio Booking prototype: http://127.0.0.1:4173`. Fresh readback command exited `0` and returned:

```json
{"RootStatus":200,"RootHasMain":true,"DomainStatus":200,"DomainHasSeoulCalendar":true,"MissingStatus":404}
```

The disposable verification listener was stopped and subsequent listener check returned `listener=stopped` (exit `0`).

## Feature inventory

- `src/catalog.js` is the exact stable screen/action registry, with Customer, Staff, Owner, and shared role scopes; Owner-only actions are not granted to Staff.
- `src/domain.js` supplies explicit-result booking validation, Seoul calendar-horizon validation, 30-minute buffered occupancy, frozen integer-won snapshots, atomic conflict/stale no-ops, rate validation, 48-hour boundary, neutral management-link handling, delivery independence, reason guards, authorization, and idempotency replay.
- The SPA renders every current screen’s canonical action under `data-screen-id` and `data-action`, supports role/scenario selection, live status feedback, required-reason guards, and destructive dialog confirmation.
- HTML/CSS include landmarks, Korean labels, visible focus, 44px controls, mobile reflow, and a reduced-motion override.

## Visual verification record

Overall visual verdict: **UNVERIFIED** for the exact browser target.

| Source | Expected observable | Observed fact | Result |
| --- | --- | --- | --- |
| Approved handoff + refinement report | Semantic/operational browser UI with desktop and 320–375px reflow | Source and HTTP readback confirmed semantic HTML, responsive CSS, reduced-motion CSS, and a `<main>` landmark. | PASS (source/readback layer) |
| Approved-reference translation requirement | Render the produced browser artifact in its native target | The local browser navigated to `http://127.0.0.1:4173/` but rendered an unrelated page titled `몽글팜 — 과일 합체 게임`, with zero `data-action` controls. The direct static-server readback of the same URL returned this prototype’s HTML. | UNVERIFIED |

The discrepancy means this report does not claim visual acceptance. It does not affect the independently verified test and direct HTTP readback layers.

## Production boundaries and concerns

This is an evaluation model only: no production authentication, persistence, email provider, encryption, database concurrency, audit immutability, or Figma Make execution is claimed. The only completion concern is the browser-target mismatch above; visual acceptance requires a browser target that reaches the exact static-server artifact.
