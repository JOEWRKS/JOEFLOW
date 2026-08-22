import test from 'node:test';
import assert from 'node:assert/strict';
import {
  POLICY_TYPES, createPrototypeState, confirmBooking, changeBookingState,
  managePolicy, requestManagementLink, useManagementLink, saveDraft, restoreDraft,
  createDelivery, advanceDelivery, resendDelivery, mutateWithVersion, cancelBooking,
  authorizeAction
} from '../src/domain.js';

const now = new Date('2026-08-21T00:00:00+09:00');
const draft = { reservationId: 'R-001', customerId: 'C-001', start: '2026-08-22T04:00:00+09:00', end: '2026-08-22T06:00:00+09:00', roomId: 'ROOM-A', attendees: 2, equipment: [{ id: 'CAM-A', quantity: 1 }] };
const prepared = () => { let state = createPrototypeState(now); for (const type of POLICY_TYPES) state = managePolicy(state, 'Owner', 'publish', type, { version: 1 }).state; return state; };

test('authoritative booking derives conflicts and preserves state on invalid input or occupancy conflict', () => {
  const state = prepared();
  const bad = confirmBooking(state, { ...draft, attendees: -1 }, { consents: Object.fromEntries(POLICY_TYPES.map((type) => [type, 1])) });
  assert.equal(bad.ok, false); assert.equal(bad.state, state); assert.equal(bad.code, 'ATTENDEES');
  const first = confirmBooking(state, draft, { consents: Object.fromEntries(POLICY_TYPES.map((type) => [type, 1])) });
  assert.equal(first.ok, true); assert.equal(first.state.bookings.length, 1);
  const second = confirmBooking(first.state, { ...draft, reservationId: 'R-002', start: '2026-08-22T05:30:00+09:00', end: '2026-08-22T06:30:00+09:00' }, { consents: Object.fromEntries(POLICY_TYPES.map((type) => [type, 1])) });
  assert.equal(second.ok, false); assert.equal(second.state, first.state); assert.equal(second.code, 'CONFLICT'); assert.ok(second.alternatives.length);
});

test('snapshots are deep immutable, policy versions require exactly current consents, and withdrawal does not revive', () => {
  let state = prepared();
  const result = confirmBooking(state, draft, { consents: Object.fromEntries(POLICY_TYPES.map((type) => [type, 1])) });
  assert.throws(() => { result.value.priceSnapshot.room.total = 1; }, TypeError);
  state = managePolicy(state, 'Owner', 'withdraw', POLICY_TYPES[0], { reason: '개정' }).state;
  const blocked = confirmBooking(state, draft, { consents: Object.fromEntries(POLICY_TYPES.map((type) => [type, 1])) });
  assert.equal(blocked.code, 'POLICY');
  assert.equal(authorizeAction('Staff', 'publish_policy_version').ok, false);
  assert.equal(authorizeAction('Customer', 'propose_late_booking_change').ok, false);
  assert.equal(authorizeAction('Customer', 'unknown').ok, false);
});

test('management links are neutral externally and stateful internally with session and two-hour draft lifecycle', () => {
  const state = prepared();
  const unknown = requestManagementLink(state, { email: 'nobody@example.com', now });
  assert.equal(unknown.public.code, 'REQUEST_ACCEPTED'); assert.equal(unknown.state, state);
  const issued = requestManagementLink(state, { email: 'customer@example.com', now });
  assert.equal(issued.public.code, 'REQUEST_ACCEPTED'); assert.equal(issued.state.management.tokens.length, 1);
  const used = useManagementLink(issued.state, issued.token, now);
  assert.equal(used.ok, true); assert.equal(used.state.management.sessions.length, 1);
  const drafted = saveDraft(used.state, used.session.id, { note: '변경 요청' }, now);
  assert.equal(restoreDraft(drafted.state, used.session.id, new Date(+now + 60 * 60000)).value.note, '변경 요청');
  assert.equal(restoreDraft(drafted.state, used.session.id, new Date(+now + 3 * 60 * 60000)).ok, false);
});

test('delivery records initial plus 1/5/30 attempts, queues only final failure, and resend is idempotent', () => {
  let state = createPrototypeState(now); let made = createDelivery(state, { id: 'D-1', reservationId: 'R-001', idempotencyKey: 'delivery-1', now, fail: true }); state = made.state;
  assert.equal(state.deliveries[0].attempts.length, 1); assert.equal(state.deliveries[0].queue, false);
  for (const minutes of [1, 5, 30]) state = advanceDelivery(state, new Date(+now + minutes * 60000), true).state;
  assert.equal(state.deliveries[0].attempts.length, 4); assert.equal(state.deliveries[0].queue, true);
  const once = resendDelivery(state, 'D-1', 'resend-1', false); const twice = resendDelivery(once.state, 'D-1', 'resend-1', false);
  assert.equal(twice.state.deliveries[0].attempts.length, once.state.deliveries[0].attempts.length);
});

test('stale, cancellation reason/confirmation, atomic release, and authority loss are observable no-ops or transitions', () => {
  let state = prepared(); const booked = confirmBooking(state, draft, { consents: Object.fromEntries(POLICY_TYPES.map((type) => [type, 1])) }); state = booked.state;
  const stale = mutateWithVersion(state, state.version - 1, () => ({ state: { ...state, version: 99 } })); assert.equal(stale.code, 'STALE'); assert.equal(stale.state, state);
  const noReason = cancelBooking(state, 'R-001', { expectedVersion: state.version, reason: '', confirmed: true }); assert.equal(noReason.state, state);
  const cancelled = cancelBooking(state, 'R-001', { expectedVersion: state.version, reason: '운영상 취소', confirmed: true }); assert.equal(cancelled.ok, true); assert.equal(cancelled.state.bookings[0].status, 'cancelled');
  const blockedChange = changeBookingState(cancelled.state, 'R-001', draft, { expectedVersion: cancelled.state.version }); assert.equal(blockedChange.ok, false);
});
