import { expect, test } from "@playwright/test";
import { compensacionSostenibilidad, conSesion, dashboardSostenibilidad, simularApi } from "./api";

/** Consultas al dashboard: el encabezado hace una (solo hoy) al abrir el panel y la pantalla hace otra por cada periodo que elige. */
const consultasDelDashboard = (api: { peticiones: { ruta: string }[] }) =>
  api.peticiones.filter((p) => p.ruta.startsWith("/api/sostenibilidad/dashboard"));

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

    // Sin fechas elegidas, la pantalla pide el mes en curso hasta hoy (y el encabezado, solo hoy)
    const pedidos = consultasDelDashboard(api).map((p) => p.ruta);
    expect(pedidos).toHaveLength(2);
    expect(pedidos.some((ruta) => /desde=\d{4}-\d{2}-01&hasta=\d{4}-\d{2}-\d{2}$/.test(ruta))).toBe(true);
    expect(api.noSimuladas).toEqual([]);
  });

  test("el encabezado muestra los kg de CO₂ emitidos hoy y la tarjeta, la huella digital de la sesión (SWDM v4)", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");

    await expect(page.getByLabel(/^CO2 emitido hoy: 28\.4 kilogramos$/)).toBeVisible();
    await expect(page.getByText("28.4 kg CO₂")).toBeVisible();

    const tarjeta = page.getByRole("region", { name: /Huella digital de esta sesión/ });
    await expect(tarjeta).toBeVisible();
    // La tarjeta se actualiza cada 5 s: pasa de 0 a los KB que realmente descargó el navegador
    await expect(tarjeta.getByText(/^[1-9]\d*\.\d KB$/)).toBeVisible({ timeout: 12_000 });
    await expect(tarjeta.getByText(/^\d+\.\d mg CO₂e$/).first()).toBeVisible();
    expect(api.noSimuladas).toEqual([]);
  });

  test("muestra el historial por día, la proyección de cierre del mes frente a la meta y el atajo «Mes anterior»", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");

    // El periodo de prueba es octubre desde el día 1: hay proyección y se compara con la meta de 800 kg
    const proyeccion = page.getByRole("region", { name: /Proyección de cierre del mes/ });
    await expect(proyeccion).toBeVisible();
    await expect(proyeccion.getByText(/de la meta de 800 kg/)).toBeVisible();
    await expect(proyeccion.getByText(/Dentro de la meta|Supera la meta/)).toBeVisible();
    await expect(page.getByRole("img", { name: /Emisiones por día: 2 días con jornadas/ })).toBeVisible();

    const historial = page.getByRole("region", { name: /Historial por día/ });
    await expect(historial.getByRole("row")).toHaveCount(4); // encabezado, 2 días y el total
    await expect(historial.getByRole("row").nth(1)).toContainText("5 / 1"); // 21-oct: 5 entregadas y 1 fallida

    await page.getByRole("button", { name: "Mes anterior" }).click();
    await expect.poll(() => consultasDelDashboard(api).length).toBe(3);
    expect(consultasDelDashboard(api).at(-1)!.ruta).toMatch(/desde=\d{4}-\d{2}-01&hasta=\d{4}-\d{2}-(28|29|30|31)$/);
    expect(api.noSimuladas).toEqual([]);
  });

  test("elegir «Hoy» vuelve a consultar solo ese día", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");
    await expect(page.getByText("Distancia recorrida")).toBeVisible();

    await page.getByRole("button", { name: "Hoy" }).click();
    // Encabezado, mes en curso y «Hoy»
    await expect.poll(() => consultasDelDashboard(api).length).toBe(3);
    const [, desde, hasta] = /desde=(\d{4}-\d{2}-\d{2})&hasta=(\d{4}-\d{2}-\d{2})/.exec(consultasDelDashboard(api).at(-1)!.ruta)!;
    expect(desde).toBe(hasta);
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
    await expect.poll(() => consultasDelDashboard(api).length).toBe(3);

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
    // La pastilla de CO₂ del encabezado es solo del administrador: el operador no la ve ni consulta el dashboard
    await expect(page.getByLabel(/CO2 emitido hoy/)).toHaveCount(0);
    expect(consultasDelDashboard(api)).toHaveLength(0);
    await page.goto("/app/sostenibilidad");
    await expect(page).toHaveURL(/\/app\/mapa$/);
    expect(api.noSimuladas).toEqual([]);
  });
});
