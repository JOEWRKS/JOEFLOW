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

If approval history already contains a commitment whose `revision == project.definition_revision`, recompute the **entire semantic approval commitment** for the current state and compare these fields:

```text
definition_digest
manifest_digest
record_hashes
coverage_digest
surface_digest
grill_pack_set_digest
```

If any differ, emit/block:

```text
semantic_change_without_revision_increment
```

This is distinct from ordinary `stale_approval` and applies even when the active-current `definition_digest` happens to remain the same—for example, rewriting historical record content or changing exact binding commitments inside the same revision.

Consequences:

- changing current product meaning after approval while retaining the same revision cannot be re-approved;
- changing approved historical/provenance records or exact coverage commitments inside the same revision cannot be silently re-approved;
- the project must increment `definition_revision`, set approval `UNAPPROVED`, reconcile stale authority as required, then build a new manifest;
- adding unconsumed evidence and rebuilding the discovery baseline is **not** a semantic approval-commitment change and does not trigger this blocker because the semantic projection, pure manifest, record hashes, coverage/surface/pack commitments remain equal.

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

## 9. Previously approved stable records may not disappear

The V2 lifecycle requires stable IDs and explicit `SUPERSEDED` / `RETIRED` history. Once a stable record has participated in an approval commitment, silently deleting it from a later canonical state would bypass that lifecycle.

For every stable ID present in the latest previous approval commitment's `record_hashes`, require that the ID still resolves in the current canonical state, regardless of whether it remains active or currently consumed.

Emit/block:

```text
approved_record_missing_from_state
```

when a previously approved record disappears entirely.

This check applies to previously committed Product Definition records and previously consumed EVD records. A previously consumed EVD may stop contributing to the **current semantic digest**, but the `EVD-*` record itself remains in canonical state and transitions through its explicit evidence lifecycle when appropriate.

Do not treat disappearance as implicit retirement. The record must remain and carry explicit `SUPERSEDED`, `RETIRED`, or evidence lifecycle state as defined by its type.

Add this metric to approval/history blockers and tests proving that:

- changing CURRENT → RETIRED with valid provenance is representable;
- deleting the same ID is blocked;
- a formerly consumed EVD that becomes unconsumed may remain in state without invalidating approval solely because it is no longer consumed;
- deleting that previously committed EVD is blocked.

## 10. Positive authority bindings must bind semantic content, not empty values

A correct pointer and hash are not sufficient when the resolved value carries no positive semantic content. Otherwise a binding such as:

```text
DEC-001 /accepted_recommendation → null
```

could mechanically satisfy a `COVERED` or `ADDRESSED` cell.

For positive semantic proof, after pointer/type/root/hash verification, require the resolved value to be **semantically non-empty**:

```text
null                 → invalid
empty / whitespace string → invalid
empty list           → invalid
empty object         → invalid
boolean false        → valid when the permitted semantic field itself is boolean
number 0             → valid
non-empty scalar/container → valid
```

Emit `empty_authority_binding_value` and count the affected cell under `invalid_authority_binding`.

This rule applies to positive `COVERED` / `ADDRESSED` bindings. N/A basis bindings use their separate basis semantics and are not forced through this positive-content rule.

Add explicit tests for null/empty string/list/object rejection and meaningful `false`/`0` preservation.

## 11. Approval-manifest closure summary is semantic-readiness only

The pure Approval Manifest must remain identical across the control-state transition from `READY_FOR_REVIEW + UNAPPROVED` to `CLOSED + APPROVED`.

Therefore `semantic_closure_summary` inside the manifest contains only **non-approval semantic-readiness metrics**. It must not contain:

```text
missing_user_approval
stale_approval
missing_or_stale_approval_manifest
approval_history_gaps
project.definition_status-derived blockers
```

Those are validation/control-state results, not product meaning being approved.

The manifest may include a deterministic summary such as:

```text
semantic_readiness_blockers = 0
open_material_unknowns = 0
unresolved_material_contradictions = 0
coverage_binding_gaps = 0
ux_binding_gaps = 0
grill_binding_gaps = 0
```

provided every field is computed from pure semantic readiness and is invariant across the READY→CLOSED approval transition.

Add a regression that computes the manifest before approval and after installing the exact approval/history commitment and changing only `definition_status` to `CLOSED`; manifest body and manifest digest must be byte-identical.

## 12. Approval validity is a recorded human-authority claim, not cryptographic identity proof

M4 can deterministically prove that the canonical state records:

```text
approved_by = user
approved_at = supplied value
approved_revision = current revision
approved_definition_digest = exact current semantic digest
approved_manifest_digest = exact current pure manifest digest
matching approval-history commitment exists
```

It cannot cryptographically prove, from `state.json` alone, that a particular human physically clicked a UI control or authored a chat message. Do not overstate M4 as human-identity authentication.

The authoring workflow is responsible for writing `approval.status = APPROVED` only after the actual user has been shown the deterministic manifest and explicitly approved it. M4 itself never synthesizes `approved_at`, never changes `approved_by` to `user`, and never auto-approves a READY state.

The semantic-freeze reference must state this trust boundary explicitly. A future authenticated approval-receipt mechanism could strengthen identity assurance without changing the M4 semantic digest/manifest model.

## Self-review result

With these clarifications, no remaining known blocking contradiction, lifecycle escape hatch, or approval-control recursion was found in the M4 decomposition. Execution must read the frozen design, M3 audit, M4 plan and this addendum before coding.
