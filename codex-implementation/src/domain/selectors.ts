import type { Claim, DomainState, Role } from './types';

export function claimsForRole(state: DomainState, actorId: string, role: Role): Claim[] {
  const actor = state.users[actorId];
  if (!actor?.active || !actor.roles.includes(role)) return [];
  const claims = Object.values(state.claims);
  if (role === 'EMPLOYEE') return claims.filter((claim) => claim.employeeId === actorId);
  if (role === 'MANAGER') {
    return claims.filter((claim) => claim.managerId === actorId
      && claim.employeeId !== actorId
      && ['Submitted', 'Payment pending'].includes(claim.status));
  }
  if (role === 'FINANCE') {
    return claims.filter((claim) => claim.status === 'Payment pending'
      || (claim.payment.ownerId === actorId && ['Scheduled', 'Payment failed', 'Payment hold', 'Payment completed'].includes(claim.status)));
  }
  return claims;
}

export function adjustmentTotals(state: DomainState, claimId: string) {
  const claim = state.claims[claimId];
  const completed = claim.adjustmentIds.map((id) => state.adjustments[id]).filter((item) => item?.status === 'Completed');
  const recoveredKrw = completed.filter((item) => item.kind === 'Recovery').reduce((sum, item) => sum + (item.actualAmountKrw ?? item.amountKrw), 0);
  const addedKrw = completed.filter((item) => item.kind === 'Additional payment').reduce((sum, item) => sum + (item.actualAmountKrw ?? item.amountKrw), 0);
  return { originalKrw: claim.revisions.at(-1)!.krwAmount, recoveredKrw, addedKrw, netKrw: claim.revisions.at(-1)!.krwAmount - recoveredKrw + addedKrw };
}
