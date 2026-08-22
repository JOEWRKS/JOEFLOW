import { useCallback, useState } from 'react';
import { executeCommand } from '../domain/engine';
import { loadState, resetState, saveState } from '../domain/persistence';
import type { CommandResult, DomainCommand, DomainState } from '../domain/types';

interface Feedback {
  kind: 'success' | 'error' | 'info';
  message: string;
  changedFields?: string[];
  preservedInput?: Record<string, unknown>;
}

export function useDomain() {
  const [state, setState] = useState<DomainState>(() => loadState());
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const dispatch = useCallback((command: DomainCommand): CommandResult => {
    const result = executeCommand(state, command);
    if (result.state !== state) {
      setState(result.state);
      saveState(result.state);
    }
    setFeedback({
      kind: result.outcome.status === 'committed' ? 'success' : 'error',
      message: result.outcome.message,
      changedFields: result.outcome.code === 'STALE_VERSION' ? result.changedFields : undefined,
      preservedInput: result.outcome.code === 'STALE_VERSION' ? result.outcome.preservedInput : undefined,
    });
    return result;
  }, [state]);

  const reset = useCallback(() => {
    const next = resetState();
    setState(next);
    setFeedback({ kind: 'info', message: 'Workspace reset to the approved revision 55 fixture.' });
  }, []);

  return { state, dispatch, reset, feedback };
}
