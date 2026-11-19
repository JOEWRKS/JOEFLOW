# Core Semantic Closure V2 — M5 Plan Self-Review Clarifications

**Status:** `NORMATIVE_PLAN_CLARIFICATION`

**Applies to:** `docs/superpowers/plans/2026-08-29-core-semantic-closure-v2-m5-downstream-v2.md`

Where this addendum conflicts with the M5 plan, this addendum controls. The frozen Core Semantic Closure V2 design remains the higher authority.

## 1. Full M4 seed inventory is a compile-time pool; the contract commits only consumed seeds

The main plan initially describes placing `source_seed_inventory` and its digest into the contract after building all positive M4 bindings. Committing the **entire** M4 positive seed inventory would over-invalidate downstream work: a new binding in an unrelated feature would change every contract even when none of its fields use that seed.

Freeze two separate concepts:

```python
available_seed_inventory = build_source_seed_inventory(state)
consumed_seed_inventory = seeds actually referenced by successfully derived fields
```

Compilation uses the full available inventory to resolve handoff-definition field specs, but a materialized `joewrks.action-conformance/2.0` contract stores only the sorted unique `consumed_seed_inventory`.

Rename the semantic authority commitment inside a production contract to:

```text
consumed_seed_inventory_digest
```

and compute it from the exact consumed subset.

Consequences:

- unused positive M4 bindings do not enter a contract merely because they exist elsewhere in Product Definition;
- unconsumed evidence remains absent as already required;
- an unrelated new Core/Grill/UX positive binding does not alter an existing contract's semantic hash;
- every `source_seed_ref` in every semantic field must resolve exactly once inside the contract's consumed seed inventory;
- no unreferenced seed may remain in a production contract.

Add tests proving unused available seeds are absent from the materialized contract and from `consumed_seed_inventory_digest`.

## 2. Declare and commit action/lifecycle authority scope records

Consumed seeds alone are not sufficient for dependency-scoped drift. A Product Definition requirement/surface/screen may change materially while a particular bound value happens to remain byte-identical.

Every action/lifecycle already declares `authority_scope_refs`. Materialized contracts must also commit the exact current canonical record for every declared scope ref.

Add a top-level sorted unique array:

```python
"scope_commitments": [
    {
        "record_id": "REQ-001",
        "record_type": "REQ",
        "record_sha256": "<sha256 canonical entire record>"
    }
]
```

Allowed scope record types remain exactly:

```text
REQ
SURF
SCR
```

All scope records must be `CURRENT` at initial compilation.

Every action/lifecycle keeps its `authority_scope_refs`; a later audit can therefore map a changed scope commitment back only to the actions/lifecycles that consume that scope.

`scope_commitments` and their deterministic digest are part of `semantic_contract_hash`.

Required tests:

- changing an unrelated REQ/SURF/SCR not present in the contract scope does not affect local drift status;
- changing a declared scope record causes only consumers of that scope to become affected;
- retiring/superseding a declared scope record is an affected semantic change even when one old seed value still exists elsewhere;
- duplicate/missing scope commitments are invalid.

## 3. Global approved definition digest is source provenance, not the sole drift-invalidating key

`source_authority.approved_definition_digest` remains in every contract. It identifies the exact approved Product Definition revision from which the artifact was compiled and remains part of the immutable artifact's semantic hash.

However, during **audit of an already compiled contract**, a newer current Product Definition digest or revision does not by itself invalidate the old contract.

This is required by the frozen rule that unaffected in-flight work may continue after a dependency-scoped Product Definition re-entry.

Audit must distinguish:

```text
source revision/digest provenance
vs.
current local dependency compatibility
```

If the current Product Definition has a newer/different global digest but:

- all binding-contract identities used by the contract are compatible;
- every consumed source seed still resolves at the exact same semantic location with the exact same hash/status;
- every declared REQ/SURF/SCR scope commitment still matches;

then the existing contract remains `CONFORMANT` for its declared scope.

Include audit metadata:

```text
authority_revision_relation = SAME_APPROVED_REVISION | OLDER_APPROVED_REVISION_UNAFFECTED
```

Do not rewrite the contract's original approved digest to the new digest. A fresh recompile under the new revision would naturally produce a new artifact identity; the old artifact remains valid only because local dependencies proved unchanged.

## 4. Drift audit of an existing contract does not require the whole current Product Definition to be CLOSED

Initial compilation still requires an M4 `closed = true` source.

An existing contract audit is different. During a new Product Definition revision, the whole project may legitimately be `OPEN` or `READY_FOR_REVIEW` while unaffected authority remains current and byte-identical.

Freeze the audit algorithm:

1. Parse/structurally validate the current state and require a safe unique canonical record index.
2. Read the current M4 binding-contract identities.
3. Rebuild the currently available positive seed inventory **without requiring global Closure**.
4. Verify every consumed contract seed against its exact current semantic location.
5. Recompute every declared scope commitment.
6. Map changed seeds/scope commitments to their consuming actions/lifecycles.

Results:

### `CONFORMANT`

Return `CONFORMANT` when local dependencies remain exact, even if current `project.definition_status != CLOSED` or the global definition revision/digest is newer. Include `global_definition_closed: false` when applicable; do not pretend the whole current definition is closed.

### `DEFINITION_NOT_READY`

Use only when the current canonical state cannot be safely inspected—for example duplicate stable IDs, malformed binding structures, unsafe semantic projection, or other structural validation errors that make local dependency verification unreliable.

This pauses the contract. It does not manufacture a semantic re-entry event because the system cannot safely attribute the change.

### `REENTRY_REQUIRED`

Use when current state is inspectable but at least one consumed semantic dependency actually changed, disappeared, became non-current, changed binding identity/location, or a declared scope commitment changed.

