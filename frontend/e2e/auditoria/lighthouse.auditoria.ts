import { mkdirSync, writeFileSync } from "node:fs";
import { chromium, expect, test } from "@playwright/test";
import lighthouse from "lighthouse";
import desktopConfig from "lighthouse/core/config/desktop-config.js";
import { PANTALLAS, abrir } from "./pantallas";

// Lighthouse de cada pantalla, en móvil (configuración por defecto: Moto G con red 4G lenta) y en escritorio.
// Se ejecuta sobre la aplicación compilada con datos sintéticos: accesibilidad, buenas prácticas y SEO son
// comparables con producción; el rendimiento depende de la latencia de la API real y se mide aparte en producción.
const PUERTO_CDP = 9333;
const CATEGORIAS = ["performance", "accessibility", "best-practices", "seo"] as const;
const resultados: Record<string, Record<string, number>> = {};

for (const pantalla of PANTALLAS) {
  for (const factor of ["móvil", "escritorio"] as const) {
    test(`Lighthouse: ${pantalla.nombre} (${factor})`, async () => {
      const navegador = await chromium.launch({ channel: process.env.CI ? undefined : "chrome", args: [`--remote-debugging-port=${PUERTO_CDP}`] });
      try {
        const contexto = await navegador.newContext();
        const page = await contexto.newPage();
        // TEMA=claro audita el tema claro (por defecto, el oscuro): el contraste de color se mide en cada tema
        if (process.env.TEMA === "claro") await page.addInitScript(() => window.localStorage.setItem("routezero:tema", "claro"));
        await abrir(page, pantalla);

        const resultado = await lighthouse(
          page.url(),
          { port: PUERTO_CDP, output: "json", logLevel: "error", onlyCategories: [...CATEGORIAS], disableStorageReset: true },
          factor === "escritorio" ? desktopConfig : undefined,
        );
        const lhr = resultado!.lhr;
        const puntajes: Record<string, number> = {};
        for (const c of CATEGORIAS) puntajes[c] = Math.round((lhr.categories[c].score ?? 0) * 100);
        resultados[`${pantalla.nombre} (${factor})`] = puntajes;
        console.log(`Lighthouse ${pantalla.nombre} (${factor}): rendimiento ${puntajes.performance}, accesibilidad ${puntajes.accessibility}, buenas prácticas ${puntajes["best-practices"]}, SEO ${puntajes.seo}`);

        // Qué falló, para corregirlo
        for (const c of ["accessibility", "best-practices", "seo"] as const) {
          for (const ref of lhr.categories[c].auditRefs) {
            const a = lhr.audits[ref.id];
            if (a.score !== null && a.score < 1 && a.scoreDisplayMode !== "informative" && a.scoreDisplayMode !== "notApplicable") {
              const detalle = ((a.details as { items?: { node?: { snippet?: string } }[] } | undefined)?.items ?? [])
                .map((i) => i.node?.snippet).filter(Boolean).slice(0, 3).join(" | ");
              const resumen = detalle ? ` -> ${detalle.slice(0, 200)}` : "";
              console.log(`  [${c}] ${a.title}${resumen}`);
            }
          }
        }
        if (factor === "móvil" || factor === "escritorio") {
          expect.soft(puntajes.accessibility, "accesibilidad").toBeGreaterThanOrEqual(90);
          expect.soft(puntajes["best-practices"], "buenas prácticas").toBeGreaterThanOrEqual(90);
          expect.soft(puntajes.seo, "SEO").toBeGreaterThanOrEqual(90);
        }
      } finally {
        await navegador.close();
      }
    });
  }
}

test.afterAll(() => {
  mkdirSync("test-results", { recursive: true });
  writeFileSync("test-results/lighthouse.json", JSON.stringify(resultados, null, 2));
});
