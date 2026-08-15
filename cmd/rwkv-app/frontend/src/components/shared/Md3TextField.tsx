import { useId } from "react";

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  multiline?: boolean;
  rows?: number;
  disabled?: boolean;
  type?: string;
  placeholder?: string;
}

export default function Md3TextField({
  label, value, onChange, error, multiline, rows = 4, disabled, type = "text", placeholder,
}: Props) {
  const id = useId();
  const hasValue = value.length > 0 || !!placeholder;
  const fieldClass = `peer w-full min-h-[46px] rounded-[2px] border border-line-strong bg-paper-wash px-[10px] pb-[6px] pt-[18px] text-[12px] text-ink outline-none transition-[border-color,box-shadow] duration-150 placeholder:text-ink-muted focus:border-brand focus:shadow-[0_0_0_1px_var(--brand)]${error ? " border-danger focus:border-danger" : ""}`;
  const labelClass = `pointer-events-none absolute left-[10px] transition-[top,font-size,color] duration-150 ${error ? "text-danger" : hasValue ? "text-ink-soft" : "text-ink-muted"} ${hasValue ? "top-[5px] text-[9px]" : "top-[14px] text-[12px]"}`;

  return (
    <div className={`relative min-w-0${disabled ? " opacity-55" : ""}`}>
      {multiline ? (
        <textarea
          id={id}
          className={`${fieldClass} min-h-[92px] resize-y`}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={rows}
          disabled={disabled}
          placeholder={placeholder}
        />
      ) : (
        <input
          id={id}
          className={fieldClass}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
        />
      )}
      <label htmlFor={id} className={labelClass}>
        {label}
      </label>
      {error && <span className="mt-1 block text-[10px] text-danger">{error}</span>}
    </div>
  );
}
