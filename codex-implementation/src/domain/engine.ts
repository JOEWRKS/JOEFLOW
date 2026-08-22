import { commandFingerprint } from './commands';
import { claimsForRole } from './selectors';
import type { Adjustment, AuditEvent, Claim, CommandOutcome, CommandResult, DeliveryEvent, DomainCommand, DomainState, Role } from './types';

const REVIEW_COMMANDS = new Set(['APPROVE_CLAIM', 'REQUEST_CHANGES', 'FINAL_REJECT_CLAIM', 'REVOKE_APPROVAL']);
const FINANCE_COMMANDS = new Set([
  'SCHEDULE_PAYMENT', 'COMPLETE_PAYMENT', 'FAIL_PAYMENT', 'HOLD_PAYMENT', 'VERIFY_FAILED_PAYMENT',
  'VERIFY_HELD_PAYMENT', 'RESCHEDULE_PAYMENT', 'CREATE_ADJUSTMENT', 'COMPLETE_ADJUSTMENT', 'FAIL_ADJUSTMENT', 'RESOLVE_ADJUSTMENT',
]);
const EMPLOYEE_COMMANDS = new Set(['UPDATE_DRAFT', 'LINK_ATTACHMENT', 'RETRY_ATTACHMENT_SCAN', 'SUBMIT_CLAIM', 'WITHDRAW_CLAIM', 'DELETE_DRAFT', 'REVISE_CLAIM']);
const ADMIN_COMMANDS = new Set([
  'ISSUE_INVITATION', 'REISSUE_INVITATION', 'REVOKE_INVITATION', 'EXPIRE_INVITATIONS', 'UPDATE_ACCOUNT', 'ASSIGN_MANAGER',
  'CREATE_CATEGORY', 'UPDATE_CATEGORY', 'SET_LEGAL_HOLD', 'RELEASE_LEGAL_HOLD', 'REASSIGN_MANAGER', 'REASSIGN_FINANCE', 'REOPEN_HOLD',
  'RETRY_DELIVERY', 'EXPORT_CSV', 'DOWNLOAD_EXPORT', 'RUN_DAILY_OPERATIONS', 'RUN_DELIVERY_RETRIES',
]);

function hasRole(state: DomainState, actorId: string, role: Role): boolean {
  const user = state.users[actorId];
  return Boolean(user?.active && user.roles.includes(role));
}

function rejected(state: DomainState, command: DomainCommand, code: string, message: string, targetVersion: number): CommandResult {
  return {
    state,
    outcome: { status: 'rejected', code, message, targetVersion, preservedInput: structuredClone(command.input) },
    auditEventIds: [],
    deliveryEventIds: [],
    changedFields: [],
  };
}

function nextId(state: DomainState, prefix: string): string {
  const id = `${prefix}-${String(state.nextSequence).padStart(4, '0')}`;
  state.nextSequence += 1;
  return id;
}

function queueDelivery(state: DomainState, targetId: string, recipientId: string, template: string, uniqueBase?: string): string[] {
  const ids: string[] = [];
  for (const channel of ['APP', 'EMAIL'] as const) {
    const uniqueKey = uniqueBase ? `${uniqueBase}:${channel}` : undefined;
    if (uniqueKey && state.deliveries.some((item) => item.uniqueKey === uniqueKey)) continue;
    const event: DeliveryEvent = {
      id: nextId(state, 'delivery'), targetId, channel, recipientId, template,
      status: 'Queued', attempts: 0, manualRetryUsed: false, version: 1, uniqueKey,
    };
    state.deliveries.push(event);
    ids.push(event.id);
  }
  return ids;
}

function commit(
  state: DomainState,
  command: DomainCommand,
  changedFields: string[],
  message: string,
  recipients: string[] = [],
  reason?: string,
): CommandResult {
  const claim = state.claims[command.targetId];
  if (claim) {
    claim.version += 1;
    claim.updatedAt = state.now;
  }
  const audit: AuditEvent = {
    id: nextId(state, 'audit'), actorId: command.actorId, targetId: command.targetId,
    action: command.type, at: state.now, changedFields, reason,
  };
  state.auditEvents.push(audit);
  const deliveryEventIds = recipients.flatMap((recipientId) => queueDelivery(state, command.targetId, recipientId, command.type));
  const outcome: CommandOutcome = {
    status: 'committed', code: 'COMMITTED', message,
    targetVersion: claim?.version ?? command.expectedVersion + 1,
  };
  return { state, outcome, auditEventIds: [audit.id], deliveryEventIds, changedFields };
}

function ensureAccess(state: DomainState, command: DomainCommand, claim: Claim): CommandResult | undefined {
  if (EMPLOYEE_COMMANDS.has(command.type)) {
    if (!hasRole(state, command.actorId, 'EMPLOYEE') || claim.employeeId !== command.actorId) {
      return rejected(state, command, 'FORBIDDEN', 'Only the owning employee can perform this action.', claim.version);
    }
  }
  if (REVIEW_COMMANDS.has(command.type)) {
    if (!hasRole(state, command.actorId, 'MANAGER') || claim.managerId !== command.actorId) {
      return rejected(state, command, 'FORBIDDEN', 'Only the currently assigned manager can review this claim.', claim.version);
    }
    if (claim.employeeId === command.actorId) {
      return rejected(state, command, 'SELF_APPROVAL_DENIED', 'A manager cannot review their own claim.', claim.version);
    }
  }
  if (FINANCE_COMMANDS.has(command.type) && !hasRole(state, command.actorId, 'FINANCE')) {
    return rejected(state, command, 'FORBIDDEN', 'Finance role is required.', claim.version);
  }
  return undefined;
}

function requireRevision(state: DomainState, command: DomainCommand, claim: Claim): CommandResult | undefined {
  if (!REVIEW_COMMANDS.has(command.type)) return undefined;
  if (command.input.revision !== claim.currentRevision) {
    return rejected(state, command, 'REVISION_MISMATCH', 'Review actions must target the latest visible revision.', claim.version);
  }
  return undefined;
}

function text(input: Record<string, unknown>, key: string): string {
  return typeof input[key] === 'string' ? input[key].trim() : '';
}

function paymentOwnerDenied(state: DomainState, command: DomainCommand, claim: Claim): CommandResult | undefined {
  if (claim.payment.ownerId && claim.payment.ownerId !== command.actorId) {
    return rejected(state, command, 'PAYMENT_OWNER_REQUIRED', 'Only the Finance owner who claimed this payment can change it.', claim.version);
  }
  return undefined;
}

function referenceExists(state: DomainState, reference: string, adjustmentId?: string): boolean {
  return Object.values(state.claims).some((item) => item.payment.externalReference === reference)
    || Object.values(state.adjustments).some((item) => item.id !== adjustmentId && item.externalReference === reference);
}

