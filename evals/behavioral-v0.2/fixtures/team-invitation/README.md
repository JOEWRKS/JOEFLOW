# Acme Teams fixture

The service uses session authentication. `request.user_id` is always the authenticated user ID. A workspace has members with roles `OWNER`, `ADMIN`, or `MEMBER`. Existing API handlers use repository functions from `src/repository.md` and outbound email through `src/email-service.md`.

The current workspace plan limit is 25 accepted members. Product documentation does not state whether pending invitations consume this limit. No invitation feature exists yet.
