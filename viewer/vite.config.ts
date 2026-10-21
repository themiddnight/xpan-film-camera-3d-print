import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The CAD export writes out/manifest.json and out/glb/*. Serving out/ as the public
// directory makes the dev server and the static build read the same files.
export default defineConfig({
  plugins: [react()],
  publicDir: '../out',
  base: './',
  server: { port: 8642, strictPort: true },
  // three.js alone is most of the 1.23MB bundle, and this is a local review tool, so
  // splitting buys nothing. The limit sits just above today's size so real growth still warns.
  build: { chunkSizeWarningLimit: 1300 },
})