function financeTransition(state: DomainState, command: DomainCommand, claim: Claim): CommandResult {
  const today = state.now.slice(0, 10);
  const ownerDenied = paymentOwnerDenied(state, command, claim);
  const adjustmentId = text(command.input, 'adjustmentId');
  const adjustment = adjustmentId ? state.adjustments[adjustmentId] : undefined;

  switch (command.type) {
    case 'SCHEDULE_PAYMENT': {
      if (claim.status !== 'Payment pending') return rejected(state, command, 'INVALID_STATUS', 'Only Payment pending claims can be scheduled.', claim.version);
      if (claim.payment.ownerId && claim.payment.ownerId !== command.actorId) return rejected(state, command, 'PAYMENT_ALREADY_CLAIMED', 'Another Finance user already owns this payment.', claim.version);
      const scheduledDate = text(command.input, 'scheduledDate');
      if (!scheduledDate || scheduledDate < today) return rejected(state, command, 'INVALID_SCHEDULED_DATE', 'Scheduled date must be today or later.', claim.version);
      claim.payment.ownerId = command.actorId;
      claim.payment.scheduledDate = scheduledDate;
      claim.status = 'Scheduled';
      return commit(state, command, ['payment.ownerId', 'payment.scheduledDate', 'status'], 'Payment claimed and scheduled.', [claim.employeeId]);
    }
    case 'COMPLETE_PAYMENT': {
      if (claim.status !== 'Scheduled') return rejected(state, command, 'INVALID_STATUS', 'Only Scheduled payments can be completed.', claim.version);
      if (ownerDenied) return ownerDenied;
      const actualDate = text(command.input, 'actualDate');
      const approvalDate = claim.approvedAt?.slice(0, 10) ?? '';
      if (!actualDate || actualDate > today || actualDate < approvalDate) return rejected(state, command, 'INVALID_ACTUAL_DATE', 'Actual payment date must be between approval and today.', claim.version);
      const method = text(command.input, 'method');
      if (!['Bank transfer', 'Corporate card settlement', 'Cash', 'Other'].includes(method)) return rejected(state, command, 'PAYMENT_METHOD_REQUIRED', 'A supported payment method is required.', claim.version);
      if (method === 'Other' && !text(command.input, 'methodDescription')) return rejected(state, command, 'METHOD_DESCRIPTION_REQUIRED', 'Other payment method requires a description.', claim.version);
      const externalReference = text(command.input, 'externalReference');
      if (!externalReference) return rejected(state, command, 'REFERENCE_REQUIRED', 'External payment reference is required.', claim.version);
      if (referenceExists(state, externalReference)) return rejected(state, command, 'DUPLICATE_REFERENCE', 'External payment reference must be unique.', claim.version);
      claim.payment.actualDate = actualDate;
      claim.payment.method = method as NonNullable<Claim['payment']['method']>;
      claim.payment.methodDescription = text(command.input, 'methodDescription') || undefined;
      claim.payment.externalReference = externalReference;
      claim.status = 'Payment completed';
      return commit(state, command, ['payment.actualDate', 'payment.method', 'payment.externalReference', 'status'], 'Payment completed.', [claim.employeeId]);
    }
    case 'FAIL_PAYMENT': {
      if (claim.status !== 'Scheduled') return rejected(state, command, 'INVALID_STATUS', 'Only Scheduled payments can fail.', claim.version);
      if (ownerDenied) return ownerDenied;
      const reason = text(command.input, 'reason');
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Payment failure reason is required.', claim.version);
      claim.payment.failureReason = reason;
      claim.payment.verification = undefined;
      claim.status = 'Payment failed';
      return commit(state, command, ['payment.failureReason', 'status'], 'Payment failure recorded.', [claim.employeeId], reason);
    }
    case 'HOLD_PAYMENT': {
      if (claim.status !== 'Scheduled') return rejected(state, command, 'INVALID_STATUS', 'Only a Scheduled payment can be placed on hold.', claim.version);
      if (ownerDenied) return ownerDenied;
      const reason = text(command.input, 'reason');
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Payment hold reason is required.', claim.version);
      claim.payment.ownerId ||= command.actorId;
      claim.payment.holdReason = reason;
      claim.payment.holdExternalExecutionPossible = command.input.externalExecutionPossible === true;
      claim.payment.verification = undefined;
      claim.status = 'Payment hold';
      return commit(state, command, ['payment.ownerId', 'payment.holdReason', 'payment.holdExternalExecutionPossible', 'status'], 'Payment placed on hold.', [claim.employeeId], reason);
    }
    case 'VERIFY_FAILED_PAYMENT': {
      if (claim.status !== 'Payment failed') return rejected(state, command, 'INVALID_STATUS', 'Verification is available only for failed payments.', claim.version);
      if (ownerDenied) return ownerDenied;
      const result = text(command.input, 'result');
      const required = ['channel', 'maskedAccount', 'checkedFrom', 'checkedTo', 'externalReferenceOrResult', 'conclusion'];
      if (!['Not paid', 'Paid', 'Unclear'].includes(result) || required.some((key) => !text(command.input, key))) {
        return rejected(state, command, 'STRUCTURED_VERIFICATION_REQUIRED', 'All duplicate-payment verification fields are required.', claim.version);
      }
      claim.payment.verification = {
        result: result as 'Not paid' | 'Paid' | 'Unclear',
        channel: text(command.input, 'channel'), maskedAccount: text(command.input, 'maskedAccount'),
        checkedFrom: text(command.input, 'checkedFrom'), checkedTo: text(command.input, 'checkedTo'),
        externalReferenceOrResult: text(command.input, 'externalReferenceOrResult'), conclusion: text(command.input, 'conclusion'),
        checkedBy: command.actorId, checkedAt: state.now,
      };
      return commit(state, command, ['payment.verification'], 'Payment execution verification recorded.');
    }
    case 'VERIFY_HELD_PAYMENT': {
      if (claim.status !== 'Payment hold') return rejected(state, command, 'INVALID_STATUS', 'Verification is available only for held payments.', claim.version);
      if (ownerDenied) return ownerDenied;
      const result = text(command.input, 'result');
      const required = ['channel', 'maskedAccount', 'checkedFrom', 'checkedTo', 'externalReferenceOrResult', 'conclusion'];
      if (!['Not paid', 'Paid', 'Unclear'].includes(result) || required.some((key) => !text(command.input, key))) {
        return rejected(state, command, 'STRUCTURED_VERIFICATION_REQUIRED', 'All duplicate-payment verification fields are required.', claim.version);
      }
      claim.payment.verification = {
        result: result as 'Not paid' | 'Paid' | 'Unclear',
        channel: text(command.input, 'channel'), maskedAccount: text(command.input, 'maskedAccount'),
        checkedFrom: text(command.input, 'checkedFrom'), checkedTo: text(command.input, 'checkedTo'),
        externalReferenceOrResult: text(command.input, 'externalReferenceOrResult'), conclusion: text(command.input, 'conclusion'),
        checkedBy: command.actorId, checkedAt: state.now,
      };
      return commit(state, command, ['payment.verification'], 'Held-payment execution verification recorded.');
    }
    case 'RESCHEDULE_PAYMENT': {
      if (claim.status !== 'Payment failed') return rejected(state, command, 'INVALID_STATUS', 'Only failed payments can be rescheduled.', claim.version);
      if (ownerDenied) return ownerDenied;
      if (claim.payment.verification?.result !== 'Not paid') return rejected(state, command, 'NOT_PAID_VERIFICATION_REQUIRED', 'A Not paid conclusion is required before rescheduling.', claim.version);
      const scheduledDate = text(command.input, 'scheduledDate');
      if (!scheduledDate || scheduledDate < today) return rejected(state, command, 'INVALID_SCHEDULED_DATE', 'Scheduled date must be today or later.', claim.version);
      claim.payment.scheduledDate = scheduledDate;
      claim.payment.failureReason = undefined;
      claim.status = 'Scheduled';
      return commit(state, command, ['payment.scheduledDate', 'payment.failureReason', 'status'], 'Failed payment rescheduled.', [claim.employeeId]);
    }
    case 'CREATE_ADJUSTMENT': {
      if (claim.status !== 'Payment completed') return rejected(state, command, 'INVALID_STATUS', 'Adjustments require a completed payment.', claim.version);
      if (ownerDenied) return ownerDenied;
      const active = claim.adjustmentIds.map((id) => state.adjustments[id]).some((item) => item
        && (['In progress', 'Needs verification'].includes(item.status) || (item.status === 'Failed' && !item.verification)));
      if (active) return rejected(state, command, 'ACTIVE_ADJUSTMENT_EXISTS', 'Only one adjustment may be active at a time.', claim.version);
      const kind = text(command.input, 'kind');
      const amountKrw = Number(command.input.amountKrw);
      const reason = text(command.input, 'reason');
      if (!['Recovery', 'Additional payment'].includes(kind) || !Number.isFinite(amountKrw) || amountKrw <= 0 || !reason) {
        return rejected(state, command, 'INVALID_ADJUSTMENT', 'Kind, positive KRW amount, and reason are required.', claim.version);
      }
      const id = nextId(state, 'adjustment');
      const item: Adjustment = { id, claimId: claim.id, kind: kind as Adjustment['kind'], amountKrw, status: 'In progress', reason, version: 1 };
      state.adjustments[id] = item;
      claim.adjustmentIds.push(id);
      return commit(state, command, ['adjustmentIds'], 'Adjustment created.');
    }
    case 'COMPLETE_ADJUSTMENT': {
      if (ownerDenied) return ownerDenied;
      if (!adjustment || adjustment.claimId !== claim.id) return rejected(state, command, 'ADJUSTMENT_NOT_FOUND', 'Adjustment not found.', claim.version);
      if (adjustment.status !== 'In progress') return rejected(state, command, 'INVALID_ADJUSTMENT_STATUS', 'Only an In progress adjustment can be completed.', claim.version);
      const actualDate = text(command.input, 'actualDate');
      const externalReference = text(command.input, 'externalReference');
      if (!actualDate || actualDate > today || actualDate < (claim.approvedAt?.slice(0, 10) ?? '')) return rejected(state, command, 'INVALID_ACTUAL_DATE', 'Adjustment date must be between approval and today.', claim.version);
      if (!externalReference) return rejected(state, command, 'REFERENCE_REQUIRED', 'External adjustment reference is required.', claim.version);
      if (referenceExists(state, externalReference, adjustment.id)) return rejected(state, command, 'DUPLICATE_REFERENCE', 'External reference must be unique.', claim.version);
      adjustment.status = 'Completed';
      adjustment.actualAmountKrw = adjustment.amountKrw;
      adjustment.actualDate = actualDate;
      adjustment.externalReference = externalReference;
      adjustment.version += 1;
      return commit(state, command, ['adjustment.status', 'adjustment.actualDate', 'adjustment.externalReference'], 'Adjustment completed.', [claim.employeeId]);
    }
    case 'FAIL_ADJUSTMENT': {
      if (ownerDenied) return ownerDenied;
      if (!adjustment || adjustment.claimId !== claim.id) return rejected(state, command, 'ADJUSTMENT_NOT_FOUND', 'Adjustment not found.', claim.version);
      if (adjustment.status !== 'In progress') return rejected(state, command, 'INVALID_ADJUSTMENT_STATUS', 'Only an In progress adjustment can fail.', claim.version);
      const reason = text(command.input, 'reason');
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Adjustment failure reason is required.', claim.version);
      adjustment.status = 'Failed';
      adjustment.reason = `${adjustment.reason} · Failure: ${reason}`;
      adjustment.version += 1;
      return commit(state, command, ['adjustment.status', 'adjustment.reason'], 'Adjustment failure recorded.', [claim.employeeId], reason);
    }
    case 'RESOLVE_ADJUSTMENT': {
      if (ownerDenied) return ownerDenied;
      if (!adjustment || adjustment.claimId !== claim.id) return rejected(state, command, 'ADJUSTMENT_NOT_FOUND', 'Adjustment not found.', claim.version);
      if (!['Failed', 'Needs verification'].includes(adjustment.status)) return rejected(state, command, 'INVALID_ADJUSTMENT_STATUS', 'Only a failed or uncertain adjustment can be resolved.', claim.version);
      const result = text(command.input, 'result');
      const note = text(command.input, 'note');
      if (!['Not executed', 'Executed', 'Unclear'].includes(result) || !note) return rejected(state, command, 'STRUCTURED_VERIFICATION_REQUIRED', 'Execution result and note are required.', claim.version);
      adjustment.verification = { result: result as 'Not executed' | 'Executed' | 'Unclear', note, checkedBy: command.actorId, checkedAt: state.now };
      if (result === 'Unclear') {
        adjustment.status = 'Needs verification';
      } else if (result === 'Executed') {
        const actualDate = text(command.input, 'actualDate');
        const externalReference = text(command.input, 'externalReference');
        const actualAmountKrw = Number(command.input.actualAmountKrw);
        const approvalDate = claim.approvedAt?.slice(0, 10) ?? '';
        if (!Number.isFinite(actualAmountKrw) || actualAmountKrw <= 0 || !actualDate || actualDate < approvalDate || actualDate > today
          || !externalReference || referenceExists(state, externalReference, adjustment.id)) {
          return rejected(state, command, 'COMPLETION_EVIDENCE_REQUIRED', 'Executed requires a positive actual amount, bounded date, and unique external reference.', claim.version);
        }
        adjustment.status = 'Completed';
        adjustment.actualAmountKrw = actualAmountKrw;
        adjustment.actualDate = actualDate;
        adjustment.externalReference = externalReference;
      } else {
        adjustment.status = 'Cancelled';
        const replacementId = nextId(state, 'adjustment');
        state.adjustments[replacementId] = {
          id: replacementId, claimId: claim.id, kind: adjustment.kind, amountKrw: adjustment.amountKrw,
          status: 'In progress', reason: `Replacement for ${adjustment.id}: ${adjustment.reason}`,
          replacesAdjustmentId: adjustment.id, version: 1,
        };
        claim.adjustmentIds.push(replacementId);
      }
      adjustment.version += 1;
      return commit(state, command, ['adjustment.verification', 'adjustment.status', 'adjustmentIds'], 'Adjustment verification resolved.');
    }
    default:
      return rejected(state, command, 'UNSUPPORTED_COMMAND', 'This Finance command is not implemented yet.', claim.version);
  }
}

