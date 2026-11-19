# Downstream Contract Authority v0.4.1.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce full contract structure and machine-checkable semantic derivation while isolating partial A/B regression slices from production handoff contracts.

**Architecture:** A stdlib schema-keyword-subset validator enforces the checked-in contract schemas. The compiler validates semantic envelopes, executes only `exact` and `extract`, records authority coverage, and emits either a full production contract or an evaluator-only regression slice. Verifiers consume compiled values but never determine derivation authority.

**Tech Stack:** Python 3 standard library, JSON/JSONL, unittest, Node.js, Vitest, TypeScript

**Spec:** `docs/superpowers/specs/2026-08-23-downstream-contract-authority-v0.4.1.1-design.md`

## Global Constraints

- Do not modify canonical Product Definition, state schema, Product Definition validators, Closure, JSONL runtime semantics, or frozen A/B implementation sources.
- `joewrks.action-conformance/1.0` is full production handoff; `joewrks.downstream.regression-slice/1.0` is evaluator-only.
- Supported schema validation is the documented repository keyword subset, not complete JSON Schema Draft 2020-12.
- `REVIEW_REQUIRED` is structurally/provenance valid but never machine verified.
- Implement only `exact` and `extract` derivation operators.
- Every production-code behavior change follows RED, GREEN, refactor.

---

### Task 1: Authority rejection tests

**Files:**
- Modify: `tests/test_downstream_contracts.py`
- Modify: `tests/test_downstream_product_bundles.py`

**Interfaces:**
- Consumes: existing `compile_contract(state, definition)` and canonical source helpers.
- Produces: seven literal negative cases and assessment assertions that define the compiler boundary.

- [ ] **Step 1: Add the seven required negative tests**

Use literal definitions to assert `ContractError` for missing full fields, false `exact`, invalid source indices, empty provenance, superseded-only authority, changed exact/extract output, and partial definitions stamped as full.

The test module adds methods named `test_full_contract_missing_required_semantic_field_fails`, `test_machine_derived_fake_value_with_current_source_fails`, `test_semantic_source_ref_out_of_range_fails`, `test_semantic_field_without_provenance_fails`, `test_active_semantic_field_with_only_superseded_source_fails`, `test_changed_machine_derived_value_with_unchanged_source_hash_fails`, and `test_regression_slice_cannot_claim_full_contract_version`. Each calls the real compiler inside `with self.assertRaises(ContractError):`.

The fixtures use these literal envelope shapes rather than compiler helpers, so a broken compiler cannot build both actual and expected values:

```python
machine_exact = {
    "value": "Only owners may approve.",
    "source_refs": [0],
    "derivation": {"kind": "MACHINE_DERIVED", "operator": "exact"},
}
review_required = {
    "value": "SUCCESS",
    "source_refs": [0],
    "derivation": {
        "kind": "REVIEW_REQUIRED",
        "explanation": "The canonical rule requires human classification of the runtime outcome.",
    },
}
```

- [ ] **Step 2: Run only the new tests and verify RED**

Run: `python -m unittest tests.test_downstream_contracts tests.test_downstream_product_bundles`

Expected: failures show the current compiler accepts partial full contracts and does not validate semantic derivation.

### Task 2: Schema-keyword-subset validator

**Files:**
- Create: `skills/joewrks-product-definition/downstream/schema_validation.py`
- Modify: `skills/joewrks-product-definition/downstream/schemas/action-contract.schema.json`
- Modify: `skills/joewrks-product-definition/downstream/schemas/lifecycle-contract.schema.json`
- Create: `skills/joewrks-product-definition/downstream/schemas/regression-slice.schema.json`
- Test: `tests/test_downstream_contracts.py`

**Interfaces:**
- Produces: `validate_instance(instance, schema, *, root_schema=None) -> None`, raising `SchemaValidationError` with an instance path.
- Consumes: local schema JSON using only `$ref`, `type`, `required`, `properties`, `additionalProperties`, `items`, `minItems`, `const`, `enum`, `pattern`, and `oneOf`.

- [ ] **Step 1: Add focused RED tests for each supported keyword and unsupported validation keyword rejection**
- [ ] **Step 2: Implement recursive local-reference validation with exact instance paths**

The validator has one public function and rejects unrecognized validation keywords:

```python
class SchemaValidationError(ValueError):
    pass

def validate_instance(instance: object, schema: dict[str, object]) -> None:
    _validate(instance, schema, schema, path="")
```

`_validate` resolves only local definitions and dispatches the approved keyword set:

```python
SUPPORTED = {
    "$schema", "$id", "title", "$defs", "$ref", "type", "required",
    "properties", "additionalProperties", "items", "minItems", "minimum", "const",
    "enum", "pattern", "oneOf", "description",
}
```

