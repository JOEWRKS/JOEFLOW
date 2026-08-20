# EVAL-04 Comparison

## Outcome

| Run | Score | UX | Critical failure |
|---|---:|---:|---|
| Control | 60/100 | 5/5 | None |
| Initial Treatment | 99/100 | 5/5 | None |
| Final Treatment (rerun) | 99/100 | 5/5 | None |

Final Treatment delta versus Control: **+39**. Initial-to-final Treatment change: **0**.

## Material Unknowns

Expected behavior is decision replacement, revision increment, approval invalidation, stale propagation through requirement/rule/flow/screen/acceptance/task, rediscovery, contradiction prevention, and reopening before revalidation.

Control named the full downstream object set and a sensible guest scope, but missed the outstanding exact-revision approval and did not evidence rediscovery. Both Treatment runs cover every expected territory and find no new product unknown after an evidenced search; both correctly retain revision approval as the only closure decision.

## First Question

Control asked no question and treated the direct instruction as approval. Applying the policy without a clarifying question is efficient, but treating it as approval of the complete revised definition is incorrect.

Initial Treatment’s first and only question is “revision 8 … 을 승인하시나요?” after applying, recompiling, and validating the change. This is the correct closure question and timing.

Final Treatment identifies that exact approval and digest as the only remaining action, but states the requirement rather than directly asking the user to approve or reject it. This earns a one-point prioritization deduction.

## Ordering

Control jumps from impact narration to “revision 8로 확정.” Both Treatment runs reopen and invalidate approval, supersede the old decision, stale dependents, recompile, rediscover/revalidate, and move to review. Initial Treatment then asks for approval; final Treatment reports it as the required next action.

## Evidence First

All runs read the immutable revision-7 fixture. Control used it for a narrative impact analysis. Both Treatment runs additionally materialize and validate the baseline, inspect dependencies, rediscover after recompilation, and report final validator outputs and digest.

## Silent Assumptions

Control silently assumes the change instruction approves the entire revised definition. Neither Treatment run assumes new product behavior. Final Treatment is especially explicit that it does not invent unsupported failure or recovery behavior.

## Premature Build / Closure

No run edits source. Control prematurely declares the specification-level revision complete and approved without durable recompilation or revalidation. Both Treatment runs remain `READY_FOR_REVIEW`, explicitly not `CLOSED`.

## State Discipline

Control writes only a transcript and describes stale/superseded effects without applying them. Both Treatment runs preserve history and stable IDs, perform stale-to-current recompilation across every dependent object, clear approval, increment the revision, validate, and persist authoritative state. Final Treatment additionally records the stale/recompile list in `project.revision_history`.

## Rationalizations

Control’s observable rationalization is “이 지시를 새 승인으로 보고,” which bypasses the required approval invalidation/reapproval boundary. Neither Treatment run contains a comparable rationalization; both invalidate the old approval.

## Verdict

**PASS**. Final Treatment remains 99 and leads Control by 39 points. It preserves the complete ripple, stale/recompile, rediscovery, and approval-invalidation behavior with no critical regression; its only shortfall is stating rather than directly asking the final approval question.
