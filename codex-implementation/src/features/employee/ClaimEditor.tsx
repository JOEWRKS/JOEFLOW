import { useCallback, useEffect, useRef, useState } from 'react';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props {
  claim: Claim;
  state: DomainState;
  dispatch: (command: DomainCommand) => CommandResult;
}

export function ClaimEditor({ claim, state, dispatch }: Props) {
  const revision = claim.revisions.at(-1)!;
  const dirtyRef = useRef(false);
  const generationRef = useRef(0);
  const retryCycleRef = useRef(0);
  const retryTimerRef = useRef<number | undefined>(undefined);
  const idleTimerRef = useRef<number | undefined>(undefined);
  const [saveStatus, setSaveStatus] = useState('Saved');
  const [savedGeneration, setSavedGeneration] = useState(claim.version);
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
    dirtyRef.current = false;
    generationRef.current += 1;
    retryCycleRef.current += 1;
    if (retryTimerRef.current) window.clearTimeout(retryTimerRef.current);
    setSaveStatus('Saved');
    setSavedGeneration(claim.version);
  }, [claim.id, claim.currentRevision]);

  const field = (key: keyof typeof form, value: string) => {
    dirtyRef.current = true;
    generationRef.current += 1;
    retryCycleRef.current += 1;
    if (retryTimerRef.current) window.clearTimeout(retryTimerRef.current);
    setSaveStatus('Unsaved changes');
    setForm((current) => ({ ...current, [key]: value }));
  };
  const save = useCallback((generation = generationRef.current, attempt = 0, cycle = retryCycleRef.current) => {
    if (!dirtyRef.current) return;
    if (idleTimerRef.current) window.clearTimeout(idleTimerRef.current);
    setSaveStatus('Saving');
    const result = dispatch({
      type: 'UPDATE_DRAFT', actorId: 'usr-employee', targetId: claim.id, expectedVersion: claim.version,
      idempotencyKey: `ui-save-${claim.id}-g${generation}-c${cycle}-a${attempt}-v${claim.version}`,
      input: { ...form, saveGeneration: generation, originalAmount: Number(form.originalAmount), krwAmount: Number(form.krwAmount), exchangeRate: form.exchangeRate ? Number(form.exchangeRate) : undefined },
    });
    if (generation !== generationRef.current || cycle !== retryCycleRef.current) return;
    if (result.outcome.status === 'committed') {
      dirtyRef.current = false;
      setSaveStatus('Saved');
      setSavedGeneration(result.outcome.targetVersion);
    } else {
      const transient = ['SAVE_FAILED', 'TIMEOUT', 'TEMPORARY_FAILURE'].includes(result.outcome.code);
      if (transient && attempt < 5) {
        const delay = 1000 * 2 ** attempt;
        setSaveStatus(`Retrying ${attempt + 1}/5 in ${delay / 1000}s`);
        retryTimerRef.current = window.setTimeout(() => save(generation, attempt + 1, cycle), delay);
      } else {
        setSaveStatus(transient ? 'Save failed · automatic retries stopped' : 'Save failed');
      }
    }
  }, [claim.id, claim.version, dispatch, form]);

  useEffect(() => {
    if (!dirtyRef.current || claim.status !== 'Draft') return;
    const generation = generationRef.current;
    const cycle = retryCycleRef.current;
    idleTimerRef.current = window.setTimeout(() => save(generation, 0, cycle), 2000);
    return () => { if (idleTimerRef.current) window.clearTimeout(idleTimerRef.current); };
  }, [form, claim.status, claim.version, save]);

  useEffect(() => () => { if (retryTimerRef.current) window.clearTimeout(retryTimerRef.current); if (idleTimerRef.current) window.clearTimeout(idleTimerRef.current); }, []);

  useEffect(() => {
    if (!dirtyRef.current) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [saveStatus]);

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
        <span className="autosave-state"><span aria-hidden="true">{saveStatus === 'Saved' ? '✓' : saveStatus === 'Save failed' ? '!' : '•'}</span> {saveStatus}{saveStatus === 'Saved' ? ` · generation ${savedGeneration}` : ''}</span>
      </div>
      <div className="form-grid" onBlur={() => save()}>
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
      <div className="button-row"><button className="button secondary" type="button" onClick={() => { retryCycleRef.current += 1; if (retryTimerRef.current) window.clearTimeout(retryTimerRef.current); save(generationRef.current, 0, retryCycleRef.current); }}>{saveStatus.includes('stopped') ? 'Retry save manually' : 'Save draft'}</button></div>
    </section>
  );
}
