# Runtime Conformance Plan 1.0 Contract

`joewrks.runtime-conformance-plan/1.0` is deterministic verification metadata for one valid `joewrks.action-conformance/2.1` semantic contract. It is not Product Definition authority and cannot repair missing product meaning.

## Inputs and identities

`materialize_runtime_plan(contract, draft, *, review_package=None, review_output=None)` accepts only a valid action-conformance/2.1 contract, a draft containing only `actions` and `lifecycles`, and exact semantic-review/2.1 artifacts when review applies. It never accepts or reads `state.json`, M4 evidence, an Approval Manifest, or unconsumed Product Definition evidence.

Every materialized plan binds the semantic contract hash, approved definition digest, product slug, frozen runtime-responsibility/1.0 digest, planner identity, and supplied review artifact identities. `review_commitments.output_hash` is the canonical SHA-256 of the complete validated review output, including that output's own normative `output_hash` field. Review completion never changes `reliability_status = NOT_MEASURED`.

## Frozen coverage profile

The profile classifies action fields as `RUNTIME_CRITICAL`, `NON_RUNTIME_PRESENTATION`, or `ASSURANCE_ONLY`. Every lifecycle semantic field is `RUNTIME_CRITICAL`. The JSON profile is exact, digest-bound, and not caller-overridable.

Coverage is computed only from concrete case relationships: result expectations, `CHANGED` or `UNCHANGED` component expectations, evidence assertions, and lifecycle transition expectations. A bare field reference and an `ANY` component expectation never count. Missing runtime-critical coverage produces `RUNTIME_MAPPING_GAP` with remediation `RUNTIME_PLAN`; it never creates Product Definition re-entry data or a canonical unknown.

## Expected values and fixtures

Product-specific equality values must use either:

- `CONTRACT_DERIVED`, with an exact same-item semantic field path and resolvable pointer; or
- `VERIFICATION_BASIS`, with an exact seed committed by the same action's verification basis and present in the consumed contract inventory.

Lifecycle from/to state sources are always `CONTRACT_DERIVED`. Direct expected values are forbidden. Fixture requirements contain category names only: `OPAQUE_ID`, `ATTEMPT_ID`, `ORDERING_TIMESTAMP`, or `REVISION_INSTANCE`. They carry no values and cannot define states, thresholds, durations, permissions, actors, or policy.

## Review gate and identity

A mapped runtime-critical field whose semantic derivation is `REVIEW_REQUIRED` remains in `review_blocked_field_refs` until the exact bound semantic-review/2.1 obligation has `CONFIRMED_INTERPRETATION`. Rejected review completion records `REENTRY_REQUIRED`; it is not rewritten as a runtime mapping workaround.

Case and test IDs are derived from canonical normalized case content plus the owning action or lifecycle identity before IDs are inserted. Test IDs are globally unique within one plan. `plan_hash` is the canonical SHA-256 of the complete plan without `plan_hash`, so cases, result classes, component expectations, assertions, fixtures, computed coverage, mapping gaps, and review commitments all affect identity. A plan change never rewrites the source semantic contract hash or approved definition digest.

`validate_runtime_plan()` recomputes the complete deterministic plan from the supplied valid contract and exact review artifacts. Any identity, coverage, assertion, case, or hash weakening is rejected.
