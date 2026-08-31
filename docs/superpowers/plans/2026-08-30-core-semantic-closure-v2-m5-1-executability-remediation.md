# Core Semantic Closure V2 — M5.1 Downstream Executability Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a new downstream 2.1 semantic handoff and runtime-conformance-plan boundary that preserves exact approved Product Definition authority, distinguishes semantic gaps from contract/runtime limitations, and makes the stopped M6 dogfood safe to resume without changing its approved product meaning.

**Architecture:** Keep every historical downstream contract frozen and add a sibling `downstream_v21/` package. `joewrks.action-conformance/2.1` carries approved product meaning only, with narrowly field-gated `collect_exact` for lossless exact sets and a `verification_basis` that preserves outcome/acceptance provenance after verifier-only fields move out of semantic authority. `joewrks.runtime-conformance-plan/1.0` maps the valid 2.1 contract into deterministic verification cases without reading Product Definition directly or introducing product literals; runtime evidence remains the frozen `joewrks.downstream.execution/1.0` transport and is bound to the runtime plan through a new non-authoritative evidence bundle.

**Tech Stack:** Python 3 standard library, JSON/JSONL, repository-supported Draft 2020-12 schema subset, RFC 6901 JSON Pointer, canonical UTF-8 JSON SHA-256, `unittest`, Git.

**Spec:**
- `docs/superpowers/specs/2026-08-30-core-semantic-closure-v2-m5-1-executability-remediation-design.md`
- `docs/superpowers/specs/2026-08-30-core-semantic-closure-v2-m5-1-executability-remediation-self-review.md`

## Global Constraints

- Authority order: frozen Core Semantic Closure V2 design > M5.1 design self-review > M5.1 design > this plan's self-review clarification > this implementation plan > implementation convenience.
- Implement on a new isolated branch/worktree created from the exact final M5.1 planning HEAD containing this plan and its self-review. Do not code in the planning branch.
- Preserve `skills/joewrks-product-definition/downstream/` at tree `b63568d8c4632b14bc806e7bff1908e94dea9669`.
- Preserve `evals/semantic-review-v0.4.3/` at tree `a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43`.
- Preserve the complete M5 `skills/joewrks-product-definition/downstream_v2/` package at tree `33fb2653531fa85dcc8fd8c94cbbb7cc5c41d41e`.
- Preserve legacy `0.1.2.1` blobs exactly: schema `6a03894cc2164a9bfabbe8627a8468124d19b1f7`, validator `9a3b44359bddfd64c98392f235cb815a0b777cce`, reference `05ae6f4c16ab65b8de9e2773a83a5ac38adaabcf`, template `5fed7e87da243b3d234148bbbbf3baf7350d8ab0`.
- Do not modify state schema `0.2.0`, M4 authority binding, approval, Semantic Closure, Product/UX binding contracts, or Approval Manifest semantics.
- Do not redefine `joewrks.action-conformance/2.0`, `joewrks.handoff-definition/2.0`, `joewrks.downstream-responsibility/1.0`, `joewrks.semantic-review/2.0`, or `joewrks.downstream.execution/1.0`.
- New contract identities are exactly: `joewrks.action-conformance/2.1`, `joewrks.handoff-definition/2.1`, `joewrks.downstream-responsibility/2.0`, `joewrks.runtime-conformance-plan/1.0`, `joewrks.runtime-responsibility/1.0`, `joewrks.semantic-review/2.1`.
- The new transport-preserving evidence-envelope identity is `joewrks.runtime-evidence-bundle/1.0`; it is verification metadata, not Product Definition authority and not a replacement for `joewrks.downstream.execution/1.0`.
- `joewrks.semantic-review/2.1` reliability is exactly `NOT_MEASURED` throughout M5.1.
- No arbitrary `compose`, object construction, template, callback, expression language, `eval`, string concatenation, natural-language parsing, or caller-supplied product literal is allowed.
- Product-specific runtime expected values come only from a valid action-conformance/2.1 field or its committed `verification_basis` seed. Fixture-only values may be opaque IDs, ordering timestamps, or revision instances only; they may not define product policy.
- A bare contract field reference does not satisfy runtime coverage. Coverage requires a concrete executable relationship.
- `ANY` never satisfies runtime-critical semantic coverage.
- Only a true `SEMANTIC_AUTHORITY_GAP` may generate Product Definition re-entry. `CONTRACT_EXPRESSIVENESS_GAP` and `RUNTIME_MAPPING_GAP` must not allocate canonical unknowns or change Product Definition revision/approval.
- The preserved local M6 implementation worktree and local Phase-B commit `d38b0ca04768888c47e658c79f41e1cec0a7a1ce` are read-only inputs to the final dogfood replay gate. M5.1 implementation must not mutate that worktree.
- Do not merge to `main`, do not create a PR, and do not claim M6 complete.
- Every behavior-changing task follows RED → GREEN → refactor and ends with a commit.

---

# File Map

## New `downstream_v21` package

Create:

- `skills/joewrks-product-definition/downstream_v21/__init__.py` — public M5.1 library surface and version identities.
- `skills/joewrks-product-definition/downstream_v21/identity.py` — exact contract/compiler identity constants and canonical hash helpers that reuse the frozen canonical JSON convention.
- `skills/joewrks-product-definition/downstream_v21/responsibility.py` — load/validate downstream-responsibility/2.0, selector matching, field collection semantics.
- `skills/joewrks-product-definition/downstream_v21/derivation.py` — DIRECT/extract/select/collect_exact/REVIEW derivation with typed semantic vs expressiveness failures.
- `skills/joewrks-product-definition/downstream_v21/gaps.py` — gap records and routing; only semantic gaps can become M5 re-entry events.
- `skills/joewrks-product-definition/downstream_v21/contracts.py` — action-conformance/2.1 hash projection and validator.
- `skills/joewrks-product-definition/downstream_v21/compiler.py` — compile handoff-definition/2.1 from exact M4/M5 seed authority, materialize `verification_basis`, debt and gap results.
- `skills/joewrks-product-definition/downstream_v21/runtime_profile.py` — runtime-responsibility/1.0 identity and exact class inventory.
- `skills/joewrks-product-definition/downstream_v21/runtime_plan.py` — runtime-conformance-plan/1.0 materialization, hash, validation, concrete coverage calculation, mapping-gap inventory.
- `skills/joewrks-product-definition/downstream_v21/runtime_evidence.py` — `runtime-evidence-bundle/1.0`, frozen execution/1.0 admission, semantic-contract/runtime-plan hash binding and evidence inventory.
- `skills/joewrks-product-definition/downstream_v21/semantic_review/__init__.py` — semantic-review/2.1 exports.
- `skills/joewrks-product-definition/downstream_v21/semantic_review/package.py` — review package builder/validator for REVIEW_REQUIRED 2.1 fields.
- `skills/joewrks-product-definition/downstream_v21/semantic_review/output.py` — review output validation and completion classification without authority mutation.
- `skills/joewrks-product-definition/downstream_v21/README.md` — M5.1 boundary/status markers.

