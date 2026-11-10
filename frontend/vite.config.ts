/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'
import { configDefaults } from 'vitest/config'

/**
 * Al compilar, pone en el HTML el CSS principal (unos 4 KB) en lugar de enlazarlo. El navegador no pinta nada hasta
 * descargar las hojas de estilo del `<head>`; en línea, la cáscara del `index.html` se dibuja con el primer HTML recibido.
 * Las hojas de los trozos diferidos (p. ej. la de Leaflet) siguen cargándose aparte, solo al abrir una pantalla con mapa.
 */
function cssPrincipalEnLinea(): Plugin {
  return {
    name: 'css-principal-en-linea',
    apply: 'build',
    transformIndexHtml: {
      order: 'post',
      handler(html, contexto) {
        const bundle = contexto.bundle
        if (!bundle) return html
        return html.replace(/<link rel="stylesheet"[^>]*href="\/(assets\/[^"]+\.css)"[^>]*>/g, (enlace, ruta: string) => {
          const hoja = bundle[ruta]
          return hoja?.type === 'asset' ? `<style>${String(hoja.source).trim()}</style>` : enlace
        })
      },
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), cssPrincipalEnLinea()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    css: true,
    // Las pruebas de extremo a extremo (Playwright) tienen su propio ejecutor
    exclude: [...configDefaults.exclude, 'e2e/**'],
    // Cobertura sobre todo `src/` (no solo los archivos que las pruebas cargan), sin contar las propias pruebas
    coverage: {
      // `lcov` es el formato que lee SonarQube
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.test.{ts,tsx}', 'src/tests/**', 'src/main.tsx', 'src/vite-env.d.ts'],
    },
  },
})
