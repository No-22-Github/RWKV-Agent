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

  return (
    <div className={`md3-textfield${error ? " md3-textfield--error" : ""}${disabled ? " md3-textfield--disabled" : ""}`}>
      {multiline ? (
        <textarea
          id={id}
          className="md3-textfield-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={rows}
          disabled={disabled}
          placeholder={placeholder}
        />
      ) : (
        <input
          id={id}
          className="md3-textfield-input"
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
        />
      )}
      <label htmlFor={id} className={`md3-textfield-label${hasValue ? " md3-textfield-label--float" : ""}`}>
        {label}
      </label>
      {error && <span className="md3-textfield-error">{error}</span>}
    </div>
  );
}
