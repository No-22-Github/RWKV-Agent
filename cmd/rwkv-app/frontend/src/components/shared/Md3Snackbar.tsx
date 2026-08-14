import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";

interface Props {
  message: string;
  severity?: "info" | "success" | "error";
  duration?: number;
  onClose: () => void;
}

export default function Md3Snackbar({ message, severity = "info", duration = 4000, onClose }: Props) {
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setExiting(true), duration);
    return () => clearTimeout(t);
  }, [duration]);

  useEffect(() => {
    if (exiting) {
      const t = setTimeout(onClose, 200);
      return () => clearTimeout(t);
    }
  }, [exiting, onClose]);

  const Icon = severity === "success" ? CheckCircle2 : severity === "error" ? AlertCircle : Info;

  return (
    <div className={`md3-snackbar${exiting ? " md3-snackbar--exit" : ""} md3-snackbar--${severity}`}>
      <Icon className="md3-snackbar-icon" size={20} />
      <span className="md3-snackbar-text">{message}</span>
      <button className="md3-snackbar-close" onClick={() => setExiting(true)} aria-label="关闭">
        <X size={18} />
      </button>
    </div>
  );
}
