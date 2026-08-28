# Core Semantic Closure V2 — M3 Grill Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Grill Engine V2 so materiality is deterministically classified, unknowns and decisions have auditable resolution provenance, AI autonomy is constrained by policy, user interruption is limited to the highest-leverage human decision, and topology-triggered Grill Packs activate automatically without claiming Semantic Closure.

**Architecture:** Extend state `0.2.0` on top of M2 instead of introducing a second authority store. Keep `state_validation_v2.py` as the public V2 validation entrypoint, but move new M3 policy logic into focused `materiality_v2.py` and `grill_v2.py` modules so the validator does not become the policy engine. M3 may strengthen unknown/decision and discovery-baseline shapes and add specialist `grill_coverage`, but M4 still owns exact Coverage→Authority pointer/hash binding, UX binding, informed approval, and the semantic definition digest.

**Tech Stack:** Python 3 standard library, JSON, Draft 2020-12 JSON Schema documents, SHA-256 canonical JSON pack commitments, `unittest`.

**Spec:**
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md` — especially sections 13–20
- `docs/superpowers/audits/2026-08-29-core-semantic-closure-v2-m2-source-audit.md`

## Global Constraints

- Implement from an isolated branch/worktree based on the exact M3 planning HEAD; that planning branch must descend from M2 HEAD `0b69af3f302df3406b8e3d540549945873eced0b`.
- Preserve the frozen legacy `0.1.2.1` files byte-for-byte.
- Preserve `skills/joewrks-product-definition/downstream/` and `evals/semantic-review-v0.4.3/` unchanged.
- Preserve `joewrks.action-conformance/1.0` and `joewrks.semantic-review/1.0` unchanged.
- Keep V2 `schema_version` at `0.2.0`.
- Preserve all M2 Evidence/Surface/Contradiction/reverse-bootstrap authority boundaries.
- `INFERRED_INTENT` and `DESIGN_ARTIFACT` remain candidate-only for closure authority.
- M3 must not implement exact product/UX Coverage→Authority pointer/hash binding, Approval Manifest, V2 semantic definition digest, downstream 2.0, or semantic-review 2.0. Those remain M4–M5.
- M3 may require broad current authority refs for Grill-axis `ADDRESSED`/`N/A`; these are not M4 semantic coverage proofs.
- Keep the V2 Closure guard throughout M3:
  - `closed = false`
  - `definition_digest = null`
  - `semantic_closure_not_implemented = 1`
- Discovery never claims universal unknown-unknown exhaustiveness; `unknown_unknown_exhaustiveness_claimed` remains `false`.
- Question wording is a projection. Canonical state stores the decision problem, evidence, options, recommendation, consequences, resolution, and provenance; the CLI must not invent new product meaning.
- Every behavior-changing code task follows RED → GREEN → refactor.
- Strongest successful milestone label: `IMPLEMENTED_M3 / NOT_INTEGRATED`.

---

## File Map

### Create M3 policy/runtime modules

- `skills/joewrks-product-definition/scripts/materiality_v2.py`
  - deterministic Materiality classification and high-risk predicate only.
- `skills/joewrks-product-definition/scripts/grill_v2.py`
  - decision-authority derivation, unknown/decision integrity helpers, question ranking/projection, Grill Pack loading/activation/coverage metrics.
- `skills/joewrks-product-definition/scripts/next_product_question.py`
  - read-only deterministic CLI returning at most one user question projection.

### Create declarative Grill Pack contracts

- `skills/joewrks-product-definition/references/grill-packs/grill-pack.schema.json`
- `skills/joewrks-product-definition/references/grill-packs/core.json`
- `skills/joewrks-product-definition/references/grill-packs/auth.json`
- `skills/joewrks-product-definition/references/grill-packs/money.json`
- `skills/joewrks-product-definition/references/grill-packs/file-upload.json`
- `skills/joewrks-product-definition/references/grill-packs/async.json`
- `skills/joewrks-product-definition/references/grill-packs/permission.json`
- `skills/joewrks-product-definition/references/grill-packs/destructive-action.json`
- `skills/joewrks-product-definition/references/grill-contract-v0.2.0.md`

### Modify canonical V2 contract/runtime

- `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- `skills/joewrks-product-definition/scripts/discovery_v2.py`
- `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- `skills/joewrks-product-definition/references/discovery-contract-v0.2.0.md`
- `tests/v020_support.py`

### Create M3 tests

- `tests/test_materiality_v020.py`
- `tests/test_unknown_resolution_v020.py`
- `tests/test_autonomy_policy_v020.py`
- `tests/test_question_policy_v020.py`
- `tests/test_grill_packs_v020.py`
- `tests/test_grill_baseline_v020.py`

### Existing M2 tests that may require fixture-shape updates only

- `tests/test_surface_manifest_v020.py`
- `tests/test_reverse_bootstrap_v020.py`
- `tests/test_contradictions_v020.py`
- `tests/test_discovery_baseline_v020.py`
- `tests/test_state_v020_foundation.py`
- `tests/test_skill_package.py`

Do not weaken existing assertions to make M3 pass. Update only literal fixture shapes when M3 makes a new canonical field mandatory.

---

# Task 1 — Deterministic Materiality classification

**Files:**
- Create: `skills/joewrks-product-definition/scripts/materiality_v2.py`
- Create: `tests/test_materiality_v020.py`
- Modify: `tests/v020_support.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`

**Interfaces:**

```python
def classify_materiality(materiality: dict[str, object]) -> str: ...
def is_high_risk(materiality: dict[str, object]) -> bool: ...
def validate_materiality_classification(materiality: dict[str, object]) -> bool: ...
```

`classify_materiality()` returns only `MATERIAL` or `NON_MATERIAL`.

## Frozen classification rule

`NON_MATERIAL` is permitted **only** when all are true:

```text
outcome_divergence ∈ {NONE, LOW}
fan_out = LOCAL
reversibility = TRIVIALLY_REVERSIBLE
all risk_flags = false
```

Every other valid Materiality shape is `MATERIAL`.

`user_visible` does not change Materiality classification by itself; it changes the later autonomy boundary.

`is_high_risk()` returns true when any risk flag is true or reversibility is `COSTLY_TO_REVERSE`/`IRREVERSIBLE`.

- [ ] **Step 1: Fix the shared test builder so declared classification matches inputs**

Change `tests/v020_support.py::materiality()` to return two deterministic profiles:

```python
def materiality(*, classification="NON_MATERIAL", user_visible=False):
    if classification == "NON_MATERIAL":
        return {
            "outcome_divergence": "LOW",
            "fan_out": "LOCAL",
            "user_visible": user_visible,
            "reversibility": "TRIVIALLY_REVERSIBLE",
            "risk_flags": {
                "security": False, "privacy": False, "money": False,
                "legal_or_policy": False, "destructive": False,
                "data_loss": False, "external_commitment": False,
            },
            "classification": "NON_MATERIAL",
        }
    if classification == "MATERIAL":
        return {
            "outcome_divergence": "MEDIUM",
            "fan_out": "MULTI_OBJECT",
            "user_visible": True,
            "reversibility": "REVERSIBLE",
            "risk_flags": {
                "security": False, "privacy": False, "money": False,
                "legal_or_policy": False, "destructive": False,
                "data_loss": False, "external_commitment": False,
            },
            "classification": "MATERIAL",
        }
    raise ValueError(classification)
