interface Props {
  feedback: { kind: 'success' | 'error' | 'info'; message: string } | null;
}

export function FeedbackRegion({ feedback }: Props) {
  if (!feedback) return <div className="feedback-slot" aria-hidden="true" />;
  return (
    <div className={`feedback ${feedback.kind}`} role={feedback.kind === 'error' ? 'alert' : 'status'} aria-live="polite">
      <span aria-hidden="true">{feedback.kind === 'success' ? '✓' : feedback.kind === 'error' ? '!' : 'i'}</span>
      {feedback.message}
    </div>
  );
}
