# Core Semantic Closure V2 — M6 Plan Self-Review Clarifications

**Status:** `NORMATIVE_PLAN_CLARIFICATION`

**Applies to:** `docs/superpowers/plans/2026-08-30-core-semantic-closure-v2-m6-integration-adoption.md`

Where this addendum conflicts with the M6 plan, this addendum controls. The frozen Core Semantic Closure V2 design and M1–M5 implemented contract identities remain higher authority.

## 1. Migration must not manufacture typed-object semantics merely to satisfy V2 minima

The main M6 plan says a legacy record that cannot be fully mapped may be kept as a non-current typed V2 object with a machine-recognizable scaffold. That is too permissive. A scaffold would still need values for required semantic fields and could accidentally turn “unknown” into historical-looking product meaning.

Freeze the stricter rule:

> A legacy record may enter `objects.<group>` with its original stable ID only when every required V2 semantic minimum for that type can be losslessly constructed from explicit legacy fields without product inference.

For `REQ`, `DEC`, and `UNK`, this also means any required V2 Materiality data must be explicitly supported. A legacy `material: true/false` is never sufficient by itself.

If a record cannot be promoted losslessly:

- do **not** manufacture placeholder `statement`, `scope`, Materiality axes, lifecycle values, or other semantic fields;
- do **not** create a fake STALE typed object merely to preserve the ID;
- preserve the exact source record in migration provenance as described below;
- expose the missing semantics as migration reconciliation gaps.

This clarification overrides every main-plan instruction that suggests semantic scaffold values inside normal Product Definition objects.

## 2. Preserve non-promotable legacy records exactly inside migration provenance

M6 may extend only the already-reserved top-level `migration` metadata shape of state schema `0.2.0`. This is a completion of the approved migration contract, not a new Product Definition semantic model.

Freeze migrated mode to contain deterministic provenance fields plus these two inventories:

```json
{
  "mode": "MIGRATED",
  "from_schema": "0.1.2.1",
  "to_schema": "0.2.0",
  "migration_version": "0.2.0-m6.1",
  "source_digest": "<sha256>",
  "source_revision": 44,
  "source_legacy_status": "CLOSED",
  "source_legacy_approval_digest": "<sha256-or-null>",
  "plan_digest": "<sha256>",
  "preserved_ids": ["..."],
  "promoted_ids": ["..."],
  "generated_ids": ["..."],
  "legacy_records": [
    {
      "source_id": "REQ-001",
      "source_group": "requirements",
      "source_record": {},
      "source_record_sha256": "<sha256>"
    }
  ],
  "reconciliation_gaps": [
    {
      "gap_key": "gap:<24 lowercase hex>",
      "source_id": "REQ-001",
      "source_path": "/objects/requirements/0",
      "missing_v2_fields": ["materiality"],
      "reason_code": "MISSING_V2_SEMANTIC_AUTHORITY"
    }
  ],
  "reconciliation_gap_count": 1
}
```

Rules:

- `source_record` is the exact parsed legacy JSON object, not a paraphrase.
- `source_record_sha256` is the canonical JSON hash of that exact parsed object.
- inventories are deterministically sorted.
- `gap_key` is metadata, not a canonical Product Definition stable ID.
- `preserved_ids` means the legacy stable ID is preserved either as a promoted V2 typed record with the same ID or as an exact `source_id` in `legacy_records`.
- a later reconciliation may create the canonical V2 record using that same stable ID; the immutable migration archive remains historical provenance and is not removed.
- the canonical global ID index does not treat `migration.legacy_records[].source_id` as a second authority record.
- migration provenance is excluded from `approval_v2.semantic_projection`, Product Definition definition digest, positive M4 source-seed inventory, and downstream authority.

The schema/validator changes in Task 1 are limited to validating this migrated-mode metadata. They must not alter Product object semantic minima, status enums, Materiality rules, binding rules, Approval Manifest meaning, or Closure rules.

## 3. Migration reconciliation gaps are not automatically canonical UNK records

