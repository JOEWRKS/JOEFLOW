import { useEffect, useId, type FormEvent, type ReactNode, type RefObject } from 'react';

interface Props {
  open: boolean;
  title: string;
  confirmLabel: string;
  triggerRef: RefObject<HTMLButtonElement | null>;
  onConfirm: () => void;
  onCancel: () => void;
  children: ReactNode;
  destructive?: boolean;
}

export function CommandDialog({ open, title, confirmLabel, triggerRef, onConfirm, onCancel, children, destructive }: Props) {
  const titleId = useId();
  useEffect(() => {
    if (!open) triggerRef.current?.focus();
  }, [open, triggerRef]);
  if (!open) return null;

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onConfirm();
  };

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onCancel()}>
      <section className="command-dialog" role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <header>
          <p className="eyebrow">Confirm domain change</p>
          <h2 id={titleId}>{title}</h2>
        </header>
        <form onSubmit={submit}>
          <div className="form-stack">{children}</div>
          <div className="dialog-actions">
            <button type="button" className="button secondary" onClick={onCancel}>Cancel</button>
            <button type="submit" className={destructive ? 'button danger' : 'button primary'}>{confirmLabel}</button>
          </div>
        </form>
      </section>
    </div>
  );
}
