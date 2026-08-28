# v0.4.3 official calibration controller freeze

This calibration-only layer is product-neutral. It records no reviewer execution and no reviewer verdict.

- Full reviewer package SHA-256: `ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603`
- Reviewer brief SHA-256: `3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c`
- Common human evidence payload SHA-256: `7f267df32956beb47f1408b9a7ff6e64fa2e72d44fdf1a32537d34e394b23909`
- `HUMAN_ADJUDICATION_COMPLETE = NO`
- `HUMAN_ADJUDICATION_REQUIRED = NO`
- Historical human evidence status: `OPTIONAL_EXTERNAL_VALIDATION_NOT_REQUIRED_FOR_V043_CALIBRATION` (0/2 completed forms; no human validation is claimed)
- Frozen normative oracle: `PM_APPROVED_NORMATIVE_ORACLE`, SHA-256 `4126bb8d316291d8362f04fe1160f53ad86adc73ec358effad7a84d104d7a173`, 1648 bytes, exact canonical 15-pair tuple-set SHA-256 `7ddc257c085f8e9de4722b01f09646c25891418fbc92d60e7a15425657acc4aa`
- Cohorts: exactly `C1`, `C2`, and `C3`
- Planned contexts: 3 full-review plus 45 one-case golden contexts, 48 unique total
- `REAL_CALIBRATION_RUNS = 0`

The official API is `evaluate_official_calibration(evidence, *, real_mode)` in `official_calibration_controller.py`. It accepts only raw, hash-bound output wrappers for all cohorts. Each wrapper carries the raw run envelope and output plus their exact SHA-256 values; each golden cohort also binds an output-set SHA-256. Scalar golden summaries are forbidden inputs.

The controller freezes and hash-binds every raw output wrapper before loading the trusted oracle. It then validates the exact PM-approved oracle status, file hash and bytes, ordered 15 case IDs, and exact canonical verdict/rationale tuple-set hash. Caller-supplied oracle bytes, expected pairs, and golden summaries are forbidden. The controller additionally binds the full reviewer package to its trusted controller-side package hash and declared file inventory, and binds the golden-package bank to its exact controller-side file SHA-256/byte commitment and each case's verified package hash. It scans every actual reviewer-visible package file and every hash-bound run-envelope context for oracle bytes, frozen answer pairs, prior reviewer results, or structured correction hints; visibility flags alone are never proof of this firewall. The controller validates the exact package and brief identities, every context's manifest-only visibility, all 48 unique context IDs, full output/package identity, and the 15-case set in each cohort. It calls production `evaluate_goldens(...)` separately three times. Only a 15/15 verdict, 15/15 rationale, zero-unexpected-error result in every cohort is converted to the low-level all-pass summary passed to `evaluate_reliability_gate(...)`.

A future execution must stop as `BLOCKED — MANIFEST_ONLY_ISOLATION_UNAVAILABLE` if the declared isolation cannot be attested. Reviewer packages and contexts must never receive oracle bytes, expected pairs, prior results, or correction hints. The frozen oracle precedes every reviewer run and cannot be changed by any reviewer result; a normative change requires a new rubric calibration revision, a new oracle hash, and a complete calibration rerun. No cohort envelopes, outputs, reports, or aggregate evidence are materialized by this freeze.
