// Captures each chapter's picture into out/stills/<id>.png at 1600 x 900, each inventory part's
// thumbnail into out/stills/parts/<name>.png at 320 x 320, and the 1200 x 630 share card into
// out/stills/og.png. The stills must exist before `build:public`, which copies out/stills
// into the site. Usage: node scripts/stills.mjs
import { spawn } from 'node:child_process'
import { mkdirSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const viewerRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const outDir = join(viewerRoot, '..', 'out', 'stills')
const PORT = 8651
const SIZE = { width: 1600, height: 900 }
const OG_SIZE = { width: 1200, height: 630 }
const THUMB_SIZE = { width: 320, height: 320 }
const THUMB_BATCH = 4
const READY_TIMEOUT_MS = 60_000

// Console lines to ignore, each with its reason.
const IGNORED = [
  // THREE.Clock is deprecated in @react-three/fiber 9.8.2; it goes once fiber moves to THREE.Timer.
  /THREE\.Clock/,
  // The software GL driver headless Chromium uses reports every readback as a stall.
  /GPU stall due to ReadPixels/,
]

function watch(page, id, problems) {
  page.on('console', m => {
    if (!['error', 'warning'].includes(m.type())) return
    const text = m.text()
    if (IGNORED.some(pattern => pattern.test(text))) return
    problems.push(`${id} ${m.type()}: ${text}`)
  })
  page.on('pageerror', e => problems.push(`${id} pageerror: ${e.message}`))
}


const chapters = [...readFileSync(join(viewerRoot, 'src/presentation/chapters.ts'), 'utf8').matchAll(/^ {4}id: '([^']+)'/gm)].map(m => m[1])
if (chapters.length === 0) throw new Error('No chapter ids found in src/presentation/chapters.ts')

// Parts that belong to the camera, as the Parts section lists them; what loads into it has no card.
const parts = JSON.parse(readFileSync(join(viewerRoot, '..', 'out', 'manifest.json'), 'utf8')).parts
  .filter(p => p.inventory).map(p => p.name)
if (parts.length === 0) throw new Error('No inventory parts in out/manifest.json. Run: uv run python cad/export.py')

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
  async function capture(label, query, viewport, file) {
    const page = await browser.newPage({ viewport })
    watch(page, label, problems)
    await page.goto(`http://localhost:${PORT}/?${query}`)
    await page.waitForFunction(() => window.stillReady === true, null, { timeout: READY_TIMEOUT_MS })
    await page.screenshot({ path: file })
    // Closing a page while its canvas draws makes React log an unmount error; only the capture is checked.
    page.removeAllListeners()
    await page.close()
    console.log(`still ${label}`)
  }
  for (const id of chapters) await capture(id, `still=${id}`, SIZE, join(outDir, `${id}.png`))
  mkdirSync(join(outDir, 'parts'), { recursive: true })
  // Each thumbnail loads every part's model, so a few at a time keeps the run short without crowding the software GL driver.
  for (let i = 0; i < parts.length; i += THUMB_BATCH) {
    await Promise.all(parts.slice(i, i + THUMB_BATCH).map(
      name => capture(`parts/${name}`, `part=${name}`, THUMB_SIZE, join(outDir, 'parts', `${name}.png`)),
    ))
  }
  {
    const page = await browser.newPage({ viewport: OG_SIZE, deviceScaleFactor: 1 })
    watch(page, 'og', problems)
    await page.goto(`http://localhost:${PORT}/og.html`)
    await page.waitForFunction(() => window.ogCardReady === true, null, { timeout: READY_TIMEOUT_MS })
    await page.screenshot({ path: join(outDir, 'og.png') })
    page.removeAllListeners()
    await page.close()
    console.log('still og')
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
