# v0.4.2 RMA — Final Experiment Disposition

## Official outcome

- Classification: `STOPPED — TREATMENT_INTERVENTION_CONSTRUCTION_FAILED`
- Paired downstream efficacy result: `NOT RUN`
- Reason: Treatment intervention failed pre-freeze semantic review before S1 creation.

No implementation arm existed. This evidence does not establish that Treatment reduced drift, failed to reduce drift, outperformed Control, or was outperformed by Control.

## Frozen authority

- Repository baseline / remote main: `efd96410f6401cbf9624328e94b795c315164b7f`
- Official shared S0: `e557cd2a46c163f134acd0006eee84b19f9f9b8f`
- Approved Product Definition: revision `79`, digest `1f329295fa2f11bda80709a63c5f6005d0bf47f9549b8978c712059230780a9a`
- Shared Figma file key: `C8vxL0pVRja04HhqGFwSQU`

## Candidate evidence

### Candidate A

- Contract hash: `2dd2f41e996b37c22f6b960aee624160dd459b04afb31ef9e78c4e09cb76e1df`
- Review: `661 APPROVED`, `4 REJECTED`, `0 DEFERRED`, `0 PENDING`
- Raw full contract, completed review JSON, and actual review brief: `raw/candidate-a/`

### Candidate B

- Contract hash: `2621e7da2b576ca7d902989a720b6ed7af62b6c8895c2cfca77850421871e074`
- Review: `485 APPROVED`, `180 REJECTED`, `0 DEFERRED`, `0 PENDING`
- Raw full contract, completed review JSON, and actual review brief: `raw/candidate-b/`

Both complete review JSON files are preserved in this tree. `EVIDENCE_MANIFEST.json` records exact SHA-256, byte size, source path, candidate hash, and review counts; raw-evidence availability is not omitted.

## Deterministic identity comparison

- REVIEW_REQUIRED identities: `665`
- Identity mismatch: `0`
- Semantic changes between candidates: `4`
- Unchanged semantic verdict flips: `176`

| Candidate A verdict | Candidate B verdict | Count |
|---|---|---:|
| APPROVED | APPROVED | 485 |
| APPROVED | REJECTED | 176 |
| REJECTED | APPROVED | 0 |
| REJECTED | REJECTED | 4 |

## Reliability

- Agreement: `489 / 665 = 73.5338345865%`
- Disagreement: `176 / 665 = 26.4661654135%`
- Unchanged-field disagreement: `176 / 661 = 26.6263237519%`
- Positive agreement: `84.6422338569%`
- Negative agreement: `4.3478260870%`
- Cohen's kappa: `0.032087330466`

## Independent adjudication

- `FIRST_REVIEW_FALSE_NEGATIVE = 0`
- `SECOND_REVIEW_FALSE_POSITIVE = 0`
- `REVIEW_RUBRIC_AMBIGUOUS = 176`
- `CANDIDATE_SEMANTICALLY_CHANGED = 4`
- `UNRESOLVED = 0`

The immutable isolated adjudication output is preserved at `raw/adjudication/ADJUDICATION_RESULT.json`.

## Root cause

Primary failure: `REVIEW_RUBRIC_UNDERSPECIFIED`

Plus: `CONTRACT_REPRESENTATION_AMBIGUITY`

The frozen production contract requires semantic fields such as `input_invariants`, `visible_error`, and `test_obligations` structurally, but the review contract does not deterministically define whether each field must independently restate every applicable canonical constraint or whether semantics may be satisfied compositionally across sibling fields.

Therefore independent reviewers can produce incompatible verdicts while using:

- the same semantic field identities;
- valid exact provenance;
- the same canonical Product Definition.

The 176 verdict flips are not proven Product Definition defects and are not proven compiler/runtime-verifier defects.

## Experiment state

- Product Definition: `PASS / VERIFIED`
- Shared Figma: `PASS / VERIFIED`
- S0: `VALID / FROZEN`
- Treatment intervention construction: `FAIL PRE-S1`
- S1: `NOT CREATED`
- Control: `NOT RUN`
- Treatment: `NOT RUN`
- C0: `ABSENT`
- T0: `ABSENT`
- Paired downstream efficacy result: `NOT RUN`
- Product Re-entry: `NO`
- Harness Re-entry: `YES` for a separate post-v0.4.2 calibration/hardening workstream

## Refinement recommendation — do not implement in v0.4.2

Next workstream: `v0.4.3 — Deterministic Semantic Review Contract & Reliability Gate`

Required refinement families:

1. one byte-identical review instruction/rubric;
2. explicit semantic-field responsibility rules;
3. an explicit compositional-versus-local completeness rule;
4. golden adjudication cases for `input_invariants`, `visible_error`, and `test_obligations`;
5. a deterministic reviewer input manifest/hash;
6. a repeated-review reliability gate before accepting the rubric;
7. negative tests proving contradictory review interpretations fail the calibration gate.

Recommended later efficacy experiment: `v0.4.4 — Fresh Paired Downstream Efficacy Replication`.

Do not reuse v0.4.2 as the causal run after generic harness refinement.

## Evidence inventory

- `CONTRACT_REVIEW_IDENTITY_DIFF.md`
- `CONTRACT_REVIEW_DISAGREEMENT_MATRIX.json`
- `CONTRACT_REVIEW_REJECTION_FAMILIES.md`
- `CONTRACT_REVIEW_ADJUDICATION.md`
- `CONTRACT_REVIEW_RELIABILITY_REPORT.md`
- `V042_EXPERIMENT_DISPOSITION.md`
- `raw/candidate-a/`
- `raw/candidate-b/`
- `raw/adjudication/`
- `EVIDENCE_MANIFEST.json`
