/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { configDefaults } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
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
