import { StatusBadge } from '../../components/StatusBadge';
import type { Claim } from '../../domain/types';

export function RevisionTimeline({ claim }: { claim: Claim }) {
  return (
    <section className="subsection" aria-labelledby="revision-history-title">
      <div className="section-heading"><div><p className="eyebrow">Read-only history</p><h3 id="revision-history-title">Revision timeline</h3></div><StatusBadge status={claim.status} /></div>
      <ol className="timeline-list">
        {[...claim.revisions].reverse().map((revision) => (
          <li key={revision.number}>
            <span className="timeline-marker" aria-hidden="true" />
            <div><strong>Revision {revision.number}</strong><span>{revision.merchant} · {revision.krwAmount.toLocaleString()} KRW</span><small>{revision.submittedAt ?? 'Draft · not submitted'}</small></div>
          </li>
        ))}
      </ol>
    </section>
  );
}
