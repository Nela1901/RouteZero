import { mkdirSync, writeFileSync } from "node:fs";
import { expect, request, test } from "@playwright/test";

// Monitoreo de producción con Playwright. Variables de entorno (todas opcionales):
//   URL_FRONTEND   por defecto, el despliegue de Vercel
//   URL_API        por defecto, el despliegue de Render
//   CARGAS         cuántas veces se carga la página de inicio para medir Web Vitals (por defecto 5)
//   MUESTRAS       cuántas consultas seguidas al endpoint de salud para medir tiempos y disponibilidad (por defecto 10)
//   PAUSA_MS       pausa entre muestras de disponibilidad (por defecto 3000)
// El resultado se guarda en `test-results/monitoreo-produccion.json`. Render gratuito se «duerme» tras un rato sin
// tráfico: la primera petición puede tardar decenas de segundos, por eso se separa el arranque en frío de las demás.
const FRONTEND = process.env.URL_FRONTEND ?? "https://route-zero-omega.vercel.app";
const API = process.env.URL_API ?? "https://routezero-7k7j.onrender.com";
const CARGAS = Number(process.env.CARGAS ?? 5);
const MUESTRAS = Number(process.env.MUESTRAS ?? 10);
const PAUSA_MS = Number(process.env.PAUSA_MS ?? 3000);
const CABECERAS = { "User-Agent": "RouteZero-monitoreo/1.0" };

// Umbrales «buenos» de Web Vitals (web.dev) para clasificar cada medición.
const UMBRALES = { ttfb: 800, fcp: 1800, lcp: 2500 } as const;
const resultado: Record<string, unknown> = { fecha: new Date().toISOString(), frontend: FRONTEND, api: API };

const redondear = (n: number) => Math.round(n);
function percentil(valores: number[], p: number): number {
  const orden = [...valores].sort((a, b) => a - b);
  return orden[Math.min(orden.length - 1, Math.ceil((p / 100) * orden.length) - 1)];
}
function resumen(valores: number[]) {
  return {
    n: valores.length,
    min: redondear(Math.min(...valores)),
    mediana: redondear(percentil(valores, 50)),
    p95: redondear(percentil(valores, 95)),
    max: redondear(Math.max(...valores)),
  };
}

test.afterAll(() => {
  mkdirSync("test-results", { recursive: true });
  writeFileSync("test-results/monitoreo-produccion.json", JSON.stringify(resultado, null, 2));
});

test("Web Vitals y tiempos de carga de la pantalla de inicio de sesión", async ({ browser }) => {
  const cargas: { estado: number; ttfb: number; fcp: number; lcp: number; domContentLoaded: number; carga: number }[] = [];
  for (let i = 0; i < CARGAS; i++) {
    const contexto = await browser.newContext({ extraHTTPHeaders: CABECERAS });
    const page = await contexto.newPage();
    // El observador de LCP se registra antes de que la página cargue para no perder ninguna entrada.
    await page.addInitScript(() => {
      (window as unknown as { __lcp: number }).__lcp = 0;
      new PerformanceObserver((lista) => {
        const ultima = lista.getEntries().at(-1);
        if (ultima) (window as unknown as { __lcp: number }).__lcp = ultima.startTime;
      }).observe({ type: "largest-contentful-paint", buffered: true });
    });
    const respuesta = await page.goto(FRONTEND, { waitUntil: "load" });
    await expect(page.getByRole("button", { name: "Ingresar" })).toBeVisible();
    await page.waitForTimeout(500); // deja que el LCP se estabilice
    const medidas = await page.evaluate(() => {
      const nav = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming;
      const fcp = performance.getEntriesByName("first-contentful-paint")[0]?.startTime ?? 0;
      return {
        ttfb: nav.responseStart - nav.startTime,
        fcp,
        lcp: (window as unknown as { __lcp: number }).__lcp,
        domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
        carga: nav.loadEventEnd - nav.startTime,
      };
    });
    cargas.push({ estado: respuesta?.status() ?? 0, ...medidas });
    await contexto.close();
  }

  const por = (clave: "ttfb" | "fcp" | "lcp" | "domContentLoaded" | "carga") => resumen(cargas.map((c) => c[clave]));
  const vitals = { ttfb: por("ttfb"), fcp: por("fcp"), lcp: por("lcp"), domContentLoaded: por("domContentLoaded"), carga: por("carga") };
  resultado.webVitals = {
    cargas,
    resumen: vitals,
    clasificacion: {
      ttfb: vitals.ttfb.mediana <= UMBRALES.ttfb ? "bueno" : "mejorable",
      fcp: vitals.fcp.mediana <= UMBRALES.fcp ? "bueno" : "mejorable",
      lcp: vitals.lcp.mediana <= UMBRALES.lcp ? "bueno" : "mejorable",
    },
    umbralesMs: UMBRALES,
  };
  expect(cargas.every((c) => c.estado === 200)).toBe(true);
  expect(vitals.lcp.mediana).toBeGreaterThan(0);
});