```

Update existing test-local materiality literals only where required so pre-M3 tests express the same intended class under the frozen rule.

- [ ] **Step 2: Add RED classifier tests**

Create `tests/test_materiality_v020.py` covering every boundary:

```text
NONE + LOCAL + TRIVIAL + no risk      → NON_MATERIAL
LOW + LOCAL + TRIVIAL + no risk       → NON_MATERIAL
MEDIUM outcome                         → MATERIAL
HIGH outcome                           → MATERIAL
MULTI_OBJECT fan-out                   → MATERIAL
MULTI_FLOW fan-out                     → MATERIAL
SYSTEMIC fan-out                       → MATERIAL
REVERSIBLE instead of TRIVIAL          → MATERIAL
COSTLY_TO_REVERSE                      → MATERIAL + high risk
IRREVERSIBLE                           → MATERIAL + high risk
any individual risk flag true          → MATERIAL + high risk
user_visible true with otherwise low/local/trivial/no-risk → NON_MATERIAL
```

Also prove that an explicit `classification` that disagrees with recomputation is rejected.

- [ ] **Step 3: Run Task 1 tests RED**

```bash
python -m unittest tests.test_materiality_v020 -v
```

Expected: FAIL because classification is still trusted rather than recomputed.

- [ ] **Step 4: Implement `materiality_v2.py`**

Do not import `state_validation_v2`; this module must remain a pure policy dependency.

- [ ] **Step 5: Enforce recomputation for every canonical Materiality-bearing record**

In `state_validation_v2.py`, after shape validation, call `validate_materiality_classification()` for Materiality on:

```text
REQ
UNK
DEC
SURF
CON
```

Emit stable error code:

```text
materiality_classification_mismatch
```

Do not change the M2 evidence contract.

- [ ] **Step 6: Run Task 1 GREEN plus M2 regression**

```bash
python -m unittest \
  tests.test_materiality_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_reverse_bootstrap_v020 \
  tests.test_contradictions_v020 \
  tests.test_discovery_baseline_v020 \
  tests.test_state_v020_foundation -v
```

Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add skills/joewrks-product-definition/scripts/materiality_v2.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  tests/v020_support.py tests/test_materiality_v020.py \
  tests/test_surface_manifest_v020.py tests/test_reverse_bootstrap_v020.py \
  tests/test_contradictions_v020.py tests/test_discovery_baseline_v020.py
git commit -m "feat: enforce deterministic materiality classification"
```

---

# Task 2 — Unknown and Decision resolution provenance

**Files:**
- Create: `skills/joewrks-product-definition/scripts/grill_v2.py`
- Create: `tests/test_unknown_resolution_v020.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `tests/v020_support.py`
- Modify existing M2 tests that construct `UNK-*`/`DEC-*` literals.

**Interfaces:**

```python
def validate_unknown_decision_integrity(
    state: dict[str, object],
    *,
    id_index: dict[str, tuple[str, dict[str, object]]],
    evidence_index: dict[str, dict[str, object]],
) -> list[dict[str, str]]: ...

