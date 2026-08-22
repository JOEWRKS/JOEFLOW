import { useState } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props { claim: Claim; state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function PaymentPanel({ claim, state, dispatch }: Props) {
  const [scheduledDate, setScheduledDate] = useState(state.now.slice(0, 10));
  const [actualDate, setActualDate] = useState(state.now.slice(0, 10));
  const [method, setMethod] = useState('Bank transfer');
  const [methodDescription, setMethodDescription] = useState('');
  const [reference, setReference] = useState('');
  const [failureReason, setFailureReason] = useState('');
  const [holdReason, setHoldReason] = useState('');
  const [externalExecutionPossible, setExternalExecutionPossible] = useState(false);
  const [verificationOpen, setVerificationOpen] = useState(false);
  const [verification, setVerification] = useState({ result: 'Unclear', channel: '', maskedAccount: '', checkedFrom: '', checkedTo: '', externalReferenceOrResult: '', conclusion: '' });

  const run = (type: DomainCommand['type'], input: Record<string, unknown>) => dispatch({
    type, actorId: 'usr-finance', targetId: claim.id, expectedVersion: claim.version,
    idempotencyKey: `ui-${type}-${claim.id}-${claim.version}-${JSON.stringify(input)}`, input,
  });
  const vf = (key: keyof typeof verification, value: string) => setVerification((current) => ({ ...current, [key]: value }));

  return (
    <section aria-labelledby="payment-panel-title">
      <div className="section-heading">
        <div><p className="eyebrow">Payment lifecycle</p><h3 id="payment-panel-title">Finance transition</h3></div>
        <StatusBadge status={claim.status} />
      </div>
      <div className="ownership-banner">
        <span>Current owner</span><strong>{claim.payment.ownerId ? state.users[claim.payment.ownerId]?.name : 'Shared queue · unclaimed'}</strong>
        {claim.payment.ownerId && <small>Owner: {state.users[claim.payment.ownerId]?.name}</small>}
      </div>

      {claim.status === 'Payment pending' && <div className="inline-form">
        <label>Scheduled date<input value={scheduledDate} onChange={(event) => setScheduledDate(event.target.value)} /></label>
        <button className="button primary" type="button" onClick={() => run('SCHEDULE_PAYMENT', { scheduledDate })}>Claim and schedule payment</button>
      </div>}

      {claim.status === 'Scheduled' && <>
        <div className="form-grid">
          <label>Actual payment date<input value={actualDate} onChange={(event) => setActualDate(event.target.value)} /></label>
          <label>Payment method<select value={method} onChange={(event) => setMethod(event.target.value)}><option>Bank transfer</option><option>Corporate card settlement</option><option>Cash</option><option>Other</option></select></label>
          {method === 'Other' && <label>Other method description<input value={methodDescription} onChange={(event) => setMethodDescription(event.target.value)} /></label>}
          <label>External reference<input value={reference} onChange={(event) => setReference(event.target.value)} /></label>
        </div>
        <div className="button-row"><button className="button primary" type="button" onClick={() => run('COMPLETE_PAYMENT', { actualDate, method, methodDescription, externalReference: reference })}>Record payment completed</button></div>
        <details className="recovery-disclosure"><summary>Failure and hold paths</summary>
          <div className="form-grid compact">
            <label>Payment failure reason<input value={failureReason} onChange={(event) => setFailureReason(event.target.value)} /></label>
            <button className="button danger-quiet" type="button" onClick={() => run('FAIL_PAYMENT', { reason: failureReason })}>Record payment failed</button>
            <label>Payment hold reason<input value={holdReason} onChange={(event) => setHoldReason(event.target.value)} /></label>
            <label><input type="checkbox" checked={externalExecutionPossible} onChange={(event) => setExternalExecutionPossible(event.target.checked)} /> External execution may have occurred</label>
            <button className="button secondary" type="button" onClick={() => run('HOLD_PAYMENT', { reason: holdReason, externalExecutionPossible })}>Place payment on hold</button>
          </div>
        </details>
      </>}

      {claim.status === 'Payment failed' && <>
        <div className="critical-callout"><strong>Duplicate-payment check required</strong><span>{claim.payment.failureReason}</span></div>
        {claim.payment.verification
          ? <div className="verification-summary"><strong>{claim.payment.verification.result} · checked by {claim.payment.verification.checkedBy}</strong><span>{claim.payment.verification.channel} · {claim.payment.verification.maskedAccount} · {claim.payment.verification.conclusion}</span></div>
          : <button className="button secondary" type="button" onClick={() => setVerificationOpen(true)}>Verify execution</button>}
        {verificationOpen && !claim.payment.verification && <div className="verification-form form-grid">
          <label>Verification result<select value={verification.result} onChange={(event) => vf('result', event.target.value)}><option>Unclear</option><option>Not paid</option><option>Paid</option></select></label>
          <label>Payment channel<input value={verification.channel} onChange={(event) => vf('channel', event.target.value)} /></label>
          <label>Masked account<input value={verification.maskedAccount} onChange={(event) => vf('maskedAccount', event.target.value)} /></label>
          <label>Lookup from<input value={verification.checkedFrom} onChange={(event) => vf('checkedFrom', event.target.value)} /></label>
          <label>Lookup to<input value={verification.checkedTo} onChange={(event) => vf('checkedTo', event.target.value)} /></label>
          <label>Reference or lookup result<input value={verification.externalReferenceOrResult} onChange={(event) => vf('externalReferenceOrResult', event.target.value)} /></label>
          <label className="span-2">Verification conclusion<textarea value={verification.conclusion} onChange={(event) => vf('conclusion', event.target.value)} /></label>
          <div className="button-row span-2"><button className="button primary" type="button" onClick={() => run('VERIFY_FAILED_PAYMENT', verification)}>Record verification</button></div>
        </div>}
        {claim.payment.verification?.result === 'Not paid' && <div className="inline-form"><label>New scheduled date<input value={scheduledDate} onChange={(event) => setScheduledDate(event.target.value)} /></label><button className="button primary" type="button" onClick={() => run('RESCHEDULE_PAYMENT', { scheduledDate })}>Reschedule verified payment</button></div>}
        {claim.payment.verification?.result === 'Unclear' && <p className="boundary-note">Execution remains uncertain. Do not retry or create a second payment.</p>}
      </>}

      {claim.status === 'Payment hold' && <><div className="critical-callout"><strong>Payment hold</strong><span>{claim.payment.holdReason} · Admin must reopen through the current manager and a new revision.</span></div>{claim.payment.holdExternalExecutionPossible && !claim.payment.verification && <><button className="button secondary" type="button" onClick={() => setVerificationOpen(true)}>Verify held payment execution</button>{verificationOpen && <div className="verification-form form-grid"><label>Verification result<select value={verification.result} onChange={(event) => vf('result', event.target.value)}><option>Unclear</option><option>Not paid</option><option>Paid</option></select></label><label>Payment channel<input value={verification.channel} onChange={(event) => vf('channel', event.target.value)} /></label><label>Masked account<input value={verification.maskedAccount} onChange={(event) => vf('maskedAccount', event.target.value)} /></label><label>Lookup from<input value={verification.checkedFrom} onChange={(event) => vf('checkedFrom', event.target.value)} /></label><label>Lookup to<input value={verification.checkedTo} onChange={(event) => vf('checkedTo', event.target.value)} /></label><label>Reference or lookup result<input value={verification.externalReferenceOrResult} onChange={(event) => vf('externalReferenceOrResult', event.target.value)} /></label><label className="span-2">Verification conclusion<textarea value={verification.conclusion} onChange={(event) => vf('conclusion', event.target.value)} /></label><button className="button primary span-2" type="button" onClick={() => run('VERIFY_HELD_PAYMENT', verification)}>Record held-payment verification</button></div>}</>}</>}
      {claim.status === 'Payment completed' && <div className="success-callout"><strong>Original payment is immutable</strong><span>{claim.payment.actualDate} · {claim.payment.method} · ref {claim.payment.externalReference}</span></div>}
    </section>
  );
}
