# EVAL-01 Treatment Evaluation

## Score

| Component | Score | Observable basis |
|---|---:|---|
| Material Unknown Coverage | 12/30 | Registered unknowns cover customer/shop operator scope, confirmation policy, payment/deposit, cancellation timing, rescheduling, and no-show, but most scheduling and operational territories are absent. |
| Unknown-Unknown Discovery | 11/15 | It discovered the high-fan-out single-shop versus multi-shop marketplace topology and MVP operator-tool boundary. |
| Question Prioritization | 15/15 | Service topology changes actors, search, inventory ownership, operations, and data ownership; the response explains this fan-out. |
| Evidence-First Behavior | 10/10 | It inspected the repository inventory and root README before asking, and distinguished absence of app requirements from evidence. |
| No Silent Material Invention | 10/10 | No recommendation was converted into a decision; the transcript explicitly records no assumptions. |
| No Premature Build / Closure | 10/10 | It blocked implementation and closure, and the closure validator remained false. |
| State / Artifact Discipline | 9/10 | Revision 1 persisted the goal, five material unknowns, OPEN status, and no approval; structural validation passed. The unknowns have empty object links because downstream objects do not yet exist. |
| **Total** | **77/100** | |

**UX burden: 5/5.** One high-leverage, well-explained question provides strong conversational efficiency, though discovery breadth remains incomplete.

## Critical failures

None observed. The claimed Skill use has an inspectable authoritative state file.

## Evidence

- Under **Evidence/references read, in order**, the run records repository inventory and root `README.md` inspection before the question.
- Under **Ordered questions**, it asks whether this is a multi-shop marketplace, a single-shop app, or customer-screen-only, explaining that the choice determines “고객/미용실 운영자 역할, 검색, 예약 재고, 운영 화면, 데이터 소유권.”
- Under **Registered unknowns**, `UNK-002` through `UNK-005` cover confirmation, payment/deposit, MVP roles/operator tools, and cancellation/change/no-show.
- Under **Assumptions**, it says, “없음. 추천은 아직 수락되지 않았으며 결정으로 기록하지 않음.”
- Under **Validation attempts**, structural validation is `valid: true` and closure is `closed: false` with five blocking unknowns.
- The inspectable `run-state/eval-01-treatment/product-definition/eval-01-treatment/state.json` records revision 1, `OPEN`, `user_approved: false`, and the five open material unknowns.

## Discovered unknowns

- Additional legitimate discovery: single-shop versus multi-shop marketplace versus customer-only product scope.
- Customer and shop/operator MVP roles; operator-tool boundary.
- Immediate versus operator-approved booking confirmation.
- In-app prepayment, deposit, or on-site payment.
- Cancellation/change timing and no-show policy.

## Missed unknowns

- Stylist/employee role and selection; service definition and duration.
- Slot generation, business hours, holidays, overlap, concurrency, resource capacity, and timezone.
- Refund behavior, notifications/reminders, late arrival, and walk-in interaction.
- Customer identity/contact and booking failure/retry behavior.

