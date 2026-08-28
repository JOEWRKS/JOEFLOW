# v0.4.3 Calibration Disposition — Environment Blocked

## Frozen disposition

`V0.4.3_IMPLEMENTATION_VERIFIED`

`REAL_RELIABILITY_CALIBRATION_BLOCKED_BY_ENVIRONMENT`

The repaired calibration input remains the exact commit
`748254d6def81080a2fd2736115a3ab5e0bde5a3`. The protected `main` authority
remains `efd96410f6401cbf9624328e94b795c315164b7f`.

This disposition records an execution-environment capability block only. It
does not change semantic-review behavior, the reviewer brief, responsibility
rules, the normative oracle, any golden answer, the 114-identity corpus, the
repaired control plane, thresholds, Product Definition, or `main`.

## Exact status boundary

| Boundary | Frozen status |
| --- | --- |
| specification | `VERIFIED` |
| implementation | `VERIFIED` |
| repaired calibration control plane | `VERIFIED_AFTER_RUN_01_REPAIR` |
| Run-01 | `INVALID / CONTROL_PLANE_DEFECT` |
| Run-02 semantic execution | `NOT_STARTED` |
| real reviewer reliability | `NOT_MEASURED` |
| calibration PASS | `NOT_CLAIMED` |
| calibration FAIL | `NOT_CLAIMED` |
| environment isolation | `UNAVAILABLE` |
| `REAL_CALIBRATION_ATTEMPTS` | `1` |
| `VALID_REAL_CALIBRATION_RUNS` | `0` |

The capability probe was not a semantic reviewer execution, so neither
counter changes. `rubric_calibration_revision` remains `1`; no rubric or
semantic defect was established.

## Preserved semantic authority

The following exact values are read back from repaired input
`748254d6def81080a2fd2736115a3ab5e0bde5a3`:

| Authority | Frozen value |
| --- | --- |
| oracle status | `PM_APPROVED_NORMATIVE_ORACLE` |
| normative oracle file SHA-256 | `4126bb8d316291d8362f04fe1160f53ad86adc73ec358effad7a84d104d7a173` |
| exact 15-pair tuple-set SHA-256 | `7ddc257c085f8e9de4722b01f09646c25891418fbc92d60e7a15425657acc4aa` |
| golden-cases file SHA-256 | `812d99c153c736fdd6eacdb0937ba924a83c642bc78f74674b6ad708154c84f3` |
| reviewer brief SHA-256 | `3d44f6c70536be375f8b76908b8d7cb2a48e4ad2b543800c8c6378502e9f526c` |
| responsibility profile / rubric SHA-256 | `f8010b9410bfb786cc3107e78a001e226bf30ce6cf8aafcfca303851dce56fc5` |
| review identity inventory SHA-256 | `e524f2371854596fec1b8241f1a1d1db9e5a2225d44f0cd7845fd5300974e033` |
| expected identity count | `114` |

The existing oracle still contains exactly 15 answer pairs. No pair is
modified by this evidence-only disposition.

## Capability evidence

The actual preflight result is:

`BLOCKED — MANIFEST_ONLY_ISOLATION_UNAVAILABLE`

The selected capability-only probe used an ephemeral Codex execution context
from `C:\Users\tjdwo\AppData\Local\Temp` with sandbox mode `read-only`. Its
context ID was `01a0477c-238c-7583-9a65-930275634782`.

The repository filesystem was visible. In particular, the forbidden Run-01
canary path
`D:\JOEWRKS\JOEWRKS-Product-v043-calibration-run-01\evals\semantic-review-v0.4.3\calibration\run-01`
could be enumerated and returned `controller`. Therefore:

`RUN01_READABLE = YES`

That single observation is sufficient to disqualify the environment: denial
was not enforced by the execution boundary. Repository-history and oracle-read
commands were policy-blocked, so this evidence does not overstate those checks
as verified denials.

No reviewer context was spawned, no semantic output was produced, and no
semantic execution retry occurred. The preflight had one attempt and zero
preflight retries; one policy-blocked compound observation was narrowed within
that same preflight. No exact transcript file was created by the ephemeral
invocation, so there is no transcript SHA-256 to preserve. The structured
evidence summary is
[`MANIFEST_ONLY_ISOLATION_CAPABILITY_EVIDENCE.json`](MANIFEST_ONLY_ISOLATION_CAPABILITY_EVIDENCE.json).

## Future unblock condition

Real calibration may resume only after a future execution environment proves,
before any semantic reviewer run, all of the following for each fresh worker or
context:

1. the worker/context is fresh;
2. the assigned reviewer package is readable;
3. the assigned run envelope is readable;
4. the repository and every worktree are unavailable;
5. Run-01 evidence is unavailable;
6. golden answers are unavailable;
7. the seed oracle is unavailable;
8. prior reviewer outputs are unavailable; and
9. sibling packages are unavailable.

Those denials must be enforced by the execution environment, not by reviewer
instructions. An OS, container, VM, or remote-worker boundary may be evaluated
in a future task; this disposition neither selects nor installs one.

## v0.4.4 boundary

`V0.4.4 = BLOCKED_ON_VALID_V043_RELIABILITY_CALIBRATION`

The planned paired downstream efficacy experiment has not started. This is not
a Product Definition blocker; it is solely the missing valid v0.4.3 reviewer
reliability measurement under enforced isolation.
