import { MapContainer, TileLayer, CircleMarker, Polyline, Popup, Tooltip } from "react-leaflet";
import { marcaDeEntrega, textoDeEntrega } from "../../components/utilesEntrega";
import "leaflet/dist/leaflet.css";
import { useCallback, useEffect, useState } from "react";
import { api, mensajeDeError } from "../../api/client";
import { Ayuda, estiloAviso, estiloInput } from "../../components/ui";

const CENTRO_HUANCAYO: [number, number] = [-12.0653, -75.2049];
const OSM_TILES = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const REFRESCO_MS = 30_000;

const COLOR_PRIORIDAD: Record<string, string> = {
  EXPRESS: "var(--rz-accent)",
  ESTANDAR: "var(--rz-accent-2)",
  ECONOMICO: "var(--rz-accent-3)",
};

// Colores de las rutas (paleta apta para daltonismo); se reparten por orden
const COLORES_RUTA = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#7a5195", "#8c564b"];
const COLOR_NIVEL: Record<string, string> = { VERDE: "#2e9e57", AMARILLO: "#e0a800", ROJO: "#d63031" };
const ETIQUETA_NIVEL: Record<string, string> = { VERDE: "Fluido", AMARILLO: "Congestión moderada", ROJO: "Congestión alta" };
const COLOR_ENTREGA: Record<string, string> = { ENTREGADO: "#2e9e57", FALLIDO: "#d63031", CANCELADO: "#8a8a8a" };
const ETIQUETA_ESTADO: Record<string, string> = {
  PLANIFICADA: "Borrador",
  CONFIRMADA: "Confirmada",
  EN_EJECUCION: "En ejecución",
  COMPLETADA: "Completada",
};

interface Pedido {
  pedido_id: string;
  prioridad: string;
  estado: string;
  latitud: number;
  longitud: number;
  descripcion: string | null;
}

interface ParadaMapa {
  orden: number;
  pedido_id: string;
  cliente: string;
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
  distancia_km: number;
  duracion_min: number;
  en_punta: boolean;
  puntos: [number, number][];
}

export interface RutaMapa {
  ruta_id: string;
  estado: string;
  reemplaza_ruta_id: string | null;
  vehiculo: { vehiculo_id: string; placa: string; tipo: string };
  conductor: { conductor_id: string; nombre: string };
  hora_salida: string | null;
  hora_regreso: string | null;
  paradas: ParadaMapa[];
  tramos: Tramo[];
}

interface MapaDatos {
  fecha_jornada: string;
  deposito: { latitud: number; longitud: number };
  rutas: RutaMapa[];
}

interface Via {
  calle: string;
  nivel: "VERDE" | "AMARILLO" | "ROJO";
  factor: number;
  motivos: string[];
  segmentos: [number, number][][];
}

interface Congestion {
  hora: string;
  en_punta: boolean;
  vias: Via[];
}

const hora = (valor: string | null) => (valor ? valor.slice(0, 5) : "—");
const numero = (valor: number, decimales = 1) => Number(valor).toFixed(decimales);

