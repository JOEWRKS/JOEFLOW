# RERUN-EVAL-02 Treatment Evaluation

## Score

| Component | Score | Observable basis |
|---|---:|---|
| Material Unknown Coverage | 27/30 | Seventeen independently persisted unknowns cover inviter permission, recipient eligibility, pending and acceptance-time limits, granted role, expiry, single-use token storage/validation, duplicates/existing members, revoke/resend/throttling, invited-email sign-in, workspace deletion, delivery webhooks/failure UI, audit, UI placement, and email retention. Wrong-workspace acceptance, inviter deletion, and permission change before acceptance are not explicit. |
| Unknown-Unknown Discovery | 15/15 | Repository evidence drives legitimate additional questions about atomic quota enforcement, queue-versus-delivery state/UI, webhook effects, resend abuse controls, audit visibility, UI placement, workspace deletion, and privacy retention. |
| Question Prioritization | 15/15 | Inviter authority remains first and is tied to API authorization, UI exposure, audit records, and testing. The ordered list proceeds through eligibility/quota/role/token/lifecycle and operational concerns. |
| Evidence-First Behavior | 10/10 | It reads all three fixture documents, distinguishes accepted-member facts from undocumented pending behavior, and uses repository and email-service capabilities as sources without extending them into policy. |
| No Silent Material Invention | 10/10 | `OWNER + ADMIN` remains an unaccepted recommendation. The transcript enumerates policies it did not assume, including routes, token format, expiry, role default, quota, retry, and webhook behavior. |
| No Premature Build / Closure | 10/10 | Implementation is not started; closure remains false with seventeen blockers, coverage gaps, and missing/stale approval conditions. |
| State / Artifact Discipline | 9/10 | The inspectable revision-1 state is structurally valid, BLOCKED, unapproved, source-backed, and links every unknown to the requirement and acceptance criterion. The acceptance criterion calls itself a “compiled placeholder,” so the artifact is not fully clean. |
| **Total** | **96/100** | |

**UX burden: 5/5.** The user receives a concise evidence-based explanation and one high-impact choice; the seventeen-item discovery inventory is recorded for sequencing rather than presented as a questionnaire.

## Critical failures

None observed. Claimed Skill use is backed by an inspectable authoritative state file.

## Evidence

- **Evidence** records session authentication, roles, the accepted-member limit, absent invitation/token contracts, repository lookups, and the queue-versus-delivery distinction from all three fixture files.
- **Full response** asks who may invite and links the choice to API permissions, UI visibility, audit, and tests while leaving the recommendation unaccepted.
- **Ordered questions** expressly covers recipient eligibility, pending quota, role assignment, token lifecycle/security, duplicates/existing members, revoke/resend, invited-email acceptance, workspace deletion, atomic acceptance quota, webhook/UI behavior, audit, surfaces, and privacy retention.
- **Unknowns and assumptions** says all seventeen remain OPEN and enumerates product details that were not assumed.
- **Validation/closure** records valid structure and false closure with seventeen blockers and nineteen coverage gaps.
- `run-state/rerun-eval-02-treatment/product-definition/rerun-eval-02-treatment/state.json` records the facts, requirement, acceptance criterion, integration, linked unknowns, BLOCKED status, and no approval.

## Discovered unknowns

- Inviter permission, recipient eligibility, invite-granted role, expiry, duplicates/already-members, revoke, resend, invited-email acceptance, and pending-limit behavior.
- Single-use token storage/validation and atomic limit recheck at acceptance.
- Workspace deletion, delivery webhook state, delivery-failure UI, and audit visibility.
- Additional legitimate discoveries: resend throttling, invitation-management surfaces, and email exposure/retention.

## Missed unknowns

- Explicit wrong-workspace acceptance behavior.
- Inviter deletion and inviter permission changes after issuance.
- Explicit ownership/transfer semantics beyond revoke and audit-view authority.

## Regression assessment

The rerun improves from **84/100 to 96/100 (+12)** with no critical failure and unchanged **5/5** UX. It closes the initial Treatment’s principal gaps around token security/reuse, existing members, audit, workspace deletion, atomic capacity enforcement, and lifecycle delivery behavior. Remaining misses are narrow state-change and cross-workspace cases; the final result exceeds the 85-point target.
