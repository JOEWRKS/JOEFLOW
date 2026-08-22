export type Role = 'EMPLOYEE' | 'MANAGER' | 'FINANCE' | 'ADMIN';

export type ClaimStatus =
  | 'Draft'
  | 'Submitted'
  | 'Changes requested'
  | 'Manager approved'
  | 'Final rejected'
  | 'Withdrawn'
  | 'Payment pending'
  | 'Scheduled'
  | 'Payment failed'
  | 'Payment hold'
  | 'Payment completed';

export type AdjustmentStatus = 'In progress' | 'Failed' | 'Needs verification' | 'Completed' | 'Cancelled';

export interface User {
  id: string;
  name: string;
  roles: Role[];
  managerId?: string;
  active: boolean;
  authVersion: number;
}

export interface ClaimRevision {
  number: number;
  submittedAt?: string;
  merchant: string;
  categoryId: string;
  expenseDate: string;
  currency: string;
  originalAmount: number;
  krwAmount: number;
  exchangeRate?: number;
  duplicateReason?: string;
  comment?: string;
  receiptIds: string[];
}

export interface PaymentRecord {
  ownerId?: string;
  scheduledDate?: string;
  actualDate?: string;
  method?: 'Bank transfer' | 'Corporate card' | 'Other';
  methodDescription?: string;
  externalReference?: string;
  failureReason?: string;
  holdReason?: string;
  verification?: {
    result: 'Not paid' | 'Paid' | 'Unclear';
    channel: string;
    maskedAccount: string;
    checkedFrom: string;
    checkedTo: string;
    externalReferenceOrResult: string;
    conclusion: string;
    checkedBy: string;
    checkedAt: string;
  };
}

export interface Adjustment {
  id: string;
  claimId: string;
  kind: 'Recovery' | 'Additional payment';
  amountKrw: number;
  status: AdjustmentStatus;
  reason: string;
  externalReference?: string;
  actualDate?: string;
  replacesAdjustmentId?: string;
  verification?: {
    result: 'Not executed' | 'Executed' | 'Unclear';
    note: string;
    checkedBy: string;
    checkedAt: string;
  };
  version: number;
}

export interface Claim {
  id: string;
  employeeId: string;
  managerId: string;
  status: ClaimStatus;
  version: number;
  currentRevision: number;
  revisions: ClaimRevision[];
  payment: PaymentRecord;
  adjustmentIds: string[];
  approvedRevision?: number;
  approvedAt?: string;
  finalRejectedAt?: string;
  withdrawnAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Category {
  id: string;
  name: string;
  active: boolean;
  version: number;
}

export interface Invitation {
  id: string;
  email: string;
  roles: Role[];
  managerId?: string;
  status: 'Pending' | 'Accepted' | 'Expired' | 'Revoked';
  expiresAt: string;
  version: number;
}

export interface AuditEvent {
  id: string;
  actorId: string;
  targetId: string;
  action: DomainCommandType;
  at: string;
  changedFields: string[];
  reason?: string;
}

export interface DeliveryEvent {
  id: string;
  targetId: string;
  channel: 'APP' | 'EMAIL';
  recipientId: string;
  template: string;
  status: 'Queued' | 'Permanent failure' | 'Delivered';
  attempts: number;
  manualRetryUsed: boolean;
}

export interface OperationalWarning {
  id: string;
  targetId: string;
  message: string;
  resolved: boolean;
}

export type DomainCommandType =
  | 'SUBMIT_CLAIM'
  | 'WITHDRAW_CLAIM'
  | 'DELETE_DRAFT'
  | 'REVISE_CLAIM'
  | 'APPROVE_CLAIM'
  | 'REQUEST_CHANGES'
  | 'FINAL_REJECT_CLAIM'
  | 'REVOKE_APPROVAL'
  | 'SCHEDULE_PAYMENT'
  | 'COMPLETE_PAYMENT'
  | 'FAIL_PAYMENT'
  | 'HOLD_PAYMENT'
  | 'VERIFY_FAILED_PAYMENT'
  | 'RESCHEDULE_PAYMENT'
  | 'REOPEN_HOLD'
  | 'CREATE_ADJUSTMENT'
  | 'COMPLETE_ADJUSTMENT'
  | 'FAIL_ADJUSTMENT'
  | 'RESOLVE_ADJUSTMENT';

export interface DomainCommand {
  type: DomainCommandType;
  actorId: string;
  targetId: string;
  expectedVersion: number;
  idempotencyKey: string;
  input: Record<string, unknown>;
}

export interface CommandOutcome {
  status: 'committed' | 'rejected';
  code: string;
  message: string;
  targetVersion: number;
  preservedInput?: Record<string, unknown>;
}

export interface CommandResult {
  state: DomainState;
  outcome: CommandOutcome;
  auditEventIds: string[];
  deliveryEventIds: string[];
  changedFields: string[];
}

export interface IdempotencyRecord {
  fingerprint: string;
  outcome: CommandOutcome;
  auditEventIds: string[];
  deliveryEventIds: string[];
  changedFields: string[];
}

export interface DomainState {
  schemaVersion: 1;
  canonicalRevision: 55;
  canonicalDigest: string;
  now: string;
  users: Record<string, User>;
  claims: Record<string, Claim>;
  adjustments: Record<string, Adjustment>;
  categories: Record<string, Category>;
  invitations: Record<string, Invitation>;
  auditEvents: AuditEvent[];
  deliveries: DeliveryEvent[];
  warnings: OperationalWarning[];
  idempotency: Record<string, IdempotencyRecord>;
  nextSequence: number;
}
