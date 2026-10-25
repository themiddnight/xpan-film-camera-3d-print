// Captures each chapter's picture into out/stills/<id>.png at 1600 x 900. The stills must exist
// before `build:public`, which copies out/stills into the site. Usage: node scripts/stills.mjs
import { spawn } from 'node:child_process'
import { mkdirSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const viewerRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const outDir = join(viewerRoot, '..', 'out', 'stills')
const PORT = 8651
const SIZE = { width: 1600, height: 900 }
const READY_TIMEOUT_MS = 60_000

const chapters = [...readFileSync(join(viewerRoot, 'src/presentation/chapters.ts'), 'utf8').matchAll(/^ {4}id: '([^']+)'/gm)].map(m => m[1])
if (chapters.length === 0) throw new Error('No chapter ids found in src/presentation/chapters.ts')

const server = spawn('pnpm', ['exec', 'vite', '--port', String(PORT)], { cwd: viewerRoot, stdio: ['ignore', 'pipe', 'inherit'] })
const stop = () => server.kill()
process.on('exit', stop)

async function waitForServer() {
  for (let i = 0; i < 100; i++) {
    try {
      if ((await fetch(`http://localhost:${PORT}/`)).ok) return
    } catch {
      await new Promise(r => setTimeout(r, 200))
    }
  }
  throw new Error('The dev server did not start')
}

let failed = false
try {
  await waitForServer()
  mkdirSync(outDir, { recursive: true })
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
  const problems = []
  for (const id of chapters) {
    const page = await browser.newPage({ viewport: SIZE })
    page.on('console', m => {
      if (!['error', 'warning'].includes(m.type())) return
      const text = m.text()
      // THREE.Clock is deprecated in @react-three/fiber 9.8.2; it goes once fiber moves to THREE.Timer.
      if (text.includes('THREE.Clock')) return
      // The software GL driver headless Chromium uses reports every readback as a stall.
      if (text.includes('GPU stall due to ReadPixels')) return
      problems.push(`${id} ${m.type()}: ${text}`)
    })
    page.on('pageerror', e => problems.push(`${id} pageerror: ${e.message}`))
    await page.goto(`http://localhost:${PORT}/?still=${id}`)
    await page.waitForFunction(() => window.stillReady === true, null, { timeout: READY_TIMEOUT_MS })
    await page.screenshot({ path: join(outDir, `${id}.png`) })
    // Closing a page while its canvas draws makes React log an unmount error; only the capture is checked.
    page.removeAllListeners()
    await page.close()
    console.log(`still ${id}`)
  }
  await browser.close()
  if (problems.length > 0) {
    console.error(`Console output while capturing:\n${problems.join('\n')}`)
    failed = true
  }
} catch (e) {
  console.error(e)
  failed = true
} finally {
  stop()
}
process.exit(failed ? 1 : 0)
