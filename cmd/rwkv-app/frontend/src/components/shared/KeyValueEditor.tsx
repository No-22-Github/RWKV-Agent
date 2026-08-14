import { Plus, X } from "lucide-react";
import Md3TextField from "./Md3TextField";

interface Props {
  entries: Record<string, string>;
  onChange: (entries: Record<string, string>) => void;
  secretValues?: boolean;
  label?: string;
}

export default function KeyValueEditor({ entries, onChange, secretValues, label }: Props) {
  const pairs = Object.entries(entries);

  const update = (oldKey: string, newKey: string, newVal: string) => {
    const next: Record<string, string> = {};
    for (const [k, v] of Object.entries(entries)) {
      if (k === oldKey) next[newKey] = newVal;
      else next[k] = v;
    }
    onChange(next);
  };

  const remove = (key: string) => {
    const next = { ...entries };
    delete next[key];
    onChange(next);
  };

  const add = () => onChange({ ...entries, "": "" });

  return (
    <div className="kv-editor">
      {label && <div className="kv-editor-label">{label}</div>}
      {pairs.map(([k, v], i) => (
        <div key={i} className="kv-editor-row">
          <Md3TextField label="Key" value={k} onChange={(nk) => update(k, nk, v)} />
          <Md3TextField
            label="Value"
            value={v}
            onChange={(nv) => update(k, k, nv)}
            type={secretValues ? "password" : "text"}
          />
          <button className="md3-icon-btn" onClick={() => remove(k)} title="删除">
            <X size={18} />
          </button>
        </div>
      ))}
      <button className="md3-btn md3-btn--tonal" onClick={add} style={{ alignSelf: "flex-start" }}>
        <Plus size={18} /> 添加
      </button>
    </div>
  );
}
