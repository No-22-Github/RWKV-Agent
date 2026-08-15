import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";

interface Props {
  message: string;
  severity?: "info" | "success" | "error";
  duration?: number;
  onClose: () => void;
}

export default function Snackbar({ message, severity = "info", duration = 4000, onClose }: Props) {
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
  const iconClass = severity === "success" ? "text-brand-bright" : severity === "error" ? "text-danger" : "text-white/80";

  return (
    <div
      className={`fixed bottom-6 left-1/2 z-[1100] flex -translate-x-1/2 items-center gap-3 rounded-none bg-ink px-4 py-3 text-white shadow-[0_10px_30px_rgba(43,39,33,.35)] transition-all duration-200 ${exiting ? "translate-y-2 opacity-0" : "opacity-100"}`}
      role="status"
    >
      <Icon className={`flex-none ${iconClass}`} size={20} />
      <span className="text-[13px] leading-5">{message}</span>
      <button
        className="grid h-7 w-7 flex-none place-items-center rounded-none text-white/70 transition-colors hover:bg-white/10 hover:text-white"
        onClick={() => setExiting(true)}
        aria-label="关闭"
      >
        <X size={18} />
      </button>
    </div>
  );
}
