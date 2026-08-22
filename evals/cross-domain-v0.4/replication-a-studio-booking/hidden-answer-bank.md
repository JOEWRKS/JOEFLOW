# Hidden Answer Bank — Post-Run Record

Safety boundary: this file was created only after the Product Agent run ended. It is a reconstruction of answers actually supplied/accepted, not evidence that the agent saw a prewritten checklist.

## Initial bank (UNK-001..037)

The initial bank covered immediate confirmation/no payment; pricing; cancellation and rescheduling; room/equipment exclusivity, quantity and compatibility; hours, buffers, slot length and booking horizon; timezone; notifications; customer/staff authentication and authority; retention/legal hold; accessibility; metrics/export; resource administration; maintenance, capacity, terms, privacy, concurrency and conflict recovery.

Material values included atomic commit with no general customer hold, one exclusive room plus quantity-based compatible equipment, 30-minute boundaries, 1–8 hour sessions, 30-minute pre/post buffers, a 90-day horizon, Asia/Seoul, a 2-hour minimum lead time, KRW price snapshots without payment, email-only customer notifications, and an initially accepted 24-hour cancellation/reschedule cutoff.

UNK-037 was the first explicitly rediscovered `UNKNOWN_UNKNOWN`: preserve customer input and still-compatible selections after a competing commit loses, discard invalid choices, and show fresh alternatives.

## Emergent bank (UNK-038..066)

Continued interrogation added 29 records: management-link/session expiry and rate limits; account-enumeration resistance; encrypted draft recovery; equipment-shortage alternatives; operating-hours conflict disposition; bounded notification retries/provider constraints; post-cutoff inquiry and operator-change consent; KRW/rounding; exact lead-time boundary; legal-hold authority; delivery/audit retention; early privacy deletion; personal-data export prohibition and scoped access; operator login/MFA/invitation/reset/lock/recovery-code rules; latest-version proposal semantics; bidirectional inquiry threads; policy publishing; and operator-booking hold expiry/reacquisition.

Exact question and resolution text is preserved under the same stable IDs in `product-definition/studio-booking-dogfood/UNKNOWN_LEDGER.md` and canonical `state.json`. Final answer-bank status is 66/66 answered, with no blocking or deferred record.

