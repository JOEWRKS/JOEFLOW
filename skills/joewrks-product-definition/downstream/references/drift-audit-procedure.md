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

## Semantic-review sidecar audit

Before accepting any `REVIEW_REQUIRED` semantic result as reliable review evidence, audit the actual `joewrks.semantic-review/1.0` sidecar rather than reviewer narration. Recompute the reviewer input manifest hash and reviewer input package hash, then read back the reviewer brief hash, contract hash, responsibility profile hash, semantic obligation index hash, review identity inventory hash, and output schema hash from the same byte-frozen package. Confirm every run used safe declared paths, identical package/brief bytes, a unique run/context, and a valid isolation attestation with no previous-verdict access.

Verify exact 26 action plus 12 lifecycle responsibility coverage, the closed 38-entry obligation taxonomy, one owner per obligation, exact semantic pointer/value binding, allowed existing siblings, required tests, and the owner-kind/field/rule/mode tuple on every output record. Recompute each record's provenance-set hash and require exact obligation, test, sibling, and canonical-evidence bindings even when the output also contains a terminal preflight error. Confirm `superseded_sentinels` was handled only by package/provenance rule `PR-P01`, every sentinel source resolves exactly, no sentinel produced a semantic identity, and no `FR-L13` exists. Keep `APPROVED`, `REJECTED_CANDIDATE`, `RUBRIC_ERROR`, and `INPUT_PACKAGE_ERROR` distinct and preserve package → rubric → candidate → approval failure precedence.

The evidence may state `SEMANTIC_REVIEW_RELIABILITY_GATE — PASS` only after all 15 self-contained hash-bound golden packages and their finalized schema-valid outputs, at least three fresh full reviews, exact identity coverage, zero pending records, disagreement gates, and the applicable exact-rational reliability thresholds pass together. Recompute the cited frozen responsibility-rule hash on every disagreement classification. Read JSON-null reason codes on structural metric failures and use reduced rational values—not display strings—for every threshold decision. `HUMAN_ADJUDICATION_COMPLETE` must remain `NO` until external human-adjudication evidence for the frozen answer bank is supplied; PM-approved synthetic fixtures or agent review cannot set it to `YES`. Preserve every failed run set and its hashes. Majority agreement, green tests, manual approval, or a display-rounded coefficient cannot override a failed gate.

## Result boundary

Runtime adapters report observations only. They must not emit a conformance verdict. The auditor reports PASS only when every required material sequence is conformant and no frozen regression is silently excluded. Responsive/visual findings remain separate from semantic conformance unless the approved contract makes them material.
