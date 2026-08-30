# Core Semantic Closure V2 — M5.1 Executability Implementation Plan Self-Review

**Status:** `NORMATIVE_PLAN_CLARIFICATION`

**Applies to:** `docs/superpowers/plans/2026-08-30-core-semantic-closure-v2-m5-1-executability-remediation.md`

Where this clarification conflicts with the implementation plan, this clarification controls. The approved M5.1 design self-review and design remain higher authority.

---

## 1. Self-review result

The plan covers the approved architecture, but fresh-eye review found four implementation-level gaps that must be fixed before execution:

1. action-conformance/2.1 needs its own dependency-scoped drift audit, not only a compiler;
2. lifecycle runtime cases need an exact executable mapping shape;
3. M5 source seeds do not carry an independent evidence `authority_class`, so M5.1 must not fabricate one to satisfy design wording;
4. dogfood `verification_basis` selection must not become an automatic “take every eligible seed” shortcut.

The clarifications below are normative for implementation.

---

## 2. Add action-conformance/2.1 dependency-scoped audit

Add to the Task-2 file map:

```text
skills/joewrks-product-definition/downstream_v21/audit.py
tests/test_downstream_v21_audit.py
```

Required interface:

```python
def audit_action_contract_v21_against_state(
    contract: dict[str, object],
    current_state: dict[str, object],
) -> dict[str, object]: ...
```

Result shape:

```python
{
    "status": "CONFORMANT|REENTRY_REQUIRED|DEFINITION_NOT_READY",
    "authority_revision_relation": "SAME_APPROVED_REVISION|OLDER_APPROVED_REVISION_UNAFFECTED|NOT_APPLICABLE",
    "affected_consumers": [...],
    "semantic_gaps": [...],
    "errors": [...],
}
```

### Audit semantics

Initial compilation still requires actual Product Definition Closure.

Existing-contract audit does **not** require the current whole Product Definition to remain CLOSED. Preserve M5 dependency-local semantics:

- safely validate/index current state;
- rebuild current positive seed inventory without requiring global Closure;
- verify every consumed 2.1 source seed at its exact location/value;
- verify every REQ/SURF/SCR scope commitment;
- map changed dependencies to exact actions/lifecycles, including `verification_basis` consumers;
- unrelated newer Product Definition revision or unconsumed evidence does not stale the contract;
- local used-seed/scope drift returns `REENTRY_REQUIRED` with `AFFECTED_ONLY` semantics at M6 integration;
- malformed duplicate IDs/unsafe semantic projection returns `DEFINITION_NOT_READY` fail-closed.

The original approved definition/manifest digests remain contract source provenance and are not rewritten during audit.

Add Task-2 tests:

```python
def test_v21_audit_unrelated_newer_open_revision_remains_conformant(): ...
def test_v21_audit_used_field_seed_drift_requires_affected_reentry(): ...
def test_v21_audit_verification_basis_seed_drift_requires_affected_reentry(): ...
def test_v21_audit_scope_commitment_drift_requires_affected_reentry(): ...
def test_v21_audit_unconsumed_evidence_change_does_not_stale_contract(): ...
def test_v21_audit_duplicate_id_fails_closed_definition_not_ready(): ...
```

Include `tests.test_downstream_v21_audit` in every Task-2+, final focused and regression command.

---

## 3. Do not fabricate a source-seed authority class

The approved design says every collected seed must satisfy the target field's authority class. The frozen M5 source-seed record shape contains location, record ID/type, pointer, current status, hash and value; it does **not** carry a separate evidence authority-class tag.

M5.1 must not invent or infer such a tag from prose, record names, or implementation behavior.

Freeze the operational interpretation:

```text
required_authority_class
= the authority class required when a semantic field is unresolved and must route back to Product Definition

positive source-seed admissibility
= current exact M4 positive binding
  + permitted field selector
  + exact action/lifecycle scope
  + exact UX locator where applicable
  + frozen binding-contract type restrictions already embodied by the seed location
```

This preserves M5's epistemic boundary without creating a new hidden authority classification system.

If a future downstream version requires independently class-tagged source seeds, that requires a separately versioned seed/contract change; M5.1 does not guess it.

`collect_exact` still requires every member independently pass this exact admissibility test.

---

## 4. `verification_basis` is selected explicitly, never auto-filled from all eligible authority

The plan correctly puts `verification_basis` in handoff-definition/2.1 as source refs only. Freeze that choice.

The compiler must **not** discover every eligible outcome/acceptance seed and automatically consume all of them. Eligibility does not prove relevance to a particular action.

Rules:

- handoff-definition/2.1 supplies the exact basis refs;
- compiler only validates and normalizes them;
- basis contains no values/literals;
- every ref must match the action's exact scope/selectors;
- both basis arrays must be nonempty for a production 2.1 action;
- no unused basis ref may remain in the production contract;
- the runtime plan may use only basis refs committed by that action.

### Dogfood replay selection

When mechanically translating the stopped M6 dogfood:

1. first reuse exact source refs already present in successful 2.0 field derivations where those refs satisfy the 2.1 basis selectors;
2. then use exact candidate/basis refs explicitly preserved in the 2.0 stopped evidence if present;
3. if an additional exact eligible ref is required, the implementation audit must record the source location and why it is action-relevant based solely on already-approved action scope/acceptance authority;
4. if choosing among multiple semantically different eligible refs would require a product judgment, stop with `TRUE_SEMANTIC_GAP_FOUND`.

