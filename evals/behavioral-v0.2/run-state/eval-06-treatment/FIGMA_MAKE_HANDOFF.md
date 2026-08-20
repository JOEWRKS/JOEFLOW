# Figma Make handoff — Neighborhood salon booking

Authoritative definition: `state.json`, revision 12. Figma visualization: **NOT VERIFIED**.

## Exact Figma Make prompt

```text
Create an editable, low-fidelity, mobile-first responsive web prototype for a neighborhood salon booking product. Use stable IDs exactly as provided. Do not invent roles, routes, fields, policies, branches, brand colors, decorative imagery, complex animation, or high-fidelity styling.

Create pages: 00_PRODUCT_MAP, 01_USER_FLOWS, 02_WIREFRAMES, 03_SCREEN_STATES, 99_HANDOFF.

Goal: a customer reserves one salon service with a specific stylist and receives confirmation. Scope is customer web booking and shop-admin schedule management. Exclude marketplace discovery, walk-ins, subscriptions, and reviews.

Roles: customer; shop admin; stylist (availability only). Customer identity is a verified mobile number.

Locked rules:
- Exactly one service and one stylist per booking.
- Shop timezone governs displayed slots. Slots use a 30-minute grid. Service duration blocks consecutive slots. No overlap.
- Booking requires a 20% deposit.
- Cancellation is free until 24 hours before start; after that the deposit is non-refundable.
- Customer may reschedule once before the deadline.
- Admin may cancel with a full refund.
- Reminders occur 24 hours and 2 hours before the appointment.
- Snapshot price and duration on the booking.
- Store timestamps in UTC and display them in shop timezone.
- Slot display may be optimistic, but server reservation is atomic.
- Audit actor, time, and reason for admin changes.
- A verified customer may see only their own booking.
- Retry must never duplicate a payment or booking.

Create these editable frames and preserve these names:
- SCR-001__BOOK_SERVICE — route /book/service
- SCR-002__BOOK_STYLIST — route /book/stylist
- SCR-003__BOOK_TIME — route /book/time
- SCR-004__BOOK_REVIEW — route /book/review
- SCR-005__BOOK_PAYMENT — route /book/payment
- SCR-006__BOOKING_MANAGE — route /booking/:id
- SCR-007__ADMIN_CALENDAR — route /admin/calendar
- SCR-008__ADMIN_BOOKING — route /admin/booking/:id

Customer flow: choose service → choose stylist → choose available slot → verify mobile contact → review deposit/refund/reschedule policy → pay 20% deposit → atomically create booking → show confirmation.

For SCR-006 confirmation, show local date/time, service, stylist, total price, deposit/payment status, and cancellation/reschedule policy. Include eligible cancel and one-time reschedule actions; show cancellation forbidden after the deadline.

For admin screens, provide calendar schedule management and booking detail. Admin changes require a reason and visibly preserve an audit record. Admin cancellation communicates full refund.

Create state variants, using the frame-ID suffix convention, for: DEFAULT, LOADING, EMPTY_AVAILABILITY, SLOT_CONFLICT, PAYMENT_PROCESSING, PAYMENT_FAILED, REFUND_PENDING, CONFIRMED, CANCELLATION_FORBIDDEN, CANCELLED, OFFLINE, TIMEOUT, PERMISSION_DENIED. Payment success without booking creation must start an automatic refund and show REFUND_PENDING with a clear explanation and safe next step.

Show recovery for every failure. Preserve entered choices when safe. Slot conflict returns to updated availability. Payment failure permits safe retry. Offline and timeout states explain whether submission status is known. Never imply a retry can create a duplicate payment or booking.

Responsive and accessibility requirements: design from 320px width upward; keyboard-operable calendar; visible focus; semantic labels; status is not conveyed by color alone; WCAG AA contrast. Keep visual styling neutral and low fidelity so hierarchy, layout, content, navigation, interactions, and states can be reviewed without making brand decisions.

On 00_PRODUCT_MAP, map routes to frames and roles. On 01_USER_FLOWS, draw the core customer flow plus the payment-success/booking-failure automatic-refund recovery. On 03_SCREEN_STATES, group state variants by their base screen. On 99_HANDOFF, list the locked rules, acceptance checks, non-goals, and a visible note: “No additional product decisions may be introduced by the prototype.”

Acceptance checks to display in 99_HANDOFF:
1. Conflicting concurrent slot requests produce one winner.
2. Deposit/refund policy is shown before payment.
3. Confirmation contains local date/time, service, stylist, price, and policy.
4. Every failure has recovery.
5. No unresolved product decisions and no invented scope.
```

## Review boundary

After generation, compare output to revision 12 for missing/extra screens and flows, invented branches, missing states, and rule/permission/data/navigation drift. Record findings in `MAKE_REVIEW.md` by expected ID and severity. No Figma or Figma Make execution occurred in this handoff.
