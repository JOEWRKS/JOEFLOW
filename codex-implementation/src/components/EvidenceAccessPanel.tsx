import type { Claim, CommandResult, DomainCommand, DomainState } from '../domain/types';

interface Props {
  claim: Claim;
  state: DomainState;
  actorId: string;
  dispatch: (command: DomainCommand) => CommandResult;
  compact?: boolean;
}

export function EvidenceAccessPanel({ claim, state, actorId, dispatch, compact = false }: Props) {
  const files = Object.values(state.files).filter((file) => file.claimId === claim.id && file.scanStatus === 'Linked');
  const issue = (fileId: string) => dispatch({
    type: 'ISSUE_FILE_ACCESS', actorId, targetId: fileId, expectedVersion: 0,
    idempotencyKey: `ui-file-grant-${actorId}-${fileId}-${state.nextSequence}`, input: {},
  });
  const download = (fileId: string) => {
    const grant = [...state.fileGrants].reverse().find((item) => item.actorId === actorId && item.fileId === fileId);
    if (!grant) return;
    dispatch({
      type: 'DOWNLOAD_FILE', actorId, targetId: grant.id, expectedVersion: grant.version,
      idempotencyKey: `ui-file-download-${actorId}-${grant.id}-${grant.version}`, input: { rangeOrRetry: true },
    });
  };
  return (
    <section className={compact ? 'evidence-access compact' : 'evidence-access'} aria-label="Governed evidence access">
      <div className="section-heading"><div><p className="eyebrow">Five-minute access</p><h3>Receipt and FX evidence</h3></div><span>{files.length} files</span></div>
      {files.length === 0 ? <p className="helper-text">No clean linked evidence is available.</p> : <div className="attachment-list">{files.map((file) => {
        const grant = [...state.fileGrants].reverse().find((item) => item.actorId === actorId && item.fileId === file.id);
        const valid = Boolean(grant && Date.parse(grant.expiresAt) > Date.parse(state.now));
        return <article className="attachment-row" key={file.id}>
          <div><strong>{file.name}</strong><small>{file.purpose.replaceAll('_', ' ')}{file.evidenceType ? ` · ${file.evidenceType.replaceAll('_', ' ')}` : ''}</small></div>
          <button className="button secondary" type="button" onClick={() => issue(file.id)}>Request 5-minute access</button>
          <button className="button secondary" type="button" disabled={!valid} onClick={() => download(file.id)}>Download / range retry</button>
          {grant && <small>Grant expires {grant.expiresAt}. Latest login, role, relationship, and file authority are checked again on every request.</small>}
        </article>;
      })}</div>}
      <p className="helper-text">This deterministic local implementation audits authorization only; it does not claim production object storage or file transfer.</p>
    </section>
  );
}
