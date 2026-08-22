import { useState } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import { claimsForRole } from '../../domain/selectors';
import type { CommandResult, DomainCommand, DomainState } from '../../domain/types';
import { ReviewPanel } from './ReviewPanel';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function ManagerSurface({ state, dispatch }: Props) {
  const claims = claimsForRole(state, 'usr-manager', 'MANAGER');
  const [selectedId, setSelectedId] = useState('clm-submitted');
  const selected = state.claims[selectedId] ?? claims[0];
  if (!selected) return <section className="empty-panel"><h2>No assigned claims</h2><p>The current manager queue is empty.</p></section>;
  return (
    <div className="surface-layout">
      <aside className="record-list" aria-label="Assigned review queue">
        <div className="list-heading"><span>Assigned queue</span><strong>{claims.length}</strong></div>
        {claims.map((claim) => (
          <button key={claim.id} type="button" aria-label={`${claim.id} · ${claim.status}`} className={claim.id === selected.id ? 'record-button selected' : 'record-button'} onClick={() => setSelectedId(claim.id)}>
            <span>{claim.id}</span><small>{state.users[claim.employeeId]?.name} · rev {claim.currentRevision}</small><StatusBadge status={claim.status} />
          </button>
        ))}
      </aside>
      <ReviewPanel claim={selected} state={state} dispatch={dispatch} />
    </div>
  );
}
