# v0.4.3 Fresh Isolated Specification Audit

## Verdict

`PASS`

- Unresolved ambiguity count: `0`
- Auditor context: `/root/v043_pm_repair_final_fresh_audit`
- Audit type: fresh isolated complete consistency audit
- Existing `V043_SPEC_AUDIT.md`: excluded from evidence and not read
- Specification status: specification/implementation-plan only; implementation, calibration, reviewer runs, and efficacy testing remain not started

## Exact authorities and scope

- Frozen implementation/schema authority and current `main`: `efd96410f6401cbf9624328e94b795c315164b7f`
- Frozen v0.4.2 disposition/adjudication evidence: `9e734326a5b13f446a19ff9547d142b213fcf045`
- Original v0.4.3 specification commit: `7ffbc60e869f1681b48dd75e2085422d979ac14a`
- Audit worktree: `D:\JOEWRKS\JOEWRKS-Product-v043-review-reliability-spec`
- Observed `HEAD` during audit: `7ffbc60e869f1681b48dd75e2085422d979ac14a`
- `7ffbc60e869f1681b48dd75e2085422d979ac14a` has the single parent `efd96410f6401cbf9624328e94b795c315164b7f`.
- Local `main`, `origin/main`, and the merge base of `HEAD` with the frozen authority all resolve to `efd96410f6401cbf9624328e94b795c315164b7f`.
- The repair is a working-tree change directly atop `7ffbc60e869f1681b48dd75e2085422d979ac14a`; a normal commit from this state has the required repair parent without history rewriting.

The audit read all ten peer artifacts directly:

1. `COMPATIBILITY_DECISION.md`
2. `FIELD_RESPONSIBILITY_MATRIX.md`
3. `GOLDEN_CASES_SPEC.md`
4. `IMPLEMENTATION_PLAN_V043.md`
5. `NEGATIVE_REGRESSION_PLAN.md`
6. `RELIABILITY_GATE_SPEC.md`
7. `REVIEWER_BRIEF_SPEC.md`
8. `REVIEW_OUTPUT_SCHEMA_PROPOSAL.json`
9. `V042_TO_V043_TRACEABILITY.md`
10. `V043_REVIEW_CONTRACT_SPEC.md`

It also read the frozen action/lifecycle schemas, the current production downstream contract/provenance/schema/invariant/verifier core, and the frozen v0.4.2 disposition, identity comparison, reliability, candidate briefs, disagreement matrix, and adjudication evidence.

## 1. Schema, sentinel, responsibility, and output identity checks

The frozen action schema contains exactly `26` properties whose schema is `$ref: #/$defs/semanticField`. The frozen lifecycle schema contains exactly `12`. Lifecycle `superseded_sentinels` is instead exactly an array whose items are `$ref: #/$defs/source`; it has no semantic-field wrapper, `value`, `source_refs`, or `derivation` and cannot be `REVIEW_REQUIRED`.

The responsibility matrix contains exactly `38` unique semantic responsibility rows: `FR-A01` through `FR-A26` and `FR-L01` through `FR-L12`. The canonical reviewer-brief table contains the same `38` rule/field/mode assignments. No `FR-L13` responsibility exists. The only peer-text occurrence of `FR-L13` is the implementation plan's explicit statement that it is schema-ineligible.

`PR-P01` is correctly outside the semantic responsibility set. It applies provenance/package preflight to raw lifecycle sentinel records. Neither `PR-P01` nor `superseded_sentinels` can appear in a semantic review record. `G-012` creates no synthetic lifecycle review identity and reaches the finalized preflight result:

```text
INPUT_PACKAGE_ERROR / ACTIVE_SUPERSEDED_SOURCE
```

The output schema proposal parses as valid JSON and its closed enums independently match the baseline:

- `semantic_field`: `38` values, exactly the `26 + 12` baseline semantic fields;
- `responsibility_rule_id`: `38` values, exactly `FR-A01`–`FR-A26` plus `FR-L01`–`FR-L12`;
- excluded from both applicable record enums: `superseded_sentinels`, `PR-P01`, and `FR-L13`.

