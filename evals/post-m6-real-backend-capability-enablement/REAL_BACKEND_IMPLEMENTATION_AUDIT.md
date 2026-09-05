# Real backend implementation audit

## Bounded result and evidence identity

REAL_BACKEND_ADAPTER_IMPLEMENTED — BACKEND_PROVISIONING_REQUIRED

This is local implementation evidence, not admission for a real provider call.
Exactly one explicit Anthropic production candidate is registered, but it is
unprovisioned and preflight-ineligible. Real capability remains UNAVAILABLE;
synthetic preflight is NOT_RUN; real provider requests are 0; calibration is
CALIBRATION_NOT_RUN; semantic-review/2.1 reliability is NOT_MEASURED; v0.4.4
remains BLOCKED. Test doubles cannot establish real capability authority.

- Branch: `codex/post-m6-real-backend-capability-enablement`.
- Implementation-only base: `c48f341b0e8545aa6c666e9b5ccc934016e6b88f`;
  tree `46ec38dd791b8971fad9cb744c6eba48f63b12f7`.
- Approved design commit: `c1c06dca65ae007cb59353a75788eaf2096bd219`;
  design: `docs/superpowers/specs/2026-09-05-post-m6-real-backend-capability-enablement-design.md`.
- Frozen authority/main: `ab95074704af0e93248d56344d6a220dfec88a93`;
  tree `867bec6fcfe5f4dc9927beaaf143087178e09e7c`.
- Final code-only commit: `7a55d71cbef4a4ecd9950a68b06a5bf38514878c`.
- Final code-only tree: `b604a8bca785a750863fa7fdb78b076daab8f5e8`.
- Code-only parent: `be72b26e493a8115992358dadb50f17eeae61ea6`.

The code-only worktree was clean before final verification and before writing
these two evidence files. The JSON binds the code-only commit/tree above, not its
own later evidence commit, avoiding self-reference. Its exact canonical output
contains 21 fields, UTF-8 without BOM, sorted compact JSON, and one final LF.
Neither artifact adds a timestamp-derived evidence field or a credential value.

## Commit and review provenance

Exact Git subjects, in chronological order from the implementation-only base:

```text
c3e7d6d8beab8a4f2a2cdd372a122cd969a31b2a feat: add anthropic request projection
c814f83efc41263d0bc764cd14957f10ce1431e0 fix: address Task 1 review findings
a2e24a6676c93fadc21c693486940241fb1883af feat: bind anthropic preflight admission evidence
308a542409a99b68d003f76b58765c37e2ff43ce fix: address Task 2 review findings
dda079b901ee8127b282f9e9c9ebd35a14f40305 fix: address Task 2 review findings
9c9c00232e115c0cc3c5296646ea0b131b2b126f feat: add one-request anthropic transport
720898303a3df3e412891e8844df2408be61c9e9 fix: address Task 3 review findings
daf57b874283873fd4b21dfb5b301a0676fd88d2 feat: bind anthropic provider responses
2cb3e4bfd56a01dc14a57b7daf34e5b12491e57a fix: address Task 4 review findings
bb73bc41c3159f7ffffc3b20d779972d483a9cd3 feat: register anthropic backend candidate
b2912c62100302ecfbe6b42815b3dcc6daa18f17 fix: address Task 5 review findings
deaee26d2f7954a567ce843bc73a044d4f76a785 test: evolve real backend capability audit
da3b90e0a195a00282ec123afc98f5c020efb28a fix: address Task 6 review findings
d146eddf28e097dd6a81e45ad1bad04e08140bff test: harden anthropic adapter offline boundaries
3c04b3f4f4c2b31f812711ca66aa6e10acd6f34f fix: address Task 7 review findings
7acb22d15a81d191259ccfb4754c6ecf630e323b fix: address Task 7 review findings
c77a985fe1fb6b96d949087b95a2f3507968f2e4 fix: address Task 7 review findings
4cef73158800292d12fc1d6caac7f70d63104779 fix: address Task 7 review findings
688ea9b6bac5b8bb37bcf5d1621708e7af27bea4 fix: address Task 7 review findings
6208ac23b015cef74a6778875afdced50a08f946 fix: address Task 7 breaker findings
be72b26e493a8115992358dadb50f17eeae61ea6 fix: address Task 8 precondition review findings
7a55d71cbef4a4ecd9950a68b06a5bf38514878c fix: address Task 8 full-suite regressions
```

