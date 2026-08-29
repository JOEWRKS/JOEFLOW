# State 0.2.0 foundation boundary

state 0.2.0 is parallel to, not an in-place replacement for, legacy 0.1.2.1.
legacy 0.1.2.1 validation remains frozen. LEGACY_CLOSURE remains governed by the frozen legacy contract.

M1 validated V2 top-level shape, typed semantic minima, lifecycle, IDs, and migration planning.
At that historical milestone, M1 did not claim V2 Semantic Closure.
`SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1` records that explicit M1 boundary; it is
not the current M4 runtime behavior.

`migrate_state.py --plan` emits `FOUNDATION_PLAN_ONLY` and never manufactures V2 authority.
The M1 closure guard may be removed only by a later milestone that implements and verifies its frozen gate.

## M2 discovery authority boundary

M2 adds evidence, discovered surface, contradiction, reverse-bootstrap, and
deterministic discovery-baseline authority rules. The authoritative M2 detail
is the [M2 discovery authority contract](discovery-contract-v0.2.0.md).

M2 did not remove the M1 Closure guard. `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M2`
records that historical milestone boundary. M4 now supersedes only that
temporary guard, not M2's evidence and discovery semantics.

## M3 Grill Engine boundary

M3 adds deterministic Materiality, unknown-resolution authority, selective
question projection, mandatory topology profiles, declarative Grill Packs, and
Grill-aware discovery baselines. The authoritative M3 detail is the
[M3 Grill Engine contract](grill-contract-v0.2.0.md).

M3 preserved the M1/M2 Closure guard. `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M3`
records that historical boundary; M3 did not itself claim closure.

## M4 Semantic Freeze boundary

M4 replaces the temporary guard with the actual state 0.2.0 Product Definition
Semantic Closure evaluator. Valid READY states expose their deterministic
definition digest, and only an exact approved CLOSED state with every frozen
M1–M4 blocker at zero returns `closed = true`.

The authoritative current detail is the
[M4 Semantic Freeze contract](semantic-freeze-contract-v0.2.0.md).
`SEMANTIC_CLOSURE_AVAILABLE_M4` means Product Definition closure is available;
it does not mean design, implementation, deployment, downstream 2.0, or M6
adoption is complete.
