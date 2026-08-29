# Core Semantic Closure V2 — M5 Downstream V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a parallel Downstream V2 authority package that consumes an M4-closed Product Definition, reuses M4 exact bindings as source seeds, classifies downstream semantic debt as `DIRECT_AUTHORITY / MACHINE_DERIVED / REVIEW_REQUIRED`, blocks `SEMANTIC_AUTHORITY_GAP`, emits deterministic Product Definition re-entry events, and provides a new `joewrks.semantic-review/2.0` structural package whose reliability truth begins at `NOT_MEASURED`.

**Architecture:** Add a new sibling package at `skills/joewrks-product-definition/downstream_v2/`; do not modify the frozen v1 `downstream/` tree. M5 reads the canonical state 0.2.0 and the M4 public evaluator/binding APIs, but never writes Product Definition state. M4 exact Core/Grill/UX bindings are compiled into a deterministic source-seed inventory; downstream definitions reference seed keys rather than inventing new object pointers. Semantic authority gaps do not become review obligations: they emit dependency-scoped re-entry artifacts. `REVIEW_REQUIRED` is permitted only by a versioned responsibility profile and remains assurance work, not an authority-creation mechanism.

**Tech Stack:** Python 3 standard library, JSON, Draft 2020-12 JSON Schema documents, RFC 6901 JSON Pointer, canonical UTF-8 JSON SHA-256, `unittest`.

**Spec:**
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md` — especially principles 3.6–3.7 and sections 28, 34–36
- `docs/superpowers/audits/2026-08-29-core-semantic-closure-v2-m4-source-audit.md`

## Global Constraints

- Implement from an isolated branch/worktree based on the exact final M5 planning HEAD. The planning branch descends from M4 HEAD `82502688a16d53d5527f5e27171c5764d0039101`.
- M5 is **parallel**, not an in-place rewrite of downstream v1.
- The entire existing `skills/joewrks-product-definition/downstream/` tree must remain byte-identical with Git tree `b63568d8c4632b14bc806e7bff1908e94dea9669`.
- The entire existing `evals/semantic-review-v0.4.3/` tree must remain byte-identical with Git tree `a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43`.
- Preserve the frozen legacy 0.1.2.1 blobs exactly.
- Preserve the M4 core implementation files unchanged during M5, including at minimum:
  - `scripts/authority_binding_v2.py` blob `03704ea991aa72d20c2dd8c251ea22cbda8640ce`
  - `scripts/approval_v2.py` blob `41a70074d483b4e10a5954d1828a8de316919abe`
  - `scripts/state_validation_v2.py` blob `7acf26af546d299879dff29d30ca98a5753025a2`
  - `schemas/state-v0.2.0.schema.json` blob `2cea7b11800728be2cc705f43daab5cf11f7d923`
  - `references/semantic-freeze-contract-v0.2.0.md` blob `d4abccaa93377bce8f5eb6181fb80186eff14550`
- Do not redefine or modify `joewrks.action-conformance/1.0`, `joewrks.semantic-review/1.0`, or `joewrks.downstream.execution/1.0`.
- New action contract identity is exactly `joewrks.action-conformance/2.0`.
- New semantic-review identity is exactly `joewrks.semantic-review/2.0`.
- New re-entry artifact identity is exactly `joewrks.product-definition-reentry/1.0`.
- M5 never mutates `state.json`, never allocates canonical `UNK-*` IDs, never increments `definition_revision`, and never auto-invalidates/repairs approval. It only reports when Product Definition re-entry is required.
- M5 accepts a source Product Definition for authority compilation only when M4 `evaluate_closure_v2(state)` returns `closed = true`, zero errors, and a non-null definition digest matching the recorded approval.
- M5 distinguishes semantic authority identity from raw state snapshot identity. A full-state hash may change because of unconsumed evidence; that must not by itself stale the semantic downstream contract.
- M4 positive bindings are source seeds. A downstream definition references seed keys; it does not handwrite arbitrary `record_id + pointer` sources.
- `DIRECT_AUTHORITY` means the downstream value is the exact source-seed value. No interpretation and no deterministic transform occurs.
- M5 `MACHINE_DERIVED` operators are a closed set: `extract` and `select` only. There is no arbitrary Python/JavaScript expression, template language, callback, or natural-language parser.
- `REVIEW_REQUIRED` is accepted only for responsibility fields explicitly marked `REVIEW_PERMITTED`. A deterministic-required field cannot be converted to review merely because interpretation is difficult.
- Any missing stronger authority where the responsibility profile requires direct/deterministic semantics produces `SEMANTIC_AUTHORITY_GAP` and Product Definition re-entry.
- A valid authority handoff requires `authority_gap_count == 0`.
- `review_required_count` may be greater than zero, but then semantic assurance remains separate from authority readiness.
- `joewrks.semantic-review/2.0` reliability begins and remains `NOT_MEASURED` throughout M5. No v1/v0.4.3 reliability result is inherited.
- M5 does not create or modify calibration corpora, calibration outputs, human-adjudication evidence, v0.4.4 work, runtime product adapters, production deployment wiring, or migration/adoption dogfood. Those remain outside M5; M6 owns integration/adoption.
- Every behavior-changing code task follows RED → GREEN → refactor.
- Strongest successful milestone label is `IMPLEMENTED_M5 / DOWNSTREAM_V2_AUTHORITY / REENTRY_PROTOCOL / NOT_INTEGRATED`.

---

# File Map

## New parallel package

Create under `skills/joewrks-product-definition/downstream_v2/`:

- `__init__.py` — public contract identities and supported API exports.
- `authority.py` — M4 closed-authority envelope and semantic-vs-snapshot identity.
- `seeds.py` — deterministic M4 Core/Grill/UX positive-binding source-seed inventory.
- `derivation.py` — responsibility-profile loading, seed-selector enforcement, `DIRECT_AUTHORITY` and closed machine derivations.
- `semantic_debt.py` — field-level debt inventory and aggregate counts.
- `contracts.py` — action-conformance/2.0 contract materialization, semantic/artifact hashing, contract verification.
- `compiler.py` — handoff-definition compilation orchestration.
- `reentry.py` — deterministic re-entry artifacts and downstream contract drift audit.
- `compile.py` — `python -m downstream_v2.compile STATE_JSON HANDOFF_DEFINITION_JSON` CLI.
- `audit.py` — `python -m downstream_v2.audit CONTRACT_JSON STATE_JSON` CLI.
- `README.md` — M5 package boundary and invocation.

Create under `skills/joewrks-product-definition/downstream_v2/semantic_review/`:

- `__init__.py`
- `package.py` — `joewrks.semantic-review/2.0` input package builder.
- `output.py` — structural output validation and result classification.
- `build_package.py` — read-only CLI for review-package construction.

## New schemas

Create under `skills/joewrks-product-definition/downstream_v2/schemas/`:

- `handoff-definition.schema.json`
- `action-contract-v2.schema.json`
- `reentry-event.schema.json`
- `semantic-review-input-v2.schema.json`
- `semantic-review-output-v2.schema.json`

## New declarative responsibility authority

Create:

- `skills/joewrks-product-definition/downstream_v2/references/field-responsibility-v1.json`

## New normative references outside the frozen v1 tree

Create:

- `skills/joewrks-product-definition/references/downstream-v2-contract.md`
- `skills/joewrks-product-definition/references/implementation-reentry-contract.md`

## New tests

Create:

- `tests/downstream_v2_support.py`
- `tests/test_downstream_v2_frozen_boundaries.py`
- `tests/test_downstream_v2_authority.py`
- `tests/test_downstream_v2_seeds.py`
- `tests/test_downstream_v2_derivation.py`
- `tests/test_downstream_v2_compiler.py`
- `tests/test_downstream_v2_semantic_debt.py`
- `tests/test_downstream_v2_reentry.py`
- `tests/test_downstream_v2_semantic_review.py`
- `tests/test_downstream_v2_cli.py`

M5 should not require modification of pre-M5 production files. If an implementation step appears to require changing M4 core or frozen v1, stop and report the conflict instead of broadening scope.

---

# Task 1 — Freeze historical downstream and build the M4 authority/source-seed bridge

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v2/__init__.py`
- Create: `skills/joewrks-product-definition/downstream_v2/authority.py`
- Create: `skills/joewrks-product-definition/downstream_v2/seeds.py`
- Create: `tests/downstream_v2_support.py`
- Create: `tests/test_downstream_v2_frozen_boundaries.py`
- Create: `tests/test_downstream_v2_authority.py`
- Create: `tests/test_downstream_v2_seeds.py`

