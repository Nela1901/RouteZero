import { useEffect, useState } from "react";
import { api, mensajeDeError } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import { useConfirm } from "../../context/ConfirmContext";
import { useToast } from "../../context/ToastContext";
import { Ayuda, estiloAviso, estiloBotonPrimario, estiloInput } from "../../components/ui";

interface Parada {
  orden: number;
  pedido_id: string;
  cliente: string;
  descripcion: string | null;
  peso_kg: string;
  prioridad: string;
  hora_estimada: string | null;
  minutos_retraso: number;
}

interface Metricas {
  emision_co2_kg: string;
  combustible_l: string;
  combustible_ahorrado_l: string;
  distancia_km: string;
  cumplimiento_ventanas_pct: string;
}

export interface Ruta {
  ruta_id: string;
  lote_id: string;
  fecha_jornada: string;
  estado: string;
  vehiculo: { vehiculo_id: string; placa: string; tipo: string };
  conductor: { conductor_id: string; nombre: string };
  hora_salida: string | null;
  hora_regreso: string | null;
  distancia_km: string | null;
  tiempo_min: number | null;
  cantidad_paradas: number;
  metricas: Metricas | null;
  paradas: Parada[];
}

interface SinCobertura {
  pedido_id: string;
  motivo: string;
  sugerencia: string;
}

interface ResultadoGeneracion {
  lote_id: string | null;
  imposible: boolean;
  mensaje: string;
  rutas: Ruta[];
  sin_cobertura: SinCobertura[];
  fuente_distancias: "calles" | "mixta" | "aproximada";
  puntos_aproximados: number;
  comparativa_base: { mejora_distancia_pct: number; mejora_co2_pct: number } | null;
  tiempo_ejecucion_s: number;
}

const MOTIVOS: Record<string, string> = {
  PESO_EXCEDE_CAPACIDAD: "Pesa más que cualquier vehículo",
  SIN_RECURSOS: "No hay vehículos o conductores elegibles",
  FUERA_DE_JORNADA: "No cabe en ninguna jornada",
  FLOTA_INSUFICIENTE: "La flota no alcanza",
};

const hora = (valor: string | null) => (valor ? valor.slice(0, 5) : "—");
const numero = (valor: string | number | null | undefined, decimales = 1) =>
  valor === null || valor === undefined ? "—" : Number(valor).toFixed(decimales);

