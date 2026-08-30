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

## Track B — blocked bounded native existing-product reconciliation

Track B was stopped before a native V2 state or approval manifest was retained.
The intended bounded slice is `REQ-005` and `REQ-006`, but the active Core Grill
requires analytics-events and measurement behavior. The inspected legacy
documents and user decisions contain no authority for that material policy;
historical bare `COVERED` cells and evaluation metrics are not product intent.

Track B is not the full legacy migration. It does not trim, close, replace, or
supersede Track A, and it does not modify the historical dogfood directory.
Its status is `NEEDS_CONTEXT`, not `READY_FOR_REVIEW`.