**Interfaces:**

`authority.py` exports:

```python
ACTION_CONTRACT_VERSION = "joewrks.action-conformance/2.0"
SEMANTIC_REVIEW_VERSION = "joewrks.semantic-review/2.0"
REENTRY_VERSION = "joewrks.product-definition-reentry/1.0"

class DownstreamV2Error(ValueError):
    code: str
    detail: object


def canonical_json(value: object) -> str: ...
def sha256_json(value: object) -> str: ...
def canonical_state_sha256(state: dict[str, object]) -> str: ...
def require_closed_authority(state: dict[str, object]) -> dict[str, object]: ...
```

`seeds.py` exports:

```python
def build_source_seed_inventory(state: dict[str, object]) -> list[dict[str, object]]: ...
def source_seed_inventory_digest(seeds: list[dict[str, object]]) -> str: ...
def source_seed_index(seeds: list[dict[str, object]]) -> dict[str, dict[str, object]]: ...
def verify_source_seed(state: dict[str, object], seed: dict[str, object]) -> dict[str, object]: ...
```

## Supported import boundary

The M5 package is deliberately not installed/integrated yet. Production modules may import the existing M4 public Python modules by name:

```python
from state_validation_v2 import evaluate_closure_v2
from authority_binding_v2 import canonical_record_index, resolve_record_pointer, sha256_json
```

M5 tests set both paths explicitly before importing `downstream_v2`:

```text
skills/joewrks-product-definition/
skills/joewrks-product-definition/scripts/
```

Do not add hidden/dynamic `__import__`, do not mutate M4 import structure, and do not rewrite v1 package imports. M6 may normalize installed-package routing later.

## M4 authority envelope

`require_closed_authority(state)` requires:

```text
schema_version = 0.2.0
evaluate_closure_v2(state).closed = true
errors = []
definition_digest != null
project.definition_status = CLOSED
approval.status = APPROVED
approval.approved_revision = project.definition_revision
approval.approved_definition_digest = evaluator definition_digest
```

It returns exactly:

```python
{
    "state_schema_version": "0.2.0",
    "product_slug": state["project"]["slug"],
    "approved_revision": state["approval"]["approved_revision"],
    "approved_definition_digest": state["approval"]["approved_definition_digest"],
    "approved_manifest_digest": state["approval"]["approved_manifest_digest"],
    "product_binding_contract": state["project"]["closure_contract"]["product_binding_contract"],
    "ux_binding_contract": state["project"]["closure_contract"]["ux_binding_contract"],
    "snapshot_state_sha256": canonical_state_sha256(state),
}
```

`snapshot_state_sha256` is observational artifact metadata. It is **not** the semantic Product Definition identity; `approved_definition_digest` is.

## Source-seed locations

Only positive M4 bindings become downstream semantic source seeds:

```text
Core coverage cell status COVERED     → authority_bindings
Specialist Grill axis status ADDRESSED → authority_bindings
UX screen-state cell status COVERED   → authority_bindings
UX action-axis cell status COVERED    → authority_bindings
```

N/A basis bindings and OPEN unknown refs are not positive downstream source seeds.

Each seed is exactly:

```python
{
    "seed_key": "SEED-<24 lowercase hex>",
    "location": {
        "scope": "CORE | GRILL | UX_STATE | UX_ACTION",
        "owner_ref": "REQ-* | SURF-* | SCR-*",
        "axis": "<axis id>",
        "pack_id": "GRILL-* | null",
        "action_key": "<major action key> | null",
    },
    "record_id": "<canonical authority ID>",
    "record_type": "GOAL | USR | REQ | DEC | RULE | FLOW | SCR | STATE | DATA | INT | AC",
    "pointer": "<record-relative RFC 6901 pointer>",
    "value_sha256": "<64 lowercase hex>",
    "source_status": "CURRENT",
    "value": "<resolved JSON value>"
}
```

Create the seed key from SHA-256 of canonical JSON containing only `location + record_id + pointer + value_sha256`, then use the first 24 lowercase hexadecimal characters. The same semantic binding at a different Coverage/UX location is a different seed because its semantic obligation context differs.

Inventory order is ascending by `seed_key`. Duplicate seed keys are fatal.

`verify_source_seed` checks all of:

- record still exists exactly once;
- record status is `CURRENT`;
- record-relative pointer resolves;
- value hash matches;
- the exact binding still exists at the declared Core/Grill/UX location;
- the declared location status is still positive (`COVERED` or `ADDRESSED`).

## Task 1 tests

- [ ] **Step 1: Add the frozen-boundary test first**

`tests/test_downstream_v2_frozen_boundaries.py` must verify through Git that the checked-out tree contains exactly:

```text
HEAD:skills/joewrks-product-definition/downstream
= b63568d8c4632b14bc806e7bff1908e94dea9669

HEAD:evals/semantic-review-v0.4.3
= a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43
```

It must also verify the five M4 core blob SHAs frozen in Global Constraints. This test runs after every M5 task.

- [ ] **Step 2: Add a reusable literal M4 CLOSED fixture**

`tests/downstream_v2_support.py` builds a deterministic state 0.2.0 that passes the actual M4 evaluator with `closed = true`. Reuse M4 public helpers/constants where possible; do not bypass the M4 evaluator and do not hardcode `closed = true` as fixture truth.

Also provide:

```python
def closed_v2_state() -> dict[str, object]: ...
def source_seed_by_location(seeds, *, scope, owner_ref, axis, pack_id=None, action_key=None): ...
```

- [ ] **Step 3: Add RED authority tests**

Required cases in `tests/test_downstream_v2_authority.py`:

1. valid M4 CLOSED+APPROVED state returns the exact authority envelope;
2. OPEN, READY_FOR_REVIEW, stale-approval, semantically mutated, and structurally invalid states fail `PRODUCT_DEFINITION_NOT_CLOSED`;
3. `snapshot_state_sha256` changes when unconsumed evidence changes and the discovery baseline is rebuilt;
4. `approved_definition_digest` remains unchanged for that unconsumed-evidence-only change;
5. `require_closed_authority` never repairs/rewrites state.

- [ ] **Step 4: Add RED source-seed inventory tests**

Required cases in `tests/test_downstream_v2_seeds.py`:

1. all positive Core/Grill/UX bindings are inventoried;
2. OPEN and N/A cells contribute no positive seed;
3. seed keys and inventory bytes are deterministic under repeated compilation;
4. seed order is independent of input dictionary ordering;
5. each seed resolves to its exact M4 value/hash;
6. a changed bound value, stale authority, removed binding, location-status change, wrong owner, wrong action key, or wrong pack identity makes `verify_source_seed` fail closed;
7. two semantic locations pointing to the same underlying binding remain distinct seed keys;
8. unconsumed EVD changes do not alter source-seed inventory digest when M4 semantic bindings are unchanged.

- [ ] **Step 5: Run Task 1 RED**

```bash
python -m unittest \
  tests.test_downstream_v2_frozen_boundaries \
  tests.test_downstream_v2_authority \
  tests.test_downstream_v2_seeds -v
```

Expected: authority/seed tests fail because the V2 package does not yet exist; frozen-boundary test passes.

- [ ] **Step 6: Implement authority and seed modules minimally**

Use `allow_nan=False`, sorted compact JSON and UTF-8 SHA-256. No timestamps, random UUIDs, wall-clock fields, network access, or filesystem mutation.

