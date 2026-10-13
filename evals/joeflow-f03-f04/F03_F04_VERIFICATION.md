# F03 candidate preflight and F04 planning projection audit

Status: implementation candidate; not installed; not a product approval.

## Implemented boundaries

- F03 is read-only and separates state validation, semantic readiness, manifest review readiness, and user approval.
- F03 reports exact orphan identifiers/pointers and actual invalid authority-binding types without imposing contiguous numeric IDs.
- F04 obtains its required projection, semantic-review, and render-review inventories from a separately hashed scope authority.
- F04 separates materialization, structure, source identity, semantic review, and render review.
- A semantic or render PASS requires evidence bound to the current source and projection hashes, reviewer, scope, coverage where applicable, and verdict.
- Unreviewed work remains `UNKNOWN` with `findings: null`; it is never reported as zero findings or PASS.
- Resume receipts never bypass current source, projection, or evidence validation. Only unchanged completed projections are identified as resumed.
- Both tools are read-only. They do not modify canonical state or projections, create approval, or authenticate reviewer authority merely from a hash.

## Executable samples

See `fixtures/README.md`. Normal, error, PASS, and PARTIAL input/output pairs are checked in for consumer integration.

## Verification

- Focused and regression group: 84 tests PASS (`test_candidate_preflight_projection_audit`, skill package, authority binding, semantic Closure, and approval manifest).
- Independent Manager counterexamples: F03 6/6 and F04 8/8 meet expectations, including JSON `null` review evidence rejection.
- CP949-strict wrapper smoke: F03 PASS with exit 0; F04 PARTIAL with controlled exit 1 and structured JSON.
- `git diff --check`: PASS.

The independent counterexamples cover a later invalid binding after a valid binding, orphan authority, malformed shapes, required render PASS without bound evidence, false source token substitution, non-object review evidence, missing required projection, and caller downgrade of required scope.
