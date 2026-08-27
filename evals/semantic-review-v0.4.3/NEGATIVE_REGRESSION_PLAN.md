# v0.4.3 Negative Reliability Regression Plan

This plan defines exactly eight negative regression families. Every fixture SHALL preserve its input/output hashes and SHALL prove that the reliability gate fails for the stated reason. A regression test passes only when the gate rejects the run set with the expected failure code.

| ID | Regression family | Controlled mutation | Required detection | Expected gate failure |
|---|---|---|---|---|
| `NR-01` | normative reviewer brief drift | Change exactly one normative instruction byte so one brief permits composition and another requires local duplication. | Brief hashes differ before review outputs are compared. | `FAIL/BRIEF_IDENTITY_MISMATCH` |
| `NR-02` | completeness-mode drift | Assign one identity `LOCAL` in one package and `COMPOSITIONAL` in another without an approved profile version change. | Package/profile hash mismatch; mixed run set rejected. | `FAIL/PACKAGE_IDENTITY_MISMATCH` |
| `NR-03` | repeated sibling-duplication execution error | In one full-review output, the same reviewer rejects exactly two distinct identities governed by the same responsibility rule because correctly sibling-owned semantics are absent from each LOCAL field. Freeze the same incorrect duplication interpretation and a valid `REVIEWER_EXECUTION_ERROR` classification for each identity; do not label either as normative ambiguity. | The repeated same-rule cluster is detected even though each individual mistake is determinate. | `FAIL/RESPONSIBILITY_RULE_INSTABILITY` |
| `NR-04` | omitted review identity | Remove exactly one expected identity record from one completed output. | Coverage below 100%; pending count is not used to hide omission. | `FAIL/IDENTITY_COVERAGE` |
| `NR-05` | previous verdict exposure | Add a prior completed review or verdict list to one reviewer package. | Exclusion scan and manifest declaration detect forbidden input. | `FAIL/PREVIOUS_VERDICT_EXPOSURE` before reliability calculation |
| `NR-06` | unexpected candidate semantic-byte drift | Change one semantic value byte while keeping the run grouped with the prior candidate. | Recomputed semantic/contract/package hashes differ. | `FAIL/PACKAGE_IDENTITY_MISMATCH` |
| `NR-07` | reviewer input manifest drift | Add, remove, reorder normatively, or alter one declared package file without a matching identical manifest across runs. | Manifest/package hashes differ. | `FAIL/PACKAGE_IDENTITY_MISMATCH` |
| `NR-08` | contradicted frozen golden | Make one reviewer emit a wrong but schema-compatible verdict/rationale pair for one frozen golden. | Golden verdict accuracy and, necessarily under the one-to-one approved/error mapping, rationale accuracy fall below 100%. | `FAIL/GOLDEN_VERDICT` and `FAIL/GOLDEN_RATIONALE` |

## v0.4.2 regression fixture

The v0.4.2 disagreement matrix MAY be reduced to a generic regression summary fixture containing:

- `665` identical review identities;
- `0` identity mismatch;
- `4` authorized semantic changes;
- `176` unchanged-field verdict flips;
- unchanged-flip distribution `input_invariants=60`, `visible_error=60`, `test_obligations=56`;
- Candidate B total rejected-field distribution `input_invariants=62`, `visible_error=60`, `test_obligations=58`, where the extra 4 are the authorized semantic changes (`input_invariants=2`, `test_obligations=2`) that remained `REJECTED -> REJECTED` rather than flipping;
- adjudication `REVIEW_RUBRIC_AMBIGUOUS=176`.

The fixture SHALL contain no RMA canonical prose and SHALL not designate Candidate A or Candidate B verdicts as correct. Its oracle is only that a v0.4.2-shaped run set must fail:

- unchanged three-review unanimity;
- normative responsibility/completeness disagreement;
- repeated disagreement under the same responsibility rules;
- balanced/imbalanced reliability statistics as applicable.

## Test isolation requirements

Each regression test SHALL start from one known-good frozen calibration package/run set, introduce only its named mutation, and verify:

1. the original known-good set passes;
2. the mutated set fails with the expected code;
3. unrelated failure codes remain absent; deterministic dependent codes named in the table remain present;
4. original fixture bytes are unchanged after the test;
5. no production Product Definition or product-specific artifact is required.

The frozen `NR-03` base set SHALL contain at least 200 unchanged identities with balanced margins and sufficient reliability headroom. Its two identity mutations therefore retain `three_review_unanimity >= 99%` and the balanced coefficient thresholds, proving that `FAIL/RESPONSIBILITY_RULE_INSTABILITY` is independently reachable rather than a side effect of another gate failure.

## Planned test mapping

| Regression | Planned test name |
|---|---|
| `NR-01` | `test_gate_rejects_one_normative_brief_byte_difference` |
| `NR-02` | `test_gate_rejects_completeness_mode_drift` |
| `NR-03` | `test_gate_rejects_repeated_same_rule_sibling_duplication_execution_errors` |
| `NR-04` | `test_gate_rejects_missing_review_identity` |
| `NR-05` | `test_gate_rejects_previous_verdict_exposure` |
| `NR-06` | `test_gate_rejects_unexpected_candidate_semantic_bytes` |
| `NR-07` | `test_gate_rejects_manifest_drift` |
| `NR-08` | `test_gate_rejects_golden_answer_contradiction` |

Count: `8` negative regression families.
