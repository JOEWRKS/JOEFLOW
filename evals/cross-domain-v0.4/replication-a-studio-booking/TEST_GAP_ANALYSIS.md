# Replication A — Test Gap Analysis

## Frozen result

- Final implementation verdict: **FAIL — CODEX_DRIFT_UNRESOLVED**
- Final material findings: BLOCKING 1 / MAJOR 8
- Correction passes: 3/3
- Final command: `npm test`
- Final result: 14 tests / 14 pass / 0 fail
- Implementation changes made by this analysis: none

The green suite and failed verdict are consistent because the suite mostly proves inventory, direct helper behavior, and source-token presence. It does not prove that rendered user actions invoke those helpers or produce the canonical state transitions.

## What each passing test actually protects

| Passing test | What it proves | What it does not prove |
| --- | --- | --- |
| 27 screen IDs / 78 actions | Catalog identifiers and action arrays exactly match the expected inventory | That any action is usable, rendered with correct fields, authorized correctly, or connected to its domain transition |
| No Shared authority / mixed screens | Four catalog access examples and one Staff exclusion | The complete role/action/session matrix, reservation binding, or permission-loss revocation |
| Authoritative booking helper | Direct `confirmBooking()` rejects one invalid-attendee case and one overlapping booking | That the SPA calls it; operating-hours/outage/assisted-hold guards; complete screen input and recovery |
| Immutable snapshot / policy helper | Direct helper deep-freeze, current policy version, and withdrawal behavior | Document IDs, consent timestamps, pre-commit old/new/delta, or browser policy flows |
| Management link helper | Direct known/unknown issuance, token use, and one draft timing sample | SPA wiring; correct expiry capture; fresh reauthentication; discard/success/expiry deletion |
| Delivery helper | Direct initial + 1/5/30 attempts, queue, and idempotent resend | That booking/inquiry actions create delivery records or SCR-006/SCR-023 read/operate them |
| Stale/cancellation helper | Direct version guard and direct `cancelBooking()` with reason/confirmation | A reachable dialog, focus restoration, authority loss, or safe replay after later state changes |
| Rates/snapshot/48h helper | Numeric helper outputs | Rendered rate update, boundary routing, or booking/change snapshot experience |
| Reason/idempotency helper | Generic standalone helper behavior | Per-action reason requirements or current-state-safe operation replay |
| Dispatcher registry | Unknown denial and `create_resource(...).ok === true` | All 78 handlers, resulting resource shape, forms, conflicts, UI integration, or fallback semantics |
| Context/missing delivery guards | Empty Customer context denial and missing delivery error | Authenticated reservation/session binding, arbitrary IDs, or normal resend UI behavior |
| 78 labels / 27 schemas | Object counts and label uniqueness | Korean quality, schema correctness, schema consumption, fields, errors, or action outcome |
| Browser source contract | Regex presence of landmark/dialog/data attributes/media/focus CSS | DOM rendering, dialog reachability, click behavior, state mutation, focus restoration, overflow, or reduced-motion runtime behavior |
| Prototype boundary text | A disclaimer string exists | Any canonical product behavior |

## Missing protection classification

| Gap class | Applicability | Evidence |
| --- | --- | --- |
| Render-only coverage | Yes | The browser contract test reads source text with regular expressions; it does not render the SPA. |
| Handler existence without state assertion | Yes | The dispatcher test calls only `create_resource` and checks `ok=true`; no canonical resulting shape or UI state is asserted. |
| Audit-event assertion mistaken for domain-state assertion | Yes | The dispatcher returns `ok=true` for fallback actions after appending a generic audit row. The suite never distinguishes that success shell from the required booking, policy, account, inquiry, lifecycle, or attendance mutation. |
| Insufficient integration tests | Yes | No test crosses catalog → rendered button → `app.handle` → authorization → dispatcher/helper → visible/domain readback. |
| Missing end-to-end state-transition tests | Yes | None of the nine required observable scenarios is executed through the browser surface. |
| Missing permission/negative-path tests | Yes | Only a few role checks exist; Staff onboarding/thread access, arbitrary Customer reservation context, Owner-only policy/audit, authority loss, and destructive continuation are absent. |
| Fixture blindness | Yes | Happy-path helper fixtures publish policies directly and do not vary operating hours, equipment outage, assisted holds, conflicting configuration changes, expired-session capture, later state after idempotent replay, or screen-specific fields. |
| Evaluator mistake | Not the primary cause | The blind auditor identified the mismatch and preserved the initial browser-target anomaly as UNVERIFIED rather than passing it. The false confidence came from test design and implementation-report claims, not from the final evaluator count. |

