# Contract Review Reliability Report

## Population

- Old candidate: `2dd2f41e996b37c22f6b960aee624160dd459b04afb31ef9e78c4e09cb76e1df`
- New candidate: `2621e7da2b576ca7d902989a720b6ed7af62b6c8895c2cfca77850421871e074`
- Exact REVIEW_REQUIRED identity set: `665 / 665`
- Unexpected identity mismatch: `0`
- Authorized semantic value changes: `4`
- Semantically unchanged identities: `661`

## Confusion matrix

| Old verdict | New verdict | Count |
|---|---|---:|
| APPROVED | APPROVED | 485 |
| APPROVED | REJECTED | 176 |
| REJECTED | APPROVED | 0 |
| REJECTED | REJECTED | 4 |

## Reliability metrics

- Exact verdict agreement: `489/665` = `73.5338345865%`
- Exact verdict disagreement: `176/665` = `26.4661654135%`
- Both-approved count: `485`; old-approval retention: `485/661` = `73.3736762481%`
- Both-rejected count: `4`; old-rejection retention: `4/4` = `100.0000000000%`
- Binary positive agreement: `84.6422338569%`
- Binary negative agreement: `4.3478260870%`
- Cohen's kappa: `0.032087330466`

## Excluding the four authorized semantic edits

- Agreement: `485/661` = `73.3736762481%`
- Disagreement: `176/661` = `26.6263237519%`
- All 176 disagreements are semantically unchanged fields.

## Reviewer instability versus candidate defects

- Actual candidate semantic changes: `4`; all were `REJECTED → REJECTED` and therefore contributed no verdict disagreement.
- Reviewer interpretation instability: `176` unchanged-field flips. Isolated adjudication classified all 176 as `REVIEW_RUBRIC_AMBIGUOUS`, not as adjudicated candidate defects.
- Established systematic first-review false negatives: `0`.
- Established systematic second-review false positives: `0`.
- The low kappa (`0.032087330466`) shows near-chance agreement after accounting for the highly imbalanced marginal verdict rates; it does not establish which reviewer was right.

## Subsystem diagnosis

Dominant diagnosis: `F. MIXED`, specifically:

- `D. REVIEW_RUBRIC_UNDERSPECIFIED`: the common rules do not define exact-field versus distributed-field completeness, while the two run briefs use materially different wording.
- `E. CONTRACT_REPRESENTATION_AMBIGUITY`: the contract has separate sibling fields for guards, outcomes, recovery, and visibility, but the frozen representation does not state whether runtime evaluation composes them or requires duplication within each REVIEW_REQUIRED field.

Not selected as dominant: `A`, `B`, or `C`. The four old-candidate reason omissions were real narrow mapping defects, but they were corrected in the new candidate and do not explain the 176 unchanged-field flips. The evidence also does not adjudicate either reviewer as systematically false.

## Re-entry and recommendation

- Product Re-entry required: `NO`. No missing product decision was established.
- Harness Re-entry required: `YES FOR A SEPARATE POST-v0.4.2 CALIBRATION WORKSTREAM`, not as a mutation of the stopped v0.4.2 run. The review rubric and contract-field composition semantics must be made deterministic before another efficacy experiment relies on this gate.
- Recommended next workstream: versioned review-rubric and contract-representation calibration with explicit field-responsibility rules, golden adjudicated examples for all three disputed field families, a byte-identical reviewer brief, and a repeatability threshold measured before a new paired run.
