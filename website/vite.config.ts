import inertia from '@inertiajs/vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig(({ command, isSsrBuild }) => ({
  plugins: [tailwindcss(), react(), inertia()],
  root: 'frontend',
  base: command === 'serve' ? '/' : isSsrBuild ? '/' : '/static/build/',
  resolve: {
    dedupe: ['react', 'react-dom', '@inertiajs/react'],
  },
  build: {
    outDir: isSsrBuild ? '../frontend/dist/ssr' : '../static/build',
    emptyOutDir: true,
    manifest: !isSsrBuild,
    rollupOptions: {
      input: isSsrBuild ? 'frontend/ssr.tsx' : 'frontend/app.tsx',
    },
  },
  ssr: {
    noExternal: isSsrBuild ? true : ['shiki', '@inertiajs/react'],
  },
  server: {
    origin: 'http://localhost:5173',
  },
}))
