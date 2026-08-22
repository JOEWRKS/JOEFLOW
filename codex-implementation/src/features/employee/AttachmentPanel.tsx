import { useEffect, useState, type ChangeEvent } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import type { Claim, CommandResult, DomainCommand, DomainState } from '../../domain/types';

interface Props { claim: Claim; state: DomainState; dispatch: (command: DomainCommand) => CommandResult }

export function AttachmentPanel({ claim, state, dispatch }: Props) {
  const revision = claim.revisions.at(-1)!;
  const ids = [...new Set([...revision.receiptIds, ...(revision.exchangeEvidenceIds ?? []), ...Object.values(state.files).filter((file) => file.claimId === claim.id && file.scanStatus === 'Scanning').map((file) => file.id)])];
  const [uploadState, setUploadState] = useState<'Idle' | 'Scanning' | 'Failed and discarded'>('Idle');
  const [scanOutcome, setScanOutcome] = useState('Clean');
  const [fxEvidenceType, setFxEvidenceType] = useState('OFFICIAL_RATE_PDF');
  useEffect(() => {
    const timers = Object.values(state.files).filter((file) => file.claimId === claim.id && file.scanStatus === 'Scanning' && file.nextScanRetryAt).map((file) => window.setTimeout(() => {
      dispatch({
        type: 'RETRY_ATTACHMENT_SCAN', actorId: 'usr-employee', targetId: claim.id, expectedVersion: claim.version,
        idempotencyKey: `worker-scan-${claim.id}-${file.id}-${file.scanAttempts ?? 0}-${file.nextScanRetryAt}`,
        input: { fileId: file.id, scanOutcome, scheduledAt: file.nextScanRetryAt },
      });
    }, (file.scanAttempts ?? 0) === 0 ? 30_000 : 120_000));
    return () => timers.forEach((timer) => window.clearTimeout(timer));
  }, [claim.id, claim.version, dispatch, scanOutcome, state.files]);
  const issueAccess = (fileId: string) => dispatch({
    type: 'ISSUE_FILE_ACCESS', actorId: 'usr-employee', targetId: fileId, expectedVersion: 0,
    idempotencyKey: `ui-file-grant-usr-employee-${fileId}-${state.nextSequence}`, input: {},
  });
  const download = (fileId: string) => {
    const grant = [...state.fileGrants].reverse().find((item) => item.actorId === 'usr-employee' && item.fileId === fileId);
    if (!grant) return;
    dispatch({ type: 'DOWNLOAD_FILE', actorId: 'usr-employee', targetId: grant.id, expectedVersion: grant.version, idempotencyKey: `ui-file-download-usr-employee-${grant.id}-${grant.version}`, input: { rangeOrRetry: true } });
  };
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
        input: { name: file.name, mime: file.type, sizeBytes: file.size, sha256, source, purpose, scanOutcome, ...(purpose === 'FX_EVIDENCE' ? { evidenceType: fxEvidenceType } : {}) },
      });
      setUploadState(result.outcome.status === 'committed' && result.outcome.message.includes('timed out') ? 'Scanning' : result.outcome.status === 'committed' && result.outcome.message.includes('discarded') ? 'Failed and discarded' : result.outcome.status === 'committed' ? 'Idle' : 'Failed and discarded');
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
            {file.scanStatus === 'Scanning' && <small>Automatic retry due {file.nextScanRetryAt}; submission remains blocked.</small>}
            {file.scanStatus === 'Linked' && <><button className="button secondary" type="button" onClick={() => issueAccess(file.id)}>Request 5-minute access</button><button className="button secondary" type="button" disabled={!state.fileGrants.some((grant) => grant.actorId === 'usr-employee' && grant.fileId === file.id && Date.parse(grant.expiresAt) > Date.parse(state.now))} onClick={() => download(file.id)}>Download / range retry</button></>}
          </article>
        ))}
      </div>
      {claim.status === 'Draft' && <div className="button-row">
        <label>Deterministic scan result<select value={scanOutcome} onChange={(event) => setScanOutcome(event.target.value)}><option>Clean</option><option>Timeout</option><option>Malware</option></select></label>
        <label className="button secondary">Capture receipt<input className="visually-hidden" type="file" capture="environment" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void upload(event, 'camera', 'RECEIPT')} /></label>
        <label className="button secondary">Choose receipt file<input className="visually-hidden" type="file" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void upload(event, 'file', 'RECEIPT')} /></label>
        {revision.currency !== 'KRW' && <><label>FX evidence type<select value={fxEvidenceType} onChange={(event) => setFxEvidenceType(event.target.value)}><option value="CARD_STATEMENT">Card statement</option><option value="BANK_EXCHANGE_RECORD">Bank exchange record</option><option value="OFFICIAL_RATE_CAPTURE">Official-rate capture</option><option value="OFFICIAL_RATE_PDF">Official-rate PDF</option></select></label><label className="button secondary">Add FX evidence<input className="visually-hidden" type="file" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void upload(event, 'file', 'FX_EVIDENCE')} /></label></>}
      </div>}
      {uploadState !== 'Idle' && <StatusBadge status={uploadState} />}
      <p className="helper-text">JPG, PNG, or PDF up to 10 MB each. Receipt limit 10; FX evidence limit 5. The deterministic scan worker enforces due-time gates at 30 seconds and two minutes; failed bytes are discarded and must be selected again.</p>
    </section>
  );
}