function daysBetween(start: string, end: string): number {
  return Math.floor((Date.parse(`${end}T00:00:00Z`) - Date.parse(`${start}T00:00:00Z`)) / 86_400_000);
}

function validateSubmission(state: DomainState, command: DomainCommand, claim: Claim): CommandResult | undefined {
  const current = claim.revisions.at(-1)!;
  if (Object.values(state.files).some((file) => file.claimId === claim.id && file.scanStatus === 'Scanning')) {
    return rejected(state, command, 'SCAN_PENDING', 'Submission is blocked while attachment scanning remains unresolved.', claim.version);
  }
  const currentManagerId = state.users[claim.employeeId]?.managerId;
  if (!currentManagerId || !state.users[currentManagerId]?.active || !state.users[currentManagerId]?.roles.includes('MANAGER') || currentManagerId === claim.employeeId) {
    return rejected(state, command, 'MANAGER_REQUIRED', 'An active direct manager other than the employee is required.', claim.version);
  }
  if (!current.expenseDate || !current.merchant.trim() || current.originalAmount <= 0 || !current.currency || !current.businessPurpose.trim()) {
    return rejected(state, command, 'REQUIRED_FIELDS', 'Expense date, merchant, amount, currency, and business purpose are required.', claim.version);
  }
  if (current.expenseDate > state.now.slice(0, 10)) return rejected(state, command, 'FUTURE_EXPENSE_DATE', 'Future expense dates cannot be submitted.', claim.version);
  if (daysBetween(current.expenseDate, state.now.slice(0, 10)) > 90 && !current.lateReason?.trim()) {
    return rejected(state, command, 'LATE_REASON_REQUIRED', 'Expenses older than 90 days require a reason.', claim.version);
  }
  if (!state.categories[current.categoryId]?.active) return rejected(state, command, 'ACTIVE_CATEGORY_REQUIRED', 'Select an active expense category.', claim.version);
  const receipts = current.receiptIds.map((id) => state.files[id]);
  if (!receipts.length || receipts.some((file) => !file || file.scanStatus !== 'Linked')) {
    return rejected(state, command, 'CLEAN_RECEIPT_REQUIRED', 'At least one clean linked receipt is required.', claim.version);
  }
  const receiptHashes = new Set(receipts.map((file) => file.sha256));
  const exactDuplicate = Object.values(state.claims).some((item) => item.id !== claim.id && item.revisions.some((itemRevision) => itemRevision.receiptIds.some((fileId) => {
    const file = state.files[fileId];
    return Boolean(file?.sha256 && receiptHashes.has(file.sha256));
  })));
  if (exactDuplicate) return rejected(state, command, 'DUPLICATE_RECEIPT', 'This receipt has already been retained for another company claim.', claim.version);
  if (current.currency !== 'KRW') {
    const exchangeRate = current.exchangeRate ?? 0;
    const calculated = Math.round(current.originalAmount * exchangeRate);
    if (exchangeRate <= 0 || Math.abs(calculated - current.krwAmount) > 1) return rejected(state, command, 'FX_CONVERSION_INVALID', 'KRW conversion must equal amount × rate within ±1 KRW.', claim.version);
    const evidence = (current.exchangeEvidenceIds ?? []).map((id) => state.files[id]);
    if (!evidence.length || evidence.some((file) => !file || file.scanStatus !== 'Linked')) return rejected(state, command, 'FX_EVIDENCE_REQUIRED', 'Foreign-currency claims require clean linked FX evidence.', claim.version);
  }
  const duplicate = Object.values(state.claims).some((item) => item.id !== claim.id && item.employeeId === claim.employeeId && item.status !== 'Draft'
    && item.revisions.at(-1)?.merchant === current.merchant
    && item.revisions.at(-1)?.expenseDate === current.expenseDate
    && item.revisions.at(-1)?.currency === current.currency
    && item.revisions.at(-1)?.originalAmount === current.originalAmount);
  if (duplicate && !current.duplicateReason?.trim()) return rejected(state, command, 'DUPLICATE_REASON_REQUIRED', 'A likely duplicate requires a reason before submission.', claim.version);
  return undefined;
}

