# State 0.2.0 foundation boundary

state 0.2.0 is parallel to, not an in-place replacement for, legacy 0.1.2.1.
legacy 0.1.2.1 validation remains frozen. LEGACY_CLOSURE remains governed by the frozen legacy contract.

M1 validates V2 top-level shape, typed semantic minima, lifecycle, IDs, and migration planning.
M1 does not claim V2 Semantic Closure. `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M1` is the explicit M1 boundary.
`validate_closure` on 0.2.0 returns `semantic_closure_not_implemented = 1` and `closed = false`.

`migrate_state.py --plan` emits `FOUNDATION_PLAN_ONLY` and never manufactures V2 authority.
The M1 closure guard may be removed only by a later milestone that implements and verifies its frozen gate.

## M2 discovery authority boundary

M2 adds evidence, discovered surface, contradiction, reverse-bootstrap, and
deterministic discovery-baseline authority rules. The authoritative M2 detail
is the [M2 discovery authority contract](discovery-contract-v0.2.0.md).

M2 does not remove the M1 Closure guard. `SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M2`
means `validate_closure` still reports `closed = false`, `definition_digest = null`,
and `semantic_closure_not_implemented = 1` until the frozen V2 Closure gate is
implemented and verified by a later milestone.
