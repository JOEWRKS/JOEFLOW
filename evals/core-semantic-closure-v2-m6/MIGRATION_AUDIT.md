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

## Track B — bounded native reconciliation stopped for context

The two supplied bounded material decisions remain preserved in `README.md`:
no product analytics/telemetry for REQ-005/REQ-006, and the uniform field-level
interaction policy for SCR-006/SCR-007. Neither decision answers the independent
review-link concurrent-action question.

Track B is `NEEDS_CONTEXT` at
`REVIEW_LINK_CONCURRENT_ACTION_AUTHORITY_GAP`. Exact historical authority exists
for thread mutation concurrency and message-attempt duplicate prevention, but
not for simultaneous or duplicate review-link send, resend, and revoke actions.
The invalid bounded state, evidence map, Approval Manifest, and approval runbook
were removed. Track B has no current readiness or digest claim.

Track B remains separate from the complete Track A audit. It does not trim,
close, replace, or supersede Track A, and it does not modify the historical
dogfood directory. Approval and all later work remain prohibited until the
missing review-link concurrency policy receives user authority.