def grill_unknown_metrics(state: dict[str, object]) -> dict[str, int]: ...
```

## Canonical M3 unknown shape

Every `UNK-*` retains `id`, `status`, `question`, `materiality`, `decision_authority` and additionally requires these keys:

```text
why_it_matters
required_authority_class
question_category
affects
blocks_unknown_refs
origin
response_mode
options
recommendation
evidence_refs
resolved_by
resolution_mode
resolution_summary
deferral
blocked_reason
```

Nullable fields are still required keys so the contract does not drift by omission.

### `required_authority_class`

One of:

```text
FACTUAL
INTENT
CONSTRAINT
BEHAVIORAL
PREFERENCE
```

### `question_category`

One of:

```text
CORE_FLOW
SCOPE_BOUNDARY
STATE_RECOVERY
SECONDARY_BEHAVIOR
PREFERENCE
COSMETIC
```

### `origin`

Exact shape:

```json
{
  "kind": "PRODUCT_SURFACE | GRILL_PACK_AXIS | MIGRATION_RECONCILIATION | MANUAL",
  "surface_ref": null,
  "pack_id": null,
  "axis_id": null
}
```

Rules:

- `PRODUCT_SURFACE` requires `surface_ref: SURF-*` and null `pack_id/axis_id`.
- `GRILL_PACK_AXIS` requires `surface_ref`, `pack_id`, and `axis_id`.
- `MIGRATION_RECONCILIATION` and `MANUAL` require all three locator fields null.

### Response/options

`response_mode` is:

```text
MUTUALLY_EXCLUSIVE
OPEN_RESPONSE_REQUIRED
```

For mutually exclusive responses, `options` has at least two unique option objects:

```json
{
  "id": "OPT-A",
  "statement": "Allow immediate reuse.",
  "consequences": ["The old identifier can be reclaimed immediately."]
}
```

`OPEN_RESPONSE_REQUIRED` requires `options: []`.

### Resolution fields

- unresolved statuses use `resolution_mode: null`, `resolution_summary: null`, `resolved_by: []`;
- `RESOLVED` requires meaningful `resolution_summary` and a valid resolution mode;
- `MIGRATION_RECONCILIATION` is never accepted as a completed `RESOLVED` mode in M3; it remains a reconciliation gap until replaced by actual evidence/user/external/agent authority.

### Deferred unknown

`DEFERRED` requires:

```json
{
  "deferral": {
    "reason": "...",
    "accepted_by": "user",
    "impact_review": {
      "scope": "...",
      "rules": "...",
      "flows": "...",
      "states": "...",
      "privacy": "...",
      "money": "...",
      "security": "...",
      "acceptance": "..."
    }
  }
}
```

All eight impact strings must be meaningful. A valid deferral is an explicit disposition; an invalid one is a blocker.

`BLOCKED` requires a meaningful `blocked_reason`.

## Canonical M3 Decision extension

Every `DEC-*` additionally requires:

```text
decided_by
accepted_recommendation
```

`decided_by` is `USER | AGENT | EXTERNAL_AUTHORITY`.

`accepted_recommendation` is null except for `USER_ACCEPTED_RECOMMENDATION`, where it is:

```json
{
  "recommended_option": "OPT-B",
  "alternatives_presented": ["OPT-A", "OPT-B", "OPT-C"],
  "tradeoffs_presented": ["..."],
  "accepted_by": "user",
  "accepted_at": null
}
```

`accepted_at` may be null in M3; no wall-clock value is synthesized.

- [ ] **Step 1: Add canonical unknown/decision builders to `tests/v020_support.py`**

Create `unknown_record()` and `decision_record()` helpers using the complete shapes above. Replace local M2 helpers with these shared builders where practical; otherwise add the same mandatory fields without changing test meaning.

- [ ] **Step 2: Add RED unknown lifecycle/resolution tests**

Required cases:

1. every new required unknown field is structurally mandatory;
2. malformed origin/option/deferral fields fail;
3. OPEN cannot carry a resolution;
4. RESOLVED+EVIDENCE requires current closure-eligible evidence supporting `required_authority_class` and no decision ref;
5. RESOLVED+EXTERNAL_CONSTRAINT requires current closure-eligible `CONSTRAINT` evidence;
6. RESOLVED+USER_DECISION requires exactly one current `DEC-*` whose `source_unknown_refs` includes that unknown and whose mode matches;
7. RESOLVED+USER_ACCEPTED_RECOMMENDATION requires the same plus recommendation acceptance provenance;
8. RESOLVED+AGENT_NON_MATERIAL_DEFAULT requires the same plus `decided_by=AGENT`;
9. RESOLVED+MIGRATION_RECONCILIATION fails `unresolved_unknown_provenance`;
10. DEFERRED without full user-accepted eight-axis impact review fails;
11. BLOCKED without meaningful reason fails;
12. material OPEN/BLOCKED unknowns count in blocker metrics; valid DEFERRED does not count as open but remains separately reportable.

- [ ] **Step 3: Add RED decision provenance tests**

Require:

- every current decision has at least one `source_unknown_refs` entry;
- every source unknown exists;
- resolution mode and decision authority match the source unknown;
- `USER_DECISION`/`USER_ACCEPTED_RECOMMENDATION` require `decided_by=USER`;
- `AGENT_NON_MATERIAL_DEFAULT` requires `decided_by=AGENT`;
- `EXTERNAL_CONSTRAINT` decision, when used, requires `decided_by=EXTERNAL_AUTHORITY` and qualifying constraint evidence;
- material decisions may not use `AGENT_NON_MATERIAL_DEFAULT`;
- `EVIDENCE` and `MIGRATION_RECONCILIATION` are not valid current Decision resolution modes because evidence-only resolution does not require a DEC and migration reconciliation is not resolution.

- [ ] **Step 4: Run Task 2 RED**

```bash
python -m unittest tests.test_unknown_resolution_v020 -v
```

Expected: FAIL before M3 provenance validation exists.

- [ ] **Step 5: Tighten schema Unknown/Decision definitions and implement validation in `grill_v2.py`**

`state_validation_v2.validate_state_v2()` calls `validate_unknown_decision_integrity()` after M1/M2 ID/evidence/surface/contradiction validation.

Keep all errors in `{code, message, path}` shape. Required stable error codes include:

```text
invalid_unknown_contract
unresolved_unknown_provenance
invalid_unknown_resolution_authority
invalid_unknown_deferral
invalid_unknown_block
invalid_decision_provenance
unauthorized_agent_decision
invalid_recommendation_acceptance
```

- [ ] **Step 6: Extend Closure metrics but keep Closure blocked**

`evaluate_closure_v2` additionally emits:

```text
open_material_unknowns
unresolved_unknown_provenance
invalid_resolution_authority
unauthorized_agent_decisions
missing_required_user_decisions
```

Do not remove `semantic_closure_not_implemented = 1`.

- [ ] **Step 7: Run Task 2 GREEN plus M2 regression**

```bash
python -m unittest \
  tests.test_unknown_resolution_v020 \
  tests.test_reverse_bootstrap_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_contradictions_v020 \
  tests.test_evidence_v020 -v
