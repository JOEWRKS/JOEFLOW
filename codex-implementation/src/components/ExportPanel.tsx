import type { CommandResult, DomainCommand, DomainState, Role } from '../domain/types';

interface Props { state: DomainState; role: Extract<Role, 'ADMIN' | 'FINANCE'>; actorId: string; dispatch: (command: DomainCommand) => CommandResult; claimIds?: string[]; filterSnapshot?: string }

export function ExportPanel({ state, role, actorId, dispatch, claimIds, filterSnapshot = 'Current authorized scope' }: Props) {
  const latest = [...state.exports].reverse().find((item) => item.actorId === actorId);
  const generate = () => dispatch({
    type: 'EXPORT_CSV', actorId, targetId: 'current-filter-export', expectedVersion: 0,
    idempotencyKey: `ui-export-${role}-${state.exports.length}`, input: { claimIds, filterSnapshot },
  });
  const download = () => {
    if (!latest) return;
    const result = dispatch({ type: 'DOWNLOAD_EXPORT', actorId, targetId: latest.id, expectedVersion: latest.version, idempotencyKey: `ui-download-${latest.id}-${latest.version}`, input: {} });
    const exported = result.state.exports.find((item) => item.id === latest.id);
    if (result.outcome.status !== 'committed' || !exported || typeof URL.createObjectURL !== 'function') return;
    const url = URL.createObjectURL(new Blob([exported.csv], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = `${exported.id}.csv`; anchor.click(); URL.revokeObjectURL(url);
  };
  return (
    <section aria-labelledby="export-title">
      <div className="section-heading"><div><p className="eyebrow">Reauthorized at generation and download</p><h3 id="export-title">Governed CSV export</h3></div><span>10,000 row cap</span></div>
      <p className="helper-text">Current-filter rows only. Attachments, access tokens, internal IDs, file diagnostics, delivery-provider detail, and administrator-only notes are excluded.</p>
      <p className="mobile-desktop-guidance">CSV remains available on mobile; desktop recommended for reviewing bulk rows before download.</p>
      <button className="button secondary" type="button" onClick={generate}>Generate current-filter CSV</button>
      {latest && <div className="export-result"><strong>Export generated · {latest.rowCount} rows</strong><span>{latest.columns.join(', ')}</span><small>{latest.filterSnapshot} · local simulated CSV {latest.id}; no external system received data.</small><button className="button secondary" type="button" onClick={download}>Download authorized CSV</button></div>}
    </section>
  );
}
