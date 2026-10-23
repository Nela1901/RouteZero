import type { Page, Route } from "@playwright/test";

/**
 * Simulación de la API para las pruebas de extremo a extremo. Todo lo que no esté simulado se anota en
 * `noSimuladas`: cada prueba comprueba que esté vacío, de modo que un endpoint nuevo o un cambio de contrato que
 * la interfaz ya usa haga fallar la prueba en lugar de pasar por alto el cambio.
 */

export type Rol = "ADMINISTRADOR" | "OPERADOR" | "CONDUCTOR";

export const CREDENCIALES: Record<Rol, { email: string; password: string }> = {
  ADMINISTRADOR: { email: "admin@routezero.test", password: "clave-de-prueba" },
  OPERADOR: { email: "operador@routezero.test", password: "clave-de-prueba" },
  CONDUCTOR: { email: "conductor@routezero.test", password: "clave-de-prueba" },
};

const DEPOSITO = { latitud: -12.0436, longitud: -75.2264 };
const PUNTOS: [number, number][] = [
  [-12.0436, -75.2264],
  [-12.052, -75.218],
  [-12.061, -75.211],
  [-12.0653, -75.2049],
];

export interface Parada {
  orden: number;
  pedido_id: string;
  cliente: string;
  descripcion: string | null;
  peso_kg: string;
  prioridad: "EXPRESS" | "ESTANDAR" | "ECONOMICO";
  latitud: number;
  longitud: number;
  hora_estimada: string;
  minutos_retraso: number;
  estado_entrega: "PENDIENTE" | "ENTREGADO" | "FALLIDO";
  pedido_estado: string;
}

export function parada(orden: number, extra: Partial<Parada> = {}): Parada {
  const [latitud, longitud] = PUNTOS[orden] ?? PUNTOS[PUNTOS.length - 1];
  return {
    orden,
    pedido_id: `00000000-0000-4000-8000-00000000000${orden}`,
    cliente: ["", "Bodega San José", "Calzados Puno", "Minimarket Real"][orden] ?? `Cliente ${orden}`,
    descripcion: null,
    peso_kg: "25.00",
    prioridad: orden === 1 ? "EXPRESS" : "ESTANDAR",
    latitud,
    longitud,
    hora_estimada: `0${7 + orden}:30:00`,
    minutos_retraso: 0,
    estado_entrega: "PENDIENTE",
    pedido_estado: "ASIGNADO",
    ...extra,
  };
}

export function rutaMapa(id: string, placa: string, estado = "CONFIRMADA", paradas = [parada(1), parada(2), parada(3)]) {
  const tramos = [0, ...paradas.map((p) => p.orden)].map((desde, i) => ({
    desde,
    hasta: i < paradas.length ? paradas[i].orden : 0,
    distancia_km: 2.5,
    duracion_min: 7.5,
    en_punta: i === 0,
    puntos: [PUNTOS[Math.min(i, PUNTOS.length - 1)], PUNTOS[Math.min(i + 1, PUNTOS.length - 1)]],
  }));
  return {
    ruta_id: id,
    lote_id: "lote-1",
    estado,
    reemplaza_ruta_id: null,
    vehiculo: { vehiculo_id: `v-${id}`, placa, tipo: "CAMIONETA" },
    conductor: { conductor_id: `c-${id}`, nombre: `Conductor ${placa}` },
    hora_salida: "08:00:00",
    hora_regreso: "11:00:00",
    paradas,
    tramos,
  };
}

export function congestion(nivel: "VERDE" | "AMARILLO" | "ROJO" = "VERDE", hora = "10:00:00") {
  const motivos = nivel === "VERDE" ? [] : ["hora punta"];
  return {
    hora,
    en_punta: nivel !== "VERDE",
    vias: [
      { calle: "Av. Ferrocarril", nivel, factor: nivel === "VERDE" ? 1 : 1.8, motivos, segmentos: [[[-12.07, -75.2], [-12.071, -75.201]]] },
      { calle: "Av. Giráldez", nivel, factor: nivel === "VERDE" ? 1 : 1.6, motivos, segmentos: [[[-12.065, -75.21], [-12.066, -75.211]]] },
      { calle: "Calle Real", nivel, factor: nivel === "VERDE" ? 1 : 1.3, motivos, segmentos: [[[-12.06, -75.205], [-12.061, -75.206]]] },
    ],
  };
}