Task 8's evidence commit subject is `test: audit anthropic backend implementation`.
Its identity is intentionally outside the code-only evidence binding.

Independent review history is recorded below as Critical/Important/Minor counts.
The clean result is a scoped review, not a claim that the pending Task 8 evidence
review or final whole-branch review has occurred.

| Task | Controlled initial RED; final declared GREEN | Review and correction outcome |
| --- | --- | --- |
| 1: projection | 7 tests, 7 assertion failures, 0 errors; 25/25 GREEN | Initial 0/1/0; boolean response-count fix at c814f83; final 0/0/0 |
| 2: admission | 11 tests, 11 assertion failures, 0 errors; 43/43 final GREEN | Initial 0/2/1; first re-review 0/2/0; two fixes bind secret-free credential readiness, row isolation, exact methods, workspace channels and fail-before-hashing; final 0/0/0 at dda079b |
| 3: transport | 8 methods, 20 assertion failures, 0 errors; 60/60 final GREEN | Initial 0/3/0; truncation, sanitized header failure and stdlib Content-Length proof corrected; final 0/0/0 at 7208983 |
| 4: response | 13 methods, 29 assertion failures, 0 errors; 91/91 final GREEN | Initial 0/4/0; missing-credential outcome, parse order, exception containment and strict response cases corrected; final 0/0/0 at 2cb3e4b |
| 5: registration | 7 assertion failures, 0 errors; 25/25 final GREEN | Initial 0/2/0; revision inventory and absolute public-import escape corrected; final 0/0/0 at b2912c6 |
| 6: capability audit | 23 tests, 6 assertion failures, 0 errors; 24 audit plus 9 registration tests final GREEN | Initial 0/2/1; canonical injection invariance, no-access traps and loader wording corrected at da3b90e; final scoped review 0/0/0; historical v1.0 remains byte-exact |
| 7: offline boundaries | Controlled recovery RED 10 methods, 10 assertion failures, 0 errors; exact 14-module suite 247/247 GREEN | Five separate review-fix commits retained; final Task 7 review still 0/2/0, explicitly carried into Task 8 rather than called clean |
| 8: carried audit findings | 10 methods, 6 assertion failures, 0 errors; 247/247 GREEN at 6208ac2 | Invoke and mutable transport/authentication dependencies bound; precondition review found one describe-time timing gap (0/1/0) |
| 8: precondition timing fix | 10 methods, 4 assertion failures, 0 errors; 247/247 GREEN at be72b26 | Revalidate original captured bindings immediately after describe; independent review 0/0/0, including 15 describe-time mutation/path combinations; both carried Task 7 findings closed |
| 8: full-suite test correction | Original discovery had 1 failure, 46 errors, 1 known skip; targeted order/policy 33/33 and focused 247/247 GREEN | Test-module restoration and exactly five stdlib allowlist entries corrected at 7a55d71; production behavior unchanged; Task 8 scoped review pending after evidence commit |

Review-fix controlled RED assertion counts were: Task 1: 1; Task 2: 2 then 5;
Task 3: 5; Task 4: 5; Task 5: 2; Task 6: 2; Task 7 rounds 1–5: 6, 3, 3, 2,
2, each within its existing ten offline methods. Every cited controlled RED had
zero errors. Task 7 round 3 required one evidence-based compatibility correction
after its first declared suite; the corrected suite passed 247/247. These are
recorded task results, not tests newly rerun for this artifact.

Task 7's initial and successive scoped review counts were 0/3/0, 0/2/0,
0/3/0, 0/1/0, 0/1/0, and 0/2/0. The final two findings were explicitly
carried under the five-round ruling, then closed by the independent Task 8
precondition review at be72b26. Task 7's first fix also moved default credential
lookup from construction into invoke after its named credential-timing
regression; no provider change was made in the Task 8 corrections.