- [ ] **Step 7: Run Task 1 GREEN**

```bash
python -m unittest \
  tests.test_downstream_v2_frozen_boundaries \
  tests.test_downstream_v2_authority \
  tests.test_downstream_v2_seeds \
  tests.test_semantic_closure_v020 -v
```

Expected: `OK`.

- [ ] **Step 8: Commit**

```bash
git add skills/joewrks-product-definition/downstream_v2 \
  tests/downstream_v2_support.py \
  tests/test_downstream_v2_frozen_boundaries.py \
  tests/test_downstream_v2_authority.py \
  tests/test_downstream_v2_seeds.py
git commit -m "feat: bridge semantic closure into downstream v2 seeds"
```

---

# Task 2 — Freeze responsibility policy and the semantic derivation engine

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v2/derivation.py`
- Create: `skills/joewrks-product-definition/downstream_v2/references/field-responsibility-v1.json`
- Create: `skills/joewrks-product-definition/downstream_v2/schemas/handoff-definition.schema.json`
- Create: `tests/test_downstream_v2_derivation.py`

**Interfaces:**

```python
RESPONSIBILITY_PROFILE_ID = "joewrks.downstream-responsibility/1.0"

class SemanticGap(ValueError):
    code: str
    detail: object


def load_responsibility_profile() -> dict[str, object]: ...
def responsibility_profile_digest() -> str: ...
def seed_matches_selector(seed: dict[str, object], selector: dict[str, object], context: dict[str, object]) -> bool: ...
def derive_semantic_field(
    spec: dict[str, object],
    *,
    field_name: str,
    field_kind: str,
    context: dict[str, object],
    seeds: dict[str, dict[str, object]],
    profile: dict[str, object],
) -> dict[str, object]: ...
```

`field_kind` is exactly `ACTION` or `LIFECYCLE`.

## Handoff definition identity

Input definitions use:

```text
joewrks.handoff-definition/2.0
```

Top-level exact shape:

```python
{
    "definition_schema_version": "joewrks.handoff-definition/2.0",
    "product_slug": "...",
    "actions": [...],
    "lifecycles": [...],
}
```

Each action is:

```python
{
    "action_id": "...",
    "authority_scope_refs": ["REQ-*", "SURF-*", "SCR-*"],
    "ux_action_locator": {"screen_ref": "SCR-*", "action_key": "..."} | None,
    "fields": {<exact 26 action field names>},
}
```

Exact action field inventory, retained conceptually from v1:

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
default_result
result_expectations
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
test_obligations
trace
```

Each lifecycle is:

```python
{
    "lifecycle_id": "...",
    "authority_scope_refs": ["REQ-*", "SURF-*", "SCR-*"],
    "fields": {<exact 12 lifecycle field names>},
}
```

Exact lifecycle semantic field inventory:

```text
current_states
allowed_transitions
forbidden_transitions
boundary_conditions
reversibility
reversal_window
object_outcome
required_reason
required_confirmation
required_evidence
authority
history_preservation
```

Action/lifecycle IDs are downstream artifact IDs, not new canonical Product Definition IDs.

## Field-spec forms

Each field spec is exactly one of four forms.

### DIRECT

```python
{
    "kind": "DIRECT_AUTHORITY",
    "source_seed_ref": "SEED-...",
}
```

Output value equals the exact seed value. Exactly one seed is used.

### MACHINE

`extract`:

```python
{
    "kind": "MACHINE_DERIVED",
    "operator": "extract",
    "source_seed_ref": "SEED-...",
    "pointer": "/nested/path",
}
```

The pointer is relative to the seed value. Empty pointer is rejected because exact copying is `DIRECT_AUTHORITY`.

`select`:

```python
{
    "kind": "MACHINE_DERIVED",
    "operator": "select",
    "source_seed_ref": "SEED-...",
    "keys": ["field_a", "field_b"],
}
```

The seed value must be an object. Keys are non-empty, unique, lexically sorted, and every key must exist. Output is the exact sub-object containing those keys. No renaming, default insertion, calculation, templating, coercion, or natural-language parsing is allowed.

There is no `exact` machine operator in M5: exact source equality is classified more strongly as `DIRECT_AUTHORITY`.

### REVIEW

```python
{
    "kind": "REVIEW_REQUIRED",
    "source_seed_refs": ["SEED-..."],
    "proposed_value": <JSON>,
    "why_structuring_is_insufficient": "...",
    "interpretation_scope": "...",
}
```

At least one source seed is required. The responsibility profile must mark the field `REVIEW_PERMITTED`.

### UNRESOLVED

```python
{
    "kind": "UNRESOLVED",
    "gap_type": "AMBIGUITY_FOUND | CONTRACT_CONFLICT | OUT_OF_SCOPE_REQUEST",
    "description": "...",
    "required_authority_class": "FACTUAL | INTENT | CONSTRAINT | BEHAVIORAL | PREFERENCE",
    "evidence_refs": [],
}
```

`UNRESOLVED` is accepted by the handoff-definition input schema but never appears in an action-conformance/2.0 output contract. It becomes a semantic gap/re-entry event.

## Responsibility levels

Allowed expectation values:

```text
DIRECT_REQUIRED
DETERMINISTIC_REQUIRED
REVIEW_PERMITTED
```

Rules:

```text
DIRECT_REQUIRED:
  DIRECT_AUTHORITY only

DETERMINISTIC_REQUIRED:
  DIRECT_AUTHORITY or MACHINE_DERIVED

REVIEW_PERMITTED:
  DIRECT_AUTHORITY, MACHINE_DERIVED or REVIEW_REQUIRED
```

An `UNRESOLVED` spec is always a gap regardless of expectation.

## Exact action responsibility profile

Freeze these expectations and allowed seed selectors.

Selector notation below uses:

```text
CORE:<axis>
GRILL:<pack-id>:<axis>
UX_STATE:<axis>
UX_ACTION:<axis>
```

