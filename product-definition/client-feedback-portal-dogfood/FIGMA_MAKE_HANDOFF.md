# FIGMA MAKE IMPLEMENTATION CONTRACT

Figma visualization: **NOT VERIFIED**. Product definition revision 44 is CLOSED and explicitly approved with digest `2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1`.

## Objective and scope

Design the responsive v1 workflow defined by REQ-002–REQ-008: Designer authentication, project list/detail, immutable upload/version history, review-link management, role-qualified review canvas/thread, exact-Version decision, archive, and embedded history. Do not add any non-goal from `state.json`.

## Roles and permissions

Designer is the sole authenticated Workspace Owner. Client Reviewer is the one designated email identity for a project and has no account. Designer enters SCR-007 from authenticated project detail; Client enters through the active project link. Only Client creates pins and decides a Version; both roles reply; only Designer resolves. Client reply reopens a resolved thread, while Designer reply preserves resolved state.

## Locked decisions

Use all active/current decisions and all current RULE/DATA records, excluding historical superseded records. Review links expire after **30 days under DEC-015**; never render historical DEC-011 as active. Designer session 7-day idle timeout is a separate authentication policy.

## Routes and screens

- SCR-002 `/login`: login request/resend/consume and session recovery.
- SCR-003 `/projects`: project list/create/open.
- SCR-004 `/projects/:projectId`: project and Version detail, capacity and archive.
- SCR-005 `/projects/:projectId/versions/new`: immutable upload and recovery.
- SCR-006 `/projects/:projectId/review-access`: send/resend/revoke review access.
- SCR-007 Designer `/projects/:projectId/versions/:versionId/review`; Client `/review/:token/versions/:versionId`: viewer, pins and threads.
- SCR-008 `/review/:token/versions/:versionId/decision`: approval or evidence-backed changes request.
- SCR-009 `/projects/:projectId/history`: embedded histories and unarchive.

## Flows, states, and actions

Implement FLOW-002–FLOW-008 with their recorded actors; authentication, project navigation, upload, and archive are Designer-only. Cover all 16 screen states and all 22 axes per authoritative `major_actions`. Never show success during ambiguous timeout. Show loading, empty, partial, disabled, permission, unauthenticated, offline, retrying, conflict, expired/revoked/archive, notification-failure, and capacity-limit states.

## Version, approval, comment, and data semantics

Each successful file creates a new immutable exact Version. Multiple Versions may independently be IN_REVIEW; no project approval state exists. APPROVED file/ID/actor/timestamp and discussions are immutable/read-only. Pins bind exact Version coordinates; PDF adds page. Threads are append-only and non-editable/deletable. Attempt IDs and expected revisions prevent duplicate or stale effects. Raw tokens are not stored; lifecycle metadata only, without per-request IP/device logs.

## Validation and failure recovery

Accept PNG/JPG/JPEG/PDF up to 100MB and render PDF pages lazily. Reject unsupported, oversize, failed, duplicate, or 50-active-file-limit upload without Version creation. At the limit keep view/download/archive and show archive-based recovery. Separate email delivery failure from resend. Expiry, revoke and archive block all sessions on the next request. Preserve eligible local comment drafts and retry after valid authentication/link. Notification retries must not duplicate domain history.

## Responsive and accessibility

Mobile supports pin creation with simplified precision. Provide keyboard navigation, visible focus, semantic labels, error association, non-color status communication, and accessible viewer-to-pin-to-thread relationships.

## Acceptance, deferred policies, and forbidden invention

Use AC-002–AC-008. Deferred PDF page-cap/performance and hard-delete/retention policies remain only within their recorded eight-axis reviews; invent neither caps nor deletion behavior. Do not invent roles, routes, fields, states, actions, notifications, business rules, navigation destinations, or recovery branches. Stop and return any missing choice to product definition.
