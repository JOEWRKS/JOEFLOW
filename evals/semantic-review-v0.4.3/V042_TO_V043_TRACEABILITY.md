# v0.4.2 Failure to v0.4.3 Requirement Traceability

Frozen evidence source: `eval/v0.4.2-rma-disposition@9e734326a5b13f446a19ff9547d142b213fcf045`.

This document traces diagnostic facts into generic requirements. It does not import RMA product semantics, treat either historical reviewer as an oracle, or reopen v0.4.2.

| v0.4.2 evidence | Diagnostic meaning | v0.4.3 requirement | Primary artifact | Verification |
|---|---|---|---|---|
| 665 identities, mismatch 0 | Review target identity was stable. | Preserve exact expected identity inventory and require 100% output coverage. | review spec §10; output schema | `NR-04`; structural gate |
| Candidate semantic changes 4; all remained rejected | Authorized candidate edits do not explain disagreement. | Separate candidate-byte changes from unchanged-identity reliability population. | reliability spec §4 | `NR-06` |
| 176 unchanged-field flips | Independent review was not repeatable. | Minimum three fresh identical-package reviews and >=99% unanimity. | reliability spec §§1,4 | v0.4.2 summary fixture |
| agreement 73.5338%; kappa 0.0321 | Raw agreement hid near-chance reliability under imbalanced margins. | Gate on balanced kappa or imbalanced Gwet AC1 plus minority agreement. | reliability spec §§6–7 | statistics tests in implementation plan |
| 62 `input_invariants` flips | Input predicates versus sibling authority/state semantics lacked an ownership boundary. | `FR-A09` owns input predicates only; sibling-owned constraints need not be copied. | field matrix | `G-001`–`G-003`, `NR-03` |
| 60 `visible_error` flips | Presentation was interpreted both as gated composition and unconditional standalone behavior. | `FR-A23` owns observable failure/recovery and authorized disclosure, with named sibling references. | field matrix | `G-004`–`G-006` |
| 58 `test_obligations` flips | Reviewers disagreed whether labels must restate complete semantics. | `FR-A25` owns stable verification references, not copied business prose. | field matrix | `G-007`–`G-009` |
| Candidate A brief: “interpret complete current canonical meaning” | Whole-contract reading permitted distributed meaning. | One canonical brief must state exact responsibility/composition semantics. | reviewer brief spec | `NR-01` |
| Candidate B brief: “fully supported for that exact field and scope; detect omitted constraints” | Exact-field reading permitted duplication requirements. | Ad-hoc per-run instructions forbidden and hash-detected. | reviewer brief spec | `NR-01` |
| Adjudication: ambiguity 176, false negatives 0, false positives 0 | Evidence could not select either reviewer as canonical truth. | Historical reviewer verdicts excluded from golden oracles; rubric/package errors distinct. | review spec §11; golden spec | `G-015`, `NR-05` |
| Common schema required fields but no completeness relation | Structural presence did not define semantic responsibility. | Mandatory responsibility profile and obligation index sidecar. | review spec §§4,7–9 | isolated spec audit Q1/Q2 |
| Same valid exact provenance used for incompatible verdicts | Provenance alone is necessary, not sufficient. | Review output binds evidence plus responsibility rule, completeness mode, and obligation IDs. | output schema proposal | `G-014` |
| Active superseded and missing provenance already fail generic authority checks | Package validity must precede candidate semantics. | `INPUT_PACKAGE_ERROR` has highest failure precedence. | review spec §14 | `G-012`, `G-013` |
| Rubric ambiguity was reported after two differently worded briefs | Instructions could vary without a formal identity gate. | Brief bytes/version/hash required and identical across runs. | reviewer brief spec; reliability spec | `NR-01` |
| v0.4.2 stopped before S1; no arms existed | Failure was pre-experiment intervention construction, not efficacy. | v0.4.3 is calibration/hardening only; no causal reuse or new efficacy claim. | review spec §1 | branch/content audit |
| Product Re-entry NO; Harness Re-entry YES | No missing product decision was established. | Keep Product Definition untouched and change only generic review specification. | compatibility decision | protected-tree diff |

## Coverage of PM-approved direction

| Approved item | Frozen location |
|---|---|
| architecture A, mandatory sidecar | `COMPATIBILITY_DECISION.md` |
| `action-conformance/1.0` retained | `COMPATIBILITY_DECISION.md` |
| 15 goldens | `GOLDEN_CASES_SPEC.md` |
| 8 negative families | `NEGATIVE_REGRESSION_PLAN.md` |
| three or more independent reviews | `RELIABILITY_GATE_SPEC.md` |
| identical package/brief hashes | `V043_REVIEW_CONTRACT_SPEC.md`, `RELIABILITY_GATE_SPEC.md` |
| complete identities, pending 0 | output schema, reliability spec |
| golden verdict/rationale accuracy 100% | golden spec, reliability spec |
| unexpected rubric/package errors 0 | golden spec, reliability spec |
| unchanged unanimity >=99% | reliability spec |
| normative/same-rule disagreement 0 | reliability spec |
| balanced kappa >=0.90 | reliability spec |
| imbalanced Gwet AC1 >=0.95 | reliability spec |
| minority agreement >=95% | reliability spec |
| no majority escape; version/hash change and rerun | review spec §13; reliability spec §11 |

## Regression use boundary

The v0.4.2 `176`-flip data MAY be represented by counts, identity classes, semantic fields, and reliability metrics in a generic test fixture. The RMA action contract, Product Definition, Figma, reviewer rationales, and product-specific canonical clauses SHALL remain evidence-only and SHALL NOT be dependencies of the generic runtime or review contract.
