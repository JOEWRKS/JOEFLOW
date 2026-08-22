# Screen Specification

> canonical state.json revision 62 projection

## SCR-001 — 예약 검토 및 최종 확인
- Status: CURRENT
- Interactive: True
- Requirements: REQ-001, REQ-007
- Major actions: confirm_booking

## SCR-002 — 예약 관리 링크 요청
- Status: CURRENT
- Interactive: True
- Requirements: REQ-002
- Major actions: request_management_link

## SCR-003 — 고객 예약 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-002, REQ-005, REQ-006
- Major actions: open_management_link, modify_booking, cancel_booking

## SCR-004 — 시간, 공간 및 장비 선택
- Status: CURRENT
- Interactive: True
- Requirements: REQ-001, REQ-006
- Major actions: select_time, select_space, select_equipment_quantity

## SCR-005 — 영업시간 및 날짜 예외 설정
- Status: CURRENT
- Interactive: True
- Requirements: REQ-003
- Major actions: edit_weekly_hours, set_date_exception, resolve_booking_conflict, confirm_hours_change

## SCR-006 — 이메일 전달 기록
- Status: CURRENT
- Interactive: True
- Requirements: REQ-004
- Major actions: view_delivery_record

## SCR-007 — 예약 취소 확인
- Status: CURRENT
- Interactive: True
- Requirements: REQ-005
- Major actions: confirm_cancellation

## SCR-008 — 예약 변경 검토 및 확인
- Status: CURRENT
- Interactive: True
- Requirements: REQ-006, REQ-007
- Major actions: confirm_booking_change

## SCR-009 — 공간 및 장비 요금 설정
- Status: CURRENT
- Interactive: True
- Requirements: REQ-007
- Major actions: update_resource_rates

## SCR-010 — 예약 legal hold 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-009
- Major actions: set_legal_hold, release_legal_hold

## SCR-011 — 운영자 계정 및 역할 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-010
- Major actions: invite_operator, deactivate_operator, change_operator_role, unlock_staff_login

## SCR-012 — 고객 개인정보 및 감사 접근
- Status: CURRENT
- Interactive: True
- Requirements: REQ-010
- Major actions: view_customer_data, view_audit_log, view_aggregate_metrics, export_aggregate_metrics_csv

## SCR-013 — 운영자 초대 및 보안 설정
- Status: CURRENT
- Interactive: True
- Requirements: REQ-010
- Major actions: accept_operator_invite, set_operator_password, enroll_totp, issue_recovery_codes

## SCR-014 — 운영자 로그인 및 복구
- Status: CURRENT
- Interactive: True
- Requirements: REQ-010
- Major actions: sign_in_operator, reset_operator_password, use_recovery_code

## SCR-015 — 공간·장비 설정 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-011
- Major actions: create_resource, update_resource, deactivate_resource, update_resource_compatibility, resolve_resource_conflicts

## SCR-016 — 운영자 변경안 및 고객 동의
- Status: CURRENT
- Interactive: True
- Requirements: REQ-006
- Major actions: propose_late_booking_change, consent_to_booking_change, reject_booking_change, commit_consented_booking_change

## SCR-017 — 마감 후 예약 문의 thread
- Status: CURRENT
- Interactive: True
- Requirements: REQ-012
- Major actions: submit_late_cancellation_inquiry, view_booking_inquiry_thread, reply_booking_inquiry, set_inquiry_waiting_customer, resolve_booking_inquiry

## SCR-018 — 예약 정책 확인 및 동의
- Status: CURRENT
- Interactive: True
- Requirements: REQ-013
- Major actions: view_booking_policy, accept_booking_policies

## SCR-019 — 정책 문서 version 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-013
- Major actions: draft_policy_version, review_policy_version, publish_policy_version, withdraw_policy_version

## SCR-020 — 운영자 대리 예약 등록
- Status: CURRENT
- Interactive: True
- Requirements: REQ-014
- Major actions: create_assisted_booking_proposal, send_assisted_booking_confirmation, view_assisted_booking_status

## SCR-021 — 장비 불가 및 충돌 예약 처리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-015
- Major actions: mark_equipment_unavailable, view_equipment_conflicts, propose_equipment_recovery, cancel_unresolved_equipment_booking

## SCR-022 — 임시 자원 차단 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-016
- Major actions: create_resource_block, update_resource_block, release_resource_block, resolve_block_conflicts

## SCR-023 — 이메일 delivery 실패 큐
- Status: CURRENT
- Interactive: True
- Requirements: REQ-017
- Major actions: view_failed_deliveries, inspect_delivery_attempts, resend_failed_delivery

## SCR-024 — 고객 입력 draft 복구
- Status: CURRENT
- Interactive: True
- Requirements: REQ-019
- Major actions: restore_customer_draft, discard_customer_draft

## SCR-025 — 고객 개인정보 삭제 요청
- Status: CURRENT
- Interactive: True
- Requirements: REQ-022
- Major actions: request_booking_data_deletion, view_deletion_request_status

## SCR-026 — 파손·분실 사건 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-023
- Major actions: create_damage_incident, append_incident_update, send_incident_notice, view_internal_incident_notes

## SCR-027 — 예약 도착·노쇼 관리
- Status: CURRENT
- Interactive: True
- Requirements: REQ-024
- Major actions: mark_booking_late, mark_booking_no_show, revert_no_show