function adminVersion(state: DomainState, command: DomainCommand): number {
  return state.invitations[command.targetId]?.version
    ?? state.users[command.targetId]?.version
    ?? state.categories[command.targetId]?.version
    ?? state.deliveries.find((item) => item.id === command.targetId)?.version
    ?? state.claims[command.targetId]?.version
    ?? state.exports.find((item) => item.id === command.targetId)?.version
    ?? 0;
}

function adminTransition(state: DomainState, command: DomainCommand): CommandResult {
  if (!hasRole(state, command.actorId, 'ADMIN') && !(['EXPORT_CSV', 'DOWNLOAD_EXPORT'].includes(command.type) && hasRole(state, command.actorId, 'FINANCE'))) {
    return rejected(state, command, 'FORBIDDEN', 'Admin role is required.', adminVersion(state, command));
  }
  const currentVersion = adminVersion(state, command);
  if (currentVersion !== command.expectedVersion) return rejected(state, command, 'STALE_VERSION', 'The governed record changed. Review the latest state and retry.', currentVersion);
  const reason = text(command.input, 'reason');

  switch (command.type) {
    case 'ISSUE_INVITATION': {
      const email = text(command.input, 'email').toLowerCase();
      const roles = Array.isArray(command.input.roles) ? command.input.roles.filter((role): role is Role => ['EMPLOYEE', 'MANAGER', 'FINANCE', 'ADMIN'].includes(String(role))) : [];
      if (!/^\S+@\S+\.\S+$/.test(email) || !roles.length) return rejected(state, command, 'INVALID_INVITATION', 'A valid email and at least one role are required.', currentVersion);
      if (Object.values(state.invitations).some((item) => item.email === email && item.status === 'Pending')) return rejected(state, command, 'PENDING_INVITATION_EXISTS', 'A pending invitation already exists; reissue it instead.', currentVersion);
      const id = nextId(state, 'invitation');
      const expiresDate = new Date(Date.parse(state.now) + 7 * 86_400_000).toISOString().slice(0, 10);
      state.invitations[id] = { id, email, roles, managerId: text(command.input, 'managerId') || undefined, status: 'Pending', expiresAt: `${expiresDate}T09:00:00+09:00`, version: 1 };
      return commit(state, { ...command, targetId: id }, ['invitation'], 'Invitation issued.', [email]);
    }
    case 'REISSUE_INVITATION': {
      const prior = state.invitations[command.targetId];
      if (!prior || prior.status === 'Accepted' || prior.status === 'Revoked') return rejected(state, command, 'INVALID_INVITATION_STATUS', 'Only an unaccepted, non-revoked invitation can be reissued.', currentVersion);
      for (const item of Object.values(state.invitations)) {
        if (item.email === prior.email && item.status === 'Pending') { item.status = 'Expired'; item.version += 1; }
      }
      const id = nextId(state, 'invitation');
      const expiresDate = new Date(Date.parse(state.now) + 7 * 86_400_000).toISOString().slice(0, 10);
      state.invitations[id] = { ...structuredClone(prior), id, status: 'Pending', expiresAt: `${expiresDate}T09:00:00+09:00`, version: 1 };
      return commit(state, { ...command, targetId: id }, ['prior.status', 'invitation'], 'Invitation reissued; prior links invalidated.', [prior.email]);
    }
    case 'REVOKE_INVITATION': {
      const invitation = state.invitations[command.targetId];
      if (!invitation || invitation.status !== 'Pending') return rejected(state, command, 'INVALID_INVITATION_STATUS', 'Only a Pending invitation can be revoked.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Invitation revocation reason is required.', currentVersion);
      invitation.status = 'Revoked';
      invitation.version += 1;
      return commit(state, command, ['invitation.status'], 'Invitation revoked.', [], reason);
    }
    case 'EXPIRE_INVITATIONS': {
      const expired = Object.values(state.invitations).filter((item) => item.status === 'Pending' && Date.parse(item.expiresAt) <= Date.parse(state.now));
      for (const invitation of expired) {
        invitation.status = 'Expired';
        invitation.version += 1;
      }
      return commit(state, command, ['invitations.status'], `${expired.length} expired invitation(s) invalidated.`);
    }
    case 'UPDATE_ACCOUNT': {
      const user = state.users[command.targetId];
      if (!user) return rejected(state, command, 'NOT_FOUND', 'User not found.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Account or role changes require a reason.', currentVersion);
      const active = typeof command.input.active === 'boolean' ? command.input.active : user.active;
      const roles = Array.isArray(command.input.roles) ? command.input.roles.filter((role): role is Role => ['EMPLOYEE', 'MANAGER', 'FINANCE', 'ADMIN'].includes(String(role))) : user.roles;
      if (!roles.length) return rejected(state, command, 'ROLE_REQUIRED', 'At least one role is required.', currentVersion);
      if (user.roles.includes('ADMIN') && (!active || !roles.includes('ADMIN'))) {
        const activeAdmins = Object.values(state.users).filter((item) => item.active && item.roles.includes('ADMIN'));
        if (activeAdmins.length === 1) return rejected(state, command, 'LAST_ADMIN_GUARD', 'The last active Admin cannot be removed or deactivated.', currentVersion);
      }
      user.active = active;
      user.roles = roles;
      user.authVersion += 1;
      user.version += 1;
      return commit(state, command, ['user.active', 'user.roles', 'user.authVersion'], 'Account and roles updated; active sessions invalidated.', [], reason);
    }
    case 'ASSIGN_MANAGER': {
      const employee = state.users[command.targetId];
      const managerId = text(command.input, 'managerId');
      const manager = state.users[managerId];
      if (!employee || !manager?.active || !manager.roles.includes('MANAGER') || employee.id === managerId) return rejected(state, command, 'INVALID_MANAGER', 'Select a different active Manager.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Manager assignment requires a reason.', currentVersion);
      employee.managerId = managerId;
      employee.version += 1;
      return commit(state, command, ['user.managerId'], 'Direct manager updated for future submissions.', [employee.id, managerId], reason);
    }
    case 'CREATE_CATEGORY': {
      const name = text(command.input, 'name');
      if (!name || !reason) return rejected(state, command, 'CATEGORY_DETAILS_REQUIRED', 'Category name and reason are required.', currentVersion);
      if (Object.values(state.categories).some((item) => item.name.toLowerCase() === name.toLowerCase())) {
        return rejected(state, command, 'CATEGORY_NAME_EXISTS', 'Category names must be unique.', currentVersion);
      }
      const nextNumber = Math.max(0, ...Object.keys(state.categories).map((id) => Number(id.match(/(\d+)$/)?.[1] ?? 0))) + 1;
      const id = `CAT-${String(nextNumber).padStart(3, '0')}`;
      state.categories[id] = { id, name, active: true, version: 1 };
      return commit(state, { ...command, targetId: id }, ['category'], 'Active category created.', [], reason);
    }
    case 'UPDATE_CATEGORY': {
      const category = state.categories[command.targetId];
      if (!category) return rejected(state, command, 'NOT_FOUND', 'Category not found.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Category changes require a reason.', currentVersion);
      const active = typeof command.input.active === 'boolean' ? command.input.active : category.active;
      const name = text(command.input, 'name') || category.name;
      category.name = name;
      category.active = active;
      category.version += 1;
      return commit(state, command, ['category.name', 'category.active'], 'Category updated; historical revision snapshots are unchanged.', [], reason);
    }
    case 'SET_LEGAL_HOLD': {
      const claim = state.claims[command.targetId];
      if (!claim) return rejected(state, command, 'NOT_FOUND', 'Claim not found.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Legal hold reason is required.', currentVersion);
      if (claim.legalHold) return rejected(state, command, 'LEGAL_HOLD_EXISTS', 'This claim is already held.', currentVersion);
      claim.legalHold = { reason, setBy: command.actorId, setAt: state.now };
      return commit(state, command, ['legalHold'], 'Legal hold set across claim, revisions, files, and audit.', [], reason);
    }
    case 'RELEASE_LEGAL_HOLD': {
      const claim = state.claims[command.targetId];
      if (!claim?.legalHold) return rejected(state, command, 'LEGAL_HOLD_NOT_FOUND', 'This claim has no legal hold.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Legal hold release reason is required.', currentVersion);
      delete claim.legalHold;
      return commit(state, command, ['legalHold'], 'Legal hold released for the next governed deletion cycle.', [], reason);
    }
    case 'REASSIGN_MANAGER': {
      const claim = state.claims[command.targetId];
      const managerId = text(command.input, 'managerId');
      const manager = state.users[managerId];
      if (!claim || !manager?.active || !manager.roles.includes('MANAGER') || claim.employeeId === managerId) return rejected(state, command, 'INVALID_MANAGER', 'Select a valid different Manager.', currentVersion);
      if (state.users[claim.managerId]?.active) return rejected(state, command, 'CURRENT_MANAGER_ACTIVE', 'Reassignment is reserved for a manager who can no longer process the revision.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Reassignment reason is required.', currentVersion);
      const oldManager = claim.managerId;
      claim.managerId = managerId;
      return commit(state, command, ['managerId'], 'Manager review authority reassigned; prior comments preserved.', [oldManager, managerId, claim.employeeId], reason);
    }
    case 'REASSIGN_FINANCE': {
      const claim = state.claims[command.targetId];
      const financeId = text(command.input, 'financeId');
      const finance = state.users[financeId];
      if (!claim || !finance?.active || !finance.roles.includes('FINANCE') || !claim.payment.ownerId) return rejected(state, command, 'INVALID_FINANCE_OWNER', 'Select a valid Finance owner for claimed work.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Finance reassignment reason is required.', currentVersion);
      claim.payment.ownerId = financeId;
      return commit(state, command, ['payment.ownerId'], 'Finance owner reassigned.', [financeId], reason);
    }
    case 'REOPEN_HOLD': {
      const claim = state.claims[command.targetId];
      if (!claim || claim.status !== 'Payment hold') return rejected(state, command, 'INVALID_STATUS', 'Only a held payment can be reopened for correction.', currentVersion);
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Reopening a held payment requires a reason.', currentVersion);
      if (claim.payment.holdExternalExecutionPossible && claim.payment.verification?.result !== 'Not paid') {
        return rejected(state, command, 'NOT_PAID_VERIFICATION_REQUIRED', 'A Not paid conclusion is required when external execution may have occurred.', currentVersion);
      }
      claim.status = 'Changes requested';
      claim.approvedRevision = undefined;
      claim.approvedAt = undefined;
      claim.payment = {};
      return commit(state, command, ['status', 'approvedRevision', 'approvedAt', 'payment'], 'Held claim reopened for correction and reapproval.', [claim.employeeId], reason);
    }
    case 'RETRY_DELIVERY': {
      const delivery = state.deliveries.find((item) => item.id === command.targetId);
      if (!delivery || delivery.status !== 'Permanent failure') return rejected(state, command, 'DELIVERY_NOT_RETRYABLE', 'Only a permanent failure can be retried manually.', currentVersion);
      if (delivery.manualRetryUsed) return rejected(state, command, 'MANUAL_RETRY_USED', 'The one manual retry was already used.', currentVersion);
      delivery.status = 'Queued';
      delivery.attempts += 1;
      delivery.manualRetryUsed = true;
      delivery.version += 1;
      const warning = state.warnings.find((item) => item.targetId === delivery.id);
      if (warning) warning.resolved = true;
      return commit(state, command, ['delivery.status', 'delivery.attempts', 'delivery.manualRetryUsed', 'warning.resolved'], 'Manual delivery retry queued.');
    }
    case 'EXPORT_CSV': {
      const authorized = hasRole(state, command.actorId, 'ADMIN') ? Object.values(state.claims) : claimsForRole(state, command.actorId, 'FINANCE');
      const requestedIds = Array.isArray(command.input.claimIds) ? command.input.claimIds.map(String) : authorized.map((claim) => claim.id);
      const authorizedIds = new Set(authorized.map((claim) => claim.id));
      const rows = requestedIds.filter((id) => authorizedIds.has(id)).map((id) => state.claims[id]);
      if (rows.length > 10_000) return rejected(state, command, 'EXPORT_ROW_LIMIT', 'Current-filter export exceeds 10,000 rows.', currentVersion);
      const id = nextId(state, 'export');
      const columns = ['claimId', 'status', 'expenseDate', 'merchant', 'currency', 'krwAmount', 'category', 'assignee'];
      const csv = [columns.join(','), ...rows.map((claim) => {
        const revision = claim.revisions.at(-1)!;
        const assignee = state.users[claim.payment.ownerId ?? claim.managerId]?.name ?? '';
        return [claim.id, claim.status, revision.expenseDate, revision.merchant, revision.currency, revision.krwAmount,
          state.categories[revision.categoryId]?.name ?? revision.categoryNameSnapshot, assignee]
          .map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',');
      })].join('\r\n');
      state.exports.push({ id, actorId: command.actorId, createdAt: state.now, rowCount: rows.length, columns, filterSnapshot: text(command.input, 'filterSnapshot') || 'Current authorized scope', csv, version: 1 });
      return commit(state, { ...command, targetId: id }, ['exports'], `Export generated with ${rows.length} authorized rows.`);
    }
    case 'DOWNLOAD_EXPORT': {
      const item = state.exports.find((exportItem) => exportItem.id === command.targetId);
      if (!item || (item.actorId !== command.actorId && !hasRole(state, command.actorId, 'ADMIN'))) return rejected(state, command, 'EXPORT_NOT_FOUND', 'No authorized export is available.', currentVersion);
      item.downloadedAt = state.now;
      item.version += 1;
      return commit(state, command, ['export.downloadedAt'], 'CSV download authorized and audited.');
    }
    case 'RUN_DAILY_OPERATIONS': {
      const today = state.now.slice(0, 10);
      const deliveryEventIds: string[] = [];
      const extraAuditIds: string[] = [];
      for (const claim of Object.values(state.claims)) {
        if (claim.status === 'Scheduled' && claim.payment.scheduledDate && claim.payment.scheduledDate < today) {
          claim.payment.overdue = true;
          if (claim.payment.ownerId) deliveryEventIds.push(...queueDelivery(state, claim.id, claim.payment.ownerId, 'PAYMENT_OVERDUE', `PAYMENT_OVERDUE:${claim.id}:${today}`));
        }
        if (claim.status === 'Submitted') {
          const submitted = claim.revisions.at(-1)?.submittedAt?.slice(0, 10);
          const elapsed = submitted ? daysBetween(submitted, today) : 0;
          if (elapsed >= 3) deliveryEventIds.push(...queueDelivery(state, claim.id, claim.managerId, 'MANAGER_REVIEW_REMINDER', `MANAGER_REVIEW_REMINDER:${claim.id}:${claim.managerId}:${today}`));
          if (elapsed >= 7 && !state.warnings.some((item) => item.targetId === `review-${claim.id}` && !item.resolved)) {
            state.warnings.push({ id: nextId(state, 'warning'), targetId: `review-${claim.id}`, message: `${claim.id} has awaited Manager review for ${elapsed} calendar days.`, resolved: false });
          }
        }
        if (claim.status === 'Draft') {
          const age = daysBetween(claim.updatedAt.slice(0, 10), today);
          if (age >= 83 && age < 90) deliveryEventIds.push(...queueDelivery(state, claim.id, claim.employeeId, 'DRAFT_EXPIRY_WARNING', `DRAFT_EXPIRY_WARNING:${claim.id}`));
        }
      }
      const expired = Object.values(state.claims).filter((claim) => claim.status === 'Draft' && daysBetween(claim.updatedAt.slice(0, 10), today) >= 90);
      for (const claim of expired) {
        const audit: AuditEvent = {
          id: nextId(state, 'audit'), actorId: command.actorId, targetId: claim.id, action: command.type, at: state.now,
          changedFields: ['expiredDraft.deleted', 'files.deleted'], targetVersion: claim.version, revision: claim.currentRevision,
          before: structuredClone(claim) as unknown as Record<string, unknown>, reason: '90-day draft retention expiry',
        };
        state.auditEvents.push(audit); extraAuditIds.push(audit.id);
        for (const file of Object.values(state.files)) if (file.claimId === claim.id) delete state.files[file.id];
        delete state.claims[claim.id];
      }
      const result = commit(state, command, ['payment.overdue', 'review.reminders', 'draft.retention'], 'Daily KST operations completed.');
      result.deliveryEventIds.push(...deliveryEventIds);
      result.auditEventIds.push(...extraAuditIds);
      return result;
    }
    case 'RUN_DELIVERY_RETRIES': {
      const failedIds = Array.isArray(command.input.failedDeliveryIds) ? command.input.failedDeliveryIds.map(String) : [];
      const changed: string[] = [];
      for (const delivery of state.deliveries.filter((item) => failedIds.includes(item.id) && item.status === 'Queued')) {
        delivery.attempts += 1;
        delivery.version += 1;
        changed.push(delivery.id);
        if (delivery.attempts >= 3) {
          delivery.status = 'Permanent failure';
          delivery.nextRetryAt = undefined;
          if (!state.warnings.some((warning) => warning.targetId === delivery.id && !warning.resolved)) {
            state.warnings.push({ id: nextId(state, 'warning'), targetId: delivery.id, message: `${delivery.template} delivery permanently failed after three automatic retries.`, resolved: false });
          }
        } else {
          const minutes = delivery.attempts === 1 ? 10 : 60;
          delivery.nextRetryAt = new Date(Date.parse(state.now) + minutes * 60_000).toISOString();
        }
      }
      return commit(state, command, ['delivery.attempts', 'delivery.status', 'warnings'], `Processed ${changed.length} failed delivery result(s).`);
    }
    default:
      return rejected(state, command, 'UNSUPPORTED_COMMAND', 'This Admin command is not implemented.', currentVersion);
  }
}

