import { StatusBadge } from '../../components/StatusBadge';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props { claim: Claim; state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function AttachmentPanel({ claim, state, dispatch }: Props) {
  const revision = claim.revisions.at(-1)!;
  const ids = [...revision.receiptIds, ...(revision.exchangeEvidenceIds ?? [])];
  const upload = (source: 'camera' | 'file', purpose: 'RECEIPT' | 'FX_EVIDENCE') => dispatch({
    type: 'LINK_ATTACHMENT', actorId: 'usr-employee', targetId: claim.id, expectedVersion: claim.version,
    idempotencyKey: `ui-upload-${source}-${purpose}-${claim.id}-${claim.version}`,
    input: {
      name: source === 'camera' ? 'camera-receipt.jpg' : purpose === 'FX_EVIDENCE' ? 'fx-evidence.pdf' : 'receipt.pdf',
      mime: source === 'camera' ? 'image/jpeg' : 'application/pdf', sizeBytes: 245000, source, purpose,
    },
  });

  return (
    <section className="subsection" aria-labelledby="attachment-title">
      <div className="section-heading"><div><p className="eyebrow">Evidence</p><h3 id="attachment-title">Attachments</h3></div><span>{ids.length}/10 files</span></div>
      <div className="attachment-list">
        {ids.map((id) => state.files[id]).filter(Boolean).map((file) => (
          <article className="attachment-row" key={file.id}>
            <div><strong>{file.name}</strong><small>{file.purpose.replace('_', ' ')} · {(file.sizeBytes / 1000).toFixed(0)} KB · {file.source}</small></div>
            <StatusBadge status={file.scanStatus} />
          </article>
        ))}
      </div>
      {claim.status === 'Draft' && <div className="button-row">
        <button className="button secondary" type="button" onClick={() => upload('camera', 'RECEIPT')}>Capture receipt</button>
        <button className="button secondary" type="button" onClick={() => upload('file', 'RECEIPT')}>Choose receipt file</button>
        {revision.currency !== 'KRW' && <button className="button secondary" type="button" onClick={() => upload('file', 'FX_EVIDENCE')}>Add FX evidence</button>}
      </div>}
      <p className="helper-text">JPG, PNG, or PDF up to 100 MB. Scan retries are simulated at 30s and 2m; Failed bytes are discarded and must be selected again.</p>
    </section>
  );
}