The current production core confirms the architectural boundary used by the specification: compilation discovers semantic fields only by the schema's `semanticField` reference, `REVIEW_REQUIRED` proves only provenance plus a non-empty explanation, raw lifecycle sentinels are verified separately, and runtime verification consumes compiled `input_invariants`, `default_result`, and `result_expectations` without defining cross-field review completeness.

## 2. NR-03 and same-rule stability

The generic gate fails when two or more distinct disagreement identities share one responsibility rule, regardless of adjudication classification. The frozen `NR-03` fixture narrows that general rule to exactly two distinct identities in one review, under one rule, with the same incorrect requirement to duplicate sibling-owned semantics. Each identity is independently classified `REVIEWER_EXECUTION_ERROR`, not normative ambiguity, because the frozen ownership/completeness rule makes the correct result mechanically unique.

Independent reachability readback uses a balanced `N = 200`, three-review population. Start with three identical runs containing `100 APPROVED` and `100 REJECTED_CANDIDATE`; in one run change exactly two `APPROVED` identities governed by the same rule to `REJECTED_CANDIDATE` using the same sibling-duplication mistake.

- reviewer shares: `(1/2, 1/2)`, `(1/2, 1/2)`, `(49/100, 51/100)` — all balanced;
- three-review unanimity: `198/200 = 99/100 = 0.990000`;
- pairwise Cohen kappas: `1`, `49/50`, `49/50`;
- Fleiss kappa: `22199/22499 = 0.986666`;
- Gwet AC1: `22201/22501 = 0.986667`;
- minority-class agreement: `49/50 = 0.980000` (diagnostic on the balanced branch);
- golden verdict/rationale results, package identity, structural coverage, isolation, and normative-disagreement count remain passing.

Therefore `FAIL/RESPONSIBILITY_RULE_INSTABILITY` is independently reachable while every other threshold passes. `G-003`, `G-005`, and `G-008` remain unchanged positive cases proving that the correct compositional/reference interpretation is accepted.

## 3. Negative-family reachability

Exactly eight unique negative families are defined. Their planned controlled mutations reach the expected failures without requiring product-specific authority:

| Family | Independent reachability result |
|---|---|
| `NR-01` | one normative brief-byte identity difference is classified first as `FAIL/BRIEF_IDENTITY_MISMATCH` |
| `NR-02` | one unversioned completeness-mode/profile difference changes the package identity and reaches `FAIL/PACKAGE_IDENTITY_MISMATCH` |
| `NR-03` | the two-identity same-rule determinate execution-error construction above reaches only `FAIL/RESPONSIBILITY_RULE_INSTABILITY` |
| `NR-04` | removing one expected completed record makes exact coverage fail as `FAIL/IDENTITY_COVERAGE` |
| `NR-05` | exposing one prior verdict is detected before reliability calculation as `FAIL/PREVIOUS_VERDICT_EXPOSURE` |
| `NR-06` | changing one semantic value byte changes the contract/package identity and reaches `FAIL/PACKAGE_IDENTITY_MISMATCH` |
| `NR-07` | adding, removing, reordering, or altering a declared manifest file changes the manifest/package identity and reaches `FAIL/PACKAGE_IDENTITY_MISMATCH` |
| `NR-08` | one schema-valid wrong golden verdict/rationale pair makes both exact accuracies less than `1` and reaches `FAIL/GOLDEN_VERDICT` plus `FAIL/GOLDEN_RATIONALE` |

The test-isolation rule requires the original known-good set to pass, only the named mutation to be introduced, dependent codes to be explicit, and the source fixture bytes to remain unchanged.

## 4. Reliability formulas and independent vector readback

The coefficient population is the exact common set of unchanged full-review identities after sorting exact `review_identity` strings by Unicode code-point order. The categories are fixed to `C = {APPROVED, REJECTED_CANDIDATE}`. Goldens, preflight diagnostics, explanations, and rationale codes are excluded from coefficient observations. Missing/extra/duplicate identities, immutable-byte/package mismatch, `N = 0`, fewer than three comparable full reviewers, an unknown verdict, or any full-review `RUBRIC_ERROR`/`INPUT_PACKAGE_ERROR` invalidates the common population; required set-level metrics become JSON `null` with a stable reason and cannot satisfy a threshold.

For each reviewer pair `(a,b)`, nominal unweighted Cohen kappa is:

