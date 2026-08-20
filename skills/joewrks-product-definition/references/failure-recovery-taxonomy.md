# Failure and Recovery Taxonomy

For each failure identify trigger, detection, user-visible message, preserved input/state, retry eligibility, retry limit, cancellation, rollback/compensation, idempotency, side effects, notification, audit evidence, support path, and final state.

Always inspect validation failure, authorization denial, unauthenticated/session expiry, timeout, offline/network loss, dependency outage, duplicate/concurrent action, partial success, stale data/conflict, quota/limit, irreversible action, and notification failure.

Recovery must state what happens to mutated data. A retry must not duplicate irreversible side effects. Partial success must enumerate succeeded and failed items and define continuation or rollback.