function hoyLocal(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function ahoraLocal(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function etiquetaTramo(t: Tramo): string {
  const desde = t.desde === 0 ? "Depósito" : `Parada ${t.desde}`;
  const hasta = t.hasta === 0 ? "Depósito" : `Parada ${t.hasta}`;
  return `${desde} → ${hasta}`;
}

export function MapaPage() {
  const [fecha, setFecha] = useState(hoyLocal());
  const [horaVista, setHoraVista] = useState(ahoraLocal());
  const [mapa, setMapa] = useState<MapaDatos | null>(null);
  const [congestion, setCongestion] = useState<Congestion | null>(null);
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [ocultas, setOcultas] = useState<Set<string>>(new Set());
  const [verPedidos, setVerPedidos] = useState(true);
  const [automatico, setAutomatico] = useState(true);
  const [actualizado, setActualizado] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  // En pantallas angostas el panel tapa buena parte del mapa: empieza cerrado y se abre con el botón
  const [panelAbierto, setPanelAbierto] = useState(() => typeof window.matchMedia !== "function" || window.matchMedia("(min-width: 900px)").matches);
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      const [m, c, p] = await Promise.all([
        api.get<MapaDatos>(`/api/rutas/mapa?fecha=${fecha}`),
        api.get<Congestion>(`/api/rutas/congestion?hora=${horaVista}`),
        // El listado viene paginado ({ items, total, ... }); el mapa pide la página más grande permitida (200).
        api.get<{ items: Pedido[] }>("/api/pedidos?limite=200").catch(() => ({ items: [] as Pedido[] })),
      ]);
      setMapa(m);
      setCongestion(c);
      setPedidos(p.items);
      setError(null);
      setActualizado(ahoraLocal());
    } catch (err) {
      setError(mensajeDeError(err, "No se pudo cargar el mapa"));
    } finally {
      setCargando(false);
    }
  }, [fecha, horaVista]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  // Monitoreo: se vuelve a pedir todo cada 30 s mientras el refresco automático esté activo
  useEffect(() => {
    if (!automatico) return;
    const reloj = window.setInterval(() => void cargar(), REFRESCO_MS);
    return () => window.clearInterval(reloj);
  }, [automatico, cargar]);

  const rutas = mapa?.rutas ?? [];
  const pendientes = pedidos.filter((p) => p.estado === "PENDIENTE");

  function alternar(id: string) {
    setOcultas((previas) => {
      const nuevas = new Set(previas);
      if (nuevas.has(id)) nuevas.delete(id);
      else nuevas.add(id);
      return nuevas;
    });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 12, flexWrap: "wrap", padding: "12px 16px", borderBottom: "1px solid var(--rz-panel-border)" }}>
        <Campo id="mapa-fecha" etiqueta="Fecha de la jornada">
          <input id="mapa-fecha" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} style={estiloInput} />
        </Campo>
        <Campo
          id="mapa-hora"
          etiqueta="Hora de la congestión"
          ayuda="Hora a la que se muestra el estado de Av. Ferrocarril, Av. Giráldez y Calle Real. Cambiarla permite ver, por ejemplo, cómo está la vía en hora punta (7:30–9:30, 12:00–14:30 y 17:00–21:00)."
        >
          <input id="mapa-hora" type="time" value={horaVista} onChange={(e) => e.target.value && setHoraVista(e.target.value)} style={estiloInput} />
        </Campo>
        <button type="button" onClick={() => void cargar()} style={estiloBotonBarra}>
          Actualizar
        </button>
        <label style={estiloCheck}>
          <input type="checkbox" checked={automatico} onChange={(e) => setAutomatico(e.target.checked)} />{" "}
          Actualizar cada 30 s
        </label>
        <label style={estiloCheck}>
          <input type="checkbox" checked={verPedidos} onChange={(e) => setVerPedidos(e.target.checked)} />{" "}
          Pedidos pendientes
        </label>
        <output style={{ fontSize: 12, color: "var(--rz-text-muted)", marginLeft: "auto" }}>
          {textoDeCarga(cargando, mapa === null, actualizado)}
        </output>
      </div>
      {error && <div style={{ ...estiloAviso, margin: "8px 16px 0" }}>{error}</div>}

      <section aria-label="Mapa de rutas de Huancayo" style={{ position: "relative", flex: 1, minHeight: 320 }}>
        <MapContainer center={CENTRO_HUANCAYO} zoom={14} style={{ height: "100%", width: "100%" }}>
          <TileLayer url={OSM_TILES} attribution="&copy; OpenStreetMap contributors" />

          {congestion?.vias.map((via) => (
            <Polyline
              key={via.calle}
              positions={via.segmentos}
              pathOptions={{ color: COLOR_NIVEL[via.nivel], weight: 9, opacity: 0.55 }}
            >
              <Popup>
                <strong>{via.calle}</strong>
                <br />
                {ETIQUETA_NIVEL[via.nivel]} · {numero(via.factor, 2)} veces más lento
                {via.motivos.length > 0 && <> ({via.motivos.join(" + ")})</>}
              </Popup>
            </Polyline>
          ))}

          {verPedidos &&
            pendientes.map((pedido) => (
              <CircleMarker
                key={pedido.pedido_id}
                center={[Number(pedido.latitud), Number(pedido.longitud)]}
                radius={7}
                pathOptions={{
                  color: COLOR_PRIORIDAD[pedido.prioridad] ?? "var(--rz-accent-2)",
                  fillColor: COLOR_PRIORIDAD[pedido.prioridad] ?? "var(--rz-accent-2)",
                  fillOpacity: 0.85,
                }}
              >
                <Popup>
                  <strong>{pedido.descripcion ?? "Pedido"}</strong>
                  <br />
                  Prioridad: {pedido.prioridad} · Estado: {pedido.estado}
                </Popup>
              </CircleMarker>
            ))}

          {rutas.map((ruta, i) => {
            if (ocultas.has(ruta.ruta_id)) return null;
            const color = COLORES_RUTA[i % COLORES_RUTA.length];
            const borrador = ruta.estado === "PLANIFICADA";
            return (
              <RutaEnMapa key={ruta.ruta_id} ruta={ruta} color={color} borrador={borrador} />
            );
          })}

          {mapa && (
            <CircleMarker
              center={[mapa.deposito.latitud, mapa.deposito.longitud]}
              radius={9}
              pathOptions={{ color: "#14181a", fillColor: "#ffffff", fillOpacity: 1, weight: 3 }}
            >
              <Tooltip permanent direction="top">
                Depósito
              </Tooltip>
            </CircleMarker>
          )}
        </MapContainer>

        <button
          type="button"
          onClick={() => setPanelAbierto((abierto) => !abierto)}
          aria-expanded={panelAbierto}
          style={{ ...estiloBotonBarra, position: "absolute", right: 12, top: 12, zIndex: 1001, height: 36, background: "var(--rz-panel-solid-bg)" }}
        >
          {panelAbierto ? "Ocultar panel" : "Mostrar panel"}
        </button>

        {panelAbierto && (
        <PanelRutas
          rutas={rutas}
          congestion={congestion}
          ocultas={ocultas}
          onAlternar={alternar}
          sinRutas={mapa !== null && rutas.length === 0}
          hayPedidos={verPedidos && pendientes.length > 0}
        />
        )}
      </section>
    </div>
  );
}

