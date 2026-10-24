import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// The CAD export writes out/manifest.json and out/glb/*. Serving out/ as the public
// directory makes the dev server and the static build read the same files.
//
// `--mode public` builds the presentation alone into dist-public/. It copies no public directory:
// scripts/copy-public-data.mjs adds only the manifest, the GLBs and the stills, so STL and STEP
// files never reach the public site.
export default defineConfig(({ mode }) => {
  const isPublic = mode === 'public'
  return {
    plugins: [react()],
    publicDir: isPublic ? false : '../out',
    base: './',
    server: { port: 8642, strictPort: true },
    // three.js, fiber and drei are most of the one 3D chunk the page needs (1.34MB in the public build with the showcase
    // and the maker half, 379kB gzipped), and the page cannot draw anything without all of it, so splitting buys nothing.
    // The limit sits just above today's size so real growth still warns.
    build: {
      chunkSizeWarningLimit: 1345,
      outDir: isPublic ? 'dist-public' : 'dist',
      rollupOptions: { input: isPublic ? ['index.html'] : ['index.html', 'workshop.html'] },
    },
    test: { include: ['src/**/*.test.ts'] },
  }
})