Create schemas:

- `skills/joewrks-product-definition/downstream_v21/schemas/handoff-definition-v21.schema.json`
- `skills/joewrks-product-definition/downstream_v21/schemas/action-contract-v21.schema.json`
- `skills/joewrks-product-definition/downstream_v21/schemas/runtime-conformance-plan.schema.json`
- `skills/joewrks-product-definition/downstream_v21/schemas/runtime-evidence-bundle.schema.json`
- `skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-input-v21.schema.json`
- `skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-output-v21.schema.json`

Create frozen profiles:

- `skills/joewrks-product-definition/downstream_v21/references/downstream-responsibility-v2.json`
- `skills/joewrks-product-definition/downstream_v21/references/runtime-responsibility-v1.json`

Create top-level references:

- `skills/joewrks-product-definition/references/downstream-v2.1-contract.md`
- `skills/joewrks-product-definition/references/runtime-conformance-plan-contract.md`
- `skills/joewrks-product-definition/references/semantic-review-v2.1-contract.md`

Create tests/support:

- `tests/downstream_v21_support.py`
- `tests/test_downstream_v21_frozen_boundaries.py`
- `tests/test_downstream_v21_derivation.py`
- `tests/test_downstream_v21_compiler.py`
- `tests/test_downstream_v21_gap_routing.py`
- `tests/test_downstream_v21_semantic_review.py`
- `tests/test_downstream_v21_runtime_plan.py`
- `tests/test_downstream_v21_runtime_evidence.py`
- `tests/test_downstream_v21_dogfood_replay.py`

No existing `downstream_v2/` source or test is modified except that the full repository suite naturally discovers new tests.

---

### Task 1: Freeze M5 and implement 2.1 responsibility + exact derivation primitives

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v21/__init__.py`
- Create: `skills/joewrks-product-definition/downstream_v21/identity.py`
- Create: `skills/joewrks-product-definition/downstream_v21/responsibility.py`
- Create: `skills/joewrks-product-definition/downstream_v21/derivation.py`
- Create: `skills/joewrks-product-definition/downstream_v21/references/downstream-responsibility-v2.json`
- Create: `tests/downstream_v21_support.py`
- Create: `tests/test_downstream_v21_frozen_boundaries.py`
- Create: `tests/test_downstream_v21_derivation.py`

**Interfaces:**
- Consumes frozen helpers read-only from `downstream_v2.authority` and `downstream_v2.seeds` where exact canonical/hash/seed behavior is already correct.
- Produces:

```python
ACTION_CONTRACT_VERSION = "joewrks.action-conformance/2.1"
HANDOFF_DEFINITION_VERSION = "joewrks.handoff-definition/2.1"
RESPONSIBILITY_PROFILE_ID = "joewrks.downstream-responsibility/2.0"
SEMANTIC_REVIEW_VERSION = "joewrks.semantic-review/2.1"
RUNTIME_PLAN_VERSION = "joewrks.runtime-conformance-plan/1.0"
RUNTIME_PROFILE_ID = "joewrks.runtime-responsibility/1.0"
RUNTIME_EVIDENCE_BUNDLE_VERSION = "joewrks.runtime-evidence-bundle/1.0"

class SemanticAuthorityGap(ValueError): ...
class ContractExpressivenessGap(ValueError): ...

def load_responsibility_profile_v21() -> dict[str, object]: ...
def responsibility_profile_digest_v21() -> str: ...
def derive_semantic_field_v21(
    spec: dict[str, object],
    *,
    field_name: str,
    field_kind: str,
    context: dict[str, object],
    seeds: dict[str, dict[str, object]],
    profile: dict[str, object],
) -> dict[str, object]: ...
```

- `derive_semantic_field_v21()` returns exactly:

```python
{
    "value": <deep exact or deterministic derived value>,
    "source_seed_refs": [<sorted refs>],
    "derivation": <normalized derivation spec>,
}
```

#### Profile 2.0 construction rule

The new JSON profile starts from the exact retained field selector/authority mappings in frozen `downstream_v2/references/field-responsibility-v1.json`, removes only `default_result`, `result_expectations`, and `test_obligations`, and adds these required keys to every retained field entry:

```text
allowed_derivations
collection_semantics
```

Initial collection allowlist is exact:

```text
action.actor              MEMBERSHIP_SET
action.input_invariants   CONJUNCTIVE_SET
lifecycle.authority       MEMBERSHIP_SET
all other fields          NONE
```

Allowed derivations are exact:

```text
collection_semantics = MEMBERSHIP_SET or CONJUNCTIVE_SET
  → DIRECT_AUTHORITY, collect_exact
  → plus extract/select only when the frozen field was DETERMINISTIC_REQUIRED

collection_semantics = NONE and expectation = DIRECT_REQUIRED
  → DIRECT_AUTHORITY

collection_semantics = NONE and expectation = DETERMINISTIC_REQUIRED
  → DIRECT_AUTHORITY, extract, select

expectation = REVIEW_PERMITTED
  → DIRECT_AUTHORITY, extract, select, REVIEW_REQUIRED