An initial Task 8 regression fixture used the wrong descriptor field and caused
three errors; it was discarded as invalid RED, corrected before audit changes,
and followed by the controlled 6-assertion-failure RED above. The failed initial
full discovery is likewise not claimed as controlled assertion RED.

## Exact changed-file manifest

Twelve code/test files differ from the implementation-only base at the code-only
revision. Every entry has mode 100644; exact code-only Git blob IDs follow.

```text
100644 blob 9a4bc448afba2ebc86573ec5fafbe97612f0d8bf	skills/joewrks-product-definition/reviewer_runner/providers/__init__.py
100644 blob 39a3009b46feee45acb3d40c86589dcaafde0e3c	skills/joewrks-product-definition/reviewer_runner/providers/anthropic.py
100644 blob c673fc482db24f8c1a74a33cbd78cc4cec8e3a42	skills/joewrks-product-definition/reviewer_runner/providers/anthropic_admission.py
100644 blob cdd0d8da2e4f45a790f165f141918f61fadbb039	skills/joewrks-product-definition/scripts/audit_reviewer_runner.py
100644 blob 6935cbcf4660c6f6dc80a716ebc0315362f58548	tests/test_reviewer_runner_anthropic_admission.py
100644 blob ac17c50eb091c6cff1b3c61d24c1c10e48d2ad7a	tests/test_reviewer_runner_anthropic_offline.py
100644 blob b9c9ec1b18049e78918e7414c26e5de35177c816	tests/test_reviewer_runner_anthropic_projection.py
100644 blob 8cb663166b5cf88819216b114acf9038f469fa76	tests/test_reviewer_runner_anthropic_registration.py
100644 blob 1887285160800a99794535139c3315ee8ea3561c	tests/test_reviewer_runner_anthropic_response.py
100644 blob d20d2d3af0b1c171c1f456440c8a3cff57f53aac	tests/test_reviewer_runner_anthropic_transport.py
100644 blob 530e97b8a8d3898b45f651d9e4bcbd398d3aa6bb	tests/test_reviewer_runner_audit.py
100644 blob fbece719814a05474f2829453d7efef6834c3975	tests/test_skill_package.py
```

The provider package and six Anthropic test modules are additions. The audit
script, existing audit tests, and package-policy test are modifications.
The separately authorized full-suite correction changed only offline and
registration test cleanup plus the package-policy allowlist. Original module
objects and the parent package attribute are restored exactly, with identity
assertions; only the five directly imported stdlib modules `ast`, `http`,
`socket`, `threading`, and `types` were added to the allowlist.

Task 8 adds exactly these two evidence files:

```text
evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_CAPABILITY_EVIDENCE.json
evals/post-m6-real-backend-capability-enablement/REAL_BACKEND_IMPLEMENTATION_AUDIT.md
```

Total implementation-wave manifest after evidence is therefore 14 files.
The local task/review reports are workflow records, not additional tracked
implementation artifacts.

## Final code-only verification

All commands below ran from the implementation worktree on the exact final
code-only commit/tree above. These are fresh post-commit results. There were no
code changes between them.

### Complete focused runner suite

```powershell
python -m unittest tests.test_reviewer_runner_anthropic_projection tests.test_reviewer_runner_anthropic_admission tests.test_reviewer_runner_anthropic_transport tests.test_reviewer_runner_anthropic_response tests.test_reviewer_runner_anthropic_registration tests.test_reviewer_runner_anthropic_offline tests.test_reviewer_runner_identity tests.test_reviewer_runner_request tests.test_reviewer_runner_backend tests.test_reviewer_runner_preflight tests.test_reviewer_runner_response tests.test_reviewer_runner_evidence tests.test_reviewer_runner_controller tests.test_reviewer_runner_audit -v
```

Result: exit 0; 247 tests in 167.093s; OK; 0 failures, 0 errors, 0 skips.
The six Anthropic modules and every declared existing runner module passed.
The offline module still contains exactly ten test methods.

### Semantic-review/1.0 and calibration-controller regressions

```powershell
python -m unittest tests.test_semantic_review_hashing tests.test_semantic_review_responsibility tests.test_semantic_review_package tests.test_semantic_review_output tests.test_semantic_review_goldens tests.test_semantic_review_gate tests.test_semantic_review_statistics tests.test_semantic_review_negative_regressions tests.test_semantic_review_calibration_corpus tests.test_semantic_review_calibration_control_plane tests.test_official_calibration_controller tests.test_semantic_review_human_packet -v
```

