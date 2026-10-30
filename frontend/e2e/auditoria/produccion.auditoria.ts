import { mkdirSync, writeFileSync } from "node:fs";
import { chromium, expect, test, request } from "@playwright/test";
import lighthouse from "lighthouse";
import desktopConfig from "lighthouse/core/config/desktop-config.js";

// Lighthouse de producción. Variables de entorno:
//   CLAVE_PRUEBA     contraseña de las cuentas de prueba (obligatoria)
//   URL_FRONTEND     por defecto, el despliegue de Vercel
//   URL_API          por defecto, el despliegue de Render
//   CORREO_ADMIN / CORREO_CONDUCTOR   cuentas de prueba (por defecto, las del proyecto)
// Para que el mapa, Rutas y la vista del conductor tengan datos, crear antes la ruta de demostración de hoy
// (`python backend/tests_manual/demo_conductor.py crear`) y borrarla después (`... limpiar`).
const FRONTEND = process.env.URL_FRONTEND ?? "https://route-zero-omega.vercel.app";
const API = process.env.URL_API ?? "https://routezero-7k7j.onrender.com";
const CLAVE = process.env.CLAVE_PRUEBA;
const CUENTAS = {
  ADMINISTRADOR: process.env.CORREO_ADMIN ?? "prueba@routezero.dev",
  CONDUCTOR: process.env.CORREO_CONDUCTOR ?? "conductor.prueba@routezero.dev",
} as const;
const PUERTO_CDP = 9334;
const CATEGORIAS = ["performance", "accessibility", "best-practices", "seo"] as const;
const PANTALLAS = [
  { nombre: "Mapa", ruta: "/app/mapa", rol: "ADMINISTRADOR" },
  { nombre: "Rutas", ruta: "/app/rutas", rol: "ADMINISTRADOR" },
  { nombre: "Conductor", ruta: "/", rol: "CONDUCTOR" },
] as const;
const resultados: Record<string, unknown> = {};

async function tokens(rol: keyof typeof CUENTAS): Promise<{ access: string; refresh: string }> {
  const api = await request.newContext({ baseURL: API, extraHTTPHeaders: { "User-Agent": "RouteZero-auditoria/1.0" } });
  const r = await api.post("/api/auth/login", { data: { email: CUENTAS[rol], password: CLAVE }, timeout: 120_000 });
  expect(r.ok(), `login de ${CUENTAS[rol]}: ${r.status()}`).toBeTruthy();
  const d = await r.json();
  return { access: d.access_token, refresh: d.refresh_token };
}

test.beforeAll(() => {
  expect(CLAVE, "Falta la variable de entorno CLAVE_PRUEBA (ver el encabezado del archivo)").toBeTruthy();
});

for (const pantalla of PANTALLAS) {
  for (const factor of ["móvil", "escritorio"] as const) {
    test(`Producción: ${pantalla.nombre} (${factor})`, async () => {
      const t = await tokens(pantalla.rol);
      const navegador = await chromium.launch({ channel: "chrome", args: [`--remote-debugging-port=${PUERTO_CDP}`] });
      try {
        const page = await (await navegador.newContext()).newPage();
        await page.addInitScript(({ access, refresh }) => {
          window.localStorage.setItem("routezero:access_token", access);
          window.localStorage.setItem("routezero:refresh_token", refresh);
        }, t);
        await page.goto(`${FRONTEND}${pantalla.ruta}`, { timeout: 120_000 });
        await page.waitForLoadState("networkidle", { timeout: 120_000 });

        const resultado = await lighthouse(
          page.url(),
          { port: PUERTO_CDP, output: "json", logLevel: "error", onlyCategories: [...CATEGORIAS], disableStorageReset: true },
          factor === "escritorio" ? desktopConfig : undefined,
        );
        const lhr = resultado!.lhr;
        const p: Record<string, number> = {};
        for (const c of CATEGORIAS) p[c] = Math.round((lhr.categories[c].score ?? 0) * 100);
        const ms = (id: string) => Math.round(lhr.audits[id].numericValue ?? 0);
        const metricas = { fcp_ms: ms("first-contentful-paint"), lcp_ms: ms("largest-contentful-paint"), tbt_ms: ms("total-blocking-time"), cls: Number((lhr.audits["cumulative-layout-shift"].numericValue ?? 0).toFixed(3)) };
        resultados[`${pantalla.nombre} (${factor})`] = { ...p, ...metricas };
        console.log(`Producción ${pantalla.nombre} (${factor}): rendimiento ${p.performance}, accesibilidad ${p.accessibility}, buenas prácticas ${p["best-practices"]}, SEO ${p.seo} | FCP ${metricas.fcp_ms} ms, LCP ${metricas.lcp_ms} ms, TBT ${metricas.tbt_ms} ms, CLS ${metricas.cls}`);
        for (const c of ["performance", "accessibility", "best-practices", "seo"] as const) {
          for (const ref of lhr.categories[c].auditRefs) {
            const a = lhr.audits[ref.id];
            if (c === "performance" && ref.weight === 0) continue;
            if (a.score !== null && a.score < 0.9 && a.scoreDisplayMode !== "informative" && a.scoreDisplayMode !== "notApplicable") console.log(`  [${c}] ${a.title}: ${a.displayValue ?? ""}`);
          }
        }
        expect.soft(p.accessibility, "accesibilidad").toBeGreaterThanOrEqual(90);
        expect.soft(p["best-practices"], "buenas prácticas").toBeGreaterThanOrEqual(90);
        expect.soft(p.seo, "SEO").toBeGreaterThanOrEqual(90);
      } finally {
        await navegador.close();
      }
    });
  }
}

test.afterAll(() => {
  mkdirSync("test-results", { recursive: true });
  writeFileSync("test-results/lighthouse-produccion.json", JSON.stringify(resultados, null, 2));
});