function RutaEnMapa({ ruta, color, borrador }: Readonly<{ ruta: RutaMapa; color: string; borrador: boolean }>) {
  return (
    <>
      {ruta.tramos.map((t) => (
        <Polyline
          key={`${t.desde}-${t.hasta}`}
          positions={t.puntos}
          pathOptions={{ color, weight: 4, opacity: 0.9, dashArray: borrador ? "8 8" : undefined }}
        >
          <Popup>
            <strong>
              {ruta.vehiculo.placa} · {etiquetaTramo(t)}
            </strong>
            <br />
            {numero(t.duracion_min)} min · {numero(t.distancia_km, 2)} km
            {t.en_punta && <> · sale en hora punta</>}
          </Popup>
        </Polyline>
      ))}
      {ruta.paradas.map((p) => {
        const cancelada = p.pedido_estado === "CANCELADO";
        const relleno = cancelada ? COLOR_ENTREGA.CANCELADO : (COLOR_ENTREGA[p.estado_entrega] ?? color);
        const marca = marcaDeEntrega(cancelada, p.estado_entrega);
        return (
          <CircleMarker
            key={p.pedido_id}
            center={[Number(p.latitud), Number(p.longitud)]}
            radius={10}
            pathOptions={{ color: "#ffffff", weight: 2, fillColor: relleno, fillOpacity: 1 }}
          >
            <Tooltip permanent direction="center">
              {`${p.orden}${marca}`}
            </Tooltip>
            <Popup>
              <strong>
                {p.orden}. {p.cliente}
              </strong>
              <br />
              {ruta.vehiculo.placa} · {ruta.conductor.nombre}
              <br />
              Llegada estimada {hora(p.hora_estimada)}
              {p.minutos_retraso > 0 && <> (+{p.minutos_retraso} min de retraso)</>}
              <br />
              {textoDeEntrega(cancelada, p.estado_entrega)}
              {p.prioridad === "EXPRESS" && " · EXPRESS"}
            </Popup>
          </CircleMarker>
        );
      })}
    </>
  );
}

