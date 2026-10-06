import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Build the SPA into a static root inside the frontend package (frontend/dist)
// so the output layout is deterministic and declarable. The Flask backend
// serves the built assets from this directory.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
});
