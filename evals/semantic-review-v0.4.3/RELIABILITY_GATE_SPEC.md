# v0.4.3 Semantic Review Reliability Gate

All thresholds in this document are frozen before calibration. A run set cannot change thresholds, brief bytes, responsibility rules, golden answers, package bytes, or metric selection after outputs are observed.

## 1. Required run design

- Independent full reviews: at least `3`.
- Each review SHALL use a fresh isolated context with no previous verdict access.
- `review_run_id` and `reviewer_context_id` SHALL each be unique across runs; every controller-recorded, hash-verified isolation attestation SHALL verify `fresh_context: true`, `previous_verdict_access: false`, and `manifest_only_evidence: true`.
- Reviewer input package hash: identical across all comparable runs, required.
- Reviewer brief hash: identical across all comparable runs, required.
- Responsibility profile, obligation index, contract, identity inventory, and output schema hashes: identical across all comparable runs.
- Results with different hashes SHALL NOT be pooled.

Cross-run identity failures use specific-first classification: prior-verdict exposure is reported first; otherwise a reviewer-brief hash difference reports `FAIL/BRIEF_IDENTITY_MISMATCH` and suppresses the package mismatch caused solely by those brief bytes; otherwise any package hash difference reports `FAIL/PACKAGE_IDENTITY_MISMATCH`.

## 2. Structural acceptance

For every run:

- expected identity coverage = `100%`;
- duplicate or extra identities = `0`;
- pending/deferred/missing records = `0`;
- output schema validation = `PASS`;
- immutable hashes and responsibility assignments = exact match;
- prior-verdict exposure = `0`.

Any failure stops the gate before semantic reliability is calculated.

## 3. Golden acceptance

Across all 15 frozen goldens and every run:

- golden verdict accuracy = `100%`;
- golden rationale-code accuracy = `100%`;
- unexpected `RUBRIC_ERROR` = `0`;
- unexpected `INPUT_PACKAGE_ERROR` = `0`.

Expected errors in `G-012`, `G-013`, and `G-015` are correct answers and are not “unexpected.” Any other error verdict fails the gate.

## 4. Full-review exact agreement

For a byte-identical full candidate contract, define the unchanged identity set as identities whose semantic value hash, provenance-set hash, responsibility rule, completeness mode, and obligation-index entries are identical across all runs.

For `n` unchanged identities and every three-review combination selected from the at-least-three comparable runs:

```text
combination_unanimity = identities with one identical verdict across that three-run combination / n
three_review_unanimity = minimum combination_unanimity across all three-run combinations
```

Required: `three_review_unanimity >= 0.99`.

Reviewer-explanation prose is excluded. Verdict and rationale code are separately compared. Verdict disagreement cannot be hidden by matching explanations.

## 5. Normative disagreement gates

The following counts must both equal zero:

- unresolved normative responsibility/completeness disagreement;
- repeated disagreement under the same responsibility rule.

A normative responsibility/completeness disagreement exists when reviewers choose different verdicts because they assign ownership, local/compositional completeness, allowed sibling references, or duplication requirements differently. Any such disagreement is a rubric defect regardless of global percentage.

A repeated disagreement exists when two or more distinct review identities show a disagreement attributable to the same `responsibility_rule_id` in one run set. It fails the gate even if global unanimity remains at least 99%.

Every identity with a verdict or rationale-code difference SHALL receive exactly one hash-bound disagreement-classification record after all independent outputs are frozen. The record SHALL contain the review identity, responsibility rule, observed verdict/rationale pairs, exact cited obligation/rule/evidence hashes, classifier context ID, and one closed cause code:

- `REVIEWER_EXECUTION_ERROR`: the frozen rule and evidence yield one determinate answer and the record identifies the exact reviewer step that violated it;
- `PACKAGE_DEFECT`: the supposedly comparable inputs were not validly identical;
- `CANDIDATE_IDENTITY_DRIFT`: immutable candidate identity bytes differed;
- `NORMATIVE_RESPONSIBILITY`: the frozen taxonomy does not uniquely assign ownership;
- `NORMATIVE_COMPLETENESS`: the frozen rule does not uniquely decide local/compositional/reference completeness;
- `UNRESOLVED_NORMATIVE`: available evidence cannot distinguish a rubric defect from reviewer execution.

`REVIEWER_EXECUTION_ERROR` is permitted only when the classification cites one existing normative rule that makes the correct verdict/rationale mechanically unique; an adjudicator preference or majority result is insufficient. Any missing classification is `UNRESOLVED_NORMATIVE`. Any `NORMATIVE_*` or `UNRESOLVED_NORMATIVE` record fails the zero-unresolved gate. Any `PACKAGE_DEFECT` or `CANDIDATE_IDENTITY_DRIFT` fails structural identity. Two differing identities with the same responsibility rule fail the repeated-rule gate regardless of classification.

A single `REVIEWER_EXECUTION_ERROR` MAY remain diagnostic only when every other threshold still passes. Adjudication never rewrites original outputs, verdict/rationale accuracy, agreement, or reliability statistics and cannot convert a failed run set to PASS.

## 6. Balanced-case statistics

The full-review candidate verdict population is balanced when, after excluding expected meta/package-error fixtures, both `APPROVED` and `REJECTED_CANDIDATE` represent at least 5% of expected identities in every run.

