import type { CommandResult, DomainCommand, DomainState, Role } from '../domain/types';

interface Props { state: DomainState; role: Extract<Role, 'ADMIN' | 'FINANCE'>; actorId: string; dispatch: (command: DomainCommand) => CommandResult }

export function ExportPanel({ state, role, actorId, dispatch }: Props) {
  const latest = state.exports.at(-1);
  const generate = () => dispatch({
    type: 'EXPORT_CSV', actorId, targetId: 'current-filter-export', expectedVersion: 0,
    idempotencyKey: `ui-export-${role}-${state.exports.length}`, input: { filter: 'current authorized scope' },
  });
  return (
    <section aria-labelledby="export-title">
      <div className="section-heading"><div><p className="eyebrow">Reauthorized at generation</p><h3 id="export-title">Governed CSV export</h3></div><span>10,000 row cap</span></div>
      <p className="helper-text">Current-filter rows only. Attachments, access tokens, internal IDs, file diagnostics, delivery-provider detail, and administrator-only notes are excluded.</p>
      <button className="button secondary" type="button" onClick={generate}>Generate current-filter CSV</button>
      {latest && <div className="export-result"><strong>Export generated · {latest.rowCount} rows</strong><span>{latest.columns.join(', ')}</span><small>Simulated artifact {latest.id}; no external system received data.</small></div>}
    </section>
  );
}
