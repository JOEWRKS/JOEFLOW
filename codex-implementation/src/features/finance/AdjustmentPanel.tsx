import { useState } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import { adjustmentTotals } from '../../domain/selectors';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props { claim: Claim; state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function AdjustmentPanel({ claim, state, dispatch }: Props) {
  const totals = adjustmentTotals(state, claim.id);
  const adjustments = claim.adjustmentIds.map((id) => state.adjustments[id]).filter(Boolean);
  const active = adjustments.find((item) => ['In progress', 'Needs verification'].includes(item.status));
  const [creating, setCreating] = useState(false);
  const [kind, setKind] = useState('Recovery');
  const [amount, setAmount] = useState('0');
  const [reason, setReason] = useState('');
  const [reference, setReference] = useState('');
  const [failureReason, setFailureReason] = useState('');
  const [resolution, setResolution] = useState('Unclear');
  const [resolutionNote, setResolutionNote] = useState('');
  const [actualAmount, setActualAmount] = useState('');
  const run = (type: DomainCommand['type'], input: Record<string, unknown>) => dispatch({
    type, actorId: 'usr-finance', targetId: claim.id, expectedVersion: claim.version,
    idempotencyKey: `ui-${type}-${claim.id}-${claim.version}-${JSON.stringify(input)}`, input,
  });

  return (
    <section aria-labelledby="adjustment-title">
      <div className="section-heading"><div><p className="eyebrow">Settlement integrity</p><h3 id="adjustment-title">Adjustments</h3></div><button className="button secondary" type="button" disabled={Boolean(active)} onClick={() => setCreating(true)}>Create adjustment</button></div>
      <div className="totals-grid">
        <div><span>Original paid</span><strong>{totals.originalKrw.toLocaleString()} KRW</strong></div>
        <div><span>Completed recoveries</span><strong>−{totals.recoveredKrw.toLocaleString()} KRW</strong></div>
        <div><span>Completed additions</span><strong>+{totals.addedKrw.toLocaleString()} KRW</strong></div>
        <div className="net"><span>Net settled</span><strong>{totals.netKrw.toLocaleString()} KRW</strong></div>
      </div>
      {creating && !active && <div className="form-grid adjustment-form">
        <label>Adjustment kind<select value={kind} onChange={(event) => setKind(event.target.value)}><option>Recovery</option><option>Additional payment</option></select></label>
        <label>Adjustment amount KRW<input inputMode="numeric" value={amount} onChange={(event) => setAmount(event.target.value)} /></label>
        <label className="span-2">Adjustment reason<textarea value={reason} onChange={(event) => setReason(event.target.value)} /></label>
        <div className="button-row span-2"><button className="button secondary" type="button" onClick={() => setCreating(false)}>Cancel adjustment</button><button className="button primary" type="button" onClick={() => { run('CREATE_ADJUSTMENT', { kind, amountKrw: Number(amount), reason }); setCreating(false); }}>Start adjustment</button></div>
      </div>}
      <div className="adjustment-list">
        {adjustments.map((item) => <article key={item.id} className="adjustment-card">
          <div className="section-heading"><div><strong>{item.id} · {item.kind}</strong><span>{item.amountKrw.toLocaleString()} KRW · {item.reason}</span></div><StatusBadge status={item.status} /></div>
          {item.status === 'In progress' && <div className="form-grid compact">
            <label>Adjustment actual date<input value={state.now.slice(0, 10)} readOnly /></label>
            <label>Adjustment external reference<input value={reference} onChange={(event) => setReference(event.target.value)} /></label>
            <button className="button primary" type="button" onClick={() => run('COMPLETE_ADJUSTMENT', { adjustmentId: item.id, actualDate: state.now.slice(0, 10), externalReference: reference })}>Complete adjustment</button>
            <label>Adjustment failure reason<input value={failureReason} onChange={(event) => setFailureReason(event.target.value)} /></label>
            <button className="button danger-quiet" type="button" onClick={() => run('FAIL_ADJUSTMENT', { adjustmentId: item.id, reason: failureReason })}>Record adjustment failed</button>
          </div>}
          {['Failed', 'Needs verification'].includes(item.status) && <div className="form-grid compact">
            <label>Execution result<select value={resolution} onChange={(event) => setResolution(event.target.value)}><option>Unclear</option><option>Not executed</option><option>Executed</option></select></label>
            <label>Resolution note<input value={resolutionNote} onChange={(event) => setResolutionNote(event.target.value)} /></label>
            {resolution === 'Executed' && <><label>Executed actual amount KRW<input inputMode="numeric" value={actualAmount} onChange={(event) => setActualAmount(event.target.value)} /></label><label>Executed actual date<input value={state.now.slice(0, 10)} readOnly /></label><label>Executed external reference<input value={reference} onChange={(event) => setReference(event.target.value)} /></label></>}
            <button className="button primary" type="button" onClick={() => run('RESOLVE_ADJUSTMENT', { adjustmentId: item.id, result: resolution, note: resolutionNote, actualAmountKrw: Number(actualAmount), actualDate: state.now.slice(0, 10), externalReference: reference })}>Resolve adjustment uncertainty</button>
          </div>}
          {item.verification && <small>Append-only verification: {item.verification.result} · {item.verification.checkedBy} · {item.verification.note}</small>}
        </article>)}
      </div>
      <p className="helper-text">Failed and cancelled adjustments stay in history but contribute zero. Needs verification blocks new adjustments.</p>
    </section>
  );
}
