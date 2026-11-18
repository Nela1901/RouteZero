import { expect, test } from "@playwright/test";
import { CREDENCIALES, conSesion, miRuta, simularApi } from "./api";

// Disponibilidad y resiliencia: qué ve la persona cuando la API falla (red caída o error 500). La aplicación no debe
// quedarse en blanco ni en «cargando» para siempre: debe avisar con un mensaje claro y permitir volver a intentar.
// Los manejadores registrados después de `simularApi` tienen prioridad sobre los de la simulación general.
test.describe("Resiliencia ante fallos de la API", () => {
  test("si la red falla al iniciar sesión, avisa y deja volver a intentar", async ({ page }) => {
    await simularApi(page);
    await page.route("**/api/auth/login", (ruta) => ruta.abort("failed"));
    await page.goto("/");

    await page.getByLabel("Correo electrónico").fill(CREDENCIALES.ADMINISTRADOR.email);
    await page.getByLabel("Contraseña").fill(CREDENCIALES.ADMINISTRADOR.password);
    await page.getByRole("button", { name: "Ingresar" }).click();

    await expect(page.getByText("No se pudo iniciar sesión")).toBeVisible();
    await expect(page).not.toHaveURL(/\/app/);
    await expect(page.getByRole("button", { name: "Ingresar" })).toBeEnabled(); // se puede reintentar
  });

  test("si el servidor responde 500 al iniciar sesión, muestra el mensaje del error", async ({ page }) => {
    await simularApi(page);
    await page.route("**/api/auth/login", (ruta) =>
      ruta.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Error interno del servidor" }) }),
    );
    await page.goto("/");

    await page.getByLabel("Correo electrónico").fill(CREDENCIALES.ADMINISTRADOR.email);
    await page.getByLabel("Contraseña").fill(CREDENCIALES.ADMINISTRADOR.password);
    await page.getByRole("button", { name: "Ingresar" }).click();

    await expect(page.getByText("Error interno del servidor")).toBeVisible();
    await expect(page.getByRole("button", { name: "Ingresar" })).toBeEnabled();
  });

  test("si la ruta del conductor no carga por un fallo de red, lo dice en lugar de quedarse cargando", async ({ page }) => {
    await simularApi(page, { rol: "CONDUCTOR", miRuta: miRuta() });
    await page.route("**/api/rutas/mi-ruta", (ruta) => ruta.abort("failed"));
    await conSesion(page, "CONDUCTOR");
    await page.goto("/");

    await expect(page.getByText("No se pudo cargar tu ruta")).toBeVisible();
  });
});
