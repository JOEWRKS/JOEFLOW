# Core Semantic Closure V2 — M2 Discover Authority Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the V2 discovery authority layer: typed Evidence Graph, Product Surface Manifest, typed contradictions, reverse-bootstrap intent classification, and deterministic discovery-baseline commitments on top of the verified M1 State 0.2 foundation.

**Architecture:** Extend the existing `state-v0.2.0` contract rather than introducing another source of truth. Evidence, surfaces, contradictions, reverse-bootstrap classification, and discovery baseline remain inside canonical `state.json`. M2 tightens only discovery semantics; the M1 Closure guard remains mandatory, M3 still owns materiality classification and Grill/decision authority policy, M4 still owns Coverage→Authority Binding and informed approval, and M5 still owns downstream 2.0.

**Tech Stack:** Python 3 standard library, JSON, Draft 2020-12 JSON Schema documents, SHA-256 canonical JSON commitments, `unittest`.

**Spec:**
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-freeze.md`
- `docs/superpowers/specs/2026-08-28-core-semantic-closure-v2-design.md` — especially sections 8–12
- `docs/superpowers/audits/2026-08-28-core-semantic-closure-v2-m1-source-audit.md`

## Global Constraints

- Implement from an isolated branch/worktree based on exact M1 implementation HEAD `e7851e6df8855694ff8b3ec5244dd22ada141ca3` plus this planning document only; do not merge to `main`.
- Preserve the frozen legacy 0.1.2.1 files byte-for-byte.
- Preserve `skills/joewrks-product-definition/downstream/` and `evals/semantic-review-v0.4.3/` unchanged.
- Preserve `joewrks.action-conformance/1.0` and `joewrks.semantic-review/1.0` unchanged.
- Keep V2 `schema_version` at `0.2.0`; M2 extends the contract but does not create a new schema version.
- Keep the M1 V2 Closure guard throughout M2:
  - `closed = false`
  - `definition_digest = null`
  - `semantic_closure_not_implemented = 1`
- M2 must not recompute Materiality classification. It may consume the M1 materiality shape and `classification` value; deterministic classification is M3.
- M2 must not implement user-question ranking, recommendations, unknown resolution provenance, AI autonomy policy, or Grill Pack activation. Those are M3.
- M2 must not implement Coverage→Authority Binding, UX binding, Approval Manifest, V2 semantic definition digest, or downstream 2.0. Those are M4–M5.
- Observed implementation/runtime/test behavior is evidence of behavior, not automatic product intent.
- `INFERRED_INTENT` is candidate evidence only and may not independently justify an authoritative product-intent disposition.
- Discovery completeness is procedural only. `unknown_unknown_exhaustiveness_claimed` must always be `false`.
- Every behavior-changing code task follows RED → GREEN → refactor.
- Strongest successful milestone label: `IMPLEMENTED_M2 / NOT_INTEGRATED`.

---

## File Map

**Modify existing V2 contract/runtime**
- `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- `tests/v020_support.py`

**Create discovery runtime/contracts**
- `skills/joewrks-product-definition/scripts/discovery_v2.py`
- `skills/joewrks-product-definition/scripts/build_discovery_baseline.py`
- `skills/joewrks-product-definition/references/discovery-contract-v0.2.0.md`

**Create tests**
- `tests/test_evidence_v020.py`
- `tests/test_surface_manifest_v020.py`
- `tests/test_contradictions_v020.py`
- `tests/test_reverse_bootstrap_v020.py`
- `tests/test_discovery_baseline_v020.py`

---

### Task 1: Type the Evidence Graph and enforce evidence authority limits

**Files:**
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/test_evidence_v020.py`
- Modify: `tests/v020_support.py`

**Interfaces:**
- V2 evidence records use stable `EVD-*` IDs.
- Add internal helpers:
  - `_collect_evidence(state: dict[str, Any]) -> dict[str, dict[str, Any]]`
  - `_validate_evidence(state: dict[str, Any]) -> list[dict[str, str]]`
  - `_evidence_can_support(record: dict[str, Any], authority_class: str, *, for_closure: bool) -> bool`
- Do not expose a new CLI in Task 1.

- [ ] **Step 1: Add literal evidence builders**

Extend `tests/v020_support.py` with:

```python
def evidence_record(
    evidence_id="EVD-001",
    *,
    source_kind="OBSERVED_IMPLEMENTATION",
    authority_classes=None,
    confidence="DIRECT",
    status="CURRENT",
    claim="The current implementation rejects duplicate submissions.",
    locator="src/submit.py",
):
    if authority_classes is None:
        authority_classes = ["FACTUAL", "BEHAVIORAL"]
    return {
        "id": evidence_id,
        "status": status,
        "source_kind": source_kind,
        "locator": locator,
        "claim": claim,
        "confidence": confidence,
        "authority_classes": list(authority_classes),
        "observed_version": None,
        "content_hash": None,
    }
