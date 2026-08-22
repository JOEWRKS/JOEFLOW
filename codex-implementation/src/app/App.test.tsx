import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRef, useState } from 'react';
import { describe, expect, it } from 'vitest';
import { CommandDialog } from '../components/CommandDialog';
import { App } from './App';

describe('App role shell', () => {
  it('exposes all four canonical roles and switches the current workspace', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(within(screen.getByRole('navigation', { name: 'Role workspaces' })).getAllByRole('button')).toHaveLength(4);
    await user.click(screen.getByRole('button', { name: 'Finance workspace' }));
    expect(screen.getByRole('heading', { name: 'Finance operations' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Finance workspace' })).toHaveAttribute('aria-current', 'page');
  });

  it('presents current business status as text and announces reset feedback', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getAllByText('Submitted', { selector: '[data-status]' })).not.toHaveLength(0);
    await user.click(screen.getByRole('button', { name: 'Reset simulated workspace' }));
    expect(screen.getByText('Workspace reset to the approved revision 55 fixture.')).toBeVisible();
  });

  it('offers all sixteen deterministic UX presentations with visible recovery guidance', async () => {
    const user = userEvent.setup();
    render(<App />);

    const statePicker = screen.getByRole('combobox', { name: 'Preview UX state' });
    expect(within(statePicker).getAllByRole('option')).toHaveLength(16);
    await user.selectOptions(statePicker, 'Permission denied');
    expect(screen.getByRole('alert')).toHaveTextContent('Permission denied');
    expect(screen.getByText(/Ask an administrator/i)).toBeVisible();
  });
});

function DialogHarness() {
  const [open, setOpen] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);
  return (
    <>
      <button ref={trigger} type="button" onClick={() => setOpen(true)}>Open decision</button>
      <CommandDialog
        open={open}
        title="Request changes"
        confirmLabel="Send request"
        triggerRef={trigger}
        onConfirm={() => setOpen(false)}
        onCancel={() => setOpen(false)}
      >
        <label htmlFor="decision-comment">Comment</label>
        <textarea id="decision-comment" required />
      </CommandDialog>
    </>
  );
}

describe('CommandDialog', () => {
  it('has labeled controls and restores focus to its trigger after cancel', async () => {
    const user = userEvent.setup();
    render(<DialogHarness />);
    const trigger = screen.getByRole('button', { name: 'Open decision' });
    await user.click(trigger);

    expect(screen.getByRole('dialog', { name: 'Request changes' })).toBeVisible();
    expect(screen.getByRole('textbox', { name: 'Comment' })).toBeRequired();
    await user.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(trigger).toHaveFocus();
  });
});