Never use “all matching refs” as a shortcut.

---

## 5. Freeze the exact lifecycle runtime case shape

Task 4 must support lifecycle plans with this normalized shape:

```python
{
    "lifecycle_id": "...",
    "covered_contract_field_refs": [...],
    "cases": [
        {
            "case_id": "CASE-<24hex>",
            "test_id": "TEST-<24hex>",
            "transition_expectation": {
                "from_state_source": {
                    "source": "CONTRACT_DERIVED",
                    "contract_field_path": "lifecycles/<lifecycle_id>/current_states",
                    "pointer": "/..."
                },
                "to_state_source": {
                    "source": "CONTRACT_DERIVED",
                    "contract_field_path": "lifecycles/<lifecycle_id>/allowed_transitions",
                    "pointer": "/..."
                },
                "contract_field_refs": [...]
            },
            "component_expectations": [...],
            "evidence_assertions": [...],
            "fixture_requirements": [...],
            "contract_field_refs": [...]
        }
    ]
}
```

Rules:

- lifecycle state/transition product values are always `CONTRACT_DERIVED`;
- `FIXTURE_ONLY` may supply opaque object IDs, ordering timestamp or revision instances but never state names or transition policy;
- every lifecycle runtime-critical field must be covered by a concrete transition/component/assertion relationship for lifecycle coverage `FULL`;
- an `ANY` relationship never covers its linked semantic field;
- if a complete lifecycle mapping cannot be constructed without product inference, runtime-plan coverage is `INCOMPLETE` with `RUNTIME_MAPPING_GAP`;
- zero lifecycle items is the only route to lifecycle `NOT_APPLICABLE` later in M6 runtime reporting.

Add tests:

```python
def test_lifecycle_state_values_must_be_contract_derived(): ...
def test_lifecycle_bare_ref_does_not_count_as_coverage(): ...
def test_lifecycle_complete_concrete_mapping_reaches_full_plan_coverage(): ...
def test_lifecycle_ambiguous_mapping_remains_runtime_mapping_gap(): ...
```

---

## 6. Runtime-plan hashes bind review completion exactly

For Task 4, `review_commitments.output_hash` is:

```python
sha256_json(validated_semantic_review_output)
```

when an output exists, otherwise `null`.

`package_hash` is the validated semantic-review/2.1 package's own `package_hash`, otherwise `null`.

Any change in package/output identity changes runtime `plan_hash` and therefore invalidates an old runtime-evidence bundle.

A runtime-critical REVIEW_REQUIRED field can count as covered only when the exact validated output for its obligation is `CONFIRMED_INTERPRETATION`.

Review completion remains separate from reliability:

```text
reliability_status = NOT_MEASURED
```

---

## 7. Runtime-evidence bundle does not reinterpret execution/1.0

The `joewrks.runtime-evidence-bundle/1.0` decision in the plan is accepted as the transport-preserving envelope required by the design.

It contains exact parsed frozen execution/1.0 records and binds them externally to the runtime plan hash. The bundle must not add fields inside an execution record.

Each planned test ID is globally unique within one runtime plan; this lets the bundle map a record to its action/lifecycle case without adding `action_id` to the frozen transport.

The bundle validator rejects duplicate `test_id` records rather than inventing last-write/merge semantics.

---

## 8. Plan identity and cross-version validation

2.1 validators must be self-consistent and cross-version strict:

- 2.0 action contract does not validate as 2.1;
- 2.1 action contract does not validate as 2.0;
- 2.0 handoff does not validate as 2.1;
- 2.1 handoff does not validate as 2.0;
- semantic-review 2.0 and 2.1 packages/outputs are mutually rejected by identity;
- runtime plan requires action-conformance/2.1 exactly;
- runtime evidence bundle requires runtime-conformance-plan/1.0 exactly.

The final M5.1 source review must explicitly verify all six boundaries.

---

## 9. M5.1 dogfood replay is a mandatory local integration gate, not a committed copy of M6 authority

The implementation branch must not commit the M6 canonical approved `state.json` as a second authority.

`tests/test_downstream_v21_dogfood_replay.py` reads the preserved M6 worktree read-only when `JOEWRKS_M6_PHASE_B_WORKTREE` is supplied and builds temporary/in-memory replay artifacts.

Committed M5.1 evaluation documents may record hashes, counts, contract identities and the old/new outcomes, but they must not create another canonical Product Definition authority file.

The final success label `M6_RESUME_READY` is forbidden unless the external dogfood replay actually ran and passed in the final verification session.

---

## 10. Placeholder / consistency review

Placeholder scan of the implementation plan found no `TODO`, `TBD`, `implement later`, or unnamed code interfaces.

Type/interface corrections from this self-review are:

- add `audit_action_contract_v21_against_state()` and its tests;
- add exact lifecycle case shape;
- define review `output_hash` computation;
- clarify source-seed authority-class handling;
- make dogfood basis selection explicit and relevance-audited.

All implementation tasks remain one architecture: exact semantic handoff 2.1 + non-authoritative runtime mapping + frozen transport.

---

## 11. Final plan invariant

> **M5.1 may evolve how approved meaning is carried and verified, but it may not manufacture a new kind of authority in order to make that evolution convenient.**