- `actor` — `DIRECT_REQUIRED` — `CORE:actor`
- `authentication` — `DETERMINISTIC_REQUIRED` — `CORE:permission`, `CORE:security`, `GRILL:GRILL-AUTH-1:login`, `GRILL:GRILL-AUTH-1:session_expiry`, `GRILL:GRILL-AUTH-1:session_renewal`
- `relationship_predicate` — `DETERMINISTIC_REQUIRED` — `CORE:permission`, `CORE:boundary`, `GRILL:GRILL-PERMISSION-1:role`, `GRILL:GRILL-PERMISSION-1:resource_ownership`
- `object_binding` — `DETERMINISTIC_REQUIRED` — `CORE:data`, `CORE:state`
- `concurrency` — `DETERMINISTIC_REQUIRED` — `CORE:alternative_path`, `CORE:error`, `CORE:recovery`, `GRILL:GRILL-ASYNC-1:idempotency`, `GRILL:GRILL-ASYNC-1:duplicate_execution`, `UX_ACTION:duplicate_concurrent_action`
- `preconditions` — `DETERMINISTIC_REQUIRED` — `CORE:precondition`, `UX_ACTION:precondition`
- `allowed_current_states` — `DETERMINISTIC_REQUIRED` — `CORE:state`
- `forbidden_states` — `DETERMINISTIC_REQUIRED` — `CORE:state`, `CORE:boundary`
- `input_invariants` — `DETERMINISTIC_REQUIRED` — `CORE:validation`, `CORE:data`, `UX_ACTION:input`, `UX_ACTION:validation`
- `command` — `DETERMINISTIC_REQUIRED` — `CORE:happy_path`, `CORE:entry_point`, `UX_ACTION:submit`
- `expected_domain_mutation` — `DETERMINISTIC_REQUIRED` — `CORE:side_effect`, `CORE:data`, `CORE:persistence`, `UX_ACTION:data_mutation`
- `forbidden_mutations` — `DETERMINISTIC_REQUIRED` — `CORE:boundary`, `CORE:side_effect`
- `default_result` — `DETERMINISTIC_REQUIRED` — `CORE:happy_path`, `UX_ACTION:success`, `UX_STATE:success`
- `result_expectations` — `DETERMINISTIC_REQUIRED` — `CORE:happy_path`, `CORE:alternative_path`, `CORE:error`, `CORE:recovery`, `CORE:acceptance`, `UX_ACTION:success`, `UX_ACTION:failure`, `UX_STATE:success`, `UX_STATE:error`
- `version_result` — `DETERMINISTIC_REQUIRED` — `CORE:state`, `CORE:persistence`
- `history_result` — `DETERMINISTIC_REQUIRED` — `CORE:persistence`, `CORE:data`
- `business_side_effects` — `DETERMINISTIC_REQUIRED` — `CORE:side_effect`
- `delivery_effects` — `DETERMINISTIC_REQUIRED` — `CORE:notification`, `CORE:side_effect`, `UX_ACTION:notification`
- `idempotency` — `DETERMINISTIC_REQUIRED` — `GRILL:GRILL-ASYNC-1:idempotency`, `CORE:recovery`, `CORE:side_effect`
- `rejection` — `DETERMINISTIC_REQUIRED` — `CORE:error`, `CORE:validation`, `CORE:permission`, `UX_ACTION:failure`, `UX_ACTION:permission`
- `recovery` — `DETERMINISTIC_REQUIRED` — `CORE:recovery`, `GRILL:GRILL-ASYNC-1:retry`, `GRILL:GRILL-ASYNC-1:reconciliation`, `UX_ACTION:retry`
- `visible_success` — `REVIEW_PERMITTED` — `UX_STATE:success`, `UX_STATE:completed`, `UX_ACTION:success`, `CORE:acceptance`
- `visible_error` — `REVIEW_PERMITTED` — `UX_STATE:error`, `UX_ACTION:failure`, `CORE:error`
- `superseded_rules` — `DETERMINISTIC_REQUIRED` — `CORE:boundary`
- `test_obligations` — `DETERMINISTIC_REQUIRED` — `CORE:acceptance`
- `trace` — `DETERMINISTIC_REQUIRED` — `CORE:goal`, `CORE:acceptance`

## Exact lifecycle responsibility profile

- `current_states` — `DETERMINISTIC_REQUIRED` — `CORE:state`
- `allowed_transitions` — `DETERMINISTIC_REQUIRED` — `CORE:state`, `CORE:happy_path`, `CORE:alternative_path`
- `forbidden_transitions` — `DETERMINISTIC_REQUIRED` — `CORE:state`, `CORE:boundary`
- `boundary_conditions` — `DETERMINISTIC_REQUIRED` — `CORE:boundary`, `CORE:precondition`
- `reversibility` — `DETERMINISTIC_REQUIRED` — `CORE:recovery`, `CORE:boundary`, `GRILL:GRILL-DESTRUCTIVE-ACTION-1:undo`, `GRILL:GRILL-DESTRUCTIVE-ACTION-1:irreversible_boundary`
- `reversal_window` — `DETERMINISTIC_REQUIRED` — `GRILL:GRILL-DESTRUCTIVE-ACTION-1:grace_period`, `GRILL:GRILL-DESTRUCTIVE-ACTION-1:undo`, `CORE:boundary`
- `object_outcome` — `DETERMINISTIC_REQUIRED` — `CORE:state`, `CORE:side_effect`
- `required_reason` — `DETERMINISTIC_REQUIRED` — `CORE:validation`, `GRILL:GRILL-DESTRUCTIVE-ACTION-1:reason`
- `required_confirmation` — `DETERMINISTIC_REQUIRED` — `CORE:boundary`, `CORE:permission`, `GRILL:GRILL-DESTRUCTIVE-ACTION-1:confirmation`
- `required_evidence` — `DETERMINISTIC_REQUIRED` — `CORE:validation`, `CORE:data`
- `authority` — `DIRECT_REQUIRED` — `CORE:actor`, `CORE:permission`, `GRILL:GRILL-PERMISSION-1:role`
- `history_preservation` — `DETERMINISTIC_REQUIRED` — `CORE:persistence`, `CORE:data`

## Scope relevance

Every action/lifecycle declares `authority_scope_refs`. A source seed is eligible only when its `location.owner_ref` is present in that list.

For an `UX_ACTION` seed, the action must also declare an exact `ux_action_locator`, and the seed's screen/action must equal that locator. A seed from another screen action cannot satisfy the field merely because its axis name is allowed.

Every `authority_scope_ref` must resolve to a current `REQ-*`, `SURF-*`, or `SCR-*` in the M4-closed state.

## Task 2 tests

- [ ] **Step 1: Add RED responsibility-profile tests**

Verify exact profile ID, exact action/lifecycle inventories, every expectation above, every allowed selector above, canonical profile digest determinism, no duplicate selectors, and rejection of extra/missing fields.

- [ ] **Step 2: Add RED DIRECT/MACHINE/REVIEW tests**

Required cases:

1. DIRECT returns byte-equivalent JSON value from one permitted source seed;
2. DIRECT_REQUIRED rejects MACHINE and REVIEW;
3. DETERMINISTIC_REQUIRED accepts DIRECT and valid machine extraction/selection but rejects REVIEW;
4. REVIEW_PERMITTED accepts all three semantic forms;
5. `extract` uses RFC 6901, rejects empty pointer and missing pointer;
6. `select` requires an object source, sorted unique keys and no missing key;
7. arbitrary `eval`, expression, template, compose, callback and natural-language operator names are rejected;
8. wrong owner scope is rejected;
9. wrong UX action locator is rejected;
10. selector-axis mismatch is rejected;
11. REVIEW requires meaningful `why_structuring_is_insufficient` and `interpretation_scope` plus at least one permitted seed;
12. `UNRESOLVED` is recognized as a semantic gap, never emitted as a derived field.

- [ ] **Step 3: Run Task 2 RED**

```bash
python -m unittest tests.test_downstream_v2_derivation -v
```

Expected: FAIL because profile/derivation modules do not exist.

- [ ] **Step 4: Implement profile loading and derivation engine**

Responsibility JSON contains no stored self-digest. Runtime computes SHA-256 over canonical parsed JSON and rejects any inventory/mapping drift from the frozen constants in `derivation.py`.

- [ ] **Step 5: Run Task 2 GREEN plus frozen boundaries**

```bash
python -m unittest \
  tests.test_downstream_v2_derivation \
  tests.test_downstream_v2_seeds \
  tests.test_downstream_v2_frozen_boundaries -v
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add skills/joewrks-product-definition/downstream_v2/derivation.py \
  skills/joewrks-product-definition/downstream_v2/references/field-responsibility-v1.json \
  skills/joewrks-product-definition/downstream_v2/schemas/handoff-definition.schema.json \
  tests/test_downstream_v2_derivation.py
git commit -m "feat: define downstream v2 semantic responsibility policy"
```

---

# Task 3 — Compile action-conformance/2.0 and make semantic debt executable

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v2/semantic_debt.py`
- Create: `skills/joewrks-product-definition/downstream_v2/contracts.py`
- Create: `skills/joewrks-product-definition/downstream_v2/compiler.py`
- Create: `skills/joewrks-product-definition/downstream_v2/schemas/action-contract-v2.schema.json`
- Create: `tests/test_downstream_v2_compiler.py`
- Create: `tests/test_downstream_v2_semantic_debt.py`

**Interfaces:**

`semantic_debt.py`:

```python
def semantic_debt_report(
    *,
    derived_fields: list[tuple[str, dict[str, object]]],
    gaps: list[dict[str, object]],
) -> dict[str, object]: ...
```

`contracts.py`:

```python
COMPILER_ID = "joewrks-product-definition/downstream-v2"
COMPILER_VERSION = "core-semantic-closure-v2-m5.1"


