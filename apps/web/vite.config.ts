/** Vite and Vitest configuration for the Alexa+ simulator UI. */
/// <reference types="vitest/config" />
import { fileURLToPath } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// One .env at the repository root configures every app (spec §14). The page
// sees only its VITE_ variables; this file also reads the CAREMERGE_ ones.
const envDir = fileURLToPath(new URL('../..', import.meta.url))

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, envDir, 'CAREMERGE_')
  // The simulator host serves the API; the dev server proxies to it so the
  // browser stays same-origin and the host needs no CORS (spec §11).
  const simulatorPort = env.CAREMERGE_SIMULATOR_PORT ?? '8765'
  return {
    envDir,
    plugins: [react(), tailwindcss()],
    server: {
      port: 5173,
      strictPort: true,
      proxy: { '/api': { target: `http://127.0.0.1:${simulatorPort}` } },
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      css: false,
    },
  }
})