```

Expected: `OK`.

- [ ] **Step 8: Commit**

```bash
git add skills/joewrks-product-definition/scripts/grill_v2.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  tests/v020_support.py tests/test_unknown_resolution_v020.py \
  tests/test_reverse_bootstrap_v020.py tests/test_surface_manifest_v020.py \
  tests/test_contradictions_v020.py
git commit -m "feat: enforce unknown decision resolution provenance"
```

---

# Task 3 — Deterministic autonomy policy and structured recommendations

**Files:**
- Create: `tests/test_autonomy_policy_v020.py`
- Modify: `skills/joewrks-product-definition/scripts/grill_v2.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`

**Interfaces:**

```python
def derive_decision_authority(
    unknown: dict[str, object],
    *,
    evidence_index: dict[str, dict[str, object]],
) -> str: ...

def recommendation_is_confirmation_ready(unknown: dict[str, object]) -> bool: ...
```

## Frozen authority derivation order

1. If one of `unknown.evidence_refs` is current closure-eligible evidence supporting `required_authority_class` → `EVIDENCE_RESOLVABLE`.
2. If `required_authority_class` is `FACTUAL`, `CONSTRAINT`, or `BEHAVIORAL` and no qualifying evidence exists → `EXTERNAL_AUTHORITY_REQUIRED`.
3. If Materiality is `NON_MATERIAL`, `user_visible=false`, and reversibility is `TRIVIALLY_REVERSIBLE` → `AGENT_AUTONOMOUS`.
4. If Materiality is high-risk → `USER_DECISION_REQUIRED`.
5. If a structurally valid high-confidence recommendation is confirmation-ready → `USER_CONFIRMATION`.
6. Otherwise → `USER_DECISION_REQUIRED`.

A user-visible non-material choice is therefore not silently agent-autonomous; it becomes `USER_CONFIRMATION` only when a valid recommendation exists, otherwise `USER_DECISION_REQUIRED`.

## Recommendation contract

`recommendation` is null or:

```json
{
  "recommended_option": "OPT-B",
  "reasoning_refs": ["EVD-001"],
  "tradeoffs": ["Simpler recovery path", "Slightly more state handling"],
  "confidence": "HIGH"
}
```

Rules:

- `recommended_option` must be one of the unknown option IDs;
- `reasoning_refs` is non-empty, unique, and each ref resolves to current evidence or current canonical product authority;
- `tradeoffs` is non-empty meaningful text;
- confidence is `LOW | MEDIUM | HIGH`;
- confirmation-ready requires `response_mode=MUTUALLY_EXCLUSIVE`, at least two options, and `confidence=HIGH`.

`USER_CONFIRMATION` requires a confirmation-ready recommendation. `USER_DECISION_REQUIRED` may have a recommendation but does not require one.

- [ ] **Step 1: Add RED policy table tests**

Use one literal case for every authority branch and prove ordering:

```text
qualifying evidence beats every later branch;
factual/constraint/behavioral without evidence → EXTERNAL;
non-material + invisible + trivial → AGENT;
non-material + visible + high-confidence recommendation → USER_CONFIRMATION;
non-material + visible + no ready recommendation → USER_DECISION_REQUIRED;
material high-risk + high-confidence recommendation → USER_DECISION_REQUIRED;
material non-high-risk + ready recommendation → USER_CONFIRMATION;
material non-high-risk + no ready recommendation → USER_DECISION_REQUIRED.
```

- [ ] **Step 2: Add RED recommendation integrity tests**

Reject recommendation pointing to a nonexistent option, empty reasoning/tradeoffs, stale/candidate-only evidence as sole closure reasoning when intent is required, invalid confidence, and accepted recommendation provenance that does not reproduce the option set shown to the user.

- [ ] **Step 3: Add RED anti-silent-decision tests**

Prove:

- `MATERIAL + AGENT_NON_MATERIAL_DEFAULT` fails;
- any high-risk unknown declared `AGENT_AUTONOMOUS` fails;
- derived authority must exactly equal canonical `unknown.decision_authority`;
- changing materiality/evidence/recommendation so derived authority changes makes the state invalid until the unknown is updated;
- an agent cannot self-mark a user-confirmation decision as accepted.

- [ ] **Step 4: Run Task 3 RED**

```bash
python -m unittest tests.test_autonomy_policy_v020 -v
```

Expected: FAIL before policy derivation is enforced.

- [ ] **Step 5: Implement and wire the authority policy**

Add error code `invalid_decision_authority_derivation` when the canonical class disagrees with deterministic derivation.

Do not silently mutate the state to the derived value. Validation reports the mismatch; the Product Definition workflow must record the change explicitly.

- [ ] **Step 6: Run Task 3 GREEN**

```bash
python -m unittest tests.test_autonomy_policy_v020 tests.test_unknown_resolution_v020 tests.test_materiality_v020 -v
```

Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add tests/test_autonomy_policy_v020.py \
  skills/joewrks-product-definition/scripts/grill_v2.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json
git commit -m "feat: enforce product decision autonomy policy"
```