```

`action.actor` and `lifecycle.authority` therefore allow exactly `DIRECT_AUTHORITY` or `collect_exact`; `action.input_invariants` allows `DIRECT_AUTHORITY`, `extract`, `select`, `collect_exact`.

- [ ] **Step 1: Write frozen-boundary and identity tests**

Add tests that assert the M5 tree itself is frozen, not only downstream v1:

```python
FROZEN_TREES = {
    "skills/joewrks-product-definition/downstream": "b63568d8c4632b14bc806e7bff1908e94dea9669",
    "skills/joewrks-product-definition/downstream_v2": "33fb2653531fa85dcc8fd8c94cbbb7cc5c41d41e",
    "evals/semantic-review-v0.4.3": "a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43",
}
```

Use the same `git rev-parse HEAD:<path>` plus clean-worktree checks already used by `tests/test_downstream_v2_frozen_boundaries.py`.

Also assert every 2.1 identity above differs from its 2.0 predecessor where a predecessor exists.

- [ ] **Step 2: Run the new test and verify RED**

Run:

```text
python -m unittest tests.test_downstream_v21_frozen_boundaries tests.test_downstream_v21_derivation -v
```

Expected: FAIL because `downstream_v21` and profile 2.0 do not exist.

- [ ] **Step 3: Create identity/profile loader and exact profile fixture**

`responsibility.py` must reject any JSON profile not exactly equal to the expected projection of the frozen v1 profile plus the changes listed above. Do not accept extra fields or caller overrides.

The loader must use canonical JSON SHA-256 for the profile digest.

- [ ] **Step 4: Add RED tests for `collect_exact`**

Cover at least:

```python
def test_collect_exact_actor_two_sources_returns_lexically_aligned_exact_values(): ...
def test_single_actor_remains_direct_authority(): ...
def test_collect_exact_rejects_duplicate_refs(): ...
def test_collect_exact_rejects_unknown_or_stale_source(): ...
def test_collect_exact_rejects_selector_mismatch(): ...
def test_collect_exact_rejects_field_with_collection_semantics_none(): ...
def test_collect_exact_does_not_deduplicate_equal_values_from_distinct_refs(): ...
def test_collect_exact_adds_no_labels_or_caller_literals(): ...
```

The exact collect spec is:

```python
{
    "kind": "MACHINE_DERIVED",
    "operator": "collect_exact",
    "source_seed_refs": ["SEED-...", "SEED-..."],
}
```

`source_seed_refs` are normalized lexically; output values are deep exact copies aligned one-to-one to that normalized list.

- [ ] **Step 5: Implement DIRECT/extract/select/collect_exact/REVIEW behavior**

Port the frozen M5 direct/extract/select semantics without changing their meaning. Add only the field-gated `collect_exact` branch.

Unknown operators, malformed specs, malformed pointers, duplicate refs, profile drift and selector violations remain deterministic `ValueError`/`INVALID_*` failures; they are not semantic or expressiveness gaps.

An explicit handoff `UNRESOLVED` spec raises `SemanticAuthorityGap` and carries its exact gap metadata.

- [ ] **Step 6: Add the narrow expressiveness classifier**

Create an internal helper:

```python
def classify_exact_collection_request(
    *,
    field_policy: dict[str, object],
    eligible_seed_refs: list[str],
    requested_collection_semantics: str,
) -> None:
    """Return normally when representable; raise ContractExpressivenessGap only for a proven eligible exact-set request that the declared contract vocabulary cannot materialize."""
```

Rules:

- all seed eligibility is checked before this helper is called;
- `requested_collection_semantics` must be `MEMBERSHIP_SET` or `CONJUNCTIVE_SET` and must equal the field's declared non-`NONE` collection semantics;
- if the declared policy permits `collect_exact`, return normally;
- if the field declares the exact set relation but the allowed derivation vocabulary lacks a lossless collection operator, raise `ContractExpressivenessGap`;
- a field with `collection_semantics = NONE` is not automatically an expressiveness gap; a `collect_exact` attempt there remains invalid because no approved set semantics exists in the profile.

This gives the taxonomy a fail-safe production path without letting callers label arbitrary invalid input as expressiveness debt.

- [ ] **Step 7: Run Task-1 tests**

Run:

```text
python -m unittest tests.test_downstream_v21_frozen_boundaries tests.test_downstream_v21_derivation -v
```

Expected: PASS.

- [ ] **Step 8: Commit Task 1**

```text
git add skills/joewrks-product-definition/downstream_v21 tests/downstream_v21_support.py tests/test_downstream_v21_frozen_boundaries.py tests/test_downstream_v21_derivation.py
git commit -m "feat: add downstream 2.1 exact derivation core"
```

---

### Task 2: Implement action-conformance/2.1, verification basis, and correct gap routing

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v21/gaps.py`
- Create: `skills/joewrks-product-definition/downstream_v21/contracts.py`
- Create: `skills/joewrks-product-definition/downstream_v21/compiler.py`
- Create: `skills/joewrks-product-definition/downstream_v21/schemas/handoff-definition-v21.schema.json`
- Create: `skills/joewrks-product-definition/downstream_v21/schemas/action-contract-v21.schema.json`
- Create: `skills/joewrks-product-definition/references/downstream-v2.1-contract.md`
- Create: `tests/test_downstream_v21_compiler.py`
- Create: `tests/test_downstream_v21_gap_routing.py`

**Interfaces:**

```python
COMPILER_ID = "joewrks-product-definition/downstream-v2.1"
COMPILER_VERSION = "core-semantic-closure-v2-m5.1"


def semantic_contract_projection_v21(contract: dict[str, object]) -> dict[str, object]: ...
def semantic_contract_hash_v21(contract: dict[str, object]) -> str: ...
def artifact_hash_v21(contract: dict[str, object]) -> str: ...
def validate_action_contract_v21(contract: object) -> list[dict[str, str]]: ...

def compile_handoff_definition_v21(
    state: dict[str, object],
    definition: dict[str, object],
) -> dict[str, object]: ...
```

Compilation result union:

```python
# success
{
    "status": "AUTHORITY_READY_MACHINE_VERIFIED" | "AUTHORITY_READY_REVIEW_PENDING",
    "contract": {...},
    "semantic_debt": {...},
    "semantic_gaps": [],
    "expressiveness_gaps": [],
    "reentry_events": [],
}

# true product meaning gap
{
    "status": "REENTRY_REQUIRED",
    "contract": None,
    "semantic_debt": {...},
    "semantic_gaps": [...],
    "expressiveness_gaps": [],
    "reentry_events": [...],
}

# contract limitation only
{
    "status": "CONTRACT_EVOLUTION_REQUIRED",
    "contract": None,
    "semantic_debt": {...},
    "semantic_gaps": [],
    "expressiveness_gaps": [...],
    "reentry_events": [],
}
```

If semantic and expressiveness gaps coexist, `REENTRY_REQUIRED` wins and both inventories are reported; only semantic gaps produce re-entry events.

#### Exact 2.1 action inventory

`fields` contains exactly these semantic fields:

```text
actor
authentication
relationship_predicate
object_binding
concurrency
preconditions
allowed_current_states
forbidden_states
input_invariants
command
expected_domain_mutation
forbidden_mutations
version_result
history_result
business_side_effects
delivery_effects
idempotency
rejection
recovery
visible_success
visible_error
superseded_rules
trace
```

`default_result`, `result_expectations`, and `test_obligations` are forbidden in action-conformance/2.1 semantic `fields`.

Every action also contains exactly:

```python
"verification_basis": {
    "outcome_basis_seed_refs": [...],
    "acceptance_basis_seed_refs": [...],
}
```

