import { useCallback, useMemo, useRef, useState, type ReactNode } from "react";
import Snackbar from "./components/shared/Snackbar";
import { SnackbarContext, type Severity, type ToastOptions } from "./snackbar";

export interface ToastItem {
  id: number;
  key: string;
  message: string;
  severity: Severity;
  /** 每次原地替换都加一：重启自动消失的计时。 */
  revision: number;
}

/* 同时最多留几条；再多时最早的一条先走。 */
const MAX_TOASTS = 4;

/*
 * 全局通知：右下角一叠，最新的在最下面，浮在设置弹窗之上（设置页和对话页共用同一套）。
 * 带 key 的通知原地替换同 key 的旧通知，不带 key 的各占一条；完全相同的一句话不重复堆。
 */
export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const nextId = useRef(1);

  const show = useCallback((message: string, severity: Severity = "info", options: ToastOptions = {}) => {
    if (!message) return;
    setToasts((current) => {
      const key = options.key ?? `auto:${severity}:${message}`;
      const existing = current.find((toast) => toast.key === key);
      if (existing) {
        return current.map((toast) => toast === existing ? { ...toast, message, severity, revision: toast.revision + 1 } : toast);
      }
      const next = [...current, { id: nextId.current++, key, message, severity, revision: 0 }];
      return next.slice(-MAX_TOASTS);
    });
  }, []);

  const remove = useCallback((id: number) => setToasts((current) => current.filter((toast) => toast.id !== id)), []);
  const dismiss = useCallback((key: string) => setToasts((current) => current.filter((toast) => toast.key !== key)), []);
  const value = useMemo(() => ({ show, dismiss }), [show, dismiss]);

  return (
    <SnackbarContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-[18px] right-[18px] z-[1100] flex w-[min(360px,calc(100vw-36px))] flex-col items-stretch gap-[8px]" aria-live="polite">
        {toasts.map((toast) => <Snackbar key={toast.id} toast={toast} onClose={remove} />)}
      </div>
    </SnackbarContext.Provider>
  );
}
