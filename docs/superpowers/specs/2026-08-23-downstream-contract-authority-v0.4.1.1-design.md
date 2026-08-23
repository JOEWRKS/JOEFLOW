# Downstream Contract Authority v0.4.1.1 Design

## Goal

Prevent a valid canonical source hash from authorizing an arbitrary downstream semantic value, and prevent partial frozen-regression fixtures from claiming the production handoff contract version.

## Scope and invariants

- Work remains on `feat/v0.4.1-downstream-conformance`; `main` is not moved or merged.
- Canonical Product Definition state, state schema, Product Definition validators, Closure semantics, JSONL runtime protocol semantics, and frozen A/B source remain unchanged.
- `joewrks.action-conformance/1.0` is the only production implementation/Figma-Make handoff contract.
- `joewrks.downstream.regression-slice/1.0` is evaluator-only and cannot be presented as a full implementation contract.
- The compiler is the only authority for derivation validation. Runtime adapters translate invocation/readback, and the verifier evaluates observed semantics.

## Contract kinds

### Full production contract

`joewrks.action-conformance/1.0` requires every material action field and every material lifecycle field declared by the repository schemas. The compiler validates the completed bundle before hashing succeeds. Missing required fields, unexpected fields, invalid shapes, or invalid semantic envelopes fail compilation.

### Regression slice

`joewrks.downstream.regression-slice/1.0` requires the minimum evaluator contract: identity, current canonical sources, explicit default result, explicit input invariants, explicit result/component expectations, and test obligations. It may omit production handoff fields, but every semantic field it does contain uses the same derivation envelope and provenance rules as the full contract.

The handoff reference and template accept only the full contract version. Regression slices are labeled for frozen evaluator regression, harness development, and known-defect reproduction only.

## Repository schema validator

Python stdlib does not provide a general JSON Schema Draft 2020-12 validator. v0.4.1.1 therefore implements a deterministic validator for only the keyword subset used by the checked-in downstream schemas:

- `$ref` for local references such as `#/$defs/semanticField`;
- `type` for object, array, string, integer, number, boolean, and null;
- `required`, `properties`, and `additionalProperties`;
- `items`, `minItems`, and numeric `minimum`;
- `const` and `enum`;
- `pattern`;
- `oneOf`.

Any unsupported schema keyword that would affect instance validation fails schema loading rather than being silently ignored. Tests mutate every required full-contract field class and demonstrate that the checked-in full schema is enforced. This component is not described as a complete Draft 2020-12 implementation.

## Semantic authority envelope

Every material semantic field has this shape:

```json
{
  "value": "semantic value",
  "source_refs": [0],
  "derivation": {
    "kind": "MACHINE_DERIVED",
    "operator": "exact"
  }
}
```

or:

```json
{
  "value": "interpreted semantic value",
  "source_refs": [0, 1],
  "derivation": {
    "kind": "REVIEW_REQUIRED",
    "explanation": "Why the cited canonical clauses require human interpretation"
  }
}
```

Rules:

- `source_refs` is non-empty and every index resolves within the owning action or lifecycle source list.
- Active semantic fields use current sources only. Superseded references are permitted only in the separate inactive sentinel collection.
- `REVIEW_REQUIRED` needs a non-empty explanation and never counts as machine-authoritative or automatically verified.
- `MACHINE_DERIVED` executes a bounded operator and compares compiler output with the emitted value.
- Changing an emitted machine-derived value while retaining the canonical source and hash fails compilation.

## Operators

v0.4.1.1 implements only:

- `exact`: requires one source reference and returns that canonical source value.
- `extract`: requires one source reference plus a relative JSON Pointer and returns that exact nested value.

There is no natural-language parser, heuristic mapping, arbitrary code, or caller-provided constant mapping. Values that cannot be reproduced with these operators are `REVIEW_REQUIRED`.

## Covered semantic fields

For full actions, the envelope covers actor, authentication, relationship and object binding, concurrency, preconditions, allowed/forbidden states, input invariants, command, expected/forbidden mutations, default result, result/component expectations and assertions, version/history outcomes, business/delivery effects, idempotency, rejection, recovery, visible outcomes, superseded rules, test obligations, and trace.

For lifecycles, it covers current states, allowed/forbidden transitions, boundary conditions, reversibility, reversal window, object outcome, reason/confirmation/evidence requirements, authority, and history preservation. `lifecycle_id`, source records, and verified superseded sentinels remain structural/provenance records rather than derived semantic values.

The verifier unwraps already-compiled semantic values. It does not approve derivations. Every result classification used by a sequence must have an explicit compiled result expectation containing all five deep-state components; generic component defaults cannot silently authorize omissions.

## Authority assessment

Each compiled bundle reports independently:

- `structurally_valid`;
- `provenance_valid`;
- `machine_derived_obligations_verified`;
- `machine_derived_field_count`;
- `review_required_field_count`;
- `review_required_obligations_present`;
- `machine_verifiable_coverage` as machine-derived count divided by all semantic fields.

A structurally and provenance-valid full contract may contain review-required obligations. That does not mean those obligations have been semantically proven by automation.

## Testing and evidence

TDD begins with compilation failures for:

1. a full action missing required semantic fields;
2. a false machine-derived expectation using a valid current source;
3. an out-of-range source reference;
4. a semantic field with no provenance;
5. an active field using only superseded authority;
6. a changed machine-derived value with unchanged canonical source/hash;
7. a regression slice claiming the full contract version.

Additional tests cover schema keyword enforcement, explicit result components, review-required assessment, machine-derived counts, and handoff rejection of regression slices.

The actual frozen A/B runners are then executed without source modification. The final evidence must continue detecting A UI-to-domain disconnect, B030, B031 NaN, B031 positive infinity, stale latest values, historical projection, terminal retry/overdue behavior, and the superseded transition sentinel.