The same `verification_basis` section is present in handoff-definition/2.1 actions so the caller selects exact seed refs but cannot insert values.

Both ref arrays are nonempty, sorted, unique and source-seed-only.

Allowed outcome-basis selectors are exact:

```text
CORE:happy_path
CORE:alternative_path
CORE:error
CORE:recovery
CORE:acceptance
UX_ACTION:success
UX_ACTION:failure
UX_STATE:success
UX_STATE:error
```

Allowed acceptance-basis selector is exact:

```text
CORE:acceptance
```

A basis ref must match the action's `authority_scope_refs`; UX action basis must also match its exact `ux_action_locator`.

All basis refs count as consumed semantic authority and therefore remain in `source_seed_inventory` and `consumed_seed_inventory_digest` even when no ordinary semantic field references them.

- [ ] **Step 1: Write RED schema/contract tests**

Tests must prove:

```python
def test_v21_contract_rejects_2_0_identity(): ...
def test_v20_validator_rejects_v21_contract(): ...
def test_v21_action_inventory_excludes_runtime_only_fields(): ...
def test_v21_action_requires_verification_basis(): ...
def test_verification_basis_rejects_empty_unsorted_duplicate_or_wrong_selector_refs(): ...
def test_verification_basis_refs_remain_consumed_even_when_no_field_uses_them(): ...
def test_semantic_hash_changes_when_verification_basis_changes(): ...
```

- [ ] **Step 2: Run RED tests**

```text
python -m unittest tests.test_downstream_v21_compiler tests.test_downstream_v21_gap_routing -v
```

Expected: FAIL because compiler/contracts do not exist.

- [ ] **Step 3: Implement handoff-definition/2.1 validation**

High-level handoff shape remains:

```python
{
    "definition_schema_version": "joewrks.handoff-definition/2.1",
    "product_slug": "...",
    "actions": [...],
    "lifecycles": [...],
}
```

Each action requires:

```text
action_id
authority_scope_refs
ux_action_locator
fields
verification_basis
```

Field-spec union supports DIRECT, extract, select, collect_exact, REVIEW_REQUIRED and UNRESOLVED only. Do not add arbitrary value-bearing deterministic specs.

- [ ] **Step 4: Implement `verification_basis` validation and consumption**

Reuse the frozen M5 exact positive seed inventory via read-only imports. Never accept caller-supplied pointers or values.

Implement a helper:

```python
def validate_verification_basis(
    basis: object,
    *,
    context: dict[str, object],
    seeds: dict[str, dict[str, object]],
    profile: dict[str, object],
) -> dict[str, list[str]]: ...
```

It returns normalized sorted refs only after exact selector/scope checks.

- [ ] **Step 5: Implement typed gap routing**

`gaps.py` must provide separate record builders:

```python
def semantic_gap_record(...)->dict[str, object]: ...
def expressiveness_gap_record(...)->dict[str, object]: ...
```

Semantic gap code is exactly `SEMANTIC_AUTHORITY_GAP`.
Expressiveness gap code is exactly `CONTRACT_EXPRESSIVENESS_GAP`.

Only semantic records may be passed to frozen `downstream_v2.reentry.build_reentry_events()`; expressiveness records never produce Product Definition re-entry events or canonical unknown proposals.

Malformed specs and `INVALID_*` conditions are exceptions/fail-closed errors, not gap records.

- [ ] **Step 6: Implement compiler and 2.1 contract hashing/validation**

The semantic contract keeps the M5 source-authority provenance, exact scope commitments, consumed-only seed inventory, action/lifecycle semantic fields, semantic debt and semantic assurance.

Add `verification_basis` to action semantic identity.

Continue excluding only observation-only `source_authority.snapshot_state_sha256` from semantic hash; include it in artifact hash.

Production contract requires `semantic_debt.authority_gap_count == 0` and contains no gap inventories.

- [ ] **Step 7: Add gap-taxonomy regressions**

At minimum:

```python
def test_explicit_unresolved_product_meaning_returns_reentry_required_and_affected_only_event(): ...
def test_expressiveness_gap_returns_contract_evolution_required_without_reentry_event(): ...
def test_invalid_unknown_operator_fails_closed_not_expressiveness_gap(): ...
def test_disallowed_collect_on_none_field_is_invalid_not_expressiveness_gap(): ...
def test_mixed_semantic_and_expressiveness_gaps_reports_both_and_reentry_wins(): ...
```

The expressiveness unit uses the Task-1 internal classifier with a controlled field-policy fixture where exact set semantics is declared but no lossless collection derivation is available. Do not mutate the frozen profile JSON to manufacture this test.

- [ ] **Step 8: Run Task-2 tests**

```text
python -m unittest tests.test_downstream_v21_derivation tests.test_downstream_v21_compiler tests.test_downstream_v21_gap_routing -v
```

Expected: PASS.

- [ ] **Step 9: Commit Task 2**

```text
git add skills/joewrks-product-definition/downstream_v21 skills/joewrks-product-definition/references/downstream-v2.1-contract.md tests/test_downstream_v21_compiler.py tests/test_downstream_v21_gap_routing.py
git commit -m "feat: add action conformance 2.1 compiler"
```

---

### Task 3: Add semantic-review/2.1 without changing assurance meaning

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v21/semantic_review/__init__.py`
- Create: `skills/joewrks-product-definition/downstream_v21/semantic_review/package.py`
- Create: `skills/joewrks-product-definition/downstream_v21/semantic_review/output.py`
- Create: `skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-input-v21.schema.json`
- Create: `skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-output-v21.schema.json`
- Create: `skills/joewrks-product-definition/references/semantic-review-v2.1-contract.md`
- Create: `tests/test_downstream_v21_semantic_review.py`

**Interfaces:**

```python
RELIABILITY_STATUS = "NOT_MEASURED"


def build_semantic_review_package_v21(
    contract: dict[str, object],
) -> dict[str, object] | None: ...

def validate_semantic_review_package_v21(package: object) -> list[dict[str, str]]: ...

def validate_semantic_review_output_v21(
    package: dict[str, object],
    output: object,
) -> list[dict[str, str]]: ...

