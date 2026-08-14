import { useId, useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";

interface Option {
  value: string;
  label: string;
}

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  disabled?: boolean;
}

export default function Md3Select({ label, value, onChange, options, disabled }: Props) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const selected = options.find((o) => o.value === value);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open]);

  return (
    <div ref={ref} className={`md3-select${disabled ? " md3-select--disabled" : ""}${open ? " md3-select--open" : ""}`}>
      <button
        id={id}
        type="button"
        className="md3-select-trigger"
        onClick={() => !disabled && setOpen((v) => !v)}
        disabled={disabled}
      >
        <span className="md3-select-value">{selected?.label ?? ""}</span>
        <ChevronDown className="md3-select-arrow" size={20} />
      </button>
      <label className="md3-select-label">{label}</label>
      {open && (
        <div className="md3-select-menu elevation-2">
          {options.map((o) => (
            <button
              key={o.value}
              type="button"
              className={`md3-select-option${o.value === value ? " md3-select-option--selected" : ""}`}
              onClick={() => { onChange(o.value); setOpen(false); }}
            >
              {o.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
