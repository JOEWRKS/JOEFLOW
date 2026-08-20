# v0.2 Behavioral Evaluation Aggregate Results

## Methodology

Twelve primary runs and six Treatment regressions used separate Codex agents created with `fork_turns="none"`. A run received no root history, paired result, other transcript, evaluator answer key, or hidden/shared scratchpad. Control received no Skill path or contents; Treatment explicitly loaded the current `joewrks-product-definition` package. Paired runs used identical prompts and immutable synthetic evidence, while every writable state/transcript path was unique.

## Results

| Eval | Control | Treatment initial | Treatment final | Final Δ | Verdict |
|---|---:|---:|---:|---:|---|
| EVAL-01 | 38 | 77 | 89 | +51 | PASS |
| EVAL-02 | 76 | 84 | 96 | +20 | PASS |
| EVAL-03 | 59 | 93 | 100 | +41 | PASS |
| EVAL-04 | 60 | 99 | 99 | +39 | PASS |
| EVAL-05 | 62 | 95 | 100 | +38 | PASS |
| EVAL-06 | 92 | 100 | 100 | +8 | PASS |
| **Average** | **64.5** | **91.3** | **97.3** | **+32.8** | **PASS** |

Final Treatment exceeds the 85 average target, every EVAL exceeds 75, and average improvement exceeds the recommended +20. EVAL-01 through EVAL-03 all show materially higher final unknown coverage than Control. Final critical failures: **0**.

## Unknown Discovery

Treatment-only or materially stronger discoveries included product topology and operator boundary for booking; evidence-derived email delivery uncertainty and pending-member quota; upload security, retention, malware, processing-after-transport, quota, page-leave, and concurrency; transitive permission-change ripple; explicit non-acceptance of privacy/security defaults under delivery pressure; and the prohibition on Figma Make inventing product behavior.

The refinement changed durable discovery breadth without increasing visible question count: independently tracked material unknowns rose from 5 to 15 in EVAL-01, 5 to 17 in EVAL-02, and 6 to 23 in EVAL-03. Remaining misses in final EVAL-01 include some detailed late-arrival/walk-in and resource-capacity variants; these were not repeated rationalization failures and did not justify taxonomy expansion.

## Question Quality

Treatment consistently opened with a high-fan-out decision: marketplace scope, inviter permission, upload job type, permission-change consequences, privacy export authorization, or contract-preserving handoff. It exposed one question at a time with options, recommendation, consequences, and evidence while retaining broader unknowns in state. No cosmetic question led a Treatment run.

## Evidence First

EVAL-02 Treatment inspected all fixture contracts before asking and separated known auth/roles/member limit from unknown invitation policy. EVAL-01 and EVAL-03 recorded the absence of inspectable project evidence instead of inventing it. EVAL-04 and EVAL-06 compiled supplied definitions rather than asking for facts already present. No final Treatment fabricated available evidence.

## Premature Behavior

Final Treatment counts: silent material invention **0**; premature implementation **0**; premature Closure **0**. EVAL-05 did not interpret “적당히 알아서 해” as acceptance and kept security/privacy decisions open. EVAL-04 invalidated approval after change. EVAL-06 rerun remained `READY_FOR_REVIEW` because the newly compiled digest lacked separately observable approval metadata.

## State Discipline

Every Treatment created authoritative state. EVAL-01 through EVAL-03 persisted distinct unknown IDs and remained OPEN; EVAL-04 incremented revision, superseded the old decision, invalidated approval, propagated stale state, recompiled downstream objects, and stopped at review; EVAL-05 preserved ten blockers under pressure; EVAL-06 persisted the contract and handoff with `NOT VERIFIED` visualization status.

## Rationalizations

The repeated initial weakness was observable umbrella compression: policies with different evidence and closure status were grouped into a single unknown. Control-specific failures included treating a change request as revised-definition approval and treating a speed request as authorization for security/privacy defaults. Treatment resisted the latter two using existing rules.

## Refinements

Only two instruction files changed. `SKILL.md` now requires a pre-question coverage sweep and one state record per independently answerable material decision. `interrogation-engine.md` explains that expiry, revocation, reuse, duplicates, and similar policies must remain separately traceable while only the highest-leverage question is shown to the user. No validator, schema, state-contract semantic, taxonomy, stable-ID, or Closure-metric change was made.

## Regression

All six Treatment scenarios were rerun in new `fork_turns="none"` contexts against the refined Skill. Scores changed by +12, +12, +7, 0, +5, and 0. No scenario regressed, all final scores passed, and critical failures remained zero.

## UX Burden

| Eval | Final UX |
|---|---:|
| EVAL-01 | 5 |
| EVAL-02 | 5 |
| EVAL-03 | 5 |
| EVAL-04 | 5 |
| EVAL-05 | 5 |
| EVAL-06 | 5 |
| **Average** | **5.0** |

The refinement increased state breadth without dumping the coverage inventory on users.

## Final Behavioral Verdict

**PASS.** v0.2 meets all behavioral thresholds: six isolated Control/Treatment pairs, six fresh final Treatment regressions, final average 97.3, every final score at least 89, average Control delta +32.8, UX average 5.0, and zero critical failures.

## Remaining Boundary

Not executed: Figma-native wireframe generation, Figma Make actual build, Figma Make drift audit, and full end-to-end dogfood. GitHub Actions remains unconfigured; local evaluation and validator verification are reported separately.

## Git

Target: `JOEWRKS/joewrks-product-definition`, branch `main`. Commit SHA and remote readback are reported after publication.
