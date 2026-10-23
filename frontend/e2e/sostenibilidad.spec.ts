import { expect, test } from "@playwright/test";
import { compensacionSostenibilidad, conSesion, dashboardSostenibilidad, simularApi } from "./api";

test.describe("Dashboard de sostenibilidad (HU-015) y plan de compensación (HU-017)", () => {
  test("el administrador ve los indicadores del mes, el plan de compensación y la alerta de la meta", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");

    await expect(page.getByRole("heading", { name: "Sostenibilidad", level: 1 })).toBeVisible();
    await expect(page.getByText("Distancia recorrida")).toBeVisible();
    for (const texto of [/^120\.5\s*km$/, /^28\.4\s*kg$/, /^2\.5\s*L$/, /^96\.7\s*%$/, /^S\/ 11\.25$/]) {
      await expect(page.getByText(texto)).toBeVisible();
    }
    await expect(page.getByRole("region", { name: "Emisiones de CO₂ por día" })).toBeVisible();

    const plan = page.getByRole("region", { name: /Plan de compensación de carbono/ });
    await expect(plan.getByText("46", { exact: true })).toBeVisible();
    await expect(plan.getByRole("alert")).toContainText("superan la meta");
    await expect(plan.getByText(/Gobierno Regional de Junín y SERFOR/)).toBeVisible();

    // Sin fechas elegidas, la pantalla pide el mes en curso hasta hoy
    const pedido = api.peticiones.find((p) => p.ruta.startsWith("/api/sostenibilidad/dashboard"));
    expect(pedido?.ruta).toMatch(/desde=\d{4}-\d{2}-01&hasta=\d{4}-\d{2}-\d{2}$/);
    expect(api.noSimuladas).toEqual([]);
  });

  test("elegir «Hoy» vuelve a consultar solo ese día", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");
    await expect(page.getByText("Distancia recorrida")).toBeVisible();

    await page.getByRole("button", { name: "Hoy" }).click();
    await expect.poll(() => api.peticiones.filter((p) => p.ruta.startsWith("/api/sostenibilidad/dashboard")).length).toBe(2);
    const [, , hoy] = /desde=(\d{4}-\d{2}-\d{2})&hasta=(\d{4}-\d{2}-\d{2})/.exec(api.peticiones.filter((p) => p.ruta.startsWith("/api/sostenibilidad/dashboard"))[1].ruta)!;
    expect(api.peticiones.filter((p) => p.ruta.startsWith("/api/sostenibilidad/dashboard"))[1].ruta).toContain(`desde=${hoy}&hasta=${hoy}`);
    expect(api.noSimuladas).toEqual([]);
  });

  test("sin jornadas en el periodo muestra ceros y los mensajes de «sin datos»", async ({ page }) => {
    const api = await simularApi(page, {
      rol: "ADMINISTRADOR",
      sostenibilidad: { dashboard: dashboardSostenibilidad(false), compensacion: compensacionSostenibilidad(false) },
    });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");

    await expect(page.getByText("No hay jornadas operativas registradas en el periodo seleccionado.")).toBeVisible();
    await expect(page.getByText("S/ 0.00", { exact: true })).toBeVisible();
    await expect(page.getByText(/ejecute al menos una jornada operativa/)).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
    expect(api.noSimuladas).toEqual([]);
  });

  test("«Descargar reporte PDF» descarga el reporte del periodo elegido (HU-016)", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");
    await expect(page.getByText("Distancia recorrida")).toBeVisible();
    await page.getByRole("button", { name: "Hoy" }).click();
    await expect.poll(() => api.peticiones.filter((p) => p.ruta.startsWith("/api/sostenibilidad/dashboard")).length).toBe(2);

    const descarga = page.waitForEvent("download");
    await page.getByRole("button", { name: "Descargar reporte PDF" }).click();
    expect((await descarga).suggestedFilename()).toMatch(/^reporte-sostenibilidad-\d{4}-\d{2}-\d{2}-\d{4}-\d{2}-\d{2}\.pdf$/);
    await expect(page.getByText("El reporte se descargó.")).toBeVisible();

    const pedido = api.peticiones.find((p) => p.ruta.startsWith("/api/sostenibilidad/reporte"));
    const [, desde, hasta] = /desde=(\d{4}-\d{2}-\d{2})&hasta=(\d{4}-\d{2}-\d{2})/.exec(pedido!.ruta)!;
    expect(desde).toBe(hasta); // «Hoy»
    expect(api.noSimuladas).toEqual([]);
  });

  test("sin datos en el periodo el reporte avisa que no hay datos y no descarga nada", async ({ page }) => {
    const api = await simularApi(page, {
      rol: "ADMINISTRADOR",
      sostenibilidad: { dashboard: dashboardSostenibilidad(false), compensacion: compensacionSostenibilidad(false) },
    });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");

    let descargo = false;
    page.on("download", () => (descargo = true));
    await page.getByRole("button", { name: "Descargar reporte PDF" }).click();
    await expect(page.getByRole("alert").filter({ hasText: "Seleccione otro periodo" })).toBeVisible();
    expect(descargo).toBe(false);
    expect(api.noSimuladas).toEqual([]);
  });

  test("el operador no ve Sostenibilidad en el menú", async ({ page }) => {
    const api = await simularApi(page, { rol: "OPERADOR" });
    await conSesion(page, "OPERADOR");
    await page.goto("/app/mapa");

    await expect(page.getByRole("navigation", { name: "Navegación principal" })).toBeVisible();
    await expect(page.getByRole("link", { name: /Sostenibilidad/ })).toHaveCount(0);
    await page.goto("/app/sostenibilidad");
    await expect(page).toHaveURL(/\/app\/mapa$/);
    expect(api.noSimuladas).toEqual([]);
  });
});
