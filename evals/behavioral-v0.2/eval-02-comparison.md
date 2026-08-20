# EVAL-02 Comparison

## Outcome

Control **76/100**; initial Treatment **84/100**; final Treatment **96/100**. Final delta versus Control: **+20**. Initial-to-final Treatment change: **+12**. UX: Control **5/5**, initial Treatment **5/5**, final Treatment **5/5**.

## Material Unknowns

- Expected: repository role model; inviter permission, invitee role, expiry, duplicate, existing member, wrong workspace, email mismatch, revoke/reuse, member limit and pending counting, audit, notification, token security, invitation ownership, permission change, and deleted inviter/workspace.
- Control discovers roles, inviter permission, invitee role, expiry/resend/revoke, member limit/pending behavior, invitee/account eligibility, and delivery behavior.
- Initial Treatment covers the same areas plus explicit duplicate behavior; its any-email versus verified-user question partially covers email mismatch.
- Final Treatment adds acceptance-time atomic quota, single-use token storage/validation, existing-member behavior, invited-email acceptance, workspace deletion, resend throttling, audit visibility, delivery-state UI, management surfaces, and privacy retention.
- Final Treatment still misses explicit wrong-workspace acceptance, inviter deletion, permission change before acceptance, and precise invitation ownership/transfer semantics.
- Unnecessary final Treatment questions: none. All seventeen are material and independently answerable.

## First Question

All three runs ask who may invite and offer the same policy space. Final Treatment links the choice to API authorization, UI exposure, audit, and testing; it remains a strong evidence-aware first question.

## Ordering

All prioritize inviter authority. Final Treatment then records seventeen ordered questions spanning eligibility, quota, role, token, lifecycle, delivery, audit, UI, and privacy. Neither Treatment reaches rediscovery because the user has not answered the first question.

## Evidence First

Control and both Treatments read all immutable fixture files before asking. All preserve known session auth, roles, accepted-member limit, absent invitation/token contract, and queue-versus-delivery semantics. None asks for an inspectable repository fact.

## Silent Assumptions

No run silently fixes product policy. `OWNER + ADMIN` remains a recommendation awaiting user choice. Final Treatment explicitly enumerates the route, token, expiry, role, quota, retry, and webhook policies it did not assume.

## Premature Build / Closure

No run builds or closes. Initial Treatment records false closure with five blockers; final Treatment records false closure with seventeen blockers, coverage gaps, and no approval.

## State Discipline

Initial Treatment persists revision 1 with five material unknowns. Final Treatment persists source-backed facts, a requirement and acceptance criterion, an integration, and seventeen unknowns linked to downstream objects; validation passes and status remains BLOCKED without approval. Its acceptance criterion is labeled a “compiled placeholder,” a minor artifact-quality weakness. Control has only its transcript; missing the Treatment contract is not treated as a critical failure.

## Rationalizations

- Control calls the work architectural because no invitation persistence or token contract exists; fixture evidence supports that classification.
- Both Treatments recommend `OWNER + ADMIN` for a stated security/operability balance without accepting it for the user.
- Final Treatment grounds its broader lifecycle questions in specific repository and email-service evidence.
- No observable rationalization excuses evidence skipping, invention, building, or closure.

## Verdict

**PASS.** Final Treatment scores **96/100**, exceeds the 85 target, has no critical failure, and improves **+20** over Control and **+12** over initial Treatment while retaining **5/5** UX. Remaining gaps are limited to explicit wrong-workspace, inviter-deletion, permission-change, and ownership-transfer behavior.
