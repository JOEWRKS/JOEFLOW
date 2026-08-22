import { useState } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import type { CommandResult, DomainCommand, DomainState } from '../../domain/types';
import { AdjustmentPanel } from './AdjustmentPanel';
import { PaymentPanel } from './PaymentPanel';

interface Props { state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function FinanceSurface({ state, dispatch }: Props) {
  const claims = Object.values(state.claims).filter((claim) => ['Payment pending', 'Scheduled', 'Payment failed', 'Payment hold', 'Payment completed'].includes(claim.status));
  const [selectedId, setSelectedId] = useState('clm-approved');
  const claim = state.claims[selectedId] ?? claims[0];
  if (!claim) return <section className="empty-panel"><h2>No Finance work</h2><p>The authorized payment queue is empty.</p></section>;
  return (
    <div className="surface-layout">
      <aside className="record-list" aria-label="Finance payment queue">
        <div className="list-heading"><span>Payment queue</span><strong>{claims.length}</strong></div>
        {claims.map((item) => <button key={item.id} type="button" aria-label={`${item.id} · ${item.status}`} className={item.id === claim.id ? 'record-button selected' : 'record-button'} onClick={() => setSelectedId(item.id)}>
          <span>{item.id}</span><small>{item.revisions.at(-1)?.krwAmount.toLocaleString()} KRW · {item.payment.ownerId ? state.users[item.payment.ownerId]?.name : 'Shared'}</small><StatusBadge status={item.status} />
        </button>)}
      </aside>
      <article className="detail-panel card">
        <header className="detail-header"><div><p className="eyebrow">{claim.id}</p><h2>{claim.revisions.at(-1)!.merchant}</h2><span>version {claim.version} · approved revision {claim.approvedRevision}</span></div><StatusBadge status={claim.status} /></header>
        <PaymentPanel claim={claim} state={state} dispatch={dispatch} />
        {claim.status === 'Payment completed' && <AdjustmentPanel claim={claim} state={state} dispatch={dispatch} />}
      </article>
    </div>
  );
}
