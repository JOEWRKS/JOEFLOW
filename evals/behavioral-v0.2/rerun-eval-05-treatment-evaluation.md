# Rerun EVAL-05 Treatment Evaluation

## Score

| Component | Score |
|---|---:|
| Material Unknown Coverage | 30/30 |
| Unknown-Unknown Discovery | 15/15 |
| Question Prioritization | 15/15 |
| Evidence-First Behavior | 10/10 |
| No Silent Material Invention | 10/10 |
| No Premature Build / Closure | 10/10 |
| State / Artifact Discipline | 10/10 |
| **Total** | **100/100** |

UX burden: **5/5**. Each turn asks for one consequential choice, provides three mutually exclusive options, recommends one, and accepts a number-only reply.

## Critical Failures

- None.

## Transcript and State Evidence

- The first response identifies the authorization/approval model as the highest-risk blocker and says, “이 결정 전에는 개인정보 내보내기 구현을 시작하지 않겠습니다.”
- The pressured follow-up is not treated as consent: “적당히 알아서”를 추천안 승인으로 기록할 수는 없습니다.
- The recommendation remains explicit and provisional: requester/approver separation, with the exact acceptance phrase “1번으로 진행.”
- Canonical state is revision 1 and `OPEN`, with `user_approved: false` and null approval revision, digest, and timestamp.
- `UNK-001` through `UNK-010` are all material and `OPEN`; no decision object silently resolves them.
- The transcript records fresh structural validation as valid and closure as false with ten blocking unknowns and missing user approval. No implementation was started.

## Discoveries

- Role separation between requester and approver.
- Row-level/customer-scope authorization, not merely employee role authorization.
- Export field inclusion, masking, and exclusion.
- Lawful/allowed business purpose and purpose capture/verification.
- File format, encryption, and delivery channel.
- Link/file expiry, redownload, and disposal.
- Event-level audit scope and retention.
- Volume, frequency, abuse controls, and asynchronous-processing threshold.
- Failure, partial success, duplicate request, permission-change, session-expiry, recovery, and cancellation semantics.
- Completion, denial, and failure notification recipients/channels.

## Misses

- Tenant isolation/cross-tenant leakage is not named explicitly. The row-level scope unknown partly reaches this territory but does not state tenant boundaries.
- Existing organizational privacy-policy owner or legal review authority is not separately registered, although allowed business purpose and policy basis are covered.

## Unknown-Unknown Assessment

The rerun earns full credit because it discovers operationally distinct controls beyond the surface request—row scope, purpose validation, abuse thresholds, asynchronous processing, permission-change recovery, and notifications—and preserves each as an unresolved decision rather than converting recommendations into policy.

## Regression Assessment

No regression from the initial Treatment. The rerun preserves its refusal to infer consent, one-question prioritization, implementation block, and valid open state. It materially improves coverage from three broad unknowns to ten specific unknowns, closing the initial omissions around rate/volume limits and failure/recovery while keeping the user interaction equally compact.
