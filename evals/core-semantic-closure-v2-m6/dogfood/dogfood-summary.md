# Core Semantic Closure V2 M6 dogfood — Phase B stopped at re-entry

This artifact records the bounded Task 5 Phase B outcome. It is not a final
runtime-conformance result and does not start Task 6.

## Exact approval and Product Definition Closure

The supplied approval was recorded exactly against definition revision `1`:

- approved definition digest: `e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c`
- approved Approval Manifest digest: `60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705`
- approved by: `user`
- approved at: `2026-08-30T11:54:26Z`

The official state validator reports valid, the official closure validator
reports `closed = true`, and the exact revision-1 approval commitment is stored
in `approval_history`. Recording approval did not change either approved
digest or any Product Definition semantic record.

## Actual downstream handoff result

The exact handoff definition covers all six selected major actions:

`create_pin`, `reply_thread`, `resend_review_request`, `resolve_thread`,
`revoke_review_link`, and `send_review_request`.

The official compiler returned `REENTRY_REQUIRED` with `contract = null`:

- direct-authority fields compiled: `131`
- machine-derived fields compiled: `0`
- review-required fields: `0`
- semantic authority gaps: `25`
- read-only re-entry events: `25`

Every action has the same four exact contract conflicts:

- `input_invariants`: approved authority is declarative text, not an executable invariant array;
- `default_result`: no permitted bound value is an executable runtime result class;
- `result_expectations`: no permitted bound value is the required five-component expectation map;
- `test_obligations`: approved acceptance authority does not bind a unique stable test-ID array.

`reply_thread` has one additional `actor` conflict. Approved authority allows
both Designer and Client Reviewer replies, while the frozen `DIRECT_REQUIRED`
field can bind only one source seed. The handoff leaves that actor unresolved
instead of selecting one actor and silently dropping the other.

The persisted `reentry-probe.json` is the exact compiler output. Every event is
`CONTRACT_CONFLICT`, has `source_contract_hash = null`, uses
`halt_scope.mode = AFFECTED_ONLY`, and names one affected action with no
affected lifecycle. Candidate unknown text remains a proposal and was not
copied into canonical authority.

## Re-entry routing boundary

Inspection found clear approved product meaning but no representation that the
frozen handoff compiler can losslessly turn into the executable structures
required by the frozen runtime verifier. Direct authority, `extract`, and
`select` cannot construct missing literals or maps, and the responsibility
profile forbids `REVIEW_REQUIRED` for these deterministic fields.

This is an integration-contract representation conflict, not a product-policy
question. A complete canonical `UNK-*` cannot be truthfully authored without
turning an architecture decision into invented Product Definition meaning.
Under the installed Task 4 workflow, no half-applied revision, approval
invalidation, staleness transition, or candidate-text adoption is permitted.
The canonical dogfood therefore remains at the valid revision-1
`CLOSED`/`APPROVED` checkpoint while the read-only re-entry evidence is routed
for contract/design reconciliation.

No `action-contract-v2.json`, runtime fixture, runtime execution evidence,
runtime conformance report, or final-state claim was created. Track A remains
the unchanged full historical `OPEN`/`UNAPPROVED` migration reconciliation
candidate. Task 6, push, merge, deployment, and production conformance remain
unstarted and unclaimed.

## M5.1 remediation and 2.1 continuation

The stopped 2.0 result above is historical evidence and remains unchanged. M5.1
provided the lossless 2.1 `collect_exact` representation and the plan/bundle
runtime boundary; it did not revise the approved Product Definition.

The persisted 2.1 handoff and contract compile from that unchanged approval with
zero semantic or expressiveness gaps. The contract hash is
`b00b45e8ca4804289f5d8af3bb55fc6569ee65771838459b8ba49583df349b57`;
its debt inventory is 131 direct fields, 7 machine-derived fields, zero
authority gaps, and zero review-required fields. Semantic review is therefore
not required and its reliability remains `NOT_MEASURED`.

The 2.1 runtime plan is contract-bound and coverage `COMPLETE`. A deterministic
local fixture produced one frozen execution/1.0 record for every planned test.
The 2.1 verifier independently rechecked the plan's result/component/assertion
semantics against admitted records, producing `IMPLEMENTATION_CONFORMANT` with
`FULL_CONTRACT` coverage; bundle completeness alone is not treated as proof.
There are no lifecycle items, so lifecycle status is `NOT_APPLICABLE`.

`implementation-drift-probe.json` is a separate controlled partial probe with
a rejected result record and a non-conformant report. `reentry-probe-v21.json`
is separately compiled from a temporary one-field unresolved handoff and
returns one `SEMANTIC_AUTHORITY_GAP` / `REENTRY_REQUIRED` event with
`AFFECTED_ONLY` scope. Neither probe changes canonical approval, contract, or
conformant evidence. This remains local dogfood evidence only: reliability is
not measured, and no promotion, main, deployment, or final R1–R10 claim is made.