Result: exit 0; 146 tests in 40.959s; OK; 0 failures, 0 errors, 0 skips.
Controller regression fixtures do not execute real calibration.

### Semantic-review/2.1, M6, runtime and frozen boundaries

```powershell
python -m unittest tests.test_downstream_v21_derivation tests.test_downstream_v21_compiler tests.test_downstream_v21_gap_routing tests.test_downstream_v21_audit tests.test_downstream_v21_semantic_review tests.test_downstream_v21_runtime_plan tests.test_downstream_v21_runtime_evidence tests.test_downstream_v21_dogfood_replay tests.test_downstream_v21_frozen_boundaries tests.test_core_semantic_closure_v2_m6_dogfood_phase_a tests.test_core_semantic_closure_v2_m6_dogfood_phase_b tests.test_m6_runtime_v21_verification tests.test_m6_client_feedback_portal_fixture -v
```

Result: exit 0; 142 tests in 124.420s; OK; 0 failures, 0 errors, 0 skips.

### Legacy and full discovery

```powershell
python -m unittest tests.test_legacy_v0121_frozen tests.test_validators tests.test_semantic_v012 -v
python -m unittest discover -s tests -v
git -c core.autocrlf=false -c core.eol=lf diff --check
```

Legacy: exit 0; 37 tests in 4.769s; OK; 0 failures, 0 errors, 0 skips.
Full discovery: exit 0; 1,173 tests in 494.554s; OK (skipped=1);
1,172 passed, 0 failures, 0 errors. Diff check: exit 0, empty output.

The sole pre-existing environment-dependent skip was
`test_downstream_adapters.FrozenRuntimeRegressionTest.test_pinned_a_and_b_defects_are_executed_and_detected`,
with exact reason:
`set JOEWRKS_FROZEN_A_ROOT and JOEWRKS_FROZEN_B_WORKTREE for pinned runtime regression`.
No Anthropic/runner test skipped. The JSON structural-schema migration test ran
and passed; it was not skipped for a missing PowerShell facility.

### Failure retained and bounded rerun

The earlier code-only revision be72b26 passed focused 247, semantic/1.0 146,
semantic/2.1/M6 142 and legacy 37, but full discovery failed: 1,173 tests in
594.728s, 1 assertion failure, 46 errors, 1 skip. Provider-module eviction in
offline/registration cleanup left collection-time response configuration classes
stale; the package policy also omitted five new stdlib imports. This was not a
provider failure. No evidence was written for that failed run.

After the authorized test-only correction, the original order
`offline -> registration -> response` plus the exact package-policy test passed
33/33 in 63.149s, and the precommit focused suite passed 247/247 in 166.642s.
There was then exactly one full-discovery retry on final commit 7a55d71, recorded
above. All thirteen response methods and the originally failing package-policy
method passed in full discovery. No failure was hidden by a changed production
type check, weakened assertion, reordered discovery, or new skip.

## Exact historical fixture lifecycle

The semantic/2.1/M6, legacy and full-discovery commands shared one temporary
detached worktree, with `JOEWRKS_M6_PHASE_B_WORKTREE` bound throughout:

- Fixture commit: `d38b0ca04768888c47e658c79f41e1cec0a7a1ce`.
- Fixture tree: `40749d900b98936cf694b0c96db7897011cddae8`.
- Creation: `git -c core.autocrlf=false -c core.eol=lf worktree add --detach`
  at that exact commit under a new task-owned temporary root.
- Resolved path, HEAD, tree and clean status verified before binding.
- Checkout-induced LF-to-CRLF/mixed drift: 0. Eleven historically committed
  CRLF JSON files remained byte-for-byte historical; they were not normalized.
  A raw historical-revision diff was empty.
- After all suites: HEAD and tree still exactly matched; fixture status clean.
- Removal: `git worktree remove` on the exact resolved fixture, without force.
- Readback: fixture path absent, temporary root absent, exact original worktree
  registry restored. The initially absent fixture environment variable was
  restored to absence in a finally block.

