import { useCallback, useEffect, useState } from "react";
import { api, mensajeDeError } from "../../api/client";
import { Ayuda, estiloAviso, estiloBotonPrimario, estiloInput, FiltroChip } from "../../components/ui";

interface Totales {
  rutas: number;
  distancia_km: number;
  emision_co2_kg: number;
  combustible_l: number;
  combustible_ahorrado_l: number;
  ahorro_soles: number;
  cumplimiento_ventanas_pct: number;
}

interface DiaSostenibilidad {
  fecha: string;
  emision_co2_kg: number;
  distancia_km: number;
  combustible_ahorrado_l: number;
}

export interface Dashboard {
  desde: string;
  hasta: string;
  hay_datos: boolean;
  mensaje: string | null;
  totales: Totales;
  entregas: { entregadas: number; pendientes: number; fallidas: number };
  por_dia: DiaSostenibilidad[];
  precio_combustible_soles_l: number;
}

export interface Compensacion {
  hay_datos: boolean;
  mensaje: string | null;
  emision_co2_kg: number;
  toneladas_co2: number;
  kg_co2_por_arbol_anio: number;
  arboles_necesarios: number;
  mes_evaluado: { desde: string; hasta: string; emision_co2_kg: number; meta_kg: number; porcentaje_meta: number; excede_meta: boolean };
  acciones: string[];
  alianzas: { nombre: string; descripcion: string }[];
}

const numero = (valor: number, decimales = 1) =>
  valor.toLocaleString("es-PE", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });

