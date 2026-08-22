import { describe, expect, it } from 'vitest';
import { executeCommand } from './engine';
import { createSeedState } from './seed';
import { adjustmentTotals, claimsForRole } from './selectors';

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
    expect(result.changedFields).toContain('version');
  });

  it('replays an original rejected result even after the rejection condition changes', () => {
    const before = createSeedState();
    before.claims['clm-draft'].revisions[0].expenseDate = '2026-08-23';
    const command = {
      type: 'SUBMIT_CLAIM' as const,
      actorId: 'usr-employee',
      targetId: 'clm-draft',
      expectedVersion: 1,
      idempotencyKey: 'rejected-submit-once',
      input: {},
    };
    const first = executeCommand(before, command);
    first.state.claims['clm-draft'].revisions[0].expenseDate = '2026-08-18';
    const replay = executeCommand(first.state, command);

    expect(first.outcome).toMatchObject({ status: 'rejected', code: 'FUTURE_EXPENSE_DATE' });
    expect(replay.outcome).toEqual(first.outcome);
    expect(replay.state.claims['clm-draft'].status).toBe('Draft');
    expect(replay.auditEventIds).toEqual([]);
  });

  it('limits manager and Finance selectors to current processing authority', () => {
    const state = createSeedState();
    expect(claimsForRole(state, 'usr-manager', 'MANAGER').map((claim) => claim.id).sort()).toEqual([
      'clm-approved',
      'clm-submitted',
    ]);
    expect(claimsForRole(state, 'usr-finance-other', 'FINANCE').map((claim) => claim.id)).toEqual(['clm-approved']);
    state.users['usr-manager'].active = false;
    state.users['usr-employee'].active = false;
    expect(claimsForRole(state, 'usr-manager', 'MANAGER')).toEqual([]);
    expect(claimsForRole(state, 'usr-employee', 'EMPLOYEE')).toEqual([]);
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
  it('keeps timed-out scan bytes unlinked, retries at 30s/2m, and discards after the second timeout', () => {
    const started = executeCommand(createSeedState(), {
      type: 'LINK_ATTACHMENT', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'scan-timeout-start', input: { name: 'extra.pdf', mime: 'application/pdf', sizeBytes: 1000, sha256: 'scan-timeout', source: 'file', purpose: 'RECEIPT', scanOutcome: 'Timeout' },
    });
    const file = Object.values(started.state.files).find((item) => item.sha256 === 'scan-timeout')!;
    expect(file).toMatchObject({ scanStatus: 'Scanning', scanAttempts: 0 });
    expect(started.state.claims['clm-draft'].revisions[0].receiptIds).not.toContain(file.id);
    const firstRetry = executeCommand(started.state, {
      type: 'RETRY_ATTACHMENT_SCAN', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 2,
      idempotencyKey: 'scan-timeout-retry-1', input: { fileId: file.id, scanOutcome: 'Timeout' },
    });
    expect(firstRetry.state.files[file.id]).toMatchObject({ scanStatus: 'Scanning', scanAttempts: 1 });
    const finalRetry = executeCommand(firstRetry.state, {
      type: 'RETRY_ATTACHMENT_SCAN', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 3,
      idempotencyKey: 'scan-timeout-retry-2', input: { fileId: file.id, scanOutcome: 'Timeout' },
    });
    expect(finalRetry.state.files[file.id]).toBeUndefined();
    expect(finalRetry.outcome.message).toMatch(/discarded/i);
  });

  it.each([
    ['missing merchant', (state: ReturnType<typeof createSeedState>) => { state.claims['clm-draft'].revisions[0].merchant = ''; }, 'REQUIRED_FIELDS'],
    ['future date', (state: ReturnType<typeof createSeedState>) => { state.claims['clm-draft'].revisions[0].expenseDate = '2026-08-23'; }, 'FUTURE_EXPENSE_DATE'],
    ['late without reason', (state: ReturnType<typeof createSeedState>) => { state.claims['clm-draft'].revisions[0].expenseDate = '2026-01-01'; state.claims['clm-draft'].revisions[0].lateReason = ''; }, 'LATE_REASON_REQUIRED'],
    ['inactive category', (state: ReturnType<typeof createSeedState>) => { state.categories['CAT-002'].active = false; }, 'ACTIVE_CATEGORY_REQUIRED'],
    ['unclean receipt', (state: ReturnType<typeof createSeedState>) => { state.files['file-clm-draft-receipt'].scanStatus = 'Scanning'; }, 'SCAN_PENDING'],
    ['invalid FX rounding', (state: ReturnType<typeof createSeedState>) => {
      const item = state.claims['clm-draft'].revisions[0];
      item.currency = 'USD'; item.originalAmount = 100; item.exchangeRate = 1300; item.krwAmount = 130002; item.exchangeEvidenceIds = ['file-clm-draft-receipt'];
    }, 'FX_CONVERSION_INVALID'],
    ['duplicate without reason', (state: ReturnType<typeof createSeedState>) => { state.claims['clm-draft'].revisions[0].duplicateReason = ''; }, 'DUPLICATE_REASON_REQUIRED'],
    ['missing manager', (state: ReturnType<typeof createSeedState>) => { state.users['usr-employee'].managerId = undefined; }, 'MANAGER_REQUIRED'],
  ])('blocks %s without audit or delivery effects', (_name, mutate, code) => {
    const state = createSeedState();
    mutate(state);
    const result = executeCommand(state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: `invalid-${code}`, input: {},
    });
    expect(result.outcome).toMatchObject({ status: 'rejected', code });
    expect(result.auditEventIds).toEqual([]);
    expect(result.deliveryEventIds).toEqual([]);
    expect(result.state.claims['clm-draft'].status).toBe('Draft');
  });

  it('submits, requests changes, edits and resubmits a new revision, then revokes approval to the same Submitted revision', () => {
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
    expect(result.state.claims['clm-draft']).toMatchObject({ status: 'Draft', currentRevision: 2 });
    expect(result.state.claims['clm-draft'].revisions[1].submittedAt).toBeUndefined();

    state = result.state;
    result = executeCommand(state, {
      type: 'UPDATE_DRAFT', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 4,
      idempotencyKey: 'lifecycle-edit-revision', input: { merchant: 'Corrected merchant' },
    });
    state = result.state;
    result = executeCommand(state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 5,
      idempotencyKey: 'lifecycle-resubmit', input: {},
    });
    expect(result.state.claims['clm-draft']).toMatchObject({ status: 'Submitted', currentRevision: 2 });
    expect(result.state.claims['clm-draft'].revisions[1].merchant).toBe('Corrected merchant');

    state = result.state;
    result = executeCommand(state, {
      type: 'APPROVE_CLAIM', actorId: 'usr-manager', targetId: 'clm-draft', expectedVersion: 6,
      idempotencyKey: 'lifecycle-approve', input: { revision: 2 },
    });
    expect(result.state.claims['clm-draft']).toMatchObject({ status: 'Payment pending', approvedRevision: 2 });

    state = result.state;
    result = executeCommand(state, {
      type: 'REVOKE_APPROVAL', actorId: 'usr-manager', targetId: 'clm-draft', expectedVersion: 7,
      idempotencyKey: 'lifecycle-revoke', input: { revision: 2, comment: 'The receipt was invalidated.' },
    });
    expect(result.state.claims['clm-draft'].status).toBe('Submitted');
    expect(result.state.claims['clm-draft'].currentRevision).toBe(2);
    expect(result.state.claims['clm-draft'].approvedRevision).toBeUndefined();
  });

  it('creates a fresh employee draft and snapshots the current direct manager on submission', () => {
    let state = createSeedState();
    const created = executeCommand(state, {
      type: 'CREATE_DRAFT', actorId: 'usr-employee', targetId: 'claim-register', expectedVersion: 0,
      idempotencyKey: 'create-fresh-draft', input: {},
    });
    expect(created.outcome.status).toBe('committed');
    const createdClaim = Object.values(created.state.claims).find((claim) => claim.createdAt === created.state.now && claim.revisions[0].merchant === '');
    expect(createdClaim).toMatchObject({ status: 'Draft', employeeId: 'usr-employee', currentRevision: 1 });

    state = createSeedState();
    state.users['usr-employee'].managerId = 'usr-manager-other';
    const submitted = executeCommand(state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'submit-current-manager', input: {},
    });
    expect(submitted.state.claims['clm-draft'].managerId).toBe('usr-manager-other');
    expect(submitted.state.claims['clm-draft'].revisions[0].managerIdSnapshot).toBe('usr-manager-other');
    expect(submitted.state.deliveries.filter((item) => item.recipientId === 'usr-manager-other' && item.template === 'SUBMIT_CLAIM')).toHaveLength(2);
  });

  it('blocks an exact receipt hash already retained by another claim without leaking its identity', () => {
    const state = createSeedState();
    state.files['file-clm-draft-receipt'].sha256 = state.files['file-clm-submitted-receipt'].sha256;
    const result = executeCommand(state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'duplicate-receipt-hash', input: {},
    });
    expect(result.outcome).toMatchObject({ status: 'rejected', code: 'DUPLICATE_RECEIPT' });
    expect(result.outcome.message).not.toContain('clm-submitted');
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

  it('blocks a new adjustment immediately after failure until external execution is resolved', () => {
    const created = executeCommand(createSeedState(), {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 4,
      idempotencyKey: 'failed-gate-create', input: { kind: 'Recovery', amountKrw: 9000, reason: 'Recovery' },
    });
    const adjustmentId = created.state.claims['clm-completed'].adjustmentIds[0];
    const failed = executeCommand(created.state, {
      type: 'FAIL_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 5,
      idempotencyKey: 'failed-gate-fail', input: { adjustmentId, reason: 'Unknown provider result' },
    });
    const blocked = executeCommand(failed.state, {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 6,
      idempotencyKey: 'failed-gate-second', input: { kind: 'Additional payment', amountKrw: 9000, reason: 'Unsafe retry' },
    });
    expect(blocked.outcome).toMatchObject({ status: 'rejected', code: 'ACTIVE_ADJUSTMENT_EXISTS' });
  });

  it('requires the current Finance owner for all adjustment mutations and permits hold only from Scheduled', () => {
    const wrongOwner = executeCommand(createSeedState(), {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance-other', targetId: 'clm-completed', expectedVersion: 4,
      idempotencyKey: 'wrong-adjustment-owner', input: { kind: 'Recovery', amountKrw: 1000, reason: 'Correction' },
    });
    expect(wrongOwner.outcome).toMatchObject({ status: 'rejected', code: 'PAYMENT_OWNER_REQUIRED' });

    const invalidHold = executeCommand(createSeedState(), {
      type: 'HOLD_PAYMENT', actorId: 'usr-finance', targetId: 'clm-approved', expectedVersion: 1,
      idempotencyKey: 'pending-hold-denied', input: { reason: 'Investigate' },
    });
    expect(invalidHold.outcome).toMatchObject({ status: 'rejected', code: 'INVALID_STATUS' });
  });

  it('uses the verified actual adjustment amount and bounded date for Executed resolution', () => {
    const created = executeCommand(createSeedState(), {
      type: 'CREATE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 4,
      idempotencyKey: 'executed-create', input: { kind: 'Recovery', amountKrw: 18000, reason: 'Expected recovery' },
    });
    const adjustmentId = created.state.claims['clm-completed'].adjustmentIds[0];
    const failed = executeCommand(created.state, {
      type: 'FAIL_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 5,
      idempotencyKey: 'executed-fail', input: { adjustmentId, reason: 'Provider timeout' },
    });
    const resolved = executeCommand(failed.state, {
      type: 'RESOLVE_ADJUSTMENT', actorId: 'usr-finance', targetId: 'clm-completed', expectedVersion: 6,
      idempotencyKey: 'executed-resolve',
      input: { adjustmentId, result: 'Executed', note: 'Bank confirmed', actualAmountKrw: 17000, actualDate: '2026-08-22', externalReference: 'ADJ-EXEC-1' },
    });
    expect(resolved.state.adjustments[adjustmentId]).toMatchObject({ status: 'Completed', actualAmountKrw: 17000 });
    expect(adjustmentTotals(resolved.state, 'clm-completed')).toMatchObject({ recoveredKrw: 17000, netKrw: 151000 });
  });
});

