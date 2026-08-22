# Codex Implementation Handoff — Studio Booking

> Direct implementation contract derived from approved canonical revision 62.

## Authority pin

- Product: `studio-booking-dogfood`
- Canonical state: `state.json`
- Status: `CLOSED`
- Approved revision: `62`
- Approved digest: `8ebb472aa66a5b680961e102db950214cea2d0be3b644164f23712030b9d8a7c`
- Audited Figma file: `fClM2GgNhwEDIiqZcIWhNZ`
- Audited native screen root: `4:2`
- Audited mobile root: `4:656`
- Historical Figma catalog root `1:4` is not an implementation source.
- Authority order: approved Product Definition → `state.json` → uppercase projections → audited Figma roots → this handoff → generated implementation.

If this handoff appears to conflict with a higher authority, follow the higher authority and report the conflict. Do not resolve it by inventing product behavior.

## Objective and implementation boundary

Build a working, dependency-free browser prototype that makes the approved booking, management, operations, failure, and recovery semantics observable. It is an evaluation implementation, not a production backend. Local deterministic state may simulate server results, but the UI must distinguish simulated results from verified production behavior.

The implementation must:

- expose all 27 stable `SCR-*` identities and all canonical major action names;
- provide substantive, stateful customer booking/management, Staff operations, and Owner security/administration journeys;
- enforce the canonical high-fan-out boundary rules in a testable domain layer;
- render canonical failure/recovery, permission, destructive-action, concurrency, and idempotency feedback;
- work at desktop widths and at 320–375 CSS px without horizontal page scrolling;
- use semantic HTML, complete labels, keyboard operation, visible focus, error-field association, live status, reduced-motion support, and WCAG 2.2 AA-oriented contrast;
- remain Korean-only and Asia/Seoul-specific.

It must not claim production authentication, email delivery, encryption, persistence, audit immutability, provider integration, database concurrency, or Figma Make execution. It must not add payments, refunds, discounts, packages, memberships, branches, recurring bookings, calendars, SMS, customer accounts, or English localization.

## Roles and permission boundaries

| Role | Stable ID | Allowed product surface |
| --- | --- | --- |
| Customer | `USR-001` | Create, review, confirm, manage, change, cancel, inquire, consent, recover draft, and request deletion for the authenticated reservation only. |
| Studio operator | `USR-002` | Umbrella product actor for studio operations; concrete UI authority is Owner or Staff. |
| Owner | `USR-003` | All Staff work plus operator account/role management, legal hold, and complete audit access. |
| Staff | `USR-004` | Reservations, resources, operating hours, rates, delivery operations, inquiries, incidents, and attendance. No operator-account or legal-hold authority. |

Permission loss must revoke the affected operator session immediately. Legal hold blocks lifecycle deletion/anonymization but never widens Staff access. PII export is prohibited; only non-identifying aggregate CSV up to 10,000 rows is allowed to Owner and Staff.

## Canonical screen and action registry

The implementation may use an internal SPA screen registry keyed by the stable `SCR-*` ID. That registry is an evaluation navigation mechanism, not a new production route contract.