```

The canonical M2 evidence shape uses exactly these required fields:

```text
id
status
source_kind
locator
claim
confidence
authority_classes
observed_version
content_hash
```

`observed_version` and `content_hash` are required keys whose values may be JSON `null`; this prevents schema-shape drift while preserving “when available” semantics.

- [ ] **Step 2: Add RED tests for source kinds, authority classes, lifecycle, and candidate-only inference**

Create `tests/test_evidence_v020.py` and require:

```text
source_kind:
USER_CONFIRMED_INTENT
DOCUMENTED_INTENT
HISTORICAL_DECISION
EXTERNAL_CONSTRAINT
OBSERVED_IMPLEMENTATION
OBSERVED_RUNTIME
TEST_ASSERTION
DESIGN_ARTIFACT
INFERRED_INTENT

status:
CURRENT
STALE
SUPERSEDED
UNAVAILABLE

confidence:
DIRECT
CORROBORATED
INFERRED

authority classes:
FACTUAL
INTENT
CONSTRAINT
BEHAVIORAL
PREFERENCE
```

Use this frozen source-kind capability matrix in both tests and runtime:

```python
SOURCE_KIND_CAPABILITIES = {
    "USER_CONFIRMED_INTENT": {"INTENT", "PREFERENCE"},
    "DOCUMENTED_INTENT": {"INTENT", "PREFERENCE"},
    "HISTORICAL_DECISION": {"INTENT", "PREFERENCE"},
    "EXTERNAL_CONSTRAINT": {"FACTUAL", "CONSTRAINT"},
    "OBSERVED_IMPLEMENTATION": {"FACTUAL", "BEHAVIORAL"},
    "OBSERVED_RUNTIME": {"FACTUAL", "BEHAVIORAL"},
    "TEST_ASSERTION": {"FACTUAL", "BEHAVIORAL"},
    "DESIGN_ARTIFACT": {"INTENT", "PREFERENCE"},
    "INFERRED_INTENT": {"INTENT", "PREFERENCE"},
}
CANDIDATE_ONLY_SOURCE_KINDS = {"INFERRED_INTENT"}
```

Required RED cases:

1. ID not matching `EVD-[0-9]{3,}` fails.
2. duplicate EVD/object/surface/contradiction IDs fail globally.
3. empty locator/claim fails.
4. unknown source kind/confidence/status/authority class fails.
5. declared authority class outside the source-kind capability matrix fails with `invalid_evidence_authority_class`.
6. `INFERRED_INTENT` with an `INTENT` class is structurally valid but `_evidence_can_support(..., "INTENT", for_closure=True)` returns `False`.
7. `OBSERVED_IMPLEMENTATION` cannot support `INTENT` or `PREFERENCE`.
8. `USER_CONFIRMED_INTENT` can support `INTENT` for closure when status is `CURRENT`.
9. `STALE`, `SUPERSEDED`, and `UNAVAILABLE` evidence cannot support current closure authority.
10. `SUPERSEDED` requires `superseded_by` pointing to a different current `EVD-*`; `UNAVAILABLE` requires a meaningful `unavailable_reason`.

- [ ] **Step 3: Run evidence tests RED**

```bash
python -m unittest tests.test_evidence_v020 -v
```

Expected: FAIL because evidence is still a reserved untyped M1 array.

- [ ] **Step 4: Extend the schema with the exact Evidence record contract**

Add `$defs.evidence_record` using `additionalProperties: false`. Include optional lifecycle properties `superseded_by` and `unavailable_reason`; require them conditionally for `SUPERSEDED` and `UNAVAILABLE` respectively. `authority_classes` is a unique non-empty array. `observed_version` and `content_hash` use `oneOf: [{"type":"string","minLength":1},{"type":"null"}]`.

Change root `evidence.items` from permissive object to `$ref: #/$defs/evidence_record`.

- [ ] **Step 5: Implement evidence validation**

