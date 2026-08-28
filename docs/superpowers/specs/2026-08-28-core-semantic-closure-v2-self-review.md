# Core Semantic Closure V2 — Self-Review Clarifications

**Status:** `APPROVED_NORMATIVE_CLARIFICATION`

**Applies to:** [`2026-08-28-core-semantic-closure-v2-design.md`](2026-08-28-core-semantic-closure-v2-design.md)

These two architectural clarifications were found during the required post-spec self-review and were accepted with the Core Semantic Closure V2 design on 2026-08-28. They are part of the frozen normative specification set and must be carried into implementation.

## 1. Approved semantic digest vs whole-file hash

V2 intentionally allows new **unconsumed evidence** to be recorded without incrementing `definition_revision` or invalidating Product Definition approval when that evidence does not change consumed product meaning.

Therefore downstream V2 must distinguish:

```text
whole state.json file hash
```

from:

```text
approved_definition_digest
```

and from exact consumed authority binding hashes.

Normative rule:

> **Downstream V2 authority validity is governed by the approved semantic definition digest plus exact consumed source/binding commitments, not by equality of the entire state.json file hash.**

The whole-file hash may still be recorded as observational provenance, but adding or changing unconsumed evidence alone must not make an otherwise unchanged approved downstream contract semantically stale.

If evidence becomes consumed by current authority, or changes a decision, contradiction, surface disposition, coverage binding, Grill Pack commitment, or other semantic input included in the approved definition digest, the normal revision/approval/stale propagation rules apply.

## 2. Deterministic migration-generated IDs

V2 migration may generate `MIGRATION_RECONCILIATION` unknowns and other required reconciliation records. Generated IDs must never collide with preserved legacy IDs.

Normative allocation rule for each generated prefix:

1. Preserve every existing stable ID unchanged.
2. Find the greatest numeric suffix already present for that prefix; use `0` when none exists.
3. Sort reconciliation generation sites by their canonical source path.
4. Allocate generated IDs monotonically from `max_existing + 1` in that canonical path order.
5. Use the V2 three-or-more-digit rendering rule, preserving leading width of at least three digits.

Example:

```text
existing: UNK-001, UNK-007, UNK-103
canonical reconciliation paths: A, B, C

generated:
A → UNK-104
B → UNK-105
C → UNK-106
```

For identical source bytes and migrator version, the same canonical paths must receive the same generated IDs and produce the same canonical migrated bytes.

## Self-review result

No other unresolved architectural contradiction was found in the written design during this pass. The two clarifications above are normative and are referenced by the design-freeze manifest and implementation plans.