## Decisive integration evidence absent from the suite

A real browser click on `confirm_booking` returned the success-like text `confirm_booking 기록이 생성되었습니다.` while the rendered state remained `bookings=[]` with no current policies. On `SCR-007`, entering a cancellation reason and activating `confirm_cancellation` found zero dialog elements and again produced only generic audit status. Both behaviors pass all 14 tests because no test renders the application, clicks these buttons, and asserts their required state transitions.

The same gap is systematic. `app.handle()` calls only `executeAction()`; richer helpers such as `confirmBooking`, `managePolicy`, `requestManagementLink`, `useManagementLink`, `cancelBooking`, `createDelivery`, and `resendDelivery` are imported but never called by the final SPA. `SCREEN_SCHEMAS` is imported but never consumed. Unit tests for those helpers therefore cannot establish UI behavior.

## Severity rationale

### Why A-CODEX-DRIFT-001 remains BLOCKING

The evaluation objective is a substantive, stateful Customer/Staff/Owner prototype. Most user-visible actions share the same generic audit-success path, so the implementation cannot demonstrate the primary booking, management, operations, failure, or recovery journeys. This defeats the artifact's intended purpose across the whole product rather than degrading one secondary edge.

### Why the eight remaining findings are MAJOR, not MINOR

| Finding | Why outcome-changing |
| --- | --- |
| `A-CODEX-DRIFT-002` | Incorrect role/session/reservation authorization can deny required Staff workflows and grant Customer mutations without authenticated reservation binding. |
| `A-CODEX-DRIFT-003` | Missing hours/outage/complete availability checks can create invalid or conflicting reservations and fails the core atomic-booking contract. |
| `A-CODEX-DRIFT-004` | Missing document identity/consent time and pre-commit price delta changes what the customer approved and what historical price/policy evidence means. |
| `A-CODEX-DRIFT-005` | Incorrect link/session/draft expiry and reauthentication semantics affect access control, privacy, and recovery of customer input. |
| `A-CODEX-DRIFT-006` | Delivery actions no longer expose attempts, queue, or resend state, preventing operational recovery and side-effect verification even though helper tests pass. |
| `A-CODEX-DRIFT-007` | Unreachable destructive confirmation, non-revoked sessions, and stale idempotent replay can authorize unsafe changes or return obsolete state after later mutations. |
| `A-CODEX-DRIFT-008` | Unconsumed schemas and missing action-specific fields/errors make most workflows undiscoverable or unusable and break required accessible interaction semantics. |
| `A-CODEX-DRIFT-009` | The evidence suite materially overstates end-to-end conformance, so it cannot guard any of the other material failures or support an independent pass decision. |

Each finding changes permissions, committed state, recovery, consent/evidence, operational handling, or the ability to execute a required workflow. None is merely cosmetic or editorial.

## Finding and correction chronology

| Point | Existing findings | Fixed/closed | New or regressed |
| --- | --- | --- | --- |
| Initial blind audit | `001` BLOCKING; `002–009` MAJOR; `010` MINOR | None | None |
| Pass 1 re-audit | `001–005,007–009` still open | `006` closed for its then-wired normal delivery lifecycle | `011` MAJOR introduced by Boolean shadowing and missing-delivery crash |
| Pass 2 re-audit | `001–005,007–009` still open | `011` fixed; `006` remained closed | No new material finding |
| Pass 3 final audit | `001–005,007–009` still open | `011` remained closed | `006` regressed/reopened when delivery UI branches were replaced by generic dispatcher fallback |

Final current material set: `001` BLOCKING and `002,003,004,005,006,007,008,009` MAJOR. `010` remains MINOR and intentionally uncorrected under the rule that correction passes targeted only current BLOCKING/MAJOR findings.

## Required future test shape, not implemented in this freeze

No tests are added or changed here. A future correction would need behavior-first integration coverage that selects each action through the rendered SPA, provides role/session/form context, asserts the exact domain transition or unchanged-state failure, and reads the user-visible recovery result. It would also need a full action/permission table, destructive dialog continuation, later-state idempotency replay, and negative fixtures for hours, outages, conflicts, policy versions, expiry, lifecycle, and accessibility error/focus behavior.
