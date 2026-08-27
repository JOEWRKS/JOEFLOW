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

A determinate mistake that demands sibling-owned prose from one identity is `REVIEWER_EXECUTION_ERROR`, not normative ambiguity. If the same incorrect duplication interpretation appears on at least two distinct identities governed by the same responsibility rule, each identity may retain that execution-error classification, but the run set fails `FAIL/RESPONSIBILITY_RULE_INSTABILITY`.

## 6. Frozen metric population and equations

### 6.1 Common population and alignment

Let:

- `m` be the number of comparable full-review runs, with `m >= 3`;
- `N` be the number of expected unchanged review identities, with `N > 0`;
- `C = {APPROVED, REJECTED_CANDIDATE}` and `K = |C| = 2`;
- `x[i,j]` be reviewer `j`'s verdict for the `i`th identity after sorting exact `review_identity` strings by Unicode code-point order;
- `n[i,c]` be the number of reviewers assigning category `c` to identity `i`.

Golden cases, preflight diagnostics, reviewer explanations, and rationale codes are not observations in these reliability coefficients. Every run SHALL have the exact same identity set and immutable package/semantic hashes before alignment; source order in output JSON is irrelevant after identity-keyed sorting.

If `m < 3`, `N = 0`, an identity is missing/extra/duplicated, packages differ, or any full-review record contains `RUBRIC_ERROR`, `INPUT_PACKAGE_ERROR`, or an unknown verdict, structural acceptance fails and all set-level coefficients are reported as JSON `null` with a reason code. Error verdicts are never dropped, coerced to rejection, or treated as additional metric categories.

### 6.2 Pairwise unweighted nominal Cohen's kappa

For each reviewer pair `(a,b)`:

```text
p_o(a,b) = (1/N) * sum_i I[x[i,a] = x[i,b]]
p_a(c)   = (1/N) * sum_i I[x[i,a] = c]
p_b(c)   = (1/N) * sum_i I[x[i,b] = c]
p_e(a,b) = sum_(c in C) p_a(c) * p_b(c)
kappa_C(a,b) = (p_o(a,b) - p_e(a,b)) / (1 - p_e(a,b))
```

This is unweighted nominal Cohen kappa over the two frozen verdict categories. Compute it for every unordered pair of the `m` reviewers. If `1 - p_e(a,b) = 0`, that pair's kappa is `null` with reason `ALL_ONE_CLASS_CHANCE_DENOMINATOR`; do not substitute `1`, `0`, or percent agreement.

### 6.3 Multi-rater unweighted nominal Fleiss' kappa

```text
P_i       = [sum_(c in C) n[i,c] * (n[i,c] - 1)] / [m * (m - 1)]
P_bar     = (1/N) * sum_i P_i
p_c       = [sum_i n[i,c]] / [N * m]
P_e_F     = sum_(c in C) p_c^2
kappa_F   = (P_bar - P_e_F) / (1 - P_e_F)
```

Use all `m` reviewers and the same aligned identities. If `m < 3` or `N = 0`, report `null` with the corresponding input reason. If `1 - P_e_F = 0`, report `null` with reason `ALL_ONE_CLASS_CHANCE_DENOMINATOR`.

### 6.4 Multi-rater unweighted nominal Gwet AC1

The only permitted AC1 variant is the multi-rater, unweighted nominal coefficient using the same pair-agreement `P_bar` and the two fixed categories:

```text
p_c       = [sum_i n[i,c]] / [N * m]
P_e_AC1   = [sum_(c in C) p_c * (1 - p_c)] / (K - 1)
AC1       = (P_bar - P_e_AC1) / (1 - P_e_AC1)
K         = 2
```

Do not substitute a two-rater marginal formula, weighted AC2, category-specific AC1, missing-rating variant, or software-library default. For `K = 2`, `P_e_AC1 <= 1/2`, so the denominator is positive whenever the common population is valid. An all-one-class, unanimously rated population has `P_e_AC1 = 0` and `AC1 = 1`.

### 6.5 Minority-class agreement

Let pooled category totals be `T_c = sum_i n[i,c]`.

1. If exactly one category has the smaller positive `T_c`, it is `c_min`.
2. Let `D = count_i[n[i,c_min] > 0]`.
3. Let `U = count_i[n[i,c_min] = m]`.
4. `minority_class_agreement = U / D`.

If the pooled totals tie, there is no unique minority and the metric is `null` with reason `NO_UNIQUE_MINORITY`. If the smaller total is zero, `D = 0` and the metric is `null` with reason `MINORITY_CLASS_UNOBSERVED`; it MUST NOT be reported as `1.0`. Golden sensitivity cannot substitute for the required full-review minority metric.

### 6.6 Exact arithmetic and reporting

All counts, proportions, coefficients, balance checks, and threshold comparisons SHALL use exact reduced rational arithmetic equivalent to Python `fractions.Fraction`. Compare against exact thresholds `9/10`, `19/20`, `99/100`, and `1/20`; do not convert to binary floating point and do not round before a gate decision.

Each non-null metric report SHALL store its reduced `{numerator, denominator}` and a separate six-decimal display string. The display string uses exact round-half-even at six places by integer quotient/remainder comparison; it is presentation only. A `null` metric SHALL store a stable reason code and never satisfies a numeric threshold when that metric is required by the selected gate branch.

### 6.7 Edge-case table

| Condition | Required result |
|---|---|
| fewer than 3 comparable full reviewers | all set-level metrics `null`; `FAIL/INSUFFICIENT_INDEPENDENT_RUNS` |
| zero aligned identities | all metrics `null`; structural identity/coverage failure |
| identity-set or immutable-byte mismatch | all metrics `null`; applicable package/identity failure |
| any full-review `RUBRIC_ERROR` or `INPUT_PACKAGE_ERROR` | all metrics `null`; `FAIL/UNEXPECTED_ERROR_VERDICT` |
| all ratings in one category | Cohen pairs `null`; Fleiss `null`; Gwet AC1 computed (`1` when unanimous); minority agreement `null` |
| pooled category tie | minority agreement `null/NO_UNIQUE_MINORITY`; other metrics computed |
| negative coefficient | preserve the exact negative rational value; do not clamp |

## 7. Balanced/imbalanced gate selection

For each reviewer `j` and category `c`, compute `share[j,c] = count_i[x[i,j] = c] / N` exactly.

- `BALANCED` iff every reviewer has `share[j,APPROVED] >= 1/20` and `share[j,REJECTED_CANDIDATE] >= 1/20`. Equality at exactly 5% is balanced.
- `IMBALANCED` otherwise. This includes an all-one-class run or any run in which one category is below 5%.

Golden/meta/package-error fixtures are excluded from this classification because only the valid full-review identity population is used.

For `BALANCED` populations:

- every pairwise Cohen kappa SHALL be non-null and `>= 9/10`;
- the exact minimum across all pairwise Cohen values SHALL be `>= 9/10`;
- Fleiss kappa SHALL be non-null and `>= 9/10`;
- Gwet AC1 and minority agreement are reported diagnostically but do not replace the kappa gates.

For `IMBALANCED` populations:

- multi-rater Gwet AC1 SHALL be non-null and `>= 19/20`;
- minority-class agreement SHALL be non-null and `>= 19/20`;
- pairwise Cohen and Fleiss values are diagnostic and do not replace either required imbalanced metric.

A required `null` metric fails its branch. In particular, an all-one-class full review has AC1 `1` but minority agreement `null`, so it fails `FAIL/MINORITY_CLASS_RELIABILITY` rather than receiving a sensitivity exemption.

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