def semantic_contract_projection(contract: dict[str, object]) -> dict[str, object]: ...
def semantic_contract_hash(contract: dict[str, object]) -> str: ...
def artifact_hash(contract: dict[str, object]) -> str: ...
def validate_action_contract_v2(contract: dict[str, object]) -> list[dict[str, str]]: ...
```

`compiler.py`:

```python
def compile_handoff_definition(
    state: dict[str, object],
    definition: dict[str, object],
) -> dict[str, object]: ...
```

Task 3 initially returns semantic `gaps`; Task 4 attaches formal re-entry events.

## action-conformance/2.0 shape

A successful contract contains exactly these top-level fields:

```text
contract_schema_version
compiler
source_authority
responsibility_profile
source_seed_inventory
actions
lifecycles
semantic_debt
handoff_status
semantic_assurance
semantic_contract_hash
artifact_hash
```

`contract_schema_version` is `joewrks.action-conformance/2.0`.

`source_authority` is the Task-1 authority envelope plus:

```text
source_seed_inventory_digest
```

`responsibility_profile` contains:

```text
profile_id = joewrks.downstream-responsibility/1.0
digest = <64 lowercase hex>
```

Each output action is:

```python
{
    "action_id": "...",
    "authority_scope_refs": [...],
    "ux_action_locator": {...} | None,
    "fields": {
        "actor": <semantic field>,
        ... exact 26 fields ...
    },
}
```

Each lifecycle is analogous with exact 12 fields.

## Output semantic-field forms

DIRECT output:

```python
{
    "value": <exact seed value>,
    "source_seed_refs": ["SEED-..."],
    "derivation": {"kind": "DIRECT_AUTHORITY"},
}
```

MACHINE output:

```python
{
    "value": <deterministically derived value>,
    "source_seed_refs": ["SEED-..."],
    "derivation": {
        "kind": "MACHINE_DERIVED",
        "operator": "extract | select",
        ... exact operator arguments ...
    },
}
```

REVIEW output:

```python
{
    "value": <proposed interpretation>,
    "source_seed_refs": ["SEED-..."],
    "derivation": {
        "kind": "REVIEW_REQUIRED",
        "why_structuring_is_insufficient": "...",
        "interpretation_scope": "..."
    },
}
```

No output semantic field may omit provenance.

## Semantic debt report

Exact top-level counts:

```text
direct_authority_count
machine_derived_count
review_required_count
authority_gap_count
```

Also include deterministic field inventories:

```text
direct_authority_fields
machine_derived_fields
review_required_fields
authority_gaps
```

Field paths are canonical strings:

```text
actions/<action_id>/<field>
lifecycles/<lifecycle_id>/<field>
```

Every gap has:

```python
{
    "code": "SEMANTIC_AUTHORITY_GAP",
    "field_path": "...",
    "reason": "...",
    "gap_type": "AMBIGUITY_FOUND | CONTRACT_CONFLICT | OUT_OF_SCOPE_REQUEST",
    "required_expectation": "DIRECT_REQUIRED | DETERMINISTIC_REQUIRED | REVIEW_PERMITTED",
    "authority_scope_refs": [...],
    "candidate_seed_refs": [...],
    "evidence_refs": [...],
}
```

A responsibility violation such as REVIEW for DETERMINISTIC_REQUIRED becomes a semantic authority gap. It is not silently downgraded to review debt.

## Handoff status and assurance

A production contract is materialized only when `authority_gap_count == 0`.

If there are gaps, compiler result is:

```python
{
    "status": "REENTRY_REQUIRED",
    "contract": None,
    "semantic_debt": <report>,
    "gaps": [...],
    "reentry_events": [],
}
```

Task 4 fills `reentry_events`.

When no gaps exist:

```text
review_required_count = 0
→ handoff_status = AUTHORITY_READY_MACHINE_VERIFIED
→ semantic_assurance.status = NOT_REQUIRED

review_required_count > 0
→ handoff_status = AUTHORITY_READY_REVIEW_PENDING
→ semantic_assurance.status = NOT_MEASURED
```

`NOT_MEASURED` is not failure of Product Definition authority. It means semantic-review reliability has not been established.

## Semantic vs artifact hashes

`semantic_contract_hash` is SHA-256 of the canonical contract projection excluding:

```text
semantic_contract_hash
artifact_hash
source_authority.snapshot_state_sha256
```

It includes approved definition/manifest digests, binding-contract identities, seed inventory digest, responsibility profile, actions/lifecycles and semantic debt.

`artifact_hash` is SHA-256 of the entire materialized contract excluding only `artifact_hash`. It therefore includes the current snapshot state SHA.

Consequences:

- unconsumed-evidence-only state snapshot change may change `artifact_hash`;
- it must not change `semantic_contract_hash` when M4 semantic digest and source-seed inventory are unchanged.

## Task 3 tests

- [ ] **Step 1: Add RED compiler and semantic-debt tests**

Required compiler cases:

1. valid M4 CLOSED state + complete deterministic definition produces `joewrks.action-conformance/2.0`;
2. wrong product slug is rejected;
3. duplicate action/lifecycle IDs are rejected;
4. missing/extra semantic fields are rejected;
5. every output semantic field uses a permitted seed in its exact scope;
6. DIRECT output equals exact seed value;
7. machine output is recomputed rather than trusting a proposed output value;
8. REVIEW output exists only on REVIEW_PERMITTED fields;
9. DETERMINISTIC_REQUIRED + REVIEW produces `SEMANTIC_AUTHORITY_GAP` and no contract;
10. `UNRESOLVED` produces a gap and no contract;
11. no gap is ever emitted inside a production contract;
12. `authority_gap_count == 0` is mandatory for materialization.

Required debt cases:

1. counts equal field inventories exactly;
2. one field is counted in exactly one DIRECT/MACHINE/REVIEW class;
3. gaps are not counted as REVIEW_REQUIRED;
4. field order does not change report bytes;
5. `review_required_count > 0` yields `AUTHORITY_READY_REVIEW_PENDING` and assurance `NOT_MEASURED`;
6. zero review yields `AUTHORITY_READY_MACHINE_VERIFIED` and assurance `NOT_REQUIRED`.

Required hash cases:

1. repeated compilation is byte deterministic;
2. changing a semantic field changes both semantic and artifact hashes;
3. changing only `snapshot_state_sha256` changes artifact hash but not semantic contract hash;
4. source-seed inventory digest is committed into semantic contract hash;
5. responsibility-profile digest is committed into semantic contract hash;
6. malformed/non-lowercase hashes are rejected.

- [ ] **Step 2: Run Task 3 RED**

```bash
python -m unittest \
  tests.test_downstream_v2_compiler \
  tests.test_downstream_v2_semantic_debt -v
```

Expected: FAIL because compiler/contracts/debt modules do not exist.

- [ ] **Step 3: Implement compiler/debt/contracts**

Do not add an automatic field mapper that guesses semantic meaning from arbitrary product prose. The handoff definition selects a responsibility field and an approved source seed; the compiler verifies and materializes that mapping.

- [ ] **Step 4: Run Task 3 GREEN plus prior M5 tests**

```bash
python -m unittest \
  tests.test_downstream_v2_compiler \
  tests.test_downstream_v2_semantic_debt \
  tests.test_downstream_v2_derivation \
  tests.test_downstream_v2_seeds \
  tests.test_downstream_v2_frozen_boundaries -v
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/joewrks-product-definition/downstream_v2/semantic_debt.py \
  skills/joewrks-product-definition/downstream_v2/contracts.py \
  skills/joewrks-product-definition/downstream_v2/compiler.py \
  skills/joewrks-product-definition/downstream_v2/schemas/action-contract-v2.schema.json \
  tests/test_downstream_v2_compiler.py \
  tests/test_downstream_v2_semantic_debt.py
git commit -m "feat: compile action conformance v2 with semantic debt"
```

---

# Task 4 — Implement dependency-scoped Product Definition re-entry and contract drift audit

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v2/reentry.py`
- Create: `skills/joewrks-product-definition/downstream_v2/schemas/reentry-event.schema.json`
- Create: `tests/test_downstream_v2_reentry.py`
- Modify: `skills/joewrks-product-definition/downstream_v2/compiler.py`

