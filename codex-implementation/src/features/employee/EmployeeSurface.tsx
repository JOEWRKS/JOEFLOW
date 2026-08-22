import { useEffect, useRef, useState } from 'react';
import { CommandDialog } from '../../components/CommandDialog';
import { StatusBadge } from '../../components/StatusBadge';
import { claimsForRole } from '../../domain/selectors';
import type { CommandResult, DomainCommand, DomainState } from '../../domain/types';
import { AttachmentPanel } from './AttachmentPanel';
import { ClaimEditor } from './ClaimEditor';
import { RevisionTimeline } from './RevisionTimeline';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function EmployeeSurface({ state, dispatch }: Props) {
  const claims = claimsForRole(state, 'usr-employee', 'EMPLOYEE');
  const [selectedId, setSelectedId] = useState('clm-draft');
  const [deleteOpen, setDeleteOpen] = useState(false);
  const deleteTrigger = useRef<HTMLButtonElement>(null);
  const claim = state.claims[selectedId] ?? claims[0];

  useEffect(() => {
    if (!state.claims[selectedId] && claims[0]) setSelectedId(claims[0].id);
  }, [claims, selectedId, state.claims]);
  if (!claim) return <section className="empty-panel"><h2>No claims</h2><p>Create a draft to begin.</p></section>;

  const command = (type: DomainCommand['type'], input: Record<string, unknown> = {}) => dispatch({
    type, actorId: 'usr-employee', targetId: claim.id, expectedVersion: claim.version,
    idempotencyKey: `ui-${type}-${claim.id}-${claim.version}`, input,
  });

  return (
    <div className="surface-layout">
      <aside className="record-list" aria-label="My claims">
        <div className="list-heading"><span>My claims</span><strong>{claims.length}</strong></div>
        {claims.map((item) => (
          <button key={item.id} type="button" aria-label={`${item.id} · ${item.status}`} className={item.id === claim.id ? 'record-button selected' : 'record-button'} onClick={() => setSelectedId(item.id)}>
            <span>{item.id}</span><small>{item.revisions.at(-1)?.merchant}</small><StatusBadge status={item.status} />
          </button>
        ))}
      </aside>
      <article className="detail-panel card">
        <header className="detail-header">
          <div><p className="eyebrow">{claim.id}</p><h2>{claim.revisions.at(-1)!.merchant}</h2><span>Revision {claim.currentRevision} · version {claim.version}</span></div>
          <StatusBadge status={claim.status} />
        </header>
        <ClaimEditor claim={claim} state={state} dispatch={dispatch} />
        <AttachmentPanel claim={claim} state={state} dispatch={dispatch} />
        <RevisionTimeline claim={claim} />
        <div className="sticky-actions">
          {claim.status === 'Draft' && <>
            <button className="button primary" type="button" onClick={() => command('SUBMIT_CLAIM')}>Submit claim</button>
            <button ref={deleteTrigger} className="button danger-quiet" type="button" onClick={() => setDeleteOpen(true)}>Delete draft</button>
          </>}
          {claim.status === 'Submitted' && <button className="button danger-quiet" type="button" onClick={() => command('WITHDRAW_CLAIM')}>Withdraw claim</button>}
          {claim.status === 'Changes requested' && <button className="button primary" type="button" onClick={() => command('REVISE_CLAIM')}>Create and submit revision {claim.currentRevision + 1}</button>}
        </div>
      </article>
      <CommandDialog open={deleteOpen} title="Delete this draft?" confirmLabel="Delete draft permanently" triggerRef={deleteTrigger}
        destructive onCancel={() => setDeleteOpen(false)} onConfirm={() => { command('DELETE_DRAFT'); setDeleteOpen(false); }}>
        <p>This removes only this unsubmitted draft and its task-owned simulated evidence. This cannot be undone.</p>
      </CommandDialog>
    </div>
  );
}
