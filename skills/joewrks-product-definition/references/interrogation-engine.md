# Interrogation Engine

Run a loop: discover evidence → register unknown → rank materiality → ask → record decision → propagate impact → discover again.

## Evidence discovery

Inspect repositories, docs, tests, API contracts, schemas, design systems, Figma, prior specifications, business rules, observed behavior, and official integration constraints. Record source paths/URLs and observation dates. Ask humans only for judgments or facts unavailable from evidence.

## Ranking

Rank by: fan-out; security/money/privacy/irreversibility; core flow; business rule; state/recovery; secondary preference; cosmetic preference. Ask one high-leverage material question at a time.

Each material question states: question, why it matters, evidence, affected IDs/artifacts, mutually exclusive options, recommendation, and consequences. Comparison probes or low-fi wireframes are preferred when the user knows a preference tacitly but cannot express it in prose.

After every answer, write the decision first, mark dependents stale, update projections, and search for new unknowns. Never batch unrecorded answers in conversation memory.

