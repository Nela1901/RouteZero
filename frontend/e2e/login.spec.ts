import { expect, test } from "@playwright/test";
import { CREDENCIALES, conSesion, simularApi } from "./api";

test.describe("Inicio de sesión", () => {
  test("un administrador inicia sesión, llega al panel y cierra sesión", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await page.goto("/");

    await page.getByLabel("Correo electrónico").fill(CREDENCIALES.ADMINISTRADOR.email);
    await page.getByLabel("Contraseña").fill(CREDENCIALES.ADMINISTRADOR.password);
    await page.getByRole("button", { name: "Ingresar" }).click();

    await expect(page).toHaveURL(/\/app\/mapa$/);
    const menu = page.getByRole("navigation", { name: "Navegación principal" });
    await expect(menu.getByRole("link", { name: /^Rutas/ })).toBeVisible();
    await expect(menu.getByRole("link", { name: /^Flota/ })).toBeVisible(); // solo el administrador la ve

    await page.getByRole("button", { name: "Cerrar sesión" }).click();
    await page.getByRole("alertdialog").getByRole("button", { name: "Cerrar sesión" }).click(); // confirmación
    await expect(page.getByRole("button", { name: "Ingresar" })).toBeVisible();
    expect(api.peticiones.some((p) => p.metodo === "DELETE" && p.ruta === "/api/auth/sesiones")).toBe(true);
    expect(api.noSimuladas).toEqual([]);
  });

  test("las credenciales incorrectas muestran el error y no entran", async ({ page }) => {
    const api = await simularApi(page);
    await page.goto("/");

    await page.getByLabel("Correo electrónico").fill(CREDENCIALES.ADMINISTRADOR.email);
    await page.getByLabel("Contraseña").fill("otra-clave");
    await page.getByRole("button", { name: "Ingresar" }).click();

    await expect(page.getByText("Credenciales inválidas")).toBeVisible();
    await expect(page).not.toHaveURL(/\/app/);
    expect(api.noSimuladas).toEqual([]);
  });

  test("un operador no ve las secciones de flota ni de conductores", async ({ page }) => {
    const api = await simularApi(page, { rol: "OPERADOR" });
    await conSesion(page, "OPERADOR");
    await page.goto("/app/mapa");

    const menu = page.getByRole("navigation", { name: "Navegación principal" });
    await expect(menu.getByRole("link", { name: /^Rutas/ })).toBeVisible();
    await expect(menu.getByRole("link", { name: /^Flota/ })).toHaveCount(0);
    await expect(menu.getByRole("link", { name: /^Conductores/ })).toHaveCount(0);
    expect(api.noSimuladas).toEqual([]);
  });

  test("una sesión de conductor entra directo a su vista", async ({ page }) => {
    const api = await simularApi(page, { rol: "CONDUCTOR" });
    await conSesion(page, "CONDUCTOR");
    await page.goto("/");

    await expect(page.getByRole("heading", { name: /^Hola,/ })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Navegación principal" })).toHaveCount(0);
    expect(api.noSimuladas).toEqual([]);
  });
});
