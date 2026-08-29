# Core Semantic Closure V2 — M4 Semantic Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn M3’s structurally complete Product Definition into exact semantic proof by binding Coverage/UX/Grill claims to canonical values, auditing authority consumption, generating an informed approval manifest and semantic definition digest, and enabling the first valid V2 `SEMANTIC_CLOSURE` result.

**Architecture:** Keep one canonical `state.json`. Add two focused pure-policy modules: `authority_binding_v2.py` owns exact JSON-Pointer/hash bindings and bidirectional authority audit; `approval_v2.py` owns semantic projection, definition digest, approval-manifest/history commitments and approval validation. `state_validation_v2.py` remains the public state/Closure entrypoint and composes M1–M4 metrics. M4 may remove the `semantic_closure_not_implemented` guard only in Task 6 after exact binding and approval gates are implemented and verified. M5 downstream 2.0 remains untouched.

**Tech Stack:** Python 3 standard library, JSON, Draft 2020-12 JSON Schema documents, RFC 6901 JSON Pointer, canonical UTF-8 JSON SHA-256, `unittest`.

**Spec:**
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md` — especially sections 21–33 and 43–46
- `docs/superpowers/audits/2026-08-29-core-semantic-closure-v2-m3-source-audit.md`

## Global Constraints

- Implement from an isolated branch/worktree based on the exact M4 planning HEAD; that planning branch must descend from M3 HEAD `8786deb5749ba39e526d1707d63acc27f60b2b02`.
- Preserve frozen legacy `0.1.2.1` files byte-for-byte.
- Preserve `skills/joewrks-product-definition/downstream/` and `evals/semantic-review-v0.4.3/` unchanged.
- Preserve `joewrks.action-conformance/1.0` and `joewrks.semantic-review/1.0` unchanged.
- Keep V2 `schema_version = "0.2.0"`.
- Preserve M2 evidence/reverse-bootstrap authority and M3 Materiality/Grill/autonomy semantics.
- `INFERRED_INTENT` and unapproved `DESIGN_ARTIFACT` remain candidate-only evidence and cannot become M4 N/A basis authority by themselves.
- M4 exact bindings use canonical **record-relative** JSON Pointers plus SHA-256 of canonical JSON values. M5 may later translate these to downstream-global source pointers; M4 must not import or modify downstream v1 code.
- M4 binding hash canonicalization must match the frozen provenance convention: `json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))`, UTF-8, SHA-256.
- M4 must not implement `DIRECT_AUTHORITY / MACHINE_DERIVED / REVIEW_REQUIRED`, `SEMANTIC_AUTHORITY_GAP`, action-conformance/2.0 or semantic-review/2.0. Those remain M5.
- `unknown_unknown_exhaustiveness_claimed` remains `false`.
- `active_grill_packs_complete` retains M3 meaning: topology/identity/instance/inventory completeness, separate from axis resolution.
- Approval and definition digests must not be invalidated by **unconsumed** evidence alone.
- `project.definition_status` and the current `approval` object are control state, not product meaning, and are excluded from `approved_definition_digest` to avoid READY_FOR_REVIEW → CLOSED digest churn.
- Every behavior-changing code task follows RED → GREEN → refactor.
- Strongest successful milestone label is `IMPLEMENTED_M4 / SEMANTIC_CLOSURE_AVAILABLE / NOT_INTEGRATED`.

---

## File Map

### Create M4 runtime modules

- `skills/joewrks-product-definition/scripts/authority_binding_v2.py`
  - canonical value hashing, record-relative JSON Pointer resolution, binding-contract loading, Core/Grill/UX exact-binding validation, authority-consumption graph and binding metrics.
- `skills/joewrks-product-definition/scripts/approval_v2.py`
  - semantic projection, consumed-evidence selection, definition digest, approval manifest, approval commitment/history validation and approval metrics.
- `skills/joewrks-product-definition/scripts/authority_binding_value.py`
  - read-only helper CLI that returns one exact binding for `RECORD_ID + RECORD_RELATIVE_POINTER`.
- `skills/joewrks-product-definition/scripts/build_approval_manifest.py`
  - read-only compiler that emits the manifest, its digest and the matching approval-history commitment.

### Create binding contracts/references

- `skills/joewrks-product-definition/references/binding-contracts/binding-contract.schema.json`
- `skills/joewrks-product-definition/references/binding-contracts/product-coverage-binding-v1.json`
- `skills/joewrks-product-definition/references/binding-contracts/ux-coverage-binding-v1.json`
- `skills/joewrks-product-definition/references/semantic-freeze-contract-v0.2.0.md`

### Modify V2 canonical contract/runtime

- `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- `skills/joewrks-product-definition/scripts/grill_v2.py`
- `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- `skills/joewrks-product-definition/references/grill-contract-v0.2.0.md`
- `tests/v020_support.py`

### Create M4 tests

- `tests/test_authority_binding_v020.py`
- `tests/test_core_coverage_binding_v020.py`
- `tests/test_grill_binding_v020.py`
- `tests/test_ux_binding_v020.py`
- `tests/test_authority_consumption_v020.py`
- `tests/test_definition_digest_v020.py`
- `tests/test_approval_manifest_v020.py`
- `tests/test_semantic_closure_v020.py`

### Existing tests allowed fixture-shape updates only

- M1–M3 V2 tests whose literal states contain `project.closure_contract`, `coverage`, `ux_coverage`, `grill_coverage`, `approval`, or `approval_history`.
- `tests/test_skill_package.py` only for explicit sibling imports/resources introduced by M4.

Do not weaken earlier behavioral assertions. Fixture updates may only satisfy the new M4 canonical shape while preserving the original test’s meaning.

---

# Task 1 — Exact binding primitives and frozen Binding Contracts

**Files:**
- Create: `skills/joewrks-product-definition/scripts/authority_binding_v2.py`
- Create: `skills/joewrks-product-definition/scripts/authority_binding_value.py`
- Create: `skills/joewrks-product-definition/references/binding-contracts/binding-contract.schema.json`
- Create: `skills/joewrks-product-definition/references/binding-contracts/product-coverage-binding-v1.json`
- Create: `skills/joewrks-product-definition/references/binding-contracts/ux-coverage-binding-v1.json`
- Create: `tests/test_authority_binding_v020.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- Modify: `tests/v020_support.py`

