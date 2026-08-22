import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import { executeCommand } from '../../domain/engine';
import { createSeedState } from '../../domain/seed';
import type { CommandResult, DomainCommand } from '../../domain/types';
import { AdminSurface } from './AdminSurface';

function Harness() {
  const [state, setState] = useState(createSeedState);
  const [last, setLast] = useState<CommandResult['outcome']>();
  const dispatch = (command: DomainCommand) => {
    const result = executeCommand(state, command);
    setState(result.state);
    setLast(result.outcome);
    return result;
  };
  return <>{last && <div role={last.status === 'rejected' ? 'alert' : 'status'}>{last.message}</div>}<AdminSurface state={state} dispatch={dispatch} /><output aria-label="audit count">{state.auditEvents.length}</output></>;
}

describe('AdminSurface', () => {
  it('issues, reissues, and revokes a seven-day invitation with required audit reasons', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.type(screen.getByRole('textbox', { name: 'Invite email' }), 'new.employee@example.com');
    await user.click(screen.getByRole('button', { name: 'Issue invitation' }));
    expect(screen.getByText(/Expires 2026-08-29 · version 1/)).toBeVisible();
    await user.click(screen.getByRole('button', { name: /Reissue invitation/i }));
    expect(screen.getAllByText('Expired', { selector: '[data-status]' })).not.toHaveLength(0);
    await user.click(screen.getByRole('button', { name: /Revoke invitation/i }));
    await user.type(screen.getByRole('textbox', { name: 'Revocation reason' }), 'Candidate withdrew');
    await user.click(screen.getByRole('button', { name: 'Confirm invitation revocation' }));
    expect(screen.getByText('Invitation revoked.')).toBeVisible();
  });

  it('deactivates an account with reason and increments the visible authorization version', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('tab', { name: 'Accounts & roles' }));
    await user.selectOptions(screen.getByRole('combobox', { name: 'Managed user' }), 'usr-employee');
    await user.type(screen.getByRole('textbox', { name: 'Account change reason' }), 'Employment ended');
    await user.click(screen.getByRole('button', { name: 'Deactivate account' }));
    expect(screen.getByText('Inactive · auth version 2')).toBeVisible();
    expect(screen.getByLabelText('audit count')).toHaveTextContent('1');
  });

  it('exposes multi-role, direct-manager, and stable category creation controls', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('tab', { name: 'Accounts & roles' }));
    await user.type(screen.getByRole('textbox', { name: 'Account change reason' }), 'Finance coverage');
    await user.click(screen.getByRole('checkbox', { name: 'FINANCE role' }));
    await user.click(screen.getByRole('button', { name: 'Save account roles' }));
    expect(screen.getByText(/EMPLOYEE \+ FINANCE/)).toBeVisible();
    await user.clear(screen.getByRole('textbox', { name: 'Account change reason' }));
    await user.type(screen.getByRole('textbox', { name: 'Account change reason' }), 'Reporting line changed');
    await user.selectOptions(screen.getByRole('combobox', { name: 'Direct manager' }), 'usr-manager-other');
    await user.click(screen.getByRole('button', { name: 'Assign direct manager' }));
    expect(screen.getByText(/manager usr-manager-other/)).toBeVisible();

    await user.click(screen.getByRole('tab', { name: 'Categories' }));
    await user.type(screen.getByRole('textbox', { name: 'New category name' }), 'Parking');
    await user.type(screen.getByRole('textbox', { name: 'New category reason' }), 'Reimbursable travel cost');
    await user.click(screen.getByRole('button', { name: 'Create category' }));
    expect(screen.getByRole('option', { name: /CAT-010 · Parking/ })).toBeInTheDocument();
  });

  it('activates an invitation only through the invited email fixture', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.type(screen.getByRole('textbox', { name: 'Invite email' }), 'new.employee@example.com');
    await user.click(screen.getByRole('button', { name: 'Issue invitation' }));
    await user.type(screen.getByRole('textbox', { name: 'Activation email' }), 'new.employee@example.com');
    await user.type(screen.getByRole('textbox', { name: 'Activation display name' }), 'New Employee');
    await user.click(screen.getByRole('button', { name: 'Activate invited account' }));
    expect(screen.getByText('Accepted', { selector: '[data-status]' })).toBeVisible();
  });

  it('sets and releases a legal hold atomically with required reasons', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('tab', { name: 'Holds & reassignment' }));
    await user.selectOptions(screen.getByRole('combobox', { name: 'Governed claim' }), 'clm-completed');
    await user.type(screen.getByRole('textbox', { name: 'Legal hold reason' }), 'Pending tax inquiry');
    await user.click(screen.getByRole('button', { name: 'Set legal hold' }));
    expect(screen.getByText(/Held · Pending tax inquiry/i)).toBeVisible();
    await user.clear(screen.getByRole('textbox', { name: 'Legal hold reason' }));
    await user.type(screen.getByRole('textbox', { name: 'Legal hold reason' }), 'Tax inquiry closed');
    await user.click(screen.getByRole('button', { name: 'Release legal hold' }));
    expect(screen.getByText('No legal hold')).toBeVisible();
  });

  it('retries a permanent delivery failure once without rolling back its domain action', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('tab', { name: 'Operational warnings' }));
    expect(screen.getByText(/Manager reassignment remains committed/i)).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Retry delivery once' }));
    expect(screen.getByText('Manual delivery retry queued.')).toBeVisible();
    expect(screen.getByRole('button', { name: 'Retry delivery once' })).toBeDisabled();
  });

  it('keeps related-user timeline allowlisted and raw audit distinct from export', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('tab', { name: 'Audit & export' }));
    expect(screen.getByRole('heading', { name: 'Admin raw audit' })).toBeVisible();
    expect(screen.getByRole('heading', { name: 'Governed CSV export' })).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Generate current-filter CSV' }));
    expect(screen.getAllByText(/Export generated/i)).not.toHaveLength(0);
    expect(document.body.textContent).not.toMatch(/refresh token|raw token|password|provider payload/i);
  });
});
