import { createContext, useContext } from "react";

export type Severity = "info" | "success" | "error";

export interface SnackbarCtx {
  show: (message: string, severity?: Severity) => void;
}

export const SnackbarContext = createContext<SnackbarCtx>({ show: () => {} });

export function useSnackbar() {
  return useContext(SnackbarContext);
}
