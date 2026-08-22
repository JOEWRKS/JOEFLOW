import { useRef, useState } from 'react';
import { CommandDialog } from '../../components/CommandDialog';
import { StatusBadge } from '../../components/StatusBadge';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props { claim: Claim; state: DomainState; dispatch: (command: DomainCommand) => CommandResult }
type DialogAction = 'REQUEST_CHANGES' | 'FINAL_REJECT_CLAIM' | 'REVOKE_APPROVAL';

const DIALOG_META: Record<DialogAction, { title: string; field: string; confirm: string; destructive?: boolean }> = {
  REQUEST_CHANGES: { title: 'Request changes', field: 'Manager comment', confirm: 'Send changes request' },
  FINAL_REJECT_CLAIM: { title: 'Finally reject this claim?', field: 'Final rejection reason', confirm: 'Finally reject claim', destructive: true },
  REVOKE_APPROVAL: { title: 'Revoke this approval?', field: 'Revocation reason', confirm: 'Revoke and request revision', destructive: true },
};

export function ReviewPanel({ claim, state, dispatch }: Props) {
  const [dialogAction, setDialogAction] = useState<DialogAction>();
  const [comment, setComment] = useState('');
  const dialogTrigger = useRef<HTMLButtonElement>(null);
  const revision = claim.revisions.at(-1)!;
  const age = Math.max(0, Math.floor((Date.parse(`${state.now.slice(0, 10)}T00:00:00Z`) - Date.parse(`${revision.expenseDate}T00:00:00Z`)) / 86_400_000));

  const run = (type: DomainCommand['type'], input: Record<string, unknown> = {}) => dispatch({
    type, actorId: 'usr-manager', targetId: claim.id, expectedVersion: claim.version,
    idempotencyKey: `ui-${type}-${claim.id}-${claim.version}`, input: { revision: claim.currentRevision, ...input },
  });
  const open = (action: DialogAction, trigger: HTMLButtonElement) => {
    dialogTrigger.current = trigger;
    setComment('');
    setDialogAction(action);
  };
  const confirm = () => {
    if (!dialogAction) return;
    run(dialogAction, { comment });
    setDialogAction(undefined);
  };

  return (
    <article className="detail-panel card">
      <header className="detail-header">
        <div><p className="eyebrow">{claim.id}</p><h2>{revision.merchant}</h2><span>Exact review target: revision {claim.currentRevision} · version {claim.version}</span></div>
        <StatusBadge status={claim.status} />
      </header>
      <section>
        <div className="section-heading"><div><p className="eyebrow">Expense evidence</p><h3>Review facts</h3></div><strong>{revision.krwAmount.toLocaleString()} KRW</strong></div>
        <dl className="facts-grid">
          <div><dt>Employee</dt><dd>{state.users[claim.employeeId]?.name}</dd></div>
          <div><dt>Business purpose</dt><dd>{revision.businessPurpose}</dd></div>
          <div><dt>Expense age</dt><dd>{age} days {age > 90 ? `· ${revision.lateReason || 'Reason missing'}` : '· within 90 days'}</dd></div>
          <div><dt>Category snapshot</dt><dd>{revision.categoryNameSnapshot} · {revision.categoryId}</dd></div>
          <div><dt>Original / conversion</dt><dd>{revision.originalAmount.toLocaleString()} {revision.currency}{revision.currency !== 'KRW' ? ` × ${revision.exchangeRate} = ${revision.krwAmount.toLocaleString()} KRW` : ''}</dd></div>
          <div><dt>Likely duplicate</dt><dd>{revision.duplicateReason || 'No duplicate flag'}</dd></div>
        </dl>
      </section>
      <section>
        <div className="section-heading"><div><p className="eyebrow">Immutable context</p><h3>Revision history</h3></div><span>{claim.revisions.length} revisions</span></div>
        <div className="revision-strip">{claim.revisions.map((item) => <span key={item.number} className={item.number === claim.currentRevision ? 'current' : ''}>rev {item.number}{item.submittedAt ? ' · submitted' : ' · draft'}</span>)}</div>
      </section>
      <div className="sticky-actions">
        {claim.status === 'Submitted' && <>
          <button className="button primary" type="button" onClick={() => run('APPROVE_CLAIM')}>Approve revision {claim.currentRevision}</button>
          <button className="button secondary" type="button" onClick={(event) => open('REQUEST_CHANGES', event.currentTarget)}>Request changes</button>
          <button className="button danger-quiet" type="button" onClick={(event) => open('FINAL_REJECT_CLAIM', event.currentTarget)}>Final reject</button>
        </>}
        {claim.status === 'Payment pending' && <button className="button danger-quiet" type="button" onClick={(event) => open('REVOKE_APPROVAL', event.currentTarget)}>Revoke approval</button>}
        {claim.status === 'Scheduled' && <span className="boundary-note">Revocation closed when Finance scheduled payment.</span>}
      </div>
      {dialogAction && <CommandDialog open title={DIALOG_META[dialogAction].title} confirmLabel={DIALOG_META[dialogAction].confirm}
        triggerRef={dialogTrigger} destructive={DIALOG_META[dialogAction].destructive} onCancel={() => setDialogAction(undefined)} onConfirm={confirm}>
        <label htmlFor="manager-comment">{DIALOG_META[dialogAction].field}</label>
        <textarea id="manager-comment" required value={comment} onChange={(event) => setComment(event.target.value)} />
        <p className="helper-text">This outcome is pinned to revision {claim.currentRevision} and version {claim.version}. A stale response commits nothing.</p>
      </CommandDialog>}
    </article>
  );
}
