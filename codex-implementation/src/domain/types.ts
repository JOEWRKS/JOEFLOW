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
  email?: string;
  roles: Role[];
  managerId?: string;
  active: boolean;
  authVersion: number;
  version: number;
}

export interface ClaimRevision {
  number: number;
  submittedAt?: string;
  managerIdSnapshot?: string;
  merchant: string;
  categoryId: string;
  categoryNameSnapshot: string;
  expenseDate: string;
  currency: string;
  originalAmount: number;
  krwAmount: number;
  businessPurpose: string;
  exchangeRate?: number;
  exchangeEvidenceIds?: string[];
  duplicateReason?: string;
  lateReason?: string;
  comment?: string;
  receiptIds: string[];
}

export interface FileRecord {
  id: string;
  claimId: string;
  name: string;
  mime: 'image/jpeg' | 'image/png' | 'application/pdf';
  sizeBytes: number;
  sha256: string;
  purpose: 'RECEIPT' | 'FX_EVIDENCE' | 'PAYMENT_EVIDENCE';
  evidenceType?: 'CARD_STATEMENT' | 'BANK_EXCHANGE_RECORD' | 'OFFICIAL_RATE_CAPTURE' | 'OFFICIAL_RATE_PDF';
  source: 'camera' | 'file';
  scanStatus: 'Scanning' | 'Linked' | 'Failed and discarded';
  scanAttempts?: number;
  nextScanRetryAt?: string;
}

export interface FileGrant {
  id: string;
  actorId: string;
  fileId: string;
  issuedAt: string;
  expiresAt: string;
  version: number;
  lastAccessedAt?: string;
}

export interface PaymentRecord {
  ownerId?: string;
  scheduledDate?: string;
  actualDate?: string;
  method?: 'Bank transfer' | 'Corporate card settlement' | 'Cash' | 'Other';
  methodDescription?: string;
  externalReference?: string;
  failureReason?: string;
  holdReason?: string;
  holdExternalExecutionPossible?: boolean;
  overdue?: boolean;
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
  actualAmountKrw?: number;
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
  legalHold?: { reason: string; setBy: string; setAt: string };
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
  targetVersion?: number;
  revision?: number;
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
  result?: 'COMMITTED' | 'DENIED' | 'SUCCESS' | 'ERROR' | 'SKIPPED_LEGAL_HOLD';
  scopeSnapshot?: string;
  rowCount?: number;
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
  version: number;
  uniqueKey?: string;
  nextRetryAt?: string;
}

export interface OperationalWarning {
  id: string;
  targetId: string;
  message: string;
  resolved: boolean;
}

export type DomainCommandType =
  | 'CREATE_DRAFT'
  | 'SUBMIT_CLAIM'
  | 'UPDATE_DRAFT'
  | 'LINK_ATTACHMENT'
  | 'RETRY_ATTACHMENT_SCAN'
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
  | 'RESOLVE_ADJUSTMENT'
  | 'VERIFY_HELD_PAYMENT'
  | 'ISSUE_INVITATION'
  | 'REISSUE_INVITATION'
  | 'REVOKE_INVITATION'
  | 'ACCEPT_INVITATION'
  | 'EXPIRE_INVITATIONS'
  | 'UPDATE_ACCOUNT'
  | 'ASSIGN_MANAGER'
  | 'CREATE_CATEGORY'
  | 'UPDATE_CATEGORY'
  | 'SET_LEGAL_HOLD'
  | 'RELEASE_LEGAL_HOLD'
  | 'REASSIGN_MANAGER'
  | 'REASSIGN_FINANCE'
  | 'RETRY_DELIVERY'
  | 'EXPORT_CSV'
  | 'DOWNLOAD_EXPORT'
  | 'ISSUE_FILE_ACCESS'
  | 'DOWNLOAD_FILE'
  | 'RUN_DAILY_OPERATIONS'
  | 'RUN_DELIVERY_RETRIES';

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
  latestValues?: Record<string, unknown>;
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
  files: Record<string, FileRecord>;
  fileGrants: FileGrant[];
  adjustments: Record<string, Adjustment>;
  categories: Record<string, Category>;
  invitations: Record<string, Invitation>;
  auditEvents: AuditEvent[];
  deliveries: DeliveryEvent[];
  warnings: OperationalWarning[];
  exports: Array<{ id: string; actorId: string; createdAt: string; rowCount: number; claimIds: string[]; columns: string[]; filterSnapshot: string; csv: string; downloadedAt?: string; version: number }>;
  idempotency: Record<string, IdempotencyRecord>;
  nextSequence: number;
}