**Interfaces:**

```python
class BindingError(ValueError):
    code: str
    detail: object


def canonical_json(value: object) -> str: ...
def sha256_json(value: object) -> str: ...
def resolve_record_pointer(record: object, pointer: str) -> object: ...
def canonical_record_index(state: dict[str, object]) -> dict[str, tuple[str, dict[str, object]]]: ...
def make_authority_binding(state: dict[str, object], record_id: str, pointer: str) -> dict[str, str]: ...
def verify_authority_binding(
    state: dict[str, object],
    binding: dict[str, str],
    *,
    allowed_types: set[str],
    semantic_roots: dict[str, set[str]],
    basis: bool = False,
) -> tuple[str, dict[str, object]]: ...
def load_binding_contracts() -> dict[str, dict[str, object]]: ...
def binding_contract_identity() -> dict[str, dict[str, str]]: ...
```

## Binding shape

Every exact binding is exactly:

```json
{
  "record_id": "RULE-014",
  "pointer": "/statement",
  "value_sha256": "<64 lowercase hex>"
}
```

Pointers are relative to the canonical record root, never array indices in `state.json`. Empty pointer `""` is rejected for M4 Coverage/UX bindings because Closure must point at semantic content, not merely hash an entire record.

## Record type mapping

`canonical_record_index()` indexes stable records from:

```text
objects.*
evidence
surface_manifest.records
contradictions
```

with prefix types:

```text
GOAL USR REQ UNK DEC RULE FLOW SCR STATE DATA INT AC TASK EVD SURF CON
```

Duplicate IDs remain a state-validation error from earlier milestones.

## Canonical hashing

Use exactly:

```python
def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
```

This intentionally matches the existing frozen downstream v1 provenance hash convention without importing downstream code.

## Product Coverage Binding Contract

Create contract identity:

```text
contract_id = joewrks.product-coverage-binding
version = 1.0
```

The contract contains the frozen Core-axis type mapping from the design:

```text
actor              → USR DEC RULE
goal               → GOAL REQ
entry_point        → FLOW SCR RULE
precondition       → RULE STATE FLOW
happy_path         → FLOW REQ
alternative_path   → FLOW RULE
error              → FLOW STATE RULE
recovery           → FLOW STATE RULE
permission         → RULE DEC USR
state              → STATE RULE
data               → DATA RULE
side_effect        → RULE DATA INT
notification       → RULE FLOW INT
validation         → RULE DATA AC
boundary           → RULE DEC
persistence        → DATA RULE
security           → RULE DEC
privacy            → RULE DEC DATA
analytics          → RULE DATA INT
acceptance         → AC
```

The same contract defines specialist pack authority-type sets:

```text
GRILL-AUTH-1               → USR DEC RULE FLOW STATE DATA AC
GRILL-MONEY-1              → DEC RULE FLOW STATE DATA INT AC
GRILL-FILE-UPLOAD-1        → DEC RULE FLOW STATE DATA INT AC
GRILL-ASYNC-1              → DEC RULE FLOW STATE DATA INT AC
GRILL-PERMISSION-1         → USR DEC RULE FLOW STATE DATA AC
GRILL-DESTRUCTIVE-ACTION-1 → DEC RULE FLOW STATE DATA INT AC
```

### Semantic-pointer roots for COVERED/ADDRESSED proof

Contract-authorized proof pointers must begin under these semantic roots:

```text
GOAL  statement
USR   description actor_kind
REQ   statement scope ui_required materiality
DEC   statement decision_type resolution_mode decision_authority accepted_recommendation materiality
RULE  statement applies_to
FLOW  goal_refs entry preconditions paths outcomes
SCR   purpose requirement_refs interaction_mode major_actions
STATE owner_refs state_name conditions
DATA  name purpose ownership
INT   name purpose
AC    requirement_refs assertion
```

`/id`, `/status`, retirement/supersession metadata, and other control fields do not prove `COVERED`/`ADDRESSED` semantics.

### Basis bindings

N/A basis may use current `GOAL/USR/REQ/DEC/RULE/FLOW/SCR/STATE/DATA/INT/AC/SURF/EVD` records. For `EVD`, the record must be `CURRENT`, non-candidate-only and closure-eligible. Basis semantic roots may additionally include `SURF.status`, `SURF.kind`, `SURF.rationale`, `SURF.intent_classification`, and `EVD.claim/source_kind/authority_classes`.

## UX Binding Contract

Create identity:

```text
contract_id = joewrks.ux-coverage-binding
version = 1.0
```

Screen-state axis type mapping:

```text
default             → SCR STATE FLOW RULE
loading             → STATE FLOW
empty               → STATE FLOW RULE
partial             → STATE FLOW RULE
success             → STATE FLOW AC
error               → STATE FLOW RULE AC
disabled            → STATE RULE
permission_denied   → STATE RULE DEC USR
unauthenticated     → STATE RULE FLOW
offline             → STATE FLOW RULE
timeout             → STATE FLOW RULE
retrying            → STATE FLOW RULE
submitting          → STATE FLOW
completed           → STATE FLOW AC
cancelled           → STATE FLOW RULE
expired             → STATE RULE FLOW
```

Action-axis type mapping:

```text
entry                       → FLOW SCR RULE
precondition                → RULE STATE FLOW
input                       → DATA SCR RULE
validation                  → RULE DATA AC
submit                      → FLOW SCR RULE
success                     → FLOW STATE AC
failure                     → FLOW STATE RULE AC
retry                       → FLOW STATE RULE
cancel                      → FLOW STATE RULE
back                        → FLOW SCR RULE
refresh                     → FLOW STATE RULE
duplicate_concurrent_action → RULE STATE FLOW
timeout                     → FLOW STATE RULE
offline                     → STATE FLOW RULE
permission                  → RULE DEC USR
session_expiration          → STATE RULE FLOW
data_mutation               → DATA RULE FLOW
side_effect                 → RULE DATA INT
notification                → RULE FLOW INT
persistence                 → DATA RULE
undo                        → FLOW STATE RULE
destructive_confirmation    → RULE DEC FLOW
```

