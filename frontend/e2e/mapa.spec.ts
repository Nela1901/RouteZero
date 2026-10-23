import { expect, test, type Page } from "@playwright/test";
import { congestion, conSesion, rutaMapa, simularApi } from "./api";

const rutas = () => [rutaMapa("r1", "ABC-101"), rutaMapa("r2", "XYZ-202", "PLANIFICADA")];
const trazos = (page: Page) => page.locator("path.leaflet-interactive");

test.describe("Mapa de rutas (HU-013)", () => {
  test("dibuja los recorridos, las paradas numeradas y las vías, y lista el tiempo de cada tramo", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: rutas(), congestion: congestion("AMARILLO", "08:30:00") });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");

    const panel = page.getByRole("complementary", { name: "Rutas y congestión" });
    await expect(panel.getByText("ABC-101", { exact: true })).toBeVisible();
    await expect(panel.getByText("XYZ-202", { exact: true })).toBeVisible();
    await expect(page.getByRole("region", { name: "Mapa de rutas de Huancayo" })).toBeVisible();

    // 3 vías + 4 tramos y 3 paradas por ruta (2 rutas) + el depósito
    await expect(trazos(page)).toHaveCount(3 + 2 * (4 + 3) + 1);
    for (const numero of ["1", "2", "3"]) {
      await expect(page.locator(".leaflet-tooltip", { hasText: new RegExp(`^${numero}$`) }).first()).toBeVisible();
    }

    await panel.getByText("ABC-101", { exact: true }).click(); // abre la ruta
    await expect(panel.getByText("Depósito → Parada 1").first()).toBeVisible();
    await expect(panel.getByText("7.5 min · 2.50 km · punta").first()).toBeVisible();

    const congestionPanel = page.getByRole("region", { name: "Congestión de las vías" });
    await expect(congestionPanel.getByText("· hora punta", { exact: true })).toBeVisible();
    await expect(congestionPanel.getByText("Congestión moderada · hora punta")).toHaveCount(3);
    expect(api.noSimuladas).toEqual([]);
  });

  test("ocultar una ruta quita sus tramos y sus paradas del mapa", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: rutas() });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");
    await expect(trazos(page)).toHaveCount(3 + 2 * 7 + 1);

    const panel = page.getByRole("complementary", { name: "Rutas y congestión" });
    await panel.getByText("ABC-101", { exact: true }).click(); // abre la ruta para llegar a su casilla
    await panel.getByLabel("Mostrar en el mapa").first().uncheck();
    await expect(trazos(page)).toHaveCount(3 + 7 + 1);
    expect(api.noSimuladas).toEqual([]);
  });

  test("cambiar la hora vuelve a pedir la congestión a esa hora", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: [] });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");

    await page.getByLabel("Hora de la congestión").fill("12:30");
    await expect.poll(() => api.peticiones.some((p) => p.ruta === "/api/rutas/congestion?hora=12:30")).toBe(true);
    expect(api.noSimuladas).toEqual([]);
  });

  test("sin rutas en la fecha muestra el mapa base y el mensaje", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: [] });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");

    await expect(page.getByText(/no hay rutas para esta fecha/i)).toBeVisible();
    await expect(page.getByRole("region", { name: "Mapa de rutas de Huancayo" })).toBeVisible();
    await expect(trazos(page)).toHaveCount(3 + 1); // las tres vías y el depósito
    expect(api.noSimuladas).toEqual([]);
  });

  test("el refresco automático de 30 s vuelve a pedir las rutas", async ({ page }) => {
    await page.clock.install();
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: [] });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");
    const pedidas = () => api.peticiones.filter((p) => p.ruta.startsWith("/api/rutas/mapa")).length;
    await expect.poll(pedidas).toBe(1);

    await page.clock.fastForward(31_000);
    await expect.poll(pedidas).toBeGreaterThanOrEqual(2);
    expect(api.noSimuladas).toEqual([]);
  });
});
