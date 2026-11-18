import { defineConfig, devices } from "@playwright/test";

// Pruebas de extremo a extremo (HT-10). Se sirve la aplicación ya compilada y la API se simula en el navegador
// (`e2e/api.ts`), así que no dependen de Render, de Supabase ni de una cuenta con MFA.
const CI = !!process.env.CI;
const PUERTO = 4173;
// En local se usa el Chrome ya instalado; en CI, el Chromium que descarga `playwright install`.
const canal = CI ? undefined : "chrome";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: CI,
  retries: CI ? 1 : 0,
  reporter: CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: `http://localhost:${PUERTO}`,
    locale: "es-PE",
    timezoneId: "America/Lima",
    trace: "retain-on-failure",
  },
  // Tres motores de navegador (Chromium, Firefox y WebKit) para las pruebas de escritorio, y Chromium y WebKit en móvil
  // (Pixel 7 y iPhone 14). La aplicación se prueba igual en todos: un fallo en un solo motor suele ser un problema real.
  projects: [
    { name: "chromium", testIgnore: /movil\.spec\.ts/, use: { ...devices["Desktop Chrome"], channel: canal } },
    { name: "firefox", testIgnore: /movil\.spec\.ts/, use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", testIgnore: /movil\.spec\.ts/, use: { ...devices["Desktop Safari"] } },
    { name: "movil-chromium", testMatch: /movil\.spec\.ts/, use: { ...devices["Pixel 7"], channel: canal } },
    { name: "movil-webkit", testMatch: /movil\.spec\.ts/, use: { ...devices["iPhone 14"] } },
  ],
  webServer: {
    // La API se pide al mismo origen que la aplicación: así `page.route` la intercepta sin CORS.
    command: `npm run build && npx vite preview --port ${PUERTO} --strictPort`,
    url: `http://localhost:${PUERTO}`,
    reuseExistingServer: !CI,
    timeout: 180_000,
    env: { VITE_API_URL: `http://localhost:${PUERTO}` },
  },
});
