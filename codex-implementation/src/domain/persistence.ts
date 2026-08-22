import { createSeedState } from './seed';
import type { DomainState } from './types';

const STORAGE_KEY = 'joewrks-expense-reimbursement-rev55';
const memory = new Map<string, string>();

interface ReadStorage { getItem: (key: string) => string | null }
interface WriteStorage { setItem: (key: string, value: string) => void }
interface RemoveStorage { removeItem: (key: string) => void }

const memoryStorage: ReadStorage & WriteStorage & RemoveStorage = {
  getItem: (key) => memory.get(key) ?? null,
  setItem: (key, value) => memory.set(key, value),
  removeItem: (key) => memory.delete(key),
};

function browserStorage(): (ReadStorage & WriteStorage & RemoveStorage) | undefined {
  try {
    if (typeof navigator !== 'undefined' && /jsdom/i.test(navigator.userAgent)) return undefined;
    return typeof window !== 'undefined' && window.localStorage ? window.localStorage : undefined;
  } catch {
    return undefined;
  }
}

export function loadState(storage: ReadStorage = browserStorage() ?? memoryStorage): DomainState {
  const stored = storage.getItem(STORAGE_KEY);
  if (!stored) return createSeedState();
  try {
    const state = JSON.parse(stored) as DomainState;
    return state.canonicalRevision === 55 ? state : createSeedState();
  } catch {
    return createSeedState();
  }
}

export function saveState(state: DomainState, storage: WriteStorage = browserStorage() ?? memoryStorage): void {
  storage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function resetState(storage: RemoveStorage = browserStorage() ?? memoryStorage): DomainState {
  storage.removeItem(STORAGE_KEY);
  return createSeedState();
}