function hoyLocal(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function RutasPage() {
  const { usuario } = useAuth();
  const esAdministrador = usuario?.rolNombre === "ADMINISTRADOR";
  const { notificar } = useToast();
  const { confirmar } = useConfirm();
  const [fecha, setFecha] = useState(hoyLocal());
  const [rutas, setRutas] = useState<Ruta[]>([]);
  const [resultado, setResultado] = useState<ResultadoGeneracion | null>(null);
  const [generando, setGenerando] = useState(false);
  const [segundos, setSegundos] = useState(0);
  const [error, setError] = useState<string | null>(null);

  async function cargar(dia = fecha) {
    try {
      setRutas(await api.get<Ruta[]>(`/api/rutas?fecha=${dia}`));
    } catch (err) {
      setError(mensajeDeError(err, "No se pudieron cargar las rutas"));
    }
  }

  useEffect(() => {
    setResultado(null);
    setError(null);
    void cargar(fecha);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fecha]);

  // Contador visible mientras se calcula: la generación puede tardar hasta 40 s
  useEffect(() => {
    if (!generando) return;
    setSegundos(0);
    const reloj = window.setInterval(() => setSegundos((s) => s + 1), 1000);
    return () => window.clearInterval(reloj);
  }, [generando]);

  const borradores = rutas.filter((r) => r.estado === "PLANIFICADA");
  const lote = borradores[0]?.lote_id ?? null;

  async function generar() {
    setError(null);
    setGenerando(true);
    try {
      const respuesta = await api.post<ResultadoGeneracion>("/api/rutas/generar", { fecha_jornada: fecha });
      setResultado(respuesta);
      await cargar();
      if (respuesta.imposible) notificar("No fue posible generar rutas", "error");
      else notificar("Rutas generadas como borrador: revíselas y confírmelas", "exito");
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudieron generar las rutas");
      setError(mensaje);
      notificar(mensaje, "error");
    } finally {
      setGenerando(false);
    }
  }

  async function confirmarLote() {
    if (!lote) return;
    const acepto = await confirmar({
      titulo: "Confirmar rutas",
      mensaje: "Los pedidos de estas rutas pasarán a ASIGNADO y los conductores podrán verlas. ¿Confirmar?",
      textoAceptar: "Confirmar rutas",
    });
    if (!acepto) return;
    setError(null);
    try {
      await api.post(`/api/rutas/lotes/${lote}/confirmar`);
      notificar("Rutas confirmadas", "exito");
      setResultado(null);
      await cargar();
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudieron confirmar las rutas");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  async function descartarLote() {
    if (!lote) return;
    const acepto = await confirmar({
      titulo: "Descartar borrador",
      mensaje: "Se eliminarán las rutas del borrador. Los pedidos seguirán pendientes. ¿Descartar?",
      textoAceptar: "Descartar",
      peligroso: true,
    });
    if (!acepto) return;
    setError(null);
    try {
      await api.delete(`/api/rutas/lotes/${lote}`);
      notificar("Borrador descartado", "exito");
      setResultado(null);
      await cargar();
    } catch (err) {
      const mensaje = mensajeDeError(err, "No se pudo descartar el borrador");
      setError(mensaje);
      notificar(mensaje, "error");
    }
  }

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1440 }}>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Rutas</h1>
          <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
            Rutas optimizadas por calles reales de Huancayo: se generan como borrador y se confirman al revisarlas.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 10, flexWrap: "wrap" }}>
          <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
            <span>
              Fecha de la jornada
              <Ayuda texto="Día para el que se planifican las rutas. Se consideran todos los pedidos pendientes; la fecha sirve para comprobar que las licencias de los conductores estén vigentes ese día." />
            </span>
            <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} style={estiloInput} />
          </label>
          {esAdministrador && (
            <button type="button" onClick={() => void generar()} disabled={generando} style={estiloBotonPrimario}>
              {generando ? `Calculando… ${segundos} s` : "Generar rutas"}
            </button>
          )}
        </div>
      </div>

      {generando && (
        <div role="status" style={{ ...estiloAviso, background: "var(--rz-accent-soft-bg)", color: "var(--rz-accent)" }}>
          Calculando las rutas óptimas por calles reales. Puede tardar hasta 40 segundos; no cierre esta página.
        </div>
      )}
      {error && <div style={estiloAviso}>{error}</div>}

      {borradores.length > 0 && (
        <div
          role="status"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
            padding: "14px 18px",
            borderRadius: 14,
            border: "1px solid var(--rz-warning, #b7791f)",
            background: "var(--rz-panel-bg)",
          }}
        >
          <div style={{ fontSize: 13.5 }}>
            <strong>Borrador sin confirmar.</strong> Estas rutas todavía no se han enviado a los conductores y los pedidos siguen
            pendientes.
          </div>
          {esAdministrador && (
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" onClick={() => void confirmarLote()} style={estiloBotonPrimario}>
                Confirmar rutas
              </button>
              <button type="button" onClick={() => void descartarLote()} style={estiloBotonSecundario}>
                Descartar
              </button>
            </div>
          )}
        </div>
      )}

      {resultado && <ResumenGeneracion resultado={resultado} />}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 360px), 1fr))", gap: 14, alignItems: "start" }}>
        {rutas.map((r) => (
          <TarjetaRuta key={r.ruta_id} ruta={r} />
        ))}
      </div>
      {rutas.length === 0 && !generando && (
        <div style={{ padding: 24, textAlign: "center", color: "var(--rz-text-muted)", fontSize: 13.5 }}>
          No hay rutas para esta fecha{esAdministrador ? ": genere rutas para planificar la jornada." : "."}
        </div>
      )}
    </div>
  );
}

