import { useState, type FormEvent } from "react";
import { useAuth } from "../../context/AuthContext";
import { ErrorApi } from "../../api/client";
import { BotonTema } from "../../components/BotonTema";

export function LoginPage() {
  const { iniciarSesion, mfaPendiente, confirmarMfa, cancelarMfa } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [codigo, setCodigo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function manejarLogin(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await iniciarSesion(email, password);
    } catch (err) {
      setError(err instanceof ErrorApi ? String(err.detalle) : "No se pudo iniciar sesión");
    } finally {
      setEnviando(false);
    }
  }

  async function manejarMfa(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await confirmarMfa(codigo);
    } catch (err) {
      setError(err instanceof ErrorApi ? String(err.detalle) : "Código incorrecto");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", background: "var(--rz-bg)", color: "var(--rz-text)" }}>
      <PanelDeMarca />

      <div
        style={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
          position: "relative",
        }}
      >
        <div style={{ position: "absolute", top: 24, right: 24 }}>
          <BotonTema />
        </div>

        <div style={{ width: "100%", maxWidth: 440, display: "flex", flexDirection: "column", gap: 32 }}>
          <div className="rz-login-marca-movil" style={{ display: "none", alignItems: "center", gap: 12 }}>
            <Logotipo />
          </div>

          {mfaPendiente ? (
            <form onSubmit={manejarMfa} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <div>
                <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 30, margin: "0 0 8px", letterSpacing: "-0.01em" }}>
                  Verificación en dos pasos
                </h1>
                <p style={{ fontSize: 14.5, color: "var(--rz-text-muted)", margin: 0, lineHeight: 1.5 }}>
                  Ingresa el código de 6 dígitos de tu app de autenticación.
                </p>
              </div>
              <Campo
                etiqueta="Código"
                tipo="text"
                valor={codigo}
                onCambio={setCodigo}
                autoFocus
                inputMode="numeric"
                maxLength={6}
                monoespaciado
                icono={<IconoLlave />}
              />
              {error && <Aviso mensaje={error} />}
              <BotonPrimario texto="Verificar" enviando={enviando} />
              <button
                type="button"
                onClick={cancelarMfa}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--rz-text-muted)",
                  fontSize: 13,
                  cursor: "pointer",
                  padding: 0,
                }}
              >
                ← Volver a intentar con otra cuenta
              </button>
            </form>
          ) : (
            <form onSubmit={manejarLogin} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <div>
                <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 30, margin: "0 0 8px", letterSpacing: "-0.01em" }}>
                  Bienvenido de vuelta
                </h1>
                <p style={{ fontSize: 14.5, color: "var(--rz-text-muted)", margin: 0, lineHeight: 1.5 }}>
                  Ingresa a tu panel de operaciones.
                </p>
              </div>
              <Campo
                etiqueta="Correo electrónico"
                tipo="email"
                valor={email}
                onCambio={setEmail}
                autoFocus
                icono={<IconoCorreo />}
                placeholder="tú@andinareparto.pe"
              />
              <Campo
                etiqueta="Contraseña"
                tipo="password"
                valor={password}
                onCambio={setPassword}
                icono={<IconoCandado />}
                placeholder="••••••••"
              />
              {error && <Aviso mensaje={error} />}
              <BotonPrimario texto="Ingresar" enviando={enviando} />
            </form>
          )}

          <p style={{ margin: 0, fontSize: 12, color: "var(--rz-text-faint)", textAlign: "center" }}>
            Acceso exclusivo para personal de Andina Reparto S.A.C.
          </p>
        </div>
      </div>

      <style>{`
        @media (max-width: 899px) {
          .rz-login-visual { display: none !important; }
          .rz-login-marca-movil { display: flex !important; }
        }
      `}</style>
    </div>
  );
}

