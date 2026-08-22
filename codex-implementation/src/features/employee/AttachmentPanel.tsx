import { useState, type ChangeEvent } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props { claim: Claim; state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function AttachmentPanel({ claim, state, dispatch }: Props) {
  const revision = claim.revisions.at(-1)!;
  const ids = [...revision.receiptIds, ...(revision.exchangeEvidenceIds ?? [])];
  const [uploadState, setUploadState] = useState<'Idle' | 'Scanning' | 'Failed and discarded'>('Idle');
  const upload = async (event: ChangeEvent<HTMLInputElement>, source: 'camera' | 'file', purpose: 'RECEIPT' | 'FX_EVIDENCE') => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadState('Scanning');
    try {
      const bytes = await file.arrayBuffer();
      const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const sha256 = [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
      const result = dispatch({
        type: 'LINK_ATTACHMENT', actorId: 'usr-employee', targetId: claim.id, expectedVersion: claim.version,
        idempotencyKey: `ui-upload-${source}-${purpose}-${claim.id}-${claim.version}-${sha256}`,
        input: { name: file.name, mime: file.type, sizeBytes: file.size, sha256, source, purpose },
      });
      setUploadState(result.outcome.status === 'committed' ? 'Idle' : 'Failed and discarded');
    } catch {
      setUploadState('Failed and discarded');
    } finally {
      event.target.value = '';
    }
  };

  return (
    <section className="subsection" aria-labelledby="attachment-title">
      <div className="section-heading"><div><p className="eyebrow">Evidence</p><h3 id="attachment-title">Attachments</h3></div><span>{revision.receiptIds.length}/10 receipts · {revision.exchangeEvidenceIds?.length ?? 0}/5 FX</span></div>
      <div className="attachment-list">
        {ids.map((id) => state.files[id]).filter(Boolean).map((file) => (
          <article className="attachment-row" key={file.id}>
            <div><strong>{file.name}</strong><small>{file.purpose.replace('_', ' ')} · {(file.sizeBytes / 1000).toFixed(0)} KB · {file.source}</small></div>
            <StatusBadge status={file.scanStatus} />
          </article>
        ))}
      </div>
      {claim.status === 'Draft' && <div className="button-row">
        <label className="button secondary">Capture receipt<input className="visually-hidden" type="file" capture="environment" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void upload(event, 'camera', 'RECEIPT')} /></label>
        <label className="button secondary">Choose receipt file<input className="visually-hidden" type="file" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void upload(event, 'file', 'RECEIPT')} /></label>
        {revision.currency !== 'KRW' && <label className="button secondary">Add FX evidence<input className="visually-hidden" type="file" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void upload(event, 'file', 'FX_EVIDENCE')} /></label>}
      </div>}
      {uploadState !== 'Idle' && <StatusBadge status={uploadState} />}
      <p className="helper-text">JPG, PNG, or PDF up to 10 MB each. Receipt limit 10; FX evidence limit 5. Scan retries are simulated at 30s and 2m; Failed bytes are discarded and must be selected again.</p>
    </section>
  );
}
