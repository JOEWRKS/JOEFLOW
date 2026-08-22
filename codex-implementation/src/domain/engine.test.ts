import { describe, expect, it } from 'vitest';
import { executeCommand } from './engine';
import { createSeedState } from './seed';
import { adjustmentTotals } from './selectors';

describe('domain command boundary', () => {
  it('denies an unrelated manager without mutating business or audit state', () => {
    const before = createSeedState();
    const result = executeCommand(before, {
      type: 'APPROVE_CLAIM',
      actorId: 'usr-manager-other',
      targetId: 'clm-submitted',
      expectedVersion: 1,
      idempotencyKey: 'deny-unrelated',
      input: { revision: 1 },
    });

    expect(result.outcome).toMatchObject({ status: 'rejected', code: 'FORBIDDEN' });
    expect(result.state.claims['clm-submitted']).toEqual(before.claims['clm-submitted']);
    expect(result.state.auditEvents).toEqual(before.auditEvents);
    expect(result.deliveryEventIds).toEqual([]);
  });

  it('denies self approval even when the actor is a manager', () => {
    const before = createSeedState();
    const result = executeCommand(before, {
      type: 'APPROVE_CLAIM',
      actorId: 'usr-manager',
      targetId: 'clm-self-review',
      expectedVersion: 1,
      idempotencyKey: 'deny-self-approval',
      input: { revision: 1 },
    });

    expect(result.outcome).toMatchObject({ status: 'rejected', code: 'SELF_APPROVAL_DENIED' });
    expect(result.auditEventIds).toEqual([]);
  });

  it('rejects a stale request atomically and preserves user input', () => {
    const before = createSeedState();
    const result = executeCommand(before, {
      type: 'REQUEST_CHANGES',
      actorId: 'usr-manager',
      targetId: 'clm-submitted',
      expectedVersion: 0,
      idempotencyKey: 'stale-request',
      input: { revision: 1, comment: 'Please clarify the merchant.' },
    });

    expect(result.outcome).toMatchObject({ status: 'rejected', code: 'STALE_VERSION' });
    expect(result.outcome.preservedInput).toEqual({ revision: 1, comment: 'Please clarify the merchant.' });
    expect(result.state.claims['clm-submitted']).toEqual(before.claims['clm-submitted']);
    expect(result.state.auditEvents).toEqual(before.auditEvents);
  });

  it('replays the exact original result for the same idempotency key and fingerprint', () => {
    const before = createSeedState();
    const command = {
      type: 'APPROVE_CLAIM' as const,
      actorId: 'usr-manager',
      targetId: 'clm-submitted',
      expectedVersion: 1,
      idempotencyKey: 'approve-once',
      input: { revision: 1 },
    };
    const first = executeCommand(before, command);
    const replay = executeCommand(first.state, command);

    expect(first.outcome.status).toBe('committed');
    expect(replay.outcome).toEqual(first.outcome);
    expect(replay.auditEventIds).toEqual(first.auditEventIds);
    expect(replay.deliveryEventIds).toEqual(first.deliveryEventIds);
    expect(replay.state.auditEvents).toHaveLength(first.state.auditEvents.length);
    expect(replay.state.deliveries).toHaveLength(first.state.deliveries.length);
  });

  it('rejects review against a non-current revision', () => {
    const before = createSeedState();
    const result = executeCommand(before, {
      type: 'APPROVE_CLAIM',
      actorId: 'usr-manager',
      targetId: 'clm-submitted',
      expectedVersion: 1,
      idempotencyKey: 'wrong-revision',
      input: { revision: 0 },
    });

    expect(result.outcome).toMatchObject({ status: 'rejected', code: 'REVISION_MISMATCH' });
    expect(result.auditEventIds).toEqual([]);
  });

  it('appends one immutable audit event to a successful transition', () => {
    const before = createSeedState();
    const previousAudit = [...before.auditEvents];
    const result = executeCommand(before, {
      type: 'REQUEST_CHANGES',
      actorId: 'usr-manager',
      targetId: 'clm-submitted',
      expectedVersion: 1,
      idempotencyKey: 'request-changes-once',
      input: { revision: 1, comment: 'Add the receipt total.' },
    });

    expect(result.outcome.status).toBe('committed');
    expect(result.state.auditEvents.slice(0, previousAudit.length)).toEqual(previousAudit);
    expect(result.state.auditEvents.at(-1)).toMatchObject({
      actorId: 'usr-manager',
      targetId: 'clm-submitted',
      action: 'REQUEST_CHANGES',
    });
  });
});

