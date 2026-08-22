# Product Definition — Expense Reimbursement Dogfood

> Projection of `state.json`. Revision 55. Status: `READY_FOR_REVIEW`. `state.json` is authoritative.

## Goal and actors

Small-company employees submit one expense per claim with receipts; their fixed direct manager reviews it; Finance manages payment and settlement; Admin operates accounts, relationships, categories, legal holds, reassignments, audit, and warnings.

| ID | Actor | Core scope |
|---|---|---|
| USR-001 | Employee | Own drafts, claims, revisions, attachments, and user-safe timeline |
| USR-002 | Manager | Currently assigned submitted/re-submitted revisions; never self-approve |
| USR-003 | Finance | Approved payable claims, payment lifecycle, adjustments, scoped CSV |
| USR-004 | Admin | Full operational administration and raw audit view |

## Requirements

| ID | Requirement | Screen | Acceptance |
|---|---|---|---|
| REQ-001 | Draft, validate, attach evidence, submit, withdraw, revise, and inspect own claims | SCR-001 | AC-001 |
| REQ-002 | Review exact latest assigned revision; approve, request changes, reject, or revoke eligible approval | SCR-002 | AC-002 |
| REQ-003 | Claim approved work, schedule/complete/fail/hold payments, prevent duplicates, and manage settlement adjustments | SCR-003 | AC-003 |
| REQ-004 | Operate invitations, accounts/roles, managers, categories, holds, reassignments, audit, warnings, and Admin export | SCR-004 | AC-004 |

## Key product contract

- One claim contains one expense. Required fields are expense date, merchant/payee, final paid total, currency, category, business purpose, and receipt.
- KRW is company currency. Foreign claims store original-currency final total, employee-entered rate (KRW per unit, six decimals), KRW claim amount, and rate evidence. The rounded calculation permits only ±1 KRW.
- Submission binds the current direct manager. Changes requested create a new revision without a fixed limit; final rejection and employee withdrawal terminate the claim.
- Payment lifecycle is Payment pending → Scheduled → Payment completed, with explicit Payment failed and Payment hold branches. Post-payment corrections use linked Recovery or Additional-payment adjustments and never rewrite the original completed payment.
- Every mutation uses optimistic version validation and idempotency. Stale requests are atomic no-ops and return latest state plus changed fields.
- Append-only audit, least privilege, seven-year fiscal-year retention, legal hold, scheduled deletion, malware scanning, duplicate detection, and continuous file-download authorization apply throughout.
- Responsive current iOS Safari and Android Chrome support all core workflows. Native apps, offline authoring, SSO, accounting/payroll/bank integrations, organization hierarchy, cost centers, VAT separation, and automated amount policies are v1 non-goals.

## Coverage and readiness

All 20 product coverage dimensions are covered for REQ-001..004. All 16 UX state axes and 22 action axes are covered for SCR-001..004. Eight implementation tasks map requirements/rules/decisions to AC-001..004. No blocking unknown or contradiction remains.
