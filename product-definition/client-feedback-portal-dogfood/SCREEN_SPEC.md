# SCREEN SPEC

> `state.json` projection, revision 44, CLOSED and explicitly approved.

## SCR-002 — Designer Login (`/login`)

Designer-only email input, delivery result, resend, link-consume result, and session recovery. Actions: `request_login_link`, `resend_login_link`, `consume_login_link`. Distinguish delivery failure from resend; show expired/used/rotated link states and require a new link after session expiry.

## SCR-003 — Project List (`/projects`)

Authenticated Designer-only project collection with create/open actions, loading, empty, and retry states. No Client, collaborator, billing, project-count-cap, or storage-cap controls.

## SCR-004 — Project Detail and Versions (`/projects/:projectId`)

Designer-only project identity, Reviewer identity, Version list/state/history, active-file count, download, upload entry, and project archive. At 50 active files, preserve select/download/archive and direct upload recovery to archive capacity.

## SCR-005 — New Deliverable or Version (`/projects/:projectId/versions/new`)

Designer-only file picker and attempt progress. Actions: `upload_version`, `cancel_upload`, `archive_version_for_capacity`. Validate type, 100MB and capacity; no failure may create a phantom/duplicate Version. Timeout retry reuses the attempt ID.

## SCR-006 — Review Access Management (`/projects/:projectId/review-access`)

Designer-only exact-Version target, designated Reviewer email, active link lifecycle, send/resend/revoke outcomes. Actions: `send_review_request`, `revoke_review_link`, `resend_review_request`. Current expiry is 30 days; rotation leaves one active link.

## SCR-007 — Client Review Canvas

- Designer entry: `/projects/:projectId/versions/:versionId/review`
- Client entry: `/review/:token/versions/:versionId`
- Shared hierarchy: immutable image/PDF viewer, exact Version identity/state, pins, thread chronology and history.
- `create_pin`: Client Reviewer only.
- `reply_thread`: Designer or Client while mutable.
- `resolve_thread`: Designer only; hidden or disabled with explanation for Client.
- Client reply to a resolved thread reopens it; Designer reply leaves it resolved.
- Expired/revoked/archive Client access blocks reads/writes and preserves eligible local draft text.

## SCR-008 — Version Decision (`/review/:token/versions/:versionId/decision`)

Designated Client Reviewer only. Shows exact Version identity, expected revision, unresolved pins, overall change reason, `approve_version`, and `request_changes`. Changes request requires evidence. Conflict shows latest state; idempotent retry cannot duplicate history/email; APPROVED is irreversible.

## SCR-009 — Archive and History (`/projects/:projectId/history`)

Designer-only embedded Version/thread/approval/link/archive histories and `unarchive_project`. Archive blocks all Reviewer sessions; unarchive preserves history but never restores a link.

## Shared state and interaction contract

Every screen covers Default, Loading, Empty, Partial, Success, Error, Disabled, Permission denied, Unauthenticated, Offline, Timeout, Retrying, Submitting, Completed, Cancelled, and Expired. Every listed action covers all 22 interaction axes in `state.json`. Success requires authoritative confirmation; errors preserve eligible input and expose the applicable retry, reauthentication, link renewal, archive, or conflict recovery.
