import { defineConfig } from 'vitest/config'
import { loadEnv, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

// The canonical, Open Graph and Twitter tags need an absolute URL for the share image. `%SITE_URL%`
// in index.html is replaced here, from SITE_URL (in the environment or a local .env) or the default.
const DEFAULT_SITE_URL = 'https://xpan-film-camera-3d-print.vercel.app'

function siteUrl(env: Record<string, string>): Plugin {
  const url = (env.SITE_URL || DEFAULT_SITE_URL).replace(/\/+$/, '')
  return {
    name: 'site-url',
    transformIndexHtml: {
      order: 'pre',
      handler(html) {
        const out = html.replaceAll('%SITE_URL%', url)
        if (/%[A-Z_]+%/.test(out)) throw new Error(`index.html has a placeholder with no value: ${/%[A-Z_]+%/.exec(out)![0]}`)
        return out
      },
    },
  }
}

// The CAD export writes out/manifest.json and out/glb/*. Serving out/ as the public
// directory makes the dev server and the static build read the same files.
//
// `--mode public` builds the presentation alone into dist-public/. It copies no public directory:
// scripts/copy-public-data.mjs adds only the manifest, the GLBs and the stills, so STL and STEP
// files never reach the public site.
export default defineConfig(({ mode }) => {
  const isPublic = mode === 'public'
  const env = loadEnv(mode, '.', '')
  return {
    plugins: [react(), siteUrl(env)],
    publicDir: isPublic ? false : '../out',
    base: './',
    server: { port: 5173, strictPort: true },
    // three.js, fiber and drei are most of the one 3D chunk the page needs (1.36MB in the public build with the showcase
    // and the maker half, 383kB gzipped), and the page cannot draw anything without all of it, so splitting buys nothing.
    // The limit sits just above today's size so real growth still warns.
    build: {
      chunkSizeWarningLimit: 1360,
      outDir: isPublic ? 'dist-public' : 'dist',
      rollupOptions: { input: isPublic ? ['index.html'] : ['index.html', 'workshop.html'] },
    },
    test: { include: ['src/**/*.test.ts'] },
  }
})
