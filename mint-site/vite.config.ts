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
    allowedHosts: ['5173-i4ryh4j314okkoe6b74sn-a9adef6c.us4.manus.computer'],
  },
})
