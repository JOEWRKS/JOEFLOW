# Closure Gate

Run structure validation before closure validation. Closure requires all metrics below to equal zero:

- `blocking_unknowns`
- `open_material_decisions`
- `contradictions`
- `stale_artifacts`
- `coverage_gaps`
- `orphan_requirements`
- `orphan_screens`
- `orphan_acceptance_criteria`
- `unmapped_implementation_tasks`
- `missing_user_approval`

Lifecycle: `OPEN` → `READY_FOR_REVIEW` → `CLOSED`, or `BLOCKED`. Before approval, a mechanically clean definition is only `READY_FOR_REVIEW`. Record explicit approval in `project.user_approved`, rerun both validators, and only then report closure.

If Python is unavailable, perform the same deterministic checklist manually and record `validator_available: false`; never call that mechanically validated.