**Interfaces:**

```python
def build_reentry_events(
    *,
    source_authority: dict[str, object],
    definition: dict[str, object],
    gaps: list[dict[str, object]],
    source_contract_hash: str | None,
) -> list[dict[str, object]]: ...


def audit_contract_against_state(
    contract: dict[str, object],
    state: dict[str, object],
) -> dict[str, object]: ...
```

## Re-entry event identity

Every event has:

```text
schema_version = joewrks.product-definition-reentry/1.0
```

Exact event shape:

```python
{
    "schema_version": "joewrks.product-definition-reentry/1.0",
    "event_id": "REENTRY-<24 lowercase hex>",
    "event_type": "AMBIGUITY_FOUND | CONTRACT_CONFLICT | OUT_OF_SCOPE_REQUEST",
    "source_definition_digest": "<M4 approved definition digest>",
    "source_contract_hash": "<semantic contract hash>" | None,
    "affected_authority_ids": [...],
    "affected_action_ids": [...],
    "affected_lifecycle_ids": [...],
    "evidence_refs": [...],
    "halt_scope": {
        "mode": "AFFECTED_ONLY",
        "action_ids": [...],
        "lifecycle_ids": [...]
    },
    "candidate_unknown": {
        "suggested_question": "...",
        "why_it_matters": "...",
        "required_authority_class": "FACTUAL | INTENT | CONSTRAINT | BEHAVIORAL | PREFERENCE",
        "affected_ids": [...]
    },
    "recommended_action": "REENTER_PRODUCT_DEFINITION"
}
```

The event ID is the first 24 lower-hex characters of SHA-256 over canonical event content **excluding `event_id`**.

`candidate_unknown` is a proposal only. It is not a canonical `UNK-*` record, has no stable Product Definition ID, and M5 never writes it to `state.json`.

## Gap-to-event mapping

- missing deterministic/direct product meaning → `AMBIGUITY_FOUND`;
- incompatible/stale/mismatched seed or conflicting approved authority → `CONTRACT_CONFLICT`;
- handoff definition explicitly marks `gap_type = OUT_OF_SCOPE_REQUEST` → `OUT_OF_SCOPE_REQUEST`.

Every gap affects only its containing action/lifecycle. Multiple gaps for the same action/event type may be deterministically coalesced only when their affected scope and authority/evidence sets are identical; otherwise keep separate events.

## Drift audit statuses

`audit_contract_against_state` returns one of:

```text
CONFORMANT
DEFINITION_NOT_READY
REENTRY_REQUIRED
```

### CONFORMANT

- current state is M4 CLOSED;
- approved definition digest equals contract source authority;
- responsibility/binding identities match;
- every used source seed verifies at its original semantic location;
- semantic contract hash remains internally valid.

Raw `snapshot_state_sha256` is allowed to differ when semantic authority and used seeds remain equal.

### DEFINITION_NOT_READY

Use this when current state is structurally evaluable and its semantic definition digest still equals the contract's approved definition digest, but M4 currently returns `closed = false` for a non-semantic readiness/control reason such as a stale discovery baseline.

Downstream work pauses. Do not emit a semantic Product Definition re-entry event unless semantic authority actually differs.

### REENTRY_REQUIRED

Use when:

- semantic definition digest differs;
- a used seed no longer verifies;
- referenced authority disappears/becomes non-current;
- responsibility/binding contract identity changes incompatibly;
- the contract itself contains invalid semantic provenance.

Map changed seeds back to every action/lifecycle field that consumes them and emit dependency-scoped `CONTRACT_CONFLICT` events. Do not automatically halt unrelated actions.

## Task 4 tests

- [ ] **Step 1: Add RED re-entry construction tests**

Required cases:

1. ambiguity gap → deterministic `AMBIGUITY_FOUND` event;
2. explicit out-of-scope gap → `OUT_OF_SCOPE_REQUEST`;
3. wrong/mismatched seed → `CONTRACT_CONFLICT`;
4. event bytes/id deterministic under repeated build;
5. candidate unknown contains no canonical `UNK-*` ID;
6. event never mutates state;
7. affected-only halt scope excludes unrelated actions/lifecycles.

- [ ] **Step 2: Add RED drift-audit tests**

Required cases:

1. unchanged M4 authority → `CONFORMANT`;
2. new unconsumed evidence + rebuilt M4 baseline → `CONFORMANT`, same semantic contract hash, different raw snapshot allowed;
3. baseline stale but semantic digest unchanged → `DEFINITION_NOT_READY`, no semantic re-entry event;
4. consumed bound authority value changes → `REENTRY_REQUIRED`;
5. one action's seed drift halts only actions/lifecycles consuming that seed;
6. unrelated semantic seed stays runnable;
7. state authority revision/digest mismatch produces re-entry rather than silently recompiling;
8. missing/stale source record produces re-entry;
9. malformed contract fails closed and does not emit a false conformant status.

- [ ] **Step 3: Run Task 4 RED**

```bash
python -m unittest tests.test_downstream_v2_reentry -v
```

Expected: FAIL because re-entry runtime does not exist.

- [ ] **Step 4: Implement re-entry and wire compiler gaps**

After Task 4, `compile_handoff_definition` fills formal `reentry_events` whenever `authority_gap_count > 0` and still returns `contract = None`.

- [ ] **Step 5: Run Task 4 GREEN**

```bash
python -m unittest \
  tests.test_downstream_v2_reentry \
  tests.test_downstream_v2_compiler \
  tests.test_downstream_v2_semantic_debt \
  tests.test_downstream_v2_frozen_boundaries -v
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add skills/joewrks-product-definition/downstream_v2/reentry.py \
  skills/joewrks-product-definition/downstream_v2/schemas/reentry-event.schema.json \
  skills/joewrks-product-definition/downstream_v2/compiler.py \
  tests/test_downstream_v2_reentry.py
git commit -m "feat: add downstream v2 product-definition reentry protocol"
```

---

# Task 5 — Create semantic-review/2.0 as assurance-only, reliability NOT_MEASURED

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v2/semantic_review/__init__.py`
- Create: `skills/joewrks-product-definition/downstream_v2/semantic_review/package.py`
- Create: `skills/joewrks-product-definition/downstream_v2/semantic_review/output.py`
- Create: `skills/joewrks-product-definition/downstream_v2/semantic_review/build_package.py`
- Create: `skills/joewrks-product-definition/downstream_v2/schemas/semantic-review-input-v2.schema.json`
- Create: `skills/joewrks-product-definition/downstream_v2/schemas/semantic-review-output-v2.schema.json`
- Create: `tests/test_downstream_v2_semantic_review.py`

**Interfaces:**

```python
SEMANTIC_REVIEW_VERSION = "joewrks.semantic-review/2.0"
RELIABILITY_STATUS = "NOT_MEASURED"