function PanelRutas(props: Readonly<{
  rutas: RutaMapa[];
  congestion: Congestion | null;
  ocultas: Set<string>;
  onAlternar: (id: string) => void;
  sinRutas: boolean;
  hayPedidos: boolean;
}>) {
  const { rutas, congestion, ocultas, onAlternar, sinRutas, hayPedidos } = props;
  return (
    <aside
      aria-label="Rutas y congestión"
      style={{
        position: "absolute",
        right: 12,
        top: 56,
        width: "min(340px, calc(100% - 24px))",
        maxHeight: "calc(100% - 68px)",
        overflowY: "auto",
        padding: 12,
        borderRadius: 14,
        background: "var(--rz-panel-solid-bg)",
        backdropFilter: "blur(10px)",
        border: "1px solid var(--rz-panel-border)",
        zIndex: 1000,
        display: "flex",
        flexDirection: "column",
        gap: 10,
        fontSize: 12.5,
      }}
    >
      {sinRutas && (
        <output style={{ display: "block", color: "var(--rz-text-muted)", fontSize: 13 }}>
          No hay rutas para esta fecha. El mapa muestra las vías y los pedidos pendientes.
        </output>
      )}

      {rutas.length > 0 && (
        <section aria-label="Rutas de la jornada" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <strong style={{ fontSize: 13 }}>Rutas ({rutas.length})</strong>
          {rutas.map((r, i) => {
            const km = r.tramos.reduce((s, t) => s + t.distancia_km, 0);
            const min = r.tramos.reduce((s, t) => s + t.duracion_min, 0);
            const id = `mapa-ruta-${r.ruta_id}`;
            return (
              <details key={r.ruta_id} style={{ borderTop: "1px solid var(--rz-panel-border)", paddingTop: 6 }}>
                <summary style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8, listStyle: "revert" }}>
                  <span aria-hidden="true" style={{ width: 12, height: 12, borderRadius: 3, background: COLORES_RUTA[i % COLORES_RUTA.length], flexShrink: 0 }} />
                  <span style={{ flexGrow: 1, minWidth: 0 }}>
                    <span style={{ fontFamily: "var(--rz-font-mono)", fontWeight: 700 }}>{r.vehiculo.placa}</span>
                    <span style={{ color: "var(--rz-text-muted)" }}>
                      {" "}
                      · {r.conductor.nombre} · {ETIQUETA_ESTADO[r.estado] ?? r.estado}
                    </span>
                  </span>
                </summary>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, padding: "8px 0 4px 20px" }}>
                  <label htmlFor={id} style={estiloCheck}>
                    <input id={id} type="checkbox" checked={!ocultas.has(r.ruta_id)} onChange={() => onAlternar(r.ruta_id)} />{" "}
                    Mostrar en el mapa
                  </label>
                  <div style={{ color: "var(--rz-text-muted)" }}>
                    {r.paradas.length} parada(s) · {numero(km)} km · {numero(min, 0)} min · {hora(r.hora_salida)}–{hora(r.hora_regreso)}
                  </div>
                  <ol style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 3 }}>
                    {r.tramos.map((t) => (
                      <li key={`${t.desde}-${t.hasta}`} style={{ display: "flex", justifyContent: "space-between", gap: "2px 8px", flexWrap: "wrap" }}>
                        <span>{etiquetaTramo(t)}</span>
                        <span style={{ fontFamily: "var(--rz-font-mono)", whiteSpace: "nowrap" }}>
                          {numero(t.duracion_min)} min · {numero(t.distancia_km, 2)} km{t.en_punta ? " · punta" : ""}
                        </span>
                      </li>
                    ))}
                  </ol>
                </div>
              </details>
            );
          })}
        </section>
      )}

      {congestion && (
        <section aria-label="Congestión de las vías" style={{ display: "flex", flexDirection: "column", gap: 4, borderTop: rutas.length > 0 ? "1px solid var(--rz-panel-border)" : "none", paddingTop: rutas.length > 0 ? 8 : 0 }}>
          <strong style={{ fontSize: 13 }}>
            Congestión a las {hora(congestion.hora)}
            {congestion.en_punta && <span style={{ color: "var(--rz-text-muted)", fontWeight: 400 }}> · hora punta</span>}
          </strong>
          {congestion.vias.map((v) => (
            <div key={v.calle} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span aria-hidden="true" style={{ width: 22, height: 6, borderRadius: 3, background: COLOR_NIVEL[v.nivel], flexShrink: 0 }} />
              <span style={{ flexGrow: 1 }}>{v.calle}</span>
              <span style={{ color: "var(--rz-text-muted)" }}>
                {ETIQUETA_NIVEL[v.nivel]}
                {v.motivos.length > 0 && ` · ${v.motivos.join(" + ")}`}
              </span>
            </div>
          ))}
        </section>
      )}

      <section aria-label="Leyenda" style={{ display: "flex", flexWrap: "wrap", gap: "4px 14px", borderTop: "1px solid var(--rz-panel-border)", paddingTop: 8, color: "var(--rz-text-muted)" }}>
        <Leyenda color={COLOR_ENTREGA.ENTREGADO} etiqueta="Entregado ✓" />
        <Leyenda color={COLOR_ENTREGA.FALLIDO} etiqueta="Fallido ✗" />
        <Leyenda color={COLOR_ENTREGA.CANCELADO} etiqueta="Cancelado ✕" />
        <Leyenda color="#0072B2" etiqueta="Pendiente (color de la ruta)" />
        {hayPedidos && (
          <>
            <Leyenda color="var(--rz-accent)" etiqueta="Pedido express" />
            <Leyenda color="var(--rz-accent-2)" etiqueta="Pedido estándar" />
            <Leyenda color="var(--rz-accent-3)" etiqueta="Pedido económico" />
          </>
        )}
        <span>Línea discontinua: borrador sin confirmar</span>
      </section>
    </aside>
  );
}

function Campo({ id, etiqueta, ayuda, children }: Readonly<{ id: string; etiqueta: string; ayuda?: string; children: React.ReactNode }>) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
      <span>
        <label htmlFor={id}>{etiqueta}</label>
        {ayuda && <Ayuda texto={ayuda} />}
      </span>
      {children}
    </div>
  );
}

function Leyenda({ color, etiqueta }: Readonly<{ color: string; etiqueta: string }>) {
  return (
    <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}>
      <span aria-hidden="true" style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
      {etiqueta}
    </span>
  );
}

const estiloCheck: React.CSSProperties = { display: "flex", alignItems: "center", gap: 6, fontSize: 12.5, color: "var(--rz-text)" };

const estiloBotonBarra: React.CSSProperties = {
  height: 38,
  padding: "0 16px",
  borderRadius: 10,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text)",
  fontSize: 13,
  cursor: "pointer",
};

function textoDeCarga(cargando: boolean, sinMapa: boolean, actualizado: string | null): string {
  if (cargando) return sinMapa ? "Calculando los recorridos por calles… la primera carga puede tardar unos segundos." : "Actualizando…";
  return actualizado ? `Actualizado a las ${actualizado}` : "";
}