This emits dependency-scoped `CONTRACT_CONFLICT` events.

A stale discovery baseline or unrelated OPEN unknown alone is not a reason to invalidate an old contract when its local semantic dependencies still verify.

## 5. Responsibility profile must carry the authority class needed for re-entry

A compiler-generated `SEMANTIC_AUTHORITY_GAP` needs enough information to propose what kind of authority Product Definition must recover. The main plan's responsibility profile specifies expectation and allowed seed selectors but not the required authority class.

Every responsibility entry must therefore contain exactly:

```text
expectation
required_authority_class
allowed_seed_selectors
```

Freeze authority classes:

- every action field except `visible_success` and `visible_error` → `INTENT`;
- `visible_success` → `PREFERENCE`;
- `visible_error` → `PREFERENCE`;
- every lifecycle field → `INTENT`.

An explicit `UNRESOLVED` input may declare another valid authority class when the caller knows the gap is factual/constraint/behavioral. Compiler-generated gaps caused by missing/wrong derivation use the profile's required authority class.

The resulting re-entry `candidate_unknown.required_authority_class` is therefore deterministic and never guessed from prose.

Add tests for profile authority-class completeness and generated candidate-unknown class parity.

## 6. Source seed inventory building and closed-source admission are separate operations

Task 1 must not bake `closed = true` into `build_source_seed_inventory()` itself, because Task 4 needs to inspect local positive bindings in a structurally valid in-progress current revision.

Freeze APIs as:

```python
def build_source_seed_inventory(state: dict[str, object]) -> list[dict[str, object]]:
    """Build positive binding seeds from a safely inspectable V2 state; no global Closure claim."""


def build_closed_source_seed_inventory(state: dict[str, object]) -> list[dict[str, object]]:
    require_closed_authority(state)
    return build_source_seed_inventory(state)
```

Initial compiler uses `build_closed_source_seed_inventory`.

Drift audit uses the non-Closure builder only after structural/safe-index validation.

This separation must not weaken exact binding verification: each available seed still has to resolve at an exact positive M4 Core/Grill/UX location.

## 7. Review output completion never upgrades reliability

A complete `CONFIRMED_INTERPRETATION` result is not evidence that semantic-review/2.0 is reliable.

Freeze separate dimensions:

```text
review_completion:
  NOT_REQUIRED | PENDING | REVIEW_OUTPUT_RECORDED | REENTRY_REQUIRED

reliability_status:
  NOT_MEASURED
```

For contracts with no review fields, semantic assurance may report `NOT_REQUIRED` and omit a reliability requirement.

For contracts with REVIEW_REQUIRED fields, `reliability_status` is always `NOT_MEASURED` in M5, even after all review obligations receive `CONFIRMED_INTERPRETATION`.

Do not use labels such as:

```text
PASS
ASSURED
RELIABLE
CALIBRATED
```

for M5 semantic-review/2.0.

`REJECTED_INTERPRETATION` maps to `review_completion = REENTRY_REQUIRED` plus `CONTRACT_CONFLICT` event data.

`UPSTREAM_AUTHORITY_GAP` maps to `review_completion = REENTRY_REQUIRED` plus `AMBIGUITY_FOUND` event data.

Add a concrete API in Task 5:

```python
def review_results_to_reentry_events(
    contract: dict[str, object],
    review_package: dict[str, object],
    output: dict[str, object],
) -> list[dict[str, object]]: ...
```

This function emits read-only re-entry artifacts and never modifies the contract or canonical state.

## 8. M5 does not claim runtime implementation conformance

The name `joewrks.action-conformance/2.0` describes the authority contract identity, but M5 does not yet connect it to installed product adapters/runtime execution records.

M5 completion may claim:

```text
DOWNSTREAM_V2_AUTHORITY
SEMANTIC_DEBT_CLASSIFICATION
REENTRY_PROTOCOL
SEMANTIC_REVIEW_2_0_STRUCTURAL_BOUNDARY
```

It must not claim:

```text
RUNTIME_CONFORMANCE_COMPLETE
IMPLEMENTATION_CONFORMANT
SEMANTIC_ASSURANCE_RELIABLE
PRODUCTION_INTEGRATED
```

Add exact documentation marker:

```text
RUNTIME_CONFORMANCE_NOT_INTEGRATED_IN_M5
```

M6 owns installed routing, representative product dogfood, and end-to-end integration of the V2 authority package with implementation/runtime verification.

## 9. Contract schema/hash consequences of consumed seeds and scope commitments

The Task-3 action-conformance/2.0 schema and hashing projection must be updated from the main plan as follows.

A successful contract stores:

```text
source_authority.approved_definition_digest   # original compile provenance
source_authority.approved_manifest_digest
source_authority.binding contract identities
source_authority.snapshot_state_sha256         # observational artifact metadata
source_authority.consumed_seed_inventory_digest
responsibility_profile
scope_commitments
source_seed_inventory                          # consumed seeds only
actions
lifecycles
semantic_debt
handoff_status
semantic_assurance
semantic_contract_hash
artifact_hash
```

`semantic_contract_hash` includes the original approved definition digest, consumed-seed digest, scope commitments and semantic contents. It still excludes `snapshot_state_sha256`.

`artifact_hash` includes the snapshot SHA as in the main plan.

The audit of an old contract compares its frozen local dependencies to the new state; it does not recalculate the old artifact's hash using new global authority metadata.

## 10. Self-review result

With these clarifications, no remaining known blocking conflict was found between M5 semantic identity, dependency-scoped re-entry, M4 unconsumed-evidence stability, frozen v1 preservation, and semantic-review reliability truth.

Execution must read the frozen design, M4 audit, M5 main plan, and this addendum before coding.