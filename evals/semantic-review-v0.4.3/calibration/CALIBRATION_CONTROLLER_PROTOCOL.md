# v0.4.3 official calibration controller freeze

This calibration-only layer is product-neutral. It records no reviewer execution and no reviewer verdict.

- Full reviewer package SHA-256: `ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603`
- Reviewer brief SHA-256: `3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c`
- Common human evidence payload SHA-256: `265edb58fa58f690b0177d84c72f2190289a2bec26ac507a6fb28237dd68a5b3`
- `HUMAN_ADJUDICATION_COMPLETE = NO`
- Cohorts: exactly `C1`, `C2`, and `C3`
- Planned contexts: 3 full-review plus 45 one-case golden contexts, 48 unique total
- `REAL_CALIBRATION_RUNS = 0`

The official API is `evaluate_official_calibration(evidence, *, real_mode)` in `official_calibration_controller.py`. It accepts only raw, hash-bound output wrappers for all cohorts. Each wrapper carries the raw run envelope and output plus their exact SHA-256 values; each golden cohort also binds an output-set SHA-256. Scalar golden summaries are forbidden inputs.

The controller validates the exact package and brief identities, every context's manifest-only visibility, all 48 unique context IDs, full output/package identity, and the 15-case set in each cohort. It calls production `evaluate_goldens(...)` separately three times. Only a 15/15 verdict, 15/15 rationale, zero-unexpected-error result in every cohort is converted to the low-level all-pass summary passed to `evaluate_reliability_gate(...)`.

A future execution must stop as `BLOCKED — MANIFEST_ONLY_ISOLATION_UNAVAILABLE` if the declared isolation cannot be attested. Real mode remains unavailable until the manifest records two independent completed human response forms. No cohort envelopes, outputs, reports, or aggregate evidence are materialized by this freeze.
