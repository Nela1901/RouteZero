import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from "react";

interface OpcionesConfirmacion {
  titulo?: string;
  mensaje: string;
  textoAceptar?: string;
  textoCancelar?: string;
  peligroso?: boolean;
}

interface EstadoDialogo extends OpcionesConfirmacion {
  resolver: (valor: boolean) => void;
}

interface ConfirmContextValue {
  confirmar: (opciones: OpcionesConfirmacion | string) => Promise<boolean>;
}

const ConfirmContext = createContext<ConfirmContextValue | null>(null);

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [dialogo, setDialogo] = useState<EstadoDialogo | null>(null);
  const resolverActual = useRef<((valor: boolean) => void) | null>(null);

  const confirmar = useCallback((opciones: OpcionesConfirmacion | string) => {
    const normalizado = typeof opciones === "string" ? { mensaje: opciones } : opciones;
    return new Promise<boolean>((resolver) => {
      resolverActual.current = resolver;
      setDialogo({ ...normalizado, resolver });
    });
  }, []);

  function responder(valor: boolean) {
    resolverActual.current?.(valor);
    resolverActual.current = null;
    setDialogo(null);
  }

  return (
    <ConfirmContext.Provider value={{ confirmar }}>
      {children}
      {dialogo && (
        <div
          role="presentation"
          onClick={() => responder(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(10, 13, 14, 0.55)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 2000,
            padding: 20,
          }}
        >
          <div
            role="alertdialog"
            aria-modal="true"
            aria-label={dialogo.titulo ?? "Confirmación"}
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "100%",
              maxWidth: 380,
              borderRadius: 18,
              background: "var(--rz-panel-solid-bg)",
              border: "1px solid var(--rz-panel-border)",
              boxShadow: "0 24px 60px rgba(0, 0, 0, 0.35)",
              padding: 24,
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
              <IconoAlerta peligroso={dialogo.peligroso} />
              <div>
                <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 16 }}>
                  {dialogo.titulo ?? "Confirmar acción"}
                </div>
                <p style={{ margin: "6px 0 0", fontSize: 13.5, color: "var(--rz-text-muted)", lineHeight: 1.5 }}>
                  {dialogo.mensaje}
                </p>
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
              <button type="button" onClick={() => responder(false)} style={estiloBotonSecundario} autoFocus>
                {dialogo.textoCancelar ?? "Cancelar"}
              </button>
              <button
                type="button"
                onClick={() => responder(true)}
                style={dialogo.peligroso ? estiloBotonPeligro : estiloBotonPrimario}
              >
                {dialogo.textoAceptar ?? "Confirmar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  );
}

function IconoAlerta({ peligroso }: { peligroso?: boolean }) {
  const color = peligroso ? "var(--rz-danger)" : "var(--rz-accent)";
  const fondo = peligroso ? "var(--rz-danger-soft-bg)" : "var(--rz-accent-soft-bg)";
  return (
    <div
      aria-hidden="true"
      style={{
        width: 40,
        height: 40,
        borderRadius: 12,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: fondo,
        color,
      }}
    >
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8v5" />
        <path d="M12 16.2v.1" />
      </svg>
    </div>
  );
}

const estiloBotonPrimario: React.CSSProperties = {
  height: 40,
  padding: "0 18px",
  borderRadius: 12,
  border: "none",
  background: "var(--rz-accent)",
  color: "var(--rz-bg)",
  fontWeight: 700,
  fontSize: 13.5,
  cursor: "pointer",
};

const estiloBotonPeligro: React.CSSProperties = {
  height: 40,
  padding: "0 18px",
  borderRadius: 12,
  border: "none",
  background: "var(--rz-danger)",
  color: "#fff",
  fontWeight: 700,
  fontSize: 13.5,
  cursor: "pointer",
};

const estiloBotonSecundario: React.CSSProperties = {
  height: 40,
  padding: "0 16px",
  borderRadius: 12,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text)",
  fontSize: 13.5,
  cursor: "pointer",
};

export function useConfirm(): ConfirmContextValue {
  const contexto = useContext(ConfirmContext);
  if (!contexto) {
    throw new Error("useConfirm debe usarse dentro de ConfirmProvider");
  }
  return contexto;
}
