# State 0.2.0 Semantic Freeze contract

**Milestone status:** `SEMANTIC_FREEZE_IMPLEMENTED_M4`

M4 is the first milestone where a state 0.2.0 Product Definition can
legitimately become `CLOSED`. Closure now means that current material product
meaning is present, its Core, specialist Grill, and UX claims point to exact
canonical values, the defined discovery procedure is complete, and the exact
definition plus the exact user-facing Approval Manifest have a recorded user
approval commitment.

`SEMANTIC_CLOSURE_AVAILABLE_M4` applies only to Product Definition. It does not
mean design, implementation, testing, deployment, or adoption is complete. It
also does not claim that every future unknown is impossible.

## Exact semantic proof

`EXACT_COVERAGE_BINDING_REQUIRED` and `EXACT_UX_BINDING_REQUIRED` mean that a
positive Core, specialist Grill, screen-state, or screen-action claim must bind
an allowed CURRENT authority record, a record-relative JSON Pointer, and the
SHA-256 of the canonical value at that pointer. A broad record reference or a
checkbox is not proof.

`COVERED_IS_PROOF_NOT_CHECKBOX` therefore has three explicit states:

- `COVERED`/`ADDRESSED` contains non-empty, exact positive authority bindings;
- `OPEN` names the current open unknown that prevents proof;
- `N/A` contains a meaningful rationale and exact intent/constraint basis.

Every CURRENT recomputed-MATERIAL requirement must have its complete 20-axis
Core row, required acceptance criterion and task mapping, applicable specialist
Grill proof, and every current screen's exact 16-state and declared-action proof.
The bidirectional audit also requires material decisions and reachable material
authority to reach a real Core, Grill, UX, or task sink.

## Semantic definition and Approval Manifest

`INFORMED_APPROVAL_MANIFEST_REQUIRED` means approval binds both the deterministic
semantic definition digest and the deterministic
`joewrks.approval-manifest/1.0` digest. A matching current-revision approval
history commitment records definition, manifest, record, coverage, surface, and
active Grill Pack commitments. Product meaning cannot change under the same
revision and be silently re-approved.

The semantic digest excludes the current approval control object, approval
history formatting, operational timestamps, and unconsumed evidence. It includes
current semantic authority, exact bindings, current surfaces, resolved meaning,
consumed evidence, active Grill Pack identities, and the semantic fields of the
current discovery baseline.

`UNCONSUMED_EVIDENCE_DOES_NOT_INVALIDATE_APPROVAL` means a new evidence record
first makes the all-evidence discovery baseline stale. After rebuilding only
that baseline, unchanged unconsumed evidence does not change the semantic
definition or Approval Manifest and does not invalidate a valid approval. Once
the evidence is referenced by current semantic authority, it is consumed,
changes the semantic commitment, and makes the old approval stale.

## Closure rule and lifecycle

`evaluate_closure_v2` returns `closed = true` only when ordinary V2 validation
has no errors, the definition is `CLOSED`, approval is `APPROVED` for the exact
current revision/definition/manifest, one exact current history commitment
exists, and every explicitly frozen M1–M4 blocking metric is zero.
`deferred_unknowns` remains informational: a valid user-accepted deferral is not
made blocking merely because its count is non-zero.

The lifecycle pairing is:

- `OPEN`, `BLOCKED`, and `READY_FOR_REVIEW` use canonical `UNAPPROVED`;
- only semantically ready `READY_FOR_REVIEW + UNAPPROVED` may compile the
  user-facing review manifest;
- `CLOSED` requires exact `APPROVED` control state and history commitment.

Closure additionally requires a CURRENT GOAL, a CURRENT recomputed-MATERIAL
requirement, a CURRENT discovery baseline with procedure, applicable surface
classes and active pack compilation complete, and
`unknown_unknown_exhaustiveness_claimed = false`.

## Recorded approval trust boundary

M4 verifies a canonical claim that the exact manifest was approved by `user` at
a supplied UTC timestamp. It does not cryptographically authenticate a human,
observe a click, invent an approval time, change approver identity, or
auto-approve a READY state. The authoring workflow may write APPROVED only after
the actual user has seen the deterministic manifest and explicitly approved it.

## Later milestones remain later

`DOWNSTREAM_V2_NOT_IMPLEMENTED_IN_M4`: M4 does not implement or measure
`joewrks.action-conformance/2.0`, `joewrks.semantic-review/2.0`,
`DIRECT_AUTHORITY`, `MACHINE_DERIVED`, `REVIEW_REQUIRED`, semantic-debt policy,
implementation ambiguity re-entry execution, migration adoption, or dogfood
integration. Existing downstream v1 contracts and frozen v0.4.3 evidence remain
unchanged.
