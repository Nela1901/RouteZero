import { expect, test } from "@playwright/test";
import { conSesion, simularApi } from "./api";

// WCAG 2.2 AA: criterios que las herramientas automáticas no comprueban del todo
test.describe("Accesibilidad (WCAG 2.2)", () => {
  test("los campos de acceso declaran su finalidad para los gestores de contraseñas (1.3.5 y 3.3.8)", async ({ page }) => {
    const api = await simularApi(page);
    await page.goto("/");

    await expect(page.getByLabel("Correo electrónico")).toHaveAttribute("autocomplete", "username");
    await expect(page.getByLabel("Contraseña")).toHaveAttribute("autocomplete", "current-password");
    expect(api.noSimuladas).toEqual([]);
  });

  test("cada sección tiene su propio título de página (2.4.2)", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");
    await expect(page).toHaveTitle("Mapa · RouteZero");

    const menu = page.getByRole("navigation", { name: "Navegación principal" });
    await menu.getByRole("link", { name: /^Rutas/ }).click();
    await expect(page).toHaveTitle("Rutas · RouteZero");
    await menu.getByRole("link", { name: /^Sostenibilidad/ }).click();
    await expect(page).toHaveTitle("Sostenibilidad · RouteZero");
    expect(api.noSimuladas).toEqual([]);
  });

  test("el primer Tab lleva a «Saltar al contenido» y Enter mueve el foco al contenido principal (2.4.1)", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/rutas");
    await expect(page.getByRole("heading", { name: "Rutas", level: 1 })).toBeVisible();

    await page.keyboard.press("Tab");
    const enlace = page.getByRole("link", { name: "Saltar al contenido" });
    await expect(enlace).toBeFocused();
    await expect(enlace).toBeInViewport(); // al recibir el foco deja de estar fuera de la pantalla

    await page.keyboard.press("Enter");
    await expect.poll(() => page.evaluate(() => document.activeElement?.id)).toBe("contenido");
    expect(api.noSimuladas).toEqual([]);
  });

  test("el elemento con el foco del teclado tiene un contorno visible (2.4.7)", async ({ page }) => {
    await simularApi(page);
    await page.goto("/");
    await page.getByLabel("Correo electrónico").focus();
    await page.keyboard.press("Tab"); // pasa al siguiente campo con el teclado: el foco es «focus-visible»
    const contorno = await page.getByLabel("Contraseña").evaluate((el) => {
      const e = getComputedStyle(el);
      return { ancho: parseFloat(e.outlineWidth), estilo: e.outlineStyle };
    });
    expect(contorno.estilo).not.toBe("none");
    expect(contorno.ancho).toBeGreaterThanOrEqual(2);
  });

  // 1.4.10 (reflujo a 320 px) y 1.4.4 (texto al 200 %: equivale a una ventana de 640 px sobre una de 1280)
  for (const ancho of [320, 640]) {
    test(`ninguna pantalla se desborda horizontalmente con ${ancho} px de ancho (1.4.10 y 1.4.4)`, async ({ page }) => {
      const api = await simularApi(page, { rol: "ADMINISTRADOR" });
      await conSesion(page, "ADMINISTRADOR");
      await page.setViewportSize({ width: ancho, height: 700 });
      for (const ruta of ["/app/mapa", "/app/rutas", "/app/sostenibilidad"]) {
        await page.goto(ruta);
        await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
        const medidas = await page.evaluate(() => ({ contenido: document.documentElement.scrollWidth, ventana: document.documentElement.clientWidth }));
        expect(medidas.contenido, `${ruta} a ${ancho} px`).toBeLessThanOrEqual(medidas.ventana);
      }
      expect(api.noSimuladas).toEqual([]);
    });
  }

  test("con el espaciado de texto que pide WCAG no se pierde contenido ni se desborda (1.4.12)", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/sostenibilidad");
    await expect(page.getByText("Distancia recorrida")).toBeVisible();
    await page.addStyleTag({
      content: "* { line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important; } p { margin-bottom: 2em !important; }",
    });
    await expect(page.getByRole("button", { name: "Descargar reporte PDF" })).toBeVisible();
    const medidas = await page.evaluate(() => ({ contenido: document.documentElement.scrollWidth, ventana: document.documentElement.clientWidth }));
    expect(medidas.contenido).toBeLessThanOrEqual(medidas.ventana);
    expect(api.noSimuladas).toEqual([]);
  });
});
