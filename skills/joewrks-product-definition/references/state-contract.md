# Canonical State Contract v0.1.2.1

`state.json` is authoritative; Markdown is projection only. Start from `templates/state.example.json`; the structural contract is `schemas/state.schema.json`, while the standard-library Python validator is the semantic authority.

`project` owns `definition_revision`, `user_approved`, and approval metadata. The definition digest excludes only `project.status`, `project.user_approved`, and `project.approval`; all product objects, coverage, UX coverage, contradictions, and remaining project fields are hashed using sorted compact UTF-8 JSON and SHA-256.

All 13 object groups are required and IDs must match their group prefix. `CURRENT` and `STALE` objects are active; `SUPERSEDED` objects are historical. Only active objects participate in minimum-definition, coverage, UX, orphan, and task-completeness metrics. Historical objects still participate in ID uniqueness, reference integrity, and same-type supersession checks.

The minimum definition is one active goal, one active material requirement, and one active acceptance criterion. Users, decisions, flows, screens, and tasks are required only when the product actually needs them. Screenless semantics are requirement-level: an active requirement may omit screens only when `REQ.ui_required` is `false` and `REQ.no_screen_reason` is meaningful. UI and non-UI requirements may coexist in one project; a genuinely screenless product has only valid non-UI requirements, with `screens` and `ux_coverage` empty.

Every active material requirement requires exactly one complete 20-axis coverage row. Screens default to `interactive: true`; a non-interactive screen requires `non_interactive_reason` and no UX coverage row. For an interactive screen, `screens[].major_actions` is authoritative and must exactly equal the unique `ux_coverage[].actions[].key` set. An empty action inventory requires `screens[].no_major_actions_reason`.

Closed unknowns and decisions require status-specific evidence. `ASSUMED_ACCEPTED` is valid only with `accepted_by: "user"`. `DEFERRED_NON_BLOCKING` requires a non-empty, non-placeholder reason and explanatory strings for all eight impact axes: scope, rules, flows, states, privacy, money, security, and acceptance. `SUPERSEDED` requires an existing same-type `superseded_by` target; self-reference and cycles are invalid.

Closure coverage completeness evaluates rows for active material requirements only. Historical coverage rows remain subject to structural, reference, and cell validation, but their OPEN or missing axes do not create current `coverage_gaps`.

Any material change increments the revision and invalidates approval. Closure requires `CLOSED`, explicit user approval, matching revision and digest, an approval timestamp, no semantic errors, and zero blocker metrics.