def build_semantic_review_package(contract: dict[str, object]) -> dict[str, object] | None: ...
def validate_semantic_review_output(
    review_package: dict[str, object],
    output: dict[str, object],
) -> list[dict[str, str]]: ...
def semantic_assurance_result(
    contract: dict[str, object],
    review_package: dict[str, object] | None,
    output: dict[str, object] | None,
) -> dict[str, object]: ...
```

## Review input package

If `review_required_count == 0`, builder returns `None`.

Otherwise package identity is `joewrks.semantic-review/2.0` and contains:

```text
review_schema_version
reliability_status = NOT_MEASURED
source_semantic_contract_hash
source_definition_digest
responsibility_profile
review_obligations
package_hash
```

Each review obligation contains:

```python
{
    "obligation_id": "REVIEW-<24 lowercase hex>",
    "field_path": "actions/... or lifecycles/...",
    "proposed_value": <exact contract REVIEW_REQUIRED value>,
    "proposed_value_sha256": "...",
    "source_seed_refs": [...],
    "source_seeds": [<exact seed snapshots>],
    "why_structuring_is_insufficient": "...",
    "interpretation_scope": "..."
}
```

Obligation ID is deterministic from field path + proposed-value hash + source-seed refs.

The package includes only REVIEW_REQUIRED fields. DIRECT/MACHINE fields are not sent to semantic review.

## Review output

Output identity is also `joewrks.semantic-review/2.0` and records:

```text
review_schema_version
input_package_hash
reliability_status = NOT_MEASURED
results
output_hash
```

Every obligation has exactly one result:

```text
CONFIRMED_INTERPRETATION
REJECTED_INTERPRETATION
UPSTREAM_AUTHORITY_GAP
```

Each result includes the exact `obligation_id`, exact `reviewed_value_sha256`, and meaningful rationale.

`reviewed_value_sha256` must equal the review package's proposed value hash. Semantic Review cannot silently rewrite the contract value.

## Assurance semantics

- no REVIEW_REQUIRED fields → `NOT_REQUIRED`;
- REVIEW_REQUIRED fields, no complete output → `NOT_MEASURED` + `PENDING`;
- structurally complete CONFIRMED output → reliability remains `NOT_MEASURED`; completion may be recorded as `REVIEW_OUTPUT_RECORDED`, but never `PASS` or `RELIABLE`;
- any REJECTED_INTERPRETATION → Product Definition/contract conflict re-entry;
- any UPSTREAM_AUTHORITY_GAP → Product Definition ambiguity re-entry;
- semantic review output never creates canonical authority and never changes source Product Definition state or action contract values.

No M5 code may read a v0.4.3 calibration result and convert it into semantic-review/2.0 reliability.

## Task 5 tests

- [ ] **Step 1: Add RED semantic-review/2.0 tests**

Required cases:

1. machine-only contract produces no review package;
2. review-required contract produces package containing exactly review fields;
3. package bytes/hash deterministic;
4. package binds semantic contract hash, definition digest and source seeds;
5. reliability is exactly `NOT_MEASURED`;
6. output must cover every obligation exactly once;
7. reviewed value hash must match proposed value hash;
8. no output can replace proposed value;
9. confirmed output records completion but reliability remains NOT_MEASURED;
10. rejected interpretation creates CONTRACT_CONFLICT re-entry data;
11. upstream authority gap creates AMBIGUITY_FOUND re-entry data;
12. v1 semantic-review package/calibration files are never imported as reliability evidence;
13. strings `PASS`, `RELIABLE`, `CALIBRATED` are not valid M5 semantic-review/2.0 reliability states.

- [ ] **Step 2: Run Task 5 RED**

```bash
python -m unittest tests.test_downstream_v2_semantic_review -v
```

Expected: FAIL because semantic-review/2.0 package does not exist.

- [ ] **Step 3: Implement the review package/output boundary**

Use only current action-conformance/2.0 contract data. No network, no model call, no evaluator invocation, no generated adjudication, and no timestamps are part of M5.

- [ ] **Step 4: Run Task 5 GREEN plus frozen v1 semantic-review regressions**

```bash
python -m unittest \
  tests.test_downstream_v2_semantic_review \
  tests.test_semantic_review_package \
  tests.test_semantic_review_gate \
  tests.test_semantic_review_responsibility \
  tests.test_downstream_v2_frozen_boundaries -v
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/joewrks-product-definition/downstream_v2/semantic_review \
  skills/joewrks-product-definition/downstream_v2/schemas/semantic-review-input-v2.schema.json \
  skills/joewrks-product-definition/downstream_v2/schemas/semantic-review-output-v2.schema.json \
  tests/test_downstream_v2_semantic_review.py
git commit -m "feat: add semantic review 2.0 assurance boundary"
```

---

# Task 6 — Add read-only CLIs, normative docs and the M5 milestone gate

**Files:**
- Create: `skills/joewrks-product-definition/downstream_v2/compile.py`
- Create: `skills/joewrks-product-definition/downstream_v2/audit.py`
- Create: `skills/joewrks-product-definition/downstream_v2/README.md`
- Create: `skills/joewrks-product-definition/references/downstream-v2-contract.md`
- Create: `skills/joewrks-product-definition/references/implementation-reentry-contract.md`
- Create: `tests/test_downstream_v2_cli.py`

**Interfaces / CLI:**

Supported non-integrated invocation sets both package roots:

```text
PYTHONPATH=<skill-root>;<skill-root>/scripts
```

Platform-specific separator may differ. The package must not guess or mutate persistent environment configuration; M6 owns installed integration.

### Compile CLI

```text
python -m downstream_v2.compile STATE_JSON HANDOFF_DEFINITION_JSON
```

Exit codes:

```text
0 → contract compiled; stdout valid JSON; stderr empty
1 → Product Definition not closed, semantic authority gap, re-entry required, or invalid semantic input; stdout structured JSON; stderr empty
2 → usage/read/JSON parse error; stdout structured JSON; stderr empty
```

The CLI never writes source state or input definition.

### Audit CLI

```text
python -m downstream_v2.audit CONTRACT_JSON STATE_JSON
```

Exit codes:

```text
0 → CONFORMANT
1 → DEFINITION_NOT_READY or REENTRY_REQUIRED or invalid contract
2 → usage/read/JSON parse error
```

All outputs are JSON and no traceback is emitted for expected invalid input.

### Semantic-review package CLI

```text
python -m downstream_v2.semantic_review.build_package CONTRACT_JSON
```

Exit `0` with either:

```text
review_required = false, package = null
```

or a deterministic `joewrks.semantic-review/2.0` package.

Invalid contract/read/usage follows the same structured fail-closed convention.

## Normative documentation tokens

`downstream-v2-contract.md` must contain exact markers:

```text
DOWNSTREAM_V2_AUTHORITY_IMPLEMENTED_M5
ACTION_CONFORMANCE_2_0
SOURCE_SEEDS_FROM_M4_BINDINGS
SEMANTIC_AUTHORITY_GAP_REENTERS_PRODUCT_DEFINITION
REVIEW_REQUIRED_IS_ASSURANCE_NOT_AUTHORITY
AUTHORITY_GAP_COUNT_MUST_BE_ZERO
SEMANTIC_REVIEW_2_0_RELIABILITY_NOT_MEASURED
DOWNSTREAM_V1_REMAINS_FROZEN
M6_INTEGRATION_NOT_IMPLEMENTED_IN_M5
```

`implementation-reentry-contract.md` must contain:

```text
AMBIGUITY_FOUND
CONTRACT_CONFLICT
OUT_OF_SCOPE_REQUEST
AFFECTED_ONLY
CANDIDATE_UNKNOWN_IS_NOT_CANONICAL_AUTHORITY
REENTER_PRODUCT_DEFINITION
NO_SILENT_IMPLEMENTATION_PRODUCT_DECISIONS
```

Documentation must explain in plain language:

- Product Definition CLOSED is required before M5 compilation;
- action-conformance/2.0 reuses M4 exact binding seeds instead of hand-picking pointers;
- source snapshot hash and semantic authority digest are intentionally different;
- semantic authority gaps block handoff and return upstream;
- review-required fields may remain, but they are assurance work and cannot create product authority;
- semantic-review/2.0 reliability is NOT_MEASURED in M5;
- re-entry artifacts are read-only proposals and do not mutate state;
- M5 does not mean implementation/runtime/deployment has been integrated.

## Task 6 tests and final gate

- [ ] **Step 1: Add RED CLI/document contract tests**

Create `tests/test_downstream_v2_cli.py` covering successful compile, authority-gap compile, usage/read failures, conformant audit, dependency-scoped drift audit, semantic-review package/no-package cases, valid JSON output, deterministic bytes where inputs are deterministic, empty stderr, and no traceback for expected invalid input.

Also assert every normative documentation token above.

- [ ] **Step 2: Run CLI tests RED**

```bash
python -m unittest tests.test_downstream_v2_cli -v
```

Expected: FAIL before CLIs/docs exist.

- [ ] **Step 3: Implement CLIs and docs**

Do not add installation or production runtime wiring. State the exact non-integrated PYTHONPATH requirement and leave M6 as the adoption milestone.

- [ ] **Step 4: Run all M5-focused tests**

```bash
python -m unittest \
  tests.test_downstream_v2_frozen_boundaries \
  tests.test_downstream_v2_authority \
  tests.test_downstream_v2_seeds \
  tests.test_downstream_v2_derivation \
  tests.test_downstream_v2_compiler \
  tests.test_downstream_v2_semantic_debt \
  tests.test_downstream_v2_reentry \
  tests.test_downstream_v2_semantic_review \
  tests.test_downstream_v2_cli -v