def semantic_review_completion_v21(
    package: dict[str, object] | None,
    output: dict[str, object] | None,
) -> str: ...
```

Completion enum:

```text
NOT_REQUIRED
PENDING
REVIEW_OUTPUT_RECORDED
REENTRY_REQUIRED
```

Reliability is separately always `NOT_MEASURED`.

- [ ] **Step 1: Write RED review-identity tests**

Cover:

```python
def test_review_21_accepts_only_action_contract_21(): ...
def test_review_20_package_does_not_validate_as_21(): ...
def test_review_21_packages_only_review_required_fields(): ...
def test_review_21_keeps_exact_seed_provenance_and_value_hash(): ...
def test_review_21_output_cannot_change_proposed_value(): ...
def test_review_21_reliability_is_always_not_measured(): ...
```

- [ ] **Step 2: Run RED**

```text
python -m unittest tests.test_downstream_v21_semantic_review -v
```

Expected: FAIL.

- [ ] **Step 3: Port the frozen 2.0 review boundary under new identities**

Keep the conservative behavior:

- only REVIEW_REQUIRED semantic fields produce obligations;
- package binds source semantic contract hash, source definition digest, profile identity, exact source seeds and proposed-value hash;
- review output may confirm/reject interpretation but never mutate contract/state;
- rejected interpretation is `REENTRY_REQUIRED` through semantic conflict routing;
- no calibration/reliability inheritance.

Use `joewrks.semantic-review/2.1`; do not import 2.0 identity constants into 2.1 validation.

- [ ] **Step 4: Run Task-3 tests**

```text
python -m unittest tests.test_downstream_v21_semantic_review tests.test_downstream_v21_compiler -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 3**

```text
git add skills/joewrks-product-definition/downstream_v21/semantic_review skills/joewrks-product-definition/downstream_v21/schemas/semantic-review-* skills/joewrks-product-definition/references/semantic-review-v2.1-contract.md tests/test_downstream_v21_semantic_review.py
git commit -m "feat: add semantic review 2.1 boundary"
```

---

### Task 4: Implement runtime-responsibility/1.0 and runtime-conformance-plan/1.0

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v21/runtime_profile.py`
- Create: `skills/joewrks-product-definition/downstream_v21/runtime_plan.py`
- Create: `skills/joewrks-product-definition/downstream_v21/references/runtime-responsibility-v1.json`
- Create: `skills/joewrks-product-definition/downstream_v21/schemas/runtime-conformance-plan.schema.json`
- Create: `skills/joewrks-product-definition/references/runtime-conformance-plan-contract.md`
- Create: `tests/test_downstream_v21_runtime_plan.py`

**Interfaces:**

```python
RUNTIME_PROFILE_ID = "joewrks.runtime-responsibility/1.0"
RUNTIME_PLAN_VERSION = "joewrks.runtime-conformance-plan/1.0"
PLANNER_ID = "joewrks-product-definition/runtime-plan-v1"
PLANNER_VERSION = "core-semantic-closure-v2-m5.1"


def load_runtime_responsibility_profile() -> dict[str, object]: ...
def runtime_responsibility_digest() -> str: ...