describe('claim lifecycle', () => {
  it('submits, requests changes, creates a new revision, approves, and revokes before scheduling', () => {
    let state = createSeedState();
    let result = executeCommand(state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'lifecycle-submit', input: {},
    });
    expect(result.state.claims['clm-draft'].status).toBe('Submitted');
    expect(result.deliveryEventIds).toHaveLength(2);

    state = result.state;
    result = executeCommand(state, {
      type: 'REQUEST_CHANGES', actorId: 'usr-manager', targetId: 'clm-draft', expectedVersion: 2,
      idempotencyKey: 'lifecycle-changes', input: { revision: 1, comment: 'Attach the detailed invoice.' },
    });
    expect(result.state.claims['clm-draft'].status).toBe('Changes requested');

    state = result.state;
    result = executeCommand(state, {
      type: 'REVISE_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 3,
      idempotencyKey: 'lifecycle-revise', input: {},
    });
    expect(result.state.claims['clm-draft']).toMatchObject({ status: 'Submitted', currentRevision: 2 });

    state = result.state;
    result = executeCommand(state, {
      type: 'APPROVE_CLAIM', actorId: 'usr-manager', targetId: 'clm-draft', expectedVersion: 4,
      idempotencyKey: 'lifecycle-approve', input: { revision: 2 },
    });
    expect(result.state.claims['clm-draft']).toMatchObject({ status: 'Payment pending', approvedRevision: 2 });

    state = result.state;
    result = executeCommand(state, {
      type: 'REVOKE_APPROVAL', actorId: 'usr-manager', targetId: 'clm-draft', expectedVersion: 5,
      idempotencyKey: 'lifecycle-revoke', input: { revision: 2, comment: 'The receipt was invalidated.' },
    });
    expect(result.state.claims['clm-draft'].status).toBe('Changes requested');
    expect(result.state.claims['clm-draft'].approvedRevision).toBeUndefined();
  });

  it('keeps final rejection and withdrawal terminal', () => {
    const rejected = executeCommand(createSeedState(), {
      type: 'FINAL_REJECT_CLAIM', actorId: 'usr-manager', targetId: 'clm-submitted', expectedVersion: 1,
      idempotencyKey: 'terminal-reject', input: { revision: 1, comment: 'This is not a business expense.' },
    });
    expect(rejected.state.claims['clm-submitted'].status).toBe('Final rejected');
    const retry = executeCommand(rejected.state, {
      type: 'REVISE_CLAIM', actorId: 'usr-employee', targetId: 'clm-submitted', expectedVersion: 2,
      idempotencyKey: 'terminal-revise-denied', input: {},
    });
    expect(retry.outcome).toMatchObject({ status: 'rejected', code: 'INVALID_STATUS' });

    const withdrawn = executeCommand(createSeedState(), {
      type: 'WITHDRAW_CLAIM', actorId: 'usr-employee', targetId: 'clm-submitted', expectedVersion: 1,
      idempotencyKey: 'terminal-withdraw', input: {},
    });
    expect(withdrawn.state.claims['clm-submitted'].status).toBe('Withdrawn');
  });
});

