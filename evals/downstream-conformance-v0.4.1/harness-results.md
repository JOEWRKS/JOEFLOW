# Harness Results

## Frozen regressions

| Result ID | Actual runtime observation | Python-core result |
|---|---|---|
| A_UI_DOMAIN_DISCONNECT | public success; revision `1→2`; bookings `0→0` | DETECTED |
| B030_REJECTED_PARTIAL_MUTATION | rejected resolve changed verification; version/history unchanged; second create committed | DETECTED |
| B031_NAN_SUBMISSION | real JS `NaN` committed, then claim submitted | DETECTED |
| B031_POSITIVE_INFINITY_SUBMISSION | real JS `+Infinity` committed, then claim submitted | DETECTED |
| B_STALE_LATEST_VALUE | stale Admin response omitted `latestValues.user.active` | DETECTED |
| B_HISTORICAL_STATUS_PROJECTION | approval event projected later `Submitted` status | DETECTED |
| B_TERMINAL_RETRY_STOP | overdue stayed true; stopped reminder attempts `1→2` | DETECTED |

## Required semantic coverage

| Sequence | Actual result | Conformance |
|---|---|---|
| authority lost after initial access | file grant followed by `FILE_AUTHORITY_REVOKED`; only DENIED audit changed | PASS |
| stale expected version/no-op | draft stale response; all five components unchanged | PASS |
| repeated same idempotency key | original commit then replay with no duplicate component changes | PASS |
| delivery failure after business commit | Manager reassignment remained committed through permanent delivery failure | PASS |
| manual delivery retry | exactly one manual retry changed delivery/version/audit/warning | PASS |
| superseded transition sentinel | active observation matched inactive superseded `DEC-011` | EXPECTED NONCONFORMANT / DETECTED |

## Actual evidence count

- Replication A: 1 JSONL execution record.
- Replication B: 22 JSONL execution records.
- Compiled contracts: 3.
- Adapter-authored conformance verdicts: 0.

The evidence records contain exact commands, setup, before/result/after snapshots, and deltas. Counts are inventory only; the verdicts above come from the executed transition evidence.

Verification after evidence freeze: full suite `71/71 PASS`, including the pinned A/B runtime integration; original baseline `43/43 PASS` separately.
