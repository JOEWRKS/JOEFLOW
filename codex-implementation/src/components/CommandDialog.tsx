import { useEffect, useId, useRef, type FormEvent, type ReactNode, type RefObject } from 'react';

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
  const dialogRef = useRef<HTMLElement>(null);
  const wasOpen = useRef(false);
  const cancelRef = useRef(onCancel);
  cancelRef.current = onCancel;
  useEffect(() => {
    if (!open) {
      if (wasOpen.current) triggerRef.current?.focus();
      wasOpen.current = false;
      return;
    }
    wasOpen.current = true;
    const dialog = dialogRef.current;
    const focusable = () => [...(dialog?.querySelectorAll<HTMLElement>('button, input, select, textarea, [tabindex]:not([tabindex="-1"])') ?? [])].filter((item) => !item.hasAttribute('disabled'));
    focusable()[0]?.focus();
    const keydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); cancelRef.current(); return; }
      if (event.key !== 'Tab') return;
      const items = focusable();
      if (!items.length) return;
      const first = items[0]; const last = items.at(-1)!;
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener('keydown', keydown);
    return () => document.removeEventListener('keydown', keydown);
  }, [open, triggerRef]);
  if (!open) return null;

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onConfirm();
  };

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onCancel()}>
      <section ref={dialogRef} className="command-dialog" role="dialog" aria-modal="true" aria-labelledby={titleId}>
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