In `state_validation_v2.py`, use the exact capability constants above. `_validate_evidence` must verify:

- stable ID and global uniqueness through the existing collector;
- semantic text and enum shapes;
- capability matrix membership;
- supersession target existence/type/status and cycles for evidence records;
- `UNAVAILABLE` reason;
- no closure-capable use of non-current/candidate-only evidence through `_evidence_can_support`.

Call `_validate_evidence` from `validate_state_v2` after global ID collection.

- [ ] **Step 6: Run Task 1 GREEN plus M1 regression**

```bash
python -m unittest \
  tests.test_evidence_v020 \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation \
  tests.test_legacy_v0121_frozen -v
```

Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add tests/v020_support.py tests/test_evidence_v020.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py
git commit -m "feat: add state 0.2 evidence authority graph"
```

---

### Task 2: Implement Product Surface Manifest dispositions

**Files:**
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/test_surface_manifest_v020.py`
- Modify: `tests/v020_support.py`

**Interfaces:**
- Add `_collect_surfaces(state) -> dict[str, dict[str, Any]]`.
- Add `_validate_surface_manifest(state, id_index, evidence_index) -> list[dict[str, str]]`.
- Add `_surface_metrics(state) -> dict[str, int]` returning at least `open_material_surfaces` and `unbound_material_surfaces`.

- [ ] **Step 1: Add a literal surface builder**

```python
def surface_record(
    surface_id="SURF-001",
    *,
    kind="FEATURE_AREA",
    status="IN_SCOPE",
    name="Feedback submission",
    classification="MATERIAL",
):
    return {
        "id": surface_id,
        "kind": kind,
        "name": name,
        "status": status,
        "materiality": materiality(classification=classification),
        "evidence_refs": [],
        "authority_refs": [],
        "unknown_refs": [],
        "decision_refs": [],
        "contradiction_refs": [],
        "rationale": None,
        "intent_classification": None,
    }
```

Surface kinds are exactly:

```text
ACTOR
FEATURE_AREA
ENTRY_POINT
MAJOR_ACTION
DOMAIN_ENTITY
INTEGRATION
ASYNC_PROCESS
NOTIFICATION
PERSISTENT_STATE
SENSITIVE_DATA
PERMISSION
MONEY_FLOW
DESTRUCTIVE_OPERATION
LIFECYCLE_OBJECT
```

Surface statuses are exactly:

```text
IN_SCOPE
OUT_OF_SCOPE
OPEN
SUPERSEDED
RETIRED
```

- [ ] **Step 2: Add RED disposition tests**

Create `tests/test_surface_manifest_v020.py` and require:

1. `SURF-*` stable ID and global uniqueness.
2. all enum/text/array/materiality shapes are enforced.
3. every evidence ref resolves to `EVD-*`; every unknown ref resolves to `UNK-*`; every decision ref resolves to `DEC-*`; every contradiction ref resolves to `CON-*`.
4. material `IN_SCOPE` requires at least one current `authority_ref` to `REQ`, `RULE`, `FLOW`, `DATA`, or `INT`; otherwise `UNBOUND_PRODUCT_SURFACE`.
5. material `OPEN` requires at least one current/open `UNK-*`.
6. `OUT_OF_SCOPE` requires a meaningful `rationale` plus at least one closure-capable `INTENT`/`PREFERENCE` evidence ref **or** at least one current decision ref.
7. observed implementation evidence alone cannot justify `OUT_OF_SCOPE`.
8. `SUPERSEDED` requires a different `SURF-*` `superseded_by`; cycles fail.
9. `RETIRED` requires `retired_by: DEC-*`, `retired_at_revision`, and meaningful `retirement_reason` using the same V2 retirement semantics as typed authority records.
10. non-material OPEN may be structurally valid but is counted separately from `open_material_surfaces`.

- [ ] **Step 3: Run surface tests RED**

```bash
python -m unittest tests.test_surface_manifest_v020 -v
```

Expected: FAIL before surface semantics exist.

- [ ] **Step 4: Tighten `surface_manifest` schema**

Set the root shape to:

```json
{
  "type": "object",
  "required": ["records"],
  "properties": {
    "records": {"type": "array", "items": {"$ref": "#/$defs/surface_record"}}
  },
  "additionalProperties": false
}
```

`surface_record` uses `additionalProperties: false` and supports the lifecycle fields used by `SUPERSEDED`/`RETIRED`.

- [ ] **Step 5: Implement disposition validation and metrics**

