import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    port: 80,
    proxy: {
      '/api': 'http://127.0.0.1:80/api',
      '/resources': 'http://127.0.0.1:80/media',
    },
  },
})
