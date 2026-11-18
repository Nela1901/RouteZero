import { expect, test } from "@playwright/test";
import { conSesion, simularApi } from "./api";

// Guía de primeros pasos y preguntas frecuentes. Nace de la evaluación de usabilidad con la escala SUS: los ítems sobre necesitar
// ayuda y aprender antes de usar el sistema fueron los más bajos, y 8 de 10 comentarios pedían una explicación inicial.
test.describe("Ayuda y primeros pasos", () => {
  test("el administrador abre la ayuda desde el menú, ve su guía y despliega una pregunta", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/mapa");

    await page.getByRole("navigation", { name: "Navegación principal" }).getByRole("link", { name: /^Ayuda/ }).click();

    await expect(page).toHaveURL(/\/app\/ayuda$/);
    await expect(page).toHaveTitle("Ayuda · RouteZero");
    await expect(page.getByRole("heading", { name: "Ayuda y primeros pasos", level: 1 })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Primeros pasos como administrador" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Cómo leer el mapa" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Verificación en dos pasos" })).toBeVisible();

    await page.getByText("¿Cuánto tarda en generar las rutas?").click();
    await expect(page.getByText(/hasta medio minuto/).first()).toBeVisible();
    expect(api.noSimuladas).toEqual([]);
  });

  test("el operador ve su guía y no las preguntas exclusivas del administrador", async ({ page }) => {
    const api = await simularApi(page, { rol: "OPERADOR" });
    await conSesion(page, "OPERADOR");
    await page.goto("/app/ayuda");

    await expect(page.getByRole("heading", { name: "Primeros pasos como operador" })).toBeVisible();
    await expect(page.getByText("¿Qué puede ver cada rol?")).toBeVisible();
    await expect(page.getByText("¿Cuánto tarda en generar las rutas?")).toHaveCount(0);
    expect(api.noSimuladas).toEqual([]);
  });

  test("el índice lleva a la sección elegida", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/ayuda");

    await page.getByRole("navigation", { name: "Contenido de la ayuda" }).getByRole("link", { name: "Preguntas frecuentes" }).click();

    await expect(page).toHaveURL(/#ayuda-preguntas$/);
    await expect(page.getByRole("heading", { name: "Preguntas frecuentes" })).toBeInViewport();
    expect(api.noSimuladas).toEqual([]);
  });

  test("las preguntas se pueden desplegar solo con el teclado", async ({ page }) => {
    const api = await simularApi(page, { rol: "ADMINISTRADOR" });
    await conSesion(page, "ADMINISTRADOR");
    await page.goto("/app/ayuda");

    const resumen = page.getByText("¿Qué diferencia hay entre generar, confirmar y descartar?");
    await resumen.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByText(/todavía no ven los conductores/)).toBeVisible();
    expect(api.noSimuladas).toEqual([]);
  });
});
