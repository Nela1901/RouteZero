import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../../context/AuthContext";
import { api, ErrorApi } from "../../api/client";
import { useToast } from "../../context/ToastContext";

interface InscripcionMfa {
  factor_id: string;
  qr_code: string;
  secret: string;
}

interface Sesion {
  sesion_id: string;
  dispositivo_info: string | null;
  ip_origen: string | null;
  creado_en: string;
  ultimo_uso_en: string;
  actual: boolean;
}

const formateadorFecha = new Intl.DateTimeFormat("es-PE", { dateStyle: "medium", timeStyle: "short" });

export function SeguridadPage() {
  const { usuario, recargarUsuario } = useAuth();
  const [inscripcion, setInscripcion] = useState<InscripcionMfa | null>(null);
  const [codigo, setCodigo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [exito, setExito] = useState(false);

  async function iniciarInscripcion() {
    setError(null);
    setEnviando(true);
    try {
      const datos = await api.post<InscripcionMfa>("/api/auth/mfa/inscribir");
      setInscripcion(datos);
    } catch (err) {
      setError(err instanceof ErrorApi ? String(err.detalle) : "No se pudo iniciar la inscripción");
    } finally {
      setEnviando(false);
    }
  }

  async function confirmarInscripcion(evento: FormEvent) {
    evento.preventDefault();
    if (!inscripcion) return;
    setError(null);
    setEnviando(true);
    try {
      await api.post("/api/auth/mfa/confirmar", { factor_id: inscripcion.factor_id, codigo });
      setInscripcion(null);
      setCodigo("");
      setExito(true);
      await recargarUsuario();
    } catch (err) {
      setError(err instanceof ErrorApi ? String(err.detalle) : "Código incorrecto");
    } finally {
      setEnviando(false);
    }
  }

  function cancelarInscripcion() {
    setInscripcion(null);
    setCodigo("");
    setError(null);
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 640 }}>
      <div>
        <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Seguridad</h1>
        <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
          Verificación en dos pasos (MFA) para tu cuenta.
        </p>
      </div>

      <div
        style={{
          borderRadius: 16,
          border: "1px solid var(--rz-panel-border)",
          background: "var(--rz-panel-bg)",
          padding: 24,
          display: "flex",
          flexDirection: "column",
          gap: 18,
        }}
      >
        {usuario?.mfaActivo ? (
          <EstadoActivo />
        ) : inscripcion ? (
          <FormularioConfirmacion
            inscripcion={inscripcion}
            codigo={codigo}
            onCambioCodigo={setCodigo}
            onEnviar={confirmarInscripcion}
            onCancelar={cancelarInscripcion}
            error={error}
            enviando={enviando}
          />
        ) : (
          <EstadoInicial onIniciar={iniciarInscripcion} error={error} enviando={enviando} exito={exito} />
        )}
      </div>

      <SeccionSesiones />
    </div>
  );
}

