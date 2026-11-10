/**
 * Huella de carbono de los datos que descarga el navegador, con el modelo SWDM v4 (Sustainable Web Design Model, de la
 * Green Web Foundation). Usa los mismos valores y fórmulas que `scripts/calcular_huella_swdm.py`, que se contrasta con
 * CO2.js 0.16.9 (ver el informe de reducción del impacto ambiental, sección 7).
 *
 *   energía (kWh)    = GB transferidos × kWh/GB (operativa + incorporada)
 *   emisión (g CO2e) = energía (kWh) × intensidad de la red eléctrica (g CO2e/kWh)
 */

/** kWh por GB de cada segmento. Operativa: electricidad al usar el equipo. Incorporada: fabricación del hardware. */
const OPERATIVA = { centroDeDatos: 0.055, red: 0.059, dispositivo: 0.08 };
const INCORPORADA = { centroDeDatos: 0.012, red: 0.013, dispositivo: 0.081 };
const suma = (segmentos: Record<string, number>) => Object.values(segmentos).reduce((total, kwh) => total + kwh, 0);

/** 0.194 operativa + 0.106 incorporada = 0.300 kWh por GB transferido. */
export const KWH_POR_GB = suma(OPERATIVA) + suma(INCORPORADA);
/** Intensidad global de la red eléctrica que fija SWDM v4 en CO2.js (g CO2e por kWh). */
export const INTENSIDAD_GLOBAL_G_POR_KWH = 494;
const BYTES_POR_GB = 1_000_000_000;

export function energiaKwh(bytes: number): number {
  return (bytes / BYTES_POR_GB) * KWH_POR_GB;
}

export function emisionG(bytes: number): number {
  return energiaKwh(bytes) * INTENSIDAD_GLOBAL_G_POR_KWH;
}

let bytesDescargados = 0;
let iniciado = false;

/**
 * Empieza a sumar los bytes que el navegador descarga (el documento y cada recurso: archivos de la aplicación y
 * respuestas de la API). Se llama una vez al arrancar. Con `buffered` también cuenta lo que ya se descargó antes de
 * llamarla. No suma lo que viene de la caché del navegador ni las respuestas de otro dominio que no envían
 * `Timing-Allow-Origin` (el navegador informa 0 en esos casos).
 */
export function iniciarMedicionDeTransferencia(): void {
  if (iniciado || typeof PerformanceObserver === "undefined") return;
  iniciado = true;
  try {
    const observador = new PerformanceObserver((lista) => {
      for (const entrada of lista.getEntries()) {
        bytesDescargados += (entrada as PerformanceResourceTiming).transferSize || 0;
      }
    });
    observador.observe({ type: "navigation", buffered: true });
    observador.observe({ type: "resource", buffered: true });
  } catch {
    // Navegador sin soporte de estos tipos de medición: la tarjeta mostrará ceros
  }
}

/** Bytes descargados desde que se abrió la aplicación. */
export function bytesTransferidos(): number {
  return bytesDescargados;
}