| Screen | Name | Canonical major actions |
| --- | --- | --- |
| `SCR-001` | 예약 검토 및 최종 확인 | `confirm_booking` |
| `SCR-002` | 예약 관리 링크 요청 | `request_management_link` |
| `SCR-003` | 고객 예약 관리 | `open_management_link`, `modify_booking`, `cancel_booking` |
| `SCR-004` | 시간, 공간 및 장비 선택 | `select_time`, `select_space`, `select_equipment_quantity` |
| `SCR-005` | 영업시간 및 날짜 예외 설정 | `edit_weekly_hours`, `set_date_exception`, `resolve_booking_conflict`, `confirm_hours_change` |
| `SCR-006` | 이메일 전달 기록 | `view_delivery_record` |
| `SCR-007` | 예약 취소 확인 | `confirm_cancellation` |
| `SCR-008` | 예약 변경 검토 및 확인 | `confirm_booking_change` |
| `SCR-009` | 공간 및 장비 요금 설정 | `update_resource_rates` |
| `SCR-010` | 예약 legal hold 관리 | `set_legal_hold`, `release_legal_hold` |
| `SCR-011` | 운영자 계정 및 역할 관리 | `invite_operator`, `deactivate_operator`, `change_operator_role`, `unlock_staff_login` |
| `SCR-012` | 고객 개인정보 및 감사 접근 | `view_customer_data`, `view_audit_log`, `view_aggregate_metrics`, `export_aggregate_metrics_csv` |
| `SCR-013` | 운영자 초대 및 보안 설정 | `accept_operator_invite`, `set_operator_password`, `enroll_totp`, `issue_recovery_codes` |
| `SCR-014` | 운영자 로그인 및 복구 | `sign_in_operator`, `reset_operator_password`, `use_recovery_code` |
| `SCR-015` | 공간·장비 설정 관리 | `create_resource`, `update_resource`, `deactivate_resource`, `update_resource_compatibility`, `resolve_resource_conflicts` |
| `SCR-016` | 운영자 변경안 및 고객 동의 | `propose_late_booking_change`, `consent_to_booking_change`, `reject_booking_change`, `commit_consented_booking_change` |
| `SCR-017` | 마감 후 예약 문의 thread | `submit_late_cancellation_inquiry`, `view_booking_inquiry_thread`, `reply_booking_inquiry`, `set_inquiry_waiting_customer`, `resolve_booking_inquiry` |
| `SCR-018` | 예약 정책 확인 및 동의 | `view_booking_policy`, `accept_booking_policies` |
| `SCR-019` | 정책 문서 version 관리 | `draft_policy_version`, `review_policy_version`, `publish_policy_version`, `withdraw_policy_version` |
| `SCR-020` | 운영자 대리 예약 등록 | `create_assisted_booking_proposal`, `send_assisted_booking_confirmation`, `view_assisted_booking_status` |
| `SCR-021` | 장비 불가 및 충돌 예약 처리 | `mark_equipment_unavailable`, `view_equipment_conflicts`, `propose_equipment_recovery`, `cancel_unresolved_equipment_booking` |
| `SCR-022` | 임시 자원 차단 관리 | `create_resource_block`, `update_resource_block`, `release_resource_block`, `resolve_block_conflicts` |
| `SCR-023` | 이메일 delivery 실패 큐 | `view_failed_deliveries`, `inspect_delivery_attempts`, `resend_failed_delivery` |
| `SCR-024` | 고객 입력 draft 복구 | `restore_customer_draft`, `discard_customer_draft` |
| `SCR-025` | 고객 개인정보 삭제 요청 | `request_booking_data_deletion`, `view_deletion_request_status` |
| `SCR-026` | 파손·분실 사건 관리 | `create_damage_incident`, `append_incident_update`, `send_incident_notice`, `view_internal_incident_notes` |
| `SCR-027` | 예약 도착·노쇼 관리 | `mark_booking_late`, `mark_booking_no_show`, `revert_no_show` |

All actions must be visible on their screen. An action that is not substantively simulated must still provide a truthful, deterministic explanation of its guard, success/failure state, and production boundary; it must not silently do nothing.

## Booking and availability invariants

- One booking owns exactly one room and item quantities for compatible equipment.
- Start/end must be on 30-minute boundaries; shoot duration is 1–8 hours.
- A 30-minute pre-buffer and post-buffer apply to room and selected equipment availability, but not price.
- New bookings require at least 2 hours lead time and may be made through the inclusive 90th Asia/Seoul calendar day.
- Room capacity must cover attendee count at selection and commit.
- Normal customer exploration creates no hold. Final confirmation atomically rechecks room, equipment quantity, compatibility, hours, buffers, lead time, capacity, policies, and price.
- Atomic failure creates neither booking nor partial occupancy. Preserve compatible input, remove invalid selection, and show current alternatives.
- Assisted booking alone may create a 15-minute atomic resource hold; its customer confirmation link lasts 24 hours. If the hold expires, confirmation revalidates the complete configuration.

## Price and policy invariants

- KRW integer-won display with `₩` and thousands separators.
- Room hourly rate plus each equipment hourly rate × quantity, prorated in 30-minute units for shooting time only.
- Hourly rate must be an even integer won; invalid updates preserve the current valid rate.
- Confirmation freezes component rates, quantities, billable duration, line totals, and total in a price snapshot.
- Change review shows the old snapshot, new snapshot, and delta before commit.
- Five current policy versions are all required: terms, 48-hour change/cancel policy, safety, shoot restrictions, and privacy collection. A missing current publication blocks booking confirmation; withdrawal never automatically revives a previous version.

## Change, cancellation, inquiry, and recovery

