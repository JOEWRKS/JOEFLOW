# M6 dogfood Phase A approval checkpoint

```text
CORE_SEMANTIC_CLOSURE_V2_M6_APPROVAL_REQUIRED
— DOGFOOD_V2_MANIFEST_READY
```

- State: `dogfood/product-definition/client-feedback-portal-dogfood-v2/state.json`
- Definition revision: `1`
- Definition digest: `ac531d869af5310820e2af90d78d205e841d05bb944f9a16865c8808f3a69957`
- Approval Manifest: `dogfood/approval-manifest.json`
- Approval Manifest digest: `e9492282561bf4eaa4bd2fde5ecfd01b00e806b7aa76e7119d7c6ce5b1b1f1ce`
- Approval status: `UNAPPROVED`
- Semantic-readiness blockers: `0`

The full user-facing Approval Manifest is the exact JSON artifact above. It
reports 113 added records; no changed, superseded, or retired records; no
deferred nonblocking unknowns; and active Core, AUTH, ASYNC, and PERMISSION
Grill packs. Its exact high-risk decision inventory is `DEC-001`, `DEC-012`,
`DEC-013`, and `DEC-043`, each classified with the `security` risk flag.

The bounded analytics and field-level interaction decisions remain current user
intent and are not system-wide policies.

For this bounded M6 dogfood Product Definition only, review-link send, resend, and revoke each require client_attempt_id and expected_review_link_revision. The same client_attempt_id returns the previously committed result and creates no additional side effects. Distinct concurrent attempts on the same expected revision race and exactly one may commit. Once one commits and advances the revision, other stale expected revisions are rejected. A stale rejection returns the latest authoritative review-link state and revision needed for recovery and reconciliation. Retrying stale requires a new attempt based on the newly observed revision; stale is never reinterpreted against a newer revision. One logical successful attempt creates no duplicate review link, applicable email send, domain/history record, delivery record, or other externally visible side effect. Revoke uses the same attempt/revision semantics with no duplicate revocation, history, or notification effects; it has no email side effect unless this approved definition separately requires one. This policy is bounded to this M6 dogfood Product Definition and is not a universal future policy.

This current user decision is recorded without a fabricated repository version,
content hash, or timestamp. Repository-backed documented and historical intent
is separately pinned to the exact frozen historical tree and supporting blobs.
Designer-only `resolve_thread.session_expiration` binds `RULE-110`; thread
concurrency binds `RULE-084` and, where applicable, `RULE-095`/`RULE-096`;
review-link concurrency binds the bounded `RULE-131` through `RULE-134`.

No approval field, approval actor, approval time, downstream contract, runtime
evidence, re-entry artifact, Phase B work, or Task 6 work exists at this
checkpoint. A later run must receive explicit approval of this exact manifest
digest and a separately supplied UTC approval timestamp before recording any
approval.
