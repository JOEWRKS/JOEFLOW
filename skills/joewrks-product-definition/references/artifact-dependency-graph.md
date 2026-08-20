# Artifact Dependency Graph

Store explicit `depends_on` and semantic mappings in `state.json`. Typical propagation is `DEC → REQ/RULE → FLOW → SCR/STATE/DATA → AC → TASK`.

When a decision changes:

1. Increment `definition_revision` and replace approval with an unapproved record before any recompilation.
2. Preserve the old decision as `SUPERSEDED` and create/link the replacement when history requires it.
3. Traverse every direct and transitive dependent.
4. Mark affected active objects `STALE` before editing projections.
5. Recompile each object against the new decision and set it `CURRENT` only after its mappings and acceptance criteria are reconciled.
6. Rerun structure and closure validation; the new revision requires new user approval.

Do not clear `STALE` merely because text was touched. The object must be checked against all current upstream IDs. Dependency cycles and broken references are structural failures.
