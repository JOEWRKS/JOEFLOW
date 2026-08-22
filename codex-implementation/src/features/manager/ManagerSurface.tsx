import { useState } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import { Timeline } from '../../components/Timeline';
import { useClaimExplorer } from '../../components/ClaimExplorer';
import { claimsForRole } from '../../domain/selectors';
import type { CommandResult, DomainCommand, DomainState } from '../../domain/types';
import { ReviewPanel } from './ReviewPanel';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function ManagerSurface({ state, dispatch }: Props) {
  const scopedClaims = claimsForRole(state, 'usr-manager', 'MANAGER');
  const explorer = useClaimExplorer(state, scopedClaims);
  const claims = explorer.claims;
  const [selectedId, setSelectedId] = useState('clm-submitted');
  const selected = claims.find((claim) => claim.id === selectedId) ?? claims[0];
  if (!state.users['usr-manager']?.active || !state.users['usr-manager'].roles.includes('MANAGER')) return <section className="empty-panel critical-callout"><h2>Access unavailable</h2><p>The current Manager account or role is inactive. No governed claim data is displayed.</p></section>;
  if (!scopedClaims.length) return <section className="empty-panel"><h2>No assigned claims</h2><p>The current manager queue is empty.</p></section>;
  if (!selected) return <>{explorer.controls}<section className="empty-panel"><h2>No matching claims</h2><p>No claims match the current filters.</p></section></>;
  return (<>{explorer.controls}
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
    <div className="card governed-columns"><Timeline state={state} role="MANAGER" actorId="usr-manager" /></div>
  </>);
}
