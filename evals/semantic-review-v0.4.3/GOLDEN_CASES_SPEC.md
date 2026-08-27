# v0.4.3 Golden Adjudication Cases Specification

The calibration suite SHALL contain exactly 15 human-adjudicated cases before reviewer reliability runs begin. Historical Candidate A and Candidate B verdicts are evidence of instability, not oracle labels.

## Frozen case inventory

| ID | Category | Case | Expected verdict | Expected rationale code |
|---|---|---|---|---|
| `G-001` | input invariants | Canonical authority requires a non-empty reason input; the candidate omits the predicate from `input_invariants`. | `REJECTED_CANDIDATE` | `MISSING_OWNED_SEMANTIC` |
| `G-002` | input invariants | Required reason predicate is represented in `input_invariants` with exact current provenance. | `APPROVED` | `SUPPORTED_EXACTLY` |
| `G-003` | input invariants | An authority relationship is absent from `input_invariants` but correctly owned by `relationship_predicate` and linked through the obligation index. | `APPROVED` | `SUPPORTED_EXACTLY` |
| `G-004` | visible error | Canonical failure UX requires preserving submitted input; `visible_error` omits preservation. | `REJECTED_CANDIDATE` | `MISSING_OWNED_SEMANTIC` |
| `G-005` | visible error | The triggering input guard is not duplicated; `visible_error` references the rejection and input obligation and correctly owns presentation/recovery. | `APPROVED` | `SUPPORTED_EXACTLY` |
| `G-006` | visible error | Candidate adds a retry/recovery affordance that canonical authority does not allow. | `REJECTED_CANDIDATE` | `UNSUPPORTED_OVERREACH` |
| `G-007` | test obligations | One material semantic obligation has no stable test reference. | `REJECTED_CANDIDATE` | `MISSING_OWNED_SEMANTIC` |
| `G-008` | test obligations | All material obligations are covered by stable obligation IDs without duplicated semantic prose. | `APPROVED` | `SUPPORTED_EXACTLY` |
| `G-009` | test obligations | Copied semantic prose in a test obligation contradicts its owning field. | `REJECTED_CANDIDATE` | `CONTRADICTS_OWNER` |
| `G-010` | cross-cutting | A field adds an extra constraint with valid-looking structure but no canonical support. | `REJECTED_CANDIDATE` | `UNSUPPORTED_OVERREACH` |
| `G-011` | cross-cutting | One canonical clause is correctly projected across distinct owning fields with declared sibling references and no uncontrolled duplication. | `APPROVED` | `SUPPORTED_EXACTLY` |
| `G-012` | package/provenance | A lifecycle `superseded_sentinels` raw source record is both active and `SUPERSEDED`; no semantic review identity is created for the array. | `INPUT_PACKAGE_ERROR` | `ACTIVE_SUPERSEDED_SOURCE` |
| `G-013` | package/provenance | A review identity has missing provenance or an empty provenance set. | `INPUT_PACKAGE_ERROR` | `INVALID_PROVENANCE` |
| `G-014` | interpretation | Exact provenance is valid, but the emitted interpretation is not supported by the canonical value. | `REJECTED_CANDIDATE` | `UNSUPPORTED_OVERREACH` |
| `G-015` | rubric meta-case | A deliberately incomplete responsibility profile cannot determine which field owns an obligation. | `RUBRIC_ERROR` | `RESPONSIBILITY_UNDEFINED` |

## Case construction requirements

Each case SHALL be a self-contained hash-bound package with:

- canonical authority fixture and exact source refs;
- minimal action/lifecycle contract fixture;
- responsibility profile and semantic obligation index;
- expected identity inventory;
- canonical reviewer brief and output schema;
- expected verdict and rationale code in a separate hidden calibration answer file;
- a case manifest whose package hash is frozen before review.

The reviewer SHALL not receive the expected answer file. The calibration controller SHALL compare only after output finalization.

## Expected-error distinction

`G-012`, `G-013`, and `G-015` intentionally exercise finalized preflight failures rather than completed identity-level semantic reviews. Their expected error verdict/rationale pairs are read from `preflight_errors` and count as correct golden answers. `G-012` proves `PR-P01`: lifecycle `superseded_sentinels` is provenance-only, yields no synthetic `REVIEW_REQUIRED` identity, and fails before semantics when an active sentinel is superseded. “Unexpected `RUBRIC_ERROR` = 0” and “unexpected `INPUT_PACKAGE_ERROR` = 0” mean that no other golden or valid full-review scope may produce those verdicts. `G-015` is structurally hash-valid but contains a deliberately incomplete normative ownership taxonomy, so the correct result is `RUBRIC_ERROR`, not a hash/package failure.

## Human adjudication and freeze

Before reliability testing:

1. two human adjudicators independently classify every case under the proposed responsibility matrix;
2. they resolve differences using canonical evidence and record one expected verdict/rationale code;
3. the final 15-case answer bank, case manifests, responsibility profile, brief, and schemas are hashed;
4. any subsequent normative change increments the rubric or brief version/hash and invalidates prior calibration runs;
5. any failed calibration increments `rubric_calibration_revision` and the profile/rubric hash even if the diagnosed rule text is otherwise unchanged;
6. no v0.4.2 historical reviewer verdict is copied as the expected answer.

## Coverage accounting

- `input_invariants`: 3 cases (`G-001`–`G-003`)
- `visible_error`: 3 cases (`G-004`–`G-006`)
- `test_obligations`: 3 cases (`G-007`–`G-009`)
- unsupported extra constraint: 1 (`G-010`)
- valid compositional representation: 1 (`G-011`)
- active superseded lifecycle sentinel provenance: 1 (`G-012`)
- missing provenance: 1 (`G-013`)
- valid provenance with unsupported interpretation: 1 (`G-014`)
- ownership-indeterminate rubric: 1 (`G-015`)

Total: `15`.
