import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/auth/request-magic-link': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/auth/verify-magic-link': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/auth/me': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})