test("tiempos de respuesta y disponibilidad de la API (salud)", async () => {
  const api = await request.newContext({ baseURL: API, extraHTTPHeaders: CABECERAS });
  const muestras: { estado: number; ms: number }[] = [];
  for (let i = 0; i < MUESTRAS; i++) {
    const inicio = Date.now();
    let estado = 0;
    try {
      estado = (await api.get("/api/health", { timeout: 90_000 })).status();
    } catch {
      estado = 0; // red caída o tiempo agotado: cuenta como no disponible
    }
    muestras.push({ estado, ms: Date.now() - inicio });
    if (i < MUESTRAS - 1) await new Promise((r) => setTimeout(r, PAUSA_MS));
  }
  await api.dispose();

  const correctas = muestras.filter((m) => m.estado === 200);
  const [primera, ...demas] = muestras.map((m) => m.ms);
  resultado.salud = {
    muestras,
    disponibilidadPorcentaje: Number(((correctas.length / muestras.length) * 100).toFixed(1)),
    primeraPeticionMs: primera, // puede incluir el arranque en frío de Render
    siguientes: demas.length ? resumen(demas) : null,
    todas: resumen(muestras.map((m) => m.ms)),
    nota: "La primera petición puede incluir el arranque en frío del plan gratuito de Render; las siguientes reflejan el servicio en caliente.",
  };
  expect(muestras.every((m) => m.estado === 200)).toBe(true);
});

test("códigos HTTP: rutas protegidas sin sesión, ruta inexistente y CORS", async () => {
  const api = await request.newContext({ baseURL: API, extraHTTPHeaders: CABECERAS });
  const comprobaciones = [
    { nombre: "salud", metodo: "GET", ruta: "/api/health", esperado: [200] },
    { nombre: "ruta protegida sin sesión (rutas)", metodo: "GET", ruta: "/api/rutas", esperado: [401, 403] },
    { nombre: "ruta protegida sin sesión (pedidos)", metodo: "GET", ruta: "/api/pedidos", esperado: [401, 403] },
    { nombre: "ruta protegida sin sesión (sostenibilidad)", metodo: "GET", ruta: "/api/sostenibilidad/dashboard", esperado: [401, 403] },
    { nombre: "ruta inexistente", metodo: "GET", ruta: "/api/no-existe", esperado: [404] },
  ];
  const filas = [];
  for (const c of comprobaciones) {
    const respuesta = await api.get(c.ruta);
    filas.push({ ...c, obtenido: respuesta.status(), correcto: c.esperado.includes(respuesta.status()) });
  }
  // Un origen no autorizado no debe recibir cabeceras CORS que lo permitan.
  const ajeno = await api.get("/api/health", { headers: { Origin: "https://sitio-ajeno.example" } });
  const permite = ajeno.headers()["access-control-allow-origin"] ?? null;
  await api.dispose();

  resultado.codigosHttp = { filas, corsOrigenAjeno: { permiteOrigen: permite, correcto: permite === null || permite !== "https://sitio-ajeno.example" } };
  for (const fila of filas) expect(fila.correcto, `${fila.nombre}: se esperaba ${fila.esperado.join("/")} y llegó ${fila.obtenido}`).toBe(true);
  expect(permite).not.toBe("https://sitio-ajeno.example");
  expect(permite).not.toBe("*");
});