function aTexto(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function fechaLegible(texto: string): string {
  return new Date(`${texto}T00:00:00`).toLocaleDateString("es-PE", { day: "2-digit", month: "short" });
}

const hoy = () => aTexto(new Date());
const inicioDeMes = () => aTexto(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
const haceDias = (n: number) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return aTexto(d);
};

const ATAJOS = [
  { id: "hoy", etiqueta: "Hoy", rango: () => [hoy(), hoy()] },
  { id: "semana", etiqueta: "Últimos 7 días", rango: () => [haceDias(6), hoy()] },
  { id: "mes", etiqueta: "Este mes", rango: () => [inicioDeMes(), hoy()] },
] as const;

function Indicador({ etiqueta, valor, unidad, ayuda }: { etiqueta: string; valor: string; unidad: string; ayuda: string }) {
  return (
    <div
      style={{
        background: "var(--rz-panel-bg)",
        border: "1px solid var(--rz-panel-border)",
        borderRadius: 14,
        padding: "16px 18px",
        display: "flex",
        flexDirection: "column",
        gap: 6,
        minWidth: 0,
      }}
    >
      <span style={{ fontSize: 12.5, color: "var(--rz-text-muted)" }}>
        {etiqueta}
        <Ayuda texto={ayuda} />
      </span>
      <span style={{ fontFamily: "var(--rz-font-display)", fontSize: 26, fontWeight: 700, lineHeight: 1.1 }}>
        {valor}
        <span style={{ fontSize: 13, fontWeight: 500, color: "var(--rz-text-muted)", marginLeft: 6 }}>{unidad}</span>
      </span>
    </div>
  );
}

function GraficoPorDia({ dias }: { dias: DiaSostenibilidad[] }) {
  const maximo = Math.max(...dias.map((d) => d.emision_co2_kg), 0.001);
  return (
    <section
      aria-labelledby="sost-por-dia"
      style={{ background: "var(--rz-panel-bg)", border: "1px solid var(--rz-panel-border)", borderRadius: 14, padding: "16px 18px" }}
    >
      <h2 id="sost-por-dia" style={{ fontFamily: "var(--rz-font-display)", fontSize: 15, margin: "0 0 12px" }}>
        Emisiones de CO₂ por día
      </h2>
      <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 8 }}>
        {dias.map((d) => (
          <li key={d.fecha} style={{ display: "grid", gridTemplateColumns: "56px 1fr 72px", alignItems: "center", gap: 10, fontSize: 12.5 }}>
            <span style={{ color: "var(--rz-text-muted)" }}>{fechaLegible(d.fecha)}</span>
            <span aria-hidden="true" style={{ background: "var(--rz-bg)", borderRadius: 6, height: 12, overflow: "hidden" }}>
              <span
                style={{ display: "block", height: "100%", width: `${(d.emision_co2_kg / maximo) * 100}%`, background: "var(--rz-accent)", borderRadius: 6 }}
              />
            </span>
            <span style={{ textAlign: "right", fontFamily: "var(--rz-font-mono)" }}>{numero(d.emision_co2_kg)} kg</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function PlanCompensacion({ plan }: { plan: Compensacion }) {
  const mes = plan.mes_evaluado;
  return (
    <section
      aria-labelledby="sost-compensacion"
      style={{ background: "var(--rz-panel-bg)", border: "1px solid var(--rz-panel-border)", borderRadius: 14, padding: "16px 18px", display: "flex", flexDirection: "column", gap: 14 }}
    >
      <h2 id="sost-compensacion" style={{ fontFamily: "var(--rz-font-display)", fontSize: 15, margin: 0 }}>
        Plan de compensación de carbono
        <Ayuda texto={`Árboles necesarios para absorber en un año las emisiones del periodo, suponiendo que un árbol adulto absorbe ${numero(plan.kg_co2_por_arbol_anio, 0)} kg de CO₂ al año (RN-011). Es un supuesto ajustable por configuración.`} />
      </h2>
      {!plan.hay_datos ? (
        <div role="status" style={{ ...estiloAviso, background: "var(--rz-accent-soft-bg)", color: "var(--rz-accent)" }}>
          {plan.mensaje}
        </div>
      ) : (
        <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap" }}>
          <span style={{ fontFamily: "var(--rz-font-display)", fontSize: 30, fontWeight: 700 }}>{numero(plan.arboles_necesarios, 0)}</span>
          <span style={{ fontSize: 13.5, color: "var(--rz-text-muted)" }}>
            árboles para compensar {numero(plan.emision_co2_kg)} kg de CO₂ ({numero(plan.toneladas_co2, 3)} t)
          </span>
        </div>
      )}
      <div style={{ fontSize: 13, display: "flex", flexDirection: "column", gap: 6 }}>
        <span style={{ color: "var(--rz-text-muted)" }}>
          Meta mensual de emisiones: {numero(mes.emision_co2_kg)} de {numero(mes.meta_kg, 0)} kg ({numero(mes.porcentaje_meta, 0)} %)
        </span>
        <span aria-hidden="true" style={{ background: "var(--rz-bg)", borderRadius: 6, height: 10, overflow: "hidden" }}>
          <span
            style={{
              display: "block",
              height: "100%",
              width: `${Math.min(mes.porcentaje_meta, 100)}%`,
              background: mes.excede_meta ? "var(--rz-danger)" : "var(--rz-accent)",
              borderRadius: 6,
            }}
          />
        </span>
      </div>
      {mes.excede_meta && (
        <div role="alert" style={{ ...estiloAviso, display: "flex", flexDirection: "column", gap: 6 }}>
          <strong>Las emisiones del mes superan la meta. Acciones sugeridas:</strong>
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {plan.acciones.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        </div>
      )}
      {plan.alianzas.length > 0 && (
        <div style={{ fontSize: 13 }}>
          <strong>Alianzas de reforestación en Junín a explorar</strong>
          <span style={{ color: "var(--rz-text-muted)" }}> (propuestas; no hay convenios firmados)</span>
          <ul style={{ margin: "8px 0 0", paddingLeft: 18, display: "flex", flexDirection: "column", gap: 6 }}>
            {plan.alianzas.map((a) => (
              <li key={a.nombre}>
                <strong>{a.nombre}.</strong> {a.descripcion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export function SostenibilidadPage() {
  const [[desde, hasta], setRango] = useState<[string, string]>([inicioDeMes(), hoy()]);
  const [atajo, setAtajo] = useState<string | null>("mes");
  const [datos, setDatos] = useState<Dashboard | null>(null);
  const [plan, setPlan] = useState<Compensacion | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  const [generando, setGenerando] = useState(false);
  const [estadoReporte, setEstadoReporte] = useState<{ tipo: "exito" | "error"; texto: string } | null>(null);

  const cargar = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const periodo = `desde=${desde}&hasta=${hasta}`;
      const [dashboard, compensacion] = await Promise.all([
        api.get<Dashboard>(`/api/sostenibilidad/dashboard?${periodo}`),
        api.get<Compensacion>(`/api/sostenibilidad/compensacion?${periodo}`),
      ]);
      setDatos(dashboard);
      setPlan(compensacion);
    } catch (err) {
      setDatos(null);
      setPlan(null);
      setError(mensajeDeError(err, "No se pudieron cargar los indicadores"));
    } finally {
      setCargando(false);
    }
  }, [desde, hasta]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function descargarReporte() {
    setGenerando(true);
    setEstadoReporte(null);
    try {
      const archivo = await api.descargar(`/api/sostenibilidad/reporte?desde=${desde}&hasta=${hasta}`);
      const enlace = document.createElement("a");
      enlace.href = URL.createObjectURL(archivo);
      enlace.download = `reporte-sostenibilidad-${desde}-${hasta}.pdf`;
      enlace.click();
      URL.revokeObjectURL(enlace.href);
      setEstadoReporte({ tipo: "exito", texto: "El reporte se descargó." });
    } catch (err) {
      setEstadoReporte({ tipo: "error", texto: mensajeDeError(err, "No se pudo generar el reporte") });
    } finally {
      setGenerando(false);
    }
  }

  function elegirAtajo(id: string) {
    const elegido = ATAJOS.find((a) => a.id === id);
    if (!elegido) return;
    setRango(elegido.rango() as [string, string]);
    setAtajo(id);
  }

  function cambiarFecha(campo: "desde" | "hasta", valor: string) {
    if (!valor) return;
    setRango(campo === "desde" ? [valor, hasta] : [desde, valor]);
    setAtajo(null);
  }

  const t = datos?.totales;
  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", gap: 20, maxWidth: 1440 }}>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontFamily: "var(--rz-font-display)", fontSize: 22, margin: "0 0 4px" }}>Sostenibilidad</h1>
          <p style={{ margin: 0, fontSize: 13, color: "var(--rz-text-muted)" }}>
            Emisiones, combustible ahorrado y cumplimiento de las jornadas confirmadas del periodo.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 10, flexWrap: "wrap" }}>
          {ATAJOS.map((a) => (
            <FiltroChip key={a.id} etiqueta={a.etiqueta} activo={atajo === a.id} onClick={() => elegirAtajo(a.id)} />
          ))}
          <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
            <label htmlFor="sost-desde">Desde</label>
            <input id="sost-desde" type="date" value={desde} max={hasta} onChange={(e) => cambiarFecha("desde", e.target.value)} style={estiloInput} />
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12.5, color: "var(--rz-text-muted)" }}>
            <label htmlFor="sost-hasta">Hasta</label>
            <input id="sost-hasta" type="date" value={hasta} min={desde} onChange={(e) => cambiarFecha("hasta", e.target.value)} style={estiloInput} />
          </div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <button type="button" onClick={() => void descargarReporte()} disabled={generando} style={estiloBotonPrimario}>
          {generando ? "Generando reporte…" : "Descargar reporte PDF"}
        </button>
        <span style={{ fontSize: 12.5, color: "var(--rz-text-muted)" }}>
          Incluye CO₂ por ruta, costo del ciclo de vida de la flota, ahorro de combustible y metas del periodo elegido.
        </span>
        {estadoReporte && (
          <span
            role={estadoReporte.tipo === "error" ? "alert" : "status"}
            style={estadoReporte.tipo === "error" ? { ...estiloAviso, padding: "6px 10px" } : { fontSize: 12.5, color: "var(--rz-accent)" }}
          >
            {estadoReporte.texto}
          </span>
        )}
      </div>

      {error && (
        <div role="alert" style={estiloAviso}>
          {error}
        </div>
      )}
      {cargando && !datos && (
        <div role="status" style={{ color: "var(--rz-text-muted)", fontSize: 13.5 }}>
          Cargando indicadores…
        </div>
      )}

      {datos && t && (
        <>
          {!datos.hay_datos && (
            <div role="status" style={{ ...estiloAviso, background: "var(--rz-accent-soft-bg)", color: "var(--rz-accent)" }}>
              {datos.mensaje}
            </div>
          )}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 210px), 1fr))", gap: 14 }}>
            <Indicador
              etiqueta="Distancia recorrida"
              valor={numero(t.distancia_km)}
              unidad="km"
              ayuda="Suma de la distancia de las rutas confirmadas, en ejecución o completadas del periodo. Los borradores no cuentan."
            />
            <Indicador
              etiqueta="Emisiones de CO₂"
              valor={numero(t.emision_co2_kg)}
              unidad="kg"
              ayuda="Distancia recorrida por el factor de emisión de cada vehículo (kg de CO₂ por km), según la regla RN-009."
            />
            <Indicador
              etiqueta="Combustible ahorrado"
              valor={numero(t.combustible_ahorrado_l)}
              unidad="L"
              ayuda="Combustible que se evita frente a la solución inicial del optimizador, antes de mejorarla. Tras una re-optimización las métricas de la ruta cubren solo el tramo restante."
            />
            <Indicador
              etiqueta="Cumplimiento de ventanas"
              valor={numero(t.cumplimiento_ventanas_pct)}
              unidad="%"
              ayuda="Porcentaje de paradas que se estima atender dentro de la ventana de tiempo del pedido (RN-006)."
            />
            <Indicador
              etiqueta="Ahorro económico"
              valor={`S/ ${numero(t.ahorro_soles, 2)}`}
              unidad=""
              ayuda={`Combustible ahorrado por el precio del litro, que es un supuesto de S/ ${numero(datos.precio_combustible_soles_l, 2)} por litro y se ajusta por configuración.`}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 360px), 1fr))", gap: 14, alignItems: "start" }}>
            <section
              aria-labelledby="sost-entregas"
              style={{ background: "var(--rz-panel-bg)", border: "1px solid var(--rz-panel-border)", borderRadius: 14, padding: "16px 18px" }}
            >
              <h2 id="sost-entregas" style={{ fontFamily: "var(--rz-font-display)", fontSize: 15, margin: "0 0 12px" }}>
                Jornadas y entregas
              </h2>
              <dl style={{ margin: 0, display: "grid", gridTemplateColumns: "1fr auto", gap: "8px 16px", fontSize: 13.5 }}>
                <dt style={{ color: "var(--rz-text-muted)" }}>Rutas del periodo</dt>
                <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{t.rutas}</dd>
                <dt style={{ color: "var(--rz-text-muted)" }}>Entregas realizadas</dt>
                <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{datos.entregas.entregadas}</dd>
                <dt style={{ color: "var(--rz-text-muted)" }}>Entregas pendientes</dt>
                <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{datos.entregas.pendientes}</dd>
                <dt style={{ color: "var(--rz-text-muted)" }}>Entregas fallidas</dt>
                <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{datos.entregas.fallidas}</dd>
                <dt style={{ color: "var(--rz-text-muted)" }}>Combustible gastado</dt>
                <dd style={{ margin: 0, fontFamily: "var(--rz-font-mono)" }}>{numero(t.combustible_l)} L</dd>
              </dl>
            </section>
            {datos.por_dia.length > 0 && <GraficoPorDia dias={datos.por_dia} />}
          </div>
          {plan && <PlanCompensacion plan={plan} />}
        </>
      )}
    </div>
  );
}
