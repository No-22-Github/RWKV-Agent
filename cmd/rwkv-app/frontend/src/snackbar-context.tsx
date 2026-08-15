import { useCallback, useState, type ReactNode } from "react";
import Snackbar from "./components/shared/Snackbar";
import { SnackbarContext, type Severity } from "./snackbar";

interface SnackbarState {
  message: string;
  severity: Severity;
  key: number;
}

export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SnackbarState | null>(null);

  const show = useCallback((message: string, severity: Severity = "info") => {
    setState({ message, severity, key: Date.now() });
  }, []);

  return (
    <SnackbarContext.Provider value={{ show }}>
      {children}
      {state && (
        <Snackbar
          key={state.key}
          message={state.message}
          severity={state.severity}
          onClose={() => setState(null)}
        />
      )}
    </SnackbarContext.Provider>
  );
}