The UX contract uses the same semantic-pointer-root allowlist for shared record types.

- [ ] **Step 1: Add RED canonical hash/pointer/binding tests**

Create `tests/test_authority_binding_v020.py` covering:

- stable SHA-256 for string/object/list values;
- RFC 6901 `~0` and `~1` decoding;
- list-index traversal;
- invalid/non-resolving pointers;
- empty-pointer rejection for semantic bindings;
- `make_authority_binding()` returns exact record ID, relative pointer and hash;
- hash drift is rejected;
- non-CURRENT authority is rejected for semantic proof;
- wrong allowed type is rejected;
- `/status` cannot be used as COVERED authority;
- `/status` may be used as a permitted SURF N/A basis when the contract allows it;
- candidate-only `INFERRED_INTENT`/`DESIGN_ARTIFACT` evidence cannot be N/A basis;
- current closure-eligible evidence can be basis;
- `allow_nan=False` rejects NaN rather than hashing implementation-specific JSON.

- [ ] **Step 2: Add RED binding-contract identity/digest tests**

Require exactly two checked-in binding authority files, exact IDs/versions, exact axis inventories/type mappings above, exact semantic-root maps, and canonical SHA-256 identities. `binding_contract_identity()` returns:

```python
{
  "product": {"contract_id": "joewrks.product-coverage-binding", "version": "1.0", "digest": "..."},
  "ux": {"contract_id": "joewrks.ux-coverage-binding", "version": "1.0", "digest": "..."},
}
```

- [ ] **Step 3: Run Task 1 RED**

```bash
python -m unittest tests.test_authority_binding_v020 -v
```

Expected: FAIL because M4 binding runtime/contracts do not exist.

- [ ] **Step 4: Implement binding primitives/contracts minimally**

`authority_binding_v2.py` must not import `state_validation_v2` or downstream code. Binding-contract loading is deterministic and rejects missing/extra contract files, duplicate identity, contract schema drift, axis inventory drift, type mapping drift, and a stored `digest` field inside authority JSON.

- [ ] **Step 5: Strengthen `project.closure_contract`**

M4 canonical shape becomes exactly:

```json
{
  "level": "SEMANTIC_CLOSURE",
  "product_binding_contract": {
    "contract_id": "joewrks.product-coverage-binding",
    "version": "1.0",
    "digest": "<canonical current contract digest>"
  },
  "ux_binding_contract": {
    "contract_id": "joewrks.ux-coverage-binding",
    "version": "1.0",
    "digest": "<canonical current contract digest>"
  }
}
```

Update schema, template and shared fixture. Runtime validation rejects any ID/version/digest mismatch with `binding_contract_identity_mismatch`.

- [ ] **Step 6: Implement read-only binding helper CLI**

Command:

```text
python skills/joewrks-product-definition/scripts/authority_binding_value.py STATE_JSON RECORD_ID RECORD_RELATIVE_POINTER
```

It validates the V2 state enough to resolve a unique record, prints one deterministic compact JSON binding and never writes state. Read/usage errors exit `2`; invalid record/pointer exits `1` with structured JSON.

- [ ] **Step 7: Run Task 1 GREEN plus M3 regression**

```bash
python -m unittest \
  tests.test_authority_binding_v020 \
  tests.test_materiality_v020 \
  tests.test_grill_packs_v020 \
  tests.test_unknown_resolution_v020 \
  tests.test_state_v020_foundation -v
```

Expected: `OK`.

- [ ] **Step 8: Commit**

```bash
git add skills/joewrks-product-definition/scripts/authority_binding_v2.py \
  skills/joewrks-product-definition/scripts/authority_binding_value.py \
  skills/joewrks-product-definition/references/binding-contracts/ \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/templates/state-v0.2.0.example.json \
  tests/v020_support.py tests/test_authority_binding_v020.py
git commit -m "feat: add exact semantic authority binding primitives"
```

---

# Task 2 — Upgrade Core and specialist Grill coverage from claims to proof

