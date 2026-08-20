# Artifact Dependency Graph

Store explicit `depends_on` and semantic mappings in `state.json`. Typical propagation is `DEC → REQ/RULE → FLOW → SCR/STATE/DATA → AC → TASK`.

When a decision changes:

1. Preserve the old decision as `SUPERSEDED` and create/link the replacement when history requires it.
2. Traverse every direct and transitive dependent.
3. Mark affected active objects `STALE` before editing projections.
4. Recompile each object against the new decision and set it `CURRENT` only after its mappings and acceptance criteria are reconciled.
5. Rerun structure and closure validation.

Do not clear `STALE` merely because text was touched. The object must be checked against all current upstream IDs. Dependency cycles and broken references are structural failures.

