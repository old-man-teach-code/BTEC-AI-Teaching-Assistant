import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: [
      'zshops-jpeg-lottery-identity.trycloudflare.com',
      'https://matilde-biogeographical-robena.ngrok-free.dev',
      'plasma-missions-waters-worm.trycloudflare.com'
    ],
    watch: {
      usePolling: true, 
      interval: 1000, 
    },
    hmr: {
      port: 5173, 
    },
  },
})