---

# Task 4 — One-question-at-a-time selection and projection

**Files:**
- Create: `skills/joewrks-product-definition/scripts/next_product_question.py`
- Create: `tests/test_question_policy_v020.py`
- Modify: `skills/joewrks-product-definition/scripts/grill_v2.py`

**Interfaces:**

```python
def question_priority_key(unknown: dict[str, object]) -> tuple[object, ...]: ...
def select_next_user_question(state: dict[str, object]) -> dict[str, object] | None: ...
def project_user_question(unknown: dict[str, object]) -> dict[str, object]: ...
```

CLI:

```text
python skills/joewrks-product-definition/scripts/next_product_question.py STATE_JSON
```

It emits exactly one of:

```json
{"next_question": null}
```

or:

```json
{
  "next_question": {
    "unknown_id": "UNK-012",
    "question": "...",
    "why_it_matters": "...",
    "evidence_refs": [],
    "affected_ids": [],
    "response_mode": "MUTUALLY_EXCLUSIVE",
    "options": [],
    "recommendation": null
  }
}
```

The CLI is read-only and deterministic.

## Frozen ranking

Eligible unknowns are only `status=OPEN` and `decision_authority ∈ {USER_CONFIRMATION, USER_DECISION_REQUIRED}`.

Exclude `EVIDENCE_RESOLVABLE`, `AGENT_AUTONOMOUS`, `EXTERNAL_AUTHORITY_REQUIRED`, resolved, deferred, blocked, superseded, and retired unknowns.

Sort by this priority, in order:

1. more `blocks_unknown_refs` first;
2. high-risk before non-high-risk;
3. fan-out `SYSTEMIC > MULTI_FLOW > MULTI_OBJECT > LOCAL`;
4. category `CORE_FLOW > SCOPE_BOUNDARY > STATE_RECOVERY > SECONDARY_BEHAVIOR > PREFERENCE > COSMETIC`;
5. stable unknown ID ascending as deterministic tie-break.

- [ ] **Step 1: Add RED eligibility/ranking tests**

Build a state with at least nine OPEN unknowns spanning every authority/category and prove exactly one winner is returned under each ranking tie-break.

- [ ] **Step 2: Add RED projection tests**

The projection must be a pure subset/transform of canonical unknown data. Assert it does not add a new option, consequence, recommendation, or product statement absent from the state.

- [ ] **Step 3: Add RED CLI determinism/read-only tests**

Run twice on identical bytes and require byte-identical stdout. Hash source bytes before/after and require unchanged bytes. Invalid state exits `1` with validation errors; argument/read errors exit `2`.

- [ ] **Step 4: Run Task 4 RED**

```bash
python -m unittest tests.test_question_policy_v020 -v
```

Expected: FAIL before selector/CLI exists.

- [ ] **Step 5: Implement the selector and CLI**

The selector must call normal V2 validation first. It must not fix decision-authority mismatches or create questions automatically.

- [ ] **Step 6: Run Task 4 GREEN**

```bash
python -m unittest tests.test_question_policy_v020 tests.test_autonomy_policy_v020 -v
```

Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add skills/joewrks-product-definition/scripts/next_product_question.py \
  skills/joewrks-product-definition/scripts/grill_v2.py \
  tests/test_question_policy_v020.py
