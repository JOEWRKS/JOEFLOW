# Screen Specification

> Projection of authoritative `state.json`, revision 55.

| ID | Screen | Major actions | Responsive requirement |
|---|---|---|---|
| SCR-001 | Employee claim list/detail/editor | Draft, receipt/FX upload, submit, revise, resubmit | Camera/file upload and single-column mobile form |
| SCR-002 | Manager review queue/detail | Review, FX review, approve, request changes, final reject | Full review outcomes and conflict recovery on mobile |
| SCR-003 | Finance payment list/detail | Schedule, complete, fail, retry; adjustment/hold controls in detail | Core transitions on mobile; desktop recommended for bulk CSV |
| SCR-004 | Admin console | Invitations, accounts/roles, managers, categories, holds, reassignments, audit, warnings | Core operations on mobile; desktop recommended for bulk CSV |

Each interactive screen covers default, loading, empty, partial, success, error, disabled, permission denied, unauthenticated, offline, timeout, retrying, submitting, completed, cancelled, and expired states. Every declared major action covers entry, preconditions, inputs, validation, submission, success/failure/retry/cancel/back/refresh, concurrent action, timeout/offline/permission/session expiry, mutation, side effect, notification, persistence, undo, and destructive confirmation.

Related-user timelines use the fixed allowlist in RULE-185..188. Admin raw audit is a separate authorized projection.
