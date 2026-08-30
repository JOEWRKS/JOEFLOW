# M6 migration audit

## Track A — complete legacy migration audit

The complete `0.1.2.1` dogfood state was passed to the M6 migrator without
editing the source. The deterministic result is revision 45, `OPEN`, and
`UNAPPROVED`.

- Legacy stable IDs preserved: 269 of 269.
- IDs promoted automatically: 0.
- Exact legacy records archived for reconciliation: 269.
- Deterministic reconciliation gaps: 1151.
- Generated canonical unknowns: 0. Gap metadata retains every exact source
  path; no migration scaffold became current authority.
- Historical legacy approval: retained only as source migration metadata. It
  was not copied into current approval or approval history.
- Legacy `COVERED` cells promoted to V2 `COVERED`: 0.

Track A remains OPEN. Its audit is complete, but its full reconciliation is not.

## Track B — bounded native existing-product reconciliation

Track B reconciles the inspectable native V2 slice for `REQ-005` and `REQ-006`.
It contains both documented actors, the review-access and exact-Version thread
flows, `SCR-006` and `SCR-007`, acceptance criteria, tasks, and the active AUTH,
ASYNC, PERMISSION, and Core Grill packs.

The current user decision makes analytics and telemetry not applicable only to
this bounded definition. It creates no analytics events, properties, tracking
identifiers, retention/access policy, funnels, or success metrics. Existing
domain history and email delivery/send status remain ordinary product state and
are not reclassified as analytics telemetry.

Track B is not the full legacy migration. It does not trim, close, replace, or
supersede Track A, and it does not modify the historical dogfood directory.
Its status is `READY_FOR_REVIEW` and `UNAPPROVED`, with zero semantic-readiness
blockers. Approval and all later work remain outside Phase A.
