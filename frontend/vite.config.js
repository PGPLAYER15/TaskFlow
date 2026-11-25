import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  server: {
    hmr: {force: true},
    proxy: {
      '/api': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      // Mide todo src/, no solo los archivos que importan los tests
      include: ['src/**/*.{js,jsx}'],
      thresholds: { statements: 40, lines: 40 },
      exclude: ['src/__tests__/**', 'src/test/**', 'src/main.jsx', 'src/assets/**'],
    },
    css: { modules: { classNameStrategy: 'non-scoped' } },
  },
});
