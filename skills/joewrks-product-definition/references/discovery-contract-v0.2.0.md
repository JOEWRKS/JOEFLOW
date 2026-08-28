# State 0.2.0 discovery authority contract

**Milestone status:** `DISCOVER_AUTHORITY_IMPLEMENTED_M2`

This reference defines the M2 discovery boundary for state 0.2.0. It records
what discovery evidence can establish, what it cannot establish, and what must
remain explicit before product meaning can be treated as canonical authority.

## Evidence authority

Evidence records prove only the authority classes that their `source_kind` is
allowed to support. A source that proves observed behavior does not therefore
prove intent, preference, or policy.

`INFERRED_INTENT` is candidate-only evidence. It can identify a candidate for
review, but cannot independently close product intent. `DESIGN_ARTIFACT` is
also candidate-only until corroborated by closure-eligible intent authority or
a current explicit decision.

`OBSERVED_IMPLEMENTATION_IS_NOT_INTENT`: existing implementation, runtime
behavior, and test behavior are observations of what currently exists. They
are not automatically product intent and cannot silently become canonical
authority.

## Discovered product surface

Every material discovered surface must have an explicit disposition:

- `IN_SCOPE` binds to current product-definition authority.
- `OUT_OF_SCOPE` records a meaningful intent or decision basis; absence from
  the implementation is not that basis.
- `OPEN` points to an unknown that describes what remains unresolved.
- `SUPERSEDED` or `RETIRED` records the applicable replacement or retirement
  authority.

Resolved material contradictions identify either the decision that resolved
them or the selected current, closure-eligible authority. Recording that a
contradiction was noticed without selecting or deciding authority is not
resolution.

## Reverse bootstrap

For an existing product, reverse bootstrap first classifies observed surfaces
as `AUTHORITATIVE`, `OBSERVED_ONLY`, `CONFLICTING`, or `UNEXPLAINED` before
canonical intent is granted. `AUTHORITATIVE` requires valid current product
intent authority. Material `OBSERVED_ONLY` and `UNEXPLAINED` surfaces remain
unknowns or reconciliation work; they do not become requirements merely
because they were found in code, runtime, or tests.

## Discovery baseline and M2 limit

The discovery baseline is a deterministic record of the defined discovery
procedure against its current evidence and surface topology. It can become
stale when those commitments materially change; a baseline is procedural
evidence of completion, not a claim that future discovery is impossible.

`UNKNOWN_UNKNOWN_EXHAUSTIVENESS_NOT_CLAIMED`: M2 makes no universal
unknown-unknown exhaustiveness claim.

`ACTIVE_GRILL_PACKS_NOT_IMPLEMENTED_IN_M2`: M2 does not activate Grill Packs
or claim active Grill Pack completeness.

`SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M2`: M2 does not implement V2 Semantic
Closure. The M1 Closure guard remains active: closure stays false, the
definition digest stays null, and `semantic_closure_not_implemented = 1`
until a later milestone implements and verifies the frozen closure gate.