**Files:**
- Modify: `skills/joewrks-product-definition/scripts/authority_binding_v2.py`
- Modify: `skills/joewrks-product-definition/scripts/grill_v2.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Create: `tests/test_core_coverage_binding_v020.py`
- Create: `tests/test_grill_binding_v020.py`
- Modify: M1–M3 fixtures containing Core/specialist coverage cells.

**Interfaces:**

```python
def validate_product_coverage_bindings(state: dict[str, object]) -> list[dict[str, str]]: ...
def product_binding_metrics(state: dict[str, object]) -> dict[str, int]: ...
```

## Exact Core coverage cell

Every Core cell has all five keys:

```json
{
  "status": "COVERED | OPEN | N/A",
  "authority_bindings": [],
  "unknown_refs": [],
  "basis_bindings": [],
  "rationale": null
}
```

Rules:

- `COVERED`: `authority_bindings` non-empty; all other arrays empty; `rationale = null`; every binding verifies against the axis’s allowed authority types and semantic roots.
- `OPEN`: `authority_bindings = []`, `basis_bindings = []`, `rationale = null`; `unknown_refs` non-empty and each resolves to a current OPEN `UNK-*`.
- `N/A`: `authority_bindings = []`, `unknown_refs = []`; `basis_bindings` non-empty; meaningful rationale; every basis binding verifies under basis rules.

For every CURRENT recomputed-MATERIAL `REQ-*`, exactly one Core coverage row exists and its cell inventory is the frozen 20-axis Core Grill set.

## Exact specialist cell

Keep M3 status vocabulary to avoid needless semantic churn:

```json
{
  "status": "ADDRESSED | OPEN | N/A",
  "authority_bindings": [],
  "unknown_refs": [],
  "basis_bindings": [],
  "rationale": null
}
```

- `ADDRESSED` is now exact proof and requires non-empty verified `authority_bindings` under that specialist pack’s allowed type set.
- `OPEN` keeps M3 exact-origin unknown rules.
- `N/A` requires exact basis bindings plus rationale.

Remove M3 specialist `authority_refs`/`basis_refs` from the canonical coverage-cell shape. Grill topology profile `basis_refs` remains M3 discovery topology authority and is not converted to M4 exact Coverage Binding.

## M4 binding metrics

Return at least:

```text
invalid_authority_binding
stale_authority_binding
coverage_without_authority
open_coverage_without_unknown
unjustified_na_without_basis
invalid_coverage_authority_type
core_coverage_gaps
specialist_binding_gaps
```

Each metric counts affected semantic cells once, not raw duplicate errors.

- [ ] **Step 1: Add Core Coverage RED tests**

Required cases include:

- bare `{status:"COVERED"}` invalid;
- COVERED binding with correct type/pointer/hash valid;
- wrong hash → stale/invalid binding;
- SUPERSEDED/STALE/RETIRED source → stale authority binding;
- actor bound to `DATA-*` → invalid authority type;
- acceptance bound to anything except `AC-*` → invalid type;
- pointer `/status` → invalid semantic binding;
- OPEN without unknown → blocker;
- OPEN with non-open/wrong-type unknown → blocker;
- N/A without rationale/basis → blocker;
- N/A with candidate-only EVD basis → blocker;
- duplicate Core rows → coverage gap;
- missing row for material current requirement → 20 semantic gaps or one deterministic row-gap metric as defined by implementation, never silently zero.

- [ ] **Step 2: Add specialist exact-binding RED tests**

Preserve all M3 activation/identity/origin/materiality-floor tests and add:

- ADDRESSED with broad `authority_refs` only is rejected by new canonical shape;
- exact correct binding passes;
- wrong source type/hash/status fails M4 binding metrics;
- N/A uses basis bindings, not broad basis refs;
- OPEN still requires the exact unique M3 `GRILL_PACK_AXIS` origin unknown;
- binding failure does not redefine `active_grill_packs_complete`; semantic proof failure is separate from M3 activation inventory completeness.

- [ ] **Step 3: Run Task 2 RED**

```bash
python -m unittest tests.test_core_coverage_binding_v020 tests.test_grill_binding_v020 -v
```

- [ ] **Step 4: Implement exact Core/specialist binding validation**

`authority_binding_v2.py` owns hash/type/pointer proof. `grill_v2.py` is updated only enough to understand the new specialist cell field names and preserve M3 topology/origin/inventory semantics; do not duplicate exact hash verification there.

- [ ] **Step 5: Run Task 2 GREEN plus full M3 Grill regression**

```bash
python -m unittest \
  tests.test_core_coverage_binding_v020 \
  tests.test_grill_binding_v020 \
  tests.test_grill_packs_v020 \
  tests.test_grill_baseline_v020 \
  tests.test_autonomy_policy_v020 \
  tests.test_unknown_resolution_v020 \
  tests.test_question_policy_v020 -v
```

- [ ] **Step 6: Commit**

```bash
git add skills/joewrks-product-definition/scripts/authority_binding_v2.py \
  skills/joewrks-product-definition/scripts/grill_v2.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  tests/test_core_coverage_binding_v020.py tests/test_grill_binding_v020.py \
  tests/test_grill_packs_v020.py tests/test_grill_baseline_v020.py \
  tests/v020_support.py
git commit -m "feat: bind Core and Grill coverage to exact authority"
```

---

# Task 3 — Exact UX Coverage Binding

**Files:**
- Modify: `skills/joewrks-product-definition/scripts/authority_binding_v2.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Create: `tests/test_ux_binding_v020.py`
- Modify: `tests/v020_support.py`
- Modify existing fixtures with current screens.

**Interfaces:**

```python
def validate_ux_coverage_bindings(state: dict[str, object]) -> list[dict[str, str]]: ...
def ux_binding_metrics(state: dict[str, object]) -> dict[str, int]: ...
```

## UX row contract

Every CURRENT `SCR-*` requires exactly one UX coverage row:

```json
{
  "screen_id": "SCR-001",
  "states": {
    "default": {"status":"...", "authority_bindings":[], "unknown_refs":[], "basis_bindings":[], "rationale":null}
  },
  "actions": [
    {
      "key": "submit",
      "cells": {
        "entry": {"status":"...", "authority_bindings":[], "unknown_refs":[], "basis_bindings":[], "rationale":null}
      }
    }
  ]
}
```

Required screen-state inventory is exactly:

```text
default loading empty partial success error disabled permission_denied
authenticated? NO — use `unauthenticated`
unauthenticated offline timeout retrying submitting completed cancelled expired
```

The exact frozen 16-state list is:

```text
default
loading
empty
partial
success
error
disabled
permission_denied
unauthenticated
offline
timeout
retrying
submitting
completed
cancelled
expired
```

Required action-axis inventory is exactly:

```text
entry
precondition
input
validation
submit
success
failure
retry
cancel
back
refresh
duplicate_concurrent_action
timeout
offline
permission
session_expiration
data_mutation
side_effect
notification
persistence
undo
destructive_confirmation
```

`actions[].key` inventory must exactly equal `screens[].major_actions`, with no duplicates and no missing/extra action rows. An empty `major_actions` list produces an empty action array but does not exempt the screen’s 16 state axes; irrelevant states are expressed as justified exact `N/A`.

UX cells use the same exact `COVERED / OPEN / N/A` cell shape as Core coverage, but authority type eligibility comes from the UX Binding Contract.

## UX metrics

At least:

```text
ux_coverage_gaps
screen_state_gaps
screen_action_inventory_gaps
ux_invalid_authority_binding
ux_stale_authority_binding
ux_open_without_unknown
ux_unjustified_na
```

- [ ] **Step 1: Add UX RED tests**

Cover:

- no row for CURRENT screen;
- duplicate screen rows;
- missing/extra state axis;
- missing/extra/duplicate action key;
- missing/extra action axis;
- valid exact state/action binding;
- wrong type for permission/error/persistence axes;
- stale hash/status;
- OPEN unknown rules;
- N/A exact basis rules;
- a screen with zero major actions still requires all state cells and zero action rows.

