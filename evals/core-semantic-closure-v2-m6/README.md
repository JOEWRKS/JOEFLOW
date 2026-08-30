# Core Semantic Closure V2 M6 evaluation

This directory contains the partial M6 existing-product dogfood evidence.
Phase A is `NEEDS_CONTEXT`: a material analytics-events and measurement-policy
choice has no authority in the inspected legacy documents or user decisions.
It does not claim readiness for review, Product Definition Closure, downstream
compilation, runtime conformance, re-entry, or whole-M6 completion.

The two Phase A lineages are deliberately separate:

- `dogfood/migration/legacy-candidate.json` and `migration-receipt.json` are the
  complete deterministic Track A audit of the legacy state. The candidate stays
  `OPEN` and `UNAPPROVED`.
- Track B was stopped before authoring the native V2 state. The intended bounded
  slice was `REQ-005` and `REQ-006`, but the legacy sources do not define the
  required analytics events or measurement behavior. Track B is not the full
  legacy migration and cannot be used to trim or close Track A.

No approval manifest or approval fields were written. The unresolved choice
must be answered from real product authority before Track B can be completed.
