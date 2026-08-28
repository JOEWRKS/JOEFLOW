# v0.4.3 run-01 calibration control-plane postmortem

## Frozen disposition

- `REAL_CALIBRATION_ATTEMPTS = 1`
- `VALID_REAL_CALIBRATION_RUNS = 0`
- Official semantic reliability result: `NOT MEASURED`
- Root cause family: `CALIBRATION_CONTROL_PLANE_DEFECT`
- This is not a rubric failure and not a reviewer semantic-reliability result.
- Run-01 final evidence: `6f78bb610aeb52e6c475601b4327ce96f0fc509d`
- Run-01 raw-output freeze: `a4b641929f071e34eae922096ee7b21f3294b7ef`
- Run-01 pre-run lock: `f08eb78428b6f43ef76c2eed94f10be56f46cf9a`
- Frozen calibration input: `96b2b6e7c5435ccdbab5f7371073ec34c2d04078`

The historical commits and their trees remain immutable. The raw-freeze tree is `f324e4070f5eeb1cbe5a2c659da05d6275673fa0`; the final-evidence tree is `5c348672b8efe41a8a14222efb4ec9c97e0dd342`.

## Root cause A — full run-envelope mismatch

Production `verify_run_envelope()` requires exactly six fields:

1. `review_run_id`
2. `reviewer_context_id`
3. `reviewer_input_package_hash`
4. `reviewer_brief_hash`
5. `isolation_attestation`
6. `isolation_attestation_hash`

The frozen controller defined a five-field full envelope and a six-field golden envelope. Run-01 materialization followed that split and omitted `isolation_attestation_hash` from every full input. Production verification independently reproduces `PACKAGE_HASH_MISMATCH: invalid run-envelope fields` for C1, C2, and C3. C1 and C2 emitted no identity records; C3 emitted 114 records but consumed the same invalid input, so none of the three can be reliability evidence.

The repair replaces the split constants with one six-field contract. The calibration materializer computes the canonical attestation hash for every context and calls production `verify_run_envelope()` before returning. The official controller requires the same exact key set for full and golden envelopes.

## Root cause B — golden wrapper binding omission

Production `evaluate_goldens()` accepts only the exact raw item fields `case_id`, `case_manifest_hash`, `run_envelope`, and `review_output`. Run-01 assembly omitted `case_manifest_hash`, deterministically reproducing `GOLDEN_OUTPUT_INVALID: binding: G-001` before scoring.

The repaired assembler copies `case_manifest_hash` from the exact frozen case selected by `case_id`, validates the semantic output through production `validate_review_output()`, and writes the four-field binding. No reviewer supplies or changes this metadata.

## Actual-path regression

The new integration path writes reviewer semantic output bytes as `raw-output.txt`, materializes production-compatible envelopes, assembles wrappers, and invokes the official controller across `C1`, `C2`, and `C3` with 48 unique contexts. It uses production `verify_run_envelope()`, `validate_review_output()`, and `evaluate_goldens()` without mocks. Negative assertions cover a missing full attestation hash, different full/golden key sets, missing or wrong golden case hash, valid semantic output with incomplete binding, and scalar-summary shortcut rejection.

## Run-01 diagnostic salvage

Label: `RUN_01_GOLDEN_DIAGNOSTIC_ONLY`. This section is not official gate evidence. The diagnostic read the exact 45 raw golden outputs from the raw-freeze commit and added only `case_manifest_hash` in memory; raw bytes were not changed. Their envelope/output binding-manifest SHA-256 is `b55093f4f9386a0b1282241818478d31254ede1f2fc79a47056fb4fd4494ee6a`.

Production `evaluate_goldens()` did not accept any cohort because original reviewer outputs themselves contain validation defects. The first deterministic error in every cohort is `GOLDEN_OUTPUT_INVALID: G-007: INVALID_REFERENCE_SET: action:ACT-G-007:test_obligations:tests`. Per-output diagnosis also records invalid test-obligation references in G-007/G-008 (plus C1 G-009) and preflight binding mismatches in G-012/G-013/G-015. Exact findings are preserved in `RUN_01_DIAGNOSTIC.json`.

Decision-pair comparison is therefore separately labeled diagnostic-only, not a production golden score:

| Cohort | Verdict hits | Rationale-code hits | Production `evaluate_goldens()` |
| --- | ---: | ---: | --- |
| C1 | 14/15 | 13/15 | invalid raw output |
| C2 | 13/15 | 12/15 | invalid raw output |
| C3 | 12/15 | 11/15 | invalid raw output |

Label: `NON_OFFICIAL_DIAGNOSTIC`. Full inputs remain unmodified and invalid: C1 = invalid full input, C2 = invalid full input, C3 = invalid full input despite 114 emitted decisions. No hidden 114-identity seed-oracle plaintext artifact exists in the frozen run-01 final tree, so the optional C3 seed comparison is `NOT_AVAILABLE` and no result is claimed.

## Preserved authority

- Full reviewer package: `ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603`
- Reviewer brief: `3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c`
- Responsibility profile: `f8010b9410bfb786cc3107e78a001e226bf30ce6cf8aafcfca303851dce56fc5`
- Golden cases file: `812d99c153c736fdd6eacdb0937ba924a83c642bc78f74674b6ad708154c84f3`
- Normative oracle file: `4126bb8d316291d8362f04fe1160f53ad86adc73ec358effad7a84d104d7a173`
- Exact 15 answer-pair set: `7ddc257c085f8e9de4722b01f09646c25891418fbc92d60e7a15425657acc4aa`
- Production semantic-review core changes: none
- New reviewer contexts: `0`