function executeTransition(state: DomainState, command: DomainCommand, claim: Claim): CommandResult {
  if (FINANCE_COMMANDS.has(command.type)) return financeTransition(state, command, claim);
  const comment = typeof command.input.comment === 'string' ? command.input.comment.trim() : '';
  switch (command.type) {
    case 'UPDATE_DRAFT': {
      if (claim.status !== 'Draft') return rejected(state, command, 'INVALID_STATUS', 'Only a Draft can be edited.', claim.version);
      const current = claim.revisions.at(-1)!;
      const allowed = [
        'merchant', 'categoryId', 'expenseDate', 'currency', 'originalAmount', 'krwAmount', 'businessPurpose',
        'exchangeRate', 'duplicateReason', 'lateReason',
      ] as const;
      const changed: string[] = [];
      for (const key of allowed) {
        if (Object.hasOwn(command.input, key)) {
          const value = command.input[key];
          if (['originalAmount', 'krwAmount', 'exchangeRate'].includes(key)) {
            (current as unknown as Record<string, unknown>)[key] = Number(value);
          } else {
            (current as unknown as Record<string, unknown>)[key] = typeof value === 'string' ? value : '';
          }
          changed.push(`revision.${key}`);
        }
      }
      if (!changed.length) return rejected(state, command, 'NO_CHANGES', 'No editable draft fields were supplied.', claim.version);
      return commit(state, command, changed, 'Draft saved.');
    }
    case 'LINK_ATTACHMENT': {
      if (claim.status !== 'Draft') return rejected(state, command, 'INVALID_STATUS', 'Attachments can be linked only to a Draft.', claim.version);
      const mime = text(command.input, 'mime');
      const name = text(command.input, 'name');
      const source = text(command.input, 'source');
      const purpose = text(command.input, 'purpose');
      const sha256 = text(command.input, 'sha256');
      const sizeBytes = Number(command.input.sizeBytes);
      if (!name || !['image/jpeg', 'image/png', 'application/pdf'].includes(mime) || !['camera', 'file'].includes(source)
        || !['RECEIPT', 'FX_EVIDENCE'].includes(purpose) || !sha256 || !Number.isFinite(sizeBytes) || sizeBytes <= 0 || sizeBytes > 10 * 1024 * 1024) {
        return rejected(state, command, 'INVALID_ATTACHMENT', 'Use a JPG, PNG, or PDF up to 10 MB from camera or file picker.', claim.version);
      }
      const lowerName = name.toLowerCase();
      const extensionMatches = (mime === 'image/jpeg' && (lowerName.endsWith('.jpg') || lowerName.endsWith('.jpeg')))
        || (mime === 'image/png' && lowerName.endsWith('.png'))
        || (mime === 'application/pdf' && lowerName.endsWith('.pdf'));
      if (!extensionMatches) return rejected(state, command, 'MIME_EXTENSION_MISMATCH', 'The file extension and detected MIME type must agree.', claim.version);
      const current = claim.revisions.at(-1)!;
      if (purpose === 'RECEIPT' && current.receiptIds.length >= 10) return rejected(state, command, 'ATTACHMENT_LIMIT', 'A revision supports at most 10 receipt files.', claim.version);
      if (purpose === 'FX_EVIDENCE' && (current.exchangeEvidenceIds?.length ?? 0) >= 5) return rejected(state, command, 'ATTACHMENT_LIMIT', 'A revision supports at most 5 FX evidence files.', claim.version);
      const scanOutcome = text(command.input, 'scanOutcome') || 'Clean';
      if (scanOutcome === 'Malware') return commit(state, command, ['scan.failedBytesDiscarded'], 'Attachment was blocked by the scan and its bytes were discarded. Re-upload a safe file.');
      const id = nextId(state, 'file');
      const scanning = scanOutcome === 'Timeout';
      state.files[id] = {
        id, claimId: claim.id, name, mime: mime as 'image/jpeg' | 'image/png' | 'application/pdf', sizeBytes,
        sha256, purpose: purpose as 'RECEIPT' | 'FX_EVIDENCE', source: source as 'camera' | 'file', scanStatus: 'Linked',
        ...(scanning ? { scanStatus: 'Scanning' as const, scanAttempts: 0, nextScanRetryAt: new Date(Date.parse(state.now) + 30_000).toISOString() } : {}),
      };
      if (!scanning) {
        if (purpose === 'RECEIPT') current.receiptIds.push(id);
        else current.exchangeEvidenceIds = [...(current.exchangeEvidenceIds ?? []), id];
      }
      return commit(state, command, ['files', ...(scanning ? ['file.scanStatus'] : [purpose === 'RECEIPT' ? 'revision.receiptIds' : 'revision.exchangeEvidenceIds'])], scanning ? 'Scan timed out. The file remains unlinked while bounded retries are pending.' : 'Upload scanned clean and linked.');
    }
    case 'RETRY_ATTACHMENT_SCAN': {
      if (claim.status !== 'Draft') return rejected(state, command, 'INVALID_STATUS', 'Attachment scan recovery is available only for a Draft.', claim.version);
      const fileId = text(command.input, 'fileId');
      const file = state.files[fileId];
      if (!file || file.claimId !== claim.id || file.scanStatus !== 'Scanning') return rejected(state, command, 'SCAN_NOT_RETRYABLE', 'No retryable scan exists for this draft.', claim.version);
      const outcome = text(command.input, 'scanOutcome');
      if (outcome === 'Clean') {
        file.scanStatus = 'Linked'; file.nextScanRetryAt = undefined;
        const current = claim.revisions.at(-1)!;
        if (file.purpose === 'RECEIPT') current.receiptIds.push(file.id);
        else current.exchangeEvidenceIds = [...(current.exchangeEvidenceIds ?? []), file.id];
        return commit(state, command, ['file.scanStatus', file.purpose === 'RECEIPT' ? 'revision.receiptIds' : 'revision.exchangeEvidenceIds'], 'Retry scanned clean and linked the file.');
      }
      if (outcome === 'Malware') {
        delete state.files[file.id];
        return commit(state, command, ['file.failedBytesDiscarded'], 'Attachment retry was blocked and its bytes were discarded.');
      }
      file.scanAttempts = (file.scanAttempts ?? 0) + 1;
      if (file.scanAttempts >= 2) {
        delete state.files[file.id];
        return commit(state, command, ['file.failedBytesDiscarded'], 'Scan remained indeterminate after two retries; bytes were discarded and re-upload is required.');
      }
      file.nextScanRetryAt = new Date(Date.parse(state.now) + 2 * 60_000).toISOString();
      return commit(state, command, ['file.scanAttempts', 'file.nextScanRetryAt'], 'First scan retry timed out; final retry is scheduled after two minutes.');
    }
    case 'APPROVE_CLAIM':
      if (claim.status !== 'Submitted') return rejected(state, command, 'INVALID_STATUS', 'Only Submitted claims can be approved.', claim.version);
      claim.status = 'Payment pending';
      claim.approvedRevision = claim.currentRevision;
      claim.approvedAt = state.now;
      return commit(state, command, ['status', 'approvedRevision', 'approvedAt'], 'Claim approved for payment.', [claim.employeeId]);
    case 'REQUEST_CHANGES':
      if (claim.status !== 'Submitted') return rejected(state, command, 'INVALID_STATUS', 'Only Submitted claims can be returned.', claim.version);
      if (!comment) return rejected(state, command, 'COMMENT_REQUIRED', 'A changes-request comment is required.', claim.version);
      claim.status = 'Changes requested';
      claim.revisions.at(-1)!.comment = comment;
      return commit(state, command, ['status', 'revision.comment'], 'Changes requested.', [claim.employeeId], comment);
    case 'FINAL_REJECT_CLAIM':
      if (claim.status !== 'Submitted') return rejected(state, command, 'INVALID_STATUS', 'Only Submitted claims can be finally rejected.', claim.version);
      if (!comment) return rejected(state, command, 'COMMENT_REQUIRED', 'A final rejection reason is required.', claim.version);
      claim.status = 'Final rejected';
      claim.finalRejectedAt = state.now;
      return commit(state, command, ['status', 'finalRejectedAt'], 'Claim finally rejected.', [claim.employeeId], comment);
    case 'REVOKE_APPROVAL':
      if (claim.status !== 'Payment pending') return rejected(state, command, 'REVOCATION_CLOSED', 'Approval can be revoked only before the payment is Scheduled.', claim.version);
      if (claim.approvedRevision !== claim.currentRevision) return rejected(state, command, 'REVISION_MISMATCH', 'Only the currently approved revision can be revoked.', claim.version);
      if (!comment) return rejected(state, command, 'COMMENT_REQUIRED', 'A revocation reason is required.', claim.version);
      claim.status = 'Submitted';
      delete claim.approvedRevision;
      delete claim.approvedAt;
      return commit(state, command, ['status', 'approvedRevision', 'approvedAt'], 'Approval revoked; the same revision returned to review.', [claim.employeeId], comment);
    case 'SUBMIT_CLAIM':
      if (claim.status !== 'Draft') return rejected(state, command, 'INVALID_STATUS', 'Only a Draft can be submitted.', claim.version);
      {
        const invalid = validateSubmission(state, command, claim);
        if (invalid) return invalid;
      }
      {
        const managerId = state.users[claim.employeeId]?.managerId!;
        claim.managerId = managerId;
        claim.revisions.at(-1)!.managerIdSnapshot = managerId;
      }
      claim.revisions.at(-1)!.categoryNameSnapshot = state.categories[claim.revisions.at(-1)!.categoryId].name;
      claim.status = 'Submitted';
      claim.revisions.at(-1)!.submittedAt = state.now;
      return commit(state, command, ['status', 'revision.submittedAt'], 'Claim submitted.', [claim.managerId]);
    case 'WITHDRAW_CLAIM':
      if (!['Submitted', 'Changes requested'].includes(claim.status)) return rejected(state, command, 'INVALID_STATUS', 'Only a Submitted or Changes requested claim can be withdrawn.', claim.version);
      claim.status = 'Withdrawn';
      claim.withdrawnAt = state.now;
      return commit(state, command, ['status', 'withdrawnAt'], 'Claim withdrawn.', [claim.managerId]);
    case 'DELETE_DRAFT':
      if (claim.status !== 'Draft') return rejected(state, command, 'INVALID_STATUS', 'Only Draft claims can be deleted.', claim.version);
      for (const file of Object.values(state.files)) {
        if (file.claimId === claim.id) delete state.files[file.id];
      }
      delete state.claims[claim.id];
      return commit(state, command, ['claim.deleted', 'files.deleted'], 'Draft and linked evidence deleted.');
    case 'REVISE_CLAIM': {
      if (claim.status !== 'Changes requested') return rejected(state, command, 'INVALID_STATUS', 'A new revision is allowed only after Changes requested.', claim.version);
      const current = claim.revisions.at(-1)!;
      claim.currentRevision += 1;
      claim.revisions.push({ ...structuredClone(current), number: claim.currentRevision, submittedAt: undefined, managerIdSnapshot: undefined, comment: undefined });
      claim.status = 'Draft';
      return commit(state, command, ['currentRevision', 'revisions', 'status'], 'Editable revision created.');
    }
    default:
      return rejected(state, command, 'UNSUPPORTED_COMMAND', 'This command is not implemented yet.', claim.version);
  }
}