```text
p_o = sum_i I[x[i,a] = x[i,b]] / N
p_e = sum_c p_a(c) p_b(c)
kappa_C = (p_o - p_e) / (1 - p_e)
```

For all `m >= 3` reviewers, nominal unweighted Fleiss kappa is:

```text
P_i = sum_c n[i,c](n[i,c]-1) / (m(m-1))
P_bar = sum_i P_i / N
p_c = sum_i n[i,c] / (Nm)
P_e_F = sum_c p_c^2
kappa_F = (P_bar - P_e_F) / (1 - P_e_F)
```

The only permitted multi-rater unweighted nominal Gwet coefficient is AC1 with frozen `K = 2`:

```text
P_e_AC1 = sum_c p_c(1-p_c) / (K-1)
AC1 = (P_bar - P_e_AC1) / (1 - P_e_AC1)
```

For minority agreement, the unique smaller positive pooled class is `c_min`, `D` counts identities where at least one reviewer selects it, `U` counts identities where all reviewers select it, and the metric is `U/D`. A pooled tie is `null/NO_UNIQUE_MINORITY`; a zero smaller total is `null/MINORITY_CLASS_UNOBSERVED`.

All computation and threshold comparisons use reduced exact rationals. Balance is true only when every reviewer's share of both classes is at least `1/20`; equality is balanced and a share below `1/20` is imbalanced. No binary float or rounded display value participates in a decision. A non-null report stores reduced numerator/denominator plus a separate six-decimal exact round-half-even display.

Independent recalculation of every implementation-plan fraction/display produced:

### Balanced disagreement vector

```text
runs = [A,A,R,R], [A,R,R,R], [A,A,R,R]
reviewer shares = (1/2,1/2), (1/4,3/4), (1/2,1/2)
pairwise Cohen = 1/2, 1, 1/2
P_bar = 5/6
pooled shares = 5/12, 7/12
P_e_F = 37/72
Fleiss = 23/35 = 0.657143
P_e_AC1 = 35/72
AC1 = 25/37 = 0.675676
minority agreement = 1/2 = 0.500000
```

### Imbalanced prevalence vector

```text
runs = [A x20,R], [A x20,R], [A x21]
reviewer shares include R = 0 < 1/20 in the third run
pairwise Cohen = 1, 0, 0
P_bar = 61/63
pooled shares = 61/63, 2/63
P_e_F = 3725/3969
Fleiss = 59/122 = 0.483607
P_e_AC1 = 244/3969
AC1 = 3599/3725 = 0.966174
minority agreement = 0 = 0.000000
```

### Null and edge semantics

- All-one-class unanimous population: each Cohen pair is `null/ALL_ONE_CLASS_CHANCE_DENOMINATOR`; Fleiss is the same null; AC1 is exactly `1`; minority agreement is `null/MINORITY_CLASS_UNOBSERVED`. The imbalanced gate still fails because required minority reliability is null.
- Perfect balanced pooled tie: Cohen, Fleiss, and AC1 are exactly `1`; minority agreement is `null/NO_UNIQUE_MINORITY` and is diagnostic only on the balanced branch.
- `m < 3`, `N = 0`, alignment/hash/identity failure, or any full-review error verdict makes all set-level coefficients null with the specified structural/error failure.
- A negative coefficient is preserved exactly and is never clamped.
- Thresholds are exact: unanimity `99/100`, balanced Cohen/Fleiss `9/10`, imbalanced AC1 `19/20`, minority agreement `19/20`, and prevalence floor `1/20`.

## 5. Goldens and the six original ambiguity questions

The golden inventory contains exactly `15` unique cases, `G-001` through `G-015`. The three expected-error cases are `G-012`, `G-013`, and `G-015`; all other error verdicts are unexpected. The negative inventory contains exactly `8` unique families, `NR-01` through `NR-08` (each also appears once in the planned-test mapping, without creating another family).

The six original questions now resolve as follows:

