import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// 开发态把 /api 代理到本地后端；容器内由 nginx 做反向代理
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://127.0.0.1:8000'
const proxy = {
  '/api': {
    target: proxyTarget,
    changeOrigin: true,
  },
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy,
  },
  preview: {
    port: 4173,
    proxy,
  },
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 900,
  },
})
