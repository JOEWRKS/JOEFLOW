import { useState } from 'react';

const STATES = [
  'Default', 'Loading', 'Empty', 'Partial', 'Success', 'Error', 'Disabled', 'Permission denied',
  'Unauthenticated', 'Offline', 'Timeout', 'Retrying', 'Submitting', 'Completed', 'Cancelled', 'Expired',
] as const;

const GUIDANCE: Record<(typeof STATES)[number], string> = {
  Default: 'Ready for the next permitted action.',
  Loading: 'Loading current server state…',
  Empty: 'No items match the current scope.',
  Partial: 'Some records loaded. Retry to recover the missing portion.',
  Success: 'The state transition committed successfully.',
  Error: 'Nothing was committed. Review the error and retry once corrected.',
  Disabled: 'Complete the required preconditions to enable this action.',
  'Permission denied': 'Ask an administrator to restore the required current role or relationship.',
  Unauthenticated: 'Sign in again; unsaved browser input remains available for comparison.',
  Offline: 'Offline authoring is unavailable. Previously saved server draft data remains safe.',
  Timeout: 'The result is unknown. Refresh current state before attempting another write.',
  Retrying: 'Retry in progress. Duplicate submission is suppressed by idempotency key.',
  Submitting: 'Submitting the exact displayed version…',
  Completed: 'The workflow is complete and available in read-only history.',
  Cancelled: 'The operation was cancelled without a domain mutation.',
  Expired: 'This session or invitation expired. Start from a fresh authorized entry point.',
};

export function StateLab() {
  const [selected, setSelected] = useState<(typeof STATES)[number]>('Default');
  const alert = ['Error', 'Permission denied', 'Unauthenticated', 'Offline', 'Timeout', 'Expired'].includes(selected);
  return (
    <section className="state-lab card" aria-labelledby="state-lab-title">
      <div>
        <p className="eyebrow">State contract</p>
        <h2 id="state-lab-title">16-state presentation lab</h2>
      </div>
      <label htmlFor="state-picker">Preview UX state</label>
      <select id="state-picker" value={selected} onChange={(event) => setSelected(event.target.value as (typeof STATES)[number])}>
        {STATES.map((state) => <option key={state}>{state}</option>)}
      </select>
      <div className={`state-preview ${alert ? 'critical' : ''}`} role={alert ? 'alert' : 'status'}>
        <strong>{selected}</strong>
        <span>{GUIDANCE[selected]}</span>
      </div>
    </section>
  );
}
