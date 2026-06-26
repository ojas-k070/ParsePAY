import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/static/',
  build: {
    outDir: path.resolve(__dirname, '../static'),
    emptyOutDir: false,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/upload': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/download': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/delete-statement': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      }
    }
  }
})