The first Phase B fixture diagnostic had incorrectly demanded LF in every
historical file and stopped before tests. Its temporary state was fully removed
and restored. The recorded ruling preserved exact historical bytes and checked
checkout drift instead. The final successful lifecycle above is distinct from
that diagnostic and from the earlier failed-discovery lifecycle.

## Admission matrix and descriptor boundary

The unchanged generic `REQUIRED_CAPABILITIES` tuple has exactly 17 entries, each
represented exactly once, in order. For complete synthetic frozen evidence, the
exact direct-method mapping is:

| Capability | Direct method |
| --- | --- |
| stateless_fresh_request | direct:anthropic-single-message-body |
| no_continuation_id | direct:anthropic-no-continuation-fields |
| no_reviewer_memory | direct:anthropic-direct-messages-stateless-contract |
| no_tools | direct:anthropic-tool-fields-absent |
| no_retrieval | direct:anthropic-retrieval-fields-absent |
| no_web_or_browser | direct:anthropic-web-fields-absent |
| no_connectors_or_mcp | direct:anthropic-connector-mcp-fields-absent |
| no_host_filesystem | direct:anthropic-inline-text-only |
| no_code_execution | direct:anthropic-code-execution-fields-absent |
| no_file_by_reference | direct:anthropic-no-file-reference |
| immutable_model_or_deployment_identity | direct:anthropic-pinned-model-workspace-commitment |
| immutable_inference_settings | direct:anthropic-canonical-settings |
| sufficient_payload_capacity | direct:anthropic-capacity-and-quota-record |
| exact_structured_output | direct:anthropic-one-text-existing-json-validator |
| controller_only_authentication | direct:anthropic-workspace-key-controller-boundary |
| accepted_retention_and_privacy | direct:anthropic-approved-account-policy |
| request_response_commitments | direct:anthropic-request-response-hash-binding |

Admission tests bind each observation to its closed record/hash input, reject
missing and contradictory dependencies, and keep contradictions row-scoped.
Workspace evidence, retention/privacy policy, model entitlement, capacity/quota,
spend and credential-readiness evidence remain separate required dependencies.
Credential readiness is a domain-separated non-secret evidence commitment, not
a hash of an API key. Synthetic all-OBSERVED_PASS fixtures prove local logic only.

The registered production instance has non-test identity but unprovisioned
observations. Registration and descriptor counting do not admit it: classification
is UNAVAILABLE, preflight returns before invoke, and direct unprovisioned invoke
returns BACKEND_PROVISIONING_REQUIRED before credential or transport access.
A test transport or custom credential reader forces test-double identity and
UNTESTED observations; it cannot become real authority.

The frozen descriptor and its hash are computed before invocation. The current
invoke implementation does not update the descriptor; its run-specific provider
body hash enters only sanitized RESPONSE-event metadata. Admission freshness and
the existing preflight/controller descriptor-drift tests verify the boundary.
This is offline implementation proof, not an executed real P1/P2 proof.

## Offline, transport and audit integrity

The focused offline suite guards environment reads, DNS, sockets and HTTPS while
exercising import, registration, describe and audit. A key's presence alone never
triggers integration execution. Only the future authorized invoke path may read
the named credential, exactly once. Fake credential and raw workspace sentinels
are checked for exclusion from persistable objects, responses, events, audit,
exceptions and representations. No real credential value was inspected.

Transport tests use fake connections and socket-free serialization. The approved
implementation uses one fresh direct stdlib HTTPS connection, fixed Messages
endpoint, four explicit headers, exact body, no SDK/proxy lookup, no streaming,
no automatic retry, no second provider, discovery, router or fallback. Failure
classes issue zero or one request, with zero application retries. Success binds
the validated exact text bytes, model, request ID, workspace commitment and
sanitized response event through the existing freeze/parse/replay/controller.

The offline audit binds verified committed source, closed AST commitments, exact
backend and transport classes, invoke/post function and code identity, effective
bound methods and class interception. It also binds the mutable factory and
credential-reader slots and exact stdlib HTTP/authentication dependencies.
The same captured binding is checked immediately after each descriptor-consuming
describe callback, before accepting it. Committed adversarial revisions cover
wrappers, aliases, computed/reflection method access, export replacement,
post-construction seam mutation and describe-time mutation. These checks fail
closed without invoking the registered backend or reading credential values.

