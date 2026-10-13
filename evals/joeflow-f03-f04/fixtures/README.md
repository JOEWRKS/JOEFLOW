# F03/F04 executable examples

These are synthetic contract examples, not product approval or semantic-review authority.

- `f03/ready-for-review-candidate.json` and `f03/output-pass.json`: a review-ready, unapproved candidate and its successful read-only preflight.
- `f03/malformed-candidate.json` and `f03/output-error.json`: a malformed candidate and its structured failed preflight.
- `f04/audit-input-pass.json` and `f04/output-pass.json`: both required projections are materialized and bound to current synthetic review records.
- `f04/audit-input-partial.json` and `f04/output-partial.json`: one projection remains explicitly `UNKNOWN` / `PENDING`, with `findings: null` and a scoped recovery action.

The recorded outputs preserve the absolute worktree paths observed during this implementation run. Reruns may differ only in path-bearing and input-identity fields when moved to another checkout.
