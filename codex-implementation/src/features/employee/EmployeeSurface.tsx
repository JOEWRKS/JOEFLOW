import { useEffect, useRef, useState } from 'react';
import { CommandDialog } from '../../components/CommandDialog';
import { StatusBadge } from '../../components/StatusBadge';
import { Timeline } from '../../components/Timeline';
import { useClaimExplorer } from '../../components/ClaimExplorer';
import { claimsForRole } from '../../domain/selectors';
import type { CommandResult, DomainCommand, DomainState } from '../../domain/types';
import { AttachmentPanel } from './AttachmentPanel';
import { ClaimEditor } from './ClaimEditor';
import { RevisionTimeline } from './RevisionTimeline';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function EmployeeSurface({ state, dispatch }: Props) {
  const scopedClaims = claimsForRole(state, 'usr-employee', 'EMPLOYEE');
  const explorer = useClaimExplorer(state, scopedClaims);
  const claims = explorer.claims;
  const [selectedId, setSelectedId] = useState('clm-draft');
  const [deleteOpen, setDeleteOpen] = useState(false);
  const deleteTrigger = useRef<HTMLButtonElement>(null);
  const claim = claims.find((item) => item.id === selectedId) ?? claims[0];

  const createDraft = () => {
    const result = dispatch({
      type: 'CREATE_DRAFT', actorId: 'usr-employee', targetId: 'claim-register', expectedVersion: 0,
      idempotencyKey: `ui-CREATE_DRAFT-${state.nextSequence}`, input: {},
    });
    const auditId = result.auditEventIds[0];
    const createdId = result.state.auditEvents.find((event) => event.id === auditId)?.targetId;
    if (createdId) setSelectedId(createdId);
  };

  useEffect(() => {
    if (!claims.some((item) => item.id === selectedId) && claims[0]) setSelectedId(claims[0].id);
  }, [claims, selectedId]);
  if (!state.users['usr-employee']?.active || !state.users['usr-employee'].roles.includes('EMPLOYEE')) return <section className="empty-panel critical-callout"><h2>Access unavailable</h2><p>The current Employee account or role is inactive. No governed claim or attachment data is displayed.</p></section>;
  if (!scopedClaims.length) return <section className="empty-panel"><h2>No claims</h2><p>Create a draft to begin.</p><button className="button primary" type="button" onClick={createDraft}>Create new claim</button></section>;
  if (!claim) return <>{explorer.controls}<section className="empty-panel"><h2>No matching claims</h2><p>No claims match the current filters.</p></section></>;

  const command = (type: DomainCommand['type'], input: Record<string, unknown> = {}) => dispatch({
    type, actorId: 'usr-employee', targetId: claim.id, expectedVersion: claim.version,
    idempotencyKey: `ui-${type}-${claim.id}-${claim.version}`, input,
  });

  return (<>{explorer.controls}
    <div className="surface-layout">
      <aside className="record-list" aria-label="My claims">
        <div className="list-heading"><span>My claims</span><strong>{claims.length}</strong></div>
        <button className="button primary list-create" type="button" onClick={createDraft}>Create new claim</button>
        {claims.map((item) => (
          <button key={item.id} type="button" aria-label={`${item.id} · ${item.status}`} className={item.id === claim.id ? 'record-button selected' : 'record-button'} onClick={() => setSelectedId(item.id)}>
            <span>{item.id}</span><small>{item.revisions.at(-1)?.merchant}</small><StatusBadge status={item.status} />
          </button>
        ))}
      </aside>
      <article className="detail-panel card">
        <header className="detail-header">
          <div><p className="eyebrow">{claim.id}</p><h2>{claim.revisions.at(-1)!.merchant || 'Untitled claim'}</h2><span>Revision {claim.currentRevision} · version {claim.version}</span></div>
          <StatusBadge status={claim.status} />
        </header>
        <ClaimEditor claim={claim} state={state} dispatch={dispatch} />
        <AttachmentPanel claim={claim} state={state} dispatch={dispatch} />
        <RevisionTimeline claim={claim} />
        <Timeline state={state} role="EMPLOYEE" actorId="usr-employee" />
        <div className="sticky-actions">
          {claim.status === 'Draft' && <>
            <button className="button primary" type="button" onClick={() => command('SUBMIT_CLAIM')}>{claim.currentRevision > 1 ? `Submit revision ${claim.currentRevision}` : 'Submit claim'}</button>
            {claim.currentRevision === 1 && <button ref={deleteTrigger} className="button danger-quiet" type="button" onClick={() => setDeleteOpen(true)}>Delete draft</button>}
          </>}
          {claim.status === 'Submitted' && <button className="button danger-quiet" type="button" onClick={() => command('WITHDRAW_CLAIM')}>Withdraw claim</button>}
          {claim.status === 'Changes requested' && <><button className="button primary" type="button" onClick={() => command('REVISE_CLAIM')}>Create revision {claim.currentRevision + 1}</button><button className="button danger-quiet" type="button" onClick={() => command('WITHDRAW_CLAIM')}>Withdraw claim</button></>}
        </div>
      </article>
      <CommandDialog open={deleteOpen} title="Delete this draft?" confirmLabel="Delete draft permanently" triggerRef={deleteTrigger}
        destructive onCancel={() => setDeleteOpen(false)} onConfirm={() => { command('DELETE_DRAFT'); setDeleteOpen(false); }}>
        <p>This removes only this unsubmitted draft and its task-owned simulated evidence. This cannot be undone.</p>
      </CommandDialog>
    </div>
  </>);
}
