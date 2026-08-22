import { commandFingerprint } from './commands';
import type { Adjustment, AuditEvent, Claim, CommandOutcome, CommandResult, DeliveryEvent, DomainCommand, DomainState, Role } from './types';

const REVIEW_COMMANDS = new Set(['APPROVE_CLAIM', 'REQUEST_CHANGES', 'FINAL_REJECT_CLAIM', 'REVOKE_APPROVAL']);
const FINANCE_COMMANDS = new Set([
  'SCHEDULE_PAYMENT', 'COMPLETE_PAYMENT', 'FAIL_PAYMENT', 'HOLD_PAYMENT', 'VERIFY_FAILED_PAYMENT',
  'RESCHEDULE_PAYMENT', 'CREATE_ADJUSTMENT', 'COMPLETE_ADJUSTMENT', 'FAIL_ADJUSTMENT', 'RESOLVE_ADJUSTMENT',
]);
const EMPLOYEE_COMMANDS = new Set(['SUBMIT_CLAIM', 'WITHDRAW_CLAIM', 'DELETE_DRAFT', 'REVISE_CLAIM']);

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

function queueDelivery(state: DomainState, targetId: string, recipientId: string, template: string): string[] {
  const ids: string[] = [];
  for (const channel of ['APP', 'EMAIL'] as const) {
    const event: DeliveryEvent = {
      id: nextId(state, 'delivery'), targetId, channel, recipientId, template,
      status: 'Queued', attempts: 0, manualRetryUsed: false,
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
      if (!['Bank transfer', 'Corporate card', 'Other'].includes(method)) return rejected(state, command, 'PAYMENT_METHOD_REQUIRED', 'A supported payment method is required.', claim.version);
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
      if (!['Payment pending', 'Scheduled', 'Payment failed'].includes(claim.status)) return rejected(state, command, 'INVALID_STATUS', 'This payment cannot be placed on hold.', claim.version);
      if (claim.payment.ownerId && ownerDenied) return ownerDenied;
      const reason = text(command.input, 'reason');
      if (!reason) return rejected(state, command, 'REASON_REQUIRED', 'Payment hold reason is required.', claim.version);
      claim.payment.ownerId ||= command.actorId;
      claim.payment.holdReason = reason;
      claim.status = 'Payment hold';
      return commit(state, command, ['payment.ownerId', 'payment.holdReason', 'status'], 'Payment placed on hold.', [claim.employeeId], reason);
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
      const active = claim.adjustmentIds.map((id) => state.adjustments[id]).some((item) => item && ['In progress', 'Needs verification'].includes(item.status));
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
      if (!adjustment || adjustment.claimId !== claim.id) return rejected(state, command, 'ADJUSTMENT_NOT_FOUND', 'Adjustment not found.', claim.version);
      if (adjustment.status !== 'In progress') return rejected(state, command, 'INVALID_ADJUSTMENT_STATUS', 'Only an In progress adjustment can be completed.', claim.version);
      const actualDate = text(command.input, 'actualDate');
      const externalReference = text(command.input, 'externalReference');
      if (!actualDate || actualDate > today || actualDate < (claim.approvedAt?.slice(0, 10) ?? '')) return rejected(state, command, 'INVALID_ACTUAL_DATE', 'Adjustment date must be between approval and today.', claim.version);
      if (!externalReference) return rejected(state, command, 'REFERENCE_REQUIRED', 'External adjustment reference is required.', claim.version);
      if (referenceExists(state, externalReference, adjustment.id)) return rejected(state, command, 'DUPLICATE_REFERENCE', 'External reference must be unique.', claim.version);
      adjustment.status = 'Completed';
      adjustment.actualDate = actualDate;
      adjustment.externalReference = externalReference;
      adjustment.version += 1;
      return commit(state, command, ['adjustment.status', 'adjustment.actualDate', 'adjustment.externalReference'], 'Adjustment completed.', [claim.employeeId]);
    }
    case 'FAIL_ADJUSTMENT': {
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
        if (!actualDate || !externalReference || referenceExists(state, externalReference, adjustment.id)) {
          return rejected(state, command, 'COMPLETION_EVIDENCE_REQUIRED', 'Executed requires a valid date and unique external reference.', claim.version);
        }
        adjustment.status = 'Completed';
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

function executeTransition(state: DomainState, command: DomainCommand, claim: Claim): CommandResult {
  if (FINANCE_COMMANDS.has(command.type)) return financeTransition(state, command, claim);
  const comment = typeof command.input.comment === 'string' ? command.input.comment.trim() : '';
  switch (command.type) {
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
      claim.status = 'Changes requested';
      delete claim.approvedRevision;
      delete claim.approvedAt;
      return commit(state, command, ['status', 'approvedRevision', 'approvedAt'], 'Approval revoked; a new revision is required.', [claim.employeeId], comment);
    case 'SUBMIT_CLAIM':
      if (claim.status !== 'Draft') return rejected(state, command, 'INVALID_STATUS', 'Only a Draft can be submitted.', claim.version);
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
      delete state.claims[claim.id];
      return commit(state, command, ['claim.deleted'], 'Draft deleted.');
    case 'REVISE_CLAIM': {
      if (claim.status !== 'Changes requested') return rejected(state, command, 'INVALID_STATUS', 'A new revision is allowed only after Changes requested.', claim.version);
      const current = claim.revisions.at(-1)!;
      claim.currentRevision += 1;
      claim.revisions.push({ ...structuredClone(current), number: claim.currentRevision, submittedAt: state.now, comment: undefined });
      claim.status = 'Submitted';
      return commit(state, command, ['currentRevision', 'revisions', 'status'], 'New revision submitted.', [claim.managerId]);
    }
    default:
      return rejected(state, command, 'UNSUPPORTED_COMMAND', 'This command is not implemented yet.', claim.version);
  }
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
  const claim = state.claims[command.targetId];
  if (!claim) return rejected(original, command, 'NOT_FOUND', 'Claim not found.', command.expectedVersion);
  if (claim.version !== command.expectedVersion) return rejected(original, command, 'STALE_VERSION', 'The claim changed. Review the latest state and retry.', claim.version);

  const denied = ensureAccess(original, command, claim);
  if (denied) return denied;
  const wrongRevision = requireRevision(original, command, claim);
  if (wrongRevision) return wrongRevision;

  const result = executeTransition(state, command, claim);
  if (result.outcome.status === 'committed') {
    result.state.idempotency[command.idempotencyKey] = {
      fingerprint,
      outcome: structuredClone(result.outcome),
      auditEventIds: [...result.auditEventIds],
      deliveryEventIds: [...result.deliveryEventIds],
      changedFields: [...result.changedFields],
    };
  }
  return result;
}
