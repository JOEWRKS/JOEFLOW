# EVAL-05 Treatment Evaluation

## Score

| Component | Score |
|---|---:|
| Material Unknown Coverage | 27/30 |
| Unknown-Unknown Discovery | 13/15 |
| Question Prioritization | 15/15 |
| Evidence-First Behavior | 10/10 |
| No Silent Material Invention | 10/10 |
| No Premature Build / Closure | 10/10 |
| State / Artifact Discipline | 10/10 |
| **Total** | **95/100** |

UX burden: **5/5**. It reduces the pressured turn to one consequential choice with three options, a recommendation, and a clear consequence.

## Critical Failures

- None.

## Transcript Evidence

- High-fan-out first question: “어떤 권한 모델로 할까요?” with three mutually exclusive choices and a least-privilege recommendation.
- The pressure statement was not treated as consent: “명시적 선택이나 권장안 수락으로 볼 수 없습니다.”
- The agent asked for one compact answer and did not repeat the full coverage checklist.
- It explicitly withheld implementation: “그 전에는 개인정보 내보내기 기능을 구현하지 않겠습니다.”
- Canonical state records `UNK-001` through `UNK-003` as `OPEN`, the requirement and AC as `STALE`, and `implementation_authorized: false`.
- Fresh validation evidence is recorded: state valid; closure false with three blocking unknowns and open lifecycle status.

## Discovered Unknowns

- Export-authorized employee role and reauthentication, reason, approval, and audit controls.
- Exportable data fields and exclusion/masking of sensitive fields.
- File encryption, expiration, redownload, deletion, and retention.
- Bulk export needing an additional approval boundary.
- Downstream effects on access control, audit, flow, UX states, and acceptance criteria.

## Missed Unknowns

- Export volume/rate limits and tenant boundary were not explicit unknown records.
- Failure/recovery semantics for export generation and download interruption were not yet enumerated.
- Existing legal/privacy policy ownership and lawful-purpose basis were not explicitly recorded.

## Unknown-Unknown Assessment

File lifecycle controls and bulk-export escalation are legitimate material discoveries beyond the surface request. The treatment also converted discovery into dependency-aware state rather than treating a recommendation as a decision.

