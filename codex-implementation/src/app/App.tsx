import { useState } from 'react';
import { FeedbackRegion } from '../components/FeedbackRegion';
import { RoleSwitcher } from '../components/RoleSwitcher';
import { RoleStateSurface, StateLab, type UXState } from '../components/StateLab';
import { StatusBadge } from '../components/StatusBadge';
import type { Role } from '../domain/types';
import { useDomain } from './useDomain';
import { EmployeeSurface } from '../features/employee/EmployeeSurface';
import { ManagerSurface } from '../features/manager/ManagerSurface';
import { FinanceSurface } from '../features/finance/FinanceSurface';
import { AdminSurface } from '../features/admin/AdminSurface';

const ROLE_META: Record<Role, { title: string; subtitle: string; actorId: string }> = {
  EMPLOYEE: { title: 'Employee claims', subtitle: 'Create, evidence, submit, and follow your own reimbursements.', actorId: 'usr-employee' },
  MANAGER: { title: 'Manager review', subtitle: 'Review only currently assigned claims at the exact revision.', actorId: 'usr-manager' },
  FINANCE: { title: 'Finance operations', subtitle: 'Claim payment work atomically and record verified outcomes.', actorId: 'usr-finance' },
  ADMIN: { title: 'Admin control room', subtitle: 'Manage access, policy records, holds, warnings, and audit.', actorId: 'usr-admin' },
};

export function App() {
  const [role, setRole] = useState<Role>('EMPLOYEE');
  const [previewState, setPreviewState] = useState<UXState>('Default');
  const { state, dispatch, reset, feedback } = useDomain();
  const current = role === 'EMPLOYEE' ? state.claims['clm-submitted'] : role === 'MANAGER' ? state.claims['clm-submitted'] : role === 'FINANCE' ? state.claims['clm-approved'] : state.claims['clm-completed'];
  const meta = ROLE_META[role];
  const authorized = Boolean(state.users[meta.actorId]?.active && state.users[meta.actorId].roles.includes(role));

  return (
    <div className="app-shell">
      <a className="skip-link" href="#workspace-main">Skip to workspace</a>
      <aside className="sidebar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">J</span>
          <div><strong>JOEWRKS</strong><span>Expense desk</span></div>
        </div>
        <RoleSwitcher activeRole={role} onChange={setRole} />
        <div className="authority-note">
          <span>Approved authority</span>
          <strong>Revision 55</strong>
          <small>Local deterministic simulation</small>
        </div>
      </aside>

      <main id="workspace-main" className="workspace">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">{role} workspace</p>
            <h1>{meta.title}</h1>
            <p>{meta.subtitle}</p>
          </div>
          <button className="button secondary" type="button" onClick={reset}>Reset simulated workspace</button>
        </header>
        <FeedbackRegion feedback={feedback} />

        {authorized && <section className="summary-grid" aria-label="Workspace summary">
          <article className="metric-card">
            <span>Current sample</span>
            <strong>{current.id}</strong>
            <StatusBadge status={current.status} />
          </article>
          <article className="metric-card">
            <span>Domain events</span>
            <strong>{state.auditEvents.length}</strong>
            <small>Separate from {state.deliveries.length} delivery effects</small>
          </article>
          <article className="metric-card">
            <span>Authority</span>
            <strong>rev {state.canonicalRevision}</strong>
            <small title={state.canonicalDigest}>{state.canonicalDigest.slice(0, 12)}…</small>
          </article>
        </section>}

        <StateLab role={role} selected={previewState} onChange={setPreviewState} />
        {previewState !== 'Default' ? <RoleStateSurface role={role} state={previewState} onReturn={() => setPreviewState('Default')} /> : !authorized ? <section className="empty-panel critical-callout"><h2>Access unavailable</h2><p>The latest account or role authorization is inactive. Governed records and attachments are hidden immediately.</p></section> : role === 'EMPLOYEE' ? <EmployeeSurface state={state} dispatch={dispatch} /> : role === 'MANAGER' ? <ManagerSurface state={state} dispatch={dispatch} /> : role === 'FINANCE' ? <FinanceSurface state={state} dispatch={dispatch} /> : role === 'ADMIN' ? <AdminSurface state={state} dispatch={dispatch} /> : <section className="workspace-placeholder card" aria-labelledby="workspace-preview-title">
          <div>
            <p className="eyebrow">Audited surface</p>
            <h2 id="workspace-preview-title">{meta.title} workspace</h2>
            <p>Role-specific domain controls are rendered in the next implementation slice.</p>
          </div>
          <StatusBadge status={current.status} />
        </section>}
      </main>
    </div>
  );
}
