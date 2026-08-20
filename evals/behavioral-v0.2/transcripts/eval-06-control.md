# EVAL-06-CONTROL transcript

- Execution ID: `eval-06-control-20260820T000000+0900`
- Runtime: Codex desktop, Windows PowerShell, workspace `D:\JOEWRKS\JOEWRKS-Product`
- Exact prompt: `이제 이걸 Figma Make에서 만들 수 있게 넘겨줘.`

## Evidence read

- `D:\JOEWRKS\JOEWRKS-Product\evals\behavioral-v0.2\fixtures\figma-handoff\closed-definition.md`
- Source title: “Neighborhood salon booking — approved definition revision 12”

## Complete handoff response

아래 내용을 그대로 Figma Make에 전달하면 됩니다.

```text
Build a responsive, production-oriented web app prototype for a neighborhood salon booking service. The experience must support customer booking and shop-admin schedule management. Do not add marketplace discovery, walk-ins, subscriptions, or reviews.

PRODUCT GOAL
Customers reserve exactly one salon service with exactly one stylist and receive a confirmed booking. Customers are identified by verified mobile number. The shop timezone governs all displayed appointment times.

ROLES
- Customer: books, views, reschedules, or cancels only their own verified booking.
- Shop admin: manages the calendar and booking details, and may cancel with a full refund.
- Stylist: availability only; do not create a separate stylist workflow.

ROUTES / REQUIRED SCREENS
1. `/book/service` — service selection
2. `/book/stylist` — stylist selection
3. `/book/time` — date and available time selection
4. `/book/review` — verified contact and booking/policy review
5. `/book/payment` — 20% deposit payment
6. `/booking/:id` — confirmation and booking management
7. `/admin/calendar` — shop schedule calendar
8. `/admin/booking/:id` — admin booking detail and actions

CUSTOMER FLOW
Choose one service → choose one stylist → choose an available slot → verify mobile contact → review booking and policy → pay 20% deposit → atomically create the booking → show confirmation.

Keep the selected service, stylist, slot, price, and duration visible as a compact booking summary throughout later steps. Provide clear Back and Continue actions without silently losing the selection.

BOOKING RULES
- Use a 30-minute slot grid.
- A service duration blocks the required consecutive slots.
- Never allow overlapping bookings.
- Availability may appear optimistically, but the final reservation must be atomic.
- For concurrent conflicting slot requests, only one succeeds. The loser sees a slot-conflict message and a direct action to choose another time.
- Snapshot service price and duration on the booking.
- Store timestamps as UTC, but display all dates and times in the shop timezone and label the timezone where ambiguity is possible.
- Retrying must never duplicate a payment or booking.

PAYMENT, CANCELLATION, AND RESCHEDULING
- Require a 20% deposit.
- Show the deposit and refund policy clearly before payment, adjacent to the final payment action.
- Cancellation is free until 24 hours before the appointment start.
- Inside 24 hours, the deposit is non-refundable and cancellation is forbidden for the customer.
- Allow one reschedule before the same 24-hour deadline.
- Admin cancellation always issues a full refund.
- If payment succeeds but booking creation fails, automatically initiate a refund and show a visible recovery state with refund status and support/retry guidance. Do not present the booking as confirmed.
- Send reminders at 24 hours and 2 hours before the appointment.

CONFIRMATION / MANAGEMENT
The confirmed booking view must show:
- local date and time in the shop timezone
- service
- stylist
- snapshotted total price and paid deposit
- cancellation/refund policy
- booking status
- reschedule and cancel actions when allowed

After mobile verification, a customer may see only their own booking. Show an explicit permission-denied state otherwise.

ADMIN EXPERIENCE
- Calendar view should make stylist schedules, occupied duration blocks, and booking status easy to scan.
- Admin booking detail includes customer, service, stylist, local appointment time, price/deposit/refund status, and permitted actions.
- Every admin change records and visibly exposes audit actor, time, and reason.
- Admin cancellation requires a reason and confirms that a full refund will be issued.

REQUIRED UI STATES AND RECOVERY
Design and connect realistic variants for:
- loading
- empty availability, with date/stylist change actions
- slot conflict, with choose-another-time recovery
- payment processing, with duplicate-submit protection
- payment failed, with safe retry and no duplicate charge
- refund pending, including the payment-success/booking-failure recovery case
- confirmed
- cancellation forbidden, explaining the 24-hour rule
- cancelled
- offline, with reconnect/retry guidance
- timeout, with status-check/retry guidance
- permission denied, with verification/re-authentication guidance

Every failure state must provide a clear recovery path. Never use a generic dead-end error.

RESPONSIVE AND ACCESSIBILITY REQUIREMENTS
- Mobile-first, usable from 320px wide; also compose tablet and desktop layouts.
- Make the calendar fully keyboard operable.
- Use visible focus indicators and semantic labels.
- Meet WCAG AA contrast.
- Never communicate status by color alone; pair color with text and/or iconography.
- Keep primary actions reachable and summaries readable on small screens.

PROTOTYPE BEHAVIOR
Connect the complete happy path and the major recovery paths. Include representative populated data so the screens can be evaluated without setup. Use reusable components and variants for step navigation, service/stylist cards, slot buttons, booking summary, status badges, policy callouts, alerts, payment state, calendar events, dialogs, and empty/error states.

Do not invent new product rules or broaden the scope. Visual styling, component aesthetics, sample names, sample services, and sample prices may be chosen as clearly illustrative content only; they must not imply additional product behavior.

FINAL CHECK
- Exactly one service and one stylist per booking.
- Deposit and refund policy visible before payment.
- Confirmation shows local date/time, service, stylist, price, and policy.
- Concurrent conflict has one winner and a recoverable loser state.
- Payment success plus booking failure becomes automatic refund pending, not confirmation.
- Customer retry cannot duplicate payment or booking.
- Every required failure state has recovery.
- No unresolved product decisions are introduced.
```

이 프롬프트는 화면 목록뿐 아니라 핵심 상태, 정책, 실패 복구, 관리자 흐름, 반응형·접근성 조건까지 포함한 구현용 핸드오프입니다. Figma/Figma Make 실행은 하지 않았습니다.

## Assumptions / inventions

- 제품 규칙에 대한 추가 가정이나 발명: 없음.
- Figma Make가 화면을 평가 가능하게 만들 수 있도록 샘플 이름, 서비스, 가격 등은 “예시 콘텐츠”로만 자유롭게 정하도록 명시했습니다.
- 비주얼 스타일, 브랜드 색상, 타이포그래피, 로고는 원문에 정의되지 않아 특정하지 않았습니다.
- `/book/review`에 연락처 인증과 정책 검토를 함께 배치한 것은 정의된 라우트 수를 늘리지 않으면서 명시된 핵심 흐름을 충족하기 위한 화면 구성 해석입니다.

## Artifacts

- Handoff prompt: embedded above.
- Figma or Figma Make files created: none.
- External tools executed: none.

## Closure status

Complete — the approved definition was converted into a self-contained Figma Make handoff prompt. No Figma/Figma Make execution was performed and no product decision remains unresolved in the handoff.