Use existing global ID/index helpers. Authority refs for an `IN_SCOPE` material surface must resolve to a current typed record whose prefix is one of:

```python
SURFACE_AUTHORITY_PREFIXES = {"REQ", "RULE", "FLOW", "DATA", "INT"}
```

For `OUT_OF_SCOPE`, intent evidence is closure-capable only when `_evidence_can_support(record, "INTENT", for_closure=True)` or `_evidence_can_support(record, "PREFERENCE", for_closure=True)` is true.

- [ ] **Step 6: Extend M2 closure output only with discovery metrics**

`evaluate_closure_v2` remains `closed: false` with `semantic_closure_not_implemented: 1`, but its metrics dict now also includes surface metrics. Do not remove the M1 guard.

- [ ] **Step 7: Run Task 2 GREEN plus Task 1/M1 regressions**

```bash
python -m unittest \
  tests.test_surface_manifest_v020 \
  tests.test_evidence_v020 \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation \
  tests.test_legacy_v0121_frozen -v
```

Expected: `OK`.

- [ ] **Step 8: Commit**

```bash
git add tests/v020_support.py tests/test_surface_manifest_v020.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py
git commit -m "feat: add product surface manifest dispositions"
```

---

### Task 3: Type contradictions and require explicit authority resolution

**Files:**
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Create: `tests/test_contradictions_v020.py`

**Interfaces:**
- Add `_collect_contradictions(state) -> dict[str, dict[str, Any]]`.
- Add `_validate_contradictions(state, id_index, evidence_index) -> list[dict[str, str]]`.
- Add `_contradiction_metrics(state) -> dict[str, int]` with `unresolved_material_contradictions` and `stale_selected_authority`.

- [ ] **Step 1: Add RED typed contradiction tests**

The canonical contradiction record is:

```python
{
    "id": "CON-001",
    "status": "OPEN",
    "claim_a_refs": ["EVD-001"],
    "claim_b_refs": ["EVD-002"],
    "scope_refs": ["SURF-001"],
    "materiality": materiality(classification="MATERIAL"),
    "resolution": None,
    "resolved_by": [],
    "selected_authority_refs": [],
}
```

Allowed status values:

```text
OPEN
RESOLVED
SUPERSEDED
RETIRED
```

Required cases:

1. stable `CON-*` and global uniqueness.
2. both claim arrays are non-empty unique `EVD-*` refs.
3. `scope_refs` is a non-empty unique array of existing stable IDs.
4. `RESOLVED` requires meaningful `resolution` and at least one of:
   - non-empty current `DEC-*` `resolved_by`; or
   - non-empty current, closure-capable `selected_authority_refs`.
5. selected authority evidence must be `CURRENT` and cannot be `INFERRED_INTENT` candidate-only evidence.
6. a bare acknowledgement with no decision/selected authority fails `unresolved_contradiction_authority`.
7. material `OPEN` increments `unresolved_material_contradictions`.
8. non-material OPEN does not increment that material metric.
9. `SUPERSEDED` and `RETIRED` use explicit same-type/retires-by-decision lifecycle rules.

- [ ] **Step 2: Run contradiction tests RED**

```bash
python -m unittest tests.test_contradictions_v020 -v
```

Expected: FAIL because contradictions are still structurally loose.

- [ ] **Step 3: Tighten contradiction schema and runtime validation**

Use `additionalProperties: false`. `resolution` is `string|minLength:1` or `null`; `resolved_by` and `selected_authority_refs` are unique arrays. Conditional schema may require `resolution` for `RESOLVED`, but cross-reference/authority eligibility remains Python semantic validation.

- [ ] **Step 4: Extend closure metrics without enabling Closure**

Merge contradiction metrics into `evaluate_closure_v2` while keeping `semantic_closure_not_implemented = 1` and `closed = false`.

- [ ] **Step 5: Run Task 3 GREEN**

```bash
python -m unittest \
  tests.test_contradictions_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_evidence_v020 \
  tests.test_state_v020_foundation -v
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add tests/test_contradictions_v020.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py
git commit -m "feat: require explicit contradiction resolution authority"
```

---

### Task 4: Enforce reverse-bootstrap intent classification

