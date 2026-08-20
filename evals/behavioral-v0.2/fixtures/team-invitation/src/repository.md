# Repository contract

`workspace_members(workspace_id, user_id, role, joined_at)` has a unique key on `(workspace_id, user_id)`.

Available functions:

- `getWorkspace(workspaceId)` returns active or deleted status.
- `getMembership(workspaceId, userId)` returns the current role.
- `countAcceptedMembers(workspaceId)` counts accepted members.
- `findUserByVerifiedEmail(email)` returns a user only for a verified normalized email.

There is no invitation table or token contract yet.
