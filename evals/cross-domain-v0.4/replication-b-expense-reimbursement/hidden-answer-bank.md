# Hidden Answer Bank — Post-run Reconstruction

This bank was derived after the product-agent run. It records the answers the responder actually supplied or accepted; it was not available to the product agent.

## Scripted/foundational answers (UNK-001..028)

| IDs | Answer truth |
|---|---|
| 001–003 | Direct-manager routing; invitation-email app-native accounts; multiple roles allowed with least privilege and no self-approval. |
| 004–005 | Manager outcomes are Approve / Changes requested / Final rejected; changes create revisions. Drafts are editable/deletable; submitted claims can be withdrawn before a decision; initially, approval was irreversible. |
| 006–010 | Required expense fields, KRW/foreign-currency model, receipt and FX-evidence constraints, one expense per claim, and Admin-managed snapshotted categories. |
| 011–014 | Duplicate warning/override, 90-day late-claim reason, reminder/escalation behavior, and audited manager reassignment. |
| 015–018 | Finance lifecycle, completion/failure fields, append-only post-payment adjustments, and email plus in-app notifications separated from business-state transactions. |
| 019–022 | Role/relationship access, append-only audit with masked user timeline, seven-year fiscal retention/legal hold, and role-scoped search/filter/sort plus Finance/Admin CSV. |
| 023–028 | Optimistic concurrency and idempotency, draft/upload recovery, responsive web scope, explicit integration exclusions, dedicated Admin UI, and manager-change snapshot semantics. |

## Emergent answers (UNK-029..054)

| IDs | Answer truth |
|---|---|
| 029–030 | Unlimited revision loop until terminal action; exact latest revision is actionable; history visibility follows current authority. |
| 031–032 | Scheduled-payment overdue alerts and mandatory Not-paid verification before retry. |
| 033–035 | Gross final-paid-total tax model, six-decimal FX input/whole-KRW comparison, and five-minute user/file-scoped reauthorizing download access. |
| 036–040 | Invitation expiry/reissue/revocation race, immediate session invalidation, reassignment delivery retries, and strict timeline allowlist. |
| 041–045 | Calendar fiscal year, legal-hold authority/scope, daily deletion job, nine category seeds, and post-Scheduled hold → Admin reopen → employee revision → current-manager reapproval. |
| 046–050 | Sequential adjustments, failed-adjustment verification, payment-date bounds, shared Finance queue ownership, and bounded notification retries/manual retry. |
| 051–054 | Autosave trigger/state, 90-day abandoned-draft retention and warning, daily expired-draft deletion, and 1/2/4/8/16-second generation-safe save retries. |

## Mandatory changed truth

After the initial irreversible-approval decision had propagated, the responder changed it: the approving manager may revoke their own approval before `Scheduled`, with a mandatory reason, returning the same revision to `Submitted`; revocation is forbidden at or after `Scheduled`. This became DEC-022 and superseded DEC-021.