function PanelDeMarca() {
  return (
    <div
      className="rz-login-visual"
      style={{
        width: "50%",
        maxWidth: 680,
        position: "relative",
        overflow: "hidden",
        background: "var(--rz-map-bg)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: 56,
      }}
    >
      <svg
        viewBox="0 0 600 900"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
      >
        <rect width="600" height="900" fill="var(--rz-map-bg)" />
        <g fill="var(--rz-map-block)">
          <rect x="20" y="20" width="140" height="90" rx="6" />
          <rect x="180" y="20" width="90" height="150" rx="6" />
          <rect x="290" y="20" width="160" height="90" rx="6" />
          <rect x="470" y="20" width="110" height="230" rx="6" />
          <rect x="20" y="130" width="140" height="120" rx="6" />
          <rect x="290" y="130" width="160" height="200" rx="6" />
          <rect x="20" y="270" width="240" height="110" rx="6" />
          <rect x="470" y="270" width="110" height="160" rx="6" />
          <rect x="20" y="400" width="140" height="160" rx="6" />
          <rect x="180" y="350" width="90" height="210" rx="6" />
          <rect x="290" y="350" width="160" height="90" rx="6" />
          <rect x="290" y="460" width="70" height="100" rx="6" />
          <rect x="380" y="450" width="90" height="110" rx="6" />
          <rect x="20" y="580" width="240" height="130" rx="6" />
          <rect x="290" y="580" width="180" height="90" rx="6" />
          <rect x="20" y="730" width="150" height="150" rx="6" />
          <rect x="200" y="700" width="140" height="180" rx="6" />
          <rect x="370" y="580" width="110" height="150" rx="6" />
        </g>
        <path
          d="M0 400 C 140 340, 220 480, 340 410 S 560 310, 600 370"
          fill="none"
          stroke="var(--rz-accent)"
          strokeWidth="6"
          strokeLinecap="round"
          opacity="0.5"
        />
        <path
          d="M40 480 Q 180 420 260 460 T 460 360 Q 540 320 600 260"
          fill="none"
          stroke="var(--rz-accent-2)"
          strokeWidth="5"
          strokeLinecap="round"
          opacity="0.35"
        />
      </svg>

      <div style={{ position: "relative", zIndex: 1 }}>
        <Logotipo />
      </div>

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          gap: 20,
          background: "var(--rz-map-bg)",
          borderRadius: 20,
          padding: "24px 28px",
          margin: "0 -28px -24px",
        }}
      >
        <div
          style={{
            alignSelf: "flex-start",
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "10px 16px",
            borderRadius: 999,
            background: "var(--rz-accent-soft-bg)",
            border: "1px solid var(--rz-accent-soft-border)",
          }}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--rz-accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M11 20A7 7 0 019.8 6.1C15.5 5 17 3 17 3s.5 3.5 2 6c1.6 2.7 1.5 6-1 8-1 1-2.5 1-3.5 1" />
            <path d="M2 21c0-3.5 2.5-6 5-6" />
          </svg>
          <span style={{ fontFamily: "var(--rz-font-mono)", fontWeight: 600, fontSize: 13.5, color: "var(--rz-accent)" }}>
            Rutas verificadas y sostenibles
          </span>
        </div>
        <h2 style={{ fontFamily: "var(--rz-font-display)", fontSize: 34, lineHeight: 1.25, margin: 0, maxWidth: 480 }}>
          Optimización de rutas para una logística más limpia en Huancayo.
        </h2>
        <p style={{ margin: 0, fontSize: 15, color: "var(--rz-text-muted)", maxWidth: 420, lineHeight: 1.6 }}>
          MFA, control de acceso por rol y trazabilidad completa para el equipo de Andina Reparto S.A.C.
        </p>
      </div>
    </div>
  );
}

function Logotipo() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div
        aria-hidden="true"
        style={{
          width: 40,
          height: 40,
          borderRadius: 11,
          background: "var(--rz-accent)",
          color: "var(--rz-bg)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "var(--rz-font-display)",
          fontWeight: 700,
          fontSize: 15,
          flexShrink: 0,
        }}
      >
        R0
      </div>
      <div>
        <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 18 }}>RouteZero</div>
        <div style={{ fontSize: 12, color: "var(--rz-text-muted)" }}>Andina Reparto S.A.C.</div>
      </div>
    </div>
  );
}

function Campo(props: {
  etiqueta: string;
  tipo: string;
  valor: string;
  onCambio: (valor: string) => void;
  autoFocus?: boolean;
  inputMode?: "numeric";
  maxLength?: number;
  monoespaciado?: boolean;
  icono?: React.ReactNode;
  placeholder?: string;
}) {
  const id = `campo-${props.etiqueta.toLowerCase().replace(/\s+/g, "-")}`;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <label htmlFor={id} style={{ fontSize: 13, color: "var(--rz-text-muted)", fontWeight: 600 }}>
        {props.etiqueta}
      </label>
      <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
        {props.icono && (
          <span
            aria-hidden="true"
            style={{
              position: "absolute",
              left: 14,
              display: "flex",
              color: "var(--rz-text-faint)",
              pointerEvents: "none",
            }}
          >
            {props.icono}
          </span>
        )}
        <input
          id={id}
          type={props.tipo}
          value={props.valor}
          onChange={(evento) => props.onCambio(evento.target.value)}
          required
          autoFocus={props.autoFocus}
          inputMode={props.inputMode}
          maxLength={props.maxLength}
          placeholder={props.placeholder}
          style={{
            width: "100%",
            height: 52,
            borderRadius: 12,
            border: "1px solid var(--rz-panel-border)",
            background: "var(--rz-panel-bg)",
            color: "var(--rz-text)",
            padding: props.icono ? "0 14px 0 42px" : "0 14px",
            fontSize: 15,
            fontFamily: props.monoespaciado ? "var(--rz-font-mono)" : "inherit",
            letterSpacing: props.monoespaciado ? "0.3em" : "normal",
          }}
        />
      </div>
    </div>
  );
}

function BotonPrimario({ texto, enviando }: { texto: string; enviando: boolean }) {
  return (
    <button
      type="submit"
      disabled={enviando}
      style={{
        height: 54,
        borderRadius: 14,
        border: "none",
        background: "var(--rz-accent)",
        color: "var(--rz-bg)",
        fontWeight: 700,
        fontSize: 15.5,
        cursor: enviando ? "default" : "pointer",
        opacity: enviando ? 0.7 : 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
        marginTop: 4,
      }}
    >
      {enviando ? "Un momento…" : texto}
      {!enviando && (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M5 12h14M13 5l7 7-7 7" />
        </svg>
      )}
    </button>
  );
}

function Aviso({ mensaje }: { mensaje: string }) {
  return (
    <div
      role="alert"
      style={{
        borderRadius: 10,
        background: "var(--rz-danger-soft-bg)",
        color: "var(--rz-danger)",
        padding: "10px 12px",
        fontSize: 13,
      }}
    >
      {mensaje}
    </div>
  );
}

function IconoCorreo() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="M3 7l9 6 9-6" />
    </svg>
  );
}

function IconoCandado() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="11" width="16" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 018 0v4" />
    </svg>
  );
}

function IconoLlave() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="8" cy="15" r="4" />
      <path d="M10.5 12.5L20 3M20 3h-4M20 3v4" />
    </svg>
  );
}