The main plan requires a generated `UNK-*` for every migration gap. That is unsafe when the system does not yet know truthful Materiality axes for the unknown itself.

Freeze this distinction:

```text
migration.reconciliation_gaps
= explicit uncertainty discovered by deterministic migration

objects.unknowns / UNK-*
= canonical Product Definition unknown after scope + Materiality can be truthfully assessed
```

Migration apply therefore does **not** fabricate a canonical `UNK-*` merely to satisfy a gap. `generated_ids` contains only canonical records that were actually created with complete V2 semantics.

Exceptions:

- a legacy unknown may retain its existing `UNK-*` ID if all V2 required semantic fields, including Materiality and origin/provenance, can be losslessly established;
- during subsequent reverse bootstrap / Grill, a migration gap may become a canonical unknown once its Materiality and authority routing are actually assessed. When that happens, the canonical unknown's origin must point back to the exact migration `source_path`/gap key.

This is the stricter interpretation of the frozen invariant **migration may expose uncertainty but may never manufacture authority or confidence**.

The six Grill topology categories are likewise **not** populated with fake `OPEN + UNK` cells during raw migration apply. Their unresolved status is represented by migration gaps until reverse-bootstrap/Grill can create truthful canonical unknowns. The ordinary M3 Grill validator may therefore report expected reconciliation blockers before that later step.

## 4. A migration candidate may be semantically unready, but never structurally unexplained

`--apply` is allowed to produce a V2 reconciliation candidate that is not yet valid for Semantic Closure and may still produce V2 semantic validation blockers.

However:

- the JSON must satisfy the state `0.2.0` structural schema, including the migrated-mode migration metadata;
- `verify_migration_result()` must report zero migration-integrity errors;
- every semantic validation failure caused by information lost across the contract boundary must have a deterministic matching `migration.reconciliation_gaps` entry;
- no unexpected/unattributed validation failure is allowed;
- `evaluate_closure_v2(candidate).closed` must be false;
- candidate approval must be `UNAPPROVED`;
- migration apply must never build an Approval Manifest or downstream V2 contract.

Tests must compare the validator error inventory against reconciliation-gap coverage rather than weakening validators so the migrated candidate looks complete.

## 5. Full legacy migration proof and CLOSED dogfood are separate evidence tracks

The main plan implied that the full legacy portal migration candidate could then be trimmed/reconciled into the selected dogfood slice and closed. That creates pressure to silently discard or mark unrelated legacy product areas out of scope without product authority.

Do not do that.

Freeze two separate M6 evidence tracks:

### Track A — Full legacy migration audit

Apply migration to the complete historical source:

```text
product-definition/client-feedback-portal-dogfood/
```

Store the full OPEN reconciliation candidate and receipt under:

```text
evals/core-semantic-closure-v2-m6/dogfood/migration/
```

This candidate is expected to remain OPEN. Its purpose is to prove:

- source preservation;
- stable-ID preservation;
- no approval promotion;
- no coverage confidence increase;
- deterministic gap exposure.

Do **not** force this full candidate to V2 Closure in M6.

Freeze the untouched historical source tree at M5:

```text
product-definition/client-feedback-portal-dogfood/
= 22f8c2ccb8f9d77e54867c44dbdbcea63e42a052
```

and especially:

```text
product-definition/client-feedback-portal-dogfood/state.json
= 44a29cc4ecb7a8772b6441d73d7a7acb52188e6e
```

### Track B — Existing-product bounded V2 dogfood

Create the V2 dogfood state from the native V2 template with:

```text
bootstrap_mode = EXISTING_PRODUCT_RECONCILIATION
```

It defines one coherent, bounded existing-product workflow unit selected from the legacy portal's documented intent. It is **not** represented as the completed migration of the whole legacy portal.

All meaning promoted into this state must come from first-class evidence records referencing the historical docs/user decisions or from explicit current user answers. Do not mark omitted legacy product areas `OUT_OF_SCOPE` merely because they are outside the evaluation unit.

