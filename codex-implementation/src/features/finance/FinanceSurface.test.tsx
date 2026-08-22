import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import { executeCommand } from '../../domain/engine';
import { createSeedState } from '../../domain/seed';
import type { CommandResult, DomainCommand } from '../../domain/types';
import { FinanceSurface } from './FinanceSurface';

function Harness() {
  const [state, setState] = useState(createSeedState);
  const [last, setLast] = useState<CommandResult['outcome']>();
  const dispatch = (command: DomainCommand) => {
    const result = executeCommand(state, command);
    setState(result.state);
    setLast(result.outcome);
    return result;
  };
  return <>{last && <div role={last.status === 'rejected' ? 'alert' : 'status'}>{last.message}</div>}<FinanceSurface state={state} dispatch={dispatch} /><output aria-label="audit count">{state.auditEvents.length}</output></>;
}

describe('FinanceSurface', () => {
  it('atomically claims and schedules a Payment pending item', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-approved · Payment pending' }));
    expect(screen.getByRole('textbox', { name: 'Scheduled date' })).toHaveValue('2026-08-22');
    await user.click(screen.getByRole('button', { name: 'Claim and schedule payment' }));
    expect(screen.getByText('Payment claimed and scheduled.')).toBeVisible();
    expect(screen.getByText('Owner: Finance Kim')).toBeVisible();
    expect(screen.getByLabelText('audit count')).toHaveTextContent('1');
  });

  it('enforces payment method details and records a valid completion', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-scheduled · Scheduled' }));
    await user.selectOptions(screen.getByRole('combobox', { name: 'Payment method' }), 'Other');
    await user.type(screen.getByRole('textbox', { name: 'External reference' }), 'PAY-NEW-200');
    await user.click(screen.getByRole('button', { name: 'Record payment completed' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Other payment method requires a description.');
    await user.type(screen.getByRole('textbox', { name: 'Other method description' }), 'Manual cash settlement');
    await user.click(screen.getByRole('button', { name: 'Record payment completed' }));
    expect(screen.getByText('Payment completed.')).toBeVisible();
    expect(screen.getAllByText('Payment completed', { selector: '[data-status]' })).not.toHaveLength(0);
  });

  it('records structured Not paid verification before rescheduling a failed payment', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-failed · Payment failed' }));
    await user.click(screen.getByRole('button', { name: 'Verify execution' }));
    await user.selectOptions(screen.getByRole('combobox', { name: 'Verification result' }), 'Not paid');
    await user.type(screen.getByRole('textbox', { name: 'Payment channel' }), 'Bank portal');
    await user.type(screen.getByRole('textbox', { name: 'Masked account' }), '***1234');
    await user.type(screen.getByRole('textbox', { name: 'Lookup from' }), '2026-08-20');
    await user.type(screen.getByRole('textbox', { name: 'Lookup to' }), '2026-08-22');
    await user.type(screen.getByRole('textbox', { name: 'Reference or lookup result' }), 'No matching transfer');
    await user.type(screen.getByRole('textbox', { name: 'Verification conclusion' }), 'Payment not executed');
    await user.click(screen.getByRole('button', { name: 'Record verification' }));
    expect(screen.getByText(/Not paid · checked by usr-finance/i)).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Reschedule verified payment' }));
    expect(screen.getByText('Failed payment rescheduled.')).toBeVisible();
  });

  it('creates one adjustment, completes it, and updates completed-only net totals', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-completed · Payment completed' }));
    expect(screen.getByText('Net settled')).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Create adjustment' }));
    await user.selectOptions(screen.getByRole('combobox', { name: 'Adjustment kind' }), 'Recovery');
    await user.clear(screen.getByRole('textbox', { name: 'Adjustment amount KRW' }));
    await user.type(screen.getByRole('textbox', { name: 'Adjustment amount KRW' }), '18000');
    await user.type(screen.getByRole('textbox', { name: 'Adjustment reason' }), 'Personal minibar');
    await user.click(screen.getByRole('button', { name: 'Start adjustment' }));
    expect(screen.getByText('In progress', { selector: '[data-status]' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Create adjustment' })).toBeDisabled();
    await user.type(screen.getByRole('textbox', { name: 'Adjustment external reference' }), 'ADJ-NEW-200');
    await user.click(screen.getByRole('button', { name: 'Complete adjustment' }));
    expect(screen.getByText('150,000 KRW')).toBeVisible();
  });
});
