# Core Semantic Closure V2 — M2 Plan Self-Review Clarifications

**Status:** `NORMATIVE_PLAN_CLARIFICATION`

**Applies to:** `docs/superpowers/plans/2026-08-28-core-semantic-closure-v2-m2-discover-authority.md`

This addendum records three execution-critical clarifications found during the required plan self-review. Where this file conflicts with the M2 plan, this file controls. The frozen Core Semantic Closure V2 design remains the higher authority.

## 1. Candidate-only evidence includes unapproved design artifacts

The M2 plan originally listed only `INFERRED_INTENT` as candidate-only evidence. That is too permissive for `DESIGN_ARTIFACT`: merely observing a design file does not prove that the user approved it as current product intent.

Use the source-kind capability matrix from Task 1, but freeze candidate-only source kinds as:

```python
CANDIDATE_ONLY_SOURCE_KINDS = {
    "INFERRED_INTENT",
    "DESIGN_ARTIFACT",
}
```

Consequences:

- `DESIGN_ARTIFACT` may declare `INTENT` or `PREFERENCE` as the class of claim it appears to express.
- It may not independently satisfy a closure-authority requirement merely because the artifact exists.
- A design becomes current authoritative intent only when corroborated by a closure-eligible authority source such as `USER_CONFIRMED_INTENT` or qualifying `DOCUMENTED_INTENT`, or when a current explicit decision supplies the authority.
- Reverse-bootstrap `AUTHORITATIVE` classification must reject a surface whose only intent-like evidence is `DESIGN_ARTIFACT` and/or `INFERRED_INTENT`.

Add explicit Task-1 and Task-4 RED tests for this rule.

## 2. Contradiction selected authority uses class-independent closure eligibility

Task 3 says `selected_authority_refs` must be closure-capable but a contradiction may concern different claim classes, so there is no single fixed `authority_class` argument that can be supplied to `_evidence_can_support`.

Add this internal helper in Task 1:

```python
def _evidence_is_current_closure_eligible(record: dict[str, Any]) -> bool:
    if record.get("status") != "CURRENT":
        return False
    if record.get("source_kind") in CANDIDATE_ONLY_SOURCE_KINDS:
        return False
    classes = record.get("authority_classes")
    return (
        isinstance(classes, list)
        and bool(classes)
        and all(isinstance(item, str) for item in classes)
    )
```

`_evidence_can_support(record, authority_class, for_closure=True)` remains the class-specific helper used when a consumer requires `INTENT`, `PREFERENCE`, `FACTUAL`, `CONSTRAINT`, or `BEHAVIORAL`.

Task 3 `selected_authority_refs` uses `_evidence_is_current_closure_eligible` plus reference integrity. It does **not** invent an arbitrary required claim class.

Add RED tests proving:

- current non-candidate evidence can be selected;
- stale/superseded/unavailable evidence cannot be selected;
- `DESIGN_ARTIFACT` and `INFERRED_INTENT` cannot be selected as the sole resolving authority;
- a current `DEC-*` in `resolved_by` remains a valid alternative resolution path.

## 3. Baseline regeneration must bypass only baseline-freshness validation

Task 5 originally says the baseline CLI should “validate the current state” before computing a replacement baseline. Once stored baseline freshness itself is part of `validate_state_v2`, that creates a cycle: a stale baseline would make the state invalid, which would prevent the tool that exists to regenerate the stale baseline from running.

Do not weaken normal `validate_state_v2`.

Refactor V2 validation into an internal shared entrypoint:

```python
def _validate_state_v2(
    state: dict[str, Any],
    *,
    check_discovery_baseline: bool,
) -> list[dict[str, str]]:
    ...


def validate_state_v2(state: dict[str, Any]) -> list[dict[str, str]]:
    return _validate_state_v2(state, check_discovery_baseline=True)
```

`build_discovery_baseline.py` validates its input with:

```python
_validate_state_v2(state, check_discovery_baseline=False)
```

This bypass is **only** for stored baseline freshness/commitment comparison. Evidence, surfaces, contradictions, reverse-bootstrap classification, typed authority, lifecycle, global IDs, schema shape, and every other M2/M1 rule still run normally.

Freeze discovery-baseline statuses as:

```text
NOT_ESTABLISHED
CURRENT
STALE
```

Rules:

- `NOT_ESTABLISHED` is valid for a native state that has never established a baseline and increments `discovery_baseline_gaps`.
- `CURRENT` requires all stored revision/digests/counts to equal deterministic recomputation.
- `STALE` is structurally valid and increments `discovery_baseline_gaps`.
- The baseline builder always emits `CURRENT`.
- `unknown_unknown_exhaustiveness_claimed` is always `false`.
- During M2, `active_grill_packs` is `[]` and `active_grill_packs_complete` is always `false`.

Add RED tests showing that a state with a stale stored baseline:

1. fails ordinary `validate_state_v2` with `stale_discovery_baseline`;
2. is nevertheless accepted by the baseline builder’s pre-baseline validation path;
3. produces a fresh deterministic `CURRENT` baseline;
4. passes ordinary validation after that computed baseline is installed into a copy of the state.

## Self-review result

With these clarifications, no additional blocking plan contradiction was found in the M2 decomposition. Execution must read both the M2 implementation plan and this addendum before coding.