- [ ] **Step 2: Run Task 3 RED**

```bash
python -m unittest tests.test_ux_binding_v020 -v
```

- [ ] **Step 3: Implement schema/runtime UX exact binding**

Do not add a magic “non-interactive skips UX” escape hatch in M4. Every current screen is a product surface and receives state coverage; action coverage is driven solely by its explicit `major_actions` inventory.

- [ ] **Step 4: Run Task 3 GREEN plus screen regressions**

```bash
python -m unittest \
  tests.test_ux_binding_v020 \
  tests.test_state_v020_foundation \
  tests.test_surface_manifest_v020 \
  tests.test_reverse_bootstrap_v020 -v
```

- [ ] **Step 5: Commit**

```bash
git add skills/joewrks-product-definition/scripts/authority_binding_v2.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  tests/v020_support.py tests/test_ux_binding_v020.py \
  tests/test_state_v020_foundation.py
git commit -m "feat: bind UX coverage to exact authority"
```

---

# Task 4 — Bidirectional authority consumption and semantic-readiness gate

**Files:**
- Modify: `skills/joewrks-product-definition/scripts/authority_binding_v2.py`
- Create: `tests/test_authority_consumption_v020.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`

**Interfaces:**

```python
def build_authority_consumption_graph(state: dict[str, object]) -> dict[str, set[str]]: ...
def authority_consumption_metrics(state: dict[str, object]) -> dict[str, int]: ...
def semantic_readiness_metrics(state: dict[str, object]) -> dict[str, int]: ...
```

## Typed graph edges

The audit graph uses current canonical authority only. At minimum it includes:

```text
DEC.affects                    → DEC → target
RULE.applies_to                → target → RULE
FLOW.goal_refs                 → GOAL → FLOW
SCR.requirement_refs           → REQ → SCR
STATE.owner_refs               → owner → STATE
AC.requirement_refs            → REQ → AC
TASK.implements                → REQ → TASK
TASK.acceptance_refs           → AC → TASK
SURF.authority_refs            → SURF → authority (scope-to-authority trace; not a terminal consumption sink)
Core exact bindings            → bound authority → SINK:CORE
Specialist exact bindings      → bound authority → SINK:GRILL
UX exact bindings              → bound authority → SINK:UX
TASK                           → terminal delivery sink
```

Graph reference integrity is type-checked. Historical `SUPERSEDED/RETIRED` records do not satisfy current consumption.

## Material authority seeds

Seeds are:

- CURRENT `REQ-*` whose Materiality recomputes `MATERIAL`;
- CURRENT `DEC-*` whose Materiality recomputes `MATERIAL`.

Materiality propagates through typed downstream edges. `GOAL`, `USR`, and `TASK` are explicit terminal/root exceptions. Every other material-reachable current authority must have a path to at least one semantic sink (`CORE`, `GRILL`, `UX`, or TASK) or it is an orphan candidate.

A material current Decision specifically increments `unconsumed_material_decision` when it has no semantic-sink path.

## Semantic readiness

`semantic_readiness_metrics(state)` combines every M1–M4 **non-approval** blocking metric. It must include at least:

```text
open_material_surfaces
unbound_material_surfaces
unresolved_material_contradictions
stale_consumed_evidence
discovery_baseline_gaps
unassessed_materiality
open_material_unknowns
blocked_material_unknowns
unresolved_unknown_provenance
invalid_resolution_authority
unauthorized_agent_decisions
missing_required_user_decisions
active_grill_pack_gaps
unresolved_pack_axes
umbrella_unknown_compression
pack_materiality_floor_violations
invalid_authority_binding
stale_authority_binding
coverage_without_authority
open_coverage_without_unknown
unjustified_na_without_basis
invalid_coverage_authority_type
core_coverage_gaps
specialist_binding_gaps
ux_coverage_gaps
screen_state_gaps
screen_action_inventory_gaps
orphan_material_authority
unconsumed_material_decision
requirement_acceptance_gaps
task_mapping_gaps
```

Valid user-accepted `DEFERRED` unknowns are reported separately but are not blocking by count alone.

## Acceptance/task gate

Every CURRENT MATERIAL requirement must have:

- at least one CURRENT `AC-*` whose `requirement_refs` contains the requirement;
- at least one CURRENT `TASK-*` whose `implements` contains the requirement;
- that task must reference at least one CURRENT AC that belongs to that same requirement.

- [ ] **Step 1: Add graph/audit RED tests**

Cover direct and transitive examples:

```text
DEC → RULE → exact Coverage sink = consumed
REQ → AC → TASK = consumed
REQ with no AC/TASK = gap
material DEC with no sink path = unconsumed
RULE reachable from material DEC but not bound/otherwise delivered = orphan
historical source does not satisfy consumption
GOAL/USR do not false-positive as terminal roots
```

- [ ] **Step 2: Add acceptance/task RED tests**

Cover missing AC, missing task, task with wrong AC, historical AC/task and valid current mapping.

- [ ] **Step 3: Run Task 4 RED**

```bash
python -m unittest tests.test_authority_consumption_v020 -v
```

- [ ] **Step 4: Implement graph/readiness metrics**

Keep graph construction pure and deterministic. Sort only when rendering diagnostics; graph set order must never affect digests.

- [ ] **Step 5: Run Task 4 GREEN plus M1–M3 metric regressions**

```bash
python -m unittest \
  tests.test_authority_consumption_v020 \
  tests.test_unknown_resolution_v020 \
  tests.test_grill_packs_v020 \
  tests.test_discovery_baseline_v020 \
  tests.test_contradictions_v020 -v
```

- [ ] **Step 6: Commit**

```bash
git add skills/joewrks-product-definition/scripts/authority_binding_v2.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  tests/test_authority_consumption_v020.py
git commit -m "feat: audit semantic authority consumption"
```

---

# Task 5 — Semantic definition digest, informed Approval Manifest and history commitments