function ResumenGeneracion({ resultado }: { resultado: ResultadoGeneracion }) {
  const fuente =
    resultado.fuente_distancias === "calles"
      ? "calles reales"
      : resultado.fuente_distancias === "mixta"
        ? `calles reales y ${resultado.puntos_aproximados} punto(s) aproximado(s)`
        : "distancia aproximada (en línea recta)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {resultado.imposible && <div style={estiloAviso}>{resultado.mensaje}</div>}
      {!resultado.imposible && (
        <div style={{ fontSize: 13, color: "var(--rz-text-muted)", lineHeight: 1.6 }}>
          Calculado en {numero(resultado.tiempo_ejecucion_s)} s con {fuente}.
          {resultado.comparativa_base && (
            <>
              {" "}
              Frente a la solución inicial: <strong>{numero(resultado.comparativa_base.mejora_distancia_pct, 0)} %</strong> menos
              distancia y <strong>{numero(resultado.comparativa_base.mejora_co2_pct, 0)} %</strong> menos CO₂.
            </>
          )}
        </div>
      )}
      {resultado.sin_cobertura.length > 0 && (
        <div style={{ ...estiloAviso, display: "flex", flexDirection: "column", gap: 6 }}>
          <strong>{resultado.sin_cobertura.length} pedido(s) sin cobertura</strong>
          {resultado.sin_cobertura.map((s) => (
            <div key={s.pedido_id} style={{ fontSize: 12.5 }}>
              <span style={{ fontFamily: "var(--rz-font-mono)" }}>{s.pedido_id.slice(0, 8)}</span> —{" "}
              {MOTIVOS[s.motivo] ?? s.motivo}. {s.sugerencia}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TarjetaRuta({ ruta }: { ruta: Ruta }) {
  const [abierta, setAbierta] = useState(false);
  const [paradas, setParadas] = useState<Parada[]>(ruta.paradas);
  const [cargando, setCargando] = useState(false);
  const m = ruta.metricas;
  const borrador = ruta.estado === "PLANIFICADA";

  async function alternar() {
    const abrir = !abierta;
    setAbierta(abrir);
    if (abrir && paradas.length === 0 && ruta.cantidad_paradas > 0) {
      setCargando(true);
      try {
        const detalle = await api.get<Ruta>(`/api/rutas/${ruta.ruta_id}`);
        setParadas(detalle.paradas);
      } finally {
        setCargando(false);
      }
    }
  }

  return (
    <div
      style={{
        borderRadius: 16,
        border: "1px solid var(--rz-panel-border)",
        background: "var(--rz-panel-bg)",
        padding: 16,
        display: "flex",
        flexDirection: "column",
        gap: 12,
        minWidth: 0,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8, flexWrap: "wrap" }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontFamily: "var(--rz-font-mono)", fontWeight: 700, fontSize: 15 }}>{ruta.vehiculo.placa}</div>
          <div style={{ fontSize: 12.5, color: "var(--rz-text-muted)" }}>
            {ruta.vehiculo.tipo} · {ruta.conductor.nombre}
          </div>
        </div>
        <span
          style={{
            fontSize: 11.5,
            fontWeight: 600,
            padding: "3px 10px",
            borderRadius: 999,
            border: "1px solid var(--rz-panel-border)",
            color: borrador ? "var(--rz-warning, #b7791f)" : "var(--rz-accent)",
            whiteSpace: "nowrap",
          }}
        >
          {borrador ? "Borrador" : ruta.estado === "CONFIRMADA" ? "Confirmada" : ruta.estado}
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(110px, 1fr))", gap: 8, fontSize: 12.5 }}>
        <Dato etiqueta="Horario" valor={`${hora(ruta.hora_salida)}–${hora(ruta.hora_regreso)}`} />
        <Dato etiqueta="Paradas" valor={String(ruta.cantidad_paradas)} />
        <Dato etiqueta="Distancia" valor={`${numero(ruta.distancia_km)} km`} />
        <Dato etiqueta="CO₂" valor={m ? `${numero(m.emision_co2_kg)} kg` : "—"} />
        <Dato etiqueta="Combustible" valor={m ? `${numero(m.combustible_l)} L` : "—"} />
        <Dato etiqueta="En ventana" valor={m ? `${numero(m.cumplimiento_ventanas_pct, 0)} %` : "—"} />
      </div>

      <button type="button" onClick={() => void alternar()} aria-expanded={abierta} style={estiloBotonSecundario}>
        {abierta ? "Ocultar paradas" : "Ver paradas"}
      </button>

      {abierta && (
        <ol style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 6 }}>
          {cargando && <li style={{ fontSize: 12.5, color: "var(--rz-text-muted)" }}>Cargando…</li>}
          {paradas.map((p) => (
            <li key={p.pedido_id} style={{ display: "flex", gap: 10, fontSize: 12.5, alignItems: "baseline" }}>
              <span style={{ fontFamily: "var(--rz-font-mono)", color: "var(--rz-text-muted)", minWidth: 22 }}>{p.orden}.</span>
              <span style={{ flexGrow: 1, minWidth: 0 }}>
                {p.cliente}
                {p.prioridad === "EXPRESS" && <strong style={{ color: "var(--rz-danger)" }}> · EXPRESS</strong>}
                <span style={{ color: "var(--rz-text-muted)" }}> · {numero(p.peso_kg, 0)} kg</span>
              </span>
              <span style={{ fontFamily: "var(--rz-font-mono)", whiteSpace: "nowrap" }}>
                {hora(p.hora_estimada)}
                {p.minutos_retraso > 0 && <span style={{ color: "var(--rz-danger)" }}> +{p.minutos_retraso} min</span>}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function Dato({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <div>
      <div style={{ color: "var(--rz-text-muted)", fontSize: 11.5 }}>{etiqueta}</div>
      <div style={{ fontFamily: "var(--rz-font-mono)", fontWeight: 600 }}>{valor}</div>
    </div>
  );
}

const estiloBotonSecundario: React.CSSProperties = {
  height: 36,
  padding: "0 14px",
  borderRadius: 10,
  border: "1px solid var(--rz-panel-border)",
  background: "transparent",
  color: "var(--rz-text)",
  fontSize: 12.5,
  cursor: "pointer",
};
