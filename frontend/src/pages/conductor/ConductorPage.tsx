import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useCallback, useEffect, useState } from "react";
import { api, mensajeDeError } from "../../api/client";
import { BotonTema } from "../../components/BotonTema";
import { estiloAviso } from "../../components/ui";
import { useAuth } from "../../context/AuthContext";
import { useConfirm } from "../../context/ConfirmContext";
import { useToast } from "../../context/ToastContext";

const CENTRO_HUANCAYO: [number, number] = [-12.0653, -75.2049];
const OSM_TILES = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const REFRESCO_MS = 30_000;
const COLOR_RUTA = "#0072B2";
const COLOR_NIVEL: Record<string, string> = { AMARILLO: "#e0a800", ROJO: "#d63031" };
const ETIQUETA_NIVEL: Record<string, string> = { AMARILLO: "Congestión moderada", ROJO: "Congestión alta" };
const COLOR_ENTREGA: Record<string, string> = { ENTREGADO: "#2e9e57", FALLIDO: "#d63031", CANCELADO: "#8a8a8a" };

interface Parada {
  orden: number;
  pedido_id: string;
  cliente: string;
  descripcion?: string | null;
  peso_kg?: string | number;
  prioridad: string;
  latitud: string | number;
  longitud: string | number;
  hora_estimada: string | null;
  minutos_retraso: number;
  estado_entrega: "PENDIENTE" | "ENTREGADO" | "FALLIDO";
  pedido_estado: string;
}

interface Tramo {
  desde: number;
  hasta: number;
  puntos: [number, number][];
}

interface Alerta {
  calle: string;
  nivel: "AMARILLO" | "ROJO";
  factor: number;
  motivos: string[];
  en_tu_ruta: boolean;
  segmentos: [number, number][][];
}

export interface MiRuta {
  fecha_jornada: string;
  hora: string;
  deposito: { latitud: number; longitud: number };
  vinculado: boolean;
  mensaje: string | null;
  conductor: { conductor_id: string; nombre: string } | null;
  ruta: {
    ruta_id: string;
    estado: string;
    hora_salida: string | null;
    hora_regreso: string | null;
    paradas: Parada[];
    tramos: Tramo[];
  } | null;
  siguiente_orden: number | null;
  entregadas: number;
  pendientes: number;
  alertas: Alerta[];
}

const hora = (valor: string | null) => (valor ? valor.slice(0, 5) : "—");

