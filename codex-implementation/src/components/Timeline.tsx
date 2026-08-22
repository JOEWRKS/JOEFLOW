import { timelineEntriesForRole } from '../domain/selectors';
import type { DomainState, Role } from '../domain/types';

interface Props { state: DomainState; role: Role; actorId: string; raw?: boolean }

export function Timeline({ state, role, actorId, raw = false }: Props) {
  const rawEvents = raw && role === 'ADMIN' ? state.auditEvents : [];
  const relatedEntries = raw ? [] : timelineEntriesForRole(state, role, actorId);
  const count = raw ? rawEvents.length : relatedEntries.length;
  return (
    <section aria-labelledby={raw ? 'raw-audit-title' : 'timeline-title'}>
      <div className="section-heading"><div><p className="eyebrow">{raw ? 'Admin only' : 'Allowlisted'}</p><h3 id={raw ? 'raw-audit-title' : 'timeline-title'}>{raw ? 'Admin raw audit' : 'Related-user timeline'}</h3></div><span>{count} events</span></div>
      {count === 0 ? <p className="helper-text">No authorized events in this simulated fixture yet.</p> : raw ? <ol className="audit-list">
        {[...rawEvents].reverse().map((event) => <li key={event.id}>
          <strong>{event.action.replaceAll('_', ' ')}</strong>
          <span>{event.at} · {event.targetId}{event.revision ? ` · revision ${event.revision}` : ''}</span>
          <small>{event.id} · actor {event.actorId} · target version {event.targetVersion ?? 'n/a'} · changed {event.changedFields.join(', ')} · result {event.result ?? 'COMMITTED'}</small>
          <details><summary>Before / after provenance</summary><pre>{JSON.stringify({ before: event.before, after: event.after }, null, 2)}</pre></details>
        </li>)}
      </ol> : <ol className="audit-list">{[...relatedEntries].reverse().map((entry) => <li key={entry.id}>
        <strong>{entry.action.replaceAll('_', ' ')}</strong>
        <span>{entry.at}{entry.revision ? ` · revision ${entry.revision}` : ''}{entry.businessStatus ? ` · ${entry.businessStatus}` : ''}</span>
        <small>{entry.actorName} · {entry.actorRoles.join(' + ')}{entry.managerComment ? ` · ${entry.managerComment}` : ''}</small>
      </li>)}</ol>}
    </section>
  );
}