```

Expected: exit `0`.

- [ ] **Step 5: Run M4 Semantic Closure regression**

```bash
python -m unittest \
  tests.test_authority_binding_v020 \
  tests.test_core_coverage_binding_v020 \
  tests.test_grill_binding_v020 \
  tests.test_ux_binding_v020 \
  tests.test_authority_consumption_v020 \
  tests.test_definition_digest_v020 \
  tests.test_approval_manifest_v020 \
  tests.test_semantic_closure_v020 -v
```

Expected: exit `0`.

- [ ] **Step 6: Run M3/M2 authority regressions**

```bash
python -m unittest \
  tests.test_materiality_v020 \
  tests.test_unknown_resolution_v020 \
  tests.test_autonomy_policy_v020 \
  tests.test_question_policy_v020 \
  tests.test_grill_packs_v020 \
  tests.test_grill_baseline_v020 \
  tests.test_evidence_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_contradictions_v020 \
  tests.test_reverse_bootstrap_v020 \
  tests.test_discovery_baseline_v020 -v
```

Expected: exit `0`.

- [ ] **Step 7: Run frozen downstream v1 regressions**

```bash
python -m unittest \
  tests.test_downstream_adapters \
  tests.test_downstream_authority \
  tests.test_downstream_contracts \
  tests.test_downstream_handoff \
  tests.test_downstream_product_bundles \
  tests.test_downstream_protocol \
  tests.test_downstream_schema_validation \
  tests.test_downstream_verifier -v
```

Expected: exit `0` with the v1 tree SHA unchanged.

- [ ] **Step 8: Run frozen semantic-review v1/v0.4.3 regressions**

```bash
python -m unittest \
  tests.test_semantic_review_hashing \
  tests.test_semantic_review_package \
  tests.test_semantic_review_output \
  tests.test_semantic_review_responsibility \
  tests.test_semantic_review_gate \
  tests.test_semantic_review_goldens \
  tests.test_semantic_review_negative_regressions \
  tests.test_semantic_review_statistics \
  tests.test_semantic_review_calibration_corpus \
  tests.test_semantic_review_calibration_control_plane \
  tests.test_official_calibration_controller -v
```

Expected: exit `0` subject only to the already-known environment-dependent pinned-runtime skip in the full suite; M5 must add no new skip.

- [ ] **Step 9: Run legacy regressions**

```bash
python -m unittest \
  tests.test_validators \
  tests.test_semantic_v012 \
  tests.test_legacy_v0121_frozen -v
```

Expected: exit `0`.

- [ ] **Step 10: Run the full repository suite and diff check**

```bash
python -m unittest discover -s tests -v
git diff --check
```

Expected: tests exit `0`; only the pre-existing environment-dependent pinned-runtime skip may remain. `git diff --check` exits `0`.

- [ ] **Step 11: Verify exact frozen trees/blobs**

Require:

```text
HEAD:skills/joewrks-product-definition/downstream
= b63568d8c4632b14bc806e7bff1908e94dea9669

HEAD:evals/semantic-review-v0.4.3
= a2dc7eed1a9b0a86e3295f2bde679cdd3b5c1c43
```

Also require all legacy/M4 blobs in Global Constraints to remain exact.

The implementation diff must contain no changed file under:

```text
skills/joewrks-product-definition/downstream/
evals/semantic-review-v0.4.3/
skills/joewrks-product-definition/scripts/
skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json
```

M5 may add new top-level reference files and `downstream_v2/`, but must not alter the M4 authority core.

- [ ] **Step 12: Run final semantic-boundary probes**

Explicitly demonstrate:

```text
M4 closed source → downstream v2 compiles
source seeds come only from positive M4 exact bindings
direct_authority_count > 0 in a direct fixture
machine_derived_count > 0 in an extract/select fixture
review_required_count > 0 is allowed only for REVIEW_PERMITTED fields
authority_gap_count > 0 → contract = null + reentry events
authority_gap_count = 0 → authority handoff materializes
unconsumed evidence + rebuilt baseline → semantic contract hash stable
used seed drift → REENTRY_REQUIRED
unrelated action remains outside halt scope
semantic-review/2.0 reliability = NOT_MEASURED
review output never mutates contract values or Product Definition state
```

- [ ] **Step 13: Commit docs/CLI gate**

```bash
git add skills/joewrks-product-definition/downstream_v2/compile.py \
  skills/joewrks-product-definition/downstream_v2/audit.py \
  skills/joewrks-product-definition/downstream_v2/README.md \
  skills/joewrks-product-definition/references/downstream-v2-contract.md \
  skills/joewrks-product-definition/references/implementation-reentry-contract.md \
  tests/test_downstream_v2_cli.py
git commit -m "docs: define downstream v2 authority and reentry boundary"
```

- [ ] **Step 14: Report milestone precisely and STOP**

Only after every M5 gate passes, push only the M5 implementation branch and report:

```text
CORE_SEMANTIC_CLOSURE_V2_M5_IMPLEMENTED
— DOWNSTREAM_V2_AUTHORITY / REENTRY_PROTOCOL / NOT_INTEGRATED
```

Include:

- implementation branch;
- planning/base SHA;
- final HEAD/parent/tree/remote SHA;
- changed-file count/list;
- per-task commits;
- M5 focused tests;
- M4/M3/M2 regressions;
- v1 downstream regressions;
- semantic-review v1/v0.4.3 regressions;
- legacy/frozen regressions;
- full-suite result and skip reasons;
- `git diff --check`;
- v1 downstream and v0.4.3 tree verification;
- M4 core blob verification;
- action-conformance/2.0 contract identity;
- responsibility-profile ID/digest;
- source-seed inventory count/digest;
- semantic debt counts;
- authority-gap/re-entry probes;
- semantic vs artifact hash stability probe;
- semantic-review/2.0 package/reliability probe;
- confirmation that M6 was not started;
- local/remote main SHA.

Do not start M6.

---

# M5 Plan Coverage Mapping

| Frozen design responsibility | M5 task |
| --- | --- |
| Preserve historical v1 downstream and v0.4.3 evidence | Task 1 + Task 6 gate |
| Reuse M4 exact bindings as downstream source seeds | Task 1 |
| `DIRECT_AUTHORITY` | Task 2–3 |
| Closed deterministic `MACHINE_DERIVED` | Task 2–3 |
| `REVIEW_REQUIRED` only when explicitly permitted | Task 2–3 |
| `SEMANTIC_AUTHORITY_GAP` upstream strengthening | Task 3–4 |
| Semantic debt report | Task 3 |
| `authority_gap_count == 0` handoff requirement | Task 3 |
| Implementation ambiguity/conflict/out-of-scope re-entry | Task 4 |
| Dependency-scoped halt | Task 4 |
| New `joewrks.action-conformance/2.0` identity | Task 3 |
| New `joewrks.semantic-review/2.0` identity | Task 5 |
| Semantic Review assurance, not authority creation | Task 5 |
| V2 review reliability does not inherit v0.4.3 | Task 5 |
| Unconsumed evidence does not semantically stale downstream | Tasks 1, 3, 4 |
| M6 integration/adoption not started | Global constraints + Task 6 |

M5 intentionally does not integrate the new package into installed skill routing, modify existing runtime product adapters, run production dogfood, calibrate semantic-review/2.0 reliability, mutate Product Definition state on re-entry, or merge any branch. Those are later integration/operational activities.