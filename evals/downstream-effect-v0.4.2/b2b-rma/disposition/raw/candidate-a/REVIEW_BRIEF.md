# Fresh Blind RMA Contract Review Brief

You are the one completely fresh independent Contract Review Agent for the architectural RMA generator regeneration.

## Isolation boundary

Read **only** files beneath this review-package directory. Do not open its parent directories, any repository checkout, conversation history, prior agents, prior candidate contracts, prior review decisions, rejected-field lists, correction patches, hidden-answer material, or Control/Treatment implementation evidence.

The package contains only:

- approved rev79 canonical authority and all seven projections under `authority/product-definition/`;
- audited shared Figma and shared human-readable handoff under `authority/shared/`;
- the new explicit product-specific mapping, generator, compiled contract, lifecycle/sequence/coverage outputs, invariant provenance inventory, and a fresh PENDING review template under `candidate/`;
- frozen compiler/schema implementation and documentation under `frozen/downstream/`.

Shared Figma authority: file key `C8vxL0pVRja04HhqGFwSQU`; roots `4:2`, `4:3`, `4:4`, `4:5`, `4:6`, `4:7`, `4:8`. The audited Figma evidence and handoff in the package are the review inputs; do not seek any other design or implementation artifact.

## Review target

Review the new compiled `joewrks.action-conformance/1.0` contract whose declared contract hash is:

`2dd2f41e996b37c22f6b960aee624160dd459b04afb31ef9e78c4e09cb76e1df`

Review every `REVIEW_REQUIRED` semantic field from zero. Do not sample and do not focus on any presumed defect family.

For each of the 665 identities in `candidate/review-required-decisions.PENDING.json`:

1. independently read its emitted value;
2. resolve every exact source pointer against `authority/product-definition/state.json`;
3. recompute and verify each exact source value hash;
4. interpret the complete current canonical meaning, including relevant projections/Figma/handoff where applicable;
5. decide `APPROVED` or `REJECTED`;
6. write a nonempty, field-specific rationale.

Do not leave any record `PENDING`. Do not invent or defer product semantics. Absence of canonical authority means a condition must not be added.

For every rejection, begin its rationale with exactly one classification:

- `[A. PRODUCT_SPECIFIC_MAPPING_DEFECT]`
- `[B. PRODUCT_REENTRY_REQUIRED]`
- `[C. HARNESS_REENTRY_REQUIRED]`

Set top-level `product_reentry_count` to the number of B-classified rejected fields. A C-classification is appropriate only when the exact explicit RMA definition is semantically changed or rejected by the frozen compiler itself, not for a product mapping problem.

## Output contract

Write exactly one file:

`review-required-decisions.COMPLETED.json`

in this review-package root. Preserve all top-level metadata and every immutable record field from the PENDING template exactly. Change only:

- each record's `verdict`;
- each record's `rationale`;
- top-level `product_reentry_count` when B-classified rejections exist.

Use deterministic UTF-8 JSON with a trailing newline. Do not write Markdown or modify any other file.

Before reporting, verify:

- 665 reviews and 665 unique identities;
- no `PENDING` verdict;
- every rationale nonempty and field-specific;
- every emitted value exactly equals the new compiled contract;
- all exact refs resolve and hash-match;
- declared/recomputed contract hash matches;
- only the required output file changed.

Return the total APPROVED/REJECTED/PENDING counts, Product Re-entry count, Harness Re-entry count, the complete rejected identity/classification/reason list, and the output file SHA-256.
