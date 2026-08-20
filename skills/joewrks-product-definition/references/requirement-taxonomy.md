# Requirement Taxonomy

Compile continuously: problem, goals, non-goals, users, actors, jobs, scope, features, business rules, policies, permissions, roles, data ownership/lifecycle, integrations, constraints, non-functional requirements, and acceptance criteria.

Stable ID prefixes: `GOAL`, `USR`, `REQ`, `UNK`, `DEC`, `RULE`, `FLOW`, `SCR`, `STATE`, `DATA`, `INT`, `AC`, `TASK`. Use three-digit monotonic suffixes. Deleted objects become `SUPERSEDED`; IDs are never reused.

Each requirement states actor-visible behavior, dependencies, screens, rules, data, and acceptance IDs. Each acceptance criterion is observable and maps back to at least one requirement. Each implementation task maps to upstream requirement/rule/decision and acceptance IDs.

