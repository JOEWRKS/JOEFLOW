# State 0.2.0 Grill Engine contract

**Milestone status:** `GRILL_ENGINE_IMPLEMENTED_M3`

This reference defines the M3 Grill Engine boundary for state 0.2.0. M3 adds
deterministic Materiality assessment, unknown resolution and decision-authority
policy, selective question projection, mandatory Grill topology classification,
declarative Grill Packs, and Grill-aware discovery-baseline commitments.

The binding M3 statements are:

- The system looks broadly for gray areas internally but does not ask the user
  every question it finds.
- Materiality is recomputed from its factors; classification is not trusted as
  a free boolean/label.
- Evidence-resolvable decisions are not asked of the user.
- After qualifying-evidence and external factual/constraint/behavioral branches,
  every strictly recomputed `NON_MATERIAL` unknown is `AGENT_AUTONOMOUS`
  regardless of `user_visible`.
- Material/high-risk product meaning may not be silently decided by the agent.
- A user-confirmation path requires a real recommendation with alternatives and
  tradeoffs.
- Unknown resolution records how the gray area was closed.
- Questions are projected from canonical state and one highest-leverage user
  question is selected at a time.
- Core Grill is always active; specialist Grill Packs activate from product
  topology, not agent discretion.
- Pack identity/version/digest are committed into the discovery baseline.
- M3 still does not provide exact semantic Coverage Binding or Semantic Closure.

## Internal discovery and user interruption

`INTERNALLY_EXHAUSTIVE_EXTERNALLY_SELECTIVE` means the system looks broadly for
gray areas internally but does not ask the user every question it finds.
Evidence-resolvable decisions are not asked of the user. Unknown resolution
records how the gray area was closed. Questions are projected from canonical
state, and one highest-leverage user question is selected at a time.

The exact decision-authority order is:

1. Qualifying current closure-eligible evidence for the required authority class
   produces `EVIDENCE_RESOLVABLE`.
2. Required factual, constraint, or behavioral authority without qualifying
   evidence produces `EXTERNAL_AUTHORITY_REQUIRED`.
3. Strictly recomputed `NON_MATERIAL` Materiality produces `AGENT_AUTONOMOUS`,
   regardless of `user_visible`.
4. Recomputed high-risk Materiality produces `USER_DECISION_REQUIRED`.
5. Recomputed `MATERIAL`, non-high-risk Materiality with a structurally valid,
   confirmation-ready recommendation produces `USER_CONFIRMATION`.
6. Every other case produces `USER_DECISION_REQUIRED`.

`user_visible` is auditable metadata only and never changes Materiality or the
autonomy result. After qualifying-evidence and external
factual/constraint/behavioral branches, every strictly recomputed
`NON_MATERIAL` unknown is agent-autonomous. This includes visible choices.
`MATERIALITY_CLASSIFICATION_ENFORCED` means Materiality is recomputed from its
factors; classification is not trusted as a free boolean or label.
`NO_SILENT_MATERIAL_AGENT_DECISIONS` means material or high-risk product meaning
may not be silently decided by the agent.

A user-confirmation path requires a real recommendation with mutually exclusive
alternatives and explicit tradeoffs. Recommendation acceptance is user authority,
not agent self-approval.

## Grill topology, packs, and baseline

Core Grill is always active. Specialist Grill Packs activate from the complete
six-cell `surface_manifest.grill_profile`, not agent discretion and not surface
tags. Forced surface kinds constrain profile truth but do not bypass profile
validation. Checked-in pack activation metadata is descriptive and never
activates a pack independently of the profile.

`ACTIVE_GRILL_PACKS_IMPLEMENTED_M3` means the discovery baseline stores the
deterministic compiled pack-instance list. Pack identity, version, and digest are
committed into that baseline together with exact sorted target references.
`active_grill_packs_complete` covers topology, identity, instance, and axis
inventory completeness only. It remains true when valid required rows contain
`OPEN` axes; `unresolved_pack_axes` reports those separately.

## M3 Closure metrics

`evaluate_closure_v2` retains the M1/M2 metrics and adds these final M3 metrics:

- `open_material_unknowns` counts OPEN unknowns whose Materiality recomputes to
  `MATERIAL`.
- `unresolved_unknown_provenance` counts each affected record once.
- `invalid_resolution_authority` counts each affected unknown or decision once,
  including an unauthorized agent decision only once even when policy findings
  overlap.
- `unassessed_materiality` counts each Materiality-bearing canonical requirement,
  unknown, decision, surface, or contradiction record once when its Materiality
  shape or stored classification is invalid. It does not trust the stored label
  and does not crash on malformed input; ordinary validation reports the precise
  error.
- `unauthorized_agent_decisions` counts each affected decision once.
- `missing_required_user_decisions` counts unresolved user-confirmation and
  user-decision-required records.
- `active_grill_pack_gaps` counts topology, identity, instance, and inventory
  gaps.
- `unresolved_pack_axes` independently counts OPEN Core and specialist axes.
- `umbrella_unknown_compression` independently counts invalid reuse or origin
  compression for independent axes.
- `pack_materiality_floor_violations` independently counts invalid Materiality
  floors.

The pack gap, OPEN-axis, umbrella-compression, and Materiality-floor metrics are
independent and may intentionally overlap for the same malformed coverage row.

## M3 boundary

`UNKNOWN_UNKNOWN_EXHAUSTIVENESS_NOT_CLAIMED` remains immutable: broad internal
discovery is not proof that future unknowns are impossible.

`SEMANTIC_CLOSURE_NOT_AVAILABLE_IN_M3`: M3 still does not provide exact semantic
Coverage Binding or Semantic Closure. Closure remains false, the definition
digest remains null, and `semantic_closure_not_implemented = 1`. Coverage to
Authority pointer/hash proof, UX Binding, Approval Manifest authority, downstream
2.0, and full migration/adoption remain later milestones.
