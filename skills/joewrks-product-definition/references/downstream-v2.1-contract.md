# Downstream Semantic Handoff Contract 2.1

Status: normative action-conformance/2.1 boundary; M5.1 integration is outside this artifact.

## Identities

```text
handoff definition: joewrks.handoff-definition/2.1
action contract: joewrks.action-conformance/2.1
responsibility profile: joewrks.downstream-responsibility/2.0
compiler id: joewrks-product-definition/downstream-v2.1
compiler version: core-semantic-closure-v2-m5.1
```

The 2.1 package is a sibling of frozen `downstream_v2`. It may read the exact M5 authority, seed, semantic-debt, and Product Definition re-entry primitives, but it does not redefine any 2.0 identity or modify any frozen tree.

## Authority-only action contract

Action-conformance/2.1 carries exact approved Product Definition meaning and its provenance. Runtime test identifiers, result mappings, and snapshot expectations are not semantic action fields.

Every action `fields` object contains exactly:

```text
actor
authentication
relationship_predicate
object_binding
concurrency
preconditions
allowed_current_states
forbidden_states
input_invariants
command
expected_domain_mutation
forbidden_mutations
version_result
history_result
business_side_effects
delivery_effects
idempotency
rejection
recovery
visible_success
visible_error
superseded_rules
trace
```

These runtime-only 2.0 fields are forbidden in the 2.1 semantic inventory:

```text
default_result
result_expectations
test_obligations
```

Lifecycle semantic fields remain those frozen by responsibility profile 2.0.

## Handoff definition

The top-level handoff definition has exactly:

```text
definition_schema_version
product_slug
actions
lifecycles
```

Every action has exactly:

```text
action_id
authority_scope_refs
ux_action_locator
fields
verification_basis
```

An action requires nonempty, current, exact `REQ`/`SCR`/`SURF` scope refs and an exact UX locator containing `screen_ref` and `action_key`. A UX action seed is eligible only when both locator values match its source location.

The field-spec vocabulary is closed:

```text
DIRECT_AUTHORITY
MACHINE_DERIVED extract
MACHINE_DERIVED select
MACHINE_DERIVED collect_exact
REVIEW_REQUIRED
UNRESOLVED
```

No caller value-bearing deterministic spec, compose/construct operator, template, callback, expression language, `eval`, or natural-language parsing is allowed.

## Verification basis

Every handoff and materialized contract action has exactly:

```json
{
  "verification_basis": {
    "outcome_basis_seed_refs": ["SEED-..."],
    "acceptance_basis_seed_refs": ["SEED-..."]
  }
}
```

Both arrays are nonempty, lexically sorted, unique, source-seed-only, and selected explicitly by the handoff caller. The compiler validates and normalizes those exact refs; it never selects all eligible authority automatically and never accepts caller values or pointers in this section.

Outcome basis selectors are exactly:

```text
CORE:happy_path
CORE:alternative_path
CORE:error
CORE:recovery
CORE:acceptance
UX_ACTION:success
UX_ACTION:failure
UX_STATE:success
UX_STATE:error
```

Acceptance basis selectors are exactly:

```text
CORE:acceptance
```

Every basis seed must be current, belong to the action's exact `authority_scope_refs`, match an allowed selector, and, for `UX_ACTION`, match the exact `ux_action_locator`. Basis refs are semantic consumers even when no ordinary action or lifecycle field uses them. They therefore remain in `source_seed_inventory`, contribute to `consumed_seed_inventory_digest`, and participate in `semantic_contract_hash`.

## Compilation results and gap routing

Successful compilation returns one of:

```text
AUTHORITY_READY_MACHINE_VERIFIED
AUTHORITY_READY_REVIEW_PENDING
```

and includes a production contract with zero authority gaps. Failed compilation returns the same stable keys: `status`, `contract`, `semantic_debt`, `semantic_gaps`, `expressiveness_gaps`, and `reentry_events`.

The three gap codes remain distinct:

```text
SEMANTIC_AUTHORITY_GAP
CONTRACT_EXPRESSIVENESS_GAP
RUNTIME_MAPPING_GAP
```

`SEMANTIC_AUTHORITY_GAP` means approved product meaning is explicitly unresolved. Its result is `REENTRY_REQUIRED`; only these records enter the frozen Product Definition re-entry builder, which produces affected-only events.

`CONTRACT_EXPRESSIVENESS_GAP` means exact eligible authority exists but the closed semantic representation cannot carry it losslessly. Its result is `CONTRACT_EVOLUTION_REQUIRED`; it produces no Product Definition re-entry event or canonical unknown. When semantic and expressiveness gaps coexist, `REENTRY_REQUIRED` wins while both inventories remain visible.

`RUNTIME_MAPPING_GAP` belongs to runtime-plan remediation, not this semantic compiler, and never by itself re-enters Product Definition.

Unknown operators, malformed specs, unsupported derivations, invalid scope/locator/basis data, and other `INVALID_*` conditions fail closed as errors. They are not reclassified as semantic or expressiveness gaps.

## Semantic identity

The semantic contract commits the 2.1 contract/compiler identities, approved source authority, frozen binding identities, responsibility profile, exact scope commitments, consumed-only source seed inventory, action and lifecycle semantic fields, action verification basis, semantic debt, and semantic assurance.

Only `source_authority.snapshot_state_sha256` is observation-only and excluded from `semantic_contract_hash`. It remains present in the artifact and therefore affects `artifact_hash`.

## Dependency-scoped audit

`audit_action_contract_v21_against_state(contract, current_state)` returns exactly:

```text
status
authority_revision_relation
affected_consumers
semantic_gaps
errors
```

Compilation requires actual Product Definition Closure. Audit of an existing valid contract does not require the current whole definition to remain closed. It safely indexes current state, rebuilds the positive seed inventory without closure admission, verifies every consumed exact seed and every scope commitment, and maps changes only to their action/lifecycle consumers. Verification-basis consumers are first-class seed consumers.

An unrelated newer open revision or unconsumed evidence change remains `CONFORMANT` with `OLDER_APPROVED_REVISION_UNAFFECTED`. Used seed, basis, or scope drift returns `REENTRY_REQUIRED` with exact affected consumers. Duplicate IDs or an unsafe semantic projection returns `DEFINITION_NOT_READY` with errors and no fabricated semantic gap.

The source approved definition and manifest digests are immutable provenance during audit; audit never rewrites the contract or current state.

## Machine-readable schemas

The schemas are:

```text
downstream_v21/schemas/handoff-definition-v21.schema.json
downstream_v21/schemas/action-contract-v21.schema.json
```

The repository schema validator's supported JSON Schema subset cannot express uniqueness or lexical ordering. The schemas express nonempty arrays and exact shapes; runtime validators additionally enforce sorted, unique scope, seed, field, basis, and identity inventories.
