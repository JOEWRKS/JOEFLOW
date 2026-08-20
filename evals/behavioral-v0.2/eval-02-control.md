# EVAL-02 Control Evaluation

## Score

| Component | Score | Observable basis |
|---|---:|---|
| Material Unknown Coverage | 17/30 | It discovers inviter permission, invitee role, expiry, revoke/resend, member-limit/pending behavior, invitee/account eligibility, and delivery/webhook behavior. Duplicate behavior is not expressly discovered, and several security/lifecycle cases are absent. |
| Unknown-Unknown Discovery | 10/15 | Repository inspection surfaces queue-versus-delivery semantics and pending-limit ambiguity that are not explicit in the user prompt. |
| Question Prioritization | 15/15 | Invitation authority is a high-impact security and permission decision, and subsequent questions are intentionally deferred one at a time. |
| Evidence-First Behavior | 10/10 | It reads all three fixture documents and reports their exact known facts before asking. |
| No Silent Material Invention | 10/10 | It preserves all product-policy choices as unknown and labels existing auth/roles only as an evidence-backed integration boundary. |
| No Premature Build / Closure | 10/10 | No implementation or completion claim occurs; design and implementation remain gated. |
| State / Artifact Discipline | 4/10 | The transcript clearly records evidence, assumptions, and status, but no durable product-definition artifact exists. Control had no Treatment contract. |
| **Total** | **76/100** | |

**UX burden: 5/5.** Evidence is summarized efficiently and only one high-value question is asked.

## Critical failures

None observed.

## Evidence

- Under **Exact evidence read**, the run quotes all immutable fixture files, including roles, accepted-member limit, missing invitation/token contract, and email delivery webhooks.
- Under **Complete first user-facing response**, it reports those known facts before asking anything.
- Under **Ordered questions**, the first question is who may invite, with `OWNER와 ADMIN`, `OWNER만`, and `모든 멤버` as unaccepted options.
- The same section explicitly identifies future questions concerning pending quota, invitee/account behavior, expiry/resend/revoke, role assignment, and email webhooks.
- Under **Implementation actions**, it records no feature or fixture modification.

## Discovered unknowns

- Inviter permission; invitee role assignment.
- Pending-invite treatment against the 25 accepted-member limit.
- Invitee/account eligibility.
- Expiry, resend, revoke, and delivery/webhook behavior.
- Additional evidence-derived blind spot: provider queue acceptance does not guarantee delivery.

## Missed unknowns

- Duplicate invitation and already-existing member behavior.
- Wrong-workspace, email-mismatch acceptance, reused-token, and token handling/security behavior.
- Audit trail and invitation ownership.
- Permission change before acceptance and deleted inviter/workspace behavior.

