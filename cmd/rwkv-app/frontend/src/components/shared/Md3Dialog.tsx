import { useEffect, useRef, type ReactNode } from "react";

interface Action {
  label: string;
  onClick: () => void;
  variant?: "text" | "filled" | "tonal";
}

interface Props {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  actions?: Action[];
  wide?: boolean;
  extraWide?: boolean;
}

export default function Md3Dialog({ open, onClose, title, children, actions, wide, extraWide }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  // Trap focus inside dialog
  useEffect(() => {
    if (!open || !ref.current) return;
    const focusable = ref.current.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length) focusable[0].focus();
  }, [open]);

  if (!open) return null;

  return (
    <div className="md3-dialog-scrim" onClick={onClose}>
      <div
        ref={ref}
        className={`md3-dialog elevation-3${wide ? " md3-dialog--wide" : ""}${extraWide ? " md3-dialog--extra-wide" : ""}`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="md3-dialog-title">{title}</div>
        <div className="md3-dialog-body">{children}</div>
        {actions && actions.length > 0 && (
          <div className="md3-dialog-actions">
            {actions.map((a) => (
              <button
                key={a.label}
                className={`md3-btn md3-btn--${a.variant || "text"}`}
                onClick={a.onClick}
              >
                {a.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
