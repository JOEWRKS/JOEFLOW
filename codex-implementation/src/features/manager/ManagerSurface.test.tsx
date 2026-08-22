import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import { executeCommand } from '../../domain/engine';
import { createSeedState } from '../../domain/seed';
import type { CommandResult, DomainCommand } from '../../domain/types';
import { ManagerSurface } from './ManagerSurface';

function Harness() {
  const [state, setState] = useState(createSeedState);
  const [last, setLast] = useState<CommandResult['outcome']>();
  const dispatch = (command: DomainCommand) => {
    const result = executeCommand(state, command);
    setState(result.state);
    setLast(result.outcome);
    return result;
  };
  return <>{last && <div role={last.status === 'rejected' ? 'alert' : 'status'}>{last.message}</div>}<ManagerSurface state={state} dispatch={dispatch} /><output aria-label="audit count">{state.auditEvents.length}</output><output aria-label="delivery count">{state.deliveries.length}</output></>;
}

describe('ManagerSurface', () => {
  it('pins approval to the displayed revision/version and commits employee delivery', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-submitted · Submitted' }));
    expect(screen.getByText('Exact review target: revision 1 · version 1')).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Approve revision 1' }));
    expect(screen.getByText('Claim approved for payment.')).toBeVisible();
    expect(screen.getAllByText('Payment pending', { selector: '[data-status]' })).not.toHaveLength(0);
    expect(screen.getByLabelText('audit count')).toHaveTextContent('1');
    expect(screen.getByLabelText('delivery count')).toHaveTextContent('3');
  });

  it('requires a manager comment for Changes requested and commits it through a dialog', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-submitted · Submitted' }));
    await user.click(screen.getByRole('button', { name: 'Request changes' }));
    const comment = screen.getByRole('textbox', { name: 'Manager comment' });
    expect(comment).toBeRequired();
    await user.type(comment, 'Attach the itemized receipt.');
    await user.click(screen.getByRole('button', { name: 'Send changes request' }));
    expect(screen.getByText('Changes requested.')).toBeVisible();
  });

  it('surfaces the self-approval denial without audit or delivery writes', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-self-review · Submitted' }));
    await user.click(screen.getByRole('button', { name: 'Approve revision 1' }));
    expect(screen.getByRole('alert')).toHaveTextContent('cannot review their own claim');
    expect(screen.getByLabelText('audit count')).toHaveTextContent('0');
    expect(screen.getByLabelText('delivery count')).toHaveTextContent('1');
  });

  it('revokes approval with a required reason only before Scheduled', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-approved · Payment pending' }));
    await user.click(screen.getByRole('button', { name: 'Revoke approval' }));
    await user.type(screen.getByRole('textbox', { name: 'Revocation reason' }), 'Receipt was invalidated by the merchant.');
    await user.click(screen.getByRole('button', { name: 'Revoke and request revision' }));
    expect(screen.getByText(/Approval revoked/i)).toBeVisible();

    await user.click(screen.getByRole('button', { name: 'clm-scheduled · Scheduled' }));
    expect(screen.queryByRole('button', { name: 'Revoke approval' })).not.toBeInTheDocument();
    expect(screen.getByText(/Revocation closed when Finance scheduled payment/i)).toBeVisible();
  });
});
