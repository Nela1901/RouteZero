import { defineConfig, devices } from "@playwright/test";

// Monitoreo de producción (Vercel + Render) con Playwright: Web Vitals, tiempos de la API, códigos HTTP y disponibilidad.
// Se ejecuta aparte (`npm run monitorear`) porque llama a los servicios desplegados y no necesita credenciales: solo
// usa la pantalla pública de inicio de sesión y endpoints que responden sin sesión.
const CI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e/monitoreo",
  testMatch: /\.monitoreo\.ts$/,
  workers: 1,
  timeout: 300_000,
  reporter: CI ? [["github"], ["html", { open: "never" }]] : "list",
  projects: [{ name: "produccion", use: { ...devices["Desktop Chrome"], channel: CI ? undefined : "chrome" } }],
});