export function miRuta(paradas = [parada(1), parada(2), parada(3)], estado = "CONFIRMADA") {
  const atendibles = paradas.filter((p) => p.pedido_estado !== "CANCELADO");
  const pendientes = atendibles.filter((p) => p.estado_entrega === "PENDIENTE");
  const ruta = rutaMapa("ruta-1", "ABC-101", estado, paradas);
  return {
    fecha_jornada: "2026-10-22",
    hora: "10:00:00",
    deposito: DEPOSITO,
    vinculado: true,
    mensaje: null as string | null,
    conductor: { conductor_id: "c-ruta-1", nombre: "Carlos Quispe" },
    ruta: ruta as typeof ruta | null,
    siguiente_orden: pendientes.length ? Math.min(...pendientes.map((p) => p.orden)) : (null as number | null),
    entregadas: atendibles.length - pendientes.length,
    pendientes: pendientes.length,
    alertas: [] as unknown[],
  };
}

export type MiRuta = ReturnType<typeof miRuta>;

export function dashboardSostenibilidad(hayDatos = true, desde = "2026-10-01", hasta = "2026-10-22") {
  const ceros = { rutas: 0, distancia_km: 0, emision_co2_kg: 0, combustible_l: 0, combustible_ahorrado_l: 0, ahorro_soles: 0, cumplimiento_ventanas_pct: 0 };
  return {
    desde,
    hasta,
    hay_datos: hayDatos,
    mensaje: hayDatos ? null : "No hay jornadas operativas registradas en el periodo seleccionado.",
    totales: hayDatos
      ? { rutas: 3, distancia_km: 120.5, emision_co2_kg: 28.4, combustible_l: 14.2, combustible_ahorrado_l: 2.5, ahorro_soles: 11.25, cumplimiento_ventanas_pct: 96.7 }
      : ceros,
    entregas: hayDatos ? { entregadas: 8, pendientes: 3, fallidas: 1 } : { entregadas: 0, pendientes: 0, fallidas: 0 },
    por_dia: hayDatos
      ? [
          { fecha: "2026-10-20", emision_co2_kg: 10.2, distancia_km: 40, combustible_ahorrado_l: 1 },
          { fecha: "2026-10-21", emision_co2_kg: 18.2, distancia_km: 80.5, combustible_ahorrado_l: 1.5 },
        ]
      : [],
    precio_combustible_soles_l: 4.5,
  };
}

export function compensacionSostenibilidad(hayDatos = true, excede = true) {
  return {
    hay_datos: hayDatos,
    mensaje: hayDatos ? null : "No hay datos suficientes: ejecute al menos una jornada operativa antes de generar el plan.",
    emision_co2_kg: hayDatos ? 1000 : 0,
    toneladas_co2: hayDatos ? 1 : 0,
    kg_co2_por_arbol_anio: 22,
    arboles_necesarios: hayDatos ? 46 : 0,
    mes_evaluado: { desde: "2026-10-01", hasta: "2026-10-22", emision_co2_kg: hayDatos ? 1000 : 0, meta_kg: 800, porcentaje_meta: hayDatos ? 125 : 0, excede_meta: hayDatos && excede },
    acciones: hayDatos && excede ? ["Regenerar y re-optimizar las rutas para acortar la distancia total recorrida.", "Reducir las jornadas o consolidar pedidos de zonas cercanas en una misma ruta."] : [],
    alianzas: hayDatos ? [{ nombre: "Gobierno Regional de Junín y SERFOR", descripcion: "Programas públicos de reforestación en la región." }] : [],
  };
}

export interface Escenario {
  rol?: Rol;
  mapa?: ReturnType<typeof rutaMapa>[];
  congestion?: ReturnType<typeof congestion>;
  miRuta?: MiRuta;
  incidentes?: unknown[];
  pedidos?: unknown[];
  /** Rutas del listado de Rutas (sin paradas), como las devuelve `GET /api/rutas?fecha=`. */
  rutas?: unknown[];
  /** Respuestas de `GET /api/sostenibilidad/dashboard` y `/compensacion`. */
  sostenibilidad?: { dashboard: ReturnType<typeof dashboardSostenibilidad>; compensacion: ReturnType<typeof compensacionSostenibilidad> };
}

