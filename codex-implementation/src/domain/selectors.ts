import type { AuditEvent, Claim, DomainState, Role } from './types';

export function canAccessClaim(state: DomainState, actorId: string, role: Role, claim: Claim): boolean {
  const actor = state.users[actorId];
  if (!actor?.active || !actor.roles.includes(role)) return false;
  if (role === 'ADMIN') return true;
  if (role === 'EMPLOYEE') return claim.employeeId === actorId;
  if (role === 'MANAGER') return claim.managerId === actorId && claim.employeeId !== actorId
    && ['Submitted', 'Payment pending'].includes(claim.status);
  return claim.status === 'Payment pending'
    || (claim.payment.ownerId === actorId && ['Scheduled', 'Payment failed', 'Payment hold', 'Payment completed'].includes(claim.status));
}

export function claimsForRole(state: DomainState, actorId: string, role: Role): Claim[] {
  return Object.values(state.claims).filter((claim) => canAccessClaim(state, actorId, role, claim));
}

function claimForAuditEvent(state: DomainState, event: AuditEvent): Claim | undefined {
  const direct = state.claims[event.targetId];
  if (direct) return direct;
  const file = state.files[event.targetId];
  if (file) return state.claims[file.claimId];
  const adjustment = state.adjustments[event.targetId];
  if (adjustment) return state.claims[adjustment.claimId];
  const delivery = state.deliveries.find((item) => item.id === event.targetId);
  return delivery ? state.claims[delivery.targetId] : undefined;
}

export interface TimelineEntry {
  id: string;
  targetId: string;
  action: AuditEvent['action'];
  at: string;
  revision?: number;
  businessStatus?: string;
  actorName: string;
  actorRoles: Role[] | ['SYSTEM'];
  managerComment?: string;
}

const RELATED_COMMENT_ACTIONS = new Set<AuditEvent['action']>(['REQUEST_CHANGES', 'FINAL_REJECT_CLAIM', 'REVOKE_APPROVAL']);

export function timelineEntriesForRole(state: DomainState, role: Role, actorId: string): TimelineEntry[] {
  if (role === 'ADMIN') return [];
  return state.auditEvents.flatMap((event) => {
    const claim = claimForAuditEvent(state, event);
    if (!claim || !canAccessClaim(state, actorId, role, claim)) return [];
    const actor = state.users[event.actorId];
    return [{
      id: event.id,
      targetId: claim.id,
      action: event.action,
      at: event.at,
      revision: event.revision,
      businessStatus: claim.status,
      actorName: actor?.name ?? 'System',
      actorRoles: actor?.roles ?? ['SYSTEM'],
      ...(event.reason && RELATED_COMMENT_ACTIONS.has(event.action) ? { managerComment: event.reason } : {}),
    }];
  });
}

export interface ClaimFilter {
  query?: string;
  status?: string;
  categoryId?: string;
  currency?: string;
  assignee?: string;
  expenseDateFrom?: string;
  expenseDateTo?: string;
  submissionDateFrom?: string;
  submissionDateTo?: string;
  flag?: string;
  sort?: string;
}

export function filterClaims(state: DomainState, scopedClaims: Claim[], filter: ClaimFilter): Claim[] {
  const normalized = (filter.query ?? '').trim().toLowerCase();
  return scopedClaims.filter((claim) => {
    const revision = claim.revisions.at(-1)!;
    const employee = state.users[claim.employeeId]?.name ?? '';
    const assigned = claim.payment.ownerId ?? claim.managerId;
    const submittedDate = revision.submittedAt?.slice(0, 10) ?? '';
    const late = Boolean(revision.lateReason?.trim());
    const duplicate = Boolean(revision.duplicateReason?.trim());
    return (!normalized || [claim.id, revision.merchant, employee].some((value) => value.toLowerCase().includes(normalized)))
      && (!filter.status || claim.status === filter.status)
      && (!filter.categoryId || revision.categoryId === filter.categoryId)
      && (!filter.currency || revision.currency === filter.currency)
      && (!filter.assignee || assigned === filter.assignee)
      && (!filter.expenseDateFrom || revision.expenseDate >= filter.expenseDateFrom)
      && (!filter.expenseDateTo || revision.expenseDate <= filter.expenseDateTo)
      && (!filter.submissionDateFrom || Boolean(submittedDate && submittedDate >= filter.submissionDateFrom))
      && (!filter.submissionDateTo || Boolean(submittedDate && submittedDate <= filter.submissionDateTo))
      && (!filter.flag || (filter.flag === 'Late expense' ? late : duplicate));
  }).sort((a, b) => {
    const ar = a.revisions.at(-1)!; const br = b.revisions.at(-1)!;
    if (filter.sort === 'Expense date') return br.expenseDate.localeCompare(ar.expenseDate);
    if (filter.sort === 'Submission date') return (br.submittedAt ?? '').localeCompare(ar.submittedAt ?? '');
    if (filter.sort === 'Amount') return br.krwAmount - ar.krwAmount;
    return b.updatedAt.localeCompare(a.updatedAt);
  });
}

export function adjustmentTotals(state: DomainState, claimId: string) {
  const claim = state.claims[claimId];
  const completed = claim.adjustmentIds.map((id) => state.adjustments[id]).filter((item) => item?.status === 'Completed');
  const recoveredKrw = completed.filter((item) => item.kind === 'Recovery').reduce((sum, item) => sum + (item.actualAmountKrw ?? item.amountKrw), 0);
  const addedKrw = completed.filter((item) => item.kind === 'Additional payment').reduce((sum, item) => sum + (item.actualAmountKrw ?? item.amountKrw), 0);
  return { originalKrw: claim.revisions.at(-1)!.krwAmount, recoveredKrw, addedKrw, netKrw: claim.revisions.at(-1)!.krwAmount - recoveredKrw + addedKrw };
}
