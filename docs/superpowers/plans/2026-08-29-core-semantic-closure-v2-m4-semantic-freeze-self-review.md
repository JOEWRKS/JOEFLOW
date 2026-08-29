# Core Semantic Closure V2 — M4 Plan Self-Review Clarifications

**Status:** `NORMATIVE_PLAN_CLARIFICATION`

**Applies to:** `docs/superpowers/plans/2026-08-29-core-semantic-closure-v2-m4-semantic-freeze.md`

Where this addendum conflicts with the M4 plan, this addendum controls. The frozen Core Semantic Closure V2 design remains the higher authority.

## 1. Approval Manifest computation must be pure and independent of approval lifecycle state

The main plan correctly requires the user-facing `build_approval_manifest.py` CLI to accept only a semantically ready:

```text
READY_FOR_REVIEW + UNAPPROVED
```

state. However, the already-approved `CLOSED + APPROVED` state must also be able to recompute the **same** manifest/digest during approval validation. Reusing a lifecycle-gated manifest builder would create a cycle and make valid approved state impossible to verify.

Freeze two layers:

```python
def compute_approval_manifest(state: dict[str, object]) -> dict[str, object]:
    """Pure semantic manifest. Ignores current definition_status/approval control state."""


def build_approval_manifest_for_review(state: dict[str, object]) -> dict[str, object]:
    """Requires READY_FOR_REVIEW + UNAPPROVED + semantic readiness, then calls compute_approval_manifest."""
```

`build_approval_manifest.py` uses `build_approval_manifest_for_review`.

`validate_approval()` on a `CLOSED + APPROVED` state uses `compute_approval_manifest()` directly.

Because `project.definition_status`, `approval`, and `approval_history` are excluded from semantic product meaning, the pure manifest and its digest must be identical before and after the control-state transition:

```text
READY_FOR_REVIEW + UNAPPROVED
→ user approves exact manifest
→ CLOSED + APPROVED
```

Add explicit regression tests for manifest/definition digest stability across that transition.

## 2. Current history commitment and previous comparison commitment are different roles

An APPROVED state contains one matching approval-history commitment for the **current** revision. The manifest diff baseline must nevertheless use the greatest history revision **strictly less than** the current revision.

Freeze helpers:

```python
def current_approval_commitment(state) -> dict[str, object] | None: ...
def previous_approval_commitment(state) -> dict[str, object] | None: ...
```

Rules:

- duplicate history revisions are invalid;
- an APPROVED state requires exactly one matching current-revision commitment;
- `compute_approval_manifest()` ignores the current-revision commitment when computing `from_revision` and semantic diff;
- first approval has `previous_approval_commitment = None` and `from_revision = null`;
- current history entries never create manifest-digest recursion because `manifest_digest` is not embedded in the manifest body.

## 3. Semantic changes require a new definition revision

The frozen design requires material Product Definition changes to increment `definition_revision` and invalidate approval. Approval-history commitments now make this enforceable.

If approval history contains a commitment whose `revision == project.definition_revision` but its `definition_digest` differs from the current recomputed semantic definition digest, emit/block:

```text
semantic_change_without_revision_increment
```

This is distinct from ordinary `stale_approval`.

Consequences:

- changing product meaning after an approval while retaining the same revision cannot be re-approved;
- the project must increment `definition_revision`, set approval `UNAPPROVED`, reconcile stale authority as required, then build a new manifest;
- adding unconsumed evidence and rebuilding the discovery baseline is **not** a semantic definition change and does not trigger this blocker because the semantic digest remains equal.

Add this metric to Task 4/6 blocking readiness and dedicated tests to Task 5/6.

## 4. N/A evidence basis must be intent/constraint authority, never observed absence

The main plan described “closure-eligible evidence” for N/A basis too broadly. `OBSERVED_IMPLEMENTATION`, `OBSERVED_RUNTIME`, or `TEST_ASSERTION` may be current factual/behavioral evidence, but they cannot by themselves prove that a product axis is intentionally not applicable.

For M4 `basis_bindings` targeting `EVD-*`, require a CURRENT, non-candidate evidence record that can support at least one of:

```text
INTENT
PREFERENCE
CONSTRAINT
```