For all comparable runs:

- compute Cohen's kappa for every reviewer pair;
- compute Fleiss' kappa across all reviewers;
- minimum pairwise Cohen's kappa SHALL be `>= 0.90`;
- Fleiss' kappa SHALL be `>= 0.90`.

All calculations use the same identity order and exact verdict classes. Error verdicts in a valid full-review package fail separately and are not collapsed into candidate rejection.

## 7. Imbalanced-case statistics

If either candidate verdict class is below 5% in any run, the run set is imbalanced. Kappa values SHALL still be reported but are diagnostic rather than the acceptance statistic.

Required:

- multi-rater Gwet AC1 `>= 0.95`;
- minority-class agreement `>= 0.95`.

Minority-class agreement is:

```text
identities unanimously assigned the pooled minority verdict
/
identities assigned that minority verdict by at least one reviewer
```

If no reviewer assigns the minority verdict, the golden suite's minority-class cases remain the required sensitivity check; full-review minority-class agreement is reported as not applicable rather than `1.0`.

## 8. No systematic disagreement family

In addition to responsibility-rule repetition, the controller SHALL cluster disagreements by:

- semantic field;
- responsibility rule;
- completeness mode;
- rationale code;
- canonical obligation type.

Two or more disagreements with the same responsibility rule are an automatic failure. Other repeated clusters are recorded and require rubric diagnosis before a new version, even if another threshold already failed.

## 9. Frozen-threshold rationale

- `>= 3` independent full reviews is the minimum that exposes a repeated interpretation pattern instead of only a pairwise split; every three-run combination is tested when more runs exist.
- `100%` golden verdict/rationale accuracy is appropriate because the 15 fixtures are small, human-adjudicated, and frozen specifically to exercise the disputed boundaries; tolerating one miss would accept an unresolved known rule.
- `>= 99%` unchanged-identity unanimity allows at most isolated non-normative reviewer mistakes while the separate zero-tolerance normative/same-rule gates prevent systemic ambiguity from hiding inside that allowance.
- balanced pairwise/Fleiss kappa `>= 0.90` requires near-perfect pair and multi-rater reliability when both candidate classes have enough prevalence for kappa to be meaningful.
- imbalanced Gwet AC1 `>= 0.95` avoids the prevalence paradox observed in v0.4.2, while minority-class agreement `>= 95%` independently prevents high majority-class agreement from masking missed rejections.
- zero unexpected error verdicts, zero unresolved normative disagreement, and no majority escape are necessary because those outcomes identify a defective package or rubric, not ordinary reviewer noise.

These thresholds were fixed by PM approval before any v0.4.3 calibration output exists.

## 10. Decision table

| Gate | Threshold | Failure result |
|---|---:|---|
| independent full reviews | `>= 3` | `FAIL/INSUFFICIENT_INDEPENDENT_RUNS` |
| unique run/context IDs and valid isolation attestations | required | `FAIL/REVIEWER_ISOLATION` |
| identical package hash | required | `FAIL/PACKAGE_IDENTITY_MISMATCH` |
| identical brief hash | required | `FAIL/BRIEF_IDENTITY_MISMATCH` |
| previous verdict exposure | `0` | `FAIL/PREVIOUS_VERDICT_EXPOSURE` |
| identity coverage | `100%` | `FAIL/IDENTITY_COVERAGE` |
| pending | `0` | `FAIL/INCOMPLETE_REVIEW` |
| golden verdict accuracy | `100%` | `FAIL/GOLDEN_VERDICT` |
| golden rationale-code accuracy | `100%` | `FAIL/GOLDEN_RATIONALE` |
| unexpected rubric/package errors | `0 / 0` | `FAIL/UNEXPECTED_ERROR_VERDICT` |
| unchanged three-review unanimity | `>= 99%` | `FAIL/EXACT_AGREEMENT` |
| unresolved normative disagreement | `0` | `FAIL/RUBRIC_NORMATIVE_AMBIGUITY` |
| repeated same-rule disagreement | `0` | `FAIL/RESPONSIBILITY_RULE_INSTABILITY` |
| balanced pairwise/Fleiss kappa | each `>= 0.90` | `FAIL/BALANCED_RELIABILITY` |
| imbalanced Gwet AC1 | `>= 0.95` | `FAIL/IMBALANCED_RELIABILITY` |
| minority-class agreement | `>= 95%` | `FAIL/MINORITY_CLASS_RELIABILITY` |

## 11. Failure and rerun policy

There is no majority-vote, median-score, adjudication, waiver, or manual-approval escape hatch.

After any calibration failure:

1. preserve the failed packages, outputs, hashes, and metrics;
2. identify whether the responsibility profile, brief, schema, package builder, or candidate caused failure;
3. increment the responsibility profile's `rubric_calibration_revision` and produce a new normative rubric/profile hash; if brief text changes, increment its version/hash too;
4. rebuild byte-identical packages under the new hash;
5. rerun all 15 goldens and at least three fresh full reviews from zero;
6. do not pool old and new run results.

Only one complete run set satisfying every applicable row may report `SEMANTIC_REVIEW_RELIABILITY_GATE — PASS`.
