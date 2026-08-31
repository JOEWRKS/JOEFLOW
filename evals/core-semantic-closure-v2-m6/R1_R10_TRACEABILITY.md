# Core Semantic Closure V2 M6 — R1–R10 traceability

This matrix binds every frozen remediation item to production code, executable
tests, and committed M6 evidence. A specification or this matrix is context
only; no row is supported by documentation alone.

The status in this file is deliberately two-part:

- `VERIFIED` means the listed implementation, tests, and M6 artifacts exist
  and their focused verification passed.
- `FINAL_GATE_PASS` means the fresh repository-wide regression, exact frozen
  identity readback, and independent 0/0/0 review required by continuation
  Steps 15–17 passed. It is a feature-branch readiness claim, not a production
  deployment or main-merge claim.

| ID | Requirement | Implemented production files | Test files | Dogfood / evidence artifacts | Status | Known limitation |
| --- | --- | --- | --- | --- | --- | --- |
| R1 — Semantic Closure Contract | State `0.2.0` may close only when the typed semantic/readiness, binding, discovery, and approval blockers are zero. | `skills/joewrks-product-definition/schemas/state-v0.2.0.schema.json`<br>`skills/joewrks-product-definition/scripts/state_validation_v2.py`<br>`skills/joewrks-product-definition/scripts/state_contract_dispatch.py`<br>`skills/joewrks-product-definition/scripts/validate_closure.py` | `tests/test_state_v020_foundation.py`<br>`tests/test_semantic_closure_v020.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_b.py` | `dogfood/product-definition/client-feedback-portal-dogfood-v2/state.json`<br>`dogfood/final-state.json`<br>`dogfood/approval-manifest.json` | `VERIFIED / FINAL_GATE_PASS` | Closure is proven for the bounded revision-1 dogfood definition, not for the full historical portal or every future product. |
| R2 — Definition Surface | Discovered material surfaces must be dispositioned and bound; the discovery baseline commits the surface inventory without claiming unknown-unknown exhaustiveness. | `skills/joewrks-product-definition/scripts/discovery_v2.py`<br>`skills/joewrks-product-definition/scripts/build_discovery_baseline.py`<br>`skills/joewrks-product-definition/scripts/state_validation_v2.py` | `tests/test_surface_manifest_v020.py`<br>`tests/test_discovery_baseline_v020.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py` | `dogfood/final-state.json`<br>`dogfood/phase-a-evidence-map.json` | `VERIFIED / FINAL_GATE_PASS` | Track B covers one coherent existing-product unit; omitted historical portal areas are not silently declared out of scope. |
| R3 — Evidence Graph | Evidence is typed, commitment-bound, authority-class constrained, and consumed explicitly instead of treating implementation as intent. | `skills/joewrks-product-definition/scripts/discovery_v2.py`<br>`skills/joewrks-product-definition/scripts/state_validation_v2.py`<br>`skills/joewrks-product-definition/scripts/approval_v2.py` | `tests/test_evidence_v020.py`<br>`tests/test_authority_consumption_v020.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py` | `dogfood/final-state.json`<br>`dogfood/phase-a-evidence-map.json`<br>`dogfood/action-contract-v21.json` | `VERIFIED / FINAL_GATE_PASS` | Repository-backed intent and explicit current user decisions are proven for this fixture; production evidence-drift monitoring is not claimed. |
| R4 — Decision Integrity | Unknown resolution, decisions, contradictions, affected authority, and provenance must remain explicit and semantically non-empty. | `skills/joewrks-product-definition/scripts/grill_v2.py`<br>`skills/joewrks-product-definition/scripts/state_validation_v2.py`<br>`skills/joewrks-product-definition/scripts/approval_v2.py` | `tests/test_unknown_resolution_v020.py`<br>`tests/test_contradictions_v020.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py` | `dogfood/final-state.json`<br>`dogfood/approval-manifest.json`<br>`dogfood/reentry-probe-v21.json` | `VERIFIED / FINAL_GATE_PASS` | The three bounded current user decision sets remain fixture-scoped and are not universal JOEWRKS policy. |
| R5 — Materiality & Autonomy | Materiality and decision authority determine when the agent may act and when a material choice must be returned to the user. | `skills/joewrks-product-definition/scripts/materiality_v2.py`<br>`skills/joewrks-product-definition/scripts/grill_v2.py`<br>`skills/joewrks-product-definition/scripts/next_product_question.py`<br>`skills/joewrks-product-definition/scripts/state_validation_v2.py` | `tests/test_materiality_v020.py`<br>`tests/test_autonomy_policy_v020.py`<br>`tests/test_question_policy_v020.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py` | `dogfood/final-state.json`<br>`dogfood/approval-manifest.json` | `VERIFIED / FINAL_GATE_PASS` | Deterministic policy and the bounded approval checkpoint are exercised; no production autonomy or deployment claim is made. |
| R6 — Reverse Bootstrap | Existing implementation is evidence, not automatic intent; migration preserves source meaning and exposes unresolved reconciliation without manufacturing V2 authority. | `skills/joewrks-product-definition/scripts/discovery_v2.py`<br>`skills/joewrks-product-definition/scripts/migration_v2.py`<br>`skills/joewrks-product-definition/scripts/migrate_state.py` | `tests/test_reverse_bootstrap_v020.py`<br>`tests/test_migration_v020_foundation.py`<br>`tests/test_migration_v020_apply.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py` | `dogfood/migration/legacy-candidate.json`<br>`dogfood/migration/migration-receipt.json`<br>`MIGRATION_AUDIT.md` | `VERIFIED / FINAL_GATE_PASS` | Track A preserves 269/269 IDs and exposes 1,151 gaps, but remains `OPEN`/`UNAPPROVED`; Track B does not close or replace it. |
| R7 — Informed Approval | Approval binds the exact semantic definition and deterministic Approval Manifest, with one immutable revision commitment and no synthesized approval. | `skills/joewrks-product-definition/scripts/approval_v2.py`<br>`skills/joewrks-product-definition/scripts/build_approval_manifest.py`<br>`skills/joewrks-product-definition/scripts/state_validation_v2.py` | `tests/test_approval_manifest_v020.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_b.py` | `dogfood/approval-manifest.json`<br>`dogfood/final-state.json`<br>`DOGFOOD_RUNBOOK.md` | `VERIFIED / FINAL_GATE_PASS` | Approval applies only to bounded definition revision 1 and does not approve implementation deployment or the unresolved Track-A migration. |
| R8 — Adaptive Grill Packs | Topology activates versioned Core/specialist packs; triggered axes must be covered or truthfully open/N/A and cannot be silently suppressed. | `skills/joewrks-product-definition/scripts/grill_v2.py`<br>`skills/joewrks-product-definition/references/grill-packs/core.json`<br>`skills/joewrks-product-definition/references/grill-packs/auth.json`<br>`skills/joewrks-product-definition/references/grill-packs/permission.json`<br>`skills/joewrks-product-definition/references/grill-packs/async.json` | `tests/test_grill_packs_v020.py`<br>`tests/test_grill_binding_v020.py`<br>`tests/test_grill_baseline_v020.py`<br>`tests/test_core_semantic_closure_v2_m6_dogfood_phase_a.py` | `dogfood/final-state.json`<br>`dogfood/phase-a-evidence-map.json` | `VERIFIED / FINAL_GATE_PASS` | The active set is Core/Auth/Permission/Async for this topology; it is not evidence that every specialist pack or future topology was exercised. |
| R9 — Semantic Debt Reduction | Downstream must distinguish missing product meaning from contract vocabulary limits and from missing executable runtime mapping; review cannot absorb an upstream authority gap. | `skills/joewrks-product-definition/downstream_v21/compiler.py`<br>`skills/joewrks-product-definition/downstream_v21/gaps.py`<br>`skills/joewrks-product-definition/downstream_v21/contracts.py`<br>`skills/joewrks-product-definition/downstream_v21/runtime_plan.py`<br>`skills/joewrks-product-definition/integration_v2/dogfood_v21.py` | `tests/test_downstream_v21_compiler.py`<br>`tests/test_downstream_v21_gap_routing.py`<br>`tests/test_downstream_v21_runtime_plan.py`<br>`tests/test_downstream_v21_dogfood_replay.py` | `dogfood/action-contract-v21.json`<br>`dogfood/runtime-conformance-plan.json`<br>`dogfood/reentry-probe-v21.json` | `VERIFIED / FINAL_GATE_PASS` | `SEMANTIC_AUTHORITY_GAP` re-enters Product Definition; `CONTRACT_EXPRESSIVENESS_GAP` evolves the 2.1 semantic contract; `RUNTIME_MAPPING_GAP` repairs non-authoritative `runtime-conformance-plan/1.0`. Semantic-review/2.1 reliability remains `NOT_MEASURED`. |
| R10 — Lifecycle / Migration / Re-entry Integration | Preserve lifecycle/history, migrate without increasing confidence, route affected-only semantic re-entry, and verify actual runtime evidence through the 2.1 contract/runtime-plan boundary. | `skills/joewrks-product-definition/scripts/migration_v2.py`<br>`skills/joewrks-product-definition/downstream_v21/audit.py`<br>`skills/joewrks-product-definition/downstream_v21/gaps.py`<br>`skills/joewrks-product-definition/integration_v2/runtime_v21.py`<br>`skills/joewrks-product-definition/integration_v2/runtime_report.py`<br>`skills/joewrks-product-definition/references/reentry-workflow-v0.2.0.md` | `tests/test_migration_v020_apply.py`<br>`tests/test_downstream_v21_audit.py`<br>`tests/test_v2_reentry_workflow_contract.py`<br>`tests/test_m6_client_feedback_portal_fixture.py`<br>`tests/test_m6_runtime_v21_verification.py` | `dogfood/migration/legacy-candidate.json`<br>`dogfood/migration/migration-receipt.json`<br>`dogfood/runtime-evidence-bundle.json`<br>`dogfood/runtime-conformance-report.json`<br>`dogfood/implementation-drift-probe.json`<br>`dogfood/reentry-probe-v21.json` | `VERIFIED / FINAL_GATE_PASS` | The dogfood has zero lifecycle items, so runtime lifecycle is truthfully `NOT_APPLICABLE`; full historical client-feedback migration remains an `OPEN` reconciliation candidate. |

## R9/R10 layer boundary

The three gap classes are not interchangeable:

```text
SEMANTIC_AUTHORITY_GAP
  product meaning is missing/conflicting/stale/unauthorized
  → affected-only Product Definition re-entry

CONTRACT_EXPRESSIVENESS_GAP
  eligible approved meaning exists but action-conformance/2.1 cannot carry it
  → contract evolution; no Product Definition revision by itself

RUNTIME_MAPPING_GAP
  action-conformance/2.1 is valid but executable coverage is incomplete
  → runtime-conformance-plan/1.0 remediation; no Product Definition revision by itself
```

`joewrks.action-conformance/2.1` carries approved product semantics.
`joewrks.runtime-conformance-plan/1.0` is digest-bound verification metadata and
must not read Product Definition directly or become shadow product authority.
The controlled 2.1 re-entry probe produces exactly one
`SEMANTIC_AUTHORITY_GAP`; the final plan has zero runtime-mapping gaps.

## Migration boundary

Track A is a complete deterministic migration audit, not a completed product
reconciliation. Its full historical client-feedback reconciliation remains an
`OPEN` candidate. Track B is the separate bounded native V2 dogfood; its
approval and runtime result neither close nor replace Track A.