Allowed examples:

```text
USER_CONFIRMED_INTENT + INTENT
DOCUMENTED_INTENT + INTENT
HISTORICAL_DECISION + INTENT/PREFERENCE
EXTERNAL_CONSTRAINT + CONSTRAINT
```

Disallowed as sole N/A basis:

```text
OBSERVED_IMPLEMENTATION
OBSERVED_RUNTIME
TEST_ASSERTION
INFERRED_INTENT
DESIGN_ARTIFACT
```

This preserves the M2 invariant:

> Absence of implementation is not evidence of out-of-scope or N/A product intent.

For SURF basis, only current disposition statuses `IN_SCOPE` or `OUT_OF_SCOPE` may serve as M4 basis. `OPEN`, `SUPERSEDED`, and `RETIRED` surfaces cannot justify an N/A semantic cell.

## 5. Narrow semantic pointer roots for positive proof

The main plan’s initial semantic-root list was intentionally generous. For `COVERED` / specialist `ADDRESSED`, control/provenance fields must not masquerade as product semantics.

Freeze positive-proof semantic roots as:

```text
GOAL  statement
USR   description actor_kind
REQ   statement scope ui_required
DEC   statement accepted_recommendation
RULE  statement
FLOW  entry preconditions paths outcomes
SCR   purpose interaction_mode major_actions
STATE state_name conditions
DATA  name purpose ownership
INT   name purpose
AC    assertion
```

Do **not** accept positive proof rooted at:

```text
id
status
materiality
requirement_refs / goal_refs / owner_refs / applies_to
resolution_mode / decision_authority / decision_type
superseded_by / retired_by / retired_at_revision / retirement_reason
```

Those values may establish provenance/graph relationships, but they do not by themselves prove a semantic Coverage axis.

N/A basis roots remain a separate, broader contract and may include relevant disposition/provenance roots such as `SURF.status` because basis proof answers “why not applicable,” not “what behavior is covered.”

## 6. Semantic record hashes for informed approval

To preserve history while respecting the unconsumed-evidence boundary, `semantic_record_hashes()` contains:

- **all stable Product Definition records** from objects, surfaces and contradictions, including historical `SUPERSEDED/RETIRED` records so retirement/supersession changes remain visible in approval diffs;
- only **consumed** EVD records.

It does not include unconsumed EVD records.

This is intentionally different from the active-only `semantic_projection()` used for current product meaning.

If a previously consumed EVD ceases to be consumed, the overall semantic authority that used it must also have changed; the definition digest/manifest diff will capture the resulting semantic change without forcing unrelated observational evidence into approval.

## 7. Discovery baseline all-evidence digest stays outside semantic approval meaning

Retain M3’s full `evidence_commitment_digest` in the discovery baseline because discovery freshness should notice every evidence change.

But M4 `semantic_projection()` must exclude that one baseline field exactly as stated in the main plan. Do not “simplify” by hashing the whole baseline object.

Required regression sequence:

1. start from valid APPROVED/CLOSED state;
2. add an unconsumed CURRENT EVD;
3. ordinary validation reports baseline stale until rebuilt;
4. rebuild baseline;
5. `definition_digest` and pure approval-manifest digest remain identical;
6. approval remains valid and Closure returns true;
7. reference that EVD from current semantic authority;
8. digest changes and approval becomes stale.

## 8. Closure status and approval validation remain separate from structural validity

`OPEN`, `BLOCKED`, `READY_FOR_REVIEW`, and `CLOSED` are all structurally representable state statuses.

Do not make ordinary schema validation reject a semantically incomplete OPEN state simply because Closure blockers exist. The evaluator/metrics own closure readiness.

Lifecycle consistency rules are still enforced:

```text
OPEN/BLOCKED/READY_FOR_REVIEW → approval.status = UNAPPROVED
CLOSED → approval.status = APPROVED
```

The review-manifest CLI requires READY_FOR_REVIEW plus zero non-approval readiness blockers. `validate_closure` requires CLOSED plus exact approval commitments.

## Self-review result

With these clarifications, no remaining known blocking contradiction was found in the M4 decomposition. Execution must read the frozen design, M3 audit, M4 plan and this addendum before coding.