describe('payment and adjustment lifecycle', () => {
  it('atomically claims a pending payment and records a scheduled date', () => {
    const result = executeCommand(createSeedState(), {
      type: 'SCHEDULE_PAYMENT', actorId: 'usr-finance', targetId: 'clm-approved', expectedVersion: 1,
      idempotencyKey: 'schedule-payment', input: { scheduledDate: '2026-08-22' },
    });
    expect(result.outcome.status).toBe('committed');
    expect(result.state.claims['clm-approved']).toMatchObject({
      status: 'Scheduled', payment: { ownerId: 'usr-finance', scheduledDate: '2026-08-22' },
    });
    expect(result.auditEventIds).toHaveLength(1);
  });

  it('requires ownership, actual-date bounds, unique reference, and an Other description', () => {
    const otherOwner = executeCommand(createSeedState(), {
      type: 'COMPLETE_PAYMENT', actorId: 'usr-finance-other', targetId: 'clm-scheduled', expectedVersion: 2,
      idempotencyKey: 'wrong-owner', input: { actualDate: '2026-08-22', method: 'Bank transfer', externalReference: 'PAY-NEW' },
    });
    expect(otherOwner.outcome).toMatchObject({ status: 'rejected', code: 'PAYMENT_OWNER_REQUIRED' });

    const invalidOther = executeCommand(createSeedState(), {
      type: 'COMPLETE_PAYMENT', actorId: 'usr-finance', targetId: 'clm-scheduled', expectedVersion: 2,
      idempotencyKey: 'other-needs-detail', input: { actualDate: '2026-08-22', method: 'Other', externalReference: 'PAY-NEW' },
    });
    expect(invalidOther.outcome).toMatchObject({ status: 'rejected', code: 'METHOD_DESCRIPTION_REQUIRED' });

    const duplicate = executeCommand(createSeedState(), {
      type: 'COMPLETE_PAYMENT', actorId: 'usr-finance', targetId: 'clm-scheduled', expectedVersion: 2,
      idempotencyKey: 'duplicate-reference', input: { actualDate: '2026-08-22', method: 'Bank transfer', externalReference: 'PAY-1042' },
    });
    expect(duplicate.outcome).toMatchObject({ status: 'rejected', code: 'DUPLICATE_REFERENCE' });
  });

  it('reschedules only after structured verification concludes Not paid', () => {
    const denied = executeCommand(createSeedState(), {
      type: 'RESCHEDULE_PAYMENT', actorId: 'usr-finance', targetId: 'clm-failed', expectedVersion: 3,
      idempotencyKey: 'reschedule-before-check', input: { scheduledDate: '2026-08-22' },
    });
    expect(denied.outcome).toMatchObject({ status: 'rejected', code: 'NOT_PAID_VERIFICATION_REQUIRED' });

    const verified = executeCommand(createSeedState(), {
      type: 'VERIFY_FAILED_PAYMENT', actorId: 'usr-finance', targetId: 'clm-failed', expectedVersion: 3,
      idempotencyKey: 'verify-not-paid',
      input: {
        result: 'Not paid', channel: 'Bank portal', maskedAccount: '***1234', checkedFrom: '2026-08-20',
        checkedTo: '2026-08-22', externalReferenceOrResult: 'No matching transfer', conclusion: 'No payment was executed',
      },
    });
    expect(verified.state.claims['clm-failed'].payment.verification).toMatchObject({ result: 'Not paid', checkedBy: 'usr-finance' });

    const rescheduled = executeCommand(verified.state, {
      type: 'RESCHEDULE_PAYMENT', actorId: 'usr-finance', targetId: 'clm-failed', expectedVersion: 4,
      idempotencyKey: 'reschedule-after-check', input: { scheduledDate: '2026-08-22' },
    });
    expect(rescheduled.state.claims['clm-failed'].status).toBe('Scheduled');
  });

  it('allows one in-progress adjustment and calculates net from completed adjustments only', () => {
    const first = executeCommand(createSeedState(), {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 4,
      idempotencyKey: 'adjustment-first', input: { kind: 'Recovery', amountKrw: 18000, reason: 'Personal minibar charge' },
    });
    expect(first.outcome.status).toBe('committed');
    const adjustmentId = first.state.claims['clm-completed'].adjustmentIds[0];
    expect(adjustmentId).toBeTruthy();

    const duplicate = executeCommand(first.state, {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 5,
      idempotencyKey: 'adjustment-second-active', input: { kind: 'Additional payment', amountKrw: 5000, reason: 'Correction' },
    });
    expect(duplicate.outcome).toMatchObject({ status: 'rejected', code: 'ACTIVE_ADJUSTMENT_EXISTS' });
    expect(adjustmentTotals(first.state, 'clm-completed').netKrw).toBe(168000);

    const completed = executeCommand(first.state, {
      type: 'COMPLETE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 5,
      idempotencyKey: 'adjustment-complete',
      input: { adjustmentId, actualDate: '2026-08-22', externalReference: 'ADJ-1042' },
    });
    expect(adjustmentTotals(completed.state, 'clm-completed')).toEqual({
      originalKrw: 168000, recoveredKrw: 18000, addedKrw: 0, netKrw: 150000,
    });
  });

  it('blocks a replacement while failed adjustment execution remains unclear', () => {
    const created = executeCommand(createSeedState(), {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 4,
      idempotencyKey: 'unclear-create', input: { kind: 'Additional payment', amountKrw: 9000, reason: 'Underpayment' },
    });
    const adjustmentId = created.state.claims['clm-completed'].adjustmentIds[0];
    const failed = executeCommand(created.state, {
      type: 'FAIL_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 5,
      idempotencyKey: 'unclear-fail', input: { adjustmentId, reason: 'Provider timeout' },
    });
    const unclear = executeCommand(failed.state, {
      type: 'RESOLVE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 6,
      idempotencyKey: 'unclear-resolve', input: { adjustmentId, result: 'Unclear', note: 'Provider cannot confirm execution.' },
    });
    expect(unclear.state.adjustments[adjustmentId].status).toBe('Needs verification');
    const blocked = executeCommand(unclear.state, {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 7,
      idempotencyKey: 'unclear-blocks-new', input: { kind: 'Recovery', amountKrw: 1000, reason: 'Correction' },
    });
    expect(blocked.outcome).toMatchObject({ status: 'rejected', code: 'ACTIVE_ADJUSTMENT_EXISTS' });
  });
});
