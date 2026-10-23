import { expect, test } from "@playwright/test";
import { conSesion, miRuta, parada, simularApi } from "./api";

// Se ejecuta con el viewport de un celular (proyecto "movil")
test.describe("Vista del conductor en el celular (HU-014)", () => {
  test("muestra su ruta, registra una entrega y pasa a la siguiente parada", async ({ page }) => {
    const api = await simularApi(page, { rol: "CONDUCTOR", miRuta: miRuta() });
    await conSesion(page, "CONDUCTOR");
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Hola, Carlos Quispe" })).toBeVisible();
    await expect(page.getByText("0 de 3 entregas")).toBeVisible();
    const siguiente = page.getByRole("region", { name: "Siguiente parada" });
    await expect(siguiente.getByText("Bodega San José")).toBeVisible();
    await expect(siguiente.getByText("Express")).toBeVisible();
    await expect(page.getByRole("region", { name: "Mapa de tu ruta" })).toBeVisible();

    await siguiente.getByRole("button", { name: "Entregado" }).click();
    await page.getByRole("button", { name: "Sí, entregado" }).click();

    await expect(page.getByText("1 de 3 entregas")).toBeVisible();
    await expect(page.getByRole("region", { name: "Siguiente parada" }).getByText("Calzados Puno")).toBeVisible();
    const atendidas = page.getByRole("region", { name: "Paradas atendidas" });
    await expect(atendidas.getByText("Bodega San José")).toBeVisible();
    const patch = api.peticiones.find((p) => p.metodo === "PATCH");
    expect(patch?.cuerpo).toEqual({ estado: "ENTREGADO" });
    expect(patch?.ruta).toMatch(/\/api\/rutas\/ruta-1\/paradas\/.+\/entrega$/);
    expect(api.noSimuladas).toEqual([]);
  });

  test("al atender la última parada muestra que la ruta está completada", async ({ page }) => {
    const casi = [parada(1, { estado_entrega: "ENTREGADO" }), parada(2, { estado_entrega: "FALLIDO" }), parada(3)];
    const api = await simularApi(page, { rol: "CONDUCTOR", miRuta: miRuta(casi, "EN_EJECUCION") });
    await conSesion(page, "CONDUCTOR");
    await page.goto("/");

    await page.getByRole("button", { name: "Entregado" }).click();
    await page.getByRole("button", { name: "Sí, entregado" }).click();
    await expect(page.getByText("Ruta completada")).toBeVisible();
    await expect(page.getByRole("button", { name: "Entregado" })).toHaveCount(0);
    expect(api.noSimuladas).toEqual([]);
  });

  test("sin ruta asignada muestra el mensaje", async ({ page }) => {
    const api = await simularApi(page, { rol: "CONDUCTOR" });
    await conSesion(page, "CONDUCTOR");
    await page.goto("/");

    await expect(page.getByText("No tienes rutas asignadas por el momento.")).toBeVisible();
    await expect(page.getByRole("region", { name: "Mapa de tu ruta" })).toHaveCount(0);
    expect(api.noSimuladas).toEqual([]);
  });

  test("una cuenta sin vincular recibe la explicación", async ({ page }) => {
    const sinVincular = {
      ...miRuta(),
      vinculado: false,
      conductor: null,
      ruta: null,
      siguiente_orden: null,
      entregadas: 0,
      pendientes: 0,
      mensaje: "Tu usuario todavía no está vinculado a un conductor. Pide al administrador que registre tu correo en tu ficha de conductor.",
    };
    const api = await simularApi(page, { rol: "CONDUCTOR", miRuta: sinVincular });
    await conSesion(page, "CONDUCTOR");
    await page.goto("/");

    await expect(page.getByText("Cuenta sin vincular")).toBeVisible();
    await expect(page.getByText(/registre tu correo/)).toBeVisible();
    expect(api.noSimuladas).toEqual([]);
  });

  test("la pantalla no tiene desplazamiento horizontal y los botones son fáciles de tocar", async ({ page }) => {
    const api = await simularApi(page, { rol: "CONDUCTOR", miRuta: miRuta() });
    await conSesion(page, "CONDUCTOR");
    await page.goto("/");
    await expect(page.getByRole("region", { name: "Siguiente parada" })).toBeVisible();

    const ancho = await page.evaluate(() => ({ contenido: document.documentElement.scrollWidth, ventana: document.documentElement.clientWidth }));
    expect(ancho.contenido).toBeLessThanOrEqual(ancho.ventana);
    for (const nombre of ["Entregado", "No se pudo"]) {
      const caja = await page.getByRole("button", { name: nombre }).boundingBox();
      expect(caja!.height).toBeGreaterThanOrEqual(44); // tamaño mínimo de un objetivo táctil
    }
    expect(api.noSimuladas).toEqual([]);
  });
});