**Files:**
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/templates/state-v0.2.0.example.json`
- Modify: `tests/v020_support.py`
- Create: `tests/test_reverse_bootstrap_v020.py`

**Interfaces:**
- Add required `project.bootstrap_mode`:
  - `NEW_PRODUCT`
  - `EXISTING_PRODUCT_RECONCILIATION`
- Existing-product surface records require `intent_classification` from:
  - `AUTHORITATIVE`
  - `OBSERVED_ONLY`
  - `CONFLICTING`
  - `UNEXPLAINED`
- New-product surfaces require `intent_classification: null`.

- [ ] **Step 1: Update V2 test/template project shape and add RED compatibility test**

Extend `foundation_state()` and `state-v0.2.0.example.json` with:

```json
"bootstrap_mode": "NEW_PRODUCT"
```

Update the schema/runtime parity tests to require it. This is an intentional M2 extension of state 0.2.0, not a legacy contract change.

- [ ] **Step 2: Add reverse-bootstrap RED tests**

Create `tests/test_reverse_bootstrap_v020.py` covering:

### `AUTHORITATIVE`
Must have:

- at least one `authority_ref`;
- at least one `CURRENT`, closure-capable evidence ref supporting `INTENT` or `PREFERENCE`.

Observed implementation/runtime/test evidence alone must **not** qualify.

### `OBSERVED_ONLY`
Must have at least one evidence ref whose source kind is one of:

```text
OBSERVED_IMPLEMENTATION
OBSERVED_RUNTIME
TEST_ASSERTION
```

It must not automatically create/require an authority ref. If material, it requires an `OPEN` unknown ref so intent can be reconciled later.

### `CONFLICTING`
Requires at least one `CON-*` contradiction ref. A material conflicting surface with no contradiction fails.

### `UNEXPLAINED`
If material, requires an `OPEN` unknown ref. It may have observed evidence but no authoritative explanation.

Also require:

- `EXISTING_PRODUCT_RECONCILIATION` surfaces may not omit intent classification;
- `NEW_PRODUCT` surfaces must keep `intent_classification` null;
- changing bootstrap mode does not auto-promote any observed surface to authority.

- [ ] **Step 3: Run reverse-bootstrap tests RED**

```bash
python -m unittest tests.test_reverse_bootstrap_v020 -v
```

Expected: FAIL before bootstrap semantics exist.

- [ ] **Step 4: Extend project/surface schema and runtime rules**

Update `PROJECT_KEYS` and schema `project.required/properties` with `bootstrap_mode`. Update surface validation with the exact classification rules above.

Do not create REQ/RULE/FLOW records automatically in validation or helper code. Reconciliation remains explicit canonical-state work.

- [ ] **Step 5: Run Task 4 GREEN plus M1 compatibility**

```bash
python -m unittest \
  tests.test_reverse_bootstrap_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_evidence_v020 \
  tests.test_contradictions_v020 \
  tests.test_state_v020_foundation \
  tests.test_migration_v020_foundation -v
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add tests/v020_support.py tests/test_reverse_bootstrap_v020.py \
  skills/joewrks-product-definition/templates/state-v0.2.0.example.json \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json \
  skills/joewrks-product-definition/scripts/state_validation_v2.py
