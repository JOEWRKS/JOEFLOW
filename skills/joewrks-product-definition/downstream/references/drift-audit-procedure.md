# Blind Downstream Drift Audit

## Independence

The auditor receives the approved authority, compiled bundle, frozen source identity, runtime evidence, and public artifact. Do not accept the implementation agent's self-report, green test counts, build success, handler existence, or visual similarity as conformance evidence. Keep correction authorship separate from the next blind verdict where the evaluation protocol requires it.

## Material action evidence chain

For every material action, record this complete chain:

1. **Precondition** — actor, current authority/relationship, exact object, revision, state, input, confirmation/reason, and relevant boundary.
2. **Public action** — rendered control or public invocation actually used.
3. **Handler** — concrete handler reached by that invocation.
4. **Domain command** — command envelope and actual runtime call.
5. **State** — before/result/after authoritative domain state and revision.
6. **Provenance and effects** — audit/history, business side effects, delivery/notification effects, and the canonical IDs/pointers/hashes that define the expectation.
7. **Visible result or visible recovery** — success readback only after authoritative commit; error, latest-state comparison, preserved input, retry, or recovery for failure.

Missing any link leaves the action unverified. A UI control that reaches a generic audit-only handler is nonconformant when the contract requires a domain mutation.

## Procedure

1. Verify approved revision/digest, executable contract hash, adapter identity/version, and frozen commit/tree before execution.
2. Confirm every active source reference is CURRENT and every superseded sentinel is inactive.
3. Execute required sequences through the public invocation or actual domain runtime specified by the trace contract.
4. Evaluate each evidence record in the Python core. Inspect the five no-op components independently.
5. Re-run original-failure sequences after any correction. New evidence receives a new record; prior failed evidence remains preserved.
6. Report each missing or divergent chain link with canonical source ID/pointer, expected transition, observed transition, and severity.

## Result boundary

Runtime adapters report observations only. They must not emit a conformance verdict. The auditor reports PASS only when every required material sequence is conformant and no frozen regression is silently excluded. Responsive/visual findings remain separate from semantic conformance unless the approved contract makes them material.
