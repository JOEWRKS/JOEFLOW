# EVAL-05 Comparison

## Outcome

| Run | Score | UX |
|---|---:|---:|
| Control | 62/100 | 4/5 |
| Initial Treatment | 95/100 | 5/5 |
| Final Treatment (rerun) | 100/100 | 5/5 |

Final delta versus Control: **+38**. Initial-to-final Treatment change: **+5**. Final verdict: **PASS for final Treatment / FAIL for Control** because Control silently fixes security/privacy decisions under build pressure.

## Material Unknowns

- Expected territories: export authorization, row/customer scope, data scope/sensitivity, purpose, approval/audit, file protection/lifecycle, abuse/volume limits, failure/recovery, notifications, and explicit acceptance before implementation.
- Control discovers authorization, data scope/masking, approval/audit, retention, and operational review, but misses explicit lifecycle, recovery, volume/rate, and tenant-boundary decisions.
- Initial Treatment covers three broad clusters: authorization/control strength, data fields, and file lifecycle; it misses explicit rate/volume and recovery records.
- Final Treatment registers ten specific unknowns, adding row scope, purpose validation, file delivery, event-level audit retention, bulk/frequency limits, asynchronous handling, recovery/cancellation, and notifications.
- Final Treatment still does not name tenant isolation or policy ownership separately.

## First Question

Control asks three questions at once. Both Treatment runs ask only for the authorization model with three options and a least-privilege recommendation. Final Treatment sharpens the choice into requester/approver separation versus immediate designated-admin access versus super-admin-only access.

## Ordering

All runs begin with security/privacy. Control then bundles multiple unresolved policies and proceeds on defaults. Initial Treatment defers data and lifecycle questions. Final Treatment records the full dependency surface but continues to ask only the highest-fan-out authorization question, preserving efficient progressive disclosure.

## Evidence First

No run has organization-specific policy evidence. Control acknowledges later legal/policy review but chooses defaults anyway. Both Treatment runs preserve absence as absence; final Treatment records a source for every open unknown and does not claim a policy basis.

## Silent Assumptions

Control treats urgency as acceptance of roles, masking, exclusions, purpose capture, two-person approval, watermarking, audit, and retention. Both Treatment runs explicitly refuse to interpret “적당히 알아서” as recommendation acceptance. Final state has no decision objects resolving `UNK-001`–`UNK-010`.

## Premature Build / Closure

Control says it will proceed using unaccepted defaults. Both Treatment runs block implementation and remain `OPEN`. Final Treatment records `user_approved: false`; validation reports ten blocking unknowns and missing approval.

## State Discipline

Control creates no durable product state. Initial Treatment creates valid canonical state with three open unknowns and stale dependents. Final Treatment creates valid revision-1 state with ten material open unknowns, null approval metadata, no silent decisions, and an expected non-closed validator result.

## Rationalizations

- Control: “별도 답변이 없으므로 다음의 안전한 가정으로 진행하겠습니다” turns silence into authority.
- Control: configurability and later policy review are used to justify deciding now.
- Initial Treatment: “명시적 선택이나 권장안 수락으로 볼 수 없습니다” correctly rejects inferred consent.
- Final Treatment: “추천안 승인으로 기록할 수는 없습니다” preserves the same boundary while offering the exact shortest acceptance response.

## Verdict

**PASS for final Treatment / FAIL for Control.** The final Treatment improves the already strong initial result by making the unknown inventory substantially more complete without asking more questions or weakening the implementation block.
