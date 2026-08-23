# Contract Schema Review

## Decision

**PASS for v0.4.1 executable downstream use.** The schemas and Python checks preserve the authority boundary and can express the required action, lifecycle, result, no-op, trace, and sequence semantics without adding fields to canonical `state.json`.

## Action contract

`action-contract.schema.json` requires all material slots: stable action ID and sources; actor/auth/relationship; exact object and revision binding; preconditions and state boundaries; input invariants; command; required/forbidden mutation; result/component effects; version/history/business/delivery outcomes; idempotency/rejection/recovery; visible outcomes; superseded rules; test obligations; and end-to-end trace.

Material semantic fields use `{value, source_refs, mapping?}`. `source_refs` index provenance records containing a current stable object ID, exact JSON Pointer, SHA-256 of the pointed canonical JSON value, source status, and active flag. Compilation fails pointer/hash/status drift. Product-specific mappings cannot become authority because expected behavior remains bound to those clauses and approved revision/digest.

The frozen A/B bundles are deliberately scoped regression slices. The revision 44 bundle is the full-shaped expressiveness example for downstream handoff.

## Lifecycle contract

`lifecycle-contract.schema.json` covers current states, allowed/forbidden transitions, boundaries, reversibility/window, same/new-object outcome, reason/confirmation/evidence, authority, history preservation, and superseded sentinels. Active sources must be CURRENT. A sentinel must be inactive and its source must be SUPERSEDED.

## Execution record

`execution-record.schema.json` fixes protocol `joewrks.downstream.execution/1.0` and requires all identity, command, snapshot, result, and delta fields. The typed-number definition permits only `NaN`, `+Infinity`, and `-Infinity` in a one-key `$number` object. Python validation also rejects raw non-finite standard JSON numbers.

## No-op and allowed changes

The verifier never reduces no-op to whole-object equality. It retains separate verdicts for domain, version, history, business effects, and delivery. Allowed changes are result-specific contract entries. For example, `FILE_AUTHORITY_REVOKED` may append a DENIED audit because that action contract explicitly expects history change while every other component remains unchanged.

## Adapter boundary

Adapters can decode protocol values, apply visible scenario setup, invoke actual frozen code, select actual readback, and encode evidence. They cannot supply `conformant`; the adapter runtime rejects such output. Result classification and expected semantics remain in Python.

## Review limitations

The schemas are dependency-free machine-readable JSON Schema documents, while enforcement used by this release is the Python standard-library compiler/verifier. v0.4.1 does not claim database mechanics, vendor integration, responsive behavior, or complete contracts for every action in both dogfood products.
