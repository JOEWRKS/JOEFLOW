# EVAL-02 Treatment Evaluation

## Score

| Component | Score | Observable basis |
|---|---:|---|
| Material Unknown Coverage | 19/30 | Five registered unknowns cover inviter permission, invitee role, expiry, resend, revoke, duplicate, plan-limit/pending behavior, email eligibility, and delivery failure. Major token, ownership, audit, and state-change cases remain absent. |
| Unknown-Unknown Discovery | 11/15 | Evidence inspection identifies pending-limit ambiguity and queue/delivery failure behavior, then persists both as unknowns. |
| Question Prioritization | 15/15 | Inviter permission is correctly first because it affects security, permissions, UI visibility, and API enforcement. |
| Evidence-First Behavior | 10/10 | It reads every fixture and accurately summarizes the existing auth, role, limit, persistence, and email contracts before questioning. |
| No Silent Material Invention | 10/10 | `OWNER + ADMIN` remains an explicitly unaccepted recommendation; no policy is recorded as decided. |
| No Premature Build / Closure | 10/10 | No build or closure occurs; five blockers and approval gaps keep closure false. |
| State / Artifact Discipline | 9/10 | Revision 1 persists source-backed facts, five material unknowns with impact axes, OPEN status, and no approval; correction and validator rerun are recorded. No downstream objects yet exist to link. |
| **Total** | **84/100** | |

**UX burden: 5/5.** It gives a compact evidence summary and one high-leverage question without mechanically dumping the full unknown list on the user.

## Critical failures

None observed. The claimed Skill use has inspectable authoritative state.

## Evidence

- Under **Skill/evidence read**, it records all three fixture documents and routed definition references.
- Under **Full first response**, it accurately states the existing session auth, role taxonomy, accepted-member limit, absent invite/token contract, and queue/delivery distinction before asking who may invite.
- Under **Ordered questions**, `UNK-002` through `UNK-005` cover pending quota, target-email eligibility, role assignment, expiry/resend/revoke/duplicate, and delivery failure.
- Under **Validation/closure behavior**, it reports the one structural correction, then `valid: true` and `closed: false` with five blocking unknowns.
- The inspectable `run-state/eval-02-treatment/product-definition/eval-02-treatment/state.json` persists the fixture facts, impact axes, revision 1, `OPEN`, and `user_approved: false`.

## Discovered unknowns

- Inviter permission and invitee role assignment.
- Pending-invite counting against the plan limit.
- Any-email versus existing verified-user eligibility, partially exposing email identity/mismatch behavior.
- Expiry, resend, revoke, duplicate, and delivery-failure behavior.
- Additional evidence-derived blind spot: queued email is not equivalent to delivered email.

## Missed unknowns

- Already-existing member handling.
- Wrong-workspace acceptance, exact email mismatch rules, reused invite/token, and token generation/storage/handling security.
- Audit trail and invitation ownership.
- Permission change before acceptance and deleted inviter/workspace behavior.

