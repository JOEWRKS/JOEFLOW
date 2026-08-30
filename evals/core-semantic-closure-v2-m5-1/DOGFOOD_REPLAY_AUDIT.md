# M6 Phase-B Dogfood Replay Audit

Date: 2026-08-31

Disposition: `M6_RESUME_READY / NOT_INTEGRATED`

## Read-only source identity

The mandatory replay read the preserved M6 worktree only after all admission checks passed:

```text
branch: feat/core-semantic-closure-v2-m6-integration-adoption
commit: d38b0ca04768888c47e658c79f41e1cec0a7a1ce
tree: 40749d900b98936cf694b0c96db7897011cddae8
status before replay: clean
status after replay: clean
tracked-file bytes before/after: identical
```

The replay helper hashed every tracked file before and after the replay. It wrote no file in the preserved worktree and rechecked branch, commit, tree, status, and all tracked-file hashes in a `finally` boundary.

The exact dogfood authority remained:

```text
Product Definition revision: 1
definition status: CLOSED
approval status: APPROVED
approved definition digest: e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c
approved manifest digest: 60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705
approved at: 2026-08-30T11:54:26Z
approved by: user
official Closure: true
approval history: one entry, revision 1, matching definition and manifest digests
```

Read artifact SHA-256 identities:

```text
product-definition/client-feedback-portal-dogfood-v2/state.json  728744301bc0ea2a1766852b7b46bab3c610215b31f63c0a784dd804fa3ce49d
approval-manifest.json                                               f354e7baf1001bf1cd2a763569b310947ca2fd1ae4e6eb57c6f1573d9ec2eef1
handoff-definition.json                                             11fdce0fdce90d8c2f5e069cd766aa338e5f4efd7653d38e2d152509653fbaef
reentry-probe.json                                                   b6e0b4960211456a6dacf521a407667c0b838b5b1dee50db9ab02f2b9534e211
dogfood-summary.md                                                   79859d308f71eefb426fa8876c1f707f1d4fd579862e40aae87dad962c0b43ce
```

## Historical action-conformance/2.0 result

The old result was read and asserted, not regenerated or rewritten:

```text
handoff definition: joewrks.handoff-definition/2.0
status: REENTRY_REQUIRED
contract: null
direct authority fields: 131
machine-derived fields: 0
review-required fields: 0
authority gaps: 25
gap code set: {SEMANTIC_AUTHORITY_GAP}
re-entry events: 25
event type set: {CONTRACT_CONFLICT}
source_contract_hash on every old event: null
```

## Mechanical 2.0 to 2.1 translation

The replay copied all action identities, authority scopes, UX locators, lifecycles, retained field source references, and retained derivation semantics. It removed only the runtime-owned `default_result`, `result_expectations`, and `test_obligations` fields.

The known multi-authority `reply_thread.actor` was represented losslessly with `collect_exact` over exactly:

```text
SEED-65b2a6c9b4932974b3b60496
SEED-85cdd056577c5a7b55b59c5a
```

Its materialized value was exactly `['Workspace Owner / Designer', 'Client Reviewer']`. No product value was inserted by the replay.

Each action's `input_invariants` used `collect_exact` over the approved action-specific UX input and validation authority:

| Action | Exact input-invariant seed refs |
| --- | --- |
| `create_pin` | `SEED-8074b355d815df0963221327`, `SEED-9968346c37f09b10b8a89d89`, `SEED-d4f8428a81f5d608960c174f` |
| `reply_thread` | `SEED-23f1071f8cd9cf14d4ce3e72`, `SEED-257257f91c773cfe5dfe3347`, `SEED-ed9c757cbc28c40044dfd8aa` |
| `resend_review_request` | `SEED-2179f7c6d433e0f01ceedaec`, `SEED-3511c07413b4b2a8e48bc8ef`, `SEED-87ed156646ff86f1a94ffcb6`, `SEED-95b7ebff04f98f2585cdd450`, `SEED-c1f73501db4b81ff52c0bada` |
| `resolve_thread` | `SEED-1c58ea9c18b9adce056ad8d8`, `SEED-f8a9b7a517767afe06918391` |
| `revoke_review_link` | `SEED-0bbd614e466ba57d43091942`, `SEED-337c7bfafd892f3dee5ca3ed`, `SEED-5e73bd1a9391c6af52805a5f`, `SEED-96e026ef7e47422ef9be1926`, `SEED-ca488ac48f7609e656897031` |
| `send_review_request` | `SEED-1cb3f22fadee73e021bb733b`, `SEED-40f8e56657681c5a85b5badf`, `SEED-857bd5c346bdb334d2ba5c12`, `SEED-88b34506701b1ac0726ce8a8`, `SEED-f77a81284fea9021dd14872a` |

