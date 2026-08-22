# User Flows

> Projection of authoritative `state.json`, revision 55.

## FLOW-001 — Employee claim

Draft/autosave → attach scanned receipt and optional FX evidence → validate category/date/duplicate/FX rules → submit exact revision to snapshotted manager → withdraw before decision or revise after Changes requested. Mobile camera and file selection use identical server rules.

## FLOW-002 — Manager review

Open assigned latest revision → inspect every authorized historical revision read-only → review amount/FX/evidence → Approve, Changes requested with comment, or Final rejected with comment. Stale-revision decisions are rejected. Eligible approval may be revoked only before Scheduled.

## FLOW-003 — Finance payment

Approved claim enters shared queue → Finance atomically claims while setting Scheduled → complete, fail, or hold with required guards → verify before retry → manage linked settlement adjustments after completion. Unclear external execution enters Needs verification and blocks new adjustment.

## FLOW-004 — Admin operations

Manage invitations/accounts/roles/managers/categories/holds/reassignments → inspect raw audit and operational warnings → retry eligible delivery once. Every mutation is versioned, idempotent, authorized, and audited.

All flows include permission loss, stale conflict, timeout/retry, notification separation, secure download, retention, and responsive mobile branches.