- Customer change/cancel is allowed when server judgment time is exactly 48 hours or more before shoot start. Later requests are a mutation-free block with an authenticated inquiry path.
- Customer changes are unlimited but atomically revalidate the complete new configuration. Failure preserves the old booking and occupancy.
- A late operator change requires Owner/Staff reason plus customer consent to exactly one latest active proposal. Its link expires at 24 hours or shoot start, whichever comes first. Stale proposal versions are no-ops.
- Operator cancellation requires a non-empty reason and, when possible, a prior alternative proposal. Cancellation and occupancy release are atomic.
- A management link lasts 15 minutes and is one-time; successful use starts a 30-minute session. New successful issue revokes the older unused token.
- Link requests are limited to once per 60 seconds per email and five per hour. Validly formatted unknown emails receive the same neutral response and cause no token/email mutation.
- Expired management sessions reject mutation but may retain the latest encrypted booking-change or inquiry draft for two hours, bound to the same reservation and reauthenticated session. Successful mutation, explicit discard, or expiry deletes it.
- All mutations use optimistic/version checks in the evaluation model. Stale requests return a no-op plus latest state. Idempotency keys replay the original result instead of duplicating side effects.

## Operations, security, delivery, and lifecycle

- Owner/Staff may manage non-deleting resource records, hours/exceptions, conflicts, equipment outages, temporary blocks, inquiries, incidents, and attendance. Conflicting configuration changes do not commit until every affected booking has a disposition and reason.
- Email is the only v1 customer notification channel. Delivery state is separate from business state. Retry schedule is 1, 5, and 30 minutes after initial failure; final failure enters an operations queue; idempotency prevents duplicate sends. Delivery failure never rolls back booking/inquiry/change state.
- Operator activation requires a 24-hour Owner invitation, password, TOTP, and 10 one-time recovery codes. Five combined password/TOTP failures lock for 15 minutes. Only an Owner may unlock another Staff member, with a reason.
- Legal hold set/release is Owner-only and requires reason plus reference/release reason. Append-only audit is the model; prototype displays must not claim durable append-only storage.
- Customer PII anonymizes one year after completion/cancellation unless held; delivery identifiers follow that anonymization and non-identifying delivery data expires at three years; audits expire at five years with linked PII de-identification after one year. Authenticated deletion requests finish within 30 days after eligibility and are postponed by future/in-progress booking or legal hold.
- No-show is manual Owner/Staff action only, after 30 minutes, with reason; it does not release or extend occupancy. Reversal requires another reason.

## Figma-to-code visual contract

The Figma roots provide a low-fidelity structural authority, not finished product polish. Preserve:

- clean white/near-white surfaces, dark primary actions, quiet neutral borders, restrained red recovery panels;
- stable screen identity, visible role label, grouped fields, actions, contextual recovery, and navigation/session boundary;
- 27 separate desktop screen surfaces and three 360px role journeys;
- labeled controls and visible focus.

Bounded refinement may add a calm operations palette, semantic blue/green/amber/red state tokens, stronger information hierarchy, 4/8px spacing rhythm, and compact responsive navigation. Use system UI fonts. Motion is limited to 150–250ms opacity/transform feedback, never blocks input, and must respect `prefers-reduced-motion`. Avoid decorative looping motion, invented imagery, gradients that reduce legibility, glass stacking, and emoji icons.

## Required observable evaluation scenarios

1. Valid customer configuration reaches review and creates one confirmed booking with a frozen KRW snapshot.
2. A conflicting second confirmation is an atomic no-op and shows alternatives while preserving compatible input.
3. A 48-hour boundary check distinguishes allowed and blocked customer mutations.
4. Invalid capacity, equipment quantity/compatibility, odd-won rate, missing policy, and stale version each show a specific guard and preserve prior valid state.
5. Management-link neutral response/rate limit, session expiry/draft recovery, and one-time token semantics are inspectable without exposing reservation existence.
6. Staff cannot access Owner account/legal-hold actions; simulated authority loss ends the operator session.
7. Delivery failure remains independent of business commit, records attempts, and idempotent resend does not duplicate success.
8. Destructive actions require confirmation and reason where canonical; cancellation/resource release and change occupancy swap are atomic.
9. All 27 screen IDs and all action names are discoverable through role-oriented navigation on desktop and mobile.

## Verification contract

- Use Node's built-in test runner; no dependency installation is required.
- Tests are written and observed failing before production implementation.
- Unit/contract tests cover the listed booking, permission, version, idempotency, and inventory invariants.
- A local static server supports real browser readback.
- Final evidence includes commands, exits, screenshots/readback at desktop and 375px, reduced-motion behavior, source inventory, and explicit unverified production boundaries.

## Do not invent

Do not introduce any new product decision, hidden backend contract, extra role, branch, currency, locale, payment concept, cancellation fee, customer password/account, recurring reservation, calendar integration, provider guarantee, production route, or data-retention exception. If an unimplemented production detail is required, show it as `NOT VERIFIED / production boundary` rather than choosing a value.
