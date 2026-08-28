# v0.4.3 calibration control-plane repair audit

## Verdict

`PASS`

`unresolved defect = 0`

The audit ran in a fresh read-only context. It did not edit files, create commits, push refs, execute a semantic reviewer, or create reviewer contexts.

## Independent findings

- Historical run-01 commits and trees match exactly: raw-freeze tree `f324e4070f5eeb1cbe5a2c659da05d6275673fa0`, final-evidence tree `5c348672b8efe41a8a14222efb4ec9c97e0dd342`; frozen inputs and raw outputs are unchanged.
- Root cause A reproduced on all three historical full envelopes: five fields versus production's exact six, yielding `PACKAGE_HASH_MISMATCH`.
- Root cause B reproduced on all three historical cohorts: the frozen raw items have three fields versus production's exact four, yielding `GOLDEN_OUTPUT_INVALID: binding: G-001`.
- Repaired full and golden envelopes share the canonical six-field contract and production `verify_run_envelope()` accepts both.
- Repaired golden wrappers copy the frozen case-manifest hash and production scoring accepts correctly assembled actual-path wrappers.
- Production semantic-review core and all frozen reviewer inputs are byte-identical to base. The full package remains `ccc2c5af60c74cde1b281ec7026bd8d42cac9717faf210c31fb3e8a719f59603`; the corpus remains 114 identities.
- Diagnostic regeneration exactly equals the checked-in evidence. Classification remains attempts `1`, valid runs `0`, official result `NOT MEASURED`, family `CALIBRATION_CONTROL_PLANE_DEFECT`.
- Repaired-path tests: `6/6 PASS`.
- Official-controller tests: `21/21 PASS`.
- Broader semantic-review tests: `125/125 PASS`.
- Production validators are not mocked and no prebuilt-wrapper shortcut bypasses actual assembly.
- No run-02 artifact, run-02 commit, or new reviewer context exists.
- `git diff --check` passed. Local, cached, and live remote `main` all remained `efd96410f6401cbf9624328e94b795c315164b7f`.
