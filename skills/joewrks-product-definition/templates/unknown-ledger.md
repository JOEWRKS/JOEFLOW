# Unknown Ledger

> Projection of `state.json`; update state first.

| ID | Class | Question | Material | Status | Evidence/source | Affects | Resolution |
|---|---|---|---|---|---|---|---|

Allowed classes: `KNOWN_KNOWN`, `KNOWN_UNKNOWN`, `UNKNOWN_KNOWN`, `UNKNOWN_UNKNOWN`.

For `ANSWERED`, record `resolution` and `source`. For `ASSUMED_ACCEPTED`, also record `recommendation`, `accepted_by: "user"`, and `accepted_at`. For `DEFERRED_NON_BLOCKING`, record `source`, `deferral_reason`, and explanatory strings for scope, rules, flows, states, privacy, money, security, and acceptance. For `SUPERSEDED`, record an existing unknown ID in `superseded_by`.
