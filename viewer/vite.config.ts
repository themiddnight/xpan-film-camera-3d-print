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
    // three.js alone is most of the 1.02MB workshop chunk, and the workshop is a local review tool,
    // so splitting buys nothing. The limit sits just above today's size so real growth still warns.
    build: {
      chunkSizeWarningLimit: 1050,
      outDir: isPublic ? 'dist-public' : 'dist',
      rollupOptions: { input: isPublic ? ['index.html'] : ['index.html', 'workshop.html'] },
    },
    test: { include: ['src/**/*.test.ts'] },
  }
})
