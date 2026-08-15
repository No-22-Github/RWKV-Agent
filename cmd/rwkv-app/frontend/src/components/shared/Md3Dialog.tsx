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

const ACTION_CLASS: Record<NonNullable<Action["variant"]>, string> = {
  text: "",
  filled: "border-brand bg-brand text-white",
  tonal: "border-transparent bg-brand-wash text-brand",
};

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
    <div className="fixed inset-0 z-[1000] grid place-items-center bg-[rgba(43,39,33,.34)] p-7" onClick={onClose}>
      <div
        ref={ref}
        className={`flex w-[min(480px,calc(100vw-56px))] max-h-[calc(100vh-56px)] flex-col overflow-hidden rounded border border-line-strong bg-paper-wash text-ink shadow-[0_18px_55px_rgba(43,39,33,.2)]${wide ? " w-[min(760px,calc(100vw-56px))]" : ""}${extraWide ? " w-[min(920px,calc(100vw-56px))]" : ""}`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="flex-none border-b border-line px-[22px] pb-[15px] pt-5 text-[17px] font-[650]">{title}</div>
        <div className="min-h-0 overflow-auto px-[22px] pb-[22px] pt-5">{children}</div>
        {actions && actions.length > 0 && (
          <div className="flex justify-end gap-2 border-t border-line px-[22px] py-[14px]">
            {actions.map((a) => (
              <button
                key={a.label}
                className={`rounded-[2px] border border-line-strong bg-transparent px-3 py-[7px] text-ink-soft ${ACTION_CLASS[a.variant || "text"]}`}
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
