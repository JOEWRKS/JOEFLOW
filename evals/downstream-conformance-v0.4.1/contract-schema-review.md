# Contract Schema Review

## Decision

**PASS for v0.4.1.1 authority enforcement.** Full production structure, evaluator-slice separation, canonical provenance, and machine derivation integrity are enforced independently. This does not claim that REVIEW_REQUIRED values have been semantically proven by automation.

## Contract separation

- `joewrks.action-conformance/1.0` requires every full action and lifecycle field and is the only production implementation/Figma-Make handoff contract.
- `joewrks.downstream.regression-slice/1.0` requires explicit evaluator semantics but may omit full handoff fields. A/B use this version and the handoff gate rejects both.

A partial definition stamped as the full version fails structural compilation. Unknown action properties also fail, so an evaluator-only marker cannot turn a partial action into a full one.

## Structural enforcement

The stdlib validator implements only the repository-used keyword subset: local `$ref`, `type`, `required`, `properties`, `additionalProperties`, `items`, `minItems`, `minimum`, `const`, `enum`, `pattern`, and `oneOf`, plus annotations. Unsupported validation keywords fail. This is not a complete JSON Schema Draft 2020-12 implementation.

The compiler validates the full bundle against `action-contract.schema.json` and each full lifecycle against `lifecycle-contract.schema.json`. Tests remove each required action field in turn and require compilation failure.

## Semantic derivation

Every material semantic field is `{value, source_refs, derivation}`. Source refs must be non-empty, in range, active, and CURRENT. `MACHINE_DERIVED` supports only:

- `exact`: one cited canonical value;
- `extract`: one cited canonical value followed by a relative JSON Pointer.

The compiler recomputes the value and rejects an emitted-value mismatch while canonical bytes/hash remain unchanged. `REVIEW_REQUIRED` needs a non-empty explanation and contributes only to the review-required count.

Result classes, input invariants, five component expectations, assertions, default results, test obligations, and all lifecycle semantics use the same envelope. Sequence overrides absent from compiled result expectations fail verification.

## Authority assessment

| Bundle | Version | Structurally valid | Provenance valid | Machine-derived verified | MACHINE_DERIVED | REVIEW_REQUIRED | Machine coverage | Production handoff |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Replication A | regression slice | yes | yes | yes, zero machine fields | 0 | 4 | 0% | no |
| Replication B | regression slice | yes | yes | yes, zero machine fields | 0 | 64 | 0% | no |
| client-feedback rev44 | full contract | yes | yes | yes | 1 | 37 | 2.631578947% | yes |

The rev44 full contract is valid while its 37 REVIEW_REQUIRED obligations remain present. Its automated derivation claim covers only the single exact lifecycle state-list field.

## Runtime boundary

The JSONL protocol remains `joewrks.downstream.execution/1.0`. Adapters invoke/read back frozen source and cannot supply `conformant`. The Python verifier consumes compiler-approved semantic values but does not determine derivation authority.

## Scope boundary

v0.4.1.1 does not claim database mechanics, vendor integration, responsive behavior, or complete production contracts for the A/B dogfood implementations.