- [ ] **Step 3: Make the full schema require lifecycles, authority assessment, default result, and semantic envelopes; set top-level additional properties false**
- [ ] **Step 4: Define the evaluator-only slice schema with minimum explicit harness semantic fields**

Both schemas use the same semantic envelope definition:

```json
{
  "type": "object",
  "required": ["value", "source_refs", "derivation"],
  "properties": {
    "value": {},
    "source_refs": {"type": "array", "minItems": 1, "items": {"type": "integer", "minimum": 0}},
    "derivation": {"oneOf": [
      {"$ref": "#/$defs/machineDerivation"},
      {"$ref": "#/$defs/reviewDerivation"}
    ]}
  },
  "additionalProperties": false
}
```
- [ ] **Step 5: Run focused schema tests GREEN**

Run: `python -m unittest tests.test_downstream_contracts`

### Task 3: Semantic derivation compiler

**Files:**
- Modify: `skills/joewrks-product-definition/downstream/contracts.py`
- Modify: `skills/joewrks-product-definition/downstream/provenance.py`
- Test: `tests/test_downstream_contracts.py`

**Interfaces:**
- Produces: `semantic_value(field)`, `validate_semantic_field(field, sources, owner)`, and deterministic authority-assessment counts.
- `exact` returns the canonical value selected by one source record.
- `extract` resolves `derivation.pointer` inside the canonical value selected by one source record.

- [ ] **Step 1: Verify the seven authority tests are still RED against production code**
- [ ] **Step 2: Require an explicit supported contract schema version and select its schema**
- [ ] **Step 3: Validate source indices and current authority before evaluating derivation**
- [ ] **Step 4: Implement `exact`, `extract`, and strict emitted-value equality**

The compiler API is explicit and has no arbitrary mapping callback:

```python
def semantic_value(field: dict[str, object]) -> object:
    return field["value"]

def validate_semantic_field(
    state: dict[str, object],
    field: object,
    sources: list[dict[str, object]],
    *,
    owner: str,
) -> str:
    """Return MACHINE_DERIVED or REVIEW_REQUIRED, otherwise raise ContractError."""
```

For `exact`, `computed = resolve_pointer(state, sources[index]["pointer"])`. For `extract`, the compiler first obtains that canonical source value and then calls `resolve_pointer` on the declared relative pointer. It finally compares `sha256_json(computed)` with `sha256_json(field["value"])` and raises on mismatch.

- [ ] **Step 5: Validate non-empty REVIEW_REQUIRED explanations without marking their values verified**
- [ ] **Step 6: Count both derivation classes and emit the separated authority assessment**

The emitted assessment is exactly separated:

```python
{
    "structurally_valid": True,
    "provenance_valid": True,
    "machine_derived_obligations_verified": True,
    "machine_derived_field_count": machine_count,
    "review_required_field_count": review_count,
    "review_required_obligations_present": review_count > 0,
    "machine_verifiable_coverage": machine_count / (machine_count + review_count),
}
```
- [ ] **Step 7: Validate the completed bundle against its selected repository schema and run focused tests GREEN**

### Task 4: Full and slice product definitions

**Files:**
- Modify: `skills/joewrks-product-definition/downstream/product_adapters.py`
- Modify: `skills/joewrks-product-definition/downstream/products/client-feedback-rev44.json`
- Modify: `skills/joewrks-product-definition/downstream/verifier.py`
- Modify: `skills/joewrks-product-definition/downstream/run_frozen_regressions.py`
- Test: `tests/test_downstream_product_bundles.py`
- Test: `tests/test_downstream_verifier.py`

**Interfaces:**
- A/B definitions declare `joewrks.downstream.regression-slice/1.0` and wrap all present harness semantics.
- rev44 declares `joewrks.action-conformance/1.0`; only lifecycle current states use `MACHINE_DERIVED/exact`, while interpretive fields use REVIEW_REQUIRED explanations.
- `semantic_value()` unwraps compiler-approved values for the verifier.

- [ ] **Step 1: Add RED tests for version separation, unwrapped verifier behavior, explicit result components, and authority counts**
- [ ] **Step 2: Convert A/B definitions to evaluator-only slices with explicit default and result expectations**

A/B definitions start with the evaluator-only version and use an explicit REVIEW_REQUIRED envelope for every interpreted harness expectation:

```python
{
    "contract_schema_version": "joewrks.downstream.regression-slice/1.0",
    "product_slug": "expense-reimbursement-dogfood",
    "actions": [{
        "action_id": "update_draft_money",
        "sources": money_sources,
        "default_result": review("REJECTED", [0, 1], "Finite-number rejection is interpreted from RULE-010 and RULE-015."),
        "input_invariants": review([
            {"type": "finite_number", "pointer": "/originalAmount"},
            {"type": "finite_number", "pointer": "/krwAmount"},
        ], [0, 1], "The two numeric fields and finite constraint require clause interpretation."),
        "result_expectations": review({"REJECTED": rejected_no_op}, [0, 1], "Rejected deep no-op is the evaluator expectation."),
        "test_obligations": review(["B031"], [0, 1], "Known-defect regression obligation."),
    }],
    "lifecycles": [],
}
```

