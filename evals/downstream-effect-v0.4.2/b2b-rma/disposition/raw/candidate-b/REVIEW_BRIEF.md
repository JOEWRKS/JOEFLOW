# Independent Contract Review Brief

Review the complete candidate in this directory as a fresh, isolated semantic review.

## Allowed inputs

Read only files under this review-package directory:

- `authority/product-definition/`: approved canonical Product Definition revision 79 and its seven projections
- `authority/shared/`: the audited shared Figma evidence and verified shared implementation handoff
- `candidate/`: the full compiled action/lifecycle/sequence contract, product-specific source mapping, exact provenance inventory, reports, and pending review template
- `frozen/downstream/`: the frozen generic compiler, verifier, schemas, and documentation

Do not inspect Git history, sibling directories, other worktrees, other review packages, controller notes, prior candidates, prior review outputs, implementation artifacts, or hidden answers.

## Review task

Use `authority/product-definition/state.json` as canonical semantic authority. Use the current projections, audited Figma evidence, and shared handoff only as consistent supporting context. Treat the frozen compiler and schemas as representation rules, not product-semantic authority.

Independently review every one of the 665 `REVIEW_REQUIRED` records in `candidate/review-required-decisions.json`, from zero. For each record:

1. resolve every exact source pointer against the canonical state;
2. verify the recorded source hash and active/current status;
3. decide whether the emitted value is fully supported for that exact action or lifecycle field and scope;
4. detect omitted constraints, unsupported broadening, wrong role/scope/state/result behavior, stale or superseded authority, and incorrect action/variant-specific provenance;
5. set `verdict` to `APPROVED` or `REJECTED` and write a concrete non-empty rationale based only on the allowed inputs.

Do not carry forward any decision, assume that similar actions inherit semantics, or approve by sampling. Review all identities. Do not change identity, owner, field, emitted value, source references, canonical source meaning, contract hash, schema version, review context, or excluded-input declarations.

Set `product_reentry_count` to the number of rejected records whose defect cannot be corrected without changing approved product semantics. There is no deferred verdict in this review schema; finish every record with `APPROVED` or `REJECTED`.

## Output

Write exactly one new file:

`review-required-decisions.COMPLETED.json`

It must preserve the input template structure and immutable fields, contain all 665 unique review identities, and have zero `PENDING` records. Do not modify or create any other file.
