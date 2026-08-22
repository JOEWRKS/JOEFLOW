import test from 'node:test';
import assert from 'node:assert/strict';
import { SCREENS, findScreen } from '../src/catalog.js';

const expected = {
  'SCR-001': ['confirm_booking'],
  'SCR-002': ['request_management_link'],
  'SCR-003': ['open_management_link', 'modify_booking', 'cancel_booking'],
  'SCR-004': ['select_time', 'select_space', 'select_equipment_quantity'],
  'SCR-005': ['edit_weekly_hours', 'set_date_exception', 'resolve_booking_conflict', 'confirm_hours_change'],
  'SCR-006': ['view_delivery_record'],
  'SCR-007': ['confirm_cancellation'],
  'SCR-008': ['confirm_booking_change'],
  'SCR-009': ['update_resource_rates'],
  'SCR-010': ['set_legal_hold', 'release_legal_hold'],
  'SCR-011': ['invite_operator', 'deactivate_operator', 'change_operator_role', 'unlock_staff_login'],
  'SCR-012': ['view_customer_data', 'view_audit_log', 'view_aggregate_metrics', 'export_aggregate_metrics_csv'],
  'SCR-013': ['accept_operator_invite', 'set_operator_password', 'enroll_totp', 'issue_recovery_codes'],
  'SCR-014': ['sign_in_operator', 'reset_operator_password', 'use_recovery_code'],
  'SCR-015': ['create_resource', 'update_resource', 'deactivate_resource', 'update_resource_compatibility', 'resolve_resource_conflicts'],
  'SCR-016': ['propose_late_booking_change', 'consent_to_booking_change', 'reject_booking_change', 'commit_consented_booking_change'],
  'SCR-017': ['submit_late_cancellation_inquiry', 'view_booking_inquiry_thread', 'reply_booking_inquiry', 'set_inquiry_waiting_customer', 'resolve_booking_inquiry'],
  'SCR-018': ['view_booking_policy', 'accept_booking_policies'],
  'SCR-019': ['draft_policy_version', 'review_policy_version', 'publish_policy_version', 'withdraw_policy_version'],
  'SCR-020': ['create_assisted_booking_proposal', 'send_assisted_booking_confirmation', 'view_assisted_booking_status'],
  'SCR-021': ['mark_equipment_unavailable', 'view_equipment_conflicts', 'propose_equipment_recovery', 'cancel_unresolved_equipment_booking'],
  'SCR-022': ['create_resource_block', 'update_resource_block', 'release_resource_block', 'resolve_block_conflicts'],
  'SCR-023': ['view_failed_deliveries', 'inspect_delivery_attempts', 'resend_failed_delivery'],
  'SCR-024': ['restore_customer_draft', 'discard_customer_draft'],
  'SCR-025': ['request_booking_data_deletion', 'view_deletion_request_status'],
  'SCR-026': ['create_damage_incident', 'append_incident_update', 'send_incident_notice', 'view_internal_incident_notes'],
  'SCR-027': ['mark_booking_late', 'mark_booking_no_show', 'revert_no_show']
};

test('catalog exposes exactly 27 unique stable screen IDs and 78 canonical actions', () => {
  assert.equal(SCREENS.length, 27);
  assert.deepEqual(Object.fromEntries(SCREENS.map(({ id, actions }) => [id, actions])), expected);
  assert.equal(new Set(SCREENS.map((screen) => screen.id)).size, 27);
  assert.equal(new Set(SCREENS.flatMap((screen) => screen.actions)).size, 78);
});

test('catalog uses no Shared authority and leaves mixed screens to action-level authorization', () => {
  assert.equal(findScreen('SCR-001').access, 'Customer');
  assert.equal(findScreen('SCR-005').access, 'Staff');
  assert.equal(findScreen('SCR-010').access, 'Owner');
  assert.equal(findScreen('SCR-016').access, null);
  assert.equal(findScreen('SCR-010').roles.includes('Staff'), false);
});