git commit -m "feat: separate observed behavior from product intent"
```

---

### Task 5: Build deterministic discovery baselines and stale-consumption detection

**Files:**
- Create: `skills/joewrks-product-definition/scripts/discovery_v2.py`
- Create: `skills/joewrks-product-definition/scripts/build_discovery_baseline.py`
- Modify: `skills/joewrks-product-definition/scripts/state_validation_v2.py`
- Modify: `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`
- Create: `tests/test_discovery_baseline_v020.py`

**Interfaces:**
- `canonical_json_bytes(value: object) -> bytes`
- `build_discovery_baseline(state: dict[str, Any], *, procedure_complete: bool, applicable_surface_classes_complete: bool) -> dict[str, Any]`
- `validate_discovery_baseline(state: dict[str, Any]) -> list[dict[str, str]]`
- CLI:

```text
python skills/joewrks-product-definition/scripts/build_discovery_baseline.py STATE_JSON
```

The CLI prints the computed baseline JSON only; it never writes state in place.

- [ ] **Step 1: Add discovery-baseline RED tests**

Canonical baseline shape:

```python
{
    "status": "CURRENT",
    "definition_revision": 1,
    "surface_manifest_digest": "<sha256>",
    "evidence_commitment_digest": "<sha256>",
    "open_material_surface_count": 0,
    "unresolved_material_contradiction_count": 0,
    "procedure_complete": True,
    "applicable_surface_classes_complete": True,
    "active_grill_packs": [],
    "active_grill_packs_complete": False,
    "unknown_unknown_exhaustiveness_claimed": False,
}
```

Required cases:

1. same semantic input produces identical baseline bytes.
2. surface change changes `surface_manifest_digest`.
3. evidence change changes `evidence_commitment_digest`.
4. `unknown_unknown_exhaustiveness_claimed` may never be true.
5. M2 baseline always has `active_grill_packs_complete = false`; M3 owns activation/completeness.
6. a stored `CURRENT` baseline whose revision/digests/counts no longer match recomputation fails with `stale_discovery_baseline`.
7. `STALE` baseline is structurally valid but increments `discovery_baseline_gaps`.
8. current decisions/surfaces that consume `STALE`, `SUPERSEDED`, or `UNAVAILABLE` evidence increment `stale_consumed_evidence` and fail current-authority validation where that evidence is the required basis.
9. unconsumed stale evidence alone does not increment `stale_consumed_evidence`.

- [ ] **Step 2: Run baseline tests RED**

```bash
python -m unittest tests.test_discovery_baseline_v020 -v
```

Expected: FAIL before discovery compiler exists.

- [ ] **Step 3: Implement deterministic baseline compilation**

`canonical_json_bytes` uses:

```python
json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
```

Digest the canonical `surface_manifest.records` list and the canonical entire evidence list separately. Do not use the whole state hash. Count material-open surfaces and material-open contradictions using current state data.

M2 intentionally writes:

```text
active_grill_packs = []
active_grill_packs_complete = false
```

so it cannot imply M3 discovery completeness.

- [ ] **Step 4: Implement the read-only baseline CLI**

Read one state file, require `schema_version == 0.2.0`, validate the current state, and emit deterministic JSON. It must not mutate the source file. Argument/read errors exit `2`; invalid V2 state exits `1` with structured JSON error.

- [ ] **Step 5: Validate stored baselines and consumed evidence**

Call `validate_discovery_baseline` from `validate_state_v2`. Extend `evaluate_closure_v2` metrics with:

```text
open_material_surfaces
unbound_material_surfaces
unresolved_material_contradictions
stale_consumed_evidence
discovery_baseline_gaps
```

Retain `semantic_closure_not_implemented = 1` and `closed = false`.

- [ ] **Step 6: Run Task 5 GREEN**

```bash
python -m unittest \
  tests.test_discovery_baseline_v020 \
  tests.test_reverse_bootstrap_v020 \
  tests.test_contradictions_v020 \
  tests.test_surface_manifest_v020 \
  tests.test_evidence_v020 -v
```

Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add tests/test_discovery_baseline_v020.py \
  skills/joewrks-product-definition/scripts/discovery_v2.py \
  skills/joewrks-product-definition/scripts/build_discovery_baseline.py \
  skills/joewrks-product-definition/scripts/state_validation_v2.py \
  skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json
git commit -m "feat: add deterministic discovery baseline"
```

---

### Task 6: Document the M2 discovery contract and run the milestone gate

**Files:**
- Create: `skills/joewrks-product-definition/references/discovery-contract-v0.2.0.md`
- Modify: `skills/joewrks-product-definition/references/state-contract-v0.2.0.md`
- Modify: `tests/test_state_v020_foundation.py`
- Modify: `tests/test_skill_package.py` only if required to allow the new sibling `discovery_v2` import; do not weaken the existing hidden-import policy.

**Interfaces:**
- M2 documentation must use exact status marker `DISCOVER_AUTHORITY_IMPLEMENTED_M2`.
- M1 Closure guard remains explicitly documented and tested.

- [ ] **Step 1: Add RED package/document-boundary tests**

Require:

- `discovery-contract-v0.2.0.md` exists;
- state-contract links the discovery contract;
- package resources include the new discovery runtime/reference files;
- import policy permits only the explicit sibling module `discovery_v2` if needed;
- hidden `__import__` remains forbidden;
- docs contain all literals:

```text
DISCOVER_AUTHORITY_IMPLEMENTED_M2
OBSERVED_IMPLEMENTATION_IS_NOT_INTENT
UNKNOWN_UNKNOWN_EXHAUSTIVENESS_NOT_CLAIMED
ACTIVE_GRILL_PACKS_NOT_IMPLEMENTED_IN_M2
SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M2
```

- [ ] **Step 2: Run doc/package tests RED**

