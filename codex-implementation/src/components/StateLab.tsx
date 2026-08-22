import type { Role } from '../domain/types';

export const UX_STATES = [
  'Default', 'Loading', 'Empty', 'Partial', 'Success', 'Error', 'Disabled', 'Permission denied',
  'Unauthenticated', 'Offline', 'Timeout', 'Retrying', 'Submitting', 'Completed', 'Cancelled', 'Expired',
] as const;
export type UXState = (typeof UX_STATES)[number];

const GUIDANCE: Record<UXState, string> = {
  Default: 'Ready for the next permitted action.',
  Loading: 'Loading the latest authorized records and current versions…',
  Empty: 'No items match this role and current filter.',
  Partial: 'Some records loaded. Retry the missing portion without discarding visible data.',
  Success: 'The latest permitted transition committed and its effect is visible.',
  Error: 'Nothing was committed. Correct the error and retry.',
  Disabled: 'Required preconditions are shown next to the unavailable action.',
  'Permission denied': 'Ask an administrator to restore the required current role or relationship.',
  Unauthenticated: 'Sign in again; unsaved browser input remains available for comparison.',
  Offline: 'Offline authoring is unavailable. Previously saved server draft data remains safe.',
  Timeout: 'The result is unknown. Refresh current state before attempting another write.',
  Retrying: 'A bounded retry is in progress and duplicate submission is suppressed.',
  Submitting: 'Submitting the exact displayed version. Mutating actions are temporarily unavailable.',
  Completed: 'The workflow is complete and available in read-only history.',
  Cancelled: 'The operation was cancelled without a domain mutation.',
  Expired: 'This session or invitation expired. Start from a fresh authorized entry point.',
};

const RECOVERY: Record<UXState, string> = {
  Default: 'Continue',
  Loading: 'Loading current state',
  Empty: 'Refresh authorized list',
  Partial: 'Retry missing records',
  Success: 'Continue',
  Error: 'Retry last safe read',
  Disabled: 'Action unavailable',
  'Permission denied': 'Request Admin access',
  Unauthenticated: 'Sign in again',
  Offline: 'Offline writes unavailable',
  Timeout: 'Refresh latest state',
  Retrying: 'Retry in progress',
  Submitting: 'Submission in progress',
  Completed: 'Open read-only history',
  Cancelled: 'Return to workflow',
  Expired: 'Start fresh authorized entry',
};

interface Props { role: Role; selected: UXState; onChange: (state: UXState) => void }

export function StateLab({ role, selected, onChange }: Props) {
  return (
    <section className="state-lab card" aria-labelledby="state-lab-title">
      <div><p className="eyebrow">State contract · {role}</p><h2 id="state-lab-title">16-state role scenario</h2></div>
      <label htmlFor="state-picker">Preview UX state</label>
      <select id="state-picker" value={selected} onChange={(event) => onChange(event.target.value as UXState)}>
        {UX_STATES.map((state) => <option key={state}>{state}</option>)}
      </select>
      <div className="state-preview" role="status"><strong>{selected}</strong><span>{selected === 'Default' ? GUIDANCE.Default : `Applied to the current ${role.toLowerCase()} workspace below.`}</span></div>
    </section>
  );
}

export function RoleStateSurface({ role, state, onReturn }: { role: Role; state: Exclude<UXState, 'Default'>; onReturn: () => void }) {
  const alert = ['Error', 'Permission denied', 'Unauthenticated', 'Offline', 'Timeout', 'Expired'].includes(state);
  const disabled = ['Loading', 'Disabled', 'Offline', 'Retrying', 'Submitting'].includes(state);
  return (
    <section className={`role-state-surface card ${alert ? 'critical-callout' : ''}`} role={alert ? 'alert' : 'status'} aria-labelledby="role-state-title">
      <p className="eyebrow">Deterministic {role.toLowerCase()} scenario</p>
      <h2 id="role-state-title">{role[0] + role.slice(1).toLowerCase()} — {state}</h2>
      <p>{GUIDANCE[state]}</p>
      <div className="state-scenario-record"><strong>{role} workspace state</strong><span>Existing domain records remain unchanged while this presentation is active.</span></div>
      <div className="button-row"><button className="button secondary" type="button" disabled={disabled} onClick={onReturn}>{RECOVERY[state]}</button>{state !== 'Cancelled' && <button className="button secondary" type="button" onClick={onReturn}>Return to default</button>}</div>
    </section>
  );
}
