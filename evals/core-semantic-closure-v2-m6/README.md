# Core Semantic Closure V2 M6 evaluation

This directory contains the M6 existing-product dogfood evidence through the
Phase A human approval checkpoint. The bounded native V2 state is
`READY_FOR_REVIEW` and `UNAPPROVED`; it does not claim Product Definition
Closure, downstream compilation, runtime conformance, re-entry, Phase B, or
whole-M6 completion.

The two Phase A lineages are deliberately separate:

- `dogfood/migration/legacy-candidate.json` and `migration-receipt.json` are the
  complete deterministic Track A audit of the legacy state. The candidate stays
  `OPEN` and `UNAPPROVED`.
- `dogfood/product-definition/client-feedback-portal-dogfood-v2/state.json` is
  the bounded native Track B reconciliation for `REQ-005` and `REQ-006`. It is
  not the full legacy migration and cannot trim or close Track A.

The user explicitly decided that analytics and telemetry are not used for this
bounded definition. Review-link and thread actions emit no analytics events;
ordinary domain history and email delivery state remain non-analytics product
state. The decision is local to this definition, not a permanent prohibition.

The exact review packet is `dogfood/approval-manifest.json`. No approval fields
or timestamps may be written until a later run receives explicit approval for
that exact manifest digest. The corrected deterministic packet reports 81 added
records and no changed, superseded, or retired records.
