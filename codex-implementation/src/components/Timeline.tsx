import type { AuditEvent, DomainState, Role } from '../domain/types';

interface Props { state: DomainState; role: Role; actorId: string; raw?: boolean }

function visibleEvents(state: DomainState, role: Role, actorId: string): AuditEvent[] {
  if (role === 'ADMIN') return state.auditEvents;
  return state.auditEvents.filter((event) => {
    const claim = state.claims[event.targetId];
    if (!claim) return false;
    return role === 'EMPLOYEE' ? claim.employeeId === actorId : role === 'MANAGER' ? claim.managerId === actorId : ['Payment pending', 'Scheduled', 'Payment failed', 'Payment hold', 'Payment completed'].includes(claim.status);
  });
}

export function Timeline({ state, role, actorId, raw = false }: Props) {
  const events = visibleEvents(state, role, actorId);
  return (
    <section aria-labelledby={raw ? 'raw-audit-title' : 'timeline-title'}>
      <div className="section-heading"><div><p className="eyebrow">{raw ? 'Admin only' : 'Allowlisted'}</p><h3 id={raw ? 'raw-audit-title' : 'timeline-title'}>{raw ? 'Admin raw audit' : 'Related-user timeline'}</h3></div><span>{events.length} events</span></div>
      {events.length === 0 ? <p className="helper-text">No authorized events in this simulated fixture yet.</p> : <ol className="audit-list">
        {[...events].reverse().map((event) => <li key={event.id}>
          <strong>{event.action.replaceAll('_', ' ')}</strong>
          <span>{event.at} · {event.targetId}</span>
          <small>{raw ? `${event.id} · actor ${event.actorId} · changed ${event.changedFields.join(', ')}` : `Revision event · ${event.changedFields.join(', ')}`}</small>
        </li>)}
      </ol>}
    </section>
  );
}
