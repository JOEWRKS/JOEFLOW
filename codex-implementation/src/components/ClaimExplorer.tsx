import { useMemo, useState } from 'react';
import type { Claim, DomainState } from '../domain/types';

export function useClaimExplorer(state: DomainState, scopedClaims: Claim[]) {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [currency, setCurrency] = useState('');
  const [assignee, setAssignee] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [flag, setFlag] = useState('');
  const [sort, setSort] = useState('Recent change');
  const claims = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return scopedClaims.filter((claim) => {
      const revision = claim.revisions.at(-1)!;
      const employee = state.users[claim.employeeId]?.name ?? '';
      const assigned = claim.payment.ownerId ?? claim.managerId;
      const submittedDate = revision.submittedAt?.slice(0, 10) ?? '';
      const delayed = claim.status === 'Submitted' && submittedDate && (Date.parse(state.now.slice(0, 10)) - Date.parse(submittedDate)) / 86_400_000 >= 3;
      const duplicate = Boolean(revision.duplicateReason);
      return (!normalized || [claim.id, revision.merchant, employee].some((value) => value.toLowerCase().includes(normalized)))
        && (!status || claim.status === status)
        && (!categoryId || revision.categoryId === categoryId)
        && (!currency || revision.currency === currency)
        && (!assignee || assigned === assignee)
        && (!dateFrom || revision.expenseDate >= dateFrom)
        && (!dateTo || revision.expenseDate <= dateTo)
        && (!flag || (flag === 'Delayed' ? delayed : duplicate));
    }).sort((a, b) => {
      const ar = a.revisions.at(-1)!; const br = b.revisions.at(-1)!;
      if (sort === 'Expense date') return br.expenseDate.localeCompare(ar.expenseDate);
      if (sort === 'Amount') return br.krwAmount - ar.krwAmount;
      return b.updatedAt.localeCompare(a.updatedAt);
    });
  }, [assignee, categoryId, currency, dateFrom, dateTo, flag, query, scopedClaims, sort, state, status]);
  const statuses = [...new Set(scopedClaims.map((claim) => claim.status))];
  const snapshot = JSON.stringify({ query, status, categoryId, currency, assignee, dateFrom, dateTo, flag, sort });
  const controls = <section className="claim-explorer card" aria-label="Claim search, filters, and sort">
    <label>Search claims<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Claim ID, merchant, employee" /></label>
    <label>Status filter<select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option>{statuses.map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>Category filter<select value={categoryId} onChange={(event) => setCategoryId(event.target.value)}><option value="">All categories</option>{Object.values(state.categories).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
    <label>Currency filter<select value={currency} onChange={(event) => setCurrency(event.target.value)}><option value="">All currencies</option>{[...new Set(scopedClaims.map((item) => item.revisions.at(-1)!.currency))].map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>Assignee filter<select value={assignee} onChange={(event) => setAssignee(event.target.value)}><option value="">All assignees</option>{Object.values(state.users).filter((user) => user.roles.some((role) => role === 'MANAGER' || role === 'FINANCE')).map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}</select></label>
    <label>Expense date from<input value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} placeholder="YYYY-MM-DD" /></label>
    <label>Expense date to<input value={dateTo} onChange={(event) => setDateTo(event.target.value)} placeholder="YYYY-MM-DD" /></label>
    <label>Flag filter<select value={flag} onChange={(event) => setFlag(event.target.value)}><option value="">All flags</option><option>Delayed</option><option>Duplicate noted</option></select></label>
    <label>Sort claims<select value={sort} onChange={(event) => setSort(event.target.value)}><option>Recent change</option><option>Expense date</option><option>Amount</option></select></label>
    <span className="filter-count">{claims.length} of {scopedClaims.length} authorized claims</span>
  </section>;
  return { claims, controls, snapshot };
}
