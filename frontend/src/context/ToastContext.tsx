import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from "react";

type TipoToast = "exito" | "error" | "info";

interface Toast {
  id: number;
  mensaje: string;
  tipo: TipoToast;
}

interface ToastContextValue {
  notificar: (mensaje: string, tipo?: TipoToast) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const DURACION_MS = 3500;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const siguienteId = useRef(0);

  const notificar = useCallback((mensaje: string, tipo: TipoToast = "info") => {
    const id = siguienteId.current++;
    setToasts((actuales) => [...actuales, { id, mensaje, tipo }]);
    window.setTimeout(() => {
      setToasts((actuales) => actuales.filter((t) => t.id !== id));
    }, DURACION_MS);
  }, []);

  return (
    <ToastContext.Provider value={{ notificar }}>
      {children}
      <div
        aria-live="polite"
        style={{
          position: "fixed",
          bottom: 20,
          right: 20,
          display: "flex",
          flexDirection: "column",
          gap: 8,
          zIndex: 1000,
          maxWidth: 360,
        }}
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            style={{
              padding: "12px 16px",
              borderRadius: 12,
              fontSize: 13.5,
              fontWeight: 600,
              boxShadow: "0 8px 24px rgba(0, 0, 0, 0.18)",
              ...estiloPorTipo[t.tipo],
            }}
          >
            {t.mensaje}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

const estiloPorTipo: Record<TipoToast, React.CSSProperties> = {
  exito: { background: "var(--rz-accent)", color: "var(--rz-bg)" },
  error: { background: "var(--rz-danger)", color: "#fff" },
  info: { background: "var(--rz-panel-bg)", color: "var(--rz-text)", border: "1px solid var(--rz-panel-border)" },
};

export function useToast(): ToastContextValue {
  const contexto = useContext(ToastContext);
  if (!contexto) {
    throw new Error("useToast debe usarse dentro de ToastProvider");
  }
  return contexto;
}