def materialize_runtime_plan(
    contract: dict[str, object],
    draft: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> dict[str, object]: ...

def validate_runtime_plan(
    plan: object,
    contract: dict[str, object],
    *,
    review_package: dict[str, object] | None = None,
    review_output: dict[str, object] | None = None,
) -> list[dict[str, str]]: ...
```

#### Frozen runtime responsibility profile

Action `RUNTIME_CRITICAL` fields are exactly:

```text
actor
authentication
relationship_predicate
object_binding
concurrency
preconditions
allowed_current_states
forbidden_states
input_invariants
command
expected_domain_mutation
forbidden_mutations
version_result
history_result
business_side_effects
delivery_effects
idempotency
rejection
recovery
superseded_rules
```

`NON_RUNTIME_PRESENTATION`:

```text
visible_success
visible_error
```

`ASSURANCE_ONLY`:

```text
trace
```

All lifecycle semantic fields are `RUNTIME_CRITICAL`.

The profile JSON is exact and callers cannot override classifications.

#### Final plan shape

```python
{
    "plan_schema_version": "joewrks.runtime-conformance-plan/1.0",
    "planner": {"id": PLANNER_ID, "version": PLANNER_VERSION},
    "source_contract": {
        "contract_schema_version": "joewrks.action-conformance/2.1",
        "semantic_contract_hash": "<64hex>",
        "approved_definition_digest": "<64hex>",
        "product_slug": "...",
    },
    "runtime_profile": {"profile_id": RUNTIME_PROFILE_ID, "digest": "<64hex>"},
    "review_commitments": {
        "package_hash": "<64hex-or-null>",
        "output_hash": "<64hex-or-null>",
        "completion": "NOT_REQUIRED|PENDING|REVIEW_OUTPUT_RECORDED|REENTRY_REQUIRED",
        "reliability_status": "NOT_MEASURED",
    },
    "actions": [...],
    "lifecycles": [...],
    "coverage_summary": {
        "status": "COMPLETE|INCOMPLETE",
        "runtime_critical_field_refs": [...],
        "covered_field_refs": [...],
        "missing_field_refs": [...],
        "review_blocked_field_refs": [...],
    },
    "mapping_gaps": [...],
    "plan_hash": "<64hex>",
}
```

A draft omits all computed identities/hashes and supplies only `actions` and `lifecycles` case definitions. `materialize_runtime_plan()` fills identities, deterministic case/test IDs, coverage, mapping gaps and plan hash.

#### Action case shape

Each action case is normalized to:

```python
{
    "case_id": "CASE-<24hex>",
    "test_id": "TEST-<24hex>",
    "result_expectation": {
        "result_class": "SUCCESS|REJECTED|STALE|IDEMPOTENT_REPLAY",
        "contract_field_refs": [...],
    },
    "component_expectations": [
        {
            "component": "authoritative_state|revision|history|business_side_effects|delivery_effects",
            "expectation": "CHANGED|UNCHANGED|ANY",
            "contract_field_refs": [...],
        }
    ],
    "evidence_assertions": [...],
    "fixture_requirements": [...],
    "contract_field_refs": [...],
}
```

`contract_field_refs` is computed as the sorted exact union of refs used by concrete result/component/assertion relationships. Caller-supplied bare coverage refs are not accepted.

`case_id` and `test_id` are derived from the canonical case semantic content before those IDs are inserted. Callers do not choose test IDs.

`fixture_requirements` contain no values, only semantically inert categories:

```text
OPAQUE_ID
ATTEMPT_ID
ORDERING_TIMESTAMP
REVISION_INSTANCE
```

They cannot encode product states, durations, thresholds, permissions or policy literals.

#### Evidence assertion expected sources

Product-specific equality can use only:

```python
{
    "source": "CONTRACT_DERIVED",
    "contract_field_path": "actions/<action_id>/<field_name>",
    "pointer": "/..."
}
```

or:

```python
{
    "source": "VERIFICATION_BASIS",
    "seed_ref": "SEED-...",
    "pointer": "/..."
}
```

The `VERIFICATION_BASIS` seed ref must be committed by that same action's `verification_basis` and exist in the contract's consumed inventory.

No expected product literal appears in the plan.

- [ ] **Step 1: Write RED profile/identity tests**

Prove exact field classification and profile digest, including rejection of caller reclassification.

- [ ] **Step 2: Write RED runtime-plan coverage tests**

At minimum:

```python
def test_plan_binds_exact_semantic_contract_hash_and_profile_digest(): ...
def test_plan_rejects_product_literal_expected_value(): ...
def test_contract_derived_expected_value_must_resolve_exactly(): ...
def test_verification_basis_source_must_belong_to_same_action(): ...
def test_any_does_not_cover_runtime_critical_field(): ...
def test_bare_contract_field_ref_does_not_count_as_coverage(): ...
def test_concrete_component_or_assertion_relationship_counts_as_coverage(): ...
def test_missing_runtime_critical_field_produces_runtime_mapping_gap_and_incomplete(): ...
def test_runtime_critical_review_required_field_blocks_complete_until_confirmed(): ...
def test_review_completion_does_not_change_not_measured_reliability(): ...
def test_plan_case_and_test_ids_are_deterministic(): ...
def test_plan_mutation_changes_plan_hash_not_semantic_contract_hash(): ...
```

- [ ] **Step 3: Run RED**

```text
python -m unittest tests.test_downstream_v21_runtime_plan -v
```

Expected: FAIL.

- [ ] **Step 4: Implement runtime profile and plan materializer**

`materialize_runtime_plan()` first validates the 2.1 semantic contract. It never accepts state.json or Product Definition evidence as an argument.

The materializer validates every contract field path against the exact source contract and computes concrete coverage from result expectations, non-ANY component expectations and valid assertions only.

A plan may materialize with `coverage_summary.status = INCOMPLETE`; every missing concrete mapping appears as code `RUNTIME_MAPPING_GAP` in `mapping_gaps`. Such a plan is valid diagnostic metadata but may never support `IMPLEMENTATION_CONFORMANT`.

- [ ] **Step 5: Implement review-gated runtime coverage**

If a runtime-critical semantic field uses `REVIEW_REQUIRED`, exact semantic-review/2.1 completion for that field is required before it enters `covered_field_refs`. Pending review puts the path in `review_blocked_field_refs`. Rejected review completion produces `REENTRY_REQUIRED`, not a runtime mapping workaround.

- [ ] **Step 6: Run Task-4 tests**

```text
python -m unittest tests.test_downstream_v21_runtime_plan tests.test_downstream_v21_semantic_review -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 4**

```text
git add skills/joewrks-product-definition/downstream_v21/runtime_profile.py skills/joewrks-product-definition/downstream_v21/runtime_plan.py skills/joewrks-product-definition/downstream_v21/references/runtime-responsibility-v1.json skills/joewrks-product-definition/downstream_v21/schemas/runtime-conformance-plan.schema.json skills/joewrks-product-definition/references/runtime-conformance-plan-contract.md tests/test_downstream_v21_runtime_plan.py
git commit -m "feat: add runtime conformance plan boundary"
```

---

### Task 5: Bind frozen execution/1.0 evidence to the runtime plan without redefining transport

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v21/runtime_evidence.py`
- Create: `skills/joewrks-product-definition/downstream_v21/schemas/runtime-evidence-bundle.schema.json`
- Create: `tests/test_downstream_v21_runtime_evidence.py`
- Modify: `skills/joewrks-product-definition/downstream_v21/README.md`

**Interfaces:**

```python
RUNTIME_EVIDENCE_BUNDLE_VERSION = "joewrks.runtime-evidence-bundle/1.0"


def build_runtime_evidence_bundle(
    contract: dict[str, object],
    plan: dict[str, object],
    records: list[dict[str, object]],
) -> dict[str, object]: ...

def validate_runtime_evidence_bundle(
    bundle: object,
    contract: dict[str, object],
    plan: dict[str, object],
) -> list[dict[str, str]]: ...

def runtime_evidence_inventory(
    bundle: dict[str, object],
    plan: dict[str, object],
) -> dict[str, object]: ...
```

Exact bundle shape:

```python
{
    "bundle_schema_version": "joewrks.runtime-evidence-bundle/1.0",
    "source_semantic_contract_hash": "<64hex>",
    "source_runtime_plan_hash": "<64hex>",
    "source_approved_definition_digest": "<64hex>",
    "records": [<exact parsed joewrks.downstream.execution/1.0 records>],
    "bundle_hash": "<64hex>",
}
```

`bundle_hash` is SHA-256 of canonical bundle content excluding only `bundle_hash`.

- [ ] **Step 1: Write RED frozen-transport tests**

Prove that every record is first validated by frozen `downstream.protocol.validate_execution_record()` and that the frozen downstream tree remains byte/tree exact.

- [ ] **Step 2: Write RED binding/inventory tests**

Cover:

```python
def test_bundle_requires_execution_v1_record_before_v21_admission(): ...
def test_record_contract_hash_must_equal_semantic_contract_hash(): ...
def test_record_approved_digest_and_revision_must_match_source_authority(): ...
def test_record_product_slug_must_match_contract(): ...
def test_record_test_id_must_exist_in_runtime_plan(): ...
def test_each_planned_test_id_has_exactly_one_record(): ...
def test_missing_planned_record_is_incomplete(): ...
def test_unexpected_test_id_is_reported(): ...
def test_runtime_plan_hash_change_invalidates_old_bundle(): ...
def test_bundle_hash_is_deterministic(): ...
```

One execution record per planned `test_id` is the M5.1 bundle rule. Duplicate test IDs fail closed; do not invent duplicate-resolution policy.

- [ ] **Step 3: Run RED**

```text
python -m unittest tests.test_downstream_v21_runtime_evidence -v
```

Expected: FAIL.

- [ ] **Step 4: Implement transport-preserving bundle**

Use frozen `validate_execution_record()` as the first gate.

Then impose V2.1 admission:

```text
record.contract_hash == contract.semantic_contract_hash
record.authority.approved_digest == contract.source_authority.approved_definition_digest
record.authority.approved_revision == contract.source_authority.approved_revision
record.product_slug == contract.source_authority.product_slug
record.test_id exists exactly once in runtime plan
```

`runtime_evidence_inventory()` returns exact sorted inventories:

```python
{
    "required_test_ids": [...],
    "observed_test_ids": [...],
    "missing_test_ids": [...],
    "unexpected_test_ids": [...],
    "coverage_status": "COMPLETE|INCOMPLETE",
}
```

This helper does not decide runtime semantic PASS/FAIL; M6's runtime verifier consumes the plan + admitted bundle to do that.

- [ ] **Step 5: Run Task-5 tests**

```text
python -m unittest tests.test_downstream_v21_runtime_evidence tests.test_downstream_v21_runtime_plan -v
```

Expected: PASS.

- [ ] **Step 6: Write package boundary README and commit**

README status markers must include:

```text
ACTION_CONFORMANCE_2_1
HANDOFF_DEFINITION_2_1
RUNTIME_CONFORMANCE_PLAN_1_0
RUNTIME_EVIDENCE_BUNDLE_1_0
SEMANTIC_REVIEW_2_1_RELIABILITY_NOT_MEASURED
SEMANTIC_AUTHORITY_GAP_REENTERS_PRODUCT_DEFINITION
CONTRACT_EXPRESSIVENESS_GAP_DOES_NOT_REENTER_PRODUCT_DEFINITION
RUNTIME_MAPPING_GAP_DOES_NOT_REENTER_PRODUCT_DEFINITION
DOWNSTREAM_V2_0_FROZEN
M6_NOT_COMPLETED_BY_M5_1
```

Commit:

```text
git add skills/joewrks-product-definition/downstream_v21 tests/test_downstream_v21_runtime_evidence.py
git commit -m "feat: bind runtime evidence to semantic plan"
```

---

### Task 6: Replay the stopped M6 dogfood read-only, run regressions, and freeze M5.1 evidence

**Files:**
- Create: `tests/test_downstream_v21_dogfood_replay.py`
- Create: `skills/joewrks-product-definition/references/downstream-v2.1-contract.md` if Task 2 did not already finalize it; otherwise update only M5.1 implementation-status section.
- Create: `evals/core-semantic-closure-v2-m5-1/README.md`
- Create: `evals/core-semantic-closure-v2-m5-1/DOGFOOD_REPLAY_AUDIT.md`
- Create: `evals/core-semantic-closure-v2-m5-1/FINAL_IMPLEMENTATION_AUDIT.md`

**Interfaces / environment:**

The dogfood replay is mandatory for the strongest M5.1 success label and reads the preserved M6 worktree through:

```text
JOEWRKS_M6_PHASE_B_WORKTREE=<absolute path to preserved M6 worktree>
```

Do not silently skip the replay. If this environment variable is absent or the worktree identity does not match, stop M5.1 finalization with `M6_REPLAY_EVIDENCE_UNAVAILABLE`.

Before reading dogfood artifacts, verify all of:

```text
branch = feat/core-semantic-closure-v2-m6-integration-adoption
HEAD = d38b0ca04768888c47e658c79f41e1cec0a7a1ce
worktree clean
Product Definition revision = 1
CLOSED / APPROVED
approved_definition_digest = e33deda04bae78eab0da60ba432c47a0779bce17c4bee7d1c5695455d9d9f68c
approved_manifest_digest = 60ec9818666bab7d75bc4ee14d9ff4fcf2817d3cfcaa2e51c95318776be64705
approved_at = 2026-08-30T11:54:26Z
approved_by = user
Closure closed = true
```

Read-only source artifacts include at minimum:

```text
evals/core-semantic-closure-v2-m6/dogfood/product-definition/client-feedback-portal-dogfood-v2/state.json
evals/core-semantic-closure-v2-m6/dogfood/handoff-definition.json
evals/core-semantic-closure-v2-m6/dogfood/reentry-probe.json
evals/core-semantic-closure-v2-m6/dogfood/dogfood-summary.md
```

If the exact Phase-B file names differ, resolve them from the preserved worktree's tracked files; do not edit or rename them there.

#### Mechanical 2.0 → 2.1 replay transformation

Build the replay handoff in test memory or a temporary directory; do not write it into the preserved M6 worktree.

Rules:

1. Copy every 2.0 action/lifecycle identity and scope/locator exactly.
2. For every retained field that already compiled successfully under 2.0, preserve the same exact source refs and derivation semantics under 2.1.
3. Remove `default_result`, `result_expectations`, and `test_obligations` from semantic `fields`.
4. Build each action's `verification_basis` only from exact eligible seed refs in the approved state matching the frozen outcome/acceptance basis selectors. Do not insert values.
5. For a known multi-source `actor` or `input_invariants` mapping, use `collect_exact` only when every chosen source ref is exact/current/selector-eligible and the field's frozen collection semantics permits it.
6. If the transformation needs a new product value, priority, conflict resolution, or semantic choice, stop with `TRUE_SEMANTIC_GAP_FOUND`; do not stretch 2.1.
7. Record the old 2.0 `REENTRY_REQUIRED` result as historical evidence and the new 2.1 compile result separately.

The replay test must assert the source M6 worktree remains byte-for-byte clean after the read.

- [ ] **Step 1: Write the replay test harness**

Test must verify exact Phase-B identity before attempting translation and must fail, not skip, when the required worktree is unavailable during the final M5.1 gate.

For ordinary developer unit runs, expose the lower-level translation helper tests separately using synthetic fixtures in `tests/downstream_v21_support.py`; only the final replay test depends on the external preserved worktree.

- [ ] **Step 2: Run focused M5.1 tests without dogfood replay**

```text
python -m unittest \
  tests.test_downstream_v21_frozen_boundaries \
  tests.test_downstream_v21_derivation \
  tests.test_downstream_v21_compiler \
  tests.test_downstream_v21_gap_routing \
  tests.test_downstream_v21_semantic_review \
  tests.test_downstream_v21_runtime_plan \
  tests.test_downstream_v21_runtime_evidence -v
```

Expected: PASS.

- [ ] **Step 3: Run mandatory dogfood replay with preserved M6 worktree**

```text
python -m unittest tests.test_downstream_v21_dogfood_replay -v
```

Expected architectural outcome:

```text
approved Product Definition definition digest unchanged
approved Manifest digest unchanged
closure = true
2.0 historical result remains REENTRY_REQUIRED with 25 reported gaps
2.1 reply_thread.actor uses lossless exact multi-authority representation
2.1 input_invariants remains exact semantic authority
2.1 semantic contract no longer contains default_result/result_expectations/test_obligations
2.1 verification_basis preserves their exact approved outcome/acceptance provenance
authority_gap_count = 0
known-slice CONTRACT_EXPRESSIVENESS_GAP count = 0
materialized action-conformance/2.1 exists
runtime-conformance-plan/1.0 validates
runtime plan can reach coverage COMPLETE using deterministic mapping definitions without product literals
```

If the actual approved state exposes a genuine unresolved product choice, STOP and report `TRUE_SEMANTIC_GAP_FOUND`; M5.1 is not allowed to fabricate the missing meaning.

- [ ] **Step 4: Run complete M5 regression**

```text
python -m unittest \
  tests.test_downstream_v2_authority \
  tests.test_downstream_v2_seeds \
  tests.test_downstream_v2_derivation \
  tests.test_downstream_v2_compiler \
  tests.test_downstream_v2_semantic_debt \
  tests.test_downstream_v2_reentry \
  tests.test_downstream_v2_semantic_review \
  tests.test_downstream_v2_cli \
  tests.test_downstream_v2_frozen_boundaries -v
```

Expected: PASS with only the pre-existing environment-dependent frozen runtime skip if that suite reaches it.

- [ ] **Step 5: Run Core V2 regression**

```text
python -m unittest \
  tests.test_semantic_closure_v020 \
  tests.test_approval_manifest_v020 \
  tests.test_authority_binding_v020 \
  tests.test_authority_consumption_v020 \
  tests.test_core_coverage_binding_v020 \
  tests.test_grill_binding_v020 \
  tests.test_ux_binding_v020 \
  tests.test_unknown_resolution_v020 \
  tests.test_question_policy_v020 \
  tests.test_grill_packs_v020 \
  tests.test_grill_baseline_v020 \
  tests.test_discovery_baseline_v020 \
  tests.test_evidence_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_reverse_bootstrap_v020 \
  tests.test_contradictions_v020 \
  tests.test_materiality_v020 \
  tests.test_autonomy_policy_v020 \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation -v
```

Expected: PASS.

- [ ] **Step 6: Run legacy/downstream-v1/semantic-review-v1 regressions**

```text
python -m unittest \
  tests.test_validators \
  tests.test_semantic_v012 \
  tests.test_legacy_v0121_frozen \
  tests.test_downstream_contracts \
  tests.test_downstream_protocol \
  tests.test_downstream_schema_validation \
  tests.test_downstream_verifier \
  tests.test_downstream_authority \
  tests.test_downstream_handoff \
  tests.test_downstream_product_bundles \
  tests.test_downstream_adapters \
  tests.test_semantic_review_gate \
  tests.test_semantic_review_goldens \
  tests.test_semantic_review_hashing \
  tests.test_semantic_review_human_packet \
  tests.test_semantic_review_negative_regressions \
  tests.test_semantic_review_output \
  tests.test_semantic_review_package \
  tests.test_semantic_review_responsibility \
  tests.test_semantic_review_statistics \
  tests.test_official_calibration_controller \
  tests.test_semantic_review_calibration_control_plane \
  tests.test_semantic_review_calibration_corpus -v
```

Expected: PASS, preserving the historical v0.4.3 calibration disposition.

- [ ] **Step 7: Run full repository and diff check**

```text
python -m unittest discover -s tests -v
git diff --check
```

Expected: full suite PASS except only already-documented environment-dependent skip(s); `git diff --check` PASS.

- [ ] **Step 8: Perform final read-only source review**

Verify:

```text
Critical = 0
Important = 0
Minor = 0
```

Review explicitly checks:

- all frozen trees/blobs exact;
- no change under `downstream_v2/`;
- no state 0.2.0/M4 approval/binding modification;
- 2.0/2.1 cross-version rejection;
- `collect_exact` field allowlist exact;
- no literal-bearing generic construction operator;
- verification-basis consumption exact;
- semantic vs expressiveness vs runtime-mapping routing exact;
- runtime plan reads only semantic contract/review output, never Product Definition state;
- runtime-critical coverage is concrete and `ANY` does not count;
- product-specific expected values are contract/basis-derived only;
- runtime evidence bundle validates frozen execution/1.0 first and binds both semantic contract and runtime plan hashes;
- semantic-review/2.1 reliability remains NOT_MEASURED;
- preserved M6 worktree still clean and its approved Product Definition digests unchanged;
- no M6 Task 6, main merge, PR, or deployment occurred.

- [ ] **Step 9: Write final M5.1 audit evidence**

`DOGFOOD_REPLAY_AUDIT.md` records both the old 2.0 stopped result and the new 2.1 result without rewriting the historical failure.

`FINAL_IMPLEMENTATION_AUDIT.md` records exact implementation HEAD/tree, changed-file manifest, test commands/results, frozen identities, profile/contract digests and the M6 resumption decision.

Do not copy host-specific absolute worktree paths into committed evidence; record only the verified branch/commit identities.

- [ ] **Step 10: Commit final evidence**

```text
git add evals/core-semantic-closure-v2-m5-1 tests/test_downstream_v21_dogfood_replay.py skills/joewrks-product-definition/references/downstream-v2.1-contract.md
git commit -m "test: verify downstream 2.1 executability remediation"
```

- [ ] **Step 11: Push only after every gate passes**

Push only the M5.1 implementation branch. Do not push/modify the preserved M6 branch and do not touch main.

Strongest allowed report:

```text
CORE_SEMANTIC_CLOSURE_V2_M5_1_IMPLEMENTED
— DOWNSTREAM_EXECUTABILITY_REMEDIATED / M6_RESUME_READY / NOT_INTEGRATED
```

Report:

- branch;
- planning/base SHA;
- final HEAD/parent/tree/remote SHA;
- changed-file count/list;
- per-task commits;
- action-conformance/2.1 identity;
- handoff-definition/2.1 identity;
- downstream-responsibility/2.0 ID/digest;
- runtime-conformance-plan/1.0 identity;
- runtime-responsibility/1.0 ID/digest;
- runtime-evidence-bundle/1.0 identity;
- semantic-review/2.1 identity and `NOT_MEASURED` confirmation;
- collect_exact exact allowlist and dogfood multi-actor probe;
- semantic/expressiveness/runtime-mapping gap routing probes;
- verification-basis consumed-seed probe;
- runtime-plan no-product-literal and coverage probes;
- execution/1.0 transport preservation probe;
- dogfood definition/manifest digest equality and Closure result;
- old 2.0 stopped result preserved;
- new 2.1 dogfood compiler authority-gap / expressiveness-gap counts;
- runtime-plan COMPLETE feasibility result;
- all focused/regression/full-suite results and skips/reasons;
- `git diff --check`;
- exact frozen tree/blob verification;
- preserved M6 Phase-B worktree unchanged;
- local/remote main SHA;
- confirmation M6 Task 6 NOT STARTED and no PR/merge.

Then STOP. M6 integration/resumption requires a separate continuation after independent M5.1 source verification.
