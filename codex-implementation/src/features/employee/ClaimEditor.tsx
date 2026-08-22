import { useEffect, useState } from 'react';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props {
  claim: Claim;
  state: DomainState;
  dispatch: (command: DomainCommand) => CommandResult;
}

export function ClaimEditor({ claim, state, dispatch }: Props) {
  const revision = claim.revisions.at(-1)!;
  const [form, setForm] = useState(() => ({
    merchant: revision.merchant,
    expenseDate: revision.expenseDate,
    categoryId: revision.categoryId,
    originalAmount: String(revision.originalAmount),
    currency: revision.currency,
    krwAmount: String(revision.krwAmount),
    exchangeRate: String(revision.exchangeRate ?? ''),
    businessPurpose: revision.businessPurpose,
    duplicateReason: revision.duplicateReason ?? '',
    lateReason: revision.lateReason ?? '',
  }));

  useEffect(() => {
    setForm({
      merchant: revision.merchant, expenseDate: revision.expenseDate, categoryId: revision.categoryId,
      originalAmount: String(revision.originalAmount), currency: revision.currency, krwAmount: String(revision.krwAmount),
      exchangeRate: String(revision.exchangeRate ?? ''), businessPurpose: revision.businessPurpose,
      duplicateReason: revision.duplicateReason ?? '', lateReason: revision.lateReason ?? '',
    });
  }, [claim.id, claim.version, revision]);

  const field = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }));
  const save = () => dispatch({
    type: 'UPDATE_DRAFT', actorId: 'usr-employee', targetId: claim.id, expectedVersion: claim.version,
    idempotencyKey: `ui-save-${claim.id}-${claim.version}`,
    input: { ...form, originalAmount: Number(form.originalAmount), krwAmount: Number(form.krwAmount), exchangeRate: form.exchangeRate ? Number(form.exchangeRate) : undefined },
  });

  if (claim.status !== 'Draft') {
    return (
      <div className="readonly-note">
        <strong>Revision {claim.currentRevision} is read-only</strong>
        <span>Create a new revision only after an explicit Changes requested outcome.</span>
      </div>
    );
  }

  return (
    <section aria-labelledby="claim-editor-title">
      <div className="section-heading">
        <div><p className="eyebrow">Draft editor</p><h3 id="claim-editor-title">Expense details</h3></div>
        <span className="autosave-state"><span aria-hidden="true">✓</span> Saved · generation {claim.version}</span>
      </div>
      <div className="form-grid">
        <label>Merchant<input required value={form.merchant} onChange={(event) => field('merchant', event.target.value)} /></label>
        <label>Expense date<input required inputMode="numeric" value={form.expenseDate} onChange={(event) => field('expenseDate', event.target.value)} aria-describedby="expense-date-help" /></label>
        <small id="expense-date-help">Asia/Seoul date. Future dates are blocked; over 90 days needs a reason.</small>
        <label>Category<select required value={form.categoryId} onChange={(event) => field('categoryId', event.target.value)}>
          {Object.values(state.categories).filter((category) => category.active).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
        </select></label>
        <label>Original amount<input required inputMode="decimal" value={form.originalAmount} onChange={(event) => field('originalAmount', event.target.value)} /></label>
        <label>Currency<select value={form.currency} onChange={(event) => field('currency', event.target.value)}><option>KRW</option><option>USD</option><option>JPY</option><option>EUR</option></select></label>
        <label>KRW claim amount<input required inputMode="numeric" value={form.krwAmount} onChange={(event) => field('krwAmount', event.target.value)} /></label>
        {form.currency !== 'KRW' && <label>Applied KRW exchange rate<input required inputMode="decimal" value={form.exchangeRate} onChange={(event) => field('exchangeRate', event.target.value)} /></label>}
        <label className="span-2">Business purpose<textarea required value={form.businessPurpose} onChange={(event) => field('businessPurpose', event.target.value)} /></label>
        <label>Likely duplicate reason<input value={form.duplicateReason} onChange={(event) => field('duplicateReason', event.target.value)} /></label>
        <label>Over-90-day reason<input value={form.lateReason} onChange={(event) => field('lateReason', event.target.value)} /></label>
      </div>
      <div className="button-row"><button className="button secondary" type="button" onClick={save}>Save draft</button></div>
    </section>
  );
}
