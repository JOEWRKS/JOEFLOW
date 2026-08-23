# Methodology

## Boundary

Canonical Product Definition is read-only authority. Product adapters select canonical clauses by current stable ID and JSON Pointer. Compilation adds the exact canonical JSON value hash, approved revision/digest, canonical state hash, compiler identity/version, and deterministic contract hash. Full production contracts and evaluator-only regression slices use distinct schema versions and cannot be interchanged by the handoff gate.

Every material semantic value is an envelope. `MACHINE_DERIVED` runs only `exact` or `extract` and compares the emitted value with the compiler-computed canonical value. `REVIEW_REQUIRED` retains sources and a non-empty explanation but remains outstanding interpretation rather than automated proof.

Runtime adapters translate JSONL requests into actual frozen runtime calls and return before/result/after observations. They do not state expected behavior or emit a conformance verdict. The Python standard-library core derives expectations from the executable contract and evaluates each component.

## Frozen execution

Replication A ran from a clean detached worktree at `9408434e640b9cf0bf6afaadd8f9d1f5f52e8943`. Its implementation tree was `189d9f969d046ecf905680e090f65f15114aeeb4`. A Node DOM boundary invoked the actual `app.js` public handler and read the rendered state readback; neither `app.js` nor `domain.js` was patched.

Replication B ran the exact `codex-implementation` tree `6294fc9072521fdb762808b87203a7e8bac4f7f5`, identical at frozen source commit `eecebc28701006dd2c7be4045a22542e34719705` and the evidence worktree. An external Vitest runner imported the actual `engine.ts`, `seed.ts`, and `selectors.ts`. The runner lived only in the downstream subsystem. Frozen source was not modified.

## Protocol

Every evidence line uses `joewrks.downstream.execution/1.0` and binds:

- sequence/test ID and product slug;
- approved revision/digest and executable contract hash;
- adapter identity/version and frozen commit/tree;
- command/input and optional visible test setup;
- before snapshot, raw runtime result, after snapshot;
- history, business-side-effect, and delivery deltas.

`NaN`, positive infinity, and negative infinity use typed one-key sentinels. The B adapter decoded these to real JavaScript numeric values immediately before `executeCommand`; its `runtime_non_finite_inputs` observation proves the classifications passed to the engine. It re-encoded observed state before JSON serialization, so no `null` substitution was used as the test input or evidence representation.

## Verification

Deep verification independently compares:

1. authoritative domain state;
2. target revision/version;
3. audit/history;
4. business side effects;
5. delivery/notification effects.

Every declared result class explicitly states all five component expectations. There is no verifier component fallback. Canonical denial audit is an explicit REVIEW_REQUIRED slice expectation. Additional result assertions within the same semantic envelope validate latest-value presence, historical event projection, and terminal flags.

The harness result is PASS only because it detected the known frozen failures. A frozen application NONCONFORMANT result is expected evidence, not a harness failure.