function createDraftTransition(state: DomainState, command: DomainCommand): CommandResult {
  if (!hasRole(state, command.actorId, 'EMPLOYEE')) return rejected(state, command, 'FORBIDDEN', 'An active Employee role is required.', 0);
  const categoryId = Object.values(state.categories).find((category) => category.active)?.id ?? '';
  const id = nextId(state, 'claim');
  state.claims[id] = {
    id,
    employeeId: command.actorId,
    managerId: state.users[command.actorId]?.managerId ?? '',
    status: 'Draft',
    version: 0,
    currentRevision: 1,
    revisions: [{
      number: 1,
      merchant: '',
      categoryId,
      categoryNameSnapshot: '',
      expenseDate: '',
      currency: 'KRW',
      originalAmount: 0,
      krwAmount: 0,
      businessPurpose: '',
      receiptIds: [],
    }],
    payment: {},
    adjustmentIds: [],
    createdAt: state.now,
    updatedAt: state.now,
  };
  return commit(state, { ...command, targetId: id }, ['claim'], 'New draft created.');
}

function acceptInvitationTransition(state: DomainState, command: DomainCommand): CommandResult {
  const invitation = state.invitations[command.targetId];
  if (!invitation) return rejected(state, command, 'NOT_FOUND', 'Invitation not found.', command.expectedVersion);
  if (invitation.version !== command.expectedVersion) return rejected(state, command, 'STALE_VERSION', 'The invitation changed before acceptance.', invitation.version);
  if (invitation.status !== 'Pending') return rejected(state, command, 'INVALID_INVITATION_STATUS', 'Only a Pending invitation can be accepted.', invitation.version);
  if (Date.parse(invitation.expiresAt) <= Date.parse(state.now)) return rejected(state, command, 'INVITATION_EXPIRED', 'This invitation has expired.', invitation.version);
  const email = text(command.input, 'email').toLowerCase();
  const name = text(command.input, 'name');
  if (email !== invitation.email.toLowerCase()) return rejected(state, command, 'INVITED_EMAIL_REQUIRED', 'Sign in with the exact invited email.', invitation.version);
  if (!name) return rejected(state, command, 'NAME_REQUIRED', 'A display name is required to activate the account.', invitation.version);
  if (Object.values(state.users).some((item) => item.email?.toLowerCase() === email)) return rejected(state, command, 'ACCOUNT_EXISTS', 'An account already exists for the invited email.', invitation.version);
  const id = nextId(state, 'user');
  state.users[id] = { id, name, email, roles: [...invitation.roles], managerId: invitation.managerId, active: true, authVersion: 1, version: 1 };
  invitation.status = 'Accepted';
  invitation.version += 1;
  return commit(state, command, ['invitation.status', 'user'], 'Invitation accepted and account activated.');
}