Real network/provider requests during this implementation and verification: 0.
Application retries: 0. Account provisioning, Token Counting, Admin API, P1/P2,
real semantic calibration, reliability measurement and v0.4.4 work: not started.
The historical calibration counters remain attempts=1, valid runs=0; this wave
added no attempt and did not reset the historical counter.

## Audit readback and frozen compatibility

```powershell
python skills/joewrks-product-definition/scripts/audit_reviewer_runner.py --repository . --revision 7a55d71cbef4a4ecd9950a68b06a5bf38514878c --json
python skills/joewrks-product-definition/scripts/audit_reviewer_runner.py --repository . --revision 0b754bdc2502be35a7f657275f17fe117e8c49bd --json
python -m unittest tests.test_reviewer_runner_audit tests.test_reviewer_runner_anthropic_offline -v
```

The first CLI returned the exact bounded v1.1 object frozen beside this record,
with registered count 1 and provider candidate/selection anthropic, not capability
PASS. The historical v1.0 CLI still reports no selected provider and zero
registered real adapters for its historical code-only revision/tree.

Fresh subprocess stdout was compared as raw bytes against both files. The new
JSON is 907 bytes, SHA-256
`7dd95c374ab126d6605a4ee0145836185297bb521fea41ce2782a80347c08a3f`.
Both outputs exactly equal sorted compact UTF-8 JSON plus one LF, with no BOM
or CR. The v1.1 object has exactly 21 keys; the historical v1.0 object has 16.

Historical artifact:
`evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json`.

- Historical code commit: `0b754bdc2502be35a7f657275f17fe117e8c49bd`.
- Historical code tree: `8c980cf9fd8937f5ae51d6c8b509098c5a91145b`.
- Historical byte count: 725.
- SHA-256: `f6ab1dd8fc5aa8cab5a75bc5c9d926977badb7806a899747b2baec35e2b21233`.
- Git blob: `38b581536323f63d7809e1280217679406de152a`, matching frozen authority.

```powershell
git diff --exit-code ab95074704af0e93248d56344d6a220dfec88a93..HEAD -- product-definition
git diff --exit-code ab95074704af0e93248d56344d6a220dfec88a93..HEAD -- skills/joewrks-product-definition/downstream
git diff --exit-code ab95074704af0e93248d56344d6a220dfec88a93..HEAD -- skills/joewrks-product-definition/downstream_v21
git diff --exit-code ab95074704af0e93248d56344d6a220dfec88a93..HEAD -- evals/semantic-review-v0.4.3
git diff --exit-code ab95074704af0e93248d56344d6a220dfec88a93..HEAD -- evals/core-semantic-closure-v2-m6
git diff --exit-code ab95074704af0e93248d56344d6a220dfec88a93..HEAD -- evals/post-m6-semantic-review-reliability-enablement/RUNNER_CAPABILITY_EVIDENCE.json
git diff --check
```

Final evidence readback suite: exit 0; 34 tests in 81.837s; OK;
0 failures, 0 errors, 0 skips. All six frozen diffs exited 0 with empty
output. Working diff check passed. Final evidence bytes were read back as UTF-8
with zero CR and a final LF; JSON raw-byte equality was verified against the
fresh v1.1 CLI and the unchanged historical v1.0 CLI.

The exact changed-file manifest also establishes that generic runner interfaces,
four-role request/output schemas, semantic-review/1.0 and /2.1 contracts, oracle,
goldens, thresholds, counters, Product Definition, M6, action/runtime conformance
and v0.4.3 were not modified. Local `origin/main` still resolves to the frozen
authority commit; no fetch, push, remote write, merge, PR or publication occurred.
This record makes no fresh remote-state claim.

## Stop boundary

Task 8 stops after its GREEN evidence commit and clean-status verification for
independent scoped review. That review, later final whole-branch review and any
publication are not asserted complete here. Real capability remains unavailable
until separately authorized provisioning and real P1/P2 proof are accepted.
