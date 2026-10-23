import { defineConfig, devices } from "@playwright/test";

// Auditoría de calidad (HT-09): validación W3C del HTML renderizado y Lighthouse de cada pantalla. Se ejecuta aparte
// de las pruebas normales (`npm run auditar`) porque llama al validador público del W3C y tarda más.
// Usa los mismos datos sintéticos de `e2e/api.ts`: ningún dato real sale del equipo.
const PUERTO = 4173;

export default defineConfig({
  testDir: "./e2e/auditoria",
  testMatch: /.*\.auditoria\.ts$/,
  workers: 1,
  timeout: 240_000,
  reporter: "list",
  use: { baseURL: `http://localhost:${PUERTO}`, locale: "es-PE", timezoneId: "America/Lima" },
  projects: [{ name: "auditoria", use: { ...devices["Desktop Chrome"], channel: process.env.CI ? undefined : "chrome" } }],
  webServer: {
    command: `npm run build && npx vite preview --port ${PUERTO} --strictPort`,
    url: `http://localhost:${PUERTO}`,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
    env: { VITE_API_URL: `http://localhost:${PUERTO}` },
  },
});
