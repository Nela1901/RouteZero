import { defineConfig, devices } from "@playwright/test";

// Lighthouse contra producción (Vercel + Render): mide el rendimiento real, con la latencia de la API. Se ejecuta
// aparte (`npm run auditar:produccion`) y necesita CLAVE_PRUEBA: la contraseña de las cuentas de prueba.
export default defineConfig({
  testDir: "./e2e/auditoria",
  testMatch: /produccion\.auditoria\.ts$/,
  workers: 1,
  timeout: 300_000,
  reporter: "list",
  projects: [{ name: "produccion", use: { ...devices["Desktop Chrome"], channel: "chrome" } }],
});
