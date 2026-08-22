import { createSeedState } from './seed';
import type { DomainState } from './types';

const STORAGE_KEY = 'joewrks-expense-reimbursement-rev55';

export function loadState(storage: Pick<Storage, 'getItem'> = window.localStorage): DomainState {
  const stored = storage.getItem(STORAGE_KEY);
  if (!stored) return createSeedState();
  try {
    const state = JSON.parse(stored) as DomainState;
    return state.canonicalRevision === 55 ? state : createSeedState();
  } catch {
    return createSeedState();
  }
}

export function saveState(state: DomainState, storage: Pick<Storage, 'setItem'> = window.localStorage): void {
  storage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function resetState(storage: Pick<Storage, 'removeItem'> = window.localStorage): DomainState {
  storage.removeItem(STORAGE_KEY);
  return createSeedState();
}
