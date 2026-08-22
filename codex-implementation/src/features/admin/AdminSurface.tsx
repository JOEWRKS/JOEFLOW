import { useRef, useState } from 'react';
import { CommandDialog } from '../../components/CommandDialog';
import { ExportPanel } from '../../components/ExportPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { Timeline } from '../../components/Timeline';
import type { CommandResult, DomainCommand, DomainState, Role } from '../../domain/types';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }
type Tab = 'Invitations' | 'Accounts & roles' | 'Categories' | 'Holds & reassignment' | 'Operational warnings' | 'Audit & export';
const TABS: Tab[] = ['Invitations', 'Accounts & roles', 'Categories', 'Holds & reassignment', 'Operational warnings', 'Audit & export'];
const ROLES: Role[] = ['EMPLOYEE', 'MANAGER', 'FINANCE', 'ADMIN'];

export function AdminSurface({ state, dispatch }: Props) {
  const [tab, setTab] = useState<Tab>('Invitations');
  const [email, setEmail] = useState('');
  const [inviteRoles, setInviteRoles] = useState<Role[]>(['EMPLOYEE']);
  const [inviteManager, setInviteManager] = useState('usr-manager');
  const [activationEmail, setActivationEmail] = useState('');
  const [activationName, setActivationName] = useState('');
  const [revokeId, setRevokeId] = useState<string>();
  const [revokeReason, setRevokeReason] = useState('');
  const revokeTrigger = useRef<HTMLButtonElement>(null);
  const [userId, setUserId] = useState('usr-employee');
  const [accountRoles, setAccountRoles] = useState<Role[]>(state.users['usr-employee'].roles);
  const [accountReason, setAccountReason] = useState('');
  const [directManagerId, setDirectManagerId] = useState(state.users['usr-employee'].managerId ?? '');
  const [categoryId, setCategoryId] = useState('CAT-001');
  const [categoryName, setCategoryName] = useState(state.categories['CAT-001'].name);
  const [categoryReason, setCategoryReason] = useState('');
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryReason, setNewCategoryReason] = useState('');
  const [claimId, setClaimId] = useState('clm-completed');
  const [governanceReason, setGovernanceReason] = useState('');
  const [managerId, setManagerId] = useState('usr-manager-other');
  const [financeId, setFinanceId] = useState('usr-finance-other');

  const run = (type: DomainCommand['type'], targetId: string, expectedVersion: number, input: Record<string, unknown>) => dispatch({
    type, actorId: 'usr-admin', targetId, expectedVersion,
    idempotencyKey: `ui-${type}-${targetId}-${expectedVersion}-${JSON.stringify(input)}`, input,
  });
  const selectedUser = state.users[userId];
  const selectedCategory = state.categories[categoryId];
  const selectedClaim = state.claims[claimId];
  const toggleRole = (role: Role, collection: Role[], change: (next: Role[]) => void) => change(collection.includes(role) ? collection.filter((item) => item !== role) : [...collection, role]);
  const activateInvitation = () => {
    const invitation = Object.values(state.invitations).find((item) => item.status === 'Pending' && item.email.toLowerCase() === activationEmail.trim().toLowerCase());
    if (!invitation) return;
    dispatch({
      type: 'ACCEPT_INVITATION', actorId: 'invitee', targetId: invitation.id, expectedVersion: invitation.version,
      idempotencyKey: `ui-ACCEPT_INVITATION-${invitation.id}-${invitation.version}-${activationEmail}`, input: { email: activationEmail, name: activationName },
    });
  };

  return (
    <div className="admin-surface card">
      <div className="admin-tabs" role="tablist" aria-label="Admin modules">
        {TABS.map((item) => <button key={item} type="button" role="tab" aria-selected={item === tab} onClick={() => setTab(item)}>{item}</button>)}
      </div>
      <div className="admin-module" role="tabpanel">
        {tab === 'Invitations' && <section aria-labelledby="invitation-title">
          <div className="section-heading"><div><p className="eyebrow">Invite-only access</p><h2 id="invitation-title">Invitation lifecycle</h2></div><span>7-day expiry · latest link only</span></div>
          <div className="form-grid">
            <label>Invite email<input value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label>Invited direct manager<select value={inviteManager} onChange={(event) => setInviteManager(event.target.value)}>{Object.values(state.users).filter((user) => user.active && user.roles.includes('MANAGER')).map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}</select></label>
            <fieldset className="role-fieldset"><legend>Invitation roles</legend>{ROLES.map((role) => <label key={role}><input type="checkbox" aria-label={`Invite ${role} role`} checked={inviteRoles.includes(role)} onChange={() => toggleRole(role, inviteRoles, setInviteRoles)} /> {role}</label>)}</fieldset>
          </div>
          <div className="button-row"><button className="button primary" type="button" onClick={() => run('ISSUE_INVITATION', 'invitation-register', 0, { email, roles: inviteRoles, managerId: inviteManager })}>Issue invitation</button><button className="button secondary" type="button" onClick={() => run('EXPIRE_INVITATIONS', 'invitation-expiry-job', 0, {})}>Run invitation expiry check</button></div>
          <div className="readonly-note activation-fixture"><strong>Invitation link activation fixture</strong><span>This local surface simulates the separate invited-link entry. It does not implement authentication or email delivery.</span><div className="form-grid"><label>Activation email<input value={activationEmail} onChange={(event) => setActivationEmail(event.target.value)} /></label><label>Activation display name<input value={activationName} onChange={(event) => setActivationName(event.target.value)} /></label></div><button className="button secondary" type="button" onClick={activateInvitation}>Activate invited account</button></div>
          <div className="governance-list">{Object.values(state.invitations).map((invitation) => <article key={invitation.id}>
            <div><strong>{invitation.email}</strong><span>{invitation.roles.join(' + ')} · Expires {invitation.expiresAt.slice(0, 10)} · version {invitation.version}</span></div><StatusBadge status={invitation.status} />
            {invitation.status === 'Pending' && <div className="button-row"><button className="button secondary" type="button" onClick={() => run('REISSUE_INVITATION', invitation.id, invitation.version, {})}>Reissue invitation {invitation.id}</button><button ref={revokeTrigger} className="button danger-quiet" type="button" onClick={() => { setRevokeId(invitation.id); setRevokeReason(''); }}>Revoke invitation {invitation.id}</button></div>}
          </article>)}</div>
        </section>}

        {tab === 'Accounts & roles' && <section aria-labelledby="accounts-title">
          <div className="section-heading"><div><p className="eyebrow">Latest authorization</p><h2 id="accounts-title">Accounts, roles, and sessions</h2></div><span>Versioned Admin writes</span></div>
          <div className="form-grid"><label>Managed user<select value={userId} onChange={(event) => { const id = event.target.value; setUserId(id); setAccountRoles(state.users[id].roles); setDirectManagerId(state.users[id].managerId ?? ''); setAccountReason(''); }}>{Object.values(state.users).map((user) => <option key={user.id} value={user.id}>{user.name} · {user.id}</option>)}</select></label><label>Account change reason<input value={accountReason} onChange={(event) => setAccountReason(event.target.value)} /></label></div>
          <fieldset className="role-fieldset"><legend>Current roles</legend>{ROLES.map((role) => <label key={role}><input type="checkbox" aria-label={`${role} role`} checked={accountRoles.includes(role)} onChange={() => toggleRole(role, accountRoles, setAccountRoles)} /> {role}</label>)}</fieldset>
          <div className="account-summary"><strong>{selectedUser.name}</strong><span>{selectedUser.active ? 'Active' : 'Inactive'} · auth version {selectedUser.authVersion}</span><small>{selectedUser.roles.join(' + ')} · manager {selectedUser.managerId ?? 'not assigned'}</small></div>
          <div className="form-grid compact"><label>Direct manager<select value={directManagerId} onChange={(event) => setDirectManagerId(event.target.value)}><option value="">Not assigned</option>{Object.values(state.users).filter((user) => user.active && user.roles.includes('MANAGER') && user.id !== selectedUser.id).map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}</select></label></div>
          <div className="button-row"><button className="button secondary" type="button" onClick={() => run('UPDATE_ACCOUNT', selectedUser.id, selectedUser.version, { active: selectedUser.active, roles: accountRoles, reason: accountReason })}>Save account roles</button><button className="button secondary" type="button" onClick={() => run('ASSIGN_MANAGER', selectedUser.id, selectedUser.version, { managerId: directManagerId, reason: accountReason })}>Assign direct manager</button><button className={selectedUser.active ? 'button danger-quiet' : 'button primary'} type="button" onClick={() => run('UPDATE_ACCOUNT', selectedUser.id, selectedUser.version, { active: !selectedUser.active, roles: accountRoles, reason: accountReason })}>{selectedUser.active ? 'Deactivate account' : 'Activate account'}</button></div>
        </section>}

        {tab === 'Categories' && <section aria-labelledby="categories-title">
          <div className="section-heading"><div><p className="eyebrow">Stable IDs</p><h2 id="categories-title">Expense categories</h2></div><span>{Object.values(state.categories).filter((item) => item.active).length} active</span></div>
          <div className="readonly-note"><strong>Create stable category</strong><div className="form-grid"><label>New category name<input value={newCategoryName} onChange={(event) => setNewCategoryName(event.target.value)} /></label><label>New category reason<input value={newCategoryReason} onChange={(event) => setNewCategoryReason(event.target.value)} /></label></div><button className="button primary" type="button" onClick={() => run('CREATE_CATEGORY', 'category-register', 0, { name: newCategoryName, reason: newCategoryReason })}>Create category</button></div>
          <div className="form-grid"><label>Managed category<select value={categoryId} onChange={(event) => { const id = event.target.value; setCategoryId(id); setCategoryName(state.categories[id].name); }}>{Object.values(state.categories).map((item) => <option key={item.id} value={item.id}>{item.id} · {item.name}</option>)}</select></label><label>Category name<input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} /></label><label className="span-2">Category change reason<input value={categoryReason} onChange={(event) => setCategoryReason(event.target.value)} /></label></div>
          <div className="button-row"><button className="button secondary" type="button" onClick={() => run('UPDATE_CATEGORY', selectedCategory.id, selectedCategory.version, { name: categoryName, active: selectedCategory.active, reason: categoryReason })}>Rename category</button><button className={selectedCategory.active ? 'button danger-quiet' : 'button primary'} type="button" onClick={() => run('UPDATE_CATEGORY', selectedCategory.id, selectedCategory.version, { name: categoryName, active: !selectedCategory.active, reason: categoryReason })}>{selectedCategory.active ? 'Deactivate category' : 'Activate category'}</button></div>
          <p className="helper-text">Submitted revisions retain the category name snapshot captured at submission. Zero active categories blocks new submission, not governance.</p>
        </section>}

        {tab === 'Holds & reassignment' && <section aria-labelledby="holds-title">
          <div className="section-heading"><div><p className="eyebrow">Atomic governance</p><h2 id="holds-title">Legal holds and ownership</h2></div><span>Required reason</span></div>
          <div className="form-grid"><label>Governed claim<select value={claimId} onChange={(event) => { setClaimId(event.target.value); setGovernanceReason(''); }}>{Object.values(state.claims).map((claim) => <option key={claim.id} value={claim.id}>{claim.id} · {claim.status}</option>)}</select></label><label>Legal hold reason<input value={governanceReason} onChange={(event) => setGovernanceReason(event.target.value)} /></label><label>Replacement manager<select value={managerId} onChange={(event) => setManagerId(event.target.value)}>{Object.values(state.users).filter((user) => user.active && user.roles.includes('MANAGER')).map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}</select></label><label>Replacement Finance owner<select value={financeId} onChange={(event) => setFinanceId(event.target.value)}>{Object.values(state.users).filter((user) => user.active && user.roles.includes('FINANCE')).map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}</select></label></div>
          <div className="hold-summary"><strong>{selectedClaim.legalHold ? `Held · ${selectedClaim.legalHold.reason}` : 'No legal hold'}</strong><span>{selectedClaim.id} · {selectedClaim.status} · version {selectedClaim.version}</span></div>
          <div className="button-row">{selectedClaim.legalHold ? <button className="button danger-quiet" type="button" onClick={() => run('RELEASE_LEGAL_HOLD', selectedClaim.id, selectedClaim.version, { reason: governanceReason })}>Release legal hold</button> : <button className="button primary" type="button" onClick={() => run('SET_LEGAL_HOLD', selectedClaim.id, selectedClaim.version, { reason: governanceReason })}>Set legal hold</button>}<button className="button secondary" type="button" disabled={selectedClaim.status !== 'Submitted' || state.users[selectedClaim.managerId]?.active} onClick={() => run('REASSIGN_MANAGER', selectedClaim.id, selectedClaim.version, { managerId, reason: governanceReason })}>Reassign unfinished review</button><button className="button secondary" type="button" disabled={!selectedClaim.payment.ownerId} onClick={() => run('REASSIGN_FINANCE', selectedClaim.id, selectedClaim.version, { financeId, reason: governanceReason })}>Reassign Finance owner</button>{selectedClaim.status === 'Payment hold' && <button className="button danger-quiet" type="button" onClick={() => run('REOPEN_HOLD', selectedClaim.id, selectedClaim.version, { reason: governanceReason })}>Reopen held claim for correction</button>}</div>
          <div className="readonly-note"><strong>Reassignment boundary</strong><span>Manager reassignment requires the pinned manager to be inactive. Finance reassignment preserves the payment transition and changes only current owner.</span></div>
        </section>}

        {tab === 'Operational warnings' && <section aria-labelledby="warnings-title">
          <div className="section-heading"><div><p className="eyebrow">Delivery is not domain truth</p><h2 id="warnings-title">Operational warnings</h2></div><span>{state.warnings.filter((warning) => !warning.resolved).length} open</span></div>
          <div className="button-row"><button className="button primary" type="button" onClick={() => run('RUN_DAILY_OPERATIONS', `daily-${state.now.slice(0, 10)}`, 0, { scheduledAt: `${state.now.slice(0, 10)}T02:00:00+09:00` })}>Run deterministic 02:00 KST operations</button><button className="button secondary" type="button" onClick={() => run('RUN_DELIVERY_RETRIES', `delivery-retries-${state.auditEvents.length}`, 0, { failedDeliveryIds: state.deliveries.filter((item) => item.status === 'Queued').map((item) => item.id) })}>Record due delivery failures</button></div>
          <div className="governance-list">{state.warnings.map((warning) => { const delivery = state.deliveries.find((item) => item.id === warning.targetId); return <article key={warning.id}><div><strong>{warning.message}</strong><span>{delivery ? `${delivery.channel} · attempts ${delivery.attempts} · ${delivery.status}` : 'Scheduled operations warning'}</span></div><StatusBadge status={warning.resolved ? 'Resolved' : 'Operational warning'} />{delivery && <button className="button secondary" type="button" disabled={delivery.manualRetryUsed} onClick={() => run('RETRY_DELIVERY', delivery.id, delivery.version, {})}>Retry delivery once</button>}</article>; })}</div>
        </section>}

        {tab === 'Audit & export' && <div className="governed-columns"><Timeline state={state} role="ADMIN" actorId="usr-admin" raw /><ExportPanel state={state} role="ADMIN" actorId="usr-admin" dispatch={dispatch} /></div>}
      </div>
      <CommandDialog open={Boolean(revokeId)} title="Revoke pending invitation?" confirmLabel="Confirm invitation revocation" triggerRef={revokeTrigger} destructive onCancel={() => setRevokeId(undefined)} onConfirm={() => { if (!revokeId) return; const invitation = state.invitations[revokeId]; run('REVOKE_INVITATION', revokeId, invitation.version, { reason: revokeReason }); setRevokeId(undefined); }}><label htmlFor="invite-revoke-reason">Revocation reason</label><textarea id="invite-revoke-reason" required value={revokeReason} onChange={(event) => setRevokeReason(event.target.value)} /></CommandDialog>
    </div>
  );
}