function SeccionSesiones() {
  const { cerrarSesion } = useAuth();
  const { notificar } = useToast();
  const [sesiones, setSesiones] = useState<Sesion[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [revocandoId, setRevocandoId] = useState<string | null>(null);
  const [cerrandoTodas, setCerrandoTodas] = useState(false);

  async function cargar() {
    try {
      setSesiones(await api.get<Sesion[]>("/api/auth/sesiones"));
    } catch (err) {
      setError(err instanceof ErrorApi ? String(err.detalle) : "No se pudieron cargar las sesiones");
    }
  }

  useEffect(() => {
    void cargar();
  }, []);

  async function revocar(sesion: Sesion) {
    if (!window.confirm(`¿Cerrar la sesión de "${sesion.dispositivo_info ?? "dispositivo desconocido"}"?`)) return;
    setError(null);
    setRevocandoId(sesion.sesion_id);
    try {
      await api.delete(`/api/auth/sesiones/${sesion.sesion_id}`);
      await cargar();
      notificar("Sesión cerrada", "exito");
    } catch (err) {
      const mensaje = err instanceof ErrorApi ? String(err.detalle) : "No se pudo cerrar la sesión";
      setError(mensaje);
      notificar(mensaje, "error");
    } finally {
      setRevocandoId(null);
    }
  }

  async function cerrarTodas() {
    if (!window.confirm("¿Cerrar todas las sesiones, incluida esta? Deberás iniciar sesión de nuevo.")) return;
    setCerrandoTodas(true);
    try {
      await cerrarSesion();
    } finally {
      setCerrandoTodas(false);
    }
  }

  return (
    <div
      style={{
        borderRadius: 16,
        border: "1px solid var(--rz-panel-border)",
        background: "var(--rz-panel-bg)",
        padding: 24,
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15 }}>Sesiones activas</div>
          <p style={{ margin: "4px 0 0", fontSize: 13, color: "var(--rz-text-muted)", lineHeight: 1.5 }}>
            Dispositivos con acceso vigente a tu cuenta. Cerrar una sesión la invalida al instante.
          </p>
        </div>
        {sesiones && sesiones.length > 0 && (
          <button type="button" onClick={() => void cerrarTodas()} disabled={cerrandoTodas} style={estiloBotonPeligro}>
            {cerrandoTodas ? "Cerrando…" : "Cerrar todas"}
          </button>
        )}
      </div>

      {error && <div style={estiloAviso}>{error}</div>}

      {sesiones === null ? (
        <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>Cargando…</p>
      ) : sesiones.length === 0 ? (
        <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>No hay sesiones activas.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {sesiones.map((s) => (
            <div
              key={s.sesion_id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                padding: "12px 4px",
                borderTop: "1px solid var(--rz-panel-border)",
              }}
            >
              <span
                aria-hidden="true"
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  flexShrink: 0,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: "var(--rz-bg)",
                  border: "1px solid var(--rz-panel-border)",
                  color: "var(--rz-text-muted)",
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="4" y="3" width="16" height="14" rx="2" />
                  <path d="M8 21h8M12 17v4" />
                </svg>
              </span>
              <div style={{ flexGrow: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 13.5, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {s.dispositivo_info ?? "Dispositivo desconocido"}
                  </span>
                  {s.actual && (
                    <span
                      style={{
                        fontSize: 10.5,
                        fontWeight: 700,
                        textTransform: "uppercase",
                        color: "var(--rz-accent)",
                        background: "var(--rz-accent-soft-bg)",
                        padding: "2px 8px",
                        borderRadius: 999,
                        flexShrink: 0,
                      }}
                    >
                      Esta sesión
                    </span>
                  )}
                </div>
                <div style={{ fontSize: 12, color: "var(--rz-text-muted)", marginTop: 2 }}>
                  {s.ip_origen ?? "IP desconocida"} · último uso {formateadorFecha.format(new Date(s.ultimo_uso_en))}
                </div>
              </div>
              {!s.actual && (
                <button
                  type="button"
                  onClick={() => void revocar(s)}
                  disabled={revocandoId === s.sesion_id}
                  style={estiloBotonSecundario}
                >
                  {revocandoId === s.sesion_id ? "Cerrando…" : "Cerrar sesión"}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EstadoInicial({
  onIniciar,
  error,
  enviando,
  exito,
}: {
  onIniciar: () => void;
  error: string | null;
  enviando: boolean;
  exito: boolean;
}) {
  return (
    <>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
        <IconoEscudo activo={false} />
        <div>
          <div style={{ fontWeight: 700, fontSize: 15 }}>Verificación en dos pasos desactivada</div>
          <p style={{ margin: "4px 0 0", fontSize: 13, color: "var(--rz-text-muted)", lineHeight: 1.5 }}>
            Agrega una capa extra de seguridad: además de tu contraseña, pedirá un código de 6 dígitos generado por
            una app como Google Authenticator o Authy.
          </p>
        </div>
      </div>
      {exito && (
        <div style={estiloExito}>Verificación en dos pasos activada correctamente.</div>
      )}
      {error && <div style={estiloAviso}>{error}</div>}
      <button type="button" onClick={onIniciar} disabled={enviando} style={estiloBotonPrimario}>
        {enviando ? "Generando código QR…" : "Activar verificación en dos pasos"}
      </button>
    </>
  );
}

function FormularioConfirmacion({
  inscripcion,
  codigo,
  onCambioCodigo,
  onEnviar,
  onCancelar,
  error,
  enviando,
}: {
  inscripcion: InscripcionMfa;
  codigo: string;
  onCambioCodigo: (v: string) => void;
  onEnviar: (e: FormEvent) => void;
  onCancelar: () => void;
  error: string | null;
  enviando: boolean;
}) {
  return (
    <form onSubmit={onEnviar} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div>
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>Escanea el código QR</div>
        <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)", lineHeight: 1.5 }}>
          Usa tu app de autenticación para escanearlo y luego ingresa el código de 6 dígitos que te muestre.
        </p>
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start", flexWrap: "wrap" }}>
        {inscripcion.qr_code && (
          <div
            role="img"
            aria-label="Código QR para inscribir la verificación en dos pasos"
            className="rz-codigo-qr"
            style={{ width: 168, height: 168, borderRadius: 12, background: "#fff", padding: 8, flexShrink: 0 }}
            dangerouslySetInnerHTML={{ __html: inscripcion.qr_code }}
          />
        )}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, flexGrow: 1, minWidth: 200 }}>
          <div>
            <div style={{ fontSize: 12, color: "var(--rz-text-muted)", marginBottom: 4 }}>
              ¿No puedes escanear? Ingresa esta clave manualmente:
            </div>
            <code
              style={{
                display: "block",
                fontFamily: "var(--rz-font-mono)",
                fontSize: 13,
                padding: "8px 10px",
                borderRadius: 8,
                background: "var(--rz-bg)",
                border: "1px solid var(--rz-panel-border)",
                wordBreak: "break-all",
              }}
            >
              {inscripcion.secret}
            </code>
          </div>

          <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
            Código de 6 dígitos
            <input
              required
              autoFocus
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={codigo}
              onChange={(e) => onCambioCodigo(e.target.value)}
              style={{
                height: 44,
                borderRadius: 10,
                border: "1px solid var(--rz-panel-border)",
                background: "var(--rz-bg)",
                color: "var(--rz-text)",
                padding: "0 12px",
                fontSize: 16,
                fontFamily: "var(--rz-font-mono)",
                letterSpacing: "0.3em",
                width: 140,
              }}
            />
          </label>
        </div>
      </div>

      {error && <div style={estiloAviso}>{error}</div>}

      <div style={{ display: "flex", gap: 10 }}>
        <button type="submit" disabled={enviando} style={estiloBotonPrimario}>
          {enviando ? "Verificando…" : "Confirmar y activar"}
        </button>
        <button type="button" onClick={onCancelar} style={estiloBotonSecundario}>
          Cancelar
        </button>
      </div>
    </form>
  );
}

function EstadoActivo() {
  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
      <IconoEscudo activo={true} />
      <div>
        <div style={{ fontWeight: 700, fontSize: 15, color: "var(--rz-accent)" }}>Verificación en dos pasos activa</div>
        <p style={{ margin: "4px 0 0", fontSize: 13, color: "var(--rz-text-muted)", lineHeight: 1.5 }}>
          Tu cuenta pide un código además de la contraseña al iniciar sesión.
        </p>
      </div>
    </div>
  );
}

function IconoEscudo({ activo }: { activo: boolean }) {
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
        background: activo ? "var(--rz-accent-soft-bg)" : "var(--rz-panel-bg)",
        border: `1px solid ${activo ? "var(--rz-accent-soft-border)" : "var(--rz-panel-border)"}`,
        color: activo ? "var(--rz-accent)" : "var(--rz-text-muted)",
      }}
    >
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" />
        {activo && <path d="M9 12l2 2 4-4" />}
      </svg>
    </div>
  );
}

const estiloBotonPrimario: React.CSSProperties = {
  height: 44,
  padding: "0 20px",
  borderRadius: 12,
  border: "none",
  background: "var(--rz-accent)",
  color: "var(--rz-bg)",
  fontWeight: 700,
  fontSize: 13.5,
  cursor: "pointer",
  alignSelf: "flex-start",
};

const estiloBotonSecundario: React.CSSProperties = {
  height: 44,
  padding: "0 16px",
  borderRadius: 12,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text)",
  fontSize: 13.5,
  cursor: "pointer",
};

const estiloBotonPeligro: React.CSSProperties = {
  height: 36,
  padding: "0 14px",
  borderRadius: 10,
  border: "1px solid var(--rz-danger-soft-bg)",
  background: "var(--rz-danger-soft-bg)",
  color: "var(--rz-danger)",
  fontSize: 12.5,
  fontWeight: 600,
  cursor: "pointer",
  flexShrink: 0,
};

const estiloAviso: React.CSSProperties = {
  borderRadius: 10,
  background: "var(--rz-danger-soft-bg)",
  color: "var(--rz-danger)",
  padding: "10px 12px",
  fontSize: 13,
};

const estiloExito: React.CSSProperties = {
  borderRadius: 10,
  background: "var(--rz-accent-soft-bg)",
  color: "var(--rz-accent)",
  padding: "10px 12px",
  fontSize: 13,
};