**Files:**
- Create: `skills/joewrks-product-definition/scripts/approval_v2.py`
- Create: `skills/joewrks-product-definition/scripts/build_approval_manifest.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/test_definition_digest_v020.py`
- Create: `tests/test_approval_manifest_v020.py`
- Modify: `tests/v020_support.py`
- Modify: `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`

**Interfaces:**

```python
def consumed_evidence_ids(state: dict[str, object]) -> list[str]: ...
def semantic_projection(state: dict[str, object]) -> dict[str, object]: ...
def definition_digest(state: dict[str, object]) -> str: ...
def semantic_record_hashes(state: dict[str, object]) -> dict[str, str]: ...
def build_approval_manifest(state: dict[str, object]) -> dict[str, object]: ...
def approval_manifest_digest(manifest: dict[str, object]) -> str: ...
def build_approval_commitment(state: dict[str, object], manifest: dict[str, object]) -> dict[str, object]: ...
def validate_approval(state: dict[str, object]) -> list[dict[str, str]]: ...
def approval_metrics(state: dict[str, object]) -> dict[str, int]: ...
```

## Consumed evidence boundary

Consumed evidence is determined from current semantic authority, including:

- CURRENT decisions’ `evidence_refs`;
- RESOLVED current-lifecycle unknowns’ `evidence_refs` where the resolution uses evidence/constraint provenance;
- non-historical surfaces’ `evidence_refs` used for current disposition/intent classification;
- non-historical/resolved contradictions’ claim and selected-authority evidence refs;
- Grill topology `basis_refs` that target EVD records;
- Core/specialist/UX N/A `basis_bindings` that target EVD records.

Unreferenced evidence is **not** part of the semantic definition digest or approval-manifest semantic record hashes.

## Semantic projection

The semantic definition digest includes:

```text
schema_version
project.slug
project.definition_revision
project.bootstrap_mode
project.closure_contract including binding contract IDs/versions/digests
current semantic product objects and current/resolved Product Definition authority
current surface manifest and Grill profile
resolved contradiction authority
exact Core coverage
exact specialist Grill coverage
exact UX coverage
semantic discovery-baseline commitment
consumed evidence records only
active Grill Pack IDs/versions/digests/target refs
```

It excludes:

```text
project.definition_status
current approval object
approval_history
unconsumed evidence
migration run-time metadata
operational timestamps/presentation metadata
```

### Discovery-baseline semantic projection

The M3 baseline intentionally hashes **all** evidence for discovery freshness. To preserve the M1/M4 semantic boundary, do **not** embed the full stored baseline object in `definition_digest`.

Project only these baseline fields:

```text
definition_revision
surface_manifest_digest
open_material_surface_count
unresolved_material_contradiction_count
procedure_complete
applicable_surface_classes_complete
active_grill_packs
active_grill_packs_complete
unknown_unknown_exhaustiveness_claimed
```

Explicitly exclude `evidence_commitment_digest` from the semantic projection; consumed evidence records are committed separately. This allows a newly discovered but unconsumed EVD record to make discovery baseline freshness change without silently changing approved product meaning.

Top-level record collections are deterministically sorted by stable ID. Coverage rows are sorted by their canonical target identity. Order **inside semantic record fields** is preserved unless the field is contractually an unordered set; do not globally sort lists such as flow paths.

## Approval object

Canonical unapproved state:

```json
{"status":"UNAPPROVED"}
```

Canonical approved state:

```json
{
  "status": "APPROVED",
  "approved_revision": 24,
  "approved_definition_digest": "<sha256>",
  "approved_manifest_digest": "<sha256>",
  "approved_at": "2026-08-29T00:00:00Z",
  "approved_by": "user"
}
```

`approved_at` must be provided by the approving workflow/user; M4 never synthesizes a wall-clock timestamp.

## Approval Manifest

Manifest schema identity:

```text
joewrks.approval-manifest/1.0
```

The compiler requires `project.definition_status = READY_FOR_REVIEW`, `approval.status = UNAPPROVED`, a CURRENT discovery baseline and all non-approval `semantic_readiness_metrics == 0`.

Manifest contains:

```text
schema_version
from_revision
to_revision
added
changed
superseded
retired
high_risk_decisions
deferred_non_blocking
active_grill_packs
binding_contracts
semantic_closure_summary
definition_digest
```

`added/changed/superseded/retired` are deterministic arrays of objects, not bare IDs:

```json
{
  "id": "REQ-001",
  "type": "REQ",
  "summary": "User can submit feedback."
}
```

Summary derivation is deterministic from the canonical semantic field for each type (`statement`, `question`, `name`, `purpose`, `assertion`, `state_name`, surface `name`, or evidence `claim`). It never uses an LLM-generated summary.

`high_risk_decisions` includes Decision ID, statement, reversibility and true risk-flag names. `deferred_non_blocking` includes unknown ID, question and deferral reason. This is required so the user sees material meaning, not only opaque IDs.

First approval uses `from_revision = null`. Later approvals compare against the greatest approval-history commitment with `revision < current revision`.

## Manifest digest and history commitment

`approval_manifest_digest()` hashes the manifest itself; the digest is not embedded into the manifest, preventing recursion.

`build_approval_manifest.py` emits:

```json
{
  "manifest": {...},
  "manifest_digest": "...",
  "approval_commitment": {...}
}
```

`approval_commitment` is:

```text
revision
definition_digest
manifest_digest
record_hashes
coverage_digest
surface_digest
grill_pack_set_digest
```

`record_hashes` covers semantic product records plus consumed EVD records, not unconsumed evidence. `coverage_digest` commits Core + specialist + UX exact coverage and active binding-contract identities.

An APPROVED current state must contain exactly one matching commitment for its own revision in `approval_history`. Previous commitments are immutable history; duplicate revision entries are invalid.

## Approval metrics

At least:

```text
missing_user_approval
stale_approval
missing_or_stale_approval_manifest
approval_history_gaps
```

- [ ] **Step 1: Add definition-digest RED tests**

Required invariants:

