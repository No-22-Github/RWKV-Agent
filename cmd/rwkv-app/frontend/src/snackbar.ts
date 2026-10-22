import { createContext, useContext } from "react";

/*
 * 通知的种类。info / success 4 秒、warning 6 秒、error 8 秒后自动消失（悬停时暂停）；
 * loading 不自动消失，等同一个 key 的结果通知把它换掉。
 */
export type Severity = "info" | "success" | "warning" | "error" | "loading";

export interface ToastOptions {
  /** 同一件事的通知共用一个 key：新的一条原地替换旧的（例如「正在测试…」换成「连接成功」）。 */
  key?: string;
}

export interface SnackbarCtx {
  show: (message: string, severity?: Severity, options?: ToastOptions) => void;
  /** 收起某个 key 的通知（例如进行中的操作被取消）。 */
  dismiss: (key: string) => void;
}

export const SnackbarContext = createContext<SnackbarCtx>({ show: () => {}, dismiss: () => {} });

export function useSnackbar() {
  return useContext(SnackbarContext);
}
