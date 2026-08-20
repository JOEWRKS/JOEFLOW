# Product Coverage Matrix

For every material feature review: actor, goal, entry point, precondition, happy path, alternative path, error, recovery, permission, state, data, side effect, notification, validation, boundary, persistence, security, privacy, analytics, and acceptance.

Every required key must exist and contain `{ "status": "COVERED" }`, `{ "status": "OPEN" }`, or `{ "status": "N/A", "rationale": "..." }`. Missing keys, blank cells, invalid values, and `N/A` without rationale are invalid. Any `OPEN` cell for a material feature blocks closure.

Audit requirements without acceptance criteria or screens, screens without requirements/flows, acceptance criteria without requirements, and tasks without upstream/acceptance mappings.
