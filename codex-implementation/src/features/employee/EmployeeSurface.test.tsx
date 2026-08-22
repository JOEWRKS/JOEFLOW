import { fireEvent, render, screen } from '@testing-library/react';
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
  it('searches and filters only the current authorized claim list', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.type(screen.getByRole('searchbox', { name: 'Search claims' }), 'clm-draft');
    expect(screen.getByRole('button', { name: 'clm-draft · Draft' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'clm-submitted · Submitted' })).not.toBeInTheDocument();
    await user.selectOptions(screen.getByRole('combobox', { name: 'Status filter' }), 'Submitted');
    expect(screen.getByText('No claims match the current filters.')).toBeVisible();
    expect(screen.getByRole('combobox', { name: 'Sort claims' })).toBeVisible();
  });

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

  it('links an actual selected receipt through a domain mutation and exposes scan recovery state', async () => {
    const user = userEvent.setup();
    render(<Harness />);

    const receipt = new File(['receipt bytes'], 'receipt.png', { type: 'image/png' });
    await user.upload(screen.getByLabelText('Choose receipt file'), receipt);
    expect(screen.getByText('receipt.png')).toBeVisible();
    expect(screen.getAllByText('Linked', { selector: '[data-status]' })).not.toHaveLength(0);
    expect(screen.getByLabelText('audit count')).toHaveTextContent('1');
    expect(screen.getByText(/Failed bytes are discarded/i)).toBeVisible();
  });

  it('keeps a timed-out selected file unlinked and exposes bounded scan retry', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.selectOptions(screen.getByRole('combobox', { name: 'Deterministic scan result' }), 'Timeout');
    const receipt = new File(['pending bytes'], 'pending.pdf', { type: 'application/pdf' });
    await user.upload(screen.getByLabelText('Choose receipt file'), receipt);
    expect(screen.getByText('pending.pdf')).toBeVisible();
    expect(screen.getAllByText('Scanning', { selector: '[data-status]' })).not.toHaveLength(0);
    expect(screen.getByText(/Automatic retry due/)).toBeVisible();
    expect(screen.queryByRole('button', { name: /Retry scan/ })).not.toBeInTheDocument();
  });

  it('truthfully marks edits unsaved and saves on blur without losing the browser value', async () => {
    render(<Harness />);
    const merchant = screen.getByRole('textbox', { name: 'Merchant' });
    fireEvent.change(merchant, { target: { value: 'Corrected merchant' } });
    expect(screen.getByText(/Unsaved changes/i)).toBeVisible();
    fireEvent.blur(merchant);
    expect(await screen.findByText('Draft saved.')).toBeVisible();
    expect(merchant).toHaveValue('Corrected merchant');
    expect(screen.getByText(/Saved · generation 2/i)).toBeVisible();
  });

  it('submits a valid draft and commits manager delivery effects separately', async () => {
    const user = userEvent.setup();
    render(<Harness />);

    await user.click(screen.getByRole('button', { name: 'Submit claim' }));
    expect(screen.getAllByText('Submitted', { selector: '[data-status]' })).not.toHaveLength(0);
    expect(screen.getByLabelText('audit count')).toHaveTextContent('1');
    expect(screen.getByLabelText('delivery count')).toHaveTextContent('3');
  });

  it('creates, edits, and separately submits the next revision after Changes requested', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'clm-changes · Changes requested' }));
    await user.click(screen.getByRole('button', { name: 'Create revision 3' }));
    expect(screen.getByText('Revision 3', { selector: 'strong' })).toBeVisible();
    expect(screen.getAllByText('Draft', { selector: '[data-status]' })).not.toHaveLength(0);
    const merchant = screen.getByRole('textbox', { name: 'Merchant' });
    await user.clear(merchant);
    await user.type(merchant, 'Corrected lodging');
    await user.tab();
    await user.click(screen.getByRole('button', { name: 'Submit revision 3' }));
    expect(screen.getAllByText('Submitted', { selector: '[data-status]' })).not.toHaveLength(0);
  });

  it('creates a new blank claim from the public Employee surface', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'Create new claim' }));
    expect(screen.getAllByText('Draft', { selector: '[data-status]' })).not.toHaveLength(0);
    expect(screen.getByRole('textbox', { name: 'Merchant' })).toHaveValue('');
  });

  it('requires confirmation for destructive draft deletion', async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole('button', { name: 'Delete draft' }));
    expect(screen.getByRole('dialog', { name: 'Delete this draft?' })).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Delete draft permanently' }));
    expect(screen.getByText('Draft and linked evidence deleted.')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'clm-draft · Draft' })).not.toBeInTheDocument();
  });
});
