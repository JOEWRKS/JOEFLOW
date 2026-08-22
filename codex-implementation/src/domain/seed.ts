import type { Claim, ClaimRevision, DomainState } from './types';

const NOW = '2026-08-22T09:00:00+09:00';

function revision(number: number, overrides: Partial<ClaimRevision> = {}): ClaimRevision {
  return {
    number,
    merchant: 'Seoul Business Hotel',
    categoryId: 'CAT-002',
    categoryNameSnapshot: '출장 숙박비',
    expenseDate: '2026-08-18',
    currency: 'KRW',
    originalAmount: 168000,
    krwAmount: 168000,
    businessPurpose: 'Customer workshop lodging',
    duplicateReason: 'Separate approved trip night',
    receiptIds: [],
    ...overrides,
  };
}

function claim(id: string, overrides: Partial<Claim> = {}): Claim {
  const defaultRevision = revision(1, { submittedAt: NOW, receiptIds: [`file-${id}-receipt`] });
  return {
    id,
    employeeId: 'usr-employee',
    managerId: 'usr-manager',
    status: 'Submitted',
    version: 1,
    currentRevision: 1,
    revisions: [defaultRevision],
    payment: {},
    adjustmentIds: [],
    createdAt: NOW,
    updatedAt: NOW,
    ...overrides,
  };
}

export function createSeedState(): DomainState {
  const claims: Record<string, Claim> = {
    'clm-draft': claim('clm-draft', { status: 'Draft', revisions: [revision(1, { submittedAt: undefined, receiptIds: ['file-clm-draft-receipt'] })] }),
    'clm-submitted': claim('clm-submitted'),
    'clm-self-review': claim('clm-self-review', { employeeId: 'usr-manager', managerId: 'usr-manager' }),
    'clm-changes': claim('clm-changes', {
      status: 'Changes requested',
      version: 3,
      currentRevision: 2,
      revisions: [
        revision(1, { submittedAt: '2026-08-19T09:00:00+09:00', receiptIds: ['file-clm-changes-receipt'] }),
        revision(2, { receiptIds: ['file-clm-changes-receipt'] }),
      ],
    }),
    'clm-approved': claim('clm-approved', { status: 'Payment pending', approvedRevision: 1, approvedAt: '2026-08-21T10:00:00+09:00' }),
    'clm-scheduled': claim('clm-scheduled', {
      status: 'Scheduled',
      version: 2,
      approvedRevision: 1,
      approvedAt: '2026-08-20T10:00:00+09:00',
      payment: { ownerId: 'usr-finance', scheduledDate: '2026-08-22' },
    }),
    'clm-failed': claim('clm-failed', {
      status: 'Payment failed',
      version: 3,
      approvedRevision: 1,
      approvedAt: '2026-08-20T10:00:00+09:00',
      payment: { ownerId: 'usr-finance', scheduledDate: '2026-08-21', failureReason: 'Bank rejected recipient details' },
    }),
    'clm-completed': claim('clm-completed', {
      status: 'Payment completed',
      version: 4,
      approvedRevision: 1,
      approvedAt: '2026-08-20T10:00:00+09:00',
      payment: { ownerId: 'usr-finance', scheduledDate: '2026-08-21', actualDate: '2026-08-21', method: 'Bank transfer', externalReference: 'PAY-1042' },
    }),
  };
  for (const claim of Object.values(claims)) {
    for (const item of claim.revisions) item.managerIdSnapshot = claim.managerId;
  }
  const files = Object.fromEntries(Object.keys(claims).map((claimId) => {
    const id = `file-${claimId}-receipt`;
    return [id, {
      id,
      claimId,
      name: 'hotel-receipt.pdf',
      mime: 'application/pdf' as const,
      sizeBytes: 245000,
      sha256: `sha256-${claimId}`,
      purpose: 'RECEIPT' as const,
      source: 'file' as const,
      scanStatus: 'Linked' as const,
    }];
  }));
  return {
    schemaVersion: 1,
    canonicalRevision: 55,
    canonicalDigest: '18db3c33caa36d8925960523116ed4646a3756b8047cdb9098256cf67097b48f',
    now: NOW,
    users: {
      'usr-employee': { id: 'usr-employee', name: 'Minji Kim', roles: ['EMPLOYEE'], managerId: 'usr-manager', active: true, authVersion: 1, version: 1 },
      'usr-manager': { id: 'usr-manager', name: 'Joon Park', roles: ['MANAGER'], managerId: 'usr-director', active: true, authVersion: 1, version: 1 },
      'usr-manager-other': { id: 'usr-manager-other', name: 'Sora Lee', roles: ['MANAGER'], active: true, authVersion: 1, version: 1 },
      'usr-finance': { id: 'usr-finance', name: 'Finance Kim', roles: ['FINANCE'], active: true, authVersion: 1, version: 1 },
      'usr-finance-other': { id: 'usr-finance-other', name: 'Finance Choi', roles: ['FINANCE'], active: true, authVersion: 1, version: 1 },
      'usr-admin': { id: 'usr-admin', name: 'Admin Han', roles: ['ADMIN'], active: true, authVersion: 1, version: 1 },
    },
    claims,
    files,
    adjustments: {},
    categories: {
      'CAT-001': { id: 'CAT-001', name: 'Transportation', active: true, version: 1 },
      'CAT-002': { id: 'CAT-002', name: 'Business lodging', active: true, version: 1 },
      'CAT-003': { id: 'CAT-003', name: 'Meals', active: true, version: 1 },
      'CAT-004': { id: 'CAT-004', name: 'Entertainment', active: true, version: 1 },
      'CAT-005': { id: 'CAT-005', name: 'Office supplies', active: true, version: 1 },
      'CAT-006': { id: 'CAT-006', name: 'Software & subscriptions', active: true, version: 1 },
      'CAT-007': { id: 'CAT-007', name: 'Training & books', active: true, version: 1 },
      'CAT-008': { id: 'CAT-008', name: 'Communications', active: true, version: 1 },
      'CAT-009': { id: 'CAT-009', name: 'Other', active: true, version: 1 },
    },
    invitations: {},
    auditEvents: [],
    deliveries: [{
      id: 'delivery-reassign-failed', targetId: 'clm-submitted', channel: 'EMAIL', recipientId: 'usr-manager-other',
      template: 'REASSIGN_MANAGER', status: 'Permanent failure', attempts: 4, manualRetryUsed: false, version: 1,
    }],
    warnings: [{ id: 'warning-reassign', targetId: 'delivery-reassign-failed', message: 'Manager reassignment remains committed; notification delivery permanently failed.', resolved: false }],
    exports: [],
    idempotency: {},
    nextSequence: 1,
  };
}
