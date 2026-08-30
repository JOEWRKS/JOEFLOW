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

Track B is `NEEDS_CONTEXT` at `FIELD_LEVEL_UX_AUTHORITY_GAP`. The source
documents identify every required state and action axis, but do not define the
behavior of several mandatory cells at field level. The old status-only
`COVERED` cells cannot be promoted as intent.

The invalid bounded state, evidence map, approval packet, and approval runbook
were removed. Track B has no current readiness or digest claim. The already
authorized bounded no-analytics decision is preserved in `README.md`; it does
not answer the independent interaction-policy gap.

Track B remains separate from the complete Track A audit. It does not trim,
close, replace, or supersede Track A, and it does not modify the historical
dogfood directory. Approval and all later work remain prohibited until the
missing field-level interaction policy receives user authority.