describe('Admin governance', () => {
  it('runs idempotent KST daily overdue, review-reminder, warning, and draft-retention operations', () => {
    const state = createSeedState();
    state.now = '2026-08-30T02:00:00+09:00';
    state.claims['clm-submitted'].revisions[0].submittedAt = '2026-08-20T09:00:00+09:00';
    state.claims['clm-draft'].updatedAt = '2026-06-08T09:00:00+09:00';
    const first = executeCommand(state, {
      type: 'RUN_DAILY_OPERATIONS', actorId: 'usr-admin', targetId: 'daily-2026-08-30', expectedVersion: 0,
      idempotencyKey: 'daily-2026-08-30', input: {},
    });
    expect(first.state.claims['clm-scheduled'].payment.overdue).toBe(true);
    expect(first.state.deliveries.filter((item) => item.template === 'PAYMENT_OVERDUE')).toHaveLength(2);
    expect(first.state.deliveries.filter((item) => item.template === 'MANAGER_REVIEW_REMINDER')).toHaveLength(4);
    expect(first.state.deliveries.filter((item) => item.template === 'DRAFT_EXPIRY_WARNING')).toHaveLength(2);
    expect(first.state.warnings.some((item) => item.targetId === 'review-clm-submitted')).toBe(true);
    const replay = executeCommand(first.state, {
      type: 'RUN_DAILY_OPERATIONS', actorId: 'usr-admin', targetId: 'daily-2026-08-30', expectedVersion: 0,
      idempotencyKey: 'daily-2026-08-30', input: {},
    });
    expect(replay.state.deliveries).toHaveLength(first.state.deliveries.length);

    const expiryState = createSeedState();
    expiryState.now = '2026-11-22T02:00:00+09:00';
    expiryState.claims['clm-draft'].updatedAt = '2026-08-22T09:00:00+09:00';
    const expired = executeCommand(expiryState, {
      type: 'RUN_DAILY_OPERATIONS', actorId: 'usr-admin', targetId: 'daily-2026-11-22', expectedVersion: 0,
      idempotencyKey: 'daily-2026-11-22', input: {},
    });
    expect(expired.state.claims['clm-draft']).toBeUndefined();
    expect(Object.values(expired.state.files).some((file) => file.claimId === 'clm-draft')).toBe(false);
    expect(expired.state.auditEvents.some((event) => event.targetId === 'clm-draft' && event.changedFields.includes('expiredDraft.deleted'))).toBe(true);
  });

  it('applies three bounded delivery retries before permanent failure and an Admin warning', () => {
    let state = createSeedState();
    state.deliveries[0].status = 'Queued';
    state.deliveries[0].attempts = 0;
    state.warnings = [];
    for (let attempt = 1; attempt <= 3; attempt += 1) {
      state = executeCommand(state, {
        type: 'RUN_DELIVERY_RETRIES', actorId: 'usr-admin', targetId: `delivery-retry-${attempt}`, expectedVersion: 0,
        idempotencyKey: `delivery-retry-${attempt}`, input: { failedDeliveryIds: ['delivery-reassign-failed'] },
      }).state;
    }
    expect(state.deliveries[0]).toMatchObject({ status: 'Permanent failure', attempts: 3 });
    expect(state.warnings.some((warning) => warning.targetId === 'delivery-reassign-failed' && !warning.resolved)).toBe(true);
  });

  it('records target version and before/after provenance, and returns actual intervening fields on stale writes', () => {
    const changed = executeCommand(createSeedState(), {
      type: 'UPDATE_DRAFT', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'provenance-change', input: { merchant: 'Changed merchant' },
    });
    expect(changed.state.auditEvents.at(-1)).toMatchObject({
      targetId: 'clm-draft', targetVersion: 2, revision: 1,
      before: { version: 1 }, after: { version: 2 },
    });
    const stale = executeCommand(changed.state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'provenance-stale', input: {},
    });
    expect(stale.outcome).toMatchObject({ status: 'rejected', code: 'STALE_VERSION', preservedInput: {} });
    expect(stale.changedFields).toEqual(['version', 'revision.merchant']);
  });

  it('reissues invitations by invalidating the old link and rejects a stale revoke race', () => {
    const issued = executeCommand(createSeedState(), {
      type: 'ISSUE_INVITATION', actorId: 'usr-admin', targetId: 'invitation-register', expectedVersion: 0,
      idempotencyKey: 'admin-issue', input: { email: 'person@example.com', roles: ['EMPLOYEE'], managerId: 'usr-manager' },
    });
    const oldId = Object.keys(issued.state.invitations)[0];
    const reissued = executeCommand(issued.state, {
      type: 'REISSUE_INVITATION', actorId: 'usr-admin', targetId: oldId, expectedVersion: 1,
      idempotencyKey: 'admin-reissue', input: {},
    });
    expect(reissued.state.invitations[oldId]).toMatchObject({ status: 'Expired', version: 2 });
    expect(Object.values(reissued.state.invitations).filter((item) => item.status === 'Pending')).toHaveLength(1);
    const staleRevoke = executeCommand(reissued.state, {
      type: 'REVOKE_INVITATION', actorId: 'usr-admin', targetId: oldId, expectedVersion: 1,
      idempotencyKey: 'admin-stale-revoke', input: { reason: 'No longer joining' },
    });
    expect(staleRevoke.outcome).toMatchObject({ status: 'rejected', code: 'STALE_VERSION' });
    expect(staleRevoke.auditEventIds).toEqual([]);
  });

  it('invalidates sessions on account deactivation and immediately denies later work', () => {
    const updated = executeCommand(createSeedState(), {
      type: 'UPDATE_ACCOUNT', actorId: 'usr-admin', targetId: 'usr-employee', expectedVersion: 1,
      idempotencyKey: 'admin-deactivate', input: { active: false, roles: ['EMPLOYEE'], reason: 'Employment ended' },
    });
    expect(updated.state.users['usr-employee']).toMatchObject({ active: false, authVersion: 2, version: 2 });
    const denied = executeCommand(updated.state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'inactive-submit', input: {},
    });
    expect(denied.outcome).toMatchObject({ status: 'rejected', code: 'FORBIDDEN' });
  });

  it('accepts only the invited email before expiry and loses atomically to a prior revocation', () => {
    const issued = executeCommand(createSeedState(), {
      type: 'ISSUE_INVITATION', actorId: 'usr-admin', targetId: 'invitation-register', expectedVersion: 0,
      idempotencyKey: 'accept-issue', input: { email: 'invitee@example.com', roles: ['EMPLOYEE', 'MANAGER'], managerId: 'usr-manager' },
    });
    const invitation = Object.values(issued.state.invitations).find((item) => item.email === 'invitee@example.com')!;
    const wrongEmail = executeCommand(issued.state, {
      type: 'ACCEPT_INVITATION', actorId: 'invitee', targetId: invitation.id, expectedVersion: 1,
      idempotencyKey: 'accept-wrong-email', input: { email: 'wrong@example.com', name: 'Invitee' },
    });
    expect(wrongEmail.outcome).toMatchObject({ status: 'rejected', code: 'INVITED_EMAIL_REQUIRED' });
    const accepted = executeCommand(issued.state, {
      type: 'ACCEPT_INVITATION', actorId: 'invitee', targetId: invitation.id, expectedVersion: 1,
      idempotencyKey: 'accept-right-email', input: { email: 'invitee@example.com', name: 'Invitee' },
    });
    expect(accepted.state.invitations[invitation.id].status).toBe('Accepted');
    expect(Object.values(accepted.state.users).find((item) => item.email === 'invitee@example.com')).toMatchObject({ active: true, roles: ['EMPLOYEE', 'MANAGER'] });

    const revoked = executeCommand(issued.state, {
      type: 'REVOKE_INVITATION', actorId: 'usr-admin', targetId: invitation.id, expectedVersion: 1,
      idempotencyKey: 'accept-race-revoke', input: { reason: 'Offer withdrawn' },
    });
    const losingAcceptance = executeCommand(revoked.state, {
      type: 'ACCEPT_INVITATION', actorId: 'invitee', targetId: invitation.id, expectedVersion: 1,
      idempotencyKey: 'accept-race-loser', input: { email: 'invitee@example.com', name: 'Invitee' },
    });
    expect(losingAcceptance.outcome).toMatchObject({ status: 'rejected', code: 'STALE_VERSION' });
  });

  it('creates a stable category and exposes role/direct-manager governance commands', () => {
    const created = executeCommand(createSeedState(), {
      type: 'CREATE_CATEGORY', actorId: 'usr-admin', targetId: 'category-register', expectedVersion: 0,
      idempotencyKey: 'create-category', input: { name: 'Parking', reason: 'New reimbursable expense' },
    });
    expect(Object.values(created.state.categories).find((item) => item.name === 'Parking')).toMatchObject({ active: true, version: 1 });
    const roles = executeCommand(created.state, {
      type: 'UPDATE_ACCOUNT', actorId: 'usr-admin', targetId: 'usr-employee', expectedVersion: 1,
      idempotencyKey: 'multi-role', input: { active: true, roles: ['EMPLOYEE', 'FINANCE'], reason: 'Temporary Finance coverage' },
    });
    expect(roles.state.users['usr-employee'].roles).toEqual(['EMPLOYEE', 'FINANCE']);
    const manager = executeCommand(roles.state, {
      type: 'ASSIGN_MANAGER', actorId: 'usr-admin', targetId: 'usr-employee', expectedVersion: 2,
      idempotencyKey: 'assign-direct-manager', input: { managerId: 'usr-manager-other', reason: 'Reporting line changed' },
    });
    expect(manager.state.users['usr-employee'].managerId).toBe('usr-manager-other');
  });

  it('reopens a Payment hold only after required Finance verification when execution was possible', () => {
    const state = createSeedState();
    state.claims['clm-scheduled'].payment.holdExternalExecutionPossible = true;
    const held = executeCommand(state, {
      type: 'HOLD_PAYMENT', actorId: 'usr-finance', targetId: 'clm-scheduled', expectedVersion: 2,
      idempotencyKey: 'hold-possible', input: { reason: 'Bank response uncertain', externalExecutionPossible: true },
    });
    const blocked = executeCommand(held.state, {
      type: 'REOPEN_HOLD', actorId: 'usr-admin', targetId: 'clm-scheduled', expectedVersion: 3,
      idempotencyKey: 'reopen-before-verification', input: { reason: 'Correct claim' },
    });
    expect(blocked.outcome).toMatchObject({ status: 'rejected', code: 'NOT_PAID_VERIFICATION_REQUIRED' });
    const verified = executeCommand(held.state, {
      type: 'VERIFY_HELD_PAYMENT', actorId: 'usr-finance', targetId: 'clm-scheduled', expectedVersion: 3,
      idempotencyKey: 'verify-held-not-paid', input: {
        result: 'Not paid', channel: 'Bank portal', maskedAccount: '***1234', checkedFrom: '2026-08-20',
        checkedTo: '2026-08-22', externalReferenceOrResult: 'No transfer', conclusion: 'Not executed',
      },
    });
    const reopened = executeCommand(verified.state, {
      type: 'REOPEN_HOLD', actorId: 'usr-admin', targetId: 'clm-scheduled', expectedVersion: 4,
      idempotencyKey: 'reopen-after-verification', input: { reason: 'Correct and reapprove' },
    });
    expect(reopened.state.claims['clm-scheduled']).toMatchObject({ status: 'Changes requested', approvedRevision: undefined });
    expect(reopened.state.claims['clm-scheduled'].payment.ownerId).toBeUndefined();
  });

  it('allows zero active categories while submission blocks and preserves historical category snapshots', () => {
    const state = createSeedState();
    for (const category of Object.values(state.categories)) category.active = category.id === 'CAT-002';
    const deactivated = executeCommand(state, {
      type: 'UPDATE_CATEGORY', actorId: 'usr-admin', targetId: 'CAT-002', expectedVersion: 1,
      idempotencyKey: 'last-category', input: { active: false, name: 'Lodging', reason: 'Consolidation' },
    });
    expect(deactivated.outcome.status).toBe('committed');
    expect(Object.values(deactivated.state.categories).filter((item) => item.active)).toHaveLength(0);
    const blockedSubmit = executeCommand(deactivated.state, {
      type: 'SUBMIT_CLAIM', actorId: 'usr-employee', targetId: 'clm-draft', expectedVersion: 1,
      idempotencyKey: 'zero-category-submit', input: {},
    });
    expect(blockedSubmit.outcome).toMatchObject({ status: 'rejected', code: 'ACTIVE_CATEGORY_REQUIRED' });
    const renamed = executeCommand(createSeedState(), {
      type: 'UPDATE_CATEGORY', actorId: 'usr-admin', targetId: 'CAT-002', expectedVersion: 1,
      idempotencyKey: 'rename-category', input: { active: true, name: 'Accommodation', reason: 'Terminology update' },
    });
    expect(renamed.state.categories['CAT-002'].name).toBe('Accommodation');
    expect(renamed.state.claims['clm-submitted'].revisions[0].categoryNameSnapshot).toBe('Business lodging');
  });

  it('applies and releases legal hold atomically and permits one manual delivery retry', () => {
    const held = executeCommand(createSeedState(), {
      type: 'SET_LEGAL_HOLD', actorId: 'usr-admin', targetId: 'clm-completed', expectedVersion: 4,
      idempotencyKey: 'hold-set', input: { reason: 'Tax inquiry' },
    });
    expect(held.state.claims['clm-completed'].legalHold?.reason).toBe('Tax inquiry');
    const released = executeCommand(held.state, {
      type: 'RELEASE_LEGAL_HOLD', actorId: 'usr-admin', targetId: 'clm-completed', expectedVersion: 5,
      idempotencyKey: 'hold-release', input: { reason: 'Inquiry closed' },
    });
    expect(released.state.claims['clm-completed'].legalHold).toBeUndefined();

    const retried = executeCommand(released.state, {
      type: 'RETRY_DELIVERY', actorId: 'usr-admin', targetId: 'delivery-reassign-failed', expectedVersion: 1,
      idempotencyKey: 'delivery-manual', input: {},
    });
    expect(retried.state.deliveries.find((item) => item.id === 'delivery-reassign-failed')).toMatchObject({ status: 'Queued', attempts: 5, manualRetryUsed: true });
    expect(retried.state.claims['clm-submitted'].status).toBe('Submitted');
  });
});