1. **Can two compliant reviewers still disagree about whether a canonical constraint belongs in `input_invariants` vs `visible_error` vs `test_obligations`?** `PASS — No.` `FR-A09`, `FR-A23`, and `FR-A25` define unique ownership and required secondary references; `G-001`–`G-009` exercise both omissions and valid composition.
2. **Can one reviewer require semantic duplication that another permits to be compositional?** `PASS — No.` The frozen `LOCAL`, `COMPOSITIONAL`, and `REFERENCE_ONLY` modes plus allowed-sibling and must-not-duplicate rules make that interpretation determinate. A contrary single review is execution error; repetition is same-rule instability.
3. **Can review instructions vary between runs without hash mismatch?** `PASS — No.` Exact brief bytes/version/hash and package identity are required. Specific-first cross-run classification reports brief drift before the package mismatch caused solely by those bytes.
4. **Can rubric ambiguity still be mislabeled as candidate defect?** `PASS — No.` Failure precedence and the closed verdict/rationale mapping require `RUBRIC_ERROR/RESPONSIBILITY_UNDEFINED` or `RUBRIC_ERROR/COMPLETENESS_UNDEFINED`; `G-015` freezes the ownership-indeterminate case.
5. **Are reliability thresholds defined before calibration?** `PASS — Yes.` Run counts, structural/golden/error gates, unanimity, disagreement gates, formulas, branch thresholds, null behavior, and rerun/version policy are frozen before outputs are observed.
6. **Can the proposed gate detect a v0.4.2-style 176 unchanged-field flip?** `PASS — Yes.` The generic v0.4.2-shaped fixture preserves the exact unchanged population and requires failures for unanimity, normative responsibility/completeness disagreement, repeated same-rule disagreement, and the applicable reliability branch.

## 6. Corrected v0.4.2 evidence populations

Direct recomputation from the frozen disagreement matrix gives:

- exact review identities: `665`, mismatch `0`;
- authorized semantic changes: `4`;
- semantically unchanged identities: `661`;
- confusion matrix: `485 APPROVED→APPROVED`, `176 APPROVED→REJECTED`, `0 REJECTED→APPROVED`, `4 REJECTED→REJECTED`;
- unchanged verdict flips: exactly `176`, distributed as `input_invariants=60`, `visible_error=60`, `test_obligations=56`;
- Candidate B rejections: exactly `180`, distributed as `input_invariants=62`, `visible_error=60`, `test_obligations=58`.

The difference between `176` unchanged flips and `180` Candidate B rejections is exactly the four authorized semantic changes:

- `action:SCR-002-A04:input_invariants`
- `action:SCR-002-A04:test_obligations`
- `action:SCR-002-A05:input_invariants`
- `action:SCR-002-A05:test_obligations`

All four remained `REJECTED → REJECTED`; two belong to `input_invariants` and two to `test_obligations`. They are candidate-change evidence, not reviewer-instability flips. Frozen adjudication independently records `REVIEW_RUBRIC_AMBIGUOUS=176`, `FIRST_REVIEW_FALSE_NEGATIVE=0`, `SECOND_REVIEW_FALSE_POSITIVE=0`, and `UNRESOLVED=0`.

The official v0.4.2 result remains `STOPPED — TREATMENT_INTERVENTION_CONSTRUCTION_FAILED`, with paired efficacy `NOT RUN`. No implementation arm existed, so these data are calibration diagnostics only and do not become product authority or efficacy evidence.

## 7. Repository boundary and final consistency

- Relative to `7ffbc60e869f1681b48dd75e2085422d979ac14a`, every working-tree change is under `evals/semantic-review-v0.4.3/`; there is no changed path outside that directory.
- Relative to `efd96410f6401cbf9624328e94b795c315164b7f`, production `skills/joewrks-product-definition/downstream/` is byte-unchanged.
- Relative to the same authority, top-level `product-definition/` and the non-downstream Product Definition skill files are byte-unchanged.
- The ten peer artifacts agree on schema identity, responsibility count, sentinel handling, verdict/error separation, golden and negative counts, formula population, exact thresholds, failure precedence, rerun/version behavior, v0.4.2 evidence boundary, and the implementation/calibration boundary.
- `joewrks.action-conformance/1.0` remains unchanged; `joewrks.semantic-review/1.0` is specified only as a mandatory hash-bound review sidecar.
- Implementation, materialized artifacts, calibration execution, reviewer runs, action-contract migration, production integration, and efficacy testing are explicitly outside this phase.

Final result: `PASS`, unresolved ambiguity `0`.
