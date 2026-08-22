import { useMemo, useState } from 'react';
import { filterClaims } from '../domain/selectors';
import type { Claim, DomainState } from '../domain/types';

export function useClaimExplorer(state: DomainState, scopedClaims: Claim[]) {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [currency, setCurrency] = useState('');
  const [assignee, setAssignee] = useState('');
  const [expenseDateFrom, setExpenseDateFrom] = useState('');
  const [expenseDateTo, setExpenseDateTo] = useState('');
  const [submissionDateFrom, setSubmissionDateFrom] = useState('');
  const [submissionDateTo, setSubmissionDateTo] = useState('');
  const [flag, setFlag] = useState('');
  const [sort, setSort] = useState('Recent change');
  const claims = useMemo(() => filterClaims(state, scopedClaims, {
    query, status, categoryId, currency, assignee, expenseDateFrom, expenseDateTo,
    submissionDateFrom, submissionDateTo, flag, sort,
  }), [assignee, categoryId, currency, expenseDateFrom, expenseDateTo, flag, query, scopedClaims, sort, state, status, submissionDateFrom, submissionDateTo]);
  const statuses = [...new Set(scopedClaims.map((claim) => claim.status))];
  const snapshot = JSON.stringify({ query, status, categoryId, currency, assignee, expenseDateFrom, expenseDateTo, submissionDateFrom, submissionDateTo, flag, sort });
  const controls = <section className="claim-explorer card" aria-label="Claim search, filters, and sort">
    <label>Search claims<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Claim ID, merchant, employee" /></label>
    <label>Status filter<select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option>{statuses.map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>Category filter<select value={categoryId} onChange={(event) => setCategoryId(event.target.value)}><option value="">All categories</option>{Object.values(state.categories).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
    <label>Currency filter<select value={currency} onChange={(event) => setCurrency(event.target.value)}><option value="">All currencies</option>{[...new Set(scopedClaims.map((item) => item.revisions.at(-1)!.currency))].map((item) => <option key={item}>{item}</option>)}</select></label>
    <label>Assignee filter<select value={assignee} onChange={(event) => setAssignee(event.target.value)}><option value="">All assignees</option>{Object.values(state.users).filter((user) => user.roles.some((role) => role === 'MANAGER' || role === 'FINANCE')).map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}</select></label>
    <label>Expense date from<input value={expenseDateFrom} onChange={(event) => setExpenseDateFrom(event.target.value)} placeholder="YYYY-MM-DD" /></label>
    <label>Expense date to<input value={expenseDateTo} onChange={(event) => setExpenseDateTo(event.target.value)} placeholder="YYYY-MM-DD" /></label>
    <label>Submission date from<input value={submissionDateFrom} onChange={(event) => setSubmissionDateFrom(event.target.value)} placeholder="YYYY-MM-DD" /></label>
    <label>Submission date to<input value={submissionDateTo} onChange={(event) => setSubmissionDateTo(event.target.value)} placeholder="YYYY-MM-DD" /></label>
    <label>Flag filter<select value={flag} onChange={(event) => setFlag(event.target.value)}><option value="">All flags</option><option>Late expense</option><option>Duplicate noted</option></select></label>
    <label>Sort claims<select value={sort} onChange={(event) => setSort(event.target.value)}><option>Recent change</option><option>Expense date</option><option>Submission date</option><option>Amount</option></select></label>
    <span className="filter-count">{claims.length} of {scopedClaims.length} authorized claims</span>
  </section>;
  return { claims, controls, snapshot };
}
