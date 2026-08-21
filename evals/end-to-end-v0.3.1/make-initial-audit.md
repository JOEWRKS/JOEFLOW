# Initial Make Audit

Initial source readback found **BLOCKING 5 / MAJOR 7 / MINOR 1**.

| ID | Severity | Drift |
|---|---|---|
| DRIFT-001 | BLOCKING | Designer authentication/session semantics were reduced. |
| DRIFT-002 | BLOCKING | Raw review-token persistence violated the access/data contract. |
| DRIFT-003 | BLOCKING | Reviewer access was not consistently bound to the exact Version. |
| DRIFT-004 | BLOCKING | Unarchive restored an old review link. |
| DRIFT-005 | BLOCKING | Canonical Version lifecycle semantics were changed. |
| DRIFT-006 | MAJOR | Idempotency and concurrent-operation semantics were incomplete. |
| DRIFT-007 | MAJOR | Upload cancellation and recovery were incomplete. |
| DRIFT-008 | MAJOR | Notification delivery, retry, and self-notification separation were omitted. |
| DRIFT-009 | MAJOR | PDF annotation page-plus-normalized-coordinate semantics were incomplete. |
| DRIFT-010 | MAJOR | Append-only comment/history semantics were incomplete. |
| DRIFT-011 | MAJOR | Mobile review behavior was omitted. |
| DRIFT-012 | MAJOR | Changes-request evidence semantics drifted. |
| DRIFT-013 | MINOR | Unauthorized presentation branding exceeded the low-fi direction. |

These findings describe prototype divergence; they were not absorbed into the approved Product Definition.
