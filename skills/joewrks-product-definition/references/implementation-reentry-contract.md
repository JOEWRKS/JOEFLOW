# Implementation re-entry contract — M5

Normative markers:

```text
AMBIGUITY_FOUND
CONTRACT_CONFLICT
OUT_OF_SCOPE_REQUEST
AFFECTED_ONLY
CANDIDATE_UNKNOWN_IS_NOT_CANONICAL_AUTHORITY
REENTER_PRODUCT_DEFINITION
NO_SILENT_IMPLEMENTATION_PRODUCT_DECISIONS
```

## When implementation work returns upstream

Implementation or contract audit returns to Product Definition when it encounters one of three product-authority conditions:

- `AMBIGUITY_FOUND`: the approved material does not give one authoritative meaning needed by the affected field.
- `CONTRACT_CONFLICT`: a selected authority conflicts with the field contract, or a used seed or declared scope commitment has drifted.
- `OUT_OF_SCOPE_REQUEST`: the requested behavior is outside the approved Product Definition scope.

These are Product Definition questions. Implementation must not silently choose a product answer, reinterpret evidence, turn an authority gap into review work, allocate a canonical unknown ID, or modify approval.

## Affected-only scope

Every re-entry event uses `AFFECTED_ONLY`. Its halt scope names only the action and lifecycle IDs that consume the missing, conflicting, or changed dependency. Unrelated actions and lifecycles remain outside the halt scope when their committed dependencies still verify.

An existing-contract audit therefore checks its exact consumed seeds and scope commitments. It does not require the current whole Product Definition to remain CLOSED. If the current state cannot be safely inspected, the audit reports `DEFINITION_NOT_READY` without pretending it knows which semantic dependency changed.

## Read-only proposal

A re-entry artifact is a deterministic proposal for upstream work. Its `candidate_unknown` describes the affected authority and the authority class needed to resolve it, but it is not canonical Product Definition authority. It has no `UNK-*` identity and does not become authoritative merely because the artifact exists.

The artifact does not write Product Definition state, increment a revision, change approval, mutate the action contract, or decide a replacement value. Product Definition owns the later decision and any canonical unknown or authority record. After that upstream work is approved and CLOSED, a new compilation may produce a new contract; the M5 artifact itself performs no such transition.

This boundary is the M5 `REENTRY_PROTOCOL`. Runtime routing and product adoption remain outside M5 and belong to M6.
