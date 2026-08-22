import { act, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { createSeedState } from '../../domain/seed';
import type { CommandResult } from '../../domain/types';
import { ClaimEditor } from './ClaimEditor';

afterEach(() => vi.useRealTimers());

describe('ClaimEditor autosave recovery', () => {
  it('retries a transient failure after 1 and 2 seconds while preserving browser input', () => {
    vi.useFakeTimers();
    const state = createSeedState();
    let calls = 0;
    const dispatch = vi.fn((): CommandResult => {
      calls += 1;
      if (calls < 3) return {
        state, outcome: { status: 'rejected', code: 'SAVE_FAILED', message: 'Temporary save failure.', targetVersion: 1, preservedInput: {} },
        auditEventIds: [], deliveryEventIds: [], changedFields: [],
      };
      return {
        state, outcome: { status: 'committed', code: 'COMMITTED', message: 'Draft saved.', targetVersion: 2 },
        auditEventIds: [], deliveryEventIds: [], changedFields: ['revision.merchant'],
      };
    });
    render(<ClaimEditor claim={state.claims['clm-draft']} state={state} dispatch={dispatch} />);
    const merchant = screen.getByRole('textbox', { name: 'Merchant' });
    fireEvent.change(merchant, { target: { value: 'Preserved merchant' } });
    fireEvent.blur(merchant);
    expect(screen.getByText(/Retrying 1\/5 in 1s/)).toBeVisible();
    act(() => vi.advanceTimersByTime(1000));
    expect(screen.getByText(/Retrying 2\/5 in 2s/)).toBeVisible();
    act(() => vi.advanceTimersByTime(2000));
    expect(screen.getByText(/Saved · generation 2/)).toBeVisible();
    expect(merchant).toHaveValue('Preserved merchant');
    expect(dispatch).toHaveBeenCalledTimes(3);
  });
});
