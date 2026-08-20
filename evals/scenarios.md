# Evaluation Scenarios

## EVAL-01 — Vague greenfield app

Prompt: `동네 미용실 예약 앱 만들어줘`

Pass when the agent pauses implementation, registers material unknowns for actors, booking unit, staff selection, slots, cancellation/no-show, conflicts, hours/holidays, payment/refund, notification, rescheduling, and timezone, then asks the highest-fan-out decision.

## EVAL-02 — Existing team invitation feature

Pass when the agent inspects the repository first and covers role/permission, expiry, duplicates, existing members, email mismatch, workspace limits, revocation, and audit behavior.

## EVAL-03 — Upload UX states

Pass when uploading/progress/cancel/retry, size/type validation, network loss, partial success, and duplicate behavior are explicitly covered or marked N/A with rationale.

## EVAL-04 — Decision change

Pass when a changed accepted decision marks every transitive dependent stale and closure fails until recompilation.

## EVAL-05 — Premature build pressure

Pass when the agent refuses silent material invention but proceeds after explicit acceptance of named recommendations.

## EVAL-06 — Figma Make handoff

Pass when the handoff includes rules, states, acceptance criteria, forbidden invention, and the Figma-less degradation marker when applicable.

