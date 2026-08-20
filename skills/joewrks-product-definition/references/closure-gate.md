# Closure Gate

Run structure validation before closure validation. Closure requires all metrics below to equal zero:

- `blocking_unknowns`
- `open_material_decisions`
- `contradictions`
- `stale_artifacts`
- `coverage_gaps`
- `minimum_definition_gaps`
- `screen_state_gaps`
- `screen_action_gaps`
- `orphan_requirements`
- `orphan_screens`
- `orphan_acceptance_criteria`
- `unmapped_implementation_tasks`
- `missing_user_approval`
- `stale_approval`
- `invalid_closed_status`

Completeness metrics use active objects only (`CURRENT` and `STALE`). `SUPERSEDED` records are retained as history and must remain structurally referentially valid, but cannot satisfy the minimum definition or create current coverage, UX, orphan, or task obligations.

Lifecycle: `OPEN` → `READY_FOR_REVIEW` → `CLOSED`, or `BLOCKED`. Before approval, a mechanically clean definition is only `READY_FOR_REVIEW`. Record explicit approval in `approval`; `approved_revision` must equal the positive integer `definition_revision`, and project status must be `CLOSED`. Any material change increments the revision and clears approval. Rerun both validators before reporting closure.

If Python is unavailable, perform the same deterministic checklist manually and record `validator_available: false`; never call that mechanically validated.