function targetSnapshot(state: DomainState, targetId: string): Record<string, unknown> | undefined {
  const value = state.claims[targetId] ?? state.users[targetId] ?? state.categories[targetId] ?? state.invitations[targetId]
    ?? state.files[targetId] ?? state.adjustments[targetId] ?? state.deliveries.find((item) => item.id === targetId)
    ?? state.exports.find((item) => item.id === targetId);
  return value ? structuredClone(value) as unknown as Record<string, unknown> : undefined;
}

function changedFieldsForStale(state: DomainState, command: DomainCommand): string[] {
  const actual = state.auditEvents
    .filter((event) => event.targetId === command.targetId && (event.targetVersion ?? 0) > command.expectedVersion)
    .flatMap((event) => event.changedFields);
  return ['version', ...new Set(actual)];
}

function enrichCommittedAudit(original: DomainState, result: CommandResult): CommandResult {
  if (result.outcome.status !== 'committed') return result;
  const state = structuredClone(result.state);
  for (const auditId of result.auditEventIds) {
    const audit = state.auditEvents.find((event) => event.id === auditId);
    if (!audit) continue;
    const claim = state.claims[audit.targetId];
    audit.targetVersion = result.outcome.targetVersion;
    audit.revision = claim?.currentRevision;
    audit.before = targetSnapshot(original, audit.targetId);
    audit.after = targetSnapshot(state, audit.targetId);
  }
  return { ...result, state };
}

