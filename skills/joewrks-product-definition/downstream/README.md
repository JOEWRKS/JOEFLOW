# Executable Downstream Conformance

Use this subsystem after Product Definition Closure to compile approved canonical clauses into implementation obligations and evaluate actual runtime sequences. It is separate from interrogation and Closure: it reads canonical state and never writes it.

## Authority model

Every derived bundle records the product slug, approved revision/digest, canonical state hash, compiler identity/version, and deterministic contract hash. Every active semantic source resolves to one current stable object ID plus an exact JSON Pointer and SHA-256 of the referenced canonical JSON value. Active superseded sources, pointer drift, hash drift, empty/out-of-range semantic source references, and machine-derived value drift fail compilation. Inactive superseded sources may appear only as sentinels.

Product adapters map canonical clauses to executable fields. The Python core decides expected results and verification; runtime adapters only translate the protocol into actual invocation/readback.

### Contract kinds

- `joewrks.action-conformance/1.0` is the structurally complete production implementation/Figma-Make handoff contract.
- `joewrks.downstream.regression-slice/1.0` is an evaluator-only partial fixture for frozen regressions, harness development, and known-defect reproduction. It is never eligible for production handoff.

The `is_full_handoff_contract()` gate rejects the regression-slice version even when its evaluator fields are valid.

### Semantic derivation integrity

Every material semantic field contains `value`, non-empty `source_refs`, and a machine-readable `derivation`:

- `MACHINE_DERIVED` executes `exact` or `extract` against the cited canonical source and requires the emitted value to equal the compiler-computed value.
- `REVIEW_REQUIRED` preserves exact provenance and a non-empty interpretation explanation, but the compiler does not prove the semantic value itself.

No natural-language parser, heuristic mapper, arbitrary executable mapping, or caller-provided constant mapping exists. If `exact` or `extract` cannot reproduce the value, it remains review-required.

Each bundle reports `structurally_valid`, `provenance_valid`, `machine_derived_obligations_verified`, both derivation-class field counts, review-required presence, and machine-verifiable coverage. Structural validity does not convert review-required obligations into automated semantic proof.

### Repository schema subset

The stdlib-only validator implements the subset used by these repository schemas: local `$ref`, `type`, `required`, `properties`, `additionalProperties`, `items`, `minItems`, `minimum`, `const`, `enum`, `pattern`, and `oneOf`, plus schema annotations. Unsupported validation keywords fail rather than being ignored. This is not a general or complete JSON Schema Draft 2020-12 implementation.

## Runtime protocol

`joewrks.downstream.execution/1.0` is one JSON object per line. Evidence records bind sequence/test ID, product authority, contract hash, adapter identity/version, frozen commit/tree, command/input, before/result/after, history delta, business-side-effect delta, and delivery delta.

Standard JSON never carries non-finite numbers. Encode them recursively as exactly one-key typed sentinels:

```json
{"$number":"NaN"}
{"$number":"+Infinity"}
{"$number":"-Infinity"}
```

The adapter decodes these immediately before the runtime call and re-encodes observed values before JSON serialization. A `$number` object with any other key or value is invalid.

## Deep verification

The verifier reports authoritative domain state, revision/version, audit/history, business side effects, and notification/delivery effects separately. Every usable result class and all five component expectations must be explicitly present in the compiled semantic envelope. A canonical denial-audit or other permitted change must be declared explicitly in the action contract. Sequence overrides not declared by that contract fail verification. SUCCESS, REJECTED, STALE, and IDEMPOTENT REPLAY are evaluated from compiled obligations, never from an adapter verdict or generic fallback.

## Sequence catalog

Supported reusable sequence classes are:

- valid happy transition
- wrong role
- wrong object/revision
- authority lost after initial access
- stale expected version
- validation rejection
- repeated same idempotency key
- same-key replay after later state changes
- reversal before boundary
- reversal at boundary
- reversal after boundary
- superseded transition sentinel
- delivery failure after successful business commit
- manual delivery retry
- stop-after-terminal-state
- destructive action without confirmation/reason
- rejected command followed by a related second command
- historical projection after later state change

Sequence definitions supply product-specific commands and canonical expectations. A sequence verdict is based on state transitions and evidence assertions, not HTTP/UI success or test counts.

## Files

- `contracts.py`, `provenance.py`: deterministic compilation, derivation, source validation, and handoff classification.
- `schema_validation.py`: repository-specific schema-keyword-subset enforcement.
- `protocol.py`, `schemas/execution-record.schema.json`: JSONL and typed-number contract.
- `verifier.py`, `invariants.py`, `runner.py`: semantic result, deep no-op, invariant, lifecycle, and sequence evaluation.
- `adapter_runtime.py`, `adapters/`: external invocation/readback boundary.
- `product_adapters.py`, `products/`: provenance mappings for frozen regressions and revision 44.
- `run_frozen_regressions.py`: pinned A/B execution entry point.
- `references/drift-audit-procedure.md`: independent downstream audit procedure.

Run the pinned evaluation as a module with the skill directory on `PYTHONPATH`:

```text
python -m downstream.run_frozen_regressions --a-root <pinned-a-worktree> --b-worktree <b-worktree-with-frozen-source-tree> --output-dir <evidence-dir>
```

The command requires a clean A worktree at the pinned commit and a clean B worktree whose `codex-implementation` tree equals the frozen commit. It never patches either source tree.