## Explicit verification-basis audit

Basis refs were selected from the exact authority already chosen by the approved 2.0 handoff: `visible_success` plus `visible_error` for outcome, and `trace` for acceptance. The replay never scanned eligible authority and never auto-selected all candidates.

| Action | Outcome basis | Acceptance basis |
| --- | --- | --- |
| `create_pin` | `SEED-07c3ee5fc8648b578e618f5b`, `SEED-41684fac7ad6bc4a99009bde` | `SEED-ba5ac85922b87e8fb415dab0` |
| `reply_thread` | `SEED-2383c2533e4e5ad83e8b8b2d`, `SEED-276e712f11f6a6869f367df0` | `SEED-ba5ac85922b87e8fb415dab0` |
| `resend_review_request` | `SEED-0154fce39c180e44109a6f33`, `SEED-3b6a182fe085e1ffac13e56e` | `SEED-0154fce39c180e44109a6f33` |
| `resolve_thread` | `SEED-241c81dc3215aff557671dda`, `SEED-276e712f11f6a6869f367df0` | `SEED-ba5ac85922b87e8fb415dab0` |
| `revoke_review_link` | `SEED-0154fce39c180e44109a6f33`, `SEED-192daff597cf35694c577113` | `SEED-0154fce39c180e44109a6f33` |
| `send_review_request` | `SEED-0154fce39c180e44109a6f33`, `SEED-3b6a182fe085e1ffac13e56e` | `SEED-0154fce39c180e44109a6f33` |

All refs passed the exact scope, current-status, selector, and UX-locator checks. A separate synthetic probe included an additional eligible candidate and proved that the translator did not select it. The frozen `collect_exact` allowlist remained action fields `actor` and `input_invariants`, and lifecycle field `authority` only.

Had any mapping required a new value, priority, conflict resolution, or other product judgment, the helper would have stopped with `TRUE_SEMANTIC_GAP_FOUND`. That stop did not occur.

## New action-conformance/2.1 result

```text
handoff definition: joewrks.handoff-definition/2.1
action contract: joewrks.action-conformance/2.1
compiler status: AUTHORITY_READY_MACHINE_VERIFIED
semantic contract hash: b00b45e8ca4804289f5d8af3bb55fc6569ee65771838459b8ba49583df349b57
artifact hash: 03be371432ed0f2d2ada8b93d0abc6738c3b4b84e43817fb0aaad1e1e1aa1ab4
direct authority fields: 131
machine-derived fields: 7
review-required fields: 0
authority gaps: 0
semantic gaps: 0
expressiveness gaps: 0
re-entry events: 0
contract validation errors: 0
contract audit: CONFORMANT / SAME_APPROVED_REVISION
affected consumers: 0
```

The seven machine-derived fields are the six action `input_invariants` fields and `reply_thread.actor`. The semantic contract contains none of the three removed runtime-only fields. Its source authority still binds the exact approved definition and manifest digests above.

Semantic review remained:

```text
identity: joewrks.semantic-review/2.1
reliability: NOT_MEASURED
review-required fields: 0
review package: none required
```

Runtime planning remained:

```text
identity: joewrks.runtime-conformance-plan/1.0
plan hash: be6c95cc17fe986355d57d3c1b145fe4bbc7dae5af436b8df1e40ea9ea935d30
runtime profile: joewrks.runtime-responsibility/1.0
runtime profile digest: 035e83a108f96aeedc6475fe606a60312e326cb80d52522e51d67691e172ac64
coverage: COMPLETE
missing runtime-critical fields: 0
runtime mapping gaps: 0
validation errors: 0
```

The replay's deterministic known-slice draft used one `SUCCESS` verifier mapping per action, empty component/evidence overrides, and the non-value fixture category `OPAQUE_ID`. It supplied no `expected_value` or other caller product literal. All runtime-critical field references were concrete; `ANY` was not used as coverage.

## Boundary decision

The replay proves that M5.1 removes the stopped M6 executability blocker for this approved known slice. It did not execute M6 runtime tests, did not start M6 Task 6, did not modify the M6 branch, and did not merge, push, open a PR, or deploy. Resumption remains a separate continuation after independent M5.1 source verification.
