# Frozen Replication B Regression

## Source

- frozen source commit: `eecebc28701006dd2c7be4045a22542e34719705`
- exact implementation tree: `6294fc9072521fdb762808b87203a7e8bac4f7f5`
- adapter: `frozen-b-vitest-engine-selectors@1.0.0`
- executable contract: `c1d10a5330d916fdbe3c15c6039a9ee2f01b4c3f7265f3f1179ab730da8ee768`

The external runner imported and executed the actual frozen `engine.ts`, `seed.ts`, and `selectors.ts`. It did not modify frozen source.

## B030

The sequence created and failed `adjustment-0001`, then submitted `RESOLVE_ADJUSTMENT` with `result=Executed` and a note but without actual amount/date/reference.

Observed rejected step:

- result: `rejected / COMPLETION_EVIDENCE_REQUIRED`;
- claim revision: `6 -> 6`;
- audit count: `2 -> 2`;
- before adjustment: Failed with no verification;
- after adjustment: same version/status plus an `Executed` verification object.

The deep verifier independently marked authoritative domain state changed while version/history/business/delivery remained unchanged. A related second `CREATE_ADJUSTMENT` then returned `committed / COMMITTED`, demonstrating the one-active guard bypass.

**DETECTED — B030_REJECTED_PARTIAL_MUTATION.**

## B031

Two fresh sequences used protocol sentinels and decoded them immediately before the actual engine call:

- `B031-NAN-UPDATE`: runtime observations `/originalAmount=NaN`, `/krwAmount=NaN`;
- `B031-INFINITY-UPDATE`: runtime observations `/originalAmount=+Infinity`, `/krwAmount=+Infinity`.

Both `UPDATE_DRAFT` commands committed. Both following `SUBMIT_CLAIM` commands also committed. The after snapshots preserve typed sentinels rather than serializing the non-finite values as `null`.

**DETECTED — B031_NAN_SUBMISSION and B031_POSITIVE_INFINITY_SUBMISSION.**

## Other actual residuals

- `B-ADMIN-STALE`: `STALE_VERSION`, but required `latestValues.user.active` was absent — **B_STALE_LATEST_VALUE detected**.
- approval then revoke then actual timeline selector: both events projected current `Submitted`; the approval event did not retain `Payment pending` — **B_HISTORICAL_STATUS_PROJECTION detected**.
- terminal payment: status became `Payment completed`, but `payment.overdue` stayed `true` — terminal clear failure detected.
- stopped Manager reminder: attempts changed `1 -> 2` after claim decision state `Payment pending` — terminal retry-stop failure detected.

## Positive sequences

- authority loss after file grant: `FILE_AUTHORITY_REVOKED`, domain/version/business/delivery no-op, explicit DENIED audit only — PASS.
- ordinary stale draft update: complete no-op — PASS.
- identical idempotency-key replay: original result identity, no duplicate changes/effects — PASS.
- Manager reassignment followed by permanent delivery failure: reassignment stayed committed — PASS.
- one Admin manual delivery retry: version/history/warning/delivery changed once as declared — PASS.
