import { useEffect, useRef, useState } from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, Info, Loader2, X } from "lucide-react";
import type { ToastItem } from "../../snackbar-context";

/* 自动消失前停留多久；loading 不自动消失。 */
const DURATION: Record<ToastItem["severity"], number | null> = { info: 4000, success: 4000, warning: 6000, error: 8000, loading: null };
const EXIT_MS = 160;

/*
 * 右下角那一叠里的一条通知。悬停时暂停计时（错误信息常常要多看一会儿）；
 * 同一个 key 被替换时 revision 变化，计时从头开始。
 */
export default function Snackbar({ toast, onClose }: { toast: ToastItem; onClose: (id: number) => void }) {
  const [exiting, setExiting] = useState(false);
  const [hovered, setHovered] = useState(false);
  const duration = DURATION[toast.severity];
  const remaining = useRef(duration ?? 0);
  const startedAt = useRef(0);

  // 内容被替换：重新计时，也撤销正在播的退场。
  useEffect(() => {
    remaining.current = duration ?? 0;
    setExiting(false);
  }, [toast.revision, duration]);

  useEffect(() => {
    if (duration === null || hovered || exiting) return;
    startedAt.current = Date.now();
    const timer = setTimeout(() => setExiting(true), remaining.current);
    return () => {
      clearTimeout(timer);
      remaining.current = Math.max(0, remaining.current - (Date.now() - startedAt.current));
    };
  }, [duration, hovered, exiting, toast.revision]);

  useEffect(() => {
    if (!exiting) return;
    const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const timer = setTimeout(() => onClose(toast.id), reduced ? 0 : EXIT_MS);
    return () => clearTimeout(timer);
  }, [exiting, onClose, toast.id]);

  const { severity } = toast;
  const Icon = severity === "success" ? CheckCircle2 : severity === "error" ? AlertCircle : severity === "warning" ? AlertTriangle : severity === "loading" ? Loader2 : Info;
  // 和芯片菜单同一种浅色卡片；颜色只落在图标上，只有警告和错误带色。
  const iconClass = severity === "error" ? "text-danger" : severity === "warning" ? "text-warning" : severity === "success" ? "text-ink" : "text-ink-muted";

  return (
    <div
      className={`group pointer-events-auto relative flex items-start gap-[10px] overflow-hidden rounded-xl border border-line bg-paper-wash py-[11px] pl-[13px] pr-[8px] text-ink shadow-toast motion-reduce:animate-none ${exiting ? "animate-toast-out" : "animate-toast-in"}`}
      role={severity === "error" ? "alert" : "status"}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <Icon className={`mt-[2px] flex-none ${iconClass} ${severity === "loading" ? "animate-spin-fast motion-reduce:animate-none" : ""}`} size={15} strokeWidth={2.2} />
      <span className="min-w-0 flex-1 text-sm leading-[20px] text-ink-soft [overflow-wrap:anywhere]">{toast.message}</span>
      {/* 关闭只在悬停或键盘聚焦时出现，平时不占视线。 */}
      <button
        className="-my-[2px] grid h-[24px] w-[24px] flex-none place-items-center rounded-md border-0 bg-transparent text-ink-muted opacity-0 transition-[opacity,background-color,color] duration-[120ms] hover:bg-surface-active hover:text-ink focus-visible:opacity-100 group-hover:opacity-100"
        onClick={() => setExiting(true)}
        aria-label="关闭通知"
      >
        <X size={13} />
      </button>
      {/* 剩余时间：底边一条细线随计时缩短，悬停时停住；内容被替换时 key 变化、从头开始。 */}
      {duration !== null && (
        <span
          key={toast.revision}
          aria-hidden="true"
          className="absolute inset-x-0 bottom-0 h-[2px] origin-left animate-toast-progress bg-line-strong motion-reduce:hidden"
          style={{ animationDuration: `${duration}ms`, animationPlayState: hovered || exiting ? "paused" : "running" }}
        />
      )}
    </div>
  );
}
