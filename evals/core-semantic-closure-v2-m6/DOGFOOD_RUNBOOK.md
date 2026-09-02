# M6 dogfood historical Revision-1 Phase A approval checkpoint

```text
CORE_SEMANTIC_CLOSURE_V2_M6_APPROVAL_REQUIRED
— DOGFOOD_V2_MANIFEST_READY
```

- State: `dogfood/product-definition/client-feedback-portal-dogfood-v2/state.json`
- Definition revision: `1`
- Definition digest: `e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c`
- Approval Manifest: `dogfood/approval-manifest.json`
- Approval Manifest digest: `60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705`
- Approval status: `UNAPPROVED`
- Semantic-readiness blockers: `0`

The full user-facing Approval Manifest is the exact JSON artifact above. It
reports 113 added records; no changed, superseded, or retired records; no
deferred nonblocking unknowns; and active Core, AUTH, ASYNC, and PERMISSION
Grill packs. Its exact high-risk decision inventory is `DEC-001`, `DEC-008`,
`DEC-012`, `DEC-013`, and `DEC-043`, each classified with the `security` risk
flag.

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

## Current Revision-2 approved authority and regenerated chain

The section above is the immutable historical revision-1 checkpoint. The
original revision-1 approval remains the first `approval_history` commitment:

- definition digest: `e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c`
- manifest digest: `60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705`
- approved by/at: `user` / `2026-08-30T11:54:26Z`

The current canonical state is revision `2`, `CLOSED`, and `APPROVED`:

- definition digest: `81d3b7ff59dbce321dc27fab6b51f03db4201dc1f4a1ea3d6b202f3f76afddcf`
- manifest digest: `079ef1bb60ccc382a66c6c764519e67e606744a9d10425310cc1b868be490003`
- approved by/at: `user` / `2026-09-02T11:53:47Z`
- revision-1-to-2 record-hash changes: `DEC-042`, `EVD-015`, `UNK-050`

Revision 2 corrects DEC-042 provenance only. It preserves all product and UX
meaning and the revision-1 approval history. The deterministically regenerated
current chain is bound to semantic contract hash
`56027cc08452fd0736315068cde7fa2377df661f39fc5e88c919ca4d00ff4c5b`,
runtime-plan hash
`9d4476123d64635727b2a313d6b453ba38245d10cba14da3c41bd1f1e0c42d80`,
and evidence-bundle hash
`402fb2bde69f1e6af34a38cceadea4c0cd2984026df8965fba087ca3ed47a48c`.
It remains 6 actions, 0 lifecycles, 24/24 execution records, and
`IMPLEMENTATION_CONFORMANT`; semantic-review/2.1 reliability remains
`NOT_MEASURED`.
