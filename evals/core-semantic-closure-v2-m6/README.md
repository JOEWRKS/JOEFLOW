# Core Semantic Closure V2 M6 evaluation

This directory preserves the M6 existing-product dogfood evidence at an
explicit safe stop. Track A remains the complete deterministic migration audit:
revision 45, `OPEN`, `UNAPPROVED`, 269/269 stable IDs preserved, and all 1151
reconciliation gaps retained. Its full reconciliation remains open.

Track B status is `NEEDS_CONTEXT`. Final whole-branch review found that the
historical/user sources do not define simultaneous or duplicate review-link
send, resend, and revoke behavior. The bounded state, evidence map, Approval
Manifest, and approval runbook were removed so they cannot be mistaken for a
valid checkpoint. There is no current Track B definition digest, manifest
digest, or approval packet.

## Preserved bounded current user authority

For this bounded M6 existing-product V2 dogfood Product Definition only, product analytics/telemetry is NOT used. REQ-005/REQ-006 review-link access and thread actions emit no analytics events. Introduce no analytics event names, properties, tracking identifiers, analytics retention/access policy, funnels, or success metrics. Existing domain/business history remains ordinary product state/history where already required. Existing email delivery/send status remains ordinary product operational/domain state where already required. Neither is reclassified as analytics telemetry. This is an explicit current user product decision/boundary, not an inference from missing implementation. It is not a permanent system-wide prohibition for future products/revisions.

For this bounded M6 existing-product V2 dogfood Product Definition only: Loading and Submitting show pending state and never success. Empty shows the screen-specific zero state. Partial shows available authoritative data plus an explicit recovery notice. Completed follows only authoritative confirmation. Cancelled, Cancel, and Back cause no mutation and preserve eligible unsent text. Refresh reloads latest authoritative state. Committed review-link/thread mutations have no direct Undo; recovery uses documented new-link, new-reply, or reopen paths. Offline and Timeout withhold success, preserve eligible input, refresh authoritative state before retry, and must not duplicate mutation or notification. Destructive confirmation is N/A for this bounded fixture. This interaction policy is bounded to this dogfood Product Definition and is not a system-wide rule.

## REVIEW_LINK_CONCURRENT_ACTION_AUTHORITY_GAP

Thread actions have exact existing concurrency authority: `RULE-084` guards
exact-Version mutation by expected revision; `RULE-095` and `RULE-096` add
same-attempt idempotency and duplicate-record prevention for pin/reply message
submissions. `resolve_thread` uses `RULE-084`. The historical review-link
sources define one active project link, rotation, manual revoke, expiry, and
Designer-only authority, but do not define concurrent or duplicate send,
resend, and revoke semantics. `RULE-125` covers offline/timeout retry and cannot
be stretched into general concurrent-action authority.

Smallest material question: may this bounded dogfood require every review-link
send/resend/revoke to carry a client attempt ID and expected project review-link
revision, return the prior result for the same attempt, let one distinct
concurrent attempt win while rejecting stale attempts with the latest link
state, and create no duplicate link, email, or history entry? This is the
recommended uniform policy; otherwise the user must name action-specific
exceptions.

The completed actor audit also fixes the future mapping boundary:
Designer-only `resolve_thread.session_expiration` must bind exact `RULE-110`,
not Reviewer-link `RULE-027`; the other selected actor/session axes matched
their action actors. Any rebuilt checkpoint must classify the existing
magic-link identity, expiry, revocation, session, and role-scope authority as
security risk and include the resulting high-risk decisions. Consumed
repository-backed intent must bind the exact frozen Git tree/blob or exact
source-byte commitment.

No approval fields or timestamps exist. Phase B, Task 6, downstream
compilation, runtime conformance, and re-entry have not started.
