# Core Semantic Closure V2 — M5 Remote Source Audit

**Audit date:** 2026-08-30

**Implementation branch:** `feat/core-semantic-closure-v2-m5-downstream-v2`

**Implementation HEAD:** `b8ac6b87dffeb5ecda0590e31e98a306a9749609`

**Planning base:** `74f37511cb7120630ee940abacd14358265a8a70`

**Status:** `REMOTE_SOURCE_VERIFIED / USER_EXECUTION_REPORTED`

## What this audit means

This audit independently inspected the pushed GitHub source and commit topology. It did **not** re-run the user's local test suite. GitHub exposes no commit statuses or workflow runs for the M5 HEAD, so reported test counts remain execution evidence supplied by the implementer rather than independently reproduced CI evidence.

## Git identity

The remote implementation branch resolves to:

- HEAD `b8ac6b87dffeb5ecda0590e31e98a306a9749609`
- parent `0c107144a42e90de2111006f683d9636c80c7698`
- tree `0eca579a68b3611c7e3ece6e8526444522e9666a`

The branch is exactly 15 commits ahead of planning base `74f37511cb7120630ee940abacd14358265a8a70` and zero commits behind that base.

The implementation diff contains exactly 33 files:

- 21 files under `skills/joewrks-product-definition/downstream_v2/`;
- 2 new top-level V2 reference documents;
- 10 downstream V2 tests/support files.

No file in the frozen downstream v1 tree, frozen v0.4.3 semantic-review evidence, legacy state contract, or M4 protected authority core appears in the implementation diff.

Remote `main` remains `efd96410f6401cbf9624328e94b795c315164b7f`.

## Source-level contract findings

### 1. Initial compilation is M4-closure gated

`downstream_v2.authority.require_closed_authority()` calls the actual M4 `evaluate_closure_v2()` and requires state schema `0.2.0`, `closed = true`, zero closure errors, `project.definition_status = CLOSED`, exact current approval revision, and approval definition digest parity. It returns read-only source-authority metadata and does not mutate state.

### 2. M4 exact bindings seed downstream authority

The compiler builds available source seeds from positive Core, Grill and UX bindings, then materializes only the source seeds actually referenced by successfully derived fields. The production contract therefore commits `consumed_seed_inventory_digest` rather than the full available Product Definition seed pool.

### 3. Scope commitments preserve dependency-local meaning

Action/lifecycle definitions declare `authority_scope_refs`; materialized contracts commit exact current `REQ`, `SURF`, and `SCR` record hashes. This closes the case where a scope record changes materially while one individual bound value happens to remain byte-identical.

### 4. Semantic debt classes are separated from authority gaps

The M5 compiler distinguishes:

- `DIRECT_AUTHORITY`;
- `MACHINE_DERIVED`;
- `REVIEW_REQUIRED`;
- `SEMANTIC_AUTHORITY_GAP`.

An authority gap prevents contract materialization and produces re-entry data instead of being converted into `REVIEW_REQUIRED`.

### 5. Re-entry is read-only and affected-scope only

`downstream_v2.reentry` produces `joewrks.product-definition-reentry/1.0` artifacts with `halt_scope.mode = AFFECTED_ONLY`. The artifact contains a candidate unknown proposal but does not allocate a canonical `UNK-*`, write `state.json`, change approval, or increment the Product Definition revision.

The existing-contract audit distinguishes original source provenance from current local dependency compatibility. A newer global Product Definition revision does not automatically invalidate an old contract if its consumed exact seeds and declared scope commitments remain exact.

### 6. Semantic Review 2.0 does not create authority

`joewrks.semantic-review/2.0` packages contain only `REVIEW_REQUIRED` obligations. Output validation binds every result to the exact package obligation and proposed value hash. Review completion is separate from reliability; M5 hard-codes reliability to `NOT_MEASURED` and does not inherit v0.4.3 results.

Review results may emit read-only re-entry artifacts. They do not mutate contract values or Product Definition state.

### 7. Runtime integration remains deliberately absent

The M5 README explicitly scopes implementation/runtime verification, installed routing, representative dogfood and production adoption to M6 or later. This matches the M5 milestone boundary.

## Final-review correction observed in source

The final commit `b8ac6b8` strengthens fail-closed validation boundaries, including:

- deterministic source-seed key/location validation;
- nonblank and unique unresolved evidence references;
- semantic debt count validation;
- recursive/canonical JSON failure containment;
- CLI containment for excessive nesting;
- stricter scope and action locator validation.

No source-level blocker was found that requires reopening M5 before M6 planning.

## Verification boundary

The implementer reported:

- M5 focused `114/114 PASS`;
- M4 regression `105/105 PASS`;
- M3/M2 regression `146/146 PASS`;
- downstream v1 `43 PASS / 1 SKIP`;
- semantic-review v1/v0.4.3 `133/133 PASS`;
- legacy `37/37 PASS`;
- full repository `643 PASS / 1 SKIP` out of 644;
- `git diff --check` PASS;
- final review Critical/Important/Minor `0/0/0`.

Those numbers are retained as `USER_EXECUTION_REPORTED`; they are not represented as independently re-executed by this audit.

## M6 admission decision

**Source-level decision:** `ADMIT_TO_M6_PLANNING`.

M6 must preserve the verified M5 contract identities and frozen historical trees while completing only the integration/adoption work left by the frozen design: deterministic migration, installed workflow routing, implementation/runtime verification, representative existing-product dogfood, user approval checkpoints, and final R1–R10 compatibility evidence.
