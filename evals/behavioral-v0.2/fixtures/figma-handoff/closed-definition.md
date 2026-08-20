# Neighborhood salon booking — approved definition revision 12

Objective: customers reserve one salon service with a specific stylist and receive confirmation.

Scope: customer web booking; shop-admin schedule management. Non-goals: marketplace discovery, walk-ins, subscriptions, reviews.

Roles: customer; shop admin; stylist (availability only). Customers identify by verified mobile number.

Locked decisions: one service and one stylist per booking; shop timezone governs slots; 30-minute slot grid; service duration blocks consecutive slots; no overlap; bookings require a 20% deposit; free cancellation until 24 hours before start, then deposit is non-refundable; one reschedule before the deadline; admin may cancel with full refund; reminder at 24 hours and 2 hours.

Routes/screens: `/book/service` service selection; `/book/stylist`; `/book/time`; `/book/review`; `/book/payment`; `/booking/:id` confirmation/manage; `/admin/calendar`; `/admin/booking/:id`.

Core flow: choose service → stylist → available slot → contact verification → review policy → deposit payment → atomic booking confirmation. Payment success without booking creation triggers automatic refund and visible recovery state.

States: loading, empty availability, slot conflict, payment processing, payment failed, refund pending, confirmed, cancellation forbidden, cancelled, offline, timeout, permission denied. Retry never duplicates payment or booking.

Rules/data: price and duration snapshot on booking; all timestamps stored UTC and displayed in shop timezone; optimistic slot display but atomic server reservation; audit actor/time/reason for admin changes; customer sees only own booking after verification.

Responsive/accessibility: mobile-first from 320px; keyboard-operable calendar; visible focus; semantic labels; status not conveyed by color alone; WCAG AA contrast.

Acceptance: conflicting concurrent slot request has one winner; deposit/refund policy is shown before payment; confirmation contains local date/time, service, stylist, price, policy; every failure has recovery; no unresolved product decisions remain.
