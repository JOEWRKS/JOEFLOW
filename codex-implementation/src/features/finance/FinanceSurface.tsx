import { useState } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import { ExportPanel } from '../../components/ExportPanel';
import { Timeline } from '../../components/Timeline';
import { useClaimExplorer } from '../../components/ClaimExplorer';
import { claimsForRole } from '../../domain/selectors';
import type { CommandResult, DomainCommand, DomainState } from '../../domain/types';
import { AdjustmentPanel } from './AdjustmentPanel';
import { PaymentPanel } from './PaymentPanel';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function FinanceSurface({ state, dispatch }: Props) {
  const scopedClaims = claimsForRole(state, 'usr-finance', 'FINANCE');
  const explorer = useClaimExplorer(state, scopedClaims);
  const claims = explorer.claims;
  const [selectedId, setSelectedId] = useState('clm-approved');
  const claim = claims.find((item) => item.id === selectedId) ?? claims[0];
  if (!state.users['usr-finance']?.active || !state.users['usr-finance'].roles.includes('FINANCE')) return <section className="empty-panel critical-callout"><h2>Access unavailable</h2><p>The current Finance account or role is inactive. No governed claim data is displayed.</p></section>;
  if (!scopedClaims.length) return <section className="empty-panel"><h2>No Finance work</h2><p>The authorized payment queue is empty.</p></section>;
  if (!claim) return <>{explorer.controls}<section className="empty-panel"><h2>No matching claims</h2><p>No claims match the current filters.</p></section></>;
  return (<>{explorer.controls}
    <div className="surface-layout">
      <aside className="record-list" aria-label="Finance payment queue">
        <div className="list-heading"><span>Payment queue</span><strong>{claims.length}</strong></div>
        {claims.map((item) => <button key={item.id} type="button" aria-label={`${item.id} · ${item.status}`} className={item.id === claim.id ? 'record-button selected' : 'record-button'} onClick={() => setSelectedId(item.id)}>
          <span>{item.id}</span><small>{item.revisions.at(-1)?.krwAmount.toLocaleString()} KRW · {item.payment.ownerId ? state.users[item.payment.ownerId]?.name : 'Shared'}{item.payment.overdue ? ' · Payment overdue' : ''}</small><StatusBadge status={item.payment.overdue ? 'Payment overdue' : item.status} />
        </button>)}
      </aside>
      <article className="detail-panel card">
        <header className="detail-header"><div><p className="eyebrow">{claim.id}</p><h2>{claim.revisions.at(-1)!.merchant}</h2><span>version {claim.version} · approved revision {claim.approvedRevision}</span></div><StatusBadge status={claim.status} /></header>
        <PaymentPanel claim={claim} state={state} dispatch={dispatch} />
        {claim.status === 'Payment completed' && <AdjustmentPanel claim={claim} state={state} dispatch={dispatch} />}
      </article>
    </div>
    <div className="governed-columns card"><Timeline state={state} role="FINANCE" actorId="usr-finance" /><ExportPanel state={state} role="FINANCE" actorId="usr-finance" dispatch={dispatch} claimIds={claims.map((item) => item.id)} filterSnapshot={explorer.snapshot} /></div>
  </>);
}
