import { expect, test } from "@playwright/test";
import { conSesion, resumenRuta, rutaMapa, simularApi } from "./api";

test.describe("Re-optimización de rutas (HU-012)", () => {
  test("el administrador re-optimiza y ve el resumen y el borrador por confirmar", async ({ page }) => {
    const activa = rutaMapa("r1", "ABC-101", "EN_EJECUCION");
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: [activa], rutas: [resumenRuta(activa)] });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/rutas");

    await page.getByLabel(/Hora de referencia/).fill("10:00");
    await page.getByRole("button", { name: "Re-optimizar rutas" }).click();

    await expect(page.getByText(/dentro del límite de 30 s/)).toBeVisible();
    await expect(page.getByText(/Re-optimización sin confirmar/)).toBeVisible();
    await expect(page.getByRole("button", { name: "Confirmar rutas" })).toBeVisible();
    const post = api.peticiones.find((p) => p.metodo === "POST" && p.ruta === "/api/rutas/reoptimizar");
    expect(post?.cuerpo).toMatchObject({ hora_actual: "10:00" });
    expect(api.noSimuladas).toEqual([]);
  });

  test("sin rutas activas informa y sugiere generar rutas", async ({ page }) => {
    const activa = rutaMapa("r1", "ABC-101", "CONFIRMADA");
    // El listado muestra una ruta confirmada, pero el servidor ya no encuentra rutas activas
    const api = await simularApi(page, { rol: "ADMINISTRADOR", mapa: [], rutas: [resumenRuta(activa)] });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/rutas");

    await page.getByRole("button", { name: "Re-optimizar rutas" }).click();
    await expect(page.getByText(/genere nuevas rutas/i)).toBeVisible();
    expect(api.noSimuladas).toEqual([]);
  });

  test("el operador consulta las rutas pero no puede re-optimizar", async ({ page }) => {
    const activa = rutaMapa("r1", "ABC-101", "CONFIRMADA");
    const api = await simularApi(page, { rol: "OPERADOR", mapa: [activa], rutas: [resumenRuta(activa)] });
    await conSesion(page, "OPERADOR");
    await page.goto("/app/rutas");

    await expect(page.getByText("ABC-101", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Re-optimizar rutas" })).toHaveCount(0);
    expect(api.noSimuladas).toEqual([]);
  });
});
