# Implementation Plan

> Projection of authoritative `state.json`, revision 55. Product approval is required before execution.

| Task | Scope | Acceptance | Dependencies |
|---|---|---|---|
| TASK-001 | Native invitation accounts and Admin governance | AC-004 | — |
| TASK-002 | Claim draft, amount, attachments, submission, mobile capture | AC-001 | TASK-001 |
| TASK-003 | Manager review and revision-safe approval | AC-002 | TASK-002 |
| TASK-004 | Finance payment lifecycle and ownership | AC-003 | TASK-003 |
| TASK-005 | Settlement adjustments and duplicate-payment safety | AC-003 | TASK-004 |
| TASK-006 | Notifications, retries, schedules, warnings | AC-002..004 | TASK-001,003,004 |
| TASK-007 | Audit, retention, legal hold, secure file access | AC-001..004 | TASK-001,002 |
| TASK-008 | Role-scoped lists and audited CSV export | AC-001..004 | TASK-001,007 |

Each task has an observable verification contract in `state.json`. Any newly discovered material ambiguity creates a stable unknown and pauses affected tasks.
