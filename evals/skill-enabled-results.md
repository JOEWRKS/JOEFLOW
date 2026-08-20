# Skill-enabled Evaluation Results

Status: `v0.1.1 DETERMINISTIC CONTRACT VERIFIED; AGENT BEHAVIOR NOT RUN`

Verified locally:

- State validator accepts a well-formed graph and rejects duplicate IDs, invalid statuses, broken references, and dependency cycles.
- Closure validator accepts the closed fixture and blocks open material unknowns, open decisions, stale artifacts, contradictions, coverage gaps, orphan mappings, unmapped tasks, and missing approval.
- Closed, open, stale, and broken-reference fixtures exercise the packaged CLI entrypoints.
- Package structure, default discovery metadata, and standard-library-only validator imports are checked.
- Feature coverage requires all 20 dimensions and one row per requirement; missing dimensions are counted as gaps.
- Every screen requires all state and action axes; missing axes and unjustified `N/A` values fail validation.
- Empty definitions, stale approvals, non-canonical groups/versions, mistyped IDs/edges, and unsupported escape hatches fail validation.
- `state.schema.json` and `state.example.json` provide the canonical authority contract.

Not verified in this run: fresh-agent behavioral compliance for EVAL-01 through EVAL-06, non-target prompt false-positive rate, Figma-native frame generation, and Figma Make drift audit against a generated prototype.