export interface Simulacion {
  /** Peticiones a la API sin simular (deben quedar vacías). */
  noSimuladas: string[];
  /** Todas las peticiones atendidas, para comprobar qué pidió la interfaz. */
  peticiones: { metodo: string; ruta: string; cuerpo: unknown }[];
  estado: Required<Pick<Escenario, "incidentes" | "pedidos" | "rutas">> & Escenario;
}

const PNG_TRANSPARENTE = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", "base64");

const resumenRuta = (r: ReturnType<typeof rutaMapa>) => ({
  ruta_id: r.ruta_id, lote_id: r.lote_id, fecha_jornada: "2026-10-22", estado: r.estado, vehiculo: r.vehiculo, conductor: r.conductor,
  hora_salida: r.hora_salida, hora_regreso: r.hora_regreso, distancia_km: "20.00", tiempo_min: 180, cantidad_paradas: r.paradas.length,
  metricas: null, paradas: [], reemplaza_ruta_id: r.reemplaza_ruta_id,
});

export async function simularApi(page: Page, escenario: Escenario = {}): Promise<Simulacion> {
  const sim: Simulacion = {
    noSimuladas: [],
    peticiones: [],
    estado: { incidentes: [], pedidos: [], rutas: [], ...escenario },
  };
  const rol = escenario.rol ?? "ADMINISTRADOR";

  // Sin mosaicos del mapa: las pruebas no dependen de internet
  await page.route("https://tile.openstreetmap.org/**", (r) => r.fulfill({ status: 200, contentType: "image/png", body: PNG_TRANSPARENTE }));

  await page.route("**/api/**", async (route: Route) => {
    const peticion = route.request();
    const url = new URL(peticion.url());
    const metodo = peticion.method();
    const ruta = url.pathname;
    let cuerpo: unknown = null;
    try {
      cuerpo = peticion.postDataJSON();
    } catch {
      cuerpo = null;
    }
    sim.peticiones.push({ metodo, ruta: ruta + url.search, cuerpo });
    const json = (datos: unknown, status = 200) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(datos) });
    const e = sim.estado;

    if (metodo === "POST" && ruta === "/api/auth/login") {
      const { email, password } = cuerpo as { email: string; password: string };
      const rolDe = (Object.keys(CREDENCIALES) as Rol[]).find((r) => CREDENCIALES[r].email === email && CREDENCIALES[r].password === password);
      if (!rolDe) return json({ detail: "Credenciales inválidas" }, 401);
      escenario.rol = rolDe;
      return json({ estado: "ok", access_token: `token-${rolDe}`, refresh_token: "refresh", expires_in: 3600, mfa_token: null, factor_id: null });
    }
    if (metodo === "GET" && ruta === "/api/auth/me") {
      const actual = escenario.rol ?? rol;
      return json({ usuario_id: `u-${actual}`, email: CREDENCIALES[actual].email, rol_id: "r1", rol_nombre: actual, mfa_activo: false });
    }
    if (metodo === "DELETE" && ruta === "/api/auth/sesiones") return json({ sesiones_revocadas: 1 });

    if (metodo === "GET" && ruta === "/api/rutas/mapa") {
      return json({ fecha_jornada: url.searchParams.get("fecha"), deposito: DEPOSITO, rutas: e.mapa ?? [] });
    }
    if (metodo === "GET" && ruta === "/api/rutas/congestion") return json(e.congestion ?? congestion());
    if (metodo === "GET" && ruta === "/api/rutas/mi-ruta") {
      return json(e.miRuta ?? { ...miRuta(), ruta: null, siguiente_orden: null, entregadas: 0, pendientes: 0, mensaje: "No tienes rutas asignadas por el momento." });
    }
    if (metodo === "PATCH" && /^\/api\/rutas\/[^/]+\/paradas\/[^/]+\/entrega$/.test(ruta)) {
      const pedido = ruta.split("/")[5];
      const { estado } = cuerpo as { estado: "ENTREGADO" | "FALLIDO" };
      if (e.miRuta?.ruta) {
        const paradas = e.miRuta.ruta.paradas.map((p) => (p.pedido_id === pedido ? { ...p, estado_entrega: estado } : p));
        const nuevo = miRuta(paradas, paradas.every((p) => p.estado_entrega !== "PENDIENTE") ? "COMPLETADA" : "EN_EJECUCION");
        e.miRuta = { ...e.miRuta, ...nuevo };
      }
      return json({ ruta_id: "ruta-1", pedido_id: pedido, estado_entrega: estado, estado_ruta: "EN_EJECUCION" });
    }
    if (metodo === "GET" && ruta === "/api/sostenibilidad/dashboard") {
      const base = e.sostenibilidad?.dashboard ?? dashboardSostenibilidad();
      return json({ ...base, desde: url.searchParams.get("desde"), hasta: url.searchParams.get("hasta") });
    }
    if (metodo === "GET" && ruta === "/api/sostenibilidad/reporte") {
      if (e.sostenibilidad && !e.sostenibilidad.dashboard.hay_datos) {
        return json({ detail: "No hay datos suficientes para generar el reporte en el periodo seleccionado. Seleccione otro periodo." }, 404);
      }
      return route.fulfill({ status: 200, contentType: "application/pdf", body: Buffer.from("%PDF-1.4\n%%EOF\n") });
    }
    if (metodo === "GET" && ruta === "/api/sostenibilidad/compensacion") return json(e.sostenibilidad?.compensacion ?? compensacionSostenibilidad());
    if (metodo === "GET" && ruta === "/api/rutas/incidentes") return json(e.incidentes);
    if (metodo === "GET" && ruta === "/api/rutas") return json(e.rutas);
    if (metodo === "GET" && ruta === "/api/pedidos") return json({ items: e.pedidos, total: e.pedidos.length, limite: 200, desplazamiento: 0 });
    if (metodo === "POST" && ruta === "/api/rutas/reoptimizar") {
      const activas = (e.mapa ?? []).filter((r) => r.estado === "CONFIRMADA" || r.estado === "EN_EJECUCION");
      if (activas.length === 0) {
        return json({ lote_id: null, fecha_jornada: "2026-10-22", sin_rutas_activas: true, mensaje: "No hay rutas activas para re-optimizar en esa fecha. Genere nuevas rutas desde el módulo de rutas.", hora_considerada: null, rutas: [], sin_cobertura: [], pedidos_nuevos: 0, pedidos_retirados: 0, incidentes_aplicados: [], comparativa: null, fuente_distancias: "calles", iteraciones: 0, tiempo_ejecucion_s: 0, dentro_del_limite: true, tiempos: {} }, 201);
      }
      const borrador = { ...resumenRuta({ ...activas[0], estado: "PLANIFICADA" }), reemplaza_ruta_id: activas[0].ruta_id, ruta_id: "borrador-1", lote_id: "lote-2" };
      e.rutas = [...e.rutas, borrador];
      return json({ lote_id: "lote-2", fecha_jornada: "2026-10-22", sin_rutas_activas: false, mensaje: "", hora_considerada: "10:00:00", rutas: [borrador], sin_cobertura: [], pedidos_nuevos: 1, pedidos_retirados: 0, incidentes_aplicados: [], comparativa: null, fuente_distancias: "calles", iteraciones: 3, tiempo_ejecucion_s: 22.2, dentro_del_limite: true, tiempos: {} }, 201);
    }

    sim.noSimuladas.push(`${metodo} ${ruta}${url.search}`);
    return json({ detail: "Endpoint no simulado en la prueba" }, 404);
  });

  return sim;
}

/** Deja la sesión iniciada: guarda los tokens que la aplicación busca al arrancar. */
export async function conSesion(page: Page, rol: Rol) {
  await page.addInitScript((token) => {
    window.localStorage.setItem("routezero:access_token", token);
    window.localStorage.setItem("routezero:refresh_token", "refresh");
  }, `token-${rol}`);
}

export { resumenRuta };
