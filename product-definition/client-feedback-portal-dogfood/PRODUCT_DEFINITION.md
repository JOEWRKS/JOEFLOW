# PRODUCT DEFINITION — Client Feedback Portal Dogfood

> `state.json` projection, revision 44, `CLOSED`. Explicitly approved at `2026-08-20T23:57:59.2571768+09:00` with digest `2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1`.

## Objective, roles, and scope

One email-authenticated freelance Designer manages projects and immutable design Versions. One designated accountless Client Reviewer per project uses the active project-scoped link to annotate an exact Version and approve or request changes. Designer alone manages projects, files, links, archive, and thread resolution. Client alone creates pins and makes Version decisions; both may reply.

## Traceable requirements

| Requirement | Capability | Screens | Acceptance |
|---|---|---|---|
| REQ-002 | Designer magic-link authentication and session | SCR-002 | AC-002 |
| REQ-003 | Designer project list/detail | SCR-003, SCR-004 | AC-003 |
| REQ-004 | Immutable upload, Version, capacity and recovery | SCR-004, SCR-005 | AC-004 |
| REQ-005 | Designer-managed link lifecycle and Client Reviewer access/session | SCR-006, SCR-007 | AC-005 |
| REQ-006 | Designer/Client exact-Version canvas, pins and append-only threads | SCR-007 | AC-006 |
| REQ-007 | Exact-Version approval and changes request | SCR-008 | AC-007 |
| REQ-008 | Archive, unarchive and embedded object history | SCR-004, SCR-009 | AC-008 |

Each active REQ records its full DEC and RULE IDs in `state.json` and maps to a dedicated coverage row and TASK.

## Locked semantics

- Designer login link: 15-minute, single-use, resend rotation; session expires after 30 absolute days or 7 idle days.
- Review link: one active project-scoped link, **30-day expiry under DEC-015**. DEC-011 is historical `SUPERSEDED` 7-day policy only.
- PNG/JPG/JPEG/PDF, 100MB each, lazy PDF pages, immutable new Version per file, no replacement or phantom/duplicate Version.
- No workspace project/storage cap; 50 active files per project. At limit only upload is blocked; view/download/archive and archive-based recovery remain.
- Image pins store normalized x/y; PDF adds page number. Threads and approval history are append-only; approved Versions are read-only and irreversible.
- Expected Version revision and client attempt IDs prevent stale or duplicate file/message/decision/history/email mutations.
- Archive blocks Reviewer access. Unarchive never restores an old link; a new review request is required.

## Non-goals

No collaborators, multiple/replacement reviewers, public anonymous links, billing/payment/refund, realtime notification center, hard delete/retention expiry, integrated audit screen, Figma import, video review, or project-level approval state.

## Acceptance and recovery

AC-002–AC-008 are authoritative. Success appears only after authoritative confirmation. Unsupported/oversize/limit failures create no Version; ambiguous retries reuse attempt IDs; conflicts show latest state; expired/revoked/archive access blocks the next request; eligible comment drafts are preserved locally for recovery.
