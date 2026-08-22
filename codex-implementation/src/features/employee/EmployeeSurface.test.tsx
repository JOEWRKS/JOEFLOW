import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import { executeCommand } from '../../domain/engine';
import { createSeedState } from '../../domain/seed';
import type { CommandResult, DomainCommand, DomainState } from '../../domain/types';
import { EmployeeSurface } from './EmployeeSurface';

function Harness() {
  const [state, setState] = useState(createSeedState);
  const [last, setLast] = useState<CommandResult['outcome']>();
  const dispatch = (command: DomainCommand) => {
    const result = executeCommand(state, command);
    setState(result.state);
    setLast(result.outcome);
    return result;
  };
  return (
    <>
      {last && <div role={last.status === 'rejected' ? 'alert' : 'status'}>{last.message}</div>}
      <EmployeeSurface state={state} dispatch={dispatch} />
      <output aria-label="audit count">{state.auditEvents.length}</output>
      <output aria-label="delivery count">{state.deliveries.length}</output>
    </>
  );
}

describe('EmployeeSurface', () => {
  it('edits a draft with labeled required fields and blocks a future expense date', async () => {
    const user = userEvent.setup();
    render(<Harness />);

    await user.clear(screen.getByRole('textbox', { name: 'Expense date' }));
    await user.type(screen.getByRole('textbox', { name: 'Expense date' }), '2026-08-23');
    await user.click(screen.getByRole('button', { name: 'Save draft' }));
    expect(screen.getByText('Draft saved.')).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Submit claim' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Future expense dates cannot be submitted.');
  });

  it('links a camera receipt through a domain mutation and exposes scan recovery state', async () => {
    const user = userEvent.setup();
    render(<Harness />);

    await user.click(screen.getByRole('button', { name: 'Capture receipt' }));
    expect(screen.getByText('camera-receipt.jpg')).toBeVisible();
    expect(screen.getAllByText('Linked', { selector: '[data-status]' })).not.toHaveLength(0);
    expect(screen.getByLabelText('audit count')).toHaveTextContent('1');
    expect(screen.getByText(/Failed bytes are discarded/i)).toBeVisible();
  });

  it('submits a valid draft and commits manager delivery effects separately', async () => {
    const user = userEvent.setup();
    render(<Harness />);

    await user.click(screen.getByRole('button', { name: 'Submit claim' }));
    expect(screen.getAllByText('Submitted', { selector: '[data-status]' })).not.toHaveLength(0);
    expect(screen.getByLabelText('audit count')).toHaveTextContent('1');
    expect(screen.getByLabelText('delivery count')).toHaveTextContent('3');
  });

  it('creates and submits the next revision after Changes requested', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-changes · Changes requested' }));
    await user.click(screen.getByRole('button', { name: 'Create and submit revision 3' }));
    expect(screen.getByText('Revision 3', { selector: 'strong' })).toBeVisible();
    expect(screen.getAllByText('Submitted', { selector: '[data-status]' })).not.toHaveLength(0);
  });

  it('requires confirmation for destructive draft deletion', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'Delete draft' }));
    expect(screen.getByRole('dialog', { name: 'Delete this draft?' })).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Delete draft permanently' }));
    expect(screen.getByText('Draft deleted.')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'clm-draft · Draft' })).not.toBeInTheDocument();
  });
});
