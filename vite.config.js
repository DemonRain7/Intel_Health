import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3002,
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:8081',
        changeOrigin: true
      }
    },
    host: '0.0.0.0'
  }
})