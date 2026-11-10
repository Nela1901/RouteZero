/** Proyección de cierre de mes de las emisiones de CO₂, para compararla con la meta mensual (RN-010). */

export interface EmisionDia {
  fecha: string; // AAAA-MM-DD
  emision_co2_kg: number;
}

export interface ProyeccionMes {
  /** Días del calendario del mes. */
  diasDelMes: number;
  /** Último día contado: el día del mes de la fecha final del periodo. */
  diaActual: number;
  /** Kilogramos acumulados del día 1 al día `d` (un punto por cada día del calendario hasta `diaActual`). */
  acumulado: { dia: number; kg: number }[];
  emisionAcumulada: number;
  /** Cierre estimado del mes a su ritmo promedio; `null` si el mes ya terminó. */
  proyeccionKg: number | null;
  /** Lo que cerró el mes (si terminó) o lo que cerraría según la proyección. */
  cierraEnKg: number;
}

export function diasDelMes(anio: number, mes: number): number {
  return new Date(anio, mes, 0).getDate();
}

/**
 * Emisión acumulada del mes y su proyección de cierre. El ritmo es el promedio de los días del calendario
 * transcurridos (domingos incluidos): lo emitido hasta hoy, dividido entre los días transcurridos y multiplicado por
 * los días del mes. Devuelve `null` si el periodo no es «el mes desde el día 1 hasta una fecha del mismo mes»,
 * porque entonces no hay datos de todos los días para acumular.
 */
export function proyeccionDelMes(porDia: EmisionDia[], desde: string, hasta: string): ProyeccionMes | null {
  const [anioDesde, mesDesde, diaDesde] = desde.split("-").map(Number);
  const [anioHasta, mesHasta, diaActual] = hasta.split("-").map(Number);
  if (diaDesde !== 1 || anioDesde !== anioHasta || mesDesde !== mesHasta) return null;

  const total = diasDelMes(anioHasta, mesHasta);
  const porNumeroDeDia = new Map<number, number>();
  for (const d of porDia) {
    const dia = Number(d.fecha.slice(8, 10));
    porNumeroDeDia.set(dia, (porNumeroDeDia.get(dia) ?? 0) + d.emision_co2_kg);
  }

  let corriente = 0;
  const acumulado = Array.from({ length: diaActual }, (_, i) => {
    corriente += porNumeroDeDia.get(i + 1) ?? 0;
    return { dia: i + 1, kg: corriente };
  });

  const proyeccionKg = diaActual < total ? (corriente / diaActual) * total : null;
  return { diasDelMes: total, diaActual, acumulado, emisionAcumulada: corriente, proyeccionKg, cierraEnKg: proyeccionKg ?? corriente };
}
