interface Props {
  feedback: { kind: 'success' | 'error' | 'info'; message: string; changedFields?: string[]; preservedInput?: Record<string, unknown> } | null;
}

export function FeedbackRegion({ feedback }: Props) {
  if (!feedback) return <div className="feedback-slot" aria-hidden="true" />;
  return (
    <div className={`feedback ${feedback.kind}`} role={feedback.kind === 'error' ? 'alert' : 'status'} aria-live="polite">
      <span aria-hidden="true">{feedback.kind === 'success' ? '✓' : feedback.kind === 'error' ? '!' : 'i'}</span>
      <div><strong>{feedback.message}</strong>{feedback.changedFields?.length ? <small>Changed on server: {feedback.changedFields.join(', ')}. Your browser input is preserved for comparison.</small> : null}</div>
    </div>
  );
}
