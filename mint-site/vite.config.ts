import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

export default defineConfig({
  plugins: [
    react(),
    nodePolyfills({
      globals: { Buffer: false, global: false, process: false },
      protocolImports: true,
    }),
  ],
  define: {
    global: 'globalThis',
    'process.env': '{}',
    'process.browser': 'true',
  },
  server: {
    allowedHosts: ['.manus.computer'],
  },
})