```bash
python -m unittest tests.test_state_v020_foundation tests.test_skill_package -v
```

Expected: FAIL before M2 documentation/package expectations are added.

- [ ] **Step 3: Write the M2 discovery reference**

It must state, in plain contract language:

```text
- Evidence records prove only the authority classes their source kind is allowed to support.
- INFERRED_INTENT is candidate-only and cannot independently close product intent.
- Existing implementation/runtime/test behavior is not automatically product intent.
- Every material discovered surface is IN_SCOPE with authority, OUT_OF_SCOPE with intent basis, OPEN with unknown, or explicitly retired/superseded.
- Resolved contradictions identify a decision or selected current authority.
- Reverse bootstrap classifies AUTHORITATIVE / OBSERVED_ONLY / CONFLICTING / UNEXPLAINED before canonical intent is granted.
- Discovery baseline is deterministic and can become stale.
- M2 does not claim active Grill Pack completeness or universal unknown-unknown exhaustiveness.
- M2 does not remove the V2 Closure guard.
```

- [ ] **Step 4: Run all M2-focused tests**

```bash
python -m unittest \
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

- [ ] **Step 5: Run legacy regression**

```bash
python -m unittest tests.test_validators tests.test_semantic_v012 -v
```

Expected: exit `0`, with the four frozen legacy Git-blob commitments unchanged.

- [ ] **Step 6: Run full repository suite and diff check**

```bash
python -m unittest discover -s tests -v
git diff --check
```

Expected: both exit `0`. No new skip is permitted; any pre-existing environment-dependent skip may remain only with the same reason.

- [ ] **Step 7: Verify M2 scope boundaries from Git diff**

Require no changes under:

```text
skills/joewrks-product-definition/downstream/
evals/semantic-review-v0.4.3/
skills/joewrks-product-definition/schemas/state.schema.json
skills/joewrks-product-definition/scripts/state_validation.py
skills/joewrks-product-definition/references/state-contract.md
skills/joewrks-product-definition/templates/state.example.json
```

Also explicitly verify:

```text
closed = false
definition_digest = null
semantic_closure_not_implemented = 1
active_grill_packs_complete = false
unknown_unknown_exhaustiveness_claimed = false
```

- [ ] **Step 8: Commit docs/gate changes**

```bash
git add skills/joewrks-product-definition/references/discovery-contract-v0.2.0.md \
  skills/joewrks-product-definition/references/state-contract-v0.2.0.md \
  tests/test_state_v020_foundation.py tests/test_skill_package.py
git commit -m "docs: define state 0.2 discovery authority boundary"
```

- [ ] **Step 9: Report the milestone precisely**

Only after every M2 gate passes, report:

```text
CORE_SEMANTIC_CLOSURE_V2_M2_IMPLEMENTED
— DISCOVER_AUTHORITY / NOT_INTEGRATED
```

Include branch/base/HEAD/tree/remote SHA, per-task commits, changed files, exact focused/legacy/full test results, skip reasons, diff-check result, frozen legacy verification, discovery metrics/guard verification, and confirmation that M3–M6 were not started.

---

## M2 Plan Self-Review Mapping

| Frozen design requirement | M2 task |
| --- | --- |
| First-class Evidence Graph | Task 1 |
| Evidence authority classes and candidate-only inference | Task 1 |
| Product Surface Manifest | Task 2 |
| IN_SCOPE / OUT_OF_SCOPE / OPEN / SUPERSEDED / RETIRED dispositions | Task 2 |
| Typed contradiction authority resolution | Task 3 |
| Existing implementation != intended product authority | Task 4 |
| AUTHORITATIVE / OBSERVED_ONLY / CONFLICTING / UNEXPLAINED | Task 4 |
| Deterministic discovery baseline | Task 5 |
| Evidence/surface digest staleness | Task 5 |
| Stale consumed evidence surfaced | Task 5 |
| Procedural, not omniscient discovery claim | Tasks 5–6 |
| M1 Closure guard remains active | Global constraints + Tasks 2–6 |
| M3 Grill Packs not silently implemented | Global constraints + Tasks 5–6 |
| Legacy/downstream/calibration untouched | Global constraints + Task 6 gate |

M2 intentionally leaves Materiality classification/Autonomy/Unknown-resolution policy to M3, Coverage→Authority/Approval Manifest to M4, downstream 2.0 to M5, and full adoption/end-to-end integration to M6.
