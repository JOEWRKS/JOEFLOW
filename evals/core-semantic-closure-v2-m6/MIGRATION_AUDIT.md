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

## Track B — bounded native reconciliation ready for review

The user supplied all three bounded material decisions: no product analytics or
telemetry for REQ-005/REQ-006; the uniform field-level interaction policy for
SCR-006/SCR-007; and exact review-link send/resend/revoke client-attempt,
expected-revision, race, stale-recovery, and no-duplicate-side-effect semantics.
All three are recorded as current user intent without a timestamp or fabricated
repository commitment and are explicitly not universal future policies.

The bounded revision 1 state is `READY_FOR_REVIEW` and `UNAPPROVED`. Discovery,
Core and applicable Grill coverage, exact authority binding, state validation,
and deterministic manifest compilation report zero semantic-readiness blockers.
Every selected SCR-006/SCR-007 state and action axis is bound to exact semantic
record fields. The review-link concurrency surface has a complete ASYNC Grill
row, and Designer-only thread resolution uses the Designer session authority.

Magic-link identity, expiry, revocation, Designer session, and role-scoped
permission decisions are security-classified. The exact high-risk decision
inventory is `DEC-001`, `DEC-008`, `DEC-012`, `DEC-013`, and `DEC-043`. Every
consumed repository-backed documented or historical intent source is pinned to
the exact frozen historical Git tree and supporting blob commitment.

Track B remains separate from the complete Track A audit. It does not trim,
close, replace, or supersede Track A, and it does not modify the historical
dogfood directory. Approval, Phase B, Task 6, downstream compilation, runtime
conformance, and re-entry have not started.