function rememberResult(result: CommandResult, command: DomainCommand, fingerprint: string): CommandResult {
  const state = structuredClone(result.state);
  state.idempotency[command.idempotencyKey] = {
    fingerprint,
    outcome: structuredClone(result.outcome),
    auditEventIds: [...result.auditEventIds],
    deliveryEventIds: [...result.deliveryEventIds],
    changedFields: [...result.changedFields],
  };
  return { ...result, state };
}

export function executeCommand(original: DomainState, command: DomainCommand): CommandResult {
  const fingerprint = commandFingerprint(command);
  const replay = original.idempotency[command.idempotencyKey];
  if (replay) {
    if (replay.fingerprint !== fingerprint) {
      const targetVersion = original.claims[command.targetId]?.version ?? command.expectedVersion;
      return rejected(original, command, 'IDEMPOTENCY_CONFLICT', 'This idempotency key was already used for different input.', targetVersion);
    }
    return {
      state: original,
      outcome: structuredClone(replay.outcome),
      auditEventIds: [...replay.auditEventIds],
      deliveryEventIds: [...replay.deliveryEventIds],
      changedFields: [...replay.changedFields],
    };
  }

  const state = structuredClone(original);
  if (command.type === 'CREATE_DRAFT') return rememberResult(enrichCommittedAudit(original, createDraftTransition(state, command)), command, fingerprint);
  if (command.type === 'ACCEPT_INVITATION') {
    const result = acceptInvitationTransition(state, command);
    if (result.outcome.code === 'STALE_VERSION') result.changedFields = changedFieldsForStale(original, command);
    return rememberResult(enrichCommittedAudit(original, result), command, fingerprint);
  }
  if (ADMIN_COMMANDS.has(command.type)) {
    const result = adminTransition(state, command);
    if (result.outcome.code === 'STALE_VERSION') result.changedFields = changedFieldsForStale(original, command);
    return rememberResult(enrichCommittedAudit(original, result), command, fingerprint);
  }
  const claim = state.claims[command.targetId];
  if (!claim) return rememberResult(rejected(original, command, 'NOT_FOUND', 'Claim not found.', command.expectedVersion), command, fingerprint);
  if (claim.version !== command.expectedVersion) {
    const result = rejected(original, command, 'STALE_VERSION', 'The claim changed. Review the latest state and retry.', claim.version);
    result.changedFields = changedFieldsForStale(original, command);
    return rememberResult(result, command, fingerprint);
  }

  const denied = ensureAccess(original, command, claim);
  if (denied) return rememberResult(denied, command, fingerprint);
  const wrongRevision = requireRevision(original, command, claim);
  if (wrongRevision) return rememberResult(wrongRevision, command, fingerprint);

  const result = executeTransition(state, command, claim);
  return rememberResult(enrichCommittedAudit(original, result), command, fingerprint);
}
