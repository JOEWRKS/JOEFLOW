# Adding a feature to an existing product

State 0.2.0 has two bootstrap modes. `EXISTING_PRODUCT_RECONCILIATION` is for a legacy
definition being migrated: every surface must say how observed behaviour relates to intent
(`intent_classification`). That is the wrong question when the product already runs and the
plan is only about what changes. Plan an extension as `NEW_PRODUCT` scoped to the change,
with the existing product as evidence:

1. **Scope** the surfaces, requirements and screens to what is new or changed. Screens the
   change does not touch do not appear; screens it touches get their UX row as usual.
2. **Observe** the existing behaviour the change must keep and record it as evidence
   (`OBSERVED_IMPLEMENTATION`, `OBSERVED_RUNTIME` or `TEST_ASSERTION`, with the locator).
3. **Declare the baseline** once with `new_records.py --patch PATCH baseline`: it writes one
   requirement "existing behaviour stays", one rule listing the behaviours, one acceptance
   criterion (the existing checks that must still pass), the surface that owns them and the
   Core row, whose `default_authority` is the rule, so only `goal`, `happy_path` and
   `acceptance` are written by hand. Pass `--task` so the Approval Manifest can map the
   requirement to its delivery. Apply with `open_revision.py` like any patch.

```text
python <skill-directory>/scripts/new_records.py --patch rev41-patch.json evidence --id EVD-041 \
  --source-kind OBSERVED_RUNTIME --class BEHAVIORAL --locator "app v1.3 (2026-10-31), tests/e2e" \
  --claim "Undo, new game and the start screen behave as the e2e suite asserts"
python <skill-directory>/scripts/new_records.py --patch rev41-patch.json baseline \
  --requirement REQ-006 --rule RULE-047 --acceptance AC-046 --surface SURF-005 --goal GOAL-001 \
  --evidence EVD-041 --task TASK-004 --check "the existing e2e suite passes unchanged" \
  --behavior "undo restores the previous position" --behavior "new game asks before discarding"
```

The baseline requirement is ordinary authority. It is part of the approved definition and
its digest, so deciding later that a listed behaviour should change is a revision of the
rule and a new approval, never a silent edit. When the handoff definition names the
requirement (or its surface) in an action's `authority_scope_refs`, the compiled 2.1
contract pins that record under `scope_commitments` and `audit_downstream_v2.py` reports a
contract whose commitments no longer match the state. Whether the implementation kept the
behaviour is proved by the acceptance criterion, the existing checks, not by the compiler.

What this does not do: it adds no bootstrap mode or surface field. A `FEATURE_EXTENSION`
mode with per-surface `change_kind` (NEW, CHANGED, BASELINE) would need a schema version
and would stale every approval (the definition digest includes the schema version); the
convention above gets the two things the mode was for, scoped coverage and an enforceable
list of preserved behaviour, inside 0.2.0.