1. same semantic state → same digest;
2. top-level record reordering → same digest;
3. `READY_FOR_REVIEW` → `CLOSED` only → same digest;
4. approval object/history-only changes → same digest;
5. adding **unconsumed** evidence and rebuilding discovery baseline → same digest;
6. making that evidence consumed by current authority → digest changes;
7. changing consumed evidence claim/version/hash → digest changes;
8. changing exact authority binding/hash → digest changes;
9. changing active Grill Pack identity/digest/target set → digest changes;
10. binding-contract digest change → digest changes;
11. NaN/non-canonical values are rejected, not implementation-defined.

- [ ] **Step 2: Add Approval Manifest RED tests**

Cover first approval, later revision diff, deterministic summaries, added/changed/superseded/retired classification, high-risk Decision details, deferred unknown details, active pack/binding identities, manifest digest stability, and history commitment fields.

Verify unconsumed evidence addition does not appear as a semantic `added` change and does not change manifest/definition digest after baseline regeneration.

- [ ] **Step 3: Add approval validation RED tests**

Cover:

- APPROVED digest mismatch;
- wrong revision;
- wrong manifest digest;
- missing/duplicate current history commitment;
- altered record hash commitment;
- `approved_by != user`;
- fabricated/empty approved_at;
- UNAPPROVED with fabricated approval fields;
- previous history does not satisfy current approval.

- [ ] **Step 4: Run Task 5 RED**

```bash
python -m unittest tests.test_definition_digest_v020 tests.test_approval_manifest_v020 -v
```

- [ ] **Step 5: Implement pure approval/digest functions**

`approval_v2.py` must not import `state_validation_v2`. It may import pure M4/M3 modules such as `authority_binding_v2`, `materiality_v2` and `grill_v2` when no cycle results.

- [ ] **Step 6: Implement read-only manifest CLI**

Command:

```text
python skills/joewrks-product-definition/scripts/build_approval_manifest.py STATE_JSON
```

It imports `semantic_readiness_metrics` through the public validation layer, refuses invalid/not-ready input, prints deterministic compact JSON, and never edits state or fabricates approval time.

- [ ] **Step 7: Tighten approval/history schema and shared template**

The M4 default template remains `OPEN + UNAPPROVED + approval_history=[]`. It is valid state but not closed.

- [ ] **Step 8: Run Task 5 GREEN plus M1–M3 regressions**

```bash
python -m unittest \
  tests.test_definition_digest_v020 \
  tests.test_approval_manifest_v020 \
  tests.test_discovery_baseline_v020 \
  tests.test_unknown_resolution_v020 \
  tests.test_grill_baseline_v020 -v
```

- [ ] **Step 9: Commit**

```bash
git add skills/joewrks-product-definition/scripts/approval_v2.py \
  skills/joewrks-product-definition/scripts/build_approval_manifest.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/templates/state-v0.2.0.example.json \
  tests/v020_support.py tests/test_definition_digest_v020.py \
  tests/test_approval_manifest_v020.py
git commit -m "feat: add informed semantic approval commitments"
```

---

# Task 6 — Enable actual V2 Semantic Closure and freeze M4 contract

**Files:**
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/test_semantic_closure_v020.py`
- Create: `skills/joewrks-product-definition/references/semantic-freeze-contract-v0.2.0.md`
- Modify: `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- Modify: `skills/joewrks-product-definition/references/grill-contract-v0.2.0.md`
- Modify: `tests/test_skill_package.py` only for explicit new sibling modules/resources.
- Modify earlier tests that assert the M1–M3 `semantic_closure_not_implemented` guard.

**Interfaces:**

`evaluate_closure_v2(state)` becomes the actual Product Definition Semantic Closure evaluator.

## Final M4 Closure rule

`closed` is true **iff** all are true:

```text
validate_state_v2(state) returns no errors
project.definition_status == CLOSED
approval.status == APPROVED
approved_revision == project.definition_revision
approved_definition_digest == definition_digest(state)
approved_manifest_digest == deterministic current manifest digest
matching current approval_history commitment exists
all blocking M1–M4 Closure metrics == 0
```

The M1–M3 metric:

```text
semantic_closure_not_implemented
```

is removed in M4. Do not replace it with another fake blocker.

### Definition status discipline

- `OPEN` → `approval.status` must be `UNAPPROVED`.
- `BLOCKED` → `UNAPPROVED`.
- `READY_FOR_REVIEW` → `UNAPPROVED`; all non-approval semantic-readiness metrics must be zero before `build_approval_manifest.py` accepts it.
- `CLOSED` → `APPROVED` and exact approval/history commitments required.

Changing product meaning after approval causes digest/manifest mismatch and closure fails until revision/approval lifecycle is reconciled.

## Final blocking metrics

Expose all inherited M1–M3 metrics plus M4 metrics. `closed` uses an explicit frozen set of blocking metric names rather than “every integer metric”, because valid deferred counts and informational metrics may be non-zero.

At minimum informational/non-blocking metrics include valid `deferred_unknowns`. Every metric listed under Task 4 `semantic_readiness_metrics` plus all approval metrics is blocking.

## Minimum semantic definition

M4 Closure also requires:

- at least one CURRENT GOAL;
- at least one CURRENT recomputed-MATERIAL REQ;
- each current material requirement passes Core coverage, surface, acceptance/task, Grill and UX requirements applicable to its authority graph;
- CURRENT discovery baseline with `procedure_complete = true`, `applicable_surface_classes_complete = true`, `active_grill_packs_complete = true`, and `unknown_unknown_exhaustiveness_claimed = false`.

Add metrics `minimum_definition_gaps` and `discovery_procedure_gaps` if they are not already represented by exact existing metrics.

- [ ] **Step 1: Build one literal fully semantic-closed state fixture**

Do not build expected bindings/approval by calling the production function under test. Test helpers may use low-level literal hash helper `sha256_json` only after independently specifying record/pointer/value, and approval expected values must be checked against literal semantic mutations in separate tests.

The fixture includes at least:

```text
GOAL
USR
MATERIAL REQ
RULE/FLOW/SCR/STATE/DATA/INT as needed
AC
TASK
complete Surface/Grill profile
CURRENT discovery baseline
20 exact Core cells
16 exact UX state cells
exact action rows for declared major actions
all activated specialist axes ADDRESSED or justified N/A
zero material OPEN unknown/contradiction
READY_FOR_REVIEW manifest generation phase
then literal APPROVED/CLOSED phase
```