function ahoraLocal(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

export function ConductorPage() {
  const { usuario, cerrarSesion } = useAuth();
  const { notificar } = useToast();
  const { confirmar } = useConfirm();
  const [datos, setDatos] = useState<MiRuta | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actualizado, setActualizado] = useState<string | null>(null);
  const [registrando, setRegistrando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setDatos(await api.get<MiRuta>("/api/rutas/mi-ruta"));
      setError(null);
      setActualizado(ahoraLocal());
    } catch (err) {
      setError(mensajeDeError(err, "No se pudo cargar tu ruta"));
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  // Se vuelve a pedir la ruta cada 30 s: el despacho puede re-optimizarla mientras el conductor circula
  useEffect(() => {
    const reloj = window.setInterval(() => void cargar(), REFRESCO_MS);
    return () => window.clearInterval(reloj);
  }, [cargar]);

  const ruta = datos?.ruta ?? null;
  const paradas = ruta?.paradas ?? [];
  const atendibles = paradas.filter((p) => p.pedido_estado !== "CANCELADO");
  const siguiente = paradas.find((p) => p.orden === datos?.siguiente_orden) ?? null;
  const otrasPendientes = atendibles.filter((p) => p.estado_entrega === "PENDIENTE" && p.orden !== datos?.siguiente_orden);
  const atendidas = paradas.filter((p) => p.estado_entrega !== "PENDIENTE");
  const canceladas = paradas.filter((p) => p.pedido_estado === "CANCELADO" && p.estado_entrega === "PENDIENTE");

  async function registrar(parada: Parada, estado: "ENTREGADO" | "FALLIDO") {
    if (!ruta) return;
    const acepto = await confirmar({
      titulo: estado === "ENTREGADO" ? "Confirmar entrega" : "Entrega fallida",
      mensaje:
        estado === "ENTREGADO"
          ? `¿Confirmas que entregaste el pedido de ${parada.cliente}? No se puede deshacer.`
          : `¿No se pudo entregar el pedido de ${parada.cliente}? No se puede deshacer.`,
      textoAceptar: estado === "ENTREGADO" ? "Sí, entregado" : "Sí, no se pudo",
      peligroso: estado === "FALLIDO",
    });
    if (!acepto) return;
    setRegistrando(true);
    try {
      await api.patch(`/api/rutas/${ruta.ruta_id}/paradas/${parada.pedido_id}/entrega`, { estado });
      notificar(estado === "ENTREGADO" ? "Entrega registrada" : "Entrega fallida registrada", "exito");
      await cargar();
    } catch (err) {
      notificar(mensajeDeError(err, "No se pudo registrar la entrega"), "error");
    } finally {
      setRegistrando(false);
    }
  }

  const nombre = datos?.conductor?.nombre ?? usuario?.email.split("@")[0];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--rz-bg)", color: "var(--rz-text)" }}>
      <header
        style={{
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "14px 16px",
          background: "var(--rz-header-bg)",
          borderBottom: "1px solid var(--rz-panel-border)",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
          <h1 style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 16, margin: 0, overflowWrap: "anywhere" }}>Hola, {nombre}</h1>
          <span style={{ fontSize: 12, color: "var(--rz-text-muted)" }} role="status">
            Vista de conductor ·{" "}
            {cargando && datos === null ? "Cargando tu ruta…" : cargando ? "Actualizando…" : actualizado ? `Actualizado a las ${actualizado}` : ""}
          </span>
        </div>
        <div style={{ flexGrow: 1 }} />
        <BotonTema />
      </header>

      <main style={{ flexGrow: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column" }}>
        {error && <div style={{ ...estiloAviso, margin: 14 }}>{error}</div>}

        {datos && !ruta && (
          <div role="status" style={{ ...estiloTarjeta, margin: 14 }}>
            <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 18 }}>
              {datos.vinculado ? "Sin ruta por ahora" : "Cuenta sin vincular"}
            </div>
            <p style={{ margin: 0, fontSize: 14, color: "var(--rz-text-muted)", lineHeight: 1.5 }}>{datos.mensaje}</p>
          </div>
        )}

        {datos && ruta && (
          <>
            <ResumenRuta datos={datos} />

            {datos.alertas.length > 0 && (
              <section aria-label="Alertas de tráfico" style={{ margin: "0 14px 12px", display: "flex", flexDirection: "column", gap: 6 }}>
                {datos.alertas.map((a) => (
                  <div
                    key={a.calle}
                    style={{ display: "flex", gap: 10, alignItems: "center", padding: "8px 12px", borderRadius: 12, border: `1px solid ${COLOR_NIVEL[a.nivel]}`, background: "var(--rz-panel-bg)", fontSize: 13 }}
                  >
                    <span aria-hidden="true" style={{ width: 10, height: 10, borderRadius: "50%", background: COLOR_NIVEL[a.nivel], flexShrink: 0 }} />
                    <span style={{ flexGrow: 1 }}>
                      <strong>{a.calle}</strong> · {ETIQUETA_NIVEL[a.nivel]} ({a.motivos.join(" + ")})
                    </span>
                    {a.en_tu_ruta && <strong style={{ color: COLOR_NIVEL[a.nivel], whiteSpace: "nowrap" }}>En tu ruta</strong>}
                  </div>
                ))}
              </section>
            )}

            <div role="region" aria-label="Mapa de tu ruta" style={{ flexShrink: 0, height: 240, position: "relative" }}>
              <MapContainer center={CENTRO_HUANCAYO} zoom={14} style={{ height: "100%", width: "100%" }} zoomControl={false}>
                <TileLayer url={OSM_TILES} attribution="&copy; OpenStreetMap contributors" />
                {datos.alertas.filter((a) => a.en_tu_ruta).map((a) => (
                  <Polyline key={a.calle} positions={a.segmentos} pathOptions={{ color: COLOR_NIVEL[a.nivel], weight: 9, opacity: 0.5 }} />
                ))}
                {ruta.tramos.map((t) => (
                  <Polyline key={`${t.desde}-${t.hasta}`} positions={t.puntos} pathOptions={{ color: COLOR_RUTA, weight: 4, opacity: 0.9 }} />
                ))}
                {paradas.map((p) => {
                  const cancelada = p.pedido_estado === "CANCELADO";
                  const esSiguiente = p.orden === datos.siguiente_orden;
                  const relleno = cancelada ? COLOR_ENTREGA.CANCELADO : (COLOR_ENTREGA[p.estado_entrega] ?? COLOR_RUTA);
                  const marca = cancelada ? "✕" : p.estado_entrega === "ENTREGADO" ? "✓" : p.estado_entrega === "FALLIDO" ? "✗" : "";
                  return (
                    <CircleMarker
                      key={p.pedido_id}
                      center={[Number(p.latitud), Number(p.longitud)]}
                      radius={esSiguiente ? 14 : 10}
                      pathOptions={{ color: esSiguiente ? "#14181a" : "#ffffff", weight: esSiguiente ? 3 : 2, fillColor: relleno, fillOpacity: 1 }}
                    >
                      <Tooltip permanent direction="center">{`${p.orden}${marca}`}</Tooltip>
                      <Popup>
                        <strong>{p.orden}. {p.cliente}</strong>
                        <br />
                        Llegada estimada {hora(p.hora_estimada)}
                      </Popup>
                    </CircleMarker>
                  );
                })}
                <CircleMarker center={[datos.deposito.latitud, datos.deposito.longitud]} radius={8} pathOptions={{ color: "#14181a", fillColor: "#ffffff", fillOpacity: 1, weight: 3 }}>
                  <Tooltip permanent direction="top">Depósito</Tooltip>
                </CircleMarker>
              </MapContainer>
            </div>

            <div style={{ padding: 14, display: "flex", flexDirection: "column", gap: 14 }}>
              {siguiente ? (
                <section aria-label="Siguiente parada" style={estiloTarjeta}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                    <span style={estiloEtiqueta(siguiente.prioridad === "EXPRESS")}>{siguiente.prioridad === "EXPRESS" ? "Express" : `Parada ${siguiente.orden}`}</span>
                    <span style={{ fontFamily: "var(--rz-font-mono)", fontSize: 13, color: "var(--rz-text-muted)" }}>
                      Llegada {hora(siguiente.hora_estimada)}
                      {siguiente.minutos_retraso > 0 && <span style={{ color: "var(--rz-danger)" }}> (+{siguiente.minutos_retraso} min)</span>}
                    </span>
                  </div>
                  <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 20, overflowWrap: "anywhere" }}>{siguiente.cliente}</div>
                  <div style={{ fontSize: 13, color: "var(--rz-text-muted)" }}>
                    Parada {siguiente.orden} de {atendibles.length}
                    {siguiente.peso_kg !== undefined && <> · {Number(siguiente.peso_kg).toFixed(0)} kg</>}
                    {siguiente.descripcion && <> · {siguiente.descripcion}</>}
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                    <button type="button" disabled={registrando} onClick={() => void registrar(siguiente, "ENTREGADO")} style={estiloBotonGrande(true)}>
                      Entregado
                    </button>
                    <button type="button" disabled={registrando} onClick={() => void registrar(siguiente, "FALLIDO")} style={estiloBotonGrande(false)}>
                      No se pudo
                    </button>
                  </div>
                </section>
              ) : (
                <div role="status" style={estiloTarjeta}>
                  <div style={{ fontFamily: "var(--rz-font-display)", fontWeight: 700, fontSize: 18 }}>
                    {ruta.estado === "COMPLETADA" ? "Ruta completada" : "Sin paradas pendientes"}
                  </div>
                  <p style={{ margin: 0, fontSize: 14, color: "var(--rz-text-muted)" }}>
                    {ruta.estado === "COMPLETADA" ? "Atendiste todas tus paradas. ¡Buen trabajo!" : "No te quedan paradas por atender. Vuelve al depósito."}
                  </p>
                </div>
              )}

              {otrasPendientes.length > 0 && (
                <section aria-label="Paradas que faltan">
                  <h2 style={estiloTitulo}>Después ({otrasPendientes.length})</h2>
                  <ol style={estiloLista}>
                    {otrasPendientes.map((p) => (
                      <li key={p.pedido_id} style={estiloFila}>
                        <span style={{ fontFamily: "var(--rz-font-mono)", color: "var(--rz-text-muted)", minWidth: 24 }}>{p.orden}.</span>
                        <span style={{ flexGrow: 1, minWidth: 0, overflowWrap: "anywhere" }}>
                          {p.cliente}
                          {p.prioridad === "EXPRESS" && <strong style={{ color: "var(--rz-danger)" }}> · EXPRESS</strong>}
                        </span>
                        <span style={{ fontFamily: "var(--rz-font-mono)" }}>{hora(p.hora_estimada)}</span>
                      </li>
                    ))}
                  </ol>
                </section>
              )}

              {canceladas.length > 0 && (
                <section aria-label="Pedidos cancelados">
                  <h2 style={estiloTitulo}>Cancelados: no los atiendas</h2>
                  <ul style={estiloLista}>
                    {canceladas.map((p) => (
                      <li key={p.pedido_id} style={{ ...estiloFila, textDecoration: "line-through", color: "var(--rz-text-muted)" }}>
                        {p.orden}. {p.cliente}
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {atendidas.length > 0 && (
                <section aria-label="Paradas atendidas">
                  <h2 style={estiloTitulo}>Atendidas ({atendidas.length})</h2>
                  <ul style={estiloLista}>
                    {atendidas.map((p) => (
                      <li key={p.pedido_id} style={estiloFila}>
                        <span style={{ flexGrow: 1, minWidth: 0, overflowWrap: "anywhere" }}>
                          {p.orden}. {p.cliente}
                        </span>
                        <strong style={{ color: COLOR_ENTREGA[p.estado_entrega] }}>{p.estado_entrega === "ENTREGADO" ? "Entregado" : "Fallido"}</strong>
                      </li>
                    ))}
                  </ul>
                </section>
              )}
            </div>
          </>
        )}
      </main>

      <nav
        aria-label="Acciones"
        style={{ flexShrink: 0, display: "flex", background: "var(--rz-header-bg)", borderTop: "1px solid var(--rz-panel-border)", padding: "6px 4px" }}
      >
        <button type="button" onClick={() => void cargar()} style={estiloTab}>
          Actualizar
        </button>
        <button type="button" onClick={() => void cerrarSesion()} style={estiloTab}>
          Cerrar sesión
        </button>
      </nav>
    </div>
  );
}

function ResumenRuta({ datos }: { datos: MiRuta }) {
  const total = datos.entregadas + datos.pendientes;
  const porcentaje = total === 0 ? 0 : Math.round((100 * datos.entregadas) / total);
  const r = datos.ruta!;
  return (
    <section aria-label="Resumen de tu ruta" style={{ margin: 14, display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap", fontSize: 13 }}>
        <strong>
          {datos.entregadas} de {total} entregas
        </strong>
        <span style={{ color: "var(--rz-text-muted)" }}>
          {hora(r.hora_salida)}–{hora(r.hora_regreso)} · {r.estado === "EN_EJECUCION" ? "En ejecución" : r.estado === "COMPLETADA" ? "Completada" : "Confirmada"}
        </span>
      </div>
      <div role="progressbar" aria-label="Avance de entregas" aria-valuemin={0} aria-valuemax={100} aria-valuenow={porcentaje} style={{ height: 8, borderRadius: 999, background: "var(--rz-track-bg)", overflow: "hidden" }}>
        <div style={{ width: `${porcentaje}%`, height: "100%", background: "var(--rz-accent)" }} />
      </div>
    </section>
  );
}

const estiloTarjeta: React.CSSProperties = {
  borderRadius: 20,
  background: "var(--rz-panel-bg)",
  border: "1px solid var(--rz-panel-border)",
  padding: 18,
  display: "flex",
  flexDirection: "column",
  gap: 12,
};

const estiloEtiqueta = (express: boolean): React.CSSProperties => ({
  fontSize: 11,
  fontWeight: 700,
  textTransform: "uppercase",
  color: express ? "var(--rz-danger)" : "var(--rz-accent)",
  background: express ? "var(--rz-danger-soft-bg)" : "var(--rz-accent-soft-bg)",
  padding: "4px 10px",
  borderRadius: 999,
});

const estiloBotonGrande = (principal: boolean): React.CSSProperties => ({
  minHeight: 52,
  borderRadius: 14,
  border: principal ? "none" : "1px solid var(--rz-panel-border)",
  background: principal ? "var(--rz-accent)" : "transparent",
  color: principal ? "var(--rz-bg)" : "var(--rz-text)",
  fontWeight: 700,
  fontSize: 15,
  cursor: "pointer",
});

const estiloTitulo: React.CSSProperties = { margin: "0 0 8px", fontSize: 13, color: "var(--rz-text-muted)", fontWeight: 600 };
const estiloLista: React.CSSProperties = { margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 8 };
const estiloFila: React.CSSProperties = { display: "flex", gap: 10, alignItems: "baseline", fontSize: 14 };

const estiloTab: React.CSSProperties = {
  flexGrow: 1,
  background: "none",
  border: "none",
  color: "var(--rz-text-muted)",
  fontSize: 13,
  padding: "12px 0",
  cursor: "pointer",
};