The Approval Manifest shown to the user must make this bounded dogfood scope explicit. Product Definition Closure then means “this bounded V2 workflow definition is closed,” not “the entire historical client-feedback portal has been fully migrated.”

This split satisfies both M6 requirements honestly: migration is proven without manufactured closure, and one coherent existing-product V2 definition runs through the full native V2 lifecycle.

## 6. Runtime conformance requires explicit evidence coverage, not merely all supplied records passing

The main plan says all required runtime evidence must be present but does not freeze how completeness is calculated. Without that rule, an implementation could submit one passing record and appear globally conformant.

Freeze action coverage:

- every action contract contains `fields.test_obligations.value`;
- to be runtime-executable for full-contract verification, this value must be a non-empty array of unique nonblank stable test IDs;
- every required test ID must match at least one admitted `joewrks.downstream.execution/1.0` record's `test_id` for that exact action;
- unexpected/duplicate conflicting evidence for the same `(action_id, test_id)` is invalid unless byte-identical duplicates are explicitly deduplicated deterministically;
- all required records must pass semantic verification.

Report exact inventories:

```text
required_action_test_ids
observed_action_test_ids
missing_action_test_ids
unexpected_action_test_ids
```

A report with any missing required action evidence cannot be `IMPLEMENTATION_CONFORMANT`.

## 7. Lifecycle evidence must fail closed when full verification inventory is unavailable

The M5 lifecycle contract does not contain a `test_obligations` field. M6 must not invent that field or silently modify `joewrks.action-conformance/2.0` merely to complete the dogfood.

Freeze the rule:

- `verify_lifecycle_execution()` may verify individual explicitly supplied lifecycle observations against structured lifecycle field values;
- the runtime report must state whether lifecycle coverage is `NOT_APPLICABLE`, `FULL`, or `INCOMPLETE`;
- `NOT_APPLICABLE` is valid only when the contract has zero lifecycle items;
- `FULL` requires the verifier to derive a deterministic complete case inventory from structured lifecycle authority without interpretation and to observe every derived required case;
- if a complete case inventory cannot be derived from the existing lifecycle values, coverage is `INCOMPLETE` and global `IMPLEMENTATION_CONFORMANT` is forbidden;
- prose or ambiguous lifecycle semantics return `RUNTIME_CONTRACT_NOT_EXECUTABLE`, never a guessed case inventory.

The dogfood may legitimately compile with zero lifecycle items if its selected downstream authority is completely represented by action obligations. Do not add a fake lifecycle just to exercise the API. Lifecycle unit tests must still cover the supported structured verifier path.

If later work needs a richer lifecycle test-obligation contract, that requires a separately versioned contract change after M6; M6 does not silently add one.

## 8. Runtime status distinguishes full-contract conformance from partial probes

Add these report fields:

```text
verification_scope:
  FULL_CONTRACT | PARTIAL_PROBE

coverage_status:
  COMPLETE | INCOMPLETE
```

Only:

```text
verification_scope = FULL_CONTRACT
coverage_status = COMPLETE
contract_dependency_status = CONFORMANT
runtime_status = CONFORMANT
```

plus the existing semantic-review/re-entry conditions may produce:

```text
implementation_status = IMPLEMENTATION_CONFORMANT
```

A partial controlled drift/re-entry probe must use:

```text
verification_scope = PARTIAL_PROBE
```

and may never produce global `IMPLEMENTATION_CONFORMANT`, even if that probe itself passes.

This prevents the final M6 evidence from conflating “we tested the path” with “all obligations in this contract were verified.”

## 9. Reuse of `joewrks.downstream.execution/1.0` is a binding profile, not a redefinition

M6 must document an **execution binding profile**, not publish a new execution protocol identity.

The profile states:

```text
frozen execution record field contract_hash
→ for a V2 verification run, equals action-conformance/2.0 semantic_contract_hash

frozen authority.approved_digest
→ for a V2 verification run, equals source_authority.approved_definition_digest
```