- [ ] **Step 2: Add Closure RED tests**

Prove the complete state can become closed only after manifest/user approval. Individually break:

- one Core hash;
- one Core authority type;
- one OPEN cell unknown;
- one N/A basis;
- one UX state/action binding;
- one specialist binding;
- one material unknown;
- one material contradiction;
- one discovery baseline commitment;
- one active pack digest;
- one material Decision consumption path;
- acceptance/task mapping;
- definition digest;
- manifest digest;
- approval revision;
- history commitment;
- definition status.

Each mutation must make `closed == false` for the expected blocker/error class.

- [ ] **Step 3: Add explicit unconsumed-evidence approval-stability regression**

Start from an APPROVED/CLOSED state. Add a new CURRENT EVD record that is referenced nowhere, rebuild the discovery baseline, and assert:

```text
definition_digest unchanged
approval manifest digest unchanged
approval remains valid
closed remains true
```

Then consume the EVD in current semantic authority and prove approval becomes stale/closed false.

- [ ] **Step 4: Run Task 6 RED**

```bash
python -m unittest tests.test_semantic_closure_v020 -v
```

Expected: FAIL while the M3 guard still hard-codes `closed = false`.

- [ ] **Step 5: Replace M3 guard with actual Closure evaluator**

Do not enable closure until all Task 1–5 validators/metrics are wired. The evaluator returns current `definition_digest` when it can be computed, including for unapproved READY_FOR_REVIEW states; invalid structural states may use `definition_digest: null` only when deterministic semantic projection cannot safely be formed.

- [ ] **Step 6: Write M4 semantic-freeze reference**

The reference must include literal markers:

```text
SEMANTIC_FREEZE_IMPLEMENTED_M4
EXACT_COVERAGE_BINDING_REQUIRED
EXACT_UX_BINDING_REQUIRED
COVERED_IS_PROOF_NOT_CHECKBOX
UNCONSUMED_EVIDENCE_DOES_NOT_INVALIDATE_APPROVAL
INFORMED_APPROVAL_MANIFEST_REQUIRED
SEMANTIC_CLOSURE_AVAILABLE_M4
DOWNSTREAM_V2_NOT_IMPLEMENTED_IN_M4
```

Explain in plain language that M4 is the first milestone where Product Definition itself can legitimately be `CLOSED`; this still does not mean implementation/design/deployment is complete or downstream semantic-review/2.0 is measured.

- [ ] **Step 7: Run all M4-focused tests**

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

- [ ] **Step 8: Run M3 regression**

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

- [ ] **Step 9: Run legacy regression and full repository suite**

```bash
python -m unittest tests.test_validators tests.test_semantic_v012 -v
python -m unittest discover -s tests -v
git diff --check
```

Expected: exit `0`; no new skip is allowed. Existing environment-dependent pinned-runtime skip may remain only with unchanged reason.

- [ ] **Step 10: Verify protected scope**

Require zero diff under:

```text
skills/joewrks-product-definition/downstream/
evals/semantic-review-v0.4.3/
skills/joewrks-product-definition/schemas/state.schema.json
skills/joewrks-product-definition/scripts/state_validation.py
skills/joewrks-product-definition/references/state-contract.md
skills/joewrks-product-definition/templates/state.example.json
```

Verify `main` remains unchanged and M5/M6 have not started.

- [ ] **Step 11: Commit**

```bash
git add skills/joewrks-product-definition/references/semantic-freeze-contract-v0.2.0.md \
  skills/joewrks-product-definition/references/state-contract-v0.2.0.md \
  skills/joewrks-product-definition/references/grill-contract-v0.2.0.md \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  tests/test_semantic_closure_v020.py tests/test_skill_package.py
git commit -m "feat: enable state 0.2 semantic closure"
```

- [ ] **Step 12: Report M4 precisely**

Only after every M4 gate passes, report:

```text
CORE_SEMANTIC_CLOSURE_V2_M4_IMPLEMENTED
— SEMANTIC_FREEZE / SEMANTIC_CLOSURE_AVAILABLE / NOT_INTEGRATED
```

Include implementation branch/base/HEAD/tree/remote SHA, task commits, changed files, focused/M3/legacy/full results, skips, `git diff --check`, frozen legacy verification, binding contract identities/digests, exact Coverage/UX/Grill metrics, authority-consumption metrics, definition/manifest digest probes, unconsumed-evidence approval-stability probe, actual closed-state probe, and confirmation M5–M6 were not started.

---

## M4 Plan Self-Review Mapping

| Frozen design requirement | M4 task |
| --- | --- |
| `COVERED` requires exact canonical authority | Tasks 1–2 |
| OPEN requires unknown | Tasks 2–3 |
| N/A requires rationale + exact basis | Tasks 2–3 |
| Core axis authority-type contract | Task 1–2 |
| UX Coverage exact binding | Task 3 |
| Specialist Grill exact semantic proof | Task 2 |
| binding hashes detect stale authority | Tasks 1–3 |
| Coverage → Authority and Authority → consumption | Task 4 |
| per-material-requirement semantic readiness | Tasks 2–4 |
| informed Approval Manifest | Task 5 |
| dual definition/manifest digest approval | Task 5–6 |
| approval history commitments | Task 5 |
| unconsumed evidence does not invalidate approval | Tasks 5–6 |
| binding contract identities are approval-bound | Tasks 1 and 5 |
| V2 Product Definition Semantic Closure | Task 6 |
| downstream v1/v0.4.3 remain frozen | Global constraints + Task 6 gate |
| M5 downstream V2 not silently implemented | Global constraints + Task 6 docs |

M4 intentionally leaves downstream `DIRECT_AUTHORITY / MACHINE_DERIVED / REVIEW_REQUIRED`, semantic debt, action-conformance/2.0, semantic-review/2.0 and implementation ambiguity re-entry protocol execution to M5. M6 remains adoption/migration/dogfood integration.
