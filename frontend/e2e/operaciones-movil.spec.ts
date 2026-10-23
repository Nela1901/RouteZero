import { expect, test, type Page } from "@playwright/test";
import { congestion, conSesion, resumenRuta, rutaMapa, simularApi } from "./api";

// Se ejecuta con el viewport de un celular (proyecto "movil"): HT-09, diseño responsive
async function sinDesplazamientoHorizontal(page: Page) {
  const ancho = await page.evaluate(() => ({ contenido: document.documentElement.scrollWidth, ventana: document.documentElement.clientWidth }));
  expect(ancho.contenido).toBeLessThanOrEqual(ancho.ventana);
}

test.describe("Pantallas de operaciones en el celular (HT-09)", () => {
  test("el mapa con rutas cabe en el ancho del celular y su panel no se sale", async ({ page }) => {
    const api = await simularApi(page, {
      rol: "ADMINISTRADOR",
      mapa: [rutaMapa("r1", "ABC-101"), rutaMapa("r2", "XYZ-202", "PLANIFICADA")],
      congestion: congestion("AMARILLO", "08:30:00"),
    });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");
    // En el celular el panel empieza cerrado para no tapar el mapa
    await expect(page.getByRole("complementary", { name: "Rutas y congestión" })).toHaveCount(0);
    await sinDesplazamientoHorizontal(page);

    await page.getByRole("button", { name: "Mostrar panel" }).click();
    await expect(page.getByRole("complementary", { name: "Rutas y congestión" })).toBeVisible();
    const ventana = page.viewportSize()!;
    const panel = await page.getByRole("complementary", { name: "Rutas y congestión" }).boundingBox();
    expect(panel!.x).toBeGreaterThanOrEqual(0);
    expect(panel!.x + panel!.width).toBeLessThanOrEqual(ventana.width);
    expect(api.noSimuladas).toEqual([]);
  });

  test("la pantalla de sostenibilidad cabe en el ancho del celular", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");
    await expect(page.getByText("Distancia recorrida")).toBeVisible();
    await expect(page.getByRole("region", { name: /Plan de compensación de carbono/ })).toBeVisible();

    await sinDesplazamientoHorizontal(page);
    expect(api.noSimuladas).toEqual([]);
  });

  test("la pantalla de rutas cabe en el ancho del celular", async ({ page }) => {
    const activa = rutaMapa("r1", "ABC-101", "EN_EJECUCION");
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: [activa], rutas: [resumenRuta(activa)] });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/rutas");
    await expect(page.getByRole("button", { name: "Re-optimizar rutas" })).toBeVisible();

    await sinDesplazamientoHorizontal(page);
    expect(api.noSimuladas).toEqual([]);
  });
});
