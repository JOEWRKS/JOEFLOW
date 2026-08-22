interface Props {
  status: string;
}

export function StatusBadge({ status }: Props) {
  const tone = /failed|rejected|withdrawn|cancelled/i.test(status)
    ? 'critical'
    : /submitted|scheduled|pending|progress|requested/i.test(status)
      ? 'attention'
      : /completed|approved|current|linked/i.test(status)
        ? 'positive'
        : 'neutral';
  const symbol = tone === 'positive' ? '✓' : tone === 'critical' ? '!' : tone === 'attention' ? '•' : '—';
  return <span className={`status-badge ${tone}`} data-status><span aria-hidden="true">{symbol}</span> {status}</span>;
}