This is an admission rule imposed by the V2 verifier on already-valid protocol-1.0 records. It does not change the frozen schema bytes or general meaning of the v1 transport.

Add tests proving:

1. the record is first valid under frozen `joewrks.downstream.execution/1.0`;
2. then V2 admission applies the stricter contract/digest equality rules;
3. no old downstream v1 code/schema file changes.

## 10. Dogfood approval timestamp is supplied by the PM continuation, never invented by the implementation agent

At the mandatory Task-5 checkpoint the state remains `UNAPPROVED`.

After the user explicitly approves, the continuation instruction must supply:

```text
approved_by = user
approved_at = <explicit UTC timestamp supplied with the approval continuation>
approved_manifest_digest = <exact checkpoint digest>
```

The implementation agent must not call the wall clock, use commit time, infer chat time, or synthesize a timestamp itself.

If the user merely says `ㄱㄱ`, the coordinating assistant resolves the approval time in the user's actual current timezone and passes an explicit UTC value to the continuation. The implementation worker receives the value; it does not generate it.

## 11. The user approval checkpoint splits M6 execution into two runs

A single Codex execution must **not** run Task 5 Phase A and Phase B back-to-back.

### First M6 execution

May run:

```text
Task 1
Task 2
Task 3
Task 4
Task 5 Phase A through manifest compilation
```

Then it must emit:

```text
CORE_SEMANTIC_CLOSURE_V2_M6_APPROVAL_REQUIRED
— DOGFOOD_V2_MANIFEST_READY
```

and stop with dogfood approval still UNAPPROVED.

It may make local commits for completed Tasks 1–4 and Phase-A evidence, but it must not report M6 complete and must not push a final M6 implementation result as if approved.

### Second M6 execution

Starts only after the coordinating user explicitly approves the exact manifest digest and the continuation supplies the exact approval timestamp. It performs Phase B, Task 6, final review, and only then may push/report final M6.

## 12. Dogfood Product Definition authority must not be copied from historical observed behavior

The historical legacy state and Markdown may support `DOCUMENTED_INTENT` / `HISTORICAL_DECISION` evidence where they actually record intended product meaning.

Historical runtime/evaluation artifacts may support `OBSERVED_IMPLEMENTATION`, `OBSERVED_RUNTIME`, or `TEST_ASSERTION` evidence only.

Do not relabel implementation/evaluation output as intent simply because it is convenient for closing the dogfood.

Where historical documentation and observed behavior conflict, create a contradiction and resolve it under ordinary V2 authority rules. Where neither source establishes a material preference, stop for user judgment.

## 13. Final M6 claims are scope-accurate

`RUNTIME_CONFORMANCE_PATH_VERIFIED` means the V2 runtime verifier was exercised end-to-end and the final dogfood contract received complete evidence for its own contract obligations.

It does **not** mean every product ever using JOEWRKS has been runtime-verified.

`R1_R10_INTEGRATION_VERIFIED` means each redesign remediation has implementation, regression and M6 evidence. It does not erase explicitly preserved limitations, including:

```text
semantic-review/2.0 reliability = NOT_MEASURED
full historical client-feedback portal migration = OPEN reconciliation candidate, not claimed CLOSED
production deployment = NOT_CLAIMED
main merge = NOT_PERFORMED
```

No wording in README, architecture docs, dogfood summaries or final report may broaden these claims.

## 14. Self-review result

With these clarifications, the known M6 escape hatches are closed:

- migration cannot create fake semantic placeholders;
- uncertainty can exist explicitly without fabricated Materiality;
- full legacy migration is not falsely equated with a closed bounded dogfood;
- partial runtime evidence cannot produce global conformance;
- lifecycle evidence fails closed when completeness cannot be derived;
- execution/1.0 remains frozen transport rather than silently becoming a V2 protocol;
- the user approval checkpoint cannot be auto-completed;
- historical implementation evidence cannot be promoted to intent.

Execution must read the frozen design, M5 remote-source audit, the M6 main plan, and this addendum before coding.