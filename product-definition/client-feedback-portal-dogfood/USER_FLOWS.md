# USER FLOWS

> `state.json` projection, revision 44, CLOSED and explicitly approved.

## FLOW-002

Designer requests, receives, consumes, resends, and recovers provider-neutral email magic-link authentication and session.

- Actors: USR-001
- Screens: SCR-002
- Requirements: REQ-002
- Acceptance: AC-002

## FLOW-003

Designer enters project list, creates or opens one project, and reaches project detail.

- Actors: USR-001
- Screens: SCR-003, SCR-004
- Requirements: REQ-003
- Acceptance: AC-003

## FLOW-004

Designer validates a file, capacity, and attempt ID, then creates one immutable DRAFT Version or recovers without a phantom/duplicate Version.

- Actors: USR-001
- Screens: SCR-004, SCR-005
- Requirements: REQ-004
- Acceptance: AC-004

## FLOW-005

Designer sends, rotates, resends, or revokes the one active 30-day project review link; Reviewer access is blocked by expiry, revoke, or archive.

- Actors: USR-001, USR-002
- Screens: SCR-006, SCR-007
- Requirements: REQ-005
- Acceptance: AC-005

## FLOW-006

Reviewer pins an exact Version and both actors use append-only threads under locked resolve/reopen rules.

- Actors: USR-001, USR-002
- Screens: SCR-007
- Requirements: REQ-006
- Acceptance: AC-006

## FLOW-007

Reviewer approves or requests changes for the viewed exact Version with expected revision and an idempotent attempt ID.

- Actors: USR-002
- Screens: SCR-008
- Requirements: REQ-007
- Acceptance: AC-007

## FLOW-008

Designer archives/unarchives a project and inspects role-scoped embedded histories; old links never return.

- Actors: USR-001
- Screens: SCR-004, SCR-009
- Requirements: REQ-008
- Acceptance: AC-008
