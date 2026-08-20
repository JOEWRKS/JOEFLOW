# Decision Ledger

> Projection of `state.json`; update state first.

| ID | Question | Decision | Reason | Source | Status | Timestamp | Affects | Supersedes |
|---|---|---|---|---|---|---|---|---|

Allowed states: `OPEN`, `ANSWERED`, `ASSUMED_ACCEPTED`, `DEFERRED_NON_BLOCKING`, `BLOCKED_EXTERNAL`, `SUPERSEDED`.

`ANSWERED` requires decision, reason, and source. `ASSUMED_ACCEPTED` additionally requires recommendation, `accepted_by: "user"`, and `accepted_at`. `DEFERRED_NON_BLOCKING` requires source, deferral reason, and explanatory strings for all eight impact axes. `SUPERSEDED` requires an existing decision ID in `superseded_by`.
