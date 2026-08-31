# Core Semantic Closure V2 M6 dogfood — historical 2.0 stop and completed 2.1 runtime

This summary separates the approved Product Definition, the preserved 2.0
compiler failure, the M5.1 representation repair, the corrected 2.1 compile,
the full-contract runtime result, and the two controlled probes. These are
local dogfood artifacts only; they do not claim promotion, deployment, or a
final R1–R10 result.

## 1. Approved Product Definition

The canonical Client Feedback Portal Product Definition remains revision `1`,
`CLOSED`, and `APPROVED`. The official state and closure validators pass, and
the exact revision-1 approval commitment remains in `approval_history`.

- definition digest: `e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c`
- Approval Manifest digest: `60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705`
- approved by: `user`
- approved at: `2026-08-30T11:54:26Z`

The 2.1 continuation did not revise Product Definition authority or reuse the
approval for changed product meaning.

## 2. Preserved historical 2.0 stopped failure

`handoff-definition.json` and `reentry-probe.json` remain the original 2.0
evidence. The frozen 2.0 compiler returned `REENTRY_REQUIRED` with
`contract = null`, 131 direct-authority fields, zero machine-derived fields,
25 authority gaps, and 25 read-only re-entry events.

All six actions exposed the four representation conflicts for
`input_invariants`, `default_result`, `result_expectations`, and
`test_obligations`; `reply_thread.actor` added the twenty-fifth conflict
because two approved actors could not fit a single direct source binding.
Every event used `AFFECTED_ONLY` scope and named one action. This result is
historical evidence of the old contract's expressiveness limit, not evidence
that approved product meaning was absent.

At that historical stop, no 2.0 action contract or runtime result was created.
The newer 2.1 artifacts are separate files and do not rewrite that outcome.

## 3. M5.1 remediation

M5.1 introduced the lossless 2.1 `collect_exact` representation and separated
runtime-plan and evidence responsibilities from semantic contract fields. The
approved outcome and acceptance authority now remains in
`verification_basis`; `default_result`, `result_expectations`, and
`test_obligations` are not action-conformance/2.1 semantic fields.

The runtime planner consumes the valid 2.1 contract, its committed
`verification_basis`, and `joewrks.runtime-responsibility/1.0`. It does not
read Product Definition state and it does not treat a bare field reference as
executable coverage.

## 4. Corrected 2.1 compile

`handoff-definition-v21.json` compiles to `action-contract-v21.json` with:

- semantic contract hash: `b00b45e8ca4804289f5d8af3bb55fc6569ee65771838459b8ba49583df349b57`
- direct-authority fields: 131
- machine-derived fields: 7
- authority gaps: 0
- semantic gaps: 0
- contract-expressiveness gaps: 0
- review-required fields: 0
- re-entry events: 0

`reply_thread.actor` collects both approved actors exactly, and each action's
`input_invariants` is an exact approved conjunctive collection. Semantic review
is `NOT_REQUIRED`; reliability remains `NOT_MEASURED`.

## 5. Full-contract runtime result

`runtime-conformance-plan.json` has plan hash
`fb110dea04114759d95a8524c6fbe009a3b0befcd7c7404bce702574a77bf520`
and runtime-responsibility digest
`035e83a108f96aeedc6475fe606a60312e326cb80d52522e51d67691e172ac64`.
All 120 runtime-critical field references have concrete result, component, or
assertion relationships; missing references and mapping gaps are both zero.

A deterministic local Client Feedback Portal fixture executed 21 distinct
planned cases: success, rejection, and idempotent replay for all six actions,
plus stale-revision cases for send, resend, and revoke. The fixture maintains
version, review-link, pin, thread, revision, history, business-effect,
delivery-effect, and attempt-result state. It enforces the approved actors and
inputs, fresh expected revisions, replay without duplicate effects, stale
rejection with latest state, and revoke without an invented email.

`runtime-evidence.jsonl` contains exactly one frozen execution/1.0 record per
planned test ID. `runtime-evidence-bundle.json` contains 21 records, no missing,
duplicate, or unexpected IDs, and bundle hash
`ded4bfc45809c7f5cc4352289b4aced675ad2c8120ebe18b7d21639f96e9b503`.

The M6 verifier independently binds each test ID to its action and case,
re-executes the deterministic scenario, and checks the command, expected
result class, all five before/after components, assertions, deltas, authority,
and contract identity. The schema-valid
`joewrks.runtime-conformance-report/1.0` result is:

- `verification_scope = FULL_CONTRACT`
- `contract_dependency_status = CONFORMANT`
- `coverage_status = COMPLETE`
- `action_coverage_status = COMPLETE`
- `lifecycle_applicability = NOT_APPLICABLE`
- `lifecycle_coverage_status = COMPLETE`
- `runtime_status = CONFORMANT`
- `implementation_status = IMPLEMENTATION_CONFORMANT`

Lifecycle is not applicable because the semantic contract contains zero
lifecycle items.

## 6. Controlled probes

`implementation-drift-probe.json` mutates a copied `create_pin` command to the
wrong actor. Both its outer label and nested report use
`verification_scope = PARTIAL_PROBE`; the verifier returns
`runtime_status = NON_CONFORMANT` and
`implementation_status = IMPLEMENTATION_NOT_CONFORMANT`. A partial probe can
never claim global implementation conformance.

`reentry-probe-v21.json` changes one copied 2.1 handoff field to genuinely
`UNRESOLVED`. It returns one `SEMANTIC_AUTHORITY_GAP`,
`REENTRY_REQUIRED`, `contract = null`, and `AFFECTED_ONLY` scope for only the
affected action. It does not mutate canonical state, approval, the production
2.1 contract, or the preserved 2.0 evidence.