git commit -m "feat: select one high leverage product question"
```

---

# Task 5 — Adaptive Grill Packs and topology-triggered activation

**Files:**
- Create all `references/grill-packs/*` files listed in the File Map.
- Create: `tests/test_grill_packs_v020.py`
- Modify: `skills/joewrks-product-definition/scripts/grill_v2.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `tests/v020_support.py`

**Interfaces:**

```python
PACK_DIR: Path

def load_grill_packs(pack_dir: Path = PACK_DIR) -> dict[str, dict[str, object]]: ...
def canonical_pack_digest(pack: dict[str, object]) -> str: ...
def compile_active_grill_packs(state: dict[str, object]) -> list[dict[str, object]]: ...
def validate_grill_coverage(state: dict[str, object]) -> list[dict[str, str]]: ...
def grill_pack_metrics(state: dict[str, object]) -> dict[str, int]: ...
```

## Surface topology tags

Extend every `SURF-*` record with required `topology_tags`, a unique array containing zero or more of:

```text
AUTH
MONEY
FILE_UPLOAD
ASYNC
PERMISSION
DESTRUCTIVE_ACTION
```

Default test/native surface builder uses `[]`.

Automatic trigger mappings also exist for already-typed surface kinds:

```text
MONEY_FLOW            → MONEY
ASYNC_PROCESS          → ASYNC
PERMISSION             → PERMISSION
DESTRUCTIVE_OPERATION  → DESTRUCTIVE_ACTION
```

AUTH and FILE_UPLOAD require explicit topology tags because M2 surface kinds do not uniquely identify them.

## Pack schema

Every pack JSON uses:

```json
{
  "pack_id": "GRILL-AUTH-1",
  "version": "1.0",
  "activation": {
    "always": false,
    "surface_kinds": [],
    "topology_tags": ["AUTH"]
  },
  "axes": [
    {
      "id": "account_recovery",
      "description": "Account recovery policy and recovery failure behavior.",
      "independent_decision": true,
      "materiality_floor": "MATERIAL"
    }
  ]
}
```

Allowed `materiality_floor` is `INHERIT | MATERIAL`.

Pack digest is SHA-256 of canonical parsed JSON and is **not** stored inside the source JSON itself.

## Frozen pack identities and axes

### `GRILL-CORE-1@1.0`

Activation: `always=true`.

Axes exactly the existing 20 Core Grill dimensions:

```text
actor, goal, entry_point, precondition, happy_path, alternative_path,
error, recovery, permission, state, data, side_effect, notification,
validation, boundary, persistence, security, privacy, analytics, acceptance
```

Core axes use `materiality_floor=INHERIT`. Core Grill continues to use existing `coverage` rows as its storage; M3 does not duplicate those 20 cells into `grill_coverage` and does not add M4 exact authority bindings.

### `GRILL-AUTH-1@1.0`

```text
registration
verification
login
logout
session_expiry
session_renewal
password_reset
account_recovery
revocation
role_change
provider_failure
duplicate_identity
account_linking
```

Materiality floor `MATERIAL` for:

```text
session_expiry
password_reset
account_recovery
revocation
role_change
duplicate_identity
account_linking
```

others `INHERIT`.

### `GRILL-MONEY-1@1.0`

All axes `MATERIAL`:

```text
currency
price_authority
tax
discount
payment_failure
duplicate_payment
refund
partial_refund
cancellation
chargeback
settlement
receipt
```

### `GRILL-FILE-UPLOAD-1@1.0`

```text
type
size
quota
malware
processing
partial_failure
resume
retention
deletion
ownership
download_permission
```

Materiality floor `MATERIAL` for:

```text
malware
retention
deletion
ownership
download_permission
```

others `INHERIT`.

### `GRILL-ASYNC-1@1.0`

```text
pending
polling
timeout
retry
idempotency
duplicate_execution
late_completion
partial_completion
cancel
reconciliation
```

Materiality floor `MATERIAL` for:

```text
idempotency
duplicate_execution
partial_completion
reconciliation
```

others `INHERIT`.

### `GRILL-PERMISSION-1@1.0`

All axes `MATERIAL`:

```text
role
resource_ownership
read
write
delete
delegation
revocation
role_change_mid_flow
stale_permission
audit
```

### `GRILL-DESTRUCTIVE-ACTION-1@1.0`

All axes `MATERIAL`:

```text
confirmation
reason
undo
grace_period
dependency_effects
irreversible_boundary
audit
notification
```

## Specialist Grill coverage

Add new required top-level state section:

```json
"grill_coverage": []
```

Each specialist row is:

```json
{
  "target_ref": "SURF-001",
  "pack_id": "GRILL-AUTH-1",
  "pack_version": "1.0",
  "pack_digest": "<64 lowercase hex>",
  "axes": {
    "account_recovery": {
      "status": "OPEN",
      "authority_refs": [],
      "unknown_refs": ["UNK-021"],
      "basis_refs": [],
      "rationale": null
    }
  }
}
```

Axis statuses:

```text
ADDRESSED
OPEN
N/A
```

Rules:

- `ADDRESSED` requires at least one current canonical product authority ref. This is broad ID-level proof only; M4 will later require exact pointer/hash authority binding.
- `OPEN` requires one or more open unknown refs.
- `N/A` requires meaningful rationale plus at least one current basis ref.
- row axis keys must exactly equal the activated pack definition axes;
- `pack_version` and `pack_digest` must exactly match checked-in pack authority;
- one row per `(target_ref, pack_id)`; no duplicates.

For an axis with `independent_decision=true`, `OPEN` requires **exactly one** unknown whose origin is the same `GRILL_PACK_AXIS` target/pack/axis. The same unknown may not be reused as the origin unknown of another independent specialist axis. Emit `umbrella_unknown_compression` on violation.

For `materiality_floor=MATERIAL`, an OPEN axis's origin unknown must classify `MATERIAL`.

## Pack activation instances

`compile_active_grill_packs()` returns sorted instances shaped as:

```json
{
  "pack_id": "GRILL-AUTH-1",
  "version": "1.0",
  "digest": "...",
  "target_refs": ["SURF-001", "SURF-004"]
}
```

`GRILL-CORE-1` is always included; its `target_refs` are all current material `REQ-*` IDs, sorted.

Specialist targets are current, non-retired surfaces that match pack triggers. A surface may activate multiple specialist packs.

- [ ] **Step 1: Add RED pack-schema/identity tests**

Require all seven JSON files to validate against `grill-pack.schema.json`, have exact frozen identity/version/axis inventory, unique axis IDs, and deterministic lowercase-hex digests.

- [ ] **Step 2: Add RED trigger tests**

Prove every implicit kind mapping, every explicit topology tag, multiple-pack activation, no duplicate activation, and AUTH/FILE_UPLOAD not activating merely from vague `FEATURE_AREA` names.

- [ ] **Step 3: Add RED specialist coverage tests**

Cover missing row, wrong pack version/digest, missing/extra axis, invalid status payload, duplicate row, stale authority/basis, missing unknown, materiality-floor violation, and umbrella unknown compression.

- [ ] **Step 4: Add RED Core Grill activation tests**

For every current material requirement, `GRILL-CORE-1` requires exactly one existing product `coverage` row with the exact 20 core axis keys. Do not require M4 pointer/hash bindings in M3.

- [ ] **Step 5: Run Task 5 RED**

```bash
python -m unittest tests.test_grill_packs_v020 -v
```

Expected: FAIL before pack files/runtime/state section exist.

- [ ] **Step 6: Implement pack loading, activation, coverage validation, and metrics**

`grill_pack_metrics()` returns at least:

```text
active_grill_pack_gaps
unresolved_pack_axes
umbrella_unknown_compression
pack_materiality_floor_violations
```

`active_grill_pack_gaps` counts missing/mismatched required row/axis/pack identity. `unresolved_pack_axes` counts `OPEN` Core cells and specialist axes; it is independent from activation completeness.

- [ ] **Step 7: Extend state schema/root/template**

Add required root `grill_coverage` and update `ROOT_KEYS`, V2 template, test `foundation_state()`, schema/runtime parity assertions, and migration-plan tests only as necessary for the new V2 shape. Do not change legacy migration output into a V2 state.

- [ ] **Step 8: Run Task 5 GREEN plus all M2 regressions**

```bash
python -m unittest \
  tests.test_grill_packs_v020 \
  tests.test_question_policy_v020 \
  tests.test_autonomy_policy_v020 \
  tests.test_unknown_resolution_v020 \
  tests.test_evidence_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_contradictions_v020 \
  tests.test_reverse_bootstrap_v020 \
  tests.test_discovery_baseline_v020 -v
```

Expected: `OK`.

- [ ] **Step 9: Commit**

```bash
git add skills/joewrks-product-definition/references/grill-packs \
  skills/joewrks-product-definition/scripts/grill_v2.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/templates/state-v0.2.0.example.json \
  tests/v020_support.py tests/test_grill_packs_v020.py \
  tests/test_state_v020_foundation.py tests/test_migration_v020_foundation.py
git commit -m "feat: activate topology driven Grill Packs"
```

---

# Task 6 — Grill-aware discovery baseline, documentation, and M3 gate

**Files:**
- Create: `skills/joewrks-product-definition/references/grill-contract-v0.2.0.md`
- Create: `tests/test_grill_baseline_v020.py`
- Modify: `skills/joewrks-product-definition/scripts/discovery_v2.py`
- Modify: `skills/joewrks-product-definition/scripts/build_discovery_baseline.py` only if interface wiring is required; keep it read-only.
- Modify: `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- Modify: `skills/joewrks-product-definition/references/discovery-contract-v0.2.0.md`
- Modify: `tests/test_state_v020_foundation.py`
- Modify: `tests/test_skill_package.py`

**Interfaces:**

M3 discovery baseline keeps all M2 fields, but `active_grill_packs` now contains the deterministic output of `compile_active_grill_packs(state)` and `active_grill_packs_complete` becomes a computed boolean.

`active_grill_packs_complete` means **all required pack instances and axis inventories are instantiated with matching pack identity**. It does not mean all pack axes are resolved; `unresolved_pack_axes` is the separate metric.

- [ ] **Step 1: Add RED Grill-aware baseline tests**

Require:

1. identical state + identical pack files → byte-identical baseline;
2. adding a triggering topology tag changes active pack list and baseline bytes;
3. changing a checked-in pack JSON semantic value changes its digest and makes a stored baseline stale;
4. all required rows present with some OPEN axes → `active_grill_packs_complete=true` while `unresolved_pack_axes>0`;
5. missing/mismatched required pack row → `active_grill_packs_complete=false` and `active_grill_pack_gaps>0`;
6. `unknown_unknown_exhaustiveness_claimed=false` remains immutable;
7. stale baseline regeneration still bypasses only baseline freshness, not M3 materiality/unknown/autonomy/pack validation.

- [ ] **Step 2: Run Task 6 baseline tests RED**

```bash
python -m unittest tests.test_grill_baseline_v020 -v
```

Expected: FAIL while M2 baseline still hardcodes an empty pack set and false completeness.

- [ ] **Step 3: Update `discovery_v2.py`**

Import only pure pack compilation/metrics functions from `grill_v2`; do not create a circular import back to `state_validation_v2`.

Baseline's `active_grill_packs` is the sorted compiled list. Completeness is derived from `active_grill_pack_gaps == 0`.

Keep `unknown_unknown_exhaustiveness_claimed=False` hard-coded.

- [ ] **Step 4: Add final M3 closure metrics**

`evaluate_closure_v2` contains M1/M2 metrics plus:

```text
open_material_unknowns
unresolved_unknown_provenance
invalid_resolution_authority
unassessed_materiality
unauthorized_agent_decisions
missing_required_user_decisions
active_grill_pack_gaps
unresolved_pack_axes
umbrella_unknown_compression
pack_materiality_floor_violations
```

`unassessed_materiality` counts materiality-bearing records whose shape/classification is invalid; ordinary state validation also reports the precise error.

The Closure guard remains:

```text
semantic_closure_not_implemented = 1
closed = false
definition_digest = null
```

- [ ] **Step 5: Add RED documentation/package-boundary tests**

Require `grill-contract-v0.2.0.md`, pack schema/files, M3 runtime files, and exact documentation markers:

```text
GRILL_ENGINE_IMPLEMENTED_M3
INTERNALLY_EXHAUSTIVE_EXTERNALLY_SELECTIVE
MATERIALITY_CLASSIFICATION_ENFORCED
NO_SILENT_MATERIAL_AGENT_DECISIONS
ACTIVE_GRILL_PACKS_IMPLEMENTED_M3
UNKNOWN_UNKNOWN_EXHAUSTIVENESS_NOT_CLAIMED
SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M3
```

Package import policy may add only explicit sibling imports required by `materiality_v2` and `grill_v2`; hidden `__import__` remains forbidden.

- [ ] **Step 6: Write `grill-contract-v0.2.0.md`**

It must state plainly:

```text
- The system looks broadly for gray areas internally but does not ask the user every question it finds.
- Materiality is recomputed from its factors; classification is not trusted as a free boolean/label.
- Evidence-resolvable decisions are not asked of the user.
- Invisible, local, trivially reversible non-material decisions may be agent-autonomous.
- Material/high-risk product meaning may not be silently decided by the agent.
- A user-confirmation path requires a real recommendation with alternatives and tradeoffs.
- Unknown resolution records how the gray area was closed.
- Questions are projected from canonical state and one highest-leverage user question is selected at a time.
- Core Grill is always active; specialist Grill Packs activate from product topology, not agent discretion.
- Pack identity/version/digest are committed into the discovery baseline.
- M3 still does not provide exact semantic Coverage Binding or Semantic Closure.
```

Link this reference from `state-contract-v0.2.0.md` and update the M2 discovery contract to state that its former `ACTIVE_GRILL_PACKS_NOT_IMPLEMENTED_IN_M2` boundary is historical for M2 and superseded by the M3 Grill contract when operating at M3.

- [ ] **Step 7: Run all M3-focused tests**

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
  tests.test_discovery_baseline_v020 \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation \
  tests.test_state_contract_dispatch \
  tests.test_legacy_v0121_frozen -v
```

Expected: exit `0`.

- [ ] **Step 8: Run legacy regression**

```bash
python -m unittest tests.test_validators tests.test_semantic_v012 -v
```

Expected: exit `0`, with frozen legacy blob commitments unchanged.

- [ ] **Step 9: Run full suite and diff integrity**

```bash
python -m unittest discover -s tests -v
git diff --check
```

Expected: both exit `0`. No new skip is permitted; an existing environment-dependent skip may remain only with the same reason.

- [ ] **Step 10: Verify source scope**

Require zero M3 changes under:

```text
skills/joewrks-product-definition/downstream/
evals/semantic-review-v0.4.3/
skills/joewrks-product-definition/schemas/state.schema.json
skills/joewrks-product-definition/scripts/state_validation.py
skills/joewrks-product-definition/references/state-contract.md
skills/joewrks-product-definition/templates/state.example.json
```

Explicitly verify final runtime values on a valid M3 fixture:

```text
closed = false
definition_digest = null
semantic_closure_not_implemented = 1
active_grill_packs contains GRILL-CORE-1
active_grill_packs_complete reflects activation inventory truth
unknown_unknown_exhaustiveness_claimed = false
```

- [ ] **Step 11: Commit docs/gate changes**

```bash
git add skills/joewrks-product-definition/references/grill-contract-v0.2.0.md \
  skills/joewrks-product-definition/references/state-contract-v0.2.0.md \
  skills/joewrks-product-definition/references/discovery-contract-v0.2.0.md \
  skills/joewrks-product-definition/scripts/discovery_v2.py \
  tests/test_grill_baseline_v020.py tests/test_state_v020_foundation.py \
  tests/test_skill_package.py
git commit -m "docs: define Grill Engine V2 boundary"
```

- [ ] **Step 12: Report milestone precisely**

Only after every M3 gate is green, report:

```text
CORE_SEMANTIC_CLOSURE_V2_M3_IMPLEMENTED
— GRILL_ENGINE / NOT_INTEGRATED
```

Include implementation branch, planning/base SHA, final HEAD/tree/remote SHA, changed files, per-task commits, exact focused/legacy/full test results, skip reasons, `git diff --check`, frozen legacy verification, Materiality/autonomy/next-question/pack metrics, M3 Closure guard verification, and confirmation M4–M6 were not started.

Then stop. Do not start M4.

---

# M3 Plan Self-Review Mapping

| Frozen design requirement | M3 task |
| --- | --- |
| Unknown lifecycle separated from resolution mode | Task 2 |
| Traceable `UNK → DEC/evidence/constraint` resolution | Task 2 |
| Recommendation acceptance distinct from user decision | Tasks 2–3 |
| Deterministic Materiality Assessment | Task 1 |
| Agent autonomy boundary | Task 3 |
| Evidence-resolvable issues do not interrupt user | Tasks 3–4 |
| One highest-leverage question at a time | Task 4 |
| Ranking by unlock/risk/fan-out/category | Task 4 |
| Structured mutually exclusive options/recommendation/tradeoffs | Tasks 2–4 |
| Core Grill present for material requirements | Task 5 |
| Topology-triggered AUTH/MONEY/FILE_UPLOAD/ASYNC/PERMISSION/DESTRUCTIVE packs | Task 5 |
| Agent cannot suppress triggered packs | Task 5 |
| Pack identity/version/digest commitment | Tasks 5–6 |
| Independent pack decisions resist umbrella compression | Task 5 |
| Active Grill Pack baseline integration | Task 6 |
| Unknown-unknown exhaustiveness never claimed | Task 6 |
| M4 Coverage Binding/Approval not silently pulled forward | Global constraints + Tasks 5–6 |
| M1/M2/legacy/downstream boundaries preserved | Every gate |

M3 intentionally leaves exact Coverage→Authority pointer/hash proof, UX Binding, Approval Manifest, semantic definition digest, and true V2 Semantic Closure to M4. Downstream 2.0 remains M5; full migration/adoption remains M6.