- [ ] **Step 3: Convert every rev44 action/lifecycle semantic field to an envelope**

The rev44 machine-derived example is restricted to canonical exact equality:

```json
"current_states": {
  "value": ["DRAFT", "IN_REVIEW", "CHANGES_REQUESTED", "APPROVED"],
  "source_refs": [0],
  "derivation": {"kind": "MACHINE_DERIVED", "operator": "exact"}
}
```

- [ ] **Step 4: Remove verifier component/default-result escape hatches by requiring compiled declarations**

The verifier unwraps but does not validate authority:

```python
default_result = semantic_value(action["default_result"])
configured_results = semantic_value(action["result_expectations"])
if expected not in configured_results:
    raise VerificationError(f"result expectation is not declared: {expected}")
configured = configured_results[expected]
for component in COMPONENTS:
    if component not in configured:
        raise VerificationError(f"result expectation missing component: {component}")
```
- [ ] **Step 5: Run downstream contract, bundle, and verifier tests GREEN**

Run: `python -m unittest tests.test_downstream_contracts tests.test_downstream_product_bundles tests.test_downstream_verifier`

### Task 5: Handoff and reporting boundary

**Files:**
- Modify: `skills/joewrks-product-definition/references/figma-make-handoff.md`
- Modify: `skills/joewrks-product-definition/templates/figma-make-handoff.md`
- Modify: `skills/joewrks-product-definition/downstream/README.md`
- Modify: `evals/downstream-conformance-v0.4.1/contract-schema-review.md`
- Modify: `evals/downstream-conformance-v0.4.1/rev44-expressiveness.md`
- Modify: `evals/downstream-conformance-v0.4.1/aggregate-results.md`
- Test: `tests/test_downstream_handoff.py`

**Interfaces:**
- Full handoff accepts only `joewrks.action-conformance/1.0`.
- Reports expose full/slice version, both field counts, machine coverage, and outstanding review semantics.

- [ ] **Step 1: Add RED handoff tests that reject regression-slice handoff**

The handoff test invokes the contract gate rather than grepping prose:

```python
self.assertTrue(is_full_handoff_contract(full_bundle))
self.assertFalse(is_full_handoff_contract(regression_slice))
```

- [ ] **Step 2: Update reference/template and downstream documentation with the strict boundary**
- [ ] **Step 3: Correct acceptance criterion 3 and report the four independent authority statuses**
- [ ] **Step 4: Inspect the final spec/report artifacts after their last write**

### Task 6: Frozen evidence and final verification

**Files:**
- Regenerate: `evals/downstream-conformance-v0.4.1/evidence/*.json`
- Regenerate: `evals/downstream-conformance-v0.4.1/evidence/*.jsonl`
- Modify: `evals/downstream-conformance-v0.4.1/harness-results.md`
- Modify: `evals/downstream-conformance-v0.4.1/frozen-a-regression.md`
- Modify: `evals/downstream-conformance-v0.4.1/frozen-b-regression.md`

**Interfaces:**
- Consumes exact frozen A commit `9408434e640b9cf0bf6afaadd8f9d1f5f52e8943` and B source commit `eecebc28701006dd2c7be4045a22542e34719705`.
- Produces regenerated evidence with unchanged defect detection and new authority assessments.

- [ ] **Step 1: Execute actual frozen A/B adapters without patching either source**

Run:

```text
python -m downstream.run_frozen_regressions --a-root D:/JOEWRKS/.worktrees/joewrks-product-definition-v0.4.1.1-verify-a --b-worktree D:/JOEWRKS/.worktrees/joewrks-product-definition-v0.4-replication-b-codex --output-dir evals/downstream-conformance-v0.4.1/evidence
```

- [ ] **Step 2: Assert all eight required detections and positive controls**
- [ ] **Step 3: Run all downstream tests and the existing 43-test baseline**

Run:

```text
python -m unittest discover -s tests -p test_*.py
$env:PYTHONPATH = 'tests'
python -m unittest test_validators test_semantic_v012 test_skill_package test_evaluation_fixtures
```

- [ ] **Step 4: Validate revision 44 state/Closure, protected blob identity, schemas, JSON/JSONL, compile, and Skill package**
- [ ] **Step 5: Commit `fix: enforce downstream contract authority v0.4.1.1`**
- [ ] **Step 6: Push only the feature branch and read back remote feature/main SHAs**
