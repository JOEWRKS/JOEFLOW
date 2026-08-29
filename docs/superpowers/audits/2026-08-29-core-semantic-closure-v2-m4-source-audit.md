# Core Semantic Closure V2 — M4 Remote Source Audit

**Audit status:** `REMOTE_SOURCE_VERIFIED / USER_EXECUTION_REPORTED`

**Audited branch:** `feat/core-semantic-closure-v2-m4-semantic-freeze`

**Audited HEAD:** `82502688a16d53d5527f5e27171c5764d0039101`

**Tree:** `fc0aa868a2e466769e823a26d3b4d1694d6a7c12`

**Planning base:** `e463d3026b8c65938457e4cf69b201a3aaabcfd1`

## Verification boundary

This audit independently verifies remote Git history, changed-file scope, and inspected M4 source contracts through the connected GitHub repository. It does **not** claim independent execution of the local test commands reported by the implementation agent.

GitHub exposes no combined status checks and no workflow runs for the audited HEAD. Reported focused/regression/full-suite counts therefore remain `USER_EXECUTION_REPORTED`, not independently re-measured CI evidence.

## Remote history verification

Verified from GitHub:

- remote M4 branch HEAD is `82502688a16d53d5527f5e27171c5764d0039101`;
- HEAD tree is `fc0aa868a2e466769e823a26d3b4d1694d6a7c12`;
- HEAD parent is `e9264ef6f1e36ea78ee0c00f99309c5d13db9f8b`;
- compare from planning base `e463d302...` is `ahead_by: 13`, `behind_by: 0`;
- compare contains exactly 29 changed files;
- the frozen legacy `state.schema.json`, `state_validation.py`, `state-contract.md`, and `state.example.json` are absent from the M4 diff;
- no compare entry exists under `skills/joewrks-product-definition/downstream/` or `evals/semantic-review-v0.4.3/`;
- remote `main` remains `efd96410f6401cbf9624328e94b795c315164b7f`.

## Source-contract verification

### Exact semantic binding

`authority_binding_v2.py` implements record-relative RFC 6901 pointer resolution, canonical UTF-8 JSON SHA-256 value commitments, checked-in Product/UX binding-contract identity, Core/Grill/UX semantic binding validation, and authority-consumption analysis.

M4 positive semantic proof is no longer a status-only checkbox. A binding carries the stable record ID, record-relative pointer, and exact value hash. Positive proof is restricted to allowed semantic roots and rejects semantically empty values while retaining meaningful `false` and `0` values.

N/A basis authority remains separate from positive proof. Observed implementation/runtime/test evidence cannot independently justify an N/A product-intent claim, preserving the M2 rule that implementation absence is not product scope authority.

### Semantic definition digest and informed approval

`approval_v2.py` separates current product meaning from approval-control state. The semantic definition projection excludes current approval/history control objects and excludes unconsumed evidence from Product Definition meaning while retaining consumed evidence commitments.

The discovery baseline still commits all evidence for discovery freshness, but its all-evidence commitment is deliberately excluded from semantic approval meaning. This allows unconsumed evidence to stale discovery, be reconciled by rebuilding the baseline, and leave the approved semantic definition unchanged.

M4 also implements deterministic Approval Manifest/history commitments, same-revision semantic-commitment mutation detection, and stable-history retention checks so previously approved records cannot silently disappear instead of being explicitly superseded/retired.

### Approval trust boundary

The checked-in Semantic Freeze contract explicitly states that M4 verifies a **recorded approval claim** against exact revision, definition digest, manifest digest, and history commitment. It does not cryptographically authenticate the human identity behind that claim, synthesize `approved_at`, or auto-approve a READY state.

### Actual Semantic Closure gate

M4 removes the prior `semantic_closure_not_implemented` guard only after exact binding, semantic-readiness, digest, and approval gates are available.

The V2 evaluator now distinguishes structurally representable OPEN/READY states from a genuinely closed Product Definition. A valid `closed = true` result requires `project.definition_status = CLOSED`, exact current approval commitments, no frozen blocking metrics, minimum semantic definition, and completed discovery/Grill readiness.

This Closure means **Product Definition closed**, not implementation/design/deployment completion and not downstream conformance.

### Approved F5 fail-closed correction

The final commit `82502688...` closes the specifically approved second final-fix finding.

`evaluate_closure_v2()` now contains `BindingError` during malformed/duplicate-authority state validation instead of allowing the exception to escape. The final regression covers:

- duplicate stable ID + canonical OPEN Core coverage cell → evaluator returns `closed = false` rather than raising;
- the duplicate-ID validation error is preserved;
- semantic projection is marked unsafe and no definition digest is asserted;
- the official Closure CLI returns exit `1` with structured JSON and no traceback/stderr;
- the same canonical OPEN Core cell without the duplicate remains a normal non-closed state with a semantic digest;
- valid APPROVED/CLOSED behavior is not intentionally weakened by the containment path.

The correction is fail-closed; it does not select an arbitrary duplicate record as authority.

## Frozen identity checks visible in the audited tree

The audited M4 tree still contains the exact frozen legacy blobs:

```text
state.schema.json      6a03894cc2164a9bfabbe8627a8468124d19b1f7
state_validation.py    9a3b44359bddfd64c98392f235cb815a0b777cce
state-contract.md      05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf
state.example.json     5fed7e87da243b3d234148bbbbf3baf7350d8ab0
```

The audited tree also keeps:

```text
skills/joewrks-product-definition/downstream/
  b63568d8c4632b14bc806e7bff1908e94dea9669

evals/semantic-review-v0.4.3/
  a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43
```

## Execution evidence boundary

The implementation report states:

```text
M4 focused: 105/105 PASS
M3 regression: 146/146 PASS
legacy regression: 36/36 PASS
frozen legacy regression: 1/1 PASS
full suite: 530 tests OK, 1 pre-existing environment-dependent SKIP
git diff --check: PASS
final review: Critical 0 / Important 0 / Minor 0
```

It also reports valid Product/UX binding identities, zero Core/Grill/UX/authority-consumption blockers in the closed probe, deterministic definition/manifest digests, unconsumed-evidence approval stability, and a valid APPROVED/CLOSED `closed = true` probe.

Those results are preserved as implementation/user execution evidence. They were not independently rerun in this audit because the connected GitHub surface exposes no CI/status execution for this HEAD.

## Audit ruling

No source-level blocker was found against the frozen M4 scope in the inspected remote implementation.

Roadmap progression may treat M4 as:

```text
CORE_SEMANTIC_CLOSURE_V2_M4_IMPLEMENTED
— SEMANTIC_FREEZE / SEMANTIC_CLOSURE_AVAILABLE / NOT_INTEGRATED

remote source: VERIFIED
execution tests: USER_EXECUTION_REPORTED
independent execution remeasurement: NOT_PERFORMED
```

This ruling authorizes progression to M5 planning. It does not claim downstream 2.0, implementation conformance, semantic-review/2.0 reliability, deployment, or M6 integration.