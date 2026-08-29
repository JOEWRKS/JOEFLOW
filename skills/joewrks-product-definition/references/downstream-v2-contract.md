# Downstream V2 authority contract — M5

Status markers:

```text
DOWNSTREAM_V2_AUTHORITY_IMPLEMENTED_M5
ACTION_CONFORMANCE_2_0
SOURCE_SEEDS_FROM_M4_BINDINGS
SEMANTIC_AUTHORITY_GAP_REENTERS_PRODUCT_DEFINITION
REVIEW_REQUIRED_IS_ASSURANCE_NOT_AUTHORITY
AUTHORITY_GAP_COUNT_MUST_BE_ZERO
SEMANTIC_REVIEW_2_0_RELIABILITY_NOT_MEASURED
DOWNSTREAM_V1_REMAINS_FROZEN
M6_INTEGRATION_NOT_IMPLEMENTED_IN_M5
RUNTIME_CONFORMANCE_NOT_INTEGRATED_IN_M5
```

These markers mean only that M5 provides `DOWNSTREAM_V2_AUTHORITY`, `SEMANTIC_DEBT_CLASSIFICATION`, `REENTRY_PROTOCOL`, and `SEMANTIC_REVIEW_2_0_STRUCTURAL_BOUNDARY`. They do not certify an implementation or runtime, provide a reliability result, connect production adapters, calibrate review, or adopt the contract in deployed products.

## Initial authority admission

Compilation requires the source Product Definition to be actually CLOSED under the M4 evaluator, with zero Closure errors and a non-null definition digest that matches current approval. The compiler is read-only: it neither repairs Closure nor changes the source state or handoff definition.

The `joewrks.action-conformance/2.0` identity names this M5 authority contract. It does not assert that an implementation performs the described actions.

## Exact M4 sources and consumed-only seeds

M5 does not hand-pick record pointers. It builds the available seed pool only from positive, exact M4 binding cells: `COVERED` Core and UX cells and `ADDRESSED` Grill axes. Open unknowns, N/A basis bindings, unbound records, and arbitrary caller-supplied pointers are not source seeds.

Each compiled field references a deterministic seed key. A materialized contract stores only the sorted unique seeds that its successful fields consume. Unused available seeds and unconsumed evidence stay outside the contract's consumed-seed inventory and digest.

## Scope commitments and local drift

Every action and lifecycle declares its authority scope. The contract commits the exact current `REQ`, `SURF`, and `SCR` scope records it uses. A later audit checks the consumed seed locations and values plus those declared scope commitments.

Audit of an existing contract is dependency-scoped. The current whole Product Definition may be OPEN or on a newer revision while an old contract remains locally conformant, provided the state is safely inspectable and all of that contract's committed dependencies are exact. Changed unrelated evidence, bindings, or scope remain outside that contract's halt scope. A used seed or declared scope change requires affected-only re-entry.

## Semantic identity and snapshot identity

The approved Product Definition digest records semantic source provenance. The semantic contract hash commits that provenance, the responsibility profile, consumed seeds, scope commitments, fields, and debt. It intentionally excludes the full source snapshot hash.

The artifact hash includes the snapshot observation. Consequently, unconsumed evidence with a correctly rebuilt discovery baseline may change the snapshot and artifact hash while leaving the semantic contract hash stable. A snapshot difference alone is not semantic drift.

## Gaps, debt, and review

`DIRECT_AUTHORITY` copies an exact seed value. `MACHINE_DERIVED` uses only the closed `extract` or `select` operators. `REVIEW_REQUIRED` is allowed only for fields the responsibility profile marks `REVIEW_PERMITTED`.

A missing or conflicting product meaning is a `SEMANTIC_AUTHORITY_GAP`, not a review task. When `authority_gap_count` is greater than zero, compilation returns no contract and emits read-only re-entry proposals. An authority handoff materializes only when `authority_gap_count` is zero.

Review fields can remain in a materialized authority contract because they record assurance work over an already proposed value. Review cannot invent missing product authority, replace contract values, or change Product Definition state. For semantic-review/2.0, reliability is exactly `NOT_MEASURED` throughout M5, including after a structurally complete review output.

## Integration boundary

Downstream v1 and semantic-review v1/v0.4.3 remain frozen. M5 does not install this package, wire product adapters, execute implementation/runtime checks, deploy anything, calibrate semantic-review/2.0, or migrate production users. M6 owns installed routing, representative product dogfood, and end-to-end adoption of this authority boundary.
