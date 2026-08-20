# Canonical State Contract v0.1.1

`state.json` is authoritative; Markdown is projection only. Start from `templates/state.example.json`; the structural contract is `schemas/state.schema.json`, while the standard-library Python validator is the semantic authority.

`project` owns `definition_revision`, `user_approved`, and approval metadata. The definition digest excludes only `project.status`, `project.user_approved`, and `project.approval`; all product objects, coverage, UX coverage, contradictions, and remaining project fields are hashed using sorted compact UTF-8 JSON and SHA-256.

All 13 object groups are required and IDs must match their group prefix. Active material requirements require exactly one complete 20-axis coverage row. Interactive screens default to `interactive: true` and require UX state and major-action coverage; a screen with no major action needs `no_major_actions_reason`.

Any material change increments the revision and invalidates approval. Closure requires `CLOSED`, explicit user approval, matching revision and digest, an approval timestamp, no semantic errors, and zero blocker metrics.
