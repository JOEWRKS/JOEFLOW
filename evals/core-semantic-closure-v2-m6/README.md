# Core Semantic Closure V2 M6 evaluation

Track A remains the complete deterministic legacy migration audit: revision 45,
`OPEN`, `UNAPPROVED`, 269/269 stable IDs preserved, and all 1151 reconciliation
gaps retained. Its full reconciliation remains open.

Track B is the separate bounded native reconciliation for
`client-feedback-portal-dogfood-v2`. With three bounded current user decisions
recorded as first-class intent, its revision 1 state is `READY_FOR_REVIEW`,
`UNAPPROVED`, and has zero semantic-readiness blockers. It does not trim, close,
replace, or supersede Track A.

## Bounded current user authority

For this bounded M6 existing-product V2 dogfood Product Definition only, product analytics/telemetry is NOT used. REQ-005/REQ-006 review-link access and thread actions emit no analytics events. Introduce no analytics event names, properties, tracking identifiers, analytics retention/access policy, funnels, or success metrics. Existing domain/business history remains ordinary product state/history where already required. Existing email delivery/send status remains ordinary product operational/domain state where already required. Neither is reclassified as analytics telemetry. This is an explicit current user product decision/boundary, not an inference from missing implementation. It is not a permanent system-wide prohibition for future products/revisions.

For this bounded M6 existing-product V2 dogfood Product Definition only: Loading and Submitting show pending state and never success. Empty shows the screen-specific zero state. Partial shows available authoritative data plus an explicit recovery notice. Completed follows only authoritative confirmation. Cancelled, Cancel, and Back cause no mutation and preserve eligible unsent text. Refresh reloads latest authoritative state. Committed review-link/thread mutations have no direct Undo; recovery uses documented new-link, new-reply, or reopen paths. Offline and Timeout withhold success, preserve eligible input, refresh authoritative state before retry, and must not duplicate mutation or notification. Destructive confirmation is N/A for this bounded fixture. This interaction policy is bounded to this dogfood Product Definition and is not a system-wide rule.

For this bounded M6 dogfood Product Definition only, review-link send, resend, and revoke each require client_attempt_id and expected_review_link_revision. The same client_attempt_id returns the previously committed result and creates no additional side effects. Distinct concurrent attempts on the same expected revision race and exactly one may commit. Once one commits and advances the revision, other stale expected revisions are rejected. A stale rejection returns the latest authoritative review-link state and revision needed for recovery and reconciliation. Retrying stale requires a new attempt based on the newly observed revision; stale is never reinterpreted against a newer revision. One logical successful attempt creates no duplicate review link, applicable email send, domain/history record, delivery record, or other externally visible side effect. Revoke uses the same attempt/revision semantics with no duplicate revocation, history, or notification effects; it has no email side effect unless this approved definition separately requires one. This policy is bounded to this M6 dogfood Product Definition and is not a universal future policy.

## Phase A checkpoint

The exact checkpoint and manifest identities are in `DOGFOOD_RUNBOOK.md`.
Magic-link identity, expiry, revocation, Designer session, and role-scoped
permission decisions are security-classified; the Approval Manifest contains
the exact resulting high-risk decision inventory. Repository-backed intent is
pinned to the frozen historical tree/blob commitments, while current user
decisions retain null repository commitments and no fabricated timestamp.

No approval fields or timestamps exist. Phase B, Task 6, downstream
compilation, runtime conformance, and re-entry have not started.
