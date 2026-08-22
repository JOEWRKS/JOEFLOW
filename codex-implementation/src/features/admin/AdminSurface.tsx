import { useRef, useState } from 'react';
import { CommandDialog } from '../../components/CommandDialog';
import { ExportPanel } from '../../components/ExportPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { Timeline } from '../../components/Timeline';
import type { CommandResult, DomainCommand, DomainState, Role } from '../../domain/types';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }
type Tab = 'Invitations' | 'Accounts & roles' | 'Categories' | 'Holds & reassignment' | 'Operational warnings' | 'Audit & export';
const TABS: Tab[] = ['Invitations', 'Accounts & roles', 'Categories', 'Holds & reassignment', 'Operational warnings', 'Audit & export'];

export function AdminSurface({ state, dispatch }: Props) {
  const [tab, setTab] = useState<Tab>('Invitations');
  const [email, setEmail] = useState('');
  const [inviteRoles] = useState<Role[]>(['EMPLOYEE']);
  const [revokeId, setRevokeId] = useState<string>();
  const [revokeReason, setRevokeReason] = useState('');
  const revokeTrigger = useRef<HTMLButtonElement>(null);
  const [userId, setUserId] = useState('usr-employee');
  const [accountReason, setAccountReason] = useState('');
  const [categoryId, setCategoryId] = useState('CAT-001');
  const [categoryName, setCategoryName] = useState(state.categories['CAT-001'].name);
  const [categoryReason, setCategoryReason] = useState('');
  const [claimId, setClaimId] = useState('clm-completed');
  const [holdReason, setHoldReason] = useState('');

  const run = (type: DomainCommand['type'], targetId: string, expectedVersion: number, input: Record<string, unknown>) => dispatch({
    type, actorId: 'usr-admin', targetId, expectedVersion,
    idempotencyKey: `ui-${type}-${targetId}-${expectedVersion}`, input,
  });
  const selectedUser = state.users[userId];
  const selectedCategory = state.categories[categoryId];
  const selectedClaim = state.claims[claimId];

  return (
    <div className="admin-surface card">
      <div className="admin-tabs" role="tablist" aria-label="Admin modules">
        {TABS.map((item) => <button key={item} type="button" role="tab" aria-selected={item === tab} onClick={() => setTab(item)}>{item}</button>)}
      </div>
      <div className="admin-module" role="tabpanel">
        {tab === 'Invitations' && <section aria-labelledby="invitation-title">
          <div className="section-heading"><div><p className="eyebrow">Invite-only access</p><h2 id="invitation-title">Invitation lifecycle</h2></div><span>7-day expiry · latest link only</span></div>
          <div className="inline-form"><label>Invite email<input value={email} onChange={(event) => setEmail(event.target.value)} /></label><button className="button primary" type="button" onClick={() => run('ISSUE_INVITATION', 'invitation-register', 0, { email, roles: inviteRoles, managerId: 'usr-manager' })}>Issue invitation</button></div>
          <div className="governance-list">{Object.values(state.invitations).map((invitation) => <article key={invitation.id}>
            <div><strong>{invitation.email}</strong><span>Expires {invitation.expiresAt.slice(0, 10)} · version {invitation.version}</span></div><StatusBadge status={invitation.status} />
            {invitation.status === 'Pending' && <div className="button-row"><button className="button secondary" type="button" onClick={() => run('REISSUE_INVITATION', invitation.id, invitation.version, {})}>Reissue invitation {invitation.id}</button><button ref={revokeTrigger} className="button danger-quiet" type="button" onClick={() => { setRevokeId(invitation.id); setRevokeReason(''); }}>Revoke invitation {invitation.id}</button></div>}
          </article>)}</div>
        </section>}

        {tab === 'Accounts & roles' && <section aria-labelledby="accounts-title">
          <div className="section-heading"><div><p className="eyebrow">Latest authorization</p><h2 id="accounts-title">Accounts, roles, and sessions</h2></div><span>Versioned Admin writes</span></div>
          <div className="form-grid"><label>Managed user<select value={userId} onChange={(event) => { setUserId(event.target.value); setAccountReason(''); }}>{Object.values(state.users).map((user) => <option key={user.id} value={user.id}>{user.name} · {user.id}</option>)}</select></label><label>Account change reason<input value={accountReason} onChange={(event) => setAccountReason(event.target.value)} /></label></div>
          <div className="account-summary"><strong>{selectedUser.name}</strong><span>{selectedUser.active ? 'Active' : 'Inactive'} · auth version {selectedUser.authVersion}</span><small>{selectedUser.roles.join(' + ')} · manager {selectedUser.managerId ?? 'not assigned'}</small></div>
          <div className="button-row"><button className={selectedUser.active ? 'button danger-quiet' : 'button primary'} type="button" onClick={() => run('UPDATE_ACCOUNT', selectedUser.id, selectedUser.version, { active: !selectedUser.active, roles: selectedUser.roles, reason: accountReason })}>{selectedUser.active ? 'Deactivate account' : 'Activate account'}</button></div>
        </section>}

        {tab === 'Categories' && <section aria-labelledby="categories-title">
          <div className="section-heading"><div><p className="eyebrow">Stable IDs</p><h2 id="categories-title">Expense categories</h2></div><span>{Object.values(state.categories).filter((item) => item.active).length} active</span></div>
          <div className="form-grid"><label>Managed category<select value={categoryId} onChange={(event) => { const id = event.target.value; setCategoryId(id); setCategoryName(state.categories[id].name); }}>{Object.values(state.categories).map((item) => <option key={item.id} value={item.id}>{item.id} · {item.name}</option>)}</select></label><label>Category name<input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} /></label><label className="span-2">Category change reason<input value={categoryReason} onChange={(event) => setCategoryReason(event.target.value)} /></label></div>
          <div className="button-row"><button className="button secondary" type="button" onClick={() => run('UPDATE_CATEGORY', selectedCategory.id, selectedCategory.version, { name: categoryName, active: selectedCategory.active, reason: categoryReason })}>Rename category</button><button className={selectedCategory.active ? 'button danger-quiet' : 'button primary'} type="button" onClick={() => run('UPDATE_CATEGORY', selectedCategory.id, selectedCategory.version, { name: categoryName, active: !selectedCategory.active, reason: categoryReason })}>{selectedCategory.active ? 'Deactivate category' : 'Activate category'}</button></div>
          <p className="helper-text">Submitted revisions retain the category name snapshot captured at submission. Zero active categories is blocked.</p>
        </section>}

        {tab === 'Holds & reassignment' && <section aria-labelledby="holds-title">
          <div className="section-heading"><div><p className="eyebrow">Atomic governance</p><h2 id="holds-title">Legal holds and ownership</h2></div><span>Required reason</span></div>
          <div className="form-grid"><label>Governed claim<select value={claimId} onChange={(event) => { setClaimId(event.target.value); setHoldReason(''); }}>{Object.values(state.claims).map((claim) => <option key={claim.id} value={claim.id}>{claim.id} · {claim.status}</option>)}</select></label><label>Legal hold reason<input value={holdReason} onChange={(event) => setHoldReason(event.target.value)} /></label></div>
          <div className="hold-summary"><strong>{selectedClaim.legalHold ? `Held · ${selectedClaim.legalHold.reason}` : 'No legal hold'}</strong><span>{selectedClaim.id} · version {selectedClaim.version}</span></div>
          <div className="button-row">{selectedClaim.legalHold ? <button className="button danger-quiet" type="button" onClick={() => run('RELEASE_LEGAL_HOLD', selectedClaim.id, selectedClaim.version, { reason: holdReason })}>Release legal hold</button> : <button className="button primary" type="button" onClick={() => run('SET_LEGAL_HOLD', selectedClaim.id, selectedClaim.version, { reason: holdReason })}>Set legal hold</button>}</div>
          <div className="readonly-note"><strong>Reassignment boundary</strong><span>Manager reassignment is enabled only when the pinned manager can no longer process. Finance reassignment preserves the payment transition and changes only current owner.</span></div>
        </section>}

        {tab === 'Operational warnings' && <section aria-labelledby="warnings-title">
          <div className="section-heading"><div><p className="eyebrow">Delivery is not domain truth</p><h2 id="warnings-title">Operational warnings</h2></div><span>{state.warnings.filter((warning) => !warning.resolved).length} open</span></div>
          <div className="governance-list">{state.warnings.map((warning) => {
            const delivery = state.deliveries.find((item) => item.id === warning.targetId)!;
            return <article key={warning.id}><div><strong>{warning.message}</strong><span>{delivery.channel} · attempts {delivery.attempts} · {delivery.status}</span></div><StatusBadge status={warning.resolved ? 'Resolved' : 'Operational warning'} /><button className="button secondary" type="button" disabled={delivery.manualRetryUsed} onClick={() => run('RETRY_DELIVERY', delivery.id, delivery.version, {})}>Retry delivery once</button></article>;
          })}</div>
        </section>}

        {tab === 'Audit & export' && <div className="governed-columns"><Timeline state={state} role="ADMIN" actorId="usr-admin" raw /><ExportPanel state={state} role="ADMIN" actorId="usr-admin" dispatch={dispatch} /></div>}
      </div>
      <CommandDialog open={Boolean(revokeId)} title="Revoke pending invitation?" confirmLabel="Confirm invitation revocation" triggerRef={revokeTrigger} destructive onCancel={() => setRevokeId(undefined)} onConfirm={() => {
        if (!revokeId) return;
        const invitation = state.invitations[revokeId];
        run('REVOKE_INVITATION', revokeId, invitation.version, { reason: revokeReason });
        setRevokeId(undefined);
      }}><label htmlFor="invite-revoke-reason">Revocation reason</label><textarea id="invite-revoke-reason" required value={revokeReason} onChange={(event) => setRevokeReason(event.target.value)} /></CommandDialog>
    </div>
  );
}
