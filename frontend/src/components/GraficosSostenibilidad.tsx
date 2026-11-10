import { useState } from "react";
import type { ProyeccionMes } from "./proyeccionMes";
import { Ayuda, FiltroChip, estiloAviso } from "./ui";

/** Un día de operación del dashboard de sostenibilidad (lo que devuelve `por_dia` de la API). */
export interface DiaSostenibilidad {
  fecha: string;
  rutas: number;
  emision_co2_kg: number;
  distancia_km: number;
  combustible_ahorrado_l: number;
  entregadas: number;
  fallidas: number;
}

const PANEL = { background: "var(--rz-panel-bg)", border: "1px solid var(--rz-panel-border)", borderRadius: 14, padding: "16px 18px" } as const;
const TITULO = { fontFamily: "var(--rz-font-display)", fontSize: 15, margin: "0 0 12px" } as const;
const TEXTO_EJE = { fontSize: 12, fill: "var(--rz-text-muted)", fontFamily: "var(--rz-font-mono)" } as const;

const numero = (valor: number, decimales = 1) =>
  valor.toLocaleString("es-PE", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
const aFecha = (texto: string) => new Date(`${texto}T00:00:00`);
const fechaCorta = (texto: string) => aFecha(texto).toLocaleDateString("es-PE", { day: "2-digit", month: "short" });
const MS_POR_DIA = 86_400_000;

/** Un valor «redondo» (1, 2, 5 × 10ⁿ) mayor o igual que `maximo`, para el tope del eje vertical. */
function topeDelEje(maximo: number): number {
  if (maximo <= 0) return 1;
  const potencia = 10 ** Math.floor(Math.log10(maximo));
  const fraccion = maximo / potencia;
  const redondo = [1, 2, 5, 10].find((f) => fraccion <= f) ?? 10;
  return redondo * potencia;
}

function EjeVertical({ izq, ancho, arriba, alto, tope, unidad }: Readonly<{ izq: number; ancho: number; arriba: number; alto: number; tope: number; unidad: string }>) {
  return (
    <>
      {[0, 0.5, 1].map((f) => {
        const y = arriba + alto * (1 - f);
        return (
          <g key={f}>
            <line x1={izq} x2={izq + ancho} y1={y} y2={y} stroke="var(--rz-panel-border)" strokeWidth={1} />
            <text x={izq - 6} y={y + 4} textAnchor="end" {...TEXTO_EJE}>
              {numero(tope * f, 0)}
            </text>
          </g>
        );
      })}
      <text x={izq - 6} y={arriba - 12} textAnchor="end" {...TEXTO_EJE}>
        {unidad}
      </text>
    </>
  );
}

/** Columnas con las emisiones de cada día del periodo y su promedio. El detalle en texto está en `HistorialPorDia`. */
export function GraficoEmisionesPorDia({ dias, desde, hasta }: Readonly<{ dias: DiaSostenibilidad[]; desde: string; hasta: string }>) {
  const ANCHO = 420;
  const ALTO = 230;
  const m = { izq: 40, der: 8, arriba: 26, abajo: 26 };
  const anchoUtil = ANCHO - m.izq - m.der;
  const altoUtil = ALTO - m.arriba - m.abajo;

  const inicio = aFecha(desde).getTime();
  const nDias = Math.max(1, Math.round((aFecha(hasta).getTime() - inicio) / MS_POR_DIA) + 1);
  const paso = anchoUtil / nDias;
  const anchoBarra = Math.max(1.5, paso * 0.68);

  const total = dias.reduce((suma, d) => suma + d.emision_co2_kg, 0);
  const promedio = dias.length ? total / dias.length : 0;
  const pico = dias.reduce((mayor, d) => (d.emision_co2_kg > mayor.emision_co2_kg ? d : mayor), dias[0]);
  const tope = topeDelEje(Math.max(pico?.emision_co2_kg ?? 0, promedio));
  const y = (valor: number) => m.arriba + altoUtil * (1 - valor / tope);
  const cadaCuantos = Math.max(1, Math.ceil(nDias / 5));

  return (
    <section aria-labelledby="sost-por-dia" style={PANEL}>
      <h2 id="sost-por-dia" style={TITULO}>
        Emisiones de CO₂ por día
      </h2>
      <svg
        viewBox={`0 0 ${ANCHO} ${ALTO}`}
        role="img"
        aria-label={`Emisiones por día: ${dias.length} días con jornadas, ${numero(total)} kg en total, promedio de ${numero(promedio)} kg por día y máximo de ${numero(pico?.emision_co2_kg ?? 0)} kg el ${pico ? fechaCorta(pico.fecha) : "—"}. El detalle está en el historial por día.`}
        style={{ width: "100%", height: "auto", display: "block" }}
      >
        <EjeVertical izq={m.izq} ancho={anchoUtil} arriba={m.arriba} alto={altoUtil} tope={tope} unidad="kg" />
        {dias.map((d) => {
          const i = Math.round((aFecha(d.fecha).getTime() - inicio) / MS_POR_DIA);
          const x = m.izq + i * paso + (paso - anchoBarra) / 2;
          return (
            <rect key={d.fecha} x={x} y={y(d.emision_co2_kg)} width={anchoBarra} height={Math.max(0, m.arriba + altoUtil - y(d.emision_co2_kg))} rx={Math.min(3, anchoBarra / 2)} fill="var(--rz-accent)">
              <title>{`${fechaCorta(d.fecha)}: ${numero(d.emision_co2_kg)} kg de CO₂ · ${d.rutas} ${d.rutas === 1 ? "ruta" : "rutas"}`}</title>
            </rect>
          );
        })}
        {promedio > 0 && (
          <g>
            <line x1={m.izq} x2={m.izq + anchoUtil} y1={y(promedio)} y2={y(promedio)} stroke="var(--rz-accent-3)" strokeWidth={1.5} strokeDasharray="5 4" />
            <text x={m.izq + anchoUtil} y={y(promedio) - 5} textAnchor="end" {...TEXTO_EJE} style={{ fill: "var(--rz-accent-3)" }}>
              {`promedio ${numero(promedio)} kg`}
            </text>
          </g>
        )}
        {Array.from({ length: nDias }, (_, i) => i)
          .filter((i) => i % cadaCuantos === 0)
          .map((i) => (
            <text key={i} x={m.izq + i * paso + paso / 2} y={ALTO - 8} textAnchor="middle" {...TEXTO_EJE}>
              {new Date(inicio + i * MS_POR_DIA).toLocaleDateString("es-PE", { day: "2-digit", month: "short" })}
            </text>
          ))}
      </svg>
    </section>
  );
}

/** Emisión acumulada del mes frente a su meta, con la proyección de cierre a su ritmo promedio (RN-010). */
export function GraficoProyeccionDelMes({ proyeccion, metaKg }: Readonly<{ proyeccion: ProyeccionMes; metaKg: number }>) {
  const ANCHO = 640;
  const ALTO = 240;
  const m = { izq: 44, der: 60, arriba: 22, abajo: 28 };
  const anchoUtil = ANCHO - m.izq - m.der;
  const altoUtil = ALTO - m.arriba - m.abajo;
  const { diasDelMes, diaActual, acumulado, emisionAcumulada, proyeccionKg, cierraEnKg } = proyeccion;

  const tope = topeDelEje(Math.max(metaKg, cierraEnKg, emisionAcumulada) * 1.08);
  const x = (dia: number) => m.izq + (anchoUtil * (dia - 1)) / Math.max(1, diasDelMes - 1);
  const y = (kg: number) => m.arriba + altoUtil * (1 - kg / tope);
  const base = m.arriba + altoUtil;

  const lineaReal = acumulado.map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.dia).toFixed(1)} ${y(p.kg).toFixed(1)}`).join(" ");
  const areaReal = `${lineaReal} L ${x(diaActual).toFixed(1)} ${base} L ${x(1).toFixed(1)} ${base} Z`;
  const excede = cierraEnKg > metaKg;
  const porcentaje = metaKg > 0 ? (100 * cierraEnKg) / metaKg : 0;
  const resumen =
    proyeccionKg === null
      ? `El mes cerró en ${numero(cierraEnKg, 0)} kg de CO₂, el ${numero(porcentaje, 0)} % de la meta de ${numero(metaKg, 0)} kg.`
      : `Al ritmo actual el mes cerraría en unos ${numero(cierraEnKg, 0)} kg de CO₂, el ${numero(porcentaje, 0)} % de la meta de ${numero(metaKg, 0)} kg.`;
  const marcas = [1, 5, 10, 15, 20, 25, diasDelMes].filter((d, i, todas) => d <= diasDelMes && todas.indexOf(d) === i);

  return (
    <section aria-labelledby="sost-proyeccion" style={{ ...PANEL, display: "flex", flexDirection: "column", gap: 12 }}>
      <h2 id="sost-proyeccion" style={{ ...TITULO, margin: 0 }}>
        Proyección de cierre del mes
        <Ayuda texto="Emisión acumulada del mes frente a la meta mensual (RN-010). La proyección toma lo emitido hasta hoy, lo divide entre los días del calendario transcurridos (domingos incluidos) y lo multiplica por los días del mes: es una estimación a ritmo constante, no un pronóstico." />
      </h2>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", fontSize: 13.5 }}>
        <span>{resumen}</span>
        <span
          style={{
            ...estiloAviso,
            padding: "3px 10px",
            fontSize: 12,
            background: excede ? "var(--rz-danger-soft-bg)" : "var(--rz-accent-soft-bg)",
            color: excede ? "var(--rz-danger)" : "var(--rz-accent)",
          }}
        >
          {excede ? "Supera la meta" : "Dentro de la meta"}
        </span>
      </div>
      <svg
        viewBox={`0 0 ${ANCHO} ${ALTO}`}
        role="img"
        aria-label={`Emisión acumulada del mes: ${numero(emisionAcumulada)} kg al día ${diaActual} de ${diasDelMes}. ${resumen}`}
        style={{ width: "100%", height: "auto", display: "block" }}
      >
        <EjeVertical izq={m.izq} ancho={anchoUtil} arriba={m.arriba} alto={altoUtil} tope={tope} unidad="kg" />
        <path d={areaReal} fill="var(--rz-accent)" opacity={0.12} />
        <path d={lineaReal} fill="none" stroke="var(--rz-accent)" strokeWidth={2.5} strokeLinejoin="round" />
        {proyeccionKg !== null && (
          <g>
            <line x1={x(diaActual)} y1={y(emisionAcumulada)} x2={x(diasDelMes)} y2={y(proyeccionKg)} stroke="var(--rz-accent-2)" strokeWidth={2.5} strokeDasharray="6 5" />
            <circle cx={x(diasDelMes)} cy={y(proyeccionKg)} r={4.5} fill="var(--rz-accent-2)" />
            <text x={x(diasDelMes) + 8} y={y(proyeccionKg) + 4} {...TEXTO_EJE} style={{ fill: "var(--rz-accent-2)" }}>
              {`≈ ${numero(proyeccionKg, 0)}`}
            </text>
          </g>
        )}
        <circle cx={x(diaActual)} cy={y(emisionAcumulada)} r={4.5} fill="var(--rz-accent)" />
        <g>
          <line x1={m.izq} x2={m.izq + anchoUtil} y1={y(metaKg)} y2={y(metaKg)} stroke="var(--rz-danger)" strokeWidth={1.5} strokeDasharray="2 4" />
          <text x={m.izq + 4} y={y(metaKg) - 5} {...TEXTO_EJE} style={{ fill: "var(--rz-danger)" }}>
            {`meta ${numero(metaKg, 0)} kg`}
          </text>
        </g>
        {marcas.map((d) => (
          <text key={d} x={x(d)} y={ALTO - 8} textAnchor="middle" {...TEXTO_EJE}>
            {d}
          </text>
        ))}
      </svg>
      <ul aria-label="Leyenda" style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", gap: 18, flexWrap: "wrap", fontSize: 12.5, color: "var(--rz-text-muted)" }}>
        {[
          { texto: "Emisión acumulada", color: "var(--rz-accent)", trazo: "none" },
          { texto: "Proyección a ritmo constante", color: "var(--rz-accent-2)", trazo: "6 5" },
          { texto: "Meta mensual", color: "var(--rz-danger)", trazo: "2 4" },
        ].map((e) => (
          <li key={e.texto} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <svg width="26" height="8" aria-hidden="true">
              <line x1="0" x2="26" y1="4" y2="4" stroke={e.color} strokeWidth={2.5} strokeDasharray={e.trazo} />
            </svg>
            {e.texto}
          </li>
        ))}
      </ul>
    </section>
  );
}

const CELDA = { padding: "8px 10px", textAlign: "right", whiteSpace: "nowrap", fontFamily: "var(--rz-font-mono)", fontSize: 13 } as const;
const ENCABEZADO = { padding: "8px 10px", textAlign: "right", whiteSpace: "nowrap", fontSize: 12, fontWeight: 600, color: "var(--rz-text-muted)", borderBottom: "1px solid var(--rz-panel-border)" } as const;
const MAXIMO_VISIBLE = 10;

/** Tabla con el historial de las jornadas del periodo, de la más reciente a la más antigua. */
export function HistorialPorDia({ dias }: Readonly<{ dias: DiaSostenibilidad[] }>) {
  const [todos, setTodos] = useState(false);
  const filas = [...dias].sort((a, b) => b.fecha.localeCompare(a.fecha));
  const visibles = todos ? filas : filas.slice(0, MAXIMO_VISIBLE);
  const suma = (campo: "rutas" | "distancia_km" | "emision_co2_kg" | "combustible_ahorrado_l" | "entregadas" | "fallidas") =>
    dias.reduce((total, d) => total + d[campo], 0);

  return (
    <section aria-labelledby="sost-historial" style={PANEL}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
        <h2 id="sost-historial" style={{ ...TITULO, margin: 0 }}>
          Historial por día
          <Ayuda texto="Una fila por jornada del periodo elegido, con las rutas, los kilómetros, el CO₂ emitido, el combustible ahorrado frente a la solución inicial y las paradas entregadas y fallidas (sin contar los pedidos cancelados)." />
        </h2>
        {filas.length > MAXIMO_VISIBLE && (
          <FiltroChip etiqueta={todos ? `Mostrar solo los últimos ${MAXIMO_VISIBLE}` : `Ver los ${filas.length} días`} activo={todos} onClick={() => setTodos((v) => !v)} />
        )}
      </div>
      {/* Las tablas anchas se desplazan dentro de su propio recuadro (WCAG 1.4.10 lo permite en datos tabulares) */}
      <div tabIndex={0} role="group" aria-labelledby="sost-historial" style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 520 }}>
          <thead>
            <tr>
              <th scope="col" style={{ ...ENCABEZADO, textAlign: "left" }}>Fecha</th>
              <th scope="col" style={ENCABEZADO}>Rutas</th>
              <th scope="col" style={ENCABEZADO}>Distancia (km)</th>
              <th scope="col" style={ENCABEZADO}>CO₂ (kg)</th>
              <th scope="col" style={ENCABEZADO}>Ahorro (L)</th>
              <th scope="col" style={ENCABEZADO} title="Paradas entregadas / fallidas">Entregas ✔ / ✘</th>
            </tr>
          </thead>
          <tbody>
            {visibles.map((d) => (
              <tr key={d.fecha} style={{ borderBottom: "1px solid var(--rz-panel-border)" }}>
                <th scope="row" style={{ ...CELDA, textAlign: "left", fontFamily: "var(--rz-font-body)", fontWeight: 500 }}>
                  {aFecha(d.fecha).toLocaleDateString("es-PE", { weekday: "short", day: "2-digit", month: "short" })}
                </th>
                <td style={CELDA}>{d.rutas}</td>
                <td style={CELDA}>{numero(d.distancia_km)}</td>
                <td style={CELDA}>{numero(d.emision_co2_kg)}</td>
                <td style={CELDA}>{numero(d.combustible_ahorrado_l)}</td>
                <td style={CELDA}>{`${d.entregadas} / ${d.fallidas}`}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <th scope="row" style={{ ...CELDA, textAlign: "left", fontFamily: "var(--rz-font-body)", fontWeight: 700 }}>Total del periodo</th>
              <td style={{ ...CELDA, fontWeight: 700 }}>{suma("rutas")}</td>
              <td style={{ ...CELDA, fontWeight: 700 }}>{numero(suma("distancia_km"))}</td>
              <td style={{ ...CELDA, fontWeight: 700 }}>{numero(suma("emision_co2_kg"))}</td>
              <td style={{ ...CELDA, fontWeight: 700 }}>{numero(suma("combustible_ahorrado_l"))}</td>
              <td style={{ ...CELDA, fontWeight: 700 }}>{`${suma("entregadas")} / ${suma("fallidas")}`}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </section>
  );
}
